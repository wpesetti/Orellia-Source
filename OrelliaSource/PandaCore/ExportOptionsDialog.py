import wx
import os
from wx import xrc
from LoadAssetDialog import *
from Objects import *
#Class to handle export options dialog

class ExportOptionsDialog(wx.Dialog):
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource('/XRC/dlgExportOptions.xrc')
        self.res.LoadOnDialog(pre, parent, 'dlgExportOptions')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
    
    def OnCreate(self, evt=None):
        self.Unbind(wx.EVT_INIT_DIALOG)
        self.Ok = False
        
        self.options = {'defaultSound':'','loadScreen':'', 'path':'','useSceneBG':False,'cam':'' , 'camSpeed':1.0,'camHeight':0.0,'camPusher':False}
        
        self.chkEnableSound = xrc.XRCCTRL(self, "chkEnableSound")
        self.lblCurrentSound = xrc.XRCCTRL(self, "lblCurrentSound")
        self.btnLoadSound = xrc.XRCCTRL(self, "btnLoadSound")
        self.chkCamPusher = xrc.XRCCTRL(self, "chkCamPusher")
        self.choiceCam = xrc.XRCCTRL(self, "choiceCam")
        self.txtCamSpeed = xrc.XRCCTRL(self, "txtCamSpeed")
        self.txtCamHeight = xrc.XRCCTRL(self, "txtCamHeight")
        self.chkUseSceneBG = xrc.XRCCTRL(self, "chkUseSceneBG")
        self.chkUseTex = xrc.XRCCTRL(self, "chkUseTex")
        self.lblLoadScreenName = xrc.XRCCTRL(self, "lblLoadScreenName")
        self.btnLoadTexture = xrc.XRCCTRL(self, "btnLoadTexture")
        self.txtPath = xrc.XRCCTRL(self, "txtPath")
        self.btnExport = xrc.XRCCTRL(self, "btnExport")
        self.btnCancel = xrc.XRCCTRL(self, "btnCancel")
        self.btnChoosePath = xrc.XRCCTRL(self, "btnChooseLocation")
        self.btnExport.Bind(wx.EVT_BUTTON, self.onExport)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        
        self.chkCamPusher.Bind(wx.EVT_CHECKBOX, self.onUsePusher)
        self.chkEnableSound.Bind(wx.EVT_CHECKBOX, self.onSoundEnable)
        self.btnLoadSound.Bind(wx.EVT_BUTTON, self.onLoadSound)
        self.chkUseSceneBG.Bind(wx.EVT_CHECKBOX, self.onUseSceneBG)
        self.chkUseTex.Bind(wx.EVT_CHECKBOX, self.onUseTex)
        self.btnLoadTexture.Bind(wx.EVT_BUTTON, self.onLoadTexture)
        self.btnChoosePath.Bind(wx.EVT_BUTTON, self.onChoosePath)
        self.choiceCam.Bind(wx.EVT_CHOICE, self.onChooseCam)
        
        self.txtCamHeight.SetValue(str(self.options['camHeight']))
        self.txtCamSpeed.SetValue(str(self.options['camSpeed']))
        self.choiceCam.SetSelection(0) ##Default cam
        
        ##find all the cameras in the scene for export
        for obj in base.le.objectMgr.objects.values():
            if isinstance(obj, Cam):
                self.choiceCam.Append(obj.name)
        
        base.le.ui.bindKeyEvents(False) 
                      
    def onChooseCam(self, evt):
        if self.choiceCam.GetSelection() != 0:
            self.options['cam'] = self.choiceCam.GetStringSelection()
        else:
            self.options['cam'] = ''

    def onUseSceneBG(self, evt):
        self.options['useSceneBG'] = self.chkUseSceneBG.GetValue()
    
    def onUsePusher(self, evt):
        self.options['camPusher'] = self.chkCamPusher.GetValue()
    
    def onSoundEnable(self, evt):
        if self.chkEnableSound.GetValue() == True:
            self.lblCurrentSound.Enable(True)
            self.btnLoadSound.Enable(True)
        else:
            self.lblCurrentSound.Enable(False)
            self.btnLoadSound.Enable(False)
            self.lblCurrentSound.SetLabel("No Sound Loaded")
            self.options['defaultSound'] = ''
    
    def onUseTex(self, evt):
        if self.chkUseTex.GetValue() == True:
            self.lblLoadScreenName.Enable()
            self.btnLoadTexture.Enable()
        else:
            self.lblLoadScreenName.Disable()
            self.btnLoadTexture.Disable()
            self.lblLoadScreenName.SetLabel("No Texture Loaded")
            self.options['loadScreen'] = ''
            
    def onChoosePath(self, evt):
        dlg = wx.FileDialog(self, "Choose a python file to export to.", \
        defaultDir= base.le.currentProj.dir.toOsSpecific(),\
        defaultFile = base.le.currentProj.name + '.py', wildcard="*.py", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            
        if dlg.ShowModal() == wx.ID_OK:
            self.options['path'] = dlg.GetPath()
            self.txtPath.SetValue(self.options['path'])
            
    def onLoadSound(self, evt):
        dlg = LoadAssetDialog(self, filter = "Sounds")
        asset = dlg.ShowModal()
        if (asset != None):
            self.lblCurrentSound.SetLabel(asset.name)
            self.options['defaultSound'] = asset.name
            
    def onLoadTexture(self, evt):
        dlg = LoadAssetDialog(self, filter = "Textures")
        asset = dlg.ShowModal()
        if (asset != None):
            self.lblLoadScreenName.SetLabel(asset.name)
            self.options['loadScreen'] = asset.name
            
    def onCancel(self, evt = None):
        base.le.ui.bindKeyEvents(True)
        self.Close()
    
    def checkTextBoxes(self):
        try:
            height = float(self.txtCamHeight.GetValue())
            speed = float(self.txtCamSpeed.GetValue())
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            return False
        else:
            self.options['camHeight'] = height
            self.options['camSpeed'] = speed
            return True
            
                
    def onExport(self, evt = None):
        if self.options['path'] == '':
            msg = wx.MessageDialog(self, "Please Enter An Export Location", "Invalid Location",  wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
        elif not self.checkTextBoxes():
            return
        else:
            self.Ok = True
            base.le.ui.bindKeyEvents(True)
            self.Close()
            
        
    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        return self.options

        