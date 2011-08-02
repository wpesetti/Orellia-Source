import wx
import os

from wx.lib.scrolledpanel import ScrolledPanel
import wx.lib.agw.pycollapsiblepane as pyPane
from direct.wxwidgets.WxSlider import *
from pandac.PandaModules import *
from wx import xrc
from pandac.PandaModules import Filename
import Util
from ActionMgr import *
from Objects import *
from ShaderInputUI import *
from direct.interval.IntervalGlobal import *
from ObjectInputDialog import *
from WaypointDialog import *
from CamViewDialog import *
from TerrainPaintUI import *
from wx.lib.mixins.listctrl import TextEditMixin
import math

from Sound import *
#qiaosi
'''
from panda3d.physics import BaseParticleEmitter,BaseParticleRenderer
from panda3d.physics import PointParticleFactory,SpriteParticleRenderer
from panda3d.physics import LinearNoiseForce,DiscEmitter
from panda3d.core import TextNode
from panda3d.core import AmbientLight,DirectionalLight
from panda3d.core import Point3,Vec3,Vec4
from panda3d.core import Filename
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
'''
from Particle import *




RESOURCE_FILE = {'base':'XRC/ObjectUI/panelBase.xrc','appearance':'XRC/ObjectUI/panelAppearance.xrc',
                 'renderEffect':'XRC/ObjectUI/panelRenderEffect.xrc','fog':'XRC/ObjectUI/panelFog.xrc',
                 'actor':'XRC/ObjectUI/panelActor.xrc','collider':'XRC/ObjectUI/panelCollider.xrc',
                 'light':'XRC/ObjectUI/panelLight.xrc','camera':'XRC/ObjectUI/panelCamera.xrc',
                 'lens':'XRC/ObjectUI/panelLens.xrc','shader':'XRC/ObjectUI/panelShader.xrc',
                 'terrain':'XRC/ObjectUI/panelTerrain.xrc','lightLens':'XRC/ObjectUI/panelLightLens.xrc',
                 'orthoLens':'XRC/ObjectUI/panelOrthoLens.xrc', 'game':'XRC/ObjectUI/panelGame.xrc',
                 'script':'XRC/ObjectUI/panelScript.xrc', 'particle':'XRC/ObjectUI/panelParticle.xrc',#qiaosi
                 'rope':'XRC/ObjectUI/panelRope.xrc'}

