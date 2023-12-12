# main.py
import threading
import queue
import uuid
from loop2 import loop2
from groundlight import Groundlight
from sink_queries import make_sink_queries
from dotenv import load_dotenv


def setup_detector(unique: bool = True):
    """
    If unique is True, then the detector returned is guaranteed to be unique.

    returns a detector that can be used to detect a dirty sink
    """
    gl = Groundlight()
    name = "dirty_sink_detector"

    if unique:
        name = name + "_" + str(uuid.uuid4())

    # create detectors
    dirty_sink_detector = gl.get_or_create_detector(
        name=name,
        query="Is there at least one dish in the sink? Cleaning supplies like sponge, brush, soap, etc. are not considered dishes.",
    )

    return dirty_sink_detector


if __name__ == "__main__":
    load_dotenv()

    dirty_sink_detector = setup_detector(unique=True)

    sink_query_queue = queue.Queue()

    thread1 = threading.Thread(
        target=make_sink_queries, args=(sink_query_queue, dirty_sink_detector)
    )
    thread2 = threading.Thread(target=loop2, args=(sink_query_queue,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("All loops are complete")
