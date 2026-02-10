import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# ---------- Salesforce object + fields ----------
SF_OBJ                        = "Participant__c"
SF_ID                         = "Id"
SF_IS_DELETED                 = "IsDeleted"
SF_CREATED_AT                 = "CreatedDate"
SF_UPDATED_AT                 = "LastModifiedDate"

SF_TRAINING_GROUP             = "Training_Group__c"       # -> farmer_group_id
SF_HOUSEHOLD                  = "Household__c"            # -> household_id

SF_TNS_ID                     = "TNS_Id__c"
SF_PIMA_ID                    = "PIMA_ID__c"              # fallback for tns_id

SF_COMMCARE_CASE_ID           = "CommCare_Case_Id__c"
SF_CREATE_IN_CC               = "Create_In_CommCare__c"
SF_SENT_TO_OPENFN_STATUS      = "Sent_to_OpenFn_Status__c"

SF_FULL_NAME                  = "Participant_Full_Name__c" # optional helper
SF_NAME                       = "Name"                      # SF standard Name
SF_LAST_NAME                  = "Last_Name__c"
SF_MIDDLE_NAME                = "Middle_Name__c"

SF_GENDER                     = "Gender__c"               # expect 'Male'/'Female'
SF_AGE                        = "Age__c"
SF_PHONE                      = "Phone_Number__c"

SF_PRIMARY_HH_MEMBER          = "Primary_Household_Member__c"
SF_STATUS                     = "Status__c"               # 'Active'/'Inactive'
SF_STATUS_NOTES               = "Status_Notes__c"

SF_OTHER_ID                   = "Other_ID_Number__c"
SF_NATIONAL_ID                = "National_ID_Number__c"   # fallback for other_id

