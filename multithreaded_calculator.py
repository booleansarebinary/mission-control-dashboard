# Reads all rows of the database and calculates the average battery, temperature, signal, and
# velocity. Goes from 1-15 threads because I have 10 cores (4 performance, 6 efficiency).


# I know that for my case the multithreading module is probably better for performance
# because I don't need true multiprocessing, but I'm using the multiprocessing module
# because I want to see true concurrency in action. This isn't exactly multithreading
# but I'm doing by best to mimic it.
import multiprocessing
import sqlite3
import time

DB_FILE = 'telemetry.db'

def get_total(args):
    
    num_lines_to_read, offset_num, sleep_time = args
    time.sleep(sleep_time)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    totals = [0, 0, 0, 0]

    cur.execute("""
        SELECT temperature, battery, signal, velocity 
        FROM telemetry 
        LIMIT ? OFFSET ?""", (num_lines_to_read, offset_num))
    for row in cur.fetchall():
            totals[0] += row['temperature']
            totals[1] += row['battery']
            totals[2] += row['signal']
            totals[3] += row['velocity']

    conn.close()
    return totals

# Counts the number of rows in the database
def count_lines():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM telemetry")
    (count,) = cur.fetchone()
    conn.close()
    return count

def main():
    count = count_lines()
    normalTotal = count // 2
    remainder = count % 2

    args = [
        (normalTotal, 0, 3),
        (normalTotal, normalTotal, 3),
        #(normalTotal, normalTotal * 2),
        #(normalTotal, normalTotal * 3),
        #(normalTotal, normalTotal * 4),
        #(normalTotal, normalTotal * 5 + remainder),
        
    ]

    start = time.perf_counter()

    with multiprocessing.Pool(2) as pool:
         results = pool.map(get_total, args)

    end = time.perf_counter()
    grand = [sum(vals) for vals in zip(*results)]

    averages = [g / count for g in grand]

    print("Totals:", grand)
    print("Averages:", averages)
    print(f"Time Taken: {end - start}")



if __name__ == "__main__":
    main()

