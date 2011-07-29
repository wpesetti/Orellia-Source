import wx
import os
import Library
import Util
from wx import xrc
from pandac.PandaModules import Filename
import SoundMgrBase

RESOURCE_FILE = 'XRC/SoundUI.xrc'
DIALOG_RESOURCE_FILE = 'XRC/dlgSoundEditor.xrc'
#DIALOG_RESOURCE_FILE = 'XRC/test1.xrc'

class SoundUI(wx.Panel):
    def __init__(self, parent, id, editor):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(RESOURCE_FILE)
        self.res.LoadOnPanel(pre, parent, 'panelSound')
        self.PostCreate(pre)
        
        #list of sound objects (not assests) currently in the scene so the listbox gets updated 
        self.sceneSounds = []
        self.parent = parent
        self.editor = editor

        
        
        parent.SetDropTarget(SoundUIDropTarget(self,self.editor))
        
        self.listSound = xrc.XRCCTRL(self, 'listBoxSounds')
        self.btnEdit = xrc.XRCCTRL(self, 'btnEdit')
        self.btnRemove = xrc.XRCCTRL(self, 'btnRemove')
        
        self.btnEdit.Bind(wx.EVT_BUTTON, self.onEdit)
        self.btnRemove.Bind(wx.EVT_BUTTON, self.onRemove)
        
        
    def reset(self):
        self.sceneSounds = []
        self.listSound.Clear()
    
    def update(self):
        self.sceneSounds = []
        for sound in self.editor.soundMgr.sounds.values():
            self.sceneSounds.append(sound)
        self.updateList()
        
        
    def updateList(self):
        self.listSound.Clear()
        for x in self.sceneSounds:
            #just using the key here because that is the name I think?
            self.listSound.Append(x.name)
            
    def onEdit(self, evt):
        ##Make sure to pass the sound object instance, not just the name
        dlg = SoundEditDialog(self, -1, self.editor, self.sceneSounds[self.listSound.GetSelection()])
        dlg.ShowModal()
        self.editor.soundMgr.stopAllSounds()         
        self.updateList()
  
        
    def onRemove(self, evt):
        
        selected = self.listSound.GetSelection()
        #soundObj = self.sceneSounds[selected]
        self.editor.soundMgr.removeSound(self.listSound.GetString(selected))#soundObj.name)
        self.update()
        #del self.sceneSounds[selected]
        self.updateList()
        
        
class SoundUIDropTarget(wx.TextDropTarget):
    def __init__(self, parent,editor):
        wx.TextDropTarget.__init__(self)
        self.parent = parent
        self.editor = editor
        
    def OnDropText(self, x, y, text):
        print text.split('>')[1]
        self.sound = base.le.lib.sounds[text.split('>')[1]] 
        soundObj = self.editor.soundMgr.addNewSound(self.sound.name, self.sound)    
        self.parent.sceneSounds.append(soundObj)
        self.parent.updateList()
        

