import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# Salesforce fields
SF_PROJECT_OBJECT   = "Project__c"
SF_PROJECT_NAME     = "Name"
SF_PROJECT_CODE     = "Project_Unique_Id__c"       # -> projects.project_unique_id
SF_STATUS           = "Project_Status__c"
SF_START            = "Project_Start_Date__c"
SF_END              = "Project_End_Date__c"
SF_PROGRAM_LOOKUP   = "Program__c"
SF_TOP_LOCATION_ID  = "Project_Country__c"
SF_IS_DELETED       = "IsDeleted"
SF_CREATED_AT       = "CreatedDate"
SF_UPDATED_AT       = "LastModifiedDate"

def fetch_sf_projects() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT Id, {SF_PROJECT_NAME}, {SF_PROJECT_CODE}, {SF_STATUS},
             {SF_START}, {SF_END},
             {SF_PROGRAM_LOOKUP}, {SF_TOP_LOCATION_ID},
             {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT}
      FROM {SF_PROJECT_OBJECT}
      WHERE IsDeleted = false
    """
    return list(query_all(sf, soql))

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({
            "sf_id": r.get("Id"),
            "project_name": r.get(SF_PROJECT_NAME),
            "project_unique_id": r.get(SF_PROJECT_CODE) or r.get("Id"),
            "status": r.get(SF_STATUS) or "Active",
            "start_date": r.get(SF_START),
            "end_date": r.get(SF_END),
            "program_sf_id": r.get(SF_PROGRAM_LOOKUP),
            "top_location_sf_id": r.get(SF_TOP_LOCATION_ID),
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

def _fmt_eta(seconds: float) -> str:
    if seconds <= 0 or seconds != seconds: return "0s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else (f"{m}m {s}s" if m else f"{s}s")

def _id_map(conn, table: str) -> Dict[str, str]:
    # Build {sf_id -> id} map in one shot
    sql = f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL"
    rows = conn.execute(text(sql)).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/projects_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[projects] No rows to load.")
        return 0, 0

    with connect() as c:
        # Prefetch FK maps once (tiny and fast)
        program_map   = _id_map(c, "programs")
        location_map  = _id_map(c, "locations")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            param_list = []
            for row in batch:
                program_id  = program_map.get(row["program_sf_id"])
                location_id = location_map.get(row["top_location_sf_id"])

                # If you want to skip rows missing FKs, uncomment:
                # if not program_id or not location_id:
                #     skipped += 1
                #     continue

                param_list.append({
                    "id": str(uuid4()),
                    "program_id": program_id,
                    "project_unique_id": row["project_unique_id"],
                    "project_name": row["project_name"],
                    "status": row["status"],
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "location_id": location_id,
                    "sf_id": row["sf_id"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })

            if param_list:
                run_sql_many(c, upsert, param_list)
                done += len(param_list)

            # progress
            elapsed = time.time() - start
            processed = done + skipped
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(
                f"[projects] {processed:,}/{total:,} ({pct:5.1f}%) "
                f"| kept {done:,} | skipped {skipped:,} "
                f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                flush=True
            )

    print(f"[projects] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting projects migration…")
    rows = fetch_sf_projects()
    print(f"Fetched {len(rows)} projects from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} projects, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
