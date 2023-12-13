from queue import Queue
import threading
import time

from thread_safe_state import ThreadSafeState


def update_sink_state(
    state: ThreadSafeState,
    answer_queue: Queue,
    stop_event: threading.Event,
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

                    # we only care about answers that are more recent than the last update to the state
                    if timestamp > state.get_state().sink_state_timestamp:
                        # if the answer is YES, then the sink is dirty and we only need to update the sink_state and sink_timestamp
                        if answer.result.label == "YES":
                            state.update_state(
                                sink_state=answer.result.label,
                                sink_state_timestamp=timestamp,
                            )
                        # if the answer is NO, then the sink is clean and we need to update the sink_state, sink_timestamp, and last_sink_clean_timestamp
                        elif answer.result.label == "NO":
                            state.update_state(
                                sink_state=answer.result.label,
                                sink_state_timestamp=timestamp,
                                last_sink_clean_timestamp=timestamp,
                            )

            except Exception as e:
                print(f"Error: {e}")
                raise e
            print(f"current state: {state.get_state()}")