#Container panel for all of teh object propery panes
class ObjectPropertyUI(ScrolledPanel):
    def __init__(self, parent, editor):
                
        ScrolledPanel.__init__(self, parent)      
        self.parent = parent
        self.editor = editor
        parentSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(self, 1, wx.EXPAND, 0)
        parent.SetSizer(parentSizer)
        parent.Layout()
        
        self.sizer = wx.FlexGridSizer()
        #self.sizer.SetRows(13)
        #qiaosi
        self.sizer.SetRows(15)

        self.basePane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.appearancePane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.actorPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.lightPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.cameraPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.lensPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.orthoLensPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.lightLensPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.terrainPane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.colliderPane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.shaderPane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.gamePane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.scriptPane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        #qiaosi
        self.particlePane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.ropePane = pyPane.PyCollapsiblePane(self, -1, style = pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        
        panes = [self.basePane, self.lightPane, self.colliderPane,
                 self.actorPane, self.lensPane, self.orthoLensPane, 
                 self.shaderPane,self.appearancePane, self.terrainPane,
                 self.cameraPane, self.lightLensPane, self.gamePane,
                 self.scriptPane, self.particlePane, self.ropePane]#qiaosi

        
        self.basePane.SetLabel("General")
        self.actorPane.SetLabel("Actors")
        self.lightPane.SetLabel("Lights")
        self.cameraPane.SetLabel("Camera")
        self.lensPane.SetLabel("Perspective Lens")
        self.orthoLensPane.SetLabel("Orthographic Lens")
        self.lightLensPane.SetLabel("Light Lens")
        self.shaderPane.SetLabel("Shader(advanced)")
        self.appearancePane.SetLabel("Appearance")
        self.terrainPane.SetLabel("Terrain")
        self.colliderPane.SetLabel("Collider")
        self.gamePane.SetLabel("Game")
        self.scriptPane.SetLabel("Script")
        #qiaosi
        self.particlePane.SetLabel("Particle")
        self.ropePane.SetLabel("Rope")
        
        self.sizer.Add(self.basePane, wx.EXPAND)
        self.sizer.Add(self.appearancePane, wx.EXPAND)
        ## self.sizer.Add(self.materialPane, wx.EXPAND)
        ## self.sizer.Add(self.renderEffectPane, wx.EXPAND)
        ## self.sizer.Add(self.fogPane, wx.EXPAND)
        self.sizer.Add(self.actorPane, wx.EXPAND)
        self.sizer.Add(self.lightPane, wx.EXPAND)
        self.sizer.Add(self.cameraPane,wx.EXPAND)
        self.sizer.Add(self.lensPane, wx.EXPAND)
        self.sizer.Add(self.orthoLensPane, wx.EXPAND)
        self.sizer.Add(self.lightLensPane, wx.EXPAND)
        self.sizer.Add(self.terrainPane, wx.EXPAND)
        self.sizer.Add(self.colliderPane, wx.EXPAND)
        self.sizer.Add(self.shaderPane, wx.EXPAND)
        self.sizer.Add(self.gamePane, wx.EXPAND)
        self.sizer.Add(self.scriptPane, wx.EXPAND)
        #qiaosi
        self.sizer.Add(self.particlePane, wx.EXPAND)
        self.sizer.Add(self.ropePane, wx.EXPAND)


        
        self.basePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.appearancePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        ## self.renderEffectPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        ## self.fogPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.actorPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.lightPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.cameraPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.lensPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.orthoLensPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.lightLensPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.shaderPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.terrainPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.colliderPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.gamePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.scriptPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        #qiaosi
        self.particlePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.ropePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        
        self.loadPanels()

        self.SetSizerAndFit(self.sizer)
        self.onPaneChanged(None)
        self.Hide()
        
    def onPaneChanged(self, evt):
        self.parent.Layout()
        self.parent.Refresh()
        self.Layout()
        self.Refresh()
        self.SetupScrolling(self, scroll_y = True, rate_y = 20)
        
    def expandAllPanes(self, panes):
        for pane in panes:
            pane.Expand()
    
    #Updates everything on the panel based on the current state of the object
    #Movable shoudl be removed at some point        
    def updateProps(self, obj, movable=True):
        self.Show()
        for panel in self.panels:
            panel.updateProps(obj)
    
    def updateWidgets(self):
        self.gamePanel.load
            
    def clearPropUI(self):
        self.Hide()
        
    def loadPanels(self):
        self.basePanel = BasePropertyPanel(self.basePane.GetPane(), self.editor)
        self.appearancePanel = AppearancePropertyPanel(self.appearancePane.GetPane(), self.editor) 
        self.lightPanel = LightPropertyPanel(self.lightPane.GetPane(), self.editor)  
        self.actorPanel = ActorPropertyPanel(self.actorPane.GetPane(), self.editor)
        self.lensPanel = LensPropertyPanel(self.lensPane.GetPane(), self.editor)
        self.orthoLensPanel = OrthoLensPropertyPanel(self.orthoLensPane.GetPane(), self.editor)
        self.lightLensPanel = LightLensPropertyPanel(self.lightLensPane.GetPane(), self.editor)
        self.cameraPanel = CameraPropertyPanel(self.cameraPane.GetPane(), self.editor)
        self.colliderPanel = ColliderPropertyPanel(self.colliderPane.GetPane(), self.editor)
        self.shaderPanel = ShaderPropertyPanel(self.shaderPane.GetPane(), self.editor)
        self.terrainPanel = TerrainPropertyPanel(self.terrainPane.GetPane(), self.editor)
        self.gamePanel = GamePropertyPanel(self.gamePane.GetPane(), self.editor)
        self.scriptPanel = ScriptPropertyPanel(self.scriptPane.GetPane(),self.editor)
        #qiaosi
        self.particlePanel = ParticlePropertyPanel(self.particlePane.GetPane(),self.editor)
        self.ropePanel = RopePropertyPanel(self.ropePane.GetPane(), self.editor)
        
        self.panels = [self.basePanel, self.lightPanel, self.actorPanel, self.lensPanel, self.orthoLensPanel, self.colliderPanel,
                       self.shaderPanel, self.appearancePanel, self.terrainPanel, self.cameraPanel, self.lightLensPanel,
                       self.gamePanel, self.scriptPanel, self.particlePanel,  self.ropePanel]#qiaosi

#base class fro all object property panes    
class ObjectPropertyPanel(wx.Panel):            
    def __init__(self, parent, editor, XRC, panelXRCName):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(XRC)
        self.res.LoadOnPanel(pre, parent, panelXRCName)
        self.PostCreate(pre)
        #self.Layout()
        self.editor = editor
        #self.Bind(wx.EVT_CHILD_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
        
        def txtOnKeyEvent(evt):
            if evt.ControlDown() or evt.AltDown():
                self.editor.ui.onKeyEvent(evt)
                
                
            evt.Skip()
            
        for w in self.GetChildren():
            if isinstance(w, wx.TextCtrl):
                w.Bind(wx.EVT_SET_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(True))
                w.Bind(wx.EVT_KILL_FOCUS, lambda(evt): self.editor.objectMgr.onLeaveObjectPropUI(True))
                w.Bind(wx.EVT_CHAR, txtOnKeyEvent)
            else:
                w.Bind(wx.EVT_SET_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
                w.Bind(wx.EVT_KILL_FOCUS, lambda(evt): self.editor.objectMgr.onLeaveObjectPropUI(False))

class ListCtrlMultiEdit(wx.ListCtrl, TextEditMixin):
    pass
    
#General pane (transforms, tags, name , etc.)            
class BasePropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['base'], 'basePanel')
        
        self.txtObjName = xrc.XRCCTRL(self, "txtObjName")
        self.txtObjName.Bind(wx.EVT_TEXT_ENTER, self.renameObj)
        
        self.txtXPos = xrc.XRCCTRL(self, "txtXPos")
        self.txtYPos = xrc.XRCCTRL(self, "txtYPos")
        self.txtZPos = xrc.XRCCTRL(self, "txtZPos")
        
        for x in (self.txtXPos, self.txtYPos, self.txtZPos):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateObjPos)
        
        self.txtH = xrc.XRCCTRL(self, "txtH")
        self.txtP = xrc.XRCCTRL(self, "txtP")
        self.txtR = xrc.XRCCTRL(self, "txtR")
        
        for x in (self.txtH, self.txtP, self.txtR):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateObjHpr)
        
        self.txtXScale = xrc.XRCCTRL(self, "txtXScale")
        self.txtYScale = xrc.XRCCTRL(self, "txtYScale")
        self.txtZScale = xrc.XRCCTRL(self, "txtZScale")
        
        for x in (self.txtXScale, self.txtYScale, self.txtZScale):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateObjScale)
        
        self.rdoRelative = xrc.XRCCTRL(self, "rdoRelative")
        self.rdoRelative.Bind(wx.EVT_RADIOBUTTON, self.switchToRelative)

        self.rdoAbsolute = xrc.XRCCTRL(self, "rdoAbsolute")
        self.rdoAbsolute.Bind(wx.EVT_RADIOBUTTON, self.switchToAbsolute)
        
        self.chkHidden = xrc.XRCCTRL(self, "chkHidden") 
        self.chkHidden.Bind(wx.EVT_CHECKBOX, self.toggleHide)
        
        self.chkDoubleSided = xrc.XRCCTRL(self, "chkDoubleSided")
        self.chkDoubleSided.Bind(wx.EVT_CHECKBOX, self.toggleDoubleSided)
        
        self.chkGround = xrc.XRCCTRL(self, "chkGround")
        self.chkGround.Bind(wx.EVT_CHECKBOX, self.toggleGround)
        
        self.chkWall = xrc.XRCCTRL(self, "chkWall")
        self.chkWall.Bind(wx.EVT_CHECKBOX, self.toggleWall)
        
        self.listTags = xrc.XRCCTRL(self, "listTags")
        self.listTags.__class__ = ListCtrlMultiEdit
        TextEditMixin.__init__(self.listTags)
        self.listTags.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.onEditTag)
        self.listTags.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.onBeginEditTag)
        
        self.btnAddTag = xrc.XRCCTRL(self, "btnAddTag")
        self.btnAddTag.Bind(wx.EVT_BUTTON, self.onAddTag)
        
        self.btnRemoveTag = xrc.XRCCTRL(self, "btnRemoveTag")
        self.btnRemoveTag.Bind(wx.EVT_BUTTON, self.onRemoveTag)
    
        self.tags = {}
        self.mode = 'relative'
    
    def switchToRelative(self, evt=None):
        self.mode = 'relative'
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.updateProps(obj)
        
    def switchToAbsolute(self, evt=None):
        self.mode = 'absolute'
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.updateProps(obj)
    
    #function to updates everything in this pane based on the current state of the object
    #this function should NOT change the object itself
    def updateProps(self, obj):
        self.txtObjName.SetValue(obj.getName())
        
        if self.mode == 'relative':
            self.txtXPos.SetValue(str(obj.getPos()[0]))
            self.txtYPos.SetValue(str(obj.getPos()[1]))
            self.txtZPos.SetValue(str(obj.getPos()[2]))
            
            self.txtH.SetValue(str(obj.getHpr()[0]))
            self.txtP.SetValue(str(obj.getHpr()[1]))
            self.txtR.SetValue(str(obj.getHpr()[2]))
            
            self.txtXScale.SetValue(str(obj.getScale()[0]))
            self.txtYScale.SetValue(str(obj.getScale()[1]))
            self.txtZScale.SetValue(str(obj.getScale()[2]))
        else:
            self.txtXPos.SetValue(str(obj.getPos(render)[0]))
            self.txtYPos.SetValue(str(obj.getPos(render)[1]))
            self.txtZPos.SetValue(str(obj.getPos(render)[2]))
            
            self.txtH.SetValue(str(obj.getHpr(render)[0]))
            self.txtP.SetValue(str(obj.getHpr(render)[1]))
            self.txtR.SetValue(str(obj.getHpr(render)[2]))
            
            self.txtXScale.SetValue(str(obj.getScale(render)[0]))
            self.txtYScale.SetValue(str(obj.getScale(render)[1]))
            self.txtZScale.SetValue(str(obj.getScale(render)[2]))
        
        self.chkHidden.SetValue(obj.nodePath.isHidden())
        self.chkDoubleSided.SetValue(obj.nodePath.getTwoSided())
        self.chkGround.SetValue(obj.nodePath.hasTag('LE-ground'))
        self.chkWall.SetValue(obj.nodePath.hasTag('LE-wall'))
        
        if obj.getAllTags() != self.tags:
            self.tags = copy(obj.getAllTags())
            
            self.listTags.ClearAll()
            self.listTags.InsertColumn(0, "Key")
            self.listTags.InsertColumn(1, "Value")
            for k, v in obj.getAllTags().iteritems():
                if k not in  ("OBJRoot", "LE-ground", "LE-mainChar", "LE-attackable", "LE-maxHealth",
                              "LE-currentHealth", "LE-aggression", "LE-strategy", "LE-wall"): # added LE-mainChar...Anton 1/28/11...and others...4/4/11
                    pos = self.listTags.InsertStringItem(self.listTags.GetItemCount(), k)
                    self.listTags.SetStringItem(pos, 1, v)
            self.listTags.SetColumnWidth(0, self.listTags.GetSize().GetWidth()/2 - 3)
            self.listTags.SetColumnWidth(1, self.listTags.GetSize().GetWidth()/2 - 3)
        

    def updateObjPos(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            x = float(self.txtXPos.GetValue())
            y = float(self.txtYPos.GetValue())
            z = float(self.txtZPos.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtXPos.SetValue(str(obj.getPos()[0]))
            self.txtYPos.SetValue(str(obj.getPos()[1]))
            self.txtZPos.SetValue(str(obj.getPos()[2]))
        else:
            if self.mode == 'relative':
                obj.nodePath.setPos(Vec3(x, y, z))
            else:
                obj.nodePath.setPos(render, Vec3(x, y, z))
            
            action = ActionTransformObj(self.editor, obj.getName(), copy(obj.nodePath.getMat()))
            self.editor.actionMgr.push(action)
            action()
            
    def updateObjHpr(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            h = float(self.txtH.GetValue())
            p = float(self.txtP.GetValue())
            r = float(self.txtR.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtH.SetValue(str(obj.getHpr()[0]))
            self.txtP.SetValue(str(obj.getHpr()[1]))
            self.txtR.SetValue(str(obj.getHpr()[2]))
        else:
            if self.mode == 'relative':
                obj.nodePath.setHpr(Vec3(h, p, r))
            else:
                obj.nodePath.setHpr(render, Vec3(h, p, r))
            
            action = ActionTransformObj(self.editor, obj.getName(), copy(obj.nodePath.getMat()))
            self.editor.actionMgr.push(action)
            action()
        
    def updateObjScale(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            x = float(self.txtXScale.GetValue())
            y = float(self.txtYScale.GetValue())
            z = float(self.txtZScale.GetValue())
            
            if x <= 0:
                x = 0.001
            if y <= 0:
                y = 0.001
            if z <= 0:
                z = 0.001
                
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtXScale.SetValue(str(obj.getScale()[0]))
            self.txtYScale.SetValue(str(obj.getScale()[1]))
            self.txtZScale.SetValue(str(obj.getScale()[2]))
        else:
            if self.mode == 'relative':
                obj.nodePath.setScale(Vec3(x, y, z))
            else:
                obj.nodePath.setScale(render, Vec3(x, y, z))
            
            action = ActionTransformObj(self.editor, obj.getName(), copy(obj.nodePath.getMat()))
            self.editor.actionMgr.push(action)
            action()

    def onAddTag(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        tags = obj.getAllTags()
        key = 'newTag'
        i = 1
        while key + str(i) in tags.keys():
            i += 1
        
        key = key + str(i)
        
        action = ActionGeneric(self.editor, lambda: obj.nodePath.setTag(key, "1"), lambda: obj.nodePath.clearTag(key))
        self.editor.actionMgr.push(action)
        action()
        
        self.updateProps(obj)
        item = self.listTags.FindItem(-1, key)
        self.listTags.Select(item, True)
        self.listTags.EnsureVisible(item)
        self.tags = copy(obj.getAllTags())
    
    def onRemoveTag(self, evt):
        if self.listTags.GetSelectedItemCount() > 0:
            obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            item = self.listTags.GetFirstSelected()
            key = self.listTags.GetItemText(item)
            
            value = obj.nodePath.getTag(key)
            action = ActionGeneric(self.editor, lambda: obj.nodePath.clearTag(key), lambda: obj.nodePath.setTag(key, value))
            self.editor.actionMgr.push(action)
            action()
            
            self.updateProps(obj)
            self.tags = copy(obj.getAllTags())
    
    def onBeginEditTag(self, evt):
        self.editor.objectMgr.onEnterObjectPropUI(True)
        self.origTagString = evt.GetText()
    
    def onEditTag(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if evt.GetColumn() == 0:
            if evt.GetText() != self.origTagString:
                if obj.nodePath.hasTag(evt.GetText()):
                    evt.Veto()
                else:
                    oldKey = self.origTagString
                    newKey = evt.GetText()
                    action = ActionGeneric(self.editor, lambda: obj.renameTag(oldKey, newKey), lambda: obj.renameTag(newKey, oldKey))
                    self.editor.actionMgr.push(action)
                    action()
                    self.tags = copy(obj.getAllTags())
        elif evt.GetColumn() == 1:
            if evt.GetText() != self.origTagString:
                key = copy(self.listTags.GetItem(evt.GetItem().GetId(), 0).GetText())
                value = evt.GetText()
                oldValue = copy(obj.nodePath.getTag(key))
                action = ActionGeneric(self.editor, lambda: obj.nodePath.setTag(key,value), lambda: obj.nodePath.setTag(key, oldValue[:]))
                self.editor.actionMgr.push(action)
                action()
                self.tags = copy(obj.getAllTags())
        else:
            evt.Veto()
    
        self.listTags.Select(evt.GetItem().GetId(), True)
        self.editor.objectMgr.onLeaveObjectPropUI()   
        
    def toggleHide(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if obj.nodePath.isHidden():
            action = ActionGeneric(self.editor, obj.nodePath.show, obj.nodePath.hide)
            self.editor.actionMgr.push(action)
            action()
        else:
            action = ActionGeneric(self.editor, obj.nodePath.hide, obj.nodePath.show)
            self.editor.actionMgr.push(action)
            action()

    def toggleDoubleSided(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if obj.nodePath.getTwoSided():
            action = ActionGeneric(self.editor, lambda: obj.nodePath.setTwoSided(False),\
            lambda: obj.nodePath.setTwoSided(True))
            self.editor.actionMgr.push(action)
            action()
        else:
            action = ActionGeneric(self.editor, lambda: obj.nodePath.setTwoSided(True),\
            lambda: obj.nodePath.setTwoSided(False))
            self.editor.actionMgr.push(action)
            action()
    
    def toggleGround(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if obj.nodePath.hasTag('LE-ground'):
            action = ActionGeneric(self.editor, lambda: obj.nodePath.clearTag('LE-ground'),\
            lambda: obj.nodePath.setTag('LE-ground', '1'))
            self.editor.actionMgr.push(action)
            action()
        else:
            action = ActionGeneric(self.editor, lambda: obj.nodePath.setTag('LE-ground', '1'),\
            lambda: obj.nodePath.clearTag('LE-ground'))
            self.editor.actionMgr.push(action)
            action()
            
    def toggleWall(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if obj.nodePath.hasTag('LE-wall'):
            action = ActionGeneric(self.editor, lambda: obj.nodePath.clearTag('LE-wall'),\
            lambda: obj.nodePath.setTag('LE-wall', '1'))
            self.editor.actionMgr.push(action)
            action()
        else:
            action = ActionGeneric(self.editor, lambda: obj.nodePath.setTag('LE-wall', '1'),\
            lambda: obj.nodePath.clearTag('LE-wall'))
            self.editor.actionMgr.push(action)
            action()
    
    def renameObj(self, evt):
        newName = self.txtObjName.GetValue()
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if newName != obj.getName():
            if newName in self.editor.objectMgr.objects:
                dialog = wx.MessageDialog(self, "Name '" + newName + "'is already in use.", "Duplicate Name", wx.OK|wx.ICON_HAND)
                dialog.ShowModal()
                dialog.Destroy()
                self.txtObjName.SetValue(obj.getName())
            elif Util.toObjectName(newName) != newName:
                dialog = wx.MessageDialog(self, "Name '" + newName + "'is not a valid object name.", "Invalid Name", wx.OK|wx.ICON_HAND)
                dialog.ShowModal()
                dialog.Destroy()
                self.txtObjName.SetValue(obj.getName())
            else:
                oldName = obj.getName()
                action = ActionRenameObj(self.editor, oldName, newName)
                self.editor.actionMgr.push(action)
                action()

#panel for collider objects
class ColliderPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['collider'], 'colliderPanel')
        self.parent = parent
        
        self.rdoDecimal = xrc.XRCCTRL(self, "rdoDecimal")
        self.rdoBinary = xrc.XRCCTRL(self, "rdoBinary")
        self.txtFromMask = xrc.XRCCTRL(self, "txtFromMask")
        self.txtIntoMask = xrc.XRCCTRL(self, "txtIntoMask")
        self.chkTangible = xrc.XRCCTRL(self, "chkTangible")
        
        self.txtFromMask.Bind(wx.EVT_TEXT_ENTER, self.updateFromMask)
        self.txtIntoMask.Bind(wx.EVT_TEXT_ENTER, self.updateIntoMask)
        self.chkTangible.Bind(wx.EVT_CHECKBOX, self.toggleTangible)
        
        self.rdoDecimal.Bind(wx.EVT_RADIOBUTTON, self.switchToDecimal)
        self.rdoBinary.Bind(wx.EVT_RADIOBUTTON, self.switchToBinary)
        self.mode = 'binary'
        
    def updateProps(self, obj=None):
        if not obj:
                obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if isinstance(obj, Collider):
            if self.mode == 'decimal':
                self.txtFromMask.SetValue(str(obj.getFromCollideMask()))
                self.txtIntoMask.SetValue(str(obj.getIntoCollideMask()))
            else:
                self.txtFromMask.SetValue(bin(obj.getFromCollideMask())[2:])
                self.txtIntoMask.SetValue(bin(obj.getIntoCollideMask())[2:])
            
            self.chkTangible.SetValue(obj.isTangible())
    
    def switchToBinary(self, evt=None):
        self.mode = 'binary'
        self.updateProps()
        
    def switchToDecimal(self, evt=None):
        self.mode = 'decimal'
        self.updateProps()
            
    def updateFromMask(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            if self.rdoDecimal.GetValue():
                fromMask = int(self.txtFromMask.GetValue())
            else:
                fromMask = int(self.txtFromMask.GetValue(),2)
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            if self.mode == 'decimal':
                self.txtFromMask.SetValue(str(obj.getFromCollideMask()))
            else:
                self.txtFromMask.SetValue(bin(obj.getFromCollideMask())[2:])
        else:
            action = ActionSetProperty(self.editor, obj.setFromCollideMask, obj.getFromCollideMask, fromMask)
            self.editor.actionMgr.push(action)
            action()
    def updateIntoMask(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            if self.mode == 'decimal':
                intoMask = int(self.txtIntoMask.GetValue())
            else:
                intoMask = int(self.txtIntoMask.GetValue(),2)
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            if self.rdoDecimal.GetValue():
                self.txtIntoMask.SetValue(str(obj.getIntoCollideMask()))
            else:
                self.txtIntoMask.SetValue(bin(obj.getIntoCollideMask())[2:])
        else:
            action = ActionSetProperty(self.editor, obj.setIntoCollideMask, obj.getIntoCollideMask, intoMask)
            self.editor.actionMgr.push(action)
            action()
            
    def toggleTangible(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        t = self.chkTangible.GetValue()
        action = ActionSetProperty(self.editor, obj.setTangible, obj.isTangible, t)
        self.editor.actionMgr.push(action)
        action()
       
class ShaderPaneDropTarget(wx.TextDropTarget):
    def __init__(self, editor):
        wx.TextDropTarget.__init__(self)
        self.editor = editor
        
    def OnDropText(self, x, y, text):
        #Check that the dropped item is actually a shader
        if text.find('>') == -1:
            return
        if text.split('>')[0] != 'Shaders':
            return
            
        assetName = text.split('>')[-1]
        asset = self.editor.lib.shaders[assetName]
        self.editor.ui.objectPropertyUI.shaderPanel.setShaderFromAsset(asset)
        
#panel for shaders        
class ShaderPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['shader'], 'shaderPanel')
        self.parent = parent
        #UI elements
        self.btnUseAutoShader = xrc.XRCCTRL(self, "btnUseAutoShader")
        self.listInputs = xrc.XRCCTRL(self, "listInputs")
        self.btnAddInput = xrc.XRCCTRL(self, "btnAddInput")
        self.btnRemoveInput = xrc.XRCCTRL(self, "btnRemoveInput")
        self.btnApply = xrc.XRCCTRL(self, "btnApply")

        self.lblCurrentShaderName = xrc.XRCCTRL(self, "lblCurrentShaderName")
        
        self.panelFloat4 = xrc.XRCCTRL(self, "panelFloat4")
        self.panelFloat3 = xrc.XRCCTRL(self, "panelFloat3")
        self.panelFloat4x4 = xrc.XRCCTRL(self, "panelFloat4x4")
        self.panelFloat = xrc.XRCCTRL(self, "panelFloat")
        self.panelNodepath = xrc.XRCCTRL(self, "panelNodepath")
        self.panelCamera = xrc.XRCCTRL(self, "panelCamera")
        self.panelTime = xrc.XRCCTRL(self, "panelTime")
        self.panelTexture = xrc.XRCCTRL(self, "panelTexture")
        self.panelCubemap = xrc.XRCCTRL(self, "panelCubeMap")
        
        self.panelFloat4 = Float4InputPanel(self.panelFloat4)
        self.panelFloat3 = Float3InputPanel(self.panelFloat3)
        self.panelFloat4x4 = Float4x4InputPanel(self.panelFloat4x4)
        self.panelFloat = FloatInputPanel(self.panelFloat)
        self.panelNodepath = NodepathInputPanel(self.panelNodepath)
        self.panelCamera = CameraInputPanel(self.panelCamera)
        self.panelTime = TimeInputPanel(self.panelTime)
        self.panelTexture = TextureInputPanel(self.panelTexture)
        self.panelCubemap = CubemapInputPanel(self.panelCubemap)
        
        
        for w in self.GetChildren():
            w.Unbind(wx.EVT_SET_FOCUS)
            
        self.panels = (self.panelFloat4, self.panelFloat3, self.panelFloat4x4, self.panelFloat,\
        self.panelNodepath, self.panelCamera, self.panelTime, self.panelTexture, self.panelCubemap)
        self.Bind(wx.EVT_CHILD_FOCUS, self.onChildFocus)
        for p in self.panels:
            p.panel.Bind(wx.EVT_BUTTON, self.onUpdate)
            p.panel.Bind(wx.EVT_TEXT_ENTER, self.onUpdate)
            p.panel.Bind(wx.EVT_CHILD_FOCUS, self.onChildFocus)
            for w in p.panel.GetChildren():
                if isinstance(w, wx.TextCtrl):
                    #w.Bind(wx.EVT_SET_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(True))
                    w.Bind(wx.EVT_KILL_FOCUS, lambda(evt): self.editor.objectMgr.onLeaveObjectPropUI(True))
                else:
                    w.Bind(wx.EVT_KILL_FOCUS, lambda(evt): self.editor.objectMgr.onLeaveObjectPropUI(False))
                    
        self.SetDropTarget(ShaderPaneDropTarget(self.editor))
        
        for p in self.panels:
            p.Hide()
            #self.Sizer.Detach(p.panel)
            
        self.Sizer.SetRows(len(self.Sizer.GetChildren()))    
        self.Sizer.RecalcSizes()
        self.Sizer.Layout()    
        self.Layout()
        self.Refresh()
        
        self.shader = None
        
        #Bind event handlers
        self.btnAddInput.Bind(wx.EVT_BUTTON, self.OnNewInput)
        self.listInputs.Bind(wx.EVT_LISTBOX, self.onSelectInput)
        self.btnRemoveInput.Bind(wx.EVT_BUTTON, self.onRemoveInput)
        self.btnUseAutoShader.Bind(wx.EVT_BUTTON, self.onSetAutoShader)
        self.btnApply.Bind(wx.EVT_BUTTON, self.onApply)
    
    def onChildFocus(self, evt):
        if isinstance(evt.GetWindow(), wx.TextCtrl):
            self.editor.objectMgr.onEnterObjectPropUI(True)
        else:
            self.editor.objectMgr.onEnterObjectPropUI(False)    
    
    def updateProps(self, obj):
        if obj.shader:
            self.setShader(obj.shader)
        else:
            self.setAutoShader()
    
    def onSelectInput(self, evt=None):
        for p in self.panels:
            p.Hide()
            #self.Sizer.Detach(p.panel)
        if self.listInputs.GetSelection() != -1:
            self.input = self.shader.inputs[self.listInputs.GetStringSelection()]
            inputType = self.input.__class__.__name__
            if inputType == "LEShaderInputFloat":
                self.activePanel = self.panelFloat
            elif inputType == "LEShaderInputFloat4":
                self.activePanel = self.panelFloat4
            elif inputType == "LEShaderInputFloat3":
                self.activePanel = self.panelFloat3
            elif inputType == "LEShaderInputFloat4x4":
                self.activePanel = self.panelFloat4x4
            elif inputType == "LEShaderInputObj":
                self.activePanel = self.panelNodepath
            elif inputType == "LEShaderInputCameraPos":
                self.activePanel = self.panelCamera
            elif inputType == "LEShaderInputTime":
                self.activePanel = self.panelTime
            elif inputType == "LEShaderInputTexture":
                self.activePanel = self.panelTexture
            elif inputType == "LEShaderInputCubemap":
                self.activePanel = self.panelCubemap
            #self.Sizer.Add(self.activePanel.panel)
            self.activePanel.Show()
            self.activePanel.setFromInput(self.input)
            self.activePanel.setName(self.input.name)
        else:
            self.input = None

        self.Sizer.SetRows(len(self.Sizer.GetChildren()))
        self.Sizer.RecalcSizes()
        self.Sizer.Layout()
        self.Layout()
        self.Refresh()
    
    def setInputName(self, input, newName):
        oldName = input.name[:]
        self.shader.renameInput(oldName, newName)
        self.activePanel.setName(newName)
        index = self.listInputs.FindString(oldName)
        self.listInputs.SetString(index, newName)
        
    def getInputName(self, input):
        return input.name
    
    def onUpdate(self, evt=None):
        try:
            self.activePanel.setOnInput(self.input)
            name = self.activePanel.getName()
                
            if name != self.input.name:
                if name in self.shader.inputs:
                    raise DuplicateInputError(name)
                i = self.input
                setter = lambda x: self.setInputName(i, x)
                getter = lambda : self.getInputName(i)
                action = ActionSetProperty(self.editor, setter, getter, name)
                self.editor.actionMgr.push(action)
                action()
                
            self.shader.changed = True

                
        except ValueError as e:
            dlg = wx.MessageDialog(self, e.message, caption="Invalid Input", style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
            self.activePanel.setValue(self.input.getValue())
        
        except DuplicateInputError as e:
            msg = "Name '" + e.name + "' already in use."
            dlg = wx.MessageDialog(self, msg, caption="Duplicate Input Name", style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
            self.activePanel.setName(self.input.name)
    
    def onRemoveInput(self, evt):
        name = self.listInputs.GetStringSelection()
        input = self.shader.inputs[name]
        action = ActionGeneric(self.editor, lambda : self.removeInput(name), lambda : self.addInput(input))
        self.editor.actionMgr.push(action)
        action()

    def removeInput(self, inputName):
        index = self.listInputs.FindString(inputName)
        self.shader.clearInput(inputName)
        self.listInputs.Delete(index)
        self.onSelectInput()
        self.shader.changed = True
        
    def addInput(self, input):
        self.shader.setInput(input)
        self.listInputs.Append(input.name)
        self.listInputs.Select(self.listInputs.GetCount()-1)
        self.onSelectInput()
        self.shader.changed = True
    
    def setShaderFromAsset(self, asset):
        shader = LEShader(asset, inputs={})
        action = ActionGeneric(self.editor, lambda : self.setShader(shader), self.setAutoShader)      
        self.editor.actionMgr.push(action)
        action()
    
    def setShader(self, shader):
        if shader != self.shader or shader.changed:
            self.shader = shader
            self.btnAddInput.Enable(True)
            self.btnRemoveInput.Enable(True)
            self.listInputs.Enable(True)
            self.btnUseAutoShader.Enable(True)
            self.btnApply.Enable(True)
            if shader.obj:
                self.btnApply.SetLabel('Un-Apply Shader to Object')
            else:
                self.btnApply.SetLabel('Apply Shader to Object')
            self.listInputs.DeselectAll()
            self.listInputs.Clear()
            self.lblCurrentShaderName.SetLabel(shader.asset.name)
            
            for name in self.shader.inputs.keys():
                self.listInputs.Append(name)
                
            self.onSelectInput()
            shader.changed = False
    
    def onSetAutoShader(self, evt=None):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        s = obj.shader
        active = s.obj != None
        def undo():
            obj.useShader(s)
            if active:
                obj.applyShader()
        action = ActionGeneric(self.editor, obj.useAutoShader, undo)
        self.editor.actionMgr.push(action)
        action()
        self.updateProps(obj)
    
    def setAutoShader(self):
        self.shader = None
        self.btnAddInput.Enable(False)
        self.btnRemoveInput.Enable(False)
        self.listInputs.Enable(False)
        self.listInputs.Clear()
        self.btnUseAutoShader.Enable(False)
        self.btnApply.Enable(False)
        self.btnApply.SetLabel("Apply Shader To Object")
        self.lblCurrentShaderName.SetLabel("Auto shader")
        for p in self.panels:
            p.Hide()
    
    def onApply(self, evt=None):
        if not self.shader.obj:
            action = ActionGeneric(self.editor, self.apply, self.unApply)
        else:
            action = ActionGeneric(self.editor, self.unApply, self.apply)
            
        self.editor.actionMgr.push(action)
        action()
    
    def apply(self):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.applyShader()
        self.btnApply.SetLabel('Un-Apply Shader to Object')
    
    def unApply(self):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.unapplyShader()
        self.btnApply.SetLabel('Apply Shader to Object')
    
    def OnNewInput(self, e):
        dlg = ShaderInputDialog(self, -1, "Input")
        name, inputType = dlg.ShowModal()
        
        if name and inputType:
            if inputType == "float":
                i = LEShaderInputFloat(name)
            elif inputType == "float3":
                i = LEShaderInputFloat3(name)
            elif inputType == "float4":
                i = LEShaderInputFloat4(name)
            elif inputType == "float4x4":
                i = LEShaderInputFloat4x4(name)
            elif inputType == "object":
                i = LEShaderInputObj(name)
            elif inputType == "camera position":
                i = LEShaderInputCameraPos(name)
            elif inputType == "time":
                i = LEShaderInputTime(name)
            elif inputType == "texture":
                i = LEShaderInputTexture(name)
            elif inputType == "cube map":
                i = LEShaderInputCubemap(name)
                
            action = ActionGeneric(self.editor, lambda : self.addInput(i), lambda : self.removeInput(i.name))
            self.editor.actionMgr.push(action)
            action()

#panel for lights            
class LightPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['light'], 'lightPanel')
        self.editor = editor
        # Sliders
        self.slColorR = xrc.XRCCTRL(self, "slColorR")
        self.slColorR.SetRange(0, 255)
        self.slColorG = xrc.XRCCTRL(self, "slColorG")
        self.slColorG.SetRange(0, 255)
        self.slColorB = xrc.XRCCTRL(self, "slColorB")
        self.slColorB.SetRange(0, 255)
        self.slIntensity = xrc.XRCCTRL(self, "slIntensity")
        self.slIntensity.SetRange(0, 255)
        
        self.colorSliders = (self.slColorR, self.slColorG, self.slColorB)
        
        for x in self.colorSliders:
            x.Bind(wx.EVT_SCROLL, self.updateLightColorSlidersNoAction)
            x.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateLightColorSliders)
            
        self.slIntensity.Bind(wx.EVT_SCROLL, self.updateIntensitySliderNoAction)
        self.slIntensity.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateIntensitySlider)
        
        # Text boxes
        self.txtColorR = xrc.XRCCTRL(self, "txtColorR")
        self.txtColorG = xrc.XRCCTRL(self, "txtColorG")
        self.txtColorB = xrc.XRCCTRL(self, "txtColorB")
        self.txtIntensity = xrc.XRCCTRL(self, "txtIntensity")
        
        self.colorTextBoxes = (self.txtColorR, self.txtColorG, self.txtColorB)
        
        for x in self.colorTextBoxes:
            x.Bind(wx.EVT_TEXT_ENTER, self.updateLightColorTextBoxes)
        
        self.txtIntensity.Bind(wx.EVT_TEXT_ENTER, self.updateIntensityTextBox)
        
        # Shadow casting check box
        self.chkShadows = xrc.XRCCTRL(self, "chkShadows")
        self.chkShadows.Bind(wx.EVT_CHECKBOX, self.toggleShadows)
        # Shadow buffer text boxes
        self.txtBuffer = xrc.XRCCTRL(self, "txtBuffer")
        self.txtBuffer.Bind(wx.EVT_TEXT_ENTER, self.updateBuffer)
        
        # Sliders
        self.slSpecColorR = xrc.XRCCTRL(self, "slSpecR")
        self.slSpecColorR.SetRange(0, 255)
        self.slSpecColorG = xrc.XRCCTRL(self, "slSpecG")
        self.slSpecColorG.SetRange(0, 255)
        self.slSpecColorB = xrc.XRCCTRL(self, "slSpecB")
        self.slSpecColorB.SetRange(0, 255)
        self.slSpecColorI = xrc.XRCCTRL(self, "slSpecI")
        self.slSpecColorI.SetRange(0, 255)
        
        self.specSliders = (self.slSpecColorR, self.slSpecColorG, self.slSpecColorB)
        
        self.slSpecColorI.Bind(wx.EVT_SCROLL, self.updateLightSpecIntensitySliderNoAction)
        self.slSpecColorI.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateLightSpecIntensitySlider)
        
        for x in self.specSliders:
            x.Bind(wx.EVT_SCROLL, self.updateLightSpecColorSlidersNoAction)
            x.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateLightSpecColorSliders)
        
        # Text boxes
        self.txtSpecR = xrc.XRCCTRL(self, "txtSpecR")
        self.txtSpecG = xrc.XRCCTRL(self, "txtSpecG")
        self.txtSpecB = xrc.XRCCTRL(self, "txtSpecB")
        self.txtSpecI = xrc.XRCCTRL(self, "txtSpecI")
        
        self.specTextBoxes = (self.txtSpecR, self.txtSpecG, self.txtSpecB)
        
        for x in self.specTextBoxes:
            x.Bind(wx.EVT_TEXT_ENTER, self.updateLightSpecColorTextBoxes)
        
        self.txtSpecI.Bind(wx.EVT_TEXT_ENTER, self.updateLightSpecIntensityTextBox)
        
        # Sliders
        self.slAttenX = xrc.XRCCTRL(self, "slAttenX")
        self.slAttenX.SetRange(0,1000000)
        self.slAttenY = xrc.XRCCTRL(self, "slAttenY")
        self.slAttenY.SetRange(0,50000)
        self.slAttenZ = xrc.XRCCTRL(self, "slAttenZ")
        self.slAttenZ.SetRange(0,50)
        
        self.attenSliders = (self.slAttenX, self.slAttenY, self.slAttenZ)
        
        for x in self.attenSliders:
            x.Bind(wx.EVT_SCROLL, self.updateLightAttenuationSlidersNoAction)
            x.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateLightAttenuationSliders)
        
        # Text boxes
        self.txtAttenX = xrc.XRCCTRL(self, "txtAttenX")
        self.txtAttenY = xrc.XRCCTRL(self, "txtAttenY")
        self.txtAttenZ = xrc.XRCCTRL(self, "txtAttenZ")
        
        self.attenTextBoxes = (self.txtAttenX, self.txtAttenY, self.txtAttenZ)
        
        for x in self.attenTextBoxes:
            x.Bind(wx.EVT_TEXT_ENTER, self.updateLightAttenuationTextBoxes)
        
        self.slExponent = xrc.XRCCTRL(self, "slExponent")
        self.slExponent.SetRange(0,128)
        self.slExponent.Bind(wx.EVT_SCROLL, self.updateLightExponentSliderNoAction)
        self.slExponent.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateLightExponentSlider)
        self.txtExponent = xrc.XRCCTRL(self, "txtExponent")
        self.txtExponent.Bind(wx.EVT_TEXT_ENTER, self.updateLightExponentTextBox)
        
        ###Target object stuff
        self.btnAddTarget = xrc.XRCCTRL(self, "btnAdd")
        self.btnRemoveTarget = xrc.XRCCTRL(self, "btnRemove")
        self.listTarget = xrc.XRCCTRL(self, "listBoxTargets")
        
        self.btnAddTarget.Bind(wx.EVT_BUTTON, self.onAddTarget)
        self.btnRemoveTarget.Bind(wx.EVT_BUTTON, self.onRemoveTarget)
        
        self.origColor = None
        self.origAtten = None
        self.origExponent = None
        
        #hack to make list box work
        for w in self.GetChildren():
            w.Unbind(wx.EVT_SET_FOCUS)
        
        self.Bind(wx.EVT_CHILD_FOCUS, self.onChildFocus)    
        
    def onChildFocus(self, evt):
        if isinstance(evt.GetWindow(), wx.TextCtrl):
            self.editor.objectMgr.onEnterObjectPropUI(True)
        else:
            self.editor.objectMgr.onEnterObjectPropUI(False)
    
    def onAddTarget(self, evt):
        dlg = ObjectInputDialog(self)
        targetName = dlg.ShowModal()
        dlg.Destroy()
        if targetName:
            obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            target = self.editor.objectMgr.findObjectById(targetName)
            
            if target in obj.targets:
                msg = wx.MessageDialog(self, "Already a target of this light", "", wx.OK|wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
            else:
                action = ActionGeneric(self.editor, lambda : obj.addTarget(target), lambda : obj.removeTarget(target))
                self.editor.actionMgr.push(action)
                action()
                #obj.addTarget(target)
                self.listTarget.Append(targetName)
        
    def onRemoveTarget(self, evt):
        targetName = self.listTarget.GetStringSelection()
        target = base.le.objectMgr.findObjectById(targetName)
        if target:
            obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            action = ActionGeneric(self.editor, lambda : obj.removeTarget(target), lambda : obj.addTarget(target))
            self.editor.actionMgr.push(action)
            action()
            #obj.removeTarget(target)
            self.listTarget.Delete(self.listTarget.GetSelection())
                
    def updateProps(self, obj):
        if isinstance(obj, LELight):
            self.listTarget.Clear()
            for target in obj.targets:
                #is this in the scene at all?
                if target.name in self.editor.objectMgr.objects:
                    self.listTarget.Append(target.name)
            for i in range(0, len(self.colorSliders)):
                self.colorSliders[i].Enable(True)
                self.colorSliders[i].SetValue(int(obj.getColor()[i]*255))
                self.colorTextBoxes[i].Enable(True)
                self.colorTextBoxes[i].SetValue(str(obj.getColor()[i]))
            
            intensity = max(obj.getColor()[0], obj.getColor()[1], obj.getColor()[2])
            self.slIntensity.SetValue(int(intensity * 255))
            self.txtIntensity.SetValue(str(intensity))
            
            # If it is not an ambient light
            if isinstance(obj, PoiLight) or isinstance(obj, DirLight) or isinstance(obj, SpoLight):
                for i in range(0, len(self.specSliders)):
                    self.specSliders[i].Enable(True)
                    self.specSliders[i].SetValue(int(obj.getSpecularColor()[i]*255))
                    self.specTextBoxes[i].Enable(True)
                    self.specTextBoxes[i].SetValue(str(obj.getSpecularColor()[i]))
                
                specIntensity = max(obj.getSpecularColor()[0], obj.getSpecularColor()[1], obj.getSpecularColor()[2])
                    
                self.slSpecColorI.Enable(True)
                self.slSpecColorI.SetValue(int(specIntensity*255))
                self.txtSpecI.Enable(True)
                self.txtSpecI.SetValue(str(specIntensity))
                
                # If not a directional light
                if not isinstance(obj, DirLight):
                    # Set attenuation field with values
                    for i in range(0, len(self.attenSliders)):
                        self.attenSliders[i].Enable(True)
                        self.attenSliders[i].SetValue(int(obj.light.getAttenuation()[i]*1000000))
                        self.attenTextBoxes[i].Enable(True)
                        self.attenTextBoxes[i].SetValue(str(obj.light.getAttenuation()[i]))
                        
                # If it is a directional light
                else:
                    # Disable attenuation fields
                    for i in range(0, len(self.attenSliders)):
                        self.attenSliders[i].Enable(False)
                        self.attenSliders[i].SetValue(0)
                        self.attenTextBoxes[i].Enable(False)
                        self.attenTextBoxes[i].SetValue("")
                
                # If it is a spot light
                if isinstance(obj, SpoLight):
                    # Allow changes to the exponent
                    # slider
                    self.slExponent.Enable(True)
                    self.slExponent.SetValue(int(obj.light.getExponent()))
                    # text box
                    self.txtExponent.Enable(True)
                    self.txtExponent.SetValue(str(obj.light.getExponent()))
                    
                    # Shadows
                    self.chkShadows.Enable(True)
                    self.chkShadows.SetValue(obj.castsShadows)
                    # Buffer size
                    if obj.castsShadows:                    
                        self.txtBuffer.Enable(True)
                        self.txtBuffer.SetValue(str(obj.bufferX))
                    else:
                        self.txtBuffer.Enable(False)
                        self.txtBuffer.SetValue("")
                        
                # Otherwise
                else:
                    # Disable exponent value
                    # slider
                    self.slExponent.Enable(False)
                    self.slExponent.SetValue(0)
                    # text box
                    self.txtExponent.Enable(False)
                    self.txtExponent.SetValue("")
                    # Shadows
                    self.chkShadows.Enable(False)
                    self.chkShadows.SetValue(False)
                    self.txtBuffer.Enable(False)
                    self.txtBuffer.SetValue("")
            # If it is an ambient light
            else:     
                # Shadow check box
                self.chkShadows.Enable(False)
                self.chkShadows.SetValue(False)
                self.txtBuffer.Enable(False)
                self.txtBuffer.SetValue("") 
                # Specular Color
                for i in range(0, len(self.specSliders)):
                    self.specSliders[i].Enable(False)
                    self.specSliders[i].SetValue(0)
                    self.specTextBoxes[i].Enable(False)
                    self.specTextBoxes[i].SetValue("")
                
                self.slSpecColorI.SetValue(0)
                self.slSpecColorI.Enable(False)
                self.txtSpecI.SetValue('')
                self.txtSpecI.Enable(False)
                    
                # Attenuation
                for i in range(0, len(self.attenSliders)):
                    self.attenSliders[i].Enable(False)
                    self.attenSliders[i].SetValue(0)
                    self.attenTextBoxes[i].Enable(False)
                    self.attenTextBoxes[i].SetValue("")
                
                # Exponent
                # slider
                self.slExponent.Enable(False)
                self.slExponent.SetValue(0)
                # text box
                self.txtExponent.Enable(False)
                self.txtExponent.SetValue("")
    
    #updates the light color without going through the action manager
    #this a ton of extraneous steps on the undo stack
    def updateLightColorSlidersNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.colorSliders)):
            sliders.append(float(self.colorSliders[i].GetValue() / 255.0))
            # update text boxes
            self.colorTextBoxes[i].SetValue(str(sliders[i]))

        color = Vec4(sliders[0],sliders[1],sliders[2], 1.0)
        
        intensity = max(color[0], color[1], color[2])
        self.slIntensity.SetValue(int(intensity*255))
        self.txtIntensity.SetValue(str(intensity))
        
        #record the original color for undo purposes
        if not self.origColor:
            self.origColor = copy(obj.getColor())
        
        obj.setColor(color)
            
    def updateLightColorSliders(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.colorSliders)):
            sliders.append(float(self.colorSliders[i].GetValue() / 255.0))
            # update text boxes
            self.colorTextBoxes[i].SetValue(str(sliders[i]))
        
        color = Vec4(sliders[0],sliders[1],sliders[2], 1.0)#,sliders[3])
        
        #set the color back to the original one so that when we undo
        #it will revert to that one
        if self.origColor:
            obj.setColor(self.origColor)
            self.origColor = None
        action = ActionSetProperty(self.editor, obj.setColor, obj.getColor, color)
        self.editor.actionMgr.push(action)
        action()
        
    def updateLightColorTextBoxes(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            textBoxes = []
            for i in range(0, len(self.colorTextBoxes)):
                val = float(self.colorTextBoxes[i].GetValue())
                # Make sure the value is between 0.0 and 1.0
                if val > 1.0:
                    val = 1.0
                    self.colorTextBoxes[i].SetValue(str(val))
                elif val < 0.0:
                    val = 0.0
                    self.colorTextBoxes[i].SetValue(str(val))
                textBoxes.append(val)
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            for i in range(0, len(self.colorTextBoxes)):
                self.colorTextBoxes[i].SetValue(str(obj.getColor()[i]))
        else:
            # update sliders
            for i in range(0, len(textBoxes)):
                self.colorSliders[i].SetValue(int(float(textBoxes[i] * 255)))
            color = Vec4(textBoxes[0],textBoxes[1],textBoxes[2], 1.0)
            action = ActionSetProperty(self.editor, obj.setColor, obj.getColor, color)
            self.editor.actionMgr.push(action)
            action()
            
            intensity = max(color[0], color[1], color[2])
            self.slIntensity.SetValue(int(intensity*255))
            self.txtIntensity.SetValue(str(intensity))
    
    def updateIntensitySliderNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        oldIntensity = max(obj.getColor()[0], obj.getColor()[1], obj.getColor()[2])
        
        newIntensity = self.slIntensity.GetValue() / 255.0
        
        if oldIntensity == 0:
            if self.origColor and (self.origColor[0] > 0 or self.origColor[1] > 0 or self.origColor[2] > 0):
                origIntensity = max(self.origColor[0], self.origColor[1], self.origColor[2])
                color = self.origColor * newIntensity/origIntensity
            else:
                color = VBase4(newIntensity, newIntensity, newIntensity, 1)
        else:
            color = obj.getColor() * (newIntensity/oldIntensity)
        
        self.txtIntensity.SetValue(str(newIntensity))
        
        for i in range(3):
            self.colorSliders[i].SetValue(int(color[i] * 255))
            self.colorTextBoxes[i].SetValue(str(color[i]))
            
        
        if not self.origColor:
            self.origColor = copy(obj.getColor())
            
        obj.setColor(color)
        
    def updateIntensitySlider(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        oldIntensity = max(obj.getColor()[0], obj.getColor()[1], obj.getColor()[2])
        
        newIntensity = self.slIntensity.GetValue() / 255.0
        
        if oldIntensity == 0:
            if self.origColor and (self.origColor[0] > 0 or self.origColor[1] > 0 or self.origColor[2] > 0):
                origIntensity = max(self.origColor[0], self.origColor[1], self.origColor[2])
                color = self.origColor * newIntensity/origIntensity
            else:
                color = VBase4(newIntensity, newIntensity, newIntensity, 1)
        else:
            color = obj.getColor() * (newIntensity/oldIntensity)
        
        self.txtIntensity.SetValue(str(newIntensity))
        
        for i in range(3):
            self.colorSliders[i].SetValue(int(color[i] * 255))
            self.colorTextBoxes[i].SetValue(str(color[i]))
            
        
        if self.origColor:
            obj.setColor(self.origColor)
            self.origColor = None
       
        action = ActionSetProperty(self.editor, obj.setColor, obj.getColor, color)
        self.editor.actionMgr.push(action)
        action()
        
    def updateIntensityTextBox(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        oldIntensity = max(obj.getColor()[0], obj.getColor()[1], obj.getColor()[2])
        
        newIntensity = float(self.txtIntensity.GetValue())
        if newIntensity > 1.0:
            newIntensity = 1.0
            self.txtIntensity.SetValue('1.0')
        
        if newIntensity < 0:
            newIntensity = 0
            self.txtIntensity.SetValue('0.0')
        
        if oldIntensity == 0:
            color = VBase4(newIntensity, newIntensity, newIntensity, 1)
        else:
            color = obj.getColor() * (newIntensity/oldIntensity)
        
        self.slIntensity.SetValue(int(newIntensity*255))
        
        for i in range(3):
            self.colorSliders[i].SetValue(int(color[i] * 255))
            self.colorTextBoxes[i].SetValue(str(color[i]))
            
        action = ActionSetProperty(self.editor, obj.setColor, obj.getColor, color)
        self.editor.actionMgr.push(action)
        action()
        
    
    def updateLightSpecColorSlidersNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.specSliders)):
            sliders.append(float(self.specSliders[i].GetValue() / 255.0))
            # update text boxes
            self.specTextBoxes[i].SetValue(str(sliders[i]))
        
        color = Vec4(sliders[0],sliders[1],sliders[2], 1.0)
        
        intensity = max(color[0], color[1], color[2])
        self.slSpecColorI.SetValue(int(intensity*255))
        self.txtSpecI.SetValue(str(intensity))
        
        if not self.origColor:
            self.origColor = copy(obj.getSpecularColor())
        
        obj.setSpecularColor(color)
    
    def updateLightSpecColorSliders(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.specSliders)):
            sliders.append(float(self.specSliders[i].GetValue() / 255.0))
            # update text boxes
            self.specTextBoxes[i].SetValue(str(sliders[i]))
        
        color = Vec4(sliders[0],sliders[1],sliders[2], 1.0)
        
        intensity = max(color[0], color[1], color[2])
        self.slSpecColorI.SetValue(int(intensity*255))
        self.txtSpecI.SetValue(str(intensity))
        
        if self.origColor:
            obj.setSpecularColor(self.origColor)
            self.origColor = None
        action = ActionSetProperty(self.editor, obj.setSpecularColor, obj.getSpecularColor, color)
        self.editor.actionMgr.push(action)
        action()
    
    def updateLightSpecColorTextBoxes(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            textBoxes = []
            for i in range(0, len(self.specTextBoxes)):
                val = float(self.specTextBoxes[i].GetValue())
                # Make sure the value is between 0.0 and 1.0
                if val > 1.0:
                    val = 1.0
                    self.specTextBoxes[i].SetValue(str(val))
                elif val < 0.0:
                    val = 0.0
                    self.specTextBoxes[i].SetValue(str(val))
                textBoxes.append(val)
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            for i in range(0, len(self.specTextBoxes)):
                self.specTextBoxes[i].SetValue(str(obj.getSpecularColor()[i]))
        else:
            # update sliders
            for i in range(0, len(textBoxes)):
                self.specSliders[i].SetValue(int(float(textBoxes[i] * 255)))
            color = Vec4(textBoxes[0],textBoxes[1],textBoxes[2], 1.0)
            
            intensity = max(color[0], color[1], color[2])
            self.slSpecColorI.SetValue(int(intensity*255))
            self.txtSpecI.SetValue(str(intensity))
            
            action = ActionSetProperty(self.editor, obj.setSpecularColor, obj.getSpecularColor, color)
            self.editor.actionMgr.push(action)
            action()
    
    def updateLightSpecIntensitySliderNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        oldIntensity = max(obj.getSpecularColor()[0], obj.getSpecularColor()[1], obj.getSpecularColor()[2])
        
        newIntensity = self.slSpecColorI.GetValue() / 255.0
        
        if oldIntensity == 0:
            if self.origColor and (self.origColor[0] > 0 or self.origColor[1] > 0 or self.origColor[2] > 0):
                origIntensity = max(self.origColor[0], self.origColor[1], self.origColor[2])
                color = self.origColor * newIntensity/origIntensity
            else:
                color = VBase4(newIntensity, newIntensity, newIntensity, 1)
        else:
            color = obj.getSpecularColor() * (newIntensity/oldIntensity)
        
        self.txtSpecI.SetValue(str(newIntensity))
        
        for i in range(3):
            self.specSliders[i].SetValue(int(color[i] * 255))
            self.specTextBoxes[i].SetValue(str(color[i]))
            
        
        if not self.origColor:
            self.origColor = copy(obj.getSpecularColor())
            
        obj.setSpecularColor(color)
        
    def updateLightSpecIntensitySlider(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        oldIntensity = max(obj.getSpecularColor()[0], obj.getSpecularColor()[1], obj.getSpecularColor()[2])
        
        newIntensity = self.slSpecColorI.GetValue() / 255.0
        
        if oldIntensity == 0:
            if self.origColor and (self.origColor[0] > 0 or self.origColor[1] > 0 or self.origColor[2] > 0):
                origIntensity = max(self.origColor[0], self.origColor[1], self.origColor[2])
                color = self.origColor * newIntensity/origIntensity
            else:
                color = VBase4(newIntensity, newIntensity, newIntensity, 1)
        else:
            color = obj.getSpecularColor() * (newIntensity/oldIntensity)
        
        self.txtSpecI.SetValue(str(newIntensity))
        
        for i in range(3):
            self.specSliders[i].SetValue(int(color[i] * 255))
            self.specTextBoxes[i].SetValue(str(color[i]))
            
        
        if self.origColor:
            obj.setSpecularColor(self.origColor)
            self.origColor = None
       
        action = ActionSetProperty(self.editor, obj.setSpecularColor, obj.getSpecularColor, color)
        self.editor.actionMgr.push(action)
        action()
        
    def updateLightSpecIntensityTextBox(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        oldIntensity = max(obj.getSpecularColor()[0], obj.getSpecularColor()[1], obj.getSpecularColor()[2])
        
        newIntensity = float(self.txtSpecI.GetValue())
        if newIntensity > 1.0:
            newIntensity = 1.0
            self.txtIntensity.SetValue('1.0')
        
        if newIntensity < 0:
            newIntensity = 0
            self.txtIntensity.SetValue('0.0')
        
        if oldIntensity == 0:
            color = VBase4(newIntensity, newIntensity, newIntensity, 1)
        else:
            color = obj.getSpecularColor() * (newIntensity/oldIntensity)
        
        self.slSpecColorI.SetValue(int(newIntensity*255))
        
        for i in range(3):
            self.specSliders[i].SetValue(int(color[i] * 255))
            self.specTextBoxes[i].SetValue(str(color[i]))
            
        action = ActionSetProperty(self.editor, obj.setSpecularColor, obj.getSpecularColor, color)
        self.editor.actionMgr.push(action)
        action()
    
    def updateLightAttenuationSlidersNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.attenSliders)):
            sliders.append(float(self.attenSliders[i].GetValue() / 1000000.0))
            self.attenTextBoxes[i].SetValue(str(sliders[i]))
        atten = Vec3(sliders[0],sliders[1],sliders[2])
        if not self.origAtten:
            self.origAtten = copy(obj.light.getAttenuation())
        obj.light.setAttenuation(atten)
    
    def updateLightAttenuationSliders(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.attenSliders)):
            sliders.append(float(self.attenSliders[i].GetValue() / 1000000.0))
            self.attenTextBoxes[i].SetValue(str(sliders[i]))
        atten = Vec3(sliders[0],sliders[1],sliders[2])
        if self.origAtten:
            obj.light.setAttenuation(self.origAtten)
            self.origAtten = None
        action = ActionSetProperty(self.editor, obj.light.setAttenuation, obj.light.getAttenuation, atten)
        self.editor.actionMgr.push(action)
        action()
    
    def updateLightAttenuationTextBoxes(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            textBoxes = []
            for i in range(0, len(self.attenTextBoxes)):
                val = float(self.attenTextBoxes[i].GetValue())
                # Make sure the value is between 0.0 and 1.0
                if val > 1.0:
                    val = 1.0
                    self.attenTextBoxes[i].SetValue(str(val))
                elif val < 0.0:
                    val = 0.0
                    self.attenTextBoxes[i].SetValue(str(val))
                textBoxes.append(val)
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            for i in range(0, len(self.attenTextBoxes)):
                self.specTextBoxes[i].SetValue(str(obj.getAttenuation()[i]))
        else:
            # update sliders
            for i in range(0, len(textBoxes)):
                self.attenSliders[i].SetValue(int(float(textBoxes[i] * 100)))
            atten = Vec3(textBoxes[0],textBoxes[1],textBoxes[2])
            action = ActionSetProperty(self.editor, obj.setAttenuation, obj.getAttenuation, atten)
            self.editor.actionMgr.push(action)
            action()
    
    def updateLightExponentSliderNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        exp = float(self.slExponent.GetValue())
        self.txtExponent.SetValue(str(exp))
        if not self.origExponent:
            self.origExponent = copy(obj.light.getExponent())
        obj.light.setExponent(exp)
    
    def updateLightExponentSlider(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        exp = float(self.slExponent.GetValue())
        self.txtExponent.SetValue(str(exp))
        if self.origExponent:
            obj.light.setExponent(self.origExponent)
            self.origExponent = None
        action = ActionSetProperty(self.editor, obj.light.setExponent, obj.light.getExponent, exp)
        self.editor.actionMgr.push(action)
        action()
    
    def updateLightExponentTextBox(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            val = float(self.txtExponent.GetValue())
            # Make sure the value is between 0.0 and 128.0
            if val > 128.0:
                val = 128.0
                self.txtExponent.SetValue(str(val))
            elif val < 0.0:
                val = 0.0
                self.txtExponent.SetValue(str(val))
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtExponent.SetValue(str(obj.getExponent()))
        else:
            # update slider
            self.slExponent.SetValue(int(val))
            action = ActionSetProperty(self.editor, obj.setExponent, obj.getExponent, val)
            self.editor.actionMgr.push(action)
            action()
    
    def updateBuffer(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            buffer = int(self.txtBuffer.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtBuffer.SetValue(str(obj.bufferX))
        else:
            action = ActionSetProperty(self.editor, obj.setBuffer, obj.getBuffer, buffer)
            self.editor.actionMgr.push(action)
            action()
    
    def toggleShadows(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if obj.getCastsShadows():
            action = ActionSetProperty(self.editor, obj.setCastsShadows, obj.getCastsShadows, False)
            #action = ActionGeneric(self.editor, obj.light.setShadowCaster, obj.light.setShadowCaster, False)
            self.editor.actionMgr.push(action)
            action()
            self.txtBuffer.Enable(False)
            self.txtBuffer.SetValue("")
            # Turn off the shaders
            #self.shadersOff()
            ## # Turn them back on, after waiting
            ## Sequence(Wait(1.0), Func(self.shadersOn)).start()
        else:
            action = ActionSetProperty(self.editor, obj.setCastsShadows, obj.getCastsShadows, True)
            #action = ActionGeneric(self.editor, obj.light.setShadowCaster, obj.light.setShadowCaster, True, 2048, 2048)
            self.editor.actionMgr.push(action)
            action()
            self.txtBuffer.Enable(True)
            self.txtBuffer.SetValue(str(obj.bufferX))
            # Turn off the shaders
            #self.shadersOff()
            ## # Turn them back on, after waiting
            ## Sequence(Wait(1.0), Func(self.shadersOn)).start()
    
    def shadersOff(self):
        objects = base.le.objectMgr.objects
        for object in objects:
            #if not isinstance(objects[object], Light):
            objects[object].nodePath.clearShader()
        
        # Turn the autoShader back on
        Sequence(Wait(1.0), Func(self.shadersOn)).start()
    
    def shadersOn(self):
        objects = base.le.objectMgr.objects
        for object in objects:
            #if not isinstance(objects[object], Light):
            objects[object].nodePath.setShaderAuto()

class TextureListDropTarget(wx.TextDropTarget):
    def __init__(self, editor):
        wx.TextDropTarget.__init__(self)
        self.editor = editor
        
    def OnDropText(self, x, y, text):
        if text.find('>') == -1:
            return
            
        if text.split('>')[0] != 'Textures':
            return
            
        assetName = text.split('>')[-1]
        asset = self.editor.lib.textures[assetName]
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        id, flags = self.editor.ui.objectPropertyUI.appearancePanel.listTextures\
        .HitTest(wx.Point(x, y))
        
        if id == -1:
            return
            
        action = ActionReplaceTexture(self.editor, obj, id, asset)
        self.editor.actionMgr.push(action)
        action()
        self.editor.ui.objectPropertyUI.appearancePanel.texList = []
        base.le.ui.objectPropertyUI.updateProps(obj)
                
class AppearancePropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['appearance'], 'appearancePanel')
        
        self.slColorR = xrc.XRCCTRL(self, "slColorR")
        self.slColorR.SetRange(0, 255)
        self.slColorG = xrc.XRCCTRL(self, "slColorG")
        self.slColorG.SetRange(0, 255)
        self.slColorB = xrc.XRCCTRL(self, "slColorB")
        self.slColorB.SetRange(0, 255)
        self.slColorA = xrc.XRCCTRL(self, "slColorA")
        self.slColorA.SetRange(0, 255)
        
        self.colorSliders = (self.slColorR, self.slColorG, self.slColorB, self.slColorA)
        
        for x in self.colorSliders:
            x.Bind(wx.EVT_SCROLL, self.updateLightColorSlidersNoAction)
            x.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updateLightColorSliders)
        
        # Text boxes
        self.txtColorR = xrc.XRCCTRL(self, "txtColorR")
        self.txtColorG = xrc.XRCCTRL(self, "txtColorG")
        self.txtColorB = xrc.XRCCTRL(self, "txtColorB")
        self.txtColorA = xrc.XRCCTRL(self, "txtColorA")

        
        self.colorTextBoxes = (self.txtColorR, self.txtColorG, self.txtColorB, self.txtColorA)
        
        for x in self.colorTextBoxes:
            x.Bind(wx.EVT_TEXT_ENTER, self.updateLightColorTextBoxes)
        
        self.listTextures = xrc.XRCCTRL(self, "listTextures")
        self.listTextures.SetDropTarget(TextureListDropTarget(self.editor))
        
        self.btnRestoreTextures = xrc.XRCCTRL(self, "btnRestoreTextures")
        self.btnRestoreTextures.Bind(wx.EVT_BUTTON, self.restoreTextures)
        
        self.texList = []
        self.origColor = None
    
    def restoreTextures(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        action = ActionClearTextureSwaps(self.editor, obj)
        self.editor.actionMgr.push(action)
        action()
        self.texList = []
        
    def updateLightColorSlidersNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.colorSliders)):
            sliders.append(float(self.colorSliders[i].GetValue() / 255.0))
            # update text boxes
            self.colorTextBoxes[i].SetValue(str(sliders[i]))
        
        color = Vec4(sliders[0],sliders[1],sliders[2], sliders[3])#,sliders[3])
        if not self.origColor:
            self.origColor = copy(obj.getColorScale())
        obj.setColorScale(color)
    
    def updateLightColorSliders(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        sliders = []
        for i in range(0, len(self.colorSliders)):
            sliders.append(float(self.colorSliders[i].GetValue() / 255.0))
            # update text boxes
            self.colorTextBoxes[i].SetValue(str(sliders[i]))
        
        color = Vec4(sliders[0],sliders[1],sliders[2], sliders[3])#,sliders[3])
        
        if self.origColor:
            obj.setColorScale(self.origColor)
            self.origColor = None
        action = ActionSetProperty(self.editor, obj.setColorScale, obj.getColorScale, color)
        self.editor.actionMgr.push(action)
        action()
        
    def updateLightColorTextBoxes(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            textBoxes = []
            for i in range(0, len(self.colorTextBoxes)):
                val = float(self.colorTextBoxes[i].GetValue())
                # Make sure the value is between 0.0 and 1.0
                if val > 1.0:
                    val = 1.0
                    self.colorTextBoxes[i].SetValue(str(val))
                elif val < 0.0:
                    val = 0.0
                    self.colorTextBoxes[i].SetValue(str(val))
                textBoxes.append(val)
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            for i in range(0, len(self.colorTextBoxes)):
                self.colorTextBoxes[i].SetValue(str(obj.getColorScale()[i]))
        else:
            # update sliders
            for i in range(0, len(textBoxes)):
                self.colorSliders[i].SetValue(int(float(textBoxes[i] * 255)))
            color = Vec4(textBoxes[0],textBoxes[1],textBoxes[2], (textBoxes[3] ))#,textBoxes[3])
            action = ActionSetProperty(self.editor, obj.setColorScale, obj.getColorScale, color)
            self.editor.actionMgr.push(action)
            action()    
    def updateProps(self, obj):
        if isinstance(obj, LEActor) or isinstance(obj, StaticMesh):
            for i in range(0, len(self.colorSliders)):
                self.colorSliders[i].Enable(True)
                self.colorSliders[i].SetValue(int(obj.getColorScale()[i]*255))
                self.colorTextBoxes[i].Enable(True)
                self.colorTextBoxes[i].SetValue(str(obj.getColorScale()[i]))
           
            self.listTextures.Enable(True)
            self.btnRestoreTextures.Enable(True)
            imgList = wx.ImageList(60, 60)
            texList = obj.getTexList()       
            for tex in texList:
                try:
                    imgList.Add(wx.Bitmap(tex.getThumbnail().toOsSpecific()))
                except:
                    imgList.Add(wx.Bitmap('default_thumb.jpg'))
                    
            if texList != self.texList:            
                self.listTextures.ClearAll()
                self.listTextures.AssignImageList(imgList, wx.IMAGE_LIST_NORMAL)        
                for i, tex in enumerate(texList):
                    if tex:
                        label = tex.name
                    else:
                        label = 'Unknown Texture'
                    self.listTextures.InsertImageStringItem(i, label, i)
                
            self.texList = copy(texList)    
        elif isinstance(obj, LETerrain) or isinstance(obj, LETextureCard):
            for i in range(0, len(self.colorSliders)):
                self.colorSliders[i].Enable(True)
                self.colorSliders[i].SetValue(int(obj.getColorScale()[i]*255))
                self.colorTextBoxes[i].Enable(True)
                self.colorTextBoxes[i].SetValue(str(obj.getColorScale()[i]))
              
            self.listTextures.ClearAll() 
            self.listTextures.Disable()
            self.btnRestoreTextures.Disable()
            self.texList = []
            
class ActorPaneDropTarget(wx.TextDropTarget):
    def __init__(self, editor):
        wx.TextDropTarget.__init__(self)
        self.editor = editor
        
    def OnDropText(self, x, y, text):
        #Check that the dropped item is actually an animation
        if text.find('>') == -1:
            return
        if text.split('>')[0] != 'Animations':
            return
            
        assetName = text.split('>')[-1]
        asset = self.editor.lib.animations[assetName]
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.addExtraAnim(asset)
        base.le.ui.objectPropertyUI.updateProps(obj)

                
class ActorPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['actor'], 'actorPanel')
        
        self.SetDropTarget(ActorPaneDropTarget(self.editor))
        
        # Anims list
        self.cboxAnimNameList = xrc.XRCCTRL(self, "cboxAnimNameList")
        self.cboxAnimNameList.Bind(wx.EVT_COMBOBOX, self.updateAnimList)
        
        self.listSet = False
        
        # Play rate text box
        self.txtPlayRate = xrc.XRCCTRL(self, "txtPlayRate")
        self.txtPlayRate.Bind(wx.EVT_TEXT_ENTER, self.updatePlayRate)
        
        # Frame text box
        self.txtFrame = xrc.XRCCTRL(self, "txtFrame")
        self.txtFrame.Bind(wx.EVT_TEXT_ENTER, self.updatePoseBox) 
        
        # Frame slider
        self.slFrame = xrc.XRCCTRL(self, "slFrame")
        self.slFrame.Bind(wx.EVT_SCROLL, self.updatePoseSliderNoAction)
        self.slFrame.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updatePoseSlider)
        
        # Controls
        
        # Play
        self.rdoPlay = xrc.XRCCTRL(self, "rdoPlay")
        self.rdoPlay.Bind(wx.EVT_RADIOBUTTON, self.playRadio)
        
        # Loop
        self.rdoLoop = xrc.XRCCTRL(self, "rdoLoop")
        self.rdoLoop.Bind(wx.EVT_RADIOBUTTON, self.loopRadio)
        
        # Pose
        self.rdoPose = xrc.XRCCTRL(self, "rdoPose")
        self.rdoPose.Bind(wx.EVT_RADIOBUTTON, self.poseRadio)
        
        # Joint tree
        self.treeJoints = xrc.XRCCTRL(self, "treeJoints")
        self.treeJoints.Bind(wx.EVT_TREE_SEL_CHANGED, self.updateTreeSelection)
        
        # Joint buttons
        self.btnExpose = xrc.XRCCTRL(self, "btnExpose")
        self.btnExpose.Bind(wx.EVT_BUTTON, self.exposeJoint)
        self.btnControl = xrc.XRCCTRL(self, "btnControl")
        self.btnControl.Bind(wx.EVT_BUTTON, self.controlJoint)
        self.btnRelease = xrc.XRCCTRL(self, "btnRelease")
        self.btnRelease.Bind(wx.EVT_BUTTON, self.releaseJoint)
        
        #hack to make combo box work
        for w in self.GetChildren():
            if not isinstance(w, wx.TextCtrl):
                w.Unbind(wx.EVT_SET_FOCUS)
        
        self.Bind(wx.EVT_CHILD_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
        
        # I hate that this is needed to update joints tree, when
        # changing actor objects
        self.objOld = None
        self.selectedJoint = None
        
        self.oldSelected = None
        
        self.origPose = None
    
    def updateProps(self, obj):
        if isinstance(obj, LEActor):
            if obj.getAllAnims() != {}:
                self.oldSelected = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
                self.cboxAnimNameList.Enable(True)
                # Animation names list
                names = []
                for key in obj.getAllAnims():
                    names.append(key)
                if names != self.cboxAnimNameList.GetItems():
                    self.cboxAnimNameList.SetItems(names)
                if obj.nodePath.getCurrentAnim() is not None:
                    self.cboxAnimNameList.SetSelection(names.index(obj.nodePath.getCurrentAnim()))
                else:
                    self.cboxAnimNameList.SetSelection(0)
                obj.currentAnim = self.cboxAnimNameList.GetValue()
                # Playrate text box
                if obj.nodePath.getPlayRate() is None:
                    self.txtPlayRate.Enable(False)
                    self.txtPlayRate.SetValue("")
                else:
                    self.txtPlayRate.Enable(True)
                    self.txtPlayRate.SetValue(str(obj.nodePath.getPlayRate()))
                
                # Controls
                if self.cboxAnimNameList.GetItems() != []:
                    self.rdoLoop.Enable(True)
                    self.rdoPlay.Enable(True)
                    self.rdoPose.Enable(True)
                    if obj.looping:
                        self.rdoLoop.SetValue(True)
                        self.rdoPlay.SetValue(False)
                        self.rdoPose.SetValue(False)
                        self.txtFrame.Enable(False)
                        self.txtFrame.SetValue("")
                        self.slFrame.Enable(False)
                        self.slFrame.SetValue(0)
                    elif obj.playing:
                        self.rdoLoop.SetValue(False)
                        self.rdoPlay.SetValue(True)
                        self.rdoPose.SetValue(False)
                        self.txtFrame.Enable(False)
                        self.txtFrame.SetValue("")
                        self.slFrame.Enable(False)
                        self.slFrame.SetValue(0)
                    else:
                        self.rdoLoop.SetValue(False)
                        self.rdoPlay.SetValue(False)
                        self.rdoPose.SetValue(True)
                        self.txtFrame.Enable(True)
                        self.txtFrame.SetValue(str(obj.nodePath.getCurrentFrame(obj.currentAnim)))
                        self.slFrame.Enable(True)
                        self.slFrame.SetRange(0,int(obj.nodePath.getNumFrames(obj.currentAnim)))
                        self.slFrame.SetValue(int(obj.nodePath.getCurrentFrame(obj.currentAnim)))
                else:
                    self.rdoLoop.Enable(False)
                    self.rdoLoop.SetValue(False)
                    self.rdoPlay.Enable(False)
                    self.rdoPlay.SetValue(False)
                    self.rdoPose.Enable(False)
                    self.rdoPose.SetValue(False)
                    self.txtFrame.Enable(False)
                    self.txtFrame.SetValue("")
            elif self.oldSelected != self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last):
                self.oldSelected = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
                self.cboxAnimNameList.Enable(False)
                self.cboxAnimNameList.SetItems([""])
                self.cboxAnimNameList.SetSelection(0)
                self.rdoLoop.Enable(False)
                self.rdoLoop.SetValue(False)
                self.rdoPlay.Enable(False)
                self.rdoPlay.SetValue(False)
                self.rdoPose.Enable(False)
                self.rdoPose.SetValue(False)
                self.txtPlayRate.Enable(False)
                self.txtPlayRate.SetValue("")
                self.txtFrame.Enable(False)
                self.txtFrame.SetValue("")
            
            # Joints
            if obj.nodePath.getJoints() != []:
                if self.treeJoints.IsEmpty() or obj != self.objOld:
                    self.objOld = obj
                    self.selectedJoint = None
                    self.treeJoints.DeleteAllItems()
                    self.treeJoints.Enable(True)
                    # Populate the tree
                    part = obj.nodePath.getPartBundle("modelRoot").getChildren()[0]
                    root = self.treeJoints.AddRoot(part.getName())
                    for child in part.getChildren():
                        self.recurse(child, root) 
                if self.selectedJoint is not None:    
                    # Enable the proper buttons
                    self.enableButtons(obj)
                else: 
                    self.btnExpose.Enable(False)               
                    self.btnControl.Enable(False)                
                    self.btnRelease.Enable(False)
            else:
                self.treeJoints.Enable(False)
                self.treeJoints.DeleteAllItems()
                
                self.btnExpose.Enable(False)               
                self.btnControl.Enable(False)                
                self.btnRelease.Enable(False)
    
    def recurse(self, node, parent):
        item = self.treeJoints.AppendItem(parent, node.getName())
        self.treeJoints.SetItemPyData(item, node.getName())
        for child in node.getChildren():
            self.recurse(child, item)
    
    def updateAnimList(self, evt):

        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        items = self.cboxAnimNameList.GetItems()
        anim = items[evt.GetSelection()]
        self.cboxAnimNameList.SetSelection(evt.GetSelection())
        
        # added by qiaosi
        for name in obj.getAllAnims().keys():
            obj.stopSoundOfAnim(name)
        #-------------------
        
        # If the previous animation was looping or playing,
        # make the new one do the same
        if obj.looping:
            action = ActionGeneric(self.editor, obj.nodePath.loop, obj.nodePath.stop, anim)
            obj.frame = 0
            obj.loopSoundOfAnim(anim)#qiaosi
        elif obj.playing:
            action = ActionGeneric(self.editor, obj.nodePath.play, obj.nodePath.stop, anim)
            obj.frame = 0
            obj.playSoundOfAnim(anim)#qiaosi
        else:
            action = ActionGeneric(self.editor, obj.nodePath.pose, obj.nodePath.stop, anim, 0)
            obj.frame = 0
            self.slFrame.SetValue(0)
            self.txtFrame.SetValue(str(obj.frame))
        self.editor.actionMgr.push(action)
        action()
        obj.currentAnim = self.cboxAnimNameList.GetValue()
        # Playrate text box
        if obj.nodePath.getPlayRate() is None:
            self.txtPlayRate.Enable(False)
            self.txtPlayRate.SetValue("")
        else:
            self.txtPlayRate.Enable(True)
            self.txtPlayRate.SetValue(str(obj.nodePath.getPlayRate()))
        # Set the slider to be in the range of the new animation's frames
        self.slFrame.SetRange(0,obj.nodePath.getNumFrames(anim))
        ## # Reset the loop check box
        ## self.rdoLoop.Enable(True)
        ## self.rdoLoop.SetValue(False)
        

        
    def updatePlayRate(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            pr = float(self.txtPlayRate.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtPlayRate.SetValue(str(obj.nodePath.getPlayRate()))
        else:
            anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
            action = ActionSetProperty(self.editor, obj.nodePath.setPlayRate, obj.nodePath.getPlayRate, pr, anim)
            self.editor.actionMgr.push(action)
            action()
            obj.playRate = pr
    
    def updatePoseBox(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            frame = float(self.txtFrame.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFrame.SetValue(str(float(obj.frame)))
        else:
            anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
            # Make sure the value is not less than zero or greater than the number of frames
            if frame < 0:
                frame = 0
                self.txtFrame.SetValue(str(frame))
            elif frame > obj.nodePath.getNumFrames(anim):
                frame = obj.nodePath.getNumFrames(anim)
                self.txtFrame.SetValue(str(frame))
            prevFrame = obj.nodePath.getCurrentFrame(anim)
            action = ActionGeneric(self.editor, lambda : obj.nodePath.pose(anim, frame), lambda : obj.nodePath.pose(anim, prevFrame))
            #action = ActionSetProperty(self.editor, obj.nodePath.pose, obj.nodePath.stop, anim, frame)
            self.editor.actionMgr.push(action)
            action()
            self.slFrame.SetValue(int(frame))
            obj.setPosed(frame)
    
    def updatePoseSliderNoAction(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        frame = self.slFrame.GetValue()
        anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
        if self.origPose == None:
            self.origPose = copy(obj.nodePath.getCurrentFrame(anim))
        obj.nodePath.pose(anim, frame)
        self.txtFrame.SetValue(str(float(frame)))
        obj.setPosed(frame)
    
    def updatePoseSlider(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        frame = self.slFrame.GetValue()
        anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
        if self.origPose != None:
            origPose = copy(self.origPose)
            self.origPose = None
        do = lambda : obj.nodePath.pose(anim, frame)
        undo = lambda : obj.nodePath.pose(anim, origPose)
        action = ActionGeneric(self.editor, do, undo)
        self.editor.actionMgr.push(action)
        action()
        self.txtFrame.SetValue(str(float(frame)))
        obj.setPosed(frame)
    
    def loopRadio(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
        action = ActionGeneric(self.editor, obj.nodePath.loop, obj.nodePath.stop, anim)
        self.editor.actionMgr.push(action)
        action()
        self.txtPlayRate.Enable(True)
        self.txtPlayRate.SetValue(str(obj.nodePath.getPlayRate()))
        # Set the frame text box
        self.txtFrame.Enable(False)
        self.txtFrame.SetValue("")
        self.slFrame.Enable(False)
        self.slFrame.SetValue(0)
        obj.setLooping()
        #----- added by qiaosi-----
        obj.loopSoundOfAnim(anim)
        #--------------------------
        
    def playRadio(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
        action = ActionGeneric(self.editor, obj.nodePath.play, obj.nodePath.stop, anim)

        self.editor.actionMgr.push(action)
        action()
        self.txtPlayRate.Enable(True)
        self.txtPlayRate.SetValue(str(obj.nodePath.getPlayRate()))
        # Set the frame text box
        self.txtFrame.Enable(False)
        self.txtFrame.SetValue("")
        self.slFrame.Enable(False)
        self.slFrame.SetValue(0)
        obj.setPlaying()
        #-----------added by qiaosi--------

#        sound_name = obj.getAnims()[anim].getFullFilename()# get the full name of the animation
#        sound_for_anim = obj.sound_anims_map[sound_name]
#        sound = self.editor.soundMgr.sounds[sound_for_anim]
#        sound.play()
        obj.playSoundOfAnim(anim)
        #------------------------------
        
    def poseRadio(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        anim = self.cboxAnimNameList.GetItems()[self.cboxAnimNameList.GetSelection()]
        action = ActionGeneric(self.editor, obj.nodePath.pose, obj.nodePath.stop, anim, obj.frame)
        self.editor.actionMgr.push(action)
        action()
        # Set the playrate text box
        self.txtPlayRate.Enable(False)
        self.txtPlayRate.SetValue("")
        # Set the frame text box
        self.txtFrame.Enable(True)
        self.txtFrame.SetValue(str(float(obj.frame)))
        self.slFrame.Enable(True)
        self.slFrame.SetValue(int(obj.frame))
        obj.setPosed(obj.frame)
        #----- added by qiaosi-----
        obj.stopSoundOfAnim(anim)
        #--------------------------
    
    def updateTreeSelection(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.selectedJoint = self.treeJoints.GetItemText(self.treeJoints.GetSelection())
        # Enable the proper buttons
        Sequence(Wait(0.1), Func(self.enableButtons, obj)).start()
    
    def exposeJoint(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        jointNP = obj.nodePath.exposeJoint(None, 'modelRoot', self.selectedJoint)
        # Add the exposed joint to the actors exposedJoints dictionary
        action = ActionCreateJoint(self.editor, obj.addExposedJoint, obj.removeJoint, self.selectedJoint, jointNP)
        self.editor.actionMgr.push(action)
        action()
        # Enable the proper buttons
        Sequence(Wait(0.1), Func(self.enableButtons, obj)).start()
    
    def controlJoint(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        jointNP = obj.nodePath.controlJoint(None, 'modelRoot', self.selectedJoint)
        # Add the exposed joint to the actors exposedJoints dictionary
        action = ActionCreateJoint(self.editor, obj.addControlledJoint, obj.removeJoint, self.selectedJoint, jointNP)
        self.editor.actionMgr.push(action)
        action()
        # Enable the proper buttons
        Sequence(Wait(0.1), Func(self.enableButtons, obj)).start()
    
    def releaseJoint(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        joint = obj.joints[self.selectedJoint]
        if joint.type == "exposed":
            action = ActionRemoveJoint(self.editor, obj.removeJoint, obj.reattachJoint, self.selectedJoint, joint)
        else:
            action = ActionRemoveJoint(self.editor, obj.removeJoint, obj.reattachJoint, self.selectedJoint, joint)
        # Remove the exposed or controlled joint from the actor's dictionary and the scenegraphui
        self.editor.actionMgr.push(action)
        action()
        # Enable the proper buttons
        Sequence(Wait(0.1), Func(self.enableButtons, obj)).start()
        
    def enableButtons(self, obj):
        # If the selected item is the skeleton/root
        # do not enable the buttons
        if self.selectedJoint == "<skeleton>":
            self.btnExpose.Enable(False)
            self.btnControl.Enable(False)
            self.btnRelease.Enable(False)
            return
        # See if the joint is controlled
        used = None
        try:
            obj.joints[self.selectedJoint]
        except KeyError as e:
            used = False
        else:
            used = True
            
        # Enable release if the joint is controlled or exposed
        if used:
            self.btnExpose.Enable(False)
            self.btnControl.Enable(False)
            self.btnRelease.Enable(True)
        else:
            self.btnRelease.Enable(False)
            self.btnExpose.Enable(True)
            self.btnControl.Enable(True)

class LensPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['lens'], 'lensPanel')
        # FOV text boxes
        self.txtHoriz = xrc.XRCCTRL(self, "txtHoriz")
        self.txtVert = xrc.XRCCTRL(self, "txtVert")
        
        self.txtHoriz.Bind(wx.EVT_TEXT_ENTER, self.updateFov)
        self.txtVert.Bind(wx.EVT_TEXT_ENTER, self.updateFov)
        
        # Viewing Planes
        self.txtNear = xrc.XRCCTRL(self, "txtNear")
        self.txtFar= xrc.XRCCTRL(self, "txtFar")
        
        self.txtNear.Bind(wx.EVT_TEXT_ENTER, self.updateNear)
        self.txtFar.Bind(wx.EVT_TEXT_ENTER, self.updateFar)
        
        # Frustum checkbox
        self.chkFrustum = xrc.XRCCTRL(self, "chkFrustum")
        self.chkFrustum.Bind(wx.EVT_CHECKBOX, self.toggleFrustum)
        
        # Aspect Ratio
        self.txtAspectRatio = xrc.XRCCTRL(self, "txtAspectRatio")
        self.txtAspectRatio.Bind(wx.EVT_TEXT_ENTER, self.updateAspectRatio)
        
    
    def updateProps(self, obj, override=False):
        if isinstance(obj, Cam) and isinstance(obj.getLens(), PerspectiveLens) or override:
            # Fov
            self.txtHoriz.SetValue(str(obj.getLens().getFov()[0]))
            self.txtVert.SetValue(str(obj.getLens().getFov()[1]))
            
            # Viewing planes
            self.txtNear.SetValue(str(obj.getLens().getNear()))
            self.txtFar.SetValue(str(obj.getLens().getFar()))
            
            # Frustum checkbox
            self.chkFrustum.SetValue(not obj.frustumHidden)
            
            # # Aspect Ratio
            hRad = math.radians(obj.getLens().getFov()[0])
            vRad = math.radians(obj.getLens().getFov()[1])
            ar = math.tan(hRad/2) / math.tan(vRad/2)
            self.txtAspectRatio.SetValue(str(ar))            
    
    def updateFov(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            h = float(self.txtHoriz.GetValue())
            v = float(self.txtVert.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtHoriz.SetValue(str(obj.getLens().getFov()[0]))
            self.txtVert.SetValue(str(obj.getLens().getFov()[1]))
        else:
            action = ActionSetProperty(self.editor, obj.getLens().setFov, obj.getLens().getFov, Vec2(h,v))
            self.editor.actionMgr.push(action)
            action()
            self.updateAllProps()
    
    def updateNear(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            near = float(self.txtNear.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtNear.SetValue(str(obj.getLens().getNear()))
        else:
            action = ActionSetProperty(self.editor, obj.getLens().setNear, obj.getLens().getNear, near)
            self.editor.actionMgr.push(action)
            action()
    
    def updateFar(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            far = float(self.txtFar.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFar.SetValue(str(obj.getLens().getFar()))
        else:
            action = ActionSetProperty(self.editor, obj.getLens().setFar, obj.getLens().getFar, far)
            self.editor.actionMgr.push(action)
            action()
    
    def updateAspectRatio(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            ar = float(self.txtAspectRatio.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            hRad = math.radians(obj.getLens().getFov()[0])
            vRad = math.radians(obj.getLens().getFov()[1])
            ar = math.tan(hRad/2) / math.tan(vRad/2)
            self.txtAspectRatio.SetValue(str(ar))  
        else:
            pass
            
            vDeg = obj.getLens().getFov()[1]
            vRad = math.radians(vDeg)
            hRad = 2 * math.atan( ar * math.tan(vRad / 2) )
            hDeg = math.degrees(hRad)
            action = ActionSetProperty(self.editor, obj.getLens().setFov, obj.getLens().getFov, Vec2(hDeg, vDeg))
            self.editor.actionMgr.push(action)
            action()
            self.updateAllProps()
    
    def updateAllProps(self):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        # FOV text boxes
        self.txtHoriz.SetValue(str(obj.getLens().getFov()[0]))
        self.txtVert.SetValue(str(obj.getLens().getFov()[1]))

        hRad = math.radians(obj.getLens().getFov()[0])
        vRad = math.radians(obj.getLens().getFov()[1])
        ar = math.tan(hRad/2) / math.tan(vRad/2)
        self.txtAspectRatio.SetValue(str(ar))    
            
    def toggleFrustum(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        action = None
        if obj.frustumHidden:
            action = ActionGeneric(self.editor, obj.showFrustum, obj.hideFrustum)
        else:
            action = ActionGeneric(self.editor, obj.hideFrustum, obj.showFrustum)
        self.editor.actionMgr.push(action)
        action()
        
class OrthoLensPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['orthoLens'], 'orthoLensPanel')
        # Film size text boxes
        self.txtWidth = xrc.XRCCTRL(self, "txtWidth")
        self.txtHeight = xrc.XRCCTRL(self, "txtHeight")
        
        self.txtWidth.Bind(wx.EVT_TEXT_ENTER, self.updateFilmSize)
        self.txtHeight.Bind(wx.EVT_TEXT_ENTER, self.updateFilmSize)
        
        # Viewing Planes
        self.txtNear = xrc.XRCCTRL(self, "txtNear")
        self.txtFar= xrc.XRCCTRL(self, "txtFar")
        
        self.txtNear.Bind(wx.EVT_TEXT_ENTER, self.updateNear)
        self.txtFar.Bind(wx.EVT_TEXT_ENTER, self.updateFar)
        
        # Frustum checkbox
        self.chkFrustum = xrc.XRCCTRL(self, "chkFrustum")
        self.chkFrustum.Bind(wx.EVT_CHECKBOX, self.toggleFrustum)
        
        # Aspect Ratio
        self.txtAspectRatio = xrc.XRCCTRL(self, "txtAspectRatio")
        self.txtAspectRatio.Bind(wx.EVT_TEXT_ENTER, self.updateAspectRatio)
        
    
    def updateProps(self, obj):
        if isinstance(obj, Cam) and isinstance(obj.getLens(), OrthographicLens):
            # FilmSize
            self.txtWidth.SetValue(str(obj.getLens().getFilmSize()[0]))
            self.txtHeight.SetValue(str(obj.getLens().getFilmSize()[1]))
            
            # Viewing planes
            self.txtNear.SetValue(str(obj.getLens().getNear()))
            self.txtFar.SetValue(str(obj.getLens().getFar()))
            
            # Frustum checkbox
            self.chkFrustum.SetValue(not obj.frustumHidden)
            
            # Aspect Ratio
            ar = obj.getLens().getFilmSize()[0] / obj.getLens().getFilmSize()[1]
            self.txtAspectRatio.SetValue(str(ar))            
    
    def updateFilmSize(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            w = float(self.txtWidth.GetValue())
            h = float(self.txtHeight.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtHoriz.SetValue(str(obj.getLens().getFilmSize()[0]))
            self.txtVert.SetValue(str(obj.getLens().getFilmSize()[1]))
        else:
            action = ActionSetProperty(self.editor, obj.getLens().setFilmSize, obj.getLens().getFilmSize, Vec2(w,h))
            self.editor.actionMgr.push(action)
            action()
            self.updateAllProps()
    
    def updateNear(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            near = float(self.txtNear.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtNear.SetValue(str(obj.getLens().getNear()))
        else:
            action = ActionSetProperty(self.editor, obj.getLens().setNear, obj.getLens().getNear, near)
            self.editor.actionMgr.push(action)
            action()
    
    def updateFar(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            far = float(self.txtFar.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFar.SetValue(str(obj.getLens().getFar()))
        else:
            action = ActionSetProperty(self.editor, obj.getLens().setFar, obj.getLens().getFar, far)
            self.editor.actionMgr.push(action)
            action()
    
    def updateAspectRatio(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            ar = float(self.txtAspectRatio.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtAspectRatio.SetValue(str(obj.getLens().getFilmSize()[0] / obj.getLens().getFilmSize()[1]))
        else:
            pass
            
            h = obj.getLens().getFilmSize()[1]
            w = h * ar
            action = ActionSetProperty(self.editor, obj.getLens().setFilmSize, obj.getLens().getFilmSize, Vec2(w, h))
            self.editor.actionMgr.push(action)
            action()
            self.updateAllProps()
    
    def updateAllProps(self):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)

        self.txtWidth.SetValue(str(obj.getLens().getFilmSize()[0]))
        self.txtHeight.SetValue(str(obj.getLens().getFilmSize()[1]))

        ar = obj.getLens().getFilmSize()[0] / obj.getLens().getFilmSize()[1]
        self.txtAspectRatio.SetValue(str(ar))    
            
    def toggleFrustum(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        action = None
        if obj.frustumHidden:
            action = ActionGeneric(self.editor, obj.showFrustum, obj.hideFrustum)
        else:
            action = ActionGeneric(self.editor, obj.hideFrustum, obj.showFrustum)
        self.editor.actionMgr.push(action)
        action()

class TerrainColorMapDropTarget(wx.TextDropTarget):
    def __init__(self, editor):
        wx.TextDropTarget.__init__(self)
        self.editor = editor
        
    def OnDropText(self, x, y, text):
        #Check that the dropped item is actually a shader
        if text.find('>') == -1:
            return
        if text.split('>')[0] != 'Textures':
            return
            
        assetName = text.split('>')[-1]
        asset = self.editor.lib.textures[assetName]
        self.editor.ui.objectPropertyUI.terrainPanel.setColorMapFromAsset(asset)
        
class TerrainPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['terrain'], 'terrainPanel')
        ##need this panel to parent the color map panel to 
        self.mainPanel = xrc.XRCCTRL(self, 'terrainPanel')
        self.txtBlockSize = xrc.XRCCTRL(self, 'txtBlockSize')
        self.txtNear = xrc.XRCCTRL(self, 'txtNear')
        self.txtFar = xrc.XRCCTRL(self, 'txtFar')
        self.txtMinLevel = xrc.XRCCTRL(self, 'txtMinLevel')
        self.txtMaxLevel = xrc.XRCCTRL(self, 'txtMaxLevel')
        self.chkBruteForce = xrc.XRCCTRL(self, 'chkBruteforce')
        self.lblCurrentFocalPoint = xrc.XRCCTRL(self, 'lblCurrentFocalPoint')
        self.btnChooseFocalPoint = xrc.XRCCTRL(self, 'btnChooseFocalPoint')
        self.dropFlattenMode = xrc.XRCCTRL(self, 'dropFlattenMode')
        self.btnGenerate = xrc.XRCCTRL(self, 'btnGenerate')
        self.btnPaint = xrc.XRCCTRL(self, "btnPaint")
        
        self.colorMapPanel = xrc.XRCCTRL(self.mainPanel, 'panelColorMap')
        self.lblCurrentColorMap = xrc.XRCCTRL(self.colorMapPanel, 'lblCurrentColorMap')
        
        self.colorMapPanel.SetDropTarget(TerrainColorMapDropTarget(self.editor))
        
        
        self.txtBlockSize.Bind(wx.EVT_TEXT_ENTER, self.onBlockSize)
        self.txtNear.Bind(wx.EVT_TEXT_ENTER, self.onNear)
        self.txtFar.Bind(wx.EVT_TEXT_ENTER, self.onFar)
        self.txtMinLevel.Bind(wx.EVT_TEXT_ENTER, self.onMinLevel)
        self.chkBruteForce.Bind(wx.EVT_CHECKBOX, self.onBruteForce)
        self.dropFlattenMode.Bind(wx.EVT_COMBOBOX, self.onFlattenMode)
#        self.btnChooseFocalPoint.Bind(wx.EVT_BUTTON, self.onChooseFP)
        self.btnGenerate.Bind(wx.EVT_BUTTON, self.onGenerate)
        self.btnPaint.Bind(wx.EVT_BUTTON, self.onPaint)
        #hack to make list box work
        for w in self.GetChildren():
            w.Unbind(wx.EVT_SET_FOCUS)
        
        self.Bind(wx.EVT_CHILD_FOCUS, self.onChildFocus)    
    def onGenerate(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.update()
        obj.generate()
    
    def onPaint(self, evt):
        terrain = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        dlg = TerrainPaintUI(base.le.ui,self.editor,terrain)
        dlg.Show()
        
           
    def onChildFocus(self, evt):
        if isinstance(evt.GetWindow(), wx.TextCtrl):
            self.editor.objectMgr.onEnterObjectPropUI(True)
        else:
            self.editor.objectMgr.onEnterObjectPropUI(False)
            
    def onChooseFP(self, evt):
        dlg = ObjectInputDialog(self)
        obj = dlg.ShowModal()
        selected = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        selected.setFocalPoint(self.editor.objectMgr.findObjectById(obj).nodePath)
        self.lblCurrentFocalPoint.SetLabel(self.editor.objectMgr.findObjectById(obj).name)
        
        
    def onFlattenMode(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        val = int(self.dropFlattenMode.GetSelection())
        action = ActionSetProperty(self.editor, obj.setAutoFlattenMode, obj.getAutoFlattenMode, val)
        self.editor.actionMgr.push(action)
        action()
        obj.update()
             
    def onBruteForce(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        val = bool(self.chkBruteForce.GetValue())
        action = ActionSetProperty(self.editor, obj.setBruteforce, obj.getBruteforce, val)
        self.editor.actionMgr.push(action)
        action()
        obj.update()
#        obj.setBruteforce(bool(self.chkBruteForce.GetValue()))
#        obj.update()
   
    def onFar(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            val = int(self.txtFar.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFar.SetValue(str(obj.getFar()))
        else:
            action = ActionSetProperty(self.editor, obj.setFar, obj.getFar, val)
            self.editor.actionMgr.push(action)
            action()
            obj.update()
        
    def onNear(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            val = int(self.txtNear.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFar.SetValue(str(obj.getNear()))
        else:
            action = ActionSetProperty(self.editor, obj.setNear, obj.getNear, val)
            self.editor.actionMgr.push(action)
            action()
            obj.update()
        
    def onMinLevel(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            val = int(self.txtMinLevel.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFar.SetValue(str(obj.getMinLevel()))
        else:
            action = ActionSetProperty(self.editor, obj.setMinLevel, obj.getMinLevel, val)
            self.editor.actionMgr.push(action)
            action() 
            obj.update()
                    
    def onBlockSize(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            block = int(self.txtBlockSize.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtFar.SetValue(str(obj.getBlockSize()))
        else:
            action = ActionSetProperty(self.editor, obj.setBlockSize, obj.getBlockSize, block)
            self.editor.actionMgr.push(action)
            action()    
            obj.update()
                
    def setColorMapFromAsset(self , asset):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.setColorMap(asset)
        self.lblCurrentColorMap.SetLabel(asset.name)
        obj.update()
        
            
    def updateProps(self,obj):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if isinstance(obj, LETerrain):
            self.txtBlockSize.SetValue(str(obj.getBlockSize()))
            self.txtNear.SetValue(str(obj.getNear()))
            self.txtFar.SetValue(str(obj.getFar()))
            self.txtMinLevel.SetValue(str(obj.getMinLevel()))
            self.chkBruteForce.SetValue(bool(obj.getBruteforce()))
            self.dropFlattenMode.SetSelection(obj.getAutoFlattenMode())

class CameraPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['camera'], 'cameraPanel')
        
        self.btnCamView = xrc.XRCCTRL(self, "btnCamView")
        self.btnCamView.Bind(wx.EVT_BUTTON, self.onCamView)
        
#        self.btnAddWP = xrc.XRCCTRL(self, "btnEditWP")
#        self.btnAddWP.Bind(wx.EVT_BUTTON, self.editWaypoints)
#        
#        self.txtSeqTime = xrc.XRCCTRL(self, "txtSeqTime")
#        self.txtSeqTime.Bind(wx.EVT_TEXT_ENTER, self.updateSeqTime)
#        self.txtSeqTime.Enable(False)
#        self.txtSeqTime.ChangeValue("")
#        
#        self.btnUpdate = xrc.XRCCTRL(self, "btnUpdate")
#        self.btnUpdate.Bind(wx.EVT_BUTTON, self.updateSequence)
#        
#        self.btnPreview = xrc.XRCCTRL(self, "btnPlay")
#        self.btnPreview.Bind(wx.EVT_BUTTON, self.previewSeq)
#        
#        self.btnStop = xrc.XRCCTRL(self, "btnReset")
#        self.btnStop.Bind(wx.EVT_BUTTON, self.resetSeq)
#        
#        self.chkHide = xrc.XRCCTRL(self, "chkHide")
#        self.chkHide.Bind(wx.EVT_CHECKBOX, self.toggleRope)
#        
#        # Radio buttons
#        self.rdoLocked = xrc.XRCCTRL(self, "rdoLocked")
#        self.rdoFree = xrc.XRCCTRL(self, "rdoFree")
#        self.rdoLookAt = xrc.XRCCTRL(self, "rdoLookAt")
#        
#        self.rdoLocked.Bind(wx.EVT_RADIOBUTTON, self.updateOrient)
#        self.rdoFree.Bind(wx.EVT_RADIOBUTTON, self.updateOrient)
#        self.rdoLookAt.Bind(wx.EVT_RADIOBUTTON, self.updateOrient)
#        
#        self.rdoLocked.Enable(False)
#        self.rdoFree.Enable(False)
#        self.rdoLookAt.Enable(False)
#        
#        #hack to make combo box work
#        for w in self.GetChildren():
#            if not isinstance(w, wx.TextCtrl):
#                w.Unbind(wx.EVT_SET_FOCUS)
#        
#        self.Bind(wx.EVT_CHILD_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
    
    def updateProps(self, obj):
        return
#        if isinstance(obj, Cam):
#            if len(obj.waypoints) > 0:
#                self.txtSeqTime.Enable(True)
#                self.txtSeqTime.SetValue(str(obj.getSeqTime()))
#                self.btnUpdate.Enable(True)
#                self.btnPreview.Enable(True)
#                
#                self.rdoLocked.Enable(True)
#                self.rdoFree.Enable(True)
#                self.rdoLookAt.Enable(True)
#                self.updateRadioButtons(obj)
#            else:
#                self.txtSeqTime.Enable(False)
#                self.txtSeqTime.SetValue("")
#                
#                self.btnUpdate.Enable(False)
#                self.btnPreview.Enable(False)
#                
#                self.rdoLocked.Enable(False)
#                self.rdoFree.Enable(False)
#                self.rdoLookAt.Enable(False)
#                self.rdoLocked.SetValue(False)
#                self.rdoFree.SetValue(False)
#                self.rdoLookAt.SetValue(False)
    
    def onCamView(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if isinstance(camera, Cam):
            dlg = CamViewDialog(base.le.ui, camera)
            dlg.Show()
    
    def updateRadioButtons(self, cam):
        self.rdoLocked.Enable(True)
        self.rdoFree.Enable(True)
        self.rdoLookAt.Enable(True)
        if cam.followPath:
            self.rdoLocked.SetValue(True)
            self.rdoFree.SetValue(False)
            self.rdoLookAt.SetValue(False)
        elif cam.lookAt is not None:
            self.rdoLocked.SetValue(False)
            self.rdoFree.SetValue(False)
            self.rdoLookAt.SetValue(True)
        else:
            self.rdoLocked.SetValue(False)
            self.rdoFree.SetValue(True)
            self.rdoLookAt.SetValue(False)
    
    def updateOrient(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        if self.rdoLocked.GetValue():
            camera.followPath = True
            camera.lookAt = None
        elif self.rdoLookAt.GetValue():
            camera.followPath = False
            dlg = ObjectInputDialog(self)
            lookAtName = dlg.ShowModal()
            dlg.Destroy()
            if lookAtName:
                lookAt = self.editor.objectMgr.findObjectById(lookAtName)
                camera.lookAt = lookAt.getNodePath()
        else:
            camera.followPath = False
            camera.lookAt = None
    
    def editWaypoints(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        dlg = WaypointDialog(self, camera.getName(), self.getWaypointNames())
        waypoints = dlg.ShowModal()
        dlg.Destroy()
        camera.clearWaypoints()
        if waypoints != []:
            for waypoint in waypoints:
                camera.addWaypoint(waypoint)
            # Set the text boxes
            self.txtSeqTime.Enable(True)
            self.txtSeqTime.ChangeValue(str(camera.getSeqTime()))
            self.btnUpdate.Enable(True)
            self.btnPreview.Enable(True)
            self.updateRadioButtons(camera)
        else:
            self.txtSeqTime.Enable(False)
            self.txtSeqTime.ChangeValue("")
            self.btnUpdate.Enable(False)
            self.btnPreview.Enable(False)
            self.rdoLocked.SetValue(False)
            self.rdoFree.SetValue(False)
            self.rdoLookAt.SetValue(False)
            self.rdoLocked.Enable(False)
            self.rdoFree.Enable(False)
            self.rdoLookAt.Enable(False)
        

        # Create the visible line (rope) between them
        camera.genWaypointRope()
    
    def getWaypointNames(self):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        names = []
        for wp in camera.waypoints:
            obj = self.editor.objectMgr.findObjectById(wp)
            if obj:
                names.append(wp)
            else:
                camera.waypoints.remove(wp)
        return names   
    
    def updateSeqTime(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        try:
            seqTime = float(self.txtSeqTime.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtSeqTime.ChangeValue(str(camera.getSeqTime()))
        else:
            action = ActionSetProperty(self.editor, camera.setSeqTime, camera.getSeqTime, seqTime)
            self.editor.actionMgr.push(action)
            action() 
    
    def updateSequence(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        camera.genWaypointRope()
        
    def previewSeq(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if camera.sequence is not None:
            if self.btnPreview.GetLabel() == "Play":
                camera.previewSequence()
                self.btnPreview.SetLabel("Pause")
            elif self.btnPreview.GetLabel() == "Pause":
                camera.pauseSequence()
                self.btnPreview.SetLabel("Resume")
            elif self.btnPreview.GetLabel() == "Resume":
                camera.resumeSequence()
                self.btnPreview.SetLabel("Pause")
    
    def resetSeq(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if camera.sequence is not None:
            camera.resetSequence()
            self.btnPreview.SetLabel("Play")            
    
    def toggleRope(self, evt):
        camera = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if self.chkHide.GetValue():
            camera.rope.hide()
        else:
            camera.rope.show()

class LightLensPropertyPanel(LensPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['lightLens'], 'lightLensPanel')
    
        # FOV text boxes
        self.txtHoriz = xrc.XRCCTRL(self, "txtHoriz")
        self.txtVert = xrc.XRCCTRL(self, "txtVert")
        
        self.txtHoriz.Bind(wx.EVT_TEXT_ENTER, self.updateFov)
        self.txtVert.Bind(wx.EVT_TEXT_ENTER, self.updateFov)
        
        # Viewing Planes
        self.txtNear = xrc.XRCCTRL(self, "txtNear")
        self.txtFar= xrc.XRCCTRL(self, "txtFar")
        
        self.txtNear.Bind(wx.EVT_TEXT_ENTER, self.updateNear)
        self.txtFar.Bind(wx.EVT_TEXT_ENTER, self.updateFar)
        
        # Frustum checkbox
        self.chkFrustum = xrc.XRCCTRL(self, "chkFrustum")
        self.chkFrustum.Bind(wx.EVT_CHECKBOX, self.toggleFrustum)
        
        # Aspect Ratio
        self.txtAspectRatio = xrc.XRCCTRL(self, "txtAspectRatio")
        self.txtAspectRatio.Bind(wx.EVT_TEXT_ENTER, self.updateAspectRatio)
    
    def updateProps(self, obj):
        if isinstance(obj, SpoLight):
           LensPropertyPanel.updateProps(self, obj, override=True)

class CustomEditableListCtrl(wx.ListCtrl):
    def __init__(self, listCtrl):
        wx.ListCtrl.__init__(self,listCtrl)
    def OpenEditor(self, col, row): 
        if col in [0]: 
            return 
        else: 
            listmix.TextEditMixin.OpenEditor(self, col, row) 
        

# added by Anton on 1/28/11
class GamePropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['game'], 'gamePanel')
        
#        self.startIcon = loader.loadModel('models/startIcon.egg')
#        self.startIcon.setColor(0.3, 1.0, 0.3) # CONSIDER: setting colors of the main character could influence startIcon's color
#        # CONSIDER: add a camera icon behind the startIcon representing game camera (but could be confusing...cannot click on it)
        
        # Controls
        self.mainCharButton = xrc.XRCCTRL(self, "mainCharButton")
        self.mainCharButton.Bind(wx.EVT_BUTTON, self.updateMainChar)
        
        step = 10
        
        self.rotateCCWButton = xrc.XRCCTRL(self, 'rotateCCWButton')
        self.rotateCCWButton.Bind(wx.EVT_BUTTON, self.rotateIconCCW)
        
        self.rotateCWButton = xrc.XRCCTRL(self, 'rotateCWButton')
        self.rotateCWButton.Bind(wx.EVT_BUTTON, self.rotateIconCW)
        
        
        self.passableChkBox = xrc.XRCCTRL(self,"passableChkbox" )
        self.Bind(wx.EVT_CHECKBOX, self.onPassableCheck, self.passableChkBox)
        
        
        #== Combat properties
        
        self.attackableChkBox = xrc.XRCCTRL(self, "attackableChkbox")
        self.maxHealthTextCtrl = xrc.XRCCTRL(self, 'maxHealthTextCtrl')
        self.currentHealthTextCtrl = xrc.XRCCTRL(self, 'currentHealthTextCtrl')
        self.aggroRangeTextCtrl = xrc.XRCCTRL(self, "aggroRangeTextCtrl")
        self.strategyRadioBox = xrc.XRCCTRL(self, 'strategyRadioBox')
        
        self.Bind(wx.EVT_CHECKBOX, self.onAttackableCheck, self.attackableChkBox)
        self.Bind(wx.EVT_TEXT, self.onMaxHealthEnter, self.maxHealthTextCtrl)
        self.Bind(wx.EVT_TEXT, self.onCurrHealthEnter, self.currentHealthTextCtrl)
        self.Bind(wx.EVT_TEXT, self.onAggroRangeEnter, self.aggroRangeTextCtrl)
        self.Bind(wx.EVT_RADIOBOX, self.onStrategyRadioChange, self.strategyRadioBox)
        
        self.passableChkBox.Hide()
        self.strategyRadioBox.Hide()
        
        #wx.EVT_RADIOBOX(self, 1,  self.onStoryRoleRadioChange)
        
#        self.triggerList = xrc.XRCCTRL(self, 'trigger_listctrl')
#        self.triggerList.InsertColumn(0, "Trigger Type")
#        self.triggerList.InsertColumn(1, "Script")
#        
#        #self.triggerList.SetColumnEditable(0, False)
#        pos = self.triggerList.GetItemCount()
#        self.triggerList.InsertStringItem(pos, "OnConversation")
#        self.triggerList.SetStringItem(pos,1, "")
#        pos = self.triggerList.GetItemCount()
#        self.triggerList.InsertStringItem(pos, "OnCollision")
#        self.triggerList.SetStringItem(pos,1, "")
        
#        if not obj.hasTag('LE-mainChar'):
#            self.rotateCCWButton.Hide()
#            self.rotateCWButton.Hide()
        
#        # Anims list
#        self.cboxAnimNameList = xrc.XRCCTRL(self, "cboxAnimNameList")
#        self.cboxAnimNameList.Bind(wx.EVT_COMBOBOX, self.updateAnimList)
#        
#        self.listSet = False
#        
#        # Play rate text box
#        self.txtPlayRate = xrc.XRCCTRL(self, "txtPlayRate")
#        self.txtPlayRate.Bind(wx.EVT_TEXT_ENTER, self.updatePlayRate)
#        
#        # Frame text box
#        self.txtFrame = xrc.XRCCTRL(self, "txtFrame")
#        self.txtFrame.Bind(wx.EVT_TEXT_ENTER, self.updatePoseBox) 
#        
#        # Frame slider
#        self.slFrame = xrc.XRCCTRL(self, "slFrame")
#        self.slFrame.Bind(wx.EVT_SCROLL, self.updatePoseSliderNoAction)
#        self.slFrame.Bind(wx.EVT_SCROLL_ENDSCROLL, self.updatePoseSlider)
    
    def onAttackableCheck(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.setTag("LE-attackable", str(evt.IsChecked()))
    
    def onAggroRangeEnter(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        changedText = evt.GetString()
        obj.setTag("LE-aggression",changedText)
        
        # CONSIDER: make sure it is a number...
#        try:
#            newRange = float(changedText)
#            obj.setTag("LE-aggression",changedText)
#        except ValueError:
#            evt.Veto()
        
    def onCurrHealthEnter(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        changedText = evt.GetString()
        obj.setTag("LE-currentHealth",changedText)
    def onMaxHealthEnter(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        changedText = evt.GetString()
        obj.setTag("LE-maxHealth",changedText)
        
    def onStrategyRadioChange(self, evt):
        curchoice = self.strategyRadioBox.GetSelection()
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #TODO: Make these enums
        
       
        
        if(curchoice == 0):
            obj.setTag("LE-strategy", "NEUTRAL")
        elif(curchoice == 1):
            obj.setTag("LE-strategy", "AGGRESSIVE")
        elif(curchoice == 2):
            obj.setTag("LE-strategy", "DEFENSIVE")
        
#        self.resetStrategyTags()
#        if(curchoice == 0):
#            obj.setTag("LE_NPC", "True")
#        elif(curchoice == 1):
#            obj.setTag("LE_NPO", "True")
#        elif(curchoice == 2):
#            obj.setTag("LE_Enemy", "True")
    
    def onPassableCheck(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.setTag("LE-passable", str(evt.IsChecked()))
            
    def resetStrategyTags(self):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.setTag("LE_NPO", "False")
        obj.setTag("LE_NPC", "False")
        obj.setTag("LE_Enemy", "False")
        
        

        
    
    def rotateIconCCW(self, evt):
        selected = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if selected.hasTag('LE-mainChar'):
            mainChar_h = int(selected.getTag('LE-mainChar')) + 45
            selected.setTag('LE-mainChar', '%d' %(mainChar_h))
            self.editor.objectMgr.updateMainCharWidget()
            
            #print 'tag changed to: %d' %(mainChar_h)
    
    def rotateIconCW(self, evt):
        selected = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if selected.hasTag('LE-mainChar'):
            mainChar_h = int(selected.getTag('LE-mainChar')) - 45
            selected.setTag('LE-mainChar', '%d' %(mainChar_h))
            self.editor.objectMgr.updateMainCharWidget()
            
            #print 'tag changed to: %d' %(mainChar_h)
    
    def setMainChar(self, mainChar):
        if mainChar.hasTag('LE-mainChar'):
            offset = float(mainChar.getTag('LE-mainChar'))
        else:
            offset = 180 # default to 180, to fit our Vasherie model for Orelia and the Storyteller
            
        mainChar.setTag('LE-mainChar', '%d' %(offset))
        self.editor.objectMgr.updateMainCharWidget()
            
    def updateMainChar(self, evt):
        # TODO: allow only one main character (check tags object list)
        # TODO: make a custom action class to save state, switch back to previous main character on undo
       # print 'main char button pressed'
        selected = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if selected.nodePath.hasTag('LE-mainChar'):
            #print 'already set as main character!'
            dialog = wx.MessageDialog(self, "'" + selected.getName() + "' is already the main character", "Main Character Set", wx.OK|wx.ICON_EXCLAMATION)
            dialog.ShowModal()
            dialog.Destroy()
        else:
            #print 'setting %s as main character...' %(selected.getName())
            oldMainCharObj = self.findUniqueObject('LE-mainChar')
            if oldMainCharObj is None:
                dialog = wx.MessageDialog(self, "'" + selected.getName() + "' set as main character", "Main Character Set", wx.OK|wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                action = ActionGeneric(self.editor, lambda: self.transferMainChar(selected),\
                                       lambda: self.clearMainChar(selected))
            else:
                dialog = wx.MessageDialog(self, "Main character changed from '" + oldMainCharObj.getName() + "' to '" + selected.getName() + "'", "Main Character Set", wx.OK|wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                action = ActionGeneric(self.editor, lambda: self.transferMainChar(toObj=selected, fromObj=oldMainCharObj),\
                                       lambda: self.transferMainChar(toObj=oldMainCharObj, fromObj=selected))
            self.editor.actionMgr.push(action)
            action()
        self.strategyRadioBox.Hide()
        self.updateProps(selected)
        #self.resetStoryRoleTags()
        
    # transferring from an existing main character to a set a new main character
    def transferMainChar(self, toObj, fromObj=None):
        if fromObj != None:
            fromObj.clearTag('LE-mainChar')
        self.setMainChar(toObj)
    
    def clearMainChar(self, selectedObj):
        # temp
        #print '=opui= clearMainChar fn called'
        
        if selectedObj.hasTag('LE-mainChar'):
            selectedObj.clearTag('LE-mainChar')
            self.editor.objectMgr.updateMainCharWidget()
            #self.startIcon.hide()
            
        self.updateProps(selectedObj)
        
    def findUniqueObject(self, tag):
        matchList = self.editor.objectMgr.findObjectsByTag(tag)
        if len(matchList) == 0:
            return None
        elif len(matchList) > 1:
            print 'WARNING: more than one object with tag: ' + tag
            return matchList[0]
        else:
            return matchList[0]
    
    def updateProps(self, obj):
        if obj.hasTag('LE-mainChar'):
            self.mainCharButton.Disable()
            self.rotateCCWButton.Enable()
            self.rotateCWButton.Enable()
            #self.strategyRadioBox.Hide()
        else:
            self.mainCharButton.Enable()
            self.rotateCCWButton.Disable()
            self.rotateCWButton.Disable()
            #self.strategyRadioBox.Show()
        
        # TODO: these default values in UI should match the default values for the GameObject class and CombatMgrBase class
        if obj.hasTag('LE-passable'):
            self.passableChkBox.SetValue(obj.getTag('LE-passable') == "True")
        else:
            self.passableChkBox.SetValue(True)
            
        if obj.hasTag('LE-attackable'):
            self.attackableChkBox.SetValue(obj.getTag('LE-attackable') == "True")
        else:
            self.attackableChkBox.SetValue(False)
            
        if obj.hasTag('LE-maxHealth'):
            self.maxHealthTextCtrl.SetValue(obj.getTag('LE-maxHealth'))
        else:
            self.maxHealthTextCtrl.SetValue(str(1))
            
        if obj.hasTag('LE-currentHealth'):
            self.currentHealthTextCtrl.SetValue(obj.getTag('LE-currentHealth'))
        else:
            self.currentHealthTextCtrl.SetValue(str(1))
            
        if obj.hasTag('LE-aggression'):
            self.aggroRangeTextCtrl.SetValue(obj.getTag('LE-aggression'))
        else:
            self.aggroRangeTextCtrl.SetValue(str(0))
        
        # TODO: strategy radio
        self.strategyRadioBox = xrc.XRCCTRL(self, 'strategyRadioBox')
             
        #print obj.scripts   
        #obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
#        if(obj.scripts.has_key("LE-trigger-onCollision_333")):
#            self.onCollisionTextCtrl.SetValue(obj.scripts["OnCollision"])
#        else:
#            self.onCollisionTextCtrl.SetValue("")
#        if(obj.scripts.has_key("LE-trigger-onConversation_3333")):
#            self.currentHealthTextCtrl.SetValue(obj.scripts["OnConversation"])
#        else:
#            self.currentHealthTextCtrl.SetValue("")

# added by Zeina on 3/25/11
DEFAULT_PRETAG = "LE-trigger-"
DEFAULT_EVENT = "onCollision"
DEFAULT_SCRIPT = "Do Nothing"

class ScriptPropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor, file=RESOURCE_FILE['script']):
        ObjectPropertyPanel.__init__(self, parent, editor, file, 'scriptPanel')
        
        
        self.startIcon = None 
        self.filename = ''
        self.name = ''
        self.parametersUI = []
        self.currentObj = None

        
        #init all the panels from XRC for parenting later on
        self.viewPanel = xrc.XRCCTRL(self, "viewPanel")
        self.editPanel = xrc.XRCCTRL(self, "editPanel")
        
        #viewPanel related
        self.eventListCtrl = xrc.XRCCTRL(self, "eventListCtrl")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelection, self.eventListCtrl)
        self.setupView()
        
        self.addEventButton = xrc.XRCCTRL(self, "addEventButton")
        self.Bind(wx.EVT_BUTTON, self.onAddEvent,self.addEventButton)
        self.removeEventButton = xrc.XRCCTRL(self, "removeEventButton")
        self.Bind(wx.EVT_BUTTON, self.onRemoveEvent, self.removeEventButton)
        self.removeEventButton.Enable(False)
        
        self.eventChoice = xrc.XRCCTRL(self.editPanel, "eventChoice")
        self.Bind(wx.EVT_CHOICE, self.onSwitchEvent, self.eventChoice)
        self.scriptChoice = xrc.XRCCTRL(self.editPanel, "scriptChoice")
        self.Bind(wx.EVT_CHOICE, self.onSwitchScript, self.scriptChoice)
        #self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        
        self.parameterGridSizer = xrc.XRCCTRL(self.editPanel, "parameterGridSizer")
                
        self.selectedItem = None
        
        self.setupParameters()
        
        #hack to make combo box work
        #CONSIDER[Zeina]: Not sure if this part is necessary but at this moment the textboxes are editable
        for w in self.GetChildren():
            if not isinstance(w, wx.TextCtrl):
                w.Unbind(wx.EVT_SET_FOCUS)
        
        self.Bind(wx.EVT_CHILD_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
    

    def setupView(self):
        self.eventListCtrl.InsertColumn(0, "Events")
        self.eventListCtrl.InsertColumn(1, "Scripts")
        self.eventListCtrl.InsertColumn(2,"Parameters")
        
    def setupParameters(self):
        for i in range(1,5):
            label = xrc.XRCCTRL(self, "label_"+str(i))
            text = xrc.XRCCTRL(self, "text_ctrl_"+str(i))
            text.Bind(wx.EVT_SET_FOCUS, self.onTextFocus)
            text.Bind(wx.EVT_KILL_FOCUS, self.onTextKillFocus)
            text.Bind(wx.EVT_TEXT, self.onTextChange)
            if(text == None or label == None):
                break
            label.SetLabel("")
            text.Disable()
            self.parametersUI.append((label,text))
        
    def loadScriptChoices(self):
        self.scriptChoice.Clear()
        self.scriptChoice.Append(DEFAULT_SCRIPT)
        for s in sorted(self.editor.lib.actionScripts):
            self.scriptChoice.Append(s)
        #load the premade ones
        #load the imported ones
    
    def onListSelection(self, event):
#        if(self.selectedItem != None):
#            self.writeFromUIToData()
        self.selectedItem = self.eventListCtrl.GetFirstSelected()
        #self.selectedListItem = event.GetItem()
        if(self.selectedItem == None):
            self.editPanel.Hide()
            return
        else:
            id = event.GetItem().GetId()
            self.updateEditPanel()
            self.editPanel.Show()
    
    
    def updateEditPanel(self):
        event, script, id = self.getCurrentEventScriptID()      
        eventID = self.eventChoice.FindString(event)
        self.eventChoice.SetSelection(eventID)
        choiceID = self.scriptChoice.FindString(script)
        self.scriptChoice.SetSelection(choiceID)
        
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #print "Event: ",event
        scripts = obj.getScriptsAndArguments(DEFAULT_PRETAG+event)
        #print "Scripts: ", scripts
        script, values = scripts[id]
        
        arguments = self.getArgumentsFromScriptFile(script)    
        #print "Arguments in ScriptUI: ",arguments
        
        
        self.enableParameters(arguments)
        
        for i in range(len(values)):
            label, text = self.parametersUI[i]
            value = values[i]
            text.ChangeValue(value)
     
    def getCurrentEventScriptID(self):
        
        event = self.eventListCtrl.GetItemText(self.selectedItem)#GetItem(id, 0).GetText()
        item = self.eventListCtrl.GetItem(self.selectedItem,1)
        script = item.GetText()#GetItem(id, 1).GetText()
        scriptID = int(self.eventListCtrl.GetItemData(self.selectedItem))
        
        return (event,script, scriptID)
         
                            
    def resetParameters(self):
        for label, text in self.parametersUI:
            label.SetLabel("")
            text.ChangeValue("")
            text.Disable()
            #text.SetEditable(False)
            #text.SetBackgroundColour(wx.Colour(128,128,128))
    
    def enableParameters(self, arguments):
        self.resetParameters()
        counter = 0
        for argument in arguments:
            if(argument == "world"):
                continue
            label, text = self.parametersUI[counter]
            label.SetLabel(argument)
            text.Enable()
            #text.SetEditable(True)
            #text.SetBackgroundColour(wx.Colour(255,255,255))
            counter += 1
    #def fillParameterVaues(self, values):
    #    pass
    def onTextChange(self, event):
        self.writeFromUIToData()
    
    def onTextFocus(self,event):
        self.editor.objectMgr.onEnterObjectPropUI(True)
        pass
    
    def writeFromUIToData(self):
        event, script, id = self.getCurrentEventScriptID()
        values = []
        for label, text in self.parametersUI:
            if(text.IsEnabled()==False):
                continue
            value = text.GetValue()
            #maybe check
            values.append(value)
            
        #print "ScriptUI:onTextKillFocus:Values: ", values
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.setScriptArguments(DEFAULT_PRETAG+event,id, values)
        self.eventListCtrl.SetStringItem(self.selectedItem, 2, "("+",".join(values)+")")
        self.editor.objectMgr.onEnterObjectPropUI(False)
    
    def onTextKillFocus(self,event):
        self.writeFromUIToData()
        
    def onLeftClick(self,event):
        self.writeFromUIToData()
        
    def getArgumentsFromScriptFile(self, script):
        if(script == "Do Nothing"):
            return []
        filename = self.editor.lib.scripts[script].getFullFilename()
        scriptFile = open(filename.toOsSpecific())
        
        lines = scriptFile.readlines()
        scriptFile.close()
        mainLine = None
        for line in lines:
            strippedLine = line.strip()
            if(strippedLine.startswith("def main")):
                mainLine = line
        
        start = mainLine.find('(')+1
        end = mainLine.find(')')
        
        argumentsText = mainLine[start:end]
        
        if(mainLine.find(',')==-1):
            arguments = str(argumentsText).strip()
            if(arguments == ""):
                return []
        
        arguments = [str(v).strip() for v in mainLine[start:end].split(',')]
        return arguments
        
            
    def onSwitchScript(self, event=None):     
        self.resetParameters()
        chosenScript = self.scriptChoice.GetStringSelection()
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        event, script, id = self.getCurrentEventScriptID()
        obj.setScript(DEFAULT_PRETAG+event, id,  chosenScript)
        self.eventListCtrl.SetStringItem(self.selectedItem, 1, chosenScript)
        self.eventListCtrl.SetStringItem(self.selectedItem, 2, "()")
        
        arguments = self.getArgumentsFromScriptFile(chosenScript)    
        
        self.enableParameters(arguments)
            
    def onSwitchEvent(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        oldEvent, oldScript, oldId = self.getCurrentEventScriptID()
        chosenEvent = self.eventChoice.GetStringSelection()
        #chosenScript = self.scriptChoice.GetStringSelection()
        if(chosenEvent == oldEvent):
            return
        else:
            arguments = obj.getScriptArguments(DEFAULT_PRETAG+oldEvent, oldId)
            success = obj.removeScript(DEFAULT_PRETAG+oldEvent, oldId)
            if(success == False):
                return
            newId = obj.addScript(DEFAULT_PRETAG+chosenEvent, oldScript)
            obj.setScriptArguments(DEFAULT_PRETAG+chosenEvent, newId, arguments)
            self.eventListCtrl.SetStringItem(self.selectedItem, 0, chosenEvent)
            #For testing
            #self.eventListCtrl.SetStringItem(self.selectedItem, 2, str(newId))
            self.eventListCtrl.SetStringItem(self.selectedItem,2, "("+",".join(arguments)+")")
            self.eventListCtrl.SetItemData(self.selectedItem, newId)   
    
    #this is not being used.
    def onGenerateParameters(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        return
        
        chosenEvent = self.eventChoice.GetStringSelection()
        chosenScript = self.scriptChoice.GetStringSelection()
        selectedID = self.eventListCtrl.GetItemData(self.selectedItem)
        
        if(chosenEvent == self.selectedEvent):
            obj.setScript(DEFAULT_PRETAG+self.selectedEvent, selectedID, chosenScript)#later on add arguments
            self.eventListCtrl.SetStringItem(self.selectedItem, 1, chosenScript)
        else:
            success = obj.removeScript(DEFAULT_PRETAG+self.selectedEvent, selectedID)
            if(success == False):
                return
            id = obj.addScript(DEFAULT_PRETAG+chosenEvent, chosenScript)
            self.eventListCtrl.SetStringItem(self.selectedItem, 0, chosenEvent)
            self.eventListCtrl.SetStringItem(self.selectedItem, 1, chosenScript)
            #for testing
            #self.eventListCtrl.SetStringItem(self.selectedItem, 2, str(id))
            self.eventListCtrl.SetStringItem(self.selectedItem, 2, "("+",".join(arguments))
            self.eventListCtrl.SetItemData(self.selectedItem, id)
        
        #self.onListSelection(None)
        pass
    
    def onAddEvent(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(self.eventChoice.IsEmpty()==False):
            defaultEvent = self.eventChoice.GetString(0)  
        id = obj.addScript(DEFAULT_PRETAG+defaultEvent,DEFAULT_SCRIPT)

        pos = self.eventListCtrl.InsertStringItem(self.eventListCtrl.GetItemCount(),defaultEvent)#DEFAULT_EVENT)
        self.eventListCtrl.SetStringItem(pos, 1, DEFAULT_SCRIPT)
        self.eventListCtrl.SetStringItem(pos, 2, "()")#str(id))
        self.eventListCtrl.SetItemData(pos, id)

        self.eventListCtrl.Select(pos, True)
        self.eventListCtrl.EnsureVisible(pos)
        self.removeEventButton.Enable(True)
        self.scriptChoice.Enable(True)
        self.eventChoice.Enable(True)
    
    def onRemoveEvent(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        event, script, id = self.getCurrentEventScriptID()
        #id = self.eventListCtrl.GetItemData(self.selectedItem)
        obj.removeScript(DEFAULT_PRETAG+event, int(id))
        self.eventListCtrl.DeleteItem(self.selectedItem)
        
        if self.eventListCtrl.GetItemCount() == 0:
            self.removeEventButton.Enable(False)
            self.eventChoice.Enable(False)
            self.scriptChoice.Enable(False)
            self.resetParameters()
        else:
            self.removeEventButton.Enable(True)
            self.eventListCtrl.Select(0)
        
    
    def buildView(self):
        self.eventListCtrl.DeleteAllItems()
        obj = self.currentObj
        if obj == None:
            return#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        for event in sorted(obj.scripts):
            #[antonjs 3/29/2011] Added so that this panel does not show the condition scripts for a conversation line (which are scripts too, technically)
            conditionEvent = 'LE-convoLineCondition' # TODO: make into constant
            if event != conditionEvent:    
                for scriptID in sorted(obj.scripts[event]):
                    eventName = event.replace(DEFAULT_PRETAG,"",1)
                    pos = self.eventListCtrl.InsertStringItem(self.eventListCtrl.GetItemCount(),eventName)
                    scriptName, parameters = obj.scripts[event][scriptID]
                    self.eventListCtrl.SetStringItem(pos, 1, scriptName)
                    #this is for testing(ID)
                    #self.eventListCtrl.SetStringItem(pos, 2, str(scriptID))
                    self.eventListCtrl.SetStringItem(pos, 2,"("+",".join(parameters)+")")
                    self.eventListCtrl.SetItemData(pos, scriptID)
                
        if self.eventListCtrl.GetItemCount() == 0:
            self.removeEventButton.Enable(False)
            self.eventChoice.Enable(False)
            self.scriptChoice.Enable(False)
            self.resetParameters()
        else:
            self.scriptChoice.Enable(True)
            self.eventChoice.Enable(True)
            self.removeEventButton.Enable(True)
            self.eventListCtrl.Select(0)
    
    def updateEventList(self):
        pass
        self.buildView()
    
    def updateScriptChoices(self):
        self.loadScriptChoices()
    def update(self):
        self.resetParameters()
        self.loadScriptChoices()
        self.buildView()
                
    def updateProps(self, obj, override=False):
        self.currentObj = obj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #self.buildView()
        #self.loadScriptChoices()
        pass
        
        #self.gameJournalPanel = xrc.XRCCTRL(self.mainPanel, "GameJournalPanel")
        #self.gameJournalTreePanel = xrc.XRCCTRL(self.gameJournalPanel, "GameJournalTreePanel")   
    
        
 #added by qiaosi on 16/4/11
class ParticlePropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['particle'], 'particlePanel')   
        
       
        self.button_1 = xrc.XRCCTRL(self, "button_1")
        self.button_1.Bind(wx.EVT_BUTTON, self.effect1)
        
        self.button_2 = xrc.XRCCTRL(self, "button_2")
        self.button_2.Bind(wx.EVT_BUTTON, self.effect2)
        
        self.button_3 = xrc.XRCCTRL(self, "button_3")
        self.button_3.Bind(wx.EVT_BUTTON, self.effect3)
        
        self.button_4 = xrc.XRCCTRL(self, "button_4")
        self.button_4.Bind(wx.EVT_BUTTON, self.effect4)
        
        self.button_5 = xrc.XRCCTRL(self, "button_5")
        self.button_5.Bind(wx.EVT_BUTTON, self.effect5)
        
        self.button_6 = xrc.XRCCTRL(self, "button_6")
        self.button_6.Bind(wx.EVT_BUTTON, self.x_add)
        self.button_7 = xrc.XRCCTRL(self, "button_7")
        self.button_7.Bind(wx.EVT_BUTTON, self.x_min)
        self.button_8 = xrc.XRCCTRL(self, "button_8")
        self.button_8.Bind(wx.EVT_BUTTON, self.y_add)
        self.button_9 = xrc.XRCCTRL(self, "button_9")
        self.button_9.Bind(wx.EVT_BUTTON, self.y_min)
        self.button_10 = xrc.XRCCTRL(self, "button_10")
        self.button_10.Bind(wx.EVT_BUTTON, self.z_add)
        self.button_11 = xrc.XRCCTRL(self, "button_11")
        self.button_11.Bind(wx.EVT_BUTTON, self.z_min)
        
        self.listParticle = xrc.XRCCTRL(self, 'listBoxParticles')
        self.listParticle.Bind(wx.EVT_LISTBOX, self.showProps)
        
        self.listCustomParticle = xrc.XRCCTRL(self, 'listBoxPtfFile')

        self.button_15 = xrc.XRCCTRL(self, "button_delParticle")
        self.button_15.Bind(wx.EVT_BUTTON, self.delParticle)
         
        self.txtXPos_p = xrc.XRCCTRL(self, "txtXPos_p")
        self.txtYPos_p = xrc.XRCCTRL(self, "txtYPos_p")
        self.txtZPos_p = xrc.XRCCTRL(self, "txtZPos_p")
        for x in (self.txtXPos_p, self.txtYPos_p, self.txtZPos_p):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateObjPos)
        
        self.txtXScale_p = xrc.XRCCTRL(self, "txtXScale_p")
        self.txtYScale_p = xrc.XRCCTRL(self, "txtYScale_p")
        self.txtZScale_p = xrc.XRCCTRL(self, "txtZScale_p")
        for x in (self.txtXScale_p, self.txtYScale_p, self.txtZScale_p):
            x.Bind(wx.EVT_TEXT_ENTER, self.updateObjScale)
        
        
        self.fileSelector_p = xrc.XRCCTRL(self, 'fileSelector_p')
        self.fileSelector_p.Bind(wx.EVT_BUTTON, self.onFileSelect_p)
        
        self.botton_addCustom = xrc.XRCCTRL(self, 'botton_addCustom')
        self.botton_addCustom.Bind(wx.EVT_BUTTON, self.addCustomParticle)
        
        self.button_removeCustom = xrc.XRCCTRL(self, "button_removeCustom")
        self.button_removeCustom.Bind(wx.EVT_BUTTON, self.removeCustomParticle)
        
        self.x=0.000
        self.y=0.000
        self.z=0.000
        self.fileName_ptf = None
        self.fileNameList_ptf = []
        #self.name_ptf = None
        self.object_particle_path = None

        self.object_particle = None
        

        
        for w in self.GetChildren():
            if not isinstance(w, wx.TextCtrl):
                w.Unbind(wx.EVT_SET_FOCUS)
        
        self.Bind(wx.EVT_CHILD_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
        
    def updateProps(self,obj):
        self.updateParticleListBox()
        self.updateCustomParticleListBox()

    
    def effect1(self,evt):
        
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #self.p = Particle()
        self.object_particle.addParticleEffect('./particles/steam.ptf')
        self.updateParticleListBox()
        

    def effect2(self,evt):
      
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.object_particle.addParticleEffect('./particles/fountain.ptf')         
        self.updateParticleListBox()
    
    def effect3(self,evt):
       
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.object_particle.addParticleEffect('./particles/fireish.ptf')      
        self.updateParticleListBox()
    
    def effect4(self,evt):
       
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.object_particle.addParticleEffect('./particles/smoke.ptf')    
        self.updateParticleListBox()
    
    def effect5(self,evt):
        
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        self.object_particle.addParticleEffect('./particles/dust.ptf')    
        self.updateParticleListBox()
    '''      
    def loadParticleConfig(self, file):
        #Start of the code from steam.ptf
       
        self.p.cleanup()
        self.p = ParticleEffect()
        self.p.loadConfig(Filename(file))        
        #Sets particles to birth relative to the object, but to render at toplevel
        #self.p.start(base.direct.selected.last)
        self.p.setPos(3.000, 0.000, 2.250)
        #Particle FX
        #particles =render.attachNewNode ('particleRenderParents')
        particles = base.direct.selected.last.attachNewNode ('particleRenderParents')
        particles.setLightOff()
        particles.setTransparency(TransparencyAttrib.MAlpha)
        particles.setBin ('fixed', 0)
        particles.setDepthWrite (False)
        particles.setShaderOff()

        self.p.start(base.direct.selected.last,particles)
        print self.p
        print self.p.renderParent
    '''       
        
    def z_add(self,evt):
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.x = self.object_particle.getParticlePositionByIndex(temp_index)[0]
            self.y = self.object_particle.getParticlePositionByIndex(temp_index)[1]
            self.z = self.object_particle.getParticlePositionByIndex(temp_index)[2]
            self.z +=1.0
            self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)
            self.updateParticleProps()
            
    def z_min(self,evt):      
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.x = self.object_particle.getParticlePositionByIndex(temp_index)[0]
            self.y = self.object_particle.getParticlePositionByIndex(temp_index)[1]
            self.z = self.object_particle.getParticlePositionByIndex(temp_index)[2]
            self.z -=1.0
            self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)
            self.updateParticleProps()
            
    def x_add(self,evt):      
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.x = self.object_particle.getParticlePositionByIndex(temp_index)[0]
            self.y = self.object_particle.getParticlePositionByIndex(temp_index)[1]
            self.z = self.object_particle.getParticlePositionByIndex(temp_index)[2]
            self.x +=1.0
            self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)
            self.updateParticleProps()
            
    def x_min(self,evt):      
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.x = self.object_particle.getParticlePositionByIndex(temp_index)[0]
            self.y = self.object_particle.getParticlePositionByIndex(temp_index)[1]
            self.z = self.object_particle.getParticlePositionByIndex(temp_index)[2]
            self.x -=1.0
            self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)
            self.updateParticleProps()
            
    def y_add(self,evt):       
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.x = self.object_particle.getParticlePositionByIndex(temp_index)[0]
            self.y = self.object_particle.getParticlePositionByIndex(temp_index)[1]
            self.z = self.object_particle.getParticlePositionByIndex(temp_index)[2]
            self.y +=1.0
            self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)
            self.updateParticleProps()
            
    def y_min(self,evt):
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.x = self.object_particle.getParticlePositionByIndex(temp_index)[0]
            self.y = self.object_particle.getParticlePositionByIndex(temp_index)[1]
            self.z = self.object_particle.getParticlePositionByIndex(temp_index)[2]
            self.y -=1.0
            self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)
            self.updateParticleProps()

        
    def updateObjPos(self,evt):
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            try:
                self.x = float(self.txtXPos_p.GetValue())
                self.y = float(self.txtYPos_p.GetValue())
                self.z = float(self.txtZPos_p.GetValue())
            except ValueError as e:
                msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
                self.txtXPos_p.SetValue(str(self.object_particle.getParticlePositionByIndex(temp_index)[0]))
                self.txtYPos_p.SetValue(str(self.object_particle.getParticlePositionByIndex(temp_index)[1]))
                self.txtZPos_p.SetValue(str(self.object_particle.getParticlePositionByIndex(temp_index)[2]))
            else:
                self.object_particle.setParticlePositionByIndex(temp_index,self.x, self.y, self.z)       
        
    def updateObjScale(self,evt):
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        temp_index =  self.listParticle.GetSelection() 
        if temp_index != -1:
            try:
                self.x = float(self.txtXScale_p.GetValue())
                self.y = float(self.txtYScale_p.GetValue())
                self.z = float(self.txtZScale_p.GetValue())
            except ValueError as e:
                msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
                self.txtXScale_p.SetValue(str(self.object_particle.getParticleScaleByIndex(temp_index)[0]))
                self.txtYScale_p.SetValue(str(self.object_particle.getParticleScaleByIndex(temp_index)[1]))
                self.txtZScale_p.SetValue(str(self.object_particle.getParticleScaleByIndex(temp_index)[2]))
            else:
                self.object_particle.setParticleScaleByIndex(temp_index,self.x, self.y, self.z)           
        

    
    def updateParticleListBox(self):
        self.listParticle.Clear()
        self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        for x in self.object_particle.particleEffectList:
            x = str(x).rsplit('/', 1)
            self.listParticle.Append(x[1])
            
    def updateCustomParticleListBox(self):
        self.listCustomParticle.Clear()
        for f in self.fileNameList_ptf:
            f = f.getBasenameWoExtension()
            self.listCustomParticle.Append(f)
        
            
    def showProps(self,evt):
        self.updateParticleProps()       
    
    
    def updateParticleProps(self):
        temp_index = self.listParticle.GetSelection() 
        if temp_index != -1:
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.txtXPos_p.SetValue(str(self.object_particle.getParticlePositionByIndex(temp_index)[0]))
            self.txtYPos_p.SetValue(str(self.object_particle.getParticlePositionByIndex(temp_index)[1]))
            self.txtZPos_p.SetValue(str(self.object_particle.getParticlePositionByIndex(temp_index)[2]))
            
            self.txtXScale_p.SetValue(str(self.object_particle.getParticleScaleByIndex(temp_index)[0]))
            self.txtYScale_p.SetValue(str(self.object_particle.getParticleScaleByIndex(temp_index)[1]))
            self.txtZScale_p.SetValue(str(self.object_particle.getParticleScaleByIndex(temp_index)[2]))    
    
    def delParticle(self,evt):
       temp_index =  self.listParticle.GetSelection() 
       if temp_index != -1: 
           self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last) 
           self.object_particle.delParticleEffectByIndex(temp_index)
           self.updateParticleListBox()
           
           
    def onFileSelect_p(self,evt):
        self.fileType_p = "Particle Effect files (*.ptf)|*.ptf"
        dialog_p = wx.FileDialog(self, "Select a .ptf file", wildcard=self.fileType_p, style=wx.FD_OPEN )
        if dialog_p.ShowModal() == wx.ID_OK:
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            self.fileName_ptf = Filename.fromOsSpecific(dialog_p.GetPath())
            self.fileNameList_ptf.append(self.fileName_ptf)
            #self.name_ptf = self.fileName_ptf.getBasenameWoExtension()
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))                        
        dialog_p.Destroy()
        self.updateCustomParticleListBox()
        
        
    def addCustomParticle(self, evt):
        temp_index =  self.listCustomParticle.GetSelection() 
        if temp_index != -1:
            temp_str =  str (self.fileNameList_ptf[temp_index])
            temp_str = "./particles/" + temp_str.rsplit('/', 1)[1]
            self.object_particle = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
            self.object_particle.addParticleEffect(temp_str)
            self.updateParticleListBox()
            
    def removeCustomParticle(self, evt):
        temp_index =  self.listCustomParticle.GetSelection() 
        if temp_index != -1:
            self.fileNameList_ptf.pop(temp_index)
            self.updateCustomParticleListBox()
class RopePropertyPanel(ObjectPropertyPanel):
    def __init__(self, parent, editor):
        ObjectPropertyPanel.__init__(self, parent, editor, RESOURCE_FILE['rope'], 'ropePanel')
        #print "Here"
                
        self.btnAddWP = xrc.XRCCTRL(self, "btnEditWP")
        self.btnAddWP.Bind(wx.EVT_BUTTON, self.editWaypoints)
        
        self.btnUpdate = xrc.XRCCTRL(self, "btnUpdate")
        self.btnUpdate.Bind(wx.EVT_BUTTON, self.updateSequence)
        
        
        self.txtObjectName = xrc.XRCCTRL(self, "txtObjectName")
        self.txtObjectName.Bind(wx.EVT_TEXT, self.updateObjectName)
        
        self.txtSeqTime = xrc.XRCCTRL(self, "txtSeqTime")
        self.txtSeqTime.Bind(wx.EVT_TEXT, self.updateSeqTime)
        #self.txtSeqTime.Enable(False)
        self.txtSeqTime.ChangeValue("5.0")
        
        
        #Preview
        self.btnPreview = xrc.XRCCTRL(self, "btnPlay")
        self.btnPreview.Bind(wx.EVT_BUTTON, self.previewSeq)
        
        self.btnStop = xrc.XRCCTRL(self, "btnReset")
        self.btnStop.Bind(wx.EVT_BUTTON, self.resetSeq)
        
        self.chkHide = xrc.XRCCTRL(self, "chkHide")
        self.chkHide.Bind(wx.EVT_CHECKBOX, self.toggleRope)
        
        # Radio buttons
        self.rdoLocked = xrc.XRCCTRL(self, "rdoLocked")
        self.rdoFree = xrc.XRCCTRL(self, "rdoFree")
        self.rdoLookAt = xrc.XRCCTRL(self, "rdoLookAt")
        
        self.rdoLocked.Bind(wx.EVT_RADIOBUTTON, self.updateOrient)
        self.rdoFree.Bind(wx.EVT_RADIOBUTTON, self.updateOrient)
        self.rdoLookAt.Bind(wx.EVT_RADIOBUTTON, self.updateOrient)
        
        self.rdoLocked.Enable(False)
        self.rdoFree.Enable(False)
        self.rdoLookAt.Enable(False)
        
        #hack to make combo box work
        for w in self.GetChildren():
            if not isinstance(w, wx.TextCtrl):
                w.Unbind(wx.EVT_SET_FOCUS)
        
        self.Bind(wx.EVT_CHILD_FOCUS, lambda(evt): self.editor.objectMgr.onEnterObjectPropUI(False))
        
        self.previewSeq = None
        self.lookAtObj = None
        self.followPath = False
        self.oldObjectName = ""
    
    def updateProps(self, obj):
        if isinstance(obj, LERope):
            #Change this later
            if len(obj.waypoints) > 1:
                self.txtSeqTime.Enable(True)
                self.btnUpdate.Enable(True)
                self.btnPreview.Enable(True)
                
                self.rdoLocked.Enable(True)
                self.rdoFree.Enable(True)
                self.rdoLookAt.Enable(True)
                self.updateRadioButtons(obj)
            else:
                self.txtSeqTime.Enable(False)
                self.txtSeqTime.ChangeValue("5.0")
                
                self.btnUpdate.Enable(False)
                self.btnPreview.Enable(False)
                
                self.rdoLocked.Enable(False)
                self.rdoFree.Enable(False)
                self.rdoLookAt.Enable(False)
                self.rdoLocked.SetValue(False)
                self.rdoFree.SetValue(False)
                self.rdoLookAt.SetValue(False)
                
            self.txtSeqTime.ChangeValue(str(obj.seqTime))
            if(obj.object != None):
                self.txtObjectName.ChangeValue(obj.object.getName())
            else:
                self.txtObjectName.ChangeValue("")
    
    
    def updateRadioButtons(self, obj):
        #obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(obj, LERope)== False):
            return
        self.rdoLocked.Enable(True)
        self.rdoFree.Enable(True)
        self.rdoLookAt.Enable(True)
        if obj.orientationChoice == 0:#self.followPath:
            self.rdoLocked.SetValue(True)
            self.rdoFree.SetValue(False)
            self.rdoLookAt.SetValue(False)
            #self.lookAtObj = None
        elif obj.orientationChoice == 1 and self.lookAtObj is not None:
            self.rdoLocked.SetValue(False)
            self.rdoFree.SetValue(False)
            self.rdoLookAt.SetValue(True)
        else:
            #print "Beginning"
            self.rdoLocked.SetValue(False)
            self.rdoFree.SetValue(True)
            self.rdoLookAt.SetValue(False)
    
    def updateOrient(self, evt):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        if self.rdoLocked.GetValue():
            self.followPath = True
            self.lookAtObj = None
            rope.orientationChoice =0
        elif self.rdoLookAt.GetValue():
            self.followPath = False
            dlg = ObjectInputDialog(self)
            lookAtName = dlg.ShowModal()
            dlg.Destroy()
            if lookAtName:
                lookAt = self.editor.objectMgr.findObjectById(lookAtName)
                self.lookAtObj = lookAt.getNodePath()
                rope.orientationChoice = 2
        else:
            self.followPath = False
            self.lookAtObj = None
            rope.orientationChoice = 1
    
    def editWaypoints(self, evt):
        obj = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(obj, LERope)== False):
            return
        dlg = WaypointDialog(self, obj.getName(), self.getWaypointNames())
        waypoints = dlg.ShowModal()
        dlg.Destroy()
        obj.clearWaypoints()
        if len(waypoints)>1:
            for waypoint in waypoints:
                obj.addWaypoint(waypoint)
            # Set the text boxes
#            self.txtSeqTime.Enable(True)
#            self.txtSeqTime.ChangeValue(str(camera.getSeqTime()))
#            self.btnUpdate.Enable(True)
            self.btnPreview.Enable(True)
#            self.updateRadioButtons(camera)
        else:
            self.btnUpdate.Enable(False)
            self.btnPreview.Enable(False)
#            self.rdoLocked.SetValue(False)
#            self.rdoFree.SetValue(False)
#            self.rdoLookAt.SetValue(False)
#            self.rdoLocked.Enable(False)
#            self.rdoFree.Enable(False)
#            self.rdoLookAt.Enable(False)
        

        # Create the visible line (rope) between them
        obj.genWaypointRope()
    
    def getWaypointNames(self):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        names = []
        for wp in rope.waypoints:
            obj = self.editor.objectMgr.findObjectById(wp)
            if obj:
                names.append(wp)
            else:
                rope.waypoints.remove(wp)
        return names   
    
    def updateObjectName(self,evt):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        self.objectName = self.txtObjectName.GetValue()
        self.object = self.editor.objectMgr.findObjectById(self.objectName)
        if(self.object != None):
            if(rope.oldObject and self.object.getName() != rope.oldObject.getName()):
                self.resetObjPosHpr()
            rope.object = self.object
            rope.startPos = self.object.getNodePath().getPos()
            rope.startHpr = self.object.getNodePath().getHpr()
            rope.oldObject = self.object
        else:
            rope.object = None
    
    def updateSeqTime(self, evt):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        try:
            seqTime = float(self.txtSeqTime.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtSeqTime.ChangeValue(str(rope.getSeqTime()))
        else:
            action = ActionSetProperty(self.editor, rope.setSeqTime, rope.getSeqTime, seqTime)
            self.editor.actionMgr.push(action)
            action() 
    
    def updateSequence(self, evt):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        rope.genWaypointRope()
        
    def previewSeq(self, evt):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        if self.btnPreview.GetLabel() == "Play":
            name = self.txtObjectName.GetValue()
            self.object = self.editor.objectMgr.findObjectById(name)
            seqTime = self.txtSeqTime.GetValue()
            if(rope.object == None):
                msg = wx.MessageDialog(self, "Cannot create sequence with non-existent object.","Invalid Object" , wx.OK|wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
                return
            rope.genWaypointRope()
            self.previewSeq = Sequence()
            temp =UniformRopeMotionInterval(rope.rope, 
                                                        rope.object.getNodePath(), 
                                                        float(seqTime), 
                                                        followPath=self.followPath, lookAt=self.lookAtObj)
            self.previewSeq.append(temp)
            self.previewSeq.append(Func(self.resetPlayUI))
            self.runSeq(self.object,self.previewSeq)
            self.btnPreview.SetLabel("Pause")
        elif self.btnPreview.GetLabel() == "Pause":
            self.previewSeq.pause()
            self.btnPreview.SetLabel("Resume")
        elif self.btnPreview.GetLabel() == "Resume":
            self.previewSeq.resume()
            self.btnPreview.SetLabel("Pause")
    
    def runSeq(self,obj, sequence):
        sequence.start()
    
    def resetPlayUI(self):
        self.btnPreview.SetLabel("Play")    
        
    def resetSeq(self, evt):  
        if self.previewSeq is not None:
            self.resetObjPosHpr()
            self.previewSeq.finish()
            self.btnPreview.SetLabel("Play")
    def resetObjPosHpr(self):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        if(rope.oldObject != None):
            rope.oldObject.setPos(rope.startPos)
            rope.oldObject.setHpr(rope.startHpr)
                  
    
    def toggleRope(self, evt):
        rope = self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        if(isinstance(rope, LERope)== False):
            return
        if self.chkHide.GetValue():
            rope.rope.hide()
        else:
            rope.rope.show()
