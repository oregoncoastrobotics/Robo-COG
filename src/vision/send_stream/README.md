To build send_stream I started with a debian based system and did the following:

Download this repo and run `Robo-COG/30-Software_Design/10-Vision/send_steam/installer.sh`

This will create a `bin/` directory in your root folder. 


Then run `~/bin/send_stream -c0 -s -f -d /dev/video0`. You may need ot adjust the video0.

You should get output like this

```
Socket Send Buffer Size: 16384
Listening for a Client Connection
```

You will run the client in `Robo-COG/30-Software_Design/100-Control Panel`


## OLD DOCS
Installed the build-essential package (sudo apt-get install build-essential), which includes gcc and standard c libraries
Installed the pkg-config package
Installed the linux-kernel-headers package which turns out was linux-libc-dev and was already installed (by build-essentials?)
Installed the libv4l-dev package

I cd to ~ make a bin directory (mkdir bin) then copy the build_send_stream and send_stream.c files to ~ and run build_send_stream

send_stream -c0 -s -f -d /dev/video0

