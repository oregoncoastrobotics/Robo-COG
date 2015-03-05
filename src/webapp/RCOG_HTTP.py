#!/usr/bin/python
#based on the ideas from http://synack.me/blog/implementing-http-live-streaming and https://gist.github.com/sakti/4761739

from wsgiref.simple_server import WSGIServer, make_server, WSGIRequestHandler
from SocketServer import ThreadingMixIn

import RCOG_NET_LINK

DEBUG = True

def debug (data):
	if DEBUG:
		print data

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

class HTTP_Server(object):
    def __init__ (self):
	self.bot = RCOG_NET_LINK.rcog_vid ()
 
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
        while True:
            yield self.mk_image ()

    def mk_image (self): #Generates the jpg image that goes to the browser
	self.bot.update ()

	return self.bot.current_frame

if __name__ == '__main__':
		#Launch an instance of wsgi server
		app = HTTP_Server()
		port = 1337
		debug ('Launching camera server on port: ' + str (port))
		httpd = create_server('', port, app) 
		try:
			debug ('Httpd serve forever')
			httpd.serve_forever()
		except KeyboardInterrupt:
			httpd.kill()
			debug ("Shutdown camera server ...")
