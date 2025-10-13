import json
import time

ITERATIVE_METRICS = ['temperature', 'battery', 'signal']

def load_json_file(filename):
    """Load JSON data from a file safely."""
    try:
        with open(filename, 'r') as f:
            first_line = f.readline();
            if not first_line:
                print(f"{filename} is empty.")
            f.seek(0)
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

        statuses[metric] = status

        if status in ['YELLOW', 'RED']:
            log_line = f"{telem_data_point.get('time', 'NO_TIME')} - {metric.upper()}: {value} - {status}\n"
            log_lines.append(log_line)

    return statuses, log_lines

def main():
    telem_data = load_json_file('telemetry.json')
    thresh_data = load_json_file('thresholds.json')

    if telem_data is None or thresh_data is None:
        print("Failed to load required data files.")
        return

    with open('errorlog.txt', 'a') as log_file:
        for packet in telem_data:
            time_data = packet.get('time', 'NO_TIME')
            battery = packet.get('battery', 'N/A')
            temperature = packet.get('temperature', 'N/A')
            signal = packet.get('signal', 'N/A')

            print(f"Time: {time_data}")
            print(f"Battery: {battery}%")
            print(f"Temperature: {temperature}°C")
            print(f"Signal: {signal}%")

            status, log_lines = status_eval(packet, thresh_data)
            print(f"Status: {status}")

            for line in log_lines:
                log_file.write(line)

            print("--------------")
            time.sleep(1)  # simulate real-time delay

if __name__ == "__main__":
    main()
