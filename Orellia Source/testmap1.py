# Used as a basis by StandaloneExporter, which fills in some of the values to reflect the local computer and project name.

#== Python and Panda imports ==
GAMEPLAY_FOLDER = 'C:/Panda3D-1.7.2/direct/ETCleveleditor'
IN_DEVELOP = False

from PauseGameState import *
import sys, math, os
from math import exp
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *
from panda3d.ai import *
from direct.filter.CommonFilters import CommonFilters

#== Special Imports for final: ####SPECIAL
from direct.gui.OnscreenText import OnscreenText
#####SPECIAL######
from Enemy import *
from SaveSystem import *
from Clickable import *
##################

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
print "Appended path"
sys.path.append("./Panda Core scripts") 
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

from panda3d.core import RopeNode
from panda3d.core import NurbsCurveEvaluator

SCENE_FILE = 'default_0.scene'
LIBRARY_INDEX = 'lib.index'
JOURNAL_FILE = 'testmap1.journal'
SCRIPTS_FILE = 'Scripts.py'

from Scripts import *
INVENTORY_FILE = 'testmap1.inventory'


#== Values for Camera and Main Character Movement (feel free to change) =====#

MAIN_CHAR_MAX_STEP = 3.0 ## SET TO 3.0!!!
MAIN_CHAR_MOVE_SPEED = 500.0 # SET TO 100.0!!! [Zeina]:This speed is with the time-step solution for movement. /CONSIDER: calculate dynamically based on model size | default = 3.0
MAIN_CHAR_ROTATE_SPEED = 2.2 # default = 3.2
MAIN_CHAR_GROUND_OFFSET = 0.0 # This is the distance (offset) above the ground plane to place the main character | default = 0.0
CAMERA_HEIGHT = 1.4 # Relative height of the camera above the main character model (positive = above) | default = 1.0
CAMERA_TRAIL = 2.7 # Relative distance camera trails behind the main character model (positive = behind) | default = 4.0
CAMERA_PITCH = -12 # Default is 10
CAMERA_TURN_THRESHOLD = 1 # The greatest angle (degrees) the main character can face before camera turns to follow his direction | default = 20 
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
        
        ##### SPECIAL VARIABLES ######
        self.seeCollide = True
        self.stealth = False
        self.billboardObjects = {}
        self.enemyMan = EnemyManager()
        self.clickMan = ClickManager()

        self.mX = 0
        self.mY = 0
        self.hasLine = False
        self.notThrow = True
        self.disMouse = False
        self.badDir = None
        self.baseHeroZ = 0
        self.textScreen = OnscreenText(text = 'my text string', pos = (-0.5, 0.02), scale = 0.07)
        self.saveMan = SaveManager(self)
        self.spawnPoint = Point3(0,0,0)
        self.disableObjects = []
        self.tasks = []
        self.camAdjust = False
        self.dTime = 0
        self.movements = []
        self.movementConstants = [['w'], ['d'], ['s'], ['a'], ['w', 'd'], ['w', 'a'], ['s', 'a'], ['s', 'd']];
        self.movementHeadings = [0, -90, 180, 90, -45, 45, 135, -135];
        self.diagonal = math.sqrt(2.0) / 2.2;

        self.currentAnim = 0
        self.animations = ["anim_idleFemale", "anim_jogFemale"]
        self.moved = False;
        self.sequencesToPause = [] #Useful array to loop through in order to pause all neccecary sequences
        self.isStopped = False
        self.blockingText = OnscreenText(text = "", pos = (0.5, 0.2), scale = 0.07,wordwrap = 10,fg = (1,1,1,1),bg = (0,0,0,1))
        self.stopTasks = []
        self.heroHeading = 0.0
        self.currScene = "default_0"
        self.mHeight = 135
        
        self.backSoundSeq = None
        self.screenSounds = {"default_0":["tutorial_music_ALPHA", "tutorial_music_background_ALPHA"], "default_1":["village_music_ALPHA","village_music_background_ALPHA"], "default_2":["forest_music_ALPHA", "forest_music_background_ALPHA"], "default_3":["ship_music_ALPHA", "ship_music_background_ALPHA"]};
        self.moveFactor = 1.0
        #############################
        

        try:
            i = 1/0
        except:
            base.disableMouse()
        #Hide the mouse from view
        props = WindowProperties() 
        props.setCursorHidden(True) 
        base.win.requestProperties(props) 
        
        self.pauseState = PauseGameState(self)
        self.createLoadScreen('./LEGameAssets/Textures/title_screen.png')
        base.graphicsEngine.renderFrame()
        
    #== Environment and Rendering Settings ==
        base.setFrameRateMeter(FLAG_SHOW_FRAMES_PER_SECOND)
        if FLAG_USE_AUTOSHADER:
            render.setShaderAuto()
        self.filters = CommonFilters(base.win, self.cam) # NEW
        if FLAG_SHOW_GLOW:
            bloomSize = 4#'small'
            #filterok = self.filters.setBloom(blend=(1,0,0,1), desat=-0.5, intensity=3.0, size=bloomSize)

            
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
                self.oldPos = self.hero.getPos()
                self.spawnPoint = self.hero.getPos()
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
        ################SPECIAL EFFECTS###################

        # remove the hero from the objects dict so it cannot be clicked by player
        if self.hero.getName() in self.objects:
            del self.objects[self.hero.getName()]
        
        ###########################SPECIAL###########################
        
                
                
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
        self.accept("`",self.cam.place)
    #== Collisions ==
        self.setupCollisions()
        
    #== Controls ==
        self.disableMouse()
        self.keyMap = { 'w':False, 'a':False, 's':False, 'd':False }
        self.enableMovement(self.hero)
        self.accept("mouse1", self.onClickin3D)
        self.accept('escape', self.close)
        #self.accept('z', render.place) 
    
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
        ## taskMgr.add(self.cameraFollowTask, 'cameraFollowTask', appendTask=True)
        taskMgr.add(self.processHeroCollisions, 'processHeroCollisions')
        ##taskMgr.add(self.updateHeroHeight, 'updateHeroHeight')
        ######MOUSE SPECIAL#####
        taskMgr.add(self.mouseTask, 'mouseTask')
        #################
        self.combatMgr.startTasks()
        
        self.accept('enter', self.destroyLoadScreen)
        self.destroyLoadScreen()
        
    ##======SPECIAL ACCEPTS========##
        self.accept('playSound',self.scriptInterface.playSound)
        self.accept('playSound3d',self.scriptInterface.playSound3d)
        self.accept('addCollision',self.addCollision)  
        self.accept('q',self.throwShroom)
        ##self.accept('mouse3-up',self.toggleMouse,[self.disMouse])
        self.accept('playerDie',self.playerDie)
        for keyVal in self.scenes:
            print keyVal;
        #print("Background Sound Scene: " + sceneName);
        self.updateBackgroundSound(self.currScene);
    ##=============================##
    
        filterok = self.filters.setBloom( blend = (1,0,0,1),desat = -.5, intensity = 3, size=8)
    
        if (filterok == False):
            print 'WARNING:Video card not powerful enough to do image postprocessing'
        
        #Starts sequence for displaying
        seq = Sequence(Func(self.displayText,"Use the mouse to rotate the character, and wasd to move."),
                       Wait(5),
                       Func(self.displayText,""))
        seq.start()
        self.spawnPoint = self.hero.getPos()

        ##################CREATE ENEMIES AND OTHER SPECIAL OBJECTS#####################
        self.enemies = {}
        for name, gameObj in self.gameObjects.iteritems():
            points = {}
            if gameObj.getNP().hasTag('enemy'):
                print len(self.enemies)
                self.enemies[len(self.enemies)] = gameObj
                if "point" in gameObj.getNP().getTag("enemy"):
                    backing = False
                    objName = gameObj.getName()
                    if "True" in gameObj.getNP().getTag("mergeSim"):
                        objName = objName[:1]
                        print gameObj.getName(),"--",objName
                    for name2, gameObj2 in self.gameObjects.iteritems():
                        if objName in name2 and "-Point" in name2:
                            points[gameObj2.getNP().getTag("point")] = gameObj2
                            print gameObj2.getNP().getTag("point")
                    if "back" in gameObj.getNP().getTag("param"):
                            backing = True
                self.enemyMan.createEnemy(self,gameObj,gameObj.getNP().getTag("enemy"),points,backing)
            if gameObj.getNP().hasTag('function') and gameObj.getNP().getTag("functionName"):
                self.clickMan.createClickable(self,gameObj,gameObj.getName(),gameObj.getNP().getTag("function"),gameObj.getNP().getTag("functionName"))
            elif gameObj.getNP().hasTag('function'):
                self.clickMan.createClickable(self,gameObj,gameObj.getName(),gameObj.getNP().getTag("function"))
            #if "int_wallA" in name and not "floor" in name:
            #    print name,"and",gameObj,"is being walled"
            #    gameObj.setTag("LE-wall","1")
        ###############LOAD THE WORLD THROUGH SAVE FILE###########
        self.saveMan.loadWorld()
    
