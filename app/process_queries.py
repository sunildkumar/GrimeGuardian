from groundlight import Groundlight
import time


def loop2(query_queue):
    query_storage = []
    gl = Groundlight()
    while True:
        try:
            # Get everything out of the queue and into storage
            while not query_queue.empty():
                query, time_submitted = query_queue.get()
                query_storage.append((query, time_submitted))
                print(f"Moved to storage: {query.id} at {time_submitted}")

            print(f"before: {[i[0].result for i in query_storage]}")
            # attempt to process things in storage. First convert any async queries to normal queries using
            for i in range(len(query_storage)):
                query, time_submitted = query_storage[i]
                if query.result is None:
                    query = gl.get_image_query(query.id)
                    query_storage[i] = (query, time_submitted)
                print(query.confidence)

            print(f"after: {[i[0].result for i in query_storage]}")

        except Exception as e:
            print(f"Error: {e}")
            raise e

        time.sleep(10)
