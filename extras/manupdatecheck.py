# Check For Update
import re,urllib2
import xbmc,xbmcgui
SkinFolder = "Q:\\Skin\\MC360\\"

def ReadSkinXML():
    f = open(SkinFolder + "skin.xml", 'r')
    dat = f.read()
    svr = re.search('<skinversion>(.*)</skinversion>', dat, re.IGNORECASE).group(1)
    f.close()
    return svr

def ReadOnlineXML(): #sv=""):
    ##udat  = urllib.urlencode({'client':"MC360", 'current-version':sv,'submit':"Check+For+Update"})
    req = urllib2.Request('http://blackbolt.x-scene.com/skins/xbmc/mc360/online.xml')
    ws= urllib2.urlopen(req)
    dat = ws.read()
    osvr = re.search('<skinversion>(.*)</skinversion>', dat, re.IGNORECASE).group(1)
    ws.close()
    return osvr

def xebi(td,t=0):
    if t == 1:
        xbmc.executebuiltin('XBMC.Notification(%s)' % td)
    else:
        xbmc.executebuiltin(td)

sv = ReadSkinXML()
osv = ReadOnlineXML()
if float(sv) < float(osv):
    xbmcgui.Dialog().ok( xbmc.getLocalizedString(31232),xbmc.getLocalizedString(31233) % (sv,osv))
    #xebi('MC360,New Version Available',1)
    xebi('Skin.SetBool(Update)')
else:
    xbmcgui.Dialog().ok( xbmc.getLocalizedString(31229), xbmc.getLocalizedString(31230),"",xbmc.getLocalizedString(31231) % (sv,osv))
    xebi('Skin.Reset(Update)')
xebi('Skin.SetString(CurrentVersion,%s)' % sv)
xebi('Skin.SetString(WebVersion,%s)' % osv)