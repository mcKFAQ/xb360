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
import traceback

import xbmc
import xbmcgui

import guibuilder

ACTION_MOVE_LEFT      = 1  
ACTION_MOVE_RIGHT     = 2
ACTION_MOVE_UP        = 3
ACTION_MOVE_DOWN      = 4
ACTION_PAGE_UP        = 5 
ACTION_PAGE_DOWN      = 6
ACTION_SELECT_ITEM    = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR     = 9
ACTION_PREVIOUS_MENU  = 10
ACTION_SHOW_INFO      = 11
ACTION_PAUSE          = 12
ACTION_STOP           = 13
ACTION_NEXT_ITEM      = 14
ACTION_PREV_ITEM      = 15
ACTION_CONTEXT_MENU   = 117

def get_input(title, default='', hidden=False):
	"""Show a virtual keyboard and return the entered text."""

	ret = None

	keyboard = xbmc.Keyboard(default, title)
	keyboard.setHiddenInput(hidden)
	keyboard.doModal()

	if keyboard.isConfirmed():
		ret = keyboard.getText()

	return ret
	
ACTION_PREVIOUS_MENU  = 10

class ContextMenu(xbmcgui.WindowDialog):
	"""Context Menu Window Class."""

	def __init__(self, skin=None):
		try: 
			self.base_path = os.getcwd().replace(';','')
			self.buttons = []
			self.items = []

			if not self.load_skin(skin):
				self.close()
				return # do something here
		except:
			xbmc.log('Exception (CxtMenu:init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if name is None:
			name = 'default'

		skin_path = os.path.join(self.base_path, 'skins', name)
		skin = os.path.join(skin_path, 'context_menu.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		guibuilder.GUIBuilder(self, skin, self.img_path, 
		                      useDescAsKey=True, fastMethod=True)

		if self.SUCCEEDED:
			for x in range(1,7):
				ctrl = self.get_control('Context Menu Button%d' % x)
				self.buttons.append(ctrl)
			self.update_button_offset()

		return self.SUCCEEDED

	def get_control(self, desc):
		"""Return the control that matches the widget description."""

		return self.controls[desc]['control']

	def update_button_offset(self):
		"""Determines the relative offsets between window and buttons."""

		btn = self.get_control('Context Menu Button1')
		dlg = self.get_control('Context Menu Background Middle')

		btn_x, btn_y = btn.getPosition()
		dlg_x, dlg_y = dlg.getPosition()

		self.btn_offx = btn_x - dlg_x
		self.btn_offy = btn_y - dlg_y

	def update_buttons(self, items):
		"""Update button visibility and new labels."""

		for btn, lbl in map(lambda *a: tuple(a), self.buttons, items):
			if lbl is not None:
				btn.setLabel(lbl)
				btn.setVisible(True)
				btn.setEnabled(True)
			else:
				btn.setVisible(False)
				btn.setEnabled(False)

		self.items = items

		self.setFocus(self.buttons[0])

	def update_position(self, center_widget):
		"""Center the context menu over a widget."""

		btn = self.get_control('Context Menu Button1')

		list_x, list_y = center_widget.getPosition()
		center_x = list_x + center_widget.getWidth() / 2
		center_y = list_y + center_widget.getHeight() / 2

		btn_gap = 2
		btn_height = btn.getHeight() + btn_gap
		buttons_height = len(self.items) * btn_height - btn_gap

		dlg_top = self.get_control('Context Menu Background Top')
		dlg_mdl = self.get_control('Context Menu Background Middle')
		dlg_btm = self.get_control('Context Menu Background Bottom')

		dlg_mdl.setHeight(buttons_height)

		dlg_top_y = center_y - buttons_height / 2 - dlg_top.getHeight()
		dlg_mdl_y = center_y - buttons_height / 2
		dlg_btm_y = center_y + buttons_height / 2

		dlg_x = center_x - dlg_top.getWidth() / 2

		dlg_top.setPosition(dlg_x, dlg_top_y)
		dlg_mdl.setPosition(dlg_x, dlg_mdl_y)
		dlg_btm.setPosition(dlg_x, dlg_btm_y)

		for i, btn in enumerate(self.buttons):
			btn_x = dlg_x + self.btn_offx
			btn_y = dlg_mdl_y + self.btn_offy + btn_height * i
			btn.setPosition(btn_x, btn_y)

	def select(self, items, center_widget, select_hook, select_udata=None):
		"""Set the Context Menu content and display."""

		if len(items) > len(self.buttons):
			raise ValueError('Too many menu items')

		self.select_hook = select_hook
		self.select_udata = select_udata
		self.update_buttons(items)
		self.update_position(center_widget)
		self.doModal()

	def onControl(self, ctrl):
		"""Handle Context Menu events."""

		try: 
			self.close()

			id = ctrl.getId()

			# Find the index of the pressed button.
			idx = filter(lambda (x,y): y.getId() == id, enumerate(self.buttons))
			if len(idx) > 0 and idx[0][0] < len(self.items):
				self.select_hook(idx[0][0], self.select_udata)
			else:
				# This should never happen.
				self.select_hook(-1, self.select_udata)
		except:
			xbmc.log('Exception (CxtMenu:onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()
