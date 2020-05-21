#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5556
#   Sends "Hello" to server, expects "World" back
#

import zmq
import time
import argparse
import numpy as np
from PIL import Image
from pathlib import Path

# https://pyzmq.readthedocs.io/en/latest/serialization.html
def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])

cur_dir = Path().absolute()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--command", required = True)
ap.add_argument("-n", "--hostname", required = True)
args = vars(ap.parse_args())

# dict of commands for sanity checking
cmds = {
    "pic": "pic"
}

try:
    cmd = cmds[args["command"]]
    context = zmq.Context()

    # Socket to talk to server
    print("Connecting to Camera server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{}:5556".format(args["hostname"]))

    # Send the command
    socket.send_string(cmd)

    # Get the reply as numpy array, convert to PIL and save locally
    image = recv_array(socket)
    pil_img = Image.fromarray(image)
    pil_img.save(cur_dir / 'image.jpg')
    print("Image received")

except KeyError:
    print("unknown command: %s" % args["command"])
