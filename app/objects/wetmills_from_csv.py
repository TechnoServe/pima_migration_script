import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import pandas as pd
from sqlalchemy import text

from ..config import settings
from ..db import connect


BASE_DIR = Path(__file__).resolve().parents[2]
FILES_DIR = BASE_DIR / "files"

WETMILLS_CSV = FILES_DIR / "wetmills.csv"
WETMILL_VISITS_CSV = FILES_DIR / "wetmill_visits.csv"
SURVEY_RESPONSES_CSV = FILES_DIR / "survey_responses.csv"
SURVEY_QUESTION_RESPONSES_CSV = FILES_DIR / "survey_question_responses.csv"
LEGACY_USERS_CSV = FILES_DIR / "tbl_users.csv"


WETMILL_INSERT_SQL = text("""
INSERT INTO pima.wetmills (
    id,
    user_id,
    wet_mill_unique_id,
    commcare_case_id,
    name,
    mill_status,
    exporting_status,
    programme,
    country,
    manager_name,
    manager_role,
    comments,
    wetmill_counter,
    ba_signature,
    manager_signature,
    tor_page_picture,
    registration_date,
    office_entrance_picture,
    office_gps,
    created_at,
    updated_at,
    is_deleted,
    deleted_at,
    created_by_id,
    last_updated_by_id
) VALUES (
    :id,
    :user_id,
    :wet_mill_unique_id,
    :commcare_case_id,
    :name,
    :mill_status,
    :exporting_status,
    :programme,
    :country,
    :manager_name,
    :manager_role,
    :comments,
    :wetmill_counter,
    :ba_signature,
    :manager_signature,
    :tor_page_picture,
    :registration_date,
    :office_entrance_picture,
    CASE
        WHEN :office_gps_hex IS NULL THEN NULL
        ELSE ST_GeomFromEWKB(decode(:office_gps_hex, 'hex'))
    END,
    :created_at,
    :updated_at,
    :is_deleted,
    NULL,
    :created_by_id,
    :last_updated_by_id
)
""")

WETMILL_UPDATE_SQL = text("""
UPDATE pima.wetmills
SET
    user_id = :user_id,
    wet_mill_unique_id = :wet_mill_unique_id,
    commcare_case_id = :commcare_case_id,
    name = :name,
    mill_status = :mill_status,
    exporting_status = :exporting_status,
    programme = :programme,
    country = :country,
    manager_name = :manager_name,
    manager_role = :manager_role,
    comments = :comments,
    wetmill_counter = :wetmill_counter,
    ba_signature = :ba_signature,
    manager_signature = :manager_signature,
    tor_page_picture = :tor_page_picture,
    registration_date = :registration_date,
    office_entrance_picture = :office_entrance_picture,
    office_gps = CASE
        WHEN :office_gps_hex IS NULL THEN office_gps
        ELSE ST_GeomFromEWKB(decode(:office_gps_hex, 'hex'))
    END,
    updated_at = :updated_at,
    is_deleted = :is_deleted,
    last_updated_by_id = :last_updated_by_id
WHERE id = :id
""")

WETMILL_VISIT_INSERT_SQL = text("""
INSERT INTO pima.wetmill_visits (
    id,
    wetmill_id,
    user_id,
    form_name,
    visit_date,
    entrance_photograph,
    geo_location,
    submission_id,
    created_at,
    updated_at,
    is_deleted,
    deleted_at,
    created_by_id,
    last_updated_by_id
) VALUES (
    :id,
    :wetmill_id,
    :user_id,
    :form_name,
    :visit_date,
    :entrance_photograph,
    CASE
        WHEN :geo_location_hex IS NULL THEN NULL
        ELSE ST_GeomFromEWKB(decode(:geo_location_hex, 'hex'))
    END,
    :submission_id,
    :created_at,
    :updated_at,
    false,
    NULL,
    :created_by_id,
    :last_updated_by_id
)
""")

