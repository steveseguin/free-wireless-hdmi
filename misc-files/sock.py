from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import socket
import cv2
import binascii
import numpy as np
import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

start = binascii.unhexlify(''.join('FF D8'.split()))
end = binascii.unhexlify(''.join('FF D9'.split()))


class SimpleEcho(WebSocket):

    def handleMessage(self):
		# echo message back to client
		self.sendMessage(self.data)
		if len(self.data)>1000:
			print "."
			data = binascii.a2b_base64(self.data)
			print "."
			data = binascii.hexlify(data)
			print "."
			data =  str(data)
			print "."
			#data = start+data.split(start)[1].split(end)[0]+end
			#print "."
			data = np.frombuffer(data, np.uint8)
			print "."
			data = cv2.imdecode(np.array(data),cv2.CV_LOAD_IMAGE_COLOR)
			print "."
			#data = cv2.resize(data, (0,0), fx=3., fy=3.) 
			#print np.shape(data)
			cv2.imshow("jpeg",data)
			cv2.waitKey(1)
		else:
			print "not image"
		
    def handleConnected(self):
		print self.address, 'connected'

    def handleClose(self):
		print self.address, 'closed'

		
server = SimpleWebSocketServer('', 8000, SimpleEcho)
server.serveforever()
