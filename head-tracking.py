## this captures the mjpeg stream from my panasonic camera and converts it into a video that is pushed to youtube.
## It will a
# http://192.168.1.222/cam.cgi?mode=camcmd&value=capture  this takes a photo
# http://192.168.1.222/cam.cgi?mode=startstream&value=5555 

## you will need python, numpy, opencv, and pygi

## for windows users, the following links provide the files need needed; things are relatively easy to install if you spend a few minutes on google
## https://www.python.org/download/releases/2.7/
## http://www.lfd.uci.edu/~gohlke/pythonlibs/
## https://sourceforge.net/projects/pygobjectwin32/files/
## Install pygi-aio-xxx ; install anything to do with gst-plugins or gstreamer

## the following also needs to be updated. figure it out on your own.
MY_IP = "192.168.1.121" ## THIS IS YOUR LOCAL IP ADDRESS 
THEIR_IP = "192.168.1.37"  ## THIS IS THE IP ADDRESS OF THE CAMERA
RTMP_OUT = "rtmp://a.rtmp.youtube.com/live2/x/steve.4txa-37t5-jk1e-e5bx"

import numpy as np
import socket
import cv2
import binascii
import threading
import time
import sys
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer


UDP_PORT = 15555
start = binascii.unhexlify(''.join('FF D8'.split()))
end = binascii.unhexlify(''.join('FF D9'.split()))
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((MY_IP, UDP_PORT))

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.connect((THEIR_IP, 80))

class myHandler(BaseHTTPRequestHandler):
	def do_GET(self):
	
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				data, addr = sock.recvfrom(999999) # buffer size is 1024 bytes
				data = data.split(start)[1].split(end)[0]
				data = start+data+end  
				#data = np.frombuffer(data, np.uint8) # to array
				#data = cv2.imdecode(np.array(data),1) #
				#print(np.shape(data)) ## uncomment to see resolution of video
				#cv2.imshow("img",data) ## 4K Video Mode = 640x360, but photo mode is 640x480 ..  
				#cv2.waitKey(1)
				self.wfile.write("--jpgboundary".encode('utf-8'))
				self.send_header('Content-type','image/jpeg')
				self.send_header('Content-length',str(len(data)))
				self.end_headers()
				self.wfile.write(data)
		elif self.path.endswith('.html'):
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write('<html><head><script src="https://stevesserver.com:82/headtrackr.js"></script></head><body style="border:0;margin:0;padding:0;">'.encode('utf-8'))
			self.wfile.write(('<img src="cam.mjpg" id="inputVideo" id="inputVideo" width=640/>\
				<canvas id="inputCanvas" width="640" height="480" style="display:none;"></canvas>\
				<canvas id="overlay" width="640" height="480" style="position: absolute; top: 0px; z-index: 100001; display: block;"></canvas>\
				<script type="text/javascript">\
				  var videoInput = document.getElementById("inputVideo");\
				  var canvasInput = document.getElementById("inputCanvas");\
				  var htracker = new headtrackr.Tracker();\
				  htracker.init(videoInput, canvasInput, false);\
				  htracker.start();\
				    var canvasOverlay = document.getElementById("overlay");\
					var overlayContext = canvasOverlay.getContext("2d");\
					document.addEventListener("facetrackingEvent", function( event ) {\
						overlayContext.clearRect(0,0,640,480);\
						if (event.detection == "CS") {\
							overlayContext.translate(event.x, event.y);\
							overlayContext.rotate(event.angle-(Math.PI/2));\
							overlayContext.strokeStyle = "#00CC00";\
							overlayContext.strokeRect((-(event.width/2)) >> 0, (-(event.height/2)) >> 0, event.width, event.height);\
							overlayContext.rotate((Math.PI/2)-event.angle);\
							overlayContext.translate(-event.x, -event.y);\
						}\
					});\
				</script>\
			').encode('utf-8'))
			self.wfile.write('</body></html>'.encode('utf-8'))
			return
			
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
	pass

def keepalive(MY_IP, THEIR_IP):
	while True:
		try:
			tcpsock.sendto(("GET /cam.cgi?mode=startstream&value="+str(UDP_PORT)+" HTTP/1.1\nHost: "+THEIR_IP+"\n\nUser-Agent:Mozilla 5.0\n").encode(), (THEIR_IP, 80))
			print("k")
			response = tcpsock.recv(1024)
			time.sleep( 8 )
			print("keep alive")
		except Exception as E:
			print(E)
			tcpsock.connect((THEIR_IP, 80))
	
print("keey")
thread = threading.Thread(target=keepalive, args=(MY_IP,THEIR_IP,))
thread.daemon = False
thread.start()
print("starting")
total=0

remote_Server = ThreadedHTTPServer(("", 80), myHandler)
#remote_Server.socket = ssl.wrap_socket(remote_Server.socket, keyfile=key_pem, certfile=chain_pem, server_side=True)
remote_Server.serve_forever()
	

print("EXIT")
sys.exit()