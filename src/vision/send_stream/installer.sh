#!/bin/bash

sudo apt-get install build-essential -y
sudo apt-get install pkg-config -y
sudo apt-get install linux-libc-dev -y
sudo apt-get install libv4l-dev -y

mkdir ~/bin
mkdir /tmp

cp build_send_stream.sh /tmp
cp send_stream.c /tmp

# You may need to adjust 
/tmp/build_send_stream.sh
cp /tmp/send_stream ~/bin

