#This is the enemy manager, it it used to keep track of all enemies on the current stage.
#This is used to create and destroy enemies.                                  
import sys,random

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.task import Task
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
sys.path.append("./PandaCore") 
import ScriptInterface  


class EnemyManager(DirectObject):
    def __init__(self):
        self.enemyList = {}
        self.accept('createEnemy',self.createEnemy)
        self.accept('destroyEnemy',self.destroyEnemy)
        self.accept('destroyAllEnemies',self.destroyAll)
        
    def createEnemy(self,world,object,enemy,points = None,back=False):
        self.enemyList[object.getName()] = Enemy(world,object,enemy,points,back) #Creates enemies
        
    def destroyEnemy(self,name): #destroys an enemy
        for ii in self.enemyList:
            if ii == name:
                temp = self.enemyList[ii]
                self.enemyList.pop(ii)
                del temp
                

    def destroyAll(self): #destroys all enemies
        for ii in self.enemyList:
            temp = self.enemyList[ii]
            self.enemyList.pop(ii)
            del temp
            
    def notifyEnemy(self,name,hero):
        self.enemyList[name].notify(hero)
    def pauseAll(self):
        for k in self.enemyList:
            self.enemyList[k].pause();
    def resumeAll(self):
        for k in self.enemyList:
            self.enemyList[k].resume();
            
            
