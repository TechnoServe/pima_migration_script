import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    """Optimized int conversion with early return"""
    if v is None:
        return None
    try:
        # Direct int conversion for already-int values
        if isinstance(v, int):
            return v
        return int(float(v))
    except (ValueError, TypeError):
        return None

def _to_float(v: Any) -> Optional[float]:
    """Optimized float conversion with early return"""
    if v is None:
        return None
    try:
        # Direct return for already-float values
        if isinstance(v, float):
            return v
        return float(v)
    except (ValueError, TypeError):
        return None

# Pre-compile observation type mapping for faster lookups
_OBSERVATION_TYPE_CACHE = {}

def _map_observation_type(sf_val: Optional[str]) -> Optional[str]:
    """Optimized observation type mapping with caching"""
    if not sf_val:
        return None
    
    # Check cache first
    if sf_val in _OBSERVATION_TYPE_CACHE:
        return _OBSERVATION_TYPE_CACHE[sf_val]
    
    s = str(sf_val).strip().lower()
    result = "Demo Plot" if "demo" in s else "Training"
    
    # Cache the result
    _OBSERVATION_TYPE_CACHE[sf_val] = result
    return result

def _combine_comments(c1: Any, c2: Any, c3: Any) -> Optional[str]:
    """Optimized comment combination"""
    if not any([c1, c2, c3]):
        return None
    comments_parts = [str(x).strip() for x in [c1, c2, c3] if x]
    return "\n".join(comments_parts) if comments_parts else None

def _extract_observation_type(r: Dict[str, Any]) -> Optional[str]:
    """Optimized observation type extraction"""
    try:
        record_type = r.get("RecordType")
        if record_type and isinstance(record_type, dict):
            return record_type.get("Name")
        return None
    except (AttributeError, TypeError):
        return None

def transform_batch(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform a batch of rows - used for parallel processing"""
    out: List[Dict[str, Any]] = []

    for r in rows:
        # Optimized comment combination
        comments = _combine_comments(
            r.get(SF_COMMENTS_1),
            r.get(SF_COMMENTS_2),
            r.get(SF_COMMENTS_3)
        )

        obs_type = _extract_observation_type(r)

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

            "observation_type": _map_observation_type(obs_type),
            "comments": comments,
        })

    return out

def transform(rows: List[Dict[str, Any]], parallel: bool = True, max_workers: int = 4) -> List[Dict[str, Any]]:
    """Transform with optional parallel processing"""
    if not parallel or len(rows) < 1000:
        # For small datasets, parallel overhead isn't worth it
        return transform_batch(rows)
    
    # Split into chunks for parallel processing
    chunk_size = max(len(rows) // max_workers, 1000)
    chunks = list(chunked(rows, chunk_size))
    
    print(f"[observations] Transforming {len(rows)} rows in {len(chunks)} chunks using {max_workers} workers...")
    
    out: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(transform_batch, chunk) for chunk in chunks]
        for future in as_completed(futures):
            out.extend(future.result())
    
    return out

def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def load(transformed: List[Dict[str, Any]], batch_size: int = 10000) -> tuple[int, int]:
    """Optimized loading with larger batches and pre-validation"""
    done = 0
    skipped = 0
    upsert = "app/sql/observations_upsert.sql"

    total = len(transformed)
    start = time.time()
    if total == 0:
        print("[observations] No rows to load.")
        return 0, 0

    with connect() as c:
        print("[observations] Pre-loading foreign key mappings...")
        
        # Load all mappings at once
        user_map = {row[0]: row[1] for row in c.execute(
            text("SELECT sf_id, id FROM pima.users WHERE sf_id IS NOT NULL")
        ).fetchall()}
        
        fg_map = {row[0]: row[1] for row in c.execute(
            text("SELECT sf_id, id FROM pima.farmer_groups WHERE sf_id IS NOT NULL")
        ).fetchall()}
        
        ts_map = {row[0]: row[1] for row in c.execute(
            text("SELECT sf_id, id FROM pima.training_sessions WHERE sf_id IS NOT NULL")
        ).fetchall()}
        
        print(f"[observations] Loaded {len(user_map)} users, {len(fg_map)} farmer groups, {len(ts_map)} training sessions")

        # Pre-generate UUIDs for the entire dataset
        print("[observations] Pre-validating and preparing batch inserts...")
        all_params = []
        
        for row in transformed:
            # Resolve foreign keys using pre-loaded maps
            observer_id = user_map.get(row["observer_sf_id"])
            trainer_id = user_map.get(row["trainer_sf_id"]) if row.get("trainer_sf_id") else None
            farmer_group_id = fg_map.get(row["farmer_group_sf_id"])
            training_session_id = ts_map.get(row["training_session_sf_id"]) if row.get("training_session_sf_id") else None

            # Early validation - skip invalid records
            if not all([row["sf_id"], row["lat"], row["lng"], row["alt"], farmer_group_id, row.get("observation_date"), row.get("submission_id"), observer_id]):
                skipped += 1
                continue

            all_params.append({
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
                "observation_type": row.get("observation_type"),

                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "system_user": settings.SYSTEM_USER_ID,
            })

        print(f"[observations] Prepared {len(all_params)} valid records, skipped {skipped} invalid records")

        # Batch insert with progress tracking
        for batch in chunked(all_params, batch_size):
            run_sql_many(c, upsert, batch)
            done += len(batch)

            # Progress reporting
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

def run(project_filter: str | None = None, parallel_transform: bool = True, batch_size: int = 10000) -> dict:
    """Optimized main runner with configurable parallelism"""
    print("Starting observations migration…")
    
    start_total = time.time()
    
    # Fetch
    fetch_start = time.time()
    rows = fetch_sf_observations()
    fetch_time = time.time() - fetch_start
    print(f"Fetched {len(rows)} observations from Salesforce in {_fmt_eta(fetch_time)}.")
    
    # Transform
    transform_start = time.time()
    tfm = transform(rows, parallel=parallel_transform)
    transform_time = time.time() - transform_start
    print(f"Transformed {len(tfm)} observations in {_fmt_eta(transform_time)}.")
    
    # Load
    load_start = time.time()
    loaded, skipped = load(tfm, batch_size=batch_size)
    load_time = time.time() - load_start
    print(f"Loaded {loaded} observations, skipped {skipped} in {_fmt_eta(load_time)}.")
    
    total_time = time.time() - start_total
    print(f"Total migration time: {_fmt_eta(total_time)}")
    
    return {
        "rows_in": len(rows),
        "rows_loaded": loaded,
        "rows_skipped": skipped,
        "timing": {
            "fetch": fetch_time,
            "transform": transform_time,
            "load": load_time,
            "total": total_time
        }
    }