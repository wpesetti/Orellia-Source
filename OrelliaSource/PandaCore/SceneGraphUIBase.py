"""
Defines Scene Graph tree UI Base
"""
import wx
import cPickle as pickle
from pandac.PandaModules import *
from ActionMgr import *
from Objects import *

import Util

class SceneGraphUIDropTarget(wx.TextDropTarget):
    def __init__(self, editor):
        wx.TextDropTarget.__init__(self)
        self.editor = editor

    def OnDropText(self, x, y, text):
        self.editor.ui.sceneGraphUI.changeHierarchy(text, x, y)
        
class SceneGraphUIBase(wx.Panel):
    def __init__(self, parent, editor):
        wx.Panel.__init__(self, parent)

        self.editor = editor
        self.tree = wx.TreeCtrl(self, id=-1, pos=wx.DefaultPosition,
                  size=wx.DefaultSize, style=wx.TR_MULTIPLE|wx.TR_DEFAULT_STYLE|wx.TR_EXTENDED,
                  validator=wx.DefaultValidator, name="treeCtrl")
        self.root = self.tree.AddRoot('render')
        self.tree.SetItemPyData(self.root, "render")

        self.shouldShowPandaObjChildren = False

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetSizer(sizer); self.Layout()

        parentSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(self, 1, wx.EXPAND, 0)
        parent.SetSizer(parentSizer); parent.Layout()

        parent.SetDropTarget(SceneGraphUIDropTarget(self.editor))

        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelected)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag)

        self.currItem = None
        self.currObj = None
        self.menu = wx.Menu()
        self.populateMenu()
        self.freeMenu = wx.Menu()
        self.populateFreeMenu()
        self.Bind(wx.EVT_CONTEXT_MENU, self.onShowPopup)
        self.itemIndex = {} #maps strings to actual items for faster lookup

    def sort(self):
        self.recursiveSort(self.root)
        
    def recursiveSort(self, item):
        self.tree.SortChildren(item)
        if self.tree.ItemHasChildren(item):
            child,cookie = self.tree.GetFirstChild(item)
            while child:
                self.recursiveSort(child)
                child, cookie = self.tree.GetNextChild(item, cookie)
    
    def reset(self):
        #import pdb;set_trace()
        itemList = list()
        item, cookie = self.tree.GetFirstChild(self.root)
        while item:
             itemList.append(item)
             item, cookie = self.tree.GetNextChild(self.root, cookie)

        for item in itemList:
            self.tree.Delete(item)
            
        self.itemIndex = {}

    def traversePandaObjects(self, parent, objNodePath):
        itemId = self.tree.GetItemPyData(parent)
        i = 0
        for child in objNodePath.getChildren():
            if child.hasTag('OBJRoot'):
                # since they are already shown in scene graph tree
                continue
            namestr = "%s.%s"%(child.node().getType(), child.node().getName())
            newItem = self.tree.PrependItem(parent, namestr)
            newItemId = "%s.%s"%(itemId, i)
            self.tree.SetItemPyData(newItem, newItemId)

            # recursing...
            self.traversePandaObjects(newItem, child)
            i = i + 1

    def addPandaObjectChildren(self, parent):
        # first, find Panda Object's NodePath of the item
        itemId = self.tree.GetItemPyData(parent)
        if itemId == "render":
           return
        obj = self.editor.objectMgr.findObjectById(itemId)
        if obj is None:
           return

        objNodePath = obj.getNodePath()
        self.traversePandaObjects(parent, objNodePath)

        item, cookie = self.tree.GetFirstChild(parent)
        while item:
             # recursing...
             self.addPandaObjectChildren(item)
             item, cookie = self.tree.GetNextChild(parent, cookie)

    def removePandaObjectChildren(self, parent):
        # first, find Panda Object's NodePath of the item
        itemId = self.tree.GetItemPyData(parent)
        if itemId == "render":
           return
        obj = self.editor.objectMgr.findObjectById(itemId)
        if obj is None:
           self.tree.Delete(parent)
           return
        item, cookie = self.tree.GetFirstChild(parent)
        while item:
           # recurse...
           itemToRemove = item
           # continue iteration to the next child
           item, cookie = self.tree.GetNextChild(parent, cookie)
           self.removePandaObjectChildren(itemToRemove)

    def add(self, item, parentNP = None):
        #import pdb;pdb.set_trace()
        if item is None:
           return
        obj = self.editor.objectMgr.findObjectByNodePath(NodePath(item))
        if obj is None:
           return

        if parentNP is None :
           parentNP = obj.getNodePath().getParent()
        # If the parent is a joint
        if parentNP.getName().find(" <joint>") != -1:
            grandParentObj = self.editor.objectMgr.findObjectByNodePath(parentNP.getParent())
            parentObj = grandParentObj.joints[parentNP.getName()[0:parentNP.getName().index(" <joint>")]]
        else:
            parentObj = self.editor.objectMgr.findObjectByNodePath(parentNP)

        if parentObj is None:
            parent = self.root
        else:
            if parentNP.getName().find(" <joint>") != -1:
                grandParentName = parentNP.getParent().getName()
                parent = self.traverse(self.root, grandParentName+"/"+parentObj.getName())
            else:
                parent = self.traverse(self.root, parentObj.getName())

        name = NodePath(item).getName()
        if not name:
            name = ' '
        #namestr = "%s_%s_%s"%(obj[OG.OBJ_DEF].name, name, obj[OG.OBJ_UID])
        namestr = name
        # Only if it does not already exist in the scenegraphui
        if self.traverse(self.root, obj.getName()) is None:
            newItem = self.tree.AppendItem(parent, namestr)
            self.tree.SetItemPyData(newItem, obj.getName())
        
            # adding children of PandaObj
            if self.shouldShowPandaObjChildren:
               self.addPandaObjectChildren(newItem)
            self.tree.Expand(self.root)
            self.sort()
            
            self.itemIndex[item.getName()] = newItem
        
    def addJoint(self, item, parentObj):
        parent = self.traverse(self.root, parentObj.getName())
        # Only if it does not already exist in the scenegraphui
        if self.traverse(self.root, parentObj.getName()+"/"+item.getName()) is None:
            newItem = self.tree.AppendItem(parent, parentObj.getName()+"/"+item.getName())
            self.tree.SetItemPyData(newItem, parentObj.getName()+"/"+item.getName())
            self.itemIndex[parentObj.getName() + "/" + item.getName()] = newItem
        # adding children of PandaObj
        if self.shouldShowPandaObjChildren:
           self.addPandaObjectChildren(newItem)
        self.tree.Expand(self.root)
        self.sort()
        self.tree.Expand(parent)
        
    def removeJoint(self, jointName, joint):
        action = ActionDeleteJoint(self.editor, joint)
        self.editor.actionMgr.push(action)
        action()
        self.delete(joint.joint.getParent().getName()+"/"+jointName+" <joint>")

    def traverse(self, parent, itemId):
        if itemId not in self.itemIndex:
            return None
        else:
            return self.itemIndex[itemId]
        # # prevent from traversing into self
        # if itemId == self.tree.GetItemPyData(parent):
           # return None

        # # main loop - serching for an item with an itemId
        # item, cookie = self.tree.GetFirstChild(parent)
        # while item:
              # # if the item was found - return it
              # if itemId == self.tree.GetItemPyData(item):
                 # return item

              # # the tem was not found - checking if it has children
              # if self.tree.ItemHasChildren(item):
                 # # item has children - delving into it
                 # child = self.traverse(item, itemId)
                 # if child is not None:
                    # return child
                    
              # # continue iteration to the next child
              # item, cookie = self.tree.GetNextChild(parent, cookie)
        # return None

    def reParentTree(self, parent, newParent):
        # main loop - iterating over item's children
        item, cookie = self.tree.GetFirstChild(parent)
        while item:
           data = self.tree.GetItemText(item)
           itemId = self.tree.GetItemPyData(item)
           newItem = self.tree.AppendItem(newParent, data)
           self.tree.SetItemPyData(newItem, itemId)
           self.itemIndex[itemId] = newItem

           # if an item had children, we need to re-parent them as well
           if self.tree.ItemHasChildren(item):
              # recursing...
              self.reParentTree(item, newItem)

           # continue iteration to the next child
           item, cookie = self.tree.GetNextChild(parent, cookie)

    def reParentData(self, parent, child):
        child.wrtReparentTo(parent)

    def reParent(self, oldParent, newParent, child):
        if newParent is None:
           newParent = self.root
        itemId = self.tree.GetItemPyData(oldParent)
        
        #make sure we aren't parenting an object to one of its descendants
        obj = self.editor.objectMgr.findObjectById(itemId)
        parentId = self.tree.GetItemPyData(newParent)
        if parentId != "render":
            if parentId.find("<joint>") != -1:
                gpName, pName = parentId.split("/")
                pName = pName.split(" <")[0]
                newGrandParentObj = self.editor.objectMgr.findObjectById(gpName)
                if obj.nodePath.isAncestorOf(newGrandParentObj.nodePath):
                    return
                else:
                    self.reParentData(newGrandParentObj.joints[pName].getNodePath(), obj.getNodePath())
                    obj.setPos(Vec3(0,0,0))
            else:
                newParentObj = self.editor.objectMgr.findObjectById(parentId)
                if obj.nodePath.isAncestorOf(newParentObj.nodePath):
                    return
                else:
                    self.reParentData(newParentObj.getNodePath(), obj.getNodePath())
        else:
            self.reParentData(render, obj.getNodePath())
        
        oldItem = self.itemIndex[child]
        newItem = self.tree.AppendItem(newParent, child)
        self.tree.SetItemPyData(newItem, itemId)
        self.itemIndex[child] = newItem
        self.reParentTree(oldItem, newItem)

        self.tree.Delete(oldItem)
        if self.shouldShowPandaObjChildren:
           self.removePandaObjectChildren(oldParent)
           self.addPandaObjectChildren(oldParent)
           self.removePandaObjectChildren(newParent)
           self.addPandaObjectChildren(newpParent)

    def changeHierarchy(self, data, x, y):
        itemId = data
        
        items = []
        
        if self.tree.GetSelections() > 1:
            for item in self.tree.GetSelections():
                items.append(item)
        else:
            items = [self.traverse(self.tree.GetRootItem(), itemId)]
        if not items:
            return
            
        dragToItem, flags = self.tree.HitTest(wx.Point(x, y))
        
        
        for item in items:
            # Prevent reparenting joints
            if self.tree.GetItemText(item).find("<joint>") != -1:
                msg = wx.MessageDialog(self, "Cannot Reparent Joints", "", wx.OK|wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
                return
                
            if dragToItem == item:
                return
                    
        for item in items:
            data = self.tree.GetItemPyData(item)
            if dragToItem.IsOk():
                # undo function setup...
                action = ActionChangeHierarchy(self.editor, self.tree.GetItemPyData(self.tree.GetItemParent(item)), self.tree.GetItemPyData(item), self.tree.GetItemPyData(dragToItem), data)
                self.editor.actionMgr.push(action)
                action()
            else:
                #if dragged to a blank spot, parent to render
                action = ActionChangeHierarchy(self.editor, self.tree.GetItemPyData(self.tree.GetItemParent(item)), self.tree.GetItemPyData(item), "render", data)
                self.editor.actionMgr.push(action)
                action()

    def parent(self, oldParentId, newParentId, childName):
        oldParent = self.traverse(self.tree.GetRootItem(), oldParentId)
        newParent = self.traverse(self.tree.GetRootItem(), newParentId)
        self.reParent(oldParent, newParent, childName)
        self.sort()

    def showPandaObjectChildren(self):
        itemList = list()
        self.shouldShowPandaObjChildren = not self.shouldShowPandaObjChildren

        item, cookie = self.tree.GetFirstChild(self.root)
        while item:
             itemList.append(item)
             item, cookie = self.tree.GetNextChild(self.root, cookie)

        #import pdb;set_trace()
        for item in itemList:
             if self.shouldShowPandaObjChildren:
                self.addPandaObjectChildren(item)
             else:
                self.removePandaObjectChildren(item)
             # continue iteration to the next child

    def delete(self, itemId):
        item = self.traverse(self.root, itemId)
        if item:
           self.deleteChildren(item)
           self.tree.Delete(item)
           del self.itemIndex[itemId]
    
    def deleteChildren(self, item):
        child, cookie = self.tree.GetFirstChild(item)
        while child:
            del self.itemIndex[self.tree.GetItemPyData(child)]
            self.deleteChildren(child)
            child, cookie = self.tree.GetNextChild(item, cookie)
    
    def select(self, itemId, ensureVisible=True):
        item = self.traverse(self.root, itemId)
        if item:
           if not self.tree.IsSelected(item):
              self.tree.SelectItem(item)
           if ensureVisible:
              self.tree.EnsureVisible(item)

    def changeLabel(self, itemId, newName):
        item = self.traverse(self.root, itemId)
        if item:
            self.tree.SetItemText(item, newName)
            self.tree.SetItemPyData(item, newName)
            self.sort()
            self.itemIndex[newName] = item
            del self.itemIndex[itemId]

    def deSelect(self, itemId):
        item =  self.traverse(self.root, itemId)
        if item is not None:
           self.tree.UnselectItem(item)

    def onSelected(self, event):
        selections = self.tree.GetSelections()
        if len(selections) > 1:
            obj = self.editor.objectMgr.findObjectById(self.tree.GetItemPyData(selections[0]))
            if obj:
                self.editor.select(obj.getNodePath(), fMultiSelect = 0, fLEPane = 1)
            for s in selections[1:]:
                obj = self.editor.objectMgr.findObjectById(self.tree.GetItemPyData(s))
                if obj:
                    self.editor.select(obj.getNodePath(), fMultiSelect = 1, fLEPane = 1)
        elif len(selections) == 1:
            obj = self.editor.objectMgr.findObjectById(self.tree.GetItemPyData(selections[0]))
            if obj:
                self.editor.select(obj.getNodePath(), fMultiSelect = 0, fLEPane = 1)
                
        else:
            self.editor.deselectAll()
        
        for s in selections:
            self.tree.SelectItem(s)
    def onBeginDrag(self, event):
        item = event.GetItem()

        if item != self.tree.GetRootItem(): # prevent dragging root item
            text = self.tree.GetItemText(item)

            tdo = wx.TextDataObject(text)
            tds = wx.DropSource(self.tree)
            tds.SetData(tdo)
            tds.DoDragDrop(True)

    def onShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)

        item, flags = self.tree.HitTest(pos)
        if not item.IsOk():
            return
        self.currItem = item
        itemId = self.tree.GetItemPyData(item)
        if not itemId:
            return
        self.currObj = self.editor.objectMgr.findObjectById(itemId);
        if self.currObj:
            self.PopupMenu(self.menu, pos)
        
        else:
            self.PopupMenu(self.freeMenu, pos)
            
        #self.currObj = self.editor.objectMgr.findObjectById(itemId);
        #if self.currObj:
        #    self.PopupMenu(self.menu, pos)
        

    def populateMenu(self):
        menuitem = self.menu.Append(-1, 'Expand All')
        self.Bind(wx.EVT_MENU, self.onExpandAllChildren, menuitem)
        menuitem = self.menu.Append(-1, 'Collapse All')
        self.Bind(wx.EVT_MENU, self.onCollapseAllChildren, menuitem)
        menuitem = self.menu.Append(-1, 'Delete')
        self.Bind(wx.EVT_MENU, self.onDelete, menuitem)
        menuitem = self.menu.Append(-1, 'Rename')
        self.Bind(wx.EVT_MENU, self.onRename, menuitem)
        self.addTerrainMenuitem = self.menu.Append(-1,'Add Terrain')
        self.Bind(wx.EVT_MENU, self.onAddNewTerrain, self.addTerrainMenuitem )
        self.populateExtraMenu()

    def populateExtraMenu(self):
        # You should implement this in subclass
        raise NotImplementedError('populateExtraMenu() must be implemented in subclass')

    def onCollapseAllChildren(self, evt=None):
        if self.currItem:
            self.tree.CollapseAllChildren(self.currItem)

    def onExpandAllChildren(self, evt=None):
        if self.currItem:
            self.tree.ExpandAllChildren(self.currItem)

    def onDelete(self, evt=None):
        if self.currObj is None:
            return
        
        #uid = self.currObj.getName()
        #self.editor.objectMgr.removeObjectById(uid)
        action = ActionDeleteObj(self.editor)
        self.editor.actionMgr.push(action)
        action()
        
    def onAddNewTerrain(self, evt):
        self.editor.addEmptyTerrain()
        #self.delete(uid)
    def populateFreeMenu(self):
        self.addTerrainMenuitem = self.freeMenu.Append(-1,'Add Terrain')
        self.Bind(wx.EVT_MENU, self.onAddNewTerrain, self.addTerrainMenuitem )
        pass
        
    def onRename(self, evt=None):
        if self.currObj is None:
            return

        self.editor.ui.bindKeyEvents(False)
        dialog = wx.TextEntryDialog(None, '', 'Input new name', defaultValue=self.currObj.getName())
        if dialog.ShowModal() == wx.ID_OK:
            newName = dialog.GetValue()
        dialog.Destroy()
        self.editor.ui.bindKeyEvents(True)
        
        if newName in self.editor.objectMgr.objects:
            dialog = wx.MessageDialog(self, "Name '" + newName + "'is already in use.", "Duplicate Name", wx.OK|wx.ICON_HAND)
            dialog.ShowModal()
            dialog.Destroy()
        elif Util.toObjectName(newName) != newName:
            dialog = wx.MessageDialog(self, "Name '" + newName + "'is not a valid object name.", "Invalid Name", wx.OK|wx.ICON_HAND)
            dialog.ShowModal()
            dialog.Destroy()
        else:
            action = ActionRenameObj(self.editor, self.currObj.getName(), newName)
            self.editor.actionMgr.push(action)
            action()
