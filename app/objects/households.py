import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked

# ------------ Salesforce object + fields ------------
SF_HH_OBJECT                = "Household__c"
SF_ID                       = "Id"
SF_IS_DELETED               = "IsDeleted"
SF_NAME                     = "Name"
SF_CREATED_AT               = "CreatedDate"
SF_UPDATED_AT               = "LastModifiedDate"

SF_TRAINING_GROUP           = "Training_Group__c"          # -> farmer_group_id
SF_COMMCARE_CASE_ID         = "CommCare_Case_Id__c"

SF_TNS_ID              = "Household_ID__c"    # preferred for tns_id

SF_HOUSEHOLD_NUMBER         = "Household_Number__c"
SF_FARM_SIZE                = "Farm_Size__c"
SF_FARM_SIZE_BEFORE         = "Farm_Size_Before__c"
SF_FARM_SIZE_AFTER          = "Farm_Size_After__c"
SF_FARM_SIZE_SINCE          = "Planted_After_Maria__c"     # best available numeric proxy

SF_STATUS                   = "Status__c"                  # -> pima.household_status_enum values 'Active'/'Inactive'
SF_FV_AA_SAMPLED            = "FV_AA_Sampled__c"
SF_FV_AA_VISITED            = "FV_AA_Visited__c"
SF_FV_AA_ROUND              = "FV_AA_Current_Sampling_Round__c"

SF_NUMBER_OF_TREES          = "Coffee_Seedlings__c"        # best numeric proxy

# ------------ Helpers ------------
def _to_int(v):
    try:
        return int(v) if v not in (None, "") else None
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return None

def _to_num(v):
    try:
        return float(v) if v not in (None, "") else None
    except Exception:
        return None

def _fmt_eta(s: float) -> str:
    if not s or s != s: return "0s"
    m, sec = divmod(int(s), 60); h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")

def _id_map(conn, table: str) -> Dict[str, str]:
    rows = conn.execute(text(f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL")).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}

# ------------ SOQL ------------

# ------------ Transform ------------
def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:

        out.append({
            "sf_id": r.get(SF_ID),
            "farmer_group_sf_id": r.get(SF_TRAINING_GROUP),

            "household_name": r.get(SF_NAME) or f"HH-{r.get(SF_ID)}",
            "household_number": _to_int(r.get(SF_HOUSEHOLD_NUMBER)) or 0,

            "tns_id": r.get(SF_TNS_ID),
            "commcare_case_id": r.get(SF_COMMCARE_CASE_ID),

            "number_of_trees": _to_int(r.get(SF_NUMBER_OF_TREES)) or 0,
            "farm_size": _to_num(r.get(SF_FARM_SIZE)),
            "sampled_for_fv_aa": bool(r.get(SF_FV_AA_SAMPLED)),
            "farm_size_before": _to_num(r.get(SF_FARM_SIZE_BEFORE)),
            "farm_size_after": _to_num(r.get(SF_FARM_SIZE_AFTER)),
            "farm_size_since": _to_num(r.get(SF_FARM_SIZE_SINCE)),

            "status": (r.get(SF_STATUS) or "Active"),
            "visited_for_fv_aa": bool(r.get(SF_FV_AA_VISITED)),
            "fv_aa_sampling_round": _to_int(r.get(SF_FV_AA_ROUND)) or 0,

            "is_deleted": bool(r.get(SF_IS_DELETED)),
            "deleted_at": None,

            "created_at": r.get(SF_CREATED_AT),
            "updated_at": r.get(SF_UPDATED_AT),
        })
    return out

# ------------ Load ------------
def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    done = 0
    skipped = 0
    upsert = "app/sql/households_upsert.sql"
    total = len(transformed)
    start = time.time()

    if total == 0:
        print("[households] No rows to load.")
        return 0, 0

    with connect() as c:
        fg_map = _id_map(c, "farmer_groups")

        for batch_idx, batch in enumerate(chunked(transformed, 1000), start=1):
            params_list = []
            for row in batch:
                farmer_group_id = fg_map.get(row["farmer_group_sf_id"])

                # Required FKs and required NOT NULLs
                if not farmer_group_id:
                    skipped += 1
                    continue
                if not row["household_name"] or row["tns_id"] is None:
                    skipped += 1
                    continue

                params_list.append({
                    "id": str(uuid4()),
                    "farmer_group_id": farmer_group_id,
                    "household_name": row["household_name"],
                    "household_number": row["household_number"],
                    "tns_id": row["tns_id"],
                    "commcare_case_id": row["commcare_case_id"],
                    "number_of_trees": row["number_of_trees"],
                    "farm_size": row["farm_size"],
                    "sampled_for_fv_aa": row["sampled_for_fv_aa"],
                    "farm_size_before": row["farm_size_before"],
                    "farm_size_after": row["farm_size_after"],
                    "farm_size_since": row["farm_size_since"],
                    "status": row["status"],
                    "visited_for_fv_aa": row["visited_for_fv_aa"],
                    "fv_aa_sampling_round": row["fv_aa_sampling_round"],
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
            print(
                f"[households] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
                f"| {rps:,.0f} rows/s | ETA {int(eta)}s",
                flush=True
            )

    print(f"[households] Completed. Kept {done:,}, skipped {skipped:,} in {int(time.time()-start)}s.")
    return done, skipped

def fetch_sf_households() -> List[Dict[str, Any]]:
    sf = sf_client()
    return list(query_all(sf, _SOQL))

# Inline SOQL kept at bottom for readability
_SOQL = f"""
  SELECT
    {SF_ID},
    {SF_IS_DELETED},
    {SF_NAME},
    {SF_CREATED_AT},
    {SF_UPDATED_AT},

    {SF_TRAINING_GROUP},
    {SF_COMMCARE_CASE_ID},

    {SF_TNS_ID},

    {SF_HOUSEHOLD_NUMBER},
    {SF_FARM_SIZE},
    {SF_FARM_SIZE_BEFORE},
    {SF_FARM_SIZE_AFTER},
    {SF_FARM_SIZE_SINCE},

    {SF_STATUS},
    {SF_FV_AA_SAMPLED},
    {SF_FV_AA_VISITED},
    {SF_FV_AA_ROUND},

    {SF_NUMBER_OF_TREES}
  FROM {SF_HH_OBJECT}
  WHERE IsDeleted = false
"""

def run(project_filter: Optional[str] = None) -> dict:
    print("Starting households migration…")
    rows = fetch_sf_households()
    print(f"Fetched {len(rows)} households from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} households, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
