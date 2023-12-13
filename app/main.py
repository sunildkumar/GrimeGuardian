from dotenv import load_dotenv
import threading
import uuid
from update_state import update_state
from thread_safe_state import ThreadSafeState
from process_queries import process_query_queue
from groundlight import Groundlight
from make_queries import clear_data, make_kitchen_queries, make_sink_queries
import os
from queue import Queue
from messaging import DiscordBot
from publish_notifications import publish_notifications
from constants import DIRTY_SINK_NAME, OCCUPIED_KITCHEN_NAME

load_dotenv()


def setup_detectors(unique: bool = True):
    """
    If unique is True, then the detectors returned are guaranteed to be unique, good for testing from scratch.

    returns dirty_sink_detector, occupied_kitchen_detector
    """
    gl = Groundlight()
    dirty_sink_name = DIRTY_SINK_NAME
    occupied_kitchen_name = OCCUPIED_KITCHEN_NAME

    if unique:
        dirty_sink_name = dirty_sink_name + "_" + str(uuid.uuid4())
        occupied_kitchen_name = occupied_kitchen_name + "_" + str(uuid.uuid4())

    # create detectors
    dirty_sink_detector = gl.get_or_create_detector(
        name=dirty_sink_name,
        query="Is there at least one dish in the sink? Cleaning supplies like sponge, brush, soap, etc. are not considered dishes. If you cannot see into the sink, consider it empty and answer NO.",
    )

    occupied_kitchen_detector = gl.get_or_create_detector(
        name=occupied_kitchen_name,
        query="Is there at least one person in this image?",
    )

    return dirty_sink_detector, occupied_kitchen_detector


if __name__ == "__main__":
    if not os.getenv("GROUNDLIGHT_API_TOKEN"):
        raise EnvironmentError("GROUNDLIGHT_API_TOKEN not set in .env file")

    if not os.getenv("BOT_TOKEN"):
        raise EnvironmentError("BOT_TOKEN not set in .env file")

    if not os.getenv("CHANNEL_ID"):
        raise EnvironmentError("CHANNEL_ID not set in .env file")

    # delete all saved data captured from previous runs
    clear_data()

    dirty_sink_detector, occupied_kitchen_detector = setup_detectors(unique=False)

    # define threadsafe things we need
    query_queue = Queue()
    answer_queue = Queue()
    notification_queue = Queue()
    state = ThreadSafeState()

    stop_event = threading.Event()

    thread1 = threading.Thread(
        target=make_sink_queries,
        args=(query_queue, dirty_sink_detector, stop_event),
    )
    thread2 = threading.Thread(
        target=process_query_queue,
        args=(
            query_queue,
            answer_queue,
            [dirty_sink_detector, occupied_kitchen_detector],
            stop_event,
        ),
    )
    thread3 = threading.Thread(
        target=update_state,
        args=(
            state,
            answer_queue,
            [dirty_sink_detector, occupied_kitchen_detector],
            stop_event,
        ),
    )
    thread4 = threading.Thread(
        target=publish_notifications,
        args=(state, notification_queue, stop_event),
    )

    bot = DiscordBot(notification_queue, stop_event)
    thread5 = threading.Thread(target=bot.run, args=(os.getenv("BOT_TOKEN"),))

    thread6 = threading.Thread(
        target=make_kitchen_queries,
        args=(query_queue, occupied_kitchen_detector, stop_event),
    )

    threads = [thread1, thread2, thread3, thread4, thread5, thread6]

    for thread in threads:
        thread.daemon = True
        thread.start()

    for thread in threads:
        thread.join()
