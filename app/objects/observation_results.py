import time
from uuid import uuid4
from typing import List, Dict, Any, Optional

from psycopg2.extras import execute_values
from sqlalchemy import text
import os
import json

from ..sf import sf_client, query_all
from ..db import connect, run_sql_many
from ..config import settings
from ..utils import chunked, first_value

SF_OBJECT = "Observation_Result__c"

# Salesforce fields
SF_ID = "Id"
SF_IS_DELETED = "IsDeleted"
SF_CREATED_AT = "CreatedDate"
SF_UPDATED_AT = "LastModifiedDate"
SF_SUBMISSION_ID = "Submission_ID__c"
SF_OBSERVATION = "Observation__c"
SF_OBSERVATION_CRITERION = "Observation_Criterion__r.Name"
SF_PARTICIPANT_SEX = "Participant_Sex__c"   
SF_RECORDTYPE = "RecordType.Name"
SF_RESULT = "Result__c"
SF_RESULT_NUMBER = "Result_Number__c"
SF_RESULT_TEXT = "Result_Text__c"
SF_RESULT_TEXT_TWO = "Result_Text_Two__c"
SF_SCORE = "Score__c"
SF_COMMENTS = "Comments__c"

def fetch_sf_observations() -> List[Dict[str, Any]]:
    sf = sf_client()
    soql = f"""
      SELECT {SF_ID},
             {SF_IS_DELETED},
             {SF_CREATED_AT},
             {SF_UPDATED_AT},
             {SF_SUBMISSION_ID},
             {SF_OBSERVATION},
            {SF_OBSERVATION_CRITERION},
            {SF_PARTICIPANT_SEX},
            {SF_RECORDTYPE},
            {SF_RESULT},
            {SF_RESULT_NUMBER},
            {SF_RESULT_TEXT},
            {SF_RESULT_TEXT_TWO},
            {SF_SCORE},
            {SF_COMMENTS}
      FROM {SF_OBJECT}
        WHERE Observation__r.Training_Group__r.Project__r.Project_Status__c = 'Inactive'
    """
    return list(query_all(sf, soql))

