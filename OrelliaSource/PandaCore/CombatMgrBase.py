# combat stuff

import math
import Debug

from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from panda3d.ai import *
from GameObject import *
from SpellConstants import *

# temp!
#from ExportGameTemplate import BITMASK_WALL, BITMASK_GROUND
BITMASK_GROUND = BitMask32.bit(0)
BITMASK_CLICK = BitMask32.bit(1)
BITMASK_HERO_COLLIDE = BitMask32.bit(2)
BITMASK_WALL = BitMask32.bit(3)


def findDistance2D(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt((dx*dx) + (dy*dy))
    return dist

def findDistance3D(x1, y1, z1, x2, y2, z2):
    dist2D = findDistance2D(x1, y1, x2, y2)
    return math.sqrt((dist2D*dist2D) + ((z2-z1)*(z2-z1)))

def findGameObjDistance(gameObj1, gameObj2):
    return findDistance3D(gameObj1.getNP().getX(render), gameObj1.getNP().getY(render), gameObj1.getNP().getZ(render),
                      gameObj2.getNP().getX(render), gameObj2.getNP().getY(render), gameObj2.getNP().getZ(render))

class CombatGraph:
    
    def __init__(self, combatMgr, gameObjsDict, mainChar):
        self.combatMgr = combatMgr
        self.gameObjsDict = gameObjsDict
        gameObjs = self.gameObjsDict.values()
        
        # temp? the main char is always attackable...
        mainChar.getNP().setTag('LE-attackable', 'True')
        
        self.graph = {}
        
        for gameObj in gameObjs:
            # CONSIDER: optimize based on tag structure...if there are no combat tags whatsoever do not include as a vertex in graph
            self.graph[gameObj.getName()] = {}
            
        # set up the relations
        for startIndex in range(len(gameObjs) - 1):
            fromObj = gameObjs[startIndex]
            for toObj in gameObjs[startIndex + 1 : ]:
                
                # temp
                #toObj.getNP().setTag('LE-aggression', '0')
                #fromObj.getNP().setTag('LE-attackable', 'False')
                #toObj.getNP().setTag('LE-attackable', 'False')
                
                # TODO: some sort of process tags function
                if self.__isAttackable(fromObj):
                    self.graph[toObj.getName()][fromObj.getName()] = True
                else:
                    self.graph[toObj.getName()][fromObj.getName()] = False
                
                if self.__isAttackable(toObj):
                    self.graph[fromObj.getName()][toObj.getName()] = True
                else:
                    self.graph[fromObj.getName()][toObj.getName()] = False
    
    def __getPotentialAttackers(self, victim):
        attackers = []
        for name, gameObj in self.gameObjsDict.iteritems():
            if name != victim.getName():
                if self.graph[name][victim.getName()] == True:
                    attackers.append(gameObj)
        return attackers
    
    def getPotentialOpponents(self, attacker):
        opponents = []
        for otherName in self.graph[attacker.getName()]:
            if self.graph[attacker.getName()][otherName] == True:
                opponent = self.gameObjsDict[otherName]
                opponents.append(opponent)
        return opponents
    
    def __isAttackable(self, gameObj):
        if gameObj.getNP().hasTag('LE-attackable'): # CONSIDER: or if it is mainChar
            if gameObj.getNP().getTag('LE-attackable') == 'True': # CONSIDER: format of bool?
                return True
        return False
    
    def __getAggressionRange(self, gameObj):
        if gameObj.getNP().hasTag('LE-aggression'):
            range = float(gameObj.getNP().getTag('LE-aggression'))
            return range
        return 0
    
    def getPotentialAttackerNameAggroMap(self, victim):
        attackersMap = {}
        
        for potentialAttacker in self.__getPotentialAttackers(victim):
            name = potentialAttacker.getName()
            aggroRange = self.__getAggressionRange(potentialAttacker)
            attackersMap[name] = aggroRange
        return attackersMap
    
    def checkCanAttack(self, attackerObj, targetObj):
        if attackerObj.getName() in self.graph:
            if targetObj.getName() in self.graph[attackerObj.getName()]:
                return self.graph[attackerObj.getName()][targetObj.getName()]
        return False
    
    def removeCombatant(self, gameObj):
        if gameObj.getName() in self.graph:
            del self.graph[gameObj.getName()]
        for otherObjName, targets in self.graph.iteritems():
            if gameObj.getName() in self.graph[otherObjName]:
                del self.graph[otherObjName][gameObj.getName()]
    
    def hasCombatant(self, gameObj):
        return gameObj.getName() in self.graph
    
    def __str__(self):
        # CONSIDER: use string representations of the relations for clarity
        return self.graph

class CombatMgrBase:
    
    def __init__(self, world):
        self.world = world
        
        self.aiWorld = AIWorld(render)
        self.combatGraph = CombatGraph(self, self.world.gameObjects, self.world.hero)
        self.inactiveEnemies = self.combatGraph.getPotentialAttackerNameAggroMap(self.world.hero)
        
        self.sequences = {}
        self.sequences[self.world.hero.getName()] = []
        # TEMP?
        self.opponentColHandlerQueues = {}
        for potentialOpponent in self.combatGraph.getPotentialOpponents(self.world.hero):
            # spell
            defaultSpell = Spell(potentialOpponent, SPELL_ENEMYBLAST)
            potentialOpponent.addSpell(defaultSpell)
            # mass
            defaultMass = 0.02
            potentialOpponent.getAICharacterHandle().setMass(defaultMass)
            # stop threshold
            defaultStopThreshold = 70
            potentialOpponent.setStopThreshold(defaultStopThreshold)
            # health bars
            self.world.gameplayUI.showHealthBar(potentialOpponent)
            # collisions
            self.setupGameObjectCollisions(potentialOpponent)
            # sequences list
            self.sequences[potentialOpponent.getName()] = []
        
        self.activeEnemies = {}
        self.projectiles = [] # list of tuples [ (projectile, targetGameObject), ... ]
        
        self.damageFxStatus = {}
        for name, obj in self.world.gameObjects.iteritems():
            self.damageFxStatus[name] = False
        self.obstacleRecoveryStatus = {}
        for name, obj in self.world.gameObjects.iteritems():
            self.obstacleRecoveryStatus[name] = False
    
    def updateAITask(self, task):
        self.manageAggro(self.world.hero)
        self.moveCombatants(self.world.hero)
        self.moveProjectiles()
        self.aiWorld.update()
        
        return task.cont
    
    def setupGameObjectCollisions(self, gameObj):
        cn_wall = CollisionNode('%s_wallCollider' %(gameObj.getName()))
        cn_wall.addSolid(CollisionSphere(0,0,0,7))
        cnp_wall = gameObj.attachNewNode(cn_wall)                
        cn_wall.setFromCollideMask(BITMASK_WALL)
        cn_wall.setIntoCollideMask(BitMask32.allOff())
        queue_wall = CollisionHandlerQueue()
        self.world.cTrav.addCollider(cnp_wall, queue_wall)
        
        cn_ground = CollisionNode('%s_groundCollider' %(gameObj.getName()))
        cn_ground.addSolid(CollisionLine(Point3(0,0,0), Vec3(0,0,-1)))
        cn_ground.setFromCollideMask(BITMASK_GROUND)
        cn_ground.setIntoCollideMask(BitMask32.allOff())
        cnp_ground = gameObj.attachNewNode(cn_ground)
        queue_ground = CollisionHandlerQueue()
        self.world.cTrav.addCollider(cnp_ground, queue_ground)
        
        self.opponentColHandlerQueues[gameObj.getName()] = {'wall':queue_wall, 'ground':queue_ground} 
    
    def startTasks(self):
        taskMgr.add(self.updateAITask, 'updateAITask', appendTask=True)
    
    def stopTasks(self):
        taskMgr.remove('updateAITask')
    
    def manageAggro(self, aggressorObj):
        namesActivated = []
        for potentialEnemyName, aggroRange in self.inactiveEnemies.iteritems():
            if findGameObjDistance(aggressorObj, self.world.gameObjects[potentialEnemyName]) <= aggroRange:
                self.activeEnemies[potentialEnemyName] = aggroRange
                newEnemy = self.world.gameObjects[potentialEnemyName]
                Debug.debug(__name__,'newEnemy : '+str(newEnemy)+str(type(newEnemy)))
                self.aiWorld.addAiChar(newEnemy.getAICharacterHandle())
                newEnemy.getAIBehaviorsHandle().pursue(aggressorObj, 1.0)
                # TODO: override other movement that the gameObj may have...paths, idle anim, etc.
                namesActivated.append(potentialEnemyName)
        for nameActivated in namesActivated:
            del self.inactiveEnemies[nameActivated]
    
    def moveCombatants(self, aggressorObj):
        # Check ground and wall collisions for all combatants, active or inactive
        for name, queues in self.opponentColHandlerQueues.iteritems():
            combatant = self.world.gameObjects[name]
            #== Walls
            wallEntries = []
            for w in queues['wall'].getEntries():
                np = w.getIntoNodePath().findNetTag('OBJRoot')
                if np.hasTag('LE-wall'):
                    wallEntries.append(w)        
            if wallEntries and not self.obstacleRecoveryStatus[combatant.getName()]:
                backupTime = 2.0
                backupDist = -5000
                
                backup_target = NodePath('%s_backupTarget')
                backup_pos = render.getRelativePoint(combatant, (0, -backupDist, 0))
                backup_target.reparentTo(render)
                backup_target.setPos(backup_pos)
#                print 'backup_pos : ', backup_pos
#                backup_target.setPos(236, 1, 11)
                
                backup = Sequence()
                backup.append(Func(self.setObstacleRecoveryFlag, combatant, True))
                backup.append(Func(self.world.disableMovement, combatant))
                backup.append(Func(combatant.getAIBehaviorsHandle().seek, backup_target, 1.0))
                backup.append(Wait(backupTime))
                backup.append(Func(combatant.getAIBehaviorsHandle().removeAi, 'seek'))
                backup.append(Func(self.setObstacleRecoveryFlag, combatant, False))
                backup.append(Func(self.attemptResumeMovement, combatant))
                backup.append(Func(self.setSequenceFinished, name, backup))
                
                self.sequences[name].append(backup)
                backup.start()
            else:
                pass
            
            queues['wall'].clearEntries()
            
            #== Ground
            groundEntries = []
            for e in queues['ground'].getEntries():
                if e.getIntoNodePath().hasNetTag('OBJRoot'):
                    #find the actual root of the object
                    np = e.getIntoNodePath().findNetTag('OBJRoot')
                    #only react to objects that are tagged as the ground
                    if np.hasTag('LE-ground'):
                        groundEntries.append(e)
                        
            if groundEntries:
                groundEntries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                                   x.getSurfacePoint(render).getZ()))
                
                combatant.setZ(groundEntries[0].getSurfacePoint(render).getZ())
            
            queues['ground'].clearEntries()

        # Manage distance and attacking for active enemies
        for enemyName, aggroRange in self.activeEnemies.iteritems():
            # CONSIDER: if player moves outside a factor of aggroRange, make enemy inactive (disable chasing)
            # TODO: play move animation of each moving gameObj
            enemy = self.world.gameObjects[enemyName]
            distToTarget = findGameObjDistance(enemy, aggressorObj)
            
            enemyBehavior = enemy.getAIBehaviorsHandle()
            stopThreshold = enemy.getStopThreshold()
            
            if distToTarget <= stopThreshold:
                self.world.disableMovement(enemy)
            elif (enemyBehavior.behaviorStatus("pursue") == "paused"):
                self.attemptResumeMovement(enemy)
                
            # CONSIDER: careful if stopThreshold > attackRange...that would be silly
            
            if enemy.hasSpell():
                enemySpell = enemy.getSpell()
                if distToTarget <= enemySpell.getAttackRange():
                    self.queueAttack(enemy, enemySpell, aggressorObj)

    def setSequenceFinished(self, gameObjName, seq):
        if gameObjName in self.sequences:
            self.sequences[gameObjName].remove(seq)

    def moveProjectiles(self):
        for tuple in self.projectiles:
            proj = tuple[0]
            targetObj = tuple[1]

            distToTarget = findGameObjDistance(proj, targetObj)

            # Projectile hit
            if distToTarget <= proj.getHitThreshold():
                targetObj.decreaseHealth(proj.getDamage())
                
                self.destroyProjectile(tuple)
                if targetObj.getHealth() <= 0:
                    self.destroyObject(targetObj)
                else:
                    # flash the object red for feedback, if visual effects aren't already playing
                    if not self.damageFxStatus[targetObj.getName()]:
                        delay = 0.2
                        flashRed = Sequence()
                        flashRed.append(Func(self.setDamageFxFlag, targetObj, True))
                        flashRed.append(LerpFunc(self.setRedColorScale, fromData=1.0, toData=3.0, duration=delay, extraArgs=[targetObj, targetObj.getColorScale()]))
                        flashRed.append(Wait(delay))
                        flashRed.append(LerpFunc(self.setRedColorScale, fromData=3.0, toData=1.0, duration=delay, extraArgs=[targetObj, targetObj.getColorScale()]))
                        flashRed.append(Func(self.setDamageFxFlag, targetObj, False))
                        flashRed.append(Func(self.setSequenceFinished, targetObj.getName(), flashRed))
                        
                        self.sequences[targetObj.getName()].append(flashRed)
                        flashRed.start()
                    
                    # Aggravate the target
                    if (targetObj.getName() not in self.activeEnemies) and (targetObj.getName() in self.inactiveEnemies):
                        aggroRange = self.inactiveEnemies[targetObj.getName()]
                        if aggroRange >= 0:
                            # Careful of task threading here with manageAggroTask - avoid calling pursue twice
                            
                            self.activeEnemies[targetObj.getName()] = aggroRange
                            self.aiWorld.addAiChar(targetObj.getAICharacterHandle())
                            
                            targetObj.getAIBehaviorsHandle().pursue(proj.getOwner(), 1.0)
                            
                            # TODO: override other movement that the gameObj may have...paths, idle anim, etc.
                            del self.inactiveEnemies[targetObj.getName()]
                
                
    
    def setDamageFxFlag(self, gameObj, flag):
        self.damageFxStatus[gameObj.getName()] = flag
    
    def setRedColorScale(self, redScale, gameObj, origColorVec):
        gameObj.setColorScale(redScale, origColorVec[1], origColorVec[2], origColorVec[3])
    
    def destroyProjectile(self, tuple):
        proj = tuple[0]
        proj.getAIBehaviorsHandle().removeAi('pursue')
        self.aiWorld.removeAiChar(proj.getName()) # CAUTION: is this the same name as the AICharacter name?
        self.projectiles.remove(tuple)
        proj.removeNode()
    
    def addNewObject(self, newObj):
        pass
        # TODO
    
    def destroyObject(self, targetObj):
        if not self.combatGraph.hasCombatant(targetObj):
            return
        
        # temp
        print '%s is defeated!' %(targetObj.getName())
        
        # TODO: death animation, remove from scene, game over for player, etc.
        # CONSIDER: remove from collision traversal
        # CONSIDER: removal...how best to do this completely?
        
        # stop any sequences related to this object
        if targetObj.getName() in self.sequences:
            for seq in self.sequences[targetObj.getName()]:
                seq.pause()
            del self.sequences[targetObj.getName()]
        
        # NEw
        if targetObj.getName() in self.opponentColHandlerQueues:
            del self.opponentColHandlerQueues[targetObj.getName()]
        
        targetObj.hide()
        self.combatGraph.removeCombatant(targetObj)
        targetObj.callTrigger(self.world, 'LE-trigger-onDeath')
        
        if targetObj.getName() in self.activeEnemies:
            del self.activeEnemies[targetObj.getName()]
        if targetObj.getName() in self.inactiveEnemies:
            del self.inactiveEnemies[targetObj.getName()]
        
        targetObjBehaviors = targetObj.getAIBehaviorsHandle()
        if targetObjBehaviors.behaviorStatus('pursue') != -1:
            targetObjBehaviors.removeAi('pursue')