class Enemy(DirectObject):
    def __init__(self,world,gameObj,enemyTag,points = None,backing = False):
        self.worldObj = world
        self.DEBUG = False
        self.paused = False;
        # This function sets the current scan range rotation, as well as sets up the scanning box
        self.gameObj = gameObj #sets the local gameObj as the inherited one
        self.points = points #sets up the nodes for a point drone
        self.back = backing
        self.isBack = backing
        if "stationary" in enemyTag: 
            self.scanrange = 180 #sets up scan range
            self.scanrange2 = 0 #sets up scan range
            self.scanlimit = 360
            self.scan = "circle"
            self.scanIncr = 15.2 #sets up how fast the scanning is
            self.isAlerted = False
            self.canWalk = False
            self.isWalking = False
        else:
            self.scanrange = 0 #sets up scan range
            self.scanrange2 = 0 #sets up scan range
            self.scanlimit = 90

            self.scan = "left"
            self.scanIncr = 2 #sets up how fast the scanning is
            self.isAlerted = False
            self.canWalk = True
            self.isWalking = False
            self.walkPoint = Point2(0,0)
            self.walkingRange = 125
            self.moveTime = 2.0 #Will fluctuate depending on distance
            self.walkS = None
        self.collisionBound = CollisionNode(self.gameObj.getName()+"EnemyCollider")
        colTube = CollisionTube((0,0,20),(0,0,5),4)
        self.collisionBound.addSolid(colTube)
        self.collisionBound.setFromCollideMask(BitMask32.bit(2))
        self.collisionSphere = gameObj.attachNewNode(self.collisionBound)

        self.scanNode = PandaNode(gameObj.getName()+"-ScanNode") #sets up all collision features
        self.ScanNodePath = gameObj.attachNewNode(self.scanNode)
        
        
        self.collisionView = CollisionNode(gameObj.getName()+"-SCAN")
        self.collisionView.addSolid(CollisionBox(Point3(-.5,0,- 10),Point3(.5,50,20)))
        self.collisionView.setIntoCollideMask(BitMask32.bit(2))
        self.collisionNode = self.ScanNodePath.attachNewNode(self.collisionView)
        
        self.scanNode2 = PandaNode(gameObj.getName()+"-ScanNode") #sets up all collision features
        self.ScanNodePath2 = gameObj.attachNewNode(self.scanNode2)
        
        self.collisionView2 = CollisionNode(gameObj.getName()+"-SCAN")
        self.collisionView2.addSolid(CollisionBox(Point3(-.5,0,- 10),Point3(.5,50,20)))
        self.collisionView2.setIntoCollideMask(BitMask32.bit(2))
        self.collisionNode2 = self.ScanNodePath2.attachNewNode(self.collisionView2)
        self.movementType = "normal"
        if "point" in enemyTag:
            self.movementType = "point"
            self.moveTime = 1.0 #Will fluctuate depending on distance
            self.walkNode = 1
            self.gameObj.setPos(points['1'].getPos())
            if self.DEBUG:
                Line = LineSegs()
                Line.setColor(1,0,0,1)
                Line.setThickness(20)
                for ii in range(len(points)):
                    ii += 1
                    ii2 = ii + 1
                    if ii2 > len(points) and not self.back:
                        ii2 = 1
                    else:
                        ii2 -= 1
                    Line.moveTo(points[str(ii)].getPos())
                    Line.drawTo(points[str(ii2)].getPos())
                render.attachNewNode(Line.create())
        ## self.viewTest = CollisionNode(gameObj.getName()+"-View")
        ## self.viewTest.addSolid(CollisionBox(Point3(-1,0,- 10),Point3(1,50,20)))
        ## self.viewTest.setIntoCollideMask(BitMask32.bit(2))
        ## self.viewTestNode = self.ScanNodePath.attachNewNode(self.collisionView)
        #Might use for view testing later on...
        
        messenger.send("addCollision",[self.collisionNode,"Queue"])
        messenger.send("addCollision",[self.collisionNode2,"Queue"])
        messenger.send("addCollision",[self.collisionSphere,"Handle"])
        
        self.collisionNode.show()
        self.collisionSphere.show()
        self.collisionNode2.show()
        taskMgr.add(self.enemyUpdate,"enemyUpdate") #starts the enemy ai loop
        #taskMgr.add(self.updateHeight,"enemyHeight") #starts the enemy ai loop
        print "ENEMY CREATED"
        self.moveS = None
        self.lerphpr = None

        
         #Line collider for setting hero height based on ground geometry
        heroLine = CollisionNode('enemyLine '+self.gameObj.getName())
        heroLine.addSolid(CollisionRay(Point3(0,0,self.gameObj.getZ() + 0), Vec3(0,0,-1)))
        heroLine.setFromCollideMask(BitMask32.bit(0))
        heroLine.setIntoCollideMask(BitMask32.allOff())
        self.enemyGroundCollide = render.attachNewNode(heroLine)
        self.enemyGroundHandler = CollisionHandlerQueue()
        self.worldObj.cTrav.addCollider(self.enemyGroundCollide, self.enemyGroundHandler)

        self.goodZ = self.gameObj.getZ()

        if self.worldObj.currScene == "default_0":
            self.pause()
        
    def pause(self):
        self.paused = True;
        if not self.moveS == None:
            self.moveS.pause()
        if not self.lerphpr == None:
            self.lerphpr.pause()
        taskMgr.remove("enemyUpdate")
    def resume(self):
        print "Resume!"
        self.paused = False;
        if not self.moveS == None:
            self.moveS.resume()
        if not self.lerphpr == None:
            self.lerphpr.resume()
        taskMgr.add(self.enemyUpdate, "enemyUpdate")
        
    def enemyUpdate(self,task):
       # self.gameObj.setZ(self.goodZ)
        if self.paused:
            return task.cont
        if self.scan == "left":
            if self.scanrange < self.scanlimit:
                self.scanrange += self.scanIncr
                self.scanrange2 -= self.scanIncr
            else:
                self.scan = "right"
        elif self.scan == "right":
            if self.scanrange > -self.scanlimit:
                self.scanrange -= self.scanIncr
                self.scanrange2 += self.scanIncr
            else:
                self.scan = "left"
        elif self.scan == "circle":
            self.scanrange -= self.scanIncr
            self.scanrange2 -= self.scanIncr
        if self.movementType == "point":
            if not self.isWalking and self.canWalk:
                self.walkPointSetup()
        elif not self.isWalking and self.canWalk:
            self.randomWalk()
        self.ScanNodePath.setH(self.scanrange)
        self.ScanNodePath2.setH(self.scanrange2)
        return task.cont
    
    def notify(self,hero):
        if not self.isAlerted:
            ## taskMgr.doMethodLater(0,self.disableCollisions,"enemyDis"+self.gameObj.getName())
            print "ALERT! ALERT! DETECTED BY ",self.gameObj.getName()
            messenger.send("playSound3d",[self.gameObj,"alert_1",False])
            ##self.isAlerted = True
            messenger.send("playerDie")
    
    def resetScan(self):
        self.isAlerted = False
        messenger.send("addCollision",[self.collisionNode])
        self.scanrange = 0
    
    def randomWalk(self):
        x = self.gameObj.getX() + random.uniform(-self.walkingRange,self.walkingRange)
        y = self.gameObj.getY() + random.uniform(-self.walkingRange,self.walkingRange)
        self.walkPoint = Point2(x,y)
        self.isWalking = True
        self.walkToPoint()
        
    def walkPointSetup(self):
        x = self.points[str(self.walkNode)].getX()
        y = self.points[str(self.walkNode)].getY()
        z = self.points[str(self.walkNode)].getZ()
        self.walkPoint = Point3(x,y,z)
        self.isWalking = True
        ##print self.isBack,",",self.back
        if not self.isBack:
            self.walkNode += 1
            if self.walkNode > len(self.points):
                if self.back:
                    self.walkNode -= 1
                    self.isBack = True
                else:
                    self.walkNode = 1
        else:
            self.walkNode -= 1
            if self.walkNode < 1:
                self.walkNode = 1
                self.isBack = False
        self.walkToPoint(self.moveTime)
    
    def walkToPoint(self,timeO = 0):
        xTrue = False
        yTrue = False
        startPoint = self.gameObj.getPos()
        endPoint = self.walkPoint
        
        oldHpr = self.gameObj.getHpr()
        self.gameObj.lookAt(endPoint)
        newHpr = self.gameObj.getHpr()
        self.gameObj.setHpr(oldHpr)
        
        ## newHpr.setX(abs(newHpr.getX()))
        isGreat = False
        ## if oldHpr.getX() < 0:
        isGreat = oldHpr.getX() < 0
        ## if oldHpr.getX() > 0:
            ## isGreat = oldHpr.getX() > 0
        if newHpr.getX() < 0: 
            if not isGreat:
                ##print 'ABS1'
                oldHpr.setX(-360 + abs(oldHpr.getX()))
                if abs(oldHpr.getX()) - abs(newHpr.getX()) > 180:
                    oldHpr.setX(360 - abs(oldHpr.getX()) )
            ## else:
                ## print 'ABS2'
                ## oldHpr.setX( (oldHpr.getX() + 360))
                ## lerphpr = LerpHprInterval(self.gameObj, .5, oldHpr, newHpr)
        else:
            if isGreat:
                ##print 'ABS2'
                oldHpr.setX(360 - abs(oldHpr.getX()) )
                if abs(oldHpr.getX()) - abs(newHpr.getX()) > 180:
                    oldHpr.setX(-360 + abs(oldHpr.getX()))
        ##print oldHpr.getX(),",",isGreat,">>",newHpr.getX()
        self.lerphpr = LerpHprInterval(self.gameObj, .5, newHpr, oldHpr)
        self.lerphpr.start()
        if timeO == 0:
            time = self.moveTime
            for ii in range(abs((startPoint.getX() - endPoint.getX()))):
                for xx in range(abs((startPoint.getY() - endPoint.getY()))):
                    time += .001
            if time > 10.0:
                time = 10.0
        else:
            time = timeO
        Move1 = LerpPosInterval(self.gameObj,time,endPoint,startPoint)
        ##print "MOVING FROM ",startPoint," TO ",endPoint
        self.moveS = Sequence(Move1)
        self.moveS.start()
        taskMgr.doMethodLater(time + 0,self.finalWalk,"YEAH")
        
    def finalWalk(self,task):
        self.isWalking = False
        
    def disableCollisions(self,task=None):
        if not self.isAlerted:
            self.isAlerted = True
            self.collisionNode.removeNode()
            self.collisionNode2.removeNode()
            self.canWalk = False
            self.moveS.pause()
            taskMgr.doMethodLater(5,self.enableCollisions,"enableEnemyC"+self.gameObj.getName())
        
    def enableCollisions(self,task=None):
        taskMgr.remove('enemyDis'+self.gameObj.getName())
        taskMgr.remove('enableEnemyC'+self.gameObj.getName())
        self.collisionNode = self.ScanNodePath.attachNewNode(self.collisionView)
        self.collisionNode2 = self.ScanNodePath2.attachNewNode(self.collisionView2)
        messenger.send("addCollision",[self.collisionNode,"Queue"])
        messenger.send("addCollision",[self.collisionNode2,"Queue"])
        self.isAlerted = False
        self.moveS.resume()
        if not "circle" in self.scan:
            self.canWalk = True

    def updateHeight(self,task=None):
        groundEntries = []
        #move the collision line to the hero position
        self.enemyGroundCollide.setPos(self.gameObj.getPos(render))
        
        #loop through every collision entry for the line
        for e in self.enemyGroundHandler.getEntries():
            #print self.gameObj.getName(),"--",e
            if e.getIntoNodePath().hasNetTag('OBJRoot'):
                #find the actual root of the object
                np = e.getIntoNodePath().findNetTag('OBJRoot')
                #only react to objects that are tagged as the ground
                if np.hasTag('LE-ground'):
                    groundEntries.append(e)
                    
        if len(groundEntries) > 0:
            #sort the collision entries based on height
            groundEntries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),x.getSurfacePoint(render).getZ()))
            #set hero height and pivot height
            ##print groundEntries[0].getSurfacePoint(render).getZ(), self.gameObj.getZ()
            self.gameObj.setZ(groundEntries[0].getSurfacePoint(render).getZ() + 20)
            self.goodZ = groundEntries[0].getSurfacePoint(render).getZ() + 20
            # TODO: unlink these from being in the same task in case we want pivot to not be linked to hero (ex. cutscene)
        self.enemyGroundHandler.clearEntries()
        return task.cont