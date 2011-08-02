import wx
import os
import shutil
import stat
import subprocess
from JournalMgr import *
from JournalEntry import *
from ActionMgr import *
import Library
import Util
from ImportUI import DuplicateNameDialog, FileCollisionDialog 
from pandac.PandaModules import *
from direct.wxwidgets.ViewPort import *
from direct.directtools.DirectManipulation import ObjectHandles
from direct.directtools.DirectGlobals import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from wx import xrc
from wx.lib.mixins.listctrl import TextEditMixin
import wx.gizmos
import xml.dom.minidom

import Debug

GUI_FILENAME = 'XRC/dlgJournalUI.xrc'

#LE_IMPORT_MASK = BitMask32.bit(4)
#LE_CAM_MASKS['import'] = LE_IMPORT_MASK

OK = 1
SKIP = 2
CANCEL = 3

class ListCtrlMultiEdit(wx.ListCtrl, TextEditMixin):
    pass
        

class JournalTextDropTarget(wx.TextDropTarget):
    def __init__(self, editor, parent, dialog=None):
        wx.TextDropTarget.__init__(self)
        self.editor = editor
        self.parent = parent
        self.dialog = dialog
        
    def OnDropText(self, x, y, text):
#        print x," ",y," ", text
#        print self.parent.GetViewStart()#journalTree.GetViewRect
#        print self.parent.GetScrollPixelsPerUnit()   
#        print "Scale: ", self.parent.GetScaleX(), " ", self.parent.GetScaleY()     
#        print self.parent.GetSize()
        # Get the libraryType and name
        ind = text.index(">")
        libraryType = text[0:ind]
        objectName = text[ind+1:len(text)]
        
        
        #if(type(self.parent) == "Panel")
        minX, minY = self.parent.GetPositionTuple()#ViewStart()
        x,y = self.parent.GetSizeTuple()
        maxX = minX + x#self.parent.GetSize()[0]
        maxY = minY + y#self.parent.GetSize()[1]
        
        #check if the item is in the range of the drop target's parent's size
        #Don't do anything if the item is outside of the drop target's parent.
        if(x<minX or x>maxX or y<minY or y>maxY):
            return
        
        #add the JournalEntry to the gameJournal
        if(libraryType == "JournalEntry"):