#        if targetObjBehaviors.behaviorStatus('flock') != -1:
#            targetObjBehaviors.removeAi('flock')
        self.aiWorld.removeAiChar(targetObj.getName()) # CAUTION: is this the same name as the AICharacter name?
    
    def attemptResumeMovement(self, gameObj):
        if gameObj.getName() in self.obstacleRecoveryStatus:
            if not self.obstacleRecoveryStatus[gameObj.getName()]:
                self.world.enableMovement(gameObj)
    
    def setObstacleRecoveryFlag(self, gameObj, flag):
        if gameObj.getName() in self.obstacleRecoveryStatus:
            self.obstacleRecoveryStatus[gameObj.getName()] = flag
    
    def queueAttack(self, attackerObj, attackerSpell, targetObj):
        if attackerSpell.isCooldownReady():
            if self.combatGraph.checkCanAttack(attackerObj, targetObj):
                dist = findGameObjDistance(attackerObj, targetObj)
                if dist > attackerSpell.getAttackRange():
                    Debug.debug(__name__,'out of attack range...')
                else:
                    Debug.debug(__name__, 'attack!')
                    
                    proj = attackerSpell.makeProjectile()
                    seq = Sequence()
                   
                    charge = Sequence()
                    
                    isActor = proj.getOwner().getActorHandle() != None
                    
                    if isActor:
                        charge.append(Func(proj.getOwner().getActorHandle().stop))
                    charge.append(Func(self.world.disableMovement, proj.getOwner()))
                    
                    if isActor and attackerSpell.properties['chargeSequence']['firstAnimation'] != '':
                        charge.append(Func(proj.getOwner().getActorHandle().play, attackerSpell.properties['chargeSequence']['firstAnimation']))##
                    charge.append(Wait(attackerSpell.properties['chargeSequence']['firstAnimationTime']))##
                    if isActor and attackerSpell.properties['chargeSequence']['secondAnimation'] != '':
                        charge.append(Func(proj.getOwner().getActorHandle().play, attackerSpell.properties['chargeSequence']['secondAnimation']))##
                    charge.append(Wait(attackerSpell.properties['chargeSequence']['secondAnimationTime']))##
                    if isActor and attackerSpell.properties['chargeSequence']['idleAnimation'] != '':
                        charge.append(Func(proj.getOwner().getActorHandle().loop, attackerSpell.properties['chargeSequence']['idleAnimation']))##
                    
                    charge.append(Func(self.attemptResumeMovement, proj.getOwner()))

                    fire = Sequence()
                    fire.append(Func(proj.setPos, proj.getOwner().getPos(render)))
                    #fire.append(Func(proj.lookAt, targetObj))
                    #fire.append(Func(proj.setH, render, 270))
                    fire.append(Func(proj.setH, render, proj.getOwner().getH(render)))
                    fire.append(Func(proj.reparentTo, render))
                    fire.append(Func(self.projectiles.append, (proj, targetObj)))
                    fire.append(Func(self.aiWorld.addAiChar, proj.getAICharacterHandle()))
                    fire.append(Func(proj.getAIBehaviorsHandle().pursue, targetObj, 1.0))
                    fire.append(Wait(attackerSpell.getCooldownTime()))
                    
                    
                    seq.append(Func(attackerSpell.setCooldownReady, False))
                    seq.append(charge)
                    seq.append(fire)
                    seq.append(Func(attackerSpell.setCooldownReady, True))
                    seq.append(Func(self.setSequenceFinished, proj.getOwner().getName(), seq))
                    
                    self.sequences[proj.getOwner().getName()].append(seq)
                    seq.start()
                    
     
    def checkCanAttack(self, attackerObj, targetObj):
        return self.combatGraph.checkCanAttack(attackerObj, targetObj)
        

