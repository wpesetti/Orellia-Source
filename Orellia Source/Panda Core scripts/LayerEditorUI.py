"""
Defines Layer UI
"""
import wx
import sys
import cPickle as pickle
from pandac.PandaModules import *

import Util
from ActionMgr import *

class Layer:
    def __init__(self, name, editor):
        self.name = name
        self.objects = set()
        self.hidden = False
        self.locked = False
        self.editor = editor
     
    def getObjectNames(self):
        return sorted(map(lambda x: x.name, self.objects))
    
    #do not call these functions directly - go through the LayerEditorUI functions
    def addObject(self, obj):
        self.objects.add(obj)
        if self.locked:
            base.direct.iRay.unpickable.append(obj.nodePath.getName())
        if self.hidden:
            #make sure child nodes do not get hidden
            for np in obj.nodePath.getChildren():
                o = self.editor.objectMgr.findObjectByNodePath(np)
                if not np.isHidden() and o and not o in self.objects:
                    np.showThrough()
            obj.nodePath.hide()
        
    def removeObject(self, obj):
        self.objects.discard(obj)
        if self.locked:
            base.direct.iRay.unpickable.remove(obj.nodePath.getName())
        if self.hidden:
            for o in obj.nodePath.getChildren():
                o.detachNode()
                if not o.isHidden():
                    o.hide()
                    o.show()
                o.reparentTo(obj.nodePath)
                
            obj.nodePath.show()
            
    def hide(self):
        self.hidden = True
        for obj in self.objects:
            #make sure child nodes do not get hidden
            for np in obj.nodePath.getChildren():
                o = self.editor.objectMgr.findObjectByNodePath(np)
                if not np.isHidden() and o and not o in self.objects:
                    np.showThrough()
            obj.nodePath.hide()
    
    def show(self, saveHack=False):
        if not saveHack:    #hack for saving - all layers are shown before saving
                            #while leaving the layer marked hidden to avoid weirdness
                            #when the scene reloads
            self.hidden = False
        #fix all of the hiding/showing
        for obj in self.objects:
            for o in obj.nodePath.getChildren():
                o.detachNode()
                if not o.isHidden():
                    o.hide()
                    o.show()
                o.reparentTo(obj.nodePath)
                
            obj.nodePath.show()

    def lock(self):
        if not self.locked:
            self.locked = True
            for obj in self.objects:
                base.direct.iRay.unpickable.append(obj.nodePath.getName())
    
    def unlock(self):
        if self.locked:
            self.locked = False
            for obj in self.objects:
                base.direct.iRay.unpickable.remove(obj.nodePath.getName())
            
