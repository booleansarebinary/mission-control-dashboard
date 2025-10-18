import sqlite3

conn = sqlite3.connect('telemetry.db')
cur = conn.cursor()

# Create the table
cur.execute('''
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL,
    battery REAL,
    temperature REAL,
    signal REAL,
    velocity REAL
)
''')

conn.commit()
conn.close()