##== Utility and World Initialization functions =============================##
    def playMovie(self, movieName):
        try:
            self.loader.loadSfx(movieName)
            hasSound = True
        except:
            hasSound = False
        movieTexture = self.loader.loadTexture(movieName)
        if hasSound:
            movieSound = self.loader.loadSfx(movieName)
        movieTexture.synchronizeTo(movieSound)
        self.movieScreen = OnscreenImage(movieTexture)
        aspect2d.hide()
        self.movieScreen.reparentTo(render2d)
        self.gameplayUI.hideAll()
        if hasSound:
            movieSound.play()
        Sequence(Wait(movieSound.length()),Func(self.killMovie)).start()
        
    def pause(self):
        #Part3: stop all of the tasks
        self.tasks = []
        self.enemyMan.pauseAll();
        
        for taskName in taskMgr.getAllTasks():
            if not "Loop" in str(taskName) and not "ival" in str(taskName):
                taskMgr.remove(taskName)
                self.tasks.append( (taskName,str(taskName)[11:]) )
            else:
                print str(taskName)[11:] + " still working";
        
        self.toggleMouse(not True);
        self.pauseState.activate()
           
        print "STUPID PENGAS"
    def resume(self):
        self.pauseState.deactivate()
        self.toggleMouse(not False);
        self.enemyMan.resumeAll();
        for taskName in self.tasks:
            print taskName
            taskMgr.add(taskName[0])
        
    def killMovie(self):
        self.movieScreen.detachNode()
        self.movieScreen.destroy()
        aspect2d.show()
        self.gameplayUI.showAll()
        
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
        
        self.cHandle = CollisionHandlerEvent()
        self.cHandle.addInPattern("HitAnything")
        self.cHandle.addAgainPattern("HitAnything")
        self.accept("HitAnything",self.handleCollision)
        
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
        ##print "processHeroCollisions"
        # CONSIDER: may not be necessary to sort
        if(self.heroCollisionQueue.getNumEntries() > 0):
            self.heroCollisionQueue.sortEntries()
        debug("queue size: "+str(self.heroCollisionQueue.getNumEntries()))
        for i in range(self.heroCollisionQueue.getNumEntries()):
            # CONSIDER: if entry.hasInto(): for efficiency
             
            ##print "i: "+str(i)   
            # TODO: check if GameObject is passable, and react accordingly (store old position, revert to it)
            if(self.heroCollisionQueue.getNumEntries() <= 0):
                return
            entry = self.heroCollisionQueue.getEntry(i)
            print "entry: "+str(entry)
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
            
            if "SCAN" in entry.getIntoNode().getName():
                name = entry.getIntoNode().getName()[:-5]
                self.enemyMan.notifyEnemy(entry.getIntoNode().getName()[:-5],self.hero)
            
            if "spawnPoint" in entry.getIntoNode().getName():
                self.spawnPoint = self.hero.getPos()
                self.disableObjects.append(entry.getIntoNode().getName())
                entry.getIntoNode().clearSolids()
                print "New spawn = ",self.spawnPoint
                model = render.attachNewNode(PandaNode("SaveParticle"))
                model.setPos(self.hero.getPos() + (0,0,25))
                model.setScale(25,25,25)
                particle = ParticleEffect()
                particle.loadConfig(Filename('./particles/particle_Checkpoint.ptf'))
                particle.start(model)
                print model
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
        
    #Entire task is now useless die to camera rotation being handled when the character is turned.
    ## def cameraFollowTask(self, task):
        ## heroH = self.hero.getH(render) + self.heroHeadingOffset
        ## camPivotH = self.camPivot.getH(render)
        
        ## # normalizes the headings to avoid jumps in the difference
        ## # which could come from passing 360 and going back to 0, for example
        ## # TODO: stress test, esp. with different values of self.heroHeadingOffset
        ## while heroH + 180 < camPivotH:
            ## heroH += 360
        ## while camPivotH + 180 < heroH:
            ## camPivotH += 360
              
        ## self.lastHeroH = heroH
        ## rotateLeft = (heroH >= camPivotH)
        ## rotateRight = not rotateLeft
        ## diff = (self.hero.getH() - self.camPivot.getH()) + 180
        ## ## print self.hero.getH(),",",self.camPivot.getH()
        ## ## up = render.getRelativeVector(self.camPivot, Vec3(0, 0, 1))
        ## ## up.normalize()
        ## ## curCamQuat = self.camPivot.getQuat()
        ## ## newCamQuat = Quat()
        ## ## newCamQuat.setFromAxisAngle(diff, up)
        ## ## self.camPivot.setQuat(curCamQuat*newCamQuat)
        ## ## self.cameraMove = LerpHprInterval(self.camPivot,.05,(heroH,self.camPivot.getP(),self.camPivot.getR()),(self.camPivot.getH(),self.camPivot.getP(),self.camPivot.getR()))
        ## ## if self.cameraMove.isPlaying():
            ## ## self.cameraMove.finish()
            ## ## print "FINISHING"
        ## ## self.cameraMove.start()
        ## ## elif rotateRight:
            ## ## self.camPivot.setH(self.camPivot.getH() - diff)
        