class LayerEditorUI(wx.Panel):
    def __init__(self, parent, editor):
        wx.Panel.__init__(self, parent)

        self.editor = editor
        self.editorTxt = "Layer Editor"
        self.layers = {}    #maps layer name to layer
        self.objIndex = {} #maps object to layer that object is in

        self.layersDataDict = dict()
        self.layersDataDictNextKey = 0
        self.systemLayerKeys = []
        self.layerLocked = {}
        self.layerList = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        self.layerList.InsertColumn(0, "Layers")
        self.layerList.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.layerList, 1, wx.EXPAND, 0)
        self.SetSizer(sizer); self.Layout()

        parentSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(self, 1, wx.EXPAND, 0)
        parent.SetSizer(parentSizer); parent.Layout()

        self.opAdd       = "Add Layer"
        self.opDelete    = "Delete Layer"
        self.opRename    = "Rename Layer"
        self.opAddObj    = "Add Selected Object(s)"
        self.opRemoveObj = "Remove Selected Object(s)"
        self.opShowObj   = "Show Layer Objects"
        self.opHideObj   = "Hide Layer Objects"
        self.opLockObj   = "Lock Layer Objects"
        self.opUnlockObj = "Unlock Layer Objects"
        self.opSelectObj = "Select Layer Objects"

        self.menuItemsGen = list()
        self.menuItemsGen.append(self.opAdd)

        self.menuItemsObj = list()
        self.menuItemsObj.append(self.opAddObj)
        self.menuItemsObj.append(self.opRemoveObj)
        self.menuItemsObj.append('')
        self.menuItemsObj.append(self.opHideObj)
        self.menuItemsObj.append(self.opShowObj)
        self.menuItemsObj.append('')
        self.menuItemsObj.append(self.opLockObj)
        self.menuItemsObj.append(self.opUnlockObj)
        self.menuItemsObj.append('')
        self.menuItemsObj.append(self.opSelectObj)
        self.menuItemsObj.append('')
        self.menuItemsObj.append(self.opRename)
        self.menuItemsObj.append(self.opDelete)

        self.popupmenu = wx.Menu()
        for item in self.menuItemsGen:
            if item:
                menuItem = self.popupmenu.Append(-1, item)
                self.Bind(wx.EVT_MENU, self.onPopupItemSelected, menuItem)
            else:
                self.popupmenu.AppendSeparator()

        self.Bind(wx.EVT_CONTEXT_MENU, self.onShowPopup)
        self.layerList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onShowMembers)

    def menuAppendGenItems(self):
        for item in self.menuItemsGen:
            if item:
                menuItem = self.popupmenu.Append(-1, item)
                self.Bind(wx.EVT_MENU, self.onPopupItemSelected, menuItem)
            else:
                self.popupmenu.AppendSeparator()

    def menuAppendObjItems(self, hitItem):
        for item in self.menuItemsObj:
            if item:
                if hitItem in self.systemLayerKeys:
                    if item in [self.opRemoveObj, self.opDelete, self.opAddObj]:
                        continue
                menuItem = self.popupmenu.Append(-1, item)
                self.Bind(wx.EVT_MENU, self.onPopupItemSelected, menuItem)
            else:
                self.popupmenu.AppendSeparator()

    def onShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)

        for menuItem in self.popupmenu.GetMenuItems():
            self.popupmenu.RemoveItem(menuItem)

        #import pdb;set_trace()
        hitItem, flags = self.layerList.HitTest(pos)
        if hitItem == -1:
           self.menuAppendGenItems()
        else:
           self.menuAppendObjItems(hitItem)
        self.PopupMenu(self.popupmenu, pos)

    def onPopupItemSelected(self, event):
        menuItem = self.popupmenu.FindItemById(event.GetId())
        text = menuItem.GetText()
        layerName = self.layerList.GetItemText(self.layerList.GetFirstSelected()).split(" <")[0]
        if text == self.opAddObj:
            action = ActionGeneric(self.editor, lambda: self.addSelected(layerName),\
            lambda: self.removeSelected(layerName))
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opRemoveObj:
            action = ActionGeneric(self.editor, lambda: self.removeSelected(layerName),\
            lambda: self.addSelected(layerName)) 
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opShowObj:
            action = ActionGeneric(self.editor, lambda: self.showLayer(layerName),\
            lambda: self.hideLayer(layerName))
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opHideObj:
            action = ActionGeneric(self.editor, lambda: self.hideLayer(layerName),\
            lambda: self.showLayer(layerName))
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opLockObj:
            action = ActionGeneric(self.editor, lambda: self.lockLayer(layerName),\
            lambda: self.unlockLayer(layerName))
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opUnlockObj:
            action = ActionGeneric(self.editor, lambda: self.unlockLayer(layerName),\
            lambda: self.lockLayer(layerName))
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opAdd:
            action = ActionAddLayer(self.editor)
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opDelete:
            action = ActionDeleteLayer(self.editor, layerName)
            self.editor.actionMgr.push(action)
            action()
        elif text == self.opRename:
            index = self.layerList.GetFirstSelected()
            oldName = self.layerList.GetItemText(index).split(" <")[0]
            dialog = wx.TextEntryDialog(None, '', 'Input new name', defaultValue=oldName)
            self.editor.ui.bindKeyEvents(False)
            if dialog.ShowModal() == wx.ID_OK:
                newName = dialog.GetValue()
                if Util.toAssetName(newName) != newName:
                    msg = wx.MessageDialog(self, "Layer name is invalid.", "Invalid Layer Name", wx.OK|wx.ICON_HAND)
                    msg.ShowModal()
                    msg.Destroy()
                elif newName in self.layers:
                    msg = wx.MessageDialog(self, "Layer name is already in use.", "Invalid Layer Name", wx.OK|wx.ICON_ERROR)
                    msg.ShowModal()
                    msg.Destroy()
                else:
                    action = ActionGeneric(self.editor, lambda: self.renameLayer(oldName, newName),\
                    lambda: self.renameLayer(newName, oldName))
                    self.editor.actionMgr.push(action)
                    action()
            self.editor.ui.bindKeyEvents(True)
        elif text == self.opSelectObj:
            self.selectLayerObjs(layerName)
        else:
           wx.MessageBox("You selected item '%s'" % text)

    def reset(self):
        self.layers = {}
        self.objIndex = {}
        self.layerList.ClearAll()
        self.layerList.InsertColumn(0, "Layers")

    def addNewLayer(self, name = None):
        if not name:
            name = 'Layer 1'
            i = 2
            while name in self.layers:
                name = 'Layer ' + str(i)
                i = i + 1
            
        newLayer = Layer(name, self.editor)
        
        self.layers[name] = newLayer
        self.layerList.InsertStringItem(self.layerList.GetItemCount(), name)
        self.layerList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        
        return name
        
    def addObjectToLayer(self, layerName, obj):
        if obj in self.objIndex:    #remove the object from other layers
            self.removeObjectFromLayer(self.objIndex[obj].name, obj)
        
        self.layers[layerName].addObject(obj)
        self.objIndex[obj] = self.layers[layerName]
        
    def removeObjectFromLayer(self, layerName, obj):
        self.layers[layerName].removeObject(obj)
        
        if self.objIndex[obj]:
            del self.objIndex[obj]
    
    def deleteLayer(self, layerName):
        for obj in list(self.layers[layerName].objects):
            self.removeObjectFromLayer(layerName, obj)
        
        del self.layers[layerName]
        
        index = self.layerList.FindItem(0, layerName)
        if index == -1:
            index = self.layerList.FindItem(0, layerName + " <", True)
        self.layerList.DeleteItem(index)

    def renameLayer(self, oldName, newName):
        self.layers[newName] = self.layers[oldName]
        del self.layers[oldName]
        self.layers[newName].name = newName
        index = self.layerList.FindItem(0, oldName)
        if index == -1:
            index = self.layerList.FindItem(0, oldName + " <", True)
        part = self.layerList.GetItemText(index).partition(" <")
        self.layerList.SetItemText(index, newName + "".join(part[1:]))
        self.layerList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        
    def addSelected(self, layer=None):
        if not layer:
            layer = self.layerList.GetItemText(self.layerList.GetFirstSelected()).split(" <")[0]
        for np in base.direct.selected.getSelectedAsList():
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            self.addObjectToLayer(layer, obj)
    
    def removeSelected(self, layer=None):
        if not layer:
            layer = self.layerList.GetItemText(self.layerList.GetFirstSelected())
        for np in base.direct.selected.getSelectedAsList():
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            self.removeObjectFromLayer(layer, obj)

    def onShowMembers(self, event): 
        layer = self.layers[event.GetItem().GetText().split(" <")[0]]
        dialog = wx.SingleChoiceDialog(None, layer.name, self.editorTxt, layer.getObjectNames())
        dialog.ShowModal()

    def hideLayer(self, layerName):
        layer = self.layers[layerName]
        layer.hide()
                
        index = self.layerList.FindItem(0, layerName)
        if index == -1:
            index = self.layerList.FindItem(0, layerName + " <", True)
        if layer.locked:
            self.layerList.SetItemText(index, layerName + " <hidden, locked>")
        else:
            self.layerList.SetItemText(index, layerName + " <hidden>")
        self.layerList.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def showLayer(self, layerName):
        layer = self.layers[layerName]
        layer.show()
        
        index = self.layerList.FindItem(0, layerName)
        if index == -1:
            index = self.layerList.FindItem(0, layerName + " <", True)
        if layer.locked:
            self.layerList.SetItemText(index, layerName + " <locked>")
        else:
            self.layerList.SetItemText(index, layerName)
    
    def lockLayer(self, layerName):
        layer = self.layers[layerName]
        layer.lock()
        
        index = self.layerList.FindItem(0, layerName)
        if index == -1:
            index = self.layerList.FindItem(0, layerName + " <", True)
        if layer.hidden:
            self.layerList.SetItemText(index, layerName + " <hidden, locked>")
        else:
            self.layerList.SetItemText(index, layerName + " <locked>")
            
        self.layerList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
    
    def unlockLayer(self, layerName):
        layer = self.layers[layerName]
        layer.unlock()
        
        index = self.layerList.FindItem(0, layerName)
        if index == -1:
            index = self.layerList.FindItem(0, layerName + " <", True)
        if layer.hidden:
            self.layerList.SetItemText(index, layerName + " <hidden>")
        else:
            self.layerList.SetItemText(index, layerName)

    def selectLayerObjs(self, layerName):
        layer = self.layers[layerName]
        
        for obj in layer.objects:
            if not obj.nodePath in base.direct.selected.getSelectedAsList():
                base.direct.select(obj.nodePath, fMultiSelect=True, fLEPane=True)
    
    #removes all references of an object from the layer editor(on object deletion)
    def clearObject(self, obj):
        if obj in self.objIndex:
            layer = self.objIndex[obj]
            self.removeObjectFromLayer(layer.name, obj)
    
    def encode(self, doc):
        layersNode = doc.createElement("layers")
        for layer in self.layers.values():           
            node = doc.createElement("layer")
            nameNode = doc.createElement("name")
            nameNode.appendChild(doc.createTextNode(layer.name))
            node.appendChild(nameNode)
            hiddenNode = doc.createElement("hidden")
            hiddenNode.appendChild(doc.createTextNode(str(int(layer.hidden))))
            node.appendChild(hiddenNode)
            lockedNode = doc.createElement("locked")
            lockedNode.appendChild(doc.createTextNode(str(int(layer.locked))))
            node.appendChild(lockedNode)
            for obj in layer.objects:
                objNode = doc.createElement("object")
                objNode.appendChild(doc.createTextNode(obj.name))
                node.appendChild(objNode)
            layersNode.appendChild(node)
        return layersNode
            
    
    def decode(self, node, merge=False, otherName=None):
        if not merge:
            self.reset()
        for layerNode in node.childNodes:
            if layerNode.localName == "layer":
                objNames = []
                hidden = False
                locked = False
                for n in layerNode.childNodes:
                    if n.localName == "name":
                        name = n.childNodes[0].data.strip()
                        if otherName:
                            name = otherName + '_' + name
                            if name in self.layers:
                                raise Util.SceneMergeError()
                    elif n.localName == "hidden":
                        hidden = bool(int(n.childNodes[0].data.strip()))
                    elif n.localName == "locked":
                        locked = bool(int(n.childNodes[0].data.strip()))
                    elif n.localName == "object":
                        objName = n.childNodes[0].data.strip()
                        if otherName:
                            objName = otherName + '_' + objName
                        objNames.append(objName)

                self.addNewLayer(name)
                if hidden:
                    self.hideLayer(name)
                if locked:
                    self.lockLayer(name)
                for o in objNames:
                    obj = self.editor.objectMgr.findObjectById(o)
                    self.addObjectToLayer(name, obj)
