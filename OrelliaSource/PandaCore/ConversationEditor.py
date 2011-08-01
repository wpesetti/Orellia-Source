"""
Dialog for making conversation trees
"""

import wx
import os
from wx import xrc

from Conversation import *

# temp?
import xml.dom.minidom
from ConversationConstants import *
from Library import *
from pandac.PandaModules import Filename
from ObjectPropertyUI import *#ScriptPropertyPanel

#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# generated by wxGlade 0.6.3 on Fri Feb 11 14:25:44 2011

#import wx

# begin wxGlade: extracode
# end wxGlade

EDITOR_XRC_FILENAME = 'XRC/ConversationUI.xrc'
SCRIPT_PANEL_XRC_FILENAME = 'XRC/ScriptUI.xrc'
CONDITION_PANEL_XRC_FILENAME = 'XRC/ConversationConditionUI.xrc'
FRAME_TITLE = 'Conversation Editor'

class ConversationEditor(wx.Frame):
    def __init__(self, parent,editor, convo=None, convoName=""):
        base.le.ui.bindKeyEvents(False)
        # TODO: onclose, unbind?
        
        self.parent = parent
        self.editor = editor
        self.convoName = convoName
        #print "Type:::", type(editor)
        # Will determine the UI (colors) and 'speaker' data of lines created
        # True: Makes a conversation between two characters, each alternating.  Two speaker types: 'player' and 'npc'
        self.isCharacterConversation = True
        self.changesSinceLastSave = False
        
        if convo == None:
            self.conversation = Conversation() # make an new, empty conversation to edit
            #firstLine = ConversationLine(1, SpeakerType.NPC)
            #self.conversation.addLine(firstLine)
            #self.convoName = ""
        else:
            self.conversation = convo
            #self.convoName = "existing_conversation"
        self.lastUsedLineID = self.conversation.getRootLine().getID()
        
        self.__setup_frame()
        
    def __setup_frame(self):

        self.res = xrc.XmlResource(EDITOR_XRC_FILENAME)
        self.frame = self.res.LoadFrame(self.parent, 'mainFrame')
        
        #print 'res', self.res
        #print 'frame', self.frame
        
        #self.frame.SetTitle(FRAME_TITLE) # will overwrite title in XRC file
        
        self.frame.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.convoTreeCtrl = xrc.XRCCTRL(self.frame, 'convoTreeCtrl')
        self.addChildBtn = xrc.XRCCTRL(self.frame, 'addChildBtn')
        self.delNodeBtn = xrc.XRCCTRL(self.frame, 'delNodeBtn')
        self.moveUpBtn = xrc.XRCCTRL(self.frame, 'moveUpBtn')
        self.moveDownBtn = xrc.XRCCTRL(self.frame, 'moveDownBtn')
        self.expandAllBtn = xrc.XRCCTRL(self.frame, 'expandAllBtn')
        self.collapseAllBtn = xrc.XRCCTRL(self.frame, 'collapseAllBtn')
        self.infoText = xrc.XRCCTRL(self.frame, 'infoText')
        
        self.lineText = xrc.XRCCTRL(self.frame, 'lineText')
        self.linkChoice = xrc.XRCCTRL(self.frame, 'linkChoice')
        self.lineText_rb = xrc.XRCCTRL(self.frame, 'lineText_rb')
        self.linkChoice_rb = xrc.XRCCTRL(self.frame, 'linkChoice_rb')
        
        self.saveBtn = xrc.XRCCTRL(self.frame, 'saveBtn')
        
        self.convoTreeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectionChange)
        self.addChildBtn.Bind(wx.EVT_BUTTON, self.onAddChild)
        self.delNodeBtn.Bind(wx.EVT_BUTTON, self.onDelNode)
        self.moveUpBtn.Bind(wx.EVT_BUTTON, self.onMoveLineUp)
        self.moveDownBtn.Bind(wx.EVT_BUTTON, self.onMoveLineDown)
        self.expandAllBtn.Bind(wx.EVT_BUTTON, self.onExpandAll)
        self.collapseAllBtn.Bind(wx.EVT_BUTTON, self.onCollapseAll)
        self.saveBtn.Bind(wx.EVT_BUTTON, self.onSave)
        
        self.lineText.Bind(wx.EVT_TEXT, self.onTextChange)
        self.linkChoice.Bind(wx.EVT_CHOICE, self.onChooseLink)
        self.lineText_rb.Bind(wx.EVT_RADIOBUTTON, self.onChooseLineType)
        self.linkChoice_rb.Bind(wx.EVT_RADIOBUTTON, self.onChooseLineType)

        self.lineText_rb.SetValue(True)

        self.processedLineIDs = set()
        self.originalTreeItems = {SpeakerType.PLAYER:[], SpeakerType.NPC:[]} # maps SpeakerType to a list of ConversationLine IDs (as strings) which are active in the conversation
        self.loadConversation()
        # expand the root node to show the first line
        self.convoTreeCtrl.Expand(self.convoTreeCtrl.GetRootItem())
        
        self.notebook = xrc.XRCCTRL(self.frame, 'notebook_1')
        
        self.pageTwo = ConditionPropertyPanel(self.notebook, self.editor, CONDITION_PANEL_XRC_FILENAME)
        self.notebook.AddPage(self.pageTwo, "Conditions")
        
        self.pageThree = ConversationScriptPanel(self.notebook, self.editor, SCRIPT_PANEL_XRC_FILENAME)
        self.notebook.AddPage(self.pageThree, "Scripts")
        
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onNotebookPageChanging)
        

        self.frame.Show()
        self.frame.Layout()
    
    def onExpandAll(self, event=None):
        self.convoTreeCtrl.ExpandAllChildren(self.convoTreeCtrl.GetRootItem())
        
    def onCollapseAll(self, event=None):
        self.convoTreeCtrl.CollapseAllChildren(self.convoTreeCtrl.GetRootItem())
    
    def onMoveLineDown(self, event):
        parentTreeID = self.convoTreeCtrl.GetItemParent(self.selectedTreeItem)
        parentLineID = self.getIDs(parentTreeID)['curID'] # CONSIDER: should this be uniqID?
        parentLine = self.conversation.getLine(parentLineID)
        
        selectedLineID = self.getIDs(self.selectedTreeItem)['curID']
        selectedLine = self.conversation.getLine(selectedLineID)
        
        parentLine.moveSuccessorDown(selectedLineID)
        
        self.refreshTreeUI()
        self.onSelectionChange()
        self.onExpandAll()
        
