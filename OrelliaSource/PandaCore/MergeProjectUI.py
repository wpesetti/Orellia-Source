import wx
from wx import xrc
from pandac.PandaModules import Filename
import Util

XRC_FILE = 'XRC/MergeProjectUI.xrc'

class MergeProjectUI(wx.Dialog):
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(XRC_FILE)
        self.res.LoadOnDialog(pre, parent, 'dlgMerge')
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
        
        self.parentToNewNode = False
        
    def OnCreate(self, evt):
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        self.txtPath = xrc.XRCCTRL(self, "txtPath")
        self.txtPath.Enable(False)
        self.btnChooseFile = xrc.XRCCTRL(self, "btnChooseFile")
        self.txtPrefix = xrc.XRCCTRL(self, "txtPrefix")
        self.chkParentToNewNode = xrc.XRCCTRL(self, "chkParentToNewNode")
        self.txtNodeName = xrc.XRCCTRL(self, "txtNodeName")
        self.btnMerge = xrc.XRCCTRL(self, "btnMerge")
    
        self.btnChooseFile.Bind(wx.EVT_BUTTON, self.onChooseFile)
        
        self.txtPrefix.Enable(False)
        
        self.chkParentToNewNode.Enable(False)
        self.chkParentToNewNode.Bind(wx.EVT_CHECKBOX, self.onToggleParent)
        
        self.txtNodeName.Enable(False)
        
        self.btnMerge.Enable(False)
        self.btnMerge.Bind(wx.EVT_BUTTON, self.onMerge)
    
    def ShowModal(self):
        base.le.ui.bindKeyEvents(False)
        wx.Dialog.ShowModal(self)
        base.le.ui.bindKeyEvents(True)
        
    def onChooseFile(self, evt):
        dlg = wx.FileDialog(None, "Choose a project to merge with.", wildcard="*.proj", style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.file = Filename.fromOsSpecific(dlg.GetPath())
            self.txtPrefix.SetValue(self.file.getBasenameWoExtension())
            self.txtPath.SetValue(self.file.toOsSpecific())
            self.txtPrefix.Enable(True)
            self.chkParentToNewNode.Enable(True)
            self.btnMerge.Enable(True)
         
        dlg.Destroy()
        
    def onToggleParent(self, evt):
        self.parentToNewNode = self.chkParentToNewNode.GetValue()
        
        if self.parentToNewNode:
            self.txtNodeName.Enable(True)
            self.txtNodeName.SetValue(self.file.getBasenameWoExtension() + '_root')
        else:
            self.txtNodeName.Enable(False)
            self.txtNodeName.SetValue('')
        
    def onMerge(self, evt):
        prefix = self.txtPrefix.GetValue()
        if Util.toObjectName(prefix) != prefix:
            dlg = wx.MessageDialog(self, "Invalid Prefix Name.", style = wx.OK)
            dlg.ShowModal()
            return
            
        if self.parentToNewNode:
            nodeName = self.txtNodeName.GetValue()
            
            if Util.toObjectName(nodeName) != nodeName or nodeName in base.le.objectMgr.objects:
                dlg = wx.MessageDialog(self, "Invalid Node Name.", style=wx.OK)
                dlg.ShowModal()
                return
          
        else:
            nodeName = ''

        base.le.mergeProject(self.file, prefix, nodeName)
        
        self.Close()
        
        
