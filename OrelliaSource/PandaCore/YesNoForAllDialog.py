import wx
from wx import xrc

XRC_FILE = 'XRC/dlgYesNoForAll.xrc'

class YesNoForAllDialog(wx.Dialog):
    def __init__(self, parent, message, checkBoxMessage="Do this for all", caption=""):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(XRC_FILE)
        self.res.LoadOnDialog(pre, parent,'dlgYesNoForAll')
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
        self.message = message
        self.checkBoxMessage = checkBoxMessage
        self.caption = caption
        
    def OnCreate(self, evt):
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        self.lblMessage = xrc.XRCCTRL(self, "lblMessage")
        self.lblMessage.SetLabel(self.message)
        
        self.btnYes = xrc.XRCCTRL(self, "btnYes")
        self.btnYes.Bind(wx.EVT_BUTTON, self.onYes)
        
        self.btnNo = xrc.XRCCTRL(self, "btnNo")
        self.btnNo.Bind(wx.EVT_BUTTON, self.onNo)
        
        self.chkDoForAll = xrc.XRCCTRL(self, "chkDoForAll")
        self.chkDoForAll.SetLabel(self.checkBoxMessage)
        
        self.SetTitle(self.caption)
        
        self.Fit()
        self.Layout()
        
    def onYes(self, evt):
        self.result = (True, self.chkDoForAll.GetValue())
        self.Close()
        
    def onNo(self, evt):
        self.result = (False, self.chkDoForAll.GetValue())
        self.Close()
        
    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        return self.result[0], self.result[1]