#        swapTreeID = self.convoTreeCtrl.GetNextSibling(self.selectedTreeItem)
#        swapLineID = self.getIDs(swapTreeID)['curID']
#        swapLine = self.conversation.getLine(swapLineID)
#        
#        if swapTreeID.IsOk():
#            swapTreeID_new = self.convoTreeCtrl.InsertItem(parentTreeID, self.selectedTreeItem, swapLine.getText())
#            swapTreeID_new.
#            self.setIDs(swapTreeID_new, {'uniqID':self.getIDs(swapTreeID)['uniqID'], 'curID':self.getIDs(swapTreeID)['curID']}) # all new lines are original (not links) by default
#            
#        self.convoTreeCtrl.SelectItem(self.selectedTreeItem)
    
    def onMoveLineUp(self, event):
        parentTreeID = self.convoTreeCtrl.GetItemParent(self.selectedTreeItem)
        parentLineID = self.getIDs(parentTreeID)['curID'] # CONSIDER: should this be uniqID?
        parentLine = self.conversation.getLine(parentLineID)
        
        selectedLineID = self.getIDs(self.selectedTreeItem)['curID']
        selectedLine = self.conversation.getLine(selectedLineID)
        
        parentLine.moveSuccessorUp(selectedLineID)
        
        self.refreshTreeUI()
        self.onSelectionChange()
        self.onExpandAll()
    
    def onNotebookPageChanging(self, event):
        if self.linkChoice_rb.GetValue():
            event.Veto()
            dlg = wx.MessageDialog(self.frame, "Cannot edit the conditions or scripts of a linked line.  You can either unlink this line and then edit it, or edit the line it links to.", "Cannot Edit", 
                                   style = wx.OK | wx.ICON_HAND)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.getIDs(self.selectedTreeItem)['curID'] == self.conversation.getRootLine().getID(): 
            event.Veto()
            dlg = wx.MessageDialog(self.frame, "Cannot edit the conditions or scripts of the root line, since it never appears in the game.", "Cannot Edit", 
                                   style = wx.OK | wx.ICON_HAND)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.changesSinceLastSave = True
    
    def onChooseLink(self, event):
        self.changesSinceLastSave = True
        #print 'change made...onChooseLink'
        index = event.GetSelection()
        self.updateLinkChoice(index)
    
    
    def updateLinkChoice(self, selectionIndex):
        if self.linkChoice_rb.GetValue():
            IDs = self.getIDs(self.selectedTreeItem)
            line = self.conversation.getLine(IDs['curID'])
            
            parentTreeID = self.convoTreeCtrl.GetItemParent(self.selectedTreeItem)
            parentLineID = self.getIDs(parentTreeID)['curID'] # CONSIDER: should this be uniqID?
            parentLine = self.conversation.getLine(parentLineID)
            
            linkLineID = int(self.originalTreeItems[line.getSpeaker()][selectionIndex])
            
            # temp
            #print 'choice selection index = %d' %(selectionIndex)
            
            test1 = parentLine.removeSuccessor(IDs['curID'])
            if not test1: # temp
                print 'ERROR: removal of successor from parent failed!'
            test2 = parentLine.addSuccessor(linkLineID)
            if not test2: # temp
                print 'ERROR: adding successor to parent failed!'
            
            # remove the unique ID of this line from the list of original lines in the tree for link selection
            if str(IDs['uniqID']) in self.originalTreeItems[line.getSpeaker()]: 
                self.originalTreeItems[line.getSpeaker()].remove(str(IDs['uniqID']))
                self.originalTreeItems[line.getSpeaker()].sort()
                self.linkChoice.SetItems(self.originalTreeItems[line.getSpeaker()])
            
            # set the curID to match the link's ID
            IDs['curID'] = linkLineID
            self.setIDs(self.selectedTreeItem, IDs)
            
            # update the UI of the tree item
            self.updateTreeItemUI(self.selectedTreeItem)
    
    def onChooseLineType(self, event):
        self.changesSinceLastSave = True
        #print 'change made...onChooseLineType'
        
        IDs = self.getIDs(self.selectedTreeItem)
        line = self.conversation.getLine(IDs['curID'])
        
        parentTreeID = self.convoTreeCtrl.GetItemParent(self.selectedTreeItem)
        parentLineID = self.getIDs(parentTreeID)['curID'] # CONSIDER: should this be uniqID?
        parentLine = self.conversation.getLine(parentLineID)
        
        if self.lineText_rb.GetValue(): # make this line an original line
            if IDs['uniqID'] == LineIDType.UNASSIGNED:
                # is a link, but has no assigned unique ID and so is not in the conversation
                newID = self.generateUnusedLineID()
                IDs['uniqID'] = newID
                newLine = ConversationLine(newID, line.getSpeaker())
                self.conversation.addLine(newLine)
                
            
            # change the successors of the parent
            test1 = parentLine.removeSuccessor(IDs['curID'])
            if not test1: # temp
                print 'ERROR: removal of successor from parent failed!'
            test2 = parentLine.addSuccessor(IDs['uniqID'])
            if not test2: # temp
                print 'ERROR: adding successor to parent failed!'
            
            # set the curID to match the original uniqID
            IDs['curID'] = IDs['uniqID']
            self.setIDs(self.selectedTreeItem, IDs)
            
            # add the unique ID of this line to the list of original lines in the tree for link selection
            if str(IDs['curID']) not in self.originalTreeItems[line.getSpeaker()]:
                self.originalTreeItems[line.getSpeaker()].append(str(IDs['curID']))
                self.originalTreeItems[line.getSpeaker()].sort()
                self.linkChoice.SetItems(self.originalTreeItems[line.getSpeaker()])
            
            # make text reflect the change
            event = wx.CommandEvent(wx.wxEVT_COMMAND_TEXT_UPDATED)
            event.SetEventObject(self.lineText)
            event.SetId(self.lineText.GetId())
            self.onTextChange(event)
        
        elif self.linkChoice_rb.GetValue():
            self.updateLinkChoice(self.linkChoice.GetSelection())
