from direct.task import Task

from UIBase import *
from ConversationUI import *
from JournalUI import *
from InventoryUI import *
from LifebarUI import *
from OffensiveSpellUI import *
from ModifierSporeUI import *
from DefensiveSpellUI import *
from ShroomUI import *
from PauseUI import *
from TimerUI import *

class HealthBar(NodePath):

    def __init__(self, owner):
        cm = CardMaker('%s_healthBar_cardMaker' %(owner.getName()))
        cm.setFrame(-5, 5, -1, 1)
        healthBar_card = cm.generate()
        NodePath.__init__(self, healthBar_card)
        
        self.owner = owner # type GameObject
        self.reparentTo(self.owner)
        #ownerHeight = self.getModelHeight(self.owner)
        min, max = Point3(), Point3()
        self.owner.calcTightBounds(min, max) 
        ownerHeight = max.getZ() - min.getZ()
        self.setZ(render, self.owner.getZ(render) + ownerHeight + ownerHeight/6.0)
        
        tex = loader.loadTexture('./LEGameAssets/Textures/lifebar.png')
        self.setTexture(tex)
        self.setScale(render, 1)
        
        self.setBillboardPointEye()
        self.refresh()
       
    def refresh(self):
        # 0 <= ratio <= 1, ratio = curHP / maxHP
        ratio = float(self.owner.getHealth()) / float(self.owner.getMaxHealth())
        
        if ratio <= 0:
            self.hide()
        else:
            self.setSx(ratio)


class GameplayUI(UIBase):
    
    def __init__(self,world):
        UIBase.__init__(self,world)
        
        #add frame border (temp!!!!!)
        #self.border = DirectFrame(image = ("./LEGameAssets/Textures/border.png"), frameColor=(0, 0, 0, 0),
        #                      image_scale = (1,1,1),image_pos = (0, 0, 0),frameSize=(-1,1,-1,1),pos=(0,0,0))
        #self.border.setTransparency(1)
        #self.border.reparentTo(render2d)
        
        self.journalUI = JournalUI(world)
        self.pauseUI = PauseUI(world)
        self.shroomUI = ShroomUI(world)
        self.conversationUI = ConversationUI(world)
        self.timerUI = TimerUI(world);
        self.timerUI.killTimer();
        
        #self.lifebarUI = LifebarUI(world)
        #self.offensiveSpellUI = OffensiveSpellUI(world)
        #self.modifierSporeUI = ModifierSporeUI(world)
        #self.defensiveSpellUI = DefensiveSpellUI(world)
        taskMgr.add(self.update, "updateUI")
        
        # change the conversationUI position
        self.world.accept('u', self.conversationUI.repositionUp)
        self.world.accept('j', self.conversationUI.repositionDown)
        
        
        # health bars
        self.healthBars = {}
        
    def removeAllHealthBars(self):
        for name, healthbar in self.healthBars.iteritems():
            healthbar.removeNode()
        self.healthBars = {}
    
    def showHealthBar(self, gameObj):
        if gameObj.getName() in self.healthBars:
            self.healthBars[gameObj.getName()].show()
        else:
            healthBar = HealthBar(gameObj)
            healthBar.setLight(self.world.overlayAmbientLightNP)
            self.healthBars[gameObj.getName()] = healthBar
    
    def hideHealthBar(self, gameObj):
        if gameObj.getName() in self.healthBars:
            self.healthBars[gameObj.getName()].hide()
    
    def removeHealthBar(self, gameObj):
        if gameObj.getName() in self.healthBars:
            self.healthBars[gameObj.getName()].removeNode()
            del self.healthBars[gameObj.getName()]
    
    def update(self, task):
        self.journalUI.update()
        self.conversationUI.update()
        self.pauseUI.update()
        self.timerUI.update()
        #self.inventoryUI.update()
        #self.lifebarUI.update()
        #self.offensiveSpellUI.update()
        #self.modifierSporeUI.update()
        #self.defensiveSpellUI.update()
        for gameObjName, healthBar in self.healthBars.iteritems():
            healthBar.refresh()
        
        return task.cont
    def hideAll(self):
        self.shroomUI.hideAll()
        self.pauseUI.hideAll()
        self.journalUI.hideAll()
        #self.border.hide()
#        self.journalUI.hide()
#        self.conversationUI.hide()
#        self.lifebarUI.hide()
#        self.offensiveSpellUI.hide()
#        self.modifierSporeUI.hide()
#        self.defensiveSpellUI.hide()
        
    def showAll(self):
        self.pauseUI.showAll()
        self.shroomUI.showAll();
        self.journalUI.showAll()
        #self.border.show()
#        self.journalUI.show()
#        self.conversationUI.show()
#        self.lifebarUI.show()
#        self.offensiveSpellUI.show()
#        self.modifierSporeUI.show()
#        self.defensiveSpellUI.show()
        
    
    def stop(self):
        taskMgr.remove("updateUI")
    
    def start(self):
        taskMgr.add(self.update, "updateUI")
        
        

