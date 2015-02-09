2-8-15
send_stream
  -Streams video to stdout or network via TCP
  -Seems unstable, sometimes 8 FPS, sometimes 30 FPS on my machine (via wireless)
  -Tries to listen again after client socket is closed, but only works in some situations
  -Test with the following command line:  send_stream -d /dev/video0 -s -f -c 0
  
Live_Stream.py
  -displays video stream
  -can capture images from video stream
  -displays FPS, IP address and Port
  -can stop and start the stream, but send_stream has to be re-started
  
Many things hard coded in above files that will need to be configurable later on.
