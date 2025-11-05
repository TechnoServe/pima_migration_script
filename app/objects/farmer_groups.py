import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# Salesforce object + fields
SF_FG_OBJECT                = "Training_Group__c"
SF_ID                       = "Id"
SF_IS_DELETED               = "IsDeleted"
SF_NAME                     = "Name"
SF_CREATED_AT               = "CreatedDate"
SF_UPDATED_AT               = "LastModifiedDate"
SF_PROJECT_LOOKUP           = "Project__c"
SF_RESPONSIBLE_STAFF        = "Responsible_Staff__c"
SF_TNS_ID                   = "TNS_Id__c"
SF_CC_CASE_ID               = "CommCare_Case_Id__c"
SF_CREATE_IN_CC             = "Create_In_CommCare__c"
SF_SENT_TO_OPENFN_STATUS    = "Sent_to_OpenFn_Status__c"
SF_GROUP_STATUS             = "Group_Status__c"
SF_FV_AA_ROUND              = "FV_AA_Current_Sampling_Round__c"
SF_LOCATION_LOOKUP          = "Location__c"

def fetch_sf_farmer_groups() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT
        {SF_ID},
        {SF_IS_DELETED},
        {SF_NAME},
        {SF_PROJECT_LOOKUP},
        {SF_RESPONSIBLE_STAFF},
        {SF_TNS_ID},
        {SF_CC_CASE_ID},
        {SF_CREATE_IN_CC},
        {SF_SENT_TO_OPENFN_STATUS},
        {SF_GROUP_STATUS},
        {SF_FV_AA_ROUND},
        {SF_LOCATION_LOOKUP},
        {SF_CREATED_AT},
        {SF_UPDATED_AT}
      FROM {SF_FG_OBJECT}
      WHERE IsDeleted = false
    """
    return list(query_all(sf, soql))

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({
            "sf_id": r.get(SF_ID),
            "project_sf_id": r.get(SF_PROJECT_LOOKUP),
            "responsible_staff_sf_id": r.get(SF_RESPONSIBLE_STAFF),
            "location_sf_id": r.get(SF_LOCATION_LOOKUP),
            "tns_id": r.get(SF_TNS_ID),
            "commcare_case_id": r.get(SF_CC_CASE_ID),
            "ffg_name": r.get(SF_NAME),
            "send_to_commcare": bool(r.get(SF_CREATE_IN_CC)),
            "send_to_commcare_status": r.get(SF_SENT_TO_OPENFN_STATUS) or "Pending",
            "status": r.get(SF_GROUP_STATUS) or "Active",
            "fv_aa_sampling_round": r.get(SF_FV_AA_ROUND),
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

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/farmer_groups_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[farmer_groups] No rows to load.")
        return 0, 0

    with connect() as c:
        project_map   = _id_map(c, "projects")
        user_map      = _id_map(c, "users")
        location_map  = _id_map(c, "locations")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                project_id = project_map.get(row["project_sf_id"])
                staff_id   = user_map.get(row["responsible_staff_sf_id"])
                location_id= location_map.get(row["location_sf_id"])

                # Enforce NOT NULL FKs and required fields; skip if missing
                if not (project_id and staff_id):
                    skipped += 1
                    continue

                # Required textual fields fallback
                ffg_name = row["ffg_name"] or f"FG-{row['sf_id']}"
                tns_id   = row["tns_id"] or uuid4().hex[:20]
                cc_case  = row["commcare_case_id"] or f"CC-{uuid4().hex[:12]}"

                params_list.append({
                    "id": str(uuid4()),
                    "project_id": project_id,
                    "responsible_staff_id": staff_id,
                    "tns_id": tns_id,
                    "commcare_case_id": cc_case,
                    "ffg_name": ffg_name,
                    "send_to_commcare": bool(row["send_to_commcare"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "send_to_commcare_status": row["send_to_commcare_status"],
                    "status": row["status"],
                    "fv_aa_sampling_round": row["fv_aa_sampling_round"],
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "location_id": location_id,
                    "system_user": settings.SYSTEM_USER_ID,
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            elapsed = time.time() - start
            processed = done + skipped
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(f"[farmer_groups] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
                  f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}", flush=True)

    print(f"[farmer_groups] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting farmer groups migration…")
    rows = fetch_sf_farmer_groups()
    print(f"Fetched {len(rows)} farmer groups from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} farmer groups, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
