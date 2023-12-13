from publish_notifications import publish_notifications
from dotenv import load_dotenv

load_dotenv()

import threading
import uuid
from update_state import update_sink_state
from thread_safe_state import ThreadSafeState
from process_queries import process_query_queue
from groundlight import Groundlight
from sink_queries import clear_data, make_sink_queries
import os
import queue
from messaging import DiscordBot


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
    if not os.getenv("GROUNDLIGHT_API_TOKEN"):
        raise EnvironmentError("GROUNDLIGHT_API_TOKEN not set in .env file")

    # delete all data captured from previous runs
    clear_data()

    dirty_sink_detector = setup_detector(unique=False)

    # define threadsafe things we need
    sink_query_queue = queue.Queue()
    sink_answer_queue = queue.Queue()
    notification_queue = queue.Queue()
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
        target=update_sink_state,
        args=(state, sink_answer_queue, stop_event),
    )
    thread4 = threading.Thread(
        target=publish_notifications,
        args=(state, notification_queue, stop_event),
    )

    bot = DiscordBot(notification_queue, stop_event)
    thread5 = threading.Thread(target=bot.run, args=(os.getenv("BOT_TOKEN"),))

    # set threads as daemons to make sure they exit when the main thread exits
    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True
    thread4.daemon = True
    thread5.daemon = True

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread4.join()
