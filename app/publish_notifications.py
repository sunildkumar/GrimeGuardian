DEFAULT_MESSAGE = "Alert! The sink is staging a dirty dishes rebellion. Time to restore order! Troops, to the kitchen!"
from datetime import datetime
from queue import Queue
import threading
import time
from thread_safe_state import StateModel, ThreadSafeState


def publish_notifications(
    state: ThreadSafeState, notification_queue: Queue, stop_event: threading.Event
):
    previous_state = None
    while not stop_event.is_set():
        current_state = state.get_state()
        if current_state == previous_state:
            time.sleep(3)
        else:
            if should_send_notification(state):
                notification_queue.put(state.get_state())
                state.update_state(last_notification_timestamp=datetime.now())

        previous_state = current_state


def should_send_notification(state: ThreadSafeState) -> bool:
    # TODO make these bigger for real use
    MIN_SECONDS_SINCE_LAST_NOTIFICATION = 10
    MIN_SECONDS_SINCE_SINK_DIRTY = 0.1

    state_obj: StateModel = state.get_state()
    time_since_last_notification = (
        datetime.now() - state_obj.last_notification_timestamp
    ).total_seconds()

    time_since_sink_dirty = (
        datetime.now() - state_obj.sink_state_timestamp
    ).total_seconds()

    # only send a notification if the sink is dirty and it has been at least MIN_SECONDS_SINCE_SINK_DIRTY seconds and it has been at least MIN_SECONDS_SINCE_LAST_NOTIFICATION seconds since the last notification
    if (
        time_since_last_notification > MIN_SECONDS_SINCE_LAST_NOTIFICATION
        and time_since_sink_dirty > MIN_SECONDS_SINCE_SINK_DIRTY
        and state_obj.sink_state == "YES"
    ):
        return True
    return False