WETMILL_VISIT_UPDATE_SQL = text("""
UPDATE pima.wetmill_visits
SET
    wetmill_id = :wetmill_id,
    user_id = :user_id,
    form_name = :form_name,
    visit_date = :visit_date,
    entrance_photograph = :entrance_photograph,
    geo_location = CASE
        WHEN :geo_location_hex IS NULL THEN geo_location
        ELSE ST_GeomFromEWKB(decode(:geo_location_hex, 'hex'))
    END,
    updated_at = :updated_at,
    last_updated_by_id = :last_updated_by_id
WHERE id = :id
""")

SURVEY_RESPONSE_INSERT_SQL = text("""
INSERT INTO pima.wv_survey_responses (
    id,
    form_visit_id,
    survey_type,
    completed_date,
    general_feedback,
    submission_id,
    created_at,
    updated_at,
    is_deleted,
    deleted_at,
    created_by_id,
    last_updated_by_id
) VALUES (
    :id,
    :form_visit_id,
    :survey_type,
    :completed_date,
    :general_feedback,
    :submission_id,
    :created_at,
    :updated_at,
    false,
    NULL,
    :created_by_id,
    :last_updated_by_id
)
""")

SURVEY_RESPONSE_UPDATE_SQL = text("""
UPDATE pima.wv_survey_responses
SET
    form_visit_id = :form_visit_id,
    survey_type = :survey_type,
    completed_date = :completed_date,
    general_feedback = :general_feedback,
    updated_at = :updated_at,
    last_updated_by_id = :last_updated_by_id
WHERE id = :id
""")

SURVEY_QUESTION_INSERT_SQL = text("""
INSERT INTO pima.wv_survey_question_responses (
    id,
    survey_response_id,
    section_name,
    question_name,
    field_type,
    submission_id,
    value_text,
    value_number,
    value_boolean,
    value_date,
    value_gps,
    created_at,
    updated_at,
    is_deleted,
    deleted_at,
    created_by_id,
    last_updated_by_id
) VALUES (
    :id,
    :survey_response_id,
    :section_name,
    :question_name,
    :field_type,
    :submission_id,
    :value_text,
    :value_number,
    :value_boolean,
    :value_date,
    CASE
        WHEN :value_gps_hex IS NULL THEN NULL
        ELSE ST_GeomFromEWKB(decode(:value_gps_hex, 'hex'))
    END,
    :created_at,
    :updated_at,
    false,
    NULL,
    :created_by_id,
    :last_updated_by_id
)
""")

SURVEY_QUESTION_UPDATE_SQL = text("""
UPDATE pima.wv_survey_question_responses
SET
    survey_response_id = :survey_response_id,
    section_name = :section_name,
    question_name = :question_name,
    field_type = :field_type,
    value_text = :value_text,
    value_number = :value_number,
    value_boolean = :value_boolean,
    value_date = :value_date,
    value_gps = CASE
        WHEN :value_gps_hex IS NULL THEN value_gps
        ELSE ST_GeomFromEWKB(decode(:value_gps_hex, 'hex'))
    END,
    updated_at = :updated_at,
    last_updated_by_id = :last_updated_by_id
WHERE id = :id
""")


