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

import re
import urllib2
import cookielib
import os.path
import time

from xml.sax.saxutils import escape

import elementtree.ElementTree

import xbmcutils.net

class VideoStreamError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class PrivilegeError(Exception):
	def __init__(self):
		self.value = 'Insufficient permissions, operation aborted.'
	def __str__(self):
		return repr(self.value)

class YouTube:
	"""YouTube dataminer class."""

	categories = {1:'Arts & Animation',
	              2:'Autos & Vehicles',
	              23:'Comedy',
	              24:'Entertainment',
	              10:'Music',
	              25:'News & Blogs',
	              22:'People',
	              15:'Pets & Animals',
	              26:'Science & Technology',
	              17:'Sports',
	              19:'Travel & Places',
	              20:'Video Games'}

	def __init__(self):
		self.base_path = os.getcwd().replace(';','')


		# pattern to match youtube video session id.
		self.session_pattern = re.compile('&t=([0-9a-zA-Z-_]{32})')
		# pattern to match login status
		self.login_pattern = re.compile('Log In')

		# various urls
		self.base_url = 'http://www.youtube.com'
		self.api_url = self.base_url + '/api2_rest?method=%s&dev_id=k1jPjdICyu0&%s'
		self.feed_url = self.base_url + '/rss/global/%s.rss'
		self.stream_url = self.base_url + '/get_video?video_id=%s&t=%s'
		self.video_url = self.base_url + '/?v=%s'
		self.search_url = self.base_url + '/rss/search/%s.rss'
		self.user_url = self.base_url + '/rss/user/%s/videos.rss'
		self.confirm_url = self.base_url + '/verify_age?next_url=/watch?v=%s'
		self.ajax_url = self.base_url + '/watch_ajax'

		# should exotic characters be stripped?
		self.strip_chars = True

		# Create the data subdirectory if it doesn't exist.
		data_dir = os.path.join(self.base_path, 'data')
		if not os.path.exists(data_dir):
			os.mkdir(data_dir)

		# Cookie stuff
		self.cookie_file = os.path.join(data_dir, 'cookie.lwp')

		self.cj = cookielib.LWPCookieJar()
		if os.path.isfile(self.cookie_file):
			self.cj.load(self.cookie_file)

		# Cookie build opener, user for content pages
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		urllib2.install_opener(opener)

		# Callback related stuff
		self.report_hook = None
		self.report_udata = None
		self.filter_hook = None
		self.filter_udata = None

	def strip_exotic_chars(self, str):
		# Dump exotic characters so we don't have to watch ugly boxes
		stripped = ''.join([c for c in str if ord(c) < 256])
		if stripped != str:
			if len(stripped) != 0:
				stripped = stripped + ' '
			str = stripped + '[invalid characters]'
		return str

	def get_rss(self, url):
		data = self.retrieve(url)
		tree = elementtree.ElementTree.XML(data)

		list = []
		for node in tree.findall('channel/item'):
			title = node.find('title').text
			if self.strip_chars:
				title = self.strip_exotic_chars(title)
			id = node.find('link').text[-11:]
			list.append((title, id))

		return list

	def get_user_videos(self, user):
		"""Assemble user videos url and return a (desc, id) list."""

		url = self.user_url % user
		return self.get_rss(url)

	def get_feed(self, feed):
		"""Assemble feed url and return a (desc, id) list."""

		url = self.feed_url % feed
		return self.get_rss(url)

	def search(self, term):
		"""Assemble a search query and return a (desc, id) list."""

		friendly_term = escape(term).replace(' ', '+')
		url = self.search_url % friendly_term
		return self.get_rss(url)


	def call_method(self, method, param):
		"""Call a REST method and return the result as an ElementTree."""
		url = self.api_url % (method, param)

		data = self.retrieve(url)
		return elementtree.ElementTree.XML(data)
	

	def get_video_list(self, method, param):
		"""Return a list of (desc, id) pairs from the REST result."""

		tree = self.call_method(method, param)
		list = []
		for node in tree.findall('video_list/video'):
			title = node.find('title').text
			if self.strip_chars:
				title = self.strip_exotic_chars(title)
			id = node.find('id').text
			list.append((title, id))

		return list

	def get_user_profile(self, name):
		"""Collect user profile data from the REST call."""

		param = 'user=%s' % name
		method = 'youtube.users.get_profile'
		tree = self.call_method(method, param)
		profile = {}
		for node in tree.findall('user_profile/*'):
			profile[node.tag] = node.text

		return profile

	def get_user_favorites(self, name):
		"""Return a list of (desc, id) pairs."""

		param = 'user=%s' % name
		method = 'youtube.users.list_favorite_videos'
		return self.get_video_list(method, param)
	
	def get_user_friends(self, name, page=None, per_page=None):
		"""Return a list of friends."""

		param = 'user=%s' % name
		method = 'youtube.users.list_friends'

		tree = self.call_method(method, param)

		friends = []
		for node in tree.findall('friend_list/friend/user'):
			friends.append(node.text)

		return friends

	def get_video_details(self, id):
		"""Collect video details data from the REST call."""

		param = 'video_id=%s' % id
		method = 'youtube.videos.get_details'

		tree = self.call_method(method, param)

		details = {}
		for node in tree.findall('video_details/*'):
			details[node.tag] = node.text

		return details

	def get_videos_by_tag(self, tag,
	                      page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'tag=%s' % tag
		method = 'youtube.videos.list_by_tag'

		return self.get_video_list(method, param)

	def get_videos_by_user(self, user,
	                       page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'user=%s' % user
		method = 'youtube.videos.list_by_user'

		return self.get_video_list(method, param)

	def get_videos_by_related(self, tag,
	                          page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'tag=%s' % tag
		method = 'youtube.videos.list_by_related'

		return self.get_video_list(method, param)

	def get_videos_by_playlist(self, id,
	                           page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'id=%s' % id
		method = 'youtube.videos.list_by_playlist'

		return self.get_video_list(method, param)

	def get_videos_by_tag_and_category(self, category, tag,
	                                   page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'category_id=%d&tag=%s' % (category, tag)
		method = 'youtube.videos.list_by_category_and_tag'

		return self.get_video_list(method, param)

	def set_filter_hook(self, hook, udata=None):
		"""Set the content filter handler."""

		self.filter_hook = hook
		self.filter_udata = udata

	def get_video_url(self, id, confirmed=False):
		"""Return a proper playback url for some YouTube id."""

		ret = None

		if not confirmed:
			# Regular video page.
			url = self.video_url % id
			data = self.retrieve(url)
		else:
			# Filtered video page.
			url = self.confirm_url % id

			next_url = self.video_url % id
			post = {'next_url': next_url,
			        'action_confirm':'Confirm'}

			data = self.retrieve(url, post)

		if data is not None:
			match = self.session_pattern.search(data)

			if match != None and len(match.groups()) == 1:
				session = match.group(1)
				ret = self.stream_url % (id, session)
			elif not confirmed:
				if not self.login_status(data):
					raise PrivilegeError()

				# With some luck this only means that the url is protected
				# by login + confirm page.
				if self.filter_hook is not None:
					# Ask the user if he wants to show the filtered content.
					if self.filter_hook(self.filter_udata):
						ret = self.get_video_url(id, confirmed=True)

		if ret is None:
			# Failed to find the video stream url, better complain.
			raise VideoStreamError(id)

		return ret

	def set_report_hook(self, func, udata=None):
		"""Set the download progress report handler."""

		self.report_hook = func
		self.report_udata = udata

	def retrieve(self, url, data=None, headers={}):
		"""Downloads an url."""

		return xbmcutils.net.retrieve (url, data, headers,
		                               self.report_hook,
		                               self.report_udata)

		return data

	def login(self, username, password):
		"""Login with username, password and return status."""

		post = {'username':username, 
		        'password':password,
		        'current_form':'loginForm',
				'action_login':'Log+In'}
		url = 'http://www.youtube.com/login?next=/'

		data = self.retrieve(url, post)
		self.cj.save(self.cookie_file)

		return self.login_status(data)

	def login_status(self, data=None):
		"""Return True if logged in, otherwise False."""

		if data is None:
			data = self.retrieve(self.base_url)

		match = self.login_pattern.search(data)
		if match is not None:
			return False

		return True

	def user_add_favorite(self, id):
		"""Add some video id to the user favorites."""

		post = {'':'OK',
		        'action_add_favorite_playlist':'1',
		        'video_id':id,
		        'playlist_id':'',
		        'add_to_favorite':'on'}

		headers = {'Content-Type':'application/x-www-form-urlencoded'}

		data = self.retrieve(self.ajax_url, post, headers)

		root = elementtree.ElementTree.XML(data)

		node = root.find('return_code')
		if node is None or node.text != '0':
			raise PrivilegeError()

		return True


if __name__ == '__main__':
	import sys

	yt = YouTube()

	def report(done, size, udata):
		str = '\r%d    ' % int((done*100.0)/size)
		sys.stderr.write(str)
		sys.stderr.flush()
		if done == size:
			print '\r'
	
	def filter_confirm(udata):
		return True
	
	yt.set_report_hook(report)

	try:
		"""
		print "User Profile (sneseglarn):"
		print yt.get_user_profile('sneseglarn')
		print "------------------------------------------"
		print "User Favorite Videos (sneseglarn):"
		print yt.get_user_favorites('sneseglarn')
		print "------------------------------------------"
		print "User Friends (bungloid):"
		print yt.get_user_friends('bungloid')
		print "------------------------------------------"
		print "Video Details (NGrrPReQaOE):"
		print yt.get_video_details('NGrrPReQaOE')
		print "------------------------------------------"
		print "Videos by Tag ('blender')"
		print yt.get_videos_by_tag('blender')
		print "------------------------------------------"
		print "Videos by Tag and Category (1, 'blender')"
		print yt.get_videos_by_tag_and_category(1, 'blender')
		print "------------------------------------------"
		print "Videos from Feed ('recently_featured')"
		print yt.get_feed('recently_featured')
		print "------------------------------------------"
		print "Videos Url from Id ('whG99kjeXOM')"
		print yt.get_video_url('whG99kjeXOM')
		print "------------------------------------------"
		print "Videos from Search ('snowboard')"
		print yt.search('snowboard')
		print "------------------------------------------"
		print "Videos from User ('sneseglarn')"
		print yt.get_user_videos('sneseglarn')
		print "------------------------------------------"
		"""

		if len(sys.argv) == 3:
			print "Login status"
			print yt.login_status()
			print "------------------------------------------"
			print "Logging in"
			print yt.login(sys.argv[1], sys.argv[2])
			print "------------------------------------------"
			print "Login status"
			print yt.login_status()
			print "------------------------------------------"
			print "Video Url from filtered Id ('M23If6Sqe-Q')"
			yt.set_filter_hook(filter_confirm)
			print yt.get_video_url('M23If6Sqe-Q')
			print "------------------------------------------"
			print "Add Video to Favorites ('M23If6Sqe-Q')"
			print yt.user_add_favorite('M23If6Sqe-Q')

	except DownloadError, e:
		print "download failed: %s" % e
	except DownloadAbort, e:
		print "download aborted: %s " % e
	except VideoStreamError, e:
		print "could not get video url for %s" % e
	except PrivilegeError, e:
		print "login required for this operation"
