
import wx
from Util import DuplicateNameError, toObjectName, SceneDeleteError

import Project

#REFERENCE: Sort, recursivesort and reset are copied/referenced and slightlty changed from
# SceneGraphUIBase
class ScenesUIBase(wx.Panel):
    def __init__(self, parent, editor):
        wx.Panel.__init__(self, parent)
        
        self.editor = editor
        self.tree = wx.TreeCtrl(self, id=-1, pos=wx.DefaultPosition,
                  size=wx.DefaultSize, style=wx.TR_MULTIPLE|wx.TR_DEFAULT_STYLE|wx.TR_EXTENDED,
                  validator=wx.DefaultValidator, name="treeCtrl")
        self.root = self.tree.AddRoot('scenes')
        self.tree.SetItemPyData(self.root, "scenes")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetSizer(sizer); self.Layout()

        parentSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(self, 1, wx.EXPAND, 0)
        parent.SetSizer(parentSizer); parent.Layout()
        
        self.menu = wx.Menu()
        self.populateMenu()
        self.Bind(wx.EVT_CONTEXT_MENU, self.onShowPopup)
        
        self.activeItem = None
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
    
    def populateTreeFromScenes(self):
        for s in self.editor.currentProj.scenes.keys():
            self.add(str(s))
        self.tree.SortChildren(self.root)
        self.updateActiveColor()
        
    def add(self, item):
        if item is None:
           return
        #print type(item)#REMOVE LATER
        scene = self.editor.currentProj.getScene(item)
        if scene is None:
           return
       
        branch = self.tree.AppendItem(self.root,item)
        #create a child under scenes and because it is not active
        #make it grey
        self.tree.SetItemPyData(branch, item)
        
        ##if(self.tree.GetChildrenCount(self.root)>1):
        self.tree.SetItemTextColour(branch, wx.Colour(128,128,128))
            
        self.tree.SortChildren(self.root)
        
    def onAddNewScene(self, event):
        name = self.editor.addScene()
        self.editor.fNeedToSave = True
        #self.editor.createSceneFile(scene)
        self.add(name)
    
    def updateActiveColor(self):
        item, cookie = self.tree.GetFirstChild(self.root)
        while item:
             self.tree.SetItemTextColour(item,wx.Colour(128,128,128))
             if(self.tree.GetItemPyData(item) == self.editor.currentSceneName):
                 self.tree.SetItemTextColour(item, wx.Colour(0,0,0))
                 if(self.tree.GetItemPyData(item) == self.editor.currentProj.sceneName):
                     self.tree.SetItemTextColour(item, wx.Colour(227,47,15))              
             elif(self.tree.GetItemPyData(item) == self.editor.currentProj.sceneName):
                     self.tree.SetItemTextColour(item, wx.Colour(247,135,115))
             item, cookie = self.tree.GetNextChild(self.root, cookie)
             
    def onActivateScene(self, event):
        self.editor.resetScene()
        self.editor.openScene(self.currObj)
        self.updateActiveColor()
   
    def onStartScene(self,event):
        self.editor.currentProj.setOpeningScene(self.currObj)
        self.updateActiveColor()     
      
    def onRenameScene(self, event):
        name = self.currObj
        base.le.ui.bindKeyEvents(False)
        dlg = wx.TextEntryDialog(self, "Choose a new name for this scene", defaultValue=name)
        if dlg.ShowModal() == wx.ID_OK:
            newName = dlg.GetValue()
            if(newName == ""):
                wx.MessageDialog(self, "Invalid Name:No Name", caption="Invalid Name",\
                style=wx.OK|wx.ICON_HAND).ShowModal()
                return
            try:    
                self.editor.renameScene(name,newName)
                self.tree.SetItemText(self.currItem, newName)
                self.tree.SetPyData(self.currItem, newName)
                self.tree.SortChildren(self.root)
            except DuplicateNameError as dne:
                wx.MessageDialog(self, "Invalid Name:"+dne.name+" already exist.", caption="Invalid Name",\
                style=wx.OK|wx.ICON_HAND).ShowModal()
        base.le.ui.bindKeyEvents(True)
        
    def onRemoveScene(self, event):
        name = self.currObj
        dlg = wx.MessageDialog(self, "Do you want to remove the scene?", caption="Removing Scene",\
                               style = wx.YES | wx.NO)
        if dlg.ShowModal() == wx.ID_YES:
            try:
                self.editor.removeScene(self.currObj,True)
                self.tree.Delete(self.currItem)
                self.updateActiveColor()
            except SceneDeleteError:
               wx.MessageDialog(self, "Cannot remove the last scene.\nThere must be at least one scene.", caption = "Cannot Remove",\
                style=wx.OK|wx.ICON_HAND).ShowModal() 
               return
        else:
            return
        #item, cookie = self.tree.GetFirstChild(self.root)
    

        
        
    
    def onShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        
        item, flags = self.tree.HitTest(pos)
        if not item.IsOk():
            return
        self.currItem = item
        if item == self.root:
            return
        itemId = self.tree.GetItemPyData(item)
        if not itemId:
            return
        
        
        self.currObj = itemId#self.editor.currentProj.itemId);
        if self.currObj:
            #self.activateMenuitem = self.menu.Remove(self.activateMenuitem)
            #self.addTerrainMenuitem = self.menu.Remove(self.addTerrainMenuitem)
            #if(self.currObj == self.editor.currentSceneName):
            #    self.menu.Append(self.addTerrainMenuitem)
            #else:
             #   self.menu.Append(self.activateMenuitem)
                
            
            self.PopupMenu(self.menu, pos)
    
    
    
    
    def populateMenu(self):
        menuitem = self.menu.Append(-1, 'Make it Starting Scene')
        self.Bind(wx.EVT_MENU, self.onStartScene, menuitem)
        menuitem = self.menu.Append(-1, 'Add New Scene')
        self.Bind(wx.EVT_MENU, self.onAddNewScene, menuitem)
#        menuitem = self.menu.Append(-1, 'Delete')
#        self.Bind(wx.EVT_MENU, self.onCollapseAllChildren, menuitem)
        self.activateMenuitem = self.menu.Append(-1, 'Activate')
        self.Bind(wx.EVT_MENU, self.onActivateScene, self.activateMenuitem)
        menuitem = self.menu.Append(-1, 'Rename')
        self.Bind(wx.EVT_MENU, self.onRenameScene, menuitem)
        menuitem = self.menu.Append(-1, 'Remove...')
        self.Bind(wx.EVT_MENU, self.onRemoveScene, menuitem)
        
#        menuitem = self.menu.Append(-1, 'Rename')
#        self.Bind(wx.EVT_MENU, self.onRename, menuitem)
        self.populateExtraMenu()
            
    def populateExtraMenu(self):
        raise NotImplementedError('populateExtraMenu() must be implemented in subclass')
    
       
       