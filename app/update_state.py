from queue import Queue
import threading
import time

from thread_safe_state import ThreadSafeState


def update_sink_state(
    state: ThreadSafeState, answer_queue: Queue, stop_event: threading.Event
):
    """
    Updates the state of the world based on the answer queue
    """
    while not stop_event.is_set():
        # only process answers if there are any, check every 3 seconds
        if answer_queue.empty():
            time.sleep(3)
            continue
        else:
            try:
                while not answer_queue.empty():
                    answer, timestamp = answer_queue.get()

                    if timestamp > state.get_state().sink_timestamp:
                        state.update_state(answer.result.label, timestamp)

            except Exception as e:
                print(f"Error: {e}")
                raise e
            print(f"current state: {state.get_state()}")
