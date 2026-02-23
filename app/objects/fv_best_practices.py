import time
from uuid import uuid4
from typing import List, Dict, Any, Optional, Set, Tuple

from sqlalchemy import text

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked


# ------------------------------------------------------------
# Salesforce object + core fields
# This code is designed to only migrate fields from Best practices object, and images associated with them.
# Best practice results will use a different file
# ------------------------------------------------------------
SF_OBJECT = "FV_Best_Practices__c"

SF_ID = "Id"
SF_IS_DELETED = "IsDeleted"
SF_CREATED_AT = "CreatedDate"
SF_UPDATED_AT = "LastModifiedDate"

SF_FARM_VISIT = "Farm_Visit__c"
SF_FARM_VISIT_SUBMISSION_ID = "FV_Submission_ID__c"

# (optional if you later need program/visit-type rules; not used now)
# SF_VISIT_TYPE = "Farm_Visit__r.Farm_Visit_Type__c"
# SF_PROGRAM_ID = "Farm_Visit__r.Training_Group__r.Project__c"


# ------------------------------------------------------------
# IMPORTANT: question_key mapping (SF field -> canonical key)
# User request: key mapping only, do NOT decode answers.
# ------------------------------------------------------------
SF_TO_QUESTION_KEY: Dict[str, str] = {
    # Compost
    "Do_you_have_compost_manure__c": "do_you_have_compost_manure",
    #"Compost_Results__c": "do_you_have_compost_manure",  # Compost BU -> same canonical key

    # Record keeping
    "do_you_have_a_record_book__c": "do_you_have_a_record_book",
    "are_there_records_on_the_record_book__c": "are_there_records_on_the_record_book",

    # Shade management
    "level_of_shade_present_on_the_farm__c": "level_of_shade_present_on_the_farm",
    "planted_intercrop_bananas__c": "planted_intercrop_bananas",
    "have_new_shade_been_planted_last_3_years__c": "new_shade_trees_in_the_last_3_years",

    # Weeding
    "how_many_weeds_under_canopy_and_how_big__c": "how_many_weeds_under_canopy_and_how_big_are_they",
    "Have_herbicides_been_used_on_the_field__c": "used_herbicides",
    "has_coffee_field_been_dug__c": "has_coffee_field_been_dug__c",

    # Stumping
    "stumping_method_on_majority_of_trees__c": "stumping_methods_used_on_majority_of_trees",
    "year_stumping__c": "year_stumping",
    "number_of_trees_stumped__c": "number_of_trees_stumped",
    "main_stems_in_majority_coffee_trees__c": "main_stems_in_majority_coffee_trees",

    # Main stems
    "number_of_main_stems_on_majority_trees__c": "number_of_main_stems_on_majority_trees",

    # Optional extras (keep if you included them in SF select)
    "Color_of_coffee_tree_leaves__c": "are_the_leave_green_or_yellow_pale_green",
    "health_of_new_planting_choice__c": "health_of_new_planting_choice",

    # Pesticide use
    "used_pesticide__c": "used_pesticides",
    "pesticide_number_of_times__c": "pesticide_number_of_times",
    "pesticide_spray_type__c": "pesticide_spray_type",

    # Kitchen garden
    "is_there_a_kitchen_garden__c": "is_there_a_kitchen_garden",

}


