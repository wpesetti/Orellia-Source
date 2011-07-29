
import os, time, wx, types, copy

from direct.task import Task
from pandac.PandaModules import *
from Sound import *
import xml.dom.minidom

import Library #added by qiaosi

class SoundMgrBase:
    """ SoundMgr will create, manage, update sounds in the scene """
    def __init__(self, editor):
        self.editor = editor

        #background music
        self.backgroundMusic=None #added by qiaosi
 
        # main sound repository
        self.sounds= {} 
    def reset(self):
        for s in self.sounds.values():
            s.asset.decSceneCount()
        self.sounds = {}

    def makeNameUnique(self, name):
        #modified by Jue 3/23/2011
        #baseName = "".join(name.split(':')[:-1])
        baseName = name
        n=1
        while True: 
            newName = baseName + ':' + str(n)
            if not newName in self.sounds:
                return newName
            n = n + 1
           
    
    def renameSound(self, sound, newName):
        del self.sounds[sound.getName()]
        self.sounds[str(newName)] = sound
                
        sound.setName(newName)       
        
    
    def stopAllSounds(self):
        for sound in self.sounds:
            self.sounds[sound].stop()
            
    def addNewSound(self, name, asset):
        if name in self.sounds:
            name = self.makeNameUnique(name)

        soundObj = Sound(name, asset)
        self.sounds[name] = soundObj
        asset.incSceneCount()
        
        return soundObj
    def removeSound(self, name):
        self.sounds[name].asset.decSceneCount()
        del self.sounds[name]
       
    def decode(self, node, merge=False, lib=None, otherName=None):
        if not merge:
            self.reset()
            
        if not lib:
            lib = base.le.lib
        
        # Add previxes, to maintain unique names when merging files
        if otherName:
            prefix = otherName+"_"
        else:
            prefix = ""
        
        for n in node.childNodes:
            if n.localName == "sound":
                sound = Sound.decode(n, lib=lib)
                sound.setName(prefix + sound.name)
                
                self.sounds[sound.getName()] = sound
                sound.asset.incSceneCount()
                               
                #qs
                actorObjList, actorNameList =  base.le.objectMgr.findObjectsByAssetRName("actor")
                for actorObj in actorObjList:
                    if actorObj.sounds_anims_map != {}:
                        for anim, sound in actorObj.sounds_anims_map.iteritems():
                            for soundName in self.sounds.keys():
                                if soundName  == sound:
                                    soundObj = self.sounds[soundName]
                                    actorObj.sounds_anims_map[anim]= soundObj


               
    def encode(self, doc):
        sounds = doc.createElement("sounds")
        for sound in self.sounds.values():
            sounds.appendChild(sound.encode(doc))
        

        
        return sounds
        
    def BVWEncode(self):
        lines = []
        lines.append("def loadSounds():\n")
        lines.append("    sounds = {}\n")
        
        for s in self.sounds.values():
            lines.append("\n")
            lines.extend(s.BVWEncode())
        
        lines.append("\n")
        lines.append("    return sounds\n")
        
        return lines
    
    #-------added by qiaosi----------------------
    def attachSoundToAnims(self, actor, anim, sound_for_anim):

        actor_obj = self.editor.objectMgr.findObjectById(actor)
        #anim_fullname = actor_obj.getAllAnims()[anim].getFullFilename()# get the full name of the animation   
        #actor_obj.sounds_anims_map[anim_fullname]= sound_for_anim #map the name of animation with the name of sound
        actor_obj.sounds_anims_map[anim]=self.sounds[sound_for_anim] #map the name of animation with the instance of sound
        
        self.sounds[sound_for_anim].anims.append(anim)
        self.sounds[sound_for_anim].actors.append(actor)
        #print "attach sound to anims :",actor_obj.sounds_anims_map
        
    def removeSoundFromAnims(self, actor, anim, sound_for_anim):
        actor_obj = self.editor.objectMgr.findObjectById(actor)
        #anim_fullname = actor_obj.getAllAnims()[anim].getFullFilename()# get the full name of the animation
        del actor_obj.sounds_anims_map[anim]
        
        self.sounds[sound_for_anim].anims.remove(anim)
        self.sounds[sound_for_anim].actors.remove(actor)
        #print "delete sound to anims :",actor_obj.sounds_anims_map
        
    
    def setBackgroundMusic(self,music):
        self.backgroundMusic = self.sounds[music]
    
    def playBackgroundMusic(self):
        if self.backgroundMusic != None:
            self.backgroundMusic.setLoop(True) 
            self.backgroundMusic.play() 
        
    def stopBackgroundMusic(self):
        if self.backgroundMusic != None:
            self.backgroundMusic.setLoop(False)
        
    #------------------------------------------------
       