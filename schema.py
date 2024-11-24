from auth import get_sqlite3_cursor


def ensure_schema():
    cur = get_sqlite3_cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY, channel_id TEXT, message TEXT, schedule TEXT, tool TEXT)"
    )
