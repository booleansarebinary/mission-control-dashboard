import sqlite3

conn = sqlite3.connect("telemetry.db")
cur = conn.cursor()
cur.execute("DELETE FROM telemetry")
conn.commit()
conn.close()

print("✅ Telemetry database cleared.")