## #        if(len(self.cameraEntriesPre)>0):
## #            #print self.cameraEntriesPre
## #            if(self.hero.getDistance(self.cam) > 5):
## #                moveAmount = min(globalClock.getDt()*200,5.0)
## #                pos = self.cam.getQuat().getForward()*moveAmount
## #                newpos = self.cam.getPos() + pos
## #                self.oldCameraEntriesPre = []
## #                for e in self.cameraEntriesPre:
## #                    self.oldCameraEntriesPre.append(e)
## #                self.cam.setFluidPos(newpos)
## #            
## #        else:
## #            if(self.hero.getDistance(self.cam) < 100):
## #                moveAmount = min(globalClock.getDt()*200,5.0)
## #                pos = self.cam.getQuat().getForward()*(-moveAmount)
## #                oldpos = self.cam.getPos()
## #                newpos = self.cam.getPos() + pos
## #                self.cam.setFluidPos(newpos)
## #                for e in self.oldCameraEntriesPre:
## #                    #print e.getIntoNodePath()
## #                    self.cTrav.traverse(e.getIntoNodePath())
## #                #self.cTrav.traverse(render)
## #                    if(len(self.cameraSphereQueue.getEntries())>0):
## #                        self.cam.setFluidPos(oldpos)
            
        
        ## return task.cont
    

    def runCamera(self, cameraName, isLoop = False):
        debug("Running the camera")
        #debug(str(self.sequences))

        self.oldCamera = self.cam
        self.dr = self.win.makeDisplayRegion()
        
        dr2 = self.cam.node().getDisplayRegion(0)#
        self.objects[cameraName].node().setLens(base.camLens)
        parent = self.cam.getParent()
        self.cam.detachNode()

        self.dr.setCamera(self.objects[cameraName])
        
        Move1 = LerpPosInterval(self.objects[cameraName],3,self.objects[cameraName].getPos(),self.objects[cameraName].getPos())
        sequence = Sequence(Move1);
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

    def updateHeroHeight(self):
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
                
        if len(groundEntries) > 0:
            #sort the collision entries based on height
            groundEntries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),x.getSurfacePoint(render).getZ()))
            if not groundEntries[0].getSurfacePoint(render).getZ() + MAIN_CHAR_GROUND_OFFSET > self.mHeight:
                #set hero height and pivot height
                self.hero.setZ(groundEntries[0].getSurfacePoint(render).getZ() + MAIN_CHAR_GROUND_OFFSET)
                self.camPivot.setZ(groundEntries[0].getSurfacePoint(render).getZ() + MAIN_CHAR_GROUND_OFFSET)
                # TODO: unlink these from being in the same task in case we want pivot to not be linked to hero (ex. cutscene)
            else:
                self.hero.setPos(self.oldPos)
        self.heroGroundHandler.clearEntries()
    
    def updateHeroPos(self, queue, stepSize):
        wallEntries = []
        for w in queue.getEntries():
            np = w.getIntoNodePath().findNetTag('OBJRoot')
            ##print np,"andddd",w
            if np.hasTag('LE-wall'):
                #if self.isInObstacleRange(self.hero, w, stepSize):
                wallEntries.append(w)
        if len(wallEntries) > 0:
            self.herowallcollision = True
            if not self.isStopped:
                self.isStopped = True
                if not w.getIntoNodePath().getTag("stopName") == None:
                    text = w.getIntoNodePath().getTag("stopName")
                else:
                    text = "I cannot go that way..."
                ##print "BLOCKED!!!!"
                self.blockingText = OnscreenText(text = text, pos = (0.5, 0.8), scale = 0.07,wordwrap = 10,fg = (1,1,1,1),bg = (0,0,0,1))
            #self.collisionsurfaceP = wallEntries[0].getSurfacePoint(render)
        else:
            ##print "NOT BLOCKED!!!!"
            self.herowallcollision = False
            self.blockingText.destroy()
            
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
        impair = 1
        if self.stealth:
            impair = .5
        moveStep = MAIN_CHAR_MOVE_SPEED*dt*impair
        if moveStep > MAIN_CHAR_MAX_STEP:
            moveStep = MAIN_CHAR_MAX_STEP
        temp.setPos(self.hero, 0,-direction*moveStep, 0)
        temp.show()
        #oldPos = self.heroWallCollideX.getPos()
        

        ##print self.oldPos,",",self.hero.getPos()
                
        ## hypot = math.sqrt( ( abs(self.hero.getX() - temp.getX()) )**2 + (abs(temp.getZ() - self.hero.getZ())) **2)
        ##angle = math.atan2((abs(self.heroWallCollideZ.getZ()) - abs(self.oldPos.getZ())),(abs(self.heroWallCollideX.getX()) - abs(self.oldPos.getX())))
        #print temp.getPos(),",",self.oldPos,">>>>>",abs(temp.getZ())-abs(self.oldPos.getZ())
        ##print (abs(self.heroWallCollideZ.getZ() - self.oldPos.getZ()))
        
        # deltaVector = self.hero.getPos() - temp.getPos()
        # length = deltaVector.length()
        # deltaVector.z = self.hero.getZ() - self.oldPos.z;
        # print length
        # if not length > 0.0:
            # print "MICRO MOVENENT YO"
        # deltaVector *= 1000.0
        # if length > 0.0 and deltaVector.z > 0.0 and canMove:
            # leg = math.sqrt((deltaVector.x **2) + (deltaVector.y **2));
            # length = math.sqrt((leg **2) + (deltaVector.z **2));
            # if leg > 0.0:
                # print length, " > ", leg
                # angle = math.degrees(math.acos(leg / length))
                # # print angle
                # canMove = angle < 30.0
        #if direction * abs(self.hero.getZ())-abs(self.oldPos.getZ()) > 3:
        #    self.badDir = direction
        #    canMove = False
        #self.oldPos = self.hero.getPos()

        # print abs(abs(self.hero.getZ())-abs(self.oldPos.getZ()));
        # print "HOLY";
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
        ##self.hero.setH(0)
        self.updateCameraCollision()
        temp.detachNode()
        #self.updateHeroHeight()
        #self.placeCamera(self.hero)
        
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

    
    def MoveHeroLR(self,dt,dir):
        ## up = render.getRelativeVector(base.cam, Vec3(0, 0, 1))
        ## up.normalize()
        
        ## curHeroQuat = self.hero.getQuat()
        ## newHeroQuat = Quat()
        ## newHeroQuat.setFromAxisAngle(MAIN_CHAR_ROTATE_SPEED, up)
        ## self.hero.setQuat(curHeroQuat*newHeroQuat)
        ## self.hero.setR(0)
        ## self.hero.setP(0)
        ## self.updateCameraCollision()
        temp = render.attachNewNode("Dummy")#NodePath()
        impair = 1
        if self.stealth:
            impair = .5
        moveStep = MAIN_CHAR_MOVE_SPEED*dt*impair
        if moveStep > MAIN_CHAR_MAX_STEP:
            moveStep = MAIN_CHAR_MAX_STEP
        temp.setPos(self.camPivot, dir * moveStep,0, 0)
        
        #self.oldPos = self.hero.getPos()
        

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
        
        ## if dir == 1:
            ## ##self.hero.setH(-90)
        ## else:
            ## ##self.hero.setH(90)

        self.updateCameraCollision()
        temp.detachNode()
        #self.updateHeroHeight()
        #self.placeCamera(self.hero)
    
    def disableMovement(self, gameObj):
        if gameObj.getName() == self.hero.getName():
            self.movements = [];
            self.tempMovements = [];
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
           ## self.accept('q',self.setKeyStatus, extraArgs=['q', True])
        else:
            if gameObj.getAIBehaviorsHandle().behaviorStatus('pursue') == 'paused': 
                gameObj.getAIBehaviorsHandle().resumeAi('pursue')
    
    def setKeyStatus(self, key, isDown):

        if isDown:
            if not key in self.movements:
                self.movements.append(key);
        else:
            if key in self.movements:
                self.movements.remove(key);
        # self.keyMap[key] = isDown
        # # if key == 'q':
            # # if self.stealth:
                # # self.phaseOut()
            # # else:
                # # self.phaseIn()
        # # play animations and disable the key's compliment, if it is down
        # if isDown:
            # if key == 'w':
                # if self.hero.getActorHandle() != None:
                    # if len(self.movements) > 0:
                        # self.hero.getActorHandle().stop("anim_jogFemale");
                        # self.movements = ['w'];
                    # else:
                        # self.hero.getActorHandle().stop('anim_idleFemale') # TODO: make a constant / set in LE
                    # self.hero.getActorHandle().setPlayRate(1.0, 'anim_jogFemale')
                    # self.hero.getActorHandle().loop('anim_jogFemale')
                    # if not 'w' in self.movements:
                        # self.movements.append('w');
                # self.keyMap['s'] = False
            # elif key == 's':
                # if self.hero.getActorHandle() != None:
                    # if len(self.movements) > 0:
                        # self.hero.getActorHandle().stop("anim_jogFemale");
                        # self.movements = ['s'];
                    # else:
                        # self.hero.getActorHandle().stop('anim_idleFemale') # TODO: make a constant / set in LE
                    # self.hero.getActorHandle().setPlayRate(-0.7, 'anim_jogFemale')
                    # self.hero.getActorHandle().loop('anim_jogFemale')
                    # if not 's' in self.movements:
                        # self.movements.append('s');
                # self.keyMap['w'] = False
            # elif key == 'a':
                # if self.hero.getActorHandle() != None:
                    # if len(self.movements) > 0:
                        # self.hero.getActorHandle().stop("anim_jogFemale");
                        # self.movements = ['a'];
                    # else:
                        # self.hero.getActorHandle().stop('anim_idleFemale') # TODO: make a constant / set in LE
                    # self.hero.getActorHandle().setPlayRate(1.0, 'anim_jogFemale')
                    # self.hero.getActorHandle().loop('anim_jogFemale')
                    # if not 'a' in self.movements:
                        # self.movements.append('a');
                # self.keyMap['d'] = False
            # elif key == 'd':
                # if self.hero.getActorHandle() != None:
                    # if len(self.movements) > 0:
                        # self.hero.getActorHandle().stop("anim_jogFemale");
                        # self.movements = ['d'];
                    # else:
                        # self.hero.getActorHandle().stop('anim_idleFemale') # TODO: make a constant / set in LE
                    # self.hero.getActorHandle().setPlayRate(1.0, 'anim_jogFemale')
                    # self.hero.getActorHandle().loop('anim_jogFemale')
                    # if not 'd' in self.movements:
                        # self.movements.append('d');
                # self.keyMap['a'] = False
        # elif not isDown:
            # if key == 'w':
                # if not self.keyMap['s']:
                    # if self.hero.getActorHandle() != None:
                        # if len(self.movements) <= 1 and 'w' in self.movements:
                            # self.hero.getActorHandle().stop('anim_jogFemale')
                            # self.hero.getActorHandle().loop('anim_idleFemale')
                        # if 'w' in self.movements:
                            # self.movements.remove('w');
            # elif key == 's':
                # if not self.keyMap['w']:
                    # if self.hero.getActorHandle() != None:
                        # if len(self.movements) <= 1 and 's' in self.movements:
                            # self.hero.getActorHandle().stop('anim_jogFemale')
                            # self.hero.getActorHandle().loop('anim_idleFemale')
                        # if 's' in self.movements:
                            # self.movements.remove('s');
            # elif key == 'a':
                # if not self.keyMap['d']:
                    # if self.hero.getActorHandle() != None:
                        # if len(self.movements) <= 1 and 'a' in self.movements:
                            # self.hero.getActorHandle().stop('anim_jogFemale')
                            # self.hero.getActorHandle().loop('anim_idleFemale')
                        # if 'a' in self.movements:
                            # self.movements.remove('a');
            # elif key == 'd':
                # if not self.keyMap['a']:
                    # if self.hero.getActorHandle() != None:
                        # if len(self.movements) <= 1 and 'd' in self.movements:
                            # self.hero.getActorHandle().stop('anim_jogFemale')
                            # self.hero.getActorHandle().loop('anim_idleFemale')
                        # if 'd' in self.movements:
                            # self.movements.remove('d');
    def processMovements(self):
        self.tempMovements = []
        for movement in self.movements:
            self.tempMovements.append(movement);
        
        if 'w' in self.tempMovements and 's' in self.tempMovements:
            self.tempMovements.remove('w')
            self.tempMovements.remove('s')
        if 'a' in self.tempMovements and 'd' in self.tempMovements:
            self.tempMovements.remove('a')
            self.tempMovements.remove('d')
        move = -1;
        isMatch = False;
        for i in range(len(self.movementConstants)):
            isMatch = True
            for movement in self.tempMovements:
                if not movement in self.movementConstants[i]:
                    isMatch = False
                    break;
            if isMatch:
                move = i;
                break;
        return move
    def setAnim(self):
        if len(self.tempMovements) == 0:
            if self.currentAnim == 1:
                self.hero.getActorHandle().stop(self.animations[self.currentAnim])
                self.currentAnim = 0 # TODO: replace with constant
                self.hero.getActorHandle().loop(self.animations[self.currentAnim])
        elif self.currentAnim == 0:
            self.hero.getActorHandle().stop(self.animations[self.currentAnim])
            self.currentAnim = 1 # TODO: replace with constant
            if False: # 's' in self.tempMovements:
                self.hero.getActorHandle().setPlayRate(-0.7, 'anim_jogFemale')
            else:

                self.hero.getActorHandle().setPlayRate(1.0, 'anim_jogFemale')
            self.hero.getActorHandle().loop(self.animations[self.currentAnim])

    def moveHeroTask(self, task):
        dt = globalClock.getDt()
        dt *= self.moveFactor
        currentMove = self.processMovements();
        self.setAnim()

        direction = int('w' in self.tempMovements or 's' in self.tempMovements)
        if len(self.tempMovements) >= 2:
            dt *= (self.diagonal);

        self.oldPos = self.hero.getPos()
        self.moved = False;
        if len(self.tempMovements) == 0:
            self.hero.getActorHandle().stop('anim_jogFemale')
            self.hero.getActorHandle().loop('anim_idleFemale')
        if 'a' in self.tempMovements:
            self.moved = True
            self.MoveHeroLR(dt,-1)
        elif 'd' in self.tempMovements:
            self.moved = True
            self.MoveHeroLR(dt,1)
        if not direction == 0:
            self.moved = True
            self.moveHero(direction, dt)
        self.updateHeroHeight()
        if self.moved:
            self.placeCamera(self.hero)
        if not currentMove == -1:
            self.heroHeading = self.movementHeadings[currentMove];
        
        return task.cont
            
    
