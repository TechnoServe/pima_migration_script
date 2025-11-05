import time
from uuid import uuid4
from typing import List, Dict, Any
from sqlalchemy import text
from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked, first_value

# Adjust these to your Salesforce API field names
SF_PROGRAM_OBJECT = "Program__c"
SF_PROGRAM_NAME   = "Name"
SF_IS_DELETED = "IsDeleted"
SF_CREATED_AT = "CreatedDate"
SF_UPDATED_AT = "LastModifiedDate"

def _fmt_eta(seconds: float) -> str:
    if seconds <= 0 or seconds != seconds:
        return "0s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else (f"{m}m {s}s" if m else f"{s}s")

def fetch_sf_programs() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""      SELECT Id, {SF_PROGRAM_NAME}, {SF_IS_DELETED}, {SF_CREATED_AT}, {SF_UPDATED_AT}
      FROM {SF_PROGRAM_OBJECT}
    """
    rows = list(query_all(sf, soql))
    return rows

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        name = r.get(SF_PROGRAM_NAME)
        out.append({
            "sf_id": r.get("Id"),
            "program_name": name,
            "program_code": name,
            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
            "is_deleted": r.get(SF_IS_DELETED),
        })
    return out

def load(transformed):
    done = 0
    skipped = 0
    upsert = "app/sql/programs_upsert.sql"

    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[programs] No rows to load.")
        return done, skipped

    with connect() as c:
        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            param_list = []
            for row in batch:
                param_list.append({
                    "id": str(uuid4()),
                    "program_name": row["program_name"],
                    "program_code": row["program_code"],
                    "sf_id": row["sf_id"],
                    "system_user": settings.SYSTEM_USER_ID,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })

            run_sql_many(c, upsert, param_list)
            done += len(param_list)

            # progress (once per batch)
            elapsed = time.time() - start
            rps = done / elapsed if elapsed > 0 else 0.0
            remaining = total - done
            eta = remaining / rps if rps > 0 else 0.0
            pct = (done / total) * 100
            print(
                f"[programs] {done:,}/{total:,} ({pct:5.1f}%)  "
                f"| {rps:,.0f} rows/s  | ETA {_fmt_eta(eta)}",
                flush=True
            )

    print(f"[programs] Completed: {done:,}/{total:,} in {_fmt_eta(time.time()-start)}.")
    return done, skipped
def run(project_filter: str | None = None) -> dict:
    rows = fetch_sf_programs()
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
