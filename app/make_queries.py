# loop1.py
from datetime import datetime
import os
from queue import Queue
import random
import threading
from PIL import Image
from groundlight import Groundlight
import cv2
import numpy as np
import time


# I used `v4l2-ctl --list-devices` to figure out the paths to the cameras. This should be stable across reboots.
KITCHEN_CAMERA_PATH = '/dev/video0'
SINK_CAMERA_PATH = '/dev/video4'

TIME_BETWEEN_QUERIES = 10

def get_cam_image(cap):
    try:
        if not cap.isOpened():
            raise IOError(f"Cannot open webcam")

        ret, frame = cap.read()

        if ret:
            # Convert the color from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            return pil_image
        else:
            print('failed to capture image from camera')
            return None
    except Exception as e:
        print(f"Error: {e}")


def get_sink_image(debug=False)->Image: 

    if debug: 
        return _get_sink_image_debug()
    
    return get_cam_image(SINK_CAMERA_PATH)

def get_kitchen_image(debug=False)->Image:

    if debug:
        return _get_debug_image()
    
    return get_cam_image(KITCHEN_CAMERA_PATH)



def _get_sink_image_debug() -> Image:
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


def _get_kitchen_image_debug() -> Image:
    """
    returns an image of a kitchen for debugging. Doesn't use a camera
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
    cap = cv2.VideoCapture(SINK_CAMERA_PATH)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    try:
        while not stop_event.is_set():
            try:
                image = get_cam_image(cap)
                if image is not None:
                    query = gl.ask_async(detector=detector, image=image)
                    submit_time = datetime.now()
                    query_queue.put((query, submit_time))
                    save_image(image, query.id)
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(TIME_BETWEEN_QUERIES)
    finally:
        cap.release()


def make_kitchen_queries(query_queue: Queue, detector, stop_event: threading.Event):
    """
    This loop will produce queries of the kitchen asynchonously and puts them in the query_queue for later processing
    """
    gl = Groundlight()
    cap = cv2.VideoCapture(KITCHEN_CAMERA_PATH)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    try:
        while not stop_event.is_set():
            try:
                image = get_cam_image(cap)
                if image is not None:
                    query = gl.ask_async(detector=detector, image=image)
                    submit_time = datetime.now()
                    query_queue.put((query, submit_time))
                    save_image(image, query.id)
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(TIME_BETWEEN_QUERIES)
    finally:
        cap.release()


def capture_and_save_images_from_all_cameras():
    '''
    debugging function to determine which indexes cameras correspond to
    '''
    max_camera_index = 10  # Maximum number of cameras to check
    for i in range(max_camera_index):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite(f'camera_{i}_image.jpg', frame)
                cap.release()
            
        except:
            print(f'failed to take a picture on camera index {i}')


