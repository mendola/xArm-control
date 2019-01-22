import numpy as np
import cv2

import socket
import sys
import struct
import pickle
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cap = cv2.VideoCapture(0)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

# Bind the socket to the port
server_address = ('', 8487)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
sock.listen(10)
print("Listening...")
conn, client_addr = sock.accept()


print("Starting Camera loop")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(frame, 0)
        conn.sendall(struct.pack(">L", len(data))+data) ### new code
except:
    print("Failure. Closing")
    cap.release()
    sock.close()