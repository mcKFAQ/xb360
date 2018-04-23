import urllib2, xml.dom.minidom, os, zipfile, traceback, sys, xbmcgui, time
import urllib, re
import cachedhttp

DEBUGMODE = 1


URL = 'http://warlion.byethost3.com/warlion/trainers.xml'

error = 'Error'
msg = 'Message'
popup = 'Popup'

#Debug data print function. Self explainary...
def printDebug(type, text):
    if DEBUGMODE == 1:
        if type == msg:
            print text
        elif type == error:
            print "\n" + "-"*5 + text + "-"*5
            traceback.print_exc(file=sys.stdout)
            print "-"*65 + "\n"
            xbmcgui.Dialog().ok('Error', text)
    if type == popup:
        xbmcgui.Dialog().ok('Error', text)
    else:
        return 
        
def mkdir(path):
    if not os.path.exists(path):
        printDebug(msg, 'Creating' + path)
        os.makedirs(path)
    else:
        printDebug(msg, 'Directory already exists')

def node_string(node):
    result = ""
    for text in node.childNodes:
        result = result + text.nodeValue
    return result
    
def node_date(node):
    return time.strptime(node_string(node), '%d/%m/%Y')

def node_int(node):
        return int(node_string(node))



#Settings class
#Much work to be done here. Should be able to change settings and so on in the future (when more settings are needed too)
class Settings:
    def __init__(self):
        #self.scriptpath = '../../scripts'
        self.scriptpath = 'Q:\\skin\\MC360\\LiveContent\\'
        self.showfolder = 0
    def loadsettings(self):
        pass
    
    def w_scriptpath(self, path):
        pass
        

settings = Settings()

###WEBSITE INTERACTION###


class MyCachedHTTP(cachedhttp.CachedHTTP):

    def __init__(self, callback):
        self.callback = callback
        cachedhttp.CachedHTTP.__init__(self)
        
    
    def onDataRetrieved(self, bytesRead, totalSize, url, localfile):
        if (not (bytesRead is None))&(not (totalSize is None)):
                pct=int(bytesRead*100.0/totalSize)
                self.callback('dl', pct)
        return True # if you return false, then it means cancel the download
   
    def onDownloadFinished(self,success):
        self.callback('done', 100)


def download(link, callback):
    printDebug(msg, 'Downloading ' + str(link))
    fetcher = MyCachedHTTP(callback)
    fetcher.setUserAgent('tintense.com')
    data = fetcher.urlopen(link)
    data = urllib2.urlopen(link).read()
    return data
    
#Gets scriptlist and parses this (xml).
def getScriptlist_site(callback):
    printDebug(msg, "Fetching content list from warlion")
    dialog = xbmcgui.DialogProgress()
    try:
        data = urllib2.urlopen(URL).read()
        if data != None or data > 50:
            printDebug(msg, "Content list downloaded successfully!")
            dialog.update(45,"Initializing...","Parsing content list...")
        else:
            printDebug(popup, "Couldn't fetch content list, returned empty object")
    except:
        printDebug(error, "Error while fetching content list.")
        pass
        
    printDebug(msg, "Parsing XML in scriptlist data")
    try:
        from xml.dom.minidom import parseString
        doc = parseString(data)
        printDebug(msg, "Parsing done successfully!")
        dialog.update(55,"Initializing...","Parsing done successfully!")
        return doc
    except:
        printDebug(error, "Parsing failed.")
        pass
       
class ParseXML:
    #Function for parsing the data got from site. Shouldn't need work really...
    def parsesite(self, callback):
        doc = getScriptlist_site(callback)
        if doc != None:
            scriptlist = []
            trainers = doc.firstChild.childNodes
            for item in trainers:
                if item.nodeType != xml.dom.minidom.Node.ELEMENT_NODE: continue
                script_temp = {}
                trainername = path = filename = "Unknown"
                for property in item.childNodes:
                    if property.nodeType != xml.dom.minidom.Node.ELEMENT_NODE: continue
                    name = property.nodeName
                    if name == "date":
                        value = node_date(property)
                    elif name == "downloads": value = node_int(property)
                    else: value = node_string(property)
                    script_temp[name] = value
                scriptlist.append(script_temp)
            return scriptlist


def DownloaderClass(message,url,dest):
    dp = xbmcgui.DialogProgress()
    dp.create("XBMC Live",message,url)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
    dp.close()

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print percent
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        db.close()
        
def unzip(path, filename): #Unzips files to path
        try:
            printDebug(msg, "Unzipping file")
            zip = zipfile.ZipFile(filename, 'r')
            namelist = zip.namelist()
            if os.path.exists(path + namelist[0]):
                if xbmcgui.Dialog().yesno('Overwrite?', 'The file ' + namelist[0] + ' already exists.', 'Overwrite this file?') != True:
                    os.remove(path + 'temp.zip')
                    return False, None
            isdir = os.path.isdir 
            join = os.path.join 
            norm = os.path.normpath 
            split = os.path.split
            dirlist = []
            xbmcgui.DialogProgress().update(95,"Unzipping file ...")
            for item in namelist:
                if not item.endswith('/'): 
                    root, name = split(item) 
                    directory = norm(join(path, root)) 
                    if not isdir(directory): 
                        os.makedirs(directory) 
                    file(join(directory, name), 'wb').write(zip.read(item)) 
            zip.close()
            del zip
            #namelist[0][0:-1] returns the name of the folder the script was installed into (root folder in zip).
            return True, namelist[0][0:-1]
        except:
            printDebug(msg, "An error occoured while unzipping.\nCorrupt file or not a zip file.")
            printDebug(error, "An error occoured while unzipping.\nCorrupt file or not a zip file.")
            return False, None


def install(installpath, url, callback, scriptinfo):
        
        data = download(url, callback)
        if data != None:
            f = open(installpath + 'temp.zip', 'wbo')
            xbmcgui.DialogProgress().update(85,"Unzipping file ...")
            f.write(data)
            xbmcgui.DialogProgress().update(90,"Unzipping file ...")
            f.close()
            state = True
            return state[0]
        else:
            print "DATA = NONE"
            return false
