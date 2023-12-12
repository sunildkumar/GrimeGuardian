import threading
import uuid
from update_state import update_sink_state
from thread_safe_state import ThreadSafeState
from process_queries import process_query_queue
from groundlight import Groundlight
from sink_queries import make_sink_queries
from dotenv import load_dotenv
import os
import queue
import yappi


def setup_detector(unique: bool = True):
    """
    If unique is True, then the detector returned is guaranteed to be unique, good for testing from scratch.

    returns a detector that can be used to detect a dirty sink
    """
    gl = Groundlight()
    name = "dirty_sink_detector"

    if unique:
        name = name + "_" + str(uuid.uuid4())

    # create detectors
    dirty_sink_detector = gl.get_or_create_detector(
        name=name,
        query="Is there at least one dish in the sink? Cleaning supplies like sponge, brush, soap, etc. are not considered dishes. If you cannot see into the sink, consider it empty and answer NO.",
    )

    return dirty_sink_detector


if __name__ == "__main__":
    # Set this to True to enable profiling and timeout
    enable_profiling_and_timeout = False

    if enable_profiling_and_timeout:
        yappi.start(builtins=False)

    load_dotenv()

    if not os.getenv("GROUNDLIGHT_API_TOKEN"):
        raise EnvironmentError("GROUNDLIGHT_API_TOKEN not set in .env file")

    dirty_sink_detector = setup_detector(unique=False)

    # define threadsafe things we need
    sink_query_queue = queue.Queue()
    sink_answer_queue = queue.Queue()
    state = ThreadSafeState()

    stop_event = threading.Event()

    thread1 = threading.Thread(
        target=make_sink_queries,
        args=(sink_query_queue, dirty_sink_detector, stop_event),
    )
    thread2 = threading.Thread(
        target=process_query_queue,
        args=(sink_query_queue, sink_answer_queue, dirty_sink_detector, stop_event),
    )
    thread3 = threading.Thread(
        target=update_sink_state, args=(state, sink_answer_queue, stop_event)
    )
    # set threads as daemons to make sure they exit when the main thread exits
    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True

    if enable_profiling_and_timeout:
        # Stop threads after timeout
        def stop_threads():
            try:
                func_stats = yappi.get_func_stats()

                func_stats.print_all(
                    columns={
                        # tells yappi to print name column wide enough to fit the long function names
                        0: ("name", 200),
                        1: ("ncall", 5),
                        2: ("tsub", 8),
                        3: ("ttot", 8),
                        4: ("tavg", 8),
                    }
                )
                yappi.stop()
            except Exception as e:
                print(f"Error: {e}")

            stop_event.set()

        timer = threading.Timer(5, stop_threads)
        timer.start()

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    print("All loops are complete")
