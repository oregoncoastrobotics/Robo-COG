#!/usr/bin/python
 
import socket
import os.path

TEST = False
DEBUG = 1

def debug (data, number):
	if number <= DEBUG:
		print data
 
class rcog_vid (object):
	def __init__(self):
		self.config_name = "config.local"
		self.IP = "192.168.1.108"
		self.Port = 27777
		self.host_base = ""
		self.capture_num = 0
		self.frame_count = 0

		self.current_frame = ''
		self.next_frame = ''

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
		
		#DHT for MJPEG to JPG conversion
		self.has_DHT = False
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
			debug ("Possible RCOG at: " + addr, 1)
			RCOG = 1
		except:
			debug (addr + " is not RCOG", 2)
			self.cli_sock.close ()

		if RCOG == 1:
			self.cli_sock.settimeout(1)
			intro_mesg = self.cli_sock.recv(2048)
			debug (intro_mesg.strip(), 2)
			if  intro_mesg[0:12] == "This is RCOG":
				debug ("Saying Hi", 2)
				self.cli_sock.send ("Hello RCOG")
				self.connected = True
				self.IP = addr

	def init_net (self):
		#search for last rcog ip in config file
		for line in self.config:
			if "RCOG_IP:" in line:
				self.IP = line.strip ("RCOG_IP:").strip ()
				debug ("Trying to connect to RCOG at: " + self.IP, 1)
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
		#If buffer contains beginning of this frame (left from last chunk of last frame)
		if self.next_frame != '':
			self.current_frame = self.next_frame

		#reset next frame buffer
		self.next_frame = ''

		frame_end = -1
		frame_start = -1

		#The while loop below assembles frame data from chunks received 
		#This assembly of frame data is based on the fact that TCP data should always arrive in-order to the application
		while frame_end < 0:
			chunk = self.cli_sock.recv(2048)

			#if no data is received connectionn is broken
			if chunk == '':
				self.connected = False
				raise RuntimeError("socket connection broken")


			#Find the beginning of the frame, it should start with FFD8
			if '\xFF\xD8' in chunk:
				frame_start = chunk.find ('\xFF\xD8')
				debug ("found start at: " + str (frame_start), 3)
			else:
				frame_start = -1
			if '\xFF\xD9' in chunk:
				frame_end = chunk.find ('\xFF\xD9')
				debug ("found end at: " + str (frame_end), 3)
			else:
				frame_end = -1

			if frame_start >= 0 and frame_end >= 0:
				debug ("frame start and end in same packet", 3)
				self.current_frame = self.current_frame + chunk[:frame_end + 2]  #include the FFD9 frame end
				self.next_frame = chunk[frame_start:]

			elif frame_start >= 0:
				debug  ("only frame start", 3)
				self.current_frame = chunk [frame_start:]

			elif frame_end >= 0:
				debug ("only frame end", 3)
				self.current_frame = self.current_frame + chunk[:frame_end + 2]  #include the FFD9 frame end

			else:
				debug ("only frame data", 3)
				self.current_frame = self.current_frame + chunk


		#Insert DHT table into frame buffer if it is missing
		if self.frame_count == 1:
			if self.current_frame.find ('\xFF\xC4') >= 0:
				self.has_DHT = True

		if not self.has_DHT:
			self.current_frame = '\xFF\xD8' + self.DHT + self.current_frame[2:]

		#save the first 10 image frames for debug
		if self.frame_count < 11 and DEBUG > 2:
			debug_file = open ("debug_image" + str(self.frame_count) + ".jpg", "w")
			debug_file.write (self.current_frame)
			debug_file.close ()

		#Add stream header to current frame
		self.current_frame = self.Header_Start + str(len(self.current_frame)) + "\r\n\r\n" + self.current_frame + "\r\n"

	def update (self):
		self.frame_count += 1
		if self.status == "ON":
			self.vid_recv ()
			return self.current_frame
		
if __name__ == '__main__' and TEST:
	bot = rcog_vid ()
	while bot.connected and bot.frame_count < 10:
		bot.update ()
	bot.stop ()