def _require_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required CSV not found: {path}")
    return path


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _clean(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() in {"null", "none", "nan", "nil"}:
        return None
    return s


def _coerce_bool(value: Any) -> bool:
    s = str(value or "").strip().lower()
    return s in {"true", "1", "t", "yes", "y"}


def _coerce_int(value: Any) -> Optional[int]:
    v = _clean(value)
    if v is None:
        return None
    try:
        return int(float(v))
    except Exception:
        return None


def _coerce_float(value: Any) -> Optional[float]:
    v = _clean(value)
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _coerce_date(value: Any):
    v = _clean(value)
    if v is None:
        return None
    ts = pd.to_datetime(v, utc=False, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.date()


def _coerce_datetime(value: Any):
    v = _clean(value)
    if v is None:
        return None
    ts = pd.to_datetime(v, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.to_pydatetime()


def _coerce_naive_datetime(value: Any):
    v = _clean(value)
    if v is None:
        return None
    ts = pd.to_datetime(v, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    dt = ts.to_pydatetime()
    return dt.replace(tzinfo=None)


def _fmt_eta(seconds: float) -> str:
    if not seconds or seconds != seconds or seconds < 0:
        return "0s"
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {sec}s"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def _build_existing_map(conn, table: str, key_col: str) -> Dict[str, str]:
    rows = conn.execute(
        text(f"SELECT id, {key_col} FROM pima.{table} WHERE {key_col} IS NOT NULL")
    ).mappings().all()
    out = {}
    for row in rows:
        key = _clean(row[key_col])
        if key and key not in out:
            out[key] = str(row["id"])
    return out


def _fetch_new_users(conn) -> Dict[str, Dict[str, str]]:
    rows = conn.execute(
        text("""
            SELECT id, sf_id, email, username
            FROM pima.users
        """)
    ).mappings().all()

    by_sf_id = {}
    by_email = {}
    by_username = {}
    by_id = {}

    for row in rows:
        user_id = str(row["id"])
        by_id[user_id] = user_id

        sf_id = _clean(row["sf_id"])
        if sf_id:
            by_sf_id[sf_id] = user_id

        email = _clean(row["email"])
        if email:
            by_email[email.lower()] = user_id

        username = _clean(row["username"])
        if username:
            by_username[username.lower()] = user_id

    return {
        "by_id": by_id,
        "by_sf_id": by_sf_id,
        "by_email": by_email,
        "by_username": by_username,
    }


def _resolve_user_id(
    legacy_user_id: Any,
    legacy_user_lookup: Dict[str, Dict[str, Optional[str]]],
    new_users_lookup: Dict[str, Dict[str, str]],
    default_user_id: str,
) -> Optional[str]:
    old_id = _clean(legacy_user_id)
    if old_id is None:
        return default_user_id

    if old_id in new_users_lookup["by_id"]:
        return new_users_lookup["by_id"][old_id]

    legacy = legacy_user_lookup.get(old_id)
    if legacy is None:
        return default_user_id

    sf_id = _clean(legacy.get("sf_user_id"))
    if sf_id and sf_id in new_users_lookup["by_sf_id"]:
        return new_users_lookup["by_sf_id"][sf_id]

    email = _clean(legacy.get("user_email"))
    if email and email.lower() in new_users_lookup["by_email"]:
        return new_users_lookup["by_email"][email.lower()]

    username = _clean(legacy.get("username"))
    if username and username.lower() in new_users_lookup["by_username"]:
        return new_users_lookup["by_username"][username.lower()]

    return default_user_id


def fetch_csv_inputs() -> Dict[str, pd.DataFrame]:
    return {
        "wetmills": _read_csv(_require_file(WETMILLS_CSV)),
        "wetmill_visits": _read_csv(_require_file(WETMILL_VISITS_CSV)),
        "survey_responses": _read_csv(_require_file(SURVEY_RESPONSES_CSV)),
        "survey_question_responses": _read_csv(_require_file(SURVEY_QUESTION_RESPONSES_CSV)),
        "legacy_users": _read_csv(_require_file(LEGACY_USERS_CSV)),
    }


def transform(inputs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    wetmills_df = inputs["wetmills"].copy()
    wetmill_visits_df = inputs["wetmill_visits"].copy()
    survey_responses_df = inputs["survey_responses"].copy()
    survey_question_responses_df = inputs["survey_question_responses"].copy()
    legacy_users_df = inputs["legacy_users"].copy()

    legacy_user_lookup = {}
    for _, row in legacy_users_df.iterrows():
        old_user_id = _clean(row.get("user_id"))
        if not old_user_id:
            continue
        email = _clean(row.get("user_email"))
        username = email.split("@")[0].lower() if email else None
        legacy_user_lookup[old_user_id] = {
            "sf_user_id": _clean(row.get("sf_user_id")),
            "user_email": email,
            "username": username,
        }

    wetmills_out = []
    for _, row in wetmills_df.iterrows():
        wetmills_out.append({
            "old_id": _clean(row.get("id")),
            "wet_mill_unique_id": _clean(row.get("wet_mill_unique_id")),
            "commcare_case_id": _clean(row.get("commcare_case_id")),
            "name": _clean(row.get("name")),
            "mill_status": _clean(row.get("mill_status")),
            "exporting_status": _clean(row.get("exporting_status")),
            "programme": _clean(row.get("programme")),
            "country": _clean(row.get("country")),
            "manager_name": _clean(row.get("manager_name")),
            "manager_role": _clean(row.get("manager_role")),
            "comments": _clean(row.get("comments")),
            "wetmill_counter": _coerce_int(row.get("wetmill_counter")),
            "ba_signature": _clean(row.get("ba_signature")),
            "manager_signature": _clean(row.get("manager_signature")),
            "tor_page_picture": _clean(row.get("tor_page_picture")),
            "registration_date": _coerce_date(row.get("registration_date")),
            "office_entrance_picture": _clean(row.get("office_entrance_picture")),
            "office_gps_hex": _clean(row.get("office_gps")),
            "created_at": _coerce_datetime(row.get("created_at")),
            "updated_at": _coerce_datetime(row.get("updated_at")),
            "user_id_old": _clean(row.get("user_id")),
            "is_deleted": _coerce_bool(row.get("is_deleted")),
        })

    wetmill_visits_out = []
    for _, row in wetmill_visits_df.iterrows():
        wetmill_visits_out.append({
            "old_id": _clean(row.get("id")),
            "wetmill_id_old": _clean(row.get("wetmill_id")),
            "user_id_old": _clean(row.get("user_id")),
            "form_name": _clean(row.get("form_name")),
            "visit_date": _coerce_date(row.get("visit_date")),
            "entrance_photograph": _clean(row.get("entrance_photograph")),
            "geo_location_hex": _clean(row.get("geo_location")),
            "created_at": _coerce_datetime(row.get("created_at")),
            "updated_at": _coerce_datetime(row.get("updated_at")),
            "submission_id": _clean(row.get("submission_id")),
            "mill_external_id": _clean(row.get("mill_external_id")),
        })

    survey_responses_out = []
    for _, row in survey_responses_df.iterrows():
        survey_responses_out.append({
            "old_id": _clean(row.get("id")),
            "form_visit_id_old": _clean(row.get("form_visit_id")),
            "survey_type": _clean(row.get("survey_type")),
            "completed_date": _coerce_date(row.get("completed_date")),
            "general_feedback": _clean(row.get("general_feedback")),
            "created_at": _coerce_datetime(row.get("created_at")),
            "updated_at": _coerce_datetime(row.get("updated_at")),
            "submission_id": _clean(row.get("submission_id")),
        })

    survey_question_responses_out = []
    for _, row in survey_question_responses_df.iterrows():
        survey_question_responses_out.append({
            "old_id": _clean(row.get("id")),
            "survey_response_id_old": _clean(row.get("survey_response_id")),
            "section_name": _clean(row.get("section_name")),
            "question_name": _clean(row.get("question_name")),
            "field_type": _clean(row.get("field_type")),
            "value_text": _clean(row.get("value_text")),
            "value_number": _coerce_float(row.get("value_number")),
            "value_boolean": None if _clean(row.get("value_boolean")) is None else _coerce_bool(row.get("value_boolean")),
            "value_date": _coerce_naive_datetime(row.get("value_date")),
            "value_gps_hex": _clean(row.get("value_gps")),
            "submission_id": _clean(row.get("submission_id")),
            "created_at": _coerce_datetime(row.get("created_at")),
            "updated_at": _coerce_datetime(row.get("updated_at")),
        })

    return {
        "wetmills": wetmills_out,
        "wetmill_visits": wetmill_visits_out,
        "survey_responses": survey_responses_out,
        "survey_question_responses": survey_question_responses_out,
        "legacy_user_lookup": legacy_user_lookup,
        "rows_in": {
            "wetmills": len(wetmills_out),
            "wetmill_visits": len(wetmill_visits_out),
            "survey_responses": len(survey_responses_out),
            "survey_question_responses": len(survey_question_responses_out),
        },
    }


def load(transformed: Dict[str, Any]) -> Dict[str, int]:
    wetmills = transformed["wetmills"]
    wetmill_visits = transformed["wetmill_visits"]
    survey_responses = transformed["survey_responses"]
    survey_question_responses = transformed["survey_question_responses"]
    legacy_user_lookup = transformed["legacy_user_lookup"]

    start = time.time()

    wetmills_done = 0
    wetmill_visits_done = 0
    survey_responses_done = 0
    survey_question_responses_done = 0

    total = len(wetmills) + len(wetmill_visits) + len(survey_responses) + len(survey_question_responses)

    if total == 0:
        print("[wetmills_from_csv] No rows to load.")
        return {
            "wetmills_loaded": 0,
            "wetmill_visits_loaded": 0,
            "survey_responses_loaded": 0,
            "survey_question_responses_loaded": 0,
            "rows_loaded": 0,
            "rows_skipped": 0,
        }

    with connect() as conn:
        system_user_id = str(settings.SYSTEM_USER_ID)
        new_users_lookup = _fetch_new_users(conn)

        existing_wetmills_by_commcare = _build_existing_map(conn, "wetmills", "commcare_case_id")
        existing_wetmills_by_id = _build_existing_map(conn, "wetmills", "id")

        existing_visits_by_submission = _build_existing_map(conn, "wetmill_visits", "submission_id")
        existing_responses_by_submission = _build_existing_map(conn, "wv_survey_responses", "submission_id")
        existing_questions_by_submission = _build_existing_map(conn, "wv_survey_question_responses", "submission_id")

        wetmill_old_to_actual: Dict[str, str] = {}
        visit_old_to_actual: Dict[str, str] = {}
        response_old_to_actual: Dict[str, str] = {}

        for idx, row in enumerate(wetmills, start=1):
            actual_user_id = _resolve_user_id(
                row["user_id_old"],
                legacy_user_lookup,
                new_users_lookup,
                system_user_id,
            )

            if row["commcare_case_id"] and row["commcare_case_id"] in existing_wetmills_by_commcare:
                actual_id = existing_wetmills_by_commcare[row["commcare_case_id"]]
                wetmill_old_to_actual[row["old_id"]] = actual_id
                params = {
                    "id": actual_id,
                    "user_id": actual_user_id,
                    "wet_mill_unique_id": row["wet_mill_unique_id"],
                    "commcare_case_id": row["commcare_case_id"],
                    "name": row["name"],
                    "mill_status": row["mill_status"],
                    "exporting_status": row["exporting_status"],
                    "programme": row["programme"],
                    "country": row["country"],
                    "manager_name": row["manager_name"],
                    "manager_role": row["manager_role"],
                    "comments": row["comments"],
                    "wetmill_counter": row["wetmill_counter"],
                    "ba_signature": row["ba_signature"],
                    "manager_signature": row["manager_signature"],
                    "tor_page_picture": row["tor_page_picture"],
                    "registration_date": row["registration_date"],
                    "office_entrance_picture": row["office_entrance_picture"],
                    "office_gps_hex": row["office_gps_hex"],
                    "updated_at": row["updated_at"],
                    "is_deleted": row["is_deleted"],
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(WETMILL_UPDATE_SQL, params)
            else:
                actual_id = row["old_id"]
                if not actual_id or actual_id in existing_wetmills_by_id:
                    actual_id = str(uuid4())

                wetmill_old_to_actual[row["old_id"]] = actual_id
                params = {
                    "id": actual_id,
                    "user_id": actual_user_id,
                    "wet_mill_unique_id": row["wet_mill_unique_id"],
                    "commcare_case_id": row["commcare_case_id"],
                    "name": row["name"],
                    "mill_status": row["mill_status"],
                    "exporting_status": row["exporting_status"],
                    "programme": row["programme"],
                    "country": row["country"],
                    "manager_name": row["manager_name"],
                    "manager_role": row["manager_role"],
                    "comments": row["comments"],
                    "wetmill_counter": row["wetmill_counter"],
                    "ba_signature": row["ba_signature"],
                    "manager_signature": row["manager_signature"],
                    "tor_page_picture": row["tor_page_picture"],
                    "registration_date": row["registration_date"],
                    "office_entrance_picture": row["office_entrance_picture"],
                    "office_gps_hex": row["office_gps_hex"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "is_deleted": row["is_deleted"],
                    "created_by_id": system_user_id,
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(WETMILL_INSERT_SQL, params)

                if row["commcare_case_id"]:
                    existing_wetmills_by_commcare[row["commcare_case_id"]] = actual_id
                existing_wetmills_by_id[actual_id] = actual_id

            wetmills_done += 1
            elapsed = time.time() - start
            processed = wetmills_done + wetmill_visits_done + survey_responses_done + survey_question_responses_done
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            print(
                f"[wetmills_from_csv][wetmills] {processed:,}/{total:,} | wetmills {wetmills_done:,}/{len(wetmills):,} | ETA {_fmt_eta(eta)}",
                flush=True,
            )

        for idx, row in enumerate(wetmill_visits, start=1):
            actual_wetmill_id = wetmill_old_to_actual.get(row["wetmill_id_old"])
            if not actual_wetmill_id:
                continue

            actual_user_id = _resolve_user_id(
                row["user_id_old"],
                legacy_user_lookup,
                new_users_lookup,
                system_user_id,
            )

            existing_id = row["submission_id"] and existing_visits_by_submission.get(row["submission_id"])
            if existing_id:
                actual_id = existing_id
                visit_old_to_actual[row["old_id"]] = actual_id
                params = {
                    "id": actual_id,
                    "wetmill_id": actual_wetmill_id,
                    "user_id": actual_user_id,
                    "form_name": row["form_name"],
                    "visit_date": row["visit_date"],
                    "entrance_photograph": row["entrance_photograph"],
                    "geo_location_hex": row["geo_location_hex"],
                    "updated_at": row["updated_at"],
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(WETMILL_VISIT_UPDATE_SQL, params)
            else:
                actual_id = row["old_id"] or str(uuid4())
                visit_old_to_actual[row["old_id"]] = actual_id
                params = {
                    "id": actual_id,
                    "wetmill_id": actual_wetmill_id,
                    "user_id": actual_user_id,
                    "form_name": row["form_name"],
                    "visit_date": row["visit_date"],
                    "entrance_photograph": row["entrance_photograph"],
                    "geo_location_hex": row["geo_location_hex"],
                    "submission_id": row["submission_id"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "created_by_id": system_user_id,
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(WETMILL_VISIT_INSERT_SQL, params)
                if row["submission_id"]:
                    existing_visits_by_submission[row["submission_id"]] = actual_id

            wetmill_visits_done += 1
            elapsed = time.time() - start
            processed = wetmills_done + wetmill_visits_done + survey_responses_done + survey_question_responses_done
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            print(
                f"[wetmills_from_csv][wetmill_visits] {processed:,}/{total:,} | visits {wetmill_visits_done:,}/{len(wetmill_visits):,} | ETA {_fmt_eta(eta)}",
                flush=True,
            )

        for idx, row in enumerate(survey_responses, start=1):
            actual_visit_id = visit_old_to_actual.get(row["form_visit_id_old"])
            if not actual_visit_id:
                continue

            existing_id = row["submission_id"] and existing_responses_by_submission.get(row["submission_id"])
            if existing_id:
                actual_id = existing_id
                response_old_to_actual[row["old_id"]] = actual_id
                params = {
                    "id": actual_id,
                    "form_visit_id": actual_visit_id,
                    "survey_type": row["survey_type"],
                    "completed_date": row["completed_date"],
                    "general_feedback": row["general_feedback"],
                    "updated_at": row["updated_at"],
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(SURVEY_RESPONSE_UPDATE_SQL, params)
            else:
                actual_id = row["old_id"] or str(uuid4())
                response_old_to_actual[row["old_id"]] = actual_id
                params = {
                    "id": actual_id,
                    "form_visit_id": actual_visit_id,
                    "survey_type": row["survey_type"],
                    "completed_date": row["completed_date"],
                    "general_feedback": row["general_feedback"],
                    "submission_id": row["submission_id"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "created_by_id": system_user_id,
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(SURVEY_RESPONSE_INSERT_SQL, params)
                if row["submission_id"]:
                    existing_responses_by_submission[row["submission_id"]] = actual_id

            survey_responses_done += 1
            elapsed = time.time() - start
            processed = wetmills_done + wetmill_visits_done + survey_responses_done + survey_question_responses_done
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            print(
                f"[wetmills_from_csv][survey_responses] {processed:,}/{total:,} | responses {survey_responses_done:,}/{len(survey_responses):,} | ETA {_fmt_eta(eta)}",
                flush=True,
            )

        for idx, row in enumerate(survey_question_responses, start=1):
            actual_response_id = response_old_to_actual.get(row["survey_response_id_old"])
            if not actual_response_id:
                continue

            existing_id = row["submission_id"] and existing_questions_by_submission.get(row["submission_id"])
            if existing_id:
                actual_id = existing_id
                params = {
                    "id": actual_id,
                    "survey_response_id": actual_response_id,
                    "section_name": row["section_name"],
                    "question_name": row["question_name"],
                    "field_type": row["field_type"],
                    "value_text": row["value_text"],
                    "value_number": row["value_number"],
                    "value_boolean": row["value_boolean"],
                    "value_date": row["value_date"],
                    "value_gps_hex": row["value_gps_hex"],
                    "updated_at": row["updated_at"],
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(SURVEY_QUESTION_UPDATE_SQL, params)
            else:
                actual_id = row["old_id"] or str(uuid4())
                params = {
                    "id": actual_id,
                    "survey_response_id": actual_response_id,
                    "section_name": row["section_name"],
                    "question_name": row["question_name"],
                    "field_type": row["field_type"],
                    "submission_id": row["submission_id"],
                    "value_text": row["value_text"],
                    "value_number": row["value_number"],
                    "value_boolean": row["value_boolean"],
                    "value_date": row["value_date"],
                    "value_gps_hex": row["value_gps_hex"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "created_by_id": system_user_id,
                    "last_updated_by_id": system_user_id,
                }
                conn.execute(SURVEY_QUESTION_INSERT_SQL, params)
                if row["submission_id"]:
                    existing_questions_by_submission[row["submission_id"]] = actual_id

            survey_question_responses_done += 1
            elapsed = time.time() - start
            processed = wetmills_done + wetmill_visits_done + survey_responses_done + survey_question_responses_done
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            print(
                f"[wetmills_from_csv][survey_question_responses] {processed:,}/{total:,} | question_responses {survey_question_responses_done:,}/{len(survey_question_responses):,} | ETA {_fmt_eta(eta)}",
                flush=True,
            )

    return {
        "wetmills_loaded": wetmills_done,
        "wetmill_visits_loaded": wetmill_visits_done,
        "survey_responses_loaded": survey_responses_done,
        "survey_question_responses_loaded": survey_question_responses_done,
        "rows_loaded": wetmills_done + wetmill_visits_done + survey_responses_done + survey_question_responses_done,
        "rows_skipped": 0,
    }


def run() -> Dict[str, Any]:
    print("Starting wetmills CSV migration...")

    inputs = fetch_csv_inputs()
    transformed = transform(inputs)
    loaded = load(transformed)

    return {
        "rows_in": (
            transformed["rows_in"]["wetmills"]
            + transformed["rows_in"]["wetmill_visits"]
            + transformed["rows_in"]["survey_responses"]
            + transformed["rows_in"]["survey_question_responses"]
        ),
        "rows_loaded": loaded["rows_loaded"],
        "rows_skipped": loaded["rows_skipped"],
        "wetmills_in": transformed["rows_in"]["wetmills"],
        "wetmill_visits_in": transformed["rows_in"]["wetmill_visits"],
        "survey_responses_in": transformed["rows_in"]["survey_responses"],
        "survey_question_responses_in": transformed["rows_in"]["survey_question_responses"],
        "wetmills_loaded": loaded["wetmills_loaded"],
        "wetmill_visits_loaded": loaded["wetmill_visits_loaded"],
        "survey_responses_loaded": loaded["survey_responses_loaded"],
        "survey_question_responses_loaded": loaded["survey_question_responses_loaded"],
    }