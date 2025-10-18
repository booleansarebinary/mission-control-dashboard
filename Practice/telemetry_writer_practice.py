import json
import os
import time
from datetime import timezone
import random
from datetime import datetime

FRUITS = ['banana', 'apple', 'strawberry', 'blueberry', 'pineapple', 'mango']

def generate_telem_packet():
    return {
        "name": random.choice(FRUITS),
        "size": round(random.uniform(0, 1), 2),
        "weight": round(random.uniform(0, 1), 2)
    }

def main():
    with open("/Users/anns/Documents/Mission Control Dashboard/Practice/practicefile.ndjson", "a+") as f:
        f.seek(0, os.SEEK_END);
        if f.tell() > 0:
            f.seek(f.tell() - 1)
            last_char = f.read(1)
            if last_char != '\n':
                f.write('\n')

        while True:
            packet = generate_telem_packet()
            f.write(json.dumps(packet) + "\n")
            f.flush()              # Flush Python’s internal buffer
            os.fsync(f.fileno())   # Flush OS buffer to disk
            print(f"Written: {packet}")
            time.sleep(1)

if __name__ == "__main__":
    main()