#!/usr/bin/python
#based on the ideas from http://synack.me/blog/implementing-http-live-streaming and https://gist.github.com/sakti/4761739
 
from Queue import Queue
from threading import Thread
import socket
import os.path
from select import select
from wsgiref.simple_server import WSGIServer, make_server, WSGIRequestHandler
from SocketServer import ThreadingMixIn
 
DEBUG = 1

class MyWSGIServer(ThreadingMixIn, WSGIServer):
     pass 
 
def create_server(host, port, app, server_class=MyWSGIServer,  
          handler_class=WSGIRequestHandler):
     return make_server(host, port, app, server_class, handler_class) 
 
INDEX_PAGE = """
<html>
<head>
    <title>Robot Vision</title>
</head>
<body>
<h1>Robot Vision Test</h1>
<img src="/mjpeg_stream" width="640" height="480"/>
<hr />
</body>
</html>
"""
ERROR_404 = """
<html>
  <head>
    <title>404 - Not Found</title>
  </head>
  <body>
    <h1>404 - Not Found</h1>
  </body>
</html>
"""
 
class rcog_vid (object):
	def __init__(self):
		self.config_name = "RCOG_Panel.config"
		self.IP = "192.168.1.108"
		self.Port = 27777
		self.host_base = ""
		self.capture_num = 0

		self.frame_buff = ''
		self.current_frame = ''

		self.status = "ON"
		self.connected = False

		self.Header_Start = "--rcognition\r\nContent-Type: image/jpeg\r\nContent-Length: "

		if not os.path.isfile(self.config_name):
			self.config_file = open (self.config_name, "w")
			self.config_file.close ()

		self.config_file = open (self.config_name, "r")
		self.config = self.config_file.read ().split ("\n")
		self.config_file.close ()

		for line in self.config:
			if "LAN_BASE:" in line:
				self.host_base = line.strip("LAN_BASE:").strip()

		self.init_net ()

		self.write_config ()
		
		self.debug_count = 0

		#DHT for MJPEG to JPG conversion
		self.Has_DHT = False
		self.DHT = \
			'\xFF\xC4\x01\xA2\x00\x00\x01\x05\x01\x01\x01\x01'\
			'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02'\
			'\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x01\x00\x03'\
			'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00'\
			'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'\
			'\x0A\x0B\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05'\
			'\x05\x04\x04\x00\x00\x01\x7D\x01\x02\x03\x00\x04'\
			'\x11\x05\x12\x21\x31\x41\x06\x13\x51\x61\x07\x22'\
			'\x71\x14\x32\x81\x91\xA1\x08\x23\x42\xB1\xC1\x15'\
			'\x52\xD1\xF0\x24\x33\x62\x72\x82\x09\x0A\x16\x17'\
			'\x18\x19\x1A\x25\x26\x27\x28\x29\x2A\x34\x35\x36'\
			'\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A'\
			'\x53\x54\x55\x56\x57\x58\x59\x5A\x63\x64\x65\x66'\
			'\x67\x68\x69\x6A\x73\x74\x75\x76\x77\x78\x79\x7A'\
			'\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94\x95'\
			'\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8'\
			'\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2'\
			'\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5'\
			'\xD6\xD7\xD8\xD9\xDA\xE1\xE2\xE3\xE4\xE5\xE6\xE7'\
			'\xE8\xE9\xEA\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9'\
			'\xFA\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05'\
			'\x04\x04\x00\x01\x02\x77\x00\x01\x02\x03\x11\x04'\
			'\x05\x21\x31\x06\x12\x41\x51\x07\x61\x71\x13\x22'\
			'\x32\x81\x08\x14\x42\x91\xA1\xB1\xC1\x09\x23\x33'\
			'\x52\xF0\x15\x62\x72\xD1\x0A\x16\x24\x34\xE1\x25'\
			'\xF1\x17\x18\x19\x1A\x26\x27\x28\x29\x2A\x35\x36'\
			'\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A'\
			'\x53\x54\x55\x56\x57\x58\x59\x5A\x63\x64\x65\x66'\
			'\x67\x68\x69\x6A\x73\x74\x75\x76\x77\x78\x79\x7A'\
			'\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94'\
			'\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7'\
			'\xA8\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA'\
			'\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4'\
			'\xD5\xD6\xD7\xD8\xD9\xDA\xE2\xE3\xE4\xE5\xE6\xE7'\
			'\xE8\xE9\xEA\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA'

	def write_config (self):
		self.config_file = open (self.config_name, "w")
		for line in self.config:
			if line.strip() != "":
				self.config_file.write (line + "\n")
		self.config_file.close ()

	def connect_rcog (self, addr,timeout):
		RCOG = 0
		self.cli_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
		self.cli_sock.settimeout(timeout)

		try:
			self.cli_sock.connect ((addr, self.Port))
			print "Possible RCOG at: " + addr
			RCOG = 1
		except:
			print addr + " is not RCOG"
			self.cli_sock.close ()

		if RCOG == 1:
			self.cli_sock.settimeout(1)
			intro_mesg = self.cli_sock.recv(2048)
			print intro_mesg.strip()
			if  intro_mesg[0:12] == "This is RCOG":
				print "Saying Hi"
				self.cli_sock.send ("Hello RCOG")
				self.connected = True
				self.IP = addr

	def init_net (self):
		#search for last rcog ip in config file
		for line in self.config:
			if "RCOG_IP:" in line:
				self.IP = line.strip ("RCOG_IP:").strip ()
				print "Trying to connect to RCOG at: " + self.IP
				self.connect_rcog (self.IP, 1)
				break

		#if we can't find rcog from config file, search local net
		while not self.connected:
			for i in range (0, 256):
				hostname = self.host_base + str (i)
				self.connect_rcog (hostname, 0.08)
				if self.connected:
					break

		#write last rcog ip into config file
		index = 0
		has_ip = False
		for line in self.config:
			if "RCOG_IP:" in line:
				self.config[index] = "RCOG_IP: " + self.IP
				has_ip = True
		index += 1
		if not has_ip:
			self.config.append ("RCOG_IP: " + self.IP)

	def close_net (self):
		self.cli_sock.close ()

	def stop (self):
		self.status = "OFF"
		self.close_net ()

	def start (self):
		self.init_net ()
		self.status = "ON"

	def capture (self):
		self.capture_num += 1
		pygame.image.save (self.image, "capture_image" + self.capture_num + ".jpg")

	def vid_recv (self):
		if len (self.frame_buff):
			self.frame_start = self.frame_buff.find ('\xFF\xD8')
		else:
			self.frame_start = -1
		
		self.frame_end = -1
		bytesinframe = 0

		while self.frame_start < 0 or self.frame_end < 0:
			chunk = self.cli_sock.recv(2048)

			if chunk == '':
				self.connected = False
				raise RuntimeError("socket connection broken")

			if self.frame_start < 0:
				self.frame_start = chunk.find ('\xFF\xD8')
			if self.frame_end < 0:
				self.frame_end = chunk.find ('\xFF\xD9')
			if self.frame_end >= 0:
				self.frame_end += len (self.frame_buff)
				

			self.frame_buff = self.frame_buff + chunk

		bytesinframe = self.frame_end - self.frame_start

		if self.frame_buff[self.frame_start + 2:self.frame_start + 4] != '\xFF\xC4':
			self.frame_buff = self.frame_buff[self.frame_start:self.frame_start + 2] + self.DHT + self.frame_buff[self.frame_start+2:]
			self.frame_end += len (self.DHT)


		self.current_frame = self.Header_Start + str(len(self.current_frame)) + "\r\n\r\n" + self.frame_buff[self.frame_start: self.frame_end + 2] + "\r\n"

		self.frame_buff = self.frame_buff [self.frame_end + 2:]
		
		if self.debug_count == 5:
			debug_file = open ("debug_image.test", "w")
			debug_file.write (self.current_frame)
			debug_file.close ()

	def update (self):
		if self.status == "ON":
			self.vid_recv ()
			return self.current_frame
		self.debug_count += 1

