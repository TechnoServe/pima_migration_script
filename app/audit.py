from datetime import datetime
from uuid import uuid4
from sqlalchemy import text
from .db import connect

DDL = """CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE IF NOT EXISTS ops.etl_runs(
  run_id UUID PRIMARY KEY,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  operator_email TEXT NOT NULL,
  status TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS ops.etl_tasks(
  task_id UUID PRIMARY KEY,
  run_id UUID NOT NULL,
  object_name TEXT NOT NULL,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  status TEXT NOT NULL,
  rows_in INTEGER DEFAULT 0,
  rows_out INTEGER DEFAULT 0,
  error TEXT,
  FOREIGN KEY (run_id) REFERENCES ops.etl_runs(run_id)
);
"""

def ensure_ops_tables():
    with connect() as c:
        c.execute(text(DDL))

def start_run(operator_email: str) -> str:
    run_id = str(uuid4())
    with connect() as c:
        c.execute(text("""            INSERT INTO ops.etl_runs(run_id, started_at, operator_email, status)
            VALUES (:run_id, :ts, :email, 'RUNNING')
        """), {"run_id": run_id, "ts": datetime.utcnow(), "email": operator_email})
    return run_id

def finish_run(run_id: str, status: str = "SUCCESS", notes: str | None = None):
    with connect() as c:
        c.execute(text("""            UPDATE ops.etl_runs
            SET ended_at=:ts, status=:status, notes=COALESCE(notes,'') || :notes
            WHERE run_id=:run_id
        """), {"run_id": run_id, "ts": datetime.utcnow(), "status": status, "notes": (notes or "")})

def start_task(run_id: str, object_name: str) -> str:
    task_id = str(uuid4())
    with connect() as c:
        c.execute(text("""
            INSERT INTO ops.etl_tasks(task_id, run_id, object_name, started_at, status)
            VALUES (:task_id, :run_id, :obj, :ts, 'RUNNING')
        """), {"task_id": task_id, "run_id": run_id, "ts": datetime.utcnow(), "obj": object_name})
    return task_id

def finish_task(task_id: str, rows_in: int, rows_out: int, status: str = "SUCCESS", error: str | None = None):
    with connect() as c:
        c.execute(text("""            UPDATE ops.etl_tasks
            SET ended_at=:ts, status=:status, rows_in=:rin, rows_out=:rout, error=:err
            WHERE task_id=:task_id
        """), {"task_id": task_id, "ts": datetime.utcnow(), "status": status, "rin": rows_in, "rout": rows_out, "err": error})
