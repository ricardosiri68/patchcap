gst-launch souphttpsrc location=http://patchcap:patchpac@192.168.3.20/mjpg/video.mjpg timeout=5 ! jpegdec ! glimagesink force-aspect-ratio=true