def transform(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for r in rows:

        CRITERION = r.get(SF_OBSERVATION_CRITERION.split(".")[0]).get(SF_OBSERVATION_CRITERION.split(".")[-1])
        RECORDTYPE = r.get(SF_RECORDTYPE.split(".")[0]).get(SF_RECORDTYPE.split(".")[-1])
        # First append for TO results
        if r.get(SF_RESULT):
            out.append({
                "sf_id": r.get(SF_ID),
                "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
                "submission_id": r.get(SF_SUBMISSION_ID),
                "observation_sf_id": r.get(SF_OBSERVATION),
                "observation_criterion": CRITERION,
                "record_type": RECORDTYPE,
                "result": r.get(SF_RESULT),
            })

        # Second append for TO gender
        if r.get(SF_PARTICIPANT_SEX):
            out.append({
                "sf_id": r.get(SF_ID),
                "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
                "submission_id": r.get(SF_SUBMISSION_ID),
                "observation_sf_id": r.get(SF_OBSERVATION),
                "observation_criterion": CRITERION,
                "record_type": RECORDTYPE,
                "participant_sex": r.get(SF_PARTICIPANT_SEX),
            })

        # Third append for TO/DPO Comments
        if r.get(SF_COMMENTS):
            out.append({
                "sf_id": r.get(SF_ID),
                "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
                "submission_id": r.get(SF_SUBMISSION_ID),
                "observation_sf_id": r.get(SF_OBSERVATION),
                "observation_criterion": CRITERION,
                "record_type": RECORDTYPE,
                "comments": r.get(SF_COMMENTS)
            })
        
        # Fourth Append for Result Number (Number of suckers)
        if r.get(SF_RESULT_NUMBER) and r.get(SF_RESULT):
            out.append({
                "sf_id": r.get(SF_ID),
                "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
                "submission_id": r.get(SF_SUBMISSION_ID),
                "observation_sf_id": r.get(SF_OBSERVATION),
                "observation_criterion": CRITERION,
                "record_type": RECORDTYPE,
                "result_number": r.get(SF_RESULT_NUMBER)
            })

        # Fifth append for result text
        if r.get(SF_RESULT_TEXT):
            out.append({
                "sf_id": r.get(SF_ID),
                "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
                "submission_id": r.get(SF_SUBMISSION_ID),
                "observation_sf_id": r.get(SF_OBSERVATION),
                "observation_criterion": CRITERION,
                "record_type": RECORDTYPE,
                "result_text": r.get(SF_RESULT_TEXT)
            })

        # Sixth append for result text two
        if r.get(SF_RESULT_TEXT_TWO):
            out.append({
                "sf_id": r.get(SF_ID),
                "is_deleted": bool(r.get(SF_IS_DELETED)) if r.get(SF_IS_DELETED) is not None else False,
                "deleted_at": None,
                "created_at": r.get(SF_CREATED_AT),
                "updated_at": r.get(SF_UPDATED_AT),
                "submission_id": r.get(SF_SUBMISSION_ID),
                "observation_sf_id": r.get(SF_OBSERVATION),
                "observation_criterion": CRITERION,
                "record_type": RECORDTYPE,
                "result_text_two": r.get(SF_RESULT_TEXT_TWO)
            })
    # print(f"This is the dictionary: {str(out)}")

    # input("Please press enter to continue. . .")

    return out

def _extract_clean_data(raw_data: dict) -> dict:
    
    # For participant
    participant_str = {
        "p1": "Participant_One_Feedback",
        "p2": "Participant_Two_Feedback",
        "p3": "Participant_Three_Feedback"
    }

    if not raw_data:
        return {}
    
    main_uuid_str = raw_data["submission_id"][:36]

    # 1. Handle participant feedback - Results
    if raw_data["record_type"] == "Participant Feedback" and raw_data.get("result") not in [None, ""]:
        ext_str = raw_data["submission_id"][-2:]
        criterion_str = raw_data["observation_criterion"].title().replace(" ", "_")
        final_dict = {
            "submission_id": f"{main_uuid_str}-{participant_str.get(ext_str)}_{criterion_str}",
            "criterion": "Participant Feedback",
            "question_key": criterion_str,
            "result_text": raw_data["result"]
        }
        return final_dict
    
    # 2. Handle participant feedback - Comments
    if raw_data["record_type"] == "Participant Feedback" and raw_data.get("comments") not in [None, ""]:
        ext_str = raw_data["submission_id"][-2:]
        criterion_str = "participant_comments"
        final_dict = {
            "submission_id": f"{main_uuid_str}-{participant_str.get(ext_str)}_{criterion_str}",
            "criterion": "Participant Feedback",
            "question_key": criterion_str,
            "result_text": raw_data["comments"]
        }
        return final_dict
    
    # 3. Handle participant feedback - Participant Gender
    if raw_data["record_type"] == "Participant Feedback" and raw_data.get("participant_sex") not in [None, ""]:
        ext_str = raw_data["submission_id"][-2:]
        criterion_str = "Participant_Gender"
        final_dict = {
            "submission_id": f"{main_uuid_str}-{participant_str.get(ext_str)}_{criterion_str}",
            "criterion": "Participant Feedback",
            "question_key": criterion_str,
            "result_text": raw_data["participant_sex"]
        }
        return final_dict
    
    # 4. Handle Observer feedback - Results
    if raw_data["record_type"] == "Training Observation" and raw_data.get("result") not in [None, ""]:
        criterion_str = raw_data["observation_criterion"].replace(" ", "_")
        final_dict = {
            "submission_id": f"{main_uuid_str}-{criterion_str}",
            "criterion": "Observer Feedback",
            "question_key": criterion_str,
            "result_text": raw_data["result"]
        }
        return final_dict
    
    # 5. Handle DPO results | Level 1 result
    if raw_data["record_type"] == "Demo Plot Observation" and raw_data.get("result") not in [None, ""]:
        # 5.1. Compost Heap
        if raw_data["observation_criterion"] == "Compost Heap":
            criterion_str = "present_compost_heap"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Compost Heap",
                "question_key": criterion_str,
                "result_text": raw_data["result"].replace("_", " ").replace("Yes compost", "Yes, compost")
            }
            return final_dict
        # 5.2. Mulch
        if raw_data["observation_criterion"] in ["Mulch", "Mulching"]:
            criterion_str = "mulch_under_the_canopy"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Mulch",
                "question_key": criterion_str,
                "result_text": raw_data["result"].replace("_", " ").replace("Yes Some", "Yes, Some")
            }
            return final_dict
        # 5.3. Shade Management
        if raw_data["observation_criterion"] == "Shade Management":
            criterion_str = "level_of_shade_present"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Shade Management",
                "question_key": criterion_str,
                "result_text": raw_data["result"].replace("_", " ")
            }
            return final_dict
        # 5.4. Vetiver Planted
        if raw_data["observation_criterion"] == "Vetiver Planted":
            criterion_str = "vetiver_planted"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Vetiver Planted",
                "question_key": criterion_str,
                "result_text": raw_data["result"].replace("_", " ").replace("Yes Row", "Yes. Row").replace("No Vetiver", "No. Vetiver")
            }
            return final_dict
        # 5.5. Weed Management
        if raw_data["observation_criterion"] == "Weed Management":
            criterion_str = "has_the_demo_plot_been_dug"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Weed Management",
                "question_key": criterion_str,
                "result_text": raw_data["result"].replace("_", " ").replace("Yes field", "Yes, field")
            }
            return final_dict
        # 5.6. Rejuvenation
        if raw_data["observation_criterion"] == "Rejuvenation":
            criterion_str = "rejuvenation_plot"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Rejuvenation",
                "question_key": criterion_str,
                "result_text": raw_data["result"]
            }
            return final_dict
        # 5.7. Sucker Selection
        if raw_data["observation_criterion"] == "Sucker Selection":
            criterion_str = "Sucker_Selection_Taken_Place"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Sucker Selection",
                "question_key": criterion_str,
                "result_text": raw_data["result"]
                                .replace("_", " ")
                                .replace("No Many", "No, Many")
                                .replace("Yes Sucker", "Yes. Sucker")
                                .replace("No. Sucker selection has not been done", "No, Many suckers")
                                .replace("is complete", "completed")
            }
            return final_dict
        # 5.8. Stumped Trees
        if raw_data["observation_criterion"] == "Stumped Trees":
            criterion_str = "stumped_trees"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Stumped Trees",
                "question_key": criterion_str,
                "result_text": raw_data["result"].replace("_", " ").replace("Yes demo", "Yes, demo")
            }
            return final_dict
        # 5.9. Pruning
        if raw_data["observation_criterion"] == "Pruning":
            criterion_str = "pruning_methods"
            ext_str = raw_data["submission_id"][-1:]
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}-{ext_str}",
                "criterion": "Pruning",
                "question_key": criterion_str,
                "result_text": raw_data["result"]
            }
            return final_dict
        # 5.10. Cover Crop
        if raw_data["observation_criterion"] == "Covercrop":
            criterion_str = "covercrop_present"
            ext_str = raw_data["submission_id"][-1:]
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}-{ext_str}",
                "criterion": "Covercrop Planted",
                "question_key": criterion_str,
                "result_text": raw_data["result"]
            }
            return final_dict
    # 6. Handler for number of suckers
    if raw_data["record_type"] == "Demo Plot Observation" and raw_data.get("result_number") not in [None, ""]:
        criterion_str = "number_of_suckers"
        final_dict = {
            "submission_id": f"{main_uuid_str}-{criterion_str}",
            "criterion": "Sucker Selection",
            "question_key": criterion_str,
            "result_numeric": int(raw_data["result_number"])
        }
        return final_dict
    
    # 7. Handler for Result Text
    if raw_data["record_type"] == "Demo Plot Observation" and raw_data.get("result_text") not in [None, ""]:
        # 7.1. Mulch - Thickness
        if raw_data["observation_criterion"] in ["Mulch", "Mulching"]:    
            criterion_str = "thickness_of_mulch"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Mulch",
                "question_key": criterion_str,
                "result_text": raw_data["result_text"].replace("_", " ").replace("mulch.", "mulch")
            }
            return final_dict
        # 7.2. Shade management - Shade trees planted
        if raw_data["observation_criterion"] == "Shade Management":    
            criterion_str = "shade_trees_planted"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Mulch",
                "question_key": criterion_str,
                "result_text": raw_data["result_text"]
            }
            return final_dict
        # 7.3 Weed Management
        if raw_data["observation_criterion"] == "Weed Management":    
            criterion_str = "how_big_are_the_weeds"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Weed Management",
                "question_key": criterion_str,
                "result_text": raw_data["result_text"]
            }
            return final_dict
        # 7.4 Rejuvenation
        if raw_data["observation_criterion"] == "Rejuvenation":    
            criterion_str = "suckers_three"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Rejuvenation",
                "question_key": criterion_str,
                "result_text": raw_data["result_text"]
            }
            return final_dict
    
    # 8. Handler for Result Text Two
    if raw_data["record_type"] == "Demo Plot Observation" and raw_data.get("result_text_two") not in [None, ""]:
        # 8.1. Weed Management
        if raw_data["observation_criterion"] == "Weed Management":    
            criterion_str = "how_many_weeds_are_under_the_tree_canopy"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Weed Management",
                "question_key": criterion_str,
                "result_text": raw_data["result_text_two"].replace("_", " ")
            }
            return final_dict
        # 8.2. Shade management - Row of bananas
        if raw_data["observation_criterion"] == "Shade Management":    
            criterion_str = "banana_intercrop"
            final_dict = {
                "submission_id": f"{main_uuid_str}-{criterion_str}",
                "criterion": "Shade Management",
                "question_key": criterion_str,
                "result_text": raw_data["result_text_two"]
            }
            return final_dict
    
    # 9. Handle Observer feedback - Comments
    if raw_data["record_type"] == "Training Observation" and raw_data.get("comments") not in [None, ""]:
        criterion_str = f'{raw_data["observation_criterion"].replace(" ", "_")}_Comments'
        final_dict = {
            "submission_id": f"{main_uuid_str}-{criterion_str}",
            "criterion": "Observer Feedback",
            "question_key": criterion_str,
            "result_text": raw_data["comments"]
        }
        return final_dict