#            # change the successors of the parent
#            linkID = 0
#            if line.getSpeaker() == SpeakerType.NPC:
#                linkID = 1 # temp
#            
#            test1 = parentLine.removeSuccessor(IDs['curID'])
#            if not test1: # temp
#                print 'ERROR: removal of successor from parent failed!'
#            test2 = parentLine.addSuccessor(linkID)
#            if not test2: # temp
#                print 'ERROR: adding successor to parent failed!'
#            
#            # remove the unique ID of this line from the list of original lines in the tree for link selection
#            self.originalTreeItems[line.getSpeaker()].remove(str(IDs['curID']))
#            self.linkChoice.SetItems(self.originalTreeItems[line.getSpeaker()])
#            
#            # set the curID to match the link's ID
#            IDs['curID'] = linkID
#            self.setIDs(self.selectedTreeItem, IDs)


#            event = wx.CommandEvent(wx.wxEVT_COMMAND_CHOICE_SELECTED)
#            event.SetEventObject(self.linkChoice)
#            event.SetId(self.linkChoice.GetId())
#            self.onChooseLink(event)
            
        
        # update the UI of the tree item
        self.updateTreeItemUI(self.selectedTreeItem)

    def updateTreeItemUI(self, treeID):
        lineID = self.getIDs(treeID)['curID']
        line = self.conversation.getLine(lineID)
        self.convoTreeCtrl.SetItemTextColour(treeID, SpeakerType.typeAsColor(line.getSpeaker()))
        if self.isOriginalLine(treeID):
            self.convoTreeCtrl.SetItemBold(treeID, bold=False)
            self.convoTreeCtrl.SetItemText(treeID, self.generateTreeText(line))
            self.infoText.SetLabel('Line ID: %d, Speaker: %s' %(lineID, line.getSpeaker()))
        else:
            self.convoTreeCtrl.SetItemBold(treeID, bold=True)
            self.convoTreeCtrl.SetItemText(treeID, ' <<LINK>> ' + self.generateTreeText(line))
            self.infoText.SetLabel('LINK TO: %d, Speaker: %s' %(lineID, line.getSpeaker()))

    def onAddChild(self, event):
        self.changesSinceLastSave = True
        #print 'change made...onAddChild'
        
        selectedLineID = self.getIDs(self.selectedTreeItem)['curID'] # CONSIDER: should this be uniqID?
        selectedLine = self.conversation.getLine(selectedLineID)
        childSpeaker = SpeakerType.PLAYER
        if self.isCharacterConversation and (selectedLine.getSpeaker() == SpeakerType.PLAYER):
            childSpeaker = SpeakerType.NPC
    
        # Make a new ConversationLine with an unused ID and the correct speaker type
        childLineID = self.generateUnusedLineID()
        childLine = ConversationLine(childLineID, childSpeaker, '')
        
        # Add the line to the Conversation object
        self.conversation.addLine(childLine)
        
        # Add the line to the Tree
        treeID = self.convoTreeCtrl.AppendItem(self.selectedTreeItem, self.generateTreeText(childLine))
        self.setIDs(treeID, {'uniqID':childLineID, 'curID':childLineID}) # all new lines are original (not links) by default
        self.updateTreeItemUI(treeID)
        
        # Add the line to the list of possible links
        self.originalTreeItems[childSpeaker].append(str(childLineID))
        self.linkChoice.SetItems(self.originalTreeItems[childSpeaker])
        
        # Add the line to the successors of its parent (currently selected)
        self.conversation.getLine(selectedLineID).addSuccessor(childLineID)
        
        # Select the new line
        self.convoTreeCtrl.SelectItem(treeID) # CONSIDER: alternatively, expand the parent and don't select the new line
        
        # TODO: after adding a new line, but having it link to an old line after clicking button,
        # MAKE SURE that the new line does not overwrite the old line with the same ID...
    
    def onDelNode(self, event):
        self.changesSinceLastSave = True
        #print 'change made...onDelNode'
        
        parentTreeID = self.convoTreeCtrl.GetItemParent(self.selectedTreeItem)
        parentLineID = self.getIDs(parentTreeID)['curID'] # CONSIDER: should this be uniqID?
        selectedLineID = self.getIDs(self.selectedTreeItem)['curID']
        selectedLine = self.conversation.getLine(selectedLineID)
        
        # Remove the unique ID from the list of possible links, if it is there
        uniqIDString = str(self.getIDs(self.selectedTreeItem)['uniqID'])
        if uniqIDString in self.originalTreeItems[selectedLine.getSpeaker()]:
            #print 'removing uniqID %s from list of possible links (curID = %s)' %(str(self.getIDs(self.selectedTreeItem)['uniqID']), str(self.getIDs(self.selectedTreeItem)['curID']))
            self.originalTreeItems[selectedLine.getSpeaker()].remove(uniqIDString)
            self.linkChoice.SetItems(self.originalTreeItems[selectedLine.getSpeaker()])
        
        # Remove the line from the successors of its parent
        self.conversation.getLine(parentLineID).removeSuccessor(selectedLineID)
        
        # TODO: if it was the last instance of that line in the conversation, delete it from the Conversation self.lines dict
        
        # After done using the ConversationLine data of the line to be removed, remove the line and its children from the Tree
        self.convoTreeCtrl.DeleteChildren(self.selectedTreeItem)
        self.convoTreeCtrl.Delete(self.selectedTreeItem) # will this mess up keeping track of selectedTreeItem, or does it generate an sel changed event?

    def onSelectionChange(self, event=None):
        if event != None:
            self.selectedTreeItem = event.GetItem()
        
        selLineID = self.getIDs(self.selectedTreeItem)['curID']
        selLine = self.conversation.getLine(selLineID)
        #self.infoText.SetLabel('Line ID: %d, Speaker: %s' %(selLineID, selLine.getSpeaker()))
        
        if self.isOriginalLine(self.selectedTreeItem):
            self.lineText_rb.SetValue(True)
        else:
            self.linkChoice_rb.SetValue(True)
        
        self.updateTreeItemUI(self.selectedTreeItem)
        self.lineText.ChangeValue(self.conversation.getLine(selLineID).getText()) # does not send a EVT_TEXT
        self.linkChoice.SetItems(self.originalTreeItems[selLine.getSpeaker()])
        if str(selLineID) in self.originalTreeItems[selLine.getSpeaker()]:
            self.linkChoice.SetSelection(self.originalTreeItems[selLine.getSpeaker()].index(str(selLineID)))
        else:
            pass
        self.pageTwo.updateProps(selLine)
        self.pageTwo.update()
        self.pageThree.updateProps(selLine)
        self.pageThree.update()
        
        if selLineID == self.conversation.getRootLine().getID():
            self.delNodeBtn.Disable()
            self.lineText.Disable()
            self.linkChoice.Disable()
            self.lineText_rb.Disable()
            self.linkChoice_rb.Disable()
            self.moveUpBtn.Disable()
            self.moveDownBtn.Disable()
            self.notebook.ChangeSelection(0)
        else:
            self.delNodeBtn.Enable()
            self.lineText.Enable()
            self.linkChoice.Enable()
            self.lineText_rb.Enable()
            self.linkChoice_rb.Enable()
            self.moveUpBtn.Enable()
            self.moveDownBtn.Enable()

    def onTextChange(self, event):
        self.changesSinceLastSave = True
        #print 'change made...onTextChange'
        
        # CONSIDER: remove for efficiency, only overwrite on selection changes and user save
        if self.isOriginalLine(self.selectedTreeItem):
            changedText = event.GetString()
            
            # Change the text of the ConversationLine data
            selLineID = self.getIDs(self.selectedTreeItem)['curID']
            selLine = self.conversation.getLine(selLineID)
            selLine.setText(changedText)
            
            # Change the text in the TreeCtrl with the updated ConversationLine
            self.convoTreeCtrl.SetItemText(self.selectedTreeItem, self.generateTreeText(selLine))

    def generateTreeText(self, convoLine):
        return '(%d | %s) ' %(convoLine.getID(), convoLine.getSpeaker()) + convoLine.getText()

    def generateUnusedLineID(self):
        while self.conversation.hasLine(self.lastUsedLineID):
            self.lastUsedLineID += 1
        return self.lastUsedLineID

    def getIDs(self, treeID):
        # TODO: do not allow if it is the root; it has no data...
        try:
            dataDict = self.convoTreeCtrl.GetItemData(treeID).GetData()
            return dataDict
        except:
            print 'Undefined error: This tree item has no data associated with it'
    
    def setIDs(self, treeID, dict):
        d = wx.TreeItemData()
        d.SetData(dict)
        self.convoTreeCtrl.SetItemData(treeID, d)

    def isOriginalLine(self, treeID):
        dataDict = self.convoTreeCtrl.GetItemData(treeID).GetData()
        uniqID = dataDict['uniqID']
        curID = dataDict['curID']
        return (uniqID == curID)

    def onSave(self, event=None):
