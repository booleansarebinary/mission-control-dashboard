# Reads all rows of the database and calculates the average battery, temperature, signal, and
# velocity. Goes from 1-15 threads. I have 10 cores (4 performance, 6 efficiency).


# I know that for my case the multithreading module is probably better for performance
# because I don't need true multiprocessing, but I'm using the multiprocessing module
# because I want to see true concurrency in action. This isn't exactly multithreading
# but I'm doing by best to mimic it.
import multiprocessing
import sqlite3
import time
import matplotlib.pyplot as plt
import numpy as np
import os

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

# Creates the threads (processes)
def run_test(num_workers):
    count = count_lines()
    normalTotal = count // num_workers
    remainder = count % num_workers

    args = [] 
    offset = 0

    for i in range(num_workers):
        n = normalTotal + (1 if i < remainder else 0)  # I'm distributing the remainder
        args.append((n, offset, 15 / min(num_workers, 10)))
        offset += n

    start = time.perf_counter()
    with multiprocessing.Pool(num_workers) as pool:
         results = pool.map(get_total, args)

    end = time.perf_counter()
    grand = [sum(vals) for vals in zip(*results)]

    averages = [g / count for g in grand]

    print(f"\nWorkers: {num_workers}")
    print("Totals:", grand)
    print("Averages:", averages)
    print(f"Time Taken: {end - start}")
    return end - start

def main():
    time_taken_per_test = []
    num_processes = []
    for workers in range(1, 16):  # 1 to 15
        time_taken_per_test.append(run_test(workers))
        num_processes.append(workers)

    # Creating the plot
    x_data = np.array(num_processes)
    y_data = np.array(time_taken_per_test)

    plt.plot(x_data, y_data)
    plt.xlabel('Number of Processes')
    plt.ylabel('Time Per Iteration')
    plt.title('Multiprocessing: Getting Averages')
    plt.grid(True) 
    
    plot_file = os.path.join(os.getcwd(), 'multiprocessing_plot.png')
    plt.savefig(plot_file, dpi=300)



if __name__ == "__main__":
    main()

