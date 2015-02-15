#!/usr/bin/python
#based on the ideas from http://synack.me/blog/implementing-http-live-streaming and https://gist.github.com/sakti/4761739
 
from Queue import Queue
from threading import Thread
import socket
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
 
class net_vid:
	def __init__(self):
		self.boarder_size = 10
		self.boarder_color = (200, 200, 200)
		self.frame_size = (640,480)
		self.IP = "192.168.1.108"
		self.Port = 27777

		self.init_net ()

		self.frame_buff = ''
		self.current_frame = ''

		self.status = "ON"

		self.Header_Start = "--rcognition\r\nContent-Type: image/jpeg\r\nContent-Length: "

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


	def init_net (self):
		self.cli_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
		self.cli_sock.connect ((self.IP, self.Port))

	def close_net (self):
		self.cli_sock.close ()

	def stop (self):
		self.status = "OFF"
		self.close_net ()

	def start (self):
		self.init_net ()
		self.status = "ON"

	def capture (self):
		pygame.image.save (self.image, "capture_image.jpg")

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

	def update (self):
		if self.status == "ON":
			self.vid_recv ()
			return self.current_frame

bots = [net_vid ()]
class IPCameraApp(object):
 
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
        bots[0].update ()
        while True:
            yield bots[0].update ()
        print 'Lost input stream from', bots[0].IP
 

if __name__ == '__main__':
 
    #Launch an instance of wsgi server
    app = IPCameraApp()
    port = 1337
    print 'Launching camera server on port', port
    httpd = create_server('', port, app)
 
    try:
        print 'Httpd serve forever'
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.kill()
        print "Shutdown camera server ..."
