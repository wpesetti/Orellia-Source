import wx
import os

from wx.lib.scrolledpanel import ScrolledPanel
import wx.lib.agw.pycollapsiblepane as pyPane
from direct.wxwidgets.WxSlider import *
from pandac.PandaModules import *
from wx import xrc
from pandac.PandaModules import Filename

RESOURCE_FILE = {'base':'/XRC/ObjectUI/panelBase.xrc','material':'/XRC/ObjectUI/panelMaterial.xrc',
                 'renderEffect':'/XRC/ObjectUI/panelRenderEffect.xrc','fog':'/XRC/ObjectUI/panelFog.xrc',
                 'staticMesh':'/XRC/ObjectUI/panelStaticMesh.xrc','actor':'/XRC/ObjectUI/panelActor.xrc',
                 'light':'/XRC/ObjectUI/panelLight.xrc','camera':'/XRC/ObjectUI/cameraBase.xrc',}

class ObjectPropertyUI(ScrolledPanel):
    def __init__(self, parent, editor):
                
        ScrolledPanel.__init__(self, parent)      
        self.parent = parent
        self.editor = editor

        
        self.sizer = wx.FlexGridSizer()
        self.sizer.SetRows(8)
        
        self.basePane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.materialPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.renderEffectPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE )
        self.fogPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.staticMeshPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.actorPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.lightPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        self.cameraPane = pyPane.PyCollapsiblePane(self, -1, style =  pyPane.CP_GTK_EXPANDER | wx.CP_NO_TLW_RESIZE)
        
        panes = [self.basePane, self.materialPane, self.renderEffectPane, 
                 self.fogPane, self.staticMeshPane, self.actorPane, 
                 self.lightPane, self.cameraPane]
        
        self.basePane.SetLabel("General")
        self.materialPane.SetLabel("Material")
        self.renderEffectPane.SetLabel("Effects")
        self.fogPane.SetLabel("Fog")
        self.staticMeshPane.SetLabel("Static Mesh")
        self.actorPane.SetLabel("Actor")
        self.lightPane.SetLabel("Lights")
        self.cameraPane.SetLabel("Camera")
        
        
        self.sizer.Add(self.basePane, wx.EXPAND)
        self.sizer.Add(self.materialPane, wx.EXPAND)
        self.sizer.Add(self.renderEffectPane, wx.EXPAND)
        self.sizer.Add(self.fogPane, wx.EXPAND)
        self.sizer.Add(self.staticMeshPane, wx.EXPAND)
        self.sizer.Add(self.actorPane, wx.EXPAND)
        self.sizer.Add(self.lightPane, wx.EXPAND)
        self.sizer.Add(self.cameraPane,wx.EXPAND)
        
        self.basePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.materialPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.renderEffectPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.fogPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneChanged)
        self.staticMeshPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.actorPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.lightPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        self.cameraPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,self.onPaneChanged)
        
        self.loadPanels()

        self.SetSizerAndFit(self.sizer)
        self.Layout()
        
    def onPaneChanged(self, evt):
        self.sizer.Fit(self)
        
    def expandAllPanes(self, panes):
        for pane in panes:
            pane.Expand()
        
    #Movable shoudl be removed at some point        
    def updateProps(self, obj, movable=True):
        pass
    
    def loadPanels(self):
        self.basePanel = ObjectPropertyPanel(self.basePane.GetPane(), self.editor, RESOURCE_FILE['base'],'basePanel')
        self.materialPanel = ObjectPropertyPanel(self.materialPane.GetPane(), self.editor, RESOURCE_FILE["base"],'basePanel') 

    
    
class ObjectPropertyPanel(wx.Panel):            
    def __init__(self, parent, editor, XRC, panelXRCName):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(XRC)
        self.res.LoadOnPanel(pre, parent, panelXRCName)
        self.PostCreate(pre)
        #self.Layout()
        