#        dlg = wx.FileDialog(self.frame, "Choose a location to save the source file", \
#        defaultDir= base.le.currentProj.dir.toOsSpecific(),\
#        defaultFile = 'conversation' + '.xml', wildcard="*.xml", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        dlg = wx.TextEntryDialog(self.frame, "Choose a name for this conversation", defaultValue=self.convoName)    
        
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            if name in base.le.lib.conversations:
                messageDlg = wx.MessageDialog(self.frame, "\"%s\" already exists, do you want to overwrite?" %(name))
                if messageDlg.ShowModal() == wx.ID_OK:
                    #print 'overwrite it'
                    base.le.lib.removeConversation(name)
                else:
                    #print 'do not overwrite it'
                    messageDlg.Destroy()
                    return
            else:
                self.convoName = name
                
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            
            #== Create temporary XML file for the asset
            doc = xml.dom.minidom.Document()
            root = doc.createElement("the_root")
            doc.appendChild(root)
            root.appendChild(self.conversation.encode(doc))
            
            tempFilePath = base.le.lib.projDir.toOsSpecific() + '/' + name + '.xml'
            assetFilename = Filename(tempFilePath)
            #print 'temporary file path for asset: ' + assetFilename.toOsSpecific()
    
            f = open(assetFilename.toOsSpecific(), 'w')
            f.write(doc.toxml())
            f.close()
            
            #== Make an Asset based on the temporary source file and add it to the library
            asset = ConversationAsset(name, assetFilename)
            base.le.lib.addConversation(asset, True)
            base.le.ui.storyObjUI.update()
            
            #== Remove the temporary source file
            tempFilename = Filename(tempFilePath)
            #print 'temporary file path to now delete: ' + tempFilename.toOsSpecific()
            os.remove(tempFilename.toOsSpecific())
            
            self.changesSinceLastSave = False
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW)) 
            
            #print 'added to library...'
    
    def onClose(self, event):
        if self.changesSinceLastSave:
            messageDlg = wx.MessageDialog(self.frame, "Save this conversation before closing?", style=wx.YES_NO)
            if messageDlg.ShowModal() == wx.ID_YES:
                #print 'save on exit? : yes'
                self.onSave()
            else:
                #print 'save on exit? : no'
                messageDlg.Destroy()
        #self.frame.Destroy()
        event.Skip() # finish the rest of the closing process

    def refreshTreeUI(self):
        self.convoTreeCtrl.DeleteAllItems()
        self.loadConversation()

    def loadConversation(self):
        self.processedLineIDs.clear()
        self.originalTreeItems.clear()
        self.originalTreeItems = {SpeakerType.PLAYER:[], SpeakerType.NPC:[]} # maps SpeakerType to a list of ConversationLine IDs (as strings) which are active in the conversation
        
        rootLine = self.conversation.getRootLine()
        rootLineID = rootLine.getID()
        self.lastUsedLineID = rootLineID
        rootTreeID = self.convoTreeCtrl.AddRoot(self.generateTreeText(rootLine))
        self.setIDs(rootTreeID, {'uniqID':rootLineID, 'curID':rootLineID})
        
        self.updateTreeItemUI(rootTreeID) # the root is always a player node
        
        self.selectedTreeItem = rootTreeID # CAUTION
        self.processedLineIDs.add(rootLineID)
        for succID in rootLine.getSuccessors():
            self.rec_loadConvoTree(rootTreeID, succID)

    def rec_loadConvoTree(self, parentTreeID, lineID):
        line = self.conversation.getLine(lineID)
        #print 'id %d, %s' %(lineID, line.getSpeaker())
        treeID = self.convoTreeCtrl.AppendItem(parentTreeID, self.generateTreeText(line))
        
        if not lineID in self.processedLineIDs:
            self.processedLineIDs.add(lineID)
            self.originalTreeItems[line.getSpeaker()].append(str(lineID))
            self.setIDs(treeID, {'uniqID':lineID, 'curID':lineID})
            for succID in line.getSuccessors():
                self.rec_loadConvoTree(treeID, succID)
        else:
            self.setIDs(treeID, {'uniqID':LineIDType.UNASSIGNED, 'curID':lineID})
        
        self.updateTreeItemUI(treeID)



