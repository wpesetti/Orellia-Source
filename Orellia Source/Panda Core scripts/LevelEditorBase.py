"""
Base class for Level Editor

You should write your own LevelEditor class inheriting this.
Refer LevelEditor.py for example.
"""

from direct.showbase.DirectObject import *
from direct.directtools.DirectUtil import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from FileMgr import *
from ActionMgr import *
from Library import *
from Project import *
from StandaloneExporter import *
import Util
import os
import stat
import shutil
import tempfile
import wx
import sys, traceback

#enums
BGC_LIGHT_BLUE = Vec4(166.0/255.0,207.0/255.0,240.0/255.0,1)
BGC_LIGHT_GREEN = Vec4(196.0/255.0,253.0/255.0,185.0/255.0,1)
BGC_BLACK = Vec4(0,0,0,1)
BGC_DARK_GREY = Vec4(45.0/255,45.0/255.0, 45.0/255.0,1)

class LevelEditorBase(DirectObject):
    """ Base Class for Panda3D LevelEditor """ 
    def __init__(self):
        #loadPrcFileData('startup', 'window-type none')
        self.currentFile = None
        
        self.fNeedToSave = False    #if there are unsaved changes
        self.actionEvents = []
        #self.objectMgr = ObjectMgr(self)
        self.fileMgr = FileMgr(self)
        self.actionMgr = ActionMgr()
        self.standaloneExporter = StandaloneExporter(self)
        self.saved = False  #if the project has been saved at all

        self.fMoveCamera = False

        self.NPParent = render

        # define your own config file in inherited class
        self.settingsFile = None

        # you can show/hide specific properties by using propertiesMask and this mode
        self.mode = BitMask32()
        
        self.tempDir = None
        
        self.manipMode = 'translate'
        
        groundRay = CollisionNode('groundRay')
        groundRay.addSolid(CollisionRay(Point3(0,0,0), Vec3(0,0,-1)))
        groundRay.setFromCollideMask(BitMask32.allOn())
        self.groundCollide = render.attachNewNode(groundRay)
        self.groundCollideHandler = CollisionHandlerQueue()
        self.groundCollideTraverser = CollisionTraverser()
        self.groundCollideTraverser.addCollider(self.groundCollide, self.groundCollideHandler)
        
        
    
    def initialize(self):
        """ You should call this in your __init__ method of inherited LevelEditor class """
        # specifiy what obj can be 'selected' as objects
        base.direct.selected.addTag('OBJRoot')

        self.actionEvents.extend([
            # Node path events
            ('DIRECT-select', self.select),
            ('DIRECT-delete', self.handleDelete),
            ('DIRECT-preDeselectAll', self.deselectAll),
            ('DIRECT_deselectAll', self.deselectAllCB),
            ('preRemoveNodePath', self.removeNodePathHook),
            ('DIRECT_deselectedNodePath', self.deselectAllCB),
            ('DIRECT_selectedNodePath_fMulti_fTag_fLEPane', self.selectedNodePathHook),
            ('DIRECT_deselectAll', self.deselectAll),
            ('LE-Undo', self.actionMgr.undo),
            ('LE-Redo', self.actionMgr.redo),
            ('LE-Duplicate', self.ui.onDuplicate),
            ('DIRECT_manipulateObjectCleanup', self.cleanUpManipulating),
            #('LE-MakeLive', self.objectMgr.makeSelectedLive),
            ('LE-NewScene', self.ui.onNew),
            ('LE-SaveScene', self.ui.onSave),
            ('LE-OpenScene', self.ui.onOpen),
            ('LE-Import', self.ui.onImport),
            ('LE-Quit', self.ui.quit),
            ('DIRECT-mouse1', self.handleMouse1),
            ('DIRECT-mouse1Up', self.handleMouse1Up),
            ('DIRECT-mouse2', self.handleMouse2),
            ('DIRECT-mouse2Up', self.handleMouse2Up),
            ('DIRECT-mouse3', self.handleMouse3),
            ('DIRECT-mouse3Up', self.handleMouse3Up),
            ('LE-translateMode', self.translateMode),
            ('LE-rotateMode', self.rotateMode),
            ('LE-scaleMode', self.scaleMode),
            ('LE-localMode', self.localMode),
            ('LE-worldMode', self.worldMode),
            ('LE-DropToGround', self.onDropToGround),
            ('LE-lookAtSelected', self.lookAtSelected),
            ('LE-moveCameraToSelected', self.moveCameraToSelected),
            ('LE-moveAllCamerasToSelected', self.moveAllCamerasToSelected),
            ])

        # Add all the action events
        for event in self.actionEvents:
            if len(event) == 3:
                self.accept(event[0], event[1], event[2])
            else:
                self.accept(event[0], event[1])        

        # editor state text display such as edit mode
        self.statusReadout = OnscreenText(
            pos = (-1.2, 0.9), bg=Vec4(1,1,1,1),
            scale = 0.05, align = TextNode.ALeft,
            mayChange = 1, font = TextNode.getDefaultFont())
        self.statusReadout.setText("")
        # Make sure readout is never lit or drawn in wireframe
        useDirectRenderStyle(self.statusReadout)
        self.statusReadout.reparentTo(hidden)
        self.statusLines = []
        taskMgr.doMethodLater(5, self.updateStatusReadoutTimeouts, 'updateStatus')
        taskMgr.add(self.updateShaders, 'updateShaders')

        self.loadSettings()
        self.reset()
        self.newProj()
        
        self.resetWidgets()
        base.direct.manipulationControl.useSeparateScaleHandles = True
        base.direct.cameraControl.switchDirBelowZero = False
        
        #self.defaultColor = BGC_LIGHT_BLUE
        self.setBackgroundColor(BGC_LIGHT_BLUE)
        
        
    
    #opens a new project in the temp directory
    def newProj(self):
        if self.tempDir and os.path.exists(self.tempDir):
            shutil.rmtree(self.tempDir)
        self.tempDir = os.path.join(Util.getTempDir(), 'NewProj')
        if os.path.exists(self.tempDir):
            for root, dirs, files in os.walk(self.tempDir):
                for f in files:
                    file = os.path.join(root, f)
                    fileAtt = os.stat(file)[0]
                    if (not fileAtt & stat.S_IWRITE):
                        os.chmod(file, stat.S_IWRITE)
                    
            shutil.rmtree(self.tempDir)
        
        projFile = Filename.fromOsSpecific(self.tempDir) + '/New Project.proj'
        self.currentProj = Project(projFile, "New Project")
        #defaultSceneName = "default"
        #self.currentProj.addScene(defaultSceneName, 
        #                          Filename(defaultSceneName+'.scene'))#Filename(projFile.getBasenameWoExtension() + '.scene'))
        #current Scene that the objectMgr manages and saves to
        #self.currentScene = self.currentProj.sceneFilename
        self.currentSceneName = self.currentProj.sceneName
        self.ui.scenesUI.populateTreeFromScenes()#add(defaultSceneName)
        self.projDir = self.currentProj.dir
        self.lib = self.currentProj.lib
        self.saved = False
        self.ui.libraryUI.update()
        self.ui.storyObjUI.update()
        self.ui.soundUI.update()
    
    def setTitleWithFilename(self, filename=""):
        title = self.ui.appname
        if filename != "":
           filenameshort = os.path.basename(filename)
           title = title + " (%s)"%filenameshort
        self.ui.SetLabel(title)

    def removeNodePathHook(self, nodePath):
        if nodePath is None:
            return
        base.direct.deselect(nodePath)
        self.objectMgr.removeObjectByNodePath(nodePath)

        if (base.direct.selected.last != None and nodePath.compareTo(base.direct.selected.last)==0):
            # if base.direct.selected.last is refering to this
            # removed obj, clear the reference
            if (hasattr(__builtins__,'last')):
                __builtins__.last = None
            else:
                __builtins__['last'] = None
            base.direct.selected.last = None

    def handleMouse1(self, modifiers):
        if base.direct.fAlt or modifiers == 4:
            self.fMoveCamera = True
            return

    def handleMouse1Up(self):
        self.fMoveCamera = False
        
        base.direct.fAlt = wx.GetKeyState(wx.WXK_ALT)
        base.direct.fControl = wx.GetKeyState(wx.WXK_CONTROL)
        base.direct.fShift = wx.GetKeyState(wx.WXK_SHIFT)

    def handleMouse2(self, modifiers):
        if base.direct.fAlt or modifiers == 4:
            self.fMoveCamera = True
            return

    def handleMouse2Up(self):
        self.fMoveCamera = False
        
        base.direct.fAlt = wx.GetKeyState(wx.WXK_ALT)
        base.direct.fControl = wx.GetKeyState(wx.WXK_CONTROL)
        base.direct.fShift = wx.GetKeyState(wx.WXK_SHIFT)
        
    def handleMouse3(self, modifiers):
        if base.direct.fAlt or modifiers == 4:
            self.fMoveCamera = True
            return

        self.ui.onRightDown()

    def handleMouse3Up(self):
        self.fMoveCamera = False
        
        base.direct.fAlt = wx.GetKeyState(wx.WXK_ALT)
        base.direct.fControl = wx.GetKeyState(wx.WXK_CONTROL)
        base.direct.fShift = wx.GetKeyState(wx.WXK_SHIFT)

    def handleDelete(self):
        oldSelectedNPs = base.direct.selected.getSelectedAsList()
        oldUIDs = []
        for oldNP in oldSelectedNPs:
            obj = self.objectMgr.findObjectByNodePath(oldNP)
            if obj:
                oldUIDs.append(obj.getName())
        action = ActionDeleteObj(self)
        self.actionMgr.push(action)
        action()

