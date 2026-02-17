import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# Salesforce object + fields
SF_TS_OBJECT                   = "Training_Session__c"
SF_ID                          = "Id"
SF_IS_DELETED                  = "IsDeleted"
SF_CREATED_AT                  = "CreatedDate"
SF_UPDATED_AT                  = "LastModifiedDate"

SF_SESSION_1_URL              = "Session_Photo_URL__c"
SF_SESSION_2_URL             = "Session_Photo_URL_2__c"

def fetch_sf_training_sessions() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT
        {SF_ID}, {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT},
        {SF_SESSION_1_URL}, {SF_SESSION_2_URL}
      FROM {SF_TS_OBJECT}
      WHERE IsDeleted = false
    """
    return list(query_all(sf, soql))

def _to_num(v):
    try:
        return float(v) if v is not None and v != "" else None
    except Exception:
        return None

def _to_int(v):
    try:
        return int(v) if v is not None and v != "" else None
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return None

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:

        out.append({
            "sf_id": r.get(SF_ID),
            "sf_session_1_url": r.get(SF_SESSION_1_URL),
            "sf_session_2_url":       r.get(SF_SESSION_2_URL),
            "is_deleted": bool(r.get(SF_IS_DELETED)),
            "deleted_at": None,
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

def _fmt_eta(s: float) -> str:
    if not s or s != s: return "0s"
    m, sec = divmod(int(s), 60); h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def _id_map(conn, table: str) -> Dict[str, str]:
    rows = conn.execute(text(f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL")).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}

def load(transformed: List[Dict[str, Any]]):
    done = 0
    skipped = 0
    upsert = "app/sql/training_sessions_images_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[training_sessions] No rows to load.")
        return 0, 0

    with connect() as c:

        training_sessions = _id_map(c, "training_sessions")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                # Add a record for the first session image URL
                params_list.append({
                    "id": str(uuid4()),
                    "image_reference_type": "training_session",
                    "image_reference_id": training_sessions.get(row["sf_id"]),
                    "image_url": row["sf_session_1_url"],
                    "submission_id": row["sf_id"] + "_1",
                    "verification_status": "unverified",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "system_user": settings.SYSTEM_USER_ID,
                })

                # If there's a second session image URL, add another record for it
                if row["sf_session_2_url"]:
                    params_list.append({
                        "id": str(uuid4()),
                        "image_reference_type": "training_session",
                        "image_reference_id": training_sessions.get(row["sf_id"]),
                        "submission_id": row["sf_id"] + "_2",
                        "image_url": row["sf_session_2_url"],
                        "verification_status": "unverified",
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
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
            print(f"[training_sessions] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
                  f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}", flush=True)

    print(f"[training_session_images] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting training sessions migration…")
    rows = fetch_sf_training_sessions()
    print(f"Fetched {len(rows)} training sessions from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} training sessions, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
