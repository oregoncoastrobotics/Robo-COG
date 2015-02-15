2-9-15

Live_Stream.py
  -displays video stream
  -can capture images from video stream
  -displays FPS, IP address and Port
  -can stop and start the stream, but send_stream has to be re-started

Many things hard coded in above files that will need to be configurable later on.

Live_Video_Server_Test.py hosts a simple html web page that shows video.  Frame rates are slow and very few clients can connect to the stream before it crashes.  Threading needs to be implemented to fix these problems.  IP addresses are hard coded.  Change for your LAN and html port connection desires.
