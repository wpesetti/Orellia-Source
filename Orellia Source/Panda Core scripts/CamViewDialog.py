import wx
import os
from wx import xrc
from pandac.PandaModules import *
from direct.wxwidgets.ViewPort import *
from direct.directtools.DirectManipulation import ObjectHandles
from direct.directtools.DirectGlobals import *

from ObjectInputDialog import *
from direct.interval.MetaInterval import Sequence
from Rope import *


"""
Dialog that allows the user to see from
a camera's point of view, in the level editor,
and manipulate some of its properties
"""

LE_CAM_MASK = BitMask32.bit(4)

class CamViewDialog(wx.Dialog):
    def __init__(self, parent, camera):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource('/XRC/ObjectUI/dlgCamView.xrc')
        self.res.LoadOnDialog(pre, parent, 'dlgCamView')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.onCreate)
        self.parent = parent
        
        # Get the cameras properties
        self.pos = camera.getPos()
        self.hpr = camera.getHpr()
        self.fov = camera.getLens().getFov()
        self.near = camera.getLens().getNear()
        self.far = camera.getLens().getFar()
        self.camera = camera
    
    def onCreate(self, evt=None):
        base.le.deselectAll()
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        # Ignore the main editor
        ## taskMgr.remove("mouseTask")
        base.le.ui.bindKeyEvents(False)
        ## base.le.ui.inPandaWindow = False
        
        ## self.Bind(wx.EVT_CHAR, self.onKeyEvent)
        ## self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        ## self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
        
        self.Show()
        base.direct.manipulationControl.disableManipulation()
        
        self.Bind(wx.EVT_CLOSE, self.close)
        
        # main panel
        self.panelMain = xrc.XRCCTRL(self, 'mainPanel')
        self.pandaPanel = xrc.XRCCTRL(self, "pandaPanel")
        self.propsPanel = xrc.XRCCTRL(self, "propsPanel")
        self.ropePanel = xrc.XRCCTRL(self, "ropePanel")
        
        # text boxes
        self.txtX = xrc.XRCCTRL(self.propsPanel, 'txtX')
        self.txtY = xrc.XRCCTRL(self.propsPanel, 'txtY')
        self.txtZ = xrc.XRCCTRL(self.propsPanel, 'txtZ')
        self.txtX.SetValue(str(self.camera.getPos()[0]))
        self.txtY.SetValue(str(self.camera.getPos()[1]))
        self.txtZ.SetValue(str(self.camera.getPos()[2]))
        
        for x in (self.txtX, self.txtY, self.txtZ):
            x.Bind(wx.EVT_TEXT_ENTER, self.updatePos)
        
        self.txtH = xrc.XRCCTRL(self.propsPanel, 'txtH')
        self.txtP = xrc.XRCCTRL(self.propsPanel, 'txtP')
        self.txtR = xrc.XRCCTRL(self.propsPanel, 'txtR')
        self.txtH.SetValue(str(self.camera.getHpr()[0]))
        self.txtP.SetValue(str(self.camera.getHpr()[1]))
        self.txtR.SetValue(str(self.camera.getHpr()[2]))
        
        for x in (self.txtH, self.txtP, self.txtR):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateHpr)
        
        self.txtHoriz = xrc.XRCCTRL(self.propsPanel, 'txtHoriz')
        self.txtVert = xrc.XRCCTRL(self.propsPanel, 'txtVert')
        self.txtHoriz.SetValue(str(self.camera.getLens().getFov()[0]))
        self.txtVert.SetValue(str(self.camera.getLens().getFov()[1]))
        
        for x in (self.txtHoriz, self.txtVert):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateFov)
        
        self.txtNear = xrc.XRCCTRL(self.propsPanel, 'txtNear')
        self.txtFar = xrc.XRCCTRL(self.propsPanel, 'txtFar')
        self.txtNear.SetValue(str(self.camera.getLens().getNear()))
        self.txtFar.SetValue(str(self.camera.getLens().getFar()))
        
        for x in (self.txtNear, self.txtFar):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateNearFar)
            
        self.txtRope = xrc.XRCCTRL(self.ropePanel, 'txtRope')
        self.txtSeqTime = xrc.XRCCTRL(self.ropePanel, 'txtSeq')
        self.txtLookAt = xrc.XRCCTRL(self.ropePanel, 'txtLookAt')
        
        #self.txtRope.Bind(wx.EVT_TEXT_ENTER, self.updateRope)
        self.txtSeqTime.Bind(wx.EVT_TEXT_ENTER, self.updateSeqTime)
        
        self.radioBoxOrientation = xrc.XRCCTRL(self.ropePanel, 'radioBoxOrientation')
        self.Bind(wx.EVT_RADIOBOX, self.onOrientationChange, self.radioBoxOrientation)
        
        
        #Preview Buttons
        self.btnPreview = xrc.XRCCTRL(self, "btnPlay")
        self.btnPreview.Bind(wx.EVT_BUTTON, self.previewSeq)
        
        self.btnStop = xrc.XRCCTRL(self, "btnReset")
        self.btnStop.Bind(wx.EVT_BUTTON, self.resetSeq)
        
        # buttons
        self.btnOk = xrc.XRCCTRL(self.panelMain, 'btnOk')
        self.btnCancel = xrc.XRCCTRL(self.panelMain, 'btnCancel')
                
        
        self.btnCancel.Bind(wx.EVT_BUTTON, self.close)
        self.btnOk.Bind(wx.EVT_BUTTON, self.onOk)
        self.ok = False
        
        # Camera view
        diff = 600 - (self.camera.getLens().getAspectRatio() * 600)
        self.SetSize((610 - diff, 759))
        pos = self.GetPosition()
        self.SetPosition((pos[0] + (diff/2), pos[1]))
        self.pandaPanel.SetSize((self.camera.getLens().getAspectRatio()*600, 600))
        self.camView = Viewport('persp', self.pandaPanel)
        self.camView.SetClientSize((self.camera.getLens().getAspectRatio()*600, 600))
        ViewportManager.updateAll()
        base.le.ui.wxStep()
        self.camView.initialize()
        self.handles = ObjectHandles('camViewWidget')
        self.handles.hide()
        base.direct.manipulationControl.widgetList.append(self.handles)
        self.camView.cam.node().setLens(self.camera.getLens())
        base.direct.drList.addDisplayRegionContext(self.camView.cam)
        self.camView.cam2d.node().setCameraMask(LE_CAM_MASK)
        self.camView.cam.node().setCameraMask(LE_CAM_MASK)
        
        self.camView.camera.reparentTo(render)
        self.camView.camera.setPos(self.camera.getPos())
        self.camView.camera.setHpr(self.camera.getHpr())
        
        base.le.ui.perspView.grid.hide(LE_CAM_MASK)
        
        #self.startPos = self.camera.getPos()
        #self.startHpr = self.camera.getHpr()
        
        self.Layout()
        
        ## # setup the keys
        ## self.setupControls()
    
    def onOk(self, evt=None):
        self.ok = True
        self.close()
    
    def close(self, evt=None):
        self.camView.Close()
        base.direct.manipulationControl.enableManipulation()
        base.direct.drList.removeDisplayRegionContext(self.camView.cam)
        base.le.ui.bindKeyEvents(True)
        
        if not self.ok:
            self.camera.setPos(self.pos)
            self.camera.setHpr(self.hpr)
            self.camera.getLens().setFov(self.fov)
            self.camera.getLens().setNearFar(self.near,self.far)
        
        ## self.killControls()
        
        ## # Give control back to the main window
        ## taskMgr.add(base.le.ui.mouseTask,"mouseTask")
        
        self.Destroy()
    
    def updatePos(self, evt=None):
        try:
            x = float(self.txtX.GetValue())
            y = float(self.txtY.GetValue())
            z = float(self.txtZ.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtX.SetValue(str(self.camera.getPos()[0]))
            self.txtY.SetValue(str(self.camera.getPos()[1]))
            self.txtZ.SetValue(str(self.camera.getPos()[2]))
        else:
            self.camera.setPos(Vec3(x, y, z))
            self.camView.camera.setPos(Vec3(x, y, z))
    
    def updateHpr(self, evt=None):
        try:
            h = float(self.txtH.GetValue())
            p = float(self.txtP.GetValue())
            r = float(self.txtR.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtH.SetValue(str(self.camera.getHpr()[0]))
            self.txtP.SetValue(str(self.camera.getHpr()[1]))
            self.txtR.SetValue(str(self.camera.getHpr()[2]))
        else:
            self.camera.setHpr(Vec3(h, p, r))
            self.camView.camera.setHpr(Vec3(h, p, r))
    
    def updateFov(self, evt=None):
        try:
            h = float(self.txtHoriz.GetValue())
            v = float(self.txtVert.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtHoriz.SetValue(str(self.camera.getLens().getFov()[0]))
            self.txtVert.SetValue(str(self.camera.getLens().getFov()[1]))
        else:
            self.camera.getLens().setFov(Vec2(h,v))
            self.camView.cam.node().getLens().setFov(Vec2(h, v))
        
    def updateNearFar(self, evt=None):
        try:
            near = float(self.txtNear.GetValue())
            far = float(self.txtFar.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtNear.SetValue(str(self.camera.getLens().getNear()))
            self.txtFar.SetValue(str(self.camera.getLens().getFar()))
        else:
            self.camera.getLens().setNearFar(near, far)
            self.camView.cam.node().getLens().setNearFar(near, far)
            
    def updateSeqTime(self, evt=None):
        try:
            seq = float(self.txtSeqTime.GetValue())
            #near = float(self.txtNear.GetValue())
            #far = float(self.txtFar.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            evt.Veto()
        else:
            pass
            #self.camera.getLens().setNearFar(near, far)
            #self.camView.cam.node().getLens().setNearFar(near, far)
            
    def onOrientationChange(self, evt = None):
        curchoice = self.radioBoxOrientation.GetSelection()
        #orientation = self.radioBoxOrientation.GetString(curchoice)
        #obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(curchoice ==2):
            dlg = ObjectInputDialog(self)
            lookAtName = dlg.ShowModal()
            dlg.Destroy()
            if lookAtName:
                lookAt = self.parent.editor.objectMgr.findObjectById(lookAtName)
                self.camView.camera.lookAt(lookAt.getNodePath())
            self.txtLookAt.ChangeValue(lookAtName)
        else:
            self.txtLookAt.ChangeValue("")
            
    
    def previewSeq(self, evt):
        #rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        curChoice = self.radioBoxOrientation.GetSelection()
        if self.btnPreview.GetLabel() == "Play":
            ropeName = self.txtRope.GetValue()
            rope = self.parent.editor.objectMgr.findObjectById(ropeName)
            seqTime = self.txtSeqTime.GetValue()
            if(rope == None):
                msg = wx.MessageDialog(self, "Cannot create sequence with non-existent rope.","Invalid Rope" , wx.OK|wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
                return
            rope.genWaypointRope()
            self.previewSeq = Sequence()
            if(curChoice == 0):
                followPathTemp = True
                lookAtObj = None
            elif(curChoice == 1):
                followPathTemp = False
                lookAtObj = None
            else:
                followPathTemp = False
                lookAtName = self.txtLookAt.GetValue()
                lookAtObj = self.parent.editor.objectMgr.findObjectById(lookAtName)
                if(lookAt == None):
                    msg = wx.MessageDialog(self, "Cannot create sequence with non-existent lookAt.","Invalid LookAt" , wx.OK|wx.ICON_HAND)
                    msg.ShowModal()
                    msg.Destroy()
                    return
                else:
                    lookAtObj = lookAtObj.getNodePath()  
            temp =UniformRopeMotionInterval(rope.rope, 
                                            self.camView.camera, 
                                            float(seqTime), 
                                            followPath=followPathTemp, lookAt=lookAtObj)
            self.previewSeq.append(temp)
            self.previewSeq.append(Func(self.resetPlayUI))
            self.previewSeq.start()#self.runSeq(self.previewSeq)
            self.btnPreview.SetLabel("Pause")
            
        elif self.btnPreview.GetLabel() == "Pause":
            self.previewSeq.pause()
            self.btnPreview.SetLabel("Resume")
        elif self.btnPreview.GetLabel() == "Resume":
            self.previewSeq.resume()
            self.btnPreview.SetLabel("Pause")

    def resetPlayUI(self):
        self.btnPreview.SetLabel("Play")    
        
    def resetSeq(self, evt):
        if self.previewSeq is not None:
            self.camView.camera.setPos(self.camera.getPos())
            self.camView.camera.setHpr(self.camera.getHpr())
            self.previewSeq.finish()
            self.btnPreview.SetLabel("Play")    
            
            
            
    
    def onKeyEvent(self, evt):
        input = ""
    
    def onKeyDown(self, evt):
        input = ""
    
    def onKeyUp(self, evt):
        input = ""
    
    ## def setupControls(self):
        ## base.accept('w', taskMgr.add, [self.moveCamForward, 'moveCamForward'])
        ## base.accept('w-up', taskMgr.remove, ['moveCamForward'])
        ## base.accept('a', taskMgr.add, [self.moveCamLeft, 'moveCamLeft'])
        ## base.accept('a-up', taskMgr.remove, ['moveCamLeft'])
        ## base.accept('s', taskMgr.add, [self.moveCamBack, 'moveCamBack'])
        ## base.accept('s-up', taskMgr.remove, ['moveCamBack'])
        ## base.accept('d', taskMgr.add, [self.moveCamRight, 'moveCamRight'])
        ## base.accept('d-up', taskMgr.remove, ['moveCamRight'])
        ## base.accept('q', taskMgr.add, [self.moveCamUp, 'moveCamUp'])
        ## base.accept('q-up', taskMgr.remove, ['moveCamUp'])
        ## base.accept('e', taskMgr.add, [self.moveCamDown, 'moveCamDown'])
        ## base.accept('e-up', taskMgr.remove, ['moveCamDown'])
        
        ## base.accept('arrow_up', taskMgr.add, [self.rotateCamUp, 'rotateCamUp'])
        ## base.accept('arrow_up-up', taskMgr.remove, ['rotateCamUp'])
        ## base.accept('arrow_left', taskMgr.add, [self.turnCamLeft, 'turnCamLeft'])
        ## base.accept('arrow_left-up', taskMgr.remove, ['turnCamLeft'])
        ## base.accept('arrow_down', taskMgr.add, [self.rotateCamDown, 'rotateCamDown'])
        ## base.accept('arrow_down-up', taskMgr.remove, ['rotateCamDown'])
        ## base.accept('arrow_right', taskMgr.add, [self.turnCamRight, 'turnCamRight'])
        ## base.accept('arrow_right-up', taskMgr.remove, ['turnCamRight'])
        ## base.accept('n', taskMgr.add, [self.rotateCamLeft, 'rotateCamLeft'])
        ## base.accept('n-up', taskMgr.remove, ['rotateCamLeft'])
        ## base.accept('m', taskMgr.add, [self.rotateCamRight, 'rotateCamRight'])
        ## base.accept('m-up', taskMgr.remove, ['rotateCamRight'])
    
    ## def killControls(self):
        ## base.ignore('w')
        ## base.ignore('w-up')
        ## base.ignore('a')
        ## base.ignore('a-up')
        ## base.ignore('s')
        ## base.ignore('s-up')
        ## base.ignore('d')
        ## base.ignore('d-up')
        ## base.ignore('q')
        ## base.ignore('q-up')
        ## base.ignore('e')
        ## base.ignore('e-up')
        
        ## base.ignore('arrow_up')
        ## base.ignore('arrow_up-up')
        ## base.ignore('arrow_left')
        ## base.ignore('arrow_left-up')
        ## base.ignore('arrow_down')
        ## base.ignore('arrow_down-up')
        ## base.ignore('arrow_right')
        ## base.ignore('arrow_right-up')
        ## base.ignore('n')
        ## base.ignore('n-up')
        ## base.ignore('m')
        ## base.ignore('m-up')
    
    ## def moveCamForward(self, task):
        ## self.camera.setPos(self.camera, 0, 0.1, 0)
        ## self.camView.camera.setPos(self.camView.camera, 0, 0.1, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def moveCamBack(self, task):
        ## self.camera.setPos(self.camera, 0, -0.1, 0)
        ## self.camView.camera.setPos(self.camView.camera, 0, -0.1, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def moveCamLeft(self, task):
        ## self.camera.setPos(self.camera, -0.1, 0, 0)
        ## self.camView.camera.setPos(self.camView.camera, -0.1, 0, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def moveCamRight(self, task):
        ## self.camera.setPos(self.camera, 0.1, 0, 0)
        ## self.camView.camera.setPos(self.camView.camera, 0.1, 0, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def moveCamUp(self, task):
        ## self.camera.setPos(self.camera, 0, 0, 0.1)
        ## self.camView.camera.setPos(self.camView.camera, 0, 0, 0.1)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def moveCamDown(self, task):
        ## self.camera.setPos(self.camera, 0, 0, -0.1)
        ## self.camView.camera.setPos(self.camView.camera, 0, 0, -0.1)
        ## self.updateTextBoxes()
        ## return task.cont
    
    ## def turnCamLeft(self, task):
        ## self.camera.setHpr(self.camera, 2.0, 0, 0)
        ## self.camView.camera.setHpr(self.camView.camera, 2.0, 0, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def turnCamRight(self, task):
        ## self.camera.setHpr(self.camera, -2.0, 0, 0)
        ## self.camView.camera.setHpr(self.camView.camera, -2.0, 0, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def rotateCamUp(self, task):
        ## self.camera.setHpr(self.camera, 0, 2.0, 0)
        ## self.camView.camera.setHpr(self.camView.camera, 0, 2.0, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def rotateCamDown(self, task):
        ## self.camera.setHpr(self.camera, 0, -2.0, 0)
        ## self.camView.camera.setHpr(self.camView.camera, 0, -2.0, 0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def rotateCamLeft(self, task):
        ## self.camera.setHpr(self.camera, 0, 0, 2.0)
        ## self.camView.camera.setHpr(self.camView.camera, 0, 0, 2.0)
        ## self.updateTextBoxes()
        ## return task.cont
    ## def rotateCamRight(self, task):
        ## self.camera.setHpr(self.camera, 0, 0, -2.0)
        ## self.camView.camera.setHpr(self.camView.camera, 0, 0, -2.0)
        ## self.updateTextBoxes()
        ## return task.cont
    
    ## def updateTextBoxes(self):
        ## self.txtX.SetValue(str(self.camera.getPos()[0]))
        ## self.txtY.SetValue(str(self.camera.getPos()[1]))
        ## self.txtZ.SetValue(str(self.camera.getPos()[2]))
        
        ## self.txtH.SetValue(str(self.camera.getHpr()[0]))
        ## self.txtP.SetValue(str(self.camera.getHpr()[1]))
        ## self.txtR.SetValue(str(self.camera.getHpr()[2]))