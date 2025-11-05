# db.py
from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from .config import settings

_engine: Engine | None = None
_sql_cache: dict[str, str] = {}  # cache SQL files by path

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.pg_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            future=True,
        )
    return _engine

@contextmanager
def connect():
    eng = get_engine()
    with eng.begin() as conn:
        yield conn

def _load_sql(sql_path: str) -> str:
    # read once and cache
    sql = _sql_cache.get(sql_path)
    if sql is None:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()
        _sql_cache[sql_path] = sql
    return sql

def run_sql(conn, sql_path: str, params: dict | None = None):
    # Backward-compatible: single-row execute using cached SQL
    sql = _load_sql(sql_path)
    conn.execute(text(sql), params or {})

def run_sql_many(conn, sql_path: str, param_list: list[dict]):
    # Fast path: DBAPI executemany
    if not param_list:
        return
    sql = _load_sql(sql_path)
    conn.execute(text(sql), param_list)
