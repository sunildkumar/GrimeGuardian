# loop1.py
import os
from queue import Queue
import random
from PIL import Image
from groundlight import Groundlight
import time


def get_sink_image() -> Image:
    """
    returns an image of a a sink
    # TODO - replace with an image from a live feed when available
    """

    clean_sink_dir = "../data_scraping/clean_sink"
    dirty_sink_dir = "../data_scraping/dirty_sink"

    clean_sinks = os.listdir(clean_sink_dir)
    dirty_sinks = os.listdir(dirty_sink_dir)

    sink_type = random.choice(["clean", "dirty"])

    if sink_type == "clean":
        chosen_sink = random.choice(clean_sinks)
        path = os.path.join(clean_sink_dir, chosen_sink)
    else:
        chosen_sink = random.choice(dirty_sinks)
        path = os.path.join(dirty_sink_dir, chosen_sink)

    image = Image.open(path)
    if image.mode in ["RGBA", "P"]:
        image = image.convert("RGB")

    return image


def make_sink_queries(query_queue: Queue, detector):
    """
    This loop will produce queries asynchonously and puts them in the query_queue for later processing
    """
    gl = Groundlight()

    while True:
        try:
            image = get_sink_image()
            query = gl.ask_async(detector=detector, image=image)
            submit_time = time.time()
            query_queue.put((query, submit_time))
            print(f"Produced: {query.id} at {submit_time}")
        except Exception as e:
            print(f"Error: {e}")
