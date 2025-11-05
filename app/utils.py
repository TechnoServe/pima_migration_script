from typing import Iterable, Dict, Any, Optional
from sqlalchemy import text

# Function to yield chunks of a specified size from an iterable
def chunked(iterable: Iterable, size: int):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

def first_value(conn, sql: str, params: Dict[str, Any]) -> Optional[Any]:
    row = conn.execute(text(sql), params).first()
    return None if not row else row[0]
