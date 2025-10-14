import json
import time


#Practice loading a file and handling errors/an empty file.
def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            first_line = f.readline()
            if not first_line:
                print(f"{filename} is empty.")
            else:
                f.seek(0)
                print("FILE LoADING DEBUGGING: REACHED HERE.")
                return json.load(f)
    except(FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        #None automatically returned

def in_range(value, range_tuple):
    return range_tuple[0] <= value <= range_tuple[1]

def evaluate_metric(value, thresholds):
    green = thresholds['green']
    yellow = thresholds['yellow']
    red = thresholds['red']

    if(in_range(value, green)):
        status = 'green'
    elif(in_range(value, yellow)):
        status = 'yellow'
    elif(in_range(value, red)):
        status = 'red'
    else:
        status = 'unknown'

    return status

def status_eval(telem_data_point, thresh_data):
    statuses = {}
    log_lines = []

    METRICS = ['size', 'weight']

    for metric in METRICS:
        value = telem_data_point.get(metric)
        if value is None:
            statuses[metric] = 'UNKNOWN'
            continue

        metric_threshold = thresh_data.get(metric)
        if not metric_threshold:
            statuses[metric] = 'NO_THRESHOLDS'
            continue

        current_status = evaluate_metric(value, metric_threshold)

        statuses[metric] = current_status

        if current_status in ['yellow', 'red']:
            log_line = f"{telem_data_point.get('time', 'NO_TIME')} - {metric.upper()}: {value} - {current_status}"
            log_lines.append(log_line)

    return statuses, log_lines

def write_log(log_lines, filename):
    with open(filename, 'a') as log_file:
        for line in log_lines:
            log_file.write(line + '\n')

def main():
    data = load_json_file("practicefile.json")
    thresh = load_json_file("practicethresholds.json")

    if data is None or thresh is None:
        print("Missing data or thresholds. Exiting.")
        return

    all_log_lines = []

    for point in data:
        statuses, log_lines = status_eval(point, thresh)
        all_log_lines.extend(log_lines)

    write_log(all_log_lines, 'errorlog.txt')

if __name__ == "__main__":
    main()