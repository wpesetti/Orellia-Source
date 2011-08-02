from pandac.PandaModules import *
from Util import *
#from Library import *

class Sound:
    def __init__(self, name, asset, stream = True ):
        self.asset = asset
        self.name = name
        self.anims=[]#added by qiaosi
        self.actors=[]#added by qiaosi

        if(stream == True):
            self.audioObj = loader.loadSfx(asset.getFullFilename().getFullpath())
        else:
            self.audioObj = base.sfxManagerList[0].getSound(asset.getFullFilename().getFullpath(), 0, AudioManager.SMSample)
        
        #self.audioObj = None
        #
        
        
        #print type(base.sfxManagerList[0])
        #self.audioObj.setActive(False)
        #self.audioObj.unref()#audioObj
        #del self.audioObj
        #base.disableAllAudio() 
        #base.sfxManagerList[0].clearCache()
        #base.sfxManagerList[0].setActive(False)
        #self.audioObj = base.sfxManagerList[0].getSound(asset.getFullFilename().getFullpath(), 0, AudioManager.SMSample)
        #base.sfxManagerList[0].clearCache()#shutdown()#uncacheSound(asset.getFullFilename().getFullpath())#stopAllSounds()
        #base.musicManager.clearCache()
        #base.sfxManagterList[0].stopAllSounds()
        #base.musicManager.stopAllSounds()
    def getAsset(self):
        return self.asset
    
    def setName(self, val):
        self.name = val
    
    def getName(self):
        return self.name
    
    def play(self):
        #self.audioObj = base.sfxManagerList[0].getSound(asset.getFullFilename().getFullpath(), 0, AudioManager.SMSample)
        self.audioObj.play()
        
    def stop(self):
        if(self.audioObj):
            self.audioObj.stop()
        
    def getBalance(self):
        return self.audioObj.getBalance()
    
    def getLoop(self):
        return self.audioObj.getLoop()
    
    def getLoopCount(self):
        return self.audioObj.getLoopCount()
#    
#    def getPlayRate(self):
#        return self.audioObj.getPlayRate()
    def getStatus(self):
        ##should be 0 for BAD, 2 for PLAYING and 1 for Ready
     
        return self.audioObj.status()
    
    def getTime(self):
        return self.audioObj.getTime()
    
    def getVolume(self):
        return self.audioObj.getVolume()
    
    def getLength(self):
        return self.audioObj.length()
    
    def setBalance(self,val):
        ##THIS DOESN"T WORK AT ALL THANKS PANDA
        self.audioObj.setBalance(val)
        
    def setLoop(self,val):
        self.audioObj.setLoop(val)
        
    def setLoopCount(self,val):
        self.audioObj.setLoopCount(val)
        
#    def setPlayRate(self,val):
#        self.audioObj.setPlayRate(val)
#        
    def setTime(self,val):
        self.audioObj.setTime(val)
        
    def setVolume(self,val):
        self.audioObj.setVolume(val)

#    def encode(self):
#        pass
    def decode(node, inEditor=True, lib=None):
        for n in node.childNodes:
            if n.localName == "asset":
                assetName = n.childNodes[0].data.strip()
                asset = lib.sounds[assetName]
            elif n.localName == "name":
                name = n.childNodes[0].data.strip()
            elif n.localName == "isLooping":
                isLooping = bool(int(n.childNodes[0].data.strip()))
            elif n.localName == "loopCount":
                loopCount = int(n.childNodes[0].data.strip())
            elif n.localName == "time":
                time = float(n.childNodes[0].data.strip())
            elif n.localName == "volume":
                volume = float(n.childNodes[0].data.strip())
        

        sound = Sound(name, asset)

        sound.setLoop(isLooping)
        sound.setLoopCount(loopCount)
        #sound.setTime(time)
        sound.setVolume(volume)
            
        return sound 
    decode = staticmethod(decode)
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    sounds['" + self.name + "'] = loader.loadSfx('" + self.asset.filename.getFullpath() + "')\n")
        lines.append("    sounds['" + self.name + "'].setLoop(" + str(self.getLoop()) + ")\n")
        lines.append("    sounds['" + self.name + "'].setLoopCount(" + str(self.getLoopCount()) + ")\n")  
        lines.append("    sounds['" + self.name + "'].setVolume(" + str(self.getVolume()) + ")\n")
        
        return lines
    
    def encode(self, doc):
        node = doc.createElement("sound")
        
        asset = doc.createElement("asset")
        asset.appendChild(doc.createTextNode(self.asset.name))
        node.appendChild(asset)
        
        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(self.name))
        node.appendChild(name)
        
        isLooping = doc.createElement("isLooping")
        if self.getLoop():
            isLooping.appendChild(doc.createTextNode("1"))
        else:
            isLooping.appendChild(doc.createTextNode("0"))
        node.appendChild(isLooping)
        
        loopCount = doc.createElement("loopCount")
        loopCount.appendChild(doc.createTextNode(str(self.getLoopCount())))
        node.appendChild(loopCount)
        
        time = doc.createElement("time")
        time.appendChild(doc.createTextNode(str(self.getTime())))
        node.appendChild(time)
        
        volume = doc.createElement("volume")
        volume.appendChild(doc.createTextNode(str(self.getVolume())))
        node.appendChild(volume)
        
        return node
