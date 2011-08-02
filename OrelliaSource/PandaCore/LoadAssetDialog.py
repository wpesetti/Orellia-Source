import wx
import os
from wx import xrc

#General dialog that returns an asset based on the selection at Ok

class LoadAssetDialog(wx.Dialog):
    ##Filter is the type of asset you want to load
    def __init__(self, parent, filter):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource('XRC/dlgLoadAsset.xrc')
        self.res.LoadOnDialog(pre, parent, 'dlgLoadAsset')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.filter = filter
    def OnCreate(self, evt=None):
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        self.btnOk = xrc.XRCCTRL(self, "btnOk")
        self.btnCancel = xrc.XRCCTRL(self, "btnCancel")
        
        self.treeLibrary = xrc.XRCCTRL(self, "treeLibrary")
        self.root = self.treeLibrary.AddRoot("Assets")

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectionChanged)
        
        self.btnOk.Bind(wx.EVT_BUTTON, self.onOk)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        
#        if self.filter == "Meshes":
#            self.meshes = self.treeLibrary.AppendItem(self.root, "Meshes")
#        elif self.filter == "Actors":
#            self.actors = self.treeLibrary.AppendItem(self.root, "Actors")
#        elif self.filter == "Animations":
#            self.animations = self.treeLibrary.AppendItem(self.root, "Animations")
#        elif self.filter == "Textures":
#            self.textures = self.treeLibrary.AppendItem(self.root, "Textures")
#        elif self.filter == "Shaders":
#            self.shaders = self.treeLibrary.AppendItem(self.root, "Shaders")
#        elif self.filter == "Sounds":
#            self.sounds = self.treeLibrary.AppendItem(self.root, "Sounds")
#        elif self.filter == "Terrains":
#            self.terrains = self.treeLibrary.AppendItem(self.root, "Terrains")
      
        self.asset = None
        
        self.lib = base.le.lib
        self.buildTree()
        
        
    def buildTree(self):
        if self.filter == "Meshes": 
            for m in sorted(self.lib.meshes.keys()):
                self.treeLibrary.AppendItem(self.root, m)
        elif self.filter == "Actors":
            for a in sorted(self.lib.actors.keys()):
                self.treeLibrary.AppendItem(self.root, a)
        elif self.filter == "Animations":
            for a in sorted(self.lib.animations.keys()):
                self.treeLibrary.AppendItem(self.root, a)
        elif self.filter == "Textures":
            for t in sorted(self.lib.textures.keys()):
                self.treeLibrary.AppendItem(self.root, t)
        elif self.filter == "Shaders":
            for s in sorted(self.lib.shaders.keys()):
                self.treeLibrary.AppendItem(self.root, s)
        elif self.filter == "Sounds":   
            for s in sorted(self.lib.sounds.keys()):
                self.treeLibrary.AppendItem(self.root, s)
        elif self.filter == "Terrains":
            for t in sorted(self.lib.terrains.keys()):
                self.treeLibrary.AppendItem(self.root, t)     
    
    
    def onSelectionChanged(self, evt=None):
        item = self.treeLibrary.GetSelection()
#        if item and item not in (self.root, self.meshes, self.actors, self.animations, self.textures, self.shaders, self.sounds, self.terrains):
        assetName = self.treeLibrary.GetItemText(item)
        parent = self.treeLibrary.GetItemParent(item)
        assetType = self.filter
            
        if assetType == "Meshes":
            self.asset = self.lib.meshes[assetName]
        elif assetType == "Textures":
            self.asset = self.lib.textures[assetName]
        elif assetType == "Actors":
            self.asset = self.lib.actors[assetName]
        elif assetType == "Animations":
            self.asset = self.lib.animations[assetName]
        elif assetType == "Shaders":
            self.asset = self.lib.shaders[assetName]
        elif assetType == "Sounds":
            self.asset = self.lib.sounds[assetName]
        elif assetType == "Terrains":
            self.asset = self.lib.terrains[assetName]
                
        self.Refresh()
                
    def onCancel(self, evt=None):
        self.Close()
        self.asset = None
        
    def onOk(self, evt=None):
        self.Ok = True
        self.Close()
        
    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        return self.asset
    
