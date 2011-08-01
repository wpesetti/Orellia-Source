import wx
import os
import Util
import time
import math
import subprocess


from pandac.PandaModules import *
from direct.wxwidgets.ViewPort import *
from direct.directtools.DirectGlobals import *
from direct.directtools.DirectManipulation import ObjectHandles
from direct.showbase.DirectObject import DirectObject
from ActionMgr import *

import Debug

from wx import xrc

GUI_FILENAME = 'XRC/TerrainPaintUI.xrc'
LE_IMPORT_MASK = BitMask32.bit(4)
LE_IMPORT_MASK2 = BitMask32.bit(5)

LE_CAM_MASKS['terrain'] = LE_IMPORT_MASK

class TerrainPaintUI(wx.Dialog):
    def __init__(self, parent, editor, terrain):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(GUI_FILENAME)
        self.res.LoadOnDialog(pre, parent, 'dlgTerrainPaint')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.onCreate)
        
        self.parent = parent
        self.editor = editor
        self.terrain = terrain
        #self.oldCanvas = PNMImgae()
        #self.oldCanvas.copyFrom(terrain.heightField())
        self.brushRadius = 1
        self.viewport = None
        
        self.oldX = -1
        self.oldY = -1
        
        self.paintCursor = loader.loadModel("models/terrain_cursor.egg")#jack")
        self.paintRing = loader.loadModel("models/terrain_ring.egg")
        self.paintCursor.setScale(12)
        self.paintCursor.reparentTo(self.editor.NPParent)
        self.paintCursor.setPos(self.terrain.getNodePath().getPos())
        self.paintRing.reparentTo(self.editor.NPParent)
        self.paintRing.setPos(self.paintCursor.getPos())
        
        taskMgr.add(self.followMouseTask, "followMouseTask")
        self.customImage = PNMImage(32,32)
        self.customImage.read("full_white_square_gradiant_alpha.tif")
        self.raiseImageWithCustomImage()
        
        #TO DO:if no light check for later
        light = PointLight('Terrain Light')
        light.setColor(Vec4(1,1,1,1))
        self.light = self.editor.NPParent.attachNewNode(light)
        pos = self.terrain.getNodePath().getPos()
        self.light.setPos(Point3(0,0,pos[2]+240))
        self.terrain.getNodePath().setLight(self.light)#self.editor.NPParent.setLight(self.light)
        #self.editor.NPParent.setPoint(Point3(0,0, pos[2]+400))
        
        self.actionMgr = ActionMgr()
    
    def onCreate(self, evt):
        self.Unbind(wx.EVT_INIT_DIALOG)
        base.le.ui.bindKeyEvents(False)
        
        self.Show()
        self.Bind(wx.EVT_CLOSE, self.Close)
        
        #init all the panels from XRC for parenting later on
        self.notebook = xrc.XRCCTRL(self, "notebook_1")
        self.canvasPanel = xrc.XRCCTRL(self, "canvasPanel")
        self.texturePanel = xrc.XRCCTRL(self,"texturePanel")
        #self.setupWxPaint()
        
        #self.canvasPanel.Bind(wx.EVT_PAINT, self.onPaint)
        #self.canvasPanel.Bind(wx.EVT_LEFT_DOWN, self.onClick)
        
        
        #edit Panel
        self.btnUpdateTerrain =  xrc.XRCCTRL(self,"btnUpdateTerrain")
        self.sliderBrushSize = xrc.XRCCTRL(self, "sliderBrushSize")
        self.textCtrlBrushSize = xrc.XRCCTRL(self, "textCtrlBrushSize")
        self.sliderGrayScale = xrc.XRCCTRL(self, "sliderGrayScale")
        self.textCtrlGrayScale = xrc.XRCCTRL(self, "textCtrlGrayScale")
        self.paintModeRadioBox = xrc.XRCCTRL(self, 'paintModeRadioBox')
        self.paintModeRadioBox.Hide()
        
        self.Bind(wx.EVT_BUTTON, self.saveTerrain, self.btnUpdateTerrain)
        self.sliderGrayScale.Bind(wx.EVT_SCROLL_ENDSCROLL, self.onSliderEnd)
        self.sliderBrushSize.Bind(wx.EVT_SCROLL_ENDSCROLL, self.onSliderEnd)
        #self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChange)
        
        
        self.setupViewport(self.canvasPanel)
        #self.setupTextureViewport()
        self.setupCanvas()
        #self.canvasPanel.CaptureMouse()

    #TODEL
    def onPageChange(self, evt):
        #0 is heightmap
        #1 is texture
        selected = self.notebook.GetSelection()
        if(self.viewport):
            self.viewport.Close()
        if(selected == 0):
            self.setupViewport(self.canvasPanel)
        else:
            self.setupViewport(self.texturePanel)
            
    
    def followMouseTask(self, task):
        panel_pos = self.canvasPanel.ScreenToClient(wx.GetMousePosition())
        if(self.isInBound(panel_pos.x,panel_pos.y)==False):
            return task.cont
        
        z = self.canvas.getBlueVal(panel_pos.x,panel_pos.y)
        #print "Blue: ", z
        
        z2 = self.canvas.getGrayVal(panel_pos.x,panel_pos.y)
        #print "Gray: ", z2
        
        if z < 128:
            z = 128
        #print "Mouse pos: ", Point3(panel_pos.x, math.fabs(panel_pos.y-512), z)
        mousePos = self.terrain.getNodePath().getPos() + Point3(panel_pos.x, math.fabs(panel_pos.y-512), z+1)
        self.paintCursor.setPos(mousePos)
        self.paintRing.setPos(mousePos)
        self.paintRing.setZ(30)
        return task.cont
        
        
        
        
        
    def setupWxPaint(self):
        self.bitmap = wx.Bitmap("bitmap")
        #self.canvasPanel.AddChild(self.bitmap)
        Debug.debug(__name__,str( self.terrain.asset.getFullFilename().getExtension()))
        self.bitmap.LoadFile(self.terrain.asset.getFullFilename().toOsSpecific(),wx.BITMAP_TYPE_ANY)
        #self.static = wx.StaticBitmap(self.canvasPanel,size = wx.Size(513,513), style = wx.EXPAND )
        #self.static.SetBitmap(self.bitmap)
        #dc =wx.ClientDC(self)
        #dc.DrawBitmap(self.bitmap, 0, 0)
    
    def onClick(self,evt):
        self.canvasPanel.Bind(wx.EVT_PAINT, self.onPaint)
        panel_pos = self.canvasPanel.ScreenToClient(wx.GetMousePosition())
        # draw a blue line (thickness = 4)
        self.dc.DrawCircle(panel_pos.x, panel_pos.y,10)
        
        
        
    def onPaint(self, evt):
        self.dc =wx.PaintDC(self.canvasPanel)
        self.dc.DrawBitmap(self.bitmap, 0, 0)
        self.dc.SetPen(wx.Pen('blue', 4))
        self.dc.SetBrush(wx.Brush('blue',wx.SOLID))

        #dc.DrawLine(50, 20, 300, 20)
        #dc.SetPen(wx.Pen('red', 1))
        # draw a red rounded-rectangle
        #rect = wx.Rect(50, 50, 100, 100) 
        #dc.DrawRoundedRectangleRect(rect, 8)
        # draw a red circle with yellow fill
        #dc.SetBrush(wx.Brush('yellow'))
        #x = 250
        #y = 100
        #r = 50
        #dc.DrawCircle(x, y, r)
          
        pass
          
        
    def setupViewport(self, panel):
        self.terrainScene = NodePath(PandaNode("TerrainPaintScene"))      
        self.terrain2d = NodePath(PandaNode("TerrainPaint2d"))
        self.terrain2dScaled =self.terrain2d.attachNewNode(PandaNode("terrain2dScaled"))
        
        base.direct.manipulationControl.disableManipulation()

           
        self.viewport = TerrainView('persp', panel)
        self.viewport.SetClientSize((513,513))
        self.viewport.Update()
        base.le.ui.wxStep()
        self.viewport.initialize()

        #apply a mask to make sure GUI stuff from the main window doesn't show up here
        self.viewport.cam2d.node().setCameraMask(LE_IMPORT_MASK)    
        self.viewport.camera.reparentTo(self.terrainScene)
        self.viewport.camera.setPos(0,-20,0)
        self.viewport.camera.lookAt(0,0,0)
        self.viewport.cam2d.reparentTo(self.terrain2d)
        
        
        
        self.viewport.accept("mouse1", self.startPaint)
        self.viewport.accept("mouse1-up", self.stopPaint)
        self.viewport.accept('z',self.actionMgr.undo)
        self.viewport.accept('y', self.actionMgr.redo)
        
        
    def setupCanvas(self):
        self.temp = loader.loadModel("jack")
        #self.temp.reparentTo(self.terrain2d)
        #self.viewport.camera.lookAt(self.temp)
        self.canvas = PNMImage(513,513)
                