##         reply = wx.MessageBox("Do you want to delete selected?", "Delete?",
##                               wx.YES_NO | wx.ICON_QUESTION)
##         if reply == wx.YES:
##             base.direct.removeAllSelected()
##         else:
##             # need to reset COA
##             dnp = base.direct.selected.last
##             # Update camera controls coa to this point
##             # Coa2Camera = Coa2Dnp * Dnp2Camera
##             mCoa2Camera = dnp.mCoa2Dnp * dnp.getMat(base.direct.camera)
##             row = mCoa2Camera.getRow(3)
##             coa = Vec3(row[0], row[1], row[2])
##             base.direct.cameraControl.updateCoa(coa)

    def translateMode(self, evt=None):
        self.manipMode = 'translate'
        self.resetWidgets()

        self.ui.translateMenuItem.Check()
        
    def rotateMode(self, evt=None):
        self.manipMode = 'rotate'
        self.resetWidgets()
        
        self.ui.rotateMenuItem.Check()
    
    def scaleMode(self, evt=None):
        self.manipMode = 'scale'
        self.resetWidgets()
        
        self.ui.scaleMenuItem.Check()
    
    def worldMode(self, evt=None):
        base.direct.manipulationControl.switchToWorldSpaceMode()
        self.ui.worldMenuItem.Check()
    
    def localMode(self, evt=None):
        base.direct.manipulationControl.switchToLocalSpaceMode()
        self.ui.localMenuItem.Check()
     
    def showWidget(self):
        for widget in base.direct.manipulationControl.widgetList:
            widget.activate()
    
    def hideWidget(self):
        for widget in base.direct.manipulationControl.widgetList:
            widget.deactivate()
     
    def resetWidgets(self):
        for widget in base.direct.manipulationControl.widgetList:
            widget.disableHandles('all')
            if self.manipMode == 'translate':
                widget.enableHandles('post')
            elif self.manipMode == 'rotate':
                widget.enableHandles('ring')
            elif self.manipMode == 'scale':
                widget.enableHandles('scale')

    #makes the camera look at the center of teh bounding box of whatever is selected
    def lookAtSelected(self):
        selected = base.direct.selected.getSelectedAsList()
        if selected:
            bounds = BoundingBox()
            for np in selected:
                b = np.getBounds()
                b.xform(np.getParent().getMat(render))
                bounds.extendBy(b)      
        else:
            bounds = BoundingBox()
            for obj in self.objectMgr.objects.values():
                np = obj.nodePath
                b = np.getBounds()
                b.xform(np.getParent().getMat(render))
                bounds.extendBy(b)
        if bounds.isEmpty() or bounds.isInfinite():
            center = Point3(0, 0, 0)
        else:
            center = Point3((bounds.getMax() + bounds.getMin()) / 2.0)
        
        np = NodePath('temp')
        np.setPos(self.ui.perspView.camera.getPos())
        np.lookAt(center)
        i = LerpHprInterval(self.ui.perspView.camera, 1.0, np.getHpr(), blendType='easeInOut')
        i.start()
        base.direct.cameraControl.coaMarkerPos.assign(center)
        np.removeNode()
    
    #moves the camera to the outside of the bounding box of whatever is selected and looks at it
    def moveCameraToSelected(self):
        selected = base.direct.selected.getSelectedAsList()
        if selected:
            bounds = BoundingBox()
            for np in selected:
                b = np.getBounds()
                b.xform(np.getParent().getMat(render))
                bounds.extendBy(b)      
        else:
            bounds = BoundingBox()
            for obj in self.objectMgr.objects.values():
                np = obj.nodePath
                b = np.getBounds()
                b.xform(np.getParent().getMat(render))
                bounds.extendBy(b)
        
        if bounds.isEmpty() or bounds.isInfinite():
            center = Point3(0, 0, 0)
            targetPos = Point3(-19, -19, 19)
        else:
            center = Point3((bounds.getMax() + bounds.getMin()) / 2.0)
            diff = self.ui.perspView.camera.getPos() - center
            diff.normalize()
            targetPos = center + diff * (bounds.getMax() - bounds.getMin()).length() * 1.8
        
        np = NodePath('temp')
        np.setPos(targetPos)
        np.lookAt(center)
        i = LerpPosHprInterval(self.ui.perspView.camera, 1, targetPos, np.getHpr(), blendType='easeInOut')
        i.start()
        base.direct.cameraControl.coaMarkerPos.assign(center)
        np.removeNode()
    
    #moves all cameras(perspective and the 3 ortho cameras) to focus on the selected object
    def moveAllCamerasToSelected(self):
        selected = base.direct.selected.getSelectedAsList()
        if selected:
            bounds = BoundingBox()
            for np in selected:
                b = np.getBounds()
                b.xform(np.getParent().getMat(render))
                bounds.extendBy(b)        
        else:
            bounds = BoundingBox()
            for obj in self.objectMgr.objects.values():
                np = obj.nodePath
                b = np.getBounds()
                b.xform(np.getParent().getMat(render))
                bounds.extendBy(b)
        
        #perspective
        if bounds.isEmpty() or bounds.isInfinite():
                center = Point3(0, 0, 0)
                targetPos = Point3(-19, -19, 19)
        else:
            center = Point3((bounds.getMax() + bounds.getMin()) / 2.0)
            diff = self.ui.perspView.camera.getPos() - center
            diff.normalize()
            targetPos = center + diff * (bounds.getMax() - bounds.getMin()).length() * 1.8
        
        np = NodePath('temp')
        np.setPos(targetPos)
        np.lookAt(center)
        i = LerpPosHprInterval(self.ui.perspView.camera, 1, targetPos, np.getHpr(), blendType='easeInOut')
        i.start()
        base.direct.cameraControl.coaMarkerPos.assign(center)
        np.removeNode()
        
        #top
        if bounds.isEmpty() or bounds.isInfinite():
            targetPos = Point3(0, 0, 600)
            base.direct.drList[base.camList.index(NodePath(self.ui.topView.camNode))].orthoFactor = 0.1
            
        else:
            targetPos = Point3((bounds.getMax().getX() + bounds.getMin().getX()) / 2.0, (bounds.getMax().getY() + bounds.getMin().getY()) / 2.0, bounds.getMax().getZ() + 600)
            size = max( (bounds.getMax().getX() - bounds.getMin().getX()), (bounds.getMax().getY() - bounds.getMin().getY()))
            base.direct.drList[base.camList.index(NodePath(self.ui.topView.camNode))].orthoFactor = size / min(self.ui.topView.ClientSize.GetWidth(), self.ui.topView.ClientSize.GetHeight() )
            
        x = self.ui.topView.ClientSize.GetWidth() * base.direct.drList[base.camList.index(NodePath(self.ui.topView.camNode))].orthoFactor
        y = self.ui.topView.ClientSize.GetHeight() * base.direct.drList[base.camList.index(NodePath(self.ui.topView.camNode))].orthoFactor
        i = LerpFunc(self.orthoPosFilmSizeInterval, extraArgs=[self.ui.topView.camera, self.ui.topView.camLens, self.ui.topView.camera.getPos(), targetPos,\
        self.ui.topView.camLens.getFilmSize().getX(), x, self.ui.topView.camLens.getFilmSize().getY(), y], blendType = 'noBlend', duration=1)
        i.start()
        
        #right
        if bounds.isEmpty() or bounds.isInfinite():
            targetPos = Point3(600, 0, 0)
            base.direct.drList[base.camList.index(NodePath(self.ui.leftView.camNode))].orthoFactor = 0.1
            
        else:
            targetPos = Point3(bounds.getMax().getX() + 600, (bounds.getMax().getY() + bounds.getMin().getY()) / 2.0, (bounds.getMax().getZ() + bounds.getMin().getZ()) / 2.0)
            size = max( (bounds.getMax().getY() - bounds.getMin().getY()), (bounds.getMax().getZ() - bounds.getMin().getZ()))
            base.direct.drList[base.camList.index(NodePath(self.ui.leftView.camNode))].orthoFactor = size / min(self.ui.leftView.ClientSize.GetWidth(), self.ui.leftView.ClientSize.GetHeight() )
            
        x = self.ui.leftView.ClientSize.GetWidth() * base.direct.drList[base.camList.index(NodePath(self.ui.leftView.camNode))].orthoFactor
        y = self.ui.leftView.ClientSize.GetHeight() * base.direct.drList[base.camList.index(NodePath(self.ui.leftView.camNode))].orthoFactor
        i = LerpFunc(self.orthoPosFilmSizeInterval, extraArgs=[self.ui.leftView.camera, self.ui.leftView.camLens, self.ui.leftView.camera.getPos(), targetPos,\
        self.ui.leftView.camLens.getFilmSize().getX(), x, self.ui.leftView.camLens.getFilmSize().getY(), y], blendType = 'noBlend', duration=1)
        i.start()
        
        #front
        if bounds.isEmpty() or bounds.isInfinite():
            targetPos = Point3(0, -600, 0)
            base.direct.drList[base.camList.index(NodePath(self.ui.frontView.camNode))].orthoFactor = 0.1
            
        else:
            targetPos = Point3((bounds.getMax().getX() + bounds.getMin().getX()) / 2.0, bounds.getMin().getY() - 600, (bounds.getMax().getZ() + bounds.getMin().getZ()) / 2.0)
            size = max( (bounds.getMax().getX() - bounds.getMin().getX()), (bounds.getMax().getZ() - bounds.getMin().getZ()))
            base.direct.drList[base.camList.index(NodePath(self.ui.frontView.camNode))].orthoFactor = size / min(self.ui.frontView.ClientSize.GetWidth(), self.ui.frontView.ClientSize.GetHeight() )
            
        x = self.ui.frontView.ClientSize.GetWidth() * base.direct.drList[base.camList.index(NodePath(self.ui.frontView.camNode))].orthoFactor
        y = self.ui.frontView.ClientSize.GetHeight() * base.direct.drList[base.camList.index(NodePath(self.ui.frontView.camNode))].orthoFactor
        i = LerpFunc(self.orthoPosFilmSizeInterval, extraArgs=[self.ui.frontView.camera, self.ui.frontView.camLens, self.ui.frontView.camera.getPos(), targetPos,\
        self.ui.frontView.camLens.getFilmSize().getX(), x, self.ui.frontView.camLens.getFilmSize().getY(), y], blendType = 'noBlend', duration=1)
        i.start()
        
            
    def orthoPosFilmSizeInterval(self, t, camera, camLens, beginPos, endPos, beginX, endX, beginY, endY):
        camera.setPos(beginPos * (1-t) + endPos * t)
        camLens.setFilmSize(beginX * (1-t) + endX * t, beginY * (1-t) + endY * t)
        
    def cleanUpManipulating(self, selectedNPs):
        for np in selectedNPs:
            obj = self.objectMgr.findObjectByNodePath(np)
            if obj and np.getMat() != self.objectMgr.objectsLastXform[obj.getName()]:
                action = ActionTransformObj(self, obj.getName(), Mat4(np.getMat()))
                self.actionMgr.push(action)
                action()

    def select(self, nodePath, fMultiSelect=0, fSelectTag=1, fResetAncestry=1, fLEPane=0, fUndo=1):
        base.direct.toggleWidgetVis()
        if fUndo:
            # Select tagged object if present
            if fSelectTag:
                for tag in base.direct.selected.tagList:
                    if nodePath.hasNetTag(tag):
                        nodePath = nodePath.findNetTag(tag)
                        break
            action = ActionSelectObj(self, nodePath, fMultiSelect=fMultiSelect, fSelectTag=fSelectTag, fResetAncestry=fResetAncestry,fLEPane=fLEPane)
            self.actionMgr.push(action)
            action()
        else:
            base.direct.selectCB(nodePath, fMultiSelect, fSelectTag, fResetAncestry, fLEPane, fUndo)
            
        if base.direct.selected.getSelectedAsList:
            self.showWidget()

    def selectedNodePathHook(self, nodePath, fMultiSelect = 0, fSelectTag = 1, fLEPane = 0):
        # handle unpickable nodepath
        if nodePath.getName() in base.direct.iRay.unpickable:
            base.direct.deselect(nodePath)
            return

        if fMultiSelect == 0 and fLEPane == 0:
           oldSelectedNPs = base.direct.selected.getSelectedAsList()
           for oldNP in oldSelectedNPs:
              obj = self.objectMgr.findObjectByNodePath(oldNP)
              if obj:
                 self.ui.sceneGraphUI.deSelect(obj.getName())
        self.objectMgr.selectObject(nodePath, fLEPane, fMultiSelect)
        self.ui.buildContextMenu(nodePath)
        
        
    def deselectAll(self, np=None):
        self.hideWidget()
        self.objectMgr.deselectAll()
        if len(base.direct.selected.getSelectedAsList()) ==0:
            return
        action = ActionDeselectAll(self)
        self.actionMgr.push(action)
        action()

    def deselectAllCB(self, dnp=None):
        if not dnp:
            self.objectMgr.deselectAll()
            self.editor.ui.sceneGraphUI.tree.UnselectAll()
        else:
            obj = self.objectMgr.findObjectByNodePath(dnp)
            if obj:
                self.ui.sceneGraphUI.deSelect(obj.name)
        
    def reset(self, resetViews=True):
        if self.fNeedToSave:
            reply = wx.MessageBox("Do you want to save the current project?", "Save?",
                               wx.YES_NO | wx.ICON_QUESTION)
            if reply == wx.YES:
                result = self.ui.onSave()
                if result == False:
                    return

        base.direct.deselectAll()
        self.ui.reset()
        self.objectMgr.reset()
        self.actionMgr.reset()
        self.soundMgr.reset()
        self.journalMgr.reset()
        self.inventoryMgr.reset()
        if resetViews:
            self.ui.perspView.camera.setPos(-19, -19, 19)
            self.ui.perspView.camera.lookAt(Point3(0, 0, 0))
            self.ui.leftView.camera.setPos(600, 0, 0)
            self.ui.frontView.camera.setPos(0, -600, 0)
            self.ui.topView.camera.setPos(0, 0, 600)
            self.resetOrthoCam(self.ui.topView)
            self.resetOrthoCam(self.ui.frontView)
            self.resetOrthoCam(self.ui.leftView)
        self.fNeedToSave = False
        self.setTitleWithFilename()
    
    def resetScene(self):
        if self.fNeedToSave:
            reply = wx.MessageBox("With Switching Scenes you will lose the previous Scene.\n Do you want to save the current project?", "Save?",
                               wx.YES_NO | wx.ICON_QUESTION)
            if reply == wx.YES:
                result = self.ui.onSave()
                if result == False:
                    return
        base.direct.deselectAll()
        self.objectMgr.reset()
        self.actionMgr.reset()
        self.soundMgr.reset()# May not reset this
        self.fNeedToSave = False
        self.setTitleWithFilename()
        
        
        
    def resetOrthoCam(self, view):
        base.direct.drList[base.camList.index(NodePath(view.camNode))].orthoFactor = 0.1
        x = view.ClientSize.GetWidth() * 0.1
        y = view.ClientSize.GetHeight() * 0.1
        view.camLens.setFilmSize(x, y)
        
    def save(self):
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        #check to make sure everything is writable
        try:
            f = open(self.currentProj.filename.toOsSpecific(), 'a')
            f.close()
        except IOError as e:
            dlg = wx.MessageDialog(self.ui, "The project file " +\
            " could not be written.  Make sure it is not marked read-only and try again",\
            caption = "Save Error", style=wx.ICON_ERROR|wx.OK)
            dlg.ShowModal()
            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            return
            
        try:
            f = open((self.projDir + '/' + self.currentProj.getScene(self.currentSceneName).getFullpath()).toOsSpecific(), 'a')
            f.close()
        except IOError as e:
            dlg = wx.MessageDialog(self.ui, "The scene file "  +\
            " could not be written.  Make sure it is not marked read-only and try again",\
            caption = "Save Error", style=wx.ICON_ERROR|wx.OK)
            dlg.ShowModal()
            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            return
            
        try:
            f = open((self.projDir + '/' + 'lib.index').toOsSpecific(), 'a')
            f.close()
        except IOError as e:
            dlg = wx.MessageDialog(self.ui, "The library index file " +\
            " could not be written.  Make sure it is not marked read-only and try again",\
            caption = "Save Error", style=wx.ICON_ERROR|wx.OK)
            dlg.ShowModal()
            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            return
        
        try:
            f = open((self.projDir + '/' +  self.currentProj.journalFilename.getFullpath()).toOsSpecific(), 'a')
            f.close()
        except IOError as e:
            dlg = wx.MessageDialog(self.ui, "The journal file " +\
            " could not be written.  Make sure it is not marked read-only and try again",\
            caption = "Save Error", style=wx.ICON_ERROR|wx.OK)
            dlg.ShowModal()
            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            return
        
        self.currentProj.saveToFile()
        self.fileMgr.saveToFile(self.projDir + '/' + self.currentProj.getScene(self.currentSceneName).getFullpath())
        self.fileMgr.saveJournalToFile(self.projDir+'/'+self.currentProj.journalFilename.getFullpath())
        self.fileMgr.saveInventoryMapToFile(self.projDir+'/'+self.currentProj.inventoryMapFilename.getFullpath())
        self.lib.saveToFile()
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def saveAs(self, fileName, projName):
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.currentProj.saveAs(fileName, projName, self.saved)
        self.tempDir = None
        self.projDir = self.currentProj.dir
        self.fileMgr.saveToFile(self.projDir + '/' + self.currentProj.getScene(self.currentSceneName).getFullpath())
        self.fileMgr.saveJournalToFile(self.projDir+'/'+self.currentProj.journalFilename.getFullpath())
        self.fileMgr.saveInventoryMapToFile(self.projDir+'/'+self.currentProj.inventoryMapFilename.getFullpath())
        self.saved = True
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
#    def createSceneFile(self,sceneFile):
#        try:
#            f = open((self.projDir + '/' + sceneFile.getFullpath()).toOsSpecific(), 'a')
#            f.close()
#        except IOError as e:
#            dlg = wx.MessageDialog(self.ui, "The scene file "  +\
#            " could not be written.  Make sure it is not marked read-only and try again",\
#            caption = "Save Error", style=wx.ICON_ERROR|wx.OK)
#            dlg.ShowModal()
#            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
#            return

    def load(self, fileName, resetViews=True, setSaved=True):
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.reset(resetViews=resetViews)
        self.currentProj = Project(fileName)
        self.projDir = self.currentProj.dir
        self.lib = self.currentProj.lib
        
        #make sure we get updated versions of assets
        ModelPool.releaseAllModels()
        TexturePool.releaseAllTextures()
        ShaderPool.releaseAllShaders()
        
        self.currentSceneName = self.currentProj.sceneName
        self.fileMgr.loadFromFile(self.projDir + '/' +self.currentProj.getScene(self.currentSceneName).getFullpath())
        self.fileMgr.loadJournalFromFile(self.projDir+'/'+self.currentProj.journalFilename.getFullpath())
        self.fileMgr.loadInventoryMapFromFile(self.projDir+'/'+self.currentProj.inventoryMapFilename.getFullpath())
        if setSaved:
            self.saved = True
        
        #self.currenScene = self.currentProj.sceneFilename
        self.ui.scenesUI.populateTreeFromScenes()
        
        self.objectMgr.updateMainCharWidget() #[antonjs 4/14/11]
        
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    #Cosider to change merging projects: Maybe just merging scenes?
    def mergeProject(self, fileName, prefix='', newNodeName= ''):
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        otherProj = Project(fileName)
        if not prefix:
            prefix = otherProj.name
        try:
            self.lib.checkLibrary(otherProj.lib, prefix)
        except Exception as e:
            print 'ERROR:Could not merge libraries'
            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            raise e
            return
            
        self.lib.mergeWith(otherProj.lib, prefix, saveAfter=True)
        try:
            self.fileMgr.loadFromFile(otherProj.dir + '/' + otherProj.scenes[otherProj.sceneName].getFullpath(), merge=True, lib=otherProj.lib, otherName=prefix, newNodeName= newNodeName)
        except Util.SceneMergeError as e:
            print 'ERROR:could not merge scenes'
            self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            traceback.print_exc(file=sys.stdout)
            return
        
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self.ui.libraryUI.update()
        self.ui.storyObjUI.update()
        self.ui.soundUI.update()
        self.objectMgr.updateMainCharWidget() #[antonjs 4/14/11]
        
        self.fNeedToSave = True
        
    def saveSettings(self):
        if self.settingsFile is None:
            return
        
        try:
            f = open(self.settingsFile, 'w')
            f.write('gridSize\n%f\n'%self.ui.perspView.grid.gridSize)
            f.write('gridSpacing\n%f\n'%self.ui.perspView.grid.gridSpacing)
            f.write('hotKey\n%s\n'%base.direct.hotKeyMap)
            f.close()
        except:
            pass        

    def loadSettings(self):
        base.direct.hotKeyMap = {   
            'control-y': ('Redo', 'LE-Redo'),
            'shift-v': ('Toggle Marker', 'DIRECT-toggleMarkerVis'),
            'control-n': ('New Scene', 'LE-NewScene'),
            'control-s': ('Save Scene', 'LE-SaveScene'),
            'escape': ('Deselect All', 'deselectAll'),
            'control-z': ('Undo', 'LE-Undo'),
            ',': ('Scale Down Widget', 'DIRECT-widgetScaleDown'),
            '.': ('Scale Up Widget', 'DIRECT-widgetScaleUp'),
            'control-o': ('Open Scene', 'LE-OpenScene'),
            'control-q': ('Quit', 'LE-Quit'),
            'control-i': ('Import', 'LE-Import'),
            # 'b': ('Toggle Backface', 'DIRECT-toggleBackface'),
            #'f': ('Fit on Widget', 'DIRECT-fitOnWidget'),
            # 't': ('Toggle Textures', 'DIRECT-toggleTexture'),
            't': ('Toggle Wireframe', 'DIRECT-toggleWireframe'),
            'f' : ('Look at Selected', 'LE-lookAtSelected'),
            'c' : ('Move Camera to Selected', 'LE-moveCameraToSelected'),
            'shift-c' : ('Move All Cameras to Selected', 'LE-moveAllCamerasToSelected'),
            'w': ('Enter Translate Mode', 'LE-translateMode'),
            'e': ('Enter Rotate Mode', 'LE-rotateMode'),
            'r': ('Enter Scale Mode', 'LE-scaleMode'),
            'delete': ('Delete', 'DIRECT-delete'),
            'control-g': ('Drop Selected to Ground', 'LE-DropToGround'),
            'control-d': ('Duplicate', 'LE-Duplicate')}
        
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        try:
            f = open(self.settingsFile, 'r')
            configLines = f.readlines()
            f.close()

            gridSize = 100.0
            gridSpacing = 5.0
            for i in range(0, len(configLines)):
                line = configLines[i]
                i = i + 1
                if line.startswith('gridSize'):
                    gridSize = float(configLines[i])
                elif line.startswith('gridSpacing'):
                    gridSpacing = float(configLines[i])
                elif line.startswith('hotKey'):
                    customHotKeyMap = eval(configLines[i])
                    customHotKeyDict = {}
                    for hotKey in customHotKeyMap.keys():
                        desc = customHotKeyMap[hotKey]
                        customHotKeyDict[desc[1]] = hotKey

                    overriddenKeys = []
                    for key in base.direct.hotKeyMap.keys():
                        desc = base.direct.hotKeyMap[key]
                        if desc[1] in customHotKeyDict.keys():
                            overriddenKeys.append(key)

                    for key in overriddenKeys:
                        del base.direct.hotKeyMap[key]
                            
                    base.direct.hotKeyMap.update(customHotKeyMap)

            self.ui.updateGrids(gridSize, gridSpacing)
            self.ui.updateMenu()
        except:
            base.direct.hotKeyMap = {   
            'control-y': ('Redo', 'LE-Redo'),
            'shift-v': ('Toggle Marker', 'DIRECT-toggleMarkerVis'),
            'control-n': ('New Scene', 'LE-NewScene'),
            'control-s': ('Save Scene', 'LE-SaveScene'),
            'escape': ('Deselect All', 'deselectAll'),
            'control-z': ('Undo', 'LE-Undo'),
            ',': ('Scale Down Widget', 'DIRECT-widgetScaleDown'),
            '.': ('Scale Up Widget', 'DIRECT-widgetScaleUp'),
            'control-o': ('Open Scene', 'LE-OpenScene'),
            'control-q': ('Quit', 'LE-Quit'),
            'control-i': ('Import', 'LE-Import'),
            # 'b': ('Toggle Backface', 'DIRECT-toggleBackface'),
            #'f': ('Fit on Widget', 'DIRECT-fitOnWidget'),
            # 't': ('Toggle Textures', 'DIRECT-toggleTexture'),
            't': ('Toggle Wireframe', 'DIRECT-toggleWireframe'),
            'f' : ('Look at Selected', 'LE-lookAtSelected'),
            'c' : ('Move Camera to Selected', 'LE-moveCameraToSelected'),
            'shift-c' : ('Move All Cameras to Selected', 'LE-moveAllCamerasToSelected'),
            'w': ('Enter Translate Mode', 'LE-translateMode'),
            'e': ('Enter Rotate Mode', 'LE-rotateMode'),
            'r': ('Enter Scale Mode', 'LE-scaleMode'),
            'g': ('Switch to World Space Manipulation', 'LE-worldMode'),
            'l': ('Switch to Local Space Manipulation', 'LE-localMode'),
            'delete': ('Delete', 'DIRECT-delete'),
            'control-g': ('Drop Selected to Ground', 'LE-DropToGround'),
            'control-d': ('Duplicate', 'LE-Duplicate')}
            self.ui.updateMenu()
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def convertMaya(self, modelname, callBack, obj=None, isAnim=False):
        if obj and isAnim:
            mayaConverter = MayaConverter(self.ui, self, modelname, callBack, obj, isAnim)
        else:
            reply = wx.MessageBox("Is it an animation file?", "Animation?",
                              wx.YES_NO | wx.ICON_QUESTION)
            if reply == wx.YES:
                mayaConverter = MayaConverter(self.ui, self, modelname, callBack, None, True)
            else:        
                mayaConverter = MayaConverter(self.ui, self, modelname, callBack, None, False)
        mayaConverter.Show()

    def convertFromMaya(self, modelname, callBack):
        mayaConverter = MayaConverter(self.ui, self, modelname, callBack, None, False)
        mayaConverter.Show()

    def updateStatusReadout(self, status, color=None):
        if status:
            # add new status line, first check to see if it already exists
            alreadyExists = False
            for currLine in self.statusLines:
                if (status == currLine[1]):
                    alreadyExists = True
                    break
            if (alreadyExists == False):
                time = globalClock.getRealTime() + 15
                self.statusLines.append([time,status,color])

        # update display of new status lines
        self.statusReadout.reparentTo(aspect2d)
        statusText = ""
        lastColor = None
        for currLine in self.statusLines:
            statusText += currLine[1] + '\n'
            lastColor = currLine[2]
        self.statusReadout.setText(statusText)
        if (lastColor):
            self.statusReadout.textNode.setCardColor(
                lastColor[0], lastColor[1], lastColor[2], lastColor[3])
            self.statusReadout.textNode.setCardAsMargin(0.1, 0.1, 0.1, 0.1)
        else:
            self.statusReadout.textNode.setCardColor(1,1,1,1)
            self.statusReadout.textNode.setCardAsMargin(0.1, 0.1, 0.1, 0.1)
            
    def updateStatusReadoutTimeouts(self,task=None):
        removalList = []
        for currLine in self.statusLines:
            if (globalClock.getRealTime() >= currLine[0]):
                removalList.append(currLine)
        for currRemoval in removalList:
            self.statusLines.remove(currRemoval)
        self.updateStatusReadout(None)
        # perform doMethodLater again after delay
        # This crashes when CTRL-C'ing, so this is a cheap hack.
        #return 2
        from direct.task import Task
        return Task.again

    def updateShaders(self, task):
        for obj in self.objectMgr.objects.values():
            if obj.shader and obj.shaderActive:
                obj.shader.update()
        return task.cont
        
    def propMeetsReq(self, typeName, parentNP):
        parentNP[0] = None
        return True
    
    def onDropToGround(self, evt=None):
        action = ActionDropSelectedToGround(self)
        self.actionMgr.push(action)
        action()
    
    def dropSelectedToGround(self):
        selected = base.direct.selected.getSelectedAsList()
        toDrop = set(selected)
        
        origParents = {}
        
        for np in toDrop:
            for otherNP in toDrop:
                if np != otherNP and otherNP.isAncestorOf(np):
                    origParents[np] = np.getParent()
                    np.wrtReparentTo(render)
                    break

        for np in toDrop:
            self.dropToGround(np)
                    
        for np, parent in origParents.iteritems():
            np.wrtReparentTo(parent)
            
    def dropToGround(self, np):
        self.groundCollide.setPos(np.getPos(render))
        
        self.groundCollideTraverser.traverse(render)
        
        if self.groundCollideHandler.getNumEntries() > 0:
            self.groundCollideHandler.sortEntries()
            for e in self.groundCollideHandler.getEntries():
                hitNP = e.getIntoNodePath()
                if hitNP.hasNetTag('OBJRoot'):
                    hitObj = hitNP.findNetTag('OBJRoot')
                    if hitObj.hasTag('LE-ground'):
                        np.setZ(render, e.getSurfacePoint(render).getZ())
                        return
    
        
                    
    def openScene(self, sceneName):
        self.ui.sceneGraphUI.reset()
        self.ui.soundUI.reset()
        sceneFile = self.currentProj.getScene(sceneName)
        #self.currentScene = sceneFile
        
        if(sceneName.strip().startswith("interior_")):
            self.setBackgroundColor(BGC_DARK_GREY)
        else:
            self.setBackgroundColor(BGC_LIGHT_BLUE)
        
        self.currentSceneName = sceneName
        f = Filename(sceneFile)
        f.setDirname(self.currentProj.dir.getFullpath())

        if os.path.exists(f.toOsSpecific()):
            self.fileMgr.loadFromFile(self.projDir + '/' +self.currentProj.getScene(self.currentSceneName).getFullpath())
        
        self.objectMgr.updateMainCharWidget() #[antonjs 4/14/11]
    
    def addScene(self):
        name, scenefile = self.currentProj.addScene()
        #create an empty sceneFile
        #cr
        doc = xml.dom.minidom.Document()
        root = doc.createElement("scene")
        doc.appendChild(root)
        root.appendChild(doc.createElement("objects"))
        root.appendChild(doc.createElement("layers"))
        root.appendChild(doc.createElement("sounds"))
        
        try:
            filename = self.projDir + '/' + scenefile.getFullpath()
            f = open(filename.toOsSpecific(), 'w')
            f.write(doc.toprettyxml())
            f.close()
        except IOError:
            raise SceneSaveError(filename.toOsSpecific())
        return name
        
    
    def removeScene(self, sceneName, delFile = False):
        toDelSceneFile = self.currentProj.getScene(sceneName)
        self.currentProj.removeScene(sceneName, delFile)
        #if the scene to remove the current Scene get the 
        if(self.currentSceneName == sceneName):
            self.openScene(self.currentProj.sceneName)
        #self.ui.onSave()
        #self.currentScene = self.currentProj.getOpeningScene()
        
        if(self.saved):
            self.save()
            
    def renameScene(self, name, newName):
        self.currentProj.renameScene(name,newName)
        if(self.currentSceneName == name):
            self.currentSceneName = newName
            if(newName.strip().startswith("interior_")):
                self.setBackgroundColor(BGC_DARK_GREY)
            else:
                self.setBackgroundColor(BGC_LIGHT_BLUE)
            
    def addEmptyTerrain(self):
        no = 0
        name =  self.currentSceneName+'_terrain'+str(no)
        tempFilePath = base.le.lib.projDir.toOsSpecific() + '/' + name+ '.png'
        assetFilename = Filename(tempFilePath)
        
        targetFilename = Filename(assetFilename)
        targetFilename.setDirname(self.currentProj.dir.getFullpath()+'/Textures')
        
        while os.path.exists(targetFilename.toOsSpecific()):
            no += 1
            tempFilePath = base.le.lib.projDir.toOsSpecific() + '/' + name+str(no)+ '.png'
            assetFilename = Filename(tempFilePath)
            targetFilename = Filename(assetFilename)
            targetFilename.setDirname(self.currentProj.dir.getFullpath()+'/Textures')
            
        
        tempImage = PNMImage(513,513)
        tempImage.fill(.5,.5,.5)
        tempImage.write(assetFilename)  
        
        no = 0
        #add the new terrain to the library
        asset = Terrain(name, assetFilename)
        while(1):
            try:
                base.le.lib.addTerrain(asset, True)
                break
            except:
                pass
                no += 1
                name =  self.currentSceneName+'_terrain'+str(no)
                #tempFilePath = base.le.lib.projDir.toOsSpecific() + '/' + name+ '.png'
                #assetFilename = Filename(tempFilePath)
                asset = Terrain(name, assetFilename)
            else:
                break
                        
        base.le.ui.libraryUI.update()
            
        #== Remove the temporary source file
        tempFilename = Filename(tempFilePath)
        #print 'temporary file path to now delete: ' + tempFilename.toOsSpecific()
        os.remove(tempFilename.toOsSpecific())
        
        pos = Vec3(512*(-.5), 512*(-.5), -128)            
        action = ActionAddNewObj(self, "Terrains", name = "terrain_"+name + ':1', asset=asset, anims={}, parent=None, pos=pos)
        self.actionMgr.push(action)
        newobj = action()
        newobj.getNodePath().setScale(1.,1.,255)
    
    #Color should a Vec4
    def setBackgroundColor(self, color):
        for i in range(4):
            base.winList[i].setClearColor(color)
        
        
        

            
        
