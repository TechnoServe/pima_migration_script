import time
from uuid import uuid4
from typing import List, Dict, Any, Optional

from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked


# Salesforce object + fields
SF_OBJECT = "Farm_Visit__c"

SF_ID = "Id"
SF_IS_DELETED = "IsDeleted"
SF_CREATED_AT = "CreatedDate"
SF_UPDATED_AT = "LastModifiedDate"

SF_DATE_VISITED = "Date_Visited__c"
SF_VISIT_TYPE = "Farm_Visit_Type__c"
SF_VISIT_COMMENTS = "visit_comments__c"
SF_LATEST_VISIT = "Latest_Visit__c"

SF_HOUSEHOLD = "Household__c"                 # -> visited_household_id
SF_PRIMARY_FARMER = "Farm_Visited__c"         # -> visited_primary_farmer_id (Participant__c)
SF_TRAINING_SESSION = "Training_Session__c"   # -> training_session_id

SF_VISITING_STAFF = "Farmer_Trainer__c"       # Contact id -> migrated to users -> visiting_staff_id

SF_SUBMISSION_ID = "FV_Submission_ID__c"      # -> submission_id (NOT NULL, UNIQUE)

SF_LAT = "Location_GPS__Latitude__s"
SF_LON = "Location_GPS__Longitude__s"
SF_ALT = "Altitude__c"

# User clarified: this maps to visited_secondary_farmer_id (nullable)
SF_SECONDARY_PARTICIPANT = "Secondary_Farmer__c"


def fetch_sf_farm_visits() -> List[Dict[str, Any]]:
    sf = sf_client()

    count_soql = f"SELECT COUNT() FROM {SF_OBJECT} WHERE IsDeleted = false"
    count_result = sf.query(count_soql)
    total_records = count_result.get("totalSize", 0)
    print(f"Total farm visits to fetch: {total_records}")

    soql = f"""
      SELECT
        {SF_ID}, {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT},
        {SF_DATE_VISITED}, {SF_VISIT_TYPE}, {SF_VISIT_COMMENTS}, {SF_LATEST_VISIT},
        {SF_HOUSEHOLD}, {SF_PRIMARY_FARMER}, {SF_TRAINING_SESSION},
        {SF_VISITING_STAFF},
        {SF_SUBMISSION_ID},
        {SF_LAT}, {SF_LON}, {SF_ALT},
        {SF_SECONDARY_PARTICIPANT}
      FROM {SF_OBJECT}
      WHERE IsDeleted = false
      ORDER BY CreatedDate
    """
    return list(query_all(sf, soql))


def _to_num(v):
    try:
        return float(v) if v is not None and v != "" else None
    except Exception:
        return None


def _to_bool(v) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "y"):
        return True
    if s in ("false", "0", "no", "n"):
        return False
    return None


def _looks_like_sf_id(v: Any) -> bool:
    if not v:
        return False
    s = str(v).strip()
    if len(s) not in (15, 18):
        return False
    # SF ids are base62-ish; keep it simple
    return s.isalnum()


def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for r in rows:
        lat = _to_num(r.get(SF_LAT))
        lon = _to_num(r.get(SF_LON))
        alt = _to_num(r.get(SF_ALT))

        secondary_raw = r.get(SF_SECONDARY_PARTICIPANT)
        secondary_sf_id = secondary_raw

        latest = _to_bool(r.get(SF_LATEST_VISIT))
        if latest is None:
            latest = True

        submission_id  =  r.get(SF_SUBMISSION_ID) if r.get(SF_SUBMISSION_ID) else r.get(SF_ID)

        farm_visit_type = r.get(SF_VISIT_TYPE) if r.get(SF_VISIT_TYPE) else 'Farm Visit'

        out.append({
            "sf_id": r.get(SF_ID),
            "is_deleted": bool(r.get(SF_IS_DELETED)),
            "deleted_at": None,
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),

            "date_visited": r.get(SF_DATE_VISITED),
            "farm_visit_type": farm_visit_type,
            "visit_comments": r.get(SF_VISIT_COMMENTS),
            "latest_visit": latest,

            "visited_household_sf_id": r.get(SF_HOUSEHOLD),
            "visited_primary_farmer_sf_id": r.get(SF_PRIMARY_FARMER),
            "training_session_sf_id": r.get(SF_TRAINING_SESSION),
            "visiting_staff_sf_id": r.get(SF_VISITING_STAFF),

            "submission_id": submission_id,

            "lat": lat,
            "lon": lon,
            "alt": alt,

            "visited_secondary_farmer_sf_id": secondary_sf_id,
        })

    return out


def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")


def _id_map(conn, table: str) -> Dict[str, str]:
    rows = conn.execute(
        text(f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL")
    ).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}


def load(transformed: List[Dict[str, Any]]):
    done = 0
    skipped = 0
    upsert = "app/sql/farm_visits_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[farm_visits] No rows to load.")
        return 0, 0

    with connect() as c:
        households_map = _id_map(c, "households")
        farmers_map = _id_map(c, "farmers")
        training_sessions_map = _id_map(c, "training_sessions")
        users_map = _id_map(c, "users")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []

            for row in batch:
                visited_household_id = households_map.get(row["visited_household_sf_id"])
                visited_primary_farmer_id = farmers_map.get(row["visited_primary_farmer_sf_id"])
                training_session_id = training_sessions_map.get(row["training_session_sf_id"])
                visiting_staff_id = users_map.get(row["visiting_staff_sf_id"])

                # secondary is optional
                visited_secondary_farmer_id = (
                    farmers_map.get(row["visited_secondary_farmer_sf_id"])
                    if row.get("visited_secondary_farmer_sf_id")
                    else None
                )

                params_list.append({
                    "id": str(uuid4()),
                    "sf_id": row["sf_id"],
                    "is_deleted": row["is_deleted"],
                    "deleted_at": row["deleted_at"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],

                    "visited_household_id": visited_household_id,
                    "visited_primary_farmer_id": visited_primary_farmer_id,
                    "visited_secondary_farmer_id": visited_secondary_farmer_id,

                    "submission_id": row["submission_id"],
                    "training_session_id": training_session_id,
                    "visiting_staff_id": visiting_staff_id,

                    "date_visited": row["date_visited"],
                    "visit_comments": row["visit_comments"],
                    "latest_visit": row["latest_visit"],

                    # SF value as-is (your instruction)
                    "farm_visit_type": row["farm_visit_type"],

                    "lat": row["lat"],
                    "lon": row["lon"],
                    "alt": row["alt"],

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

            print(
                f"[farm_visits] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
                f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                flush=True,
            )

    print(f"[farm_visits] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped


def run(project_filter: Optional[str] = None) -> dict:
    # project_filter not used here (Farm_Visit__c doesn't include Project directly in this table schema)
    print("Starting farm visits migration…")
    rows = fetch_sf_farm_visits()
    print(f"Fetched {len(rows)} farm visits from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} farm visits, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}