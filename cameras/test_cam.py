import numpy as np
import cv2
import socket

UDP_IP = "" # Any ?
UDP_PORT = 5005

cap = cv2.VideoCapture(1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    #cv2.imshow('frame',gray)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break
    sock.sendto("Frame Captured", (UDP_IP, UDP_PORT))

# When everything done, release the capture
cap.release()