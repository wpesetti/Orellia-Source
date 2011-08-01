# Code Template for exporting a world from the Level Editor.
# Used as a basis by StandaloneExporter, which fills in some of the values to reflect the local computer and project name.

#== Python and Panda imports ==
GAMEPLAY_FOLDER = None
IN_DEVELOP = False

import sys, math, os
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *
from panda3d.ai import *
from direct.filter.CommonFilters import CommonFilters

#== Storyteller tool imports and files ==

#[Zeina]Since our code is not in Panda 1.7 folder, to be able to import our classes for gameplay,
# I am adding the absolute path to the os. 
def module_exists(module_name):
    if(os.path.exists('GameObject.py')):
        return True
    else:
        return False

#if(module_exists('GameObject')==False):
#    print "The module doesn't exist"
#    sys.path.append(GAMEPLAY_FOLDER)
try:
    from direct.ETCleveleditor import LevelLoader , GameObjecy, GameplayUI, JournalEntry, \
                                      JournalMgr, ConversationMgr, ScriptMgr, ScriptInterface,\
                                      CombatMgr, InventoryMgr, SpellConstants 
except:
   print "Appended path"
   sys.path.append(GAMEPLAY_FOLDER) 
   from LevelLoader import *
   from GameObject import *
   from GameplayUI import *
   from JournalEntry import *
   from JournalMgr import *
   from ConversationMgr import *
   from ScriptMgr import *
   from ScriptInterface import * 
   from CombatMgr import *
   from InventoryMgr import *
   from SpellConstants import *
 
SCENE_FILE = None
LIBRARY_INDEX = None
JOURNAL_FILE = None
SCRIPTS_FILE = None
INVENTORY_FILE = None


#== Values for Camera and Main Character Movement (feel free to change) =====#

MAIN_CHAR_MAX_STEP = 3.0
MAIN_CHAR_MOVE_SPEED = 100.0 # [Zeina]:This speed is with the time-step solution for movement. /CONSIDER: calculate dynamically based on model size | default = 3.0
MAIN_CHAR_ROTATE_SPEED = 3.2 # default = 3.2
MAIN_CHAR_GROUND_OFFSET = 0.0 # This is the distance (offset) above the ground plane to place the main character | default = 0.0
CAMERA_HEIGHT = 1.4 # Relative height of the camera above the main character model (positive = above) | default = 1.0
CAMERA_TRAIL = 2.7 # Relative distance camera trails behind the main character model (positive = behind) | default = 4.0
CAMERA_PITCH = -12 # Default is 10
CAMERA_TURN_THRESHOLD = 20 # The greatest angle (degrees) the main character can face before camera turns to follow his direction | default = 20 
CAMERA_TURN_SPEED = 3.0 # The speed the camera turns to align with the character once the threshold is passed | default = 3.0
CLICK_RANGE = 100.0
#== Flags for game status (feel free to change) =============================#

FLAG_SHOW_FRAMES_PER_SECOND = True
FLAG_SHOW_GLOW = True
FLAG_USE_AUTOSHADER = True
FLAG_SHOW_COLLISIONS = False

#== Bitmasks for handling collisions ==

BITMASK_GROUND = BitMask32.bit(0)
BITMASK_CLICK = BitMask32.bit(1)
BITMASK_HERO_COLLIDE = BitMask32.bit(2)
BITMASK_WALL = BitMask32.bit(3)
BITMASK_CAMERA = BitMask32.bit(4)
BITMASK_WALL_TERRAIN = BitMask32.bit(3)|BitMask32.bit(5)
BITMASK_TERRAIN = BitMask32.bit(5)

#== Background Color Presets == 

BGC_LIGHT_BLUE = Vec4(166.0/255.0,207.0/255.0,240.0/255.0,1)
BGC_LIGHT_GREEN = Vec4(196.0/255.0,253.0/255.0,185.0/255.0,1)
BGC_BLACK = Vec4(0,0,0,1)
BGC_DARK_GREY = Vec4(45.0/255,45.0/255.0, 45.0/255.0,1)

#== Spells for player, given as a list of dictionaries (properties) in order of buttons on UI ==

PLAYER_SPELLS = [SPELL_NEEDLES, SPELL_SPOREBLAST, SPELL_GUASSBOOM]

#for debugging
DEBUG = False


def debug(text):
    if(DEBUG):
        print "DEBUG @",globalClock.getFrameTime()," in ",__name__, ": ", text
        

