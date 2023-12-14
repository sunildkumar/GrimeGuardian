from datetime import datetime
from queue import Queue
import threading
import time
from thread_safe_state import StateModel, ThreadSafeState
from enum import Enum


class NotificationType(Enum):
    SINK_DIRTY = "SINK_DIRTY"
    KITCHEN_OCCUPIED = "KITCHEN_OCCUPIED"


def publish_notifications(
    state: ThreadSafeState, notification_queue: Queue, stop_event: threading.Event
):
    previous_state = None
    while not stop_event.is_set():
        current_state = state.get_state()
        if current_state == previous_state:
            time.sleep(3)
        else:
            notif = determine_notification(current_state)
            if notif is not None:
                print(f"Sending notification: {notif}")
                notification_queue.put((state.get_state(), notif))

                if notif == NotificationType.SINK_DIRTY:
                    state.update_state(
                        last_dirty_sink_notification_timestamp=datetime.now()
                    )
                elif notif == NotificationType.KITCHEN_OCCUPIED:
                    state.update_state(
                        last_occupied_kitchen_notification_timestamp=datetime.now()
                    )

        previous_state = current_state


def determine_notification(state: StateModel) -> NotificationType | None:
    """
    Determines if a notification should be sent based on the current state of the world, if neither notification should be sent, returns None
    """
    # Prioritize sending kitchen occupied notifications over dirty sink notifications
    kitchen_occupied_notification = _should_send_kitchen_occupied_notification(state)
    #print(state)
    print(f'kitchen notif: {kitchen_occupied_notification}')

    if kitchen_occupied_notification is not None:
        return kitchen_occupied_notification

    dirty_sink_notification = _should_send_dirty_sink_notification(state)

    if dirty_sink_notification is not None:
        return dirty_sink_notification

    print(f'sink notif: {dirty_sink_notification}')

    return None


def _should_send_dirty_sink_notification(
    state: StateModel,
) -> NotificationType | None:
    # block sending a dirty sink notification if we have sent one in the last MIN_SECONDS_SINCE_LAST_NOTIFICATION seconds
    MIN_SECONDS_SINCE_LAST_DIRTY_SINK_NOTIFICATION = 300

    # how long we are willing to tolerate the sink being dirty before we send a notification given that we haven't notified recently
    MIN_SECONDS_SINCE_SINK_DIRTY = 60

    # how long has it been since we sent a notification about the sink being dirty
    if state.last_dirty_sink_notification_timestamp is None:
        time_since_last_dirty_sink_notification = float("inf")
    else:
        time_since_last_dirty_sink_notification = (
            datetime.now() - state.last_dirty_sink_notification_timestamp
        ).total_seconds()

    # how long has it been since the sink was last clean
    time_since_sink_clean = (
        datetime.now() - state.last_sink_clean_timestamp
    ).total_seconds()

    print(f'{time_since_sink_clean=}, {time_since_last_dirty_sink_notification=}')

    # only send a dirty sink notification if the sink is dirty and it has been at least MIN_SECONDS_SINCE_SINK_DIRTY seconds and it has been at least MIN_SECONDS_SINCE_LAST_NOTIFICATION seconds since the last notification
    if (
        time_since_last_dirty_sink_notification
        > MIN_SECONDS_SINCE_LAST_DIRTY_SINK_NOTIFICATION
        and time_since_sink_clean > MIN_SECONDS_SINCE_SINK_DIRTY
        and state.sink_state == "YES"
    ):
        return NotificationType.SINK_DIRTY
    return None


def _should_send_kitchen_occupied_notification(
    state: StateModel,
) -> NotificationType | None:
    # block sending a kitchen occupied notification if we have sent one in the last MIN_SECONDS_SINCE_LAST_KITCHEN_OCCUPIED_NOTIFICATION seconds
    MIN_SECONDS_SINCE_LAST_KITCHEN_OCCUPIED_NOTIFICATION = 120

    # how long has it been since we sent a notification about the kitchen being occupied
    if state.last_occupied_kitchen_notification_timestamp is None:
        time_since_last_kitchen_occupied_notification = float("inf")
    else:
        time_since_last_kitchen_occupied_notification = (
            datetime.now() - state.last_occupied_kitchen_notification_timestamp
        ).total_seconds()

    print(f'{state.sink_state=}, {state.kitchen_state=}, {state.kitchen_state_timestamp > state.sink_state_timestamp}, {time_since_last_kitchen_occupied_notification=} ')
    # we should send a kitchen occupied notification if
    # 1. the kitchen is occupied
    # 2. the sink is dirty
    # 3. it has been at least MIN_SECONDS_SINCE_LAST_KITCHEN_OCCUPIED_NOTIFICATION seconds since the last notification
    # 4. the kitchen was occupied more recently than the sink was dirty
    if (
        time_since_last_kitchen_occupied_notification
        > MIN_SECONDS_SINCE_LAST_KITCHEN_OCCUPIED_NOTIFICATION
        and state.kitchen_state == "YES"
        and state.sink_state == "YES"
        and state.kitchen_state_timestamp >= state.sink_state_timestamp
    ):
        return NotificationType.KITCHEN_OCCUPIED
