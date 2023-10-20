# this captures the mjpeg stream from my panasonic camera and display it as a window

# http://192.168.1.222/cam.cgi?mode=camcmd&value=capture  this takes a photo
# http://192.168.1.222/cam.cgi?mode=startstream&value=5555

## you will need python, numpy, pillow:
# download and install Python 3.x, then
# pip3 install numpy
# pip3 install Pillow

## the following also needs to be updated. figure it out on your own.
MY_IP = "192.168.1.166" ## THIS IS YOUR LOCAL IP ADDRESS
THEIR_IP = "192.168.1.222"  ## THIS IS THE IP ADDRESS OF THE CAMERA

import numpy as np
import socket
import PIL
import binascii
import threading
import time
import sys
from io import BytesIO

UDP_PORT = 5555
start = binascii.unhexlify(''.join('FF D8'.split()))
end = binascii.unhexlify(''.join('FF D9'.split()))
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((MY_IP, UDP_PORT))

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def bytes_to_ndarray(bytes):
    bytes_io = bytearray(bytes)
    img = Image.open(BytesIO(bytes_io))
    return np.array(img)
  
def keepalive(MY_IP, THEIR_IP):
    while True:
        try:
            tcpsock.sendto("GET /cam.cgi?mode=startstream&value=5555 HTTP/1.1\nHost: "+MY_IP+"\n\nUser-Agent:Mozilla 5.0\n", (MY_IP, 80))
            response = tcpsock.recv(1024)
            time.sleep( 8 )
            print("keep alive")
        except:
            tcpsock.connect(("192.168.1.222", 80))


thread = threading.Thread(target=keepalive, args=(MY_IP,THEIR_IP,))
thread.daemon = True
thread.start()

while (1==1):
    data, addr = sock.recvfrom(999999) # buffer size is 1024 bytes
    data = data.split(start)[1].split(end)[0]
    data = start+data+end
    data = np.array(np.frombuffer(data, np.uint8))
    data = bytearray(data)
    im = Image.open(BytesIO(data))
    im.show()

print("EXITING")
sys.exit()