#=====

CONDITION_EVENT = 'LE-convoLineCondition'

class ConditionPropertyPanel(wx.Panel):
    def __init__(self, parent, editor, file=CONDITION_PANEL_XRC_FILENAME):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(file)
        self.res.LoadOnPanel(pre, parent, 'conditionPanel')
        self.PostCreate(pre)
        self.editor = editor
        
        self.startIcon = None 
        self.filename = ''
        self.name = ''
        self.parametersUI = []
        
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
        self.eventChoice.Hide()
#        self.Bind(wx.EVT_CHOICE, self.onSwitchEvent, self.eventChoice)
        self.scriptChoice = xrc.XRCCTRL(self.editPanel, "scriptChoice")
        self.Bind(wx.EVT_CHOICE, self.onSwitchScript, self.scriptChoice)
        
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
        #self.eventListCtrl.InsertColumn(0, "event")
        self.eventListCtrl.InsertColumn(0, "Condition")
        self.eventListCtrl.InsertColumn(1, "Parameters")
        
    def setupParameters(self):
        for i in range(1,5):
            #print i
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
        #print len(self.parametersUI)
        
    def loadScriptChoices(self):
        self.scriptChoice.Clear()
        self.scriptChoice.Append(DEFAULT_SCRIPT)
        for s in sorted(self.editor.lib.conditionScripts):
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
#        eventID = self.eventChoice.FindString(event)
#        self.eventChoice.SetSelection(eventID)
        #print "Script: ", script
        choiceID = self.scriptChoice.FindString(script)
        self.scriptChoice.SetSelection(choiceID)
        
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #print "Event: ",event
        scripts = obj.getScriptsAndArguments(event)
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
        
        #print '=debug condition panel= selectedItem : ', self.selectedItem
        
        #event = self.eventListCtrl.GetItemText(self.selectedItem)#GetItem(id, 0).GetText()
        event = CONDITION_EVENT
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
            #print "Counter:",counter
            #print len(self.parametersUI)
            label, text = self.parametersUI[counter]
            label.SetLabel(argument)
            text.Enable()
            #text.SetEditable(True)
            #text.SetBackgroundColour(wx.Colour(255,255,255))
            counter += 1
    #def fillParameterVaues(self, values):
    #    pass
    
    def onTextFocus(self,event):
        self.editor.objectMgr.onEnterObjectPropUI(True)
        pass
    
    def onTextChange(self, event):
        self.writeFromUIToData()
    
    def writeFromUIToData(self):
        event, script, id = self.getCurrentEventScriptID()
        values = []
        for label, text in self.parametersUI:
            if(text.IsEnabled()==False):
                continue
            value = text.GetValue()
            #maybe check
            values.append(value)
            
        #print "==== Writing parameter values to data : ", values
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        obj.setScriptArguments(event,id, values)
        self.eventListCtrl.SetStringItem(self.selectedItem, 1, "("+",".join(values)+")")
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
            #print strippedLine
            #pos = strippedLine.find("def main")
            #if(pos != -1):
            #    mainLine = line
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
        obj.setScript(event, id,  chosenScript)
        self.eventListCtrl.SetStringItem(self.selectedItem, 0, chosenScript)
        self.eventListCtrl.SetStringItem(self.selectedItem, 1, "()")
        
        arguments = self.getArgumentsFromScriptFile(chosenScript)    
        #print "Arguments in ScriptUI: ",arguments
        
        
        self.enableParameters(arguments)
    
    def onGenerateParameters(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #print self.getCurrentEventScriptID()
        
        #print obj.scripts
        return
        
#        chosenEvent = self.eventChoice.GetStringSelection()
        chosenEvent = CONDITION_EVENT
        chosenScript = self.scriptChoice.GetStringSelection()
        selectedID = self.eventListCtrl.GetItemData(self.selectedItem)
        
        if(chosenEvent == self.selectedEvent):
            obj.setScript(self.selectedEvent, selectedID, chosenScript)#later on add arguments
            self.eventListCtrl.SetStringItem(self.selectedItem, 0, chosenScript)
        else:
            #print "different event:", chosenEvent," ", self.selectedEvent
            success = obj.removeScript(self.selectedEvent, selectedID)
            if(success == False):
                return
            id = obj.addScript(chosenEvent, chosenScript)
            #self.eventListCtrl.SetStringItem(self.selectedItem, 0, chosenEvent)
            self.eventListCtrl.SetStringItem(self.selectedItem, 0, chosenScript)
            #self.eventListCtrl.SetStringItem(self.selectedItem, 1, str(id))
            self.eventListCtrl.SetStringItem(self.selectedItem, 1, "("+",".join(arguments))
            self.eventListCtrl.SetItemData(self.selectedItem, id)
        
        #self.onListSelection(None)
        pass
    
    def onAddEvent(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        id = obj.addScript(CONDITION_EVENT, DEFAULT_SCRIPT)

        pos = self.eventListCtrl.InsertStringItem(self.eventListCtrl.GetItemCount(),DEFAULT_SCRIPT)
        #self.eventListCtrl.SetStringItem(pos, 1, str(id))
        self.eventListCtrl.SetStringItem(pos, 1, "()")
        self.eventListCtrl.SetItemData(pos, id)

        self.eventListCtrl.Select(pos, True)
        self.eventListCtrl.EnsureVisible(pos)
        self.removeEventButton.Enable(True)
        self.scriptChoice.Enable(True)
    
    def onRemoveEvent(self, event):
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        event, script, id = self.getCurrentEventScriptID()
        #id = self.eventListCtrl.GetItemData(self.selectedItem)
        obj.removeScript(event, int(id))
        self.eventListCtrl.DeleteItem(self.selectedItem)
        
        if self.eventListCtrl.GetItemCount() == 0:
            self.removeEventButton.Enable(False)
            self.scriptChoice.Enable(False)
            self.resetParameters()
        else:
            self.removeEventButton.Enable(True)
            self.eventListCtrl.Select(0)
        
    
    def buildView(self):
        self.eventListCtrl.DeleteAllItems()
        obj = self.currentObj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        
        if obj == None:
            return
        
        #print 'scripts for this line : ', obj.scripts
        if CONDITION_EVENT in obj.scripts:
            for scriptID in sorted(obj.scripts[CONDITION_EVENT]):
                scriptName, parameters = obj.scripts[CONDITION_EVENT][scriptID]
                pos = self.eventListCtrl.InsertStringItem(self.eventListCtrl.GetItemCount(), scriptName)
                #self.eventListCtrl.SetStringItem(pos, 1, str(scriptID))
                self.eventListCtrl.SetStringItem(pos, 1,"("+",".join(parameters)+")")
                self.eventListCtrl.SetItemData(pos, scriptID)
                
        if self.eventListCtrl.GetItemCount() == 0:
            self.removeEventButton.Enable(False)
            self.scriptChoice.Enable(False)
            self.resetParameters()
        else:
            self.scriptChoice.Enable(True)
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
        #print "Here"
                
    def updateProps(self, obj, override=False):
        self.currentObj = obj#self.editor.objectMgr.findObjectByNodePath(base.direct.selected.last)
        #self.buildView()
        #self.loadScriptChoices()
        pass
    
class ConversationScriptPanel(ScriptPropertyPanel):
    def __init__(self,parent, editor, file):
        ScriptPropertyPanel.__init__(self, parent, editor, file)
        
    
    def setupView(self):
        self.eventListCtrl.InsertColumn(0, "Conditions")
        self.eventListCtrl.SetColumnWidth(0, 0)
        self.eventListCtrl.InsertColumn(1, "Scripts")
        self.eventListCtrl.InsertColumn(2,"Values")