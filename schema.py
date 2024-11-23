def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY, channel_id TEXT, message TEXT, schedule TEXT, tool TEXT)"
    )
