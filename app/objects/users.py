# app/etl/users.py
import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

SF_PROJECT_OBJECT   = "Contact"  # Contact object in Salesforce will be migrated to users table
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
            "username":   None,              # will set from email/local-part during load
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

def _load_existing_sets(conn) -> tuple[set, set]:
    usernames = {
        (r["username"] or "").lower()
        for r in conn.execute(text("SELECT username FROM pima.users WHERE username IS NOT NULL")).mappings()
    }
    emails = {
        (r["email"] or "").lower()
        for r in conn.execute(text("SELECT email FROM pima.users WHERE email IS NOT NULL")).mappings()
    }
    return usernames, emails

def _unique_username_email(
    base_email: Optional[str],
    existing_usernames: set,
    existing_emails: set,
    session_usernames: set,
    session_emails: set,
) -> tuple[str, str]:
    # If we have an email from SF, use it; username = local-part
    if base_email:
        be = base_email.strip().lower()
        # guard against malformed emails
        if "@" in be and be.split("@", 1)[0]:
            local, domain = be.split("@", 1)
            username = local
            email = f"{local}@{domain}"
        else:
            be = None  # treat as missing

    if not base_email or not be:
        # fabricate both if email missing/bad
        suf = uuid4().hex[:6]
        username = f"user-{suf}"
        email = f"user-{suf}@pima.org"

    # ensure uniqueness (DB + this run)
    def bump_username(u: str) -> str:
        cand = u
        while (cand in existing_usernames) or (cand in session_usernames) or (cand == ""):
            cand = f"{u}-{uuid4().hex[:4]}"
        session_usernames.add(cand)
        return cand

    def bump_email(e: str) -> str:
        cand = e
        while (cand.lower() in existing_emails) or (cand.lower() in session_emails) or (cand == "") or ("@" not in cand):
            if "@" in e:
                l, d = e.split("@", 1)
                cand = f"{l}.{uuid4().hex[:4]}@{d}"
            else:
                cand = f"user-{uuid4().hex[:6]}@pima.org"
        session_emails.add(cand.lower())
        return cand

    username = bump_username(username.lower())
    email = bump_email(email.lower())
    return username, email

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
        existing_usernames, existing_emails = _load_existing_sets(c)
        session_usernames: set = set()
        session_emails: set = set()

        for idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                username, email = _unique_username_email(
                    row.get("email"),
                    existing_usernames, existing_emails,
                    session_usernames, session_emails,
                )
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
                # Promote newly used ids to the global sets so next batches see them
                for p in params_list:
                    existing_usernames.add(p["username"].lower())
                    existing_emails.add(p["email"].lower())
                done += len(params_list)

            # progress per batch
            elapsed = time.time() - start
            processed = done + skipped
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(f"[users] {processed:,}/{total:,} ({pct:5.1f}%) "
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
