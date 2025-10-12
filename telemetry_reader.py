import json
import time

# Load the Telemetry JSON file
with open('telemetry.json') as f:
    telemData = json.load(f)

#Load the Thresholds JSON file
with open('thresholds.json') as h:
    threshData = json.load(h)


def status_eval(telemDataPoint, threshData):
    iterative = ['temperature','battery', 'signal']
    
    def in_range(value, r):
        return r[0] <= value <= r[1]
    
    statuses = {}

    for item in iterative:
        value = telemDataPoint.get(item)
        if value is None:
            # Skip or mark as UNKNOWN — your choice
            statuses[item] = 'UNKNOWN'
            continue

        metric_thresholds = threshData.get(item)

        if not metric_thresholds:
            statuses[item] = 'NO_THRESHOLDS'
            continue

        green_range = metric_thresholds['green']
        yellow_range = metric_thresholds['yellow']
        red_range = metric_thresholds['red']

        # Check green
        if in_range(value, green_range):
            status = 'GREEN'
        # Check yellow
        elif in_range(value, yellow_range):
            status = 'YELLOW'
        # Otherwise red
        else:
            status = 'RED'
        
        statuses[item] = status

        if status in ['YELLOW', 'RED']:
            # Compose log line
            log_line = f"{telemDataPoint.get('time', 'NO_TIME')} - {item.upper()}: {value} - {status}\n"
            with open('erorrlog.txt', 'a') as f:
                f.write(log_line)
    
    return statuses

# Loop through each "telemetry" datapoint
for packet in telemData:
    timeData = packet['time']
    battery = packet['battery']
    temp = packet['temperature']
    signal = packet['signal']
    print(f"Time: {timeData}")
    print(f"Battery: {battery}%")
    print(f"Temperature: {temp}°C")
    print(f"Signal: {signal}%")

    #Get the status evaluation
    status = status_eval(packet, threshData)
    print(f"Status: {status}")

    print("--------------")
    time.sleep(1)  # wait 1 second like real-time telemetry

