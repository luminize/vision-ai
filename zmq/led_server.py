#!/usr/bin/python3
#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import board
import neopixel

cmds = {
    "color_r": (255, 0, 0),
    "color_g": (0, 255, 0),
    "color_b": (0, 0, 255),
    "color_y": (255, 255, 0),
    "color_c": (0, 255, 255),
    "color_p": (255, 0, 255),
    "color_w": (255, 255, 255),
    "color_o": (255, 140, 0),
    "br_100": "br_100",
    "br_50": "br_50",
    "br_10": "br_10",
    "br_0": "br_0"
}

pixels = neopixel.NeoPixel(board.D18, 16)
color_r = (255, 0, 0)
color_g = (0, 255, 0)
color_b = (0, 0, 255)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    # Wait for next request from client
    # receive a string for ease of use
    message = socket.recv_string()
    print("Received request: %s" % message)
    
    # check if command is known
    try:
        cmd = cmds[message]
        # check if we're setting brightness or color
        if cmd[0:3] == "br_":
            # set pixels brightness
            pixels.brightness = float(cmd.split('_')[1]) / 100
        else:
            # set color for each individual pixel
            for i in range(len(pixels)):
                pixels[i] = cmd

        # Send reply back to client
        socket.send_string("success")

    except KeyError:
        print("unknown command: %s" % args["command"])
        socket.send_string("fail")
