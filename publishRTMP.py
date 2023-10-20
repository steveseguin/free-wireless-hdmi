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
MY_IP = "192.168.1.166" ## THIS IS YOUR LOCAL IP ADDRESS 
THEIR_IP = "192.168.1.222"  ## THIS IS THE IP ADDRESS OF THE CAMERA
RTMP_OUT = "rtmp://a.rtmp.youtube.com/live2/x/steve.4txa-37t5-jk1e-e5bx"

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
import numpy as np
import socket
import cv2
import binascii
import threading
import time
import sys


GObject.threads_init()
Gst.init(None)
UDP_PORT = 5555
start = binascii.unhexlify(''.join('FF D8'.split()))
end = binascii.unhexlify(''.join('FF D9'.split()))
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((MY_IP, UDP_PORT))

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## ## 4K Video Mode = 640x360, but photo mode is 640x480 ..    adust the below line accordingly. It's currently set for 640x360, but will scale the output up to 1280x720.
## min-threshold-time=1130000000 can be adjusted to get the audio/video sink more aligned. It should be pretty close as is.
CLI='appsrc name=mysource format=TIME do-timestamp=TRUE is-live=TRUE caps="video/x-raw,format=BGR,width=640,height=360,framerate=(fraction)30/1,pixel-aspect-ratio=(fraction)1/1" ! videoconvert ! videoscale ! videorate ! capsfilter caps="video/x-raw,format=I420,width=1280,height=720,framerate=(fraction)30/1" ! queue max-size-time=0 max-size-bytes=0 max-size-buffers=0 ! tee name=RAW RAW. ! queue max-size-time=0 max-size-bytes=0 max-size-buffers=0 ! autovideosink sync=false RAW. ! queue  max-size-time=0 max-size-bytes=0 max-size-buffers=0 ! x264enc cabac=true aud=true tune=zerolatency byte-stream=false sliced-threads=true threads=4 speed-preset=1 bitrate=2000 key-int-max=20 bframes=0 ! h264parse ! video/x-h264,profile=main ! mux. autoaudiosrc ! audioconvert ! voaacenc bitrate=128000 ! queue  max-size-time=0 max-size-bytes=0 max-size-buffers=0 ! aacparse ! audio/mpeg,mpegversion=4,stream-format=raw ! queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 min-threshold-time=1140000000 ! flvmux streamable=true name=mux ! queue max-size-buffers=3 max-size-time=0 max-size-bytes=0 ! rtmpsink location="'+RTMP_OUT+'" sync=false'

pipline=Gst.parse_launch(CLI)

appsrc=pipline.get_by_name("mysource")
#appsink=pipline.get_by_name("sink")
appsrc.set_property('emit-signals',True) #tell sink to emit signals

pipline.set_state(Gst.State.PLAYING)

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

total=0
while (1==1):
	#begin = time.time()
	data, addr = sock.recvfrom(999999) # buffer size is 1024 bytes
	data = data.split(start)[1].split(end)[0]
	data = start+data+end  
	data = np.frombuffer(data, np.uint8) # to array
	data = cv2.imdecode(np.array(data),cv2.CV_LOAD_IMAGE_COLOR) #
	#print np.shape(data) ## uncomment to see resolution of video
	#cv2.imshow("img",data) ## 4K Video Mode = 640x360, but photo mode is 640x480 ..  
	#cv2.waitKey(1)
	frame = data.tostring()
	buf = Gst.Buffer.new_allocate(None, len(frame), None)
	buf.fill(0,frame)
	appsrc.emit("push-buffer", buf)
	#final = time.time()
	#total = total*0.8 + (final - begin)*.2
	#print "time",str(1.0/total)
print("EXIT")
sys.exit()