##== Scene Handling =========================================================##

    def loadScenes(self):

        self.scenes['default_0'] = 'default_0.scene'
        self.scenes['default_1.scene'] = 'default_1.scene'
        self.scenes['default_2.scene'] = 'default_2.scene'
        self.scenes['default_3.scene'] = 'default_3.scene'
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
        
        self.currScene = sceneName

        #Part2:Clear all of the collision lists
        self.cTrav.removeCollider(self.heroCNP)
        self.heroGroundHandler.clearEntries()
        self.heroCollisionQueue.clearEntries()
        
        self.journalMgr.reset()
        

        self.resetAllSequences()
        self.increaseLoadBar(1)
        
        #Part3: stop all of the tasks
        
        taskMgr.remove('processHeroCollisions')
        taskMgr.remove('moveHeroTask')
        ## taskMgr.remove('cameraFollowTask')
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
        if(self.objects.has_key(self.hero.getName())):
           object = self.objects[self.hero.getName()]
           if(object.hasTag('LE-mainChar')):
               self.hero.setPos(object.getPos())
               self.placeCamera(self.hero)
               object.detachNode()
               del self.objects[self.hero.getName()]
               
        for name, gameObj in self.gameObjects.iteritems():
            if gameObj.getNP().hasTag('LE-ground'):
                #debug("is Ground")
                bitmask = gameObj.getNP().getCollideMask()
                bitmask |= BITMASK_GROUND
                gameObj.getNP().setCollideMask(bitmask)

        ##################CREATE ENEMIES AND OTHER SPECIAL OBJECTS#####################
        self.enemies = {}
        for name, gameObj in self.gameObjects.iteritems():
            points = {}
            if gameObj.getNP().hasTag('enemy'):
                print len(self.enemies)
                self.enemies[len(self.enemies)] = gameObj
                if "point" in gameObj.getNP().getTag("enemy"):
                    backing = False
                    objName = gameObj.getName()
                    if "True" in gameObj.getNP().getTag("mergeSim"):
                       objName = objName[:1]
                       print gameObj.getName(),"--",objName
                    for name2, gameObj2 in self.gameObjects.iteritems():
                       if objName in name2 and "-Point" in name2:
                           points[gameObj2.getNP().getTag("point")] = gameObj2
                           print gameObj2.getNP().getTag("point")
                    if "back" in gameObj.getNP().getTag("param"):
                       backing = True
                self.enemyMan.createEnemy(self,gameObj,gameObj.getNP().getTag("enemy"),points,backing)
            if gameObj.getNP().hasTag('function') and gameObj.getNP().getTag("functionName"):
                self.clickMan.createClickable(self,gameObj,gameObj.getName(),gameObj.getNP().getTag("function"),gameObj.getNP().getTag("functionName"))
            elif gameObj.getNP().hasTag('function'):
                self.clickMan.createClickable(self,gameObj,gameObj.getName(),gameObj.getNP().getTag("function"))
        #if "int_wallA" in name and not "floor" in name:
        #    print name,"and",gameObj,"is being walled"
        #    gameObj.setTag("LE-wall","1")
        self.increaseLoadBar(1)
        
        #Part10:Restart the tasks.                    
        self.combatMgr = CombatMgr(self)
        
        taskMgr.add(self.processHeroCollisions, 'processHeroCollisions')
        ##taskMgr.add(self.updateHeroHeight, 'updateHeroHeight')
        taskMgr.add(self.moveHeroTask, 'moveHeroTask')
        ## taskMgr.add(self.cameraFollowTask, 'cameraFollowTask')
        
        ################SPECIAL FUNCTIONS################
        taskMgr.add(self.mouseTask, 'mouseTask')
        #############################################
        
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
        self.currLevel = sceneName
        print("Background Sound Scene: " + sceneName);
        self.updateBackgroundSound(sceneName);
        #self.loadBar.hide()
        #self.destroyLoadScreen() 