# TODO: make sure that the projectile isn't so fast that it passes up the target
# ex. compare distance to target with the last cycle of task, if it increased then stop
# ex. control this by making sure self.step is smaller than self.hitThreshold

# CONSIDER: do projectiles die off after a time, or do they keep going and homing until they hit?
                                

class Spell:
    
    def __init__(self, ownerGameObj, properties=ATTACK_MEDIUM):
        self.owner = ownerGameObj
        self.properties = properties
        self.cooldownReady = True
        # CONSIDER: limit on how many projectiles can be made at one time
    
        self.projIndex = 0
    
    def isCooldownReady(self):
        return self.cooldownReady
    
    def setCooldownReady(self, flag):
        self.cooldownReady = flag
    
    def getCooldownTime(self):
        return self.properties['cooldown']
    
    def getAttackRange(self):
        return self.properties['attackRange']
    
    def getOwner(self):
        return self.owner
    
    def generateOriginalProjName(self):
        index = self.projIndex
        self.projIndex += 1
        return '%s_%s_%d' %(self.owner.getName(), self.properties['name'], index)
    
    def makeProjectile(self, modifiersList=[]):
        proj = Projectile(self.generateOriginalProjName(), self, self.properties, modifiersList)
        proj.getAICharacterHandle().setMass(self.properties['mass'])
        
        return proj


class Projectile(GameObject):

    # CONSIDER: pass a stripped version of properties...model, anims, 
    # and modifiers...and a reference to spell class to refer to for damage etc.
    def __init__(self, name, parentSpell, properties, modifiersList=[]):
        actorNP = Actor(properties['modelPath'], properties['anims'])
        actorNP.setName(name)
        
        GameObject.__init__(self, actorNP)
        
        self.parentSpell = parentSpell
        self.properties = properties
    
    def getOwner(self):
        return self.parentSpell.getOwner()
    
    def getMoveStep(self):
        # TODO: include any modifiers
        return self.properties['step']
    
    def getHitThreshold(self):
        # TODO: include any modifiers
        return self.properties['hitThreshold']
    
    def getDamage(self):
        # TODO: include any modifiers
        return self.properties['damage']

