import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
from sqlalchemy import text

from ..db import connect
from ..config import settings


SYSTEM_ROLES = [
    "CI Leadership",
    "Project Manager",
    "Senior MEL Specialist",
    "MEL Specialist",
    "Agronomy Advisor",
    "Senior Agronomy Advisor",
    "Senior Business Advisor",
    "Business Advisor",
    "Farmer Trainer",
    "Super Admin",
]

OLD_ROLE_TO_NEW_ROLE = {
    "ci_leadership": "CI Leadership",
    "project_manager": "Project Manager",
    "senior_mel_specialist": "Senior MEL Specialist",
    "mel_specialist": "MEL Specialist",
    "mel_analyst": "MEL Specialist",
    "agronomy_advisor": "Agronomy Advisor",
    "senior_agronomy_advisor": "Senior Agronomy Advisor",
    "standard": "Agronomy Advisor",
    "senior_business_advisor": "Senior Business Advisor",
    "business_advisor": "Business Advisor",
    "business_councelor": "Business Advisor",
    "farmer_trainer": "Farmer Trainer",
    "super_admin": "Super Admin",
}

PROJECT_ROLE_SKIP = {"Super Admin", "CI Leadership"}

BASE_DIR = Path(__file__).resolve().parents[2]
FILES_DIR = BASE_DIR / "files"

USERS_CSV = FILES_DIR / "tbl_users.csv"
ROLES_CSV = FILES_DIR / "tbl_roles.csv"
PROJECT_ROLES_CSV = FILES_DIR / "tbl_project_role.csv"
OLD_PROJECTS_CSV = FILES_DIR / "tbl_projects.csv"


USERS_UPSERT_SQL = text("""
INSERT INTO pima.users (
    id,
    first_name,
    middle_name,
    last_name,
    email,
    username,
    password,
    created_at,
    updated_at,
    tns_id,
    phone_number,
    job_title,
    user_role,
    status,
    from_sf,
    sf_id,
    is_deleted,
    deleted_at,
    commcare_mobile_worker_id,
    manager_id,
    created_by_id,
    last_updated_by_id
) VALUES (
    :id,
    :first_name,
    :middle_name,
    :last_name,
    :email,
    :username,
    :password,
    :created_at,
    :updated_at,
    :tns_id,
    :phone_number,
    :job_title,
    :user_role,
    :status,
    false,
    :sf_id,
    false,
    NULL,
    NULL,
    NULL,
    :created_by_id,
    :last_updated_by_id
)
ON CONFLICT (id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    middle_name = EXCLUDED.middle_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    username = EXCLUDED.username,
    password = EXCLUDED.password,
    updated_at = EXCLUDED.updated_at,
    tns_id = EXCLUDED.tns_id,
    phone_number = EXCLUDED.phone_number,
    job_title = EXCLUDED.job_title,
    user_role = EXCLUDED.user_role,
    status = EXCLUDED.status,
    sf_id = EXCLUDED.sf_id,
    last_updated_by_id = EXCLUDED.last_updated_by_id
""")