class World(ShowBase): # CONDISER: change to DirectObject/FSM
 
    def __init__(self):
        ShowBase.__init__(self)
        
        self.createLoadScreen('./LEGameAssets/Textures/title_screen.png')
        base.graphicsEngine.renderFrame()
        
    #== Environment and Rendering Settings ==
        base.setFrameRateMeter(FLAG_SHOW_FRAMES_PER_SECOND)
        if FLAG_USE_AUTOSHADER:
            render.setShaderAuto()
        self.filters = CommonFilters(base.win, self.cam) # NEW
        if FLAG_SHOW_GLOW:
            bloomSize = 4#'small'
            filterok = self.filters.setBloom(blend=(0,0,0,1), desat=-0.5, intensity=3.0, size=bloomSize)
            if (filterok == False):
                print 'WARNING:Video card not powerful enough to do image postprocessing'
            
        #tex = loader.loadTexture("./LEGameAssets/Textures/loadbar_tray.png")
        self.loadBar = DirectWaitBar(text = "", value = 0, scale =(.35,.5,.5), pos = (0.006,.83,.83))
        #self.loadBar['barRelief'] = DirectWaitBar.GROOVE
        #self.loadBar['scale'] = 0.05
        #self.loadBar['barTexture'] = tex
        self.loadBar['barColor'] = (6.0/255.0, 11.0/255, 28.0/255.0, 1)
        self.loadBar.reparentTo(render2d)
        self.loadBar.hide()
        base.graphicsEngine.renderFrame()
        
        self.setBackgroundColor(166.0/255.0,207.0/255.0,240.0/255.0,1)
        self.skybox = self.loader.loadModel("LEGameAssets/Models/skybox_final.egg")
        self.skybox.setScale(50)
        self.skybox.reparentTo(render)
        
    #== Load the level and the managers ==
        self.assets, self.objects, self.gameObjects, self.sounds, self.sequences= loadWorld(SCENE_FILE, LIBRARY_INDEX)
        self.loadBar['value'] += 5
        base.graphicsEngine.renderFrame() 
        
        
        self.conversations = loadConversations(SCENE_FILE, LIBRARY_INDEX)
        self.scenes = {}
        self.loadScenes()
        self.loadBar['value'] += 5
        base.graphicsEngine.renderFrame()
        
        self.journalMgr = JournalMgr(self)
        self.loadJournal(self.journalMgr,JOURNAL_FILE)
        
        self.conversationMgr = ConversationMgr(self, self.conversations)
        
        self.scriptMgr = ScriptMgr(self)
        self.scriptMgr.loadScripts(SCRIPTS_LIST)
        self.scriptInterface = ScriptInterface(self)
        
        self.inventoryMgr = InventoryMgr(self)
        loadInventory(self.inventoryMgr,INVENTORY_FILE)
        
        self.loadBar['value'] += 5
        base.graphicsEngine.renderFrame()
        
        self.ranSequences = []
        
    #== Main Character ==
        self.hero = None
        for name, gameObj in self.gameObjects.iteritems():
            if gameObj.getNP().hasTag('LE-mainChar'):
                self.hero = gameObj
                break
        else:
            # make a default hero
            defaultHeroNP = loader.loadModel("panda")
            self.hero = GameObject(defaultHeroNP)
            self.hero.reparentTo(render)
            self.hero.setPos(0, 0, 0)
            self.hero.setTag('LE-mainChar', '180')
            self.gameObjects[self.hero.getName()] = self.hero
        
        self.setCollideMasks(self.gameObjects)
             
        # remove the hero from the objects dict so it cannot be clicked by player
        if self.hero.getName() in self.objects:
            del self.objects[self.hero.getName()]
        
    #== Camera ==
        camHeightFactor = CAMERA_HEIGHT
        camTrailFactor = -CAMERA_TRAIL # careful of +/- distinction
        self.heroHeight = self.getModelHeight(self.hero)
        self.heroHeadingOffset = float(self.hero.getTag('LE-mainChar'))
        self.lastHeroH = self.hero.getH(render) + self.heroHeadingOffset
        
        # setup the camera pivot, which will follow the main character model and anchor the camera
        self.camPivot = NodePath('camPivot')
        self.camPivot.reparentTo(render)
        
        self.camHeight = camHeightFactor*self.heroHeight
        self.camTrail = camTrailFactor*self.heroHeight
        self.cam.setPos(self.camPivot.getPos() + (0, self.camTrail, self.camHeight))
        self.cam.wrtReparentTo(self.camPivot)
        
        self.placeCamera(self.hero) # match X and Y to main character
        self.alignCamera(self.hero) # match heading to main character
        #self.camPivot.setH(render, self.hero.getH(render) + self.heroHeadingOffset)
        
        self.gameCam = self.cam
        
    #== Collisions ==
        self.setupCollisions()
        
    #== Controls ==
        self.disableMouse()
        self.keyMap = { 'w':False, 'a':False, 's':False, 'd':False }
        self.enableMovement(self.hero)
        self.accept("mouse1", self.onClickin3D)
        self.accept('escape', sys.exit)
        
        self.accept('z', render.place) 
    
    #== UI and Combat ==
        self.gameplayUI = GameplayUI(self)
        self.gameplayUI.hideAll()
        
        # for health bars and on screen UI
        self.overlayAmbientLight = AmbientLight('overlayAmbientLight')
        self.overlayAmbientLight.setColor(VBase4(1.0, 1.0, 1.0, 1.0))
        self.overlayAmbientLightNP = render.attachNewNode(self.overlayAmbientLight)
        
        # initialize the combat manager (which includes AI) now that a main character and gameplayUI instance and overlay light is established
        self.combatMgr = CombatMgr(self)

        # initialize player's spells
        self.heroSpells = []
        for properties in PLAYER_SPELLS:
            spell = Spell(self.hero, properties)
            self.heroSpells.append(spell)
    
    #== Start Tasks
        taskMgr.add(self.moveHeroTask, 'moveHeroTask', appendTask=True)
        taskMgr.add(self.cameraFollowTask, 'cameraFollowTask', appendTask=True)
        taskMgr.add(self.processHeroCollisions, 'processHeroCollisions')
        taskMgr.add(self.updateHeroHeight, 'updateHeroHeight')
        self.combatMgr.startTasks()
        
        self.accept('enter', self.destroyLoadScreen)
        self.destroyLoadScreen()
        
    

