from pandac.PandaModules import *
from direct.actor.Actor import Actor
from panda3d.ai import AICharacter

import Debug

class LifeStatus:
    ALIVE = 3
    DYING = 2
    DEAD = 1
    INANIMATE = 0
    
    def interpretLifeStatusString(string):
        if string == "ALIVE":
            return LifeStatus.ALIVE
        elif string == "DYING":
            return LifeStatus.DYING
        elif string == "DEAD":
            return LifeStatus.DEAD
        elif string == "INANIMATE":
            return LifeStatus.INANIMATE
        else:
            print "ERROR: invalid string passed to LifeStatus.interpretLifeStatusString (%s)" %(string)
            return LifeStatus.INANIMATE
    interpretLifeStatusString = staticmethod(interpretLifeStatusString)


class Strategy:
    NEUTRAL = 0
    
    def interpretStrategyString(string):
        if string == "NEUTRAL":
            return Strategy.NEUTRAL
        else:
            print "ERROR: invalid string passed to Strategy.interpretStrategyString (%s)" %(string)
            return Strategy.NEUTRAL
    interpretStrategyString = staticmethod(interpretStrategyString)

class GameObject(NodePath):
    
    def __init__(self, nodePath):
        NodePath.__init__(self, nodePath)
        
        self.actorHandle = None
        if isinstance(nodePath, Actor):
            self.actorHandle = nodePath
        
        self.aiCharHandle = AICharacter(nodePath.getName(), nodePath, 0.01, 0.01, 0.01)
        
        # default properties for a GameObject
        self.name = self.getName()
        self.scripts = {} # {string triggerType : list of string scriptTags} TODO: argsList
        self.passable = True
        #self.lifeStatus = LifeStatus.INANIMATE
        self.lifeStatus = LifeStatus.ALIVE
        self.curHP = 1 # CONSIDER: bundle HP and LifeStatus together
        self.maxHP = 1
        self.strategy = Strategy.NEUTRAL
        self.spells = []
        self.stopThreshold = 60
        
        self.__processTags()
    
    def setStopThreshold(self, threshold):
        self.stopThreshold = threshold
    
    def getStopThreshold(self):
        return self.stopThreshold
    
    # set properties based on tags of NodePath set in LE
    def __processTags(self):
        
        # passable
        if self.hasTag('LE-passable'):
            val = self.getTag('LE-passable')
            if val == "True":
                self.passable = True
            elif val == "False":
                self.passable = False
            else:
                print "ERROR: invalid value for \'LE-passable\' tag"
        
        # lifeStatus
        if self.hasTag('LE-lifeStatus'):
            val = self.getTag('LE-lifeStatus')
            self.lifeStatus = LifeStatus.interpretLifeStatusString(val)
        
        # HP
        # CONSIDER: automatically fill in one if the other is missing
        if self.hasTag('LE-currentHealth'):
            self.curHP = int(self.getTag('LE-currentHealth'))
        if self.hasTag('LE-maxHealth'):
            self.maxHP = int(self.getTag('LE-maxHealth'))
        
        # strategy
        if self.hasTag('LE-strategy'):
            val = self.getTag('LE-strategy')
            self.strategy = Strategy.interpretStrategyString(val)
            
    def setScripts(self, scriptsDict):
        # scriptsData form is
        # [ ( 'scriptName' , [ arg1 , arg2 ] ) , ... ]
        for trigger, scriptData in scriptsDict.items():
            self.scripts[trigger] = scriptData
            
    def callTrigger(self, world, triggerName):
        if triggerName in self.scripts:
            scriptsData = self.scripts[triggerName]
            Debug.debug(__name__,str(scriptsData))
            for key in sorted(scriptsData):
                tuple = scriptsData[key]
                world.scriptMgr.doScript(tuple)
                # CONSIDER: use world param to check scene, pass to scriptMgr to queue if scene is different
        else:
            pass
    
    # TODO: deprecated...remove
    def getNP(self):
        return self
    
    def getActorHandle(self):
        return self.actorHandle
    
    def getAICharacterHandle(self):
        return self.aiCharHandle
    
    def getAIBehaviorsHandle(self):
        return self.aiCharHandle.getAiBehaviors()
    
    def hasSpell(self):
        return (len(self.spells) > 0)
    
    def getSpell(self, index=0):
        if index < len(self.spells):
            return self.spells[index]
        else:
            print 'ERROR: tried to get a spell out of the list range'
    
    def addSpell(self, spell):
        self.spells.append(spell)
    
    def isPassable(self):
        return self.passable
    
    def getHealth(self):
        return self.curHP
    
    def getMaxHealth(self):
        return self.maxHP
    
    def decreaseHealth(self, delta):
        if self.lifeStatus == LifeStatus.ALIVE:
            self.curHP -= delta
            if self.curHP <= 0:
                self.curHP = 0
                self.lifeStatus = LifeStatus.DYING
                # TODO: launch onDeath trigger?  done in CombatMgrBase already
                # TODO: change status to DEAD

    def die(self):
        self.decreaseHealth(self.maxHP)
    
    def increaseHealth(self, delta):
        # CONSIDER: does increasing HP from 0 revive the object (switch LifeStatus) or do nothing?
        if self.lifeStatus == LifeStatus.ALIVE:
            self.curHP += delta
            if self.curHP > self.maxHP:
                self.curHP = self.maxHP
    
    def fillHealth(self):
        self.increaseHealth(self.maxHP)
    
    def __str__(self):
        return 'GameObject, name: %s' %(self.getName())