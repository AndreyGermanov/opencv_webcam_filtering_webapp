import os
import cv2
import time
from threading import Thread
from flask import Flask, request
from waitress import serve
import numpy as np

app = Flask(__name__, static_url_path='', static_folder='.')


# Dictionary of filter functions
# that can be applied to video
# frame.
filter_funcs = {}


# Dictionary of filter options
# to apply to video frames
# Keys should match keys of
# the `filter_funcs` dictionary
# Values will pass to these functions
# as a `value` parameter
image_filters = {
    "colors": ""
}


def main():
    # Define a dictionary of filtering functions
    # (You can add more different functions here)
    filter_funcs["colors"] = colors
    filter_funcs["blur"] = blur
    filter_funcs["binary"] = binary
    filter_funcs["brightness"] = brightness
    filter_funcs["contrast"] = contrast
    filter_funcs["edges"] = edges
    filter_funcs["only_face"] = only_face

    # Run camera capturing and filtering
    # in a background thread
    thread = Thread(target=run_camera)
    thread.start()

    # Run web service in a main thread
    serve(app, port=8080)


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/filter', methods=["POST"])
def filter():
    """
    Receives a dictionary of filters
    that user setup on the frontend
    in a POST request and set it to
    the `image_filters` global variable.
    """
    global image_filters
    image_filters = request.json
    return "OK"


def run_camera():
    """
    Function captures each video frame from web camera
    as OpenCV image in a background thread,
    applies defined filters to it using
    defined filter functions and saves modified
    frame to the `frame.jpg` file
    """

    # Connect to the default web camera
    source = cv2.VideoCapture(0)

    # capture frames from web camera every 30 ms
    while True:
        has_frame, frame = source.read()
        if not has_frame:
            break
        # go over all enabled image filters that came
        # from frontend and call appropriate filter
        # functions to apply them to current
        # frame
        for filter_func, value in image_filters.items():
            frame = filter_funcs[filter_func](frame, value)
        # save modified frame to the image file
        cv2.imwrite("temp.jpg", frame)
        os.rename("temp.jpg", "frame.jpg")
        time.sleep(0.03)


def colors(frame, colors):
    """
    Color channels filter. Used to apply
    specified color channels to the frame
    :param frame: Current video frame
    :param colors: Color channels string, that can contain "r", "g" and "b" symbols
    :return: Modified frame
    """

    # if no channels, return grayscale image
    if len(colors) == 0:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # get color channels of original frame
    b, g, r = cv2.split(frame)

    # create an empty black image
    empty = np.zeros(r.shape, dtype=np.uint8)
    res_channels = [empty, empty, empty]

    # Add only color channels, that
    # specified in the `colors` string
    # to the source video frame
    if str(colors).find("r") != -1:
        res_channels[2] = r
    if str(colors).find("g") != -1:
        res_channels[1] = g
    if str(colors).find("b") != -1:
        res_channels[0] = b
    frame = cv2.merge(res_channels)
    return frame


def blur(frame, value):
    """
    Blur filter
    :param frame: Current video frame
    :param value: Blur kernel size
    :return: Modified frame
    """
    if value == 0:
        return frame
    return cv2.blur(frame, (value, value))


def binary(frame, value):
    """
    Black and white threshold filter
    :param frame: Current video frame
    :param value: Threshold value
    :return: Modified frame
    """
    if value == 0:
        return frame
    if len(frame.shape) == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    (_, result) = cv2.threshold(frame, value, 255, cv2.THRESH_BINARY)
    return result


def brightness(frame, value):
    """
    Brightness filter
    :param frame: Current video frame
    :param value: Brightness value
    :return: Modified frame
    """
    to_add = np.ones(frame.shape, dtype=np.uint8)*abs(value)
    if value < 0:
        return cv2.subtract(frame, np.uint8(to_add))
    else:
        return cv2.add(frame, np.uint8(to_add))


def contrast(frame, value):
    """
    Contrast filter
    :param frame: Current video frame
    :param value: Contrast value
    :return: Modified frame
    """
    to_add = np.ones(frame.shape, dtype=np.float64)*value
    return np.uint8(np.clip(cv2.multiply(np.float64(frame), to_add),0,255))


def edges(frame, value):
    """
    Canny edge detector filter
    :param frame: Current video frame
    :param value: unused
    :return:
    """
    return cv2.Canny(frame, 80, 150)


def only_face(frame, value):
    net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
    # Model parameters
    in_width = 300
    in_height = 300
    mean = [104, 117, 123]
    conf_threshold = 0.7

    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    blob = cv2.dnn.blobFromImage(frame, 1.0, (in_width, in_height), mean, swapRB=False, crop=False)

    net.setInput(blob)
    detections = net.forward()
    print(detections)
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x_left_bottom = int(detections[0, 0, i, 3] * frame_width)
            y_left_bottom = int(detections[0, 0, i, 4] * frame_height)
            x_right_top = int(detections[0, 0, i, 5] * frame_width)
            y_right_top = int(detections[0, 0, i, 6] * frame_height)
            print(y_right_top,y_left_bottom,x_right_top,x_left_bottom)
            return frame[y_left_bottom:y_right_top, x_left_bottom:x_right_top]
    return frame


main()
