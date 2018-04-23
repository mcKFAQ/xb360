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
import pickle
import sys
import traceback

import xbmcgui
import xbmc

import youtube
import details

from xbmcutils.net import DownloadAbort, DownloadError

import xbmcutils.gui
import xbmcutils.guibuilder

class Logger:
	def write(data):
		xbmc.log(data)
	write = staticmethod(write)
sys.stdout = Logger
sys.stderr = Logger

class YouTubeGUI(xbmcgui.Window):
	"""YouTube browser GUI."""

	# GUI States.
	STATE_MAIN = 1
	STATE_FEEDS = 2
	STATE_USERS = 4
	STATE_MOST_DISCUSSED = STATE_FEEDS | 8
	STATE_MOST_VIEWED = STATE_MOST_DISCUSSED | 16
	STATE_SEARCH = 32
	STATE_USERS = 64

	# Content list states
	CONTENT_STATE_NONE = 0
	CONTENT_STATE_VIDEO = 1
	CONTENT_STATE_USERS = 2
	CONTENT_STATE_FAVORITES = 4
	CONTENT_STATE_SEARCH_HISTORY = 8

	def __init__(self):
		"""Setup the default skin, state and load 'recently_featured' feed"""

		try: 
			self.base_path = os.getcwd().replace(';','')

			if not self.load_skin('default'):
				self.close()

			self.data = []
			
			self.yt = youtube.YouTube()
			self.yt.set_filter_hook(self.confirm_content)

			self.state = YouTubeGUI.STATE_MAIN
			self.list_state = YouTubeGUI.CONTENT_STATE_NONE

			self.cxt = xbmcutils.gui.ContextMenu()
			self.details = details.Details()

			# Get the last search term
			history = self.get_search_history()
			if history is not None and len(history) > 0:
				self.last_search_term = history[0]
			else:
				self.last_search_term = ''

			self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)

			self.get_feed('recently_featured')
		except:
			xbmc.log('Exception (init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def confirm_content(self, udata):
		"""Let the user choose to watch offensive crap."""

		dlg = xbmcgui.Dialog()
		return dlg.yesno('YouTube',
		                 'This clip may contain inappropriate content.',
		                 'Do you want to watch it anyway?')

	def get_search_history(self):
		"""Return a list of old search terms."""

		history_list = []
		path = os.path.join(self.base_path, 'data', 'history.txt')

		try:
			f = open(path, 'rb')
			history_list = pickle.load(f)
			f.close()
		except IOError, e:
			# File not found, will be created upon save
			pass

		return history_list

	def add_search_history(self, term):
		"""Append a term, and trim the search history to max 50 entries."""

		history_list = self.get_search_history()

		# Filter out the term to add from the list so only one copy is stored.
		history_list = filter(lambda x: x != term, history_list)
		history_list.insert(0, term)

		if len(history_list) > 50:
			history_list = history_list[:50]

		try:
			dir = os.path.join(self.base_path, 'data')
			# Create the 'data' directory if it doesn't exist.
			if not os.path.exists(dir):
				os.mkdir(dir)
			path = os.path.join(dir, 'history.txt')
			f = open(path, 'wb')
			pickle.dump(history_list, f, protocol=pickle.HIGHEST_PROTOCOL)
			f.close()
		except IOError, e:
			print 'There was an error while saving the pickle (%s)' % e

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if not name:
			name = 'default'

		skin_path = os.path.join(self.base_path, 'skins', name)
		skin = os.path.join(skin_path, 'skin.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		xbmcutils.guibuilder.GUIBuilder(self, skin, self.img_path,
		                                useDescAsKey=True, fastMethod=True)

		return self.SUCCEEDED

	def show_about(self):
		"""Show an 'About' dialog."""

		dlg = xbmcgui.Dialog()
		dlg.ok('About', 'By: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Bugs: XBMC Forum - Python Script Development')

	def get_control(self, desc):
		"""Return the control that matches the widget description."""

		return self.controls[desc]['control']

	def not_implemented(self):
		"""Show a 'not implemented' dialog."""
		dlg = xbmcgui.Dialog()
		dlg.ok('YouTube', 'Not Implemented, check back later')

	def progress_handler(self, done, total, dlg):
		"""Update progress dialog percent and return abort status."""

		percent = int((done * 100.0) / total)

		dlg.update(percent)
		return not dlg.iscanceled()
	
	def download_data(self, arg, func):
		"""Show a progress dialog while downloading and return the data."""

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Downloading content')

		self.yt.set_report_hook(self.progress_handler, dlg)

		try:
			data = func(arg)
		except DownloadError, e:
			dlg.close()
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.', e.value)
			return None
		except DownloadAbort:
			dlg.close()
			return None
		except Exception, e:
			# In Python 2.5 this would have been a finally
			dlg.close()
			raise e

		dlg.close()

		return data

	def get_user_videos(self, method, title, user=None):
		"""Get rss data and update the list."""

		if user is None:
			user = xbmcutils.gui.get_input('User')
	
		if user is not None:
			data = self.download_data(user, method)
			if self.update_list(data):
				lbl = '%s user %s' % (title, user)
				self.get_control('Feed Label').setLabel(lbl)
				self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
	
	def get_feed(self, feed):
		"""Get rss data and update the list."""
		data = self.download_data(feed, self.yt.get_feed)
		if self.update_list(data):
			# Change 'something_bleh_bluh' to 'Something Bleh Bluh'.
			lbl = ' '.join(map(lambda x: x.capitalize(), feed.split('_')))
			self.get_control('Feed Label').setLabel(lbl)
			self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
		
	def search(self, term=None):
		"""Get user input and perform a search. On success update the list."""

		if term is None:
			term = xbmcutils.gui.get_input('Search', self.last_search_term)
		
		# Only update the list if the user entered something.
		if term != None:
			self.last_search_term = term
			data = self.download_data(term, self.yt.search)
			if self.update_list(data):
				lbl = 'Search: %s' % term
				self.get_control('Feed Label').setLabel(lbl)
				self.add_search_history(term)
				self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
			else:
				dlg = xbmcgui.Dialog()
				dlg.ok('YouTube', 'No videos were found that match your query.')

	def search_history(self):
		"""Get search history and update the list."""

		data = [(x,None) for x in self.get_search_history()]
		if self.update_list(data):
			self.get_control('Feed Label').setLabel('Search History')
			self.list_state = YouTubeGUI.CONTENT_STATE_SEARCH_HISTORY
		else:
			dlg = xbmcgui.Dialog()
			dlg.ok('YouTube', 'Search history empty.')

	def update_list(self, data):
		"""Updates the list widget with new data."""

		# Either an error dialog has been shown, or the user
		# aborted the download. Anyway, there's no new data
		# to put in the list, so lets just keep the old.
		if data == None or len(data) == 0:
			return False

		self.data = data

		content_list = self.get_control('Content List')

		xbmcgui.lock()
		content_list.reset()
		for desc, id in self.data:
			item = xbmcgui.ListItem (label=desc)
			content_list.addItem(item)
		xbmcgui.unlock()

		return True

	def login(self, username=None, password=None):
		"""Get username and password from the user and try to login."""

		ret = False

		if username is None:
			username = xbmcutils.gui.get_input('Username')

		if password is None:
			password = xbmcutils.gui.get_input('Password', hidden=True)

		try:
			ret = self.yt.login(username, password)
		except DownloadAbort, e:
			# Just fall through as ret defaults to False
			pass
		except DownloadError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.', e.value)

		return ret

	def add_favorite(self):
		content_list = self.get_control('Content List')
		pos = content_list.getSelectedPosition()

		desc, id = self.data[pos]

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Adding \'%s\' to favorites' % desc)

		self.yt.set_report_hook(self.progress_handler, dlg)

		try:
			if not self.yt.login_status() and not self.login():
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'Login failed.')
			elif self.yt.user_add_favorite(id):
				added_dlg = xbmcgui.Dialog()
				added_dlg.ok('YouTube', 'Favorite added.')
		except DownloadAbort, e:
			# Just fall through as the method shouldn't return anyhting.
			pass
		except DownloadError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.', e.value)

		dlg.close()

	def video_details(self, id=None):
		"""Get video details about some id."""

		details = None

		if id is None:
			content_list = self.get_control('Content List')
			pos = content_list.getSelectedPosition()

			desc, id = self.data[pos]

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Getting video details')

		self.yt.set_report_hook(self.progress_handler, dlg)

		try:
			details = self.yt.get_video_details(id)
		except DownloadAbort, e:
			# Just fall through as return value defaults to None
			pass
		except DownloadError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.', e.value)

		dlg.close()

		return details

	def show_video_details(self):
		"""Get the details, and show the details window."""

		details = self.video_details()

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Downloading thumbnail.')
		self.yt.set_report_hook(self.progress_handler, dlg)

		if details is not None and details.has_key('thumbnail_url'):
			try:
				thumb = self.yt.retrieve(details['thumbnail_url'])
			except DownloadAbort, e:
				# Just fall through as a thumbnail is not required.
				pass
			except DownloadError, e:
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'There was an error.', e.value)
			else:
				# Save the thumbnail to a local file so it can be used.
				path = os.path.join(self.base_path, 'data', 'thumb.jpg')
				fp = open(path, 'wb')
				fp.write(thumb)
				fp.close()
				details['thumbnail_url'] = path

		dlg.close()
		
		if details is not None:
			self.details.display(details)

	def videos_by_user(self):
		details = self.video_details()

		if details is not None and not details.has_key('author'):
			dlg = xbmcgui.Dialog()
			dlg.ok('YouTube', 'Could not find author.')
		elif details is not None:
			user = details['author']

			dlg = xbmcgui.DialogProgress()
			dlg.create('YouTube', 'Getting videos by %s' % user)

			self.yt.set_report_hook(self.progress_handler, dlg)

			try:
				list = self.yt.get_videos_by_user(user, per_page=40)
			except DownloadAbort, e:
				# No data gathered, no need to update list.
				dlg.close()
				return
			except DownloadError, e:
				# No data gathered, no need to update list.
				dlg.close()
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'There was an error.', e.value)
				return

			dlg.close()

			if self.update_list(list):
				self.get_control('Feed Label').setLabel('Videos by %s' % user)
				self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
			else:
				dlg = xbmcgui.Dialog()
				dlg.ok('YouTube', '%s hasn\'t uploaded any videos.')

	def videos_related(self):
		details = self.video_details()

		if not details.has_key('tags'):
			dlg = xbmcgui.Dialog()
			dlg.ok('YouTube', 'Could not find any tags.')
		else:
			dlg = xbmcgui.DialogProgress()
			dlg.create('YouTube', 'Getting related videos')

			self.yt.set_report_hook(self.progress_handler, dlg)

			list = None

			try:
				tags = details['tags']
				list = self.yt.get_videos_by_related(tags, per_page=40)
			except DownloadError, e:
				# No data gathered, no need to update list.
				dlg.close()
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'There was an error.', e.value)
				return
			except DownloadAbort, e:
				# No data gathered, no need to update list.
				dlg.close()
				return

			dlg.close()

			if self.update_list(list):
				if details.has_key('title'):
					lbl = 'Videos related to \'%s\'' % details['title']
				else:
					lbl = 'Related videos'
				self.get_control('Feed Label').setLabel(lbl)
				self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
			else:
				dlg = xbmcgui.Dialog()
				dlg.ok('YouTube', 'No related videos found.')

	def play_clip(self, id):
		"""Get the url for the id and start playback."""

		try:
			file = self.download_data(id, self.yt.get_video_url)
			self.player.play(str(file))
		except youtube.PrivilegeError, e:
			dlg = xbmcgui.Dialog()
			ret = dlg.yesno('YouTube',
			                'You need to be logged in to watch this clip.',
			                'Do you want to login?')

			# If the user wants to login, and login works, then try again
			try:
				if ret:
					if self.login():
						self.play_clip(id)
					else:
						dlg = xbmcgui.Dialog()
						dlg.ok('YouTube', 'Login failed.')
			except DownloadError, e:
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'There was an error.', e.value)
			except DownloadAbort, e:
				# Just fall through as the method shouldn't return anything.
				pass
		except youtube.VideoStreamError, e:
			dlg = xbmcgui.Dialog()
			dlg.ok('YouTube', 'Unable to play the video clip.')

	def onAction(self, action):
		"""Handle user input events."""

		try: 
			if action == xbmcutils.gui.ACTION_PREVIOUS_MENU:
				if self.state is YouTubeGUI.STATE_MAIN:
					self.close()
				elif self.state & ~YouTubeGUI.STATE_FEEDS & YouTubeGUI.STATE_MOST_DISCUSSED:
					self.set_button_state(YouTubeGUI.STATE_FEEDS)
				else:
					self.set_button_state(YouTubeGUI.STATE_MAIN)
			elif action == xbmcutils.gui.ACTION_CONTEXT_MENU:
				if self.list_state is YouTubeGUI.CONTENT_STATE_VIDEO:
					self.context_menu_video()
				else:
					self.not_implemented()
		except:
			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def context_menu_video_handler(self, id, udata):
		if id is 0: # 'Add Favorites'
			self.add_favorite()
		elif id is 1: # 'Information'
			self.show_video_details()
		elif id is 2: # 'Related Videos'
			self.videos_related()
		elif id is 3: # 'Other Videos By User'
			self.videos_by_user()

	def context_menu_video(self):
		items = ['Add Favorite',
		         'Details',
		         'Related Videos',
		         'Other Videos By User']
		center_widget = self.get_control('Content List')
		self.cxt.select(items, center_widget, self.context_menu_video_handler)

	def onControl(self, ctrl):
		"""Handle widget events."""

		try: 
			if ctrl is self.get_control('Content List'):
				self.on_control_list(ctrl)
			elif self.state is YouTubeGUI.STATE_MAIN:
				self.on_control_main(ctrl)
			elif self.state is YouTubeGUI.STATE_SEARCH:
				self.on_control_search(ctrl)
			elif self.state is YouTubeGUI.STATE_USERS:
				self.on_control_users(ctrl)
			elif self.state is YouTubeGUI.STATE_FEEDS:
				self.on_control_feeds(ctrl)
			elif self.state is YouTubeGUI.STATE_MOST_VIEWED:
				self.on_control_most_viewed(ctrl)
			elif self.state is YouTubeGUI.STATE_MOST_DISCUSSED:
				self.on_control_most_discussed(ctrl)
		except:
			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def on_control_list(self, ctrl):
		"""Handle content list events."""
		pos = ctrl.getSelectedPosition()

		try:
			desc, id = self.data[pos]
		except IndexError, e:
			# If this happens something is terribly wrong
			print 'Index out of bounds'
			self.close()
			return

		if self.list_state is YouTubeGUI.CONTENT_STATE_VIDEO:
			self.play_clip(id)
		elif self.list_state is YouTubeGUI.CONTENT_STATE_SEARCH_HISTORY:
			self.search(desc)
		else:
			self.not_implemented()

	def on_control_main(self, ctrl):
		"""Handle main menu events."""

		if ctrl is self.get_control('Feeds Button'):
			self.set_button_state(YouTubeGUI.STATE_FEEDS)
		elif ctrl is self.get_control('Users Button'):
			self.set_button_state(YouTubeGUI.STATE_USERS)
		elif ctrl is self.get_control('Search Button'):
			self.set_button_state(YouTubeGUI.STATE_SEARCH)
		elif ctrl is self.get_control('About Button'):
			self.show_about()

	def on_control_search(self, ctrl):
		"""Handle search menu events."""
		if ctrl is self.get_control('Search Entry Button'):
			self.search()
		elif ctrl is self.get_control('Search History Button'):
			self.search_history()

	def on_control_users(self, ctrl):
		if ctrl is self.get_control('User Favorites Button'):
			self.get_user_videos(self.yt.get_user_favorites, 'Favorites of')
		elif ctrl is self.get_control('User Videos Button'):
			self.get_user_videos(self.yt.get_user_videos, 'Videos by')
		elif ctrl is self.get_control('User Friends Button'):
			self.not_implemented()

	def on_control_feeds(self, ctrl):
		"""Handle feeds menu events."""

		if ctrl is self.get_control('Recently Added Button'):
			self.get_feed('recently_added')
		elif ctrl is self.get_control('Recently Featured Button'):
			self.get_feed('recently_featured')
		elif ctrl is self.get_control('Top Favorites Button'):
			self.get_feed('top_favorites')
		elif ctrl is self.get_control('Top Rated Button'):
			self.get_feed('top_rated')
		elif ctrl is self.get_control('Most Viewed Button'):
			self.set_button_state(YouTubeGUI.STATE_MOST_VIEWED)
		elif ctrl is self.get_control('Most Discussed Button'):
			self.set_button_state(YouTubeGUI.STATE_MOST_DISCUSSED)

	def on_control_most_viewed(self, ctrl):
		"""Handle most viewed time frame events."""

		if ctrl is self.get_control('Today Button'):
			self.get_feed('top_viewed_today')
		elif ctrl is self.get_control('This Week Button'):
			self.get_feed('top_viewed_week')
		elif ctrl is self.get_control('This Month Button'):
			self.get_feed('top_viewed_month')
		elif ctrl is self.get_control('All Time Button'):
			self.get_feed('top_viewed')

	def on_control_most_discussed(self, ctrl):
		"""Handle most discussed time frame events."""

		if ctrl is self.get_control('Today Button'):
			self.get_feed('most_discussed_today')
		elif ctrl is self.get_control('This Week Button'):
			self.get_feed('most_discussed_week')
		elif ctrl is self.get_control('This Month Button'):
			self.get_feed('most_discussed_month')

	def set_button_state(self, state):
		"""Update button visibility, current state and focused widget."""

		xbmcgui.lock()

		# Are we in the main menu?
		visible = bool(state & YouTubeGUI.STATE_MAIN)

		self.get_control('Feeds Button').setVisible(visible)
		self.get_control('Users Button').setVisible(visible)
		self.get_control('Search Button').setVisible(visible)
		self.get_control('About Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Feeds Button')

		# Are we in the feeds menu?
		visible = bool(state & YouTubeGUI.STATE_FEEDS)

		self.get_control('Recently Added Button').setVisible(visible)
		self.get_control('Recently Featured Button').setVisible(visible)
		self.get_control('Top Favorites Button').setVisible(visible)
		self.get_control('Top Rated Button').setVisible(visible)
		self.get_control('Most Viewed Button').setVisible(visible)
		self.get_control('Most Discussed Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Recently Added Button')

		# Are we in the most discussed menu?
		visible = bool(state & ~YouTubeGUI.STATE_FEEDS &
		               YouTubeGUI.STATE_MOST_DISCUSSED)

		self.get_control('Today Button').setVisible(visible)
		self.get_control('This Week Button').setVisible(visible)
		self.get_control('This Month Button').setVisible(visible)
		self.get_control('All Time Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Today Button')

		# Are we in the most viewed menu?
		visible = bool(state & ~YouTubeGUI.STATE_MOST_DISCUSSED &
		               YouTubeGUI.STATE_MOST_VIEWED)

		self.get_control('All Time Button').setEnabled(visible)

		# Are we in the users menu?
		visible = bool(state & YouTubeGUI.STATE_USERS)

		self.get_control('User Favorites Button').setVisible(visible)
		self.get_control('User Videos Button').setVisible(visible)
		self.get_control('User Friends Button').setVisible(visible)

		if visible:
			dominant = self.get_control('User Favorites Button')

		# Are we in the search menu?
		visible = bool(state & YouTubeGUI.STATE_SEARCH)

		self.get_control('Search Entry Button').setVisible(visible)
		self.get_control('Search History Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Search Entry Button')



		# Set focus to the top-most relevant button, and move
		# to that when leaving the list.
		self.setFocus(dominant)
		self.get_control('Content List').controlLeft(dominant)
		
		self.state = state

		xbmcgui.unlock()

yt = YouTubeGUI()
yt.doModal()
del yt 