def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    start = time.time()
    skipped = 0
    skipped_ids = []

    if not transformed:
        print("[observation_results] No rows to load.")
        return 0, 0

    with connect() as c:
        # Preload FK map once
        _obs_map = {
            row[0]: row[1]
            for row in c.execute(
                text("SELECT sf_id, id FROM pima.observations WHERE sf_id IS NOT NULL")
            ).fetchall()
        }

        deduped = {}

        for row in transformed:
            observation_id = _obs_map.get(row["observation_sf_id"])
            cleaned = _extract_clean_data(row)

            if not cleaned or not row.get("sf_id") or not observation_id:
                skipped += 1
                skipped_ids.append(row.get("sf_id"))
                continue

            submission_id = cleaned["submission_id"]

            record_tuple = (
                str(uuid4()),
                submission_id,
                observation_id,
                cleaned.get("criterion"),
                cleaned.get("question_key"),
                cleaned.get("result_text"),
                cleaned.get("result_numeric"),
                None,  # result_boolean
                None,  # result_url
                row["created_at"],
                row["updated_at"],
                settings.SYSTEM_USER_ID,
                settings.SYSTEM_USER_ID,
                True,
                row["sf_id"],
                row["is_deleted"],
                row["deleted_at"],
            )

            existing = deduped.get(submission_id)

            # If duplicate exists, keep newest updated_at
            if not existing or row["updated_at"] > existing[10]:
                deduped[submission_id] = record_tuple

        values = list(deduped.values())
        total_kept = len(values)

        if not values:
            print("[observation_results] Nothing to insert after dedupe.")
            return 0, skipped

        cursor = c.connection.cursor()

        # -------------------------------------------------
        # Create temp staging table
        # -------------------------------------------------
        cursor.execute("""
            CREATE TEMP TABLE tmp_observation_results
            (LIKE pima.observation_results INCLUDING ALL)
            ON COMMIT DROP;
        """)

        # -------------------------------------------------
        # Bulk insert into temp table
        # -------------------------------------------------
        execute_values(
            cursor,
            """
            INSERT INTO tmp_observation_results (
                id, submission_id, observation_id, criterion, question_key,
                result_text, result_numeric, result_boolean, result_url,
                created_at, updated_at, created_by_id, last_updated_by_id,
                from_sf, sf_id, is_deleted, deleted_at
            ) VALUES %s
            """,
            values,
            page_size=10000,
        )

        # -------------------------------------------------
        # Single set-based upsert
        # -------------------------------------------------
        cursor.execute("""
            INSERT INTO pima.observation_results AS t
            SELECT * FROM tmp_observation_results
            ON CONFLICT (submission_id)
            DO UPDATE SET
                observation_id = EXCLUDED.observation_id,
                criterion = EXCLUDED.criterion,
                question_key = EXCLUDED.question_key,
                result_text = EXCLUDED.result_text,
                result_numeric = EXCLUDED.result_numeric,
                result_boolean = EXCLUDED.result_boolean,
                result_url = EXCLUDED.result_url,
                updated_at = EXCLUDED.updated_at,
                last_updated_by_id = EXCLUDED.last_updated_by_id,
                from_sf = TRUE,
                sf_id = EXCLUDED.sf_id,
                is_deleted = EXCLUDED.is_deleted,
                deleted_at = EXCLUDED.deleted_at
            WHERE t.updated_at IS DISTINCT FROM EXCLUDED.updated_at;
        """)

        c.commit()

    # -------------------------------------------------
    # Final reporting
    # -------------------------------------------------
    elapsed = time.time() - start
    rps = total_kept / elapsed if elapsed else 0

    with open("skipped_ids_inactive.json", "w") as f:
        json.dump(skipped_ids, f)

    print(
        f"[observation_results] Completed. "
        f"Kept {total_kept:,}, skipped {skipped:,} "
        f"in {_fmt_eta(elapsed)} | {rps:,.0f} rows/sec"
    )

    return total_kept, skipped


