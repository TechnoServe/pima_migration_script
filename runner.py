import typer

from app.audit import ensure_ops_tables, start_run, finish_run, start_task, finish_task
from app.config import settings
# FULL implementations
from app.objects import (
    users, programs, locations, projects,
    project_staff_roles, training_modules, farmer_groups,
    training_sessions, households, farmers, attendances,
    observations, observation_results
)

app = typer.Typer(help="Pima Migration CLI (Salesforce -> Postgres)")


@app.command("init")
def init_ops():
    ensure_ops_tables()
    typer.secho("ops schema ready.", fg=typer.colors.GREEN)


def _run_step(run_id: str, name: str, fn):
    tid = start_task(run_id, name)
    try:
        res = fn.run()
        finish_task(tid, rows_in=res["rows_in"], rows_out=res["rows_loaded"], status="SUCCESS")
        typer.echo({name: res})
        return res
    except Exception as e:
        finish_task(tid, rows_in=0, rows_out=0, status="FAILED", error=str(e))
        raise

@app.command("users")
def cmd_users():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)

    try:
        res = _run_step(run_id, "users", users)
        finish_run(run_id, "SUCCESS", f"Users: {res}")
    except Exception as e:
        finish_run(run_id, "FAILED", f"Users error: {e}")
        raise

@app.command("programs")
def cmd_programs():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "programs", programs)
        finish_run(run_id, status="SUCCESS", notes=f"Programs: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Programs error: {e}")
        raise


@app.command("locations")
def cmd_locations():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "locations", locations)
        finish_run(run_id, status="SUCCESS", notes=f"Locations: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Locations error: {e}")
        raise


@app.command("projects")
def cmd_projects():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "projects", projects)
        finish_run(run_id, status="SUCCESS", notes=f"Projects: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Projects error: {e}")
        raise

@app.command("project_roles")
def cmd_project_roles():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "project_staff_roles", project_staff_roles)
        finish_run(run_id, status="SUCCESS", notes=f"Project roles: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Project roles error: {e}")
        raise

@app.command("training_modules")
def cmd_training_modules():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "training_modules", training_modules)
        finish_run(run_id, status="SUCCESS", notes=f"Training modules: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Training modules error: {e}")
        raise

@app.command("farmer_groups")
def cmd_farmer_groups():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "farmer_groups", farmer_groups)
        finish_run(run_id, status="SUCCESS", notes=f"Farmer groups: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Farmer groups error: {e}")
        raise

@app.command("training_sessions")
def cmd_training_sessions():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "training_sessions", training_sessions)
        finish_run(run_id, status="SUCCESS", notes=f"Training sessions: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Training sessions error: {e}")
        raise

@app.command("households")
def cmd_households():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "households", households)
        finish_run(run_id, status="SUCCESS", notes=f"Households: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Households error: {e}")
        raise

@app.command("farmers")
def cmd_farmers():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "farmers", farmers)
        finish_run(run_id, status="SUCCESS", notes=f"Farmers: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Farmers error: {e}")
        raise

@app.command("attendances")
def cmd_attendances():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "attendances", attendances)
        finish_run(run_id, status="SUCCESS", notes=f"Attendances: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Attendances error: {e}")
        raise

@app.command("observations")
def cmd_observations():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "observations", observations)
        finish_run(run_id, status="SUCCESS", notes=f"Observations: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Observations error: {e}")
        raise

@app.command("observation_results")
def cmd_observation_results():
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)
    try:
        res = _run_step(run_id, "observation_results", observation_results)
        finish_run(run_id, status="SUCCESS", notes=f"Observation results: {res}")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"Observation results error: {e}")
        raise

@app.command("run-all")
def run_all():
    """Run in dependency order;"""
    ensure_ops_tables()
    run_id = start_run(settings.MIGRATION_OPERATOR_EMAIL)

    def go(name, mod):
        return _run_step(run_id, name, mod)

    try:
        go("users", users)
        go("programs", programs)
        go("locations", locations)
        go("projects", projects)
        go("project_staff_roles", project_staff_roles)
        go("training_modules", training_modules)
        go("farmer_groups", farmer_groups)
        go("training_sessions", training_sessions)
        go("households", households)
        go("farmers", farmers)
        go("attendances", attendances)
        go("observations", observations)
        go("observation_results", observation_results)

        go("farm_visits", farm_visits)
        go("farms", farms)
        go("fv_best_practices", fv_best_practices)
        go("fv_best_practice_answers", fv_best_practice_answers)
        go("coffee_varieties", coffee_varieties)
        go("checks", checks)
        go("images", images)


        finish_run(run_id, status="SUCCESS", notes="run-all finished")
    except Exception as e:
        finish_run(run_id, status="FAILED", notes=f"run-all failed: {e}")
        raise


if __name__ == "__main__":
    app()