##== Utility and World Initialization functions =============================##
    
    def loadJournal(self,journalMgr,journalFile):
        f = open(Filename(journalFile).toOsSpecific())
        doc = xml.dom.minidom.parse(f)
        root = doc.childNodes[0]
        
        for n in root.childNodes:
            if n.localName == "journalEntries":
                journalMgr.decode(n)
        f.close()
    
    def getModelHeight(self, model):
        min, max = Point3(), Point3()
        model.calcTightBounds(min, max) 
        return max.getZ() - min.getZ()
    
    def createLoadScreen(self, imageFile='./LEGameAssets/Textures/load_screen.png'):
        self.loadScreen = OnscreenImage(image=imageFile)
        aspect2d.hide()
        self.loadScreen.reparentTo(render2d)
        if(hasattr(self, "gameplayUI")):
            self.gameplayUI.hideAll()

    def destroyLoadScreen(self):
        self.loadBar.hide()
        self.loadScreen.detachNode()
        self.loadScreen.destroy()
        aspect2d.show()
        self.ignore('enter')
        self.gameplayUI.showAll()
        for name, gameObj in self.gameObjects.iteritems():
            gameObj.callTrigger(self, 'LE-trigger-onScene')
    
    def startLoadBar(self, range=100):
        self.loadBar.show()
        self.loadBar['range'] = range
        self.loadBar['value'] = 0
        base.graphicsEngine.renderFrame()
        
    def increaseLoadBar(self, value):
        self.loadBar['value'] += value
        base.graphicsEngine.renderFrame()

##== Collisions =============================================================##
    
    def setupCollisions(self):
        self.cTrav = CollisionTraverser('mainTraverser')
        self.cTrav.setRespectPrevTransform(True)
        
        # Line collider for setting hero height based on ground geometry
        heroLine = CollisionNode('heroLine')
        heroLine.addSolid(CollisionRay(Point3(0,0,self.heroHeight), Vec3(0,0,-1)))
        heroLine.setFromCollideMask(BITMASK_GROUND)
        heroLine.setIntoCollideMask(BitMask32.allOff())
        self.heroGroundCollide = render.attachNewNode(heroLine)
        self.heroGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroGroundCollide, self.heroGroundHandler)
        
        
#        cameraSphere = CollisionNode('cameraSphere')
#        cameraSphere.addSolid(CollisionSphere(0,0,0,10))
#        cameraSphere.setFromCollideMask(BITMASK_CAMERA)
#        cameraSphere.setIntoCollideMask(BitMask32.allOff())
#        self.cameraSphereCollide = self.cam.attachNewNode(cameraSphere)
#        self.cameraSphereQueue = CollisionHandlerQueue()
#        self.cTrav.addCollider(self.cameraSphereCollide, self.cameraSphereQueue)
        
        
        self.herowallcollision = False
        
        self.heroWallCollideX = render.attachNewNode("heroWallX")
        self.heroWallCollideY = render.attachNewNode("heroWallY")
        self.heroWallCollideZ = render.attachNewNode("heroWallZ")
        
        # Line collider for running into obstacles and walls in X direction
        heroLineX = CollisionNode('heroLineX')
        heroLineX.addSolid(CollisionRay(Point3(0,0,0), Vec3(0,0,1)))
        self.heroWallCollideLineX = self.heroWallCollideX.attachNewNode(heroLineX)      
        self.heroWallCollideLineX.node().setFromCollideMask(BITMASK_WALL_TERRAIN)
        self.heroWallCollideLineX.node().setIntoCollideMask(BitMask32.allOff())
        self.heroWallQueueX = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroWallCollideLineX, self.heroWallQueueX)
        
        # Line collider for running into obstacles and walls in Y direction
        heroLineY = CollisionNode('heroLineY')
        heroLineY.addSolid(CollisionRay(Point3(0,0,0), Vec3(0,0,1)))
        self.heroWallCollideLineY = self.heroWallCollideY.attachNewNode(heroLineY)      
        self.heroWallCollideLineY.node().setFromCollideMask(BITMASK_WALL_TERRAIN)
        self.heroWallCollideLineY.node().setIntoCollideMask(BitMask32.allOff())
        self.heroWallQueueY = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroWallCollideLineY, self.heroWallQueueY)
        
        # Line collider for running into obstacles and walls in Z direction
        heroLineZ = CollisionNode('heroLineZ')
        heroLineZ.addSolid(CollisionRay(Point3(0,0,0), Vec3(0,0,1)))
        self.heroWallCollideLineZ = self.heroWallCollideZ.attachNewNode(heroLineZ)      
        self.heroWallCollideLineZ.node().setFromCollideMask(BITMASK_WALL_TERRAIN)
        self.heroWallCollideLineZ.node().setIntoCollideMask(BitMask32.allOff())
        self.heroWallQueueZ = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroWallCollideLineZ, self.heroWallQueueZ)
        
