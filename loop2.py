# loop2.py
import time


def loop2(q):
    while True:
        item = q.get()
        print(f"Consumed: {item}")
        q.task_done()
        time.sleep(2)
