import pygame
import socket
import time
import cStringIO

DEBUG_LVL = 0

pygame.init ()

screen_size = (1024, 768)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Bot1')

class button_actions:
	def start (self):
		bot1_vid.start ()
	def stop (self):
		bot1_vid.stop ()
	def capture (self):
		bot1_vid.capture ()

class buttons:
	def __init__ (self, function, text = ""):
		self.function = function
		self.text = text
		self.font_size = 20
		self.font = pygame.font.Font(None, self.font_size)
		self.image = pygame.Surface ((150, 60))
		self.pressed_image = pygame.image.load ("button1.png")
		self.unpressed_image = pygame.image.load ("button2.png")
		self.rect = self.image.get_rect ()
		
		self.pressed_color = (100, 100, 100)
		self.unpressed_color = (50, 50, 50)
		self.pressed = False

		self.button_setup ()

	def button_setup (self):
		self.image.blit (self.unpressed_image, (0, 0))
		txt_img = self.font.render(self.text, 1, self.unpressed_color)
		txt_rect = txt_img.get_rect (center = (self.rect.width/2, self.rect.height/2))
		self.image.blit (txt_img, txt_rect)

	def update (self):
		pos = pygame.mouse.get_pos ()
		if self.rect.collidepoint (pos) and pygame.mouse.get_pressed ()[0] and self.pressed == False:
			self.image.blit (self.pressed_image, (0, 0))
			txt_img = self.font.render(self.text, 1, self.pressed_color)
			txt_rect = txt_img.get_rect (center = (self.rect.width/2, self.rect.height/2))		
			self.image.blit (txt_img, txt_rect)
			self.pressed = True
		elif not pygame.mouse.get_pressed ()[0] and self.pressed == True:
			self.image.blit (self.unpressed_image, (0, 0))
			txt_img = self.font.render(self.text, 1, self.unpressed_color)
			txt_rect = txt_img.get_rect (center = (self.rect.width/2, self.rect.height/2))		
			self.image.blit (txt_img, txt_rect)
			self.pressed = False
			#exec funciton
			result = getattr(actions, self.function)()

class bottom_box:
	def __init__ (self):
		self.background_color = (50, 50, 50)
		self.txt_color = (100, 100, 100)
		self.margin = 5

		self.image = pygame.Surface ((screen_size[0], screen_size[1] - bot1_vid.rect.height))
		self.rect = self.image.get_rect (y=bot1_vid.rect.height)

		self.stop_button = buttons ("stop", "STOP")
		self.start_button = buttons ("start", "START")
		self.capture_button = buttons ("capture", "IMG")

		self.stop_button.rect.centery = self.rect.centery
		self.start_button.rect.centery = self.rect.centery
		self.capture_button.rect.centery = self.rect.centery

		self.stop_button.rect.x = self.margin
		self.start_button.rect.x = self.stop_button.rect.right + self.margin
		self.capture_button.rect.x = self.start_button.rect.right + self.margin

	def update (self):
		self.image.fill (self.background_color)
		self.stop_button.update ()
		self.start_button.update ()
		self.capture_button.update ()

class stat:
	def __init__ (self):
		self.font_size = 36
		self.font = pygame.font.Font(None, self.font_size)
		self.image = pygame.Surface ((1, self.font_size))
		self.rect = self.image.get_rect ()
		self.x = 0
		self.y = 0
		self.text = ""
		self.txt_color = (100, 100, 100)

	def update (self):
		self.image = self.font.render(self.text, 1, self.txt_color)
		self.rect = self.image.get_rect (x = self.x, y = self.y)

