# Coded By DONNO (Email: darkdonno@gmail.com)
import urllib, os,re
import xbmc

SkinFolder = "q:\\skin\\MC360\\PAL\\"
SkinMediaFolder = "q:\\skin\\MC360\\media\\"

def ping(host):
    import socket,time
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    t1=float(0)
    t2=float(0)
    t1 = float(time.time()*1000)
    try:
        s.connect(( host, 80 ))
        t2 = float(time.time()*1000)
        s.close()
        del s
        return int((t2 - t1))
    except socket.error, (errcode, errmsg):
        t2 = time.time()
        if errcode == 111:# connection refused; means that the machine is up
            return int((t2 - t1))
        else:# something else; means that the machine is not up
            return None

def onlineChecker():
    pingdns=ping("www.teamxlink.co.uk")
    pingip=ping("158.69.102.211")
    if not(pingdns and pingip):
        xebi('XBMC.Notification(GamerCard,Update Failed)')
        #xbmcgui.Dialog().ok('GamerCard','Detected that DNS is most likey','not working correctly','Please set and try again')
        return 0
    else:
        return 1

def xebi(td):
    xbmc.executebuiltin(td)
def SetSettings(gamername,rep,score,zone):
    xebi('XBMC.Skin.SetString(GamerName,' +gamername+ ')')
    xebi('XBMC.Skin.SetString(GamerScore,' +score+ ')')
    xebi('XBMC.Skin.SetString(GamerRep,' +rep+ ')')
    xebi('XBMC.Skin.SetString(GamerZone,' +zone+ ')')
    #xebi('XBMC.Skin.SetString(GamerIcon,' +SkinMediaFolder+"myusericon.jpg"+')')

def DownloadImage(url,destfold,dest=None):
    """ From the KML Browser :P  """
    rawfilename = destfold + dest
    filename = os.path.abspath(rawfilename)
    try:
        urllib.urlretrieve(url, filename)
        xebi('XBMC.Skin.SetString(GamerIcon,' +SkinMediaFolder+"myusericon.jpg"+')')
        return 1
    except:
        return 0

def GetGTNFO(GamerNamer):
    card_html = ""
    xebi('XBMC.Notification(' + GamerNamer +',' + xbmc.getLocalizedString(31227) +')')
    GamerNamer = GamerNamer.replace(" ","%20")
    card_url = "http://gamercard.xbox.com/" + GamerNamer + ".card"
   
    wsock = urllib.urlopen(str(card_url))
    card_html = wsock.readlines()
    wsock.close()
    card_data = card_html[7]
    nfo = re.compile('</head><body><div class="XbcgcContainer"><div class="Xbcgc"><h3 class=".*"><a href="http://live.xbox.com/member/.*"><span class="XbcFLAL">(.*)</span></a></h3><div class="XbcgcInfo"><a href="http://live.xbox.com/member/.*"><img class="XbcgcGamertile" height="64" width="64" src="(.*)" alt=".*" title=".*" /></a><div class="XbcgcStats"><p><span class="XbcFLAL">Rep</span><span class="XbcFRAR"><img src="/xweb/lib/images/gc_repstars_external_(.*).gif" /></span></p><p><span class="XbcFLAL"><img alt="Gamerscore" src=".*" /></span><span class="XbcFRAR">(.*)</span></p><p><span class="XbcFLAL">Zone</span><span class="XbcFRAR">(.*)</span>.*', re.IGNORECASE).findall(card_data)[0]
    return nfo

global mode
mode = -1

def main():
    if xbmc.getInfoLabel('skin.string(gamername)') == "":
        return
    gamername = xbmc.getInfoLabel('skin.string(gamername)')
    online = onlineChecker()
    if online == 1:
        nfo = GetGTNFO(gamername)
        SetSettings(nfo[0],"gamercard_rep_"+nfo[2]+".png",nfo[3],nfo[4])
        DownloadImage(nfo[1],SkinMediaFolder,"myusericon.jpg")

if __name__ == "__main__":
    main()
