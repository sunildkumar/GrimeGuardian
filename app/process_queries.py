import threading
from groundlight import Groundlight
from groundlight.client import Detector
from groundlight.binary_labels import Label
import time


def process_queries(query_storage, gl, detector):
    answer_indexes = []
    for i in range(len(query_storage)):
        query, time_submitted = query_storage[i]
        if (
            query.result
            and query.result.label in [Label.YES, Label.NO]
            and (
                query.result.confidence is None
                or query.result.confidence > detector.confidence_threshold
            )
        ):
            answer_indexes.append(i)
        else:
            query = gl.get_image_query(query.id)
            query_storage[i] = (query, time_submitted)

    return answer_indexes


def remove_answered_queries(query_storage, answer_indexes):
    for i in reversed(answer_indexes):
        query, time_submitted = query_storage.pop(i)
    return len(answer_indexes)


def remove_expired_queries(query_storage):
    expired_queries = 0
    new_query_storage = []
    for i in range(len(query_storage)):
        if time.time() - query_storage[i][1] <= 10:
            new_query_storage.append(query_storage[i])
        else:
            expired_queries += 1
    return new_query_storage, expired_queries


def loop2(query_queue, detector: Detector, stop_event: threading.Event):
    query_storage = []
    gl = Groundlight()
    total_queries = 0
    total_answered = 0
    total_expired = 0
    while not stop_event.is_set():
        try:
            while not query_queue.empty():
                query, time_submitted = query_queue.get(timeout=0)
                query_storage.append((query, time_submitted))
                total_queries += 1

            answer_indexes = process_queries(query_storage, gl, detector)
            total_answered += remove_answered_queries(query_storage, answer_indexes)
            query_storage, expired = remove_expired_queries(query_storage)
            total_expired += expired

        except Exception as e:
            print(f"Error: {e}")
            raise e

        print(
            f"Total queries: {total_queries}, Total answered: {total_answered}, Total expired: {total_expired}"
        )
        time.sleep(1.0)