class stats_box:
	def __init__(self):
		self.background_color = (50, 50, 50)
		self.txt_color = (100, 100, 100)
		self.margin = 5

		self.image = pygame.Surface ((screen_size[0] - bot1_vid.rect.width, bot1_vid.rect.height))
		self.rect = self.image.get_rect (x=bot1_vid.rect.width)

		self.FPS = stat ()
		self.FPS.x = self.margin
		self.FPS.y = self.margin

		self.IP = stat ()
		self.IP.text = "IP: " + str (bot1_vid.IP)
		self.IP.x = self.margin
		self.IP.y = self.margin + self.FPS.rect.bottom
		self.IP.update ()


		self.Port = stat ()
		self.Port.text = "Port: " + str (bot1_vid.Port)
		self.Port.x = self.margin
		self.Port.y = self.margin + self.IP.rect.bottom
		self.Port.update ()


		self.FPS_time = 0

	def fps (self):
		current_t = time.time ()
		if current_t - self.FPS_time >= 1: #1 second has passed
			self.FPS_time = current_t
			self.FPS.text = "FPS: " + str(bot1_vid.good_frames)
			self.FPS.update ()
			bot1_vid.good_frames = 0

	def update (self):
		self.image.fill (self.background_color)
		self.image.blit (self.FPS.image, self.FPS.rect)
		self.image.blit (self.IP.image, self.IP.rect)
		self.image.blit (self.Port.image, self.Port.rect)
		self.fps ()

class net_vid:
	def __init__(self):
		self.boarder_size = 10
		self.boarder_color = (200, 200, 200)
		self.frame_size = (640,480)
		self.IP = "192.168.1.108"
		self.Port = 27777

		self.init_net ()
		self.image = pygame.Surface ((self.frame_size[0] + self.boarder_size * 2, self.frame_size[1] + self.boarder_size * 2))
		self.rect = self.image.get_rect ()
		self.image.fill (self.boarder_color)
		
		self.bad_frames = 0
		self.good_frames = 0
		self.frame_buff = ''

		self.status = "ON"

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

		if DEBUG_LVL > 1:
			self.save_first = True
			self.save_file = open ("first_image.jpg", "w")

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
		if DEBUG_LVL > 2:
			f = open ("test_data.jpg", "wb")
			f.write (self.frame_buff[self.frame_start: self.frame_end + 2])
			f.close ()

	def vid_recv (self):
		if len (self.frame_buff):
			self.frame_start = self.frame_buff.find ('\xFF\xD8')
		else:
			self.frame_start = -1
		
		self.frame_end = -1
		bytesinframe = 0
		if DEBUG_LVL > 2:
			data_frames = 0
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

		if DEBUG_LVL > 2:
			print "loading image of length: " + str (bytesinframe)


		self.img_buff = cStringIO.StringIO (self.frame_buff[self.frame_start: self.frame_end + 2])

		try:
			self.image.blit (pygame.image.load (self.img_buff, "test.jpg").convert (), (self.boarder_size, self.boarder_size))
			self.good_frames += 1
		except:
			
			self.bad_frames += 1
			if DEBUG_LVL > 2:
				self.capture ()
				print "Bad Frame Count: " + str(self.bad_frames)
				self.status = "OFF"

		self.frame_buff = self.frame_buff [self.frame_end + 2:]

	def update (self):
		if self.status == "ON":
			self.vid_recv ()

bot1_vid = net_vid ()
bot1_stats = stats_box ()
bot1_bottom = bottom_box ()
actions = button_actions ()

FPS_time = 0
watch_bots = True
while watch_bots:
	time.sleep (.01)
	for event in pygame.event.get():
	    if event.type == pygame.QUIT:
		watch_bots = False
	bot1_vid.update ()
	bot1_stats.update ()
	bot1_bottom.update ()

	screen.blit(bot1_vid.image, bot1_vid.rect)
	screen.blit(bot1_stats.image, bot1_stats.rect)
	screen.blit(bot1_bottom.image, bot1_bottom.rect)
	screen.blit(bot1_bottom.stop_button.image, bot1_bottom.stop_button.rect)
	screen.blit(bot1_bottom.start_button.image, bot1_bottom.start_button.rect)
	screen.blit(bot1_bottom.capture_button.image, bot1_bottom.capture_button.rect)

	pygame.display.flip()

