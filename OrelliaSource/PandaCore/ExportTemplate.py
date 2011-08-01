from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *

from direct.ETCleveleditor import LevelLoader
 
SCENE_FILE = None
LIBRARY_INDEX = None

CAM_MOVE_SPEED = None
CAM_ROTATE_SPEED = 60
HEIGHT = None
 
class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
        
        #Load the Level
        #self.objects is a dictionary that maps names(provided in the level editor) to nodepaths
        self.assets, self.objects, self.sounds, self.sequences= LevelLoader.loadLevel(SCENE_FILE, LIBRARY_INDEX)
    
        self.cTrav = CollisionTraverser()
        
        self.setupCameraControls()      
        
    #Setup basic fly-through WASD camera controls
    def setupCameraControls(self):
        self.disableMouse()
        
        self.accept('w', taskMgr.add, [self.moveCamForward, 'moveCamForward'])
        self.accept('w-up', taskMgr.remove, ['moveCamForward'])
        self.accept('a', taskMgr.add, [self.rotateCamLeft, 'rotateCamLeft'])
        self.accept('a-up', taskMgr.remove, ['rotateCamLeft'])
        self.accept('s', taskMgr.add, [self.moveCamBack, 'moveCamBack'])
        self.accept('s-up', taskMgr.remove, ['moveCamBack'])
        self.accept('d', taskMgr.add, [self.rotateCamRight, 'rotateCamRight'])
        self.accept('d-up', taskMgr.remove, ['rotateCamRight'])
        
        self.accept('mouse3', self.startRotateCam)
        self.accept('mouse3-up', self.stopRotateCam)
        
        #setup collisions to cast a ray from the camera to the ground
        cameraLine = CollisionNode('cameraLine')
        cameraLine.addSolid(CollisionLine(Point3(0,0,0), Vec3(0,0,-1)))
        cameraLine.setFromCollideMask(BitMask32.allOn())
        cameraLine.setIntoCollideMask(BitMask32.allOff())
        self.cameraGroundCollide = render.attachNewNode(cameraLine)
        self.cameraGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.cameraGroundCollide, self.cameraGroundHandler)
        
        taskMgr.add(self.updateCamHeight, 'updateCamHeight')
 
    #updates the cameras height based on the ground
    def updateCamHeight(self, task):
        groundEntries = []
        #move the collision line to the camera's position
        self.cameraGroundCollide.setPos(self.cam.getPos(render))
        
        #loop through every collision entry for the line
        for e in self.cameraGroundHandler.getEntries():
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

            #set the camera's height based on the highest collision point
            self.cam.setZ(groundEntries[0].getSurfacePoint(render).getZ() + HEIGHT)
        
        
        self.cameraGroundHandler.clearEntries()
        return task.cont
 
    def moveCamForward(self, task):
        self.cam.setPos(self.cam, 0, CAM_MOVE_SPEED, 0)
        return task.cont
        
    def rotateCamLeft(self, task):
        currentQuat = self.cam.getQuat()
        up = render.getRelativeVector(base.cam, Vec3(0, 0, 1))
        q = Quat()
        q.setFromAxisAngle(CAM_ROTATE_SPEED/50.0, up)
        self.cam.setQuat(currentQuat*q)
        self.cam.setR(0)
        return task.cont
        
    def moveCamBack(self, task):
        self.cam.setPos(self.cam, 0, -CAM_MOVE_SPEED, 0)
        return task.cont
    
    def rotateCamRight(self, task):
        currentQuat = self.cam.getQuat()
        up = render.getRelativeVector(base.cam, Vec3(0, 0, 1))
        q = Quat()
        q.setFromAxisAngle(-CAM_ROTATE_SPEED/50.0, up)
        self.cam.setQuat(currentQuat*q)
        self.cam.setR(0)
        return task.cont
    
    def startRotateCam(self):
        if self.mouseWatcherNode.hasMouse():
            self.mouseLastX = self.mouseWatcherNode.getMouseX()
            self.mouseLastY = self.mouseWatcherNode.getMouseY()
            taskMgr.add(self.rotateCam, 'rotateCam')
    
    #rotate the camera based on mouse movement
    def rotateCam(self, task):
        if self.mouseWatcherNode.hasMouse():
            currX = self.mouseWatcherNode.getMouseX()
            currY = self.mouseWatcherNode.getMouseY()
            
            xDiff = currX - self.mouseLastX
            yDiff = currY - self.mouseLastY
            
            currentQuat = self.cam.getQuat()
            up = render.getRelativeVector(base.cam, Vec3(0, 0, 1))
            right = render.getRelativeVector(base.cam, Vec3(1, 0, 0))
            qX = Quat()
            qX.setFromAxisAngle(xDiff * -CAM_ROTATE_SPEED, up)
            
            qY = Quat()
            qY.setFromAxisAngle(yDiff * CAM_ROTATE_SPEED, right)
            
            q = qX*qY
            
            self.cam.setQuat(currentQuat*q)
            
            self.mouseLastX = currX
            self.mouseLastY = currY
            
            self.cam.setR(0)
            
            return task.cont
        else:
            return task.done
    
    def stopRotateCam(self):
        taskMgr.remove('rotateCam')
    
app = MyApp()
app.run()