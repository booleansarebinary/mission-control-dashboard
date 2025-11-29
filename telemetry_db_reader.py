import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time

# Settings
DB_FILE = 'telemetry.db'
ITERATIVE_METRICS = ['temperature', 'battery', 'signal', 'velocity']
UNITS = {
    'temperature': '°C',
    'battery': '%',
    'signal': '%',
    'velocity': 'm/s'
}

def fetch_new_packets(last_time=None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if last_time:
        cur.execute("SELECT * FROM telemetry WHERE time > ? ORDER BY time ASC", (last_time,))
    else:
        cur.execute("SELECT * FROM telemetry ORDER BY time ASC")

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def live_plot():
    plt.ion()
    fig, axes = plt.subplots(len(ITERATIVE_METRICS), 1, figsize=(10, 12), sharex=True)
    fig.suptitle("Live Telemetry Dashboard", fontsize=16)

    time_data = []
    value_data = {metric: [] for metric in ITERATIVE_METRICS}
    lines = {}

    # Initialize subplots
    for i, metric in enumerate(ITERATIVE_METRICS):
        ax = axes[i]
        lines[metric], = ax.plot_date([], [], linestyle='solid', marker='o', label=metric)
        ax.set_ylabel(f"{metric.capitalize()} ({UNITS[metric]})")
        ax.grid(True)
        ax.legend(loc='upper left')

    axes[-1].set_xlabel("Time")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    last_time = None

    try:
        while True:
            new_packets = fetch_new_packets(last_time)

            if new_packets:
                for packet in new_packets:
                    t = datetime.fromisoformat(packet['time'].replace('Z', '+00:00'))
                    if t not in time_data:
                        time_data.append(t)
                        for metric in ITERATIVE_METRICS:
                            value_data[metric].append(packet[metric])
                        last_time = packet['time']

                # Update plots
                for i, metric in enumerate(ITERATIVE_METRICS):
                    lines[metric].set_data(time_data, value_data[metric])
                    axes[i].relim()
                    axes[i].autoscale_view()

                fig.autofmt_xdate()
                plt.draw()
                plt.pause(0.1)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Live plotting stopped by user.")
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    live_plot()