#            print "JournalEntry is catched"
#            print type(self.editor.lib.journalEntries[objectName])
#            print self.editor.lib.journalEntries[objectName]
            filename = Filename(self.editor.lib.journalEntries[objectName].getFullFilename())
            f = open(filename.toOsSpecific())
            doc = xml.dom.minidom.parse(f)
            root = doc.childNodes[0]
            
            if(root.localName == "journalEntry"):
                journalEntry = JournalEntry.decode(root)
                if(not self.editor.journalMgr.addJournalEntry(journalEntry)):
                    dlg = wx.MessageDialog(self.dialog, "The Journal Entry with tag "+journalEntry.tag+" already exist",\
                                           "Cannot add the journalEntry "+objectName+".",\
                    style=wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    if(self.dialog != None):
                        self.dialog.update() 
            else:
                #print the error message that the file has incorrect value.
                pass
            
          
            
            #load the journal Entry into the Scene's Journal
        
        
        

#dialog box for importing assets
class JournalDialog(wx.Dialog):
    def __init__(self, parent, id, title, editor):
        #Pre creation routine to allow wx to do layout from XRC
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(GUI_FILENAME)
        self.res.LoadOnDialog(pre, parent, 'dlgJournalUI')
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
        self.editor = editor
        self.filename = ''
        self.name = ''
    
    def OnCreate(self, e): 
        self.Unbind(wx.EVT_INIT_DIALOG)
        base.le.ui.bindKeyEvents(False) 
        
        #init all the panels from XRC for parenting later on
        self.mainPanel = xrc.XRCCTRL(self, "mainPanel")
        
        self.gameJournalPanel = xrc.XRCCTRL(self.mainPanel, "GameJournalPanel")
        self.gameJournalTreePanel = xrc.XRCCTRL(self.gameJournalPanel, "GameJournalTreePanel")
        #attaching a drop target on the gameJournalPanel
        gamejournalTextDrop = JournalTextDropTarget(self.editor,self.gameJournalTreePanel, self)
        self.SetDropTarget(gamejournalTextDrop)
        
        self.importedJournalPanel = xrc.XRCCTRL(self, "ImportedJournalPanel")     
        #the imported Journal entry List
        self.listCtrlImportedJE = xrc.XRCCTRL(self.importedJournalPanel,"listCtrlUnusedJournalEntries")
        self.listCtrlImportedJE.InsertColumn(0, "Quest Files")

        for i in range(self.listCtrlImportedJE.GetColumnCount()):
                self.listCtrlImportedJE.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        
        #buttons
        self.btnImportJE = xrc.XRCCTRL(self.importedJournalPanel, "btnImportJE")
        self.btnImportJE.Bind(wx.EVT_BUTTON, self.onImportJournalEntry)
        self.btnRemoveSelected = xrc.XRCCTRL(self.importedJournalPanel, "btnRemoveSelected")
        self.btnRemoveSelected.Bind(wx.EVT_BUTTON, self.onRemoveJournalEntryFromLibrary)
        self.btnRemoveSelected.Enable(False)
        
        #scroll=wx.ScrolledWindow(self.gameJournalTreePanel,-1, size = (500,500))
        self.journalTree = wx.gizmos.TreeListCtrl(self.gameJournalTreePanel, -1,style = wx.TR_DEFAULT_STYLE|wx.TR_ROW_LINES|wx.VSCROLL|wx.HSCROLL|wx.ALWAYS_SHOW_SB, name = "temp",size = (800,400))
        self.journalTree.AddColumn("Text", width=450)
        self.journalTree.AddColumn("Tag", width=150)
        self.journalTree.AddColumn("Endpoint", width=100)
        self.journalTree.AddColumn("Entry Value", width=100)
        #self.journalTree.AddColumn("Filename", width = 100)

        #self.journalTree.ShowColumn(4, False)
        #self.journalTree.SetStyle()
        #self.gameJournalTreePanel.SetScrollbars(20, 20, 1000/20, 1000/20)
        
        self.journalTree.SetColumnEditable(0, False)
        self.journalTree.SetColumnEditable(1, False)
        self.journalTree.SetColumnEditable(2, False)
        self.journalTree.SetColumnEditable(3, False)
        #self.journalTree.SetColumnEditable(4, False)
        
        self.root = self.journalTree.AddRoot("Quests")
        item=self.journalTree.AppendItem(self.root, "B", data=None)
        self.journalTree.SetItemText(item, "B1" , 1)
        self.journalTree.SetItemText(item, "B2" , 2)
        self.journalTree.SetItemText(item, "B3" , 3)
        #x = 20
        #y = 20
        #scroll.SetScrollbars(0,20,0,20+1)
       
       
       #Editing Panel
        self.editPanel = xrc.XRCCTRL(self, "EditPanel")
        
        self.editTag = xrc.XRCCTRL(self.editPanel, "tagTextCtrl")
        self.Bind(wx.EVT_TEXT, self.onTagEnter, self.editTag)
        self.editTag.Bind(wx.EVT_SET_FOCUS, self.onTagFocus)
        self.editTag.Bind(wx.EVT_KILL_FOCUS, self.onTagKillFocus)
        self.editEntryValue = xrc.XRCCTRL(self.editPanel, "entryValueTextCtrl")
        self.Bind(wx.EVT_TEXT, self.onEntryValueEnter, self.editEntryValue)
        self.editEntryValue.Bind(wx.EVT_SET_FOCUS, self.onEntryValueFocus)
        self.editEntryValue.Bind(wx.EVT_KILL_FOCUS, self.onEntryValueKillFocus)
        self.editEndpoint =  xrc.XRCCTRL(self.editPanel, "endpointCheckbox")
        self.Bind(wx.EVT_CHECKBOX, self.onCheck, self.editEndpoint)
        self.editText = xrc.XRCCTRL(self.editPanel, "text_ctrl_3")
        self.origValue = ""
        self.newValue = ""
        self.Bind(wx.EVT_TEXT, self.onTextEnter, self.editText)
        self.btnExport = xrc.XRCCTRL(self.mainPanel, "btnExportJE")
        self.btnExport.Bind(wx.EVT_BUTTON, self.onExportJournalEntry)
        

        #self.keyboarCheckbtn = wx.Button(self.editPanel)
        
        self.editTag.Bind(wx.EVT_TEXT_ENTER, self.onTagKeyDown)
        #self.editPanel.Bind(wx.EVT_LEFT_DOWN, self.OnTextCtrl1LeftDown) 
         
        
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onBeginDrag)
        #self.journalTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onChanged)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.onBeginEdit, self.journalTree)
        self.editItem = self.journalTree.GetRootItem()
        
        self.Bind(wx.EVT_TREE_ITEM_MENU, self.onRightClick, self.journalTree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,self.onRightClick, self.journalTree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onChanged, self.journalTree)
        
        self.oldJournalEntry = None
        self.oldJournalLine = None
        
        self.update()
        self.Show()
        self.Layout()
    
    def OnTextCtrl1LeftDown(self, evt):
        #print "LEFT CLICK"
        if(self.editTag.IsModified()):
            #"print here"
            self.onTagKeyDown(evt)
        
    def onImportJournalEntry(self, evt):
        dialog = wx.FileDialog(self, "Select a Journal Entry file", style=wx.FD_OPEN, wildcard= "Journal files(*.xml)|*.xml")
        if dialog.ShowModal() == wx.ID_OK:
            filename = Filename.fromOsSpecific(dialog.GetPath())
            self.name = filename.getBasenameWoExtension()
            self.filename = filename
            journalEntry = self.getJournalEntry()
            while True:
                try:
                    base.le.lib.checkJournalEntry(journalEntry)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        #self.restoreAssets()
                        #self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        #self.restoreAssets()
                        #self.Close()
                        return
                else:
                    break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addJournalEntry(journalEntry, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW)) 
            
            self.update()
            
            self.btnRemoveSelected.Enable(True)
    def onExportJournalEntry(self, evt):
        selected = self.journalTree.GetSelection()
        if(selected == self.root):
            return
        parent = self.journalTree.GetItemParent(selected)
        
        if(parent != self.root):
            return
        tag = self.journalTree.GetItemText(selected,1)
        journalEntryData = self.editor.journalMgr.getJournalEntry(tag)
        dlg = wx.TextEntryDialog(self, "Choose a name for this journal", defaultValue=tag)
        
        
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            filename = Filename(name+".xml")
            self.name = name
            self.filename = filename
            journalEntry = self.getJournalEntry()
            while True:            
                try:
                    base.le.lib.checkJournalEntry(journalEntry)
                except Library.DuplicateNameError as e:
                       dialog = DuplicateNameDialog(self, -1, e)
                       result = dialog.ShowModal()
                       dialog.Destroy()
                       if result == CANCEL or result == SKIP:
                            #self.restoreAssets()
                            #self.Close()
                           return
                except Library.FileCollisionError as e:
                        dialog = FileCollisionDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL or result == SKIP:
                            #self.restoreAssets()
                            #self.Close()
                            return
                else:
                    break
                    
            doc = xml.dom.minidom.Document()
            doc.appendChild(journalEntryData.encode(doc))
            
            # write the temporary source file
            f = open(self.filename.toOsSpecific(), 'w')
            f.write(doc.toxml())
            f.close()
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addJournalEntry(journalEntry, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW)) 
            
            self.update()
            
            self.btnRemoveSelected.Enable(True)
            
                   
            
                
    def getJournalEntry(self):
        return Library.JournalEntry(Util.toAssetName(self.name),self.filename)
    
    def builtList(self):
        #print "BuiltList Keys: " , self.lib.journalEntries.keys()
        for je in (self.lib.journalEntries.keys()):
            #if(not(self.editor.journalMgr.hasJournalEntryFile(je))):
            pos = self.listCtrlImportedJE.InsertStringItem(self.listCtrlImportedJE.GetItemCount(), je)
            self.listCtrlImportedJE.Select(pos, True)
            self.listCtrlImportedJE.EnsureVisible(pos)
                
            for i in range(self.listCtrlImportedJE.GetColumnCount()):              
                self.listCtrlImportedJE.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER&wx.LIST_AUTOSIZE)
        
        if self.listCtrlImportedJE.GetItemCount() == 0:
            self.btnRemoveSelected.Enable(False)
        else:
            self.btnRemoveSelected.Enable(True)
            self.listCtrlImportedJE.Select(0)
    def buildTree(self):
        #print "BuiltTree Keys: " , self.editor.journalMgr.journalEntries.keys()
        self.root = self.journalTree.AddRoot("root")
        for i in (self.editor.journalMgr.getJournalInOrder()):
            je = self.editor.journalMgr.journalEntries[i]
            item=self.journalTree.AppendItem(self.root, je.name, data=None)
            self.journalTree.SetItemText(item, je.tag , 1)
            #self.journalTree.SetItemText(item, je.filename, 4)
            #can we set these uneditable?
            self.journalTree.SetItemText(item, "" , 2)
            self.journalTree.SetItemText(item, "" , 3)
            for j in (je.getJournalLinesInOrder()):
                jl = je.journalLines[j]
                item2 = self.journalTree.AppendItem(item, jl.text, data=None)
                self.journalTree.SetItemText(item2, "" , 1)
                self.journalTree.SetItemText(item2, str(jl.endpoint) , 2)
                self.journalTree.SetItemText(item2, str(jl.entryValue) , 3)
                
        self.journalTree.ExpandAll(self.root)
                  
    def update(self, evt =None):
        self.lib = self.editor.lib
        self.listCtrlImportedJE.DeleteAllItems()
        self.builtList()
        #self.journalTree.EditLabel(self.editItem)
        #temp, cookie = self.journalTree.GetFirstChild(self.journalTree.GetRootItem())
        #print "Before update ",self.journalTree.GetItemText(temp,1)
        self.journalTree.DeleteRoot()
        self.buildTree()
        
        
