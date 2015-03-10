#gst-launch rtspsrc location=rtsp://root:root@192.168.3.20:554/cam1/h264 ! decodebin ! autovideosink
#mjpeg
#gst-launch -v souphttpsrc location="`sed -n '2p' sources.txt`" do-timestamp=true is_live=true ! multipartdemux ! jpegdec ! ffmpegcolorspace ! autovideosink
#rtsp
#gst-launch -v rtspsrc location="`sed -n '2p' sources.txt`" debug=1 ! rtpmp4vdepay ! mpeg4videoparse ! ffdec_mpeg4 ! ffmpegcolorspace! autovideosink
ffplay 'rtsp://192.168.2.50:554/cam/realmonitor?channel=1&subtype=0&authbasic=YWRtaW46YWRtaW4=' &
ffplay -rtsp_transport tcp 'rtsp://192.168.2.50:554/cam/realmonitor?channel=1&subtype=1&authbasic=YWRtaW46YWRtaW4=' &
 
