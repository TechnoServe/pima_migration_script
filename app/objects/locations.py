import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# Salesforce fields
SF_LOCATION_OBJECT = "Location__c"
SF_LOCATION_NAME   = "Name"
SF_LOCATION_TYPE   = "Type__c"
SF_PARENT_LOOKUP   = "Parent_Location__c"
SF_IS_DELETED      = "IsDeleted"
SF_CREATED_AT      = "CreatedDate"
SF_UPDATED_AT      = "LastModifiedDate"

def fetch_sf_locations() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT Id, {SF_LOCATION_NAME}, {SF_LOCATION_TYPE},
             {SF_PARENT_LOOKUP}, {SF_IS_DELETED},
             {SF_CREATED_AT}, {SF_UPDATED_AT}
      FROM {SF_LOCATION_OBJECT}
      WHERE IsDeleted = false
    """
    rows = list(query_all(sf, soql))
    return rows

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({
            "sf_id": r.get("Id"),
            "name": r.get(SF_LOCATION_NAME),
            "type": r.get(SF_LOCATION_TYPE) or "Unknown",
            "parent_sf_id": r.get(SF_PARENT_LOOKUP),
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/locations_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[locations] No rows to load.")
        return 0, 0

    with connect() as c:
        # Pass 1: upsert all with parent_location_id=None (batch executemany)
        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = [{
                "id": str(uuid4()),
                "name": r["name"],
                "type": r["type"],
                "parent_location_id": None,
                "sf_id": r["sf_id"],
                "system_user": settings.SYSTEM_USER_ID,
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            } for r in batch]

            if params_list:
                run_sql_many(c, upsert, params_list)
                done += len(params_list)

            # progress per batch
            elapsed = time.time() - start
            rps = done / elapsed if elapsed > 0 else 0.0
            pct = (done / total) * 100
            eta = (total - done) / rps if rps > 0 else 0.0
            print(f"[locations] pass1 {done:,}/{total:,} ({pct:5.1f}%) "
                  f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                  flush=True)

        # Pass 2: link parents by joining on parent.sf_id (simple, readable)
        linked = 0
        for r in transformed:
            parent_sf = r["parent_sf_id"]
            if not parent_sf:
                continue
            c.execute(text("""
                UPDATE pima.locations AS child
                SET parent_location_id = parent.id,
                    last_updated_by_id = :uid,
                    updated_at = GREATEST(child.updated_at, NOW())
                FROM pima.locations AS parent
                WHERE child.sf_id = :child_sf
                  AND parent.sf_id = :parent_sf
                  AND (child.parent_location_id IS DISTINCT FROM parent.id)
            """), {
                "uid": settings.SYSTEM_USER_ID,
                "child_sf": r["sf_id"],
                "parent_sf": parent_sf
            })
            linked += 1

        print(f"[locations] pass2 linked parents for ~{linked:,} rows.", flush=True)

    print(f"[locations] Completed. Upserted {done:,} rows in {_fmt_eta(time.time()-start)}.")
    return done, skipped

def run(project_filter: str | None = None) -> dict:
    print("Starting locations migration…")
    rows = fetch_sf_locations()
    print(f"Fetched {len(rows)} locations from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} locations, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
