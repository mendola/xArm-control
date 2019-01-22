import socket
import sys
import struct
import pickle
import cv2

RPI_IP = "192.168.1.110"
server_address = (RPI_IP, 8487)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)

data = b""
payload_size = struct.calcsize(">L")
try:
    while True:
        while len(data) < payload_size:
            data += sock.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += sock.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow('ImageWindow',frame)
        cv2.waitKey(1)
except:
    print("Failure. Closing")
    cv2.destroyAllWindows()
    sock.close()