#        # Sphere collider for running into obstacles and walls
#        heroSphere = CollisionNode('heroSphere')
#        heroSphere.addSolid(CollisionSphere(0,0,0,7))
#        self.heroWallCollide = render.attachNewNode(heroSphere)        
#        self.heroWallCollide.node().setFromCollideMask(BITMASK_WALL)
#        self.heroWallCollide.node().setIntoCollideMask(BitMask32.allOff())
#        self.heroWallQueue = CollisionHandlerQueue()
#        self.cTrav.addCollider(self.heroWallCollide, self.heroWallQueue)
#        self.herowallcollision = False
        
        # Sphere collider for running into obstacles and walls in X direction
        heroSphereX = CollisionNode('heroSphereX')
        heroSphereX.addSolid(CollisionSphere(0,0,0,7))
        self.heroWallCollideSphereX = self.heroWallCollideX.attachNewNode(heroSphereX)      
        self.heroWallCollideSphereX.node().setFromCollideMask(BITMASK_WALL)
        self.heroWallCollideSphereX.node().setIntoCollideMask(BitMask32.allOff())
        #self.heroWallQueueX = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroWallCollideSphereX, self.heroWallQueueX)
        self.herowallcollision = False
        
        # Sphere collider for running into obstacles and walls in Y direction
        heroSphereY = CollisionNode('heroSphereY')
        heroSphereY.addSolid(CollisionSphere(0,0,0,7))
        self.heroWallCollideSphereY = self.heroWallCollideY.attachNewNode(heroSphereY)      
        self.heroWallCollideSphereY.node().setFromCollideMask(BITMASK_WALL)
        self.heroWallCollideSphereY.node().setIntoCollideMask(BitMask32.allOff())
        #self.heroWallQueueY = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroWallCollideSphereY, self.heroWallQueueY)
        
        # Sphere collider for running into obstacles and walls in Z direction
        heroSphereZ = CollisionNode('heroSphereZ')
        heroSphereZ.addSolid(CollisionSphere(0,0,0,7))
        self.heroWallCollideSphereZ = self.heroWallCollideZ.attachNewNode(heroSphereZ)      
        self.heroWallCollideSphereZ.node().setFromCollideMask(BITMASK_WALL)
        self.heroWallCollideSphereZ.node().setIntoCollideMask(BitMask32.allOff())
        #self.heroWallQueueZ = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroWallCollideSphereZ, self.heroWallQueueZ)
        
        
        
        
        
        
        
        # Ray collider for clicking on objects in the game
        self.pickerCollisionQueue = CollisionHandlerQueue()
        self.pickerCN = CollisionNode('pickerRayCN')
        self.pickerCNP = self.cam.attachNewNode(self.pickerCN)
        self.pickerCN.setFromCollideMask(BITMASK_CLICK)
        self.pickerCN.setIntoCollideMask(BitMask32.allOff())
        self.pickerRay = CollisionRay()
        self.pickerCN.addSolid(self.pickerRay)
        self.cTrav.addCollider(self.pickerCNP, self.pickerCollisionQueue)
    
        # Sphere collider for triggering scripts
        self.heroCN = CollisionNode('heroCN')
        self.heroCN.addSolid(CollisionSphere(0, 0, 0, 5)) # TODO: find good radius
        self.heroCNP = self.hero.attachNewNode(self.heroCN)
        self.heroCN.setFromCollideMask(BITMASK_HERO_COLLIDE)
        self.heroCN.setIntoCollideMask(BitMask32.allOff())
        self.heroCollisionQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.heroCNP, self.heroCollisionQueue)
        
        # Line collider for transparency
        self.cameraEntriesPre = []
        radius = self.getModelHeight(self.hero)*CAMERA_TRAIL/2
        self.cameraCollisionQueue = CollisionHandlerQueue()
        self.cameraHero = CollisionNode('cameraHero')
        self.cameraHeroLine = CollisionSegment(self.hero.getPos(render), self.cam.getPos(render))
        self.cameraHero.addSolid(self.cameraHeroLine)
        self.cameraHero.setFromCollideMask(BITMASK_CAMERA)
        self.cameraHero.setIntoCollideMask(BitMask32.allOff())
        self.cameraHeroP = self.render.attachNewNode(self.cameraHero)
        self.cTrav.addCollider(self.cameraHeroP, self.cameraCollisionQueue)
        #self.cameraHeroP.show()
        
        if FLAG_SHOW_COLLISIONS:
            self.cTrav.showCollisions(render)
            # TODO: show specific collision nodepaths
    
    def setCollideMasks(self, gameObjDict):
        for name, obj in gameObjDict.iteritems():
            bitmask = obj.getCollideMask()
            if obj.hasTag('LE-ground'):
                bitmask |= BITMASK_GROUND
                #obj.getNP().setCollideMask(bitmask) # TODO: remove
            if obj.hasTag('LE-attackable'):
                bitmask |= BITMASK_CLICK
            if obj.hasTag('LE-wall'):
                if(isinstance(obj.getNP(), GeoMipTerrain)):
                    bitmask |= BITMASK_TERRAIN
                else:
                    bitmask |= BITMASK_WALL
            if obj.scripts.has_key('LE-trigger-onClick'):
                bitmask |=BITMASK_CLICK
            if obj.scripts.has_key('LE-trigger-onCollision'):
                bitmask |=BITMASK_HERO_COLLIDE
            if obj.hasTag('OBJRoot'):
                if obj.hasTag('LE-ground') or obj.hasTag('LE-mainChar'):
                    pass
                else:
                    bitmask |= BITMASK_CAMERA
                
            obj.setCollideMask(bitmask)
      
    def onClickin3D(self):
        pickedObj = None
        if self.conversationMgr.isConversationOpen():
            return
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
        else:
            return
            
        self.cTrav.addCollider(self.pickerCNP, self.pickerCollisionQueue)
        
        self.pickerRay.setFromLens(self.cam.node(), mpos.getX(), mpos.getY())
        
        self.cTrav.traverse(render)
        if(self.pickerCollisionQueue.getNumEntries() > 0):
            self.pickerCollisionQueue.sortEntries()
        for i in range(self.pickerCollisionQueue.getNumEntries()):
            parent = self.pickerCollisionQueue.getEntry(i).getIntoNodePath().getParent()
            while not self.objects.has_key(parent.getName()):
                if(parent.getName() == "render"):
                    return
                parent = parent.getParent()
            pickedObj = parent
            
            if(pickedObj == None):
                continue
            else:
                break
            
            #if pickedObj.hasTag("LE-trigger-onClick"): # TODO: needed, or is having key in self.objects enough?
        if (pickedObj == None):
            return
        
        self.pickerCollisionQueue.clearEntries()
        
        self.cTrav.removeCollider(self.pickerCNP)
        
        gameObj = self.gameObjects[pickedObj.getName()]
        distToTarget = self.hero.getDistance(gameObj)
        
        if self.combatMgr.checkCanAttack(self.hero, gameObj):
            if distToTarget <= self.heroSpells[self.curSpellIndex].getAttackRange():
                self.combatMgr.queueAttack(self.hero, self.heroSpells[self.curSpellIndex], gameObj)
            else:
                textObject = OnscreenText(text = 'The target is out of range!',fg =(1,0,0,1), pos = (0, 0), scale = 0.09, align = TextNode.ACenter )
                def destroyWarning1():
                    textObject.destroy()
                sequence =Sequence(Wait(2), Func(destroyWarning1))
                sequence.start()
                return
        elif(distToTarget > CLICK_RANGE):
            textObject = OnscreenText(text = 'The target is out of range!',fg =(1,0,0,1), pos = (0, 0), scale = 0.09, align = TextNode.ACenter )
            def destroyWarning2():
                textObject.destroy()
            sequence =Sequence(Wait(2), Func(destroyWarning2))
            sequence.start()
            return
        gameObj.callTrigger(self, 'LE-trigger-onClick')
        
        
            

    
    # Task for processing hero's collisions with GameObjects, triggering OnCollision scripts
    def processHeroCollisions(self, task):
        #self.cTrav.traverse(render)
        debug("processHeroCollisions")
        # CONSIDER: may not be necessary to sort
        if(self.heroCollisionQueue.getNumEntries() > 0):
            self.heroCollisionQueue.sortEntries()
        debug("queue size: "+str(self.heroCollisionQueue.getNumEntries()))
        for i in range(self.heroCollisionQueue.getNumEntries()):
            # CONSIDER: if entry.hasInto(): for efficiency
             
            debug("i: "+str(i))   
            # TODO: check if GameObject is passable, and react accordingly (store old position, revert to it)
            if(self.heroCollisionQueue.getNumEntries() <= 0):
                return
            entry = self.heroCollisionQueue.getEntry(i)
            debug("entry: "+str(entry))
            if(entry):
                intoNP = entry.getIntoNodePath()
            else:
                continue
            if (intoNP != None) or (not intoNP.isEmpty()):
                while not self.objects.has_key(intoNP.getName()):
                    if(intoNP.getName() == "render"):
                        return task.cont
                    intoNP = intoNP.getParent()
                pickedObj = intoNP
                
                if pickedObj == None:
                    continue
                gameObj = self.gameObjects[pickedObj.getName()]
                gameObj.callTrigger(self, 'LE-trigger-onCollision')
                
        return task.cont

