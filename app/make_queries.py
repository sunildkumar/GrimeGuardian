# loop1.py
from datetime import datetime
import os
from queue import Queue
import random
import threading
from PIL import Image
from groundlight import Groundlight


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


def get_kitchen_image() -> Image:
    """
    returns an image of a kitchen
    # TODO - replace with an image from a live feed when available
    """

    empty_kitchen_dir = "../data_scraping/empty_kitchen"
    nonempty_kitchen_dir = "../data_scraping/nonempty_kitchen"

    empty_kitchens = os.listdir(empty_kitchen_dir)
    nonempty_kitchens = os.listdir(nonempty_kitchen_dir)

    kitchen_type = random.choice(["empty", "nonempty"])

    if kitchen_type == "empty":
        chosen_kitchen = random.choice(empty_kitchens)
        path = os.path.join(empty_kitchen_dir, chosen_kitchen)
    else:
        chosen_kitchen = random.choice(nonempty_kitchens)
        path = os.path.join(nonempty_kitchen_dir, chosen_kitchen)

    image = Image.open(path)
    if image.mode in ["RGBA", "P"]:
        image = image.convert("RGB")
    return image


def clear_data():
    """
    Clear the data directory of all jpg files
    """
    for file in os.listdir("../data"):
        if file.endswith(".jpg"):
            os.remove(os.path.join("../data", file))


def save_image(image: Image, query_id: str):
    """
    Save the image to disk using the image query id as the name of the file
    """
    image.save(f"../data/{query_id}.jpg")


def make_sink_queries(query_queue: Queue, detector, stop_event: threading.Event):
    """
    This loop will produce queries of the sink asynchonously and puts them in the query_queue for later processing
    """
    gl = Groundlight()

    while not stop_event.is_set():
        try:
            image = get_sink_image()
            query = gl.ask_async(detector=detector, image=image)
            submit_time = datetime.now()
            query_queue.put((query, submit_time))
            save_image(image, query.id)
        except Exception as e:
            print(f"Error: {e}")


def make_kitchen_queries(query_queue: Queue, detector, stop_event: threading.Event):
    """
    This loop will produce queries of the kitchen asynchonously and puts them in the query_queue for later processing
    """
    gl = Groundlight()

    while not stop_event.is_set():
        try:
            image = get_kitchen_image()
            query = gl.ask_async(detector=detector, image=image)
            submit_time = datetime.now()
            query_queue.put((query, submit_time))
            save_image(image, query.id)
        except Exception as e:
            print(f"Error: {e}")