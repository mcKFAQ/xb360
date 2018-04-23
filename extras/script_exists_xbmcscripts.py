SCRIPT = "q:\\scripts\\XBMCScripts\\default.py"
TITLE = "Warning, Script Installer"
MSG_LINE1 = "This script needed for this button \nis not installed on your Xbox."
MSG_LINE2 = ""
ONLINE = False
import os, xbmc, xbmcgui
if xbmc.getCondVisibility('system.internetstate'):
  ONLINE = True
  MSG_LINE3 = "Would you like to download and install it?"
else:
  MSG_LINE3 = "It can be downloaded from \nhttp://www.xbmcscripts.com."

def dlXSupdate(url,dest):
  dp = xbmcgui.DialogProgress()
  dp.create("XBMCScripts installer","Downloading File",url)
  urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
  dp.close()
  zip = zipfile.ZipFile('z:\\xbmcscripts.zip')
  for name in zip.namelist():
    if name.endswith('/'):
      if not os.path.exists(os.path.join('q:\\scripts', name)):
        try:
          os.mkdir(os.path.join('q:\\scripts', name))
        except:
          print "Creation of dir: %s failed!" % name
          raise
    else:
      try:
        f = open(os.path.join('q:\\scripts', name), 'wb')
        f.write(zip.read(name))
        f.close()
      except:
        print "writing of file: %s failed!" % name
        raise
  zip.close()
  try:
    os.remove('z:\\xbmcscripts.zip')
  except:
    print "Couldn't remove z:\\xbmcscripts.zip!"
    pass
  xbmc.executebuiltin( 'XBMC.RunScript(%s)' % SCRIPT )

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
  global percent
  try:
    percent = min((numblocks*blocksize*100)/filesize, 100)
    dp.update(percent)
  except:
    percent = 100
    dp.update(percent)
  if dp.iscanceled():
    print "DOWNLOAD CANCELLED" # need to get this part working
    dp.close()


if ( os.path.isfile( SCRIPT ) ):
  xbmc.executebuiltin( 'XBMC.RunScript(%s)' % SCRIPT )
else:
  if ONLINE:
    if xbmcgui.Dialog().yesno( TITLE, MSG_LINE1, MSG_LINE2, MSG_LINE3 ):
      import urllib, zipfile
      dlXSupdate("http://www.xbmcscripts.com/scriptservice/XBMCScripts.zip", "Z:\\XBMCScripts.zip")
  else: xbmcgui.Dialog().ok( TITLE, MSG_LINE1, MSG_LINE2, MSG_LINE3 )