##== Camera Movement ========================================================##

    # places the camera pivot to match the position of the node path parameter
    # used to have the camera pivot match the main character's position as he moves
    def placeCamera(self, np):
        self.camPivot.setX(render, np.getX(render))
        self.camPivot.setY(render, np.getY(render))
    
    def alignCamera(self, np):
        self.camPivot.setH(render, self.hero.getH(render) + self.heroHeadingOffset)
        self.cam.setP(CAMERA_PITCH)
    
    def cameraFollowTask(self, task):
        heroH = self.hero.getH(render) + self.heroHeadingOffset
        camPivotH = self.camPivot.getH(render)
        
        # normalizes the headings to avoid jumps in the difference
        # which could come from passing 360 and going back to 0, for example
        # TODO: stress test, esp. with different values of self.heroHeadingOffset
        while heroH + 180 < camPivotH:
            heroH += 360
        while camPivotH + 180 < heroH:
            camPivotH += 360
              
        self.lastHeroH = heroH
        rotateLeft = (heroH >= camPivotH)
        rotateRight = not rotateLeft
        diff = math.fabs(heroH - camPivotH)

        if diff > CAMERA_TURN_THRESHOLD:
            if rotateLeft:
                self.camPivot.setH(self.camPivot.getH() + CAMERA_TURN_SPEED)
            elif rotateRight:
                self.camPivot.setH(self.camPivot.getH() - CAMERA_TURN_SPEED)
        
