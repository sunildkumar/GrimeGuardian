DEFAULT_MESSAGE = "Alert! The sink is staging a dirty dishes rebellion. Time to restore order! Troops, to the kitchen!"
from queue import Queue
import threading
import time
from thread_safe_state import ThreadSafeState

DEFAULT_MESSAGE = "Alert! The sink is staging a dirty dishes rebellion. Time to restore order! Troops, to the kitchen!"


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
                notification_queue.put(DEFAULT_MESSAGE)

        previous_state = current_state


def should_send_notification(state: ThreadSafeState) -> bool:
    return True
