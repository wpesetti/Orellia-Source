import wx
import os
from wx import xrc

#General dialog that returns an object select

class WaypointDialog(wx.Dialog):
    def __init__(self, parent, cameraName, wps):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource('XRC/ObjectUI/dlgWaypoint.xrc')
        self.res.LoadOnDialog(pre, parent, 'dlgWaypoint')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.wps = wps
        
        self.cameraName = cameraName
    
    def OnCreate(self, evt=None):
        self.ok = False
        self.waypoints = []      
        self.Unbind(wx.EVT_INIT_DIALOG)
        self.treeSceneGraph = xrc.XRCCTRL(self, 'treeSceneGraph')
        self.btnAdd = xrc.XRCCTRL(self, 'btnAdd')
        self.btnCancel = xrc.XRCCTRL(self, 'btnCancel')
        
        self.btnAdd.Bind(wx.EVT_BUTTON, self.onAdd)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.treeSceneGraph.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag)
        
        #self.btnAdd.Enable(False)
        
        # List order buttons
        self.btnUp = xrc.XRCCTRL(self, 'btnUp')
        self.btnDown = xrc.XRCCTRL(self, 'btnDown')
        
        self.btnUp.Bind(wx.EVT_BUTTON, self.onUp)
        self.btnDown.Bind(wx.EVT_BUTTON, self.onDown)
        
        # Clear and remove buttons
        self.btnClear = xrc.XRCCTRL(self, 'btnClear')
        self.btnRemove = xrc.XRCCTRL(self, 'btnRemove')
        
        self.btnClear.Bind(wx.EVT_BUTTON, self.onClear)
        self.btnRemove.Bind(wx.EVT_BUTTON, self.onRemove)
        
        # Waypoint list
        self.listBoxWP = xrc.XRCCTRL(self, 'listBoxWP')
        self.listBoxWP.Bind(wx.EVT_LISTBOX, self.onSelect)
        self.listBoxWP.SetDropTarget(WaypointTextDropTarget(self.listBoxWP))
        
        self.listBoxWP.SetItems(self.wps)
        
        self.root = self.treeSceneGraph.AddRoot('render')
        
        sceneTree = base.le.ui.sceneGraphUI.tree
        self.buildTree(self.root, sceneTree.GetRootItem(), sceneTree)
        
        # If the dialog is opened on a camera with waypoints
        if self.wps != []:
            self.btnUp.Enable(True)
            self.btnDown.Enable(True)
            self.btnRemove.Enable(True)
        else:
            self.btnUp.Enable(False)
            self.btnDown.Enable(False)
            self.btnRemove.Enable(False)
        
    def buildTree(self, ownItem, otherItem, otherTree):
        if otherTree.ItemHasChildren(otherItem):
            child, cookie = otherTree.GetFirstChild(otherItem)
            while child:
                newItem = self.treeSceneGraph.AppendItem(ownItem, otherTree.GetItemText(child))
                self.buildTree(newItem, child, otherTree)
                child, cookie = otherTree.GetNextChild(otherItem, cookie)
    
    def onSelect(self, evt=None):
        if self.listBoxWP.GetItems() != []:
            self.btnUp.Enable(True)
            self.btnDown.Enable(True)
            self.btnRemove.Enable(True) 
    
    def onBeginDrag(self, evt=None):
        item = evt.GetItem()
        itemName = self.treeSceneGraph.GetItemText(item)
        if itemName != self.cameraName and itemName != "render":
            if self.listBoxWP.GetItems().count(itemName) == 0:
                txtData = wx.TextDataObject(itemName)
                txtDropSource = wx.DropSource(self.treeSceneGraph)
                txtDropSource.SetData(txtData)
                txtDropSource.DoDragDrop(True)
        
    def onCancel(self, evt=None):
        self.Close()
        self.waypoints = self.wps
        
    def onAdd(self, evt=None):
        self.ok = True
        self.waypoints = self.listBoxWP.GetItems()
        self.Close()
        
    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        if self.ok:
            return self.waypoints
        else:
            return self.wps
        return self.waypoints
    
    def onUp(self, evt=None):
        ind = self.listBoxWP.GetSelection()
        items = self.listBoxWP.GetItems()
        if len(items) > 1:
            wp = items.pop(ind)
            if ind >=1:
                items.insert(ind-1,wp)
                self.listBoxWP.SetItems(items)
                self.listBoxWP.SetSelection(ind-1)      
    
    def onDown(self, evt=None):
        ind = self.listBoxWP.GetSelection()
        items = self.listBoxWP.GetItems()
        length = len(items)
        if length > 1:
            wp = items.pop(ind)
            if ind <(length-1):
                items.insert(ind+1,wp)
                self.listBoxWP.SetItems(items)
                self.listBoxWP.SetSelection(ind+1)
    
    def onRemove(self, evt=None):
        ind = self.listBoxWP.GetSelection()
        items = self.listBoxWP.GetItems()
        if items != []:
            items.pop(ind)
            self.listBoxWP.SetItems(items)
            if items == []:
                self.btnUp.Enable(False)
                self.btnDown.Enable(False)
                self.btnRemove.Enable(False)
    
    def onClear(self, evt=None):
        self.listBoxWP.Clear()
        self.btnUp.Enable(False)
        self.btnDown.Enable(False)
        self.btnRemove.Enable(False)
    
    def enableButtons(self):
        self.btnUp.Enable(True)
        self.btnDown.Enable(True)
        self.btnRemove.Enable(True)
        

class WaypointTextDropTarget(wx.TextDropTarget):
    def __init__(self, box):
        wx.TextDropTarget.__init__(self)
        self.box = box
    
    def OnDropText(self, x, y, wp):
        self.box.Append(wp)
        length = len(self.box.GetItems())
        self.box.SetSelection(length-1)