#        if(len(self.cameraEntriesPre)>0):
#            #print self.cameraEntriesPre
#            if(self.hero.getDistance(self.cam) > 5):
#                moveAmount = min(globalClock.getDt()*200,5.0)
#                pos = self.cam.getQuat().getForward()*moveAmount
#                newpos = self.cam.getPos() + pos
#                self.oldCameraEntriesPre = []
#                for e in self.cameraEntriesPre:
#                    self.oldCameraEntriesPre.append(e)
#                self.cam.setFluidPos(newpos)
#            
#        else:
#            if(self.hero.getDistance(self.cam) < 100):
#                moveAmount = min(globalClock.getDt()*200,5.0)
#                pos = self.cam.getQuat().getForward()*(-moveAmount)
#                oldpos = self.cam.getPos()
#                newpos = self.cam.getPos() + pos
#                self.cam.setFluidPos(newpos)
#                for e in self.oldCameraEntriesPre:
#                    #print e.getIntoNodePath()
#                    self.cTrav.traverse(e.getIntoNodePath())
#                #self.cTrav.traverse(render)
#                    if(len(self.cameraSphereQueue.getEntries())>0):
#                        self.cam.setFluidPos(oldpos)
            
        
        return task.cont
    

    def runCamera(self, cameraName, sequence, isLoop = False):
        debug("Running the camera")
        #debug(str(self.sequences))

        self.oldCamera = self.cam
        self.dr = self.win.makeDisplayRegion()
        
        dr2 = self.cam.node().getDisplayRegion(0)#
        self.objects[cameraName].node().setLens(base.camLens)
        parent = self.cam.getParent()
        self.cam.detachNode()

        self.dr.setCamera(self.objects[cameraName])
        
        def temp():

            dr2.setCamera(self.oldCamera)
            self.oldCamera.reparentTo(parent)
            self.dr.setActive(False)
            del self.dr
            self.dr = None
            self.accept("mouse1", self.onClickin3D) 
            debug("Ran")
            
        if(isLoop):
            newSequence = Sequence(sequence)
            self.addSequence(newSequence)
            def stopCameraFromLoop():
                newSequence.finish()
                temp()
            self.accept("mouse1", stopCameraFromLoop)
            self.addSequence(newSequence)
            newSequence.loop()
        else:
            newSequence = Sequence(sequence,Func(temp))
            def stopCamera():
                newSequence.finish()
            self.accept("mouse1", stopCamera)
            self.addSequence(newSequence)
            newSequence.start()
        
 
 
##== Character Movement =====================================================##

    def moveHeroTo(self, destinationObj):
        pos = destinationObj.getPos(render)
        hpr = destinationObj.getHpr(render)
        self.hero.setPosHpr(render, pos, hpr)
        self.placeCamera(self.hero)
        self.alignCamera(self.hero)

    def updateHeroHeight(self, task=None):
        groundEntries = []
        #move the collision line to the hero position
        self.heroGroundCollide.setPos(self.hero.getPos(render))
        
        #loop through every collision entry for the line
        for e in self.heroGroundHandler.getEntries():
            if e.getIntoNodePath().hasNetTag('OBJRoot'):
                #find the actual root of the object
                np = e.getIntoNodePath().findNetTag('OBJRoot')
                #only react to objects that are tagged as the ground
                if np.hasTag('LE-ground'):
                    groundEntries.append(e)
                    
        if groundEntries:
            #sort the collision entries based on height
            groundEntries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),\
