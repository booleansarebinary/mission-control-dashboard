import json
import time
import os
from datetime import timezone
import random
from datetime import datetime

def generate_telem_packet():
    return {
        "time": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "battery": round(random.uniform(0, 100), 1),
        "temperature": round(random.uniform(-20, 120), 1),
        "signal": round(random.uniform(0, 100), 1),
        "velocity": round(random.uniform(0, 20000), 1)
    }

def main():
    try:
        with open("telemetry.ndjson", "a+") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() > 0:
                f.seek(f.tell() - 1)
                last_char = f.read(1)
                if last_char != '\n':
                    f.write('\n')
            while True:  
                packet = generate_telem_packet()
                f.write(json.dumps(packet) + "\n")
                f.flush()  # Ensure data is written immediately
                os.fsync(f.fileno())
                print(f"Written: {packet}")
                time.sleep(1)
    except KeyboardInterrupt:
         print("\nWriter interrupted by user. Exiting.")
if __name__ == "__main__":
    main()
