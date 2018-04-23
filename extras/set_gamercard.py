# Coded By DONNO (Email: darkdonno@gmail.com)
import urllib, os,re
import xbmc,xbmcgui

StuffFolder = "q:\\skin\\MC360\\extras\\"
SkinFolder = "q:\\skin\\MC360\\PAL\\"
SkinMediaFolder = "q:\\skin\\MC360\\media\\"
bnf="button-nofocus.png"
bf="button-focus.png"
lcf="iconlist-nofocus.png"
lcnf="iconlist-focus.png"
fc = "0xFF000000"

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
def unikeyboard(default,header=""):
    kb = xbmc.Keyboard(default,header)
    kb.doModal()
    if (kb.isConfirmed()):
        return kb.getText()
    else:
        return default
def onlineChecker():
    pingdns=ping("www.xbox.com")
    pingip=ping("65.59.234.166")
    if not(pingdns and pingip):
        xbmcgui.Dialog().ok(xbmc.getLocalizedString(31212),xbmc.getLocalizedString(31213),xbmc.getLocalizedString(31214),xbmc.getLocalizedString(31215))
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
    xebi('XBMC.Skin.SetString(GamerIcon,' +SkinMediaFolder+"myusericon.jpg"+')')
  
def DownloadImage(url,destfold,dest=None):
    """ From the KML Browser :P  """
    rawfilename = destfold + dest
    filename = os.path.abspath(rawfilename)
    try:
        urllib.urlretrieve(url, filename)
        return rawfilename
    except:
        return None

def GetGTNFO(GamerNamer):
    card_html = ""
    GamerNamer = GamerNamer.replace(" ","%20")
    card_url = "http://gamercard.xbox.com/" + GamerNamer + ".card"
    #nfArg = '%s,%s' % (xbmc.getLocalizedString(31216),xbmc.getLocalizedString(31217))
    xebi('XBMC.Notification(' + xbmc.getLocalizedString(31216) +',' + xbmc.getLocalizedString(31217) +')')
    wsock = urllib.urlopen(str(card_url))
    card_html = wsock.readlines()
    wsock.close()
    card_data = card_html[7]
    nfo = re.compile('</head><body><div class="XbcgcContainer"><div class="Xbcgc"><h3 class=".*"><a href="http://live.xbox.com/member/.*"><span class="XbcFLAL">(.*)</span></a></h3><div class="XbcgcInfo"><a href="http://live.xbox.com/member/.*"><img class="XbcgcGamertile" height="64" width="64" src="(.*)" alt=".*" title=".*" /></a><div class="XbcgcStats"><p><span class="XbcFLAL">Rep</span><span class="XbcFRAR"><img src="/xweb/lib/images/gc_repstars_external_(.*).gif" /></span></p><p><span class="XbcFLAL"><img alt="Gamerscore" src=".*" /></span><span class="XbcFRAR">(.*)</span></p><p><span class="XbcFLAL">Zone</span><span class="XbcFRAR">(.*)</span>.*', re.IGNORECASE).findall(card_data)[0]
    return nfo
def SetupButtons(win,x,y,w,h,gap=0,):
    win.numbut  = 0
    win.butx = x
    win.buty = y
    win.butwidth = w
    win.butheight = h
    win.gap = gap

def AddButton(win,text,ext_gap=0,text_fc="dialog-context-button-FO.png",textn_fc="dialog-context-button-NF.png"):
    #text_fc="button-focus.png",textn_fc="button-nofocus.png"
    win.buty = win.buty + ext_gap
    c = xbmcgui.ControlButton(win.butx ,win.buty + (win.numbut * win.butheight + win.gap*win.numbut),win.butwidth,win.butheight,text,text_fc,textn_fc,textColor=fc,font="font13",alignment=6)
    win.addControl(c)
    win.numbut += 1
    return c

class Context(xbmcgui.WindowDialog):
    def __init__(self):
        DiaConTxt_X = 260
        DiaConTxt_X = int(self.getWidth() / float(2) -  235 / float(2))
        base_height = int(self.getHeight() / float(2) - 180 /2)
        #base_height = 215
        self.cbg1 = xbmcgui.ControlImage(DiaConTxt_X, base_height, 235,25, "dialog-context-top.png")
        self.cbg2 = xbmcgui.ControlImage(DiaConTxt_X, base_height+25, 235,130, "dialog-context-middle.png")
        self.cbg3 = xbmcgui.ControlImage(DiaConTxt_X,base_height+130+25, 235,25, "dialog-context-bottom.png")
        self.addControl(self.cbg1)
        self.addControl(self.cbg2)
        self.addControl(self.cbg3)
        SetupButtons(self,DiaConTxt_X+20,base_height+25,200,38,5)
        self.btnGrb = AddButton(self,xbmc.getLocalizedString(31218))
        self.btnEdt = AddButton(self,xbmc.getLocalizedString(31219))
        self.btnCan = AddButton(self,xbmc.getLocalizedString(31220))
        self.setFocus(self.btnGrb)
        self.btnGrb.controlDown(self.btnEdt)
        self.btnEdt.controlDown(self.btnCan)
        self.btnCan.controlDown(self.btnGrb)
        self.btnGrb.controlUp(self.btnCan)
        self.btnEdt.controlUp(self.btnGrb)
        self.btnCan.controlUp(self.btnEdt)
    def onAction(self, action):
        global mode
        if action == 10:
            mode = 0
            self.close()
    def onControl(self, control):
        global mode
        if control == self.btnCan:
            mode = 0
        elif control == self.btnGrb:
            mode = 1
        elif control == self.btnEdt:
            mode = 2
        else:
            mode = 0
        self.close()
#########
## MAIN #
#########
global mode
mode = -1
def main():
    #kb = xbmc.Keyboard(xbmc.getInfoLabel('skin.string(gamername)'),"Enter Xbox.com Gamertag")
    kb = xbmc.Keyboard("",xbmc.getLocalizedString(31221))
    kb.doModal()
    if (kb.isConfirmed()):
        gamername =  kb.getText()
        if gamername == "":
            xbmcgui.Dialog().ok(xbmc.getLocalizedString(31212),xbmc.getLocalizedString(31222),xbmc.getLocalizedString(31223))
        else:
            online = onlineChecker()
            if online == 1:
                nfo = GetGTNFO(gamername)
                SetSettings(nfo[0],"gamercard_rep_"+nfo[2]+".png",nfo[3],nfo[4])
                print nfo[1]
                DownloadImage(nfo[1],SkinMediaFolder,"myusericon.jpg")
                xebi("XBMC.ReloadSkin")
            else: 
                if not xbmcgui.Dialog().yesno(xbmc.getLocalizedString(31212),xbmc.getLocalizedString(31224),xbmc.getLocalizedString(31225)):
                        SetSettings(gamername,"gamercard_rep_12.png","-","-")
                        xebi("XBMC.ReloadSkin")

if __name__ == "__main__":
    main()
    """
    cnxselect = Context()
    cnxselect.doModal()
    del cnxselect
    if mode == 1:
        main()
    elif mode == 2:
        #xbmc.executebuiltin('XBMC.ActivateWindow(1122)')
        xbmc.executebuiltin('XBMC.ActivateWindow(1125)')
    else:
        pass
    """
