# users.py
import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

SF_PROJECT_OBJECT   = "Contact" # Contact object in Salesforce will be migrated to users table
SF_FIRST_NAME       = "FirstName"
SF_LAST_NAME        = "LastName"
SF_EMAIL            = "Email"
SF_TITLE            = "Title"
SF_TNS_ID           = "TNS_Id__c"
SF_PHONE            = "Phone"
SF_JOB_TITLE        = "Role_In_Hierarchy__c"
SF_USER_ROLE        = "Role_In_Hierarchy__c"
SF_STATUS           = "contact_status__c"
SF_GENDER           = "Gender__c"
SF_CC_CASE_ID       = "CommCare_Case_Id__c"
SF_REPORTS_TO       = "ReportsToId"
SF_TOP_LOCATION_ID  = "Location__c"
SF_IS_DELETED       = "IsDeleted"
SF_CREATED_AT       = "CreatedDate"
SF_UPDATED_AT       = "LastModifiedDate"

def fetch_sf_staff() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT Id, {SF_FIRST_NAME}, {SF_LAST_NAME}, {SF_EMAIL},
             {SF_TITLE}, {SF_TNS_ID}, {SF_PHONE},
             {SF_JOB_TITLE}, {SF_STATUS},
             {SF_GENDER}, {SF_CC_CASE_ID}, {SF_REPORTS_TO},
             {SF_TOP_LOCATION_ID}, {SF_IS_DELETED},
             {SF_CREATED_AT}, {SF_UPDATED_AT}
      FROM {SF_PROJECT_OBJECT}
    """
    return list(query_all(sf, soql))

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({
            "sf_id": r.get("Id"),
            "first_name": r.get(SF_FIRST_NAME),
            "last_name":  r.get(SF_LAST_NAME),
            "email":      r.get(SF_EMAIL),
            "username":   None,              # will derive below if missing
            "password":   None,              # leave NULL
            "tns_id":     r.get(SF_TNS_ID),
            "phone_number": r.get(SF_PHONE),
            "job_title":  r.get(SF_JOB_TITLE),
            "user_role":  r.get(SF_USER_ROLE),
            "status":     r.get(SF_STATUS),
            "gender":     r.get(SF_GENDER),
            "cc_mobile_worker_id": None,
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

def _fmt_eta(s: float) -> str:
    if not s or s != s: return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def _derive_username_email(first_name: Optional[str], last_name: Optional[str],
                           email: Optional[str]) -> tuple[Optional[str], str]:
    # username: first initial + last name + 2-hex suffix; lowercased
    if first_name and last_name:
        uname = (first_name[:1] + last_name).lower() + uuid4().hex[:2]
    else:
        uname = None
    # email: keep provided; else derive from username
    if email:
        return uname, email
    if uname:
        return uname, f"{uname}@pima.org"
    return None, "unknown@pima.org"  # last-resort fallback

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/users_upsert.sql"

    total = len(transformed)
    start = time.time()
    if total == 0:
        print("[users] No rows to load.")
        return 0, 0

    with connect() as c:
        for idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                username, email = _derive_username_email(
                    row["first_name"], row["last_name"], row["email"]
                )
                if not username:
                    skipped += 1
                    continue
                tns_id = row["tns_id"] or uuid4().hex[:20]

                params_list.append({
                    "id": str(uuid4()),
                    "first_name": row["first_name"],
                    "last_name":  row["last_name"],
                    "email":      email,
                    "username":   username,
                    "password":   row["password"],
                    "tns_id":     tns_id,
                    "phone_number": row["phone_number"],
                    "job_title":  row["job_title"],
                    "status":     row["status"],
                    "user_role":  row["user_role"],
                    "commcare_mobile_worker_id": row["cc_mobile_worker_id"],
                    "sf_id":      row["sf_id"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            # progress per batch
            elapsed = time.time() - start
            rps = (done + skipped) / elapsed if elapsed > 0 else 0.0
            eta = (total - (done + skipped)) / rps if rps > 0 else 0.0
            pct = ((done + skipped) / total) * 100
            print(f"[users] {done+skipped:,}/{total:,} ({pct:5.1f}%) "
                  f"| kept {done:,} | skipped {skipped:,} "
                  f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                  flush=True)

    print(f"[users] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: str | None = None) -> dict:
    print("Starting users migration…")
    rows = fetch_sf_staff()
    print(f"Fetched {len(rows)} contacts from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} users, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