class IPCameraApp(object):
    def __init__ (self, bot):
	self.bot = bot
 
    def __call__(self, environ, start_response):    
        if environ['PATH_INFO'] == '/':
            start_response("200 OK", [
                ("Content-Type", "text/html"),
                ("Content-Length", str(len(INDEX_PAGE)))
            ])
            return iter([INDEX_PAGE])    
        elif environ['PATH_INFO'] == '/mjpeg_stream':
            return self.stream(start_response)
        else:
            start_response("404 Not Found", [
                ("Content-Type", "text/html"),
                ("Content-Length", str(len(ERROR_404)))
            ])
            return iter([ERROR_404])
 
    def stream(self, start_response):
        start_response('200 OK', [('Content-type', 'multipart/x-mixed-replace; boundary=--rcognition')])
        #self.bot.update ()
        while True:
            yield self.bot.update ()
        print 'Lost input stream from', self.bot.IP
 

if __name__ == '__main__':
	bot = rcog_vid ()
	if bot.connected:
		#Launch an instance of wsgi server
		app = IPCameraApp(bot)
		port = 1337
		print 'Launching camera server on port', port
		httpd = create_server('', port, app) 
		try:
			print 'Httpd serve forever'
			httpd.serve_forever()
		except KeyboardInterrupt:
			httpd.kill()
			print "Shutdown camera server ..."
