"""
    By DarkDonno [Team BlackBolt]     (darkdonno@gmail.com)
    Designed For MC360
"""

import xbmc, xbmcgui,os

__title__ = "Wallpaper Setter"
__version__ = '1.0'

"""
 Possible Features for Future
 - Download From NET
 - Select ZIP and Extract then Set
"""

"""
Doc

For wallpaper packs do this
Note: They can be png or bmp or gif
NOTE: GIF will slow the xbox down.

Halo\
Halo\wallpaper-guidepanel.png
Halo\wallpaper-Games.png
Halo\wallpaper-kai.png         #notes this is for both kai or the extra window
Halo\wallpaper-Media.png
Halo\wallpaper-System.png

OR

Halo2\
Halo2\wallpaper-guidepanel.png
Halo2\wallpaper-all.png
"""

def main():
    dir = xbmcgui.Dialog().browse(0, xbmc.getLocalizedString(31234), xbmc.getLocalizedString(31235))
    if dir != "":
        dostuff(dir,"GuidePanel")
        alldir = "%s\\wallpaper-all.png" % (dir)
        if os.path.exists(alldir):
            doAll(alldir)
        else:
            dostuff(dir,"KAI")
            dostuff(dir,"Games")
            dostuff(dir,"Media")
            dostuff(dir,"System")
            dostuff(dir,"Login")

def doAll(mypath):
    mypath.replace("\\\\","\\")
    SetStr("KAI",mypath)
    SetStr("Games",mypath)
    SetStr("Media",mypath)
    SetStr("System",mypath)
    SetStr("Login",mypath)

def SetStr(name,value):
    bicmd = 'Skin.SetString(%s,%s)' % (name,value)
    xbmc.executebuiltin(bicmd)

def dostuff(mypath,ttype):
    dire = "%s\\wallpaper-%s.png" % (mypath,ttype)
    dire = dire.replace('\\\\','\\')
    dire2 = "%s\\wallpaper-%s.jpg" % (mypath,ttype)
    dire2 = dire2.replace('\\\\','\\')
    dir_gif = "%s\\wallpaper-%s.gif" % (mypath,ttype)
    dir_gif = dir_gif.replace('\\\\','\\')
    if os.path.exists(dire):
        SetStr(ttype,dire)
    elif os.path.exists(dire2):
        SetStr(ttype,dire2)
    elif os.path.exists(dir_gif):
        SetStr(ttype,dir_gif)
    else:
        xbmcgui.Dialog().ok(xbmc.getLocalizedString(31238), xbmc.getLocalizedString(31236) % ttype, xbmc.getLocalizedString(31237))

if __name__ == "__main__":
    main()