#        if(self.terrain.terrain.hasColorMap()==False):
#            self.canvas.fill(1,1,1)
#            self.canvas.makeRgb()
#            print self.canvas.getNumChannels()
#            self.terrain.terrain.setColorMap(self.canvas)
#        else:
        self.canvas = self.terrain.terrain.heightfield()#self.canvas.read(Filename(self.terrain.asset.getFullFilename()))
        if(self.canvas.hasAlpha()):
            Debug.debug(__name__,"In canvas there is alpha")
        self.canvas.addAlpha()
        for i in range(0,self.canvas.getReadXSize()):
            for j in range(0, self.canvas.getReadYSize()):
                self.canvas.setAlpha(i,j,.5)
        sizeX =  self.canvas.getReadXSize()
        sizeY =  self.canvas.getReadYSize()
        #self.canvas.makeGrayscale()
        Debug.debug(__name__, str(sizeX)+" "+str(sizeY))
        self.tex = Texture()
        self.tex.load(self.canvas)
        #self.tex.reparentTo(self.terrain2d)
        CM=CardMaker('') 
        CM.setFrameFullscreenQuad()
        self.card=self.terrain2d.attachNewNode(CM.generate()) 
        self.card.setTexture(self.tex) 
        
        self.viewport.SetClientSize((sizeX, sizeY))
        self.canvasPanel.SetSize(wx.Size(sizeX, sizeY))
        self.viewport.Update()
        base.le.ui.wxStep()
        
        self.painter = PNMPainter(self.canvas)
        brush = PNMBrush.makeSpot((1,1,1,1),5.0,True )
        self.painter.setPen(brush)
        #print terrain2d
        #self.canvas.reparentTo(self.terrain2d)
        
        #panel_pos = self.canvasPanel.ScreenToClient(wx.GetMousePosition())
        #print self.viewport.bt.getParent().getMouseX() 
    
    def onSliderEnd(self,evt):
        size = self.sliderBrushSize.GetValue()
        self.brushRadius = size
        grayScale = self.sliderGrayScale.GetValue()
        self.setBrush(size,grayScale)
    
    
    def setBrush(self, size, grayScale):             
        scale = grayScale/255.0
        brush = PNMBrush.makeSpot((scale,scale,scale,1.0),size,True, effect=(PNMBrush.BEBlend)  )
        self.paintRing.setScale(size)
        #brush = PNMBrush.makeImage("75%.tif",16,16)
        self.painter.setPen(brush)
        self.painter.setFill(brush)
        
        pass
    # x and y position of the draw point
    def paintSpot(self,x,y,radius,higher = True, step = 1):
        topX = x-radius
        topY = y - radius
        bottomX = x+radius
        bottomY = y+radius
        if(self.isInBound(x,y)==False):
           return
        baseVal = self.canvas.getGrayVal(x,y)
        #print "baseVal ",baseVal
        baseRGB = self.canvas.getXel(x,y)
        #print "baseRGB ",baseRGB
        for i in range(topX,bottomX):
            for j in range(topY,bottomY):
                if(self.isInBound(i,j)==False):
                    continue
                #print "=========="
                #print i, " ", j
                sum = math.fabs(i-x)+math.fabs(j-y)
                strength = radius-sum
                if(sum<=radius):
                    val = self.canvas.getGrayVal(i, j)#get the current Color
                    #raise it or lower it.
                    if(higher):
                        newVal = self.roundGrayScale(val+strength)
                    else:
                        newVal = self.roundGrayScale(val-stength)
                    
                    #newVal = Vec3(newVal,newVal,newVal)
                    newVal /= 255.0
                    self.canvas.setXel(i,j, newVal, newVal,newVal)
                    
                   
        
        
    def roundGrayScale(self, val, min=0, max=255):
        if val < 0 :    return 0
        elif val > 255: return 255
        else:             return val 
    def isInBound(self, x,y):
        a = x
        b = y
        xMax = self.canvas.getReadXSize()-1
        yMax = self.canvas.getReadYSize()-1
        if(a<0):
            return False
        elif(a>xMax):
            return False
        if(b<0):
            return False
        elif(b>yMax):
            return False
        
        return True
            
        
        
    def roundCoord(self, x, y):
        a = x
        b = y
        xMax = self.canvas.getReadXSize()
        yMax = self.canvas.getReadYSize()
        if(a<0):
            a = 0
        elif(a>xMax):
            a = xMax
        if(b<0):
            b = 0
        elif(b>yMax):
            b = yMax
            
        return (a,b)
            
    
    def updateImage(self):
        #sizeX =  self.canvas.getReadXSize()
        #sizeY =  self.canvas.getReadYSize()
        #self.tex = Texture()
        self.tex.load(self.canvas)
        self.card.clearTexture()
        self.card.setTexture(self.tex)
        #self.canvas.alphaFill(0)
        
    def resetTerrain(self, event = None):
        print "Terrain is Saved"
        file = Filename("temp.jpeg")
        file.setDirname(self.editor.currentProj.dir.getFullpath()+'/Textures')
        status = self.canvas.write(file)
        #print "Status: ",status
                 
        #self.canvas.fill(.5,.5,.5)
        #self.updateTerrain()
        #self.updateImage()
    def saveTerrain(self, event = None):
        #print type(self.terrain.asset)
        #print self.terrain.asset.getFullFilename().toOsSpecific()
        file = self.terrain.asset.getFullFilename().toOsSpecific()
        status = self.canvas.write(file)
        
        
        thumbnailFile = self.terrain.asset.getThumbnail()#.getFullpath()
        #thumbnailPath = Filename('Thumbnails/' + texture.filename.getBasename())
