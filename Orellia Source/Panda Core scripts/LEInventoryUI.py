import wx
from wx import xrc
from wx.lib.mixins.listctrl import TextEditMixin

from InventoryMgr import *
from LoadAssetDialog import *
import Util


GUI_FILENAME = 'XRC/dlgInventoryUI.xrc'
DEFAULT_SCRIPT = 'Do Nothing'

class ListCtrlMultiEdit(wx.ListCtrl, TextEditMixin):
    pass

class LEInventoryUI(wx.Dialog):
    def __init__(self, parent, id, title, editor):
        #Pre creation routine to allow wx to do layout from XRC
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(GUI_FILENAME)
        self.res.LoadOnDialog(pre, parent, 'dlgInventoryUI')
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
        self.editor = editor
        self.inventoryMgr = self.editor.inventoryMgr
        self.filename = ''
        self.name = ''
        self.parametersUI = []
    
    def OnCreate(self, e):
        self.Unbind(wx.EVT_INIT_DIALOG)
        base.le.ui.bindKeyEvents(False)
        
        self.inventoryMapListCtrl = xrc.XRCCTRL(self, "InventoryMapListCtrl")
        #self.inventoryMapListCtrl.__class__ = ListCtrlMultiEdit
        self.setupInventoryMapList()
        
        self.addEntryBtn = xrc.XRCCTRL(self, "addButton")
        self.removeEntryBtn = xrc.XRCCTRL(self, "removeButton")
        
        
        self.tagTextCtrl = xrc.XRCCTRL(self,'tagTextCtrl')
        self.thumbnail = xrc.XRCCTRL(self, 'imgThumbnail')
        self.scriptChoice = xrc.XRCCTRL(self, "scriptChoice")
        self.loadScriptChoices()
        self.setupParameters()
       
        
        
        
        #self.inventoryMapListCtrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.onEditMap)
        self.buildInventoryMapList()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelection, self.inventoryMapListCtrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListDeSelection, self.inventoryMapListCtrl)
        self.Bind(wx.EVT_BUTTON, self.onAddEntry, self.addEntryBtn)
        self.Bind(wx.EVT_BUTTON, self.onRemoveEntry, self.removeEntryBtn)
 
        
        self.tagTextCtrl.Bind(wx.EVT_TEXT_ENTER, self.onTagEnter)
        self.tagTextCtrl.Enable(False)
        self.thumbnail.Bind(wx.EVT_BUTTON, self.onPickImage)
        self.thumbnail.Enable(False)   
        self.Bind(wx.EVT_CHOICE, self.onSwitchScript, self.scriptChoice)
        self.scriptChoice.Enable(False)
        
        #TextEditMixin.__init__(self.inventoryMapListCtrl)
        
        self.Show()
        self.Layout()

        
    def setupInventoryMapList(self):
        self.inventoryMapListCtrl.InsertColumn(0, "Item Tags")
        self.inventoryMapListCtrl.InsertColumn(1, "Thumbnail Image")
        self.inventoryMapListCtrl.InsertColumn(2, "Script on Use")
        self.inventoryMapListCtrl.InsertColumn(3, "Parameters")
        
    def buildInventoryMapList(self):
        self.inventoryMapListCtrl.DeleteAllItems()
        
        for entry in sorted(self.inventoryMgr.inventoryMap):
            itemTag = entry
            image = self.inventoryMgr.inventoryMap[entry].imageName
            script,values = self.inventoryMgr.getScriptAndArguments(entry) 
            pos = self.inventoryMapListCtrl.InsertStringItem(self.inventoryMapListCtrl.GetItemCount(), itemTag)
            self.inventoryMapListCtrl.SetStringItem(pos,1, image)
            self.inventoryMapListCtrl.SetStringItem(pos,2, script )
            self.writeValuesToList(pos, values)
            
            
                            
        if self.inventoryMapListCtrl.GetItemCount() == 0:
            self.removeEntryBtn.Enable(False)
        else:
            self.removeEntryBtn.Enable(True)
            self.inventoryMapListCtrl.Select(0)
        
    def onAddEntry(self, evt):
        no = 1
        tag = "item_"+str(no)
        while(self.inventoryMgr.hasItemTag(tag)):
            tag = "item_"+str(no)
            no += 1
            
        picture = ""
        success = self.inventoryMgr.addInventoryMapEntry(tag,picture)
        if(not success):
            return
        pos = self.inventoryMapListCtrl.InsertStringItem(self.inventoryMapListCtrl.GetItemCount(),tag)
        self.inventoryMapListCtrl.SetStringItem(pos, 1, picture)
        script, values = self.inventoryMgr.getScriptAndArguments(tag)
        self.inventoryMapListCtrl.SetStringItem(pos, 2,script )
        self.writeValuesToList(pos, values)
                
        self.removeEntryBtn.Enable(True)
    
    def onRemoveEntry(self,evt):
        item = self.inventoryMapListCtrl.GetFirstSelected()
        tag = self.inventoryMapListCtrl.GetItemText(item)
        self.inventoryMgr.removeInventoryMapEntry(tag)
        self.inventoryMapListCtrl.DeleteItem(item)
        
        
        if self.inventoryMapListCtrl.GetItemCount() == 0:
            self.removeEntryBtn.Enable(False)
        else:
            self.removeEntryBtn.Enable(True)
            self.inventoryMapListCtrl.Select(0)
    
    def onTagEnter(self, evt):
        selectedItem = self.inventoryMapListCtrl.GetFirstSelected()
        oldTag = self.inventoryMapListCtrl.GetItemText(selectedItem)
        
        tag = self.tagTextCtrl.GetValue()
        if(self.inventoryMgr.hasItemTag(tag)):
                evt.Veto()
        else:
            self.inventoryMgr.changeItemTag(oldTag,tag)
        
        self.inventoryMapListCtrl.SetItemText(selectedItem, tag)
        
        pass       
    def onEditMap(self,evt):
        id = evt.GetItem().GetId()
        tag = self.inventoryMapListCtrl.GetItem(id, 0).GetText()

        #if the tag is changed
        if(evt.GetColumn() == 0):
            oldTag = tag
            tag = evt.GetText()
            if(self.inventoryMgr.hasItemTag(tag)):
                evt.Veto()
            else:
                self.inventoryMgr.changeItemTag(oldTag, tag)
        elif(evt.GetColumn()==1):
            picture = evt.GetText()
            self.inventoryMgr.changeItemImage(tag,picture)
            
    def loadScriptChoices(self):
        self.scriptChoice.Clear()
        self.scriptChoice.Append(DEFAULT_SCRIPT)
        for s in sorted(self.editor.lib.actionScripts):
            self.scriptChoice.Append(s)

            
    def onListSelection(self,evt):
        self.scriptChoice.Enable(True)
        self.tagTextCtrl.Enable(True)
        self.thumbnail.Enable(True)
        
        selectedItem = self.inventoryMapListCtrl.GetFirstSelected()
        tag = self.inventoryMapListCtrl.GetItemText(selectedItem)
        item = self.inventoryMapListCtrl.GetItem(selectedItem,2)
        
        script, values = self.inventoryMgr.getScriptAndArguments(tag)
        image = self.inventoryMgr.inventoryMap[tag].imageName
        
        
        self.tagTextCtrl.SetValue(tag)
        
        if(image != ""):
            #self.thumbnail.Show()
            asset = self.editor.lib.textures[image]
            path = asset.getThumbnail().toOsSpecific()
            #self.lblInstanceCount.SetLabel(str(asset.numInScene))
            try:
                self.thumbnail.SetBitmapLabel(wx.Bitmap(path))
            except Exception as e:
                print e.message
        else:
            pass
            self.thumbnail.SetBitmapLabel(wx.Bitmap("default_thumb.jpg"))
            
        self.Refresh()
        
        choiceID = self.scriptChoice.FindString(script)
        self.scriptChoice.SetSelection(choiceID)
         
        if(script == "Do Nothing"):
            arguments = []
        else:
            scriptFile = self.editor.lib.scripts[script].getFullFilename()
            arguments = Util.getArgumentsFromScriptFile(scriptFile)    
    
        self.enableParameters(arguments)
        
        for i in range(len(values)):
            label, text = self.parametersUI[i]
            value = values[i]
            text.SetValue(value)
            
    def onListDeSelection(self, evt):
         self.tagTextCtrl.Enable(False)
         self.tagTextCtrl.SetValue("")
         self.thumbnail.SetBitmapLabel(wx.Bitmap("default_image.jpg"))
         self.thumbnail.Enable(False)
         self.scriptChoice.Enable(False)
         self.scriptChoice.SetSelection(-1)
         self.resetParameters()
        
        #self.selectedListItem = event.GetItem()
        #self.updateEditPanel()
        #self.editPanel.Show()
            
    def onSwitchScript(self, event=None):     
        self.resetParameters()
        selectedItem = self.inventoryMapListCtrl.GetFirstSelected()
        chosenScript = self.scriptChoice.GetStringSelection()
        tag =self.inventoryMapListCtrl.GetItemText(selectedItem)
        
        #script = self.inventoryMapListCtrl.GetItem(selectedItem,2)
        #event, script, id = self.getCurrentEventScriptID()
        #obj.setScript(DEFAULT_PRETAG+event, id,  chosenScript)
        self.inventoryMapListCtrl.SetStringItem(selectedItem, 2, chosenScript)
        self.inventoryMapListCtrl.SetStringItem(selectedItem, 3, "()")
        
        self.inventoryMgr.changeScriptNameAndArguments(tag, chosenScript,[])
        
        if(chosenScript == "Do Nothing"):
            arguments = []
        else:
            scriptFile = self.editor.lib.scripts[chosenScript].getFullFilename()
            arguments = Util.getArgumentsFromScriptFile(scriptFile) 
        self.enableParameters(arguments)
        self.writeFromUIToData()
        
            
    def setupParameters(self):
        #print "HEREEEEEEEEEEEE"
        for i in range(1,5):
            label = xrc.XRCCTRL(self, "label_"+str(i))
            text = xrc.XRCCTRL(self, "text_ctrl_"+str(i))
            text.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter)
            #text.Bind(wx.EVT_SET_FOCUS, self.onTextFocus)
            #text.Bind(wx.EVT_KILL_FOCUS, self.onTextKillFocus)
            if(text == None or label == None):
                break
            label.SetLabel("")
            text.Disable()
            self.parametersUI.append((label,text))
        
    def resetParameters(self):
        for label, text in self.parametersUI:
            label.SetLabel("")
            text.SetValue("")
            text.Disable()
            
    def enableParameters(self, arguments):
        self.resetParameters()
        counter = 0
        for argument in arguments:
            if(argument == "world"):
                continue
            #print "Counter:",counter
            #print len(self.parametersUI)
            label, text = self.parametersUI[counter]
            label.SetLabel(argument)
            text.Enable()
            #text.SetEditable(True)
            #text.SetBackgroundColour(wx.Colour(255,255,255))
            counter += 1
            
    def onTextEnter(self, evt):
        self.writeFromUIToData()
         
            
    def writeFromUIToData(self):
        selectedItem = self.inventoryMapListCtrl.GetFirstSelected()
        tag = self.inventoryMapListCtrl.GetItemText(selectedItem)
        values = []
        for label, text in self.parametersUI:
            if(text.IsEnabled()==False):
                continue
            value = text.GetValue()
            #maybe check
            values.append(value)
        
        self.inventoryMgr.changeScriptValues(tag, values)
        self.writeValuesToList(selectedItem,values)
            
    def writeValuesToList(self,item, values):
        self.inventoryMapListCtrl.SetStringItem(item, 3, "("+",".join(values)+")")
        
    def onPickImage(self,evt):
        selectedItem = self.inventoryMapListCtrl.GetFirstSelected()
        tag = self.inventoryMapListCtrl.GetItemText(selectedItem)
        dlg = LoadAssetDialog(self, filter = "Textures")
        asset = dlg.ShowModal()
        if (asset != None):
            #asset = self.editor.lib.textures[image]
            path = asset.getThumbnail().toOsSpecific()
            try:
                self.thumbnail.SetBitmapLabel(wx.Bitmap(path))
            except Exception as e:
                print e.message
        
            self.inventoryMapListCtrl.SetStringItem(selectedItem,1, str(asset.name))
            self.inventoryMgr.changeItemImage(tag, asset.name)
            
    #Put it to the util       
#    def getArgumentsFromScriptFile(self, script):
#        if(script == "Do Nothing"):
#            return []
#        filename = self.editor.lib.scripts[script].getFullFilename()
#        scriptFile = open(filename.toOsSpecific())
        
        
        
        
    
    
        
    