#        pos = self.listCtrlImportedJE.InsertStringItem(self.listCtrlImportedJE.GetItemCount(), filename.getBasenameWoExtension())
#        #self.listCtrlImportedJE.SetStringItem(pos, 1, filename.getBasenameWoExtension())
#        #self.listCtrlImportedJE.SetStringItem(pos, 2, filename.toOsSpecific())
#        self.listCtrlImportedJE.Select(pos, True)
#        self.listCtrlImportedJE.EnsureVisible(pos)
#        for i in range(self.listCtrlImportedJE.GetColumnCount()):
#            self.listCtrlImportedJE.SetColumnWidth(i, wx.LIST_AUTOSIZE)
        
        pass
    def onRemoveJournalEntryFromLibrary(self, evt):
        
        success = False
        try: 
            toDelete = self.listCtrlImportedJE.GetFirstSelected()
            #print self.listCtrlImportedJE.GetItemText(toDelete)
            if(toDelete == -1):
                return
            
            msg = "Remove local files in addition to removing from library?"
            dialog = wx.MessageDialog(self, msg, caption = "Remove Asset", \
            style = wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            result = dialog.ShowModal()
            removeFile = result == wx.ID_YES
            if result == wx.ID_CANCEL:
                return
            #first try to delete from the library then delete from the list
            assetName = self.listCtrlImportedJE.GetItemText(toDelete)
            #print assetName
            self.editor.lib.removeJournalEntry(assetName, removeFile)
            #[Zeina]Since self.update() is called below we don't need to call this function.
            #self.listCtrlImportedJE.DeleteItem(toDelete)
                        
        except Library.AssetInUseError as e:
               dlg = wx.MessageDialog(self, "The Journal Entry '" + e.asset.name + "' could not be removed because it is being used by the Jouenal.",\
               caption = "Journal Entry In Use", style = wx.OK|wx.ICON_ERROR)
               dlg.ShowModal()
        except Library.AssetReferencedError as e:
               dlg = wx.MessageDialog(self, "The asset '" + e.asset.name + "' could not be removed because it is being referenced by another asset in the library.",\
               caption = "Could not Remove Asset", style = wx.OK|wx.ICON_ERROR)
               dlg.ShowModal()
        else:       
            success = True

        if success:
            if self.editor.saved:
                dlg = wx.MessageDialog(self, "This will save the project.", style=wx.OK)
                dlg.ShowModal()
            #self.editor.save()
            #self.editor.load(self.editor.currentProj.filename, resetViews=False, setSaved=False)
            self.update()
    def onBeginDrag(self, evt):
        item = evt.GetIndex()#GetItem()

        txtData = wx.TextDataObject(\
        'JournalEntry' + '>' + self.listCtrlImportedJE.GetItemText(item))
        txtDropSource = wx.DropSource(self.listCtrlImportedJE)
        txtDropSource.SetData(txtData)
        txtDropSource.DoDragDrop(True)
    
    def onBeginEdit(self, evt):
        item = evt.GetItem()
        rootItem = self.journalTree.GetRootItem()
        if(item == rootItem):
            evt.Veto()
    
    def resetEdit(self):
        self.editTag.Clear()
        self.editEntryValue.Clear()
        #self.editEndpoint.Hide()
        self.editText.Clear()
        
            
    def hideEdit(self):
        #Editing Panel
        #self.editTag.Hide()
        self.disableText(self.editTag)
        self.disableText(self.editEntryValue)
        #self.editEntryValue.Hide()
        self.editEndpoint.Hide()
        #self.editText.Hide()
        self.disableText(self.editText)
    
    def disableText(self, text):
        text.ChangeValue("")
        text.Disable()
        #text.SetEditable(False)
        #text.SetBackgroundColour(wx.Colour(128,128,128))
    def enableText(self, text):
        text.Enable()
        #text.SetEditable(True)
        #text.SetBackgroundColour(wx.Colour(255,255,255))
        
    def onCheck(self,evt):

        item = self.journalTree.GetSelection()
        if(not(item.IsOk())):
            return
        rootItem = self.journalTree.GetRootItem()
        if(item == rootItem):
            return
        if(self.journalTree.GetItemParent(item) == rootItem):
            return
#        if(self.editEndpoint.isChecked()):
#            self.journalTree.SetItemText(item,2,True)
#        else:
#            self.journalTree.SetItemText(item,2,False)
        self.oldJournalLine.endpoint = evt.IsChecked() 
        self.journalTree.SetItemText(item,str(evt.IsChecked()), 2)
   
    #wxTE_PROCESS_ENTER
    def onTextEnter(self, evt):
        item = self.journalTree.GetSelection()
        if(not(item.IsOk())):
            return
        rootItem = self.journalTree.GetRootItem()
        if(item == rootItem):
            return        
        parent = self.journalTree.GetItemParent(item)
        
        changedText = evt.GetString()
        
        #update the texts for Journal Entry or JournalLine
        #depending on which one was selected.
        self.recordSelected()
        if(parent == rootItem):
            self.oldJournalEntry.name = changedText 
            self.journalTree.SetItemText(item,changedText, 0)
        else:
            self.oldJournalLine.text = changedText
            self.journalTree.SetItemText(item,changedText, 0)
    
    def changeValueOnItem(self,item,col, value, newValue):
        self.journalTree.SetItemText(item,newValue, col)
    
    def changeValueBackOnItem(self, item, col, value, newValue):
        self.journalTree.SetItemText(item, value, col)
    
    def onTagKeyDown(self,evt):
        action = ActionGeneric(self.editor, self.editTag.Redo, self.editTag.Undo)
        self.editor.actionMgr.push(action)
        
    def undoWrapper(self):
        self.tagUndoCalled = True
        self.editTag.Undo()#undoFn()
    def redoWrapper(self, str):
        #self.tagUndoCalled+=1
        self.editTag.Redo()
        
        
    

    #self.tagRedoCalled =
    def onTagFocus(self, evt):
        if self.editTag.IsEnabled()==False:
            return
        self.recordSelected()
        self.origValue = self.oldJournalEntry.tag
        self.newValue = self.oldJournalEntry.tag
    
    def onTagKillFocus(self, evt):
        if self.editTag.IsEnabled()==False:
            return
        item = self.journalTree.GetSelection()
        if(self.origValue == self.newValue):
            return
        if(self.newValue == None or self.newValue == ""):
            self.editTag.SetValue(self.oldJournalEntry.tag)
            return
        
        if(self.updateJournalEntryTag(self.newValue)):
            self.journalTree.SetItemText(item,self.newValue,1)
        else:
            self.editTag.SetValue(self.oldJournalEntry.tag)
        
                        
    def onTagEnter(self, evt):
        item = self.journalTree.GetSelection()
        if(not(item.IsOk())):
            return
        rootItem = self.journalTree.GetRootItem()
        if(item == rootItem):
            return
        if(self.journalTree.GetItemParent(item) != rootItem):
            return
        changedText = evt.GetString()
        self.newValue = changedText
        self.journalTree.SetItemText(item,changedText, 1)
    
    def onEntryValueFocus(self, evt):
        if self.editEntryValue.IsEnabled()==False:
            return
        self.recordSelected()
        self.origValue = int(self.oldJournalLine.entryValue)
        self.newValue = int(self.oldJournalLine.entryValue)
    
    def onEntryValueKillFocus(self, evt):
        if self.editEntryValue.IsEnabled()==False:
            return
        item = self.journalTree.GetSelection()
        if(self.newValue == self.origValue):
            return
        
        if(self.newValue == None or 
           self.newValue == "" or
           str(self.newValue).isdigit() == False):
            self.editEntryValue.setValue(self.origValue)
            return
        
        if(self.updateLineEntryValue(int(self.newValue))== False):
            self.editEntryValue.SetValue(str(self.origValue))#(item,str(self.origValue),3)
            
        
     
    def onEntryValueEnter(self, evt):
        item = self.journalTree.GetSelection()
        if(not(item.IsOk())):
            return
        rootItem = self.journalTree.GetRootItem()
        if(item == rootItem):
            return
        if(self.journalTree.GetItemParent(item) == rootItem):
            return
        changedText = evt.GetString()
        if(str(changedText).isdigit() == False):
            evt.Veto()
            return
        self.newValue = int(changedText)
        self.journalTree.SetItemText(item,changedText, 3)
        #self.journalTree.SetItemText(item, changedText,3)
#        if changedText == "" or str(changedText).isdigit()== False:
#            entryValue = self.journalTree.GetItemText(item,3)
#            self.editEntryValue.SetValue(entryValue)
#            return
#            
        
        #if(self.updateLineEntryValue(int(changedText))):
        #    self.journalTree.SetItemText(item,changedText, 3)
        #else:
        #    self.journalTree.SetItemText(item,str(self.oldJournalLine.entryValue), 3)             
        
    def onChanged(self, evt):
        
        #print "Changed"
        item = evt.GetItem()
        #print "Tag begin ",self.journalTree.GetItemText(item, 1)
        #self.resetEdit()
        self.hideEdit()
        
        rootItem = self.journalTree.GetRootItem()
        if(item == rootItem):
            return
        
        parent = self.journalTree.GetItemParent(item)
        
        #if the parent is the rootItem then it is an Journal Entry title 
        if(parent == rootItem):
            #self.editTag.Show()
            self.enableText(self.editTag)
            tag = self.journalTree.GetItemText(item,1)
            self.editTag.SetValue(tag)
            #self.editText.Show()
            self.enableText(self.editText)
            self.editText.SetValue(self.journalTree.GetItemText(item,0))
        else:
            entryValue = self.journalTree.GetItemText(item,3)
            tag = self.journalTree.GetItemText(parent,1)            
            #self.editText.Show()
            self.enableText(self.editText)
            self.editText.SetValue(self.journalTree.GetItemText(item,0))
            #self.editEntryValue.Show()
            self.enableText(self.editEntryValue)
            self.editEntryValue.SetValue(entryValue)  
            self.editEndpoint.Show()
            endpoint = self.journalTree.GetItemText(item,2)
            if(endpoint == "False"):
                self.editEndpoint.SetValue(False)
            else:
                self.editEndpoint.SetValue(True)
            #self.editEndpoint.SetValue(bool(self.journalTree.GetItemText(item,2)))
        width, height = self.GetSizeTuple() 
        self.SetSizeWH(width*0.000001, height*0.000001)    
        #self.updateData()
        
    def onRightClick(self, evt):
        #print "Right Click"
        item = evt.GetItem()
        
        #if the root exist in the selection then return. This might be removed.
#        for x in self.journalTree.GetSelections():
#            if x == self.root:
#                return
        
        if len(self.journalTree.GetSelections()) > 1:
            menu = wx.Menu()
            it = wx.MenuItem(menu, wx.NewId(), "Remove... ")
            menu.AppendItem(it)
            menu.Bind(wx.EVT_MENU, lambda x : self.onRemove(x, item), it)
            
            self.PopupMenu(menu)
       
        else:
            if item:
                menu = wx.Menu()
                it = wx.MenuItem(menu, wx.NewId(), "Add Quest...")
                menu.AppendItem(it)
                menu.Bind(wx.EVT_MENU, lambda x : self.onAddEntry(x, item), it)
                
                #print self.journalTree.GetItemText(item,0)
                if(item != self.root):
                    it = wx.MenuItem(menu, wx.NewId(), "Add Entry... ")
                    menu.AppendItem(it)
                    menu.Bind(wx.EVT_MENU, lambda x : self.onAddLine(x, item), it)
                    it = wx.MenuItem(menu, wx.NewId(), "Remove... ")
                    menu.AppendItem(it)
                    menu.Bind(wx.EVT_MENU, lambda x : self.onRemove(x, item), it)
                
                self.PopupMenu(menu)
                
# Helper functions for ActionMgr
    def removeJournalLineFromJournalEntry(self, journalEntry, line):
        journalEntry.removeJournalLine(line.entryValue)
        if(len(journalEntry.journalLines)==0 ):
                self.editor.journalMgr.removeJournalEntry(journalEntry.tag)
        self.update()
    #this function is undo of removeJournalLines
    def addJournalEntryAndJournalLine(self, journalEntry, line):
        self.editor.journalMgr.addJournalEntry(journalEntry)
        journalEntry.addJournalLine(line)
        self.update()
                
    def addJournalLineToJournalEntry(self, journalEntry, line):
        while(journalEntry.addJournalLine(line)==False):
            #print "HERE LOOP"
            entryValue += 10
            line = JournalLine(text,int(entryValue),endpoint)
        self.update()
            
    def addJournalEntry(self, journalEntry):
        self.editor.journalMgr.addJournalEntry(journalEntry)
        self.update()
        
    def removeJournalEntry(self, journalEntry):
        self.editor.journalMgr.removeJournalEntry(journalEntry.tag)
        self.update()
#-------------------------------------
   
    def onAddEntry(self, evt, item):
        tag = "Tag"
        copy = "Copy"
        copyNo = 1
        #journalEntry = JournalEntry(tag,"Title" )
        while(self.editor.journalMgr.journalEntryExist(tag)):#not(self.editor.journalMgr.addJournalEntry(journalEntry))):
            tag = "Tag"+"-"+copy+str(copyNo)
            copyNo +=1
        journalEntry = JournalEntry(tag,"Quest" )     
        line = JournalLine("Template Entry", 10, False)
        journalEntry.addJournalLine(line)
        self.addJournalEntry(journalEntry)
#        action = ActionJournalGeneric(self.editor, self.addJournalEntry, self.removeJournalEntry, journalEntry)
#        self.editor.actionMgr.push(action)
#        action()
#        for i in self.editor.journalMgr.getJournalEntry(tag).journalLines.keys():
#            print "Key: ",i
#            print self.editor.journalMgr.getJournalEntry(tag).journalLines[i].entryValue
    
    def onRemove(self,evt,item):
        toDelete = item#self.journalTree.GetSelection()
        
        if(toDelete == self.root ):
            return
        parent = self.journalTree.GetItemParent(toDelete)
        
        if(parent == self.root):
            tag = self.journalTree.GetItemText(toDelete,1)
            journalEntry = self.editor.journalMgr.getJournalEntry(tag)
            self.removeJournalEntry(journalEntry)
#            action = ActionJournalGeneric(self.editor, 
#                                          self.removeJournalEntry, 
#                                          self.addJournalEntry,
#                                          journalEntry)
#            self.editor.actionMgr.push(action)
#            action()
            
            
        else:
            tag = self.journalTree.GetItemText(parent,1)
            entryValue = self.journalTree.GetItemText(toDelete,3)
            journalEntry = self.editor.journalMgr.getJournalEntry(tag)
            line = journalEntry.getJournalLine(int(entryValue))
            self.removeJournalLineFromJournalEntry(journalEntry, line)
            
#            action =ActionJournalGeneric(self.editor,
#                                 self.removeJournalLineFromJournalEntry,
#                                 self.addJournalEntryAndJournalLine,
#                                 journalEntry,
#                                 line)
#            self.editor.actionMgr.push(action)
#            action()
            
        pass
    
    def onAddLine(self, evt, item):
        #print "add line"
        selected = item#self.journalTree.GetSelection()
        #print self.journalTree.GetItemText(selected,0)
        if(selected == self.root):
            return
        parent = self.journalTree.GetItemParent(selected)
        text = "Template Entry"
        entryValue = 10
        endpoint = False
        tag =""
        
        if(parent == self.root):
            tag = self.journalTree.GetItemText(selected,1)
        else:
            tag = self.journalTree.GetItemText(parent,1)
        
        #print "Tag in adding",tag    
        journalEntry = self.editor.journalMgr.getJournalEntry(tag)
        
        while(journalEntry.journalLineExists(int(entryValue))):
            entryValue += 10
            
        line = JournalLine(text,int(entryValue),endpoint)
        
        self.addJournalLineToJournalEntry(journalEntry,line)
#        action = ActionJournalGeneric(self.editor, 
#                                      self.addJournalLineToJournalEntry,
#                                      self.removeJournalLineFromJournalEntry,
#                                      journalEntry,
#                                      line)
#        self.editor.actionMgr.push(action)
#        action()
        
    def updateData(self,evt = None):
        Debug.debug(__name__,"Data is being Updating")
        self.editor.fNeedToSave = True
        #children = self.journalTree.GetChildren(rootItem)
        parent = self.journalTree.GetRootItem()
        node, cookie = self.journalTree.GetLastChild(parent)
        #LEjournalEntries  = {}
        self.editor.journalMgr.reset()
        while node.IsOk():#for i in range(self.journalTree.GetChildrenCount(rootItem)): 
             name = self.journalTree.GetItemText(node, 0)
             tag = self.journalTree.GetItemText(node, 1)
             #print "Tag ", tag
             #filename  = self.journalTree.GetItemText(node, 4)
             journalEntry = JournalEntry(tag, name)
             #lines = self.journalTree.GetChildren(node)
             l, cookie = self.journalTree.GetFirstChild(node)
             while l.IsOk():#for j in range(self.journalTree.GetChildrenCount(node)):
                    text = self.journalTree.GetItemText(l, 0)
                    endpoint = self.journalTree.GetItemText(l, 2)
                    entryValue = self.journalTree.GetItemText(l,3)
                    journalLine = JournalLine(text,entryValue, endpoint)
                    journalEntry.addJournalLine(journalLine)
                    l = self.journalTree.GetNextSibling(l)
                    self.editor.journalMgr.addJournalEntry(journalEntry)
             #LEjournalEntries[LEjournalEntry.tag] = LEjournalEntry
             node = self.journalTree.GetPrevSibling(node)
             #self.editor.journalMgr.replaceJournalEntries(LEjournalEntries)
        #self.update()
    
    def recordSelected(self):
        item = self.journalTree.GetSelection()
        
        if(item):
            if(item == self.root):
                return
            #print self.journalTree.GetItemText(item ,0)
            parent =self.journalTree.GetItemParent(item)
            if(parent == self.root):
                tag = self.journalTree.GetItemText(item,1)
                self.oldJournalEntry = self.editor.journalMgr.getJournalEntry(tag)
            else:
                entryValue = self.journalTree.GetItemText(item,3)
                tag = self.journalTree.GetItemText(parent,1)
                self.oldJournalEntry = self.editor.journalMgr.getJournalEntry(tag)    
                self.oldJournalLine = self.oldJournalEntry.getJournalLine(int(entryValue))
                
                
         
    def updateLineEntryValue(self,entryValue, evt=None, ):
        #self.recordSelected()
        return self.oldJournalEntry.changeLineEntryValue(self.oldJournalLine.entryValue,entryValue)
   
    def updateJournalEntryTag(self,tag, evt = None, ):
        isSuccess =  self.editor.journalMgr.changeJournalEntryTag(self.oldJournalEntry.tag, tag)
        return isSuccess
    
                 
    def onClose(self, evt):
        #self.updateData()
        self.Destroy()
        
        