def _fmt_eta(s: float) -> str:
    if not s or s != s:
        return "0s"
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {sec}s" if h else (f"{m}m {sec}s" if m else f"{sec}s")



# def load(transformed: List[Dict[str, Any]]) -> tuple[int, int]:
    # done = 0
    # skipped = 0
    # upsert = "app/sql/observation_results_upsert.sql"

    # skipped_ids = []

    # total = len(transformed)
    # start = time.time()
    # if total == 0:
    #     print("[observation_results] No rows to load.")
    #     return 0, 0

    # with connect() as c:
    #     _obs_map = {row[0]: row[1] for row in c.execute(
    #         text("SELECT sf_id, id FROM pima.observations WHERE sf_id IS NOT NULL")
    #     ).fetchall()}
    #     for batch in chunked(transformed, 5000):
    #         params_list = []

    #         for row in batch:
    #             # Resolve foreign keys
    #             observation_id = _obs_map.get(row["observation_sf_id"])

    #             # Get cleaned data
    #             cleaned_data = _extract_clean_data(row)

    #             # print(f"This is the cleaned data: {str(cleaned_data)}")

    #             # input("Press enter to continue. . .")

    #             # Required fields in Postgres observation_results
    #             if not all([row["sf_id"], observation_id]):
    #                 skipped += 1
    #                 skipped_ids.append(row["sf_id"])
    #                 continue
                
    #             init_dict = {
    #                 "id": str(uuid4()),
    #                 "sf_id": row["sf_id"],
    #                 "is_deleted": row["is_deleted"],
    #                 "deleted_at": row["deleted_at"],
    #                 "observation_id": observation_id,
    #                 "created_at": row["created_at"],
    #                 "updated_at": row["updated_at"],
    #                 "system_user": settings.SYSTEM_USER_ID,
    #                 "result_text": None,
    #                 "result_numeric": None,
    #                 "result_url": None,
    #                 "result_boolean": None,
    #             }

    #             # print(f"This is the first dictionary: {str(init_dict)}")

    #             # input("Press enter to continue. . .")

    #             init_dict.update(cleaned_data)

    #             # print(f"This is the second dictionary: {str(init_dict)}")

    #             # input("Press enter to continue. . .")

    #             params_list.append(init_dict)

    #         # print(f"Params List: {str(params_list)}")

    #         # input("Press enter to continue. . .")

    #         if params_list:
    #             run_sql_many(c, upsert, params_list)
    #             done += len(params_list)

    #         # progress
    #         processed = done + skipped
    #         elapsed = time.time() - start
    #         rps = processed / elapsed if elapsed > 0 else 0.0
    #         eta = (total - processed) / rps if rps > 0 else 0.0
    #         pct = (processed / total) * 100
    #         print(
    #             f"[observation_results] {processed:,}/{total:,} ({pct:5.1f}%) | kept {done:,} | skipped {skipped:,} "
    #             f"| {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
    #             flush=True
    #         )

    # # Export Skipped IDs
    # with open('skipped_ids.json', 'w') as f:
    #     json.dump(skipped_ids,f)

    # print(f"[observation_results] Completed. Kept {done:,}, skipped {skipped:,} in {_fmt_eta(time.time()-start)}.")
    # return done, skipped

def run(project_filter: str | None = None) -> dict:
    print("Starting observation results migration…")
    rows = fetch_sf_observations()
    print(f"Fetched {len(rows)} observation results from Salesforce.")
    tfm = transform(rows)
    loaded, skipped = load(tfm)
    print(f"Loaded {loaded} observation results, skipped {skipped}.")
    return {"rows_in": len(rows), "rows_loaded": loaded, "rows_skipped": skipped}