#        print thumbnailFile
        cwd = os.getcwd()
        os.chdir((self.editor.projDir + '/Textures/').toOsSpecific())
        #os.remove(thumbnailFile.toOsSpecific())
        subprocess.call(["image-resize","-x 60", "-y 60", "-g 1", "-o" +thumbnailFile.toOsSpecific(),self.terrain.asset.filename.getBasename()])
        #self.terrain.asset.thumbnail = thumbnailFile
        
        os.chdir(cwd)
        print "Terrain is Saved"
        
        self.editor.ui.libraryUI.update()
        
    
    def updateTerrain(self, event=None):
        #self.terrain.terrain.setHeightfield(self.canvas)
        #self.paintCursor.detachNode()#reparentTo(self.terrain.getNodePath())
        #self.terrain.terrain.setTexture(self.canvas)
        self.terrain.update()
        self.terrain.generate()
        x = self.terrain.getScale()[0]
        y = self.terrain.getScale()[1]
        z = 255.0
        self.terrain.setScale(Vec3(x, y, z))
    
    def mouse(self, event=None):
        pos = event.GetPosition()
        #print pos
        #print "HEREREREREER"
    
    def startPaint(self):
        panel_pos = self.canvasPanel.ScreenToClient(wx.GetMousePosition())
        #print panel_pos.x, " ", panel_pos.y
        x = self.canvas.getReadXSize
        y = self.canvas.getReadYSize
        if(panel_pos.x > x or panel_pos.x < 0):
            return
        if(panel_pos.y > y or panel_pos.y < 0):
            return
        
        self.drawAction = ActionDraw(self.editor, self)
        taskMgr.add(self.OnMove, "paintTask")
    
    def stopPaint(self):
        if(taskMgr.hasTaskNamed("paintTask") == False):
            return
        taskMgr.remove("paintTask")
        self.actionMgr.push(self.drawAction)
        self.drawAction()
        self.updateTerrain()

    
    
    def paintTask(self, task):
        pass
        
        
    def OnMove(self, task=None):
        curchoice = self.paintModeRadioBox.GetSelection()
        panel_pos = self.canvasPanel.ScreenToClient(wx.GetMousePosition())
        #if(self.oldX == panel_pos.x and self.oldY == panel_pos.y):
        #    return
        if(curchoice == 0):
            self.painter.drawPoint(panel_pos.x,panel_pos.y)
        #self.canvas.renderSpot(VBase4D(.5,.5,.5,1),VBase4D(.5,.5,.5,1),.00001,.00003)
        #self.oldX = panel_pos.x
        #self.oldY = panel_pos.y
        #OR
            #self.paintSpot(panel_pos.x,panel_pos.y,self.brushRadius)
        #OR
        elif(curchoice == 1):
            subImage = PNMImage(32,32)
            subImage = PNMImage("full_white_square_gradiant_alpha.tif")
            #subImage.gaussianFilter(32)
            if(subImage.hasAlpha()):
                pass# print "Sub Image has alpha"
                #subImage.addAlpha()
            self.canvas.blendSubImage(subImage,panel_pos.x,panel_pos.y,0,0,-1,-1,.1)
        elif(curchoice == 2):
            subImage = PNMImage(32,32)
            subImage = PNMImage("brush_512_75%gray.tif")
            #subImage.gaussianFilter(32)
            if(subImage.hasAlpha()):
                pass#print "Sub Image gray has alpha"
            self.canvas.blendSubImage(subImage,panel_pos.x,panel_pos.y,0,0,-1,-1,.1)
        #print panel_pos
        self.updateImage()
        #print "HEREREREREER"
        
        if(task != None):
            return task.cont
        else:
            return task.done
   
    def Close(self, evt=None):
        self.saveTerrain()
        if(self.viewport):
            self.viewport.Close()
        #base.direct.manipulationControl.widgetList.remove(self.handles)
        base.direct.drList.removeDisplayRegionContext(self.viewport.cam)
        base.direct.manipulationControl.enableManipulation()
        base.le.ui.bindKeyEvents(True)
        self.viewport.ignore("mouse1")
        self.viewport.ignore("mouse1-up")
        self.viewport.ignore("z")
        self.viewport.ignore("y")
        self.paintCursor.detachNode()
        self.paintRing.detachNode()
        taskMgr.remove("followMouseTask")
        #self.editor.NPParent.clearLight(self.light)
        self.terrain.getNodePath().clearLight(self.light)
        self.light.detachNode()

        #self.ReleaseMouse()
        
        self.Destroy()
        
    def raiseImageWithCustomImage(self):
        for i in range(0,self.customImage.getReadXSize()):
            line = []
            for j in range(0, self.customImage.getReadYSize()):
                line.append("["+str(self.customImage.getXelA(i,j))+"]")
            #print line
            
    #def  


