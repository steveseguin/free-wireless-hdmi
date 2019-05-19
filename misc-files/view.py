import socket
import cv2
import binascii
import numpy as np
import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

UDP_IP = "192.168.1.121"
UDP_PORT = 5555

start = binascii.unhexlify(''.join('FF D8'.split()))
end = binascii.unhexlify(''.join('FF D9'.split()))

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
while True:
	cv2.waitKey(1)
	data, addr = sock.recvfrom(999999) # buffer size is 1024 bytes
	#print data.count(start)
	#print data.count(end)
	print "."
	#print len(data)
	data = data.split(start)[1].split(end)[0]
	data = start+data+end
	#print len(data)
	data = np.frombuffer(data, np.uint8)
	
	data = cv2.imdecode(np.array(data),cv2.CV_LOAD_IMAGE_COLOR)
	data = cv2.resize(data, (0,0), fx=3., fy=3.) 
	#print np.shape(data)
	cv2.imshow("jpeg",data)
	#print "received message:", data