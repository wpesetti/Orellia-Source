import wx
import os
import Library
import Util
from wx import xrc

class PrefsDialog(wx.Dialog):
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource('XRC/dlgPreferences.xrc')
        self.res.LoadOnDialog(pre, parent, 'dlgPreferences')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
    
    def OnCreate(self, evt=None):
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        self.btnApply = xrc.XRCCTRL(self, "btnApply")
        self.btnCancel = xrc.XRCCTRL(self, "btnCancel")
        
        
        self.txtColorR = xrc.XRCCTRL(self, "txtColorR")
        self.txtColorG = xrc.XRCCTRL(self, "txtColorG")
        self.txtColorB = xrc.XRCCTRL(self, "txtColorB")
        
        self.txtPerspFar = xrc.XRCCTRL(self, "txtPerspFar")
        self.txtPerspNear = xrc.XRCCTRL(self, "txtPerspNear")
        
        self.txtOrthoNear = xrc.XRCCTRL(self, "txtOrthoNear")
        self.txtOrthoFar = xrc.XRCCTRL(self, "txtOrthoFar")

        self.txtBoxes = [self.txtColorB, self.txtColorG, self.txtColorR]
        
        self.btnApply.Bind(wx.EVT_BUTTON, self.onApply)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        
        self.txtPerspNear.SetValue(str(base.le.ui.perspView.camLens.getNear()))
        self.txtPerspFar.SetValue(str(base.le.ui.perspView.camLens.getFar()))
        
        #just use Top view for now as the orthographic value
        self.txtOrthoNear.SetValue(str(base.le.ui.topView.camLens.getNear()))
        self.txtOrthoFar.SetValue(str(base.le.ui.topView.camLens.getFar()))
            
        self.bgColor = base.getBackgroundColor()
        
        self.txtColorR.SetValue(str(self.bgColor[0] * 255.0))
        self.txtColorG.SetValue(str(self.bgColor[1] * 255.0))
        self.txtColorB.SetValue(str(self.bgColor[2] * 255.0))
        
        base.le.ui.bindKeyEvents(False)
        
    def onApply(self, evt):
        try:
            perspNear = float(self.txtPerspNear.GetValue())
            perspFar = float(self.txtPerspFar.GetValue())
            orthoNear = float(self.txtOrthoNear.GetValue())
            orthoFar = float(self.txtOrthoFar.GetValue())
            
            r = float(self.txtColorR.GetValue()) / 255
            g = float(self.txtColorG.GetValue()) / 255
            b = float(self.txtColorB.GetValue()) / 255
        except ValueError as e:
            dlg = wx.MessageDialog(self, e.message, "Invalid Value", style = wx.OK|wx.ICON_HAND)
            dlg.ShowModal()
            return
    
        base.le.ui.perspView.camLens.setNear(perspNear)
        base.le.ui.perspView.camLens.setFar(perspFar)
        
        for view in (base.le.ui.topView, base.le.ui.frontView, base.le.ui.leftView):
            view.camLens.setNear(orthoNear)
            view.camLens.setFar(orthoFar)

            base.setBackgroundColor(r, g, b, win=view.win)
        
        base.setBackgroundColor(r, g, b)
        
        
        base.le.ui.bindKeyEvents(True)
        self.Destroy()
    
    def onCancel(self, evt):
        base.le.ui.bindKeyEvents(True)
        self.Destroy()
        
    def Close(self, evt = None):
        base.le.ui.bindKeyEvents(True)
