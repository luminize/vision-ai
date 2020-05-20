import canopen
import sys
import os
import argparse
import time
import datetime
import cv2
import numpy as np
from pathlib import Path
from imutils.video import VideoStream

# instantiate the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required = True)
ap.add_argument("-l", "--labels", required = True)
#	help = "Path to the image to be scanned")
args = vars(ap.parse_args())

# instantiate CAN bus
# Start with creating a network representing one CAN bus
can = canopen.Network()
# Connect to the CAN bus
can.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)
can.check()

# Add some nodes with corresponding Object Dictionaries
pd2c = canopen.BaseNode402(3, 'PD2-C4118L1804-E-08.eds')
can.add_node(pd2c)

# instantiate cv2 and file stuff
cur_dir = Path().absolute()
# read file telling which directory to save to
directoryfile = args["directory"]
with open(cur_dir / directoryfile) as file: # Use file to refer to the file object
    directory = file.read()
    label_dir = cur_dir / directory

# read file telling which labels to use
with open(cur_dir / args["labels"]) as file: # Use file to refer to the file object
    lbls = file.read()

try: 
    Path.mkdir(label_dir)
except:
    pass

#open webcam
camera = VideoStream(src=1, resolution=(1280, 960)).start()
focus = 115
camera.stream.set(28, focus)

pd2c.nmt.state = 'RESET'
time.sleep(3.0)
while not (pd2c.nmt.state == 'PRE-OPERATIONAL'):
    print(pd2c.nmt.state)
    time.sleep(0.5)

pd2c.load_configuration()
pd2c.setup_402_state_machine()
pd2c.nmt.state == 'OPERATIONAL'
print(pd2c.nmt.state)

print('set closed loop')
time.sleep(10)
pd2c.sdo[0x3202].phys = 1
print(pd2c.state)

steps_per_rev = 720
pause_time = 1
counter = 0
position = 0
gearratio = 5
rotation_pos = 0.
rotation_step = 1.
resolution = 2000 #4096
target = 0. #rotation_pos + (rotation_step * resolution * gearratio)
record = -1

# first move to zero
pd2c.sdo['Target Position'].phys = position
pd2c.sdo['Modes of operation'].phys = 1
pd2c.sdo[0x6040].phys = 6
pd2c.sdo[0x6040].phys = 7
pd2c.sdo[0x6040].raw = 0x0F
time.sleep(1)
pd2c.sdo[0x6040].raw = 0x1F
time.sleep(2)
pd2c.sdo[0x6040].raw = 0x0F

# now do the main loop:
while True:
        # do opencv stuff
        k = cv2.waitKey(1)

        if ((k%256 == 27) or (k%256 == 113)):
            # ESC or 'q' pressed
            print("Escape hit, quitting...")
            break

        if k%256 == 49:
            # '1' pressed
            rotation_step = 1.       

        if k%256 == 50:
            # '2' pressed
            rotation_step = 0.5 

        if k%256 == 52:
            # '4' pressed
            rotation_step = 0.25 

        if k%256 == 100:
            # 'd' pressed
            with open(cur_dir / directoryfile) as file: # Use file to refer to the file object
                directory = file.read()
                label_dir = cur_dir / directory

        if k%256 == 114:
            # 'r' pressed
            record *= -1

        if k%256 == 115:
            # 's' pressed
            # set new target and record
            rotation_pos = position
            target = rotation_pos + (rotation_step * resolution * gearratio)
            counter = 0
            record = 1

        if k%256 == 108:
            # 'l' pressed
            # stop recording
            record = -1
            # reread labels file
            with open(cur_dir / "labels.txt") as file: # Use file to refer to the file object
                lbls = file.read()

        if k%256 == 45:
            # '=' or minus pressed
            if ((focus <= 255) and (focus > 0)):
                focus -= 5
                camera.stream.set(28, focus)

        if k%256 == 61:
            # '+ is 43' '=' is 61 pressed
            if ((focus < 255) and (focus >= 0)):
                focus += 5
                camera.stream.set(28, focus)

        # read from the camera
        time.sleep(0.001)
        image2 = camera.read()
        image = np.copy(image2)

        if (position < target) :
            counter += 1
            position = rotation_pos + (counter / steps_per_rev) * gearratio * resolution
            pd2c.sdo['Target Position'].phys = position
            pd2c.sdo[0x6040].raw = 0x0F
            #print('moving to new position %s' % position)
            pd2c.sdo[0x6040].raw = 0x1F
            time.sleep(pause_time)
            pd2c.sdo[0x6040].raw = 0x0F
        else:
            record = -1
            cv2.putText(image,"loop finished!", (25,75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,225), 2)
        
        if record > 0:
            now = datetime.datetime.now()
            filename = str(now).replace(' ', '_')
            filename = filename.replace(':', '_')
            filename = filename.replace('.', '_')
            filename += ".jpg"
            with open(label_dir / "image_labels.csv", "a+") as file: # Use file to refer to the file object
                data = file.write("{},{}\n".format(filename, lbls))
            cv2.imwrite(str(label_dir / filename), image2)

        # show screen
        cv2.putText(image,"focus = {}, pos = {:.2f}, target = {}".format(str(focus), position, target), (25,50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,225), 2)
        cv2.putText(image,"labels: {}".format(lbls), (25,25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,225), 2)
        cv2.imshow("Camera", image)

cv2.destroyAllWindows()
pd2c.sdo[0x6040].raw = 0x0F
pd2c.sdo[0x6040].phys = 7
pd2c.sdo[0x6040].phys = 6
print('done')