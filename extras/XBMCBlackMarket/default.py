# Main imports
import sys, os, shutil
import xbmc, xbmcgui
import urllib2

# Script constants
__scriptname__ = 'Theme Browser'
__author__ = 'XBMC Black Market Team'
__url__ = 'http://blackmarket.ictcsc.net'
__credits__ = 'XBMC Black Market Team, freenode/#xbmc-blackmarket'

# Shared resources
BASE_RESOURCE_PATH = os.path.join(os.getcwd().replace(';',''), 'resources')
sys.path.append(os.path.join(BASE_RESOURCE_PATH, 'lib'))
currentSkin = xbmc.getSkinDir()
import language
__language__ = language.Language().localized

def onlineCheck(url):
	try:
		check = urllib2.urlopen( url + '/check.php' ).geturl()
	except urllib2.HTTPError, e:
		if e.code != 404:
			return 0
	except urllib2.URLError, e:
		return 0
	else:
		return 1

# Start main ThemeBrowser gui
if ( __name__ == '__main__' ):
	try:
		if ( xbmc.getCondVisibility( 'System.HasNetwork' ) ):
			if onlineCheck(__url__):
				if not ( currentSkin == 'MC360' ):
					xbmcgui.Dialog().ok( __language__( 0 ) , __language__( 639 ) )
				else:
					xbmc.executebuiltin('Skin.Reset(ThemeBrowserReady)')
					xbmc.executebuiltin('Skin.Reset(ThemeBrowserBusy)')
					xbmc.executebuiltin('Skin.Reset(ThemeBrowserFullPreview)')
					import main
					window = 'main'
					ui = main.ThemeBrowser('script-%s-%s.xml' % ( __scriptname__.replace( ' ', '_' ), window, ), BASE_RESOURCE_PATH, currentSkin )
					ui.doModal()
					del ui
			else:
				xbmcgui.Dialog().ok( __language__( 0 ) , __language__( 641 ) )
		else:
			xbmcgui.Dialog().ok( __language__( 0 ) , __language__( 638 ) )
	finally:
		tempDir = os.path.join( 'T:\\script_data', __scriptname__ + '\\temp\\')
		if os.path.isdir(tempDir): shutil.rmtree( tempDir, True )
