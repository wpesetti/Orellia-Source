#Class to handle events through clickable objects
import sys,random,ast

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.task import Task
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
sys.path.append("./Panda Core scripts")
import ScriptInterface  


class ClickManager(DirectObject):
    def __init__(self):
        self.ClickableList = {}
        self.accept('createClickable',self.createClickable)
        self.accept('destroyClickable',self.destroyClickable)
        self.accept('destroyAllClickables',self.destroyAll)
        
    def createClickable(self,world,object,name,clickFunc,textIn = None):
        self.ClickableList[object.getName()] = Clickable(world,object,name,clickFunc,textIn) #Creates enemies
        
    def destroyClickable(self,name): #destroys an Clickable
        try:
            self.ClickableList[ii].delete()
            self.ClickableList.pop(ii)
        except:
            print "Gone"

    def destroyAll(self): #destroys all Clickables
        for ii in self.ClickableList:
            temp = self.ClickableList[ii]
            self.ClickableList.pop(ii)
            del temp
    def notifyClickable(self,name):
        self.ClickableList[name].notify()

#This object excecuts a command when pressed
class Clickable(DirectObject):
    def __init__(self,world,object,name,clickFunc,textIn=None):
        self.worldObj = world
        self.gameObj = object
        self.name = name
        self.clickFunc = clickFunc
        self.textOn = False
        self.keyBind = 'u'
        self.disable = False
        print textIn
        if not textIn == None:
            self.text = textIn.format(self.keyBind)
        else:
            self.text = "Press \""+self.keyBind+"\" to talk with "+self.name
        print self.clickFunc,"-TEXT"
        self.textScreen = OnscreenText(text = "", pos = (-0.6, 0.5), scale = 0.07,wordwrap = 10,fg = (1,0,0,1))
        taskMgr.add(self.clickUpdate,"clickUpdater")
        
    def clickUpdate(self,task):
        if not self.disable:
            playerPos = Vec2(self.worldObj.hero.getX(), self.worldObj.hero.getY())
            clickPos = Vec2(self.gameObj.getX(), self.gameObj.getY())
            if (clickPos - playerPos).length() < 60.0:
                if not self.textOn:
                    self.textScreen = OnscreenText(self.text, pos = (.5, 0.5), scale = 0.07,wordwrap = 10,fg = (1,1,1,1),bg = (0,0,0,1))
                self.accept('u',self.handleFunc)
                self.textOn = True
            else:
                if self.textOn:
                    self.textScreen.destroy()
                    self.textOn = False
                    self.ignore('u')
                    self.worldObj.scriptInterface.CloseConversation()
            return task.cont
    
    def handleFunc(self):
        exec "self."+self.clickFunc
    
    def talkToNpc(self,convoTag):
        self.textScreen.destroy()
        self.worldObj.scriptInterface.OpenConversation(convoTag)
    
    def pickUpItem(self,entryTag,value,isIncr,minValue,delObj):
        condit = self.worldObj.scriptInterface.SetJournalEntryValue(entryTag, value,isIncr,minValue,delObj)
        if condit:
            self.textScreen.destroy()
            self.textOn = False
            self.disable = True
            self.worldObj.scriptInterface.DestroyGameObject(delObj)
            self.ignore('u')

        
    def worldCall(self,funcName,condition):
        if self.gameObj.getTag("param") == "oneShot":
            self.textScreen.destroy()
            self.textOn = False
            self.ignore('u')
            self.disable = True

        if eval("self.worldObj."+condition):
            exec "self.worldObj."+funcName

    def delete(self):
        taskMgr.remove("clickUpdater")
        del self

    def activateTerminal(self):
        condit = self.worldObj.scriptInterface.SetJournalEntryValue("Ship",10,True,0,None)
        if condit:
            self.worldObj.terminals += 1
            self.textScreen.destroy()
            self.textOn = False
            self.ignore('u')
            self.disable = True
        print self.worldObj.terminals
        if self.worldObj.terminals == 3:
            self.worldObj.scriptInterface.DestroyGameObject("SpecialWall")