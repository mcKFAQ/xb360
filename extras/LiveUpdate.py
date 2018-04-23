"""
	By Name for Team BlackBolt     (YourEmailhereIfUWantitHere)
	Designed For use with MC360 Only
"""
import os,xbmc, urllib,shutil

__title__ = "Live Ads"
__version__ = '0.2'
__site__ = "http://blackbolt.x-scene.com/xbmcliveplace/liveads/"

def main():
	print "---> %s <--" % __title__
	# Clear out Temp Download Folder
	if os.path.exists("Z:\\LiveAds\\"):
		shutil.rmtree("Z:\\LiveAds\\")
	os.mkdir("Z:\\LiveAds\\")
	# Get Advert List and Download adverts to Z:\\LiveAds
	gotit = Downloadads()

	# if 100%, delete Q:\skin\*currentskin*\liveads\
	if gotit:
		shutil.rmtree("Q:\\skin\\" + xbmc.getSkinDir() + "\\LiveAds\\")
		# Copy LiveAds to Q:\skin\*currentskin*\
		copyfailed = 0
		try:    
			shutil.copytree(source, destination)
			copyfailed = 1
		except:
			print "error in copying liveads"
			copyfailed = 0

		if copyfailed == 0:	# copy failed so remove adverts
			if os.path.exists("Z:\\LiveAds\\"):
				shutil.rmtree("Z:\\LiveAds\\")

def DownloadImage(filename):
	""" From the KML Browser :P  """
	try:
		urllib.urlretrieve(__site__ + filename, "Z:\\LiveAds\\" + filename)
		return 1
	except:
		return 0

def Downloadads():
	wsock = urllib.urlopen(__site__+ "liveads.php")
	card_html = wsock.readlines()
	wsock.close()
	print card_html
	for t in card_html:
		t = t.replace("\r\n","")
		if (DownloadImage(t) == 0):
			return 0
	return 1

if __name__ == "__main__":
	main()