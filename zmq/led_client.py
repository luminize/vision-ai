#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import time
import argparse

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--command", required = True)
ap.add_argument("-n", "--hostname", required = True)
args = vars(ap.parse_args())

# dict of commands for sanity checking
cmds = {
    "color_r": "color_r",
    "color_g": "color_g",
    "color_b": "color_b",
    "color_y": "color_y",
    "color_c": "color_c",
    "color_p": "color_p",
    "color_w": "color_w",
    "color_o": "color_o",
    "br_100": "br_100",
    "br_50": "br_50",
    "br_10": "br_10",
    "br_0": "br_0"
}

try:
    cmd = cmds[args["command"]]
    context = zmq.Context()

    # Socket to talk to server
    print("Connecting to Neopixel LED server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{}:5555".format(args["hostname"]))

    # Send the command
    socket.send_string(cmd)

    # Get the reply.
    message = socket.recv_string()
    print("Received reply: [ %s ]" % message)

except KeyError:
    print("unknown command: %s" % args["command"])
