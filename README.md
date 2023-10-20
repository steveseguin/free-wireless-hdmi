# Free Wireless HDMI for Panasonic Lumix cameras (g85 tested)
Turn your wifi-enabled Camera into a wireless webcam for youtube, obs, etc.

This initial software release is designed for LUMIX cameras that have wifi-enabled (G85 in particular, but also GX80, GH4, GH3, and perhasp the GH5?)  It can be extended to support many other wifi-enabled cameras -- from GoPros to Sony AR7s, but those are not supported atm.

sample result and release video: https://www.youtube.com/watch?v=fhfLvUgQ9SU

## To install this

[updated option] if using the new window display option instead, just Python 3.x, Numpy, and Pillow needed. Use the `windowcap.py` script.

This should work for Windows users, without needing GI or OpenCV, but rather just the accessible Pillow addon for Python 3.  The code is also updated for Python 3 support

[obsolete option] 
install the required software (python 2.7 + numpy + openCV + pygi .. ) on a computer that is connected to a router.

for windows users, the following links provide the files need needed; things are relatively easy to install if you spend a few minutes on google
```
https://www.python.org/download/releases/2.7/
http://www.lfd.uci.edu/~gohlke/pythonlibs/
https://sourceforge.net/projects/pygobjectwin32/files/ ; Install pygi-aio-xxx ; install anything to do with gst-plugins or gstreamer
```

## To set it up

Next, connect your wifi Camera to the same router used by your computer. Check the manual.

Check your camera to see what it's IP is. Also find out what the IP address of your computer is.
(IP is listed deep in the settings of your camera, but it might also be listed in your router's admin page)

Update the python script with the two IP addresses.

If pushing to Youtube, update the stream key in the publishRTMP.py to match your own stream key. (youtube.com/live_dashboard)

## run the script:

`python windowcap.py.py` if using the window capture method
or 
`python publishRTMP.py` if publishing via rtmp (obsolete option)

Your camera will likely output a 640x360 or 640x480 stream; this is typically used for previewing the camera on your smartphone. It is a series of jpeg images, streaming in fast succession. This program simply grabs them out of the air and turns them into a video, adds audio, and pushes them to the internet as a h264 video stream.  

There is a lot to fiddle with if you want, but it's not easy to get things right. Lumix cameras in particular need to be activated with an HTTP request to get a stream started, and again later to keep it going. Lumix cameras also seperate images with unique bits of data -- different brands of cameras will inject their own stuff inbetween video frames as well, or nothing at all. 

Since it's hard to produce videos with this tool; as the video streams go straight to the internet, I would recommend you check out http://stageten.tv if you want more production control -- Stageten is a cloud-based live video production service that lets your send multiple live video streams to their servers (one perhaps being a Lumix video stream) -- where you can then edit, mix, and publish your videos in real-time --- pushing them also live to Facebook, Youtube, Twitch and other sites easily. You can also mix and match video inputs; smartphones, webcams, vod, etc.

