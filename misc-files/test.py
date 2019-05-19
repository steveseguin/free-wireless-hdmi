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

UDP_IP = "192.168.1.121"
UDP_PORT = 5555
start = binascii.unhexlify(''.join('FF D8'.split()))
end = binascii.unhexlify(''.join('FF D9'.split()))
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

frame = np.zeros((360,640,3)).astype("uint8")
frame[20:50,:,0]=255
frame[60:80,:,1]=255
frame[100:120,:,2]=255
frame = frame.tostring()

connected=False


def socket_listener():
	global frame,connected,appsrc,sock,start,end
	total=0
	while (1==1):
		#global data,start,stop,appsrc
		begin = time.time()
		data, addr = sock.recvfrom(999999) # buffer size is 1024 bytes
		connected=True
		#print "data recieved"
		#print data.count(start)
		#print data.count(end)
		#print len(data)
		data = data.split(start)[1].split(end)[0]
		data = start+data+end  # string
		###############################
		data = np.frombuffer(data, np.uint8) # to array
		data = cv2.imdecode(np.array(data),cv2.CV_LOAD_IMAGE_COLOR) #
		data[20:50,:,:]=255
		#data = cv2.resize(data, (0,0), fx=3., fy=3.)
		frame = data.tostring()
		#############################
		#print len(data)
		#print "updated socket"
		#data = "1234" * 12
		#buf = Gst.Buffer.new_allocate(None, len(frame), None)
		#buf.fill(0,frame)
		#appsrc.emit("push-buffer", buf)
		final = time.time()
		total = total*0.8 + (final - begin)*.2
		print "time",str(1.0/total)
	print "FAIL"
	sys.exit()

def need_new_buffer(appsrc,need_bytes):
	global frame
	#print "empty"
	buf = Gst.Buffer.new_allocate(None, len(frame), None)
	buf.fill(0,frame)
	appsrc.emit("push-buffer", buf)

# def YUV_stream2RGB_frame(data):

    # w=640
    # h=360
    # size=w*h

    # stream=np.fromstring(data,np.uint8) #convert data form string to numpy array

    # #Y bytes  will start form 0 and end in size-1 
    # y=stream[0:size].reshape(h,w) # create the y channel same size as the image

    # #U bytes will start from size and end at size+size/4 as its size = framesize/4 
    # u=stream[size:(size+(size/4))].reshape((h/2),(w/2))# create the u channel  itssize=framesize/4

    # #up-sample the u channel to be the same size as the y channel and frame using pyrUp func in opencv2
    # u_upsize=cv2.pyrUp(u)

    # #do the same for v channel 
    # v=stream[(size+(size/4)):].reshape((h/2),(w/2))
    # v_upsize=cv2.pyrUp(v)

    # #create the 3-channel frame using cv2.merge func watch for the order
    # yuv=cv2.merge((y,u_upsize,v_upsize))

    # #Convert TO RGB format
    # rgb=cv2.cvtColor(yuv,cv2.cv.CV_YCrCb2RGB)

    # #show frame
    # cv2.imshow("show",rgb)
    # cv2.waitKey(5)

# def on_new_buffer(appsink):
	# #print "data sent thru"
	# sample = appsink.emit('pull-sample')
	# #get the buffer
	# buf=sample.get_buffer()
	# #extract data stream as string
	# data=buf.extract_dup(0,buf.get_size())
	# #YUV_stream2RGB_frame(data)
	
	# img = np.frombuffer(data, np.uint8)
	# #if len(data)<360*640*3:
	# #	print "too short to be valid:",str(len(img))
	# #	return False
	# #img = np.array(img).reshape(360,640,3)
	# try:
		# print "GOT DATA",str(len(img))
		# #img = cv2.imdecode(np.array(img),cv2.CV_LOAD_IMAGE_COLOR)
	# except:
		# print "failed to decode"
		# return
	# #data = cv2.resize(data, (0,0), fx=3., fy=3.)
	# #cv2.imshow("jpeg",img)
	# #cv2.waitKey(1)
	# return False

  
CLI='appsrc name=mysource ! video/x-raw,format=BGR,width=640,height=360,framerate=(fraction)30/1,pixel-aspect-ratio=(fraction)1/1 ! queue ! \
videoconvert ! queue ! capsfilter caps="video/x-raw,format=I420" ! queue ! \
videoscale ! queue ! capsfilter caps="video/x-raw,width=640,height=360" ! queue ! \
tee name=RAW RAW. ! queue ! autovideosink RAW. ! queue ! \
x264enc cabac=true aud=true tune=zerolatency byte-stream=false sliced-threads=true threads=0 speed-preset=1 bitrate=1200 key-int-max=20 bframes=0 ! \
h264parse ! video/x-h264,profile=main ! queue max-size-buffers=10  ! mux. autoaudiosrc ! audioconvert ! \
voaacenc bitrate=64000 ! aacparse ! audio/mpeg,mpegversion=4,stream-format=raw ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=1130000000 ! \
flvmux streamable=true name=mux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/x/steve.4txa-37t5-jk1e-e5bx"'

#simplest way to create a pipline
pipline=Gst.parse_launch(CLI)

#getting the sink by its name set in CLI
appsrc=pipline.get_by_name("mysource")
#appsink=pipline.get_by_name("sink")

appsrc.set_property('emit-signals',True) #tell sink to emit signals

#setting some important properties of appsnik
#appsink.set_property("max-buffers",20) # prevent the app to consume huge part of memory
#appsink.set_property('emit-signals',True) #tell sink to emit signals
#appsink.set_property('sync',False) #no sync to make decoding as fast as possible

#appsink.connect('new-sample', on_new_buffer) #connect signal to callable func // commented out for now
appsrc.connect('need-data', need_new_buffer)

pipline.set_state(Gst.State.PLAYING)

##############
thread = threading.Thread(target=socket_listener)
thread.daemon = True
thread.start()
##########

data = np.zeros((360,640,3)).astype("uint8")
row,col,ch = data.shape
counter=0
color=0
while (1==1):
	if connected==False:
		counter+=1
		data[counter%360,:,:] +=128
		frame = data.tostring()
		#cv2.imshow("a",data)
		#cv2.waitKey(1)
		#print "new"
		#buf = Gst.Buffer.new_allocate(None, len(frame), None)
		#buf.fill(0,frame)
		#appsrc.emit("push-buffer", buf)
		time.sleep(1.0/30)
	else:
		connected=False
		time.sleep(5.0)