def fetch_sf_farmers() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT
        {SF_ID}, {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT},
        {SF_TRAINING_GROUP}, {SF_HOUSEHOLD},
        {SF_TNS_ID}, {SF_PIMA_ID},
        {SF_COMMCARE_CASE_ID}, {SF_CREATE_IN_CC}, {SF_SENT_TO_OPENFN_STATUS},
        {SF_FULL_NAME}, {SF_NAME}, {SF_LAST_NAME}, {SF_MIDDLE_NAME},
        {SF_GENDER}, {SF_AGE}, {SF_PHONE},
        {SF_PRIMARY_HH_MEMBER}, {SF_STATUS}, {SF_STATUS_NOTES},
        {SF_OTHER_ID}, {SF_NATIONAL_ID}
      FROM {SF_OBJ}
      WHERE IsDeleted = false
    """
    return list(query_all(sf, soql))

def _to_int(v):
    try:
        return int(v) if v not in (None, "") else None
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return None

def _norm_gender(v: Optional[str]) -> Optional[str]:
    if not v:
        return None
    v = v.strip().lower()
    if v.startswith("m"):
        return "Male"
    if v.startswith("f"):
        return "Female"
    return None

def _split_name(full: Optional[str], last: Optional[str]) -> (Optional[str], Optional[str]):
    """
    Very simple name splitter:
    - If last name is present and included in full, use the remainder as first.
    - Else, split full by spaces into first and last tokens.
    """
    if full:
        parts = full.strip().split()
        if last and last in full and len(parts) >= 2:
            # take everything before last as first_name
            try:
                last_idx = len(parts) - parts[::-1].index(last) - 1
                first = " ".join(parts[:last_idx])
                ln = " ".join(parts[last_idx:])
                return (first or None), (ln or last)
            except Exception:
                pass
        if len(parts) >= 2:
            return parts[0], " ".join(parts[1:])
        return parts[0], last or None
    # no full name; fall back to last only
    return None, last

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        # IDs and FKs
        farmer_group_sf_id = r.get(SF_TRAINING_GROUP)
        household_sf_id    = r.get(SF_HOUSEHOLD)

        # Names
        full_name  = r.get(SF_FULL_NAME) or r.get(SF_NAME)
        last_name  = r.get(SF_LAST_NAME)
        middle     = r.get(SF_MIDDLE_NAME)
        first, last = _split_name(full_name, last_name)
        # Ensure last_name not empty
        last = last or last_name or (full_name.split()[-1] if full_name else None)

        # Required/raw fields
        tns_id  = r.get(SF_TNS_ID) or r.get(SF_PIMA_ID) or uuid4().hex[:20]
        cc_id   = r.get(SF_COMMCARE_CASE_ID) or f"CC-{uuid4().hex[:12]}"
        gender  = _norm_gender(r.get(SF_GENDER)) or "Male"  # default Male if missing/unknown
        age     = _to_int(r.get(SF_AGE)) or 0              # default 0 if missing

        out.append({
            "sf_id": r.get(SF_ID),

            "farmer_group_sf_id": farmer_group_sf_id,
            "household_sf_id": household_sf_id,

            "first_name": first or "Unknown",
            "middle_name": middle,
            "last_name": last or "Unknown",

            "other_id": r.get(SF_OTHER_ID) or r.get(SF_NATIONAL_ID),
            "gender": gender,
            "age": age,
            "phone_number": r.get(SF_PHONE),

            "is_primary_household_member": bool(r.get(SF_PRIMARY_HH_MEMBER)),
            "status": (r.get(SF_STATUS) or "Active"),
            "send_to_commcare": bool(r.get(SF_CREATE_IN_CC)),
            "send_to_commcare_status": (r.get(SF_SENT_TO_OPENFN_STATUS) or "Pending"),
            "status_notes": r.get(SF_STATUS_NOTES),

            "tns_id": tns_id,
            "commcare_case_id": cc_id,

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
    upsert = "app/sql/farmers_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[farmers] No rows to load.")
        return 0, 0

    with connect() as c:
        fg_map  = _id_map(c, "farmer_groups")
        hh_map  = _id_map(c, "households")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                farmer_group_id = fg_map.get(row["farmer_group_sf_id"])
                household_id    = hh_map.get(row["household_sf_id"])

                # Enforce required FKs and NOT NULL columns
                required_ok = all([
                    farmer_group_id, household_id,
                    row["tns_id"]
                ])
                if not required_ok:
                    print({
                    "id": str(uuid4()),
                    "household_id": household_id,
                    "farmer_group_id": farmer_group_id,
                    "tns_id": row["tns_id"],
                    "commcare_case_id": row["commcare_case_id"],
                    "first_name": row["first_name"],
                    "middle_name": row["middle_name"],
                    "last_name": row["last_name"],
                    "other_id": row["other_id"],
                    "gender": row["gender"],
                    "age": row["age"],
                    "phone_number": row["phone_number"],
                    "is_primary_household_member": row["is_primary_household_member"],
                    "status": row["status"],
                    "send_to_commcare": row["send_to_commcare"],
                    "send_to_commcare_status": row["send_to_commcare_status"],
                    "status_notes": row["status_notes"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })
                    skipped += 1
                    continue

                params_list.append({
                    "id": str(uuid4()),
                    "household_id": household_id,
                    "farmer_group_id": farmer_group_id,
                    "tns_id": row["tns_id"],
                    "commcare_case_id": row["commcare_case_id"],
                    "first_name": row["first_name"],
                    "middle_name": row["middle_name"],
                    "last_name": row["last_name"],
                    "other_id": row["other_id"],
                    "gender": row["gender"],
                    "age": row["age"],
                    "phone_number": row["phone_number"],
                    "is_primary_household_member": row["is_primary_household_member"],
                    "status": row["status"],
                    "send_to_commcare": row["send_to_commcare"],
                    "send_to_commcare_status": row["send_to_commcare_status"],
                    "status_notes": row["status_notes"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            processed = done + skipped
            elapsed = time.time() - start
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(f"[farmers] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
                  f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}", flush=True)

    print(f"[farmers] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting farmers migration…")
    rows = fetch_sf_farmers()
    print(f"Fetched {len(rows)} farmers from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} farmers, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
