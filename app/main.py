# main.py
import threading
import queue
from app.loop1 import loop1
from app.loop2 import loop2

if __name__ == "__main__":
    shared_queue = queue.Queue()

    thread1 = threading.Thread(target=loop1, args=(shared_queue,))
    thread2 = threading.Thread(target=loop2, args=(shared_queue,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("All loops are complete")
