#gst-launch rtspsrc location=`head -n 1 sources.txt` ! decodebin ! mpegtsmux ! filesink location=file.mpeg
#gst-launch-0.10 -e rtspsrc location="`head -n 1 sources.txt`" !  mp4mux ! filesink location=video.mkv

#gst-launch-0.10 -e rtspsrc location=`head -n 1 sources.txt` ! rtpmp4vdepay ! mpeg4videoparse ! gdppay ! filesink location=/tmp/test.gdp
#gst-launch-0.10 udpsrc multicast-group=224.1.1.1 auto-multicast=true
#port=5010 caps='application/x-rtp, media=(string)video,
#clock-rate=(int)90000, encoding-name=(string)H264,
#sprop-parameter-sets=(string)\"Z0KAHukBQHpCAAAH0AAB1MAIAA\\=\\=\\,aM48gAA\\=\",
#payload=(int)96, ssrc=(uint)3315029550, clock-base=(uint)3926529534,
#seqnum-base=(uint)45576' ! gstrtpjitterbuffer drop-on-latency=true
#latency=10 ! rtph264depay ! ffdec_h264 ! x264enc ! matroskamux ! filesink
#location=movie.mkv

#gst-launch rtspsrc location=`head -n 1 sources.txt` ! decodebin ! mpegtsmux ! filesink location=$1
#ffmpeg -i `head -n 1 sources.txt` -vcodec copy -t 30 -y -r 15 $1
gst-launch-0.10 rtspsrc location=`head -n 1 sources.txt` !  rtph264depay  ! capsfilter caps="video/x-h264,width=640,height=480,framerate=(fraction)15/1" !  mp4mux ! filesink location=dump.mp4
