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
cap.set(3,320)
cap.set(4,240)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

# Bind the socket to the port
server_address = ('', 8487)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
sock.listen(10)
print("Listening...")
conn, client_addr = sock.accept()


print("Starting Camera loop")
while True:
    #print('\nwaiting to receive message')
    #print('received {} bytes from {}'.format(len(data), address))
    #print(data)

    ret, frame = cap.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    data = pickle.dumps(frame, 0)
   # sock.sendto(data, address)
    #sock.sendall(struct.pack(">L", len(data))+data) ### new code
    sock.sendall(b'hello')
    time.sleep(1)
cap.release()