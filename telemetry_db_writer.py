import sqlite3
import time
import random
from datetime import datetime, timezone

def generate_telem_packet():
    return {
        "time": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "battery": round(random.uniform(0, 100), 1),
        "temperature": round(random.uniform(-20, 120), 1),
        "signal": round(random.uniform(0, 100), 1),
        "velocity": round(random.uniform(0, 20000), 1)
    }

def insert_packet(cur, table_name, packet):
    keys = packet.keys()
    columns = ", ".join(keys)
    placeholders = ", ".join(["?"] * len(keys))
    values = tuple(packet[k] for k in keys)
    cur.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)

def main():
    conn = sqlite3.connect('telemetry.db')
    cur = conn.cursor()

    try:
        while True:
            packet = generate_telem_packet()
            insert_packet(cur, 'telemetry', packet)
            conn.commit()
            print(f"Inserted: {packet}")
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\nWriter interrupted by user. Closing DB.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()