class ActionDraw(ActionBase):
    def __init__(self, editor,terrainUI, *args, **kargs):
        ActionBase.__init__(self, editor,function =None, *args, **kargs)        
        self.oldCanvas = PNMImage()
        self.oldCanvas.copyFrom(terrainUI.canvas)
        self.terrainUI = terrainUI
        self.canvas = terrainUI.canvas

    def saveStatus(self):
        pass#self.oldValue = copy(self.getter())
    
    
    def postCall(self):
        self.newCanvas = PNMImage()
        self.newCanvas.copyFrom(self.canvas)
    
    def undo(self):
        self.canvas.copyFrom(self.oldCanvas)
        self.terrainUI.updateImage()
        self.terrainUI.updateTerrain()
        
    def redo(self):
        self.canvas.copyFrom(self.newCanvas)
        self.terrainUI.updateImage()
        self.terrainUI.updateTerrain()
    
        
class TerrainView(wx.Panel, DirectObject):
  def __init__(self, name, *args, **kwargs):
    self.name = name
    DirectObject.__init__(self)
    wx.Panel.__init__(self, *args, **kwargs)

    self.win = None
    self.camera = None
    self.lens = None
    self.camPos = None
    self.camLookAt = None
    self.initialized = False
    self.grid = None
    self.collPlane = None
    
    #self.evtloop = wx.EventLoop() 
    #self.old = wx.EventLoop.GetActive() 
    #wx.EventLoop.SetActive(self.evtloop) 
    #taskMgr.add(self.wx, "Custom wx Event Loop")


  def initialize(self):
    self.Update()
    wp = WindowProperties()
    wp.setOrigin(0, 0)
    wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
    assert self.GetHandle() != 0
    wp.setParentWindow(self.GetHandle())
    wp.setForeground(1) 
    #base.win.requestProperties(wp)
    
    

    # initializing panda window
    base.windowType = "onscreen"
    props = WindowProperties.getDefault()
    props.addProperties(wp)
    self.win = base.openWindow(props = props)#, gsg = ViewportManager.gsg)
    #print self.win
    if self.win:
      self.cam2d = base.makeCamera2d(self.win)
      self.cam2d.node().setCameraMask(LE_CAM_MASKS[self.name])
      
    self.cam = base.camList[-1]
    self.camera = render.attachNewNode(self.name)
    #self.camera.setName(self.name)
    #self.camera.reparentTo(render)
    self.cam.reparentTo(self.camera)
    self.camNode = self.cam.node()

    self.camNode.setCameraMask(LE_CAM_MASKS[self.name])
    
    self.buttonThrowers = [] 
    for i in range(self.win.getNumInputDevices()): 
        name = self.win.getInputDeviceName(i) 
        mk = base.dataRoot.attachNewNode(MouseAndKeyboard(self.win, i, name)) 
        mw = mk.attachNewNode(MouseWatcher(name)) 
        bt = mw.attachNewNode(ButtonThrower(name)) 
        if (i != 0): 
            bt.node().setPrefix('mousedev'+str(i)+'-') 
        mods = ModifierButtons() 
        bt.node().setModifierButtons(mods) 
        self.buttonThrowers.append(bt) 

            
    self.mouseWatcher = self.buttonThrowers[0].getParent() 
    self.mouseWatcherNode = self.mouseWatcher.node()
    
    self.drive = self.mouseWatcher.attachNewNode(DriveInterface('drive')) 

