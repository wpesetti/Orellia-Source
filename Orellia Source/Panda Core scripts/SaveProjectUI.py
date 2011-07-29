import wx
import os
from pandac.PandaModules import Filename
import Util

class SaveProjectUI(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(300,150))
        
        self.dir = None
        
        self.parent = parent
        
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        message = wx.StaticText(self,-1,"Select a Directory for the Project.")
        button = wx.Button(self, -1, 'Select')
        button.Bind(wx.EVT_BUTTON, self.onChooseFolder)
        
        self.dirText = wx.StaticText(self, -1, "")
        self.okButton = wx.Button(self, wx.ID_OK)
        #self.okButton.Enable(False)
        
        hSizer.Add(button)
        hSizer.Add(self.dirText)
        
        message2 = wx.StaticText(self, -1, "Choose a name for the project.")
        self.nameInput = wx.TextCtrl(self, -1, "")
        #self.nameInput.Bind(wx.EVT_TEXT, self.onNameInput)
        
        vSizer.Add(message)
        vSizer.Add(button)
        vSizer.Add(hSizer)
        vSizer.Add(message2)
        vSizer.Add(self.nameInput)
        vSizer.Add(self.okButton)
        
        self.SetSizer(vSizer)
        self.Layout()
        
        self.projName = ""
    
#    def onNameInput(self, evt):
#        self.nameInput.SetValue(Util.toFilename(self.nameInput.GetValue(), stripEnd=False))
#        self.projName = self.nameInput.GetValue()
#        if self.dir and self.projName:
#            self.okButton.Enable(True)
#        else:
#            self.okButton.Enable(False)
        
    def onChooseFolder(self, evt):
        dialog = wx.DirDialog(None, "Choose a project directory", os.getcwd())
        if dialog.ShowModal() == wx.ID_OK:
            self.dir = Filename.fromOsSpecific(dialog.GetPath())
            self.dirText.SetLabel(self.dir.toOsSpecific())
            if self.dir and self.projName:
                self.okButton.Enable(True)
    
    def ShowModal(self):
        base.le.ui.bindKeyEvents(False)
        result = wx.Dialog.ShowModal(self)
        self.projName = self.nameInput.GetValue()
        base.le.ui.bindKeyEvents(True)
        return result