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

SF_TRAINING_GROUP              = "Training_Group__c"      # -> farmer_group_id
SF_TRAINING_MODULE             = "Training_Module__c"     # -> module_id
SF_TRAINER                     = "Trainer__c"             # -> users.id (nullable)

SF_COMMCARE_CASE_ID            = "CommCare_Case_Id__c"
SF_CREATE_IN_CC                = "Create_In_CommCare__c"
SF_SENT_TO_OPENFN_STATUS       = "Sent_to_OpenFn_Status__c"

SF_DATE_1                      = "Date__c"
SF_LAT_1                       = "Location_GPS__Latitude__s"
SF_LON_1                       = "Location_GPS__Longitude__s"
SF_ALT_1                       = "Altitude__c"

SF_MALE_1                      = "Male_Attendance__c"
SF_FEMALE_1                    = "Female_Attendance__c"
SF_TOTAL_1                     = "Number_in_Attendance__c"

SF_DATE_2                      = "Date_2__c"
SF_LAT_2                       = "Second_Location_GPS__Latitude__s"
SF_LON_2                       = "Second_Location_GPS__Longitude__s"
SF_ALT_2                       = "Second_Altitude__c"

SF_MALE_2                      = "Second_Male_Attendance__c"
SF_FEMALE_2                    = "Second_Female_Attendance__c"
SF_TOTAL_2                     = "Second_Number_in_Attendance__c"

SF_MALE_ATT_FULL               = "Male_Count_Light_Full__c"
SF_FEMALE_ATT_FULL             = "Female_Count_Light_Full__c"
SF_TOTAL_ATT_FULL              = "Total_Count_Light_Full__c"

def fetch_sf_training_sessions() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT
        {SF_ID}, {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT},
        {SF_TRAINING_GROUP}, {SF_TRAINING_MODULE}, {SF_TRAINER},
        {SF_COMMCARE_CASE_ID}, {SF_CREATE_IN_CC}, {SF_SENT_TO_OPENFN_STATUS},
        {SF_DATE_1}, {SF_LAT_1}, {SF_LON_1}, {SF_ALT_1},
        {SF_MALE_1}, {SF_FEMALE_1}, {SF_TOTAL_1},
        {SF_DATE_2}, {SF_LAT_2}, {SF_LON_2}, {SF_ALT_2},
        {SF_MALE_2}, {SF_FEMALE_2}, {SF_TOTAL_2}, 
        {SF_MALE_ATT_FULL}, {SF_FEMALE_ATT_FULL}, {SF_TOTAL_ATT_FULL}
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
        male1   = _to_int(r.get(SF_MALE_1))
        female1 = _to_int(r.get(SF_FEMALE_1))
        total1  = _to_int(r.get(SF_TOTAL_1))

        male2   = _to_int(r.get(SF_MALE_2))
        female2 = _to_int(r.get(SF_FEMALE_2))
        total2  = _to_int(r.get(SF_TOTAL_2))

        # simple aggregates (sum of sessions if provided)
        male_agg   = (male1 or 0) + (male2 or 0)
        female_agg = (female1 or 0) + (female2 or 0)
        total_agg  = (total1 or 0) + (total2 or 0)

        out.append({
            "sf_id": r.get(SF_ID),
            "farmer_group_sf_id": r.get(SF_TRAINING_GROUP),
            "module_sf_id":       r.get(SF_TRAINING_MODULE),
            "trainer_sf_id":      r.get(SF_TRAINER),
            "commcare_case_id":   r.get(SF_COMMCARE_CASE_ID),
            "send_to_commcare":   bool(r.get(SF_CREATE_IN_CC)),
            "send_to_commcare_status": r.get(SF_SENT_TO_OPENFN_STATUS) or "Pending",

            "date_session_1": r.get(SF_DATE_1),
            "lat1": _to_num(r.get(SF_LAT_1)),
            "lon1": _to_num(r.get(SF_LON_1)),
            "alt1": _to_num(r.get(SF_ALT_1)),
            "male1": male1,
            "female1": female1,
            "total1": total1,

            "date_session_2": r.get(SF_DATE_2),
            "lat2": _to_num(r.get(SF_LAT_2)),
            "lon2": _to_num(r.get(SF_LON_2)),
            "alt2": _to_num(r.get(SF_ALT_2)),
            "male2": male2,
            "female2": female2,
            "total2": total2,

            "male_agg": male_agg,
            "female_agg": female_agg,
            "total_agg": total_agg,

            "male_att_full": _to_int(r.get(SF_MALE_ATT_FULL)),
            "female_att_full": _to_int(r.get(SF_FEMALE_ATT_FULL)),
            "total_att_full": _to_int(r.get(SF_TOTAL_ATT_FULL)),

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
    upsert = "app/sql/training_sessions_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[training_sessions] No rows to load.")
        return 0, 0

    with connect() as c:
        module_map = _id_map(c, "training_modules")
        fg_map     = _id_map(c, "farmer_groups")
        user_map   = _id_map(c, "users")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                module_id = module_map.get(row["module_sf_id"])
                fg_id     = fg_map.get(row["farmer_group_sf_id"])
                if not (module_id and fg_id):
                    skipped += 1
                    continue
                trainer_id = user_map.get(row["trainer_sf_id"]) if row["trainer_sf_id"] else None

                params_list.append({
                    "id": str(uuid4()),
                    "module_id": module_id,
                    "farmer_group_id": fg_id,
                    "date_session_1": row["date_session_1"],
                    "commcare_case_id": row["commcare_case_id"] or row["sf_id"],

                    "male_attendees_agg": row["male_agg"],
                    "female_attendees_agg": row["female_agg"],
                    "total_attendees_agg": row["total_agg"],

                    "send_to_commcare": bool(row["send_to_commcare"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "send_to_commcare_status": row["send_to_commcare_status"],

                    "female_attendees_session_1": row["female_att_full"] or row["female1"],
                    "male_attendees_session_2": row["male2"],
                    "female_attendees_session_2": row["female2"],
                    "total_attendees_session_1": row["total_att_full"] or row["total1"],
                    "total_attendees_session_2": row["total2"],

                    "lat1": row["lat1"], "lon1": row["lon1"], "alt1": row["alt1"],
                    "lat2": row["lat2"], "lon2": row["lon2"], "alt2": row["alt2"],

                    "date_session_2": row["date_session_2"],
                    "sf_id": row["sf_id"],
                    "male_attendees_session_1": row["male_att_full"] or row["male1"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "trainer_id": trainer_id,
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

    print(f"[training_sessions] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting training sessions migration…")
    rows = fetch_sf_training_sessions()
    print(f"Fetched {len(rows)} training sessions from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} training sessions, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