PROJECT_ROLE_INSERT_SQL = text("""
INSERT INTO pima.project_staff_roles (
    id,
    staff_id,
    project_id,
    tns_id,
    role,
    status,
    commcare_location_id,
    commcare_case_id,
    created_at,
    updated_at,
    send_to_commcare_status,
    from_sf,
    sf_id,
    is_deleted,
    deleted_at,
    send_to_commcare,
    created_by_id,
    last_updated_by_id
) VALUES (
    :id,
    :staff_id,
    :project_id,
    :tns_id,
    :role,
    :status,
    NULL,
    :commcare_case_id,
    :created_at,
    :updated_at,
    'Pending',
    false,
    NULL,
    false,
    NULL,
    false,
    :created_by_id,
    :last_updated_by_id
)
ON CONFLICT (id) DO NOTHING
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
    if not s or s.lower() in {"nan", "null", "none", "nil"}:
        return None
    return s


def _split_name(full_name: Any) -> Tuple[str, Optional[str], str]:
    parts = [p for p in str(full_name or "").strip().split() if p]
    if not parts:
        return "Unknown", None, "User"
    if len(parts) == 1:
        return parts[0], None, parts[0]
    if len(parts) == 2:
        return parts[0], None, parts[1]
    return parts[0], " ".join(parts[1:-1]), parts[-1]


def _normalize_status(value: Any) -> str:
    s = str(value or "").strip().lower()
    return "Inactive" if s in {"inactive", "disabled", "false", "0"} else "Active"


def _normalize_role(old_role_name: Any) -> Optional[str]:
    cleaned = _clean(old_role_name)
    if not cleaned:
        return None
    return OLD_ROLE_TO_NEW_ROLE.get(cleaned.lower())


def _build_username(email: Any, full_name: Any) -> Optional[str]:
    email = _clean(email)
    if email:
        return email.split("@")[0].strip().lower()
    full_name = _clean(full_name)
    if full_name:
        return ".".join(full_name.lower().split())
    return None


def _build_tns_id(prefix: str, raw_id: Any, sf_id: Any = None) -> str:
    sf_id = _clean(sf_id)
    if sf_id:
        return f"{prefix}-sf-{sf_id}"
    raw = _clean(raw_id)
    if raw:
        return f"{prefix}-{raw}"
    digest = hashlib.sha1(str(raw_id).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _make_commcare_case_id(pr_id: str) -> str:
    digest = hashlib.sha1(pr_id.encode("utf-8")).hexdigest()[:20]
    return f"LEGACY-PR-{digest}"


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


def _coerce_timestamp(value: Any):
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    return None if pd.isna(ts) else ts.to_pydatetime()


def _normalize_email(value: Any) -> Optional[str]:
    email = _clean(value)
    return email.lower() if email else None


def _pick_column(df: pd.DataFrame, candidates: List[str], label: str) -> str:
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError(f"Could not find {label}. Expected one of {candidates}. Got {list(df.columns)}")


def _new_project_map(conn) -> Dict[str, str]:
    rows = conn.execute(
        text("SELECT sf_id, id FROM pima.projects WHERE sf_id IS NOT NULL")
    ).mappings().all()
    return {str(r["sf_id"]).strip(): str(r["id"]) for r in rows if r["sf_id"]}


def _fetch_existing_users(conn) -> Dict[str, Dict[str, str]]:
    rows = conn.execute(text("""
        SELECT id, email, username, sf_id
        FROM pima.users
    """)).mappings().all()

    by_id = {}
    by_email = {}
    by_username = {}
    by_sf_id = {}

    for row in rows:
        user_id = str(row["id"])
        by_id[user_id] = user_id

        email = _normalize_email(row["email"])
        if email:
            by_email[email] = user_id

        username = _clean(row["username"])
        if username:
            by_username[username.lower()] = user_id

        sf_id = _clean(row["sf_id"])
        if sf_id:
            by_sf_id[sf_id] = user_id

    return {
        "by_id": by_id,
        "by_email": by_email,
        "by_username": by_username,
        "by_sf_id": by_sf_id,
    }


def _fetch_existing_project_roles(conn) -> Dict[Tuple[str, str, str], str]:
    rows = conn.execute(text("""
        SELECT id, staff_id, project_id, role
        FROM pima.project_staff_roles
    """)).mappings().all()

    existing = {}
    for row in rows:
        key = (str(row["staff_id"]), str(row["project_id"]), str(row["role"]))
        existing[key] = str(row["id"])
    return existing


def _resolve_user_target_id(
    legacy_user: Dict[str, Any],
    existing_users: Dict[str, Dict[str, str]],
) -> str:
    legacy_id = str(legacy_user["legacy_user_id"])
    sf_id = _clean(legacy_user["sf_id"])
    email = _normalize_email(legacy_user["email"])
    username = _clean(legacy_user["username"])
    username = username.lower() if username else None

    if legacy_id in existing_users["by_id"]:
        return existing_users["by_id"][legacy_id]

    if sf_id and sf_id in existing_users["by_sf_id"]:
        return existing_users["by_sf_id"][sf_id]

    if email and email in existing_users["by_email"]:
        return existing_users["by_email"][email]

    if username and username in existing_users["by_username"]:
        return existing_users["by_username"][username]

    return legacy_id


def fetch_csv_inputs() -> Dict[str, pd.DataFrame]:
    return {
        "users": _read_csv(_require_file(USERS_CSV)),
        "roles": _read_csv(_require_file(ROLES_CSV)),
        "project_roles": _read_csv(_require_file(PROJECT_ROLES_CSV)),
        "old_projects": _read_csv(_require_file(OLD_PROJECTS_CSV)),
    }


def transform(inputs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    users_df = inputs["users"].copy()
    roles_df = inputs["roles"].copy()
    project_roles_df = inputs["project_roles"].copy()
    old_projects_df = inputs["old_projects"].copy()

    old_project_id_col = _pick_column(old_projects_df, ["id", "project_id"], "old project id column")
    old_project_sf_col = _pick_column(old_projects_df, ["sf_id", "sf_project_id"], "old project sf_id column")

    print("Old projects columns:", list(old_projects_df.columns))
    print("Project roles columns:", list(project_roles_df.columns))
    print("Sample old project ids:", old_projects_df[old_project_id_col].astype(str).head(5).tolist())
    print("Sample project role project_ids:", project_roles_df["project_id"].astype(str).head(5).tolist())

    role_lookup = {
        str(row["role_id"]).strip(): _clean(row["role_name"])
        for _, row in roles_df.iterrows()
        if _clean(row.get("role_id"))
    }

    old_project_to_sf = {
        str(row[old_project_id_col]).strip(): _clean(row[old_project_sf_col])
        for _, row in old_projects_df.iterrows()
        if _clean(row.get(old_project_id_col))
    }

    with connect() as conn:
        new_project_by_sf = _new_project_map(conn)

    users_out: List[Dict[str, Any]] = []
    user_ids_in_scope = set()
    user_missing_role_map = []

    for _, row in users_df.iterrows():
        legacy_user_id = str(row["user_id"]).strip()
        old_role_name = role_lookup.get(str(row["role_id"]).strip())
        normalized_role = _normalize_role(old_role_name)

        if old_role_name and not normalized_role:
            user_missing_role_map.append({
                "role_id": str(row["role_id"]).strip(),
                "old_role_name": old_role_name,
            })

        first_name, middle_name, last_name = _split_name(row.get("user_name"))

        users_out.append({
            "legacy_user_id": legacy_user_id,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "email": _clean(row.get("user_email")),
            "username": _build_username(row.get("user_email"), row.get("user_name")),
            "password": "MP@1234",
            "created_at": _coerce_timestamp(row.get("createdAt")),
            "updated_at": _coerce_timestamp(row.get("updatedAt")),
            "tns_id": _build_tns_id("legacy-user", legacy_user_id, row.get("sf_user_id")),
            "phone_number": _clean(row.get("mobile_no")),
            "job_title": None,
            "user_role": normalized_role,
            "status": _normalize_status(row.get("account_status")),
            "sf_id": _clean(row.get("sf_user_id")),
        })
        user_ids_in_scope.add(legacy_user_id)

    project_roles_out: List[Dict[str, Any]] = []
    skipped_roles: List[Dict[str, Any]] = []
    missing_old_projects: List[Dict[str, Any]] = []
    missing_new_projects: List[Dict[str, Any]] = []
    missing_role_map: List[Dict[str, Any]] = user_missing_role_map[:]

    for _, row in project_roles_df.iterrows():
        legacy_user_id = str(row["user_id"]).strip()
        if legacy_user_id not in user_ids_in_scope:
            continue

        pr_id = str(row["pr_id"]).strip()
        old_project_id = str(row["project_id"]).strip()
        old_role_name = role_lookup.get(str(row["role"]).strip())
        normalized_role = _normalize_role(old_role_name)

        if old_role_name and not normalized_role:
            missing_role_map.append({
                "role_id": str(row["role"]).strip(),
                "old_role_name": old_role_name,
            })
            continue

        if normalized_role in PROJECT_ROLE_SKIP:
            skipped_roles.append({
                "pr_id": pr_id,
                "legacy_user_id": legacy_user_id,
                "old_project_id": old_project_id,
                "role": normalized_role,
            })
            continue

        project_sf_id = old_project_to_sf.get(old_project_id)
        if not project_sf_id:
            missing_old_projects.append({
                "old_project_id": old_project_id,
                "pr_id": pr_id,
                "legacy_user_id": legacy_user_id,
            })
            continue

        new_project_id = new_project_by_sf.get(project_sf_id)
        if not new_project_id:
            missing_new_projects.append({
                "old_project_id": old_project_id,
                "project_sf_id": project_sf_id,
                "pr_id": pr_id,
                "legacy_user_id": legacy_user_id,
            })
            continue

        project_roles_out.append({
            "legacy_project_role_id": pr_id,
            "legacy_user_id": legacy_user_id,
            "project_id": new_project_id,
            "tns_id": _build_tns_id("legacy-pr", pr_id),
            "role": normalized_role,
            "status": "Active",
            "commcare_case_id": _make_commcare_case_id(pr_id),
            "created_at": _coerce_timestamp(row.get("createdAt")),
            "updated_at": _coerce_timestamp(row.get("updatedAt")),
        })

    dedup_missing_role_map = []
    seen_missing_roles = set()
    for item in missing_role_map:
        key = (item["role_id"], item["old_role_name"])
        if key not in seen_missing_roles:
            seen_missing_roles.add(key)
            dedup_missing_role_map.append(item)

    return {
        "users": users_out,
        "project_roles": project_roles_out,
        "skipped_roles": skipped_roles,
        "missing_old_projects": missing_old_projects,
        "missing_new_projects": missing_new_projects,
        "missing_role_map": dedup_missing_role_map,
        "rows_in": {
            "users": len(users_df),
            "project_roles": int(project_roles_df["user_id"].astype(str).str.strip().isin(user_ids_in_scope).sum()),
        },
    }


def load(transformed: Dict[str, Any]) -> Dict[str, int]:
    users = transformed["users"]
    project_roles = transformed["project_roles"]
    start = time.time()

    users_done = 0
    project_roles_done = 0
    project_roles_skipped_existing = 0

    total = len(users) + len(project_roles)

    if total == 0:
        print("[csv_users_project_roles] No rows to load.")
        return {
            "users_loaded": 0,
            "project_roles_loaded": 0,
            "rows_loaded": 0,
            "rows_skipped": 0,
        }

    with connect() as conn:
        system_user_id = str(settings.SYSTEM_USER_ID)

        existing_users = _fetch_existing_users(conn)
        legacy_to_actual_user_id: Dict[str, str] = {}

        user_params_list = []
        for user in users:
            actual_user_id = _resolve_user_target_id(user, existing_users)

            email = _normalize_email(user["email"])
            username = _clean(user["username"])
            username = username.lower() if username else None
            sf_id = _clean(user["sf_id"])

            legacy_to_actual_user_id[user["legacy_user_id"]] = actual_user_id

            existing_users["by_id"][actual_user_id] = actual_user_id
            if email:
                existing_users["by_email"][email] = actual_user_id
            if username:
                existing_users["by_username"][username] = actual_user_id
            if sf_id:
                existing_users["by_sf_id"][sf_id] = actual_user_id

            user_params_list.append({
                "id": actual_user_id,
                "first_name": user["first_name"],
                "middle_name": user["middle_name"],
                "last_name": user["last_name"],
                "email": email,
                "username": username,
                "password": user["password"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"],
                "tns_id": user["tns_id"],
                "phone_number": user["phone_number"],
                "job_title": user["job_title"],
                "user_role": user["user_role"],
                "status": user["status"],
                "sf_id": sf_id,
                "created_by_id": system_user_id,
                "last_updated_by_id": system_user_id,
            })

        for batch_start in range(0, len(user_params_list), 1000):
            batch = user_params_list[batch_start: batch_start + 1000]
            if batch:
                conn.execute(USERS_UPSERT_SQL, batch)
                users_done += len(batch)

            processed = users_done + project_roles_done
            elapsed = time.time() - start
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100

            print(
                f"[csv_users_project_roles][users] {processed:,}/{total:,} ({pct:5.1f}%) | "
                f"users {users_done:,}/{len(users):,} | roles {project_roles_done:,}/{len(project_roles):,} | "
                f"batch {(batch_start // 1000) + 1:,} | {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                flush=True,
            )

        existing_project_roles = _fetch_existing_project_roles(conn)

        project_role_params_list = []
        for role_row in project_roles:
            actual_staff_id = legacy_to_actual_user_id.get(role_row["legacy_user_id"])
            if not actual_staff_id:
                continue

            existing_key = (actual_staff_id, role_row["project_id"], role_row["role"])
            if existing_key in existing_project_roles:
                project_roles_skipped_existing += 1
                continue

            existing_project_roles[existing_key] = role_row["legacy_project_role_id"]

            project_role_params_list.append({
                "id": role_row["legacy_project_role_id"],
                "staff_id": actual_staff_id,
                "project_id": role_row["project_id"],
                "tns_id": role_row["tns_id"],
                "role": role_row["role"],
                "status": role_row["status"],
                "commcare_case_id": role_row["commcare_case_id"],
                "created_at": role_row["created_at"],
                "updated_at": role_row["updated_at"],
                "created_by_id": system_user_id,
                "last_updated_by_id": system_user_id,
            })

        for batch_start in range(0, len(project_role_params_list), 1000):
            batch = project_role_params_list[batch_start: batch_start + 1000]
            if batch:
                conn.execute(PROJECT_ROLE_INSERT_SQL, batch)
                project_roles_done += len(batch)

            processed = users_done + project_roles_done
            elapsed = time.time() - start
            rps = processed / elapsed if elapsed > 0 else 0.0
            eta = (total - processed) / rps if rps > 0 else 0.0
            pct = (processed / total) * 100

            print(
                f"[csv_users_project_roles][project_roles] {processed:,}/{total:,} ({pct:5.1f}%) | "
                f"users {users_done:,}/{len(users):,} | roles {project_roles_done:,}/{len(project_roles):,} | "
                f"batch {(batch_start // 1000) + 1:,} | {rps:,.0f} rows/s | ETA {_fmt_eta(eta)}",
                flush=True,
            )

    skipped = (
        len(transformed["skipped_roles"])
        + len(transformed["missing_old_projects"])
        + len(transformed["missing_new_projects"])
        + project_roles_skipped_existing
    )

    print(
        f"[csv_users_project_roles] Completed. Users {users_done:,}, "
        f"project roles {project_roles_done:,}, skipped {skipped:,} in {_fmt_eta(time.time() - start)}.",
        flush=True,
    )

    return {
        "users_loaded": users_done,
        "project_roles_loaded": project_roles_done,
        "rows_loaded": users_done + project_roles_done,
        "rows_skipped": skipped,
    }


def run() -> Dict[str, Any]:
    print("Starting CSV users + project roles migration...")

    inputs = fetch_csv_inputs()
    print(
        f"Fetched {len(inputs['users'])} users, {len(inputs['roles'])} roles, "
        f"{len(inputs['project_roles'])} project roles, {len(inputs['old_projects'])} old projects from CSV."
    )

    transformed = transform(inputs)

    print(f"Transformed {len(transformed['users'])} users.")
    print(f"Mapped {len(transformed['project_roles'])} project roles for load.")
    print(f"Skipped roles due to Super Admin / CI Leadership: {len(transformed['skipped_roles'])}")
    print(f"Missing old project mapping rows: {len(transformed['missing_old_projects'])}")
    print(f"Missing new project rows by sf_id: {len(transformed['missing_new_projects'])}")
    print(f"Missing role mapping rows: {len(transformed['missing_role_map'])}")

    if transformed["missing_role_map"]:
        print("\nUnmapped legacy roles:")
        for item in transformed["missing_role_map"]:
            print(f"  - role_id={item['role_id']} role_name={item['old_role_name']}")

    if transformed["missing_old_projects"]:
        print("\nOld project ids not found in old projects CSV:")
        for item in transformed["missing_old_projects"][:20]:
            print(
                f"  - old_project_id={item['old_project_id']} "
                f"pr_id={item['pr_id']} legacy_user_id={item['legacy_user_id']}"
            )

    if transformed["missing_new_projects"]:
        print("\nProjects whose sf_id was found in old projects CSV but not in new pima.projects:")
        for item in transformed["missing_new_projects"][:20]:
            print(
                f"  - old_project_id={item['old_project_id']} project_sf_id={item['project_sf_id']} "
                f"pr_id={item['pr_id']} legacy_user_id={item['legacy_user_id']}"
            )

    loaded = load(transformed)

    return {
        "rows_in": transformed["rows_in"]["users"] + transformed["rows_in"]["project_roles"],
        "rows_loaded": loaded["rows_loaded"],
        "rows_skipped": loaded["rows_skipped"],
        "users_in": transformed["rows_in"]["users"],
        "project_roles_in_scope": transformed["rows_in"]["project_roles"],
        "users_loaded": loaded["users_loaded"],
        "project_roles_loaded": loaded["project_roles_loaded"],
    }