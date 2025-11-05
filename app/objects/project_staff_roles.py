# app/etl/project_staff_roles.py
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

SF_PROJECT_OBJECT   = "Project_Role__c"
SF_PROJECT_LOOKUP   = "Project__c"
SF_STAFF_LOOKUP     = "Staff__c"
SF_PROJECT_LOCATION = "Project_Location__c"
SF_TNS_ID           = "TNS_Id__c"
SF_ROLE             = "Role__c"
SF_ROLE_FOR_CC      = "Role_for_CommCare__c"
SF_STATUS           = "Roles_Status__c"
SF_CC_CASE_ID       = "CommCare_Case_Id__c"
SF_CREATE_IN_CC     = "Create_In_CommCare__c"
SF_SEND_CC_STATUS   = "Sent_to_OpenFn_Status__c"
SF_IS_DELETED       = "IsDeleted"
SF_CREATED_AT       = "CreatedDate"
SF_UPDATED_AT       = "LastModifiedDate"

def fetch_sf_project_roles() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT Id, {SF_PROJECT_LOOKUP}, {SF_STAFF_LOOKUP}, {SF_TNS_ID},
             {SF_ROLE}, {SF_ROLE_FOR_CC},
             {SF_STATUS}, {SF_CC_CASE_ID},
             {SF_CREATE_IN_CC}, {SF_SEND_CC_STATUS}, {SF_PROJECT_LOCATION},
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
            "staff_sf_id": r.get(SF_STAFF_LOOKUP),
            "project_sf_id": r.get(SF_PROJECT_LOOKUP),
            "tns_id": r.get(SF_TNS_ID),
            "role": r.get(SF_ROLE),
            "status": r.get(SF_STATUS),
            "commcare_case_id": r.get(SF_CC_CASE_ID),
            "create_in_commcare": r.get(SF_CREATE_IN_CC),
            "send_to_commcare_status": r.get(SF_SEND_CC_STATUS) or "Pending",
            "project_location_id": r.get(SF_PROJECT_LOCATION),
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

def _resolve_cc_location_ids(project_location_ids: List[str]) -> Dict[str, str]:
    if not project_location_ids:
        return {}
    sf = sf_client()
    cc_location_map: Dict[str, str] = {}
    chunk_size = 100
    for i in range(0, len(project_location_ids), chunk_size):
        chunk = project_location_ids[i:i + chunk_size]
        soql = f"""
          SELECT Location_Id__c, CC_Mobile_Worker_Group_Id__c
          FROM CommCare_Mobile_Worker_Group_Id__c
          WHERE Location_Id__c IN ({','.join(f"'{x}'" for x in chunk)})
        """
        rows = list(query_all(sf, soql))
        for row in rows:
            cc_location_map[row["Location_Id__c"]] = row.get("CC_Mobile_Worker_Group_Id__c") or ""
    return cc_location_map

def _id_map(conn, table: str) -> Dict[str, str]:
    rows = conn.execute(text(f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL")).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}

def _fmt_eta(s: float) -> str:
    if not s or s != s: return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/project_staff_roles_upsert.sql"

    total = len(transformed)
    if total == 0:
        print("[psr] No rows to load.")
        return 0, 0

    # Collect and resolve CommCare location ids once
    project_location_ids = sorted({r["project_location_id"] for r in transformed if r["project_location_id"]})
    cc_location_map = _resolve_cc_location_ids(project_location_ids)

    start = time.time()
    with connect() as c:
        # Preload {sf_id -> id} maps once
        user_map    = _id_map(c, "users")
        project_map = _id_map(c, "projects")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                if not row["project_location_id"]:
                    skipped += 1
                    continue

                staff_id   = user_map.get(row["staff_sf_id"])
                project_id = project_map.get(row["project_sf_id"])
                cc_loc_id  = cc_location_map.get(row["project_location_id"], "")

                params_list.append({
                    "id": str(uuid4()),
                    "staff_id": staff_id,
                    "project_id": project_id,
                    "tns_id": row["tns_id"],
                    "role": row["role"] or "Unknown",
                    "status": row["status"],
                    "commcare_location_id": cc_loc_id,
                    "commcare_case_id": row["commcare_case_id"],
                    "create_in_commcare": bool(row["create_in_commcare"]),
                    "send_to_commcare_status": row["send_to_commcare_status"] or "Pending",
                    "sf_id": row["sf_id"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            # progress log
            processed = done + skipped
            elapsed = time.time() - start
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(f"[psr] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} | "
                  f"{rps:,.0f} rows/s | ETA {_fmt_eta(eta)}", flush=True)

    print(f"[psr] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting project staff roles migration…")
    rows = fetch_sf_project_roles()
    print(f"Fetched {len(rows)} roles from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} roles, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
