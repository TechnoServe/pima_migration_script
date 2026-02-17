import time
from uuid import uuid4
from typing import List, Dict, Any, Optional

from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked, first_value

SF_OBJECT = "Observation__c"

# Salesforce fields
SF_ID = "Id"
SF_IS_DELETED = "IsDeleted"
SF_CREATED_AT = "CreatedDate"
SF_UPDATED_AT = "LastModifiedDate"

SF_SUBMISSION_ID = "Submission_ID__c"
SF_DATE = "Date__c"

SF_OBSERVER = "Observer__c"               # Contact Id (maps to users.sf_id)
SF_TRAINER = "Trainer__c"                 # Contact Id (maps to users.sf_id)
SF_TRAINING_GROUP = "Training_Group__c"   # Training_Group__c (maps to farmer_groups.sf_id)
SF_TRAINING_SESSION = "Training_Session__c"  # Training_Session__c (maps to training_sessions.sf_id)

SF_FEMALE_PARTICIPANTS = "Female_Participants__c"
SF_MALE_PARTICIPANTS = "Male_Participants__c"
SF_NUM_PARTICIPANTS = "Number_of_Participants__c"

SF_LAT = "Observation_Location__Latitude__s"
SF_LNG = "Observation_Location__Longitude__s"
SF_ALT = "Altitude__c"

SF_OBSERVATION_TYPE = "RecordType.Name"

# Comments fields (we will combine)
SF_COMMENTS_1 = "Comments_1__c"
SF_COMMENTS_2 = "Comments_2__c"
SF_COMMENTS_3 = "Comments_3__c"

def fetch_sf_observations() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT {SF_ID},
             {SF_IS_DELETED},
             {SF_CREATED_AT},
             {SF_UPDATED_AT},
             {SF_SUBMISSION_ID},
             {SF_DATE},
             {SF_OBSERVER},
             {SF_TRAINER},
             {SF_TRAINING_GROUP},
             {SF_TRAINING_SESSION},
             {SF_FEMALE_PARTICIPANTS},
             {SF_MALE_PARTICIPANTS},
             {SF_NUM_PARTICIPANTS},
             {SF_LAT},
             {SF_LNG},
             {SF_ALT},
             {SF_OBSERVATION_TYPE},
             {SF_COMMENTS_1},
             {SF_COMMENTS_2},
             {SF_COMMENTS_3}
      FROM {SF_OBJECT}
    """
    return list(query_all(sf, soql))

def _to_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(float(v))
    except Exception:
        return None

def _to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None

def _map_observation_type(sf_val: Optional[str]) -> Optional[str]:
    if not sf_val:
        return None
    s = str(sf_val).strip().lower()
    if "demo" in s:
        return "Demo Plot"
    if "training" in s:
        return "Training"
    return "Training"

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for r in rows:
        c1 = r.get(SF_COMMENTS_1)
        c2 = r.get(SF_COMMENTS_2)
        c3 = r.get(SF_COMMENTS_3)
        comments_parts = [x for x in [c1, c2, c3] if x]
        comments = "\n".join(str(x).strip() for x in comments_parts) if comments_parts else None

        out.append({
            "sf_id": r.get(SF_ID),
            "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
            "deleted_at": None,
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),

            "submission_id": r.get(SF_SUBMISSION_ID),
            "observation_date": r.get(SF_DATE),

            "observer_sf_id": r.get(SF_OBSERVER),
            "trainer_sf_id": r.get(SF_TRAINER),
            "farmer_group_sf_id": r.get(SF_TRAINING_GROUP),
            "training_session_sf_id": r.get(SF_TRAINING_SESSION),

            "female_attendees": _to_int(r.get(SF_FEMALE_PARTICIPANTS)),
            "male_attendees": _to_int(r.get(SF_MALE_PARTICIPANTS)),
            "total_attendees": _to_int(r.get(SF_NUM_PARTICIPANTS)),

            "lat": _to_float(r.get(SF_LAT)),
            "lng": _to_float(r.get(SF_LNG)),
            "alt": _to_float(r.get(SF_ALT)),

            "observation_type": _map_observation_type(r.get(SF_OBSERVATION_TYPE)),
            "comments": comments,

            # add missing fields in a different script
            # photos, signatures, etc.
        })

    return out

def _resolve_user_id(conn, user_sf_id: Optional[str]) -> Optional[str]:
    if not user_sf_id:
        return None
    return first_value(conn, "SELECT id FROM pima.users WHERE sf_id=:sf", {"sf": user_sf_id})

def _resolve_farmer_group_id(conn, fg_sf_id: Optional[str]) -> Optional[str]:
    if not fg_sf_id:
        return None
    return first_value(conn, "SELECT id FROM pima.farmer_groups WHERE sf_id=:sf", {"sf": fg_sf_id})

def _resolve_training_session_id(conn, ts_sf_id: Optional[str]) -> Optional[str]:
    if not ts_sf_id:
        return None
    return first_value(conn, "SELECT id FROM pima.training_sessions WHERE sf_id=:sf", {"sf": ts_sf_id})

def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/observations_upsert.sql"

    total = len(transformed)
    start = time.time()
    if total == 0:
        print("[observations] No rows to load.")
        return 0, 0

    with connect() as c:
        for batch in chunked(transformed, 1000):
            params_list = []

            for row in batch:
                # Resolve foreign keys
                observer_id = _resolve_user_id(c, row["observer_sf_id"])
                trainer_id = _resolve_user_id(c, row["trainer_sf_id"]) if row.get("trainer_sf_id") else None
                farmer_group_id = _resolve_farmer_group_id(c, row["farmer_group_sf_id"])
                training_session_id = _resolve_training_session_id(c, row["training_session_sf_id"]) if row.get("training_session_sf_id") else None

                observation_type = row.get("observation_type")

                # Required fields in Postgres observations
                if not row["sf_id"]:
                    skipped += 1
                    continue

                missing = []
                if not row.get("observation_date"):
                    missing.append("observation_date")

                if missing:
                    skipped += 1
                    print(f"[observations][skip] sf_id={row['sf_id']} missing={', '.join(missing)}")
                    continue

                params_list.append({
                    "id": str(uuid4()),
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],

                    "submission_id": row["submission_id"],
                    "observer_id": observer_id,
                    "trainer_id": trainer_id,
                    "farmer_group_id": farmer_group_id,
                    "training_session_id": training_session_id,

                    "observation_date": row["observation_date"],
                    "location_gps_latitude": row["lat"],
                    "location_gps_longitude": row["lng"],
                    "location_gps_altitude": row["alt"],

                    "female_attendees": row["female_attendees"],
                    "male_attendees": row["male_attendees"],
                    "total_attendees": row["total_attendees"],

                    "comments": row["comments"],
                    "observation_type": observation_type,

                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "system_user": settings.SYSTEM_USER_ID,
                })

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            # progress
            processed = done + skipped
            elapsed = time.time() - start
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100
            print(
                f"[observations] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
                f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                flush=True
            )

    print(f"[observations] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: str | None = None) -> dict:
    print("Starting observations migration…")
    rows = fetch_sf_observations()
    print(f"Fetched {len(rows)} observations from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} observations, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
