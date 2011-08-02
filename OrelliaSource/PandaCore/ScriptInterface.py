from Rope import *
from pandac.libpandaModules import *
from direct.showbase import Audio3DManager

class ScriptInterface:
    
    def __init__(self, world):
        self.world = world
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], world.cam)

    
    # IMPORTANT NOTE: Currently, all parameters passed to these functions are strings.  If they should be another type,
    # they must be cast or looked up

    # Controls
    
    def DisableControls(self):
        pass
    
    def EnableControls(self):
        pass
    
    # Cameras and Cutscenes
    
    def SetCamera(self, cameraNP):
        pass

    # Journal and Quests
    
    def OpenJournalEntry(self, entryTag):
        self.world.journalMgr.openJournalEntry(entryTag)
    
    def SetJournalEntryValue(self, entryTag, valueString,isIncr,minValue,delObj):
        print entryTag, valueString,isIncr,minValue,delObj
        return self.world.journalMgr.setEntryValue(entryTag, int(valueString),isIncr,minValue,delObj)

    # Conversations
    
    def OpenConversation(self, convoTag):
        self.world.conversationMgr.openConversation(convoTag)
    
    def CloseConversation(self):
        self.world.conversationMgr.closeConversation()
    
    # GameObject Property Manipulation
    
    # TODO: test
    def DestroyGameObject(self, gameObjString):
        print "Killing..."
        gameObj = self.GetGameObject(gameObjString)
        if gameObj != None:
            self.world.combatMgr.destroyObject(gameObj)
            self.world.enemyMan.destroyEnemy(gameObjString)
            self.world.clickMan.destroyClickable(gameObjString)
            if gameObjString in self.world.gameObjects:
                del self.world.gameObjects[gameObjString]
            if gameObjString in self.world.objects:
                del self.world.objects[gameObjString]
            gameObj.removeNode()
    
    def AddMainCharHP(self, hpString):
        self.AddHP(self.world.hero, int(hpString))
        
    def FillMainCharHP(self):
        self.FillHP(self.world.hero)
        
    def SubtractMainCharHP(self, hpString):
        self.SubtractHP(self.world.hero, int(hpString))
        
    def KillMainChar(self):
        self.Kill(self.world.hero)
        
    def AddHP(self, gameObjString, hpString):
        gameObj = self.GetGameObject(gameObjString)
        gameObj.increaseHealth(int(hpString))
    
    def FillHP(self, gameObjString):
        gameObj = self.GetGameObject(gameObjString)
        gameObj.fillHealth()
    
    def SubtractHP(self, gameObjString, hpString):
        gameObj = self.GetGameObject(gameObjString)
        gameObj.decreaseHealth(int(hpString))
    
    def Kill(self, gameObj):
        gameObj = self.GetGameObject(gameObjString)
        gameObj.die()
        
    def SetStrategy(self, gameObjString, strategyKey):
        gameObj = self.GetGameObject(gameObjString)
        pass
    
    def SetPassable(self, gameObjString, flag):
        gameObj = self.GetGameObject(gameObjString)
        pass
        # TODO: need to alter collision thingys here as well as GameObject variable
    
    # CONSIDER: knockback    
    # TODO: revive
    # TODO: respawn/relocate to the position of a placeholder object or start location
    
    # Changing Scenes
    
    def ChangeScene(self, sceneName):
        self.world.openScene(sceneName)
    
    def ChangeSceneTo(self, sceneName, startObjectName):
        self.world.openScene(sceneName)
        startObject = self.GetGameObject(startObjectName)
        if startObject != None:
            self.world.moveHeroTo(startObject)
        
    # Utility and Debugging
    
    def PrintToConsole(self, message):
        print 'SCRIPT MESSAGE: %s' %(message)
    
    def GetGameObject(self, gameObjString):
        if gameObjString in self.world.gameObjects:
            gameObj = self.world.gameObjects[gameObjString]
            return gameObj
        else:
            self.PrintToConsole('==ERROR== no GameObject named \'%s\' in scene' %(gameObjString))
            return None
    def RunCamera(self, cameraName, isLoop):
        self.world.runCamera(cameraName, isLoop)
        
    def AddItem(self,itemType, count):
        self.world.inventoryMgr.addItem(itemType,int(count))
        
        
        
    # Check Conditions
    
    def HasJournalEntry(self, entryTag):
        return self.world.journalMgr.isJournalEntryOpen(entryTag)
    
    def HasJournalEntryAndValue(self, entryTag, valueString):
        return self.world.journalMgr.isJournalEntryOnValue(entryTag, int(valueString))
    
    def HasManyItems(self, itemTag, count):
        return (self.world.inventoryMgr.getItemCount(itemTag) == count)
    
    def HasItem(self, itemTag):
        return self.world.inventoryMgr.hasItem(itemTag)
    
    def RunObjectOnRope(self, gameObjString, 
                        ropeString, 
                        sequenceTime,
                        isLoop=False,
                        followPath = False,
                        lookAtObject = None):
                            
        gameObj = self.GetGameObject(gameObjString)

        if(gameObj == None):
            return
        if ropeString in self.world.objects:
            rope = self.world.objects[ropeString]
        else:
            self.PrintToConsole('==ERROR== no GameObject named \'%s\' in scene' %(ropeString))
            return
        if(lookAtObject):
            lookAtObject = self.GetGameObject(lookAtObject)
            if(lookAtObject==None):
                return
            #print "type: ", type(gameObj.getNP().node())
        sequence = UniformRopeMotionInterval(rope,
                                             gameObj.getNP(),
                                             duration= float(sequenceTime),
                                             followPath = followPath,
                                             lookAt = lookAtObject)
        
        if(isinstance(gameObj.getNP().node(), Camera)):
            self.world.runCamera(gameObjString, sequence, isLoop)
            return
                
        self.world.addSequence(sequence)

        if(isLoop):
            sequence.loop()
        else:
            sequence.start()
            
            
    def RunObjectRope(self, gameObj, 
                        ropeObj, 
                        sequenceTime,
                        isLoop=False,
                        followPath = False,
                        lookAtObject = None):
                            
        rope = ropeObj 
        
        if(lookAtObject):
            lookAtObject = self.GetGameObject(lookAtObject)
            if(lookAtObject==None):
                return
            #print "type: ", type(gameObj.getNP().node())
        sequence = UniformRopeMotionInterval(rope,
                                             gameObj,
                                             duration= float(sequenceTime),
                                             followPath = followPath,
                                             lookAt = lookAtObject)
        
        if(isinstance(gameObj, Camera)):
            self.world.runCamera(gameObjString, sequence, isLoop)
            return
                
        self.world.addSequence(sequence)

        if(isLoop):
            sequence.loop()
        else:
            sequence.start()
        
    def playSound(self, soundName,canLoop,bypass=False):
        if soundName in self.world.assets.sounds:
            soundObj = self.world.assets.sounds[soundName]
        elif bypass:
            soundObj = soundName;
        else:
            self.PrintToConsole('==ERROR== no GameObject named \'%s\' in scene' %(soundName))
            return
        print soundObj
        mySound = base.loader.loadSfx(soundObj)
        if canLoop:
            mySound.setLoop(True)
        mySound.play()

    def playSound3d(self, object,soundName,canLoop,bypass=False):
        if soundName in self.world.assets.sounds:
            soundObj = self.world.assets.sounds[soundName]
        elif bypass:
            soundObj = soundName;
        else:
            self.PrintToConsole('==ERROR== no GameObject named \'%s\' in scene' %(soundName))
            return
        print soundObj
        mySound = self.audio3d.loadSfx(soundObj)
        self.audio3d.setSoundMinDistance(mySound,1)
        self.audio3d.attachSoundToObject(mySound,object)
        if canLoop:
            mySound.setLoop(True)
        mySound.play()
    
    def playMovie(self, movieName):
        self.world.playMovie(movieName) #nibbles
        
        
#    def RunObjectOnRopeFollow(self, gameObjString, ropeString, sequenceTime, isLoop = False):
#        gameObj = self.GetGameObject(gameObjString)
#        if(gameObj == None):
#            return
#        rope = self.GetGameObject(ropeString)
#        if ropeString in self.world.objects:
#            rope = self.world.objects[ropeString]
#        else:
#            self.PrintToConsole('==ERROR== no GameObject named \'%s\' in scene' %(ropeString))
#            return
#        
#        sequence = UniformRopeMotionInterval(rope,
#                                             gameObj.getNP(),
#                                             duration= float(sequenceTime),
#                                             followPath = True)
#         
#        self.world.addSequence(sequence)
#        if(isLoop):
#            sequence.loop()
#        else:
#            sequence.start()
            
        
    
    