#    self.bt = base.setupMouse(self.win, True)
#    self.bt.node().setPrefix('_le_%s_'%self.name[:3])    
#    mw = self.bt.getParent()
#    mk = mw.getParent()
#    winCtrl = WindowControls(
#                self.win, mouseWatcher=mw,
#                cam=self.camera,
#                camNode = self.camNode,
#                cam2d=None,
#                mouseKeyboard =mk,
#                grid = self.grid)
#    base.setupWindowControls(winCtrl)

    self.initialized = True
    if self.lens != None:      self.cam.node().setLens(self.lens)
    if self.camPos != None:    self.camera.setPos(self.camPos)
    if self.camLookAt != None: self.camera.lookAt(self.camLookAt)

    self.camLens = self.camNode.getLens()

#    if self.name in ['top', 'front', 'left']:
#      x = self.ClientSize.GetWidth() * 0.1
#      y = self.ClientSize.GetHeight() * 0.1
#      self.camLens.setFilmSize(x, y)

    #self.Bind(wx.EVT_SIZE, self.onSize)
    #self.Bind(wx.EVT_LEFT_DOWN, self.Close)
    #self.accept("mouse1", self.Close)

  def Close(self):
    """Closes the viewport."""
    if self.initialized:
       wx.Window.Close(self)
    base.closeWindow(self.win)
    #wx.EventLoop.SetActive(self.old) 
  
  def onSize(self, evt):
    """Invoked when the viewport is resized."""
    if self.win != None:
      wp = WindowProperties()
      wp.setOrigin(0, 0)
      newWidth = self.ClientSize.GetWidth()
      newHeight = self.ClientSize.GetHeight()
      wp.setSize(newWidth, newHeight)
      self.win.requestProperties(wp)

      if hasattr(base, "direct") and base.direct:
        for dr in base.direct.drList:
          if dr.camNode == self.camNode:
            dr.updateFilmSize(newWidth, newHeight)
            break
  def wx(self, task): 
        while self.evtloop.Pending(): 
            self.evtloop.Dispatch() 
        time.sleep(0.01) 
        #self.ProcessIdle() 
        return task.cont 
          
         
        
        