############################# SPECIAL TEST FUNCTIONS #######################################
    def phaseIn(self):
        self.stealth = True
        self.hero.setAlphaScale(0.5)
        
    def phaseOut(self):
        self.stealth = False
        self.hero.setAlphaScale(1)
    def Billboard(self,npcName,type,name):
        text = TextNode(npcName + '-node')
        text.setText(npcName)
        print type
        if type == "friendly":
            text.setTextColor(0, 255, 0, 1)
        if type == "neutral":
            text.setTextColor(1, 1, 1, 1)
        if type == "hostile":
            text.setTextColor(255, 0, 0, 1)
        textNodePath = NodePath(text.generate())
        textNodePath.reparentTo(self.objects[name])
        textNodePath.setScale(10)
        textNodePath.setPos(0,0,18)
        if type == "friendly":
            textNodePath.setColor(0, 255, 0)
        if type == "neutral":
            textNodePath.setColor(255, 255, 255)
        if type == "hostile":
            textNodePath.setColor(255, 0, 0)
        billboard = BillboardEffect.make((0,0,1),True,True,0.0,self.cam,self.cam.getPos())
        textNodePath.setEffect(billboard)
        self.billboardObjects[npcName] = textNodePath
        
    def addCollision(self,object,traverse):
        if traverse == "Queue":
            self.cTrav.addCollider(object,self.heroGroundHandler)
        if traverse == "Handle":
            self.cTrav.addCollider(object,self.cHandle)
    def mouseTask(self,task):
        if not self.disMouse and base.mouseWatcherNode.hasMouse():
            centerx =  base.win.getProperties().getXSize()/2.0 
            centery =  base.win.getProperties().getYSize()/2.0 
            mouse = base.win.getPointer(0)
            if abs( mouse.getX() - centerx) / 2.0:
                if mouse.getX() > centerx:
                    self.mX -= abs( mouse.getX() - centerx) / 2.0
                else:
                    self.mX += abs( mouse.getX() - centerx) / 2.0
                    
                if mouse.getY() > centery:
                    self.mY -= abs( mouse.getY() - centery) / 2.0
                else:
                    self.mY += abs( mouse.getY() - centery) / 2.0
                self.dTime = 0
            HValue = (self.mX/400.0) * 180
            RotValue = (self.mY/300.0) * 25
            if RotValue > 0:
                if RotValue > 50:
                    RotValue = 50
                expon =  exp(-RotValue / 50)
                rotsmooth = RotValue*expon

                RotValue = rotsmooth
            elif RotValue < 0:
                if RotValue < -50:
                    RotValue = -50
                expon =  exp(RotValue / 50)
                rotsmooth = RotValue*expon

                RotValue = rotsmooth
            if self.moved or self.hasLine:
                self.hero.setH(HValue + self.heroHeading)


            
            self.camH = HValue + 180 #What camera should be
            self.camHCurr = self.camPivot.getH() #What cam is
            
            self.camP = RotValue
            self.camPCurr = self.camPivot.getP()
            
            self.dTime += globalClock.getDt()
            
            if self.dTime < .2:
                self.dTime = .2
            
            camHDelta = self.camH - self.camHCurr
            camPDelta = self.camP - self.camPCurr
            
            exponH = (0.3) ** self.dTime
            
            self.camHCurr += camHDelta * (1 - exponH)
            self.camPCurr += camPDelta * (1 - exponH)
            
            self.camPivot.setH(self.camHCurr)
            self.camPivot.setP(self.camPCurr)
            
            self.throwV = (RotValue + 30) * ( (RotValue + 30) / 20)
            base.win.movePointer(0,centerx,centery)
        return task.cont
    
    def throwShroom(self):
        if not self.hasLine:
            ## parabolaNum = 50
            ## points = range(parabolaNum)
            self.LinePoint1 = render.attachNewNode(PandaNode("LinePoint1"))
            self.LinePoint1.setPos(-2,0,10)
            self.LinePoint2 = render.attachNewNode(PandaNode("LinePoint2"))
            self.LinePoint2.setPos(-2,-35,15)
            self.LinePoint3 = render.attachNewNode(PandaNode("LinePoint3"))
            self.LinePoint3.setPos(-2,-55,0)
            self.LinePoint4 = render.attachNewNode(PandaNode("LinePoint4"))
            self.LinePoint4.setPos(-2,-55,-self.hero.getZ())
            
            self.LinePoint1.reparentTo(self.hero)
            self.LinePoint2.reparentTo(self.hero)
            self.LinePoint3.reparentTo(self.hero)
            self.LinePoint4.reparentTo(self.hero)
            
            self.hasLine = True
            self.ropetst = Rope("tstArc")
            self.ropetst.setup(3,[(self.LinePoint1,self.LinePoint1.getPos()),(self.LinePoint2,self.LinePoint2.getPos()),(self.LinePoint3,self.LinePoint3.getPos()),(self.LinePoint4,self.LinePoint4.getPos())])
            self.ropetst.setColor(1,0,0,1) 
            self.ropetst.reparentTo(self.hero)
            self.throwV = 55
            
            ##self.accept('wheel_up',self.incrThrow,[1])
            ##self.accept('wheel_down',self.incrThrow,[-1])
            self.accept('e',self.stopLine)
            taskMgr.add(self.updateArc,"updateArk")
        elif self.notThrow:
            self.notThrow = False
            if self.hasShrooms():
                self.collisionShroom = CollisionNode("Shroom")
                self.collisionShroom.addSolid(CollisionSphere((0,0,0),5))
                self.collisionShroom.setIntoCollideMask(BitMask32.bit(2))
                self.collisionNode = render.attachNewNode(self.collisionShroom)
                self.addCollision(self.collisionNode,"Handle")
                self.collisionNode.show()
                ##self.scriptInterface.RunObjectRope(self.collisionNode,self.ropetst, 5,False,True)
                sequence = UniformRopeMotionInterval(self.ropetst,
                                                 self.collisionNode,
                                                 duration= 1.9,
                                                 followPath = True)
                mySequence = Sequence(Func(sequence.start),Wait(1.1),Func(sequence.finish),Func(self.stopLine))
                sequence.start()
                mySequence.start()
                self.gameplayUI.shroomUI.takeShroom();
            self.ropetst.hide()
            taskMgr.remove("updateArk")
            ##self.ignore('wheel_up')
            ##self.ignore('wheel_down')
            self.ignore('e')
            if not self.hasShrooms():
                self.stopLine();
    def hasShrooms(self):
        return (self.gameplayUI.shroomUI.shroomCount > 0);
    def updateArc(self,task):
            self.LinePoint1.setHpr(0,0,0)
            self.LinePoint2.setHpr(0,0,0)
            self.LinePoint3.setHpr(0,0,0)
            
            print self.throwV
            self.LinePoint2.setPos(-2,-35 + (-self.hero.getZ() / 150),self.throwV / 2 - 18)
            self.LinePoint3.setPos(-2,-self.throwV * (self.hero.getZ() / 45),0)
            self.LinePoint4.setPos(-2,-self.throwV * (self.hero.getZ() / 45),-self.hero.getZ())
            
            if self.hasLine:
                self.ropetst.removeNode()
                self.ropetst = Rope("tstArc")
                self.ropetst.setup(3,[(self.LinePoint1,self.LinePoint1.getPos()),(self.LinePoint2,self.LinePoint2.getPos()),(self.LinePoint3,self.LinePoint3.getPos()),(self.LinePoint4,self.LinePoint4.getPos())])
                self.ropetst.setColor(1,0,0,1) 
                self.ropetst.reparentTo(self.hero)
                return Task.cont
        
    def incrThrow(self,value):
        print "in incrThrow"
        self.throwV += value
        if self.throwV > 60:
            self.throwV = 60
        elif self.throwV < 20:
            self.throwV = 20
    
    def stopLine(self,task=None):
        self.ropetst.removeNode()
        try:
            if self.collisionShroom != None:
                self.collisionShroom.removeNode()
        except:
            pass
        self.hasLine = False
        self.notThrow = True
    
    def handleCollision(self,entry):
        if "Shroom" in entry.getFromNode().getName():
                if "EnemyCollider"  in entry.getIntoNode().getName():
                    name = entry.getIntoNode().getName()[:-13]
                    taskMgr.doMethodLater(.5,self.enemyMan.enemyList[name].disableCollisions,"disableCollisions")
    def toggleMouse(self,toggle):
        print toggle
        props = WindowProperties() 
        if toggle:
            self.disMouse = False
            props.setCursorHidden(True)
            centerx =  base.win.getProperties().getXSize()/2 
            centery =  base.win.getProperties().getYSize()/2 
            base.win.movePointer(0,centerx,centery)
        else:
            self.disMouse = True
            props.setCursorHidden(False)
            self.enableMouse()
        base.win.requestProperties(props)
        ##self.accept('mouse3-up',self.toggleMouse,[self.disMouse]) 
    
    def displayText(self,text1):
        self.textScreen.destroy()
        self.textScreen = OnscreenText(text = text1, pos = (-0.6, 0.5), scale = 0.07,wordwrap = 10,fg = (1,1,1,1),bg = (0,0,0,1))
    
    def close(self):
        ##self.saveMan.saveWorld()
        sys.exit()
    def playerDie(self):
        self.hero.setPos(self.spawnPoint)
        self.placeCamera(self.hero)
    def startMob(self,mobName):
        self.enemyMan.enemyList[mobName].resume()
    def moveDownward(self,gameObj,sec,useParticles):
        print gameObj,sec,useParticles
        downObj = self.objects[gameObj]
        moveLerp = LerpPosInterval(downObj,sec,downObj.getPos() + (0,0,-150),downObj.getPos())
        self.stopTasks.append(moveLerp)
        ##if useParticles:
        ##    model = render.attachNewNode(PandaNode("DustParticle"))
        ##    model.setPos(downObj.getPos() + (0,0,25))
        ##    model.setScale(25,25,25)
        ##    particle = ParticleEffect()
        ##    print Filename('./particles/steam.ptf')
        ##    particle.loadConfig(Filename('./particles/steam.ptf'))
        ##    particle.start(model)
        moveLerp.start()
    def callFunc(self,funcName):
        print funcName
        exec "self."+funcName

    def resumeEnemiesStagger(self):
        enemySeq = Sequence()
        for ii in self.enemyMan.enemyList:
            enemySeq.append(Func(self.enemyMan.enemyList[ii].resume))
            enemySeq.append(Wait(2))
        print "Start em!"
        enemySeq.start()
    def Truth(self):
        return True

    def endDemo(self):
        seq = Sequence(Func(self.displayText,"This ends our demo of Orellia. Thank you for participating in the Alpha phase of this project."),
                       Wait(10),
                       Func(sys.exit))
        seq.start()

    def setMountainHeight(self,newHeight):
        self.mHeight = newHeight

    def updateBackgroundSound(self, sceneName):
        try:
            if sceneName == "default_2.scene" or sceneName == "default_2":
                print "fail0: " + sceneName
                self.moveFactor = 500.0;
            else:
                print "fail: " + sceneName
                self.moveFactor = 1.0;

            if not self.backSoundSeq == None:
                self.backSoundSeq.finish();
            self.backSoundSeq = Sequence();
            paraSeq = Parallel();
            print(sceneName)
            for soundName in self.screenSounds[sceneName]:
                print soundName;
                paraSeq.append(Func(self.playBackground, "Sounds\\" + soundName + ".mp3"));
            self.backSoundSeq.append(paraSeq);
            self.backSoundSeq.start();
        except:
            pass
    def playBackground(self, sound):
        mySound = base.loader.loadSfx(sound)
        mySound.setLoop(True)
        mySound.play()
      

world = World()
world.run();