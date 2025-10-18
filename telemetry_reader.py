import json
import time
import os

ITERATIVE_METRICS = ['temperature', 'battery', 'signal', 'velocity']
UNITS = {
    'temperature': '°C',
    'battery': '%',
    'signal': '%',
    'velocity': 'm/s'
}
TELEMETRY_FILE = 'telemetry.ndjson'
THRESHOLDS_FILE = 'thresholds.json'
ERROR_LOG_FILE = 'errorlog.txt'

def load_thresholds(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return None

def in_range(value, range_tuple):
    """Check if value is within a given range (inclusive)."""
    return range_tuple[0] <= value <= range_tuple[1]

def status_eval(telem_data_point, thresh_data):
    statuses = {}
    log_lines = []

    for metric in ITERATIVE_METRICS:
        value = telem_data_point.get(metric)
        if value is None:
            statuses[metric] = 'UNKNOWN'
            continue

        metric_thresholds = thresh_data.get(metric)
        if not metric_thresholds:
            statuses[metric] = 'NO_THRESHOLDS'
            continue

        green_range = metric_thresholds['green']
        yellow_range = metric_thresholds['yellow']
        red_range = metric_thresholds['red']

        if in_range(value, green_range):
            status = 'GREEN'
        elif in_range(value, yellow_range):
            status = 'YELLOW'
        elif in_range(value, red_range):
            status = 'RED'
        else:
            status = 'UNKNOWN'

        statuses[metric] = status

        if status in ['YELLOW', 'RED']:
            log_line = f"{telem_data_point.get('time', 'NO_TIME')} - {metric.upper()}: {value} - {status}\n"
            log_lines.append(log_line)

    return statuses, log_lines

def main():
    try:
        thresh_data = load_thresholds(THRESHOLDS_FILE)
        if thresh_data is None:
            print("Failed to load threshold data.")
            return

        # Wait for telemetry file to exist
        while not os.path.exists(TELEMETRY_FILE):
            print("Waiting for telemetry file...")
            time.sleep(1)

        with open(TELEMETRY_FILE, 'r') as f, open(ERROR_LOG_FILE, 'a') as log_file:
            # Seek to end if you want to skip old lines or comment this line to read from start
            # f.seek(0, os.SEEK_END)  

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)  # No new line, wait and try again
                    continue

                try:
                    packet = json.loads(line.strip())
                except json.JSONDecodeError:
                    # Possibly partial write, skip this line and wait for full line later
                    continue

                
                time_data = packet.get('time', 'NO_TIME')
                print(f"Time: {time_data}")

                for input in ITERATIVE_METRICS:
                    value = packet.get(input, 'N/A')
                    unit = UNITS.get(input, '')
                    print(f"{input.capitalize()}: {value}{unit}")

                status, log_lines = status_eval(packet, thresh_data)
                print(f"Status: {status}")

                for log_line in log_lines:
                    log_file.write(log_line)

                print("--------------")
    except KeyboardInterrupt:
         print("\nReader interrupted by user. Exiting.")

if __name__ == "__main__":
    main()