# ------------------------------------------------------------
# Best practice groups (what becomes fv_best_practices rows)
# best_practice_type stored in DB should be consistent with your other codebase labels
# ------------------------------------------------------------
BEST_PRACTICE_DEFS = [

    # 1. Health of New Planing
    {
        "best_practice_type": "Health of New Planting",
        "fields": ["health_of_new_planting_choice__c"],
        "image_fields": [],
    },
    # 2. Main Stems
    {
        "best_practice_type": "Main Stems",
        "fields": ["number_of_main_stems_on_majority_trees__c"],
        "image_fields": ["photo_of_trees_and_average_main_stems__c"],
    },
    # 3. Nutrition
    # are_the_leave_green_or_yellow_pale_green
    # type_chemical_applied_on_coffee_last_12_months
    {
        "best_practice_type": "Nutrition",
        "fields": ["Color_of_coffee_tree_leaves__c"],
        "image_fields": [],

    },

    # 4. Weeding
    # check which_product_have_you_used again
    {
        "best_practice_type": "Weeding",
        "fields": ["how_many_weeds_under_canopy_and_how_big__c", "Have_herbicides_been_used_on_the_field__c", "has_coffee_field_been_dug__c"],
        "image_fields": ["photo_of_weeds_under_the_canopy__c"],
    },
    # 5. IPDM
    # methods_of_controlling_coffee_berry_borer
    # methods_of_controlling_white_stem_borer
    # methods_of_controlling_coffee_leaf_rust

    # 6. Erosion Control
    # methods_of_erosion_control

    # 7. Shade management
    {
        "best_practice_type": "Shade Management",
        "fields": ["level_of_shade_present_on_the_farm__c", "planted_intercrop_bananas__c", "have_new_shade_been_planted_last_3_years__c"],
        "image_fields": ["photo_of_level_of_shade_on_the_plot__c"],
    },
    # 8. Record Keeping
    # NOTE: REMEMBER TO MAP RECORD BOOK METHODS IN PB ANSWERS
    {
        "best_practice_type": "Record Keeping",
        "fields": ["do_you_have_a_record_book__c", "are_there_records_on_the_record_book__c"],
        "image_fields": ["take_a_photo_of_the_record_book__c"],
    },
    # 9. Compost
    {
        "best_practice_type": "Compost",
        "fields": ["Do_you_have_compost_manure__c"],
        "image_fields": ["photo_of_the_compost_manure__c"],
    },
    # 10. Stumping
    {
        "best_practice_type": "Stumping",
        "fields": ["stumping_method_on_majority_of_trees__c", "number_of_trees_stumped__c", "year_stumping__c", "main_stems_in_majority_coffee_trees__c"],
        "image_fields": ["photos_of_stumped_coffee_trees__c"],
    },
    # 11. Pesticide use
    # NOTE: MAP THESE IN BP RESULTS JOB
    # do_you_spray_any_of_the_following_on_your_farm_for_leaf_miner_or_rust
    # which_pests_cause_you_problems
    {
        "best_practice_type": "Pesticide Use",
        "fields": ["used_pesticide__c", "pesticide_number_of_times__c", "pesticide_spray_type__c"],
        "image_fields": [],
    },
    # 12. Kitchen garden
    # NOTE: MAP THESE IN BP RESULTS JOB
    # vegetables_planted
    {
        "best_practice_type": "Kitchen Garden",
        "fields": ["is_there_a_kitchen_garden__c"],
        "image_fields": ["photograph_of_kitchen_garden__c"],
    }
]


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _has_value(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str) and v.strip() == "":
        return False
    return True


def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")


def _id_map(conn, table: str) -> Dict[str, str]:
    rows = conn.execute(text(f"SELECT sf_id, id FROM pima.{table} WHERE sf_id IS NOT NULL")).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}


def _bp_header_id_map(conn) -> Dict[str, str]:
    rows = conn.execute(text("SELECT sf_id, id FROM pima.fv_best_practices WHERE sf_id IS NOT NULL")).mappings().all()
    return {r["sf_id"]: r["id"] for r in rows}


def _looks_like_url(s: str) -> bool:
    s = s.strip().lower()
    return s.startswith("http://") or s.startswith("https://")


def _to_bool(v: Any) -> Optional[bool]:
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


