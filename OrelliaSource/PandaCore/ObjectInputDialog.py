import wx
import os
from wx import xrc

#General dialog that returns an object select

class ObjectInputDialog(wx.Dialog):
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource('/XRC/ObjectUI/ShaderInputs/dlgObjectInput.xrc')
        self.res.LoadOnDialog(pre, parent, 'dlgObjectInput')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
    
    def OnCreate(self, evt=None):
        self.Unbind(wx.EVT_INIT_DIALOG)
        self.treeSceneGraph = xrc.XRCCTRL(self, 'treeSceneGraph')
        self.btnOk = xrc.XRCCTRL(self, 'btnOk')
        self.btnCancel = xrc.XRCCTRL(self, 'btnCancel')
        
        self.btnOk.Bind(wx.EVT_BUTTON, self.onOk)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.treeSceneGraph.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        
        self.btnOk.Enable(False)
        
        self.Ok = False
        
        self.root = self.treeSceneGraph.AddRoot('render')
        
        sceneTree = base.le.ui.sceneGraphUI.tree
        self.buildTree(self.root, sceneTree.GetRootItem(), sceneTree)
          
        self.objName = ''
        
    def buildTree(self, ownItem, otherItem, otherTree):
        if otherTree.ItemHasChildren(otherItem):
            child, cookie = otherTree.GetFirstChild(otherItem)
            while child:
                newItem = self.treeSceneGraph.AppendItem(ownItem, otherTree.GetItemText(child))
                self.buildTree(newItem, child, otherTree)
                child, cookie = otherTree.GetNextChild(otherItem, cookie)
        
    def onSelect(self, evt=None):
        item = evt.GetItem()
        if item != self.root:
            self.btnOk.Enable(True)
            self.objName = self.treeSceneGraph.GetItemText(item)
        else:
            self.btnOk.Enable(False)
        
        
    def onCancel(self, evt=None):
        self.Close()
        self.objName = ''
        
    def onOk(self, evt=None):
        self.Ok = True
        self.Close()
        
    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        return self.objName