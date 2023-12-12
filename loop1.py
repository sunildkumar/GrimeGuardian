# loop1.py
import time


def loop1(q):
    counter = 0
    while True:
        q.put(f"Item {counter}")
        print(f"Published: Item {counter}")
        counter += 1
        time.sleep(1)
