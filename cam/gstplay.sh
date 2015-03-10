#gst-launch-1.0 -v rtspsrc location=`sed -n '2p' sources.txt` ! decodebin debug=1 ! autovideosink
#mjpeg
#gst-launch -v souphttpsrc location="`sed -n '1p' sources.txt`" do-timestamp=true is_live=true ! multipartdemux ! jpegdec ! ffmpegcolorspace ! autovideosink
#rtsp
#gst-launch -v rtspsrc location="`sed -n '2p' sources.txt`" debug=1 ! rtpmp4vdepay ! mpeg4videoparse ! ffdec_mpeg4 ! ffmpegcolorspace! autovideosink
#ffplay 'rtsp://admin:4502@192.168.2.40:554/cam/realmonitor?channel=2&subtype=0' &
 
#gst-launch-1.0 -v rtspsrc location="`sed -n '2p' sources.txt`" ! rtph264depay ! rtph264pay ! udpsink sync=false host=localhost port=554
gst-launch-1.0 -v rtspsrc location="`sed -n '2p' sources.txt`" ! decodebin ! rtph264pay ! udpsink sync=false host=localhost port=554

#caps
# application/x-rtp, media='video'
gst-launch-1.0 udpsrc caps="application/x-rtp, media=(string)video,clock-rate=(int)90000, encoding-name=(string)H263-1998" ! rtpjitterbuffer latency=100 ! rtph263pdepay !  avdec_h263 ! autovideosink
gst-launch-1.0 v4l2src ! videoconvert ! avenc_h263p ! rtph263ppay ! udpsink

v=0
m=video 5000 RTP/AVP 96
c=IN IP4 127.0.0.1
a=rtpmap:96 MP4V-ES/90000

gst-launch videotestsrc ! ffenc_mpeg4 ! rtpmp4vpay send-config=true ! udpsink host=127.0.0.1 port=5000