class SoundEditDialog(wx.Dialog):
    ##needs to have sound OBJECT not ASSET here
    def __init__(self, parent, id, editor, sound):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(DIALOG_RESOURCE_FILE)
        self.res.LoadOnDialog(pre, parent, 'dlgSoundEdit')
        #self.res.LoadOnDialog(pre, parent, 'test')
        self.PostCreate(pre)
        
        self.sound = sound
        self.editor = editor
        self.animlist = []
        
        self.ok = False
        
        self.currentName = xrc.XRCCTRL(self, 'lblCurrentName')
        self.textNewName = xrc.XRCCTRL(self, 'txtNewName')
        self.chkLoop = xrc.XRCCTRL(self, 'chkLoop')
        self.spinPlayCount = xrc.XRCCTRL(self, 'spinPlayCount')
        self.slVolume = xrc.XRCCTRL(self, 'slVolume')
        self.txtVolume = xrc.XRCCTRL(self, 'txtVolume')
        self.slBalance = xrc.XRCCTRL(self, 'slBalance')
        self.btnPlay = xrc.XRCCTRL(self, 'btnPlay')
        self.btnStop = xrc.XRCCTRL(self, "btnStop")
        self.btnChangeName = xrc.XRCCTRL(self, 'btnChangeName')
        self.btnOk = xrc.XRCCTRL(self, 'btnOk')
        self.btnCancel = xrc.XRCCTRL(self, 'btnCancel')
        
        self.btnAddPlay = xrc.XRCCTRL(self, 'btnAddPlay')
        self.btnAddPlay.Bind(wx.EVT_BUTTON, self.onAdd)
        self.btnRemovePlay = xrc.XRCCTRL(self, 'btnRemovePlay')
        self.btnRemovePlay.Bind(wx.EVT_BUTTON, self.onRemove)
        self.chkBg = xrc.XRCCTRL(self, 'chkBg')
        self.chkBg.Bind(wx.EVT_CHECKBOX, self.setBg)
        
        self.actorList, self.actorName = self.editor.objectMgr.findObjectsByAssetRName("actor")
        
        self.dropActor = xrc.XRCCTRL(self, 'dropActor')
        self.dropActor.Bind(wx.EVT_COMBOBOX, self.getActorList)
        self.dropActor.SetItems(self.actorName)
        
        self.dropAnim = xrc.XRCCTRL(self, 'dropAnimation')
        self.dropAnim.Bind(wx.EVT_COMBOBOX, self.getAnimList)
        
        self.playwithlist = xrc.XRCCTRL(self, 'playwithlist')
        self.playwithlist.InsertColumn(0, "Actor")
        self.playwithlist.SetColumnWidth(0, 100)
        self.playwithlist.InsertColumn(1, "Animation")
        self.playwithlist.SetColumnWidth(1, 150)
        i=0
        if self.sound.anims != []:
            for n in self.sound.anims:
                pos = self.playwithlist.GetItemCount()
                self.playwithlist.InsertStringItem(pos, self.sound.actors[i])
                self.playwithlist.SetStringItem(pos, 1, n)
                self.animlist.append(n)
                i=i+1
                       
        
        self.currentName.SetLabel(self.sound.name)
        
        self.sliders = [self.slVolume]
        self.textValueBoxes = [ self.txtVolume]
        
        self.txtVolume.SetValue(str((self.sound.getVolume() * 100.0)))
        self.slVolume.SetValue(int(self.sound.getVolume() * 100.0))
 
        self.chkLoop.SetValue(self.sound.getLoop())
        self.spinPlayCount.SetValue(int(self.sound.getLoopCount()))
        
        
        self.origVolume = self.sound.getVolume()
        self.origName = self.currentName.GetLabel()
        self.origLoop = self.sound.getLoop()
        self.origLoopCount = self.sound.getLoopCount()
        
        self.chkLoop.Bind(wx.EVT_CHECKBOX, self.onLoop)
        self.spinPlayCount.Bind(wx.EVT_SPINCTRL, self.onLoopCount)
        self.spinPlayCount.Bind(wx.EVT_TEXT, self.onLoopCount)
        self.slVolume.Bind(wx.EVT_SLIDER, self.onSliderVolume )
        self.txtVolume.Bind(wx.EVT_TEXT_ENTER, self.onTextVolume)
        self.btnChangeName.Bind(wx.EVT_BUTTON, self.onChangeName)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.btnOk.Bind(wx.EVT_BUTTON, self.onOk)
        self.btnPlay.Bind(wx.EVT_BUTTON, self.onPlay)
        self.btnStop.Bind(wx.EVT_BUTTON, self.onStop)
        
        # Keep the editor from binding the keys
        base.le.ui.bindKeyEvents(False)
        
    def onCancel(self, evt):
        self.sound.setVolume(self.origVolume)
        self.sound.setLoop(self.origLoop)
        self.sound.setLoopCount(self.origLoopCount)
        self.editor.soundMgr.renameSound(self.sound, self.origName)
        self.Destroy()
        
    def onOk(self, evt):
        
        self.Destroy()       
    
    def onLoop(self, evt):
        val = int(self.chkLoop.GetValue())
        if val == 1:
            self.spinPlayCount.Disable()
        else:
            self.spinPlayCount.Enable()
        
        self.sound.setLoop(val)
        
    def onLoopCount(self, evt):
        val = self.spinPlayCount.GetValue()
        self.sound.setLoopCount(val)
    
    def onSliderVolume(self, evt):
        val = float(self.slVolume.GetValue() / 100.0)
        self.txtVolume.SetValue(str(val * 100.0))
        self.sound.setVolume(val)
    
    def onTextVolume(self, evt):
        try:
            val = float(self.txtBalance.GetValue())
            if val > 100.0:
                val = 100.0
            elif val < 0.0:
                val = 0.0
        except ValueError as e:
            msg = wx.MessageDialog(self, e.message, "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()
            self.txtVolume.SetValue(str(self.sound.getVolume() * 100.0))
        else:
            self.txtVolume.SetValue(str(val * 1.0))
            self.sound.setVolume(val / 100.0) 
            self.slVolume.SetValue(int(val)) 
       
    def onPlay(self, evt):
        if self.sound.getStatus() == 2:
            self.sound.stop()
            self.sound.play()
        else:
            self.sound.play()
            
    def onStop(self, evt):
        self.sound.stop()
    
    def onChangeName(self, evt):
        if self.textNewName.GetValue() != '':
            self.editor.soundMgr.renameSound(self.sound, self.textNewName.GetValue())
            self.currentName.SetLabel(self.textNewName.GetValue())      
        else:
            msg = wx.MessageDialog(self, "Invalid Name: Empty String", "Invalid Input", wx.OK|wx.ICON_HAND)
            msg.ShowModal()
            msg.Destroy()

    def Close(self, evt):
        base.le.ui.bindKeyEvents(True)
        self.Destroy()
        
    def setBg(self, evt):
        val = self.chkBg.GetValue()
        if val == True:
            self.editor.soundMgr.setBackgroundMusic(self.sound.name)
    
    def onAdd(self, evt):
        actor = self.dropActor.GetValue()
        animation = self.dropAnim.GetValue()
        if (actor == "") | (animation == ""):
            dialog = wx.MessageDialog(self,"No Actor or Animation Selected", "Error", wx.OK|wx.ICON_HAND)
            dialog.ShowModal()
            dialog.Destroy()
            return
        pos = self.playwithlist.GetItemCount()
        pos1 = self.playwithlist.InsertStringItem(pos, actor)
        self.playwithlist.SetStringItem(pos1, 1, animation)
        self.editor.soundMgr.attachSoundToAnims(actor, animation, self.sound.name)
        self.animlist.append(animation)
    
    def onRemove(self, evt):
        index = self.playwithlist.GetFocusedItem()
        #print index
        if index == -1:
            return
        actor = self.playwithlist.GetItemText(index)
        self.editor.soundMgr.removeSoundFromAnims(actor, self.animlist[index], self.sound.name)
        self.animlist.pop(index)
        self.playwithlist.DeleteItem(index)
    
    
    def getActorList(self, evt):
        val = self.dropActor.GetValue()
        i = self.actorName.index(val)
        self.animName = []
        for n in self.actorList[i].getAllAnims():
            self.animName.append(n)
        self.dropAnim.SetItems(self.animName)
    
    def getAnimList(self, evt):
        pass
    
