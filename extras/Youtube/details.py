"""
 Copyright (c) 2007 Daniel Svensson, <dsvensson@gmail.com>

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import sys
import time
import traceback
import urllib2


import xbmc
import xbmcgui

import xbmcutils.guibuilder

ACTION_PREVIOUS_MENU  = 10

class Details(xbmcgui.WindowDialog):
	"""Details Window Class."""

	def __init__(self, skin=None):
		try: 
			self.base_path = os.getcwd().replace(';','')

			if not self.load_skin(skin):
				self.close()
		except:
			xbmc.log('Exception (Details:init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if name is None:
			name = 'default'

		skin_path = os.path.join(self.base_path, 'skins', name)
		skin = os.path.join(skin_path, 'details.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		xbmcutils.guibuilder.GUIBuilder(self, skin, self.img_path, 
		                                useDescAsKey=True, fastMethod=True)

		return self.SUCCEEDED

	def get_control(self, desc):
		"""Return the control that matches the widget description."""

		return self.controls[desc]['control']

	def display(self, data):
		"""Set the Details content and display."""

		ctrl = self.get_control('Description')
		if data.has_key('description'):
			ctrl.setText(data['description'])
		else:
			ctrl.setText('')

		ctrl = self.get_control('Video Thumbnail')
		if data.has_key('thumbnail_url'):
			ctrl.setImage(data['thumbnail_url'])
		else:
			ctrl.setImage('dialog-context-middle.png')

		ctrl = self.get_control('Title Label')
		if data.has_key('title'):
			ctrl.setLabel(data['title'])
		else:
			ctrl.setLabel('')

		ctrl = self.get_control('Tags Text Label')
		if data.has_key('tags'):
			ctrl.reset()
			ctrl.addLabel(data['tags'])
		else:
			ctrl.reset()

		ctrl = self.get_control('Author Text Label')
		if data.has_key('author'):
			ctrl.setLabel(data['author'])
		else:
			ctrl.setLabel('')

		ctrl = self.get_control('Length Text Label')
		if data.has_key('length_seconds') and len(data['length_seconds']) > 0:
			length = int(data['length_seconds'])
			lbl = '%d minutes, %d seconds' % (length / 60, length % 60)
			ctrl.setLabel(lbl)
		else:
			ctrl.setLabel('')

		ctrl = self.get_control('Rating Text Label')
		if data.has_key('rating_avg'):
			ctrl.setLabel(data['rating_avg'])
		else:
			ctrl.setLabel('')

		ctrl = self.get_control('Added Text Label')
		if data.has_key('upload_time') and len(data['upload_time']) > 0:
			unixtime = int(data['upload_time'])
			y, m, d, hour, min, sec, wd, yd, dst = time.gmtime(unixtime)
			lbl = '%d-%02d-%02d %02d:%02d' % (y, m, d, hour, min)
			ctrl.setLabel(lbl)
		else:
			ctrl.setLabel('')

		self.doModal()
