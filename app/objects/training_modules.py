import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# Salesforce object and fields
SF_TM_OBJECT            = "Training_Module__c"
SF_ID                   = "Id"
SF_NAME                 = "Name"
SF_CREATED_AT           = "CreatedDate"
SF_UPDATED_AT           = "LastModifiedDate"
SF_IS_DELETED           = "IsDeleted"
SF_MODULE_DATE          = "Date__c"
SF_MODULE_NUMBER        = "Module_Number__c"
SF_MODULE_TITLE         = "Module_Title__c"
SF_PROJECT_LOOKUP       = "Project__c"
SF_CURRENT_MODULE       = "Current_Training_Module__c"
SF_CURRENT_PREVIOUS     = "Current_Previous_Module__c"
SF_UNIQUE_NAME          = "Unique_Name__c"
SF_STATUS               = "Module_Status__c"
SF_SAMPLE_AA_FV         = "Sample_AA_FV_Farmers__c"

def fetch_sf_training_modules() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT
        {SF_ID},
        {SF_NAME},
        {SF_MODULE_TITLE},
        {SF_MODULE_NUMBER},
        {SF_PROJECT_LOOKUP},
        {SF_CURRENT_MODULE},
        {SF_CURRENT_PREVIOUS},
        {SF_STATUS},
        {SF_SAMPLE_AA_FV},
        {SF_IS_DELETED},
        {SF_CREATED_AT},
        {SF_UPDATED_AT}
      FROM {SF_TM_OBJECT}
      WHERE IsDeleted = false
    """
    return list(query_all(sf, soql))

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        # Prefer Module_Title__c, fallback to Name
        module_name = r.get(SF_MODULE_TITLE) or r.get(SF_NAME)
        out.append({
            "sf_id":                r.get(SF_ID),
            "project_sf_id":        r.get(SF_PROJECT_LOOKUP),
            "module_name":          module_name,
            "module_number":        r.get(SF_MODULE_NUMBER),
            "current_module":       bool(r.get(SF_CURRENT_MODULE)),
            "current_previous":     r.get(SF_CURRENT_PREVIOUS) or "Current",
            "status":               (r.get(SF_STATUS) or "Active"),
            "sample_fv_aa_households": bool(r.get(SF_SAMPLE_AA_FV)),
            "sample_fv_aa_households_status": None,
            "is_deleted":           bool(r.get(SF_IS_DELETED)),
            "deleted_at":           None,
            "created_at":           r.get(SF_CREATED_AT),
            "updated_at":           r.get(SF_UPDATED_AT),
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
    upsert = "app/sql/training_modules_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[training_modules] No rows to load.")
        return 0, 0

    with connect() as c:
        # Resolve project foreign keys once
        project_map = _id_map(c, "projects")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                project_id = project_map.get(row["project_sf_id"])
                params_list.append({
                    "id": str(uuid4()),
                    "project_id": project_id,
                    "module_name": row["module_name"],
                    "module_number": row["module_number"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "current_module": row["current_module"],
                    "sample_fv_aa_households": row["sample_fv_aa_households"],
                    "sample_fv_aa_households_status": row["sample_fv_aa_households_status"],
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "current_previous": row["current_previous"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "status": row["status"],
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            # progress per batch
            elapsed = time.time() - start
            rps = done / elapsed if elapsed > 0 else 0.0
            pct = (done / total) * 100
            eta = (total - done) / rps if rps > 0 else 0.0
            print(
                f"[training_modules] {done:,}/{total:,} ({pct:5.1f}%)  "
                f"| {rps:,.0f} rows/s  | ETA {_fmt_eta(eta)}",
                flush=True
            )

    print(f"[training_modules] Completed. Upserted {done:,} rows in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting training modules migration…")
    rows = fetch_sf_training_modules()
    print(f"Fetched {len(rows)} training modules from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} training modules, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