x.getSurfacePoint(render).getZ()))

            #set hero height and pivot height
            self.hero.setZ(groundEntries[0].getSurfacePoint(render).getZ() + MAIN_CHAR_GROUND_OFFSET)
            self.camPivot.setZ(groundEntries[0].getSurfacePoint(render).getZ() + MAIN_CHAR_GROUND_OFFSET)
            # TODO: unlink these from being in the same task in case we want pivot to not be linked to hero (ex. cutscene)
        
        self.heroGroundHandler.clearEntries()
        return task.cont
    
    def updateHeroPos(self, queue, stepSize):
        wallEntries = []
        for w in queue.getEntries():
            np = w.getIntoNodePath().findNetTag('OBJRoot')
            if np.hasTag('LE-wall'):
                if self.isInObstacleRange(self.hero, w, stepSize):
                    wallEntries.append(w)
        if len(wallEntries) > 0:
            self.herowallcollision = True
            #self.collisionsurfaceP = wallEntries[0].getSurfacePoint(render)
        else:
            self.herowallcollision = False
            
    def updateCameraCollision(self):
        self.cameraHeroLine.setPointA(self.cam.getPos(render))
        self.cameraHeroLine.setPointB(self.hero.getPos(render))

        if(self.cameraEntriesPre):
            for i in self.cameraEntriesPre:
                i.getIntoNodePath().setTransparency(TransparencyAttrib.MAlpha)
                i.getIntoNodePath().setAlphaScale(1.0)
            del self.cameraEntriesPre[:]
            
        for i in self.cameraCollisionQueue.getEntries():
            i.getIntoNodePath().setAlphaScale(0.5)
            self.cameraEntriesPre.append(i)
        
        
            
        

    def moveHero(self,direction, dt):
        temp = render.attachNewNode("Dummy")#NodePath()
        moveStep = MAIN_CHAR_MOVE_SPEED*dt
        if moveStep > MAIN_CHAR_MAX_STEP:
            moveStep = MAIN_CHAR_MAX_STEP
        temp.setPos(self.camPivot, 0,direction*moveStep, 0)
        
        #oldPos = self.heroWallCollideX.getPos()
        self.heroWallCollideX.setX(temp.getX())
        self.heroWallCollideY.setY(temp.getY())
        self.heroWallCollideZ.setZ(temp.getZ())#+10)
        self.cTrav.traverse(render)
        
        #check on X direction
        self.updateHeroPos(self.heroWallQueueX, moveStep)
        self.moveHeroToWallCollide(Point3(temp.getX(),self.hero.getY(),self.hero.getZ()))
        
        #check on Y direction
        self.updateHeroPos(self.heroWallQueueY, moveStep)
        self.moveHeroToWallCollide(Point3(self.hero.getX(),temp.getY(),self.hero.getZ()))
        
        #check on Z direction
        self.updateHeroPos(self.heroWallQueueZ, moveStep)
        self.moveHeroToWallCollide(Point3(self.hero.getX(),self.hero.getY(),temp.getZ()))
        
        
        self.heroWallCollideX.setPos(self.hero.getPos())
        self.heroWallCollideY.setPos(self.hero.getPos())
        self.heroWallCollideZ.setPos(self.hero.getPos())
        
        self.placeCamera(self.hero)
        self.updateCameraCollision()
        temp.detachNode()
        
    def moveHeroToWallCollide(self,pos):
        if self.herowallcollision==False:
            self.hero.setPos(pos)#self.camPivot, 0, MAIN_CHAR_MOVE_SPEED, 0)
    
    def isInObstacleRange(self, mover, colEntry, stepSize):
        colPoint = colEntry.getSurfacePoint(render)
        if colPoint[2] >= mover.getZ(render):
            dist = findDistance3D(mover.getX(), mover.getY(), mover.getZ(), colPoint[0], colPoint[1], colPoint[2])
            obstacleThreshold = self.heroHeight*self.heroHeight + stepSize*stepSize
            if dist*dist <= obstacleThreshold:
                return True
        return False

    
    def turnHeroLeft(self):
        up = render.getRelativeVector(base.cam, Vec3(0, 0, 1))
        up.normalize()
        
        curHeroQuat = self.hero.getQuat()
        newHeroQuat = Quat()
        newHeroQuat.setFromAxisAngle(MAIN_CHAR_ROTATE_SPEED, up)
        self.hero.setQuat(curHeroQuat*newHeroQuat)
        self.hero.setR(0)
        self.hero.setP(0)
        self.updateCameraCollision()
        
    def turnHeroRight(self):
        up = render.getRelativeVector(base.cam, Vec3(0, 0, 1))
        up.normalize()
        
        curHeroQuat = self.hero.getQuat()
        newHeroQuat = Quat()
        newHeroQuat.setFromAxisAngle(-MAIN_CHAR_ROTATE_SPEED, up)
        self.hero.setQuat(curHeroQuat*newHeroQuat)
        self.hero.setR(0)
        self.hero.setP(0)
        self.updateCameraCollision()
    
    def disableMovement(self, gameObj):
        if gameObj.getName() == self.hero.getName():
            self.ignore('w')
            self.ignore('w-up')
            self.ignore('a')
            self.ignore('a-up')
            self.ignore('s')
            self.ignore('s-up')
            self.ignore('d')
            self.ignore('d-up')
        else:
            if gameObj.getAIBehaviorsHandle().behaviorStatus('pursue') != -1:
                gameObj.getAIBehaviorsHandle().pauseAi('pursue')
    
    def enableMovement(self, gameObj):
        if gameObj.getName() == self.hero.getName():
            self.accept('w', self.setKeyStatus, extraArgs=['w', True])
            self.accept('w-up', self.setKeyStatus, extraArgs=['w', False])
            self.accept('a', self.setKeyStatus, extraArgs=['a', True])
            self.accept('a-up', self.setKeyStatus, extraArgs=['a', False])
            self.accept('s', self.setKeyStatus, extraArgs=['s', True])
            self.accept('s-up', self.setKeyStatus, extraArgs=['s', False])
            self.accept('d', self.setKeyStatus, extraArgs=['d', True])
            self.accept('d-up', self.setKeyStatus, extraArgs=['d', False])
        else:
            if gameObj.getAIBehaviorsHandle().behaviorStatus('pursue') == 'paused': 
                gameObj.getAIBehaviorsHandle().resumeAi('pursue')
    
    def setKeyStatus(self, key, isDown):
        self.keyMap[key] = isDown
        
        # play animations and disable the key's compliment, if it is down
        if isDown:
            if key == 'w':
                if self.hero.getActorHandle() != None:
                    self.hero.getActorHandle().stop('anim_idleFemale') # TODO: make a constant / set in LE
                    self.hero.getActorHandle().setPlayRate(1.0, 'anim_jogFemale')
                    self.hero.getActorHandle().loop('anim_jogFemale')  
                self.keyMap['s'] = False
            elif key == 's':
                if self.hero.getActorHandle() != None:
                    self.hero.getActorHandle().stop('anim_idleFemale') # TODO: make a constant / set in LE
                    self.hero.getActorHandle().setPlayRate(-0.7, 'anim_jogFemale')
                    self.hero.getActorHandle().loop('anim_jogFemale')
                self.keyMap['w'] = False
            elif key == 'a':
                self.keyMap['d'] = False
            elif key == 'd':
                self.keyMap['a'] = False
        elif not isDown:
            if key == 'w':
                if not self.keyMap['s']:
                    if self.hero.getActorHandle() != None:
                        self.hero.getActorHandle().stop('anim_jogFemale')
                        self.hero.getActorHandle().loop('anim_idleFemale')
            elif key == 's':
                if not self.keyMap['w']:
                    if self.hero.getActorHandle() != None:
                        self.hero.getActorHandle().stop('anim_jogFemale')
                        self.hero.getActorHandle().loop('anim_idleFemale')
            elif key == 'a':
                pass
            elif key == 'd':
                pass
    
    def moveHeroTask(self, task):
        dt = globalClock.getDt()

        direction = int(self.keyMap['w'])-int(self.keyMap['s'])
        self.moveHero(direction, dt)      
        if self.keyMap['a']:
            self.turnHeroLeft()
        elif self.keyMap['d']:
            self.turnHeroRight()
        
        return task.cont
            
    
