#!/usr/bin/python3
#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5556
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
from pathlib import Path
from picamera import PiCamera
import numpy as np
from PIL import Image

# https://pyzmq.readthedocs.io/en/latest/serialization.html
def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype = str(A.dtype),
        shape = A.shape,
    )
    socket.send_json(md, flags|zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)

cmds = {
    "pic": "pic"
}

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

cur_dir = Path().absolute()
camera = PiCamera()

while True:
    # Wait for next request from client
    # receive a string for ease of use
    message = socket.recv_string()
    print("Received request: %s" % message)
    
    # check if command is known
    try:
        cmd = cmds[message]
        # keep it simple for now and save the capture locally
        # get smarter at a later stage
        camera.capture(str(cur_dir / 'image.jpg'))
        # open as a numpy array from disk
        image = np.array(Image.open(cur_dir / 'image.jpg'))
        # Send reply back to client
        send_array(socket, image)

    except KeyError:
        print("unknown command: %s" % args["command"])
        socket.send(b"fail")