def _to_num(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        if s == "":
            return None
        return float(s)
    except Exception:
        return None


def cast_raw_answer(raw_value: Any) -> Dict[str, Any]:
    """
      - answer_boolean if clearly boolean
      - answer_numeric if numeric
      - answer_url if URL
      - else answer_text
    """
    # if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == ""):
    #     return {"answer_text": None, "answer_numeric": None, "answer_boolean": None, "answer_url": None}

    # bool first
    b = _to_bool(raw_value)
    if b is not None:
        return {"answer_text": None, "answer_numeric": None, "answer_boolean": b, "answer_url": None}

    # numeric
    n = _to_num(raw_value)
    if n is not None:
        return {"answer_text": None, "answer_numeric": n, "answer_boolean": None, "answer_url": None}

    s = str(raw_value).strip()

    # url
    if _looks_like_url(s):
        return {"answer_text": None, "answer_numeric": None, "answer_boolean": None, "answer_url": s}

    return {"answer_text": s, "answer_numeric": None, "answer_boolean": None, "answer_url": None}


# ------------------------------------------------------------
# 1) Fetch from Salesforce
# ------------------------------------------------------------
def fetch_sf_rows() -> List[Dict[str, Any]]:
    sf = sf_client()

    select_fields: Set[str] = {
        SF_ID, SF_IS_DELETED, SF_CREATED_AT, SF_UPDATED_AT,
        SF_FARM_VISIT, SF_FARM_VISIT_SUBMISSION_ID,
    }

    for d in BEST_PRACTICE_DEFS:
        for f in d.get("fields", []):
            select_fields.add(f)
        for img in d.get("image_fields", []):
            select_fields.add(img)

    soql = f"""
      SELECT {", ".join(sorted(select_fields))}
      FROM {SF_OBJECT}
      WHERE IsDeleted = false
      ORDER BY CreatedDate DESC
      LIMIT 10000
    """
    return list(query_all(sf, soql))


# ------------------------------------------------------------
# 2) Transform into 3 datasets
# ------------------------------------------------------------
def transform(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns: (headers, answers, images)
    """
    headers: List[Dict[str, Any]] = []
    answers: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []

    for r in rows:
        parent_sf_id = r.get(SF_ID)
        farm_visit_sf_id = r.get(SF_FARM_VISIT)
        base_sub = r.get(SF_FARM_VISIT_SUBMISSION_ID)

        for d in BEST_PRACTICE_DEFS:
            bp_type = d["best_practice_type"]
            fields = d.get("fields", [])
            image_fields = d.get("image_fields", [])

            # Does this practice exist for this SF record?
            has_any = any(_has_value(r.get(f)) for f in fields) or any(_has_value(r.get(img)) for img in image_fields)
            if not has_any:
                continue

            # ---------- Header ----------
            header_sf_id = f"{parent_sf_id}:{bp_type}"
            header_submission_id = f"{base_sub}:{bp_type}"

            headers.append({
                "sf_id": header_sf_id,
                "submission_id": header_submission_id,
                "farm_visit_sf_id": farm_visit_sf_id,
                "best_practice_type": bp_type,

                "is_deleted": bool(r.get(SF_IS_DELETED)),
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
            })

            # ---------- Answers (raw, typed only) ----------
            for sf_field in fields:
                raw_val = r.get(sf_field)
                if not _has_value(raw_val):
                    continue

                question_key = SF_TO_QUESTION_KEY.get(sf_field)
                if not question_key:
                    # fallback that still stays stable
                    question_key = sf_field.replace("__c", "").strip()

                casted = cast_raw_answer(raw_val)

                # Unique per answer
                answers.append({
                    "bp_header_sf_id": header_sf_id,  # to resolve fv_best_practice_id at load time
                    "sf_id": f"{parent_sf_id}:{bp_type}:{question_key}",
                    "submission_id": f"{base_sub}:{bp_type}:{question_key}",
                    "question_key": question_key,

                    **casted,

                    "is_deleted": bool(r.get(SF_IS_DELETED)),
                    "deleted_at": None,
                    "created_at": r.get(SF_CREATED_AT),
                    "updated_at": r.get(SF_UPDATED_AT),
                })

            # ---------- Images ----------
            for img_field in image_fields:
                img_url = r.get(img_field)
                if not _has_value(img_url):
                    continue

                images.append({
                    "bp_header_sf_id": header_sf_id,
                    "submission_id": f"{base_sub}:{bp_type}:{img_field}",
                    "image_url": str(img_url).strip(),
                    "image_description": img_field,
                    "verification_status": None,

                    "is_deleted": bool(r.get(SF_IS_DELETED)),
                    "deleted_at": None,
                    "created_at": r.get(SF_CREATED_AT),
                    "updated_at": r.get(SF_UPDATED_AT),
                })

    return headers, answers, images


# ------------------------------------------------------------
# 3) Load in correct order
# ------------------------------------------------------------
def load(headers: List[Dict[str, Any]], answers: List[Dict[str, Any]], images: List[Dict[str, Any]]):
    """
    Requires:
      - farm_visits (farm_visits.sf_id)
    """
    upsert_headers = "app/sql/fv_best_practices_upsert.sql"
    upsert_answers = "app/sql/fv_best_practice_answers_upsert.sql"
    upsert_images  = "app/sql/training_sessions_images_upsert.sql"

    start = time.time()

    kept_h = kept_a = kept_i = 0
    skipped_h = skipped_a = skipped_i = 0

    with connect() as c:
        # Resolve farm_visit_id using sf_id
        farm_visits_map = _id_map(c, "farm_visits")

        # -----------------------
        # 3.1 Load headers first
        # -----------------------
        print("UPSERTING HEADERS")
        if headers:
            for batch in chunked(headers, 1000):
                params_list = []
                for row in batch:
                    farm_visit_id = farm_visits_map.get(row["farm_visit_sf_id"])
                    if not (farm_visit_id and row.get("submission_id") and row.get("best_practice_type")):
                        print("missing farm_visit_id or submission_id or best_practice_type, skipping this header")
                        print("farm_visit_id from farm_visit_sf_id:", row.get("farm_visit_sf_id"))
                        print("submission_id:", row.get("submission_id"))
                        print("best_practice_type:", row.get("best_practice_type"))
                        skipped_h += 1
                        continue

                    params_list.append({
                        "id": str(uuid4()),
                        "sf_id": row["sf_id"],
                        "submission_id": row["submission_id"],
                        "farm_visit_id": farm_visit_id,
                        "best_practice_type": row["best_practice_type"],
                        "is_bp_verified": False,

                        "is_deleted": row["is_deleted"],
                        "deleted_at": row["deleted_at"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],

                        "system_user": settings.SYSTEM_USER_ID,
                    })

                if params_list:
                    run_sql_many(c, upsert_headers, params_list)
                    kept_h += len(params_list)

        # Build header id map AFTER header upserts
        bp_header_map = _bp_header_id_map(c)  # sf_id -> id

        # -----------------------
        # 3.2 Load answers
        # -----------------------
        print("UPSERTING ANSWERS")
        if answers:
            for batch in chunked(answers, 1000):
                params_list = []
                for row in batch:
                    bp_id = bp_header_map.get(row["bp_header_sf_id"])
                    if not (bp_id and row.get("submission_id") and row.get("question_key")):
                        skipped_a += 1
                        continue

                    params_list.append({
                        "id": str(uuid4()),
                        "sf_id": row["sf_id"],
                        "submission_id": row["submission_id"],
                        "fv_best_practice_id": bp_id,
                        "question_key": row["question_key"],

                        "answer_text": row.get("answer_text"),
                        "answer_numeric": row.get("answer_numeric"),
                        "answer_boolean": row.get("answer_boolean"),
                        "answer_url": row.get("answer_url"),

                        "is_deleted": row["is_deleted"],
                        "deleted_at": row["deleted_at"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],

                        "system_user": settings.SYSTEM_USER_ID,
                    })

                if params_list:
                    run_sql_many(c, upsert_answers, params_list)
                    kept_a += len(params_list)
        # -----------------------
        # 3.3 Load images
        # -----------------------
        print("UPSERTING IMAGES")
        if images:
            for batch in chunked(images, 1000):
                params_list = []
                for row in batch:
                    bp_id = bp_header_map.get(row["bp_header_sf_id"])
                    if not (bp_id and row.get("submission_id") and row.get("image_url")):
                        print("missing bp_id or submission_id or image_url, skipping this image")
                        print("bp_id:", bp_id, "from bp_header_sf_id:", row.get("bp_header_sf_id"))
                        print("submission_id:", row.get("submission_id"))
                        print("image_url:", row.get("image_url"))
                        skipped_i += 1
                        continue

                    params_list.append({
                        "id": str(uuid4()),
                        "image_reference_type": "fv_best_practice",
                        "image_reference_id": bp_id,
                        "image_url": row["image_url"],
                        "verification_status": row.get("verification_status"),
                        "submission_id": row["submission_id"],
                        "image_description": row.get("image_description"),

                        "is_deleted": row.get("is_deleted", False),
                        "deleted_at": row.get("deleted_at"),
                        "created_at": row.get("created_at"),
                        "updated_at": row.get("updated_at"),

                        "system_user": settings.SYSTEM_USER_ID,
                    })

                if params_list:
                    run_sql_many(c, upsert_images, params_list)
                    kept_i += len(params_list)

    elapsed = _fmt_eta(time.time() - start)
    print(
        f"[fv_best_practices_all] Done in {elapsed}. "
        f"headers kept {kept_h:,} skipped {skipped_h:,} | "
        f"answers kept {kept_a:,} skipped {skipped_a:,} | "
        f"images kept {kept_i:,} skipped {skipped_i:,}"
    )

    done = kept_h + kept_a + kept_i
    skipped = skipped_h + skipped_a + skipped_i

    return done, skipped


def run(project_filter: Optional[str] = None) -> dict:
    print("Starting FV Best Practices (headers + answers + images) migration…")
    rows = fetch_sf_rows()
    print(f"Fetched {len(rows)} rows from Salesforce {SF_OBJECT}.")
    headers, answers, images = transform(rows)
    print(f"Transform produced: headers={len(headers):,}, answers={len(answers):,}, images={len(images):,}")
    loaded, skipped = load(headers, answers, images)
    print(f"Loaded {loaded} training sessions, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}