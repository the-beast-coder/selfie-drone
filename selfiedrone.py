from djitellopy import Tello
import time
import os
import cv2
import sys
from enum import Enum

class State (Enum):
    detectingFaces = 1
    goingToPerson = 2

state = State.detectingFaces

tello = Tello()

S = 60
FPS = 30

distanceThreshold = 250


speed = 10

currentScreenshot = 1


def takePicture ():
    os.system("screencapture screenshot" + str(currentScreenshot) + ".png")
    currentScreenShot = currentScreenshot + 1

if not tello.connect():
    print("Tello not connected")
    sys.exit()

if not tello.set_speed(speed):
    print("Not set speed to lowest possible")
    sys.exit()

# In case streaming is on. This happens when we quit this program without the escape key.
if not tello.streamoff():
    print("Could not stop video stream")
    sys.exit()

if not tello.streamon():
    print("Could not start video stream")
    sys.exit()

print ("Current battery is " + tello.get_battery())

tello.takeoff()
time.sleep(9)

tello.move_up(82)
time.sleep(2)

frame_read = tello.get_frame_read()
stop = False

face_cascade = cv2.CascadeClassifier("face detector.xml")

while not stop:

    frame = frame_read.frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if state == State.detectingFaces:
        tello.rotate_clockwise(20)
        time.sleep(0.1)

    x_pos = None
    y_pos = None
    width = None
    height = None

    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        x_pos = x
        y_pos = y
        width = w
        height = h
        if state == State.detectingFaces:
            state = State.goingToPerson
            print ("X and Y are: " + str(x) + ", " + str(y) + " and width and height are: " + str(w) + ", " + str(h))

    if width != None and height != None:
        if width >= distanceThreshold:
            takePicture()
            tello.land()
            break
        else:
            tello.move_forward(35)
            time.sleep(1)


    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    time.sleep(1/FPS)

tello.land()
tello.streamoff()
cv2.destroyAllWindows()
sys.exit()
