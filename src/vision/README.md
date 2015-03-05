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

---

### Running the service
To run send_stream you need to tell it what device to use for the video feed.

Your camera device should show up in `/dev` as **videoN** where N could be and interger, usaully it's video0.

> Respberry Pi
>On the Raspberry Pi you will need to start the camera. You will need to install `uv4l` to do this. [See here for instructions](../blob/master/vision/raspberrypi-streaming.md). Once `uv4l` is installed run the following command to create the device file,  e.g. `/dev/video0`. 

```
uv4l --driver raspicam --auto-video_nr --extension-presence=1

# Test the camera with 
raspistill -o cam.jpg

```

Once you have a device file start the service with

```
# Adjust the /dev/video0 to whatever your device is
~/bin/send_stream -c0 -s -f -d /dev/video0

```

You should get output like this

```
Socket Send Buffer Size: 16384
Listening for a Client Connection
```

----



### Running the web app client

1. Change directories to `/src/webapp/`

1. Copy `config.template` to `config.local` and point it at the camera's IP address

2. Run `RCOG_HTTP.py`

3. If successful you should see output in the broswer at `http://<CAMERA-IP>:1337/` 


### Advanced Usage
1. To set debug levels (how much printout info you see), change the DEBUG variable at the top of RCOG_NET_LINK.py.  The bigger the number, the more printout you'll see.

2. To test connection to your bot without the HTTP server, set the TEST varialbe to True in RCOG_NET_LINK.py

2-9-15 -- Old

Live_Stream.py
  -displays video stream
  -can capture images from video stream
  -displays FPS, IP address and Port
  -can stop and start the stream, but send_stream has to be re-started

Many things hard coded in above files that will need to be configurable later on.

Live_Video_Server_Test.py hosts a simple html web page that shows video.  Frame rates are slow and very few clients can connect to the stream before it crashes.  Threading needs to be implemented to fix these problems.  IP addresses are hard coded.  Change for your LAN and html port connection desires.

