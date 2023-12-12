# main.py
import threading
import uuid
from process_queries import loop2
from groundlight import Groundlight
from sink_queries import make_sink_queries
from dotenv import load_dotenv
import os
import queue


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
    load_dotenv()

    if not os.getenv("GROUNDLIGHT_API_TOKEN"):
        raise EnvironmentError("GROUNDLIGHT_API_TOKEN not set in .env file")

    dirty_sink_detector = setup_detector(unique=False)

    sink_query_queue = queue.Queue()

    thread1 = threading.Thread(
        target=make_sink_queries, args=(sink_query_queue, dirty_sink_detector)
    )
    thread2 = threading.Thread(target=loop2, args=(sink_query_queue,))
    # set threads as daemons to make sure they exit when the main thread exits
    thread1.daemon = True
    thread2.daemon = True

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("All loops are complete")
