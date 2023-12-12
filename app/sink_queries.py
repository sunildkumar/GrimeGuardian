# loop1.py
import queue
import os
import random
from PIL import Image
from groundlight import Groundlight
import time


def get_sink_image() -> Image:
    """
    returns an image of a a sink
    # TODO - replace with an image from a live feed when available
    """

    clean_sink_dir = "data_scraping/clean_sink"
    dirty_sink_dir = "data_scraping/dirty_sink"

    clean_sinks = os.listdir(clean_sink_dir)
    dirty_sinks = os.listdir(dirty_sink_dir)

    sink_type = random.choice(["clean", "dirty"])

    if sink_type == "clean":
        chosen_sink = random.choice(clean_sinks)
        path = os.path.join(clean_sink_dir, chosen_sink)
    else:
        chosen_sink = random.choice(dirty_sinks)
        path = os.path.join(dirty_sink_dir, chosen_sink)

    return Image.open(path)


def make_sink_queries(query_queue: queue.Queue, detector):
    gl = Groundlight()

    while True:
        image = get_sink_image()
        query = gl.ask_async(detector=detector, image=image)
        query_queue.put(query)
        print(f"Produced: {query.id}")
        time.sleep(2)
