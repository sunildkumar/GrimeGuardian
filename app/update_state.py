from queue import Queue
import threading
import time

from constants import DIRTY_SINK_NAME, OCCUPIED_KITCHEN_NAME
from thread_safe_state import ThreadSafeState
from groundlight.client import Detector


def update_state(
    state: ThreadSafeState,
    answer_queue: Queue,
    detectors: list[Detector],
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

                    # determine which detector the answer came from
                    detector = None
                    for d in detectors:
                        if d.id == answer.detector_id:
                            detector = d
                            break
                    if detector is None:
                        raise ValueError(
                            f"Could not find detector with id {answer.detector_id}"
                        )
                    # we only care about answers that are more recent than the last update to the state
                    if (
                        DIRTY_SINK_NAME in detector.name
                        and timestamp > state.get_state().sink_state_timestamp
                    ):
                        # if the answer is YES, then the sink is dirty
                        if answer.result.label == "YES":
                            state.update_state(
                                sink_state=answer.result.label,
                                sink_state_timestamp=timestamp,
                                sink_state_iq_id=answer.id,
                            )
                        # if the answer is NO, then the sink is clean
                        elif answer.result.label == "NO":
                            state.update_state(
                                sink_state=answer.result.label,
                                sink_state_timestamp=timestamp,
                                last_sink_clean_timestamp=timestamp,
                                sink_state_iq_id=answer.id,
                            )
                    elif (
                        OCCUPIED_KITCHEN_NAME in detector.name
                        and timestamp > state.get_state().kitchen_state_timestamp
                    ):
                        # we update the state of the kitchen uniformly, regardless of the answer
                        state.update_state(
                            kitchen_state=answer.result.label,
                            kitchen_state_timestamp=timestamp,
                            kitchen_state_iq_id=answer.id,
                        )

            except Exception as e:
                print(f"Error: {e}")
                raise e
