import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# ---------- Salesforce object + fields ----------
SF_OBJ               = "Attendance__c"
SF_ID                = "Id"
SF_IS_DELETED        = "IsDeleted"
SF_CREATED_AT        = "CreatedDate"
SF_UPDATED_AT        = "LastModifiedDate"

SF_PARTICIPANT       = "Participant__c"
SF_TRAINING_SESSION  = "Training_Session__c"
SF_DATE              = "Date__c"
SF_STATUS            = "Status__c"
SF_ATTENDED          = "Attended__c"
SF_SUBMISSION_ID     = "Submission_ID__c"

def fetch_sf_attendances() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT
        {SF_ID}, {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT},
        {SF_PARTICIPANT}, {SF_TRAINING_SESSION},
        {SF_DATE}, {SF_STATUS}, {SF_ATTENDED}, {SF_SUBMISSION_ID}
      FROM {SF_OBJ}
      WHERE IsDeleted = false
      AND Training_Session__r.Training_Module__r.Project__c 
      IN ( 'a0EOj000005ZTyjMAG', 'a0EOj000003TZQTMA4', 'a0EOj000005ct73MAA')
    """
    return list(query_all(sf, soql))

def _to_float(v) -> Optional[float]:
    try:
        return float(v) if v not in (None, "") else None
    except Exception:
        return None

def _map_status(sf_status: Optional[str], attended_val: Optional[float]) -> str:
    """
    Postgres enum: ('Present', 'Absent')
    SF may have different values. We map the common ones and fall back to Attended__c.
    """
    if sf_status:
        s = sf_status.strip().lower()
        if s in ("present", "attended", "yes", "true"):
            return "Present"
        if s in ("absent", "no", "false"):
            return "Absent"
    if attended_val is not None:
        return "Present" if attended_val > 0 else "Absent"
    return "Absent"

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        attended_val = _to_float(r.get(SF_ATTENDED))
        out.append({
            "sf_id": r.get(SF_ID),
            "farmer_sf_id": r.get(SF_PARTICIPANT),
            "training_session_sf_id": r.get(SF_TRAINING_SESSION),
            "date_attended": r.get(SF_DATE),
            "submission_id": r.get(SF_SUBMISSION_ID),
            "status": _map_status(r.get(SF_STATUS), attended_val),
            "is_deleted": bool(r.get(SF_IS_DELETED)),
            "deleted_at": None,
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def _id_map(conn, table: str) -> Dict[str, str]:
    rows = conn.execute(text(f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL")).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/attendances_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[attendances] No rows to load.")
        return 0, 0

    # Track submission_id duplicates within this run to avoid UNIQUE violations
    seen_submission_ids: set[str] = set()

    with connect() as c:
        farmer_map = _id_map(c, "farmers")
        ts_map = _id_map(c, "training_sessions")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                farmer_id = farmer_map.get(row["farmer_sf_id"])
                ts_id = ts_map.get(row["training_session_sf_id"])
                submission_id = row.get("submission_id")

                # Required by schema
                if not farmer_id or not ts_id:
                    skipped += 1
                    continue

                # Avoid failing on duplicates inside the same run
                # if submission_id in seen_submission_ids:
                #     skipped += 1
                #     continue
                # seen_submission_ids.add(submission_id)

                params_list.append({
                    "id": str(uuid4()),
                    "farmer_id": farmer_id,
                    "training_session_id": ts_id,
                    "date_attended": row["date_attended"],
                    "submission_id": submission_id,
                    "status": row["status"],  # 'Present'/'Absent'
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "system_user": settings.SYSTEM_USER_ID,
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            processed = done + skipped
            elapsed = time.time() - start
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(
                f"[attendances] {processed:,}/{total:,} ({pct:5.1f}%) "
                f"| kept {done:,} | skipped {skipped:,} "
                f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                flush=True
            )

    print(f"[attendances] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting attendances migration…")
    rows = fetch_sf_attendances()
    print(f"Fetched {len(rows)} attendances from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} attendances, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