##== Scene Handling =========================================================##

    def loadScenes(self):
        # NOTE: Do not remove!  This function is populated by StandaloneExporter
        pass
    
    def addSequence(self, sequence):
        self.ranSequences.append(sequence)
        
    #this is for changing scenes
    def resetAllSequences(self):
        for seq in self.ranSequences:
            seq.finish()
        
        dr = self.cam.node().getDisplayRegion(0)
        dr.setCamera(self.gameCam)
        
        self.ranSequences = []
    
    def openScene(self, sceneName):
        if (self.scenes.has_key(sceneName)==False):
            print "ERROR:There is no scene under the name ", sceneName,"."
            return
        
        self.startLoadBar(12)
        self.createLoadScreen()
        
        #Part2:Clear all of the collision lists
        self.cTrav.removeCollider(self.heroCNP)
        self.heroGroundHandler.clearEntries()
        self.heroCollisionQueue.clearEntries()
        
        

        self.resetAllSequences()
        self.increaseLoadBar(1)
        
        #Part3: stop all of the tasks
        
        taskMgr.remove('processHeroCollisions')
        taskMgr.remove('updateHeroHeight')
        taskMgr.remove('moveHeroTask')
        taskMgr.remove('cameraFollowTask')
        taskMgr.remove("updateShaders") # ?
        self.combatMgr.stopTasks()
        
        self.gameplayUI.stop()
        self.gameplayUI.removeAllHealthBars()
        
        self.increaseLoadBar(1)
        
        #Part1.1: Stop currently running parts like conversations or camera
        if(self.conversationMgr.isConversationOpen()):
            self.conversationMgr.closeConversation()
        
        #Part 1.2: stop the camera

        
        self.increaseLoadBar(1)
        
        #Part4: Turn-Off all of the player controls
        self.ignore("mouse1")
        
        self.increaseLoadBar(1)
        
        #Part5: Remove all of the game elements that are related with the current scene  
        del self.combatMgr
        
        self.increaseLoadBar(1)
        
        #Part6: Remove all of the children and the lights from the render
        render.getChildren().detach()
        render.clearLight()
        
        self.increaseLoadBar(1)
        
        #Part7:Add the camera and hero or any game element that should be exist in any scene back 
        self.camPivot.reparentTo(render)
        self.hero.reparentTo(render)
        #self.heroWallCollide.reparentTo(render)
        self.heroWallCollideX.reparentTo(render)
        self.heroWallCollideY.reparentTo(render)
        self.heroWallCollideZ.reparentTo(render)
        self.heroGroundCollide.reparentTo(render)
        self.cameraHeroP.reparentTo(render)
        
        self.overlayAmbientLightNP.reparentTo(render)
        
        self.increaseLoadBar(1)
        
        #Part8:Add the new objects from the new scene        
        self.assets, self.objects, self.gameObjects, self.sounds, self.sequences = loadWorld(self.scenes[sceneName], LIBRARY_INDEX)
        
        self.increaseLoadBar(1)
        
        #Part9:Add the hero to the new gameObject list and remove the duplicates of the hero
        self.gameObjects[self.hero.getName()] = self.hero      
        if(self.objects.has_key(self.hero.getName())):
           object = self.objects[self.hero.getName()]
           if(object.hasTag('LE-mainChar')):
               object.detachNode()
               del self.objects[self.hero.getName()]
               
        for name, gameObj in self.gameObjects.iteritems():
            if gameObj.getNP().hasTag('LE-ground'):
                #debug("is Ground")
                bitmask = gameObj.getNP().getCollideMask()
                bitmask |= BITMASK_GROUND
                gameObj.getNP().setCollideMask(bitmask)
        self.increaseLoadBar(1)
        
        #Part10:Restart the tasks.                    
        self.combatMgr = CombatMgr(self)
        
        taskMgr.add(self.processHeroCollisions, 'processHeroCollisions')
        taskMgr.add(self.updateHeroHeight, 'updateHeroHeight')
        taskMgr.add(self.moveHeroTask, 'moveHeroTask')
        taskMgr.add(self.cameraFollowTask, 'cameraFollowTask')
        self.combatMgr.startTasks()
        self.gameplayUI.start()
        
        self.increaseLoadBar(1)
        
        
        self.setCollideMasks(self.gameObjects)
        
        self.increaseLoadBar(1)
        
        #Part11: Change the color of the sky
        if(sceneName.startswith("interior") or sceneName.startswith("Interior")):
            self.setBackgroundColor(BGC_DARK_GREY)
        else:
            self.skybox.reparentTo(render)
            self.setBackgroundColor(BGC_LIGHT_BLUE)
            
        self.increaseLoadBar(1)    
        
        #Part12: Restart the player controls    
        self.accept("mouse1", self.onClickin3D)
        
        self.increaseLoadBar(1)
        self.accept("enter",self.destroyLoadScreen)
        
        debug("After open Scene: "+str(self.heroCollisionQueue.getNumEntries()))
        self.heroCollisionQueue.clearEntries()
        self.cTrav.addCollider(self.heroCNP, self.heroCollisionQueue)
        
        self.destroyLoadScreen()
        #self.loadBar.hide()
        #self.destroyLoadScreen() 
         
    
world = World()
world.run()
