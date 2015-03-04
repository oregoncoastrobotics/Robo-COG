## send_stream
  
Streams video to stdout or network via TCP

### Install and Build

* Clone the repo.
```
mkdir ~/projects
cd ~/projects
git clone https://github.com/oregoncoastrobotics/Robo-COG.git

~/projects/Robo-COG/vision/send_stream/installer.sh

```

This will put the built file named `send_stream` in `~/bin/`.


### Running the service
To run send_stream you need to tell it what device to use for the video feed.

Your camera device should show up in `/dev` as **videoN** where N could be and interger, usaully it's video0.

> Respberry Pi
>On the Raspberry Pi you will need to start the camera. You will need to install `uv4l` to do this. [See here for instructions](../blob/master/vision/raspberrypi-streaming.md). Once `uv4l` is installed run the following command to create the device file,  e.g. `/dev/video0`. 

```
uv4l --driver raspicam --auto-video_nr --extension-presence=1
```




```
# Adjust the /dev/video0 to whatever your device is
`~/bin/send_stream -c0 -s -f -d /dev/video0`.

```

You should get output like this

```
Socket Send Buffer Size: 16384
Listening for a Client Connection
```

You will run the client in `Robo-COG/30-Software_Design/100-Control Panel`




I cd to ~ make a bin directory (mkdir bin) then copy the build_send_stream and send_stream.c files to ~ and run build_send_stream

send_stream -c0 -s -f -d /dev/video0



2-8-15
send_stream
  -Streams video to stdout or network via TCP
  -Seems unstable, sometimes 8 FPS, sometimes 30 FPS on my machine (via wireless)
  -Tries to listen again after client socket is closed, but only works in some situations
  -Test with the following command line:  send_stream -d /dev/video0 -s -f -c 0
  

  
Many things hard coded in above files that will need to be configurable later on.

2-9-15
  -Sability problem seems to be have been with receiving app, stable at 30FPS now
  -Added cross-compiles rpi binary to bin
  -Test with the following command line:  send_stream -d /dev/video0 -s -f -c 0
  -Would like to change to config file rather than command line at some point
  -Need to add support for other video types/settings and negotiation with control panel
