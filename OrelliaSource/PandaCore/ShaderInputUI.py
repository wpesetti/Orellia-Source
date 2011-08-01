import wx
import os
from wx import xrc
from ObjectInputDialog import *
from pandac.PandaModules import Vec3, VBase4, Mat4

from ActionMgr import *

DLG_FILENAME = 'XRC/ObjectUI/ShaderInputs/dlgInputType.xrc'

XRC_PANELS = {'float':'XRC/ObjectUI/ShaderInputs/panelFloat.xrc',
                'float3':'XRC/ObjectUI/ShaderInputs/panelFloat.xrc',
                'float4':'XRC/ObjectUI/ShaderInputs/panelFloat4.xrc',
                'float4x4':'XRC/ObjectUI/ShaderInputs/panelFloat4x4.xrc'}



class ShaderInputDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        #Pre creation routine to allow wx to do layout from XRC
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(DLG_FILENAME)
        self.res.LoadOnDialog(pre, parent, 'dlgShaderInputType')
        self.PostCreate(pre)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
    
    def OnCreate(self, e): 
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        self.Ok = False
        self.inputType = ''
        self.name = ''
        
        self.btnOK = xrc.XRCCTRL(self,'btnOK')
        self.choiceInputType = xrc.XRCCTRL(self, 'choiceType')
        self.txtName = xrc.XRCCTRL(self, 'txtName')
        self.txtName.Bind(wx.EVT_TEXT, self.onNameInput)
        
        self.btnOK.Enable(False)
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnOk)
        
        self.btnCancel = xrc.XRCCTRL(self, 'btnCancel')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        
        base.le.ui.bindKeyEvents(False)
    def onNameInput(self, e):
        self.btnOK.Enable(self.txtName.GetValue()!='')
    
    def OnOk(self, e):
        self.inputType = self.choiceInputType.GetStringSelection()
        self.name = self.txtName.GetValue()
        
        if self.name in self.parent.shader.inputs:
            msg = "Name '" + self.name + "' already in use."
            dlg = wx.MessageDialog(self, msg, caption="Duplicate Input Name", style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        self.Ok = True
        self.Close()
    
    def onCancel(self, e):
        self.Close()
        self.name = ''
        self.inputType = ''
    
    def ShowModal(self):
        base.le.ui.bindKeyEvents(False)
        wx.Dialog.ShowModal(self)
        base.le.ui.bindKeyEvents(True)
        return self.name, self.inputType


    
        
class FloatInputPanel:
    def __init__(self, panel):
        self.panel = panel
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        
        self.txtValue = xrc.XRCCTRL(self.panel, "txtValue")
  
    def setFromInput(self, input):
        self.txtValue.SetValue(str(input.getValue()))
        
    def setOnInput(self, input):
        value = float(self.txtValue.GetValue())
        action = ActionSetProperty(base.le, input.setValue, input.getValue, value)
        base.le.actionMgr.push(action)
        action()
    
    def setName(self, name):
        self.txtInputName.SetValue(name)
        
    def getName(self):
        return self.txtInputName.GetValue()
    
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()
class Float3InputPanel:
    def __init__(self, panel):
        self.panel = panel
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        
        self.txtF1 = xrc.XRCCTRL(self.panel, "txtF1")
        self.txtF2 = xrc.XRCCTRL(self.panel, "txtF2")
        self.txtF3 = xrc.XRCCTRL(self.panel, "txtF3")

    def getName(self):
        return self.txtInputName.GetValue()
        
    def setName(self, name):
        self.txtInputName.SetValue(name)
    
    def setFromInput(self, input):
        value = input.getValue()
        self.txtF1.SetValue(str(value[0]))
        self.txtF2.SetValue(str(value[1]))
        self.txtF3.SetValue(str(value[2]))
        
    def setOnInput(self, input):
        value = Vec3(float(self.txtF1.GetValue()),
                    float(self.txtF2.GetValue()),
                    float(self.txtF3.GetValue()))
        
        action = ActionSetProperty(base.le, input.setValue, input.getValue, value)
        base.le.actionMgr.push(action)
        action()
    
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()

class Float4InputPanel:
    def __init__(self, panel):
        self.panel = panel
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        
        self.txtF1 = xrc.XRCCTRL(self.panel, "txtF1")
        self.txtF2 = xrc.XRCCTRL(self.panel, "txtF2")
        self.txtF3 = xrc.XRCCTRL(self.panel, "txtF3")
        self.txtF4 = xrc.XRCCTRL(self.panel, "txtF4")
    
    def getName(self):
        return self.txtInputName.GetValue()
    
    def setName(self, name):
        self.txtInputName.SetValue(name)
    
    def setFromInput(self, input):
        value = input.getValue()
        self.txtF1.SetValue(str(value[0]))
        self.txtF2.SetValue(str(value[1]))
        self.txtF3.SetValue(str(value[2]))
        self.txtF4.SetValue(str(value[3]))
    
    def setOnInput(self, input):
        value = VBase4(float(self.txtF1.GetValue()),
                    float(self.txtF2.GetValue()),
                    float(self.txtF3.GetValue()),
                    float(self.txtF4.GetValue()))
                    
        action = ActionSetProperty(base.le, input.setValue, input.getValue, value)
        base.le.actionMgr.push(action)
        action()
    
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()
class Float4x4InputPanel:
    def __init__(self, panel):
        self.panel = panel
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        
        self.txtR0C0 = xrc.XRCCTRL(self.panel, "txtR0C0")
        self.txtR0C1 = xrc.XRCCTRL(self.panel, "txtR0C1")
        self.txtR0C2 = xrc.XRCCTRL(self.panel, "txtR0C2")
        self.txtR0C3 = xrc.XRCCTRL(self.panel, "txtR0C3")
        
        self.txtR1C0 = xrc.XRCCTRL(self.panel, "txtR1C0")
        self.txtR1C1 = xrc.XRCCTRL(self.panel, "txtR1C1")
        self.txtR1C2 = xrc.XRCCTRL(self.panel, "txtR1C2")
        self.txtR1C3 = xrc.XRCCTRL(self.panel, "txtR1C3")
        
        self.txtR2C0 = xrc.XRCCTRL(self.panel, "txtR2C0")
        self.txtR2C1 = xrc.XRCCTRL(self.panel, "txtR2C1")
        self.txtR2C2 = xrc.XRCCTRL(self.panel, "txtR2C2")
        self.txtR2C3 = xrc.XRCCTRL(self.panel, "txtR2C3")
        
        self.txtR3C0 = xrc.XRCCTRL(self.panel, "txtR3C0")
        self.txtR3C1 = xrc.XRCCTRL(self.panel, "txtR3C1")
        self.txtR3C2 = xrc.XRCCTRL(self.panel, "txtR3C2")
        self.txtR3C3 = xrc.XRCCTRL(self.panel, "txtR3C3")
    
    def getName(self):
        return self.txtInputName.GetValue()
    
    def setName(self, name):
        self.txtInputName.SetValue(name)
    
    def setFromInput(self, input):
        value = input.getValue()
        self.txtR0C0.SetValue(str(value.getCell(0,0)))
        self.txtR0C1.SetValue(str(value.getCell(0,1)))
        self.txtR0C2.SetValue(str(value.getCell(0,2)))
        self.txtR0C3.SetValue(str(value.getCell(0,3)))
        
        self.txtR1C0.SetValue(str(value.getCell(1,0)))
        self.txtR1C1.SetValue(str(value.getCell(1,1)))
        self.txtR1C2.SetValue(str(value.getCell(1,2)))
        self.txtR1C3.SetValue(str(value.getCell(1,3)))
        
        self.txtR2C0.SetValue(str(value.getCell(2,0)))
        self.txtR2C1.SetValue(str(value.getCell(2,1)))
        self.txtR2C2.SetValue(str(value.getCell(2,2)))
        self.txtR2C3.SetValue(str(value.getCell(2,3)))
        
        self.txtR3C0.SetValue(str(value.getCell(3,0)))
        self.txtR3C1.SetValue(str(value.getCell(3,1)))
        self.txtR3C2.SetValue(str(value.getCell(3,2)))
        self.txtR3C3.SetValue(str(value.getCell(3,3)))
    
    def setOnInput(self):
        value = Mat4(float(self.txtR0C0.GetValue()),
                    float(self.txtR0C1.GetValue()),
                    float(self.txtR0C2.GetValue()),
                    float(self.txtR0C3.GetValue()),
                    float(self.txtR1C0.GetValue()),
                    float(self.txtR1C1.GetValue()),
                    float(self.txtR1C2.GetValue()),
                    float(self.txtR1C3.GetValue()),
                    float(self.txtR2C0.GetValue()),
                    float(self.txtR2C1.GetValue()),
                    float(self.txtR2C2.GetValue()),
                    float(self.txtR2C3.GetValue()),
                    float(self.txtR3C0.GetValue()),
                    float(self.txtR3C1.GetValue()),
                    float(self.txtR3C2.GetValue()),
                    float(self.txtR3C3.GetValue()))
                    
        action = ActionSetProperty(base.le, input.setValue, input.getValue, value)
        base.le.actionMgr.push(action)
        action()
    
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()
        
class NodepathInputPanel:
    def __init__(self, panel):
        self.panel = panel
        
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        self.lblSelectedName = xrc.XRCCTRL(self.panel, "lblSelectedName")
        self.btnLoadObject = xrc.XRCCTRL(self.panel, "btnLoadObject")
        self.btnLoadObject.Bind(wx.EVT_BUTTON, self.onLoadObject)
        self.object = None
   
    def onLoadObject(self, evt=None):
        dlg = ObjectInputDialog(self.panel)
        objName = dlg.ShowModal()
        dlg.Destroy()
        
        self.object = base.le.objectMgr.findObjectById(objName)
        self.lblSelectedName.SetLabel(objName)
        
        self.setOnInput(base.le.ui.objectPropertyUI.shaderPanel.input)
   
    def getName(self):
        return self.txtInputName.GetValue()
    
    def setName(self, name):
        self.txtInputName.SetValue(name)
   
    def setFromInput(self, input):
        if input.obj:
            self.lblSelectedName.SetLabel(input.obj.name)
            self.object = input.obj
        else:
            self.lblSelectedName.SetLabel("")
            self.object = None
        
    def setOnInput(self, input):
        action = ActionSetProperty(base.le, input.setObj, input.getObj, self.object)
        base.le.actionMgr.push(action)
        action()
        
    def Hide(self):
        self.panel.Hide()
    
    def Show(self):
        self.panel.Show()
    
class CameraInputPanel:
    def __init__(self, panel):
        self.panel = panel
        
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        
    def getName(self):
        return self.txtInputName.GetValue()
        
    def setName(self, name):
        self.txtInputName.SetValue(name)
        
    def setFromInput(self, input):
        pass
        
    def setOnInput(self, input):
        pass     
        
    def Hide(self):
        self.panel.Hide()
    
    def Show(self):
        self.panel.Show()
        
class TimeInputPanel:
    def __init__(self, panel):
        self.panel = panel
        
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        self.txtOffset = xrc.XRCCTRL(self.panel, "txtOffset")
        
    def getName(self):
        return self.txtInputName.GetValue()
        
    def setName(self, name):
        self.txtInputName.SetValue(name)
        
    def setFromInput(self, input):
        self.txtOffset.SetValue(str(input.offset))
    
    def setOnInput(self, input):
        offset = float(self.txtOffset.GetValue())
        action = ActionSetProperty(base.le, input.setOffset, input.getOffset, offset)
        base.le.actionMgr.push(action)
        action()
        
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()
        
class TextureInputPanel(wx.TextDropTarget):
    def __init__(self, panel):
        self.panel = panel
        
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        self.labelSelectedName = xrc.XRCCTRL(self.panel, "lblSelectedName")
        wx.TextDropTarget.__init__(self)
        self.panel.SetDropTarget(self)
        
        self.texture = None
        
    def getName(self):
        return self.txtInputName.GetValue()
        
    def setName(self, name):
        self.txtInputName.SetValue(name)
        
    def setFromInput(self, input):
        self.texture = input.tex
        if self.texture:
            self.labelSelectedName.SetLabel(self.texture.name)
        else:
            self.labelSelectedName.SetLabel("")
    
    def setOnInput(self, input):
        texture = self.texture
        action = ActionSetProperty(base.le, input.setTexture, input.getTexture, texture)
        base.le.actionMgr.push(action)
        action()
        
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()
        
    def OnDropText(self, x, y, text):
        #make sure this is a texture, not something else random
        if text.find('>') == -1:
            return
        if text.split('>')[0] != 'Textures':
            return
        
        self.texture = base.le.lib.textures[text.split('>')[1]]
        
        if self.texture.isCubeMap():
            dlg = wx.MessageDialog(self.panel, "You may not choose a cubemap texture asset for this input.", "Non-Cubemap required", style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.labelSelectedName.SetLabel(text.split('>')[1])
        self.setOnInput(base.le.ui.objectPropertyUI.shaderPanel.input)
        
class CubemapInputPanel(wx.TextDropTarget):
    def __init__(self, panel):
        self.panel = panel
        
        self.txtInputName = xrc.XRCCTRL(self.panel, "txtInputName")
        self.labelSelectedName = xrc.XRCCTRL(self.panel, "lblSelectedName")
        wx.TextDropTarget.__init__(self)
        self.panel.SetDropTarget(self)
        
        self.texture = None
        
    def getName(self):
        return self.txtInputName.GetValue()
        
    def setName(self, name):
        self.txtInputName.SetValue(name)
        
    def setFromInput(self, input):
        self.texture = input.tex
        if self.texture:
            self.labelSelectedName.SetLabel(self.texture.name)
        else:
            self.labelSelectedName.SetLabel("")
    
    def setOnInput(self, input):
        texture = self.texture
        action = ActionSetProperty(base.le, input.setTexture, input.getTexture, texture)
        base.le.actionMgr.push(action)
        action()
        
    def Hide(self):
        self.panel.Hide()
        
    def Show(self):
        self.panel.Show()
        
    def OnDropText(self, x, y, text):
        #make sure this is a cubemap, not something else random
        if text.find('>') == -1:
            return
        if text.split('>')[0] != 'Textures':
            return 
        
        self.texture = base.le.lib.textures[text.split('>')[1]]
        if not self.texture.isCubeMap():
            dlg = wx.MessageDialog(self.panel, "You must choose a cubemap texture asset (.dds files).", "Cube Map required", style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.labelSelectedName.SetLabel(text.split('>')[1])
