import datetime
import threading
from groundlight import Groundlight
from groundlight.client import Detector
from groundlight.binary_labels import Label
import time


def process_queries(query_storage, gl, detectors: list[Detector]):
    answer_indexes = []
    for i in range(len(query_storage)):
        query, time_submitted = query_storage[i]

        # choose the detector that matches query.detector_id
        detector = None
        for d in detectors:
            if d.id == query.detector_id:
                detector = d
                break

        if detector is None:
            raise ValueError(f"Could not find detector with id {query.detector_id}")

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


def remove_answered_queries(query_storage, answer_queue, answer_indexes):
    for i in reversed(answer_indexes):
        answer = query_storage.pop(i)
        answer_queue.put(answer)
    return len(answer_indexes)


def remove_expired_queries(query_storage):
    expired_queries = 0
    new_query_storage = []
    for i in range(len(query_storage)):
        if (datetime.datetime.now() - query_storage[i][1]).total_seconds() <= 10:
            new_query_storage.append(query_storage[i])
        else:
            expired_queries += 1
    return new_query_storage, expired_queries


def process_query_queue(
    query_queue, answer_queue, detectors: list[Detector], stop_event: threading.Event
):
    query_storage = []
    gl = Groundlight()
    total_queries = 0
    total_answered = 0
    total_expired = 0
    while not stop_event.is_set():
        # only process queries if there are any, check every 3 seconds
        if query_queue.empty():
            time.sleep(3)
            continue
        else:
            try:
                while not query_queue.empty():
                    query, time_submitted = query_queue.get(timeout=0)
                    query_storage.append((query, time_submitted))
                    total_queries += 1

                answer_indexes = process_queries(query_storage, gl, detectors)
                total_answered += remove_answered_queries(
                    query_storage, answer_queue, answer_indexes
                )
                query_storage, expired = remove_expired_queries(query_storage)
                total_expired += expired

            except Exception as e:
                print(f"Error: {e}")
                raise e

            print(
                f"Total queries: {total_queries}, Total answered: {total_answered}, Total expired: {total_expired}"
            )
