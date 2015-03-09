#!/usr/bin/python
# This face detector uses the dlib library

import sys

import dlib
import Image, ImageDraw #imports from PIL or Pillow
import numpy
import cStringIO

TEST = False

DEBUG = False
def debug (data):
	if DEBUG:
		print data

class find_faces (object):
	def __init__ (self):
		self.draw_face_rect = False
		self.detector = dlib.get_frontal_face_detector()
		
		if TEST:
			self.win = dlib.image_window()

	def detect (self, image):
		debug("Loading image")
		in_data = Image.open(cStringIO.StringIO(image)) 
		data = numpy.array(in_data)

		dets = self.detector(data)
		debug ("Number of faces detected: {}".format(len(dets)))
		

		if len(dets) > 0:
			draw = ImageDraw.Draw(in_data)

			#if show rects is on?
			for detect in dets:
				draw.rectangle ([detect.left(), detect.top(), detect.right(), detect.bottom()], outline = (0, 200, 0))

			del draw
		
		img = cStringIO.StringIO()

		in_data.save (img, format='JPEG')

		img.seek (0)

		if DEBUG:
			for k, d in enumerate(dets):
				debug ("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
		if TEST:
			
		
			self.win.clear_overlay()
			self.win.set_image(data)
			self.win.add_overlay(dets)

		return dets, img.read () #this is a dlib rectangles object with a rectangle around each detected face

