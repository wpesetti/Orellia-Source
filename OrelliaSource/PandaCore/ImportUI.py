import wx
import os
import shutil
import stat
import subprocess
import Library
import Util
from pandac.PandaModules import *
from direct.wxwidgets.ViewPort import *
from direct.directtools.DirectManipulation import ObjectHandles
from direct.directtools.DirectGlobals import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from wx import xrc
from wx.lib.mixins.listctrl import TextEditMixin

GUI_FILENAME = 'XRC/ImportUI.xrc'

LE_IMPORT_MASK = BitMask32.bit(4)
LE_CAM_MASKS['import'] = LE_IMPORT_MASK

class ListCtrlMultiEdit(wx.ListCtrl, TextEditMixin):
    pass
        

#dialog box for importing assets
class ImportUI(wx.Dialog):
    def __init__(self, parent, id, title):
        #Pre creation routine to allow wx to do layout from XRC
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(GUI_FILENAME)
        self.res.LoadOnDialog(pre, parent, 'dlgImportUI')
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
    
    def OnCreate(self, e): 
        self.Unbind(wx.EVT_INIT_DIALOG)
        base.le.ui.bindKeyEvents(False)  
        self.filename = None
        self.name=''
        self.Ok = False
        self.assetType = "Static Mesh"
        self.importScene = NodePath(PandaNode("importScene"))      
        self.import2d = NodePath(PandaNode("import2d"))
        self.import2dScaled =self.import2d.attachNewNode(PandaNode("import2dScaled"))
        self.objPreview = None
        self.thumbnailTaken = False
        
        self.Bind(wx.EVT_CLOSE, self.Close)
        
        base.direct.manipulationControl.disableManipulation()
        self.Show()
        
        #init all the panels from XRC for parenting later on
        self.mainPanel = xrc.XRCCTRL(self, "mainPanel")
        self.pandaPanel = xrc.XRCCTRL(self, "pandaPanel")
        self.animPanel = xrc.XRCCTRL(self, "animPanel")
        self.libraryPanel = xrc.XRCCTRL(self, "libraryPanel")
        
  
        self.typeSelector = xrc.XRCCTRL(self.libraryPanel, 'choiceAssetType')
        self.typeSelector.Bind(wx.EVT_CHOICE, self.onSwitchType)
        self.typeSelector.SetStringSelection(self.assetType)
        
        self.btnScreenshot = xrc.XRCCTRL(self.mainPanel, "btnScreenShot")
        self.btnScreenshot.Bind(wx.EVT_BUTTON, self.onScreenShot)
        self.btnScreenshot.Disable()
        
        self.imgThumbnail = xrc.XRCCTRL(self.libraryPanel, 'imgThumbnail')
        self.btnPlay = xrc.XRCCTRL(self.libraryPanel, "btnPlay")
        self.btnStop = xrc.XRCCTRL(self.libraryPanel, "btnStop")
        
        self.viewport = Viewport('persp', self.pandaPanel)
        self.viewport.SetClientSize((500,500))
        ViewportManager.updateAll()
        base.le.ui.wxStep()
        self.viewport.initialize()
        self.handles = ObjectHandles('importUIWidget')
        self.handles.hide()
        base.direct.manipulationControl.widgetList.append(self.handles)
        base.direct.drList.addDisplayRegionContext(self.viewport.cam)
        #apply a mask to make sure GUI stuff from the main window doesn't show up here
        self.viewport.cam2d.node().setCameraMask(LE_IMPORT_MASK)
        
        self.viewport.camera.reparentTo(self.importScene)
        self.viewport.camera.setPos(-19,-19,19)
        self.viewport.camera.lookAt(0,0,0)
        self.viewport.cam2d.reparentTo(self.import2d)  

        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.8,0.8,0.8,1))
        dlnp = self.importScene.attachNewNode(dlight)
        self.importScene.setLight(dlnp)
        dlnp.setHpr(45,-45,0)
        
        alight = AmbientLight('alight')
        alight.setColor(VBase4(0.25,0.25,0.25,1))
        alnp = self.importScene.attachNewNode(alight)
        self.importScene.setLight(alnp)

        fileSelector = xrc.XRCCTRL(self.mainPanel, 'btnLoadAsset')
        fileSelector.Bind(wx.EVT_BUTTON, self.onFileSelect)
            
        if self.assetType != "Library":
            
            self.nameInput = xrc.XRCCTRL(self.libraryPanel, 'txtObjName')
            self.nameInput.Bind(wx.EVT_TEXT, self.onNameInput)

        self.okButton = xrc.XRCCTRL(self.mainPanel, 'btnSendToLibrary')
        self.okButton.Bind(wx.EVT_BUTTON, self.onOk)        
        self.okButton.Enable(False)
        
        self.animPanel = xrc.XRCCTRL(self.mainPanel, 'animPanel')
        self.btnImportAnim = xrc.XRCCTRL(self.animPanel, 'btnImportAnim')
        self.btnImportAnim.Bind(wx.EVT_BUTTON, self.onImportAnim)
        self.btnImportAnim.Enable(False)
        self.btnRemoveSelected = xrc.XRCCTRL(self.animPanel, 'btnRemoveSelected')
        self.btnRemoveSelected.Bind(wx.EVT_BUTTON, self.onRemoveSelected)
        self.btnRemoveSelected.Enable(False)
        self.listCtrlAnim = xrc.XRCCTRL(self.animPanel, 'listCtrlAnim')
        self.listCtrlAnim.__class__ = ListCtrlMultiEdit
        self.btnPlay.Bind(wx.EVT_BUTTON, self.onPlaySound)
        self.btnStop.Bind(wx.EVT_BUTTON, self.onStopSound)
        self.listCtrlAnim.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.onEditAnim)
        self.listCtrlAnim.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectAnim)
        self.imgThumbnail.Bind(wx.EVT_BUTTON, self.onScreenShot)
        
        TextEditMixin.__init__(self.listCtrlAnim)

        self.Layout()
        
    def onPlaySound(self, evt):
        base.sfxManagerList[0].stopAllSounds()
        self.objPreview.setLoop(False)
        self.objPreview.play()

    def onStopSound(self, evt):
        self.objPreview.stop()

    def onScreenShot(self, evt):
        if self.assetType == "Static Mesh" or self.assetType == "Actor":
            camnode = self.viewport.cam.node()
            dr = camnode.getDisplayRegion(0)
            filename = Filename("thumbnail")
            filename.setDirname(Util.getTempDir())
            filename.setExtension("jpg")
            dr.saveScreenshot(filename)
            
            #resize to 60x60
            cwd = os.getcwd()
            os.chdir(Filename(filename.getDirname()).toOsSpecific())
            subprocess.call(["image-resize","-x 60", "-y 60", "-g 1", "-o" + filename.getBasename(), filename.getBasename()])
            os.chdir(cwd)
            
            self.imgThumbnail.SetBitmapLabel(wx.Bitmap(filename.toOsSpecific()))
            
            self.thumbnailTaken = True

    def onSwitchType(self, evt):
        self.assetType = self.typeSelector.GetStringSelection()
        self.nameInput.SetValue("")
        self.name = None      
        self.filename = None
        self.thumbnailTaken = False
        self.btnScreenshot.Disable()
        
        if self.objPreview:
            if not isinstance(self.objPreview, AudioSound):
                self.objPreview.removeNode()
            
        if self.assetType == "Static Mesh" or self.assetType == "Actor":
            self.viewport.camera.setPos(-19,-19,19)
            self.viewport.camera.lookAt(0,0,0)
        

        self.btnImportAnim.Enable(False)
        self.btnRemoveSelected.Enable(False)
        self.btnPlay.Enable(False)
        self.btnStop.Enable(False)
        
        base.sfxManagerList[0].stopAllSounds()
        
        self.listCtrlAnim.ClearAll()
        
        if self.assetType == "Actor":
            self.listCtrlAnim.InsertColumn(0, "Local Name")
            self.listCtrlAnim.InsertColumn(1, "Asset Name")
            self.listCtrlAnim.InsertColumn(2, "File")
            for i in range(self.listCtrlAnim.GetColumnCount()):
                self.listCtrlAnim.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        
    def onNameInput(self, evt):
        iPoint = self.nameInput.GetInsertionPoint()
        self.nameInput.ChangeValue(Util.toAssetName(self.nameInput.GetValue(), False))
        self.nameInput.SetInsertionPoint(iPoint)
        self.name = self.nameInput.GetValue()
        if self.name and self.filename:
            self.okButton.Enable(True)
        else:
            self.okButton.Enable(False)
    
    def onFileSelect(self, evt):
        self.thumbnailTaken = False
        fileType = "*.*"
        
        if self.assetType == "Static Mesh" or self.assetType == "Actor" or self.assetType == "Animation":
            fileType = "Egg files (*.egg;*.egg.pz)|*.egg;*.egg.pz"
        elif self.assetType == "Texture" or self.assetType == "Terrain":
            fileType = "Texture files (*.png;*.jpg;*.jpeg;*.bmp;*.rgb;*.tif;*.avi;*.mpg;*.mpeg;*.dds)|*.png;*.jpg;*.jpeg;*.bmp;*.rgb;*.tif;*.avi;*.mpg;*.mpeg;*.dds"
        elif self.assetType == "Shader":
            fileType = "Shader files (*.sha;*.cg)|*.sha;*.cg"
        elif self.assetType == "Sound":
            fileType = "Sound files (*.wav;*.mp3;*.aiff;*.ogg) | *.wav;*.mp3;*.aiff;*.ogg"
        elif self.assetType == "Texture Sequence":
            fileType = "Texture files (*.png;*.jpg;*.jpeg;*.bmp;*.rgb;*.tif)|*.png;*.jpg;*.jpeg;*.bmp;*.rgb;*.tif"
        elif self.assetType == "Journal Entry":
            fileType = "Journal Entry files (*.xml)|*.xml"
        elif self.assetType == "Conversation":
            fileType = "Conversation files (*.xml)|*.xml"
        
        if self.assetType != "Texture Sequence":
            dialog = wx.FileDialog(self, "Select a " + self.assetType +" file", wildcard=fileType, style=wx.FD_OPEN )
        else:
            dialog = wx.FileDialog(self, "Select the texture files to use.", wildcard=fileType, style=wx.FD_OPEN|wx.FD_MULTIPLE)
        
        
        if dialog.ShowModal() == wx.ID_OK:
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            if self.assetType != "Texture Sequence":
                self.filename = Filename.fromOsSpecific(dialog.GetPath())
                self.name = self.filename.getBasenameWoExtension()
            else:
                filenames = []
                for p in sorted(dialog.GetPaths()):
                    filenames.append(Filename.fromOsSpecific(p))
                self.name = filenames[0].getBasenameWoExtension().strip('1234567890-_')

            self.okButton.Enable(True)	
            self.nameInput.SetValue(self.name)
            
            if self.assetType == "Static Mesh":
                if self.objPreview:
                    self.objPreview.removeNode()
                self.objPreview = loader.loadModel(self.filename)
                self.objPreview.reparentTo(self.importScene)
                self.btnScreenshot.Enable(True)
                center = self.objPreview.getBounds().getCenter()
                radius = self.objPreview.getBounds().getRadius()
                self.viewport.camera.setPos(center + Vec3(-radius*2,-radius*2,radius*2))
                self.viewport.camera.lookAt(center)
                self.viewport.camLens.setNearFar(radius/10, radius*1000)
                
            elif self.assetType == "Texture" or self.assetType == "Terrain":
                if self.objPreview:
                    self.objPreview.removeNode()
                
                self.objPreview = OnscreenImage(parent=self.import2d, image = self.filename.getFullpath(), pos = (0.0,0.0,0.0))    
                
                x = float(self.objPreview.getTexture().getOrigFileXSize())                
                y = float(self.objPreview.getTexture().getOrigFileYSize())

                if x == 0.0 or y == 0.0:
                    x = float(self.objPreview.getTexture().getVideoWidth()) * self.objPreview.getTexture().getTexScale().getX()
                    y = float(self.objPreview.getTexture().getVideoHeight()) * self.objPreview.getTexture().getTexScale().getY()
                    self.objPreview.setTexScale(TextureStage.getDefault(), self.objPreview.getTexture().getTexScale())

                if x>y:
                    self.objPreview.setScale(1, 1, y/x)
                else:
                    self.objPreview.setScale(x/y, 1, 1)
                
                self.objPreview.setLightOff(True)
            elif self.assetType == "Actor":
                self.btnImportAnim.Enable(True)
                if self.objPreview:
                    self.objPreview.removeNode()
                self.objPreview = Actor(self.filename, {})
                self.objPreview.reparentTo(self.importScene)
                self.btnScreenshot.Enable(True)
                center = self.objPreview.getBounds().getCenter()
                radius = self.objPreview.getBounds().getRadius()
                self.viewport.camera.setPos(center + Vec3(-radius*2,-radius*2,radius*2))
                self.viewport.camera.lookAt(center)
                self.viewport.camLens.setNearFar(radius/10, radius*1000)
            
            elif self.assetType == "Texture Sequence":
                tempFolder = Filename.fromOsSpecific(Util.getTempDir() + '/staging')
                if os.path.exists((tempFolder + ' /').toOsSpecific()):
                    shutil.rmtree(tempFolder.toOsSpecific())


                os.makedirs(tempFolder.toOsSpecific())

                for f in filenames:
                    dest = tempFolder + '/' + f.getBasename()
                    shutil.copy(f.toOsSpecific(), tempFolder.toOsSpecific())
                    fileAtt = os.stat(dest.toOsSpecific())[0]
                    if (not fileAtt & stat.S_IWRITE):
                        os.chmod(dest.toOsSpecific(), stat.S_IWRITE)
                    f.setDirname(tempFolder.getFullpath())
                
                args = ["egg-texture-cards","-o", self.name + ".egg", "-fps", "30"]
                

                for f in filenames:
                    args.append(f.getBasename())
                
                cwd = os.getcwd()
                os.chdir(tempFolder.toOsSpecific())    
                subprocess.call(args)
                os.chdir(cwd)
                
                self.filename = tempFolder + '/' + self.name + '.egg'
                
                if self.objPreview:
                    self.objPreview.removeNode()
                    
                self.objPreview = loader.loadModel(self.filename)
                self.objPreview.reparentTo(self.importScene)
                    
                self.viewport.camera.setPos(0, -5, 0)
                self.viewport.camera.lookAt(0,0,0)
                self.viewport.camLens.setNearFar(0.1, 10000)
                self.okButton.Enable(True)
			
            elif self.assetType == "Sound":
                if self.objPreview:
                    if not isinstance(self.objPreview, AudioSound):
                        self.objPreview.removeNode()
                self.objPreview = loader.loadSfx(self.filename.getFullpath())
                
                self.btnPlay.Enable()
                self.btnStop.Enable()
                	
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))                        
        dialog.Destroy()
    
    def onImportAnim(self, evt):
        dialog = wx.FileDialog(self, "Select an animation file", style=wx.FD_OPEN, wildcard= "Egg files(*.egg;*.egg.pz)|*.egg;*.egg.pz")
        if dialog.ShowModal() == wx.ID_OK:
            filename = Filename.fromOsSpecific(dialog.GetPath())
            
            pos = self.listCtrlAnim.InsertStringItem(self.listCtrlAnim.GetItemCount(), filename.getBasenameWoExtension())
            self.listCtrlAnim.SetStringItem(pos, 1, filename.getBasenameWoExtension())
            self.listCtrlAnim.SetStringItem(pos, 2, filename.toOsSpecific())
            self.listCtrlAnim.Select(pos, True)
            self.listCtrlAnim.EnsureVisible(pos)
            for i in range(self.listCtrlAnim.GetColumnCount()):
                self.listCtrlAnim.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            
            self.btnRemoveSelected.Enable(True)
    
    def onEditAnim(self, evt):
        if evt.GetColumn() == 0:
            if Util.toAssetName(evt.GetText()) != evt.GetText():
                evt.Veto()
        elif evt.GetColumn() == 1:
            if Util.toAssetName(evt.GetText()) != evt.GetText():
                evt.Veto()
        else:
            evt.Veto()
    
    def onSelectAnim(self, evt):
        self.objPreview.stop()
        self.objPreview.unloadAnims()
        id = evt.GetItem().GetId()
        name = self.listCtrlAnim.GetItem(id, 0).GetText()
        file = Filename.fromOsSpecific(self.listCtrlAnim.GetItem(id, 2).GetText())
        
        self.objPreview.loadAnims({name:file})
        self.objPreview.loop(name)
    
    def onRemoveSelected(self, evt):
        toDelete = self.listCtrlAnim.GetFirstSelected()
        self.objPreview.stop()
        self.objPreview.unloadAnims()
        self.listCtrlAnim.DeleteItem(toDelete)
        if self.listCtrlAnim.GetItemCount() == 0:
            self.btnRemoveSelected.Enable(False)
        else:
            self.listCtrlAnim.Select(0)
    
    def onOk(self, evt):
        self.Ok = True
        
        libFile =(base.le.lib.projDir + '/lib.index').toOsSpecific()
        while True: #make sure that the library file is writable
            try:
                f = open(libFile, 'a')
                f.close()
            except IOError as e:
                dlg = wx.MessageDialog(self, "The library file '" + libFile + "' could not be written.\
                Make sure that it is not marked read-only and click OK.", caption = "Permission Denied",
                style = wx.OK|wx.CANCEL|wx.ICON_ERROR)
                if dlg.ShowModal() == wx.ID_CANCEL:
                    self.Close()
                    return
            else:
                break
        
        removedAssetsDir = Filename.fromOsSpecific(Util.getTempDir()) + '/removedAssets'
        if os.path.exists((removedAssetsDir + '/').toOsSpecific()):
            shutil.rmtree(removedAssetsDir.toOsSpecific())
        
        self.removedAssets = []
        
        if self.assetType == "Static Mesh" or self.assetType == "Texture Sequence":              
                mesh = self.getMesh()
                while True:
                    try:
                        base.le.lib.checkMesh(mesh)
                    except Library.DuplicateNameError as e:
                        dialog = DuplicateNameDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
                            self.Close()
                            return
                        elif result == SKIP:
                            if e.oldAsset.__class__.__name__ == 'Mesh':
                                self.restoreAssets()
                                self.Close()
                                return
                            mesh.textures.remove(e.newAsset)
                            mesh.textures.append(e.oldAsset)
                    except Library.FileCollisionError as e:
                        dialog = FileCollisionDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
                            self.Close()
                            return
                        elif result == SKIP:
                            if e.asset.__class__.__name__ == 'Mesh':
                                self.restoreAssets()
                                self.Close()
                                return
                            mesh.textures.remove(e.asset)
                            f = Filename.fromOsSpecific(e.destPath)
                            f.makeRelativeTo(base.le.lib.projDir)
                            mesh.textures.append(base.le.lib.filenameIndex[f])
                    except Library.TextureNotFoundError as e:
                        message = "Egg file contains an invalid texture reference.\n"
                        message += "Texture '" + e.filename.getFullpath() + "' not found.\n"
                        message += "Please fix your texture paths in your egg file before importing."
                        dialog = wx.MessageDialog(self, message, "Texture Not Found", style = wx.OK|wx.ICON_ERROR)
                        dialog.ShowModal()
                        dialog.Destroy()
                        return
                    else:
                        break
                base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
                base.le.lib.addMesh(mesh, True)
                if self.thumbnailTaken:
                    thumbnailPath = base.le.lib.projDir + '/Models/Thumbnails/' + \
                    mesh.filename.getBasenameWoExtension() + '.jpg'
                    tempPath = Filename.fromOsSpecific(Util.getTempDir() + '/thumbnail.jpg')
                    shutil.move(tempPath.toOsSpecific(),\
                    (thumbnailPath).toOsSpecific())
                base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        elif self.assetType == "Actor":           
            actor = self.getActor()
            for anim in self.anims:
                while True:
                    try:
                        base.le.lib.checkAnimation(anim)
                    except Library.DuplicateNameError as e:
                        dialog = DuplicateNameDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
                            self.Close()
                            return
                        elif result == SKIP:
                            self.anims.remove(e.newAsset)
                            self.anims.append(e.oldAsset)
                    except Library.FileCollisionError as e:
                        dialog = FileCollisionDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
                            self.Close()
                            return
                        elif result == SKIP:
                            self.anims.remove(e.asset)
                            f = Filename.fromOsSpecific(e.destPath)
                            f.makeRelativeTo(base.le.lib.projDir)
                            self.anims.append(base.le.lib.filenameIndex[f])
                    else:
                        break
            
            while True:
                try:
                    base.le.lib.checkActor(actor)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL:
                        self.restoreAssets()
                        self.Close()
                        return
                    elif result == SKIP:
                        if e.oldAsset.__class__.__name__ == 'Actor':
                            self.restoreAssets()
                            self.Close()
                            return
                        actor.textures.remove(e.newAsset)
                        actor.textures.append(e.oldAsset)
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL:
                        self.restoreAssets()
                        self.Close()
                        return
                    elif result == SKIP:
                        if e.asset.__class__.__name__ == 'Actor':
                            self.restoreAssets()
                            self.Close()
                            return
                        actor.textures.remove(e.asset)
                        f = Filename.fromOsSpecific(e.destPath)
                        f.makeRelativeTo(base.le.lib.projDir)
                        actor.textures.append(base.le.lib.filenameIndex[f])
                except Library.TextureNotFoundError as e:
                    message = "Egg file contains an invalid texture reference.\n"
                    message += "Texture '" + e.filename.getFullpath() + "' not found.\n"
                    message += "Please fix your texture paths in your egg file before importing."
                    dialog = wx.MessageDialog(self, message, "Texture Not Found", style = wx.OK|wx.ICON_ERROR)
                    dialog.ShowModal()
                    dialog.Destroy()
                    return
                else:
                        break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            for anim in self.anims:
                base.le.lib.addAnimation(anim)
                        
            base.le.lib.addActor(actor, True)
            if self.thumbnailTaken:
                thumbnailPath = base.le.lib.projDir + '/Models/Thumbnails/' + \
                actor.filename.getBasenameWoExtension() + '.jpg'
                tempPath = Filename.fromOsSpecific(Util.getTempDir() + '/thumbnail.jpg')
                shutil.move(tempPath.toOsSpecific(), (thumbnailPath).toOsSpecific())
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        elif self.assetType == "Animation":
            anim = self.getAnimation()
            while True:
                try:
                    base.le.lib.checkAnimation(anim)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))        
            base.le.lib.addAnimation(anim)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        elif self.assetType == "Texture":

            tex = self.getTexture()
            while True:
                try:
                    base.le.lib.checkTexture(tex)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)                    
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addTexture(tex,True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        elif self.assetType == "Shader":
            shader = self.getShader()
            while True:
                try:
                    base.le.lib.checkShader(shader)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
                    
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addShader(shader, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        elif self.assetType == "Sound":
            sound = self.getSound()
            while True:
                try:
                    base.le.lib.checkSound(sound)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addSound(sound, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
        elif self.assetType == "Terrain":
            tex = self.getTerrain()
            while True:
                try:
                    base.le.lib.checkTerrain(tex)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)                    
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if not result:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addTerrain(tex, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        #TODO: Take the Journal Entry import from Import assets.
        elif self.assetType == "Script":
            script = self.getScript()
            while True:
                try:
                    base.le.lib.checkScript(script)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addScript(script, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        elif self.assetType == "Conversation":
            conversation = self.getConversation()
            while True:
                try:
                    base.le.lib.checkConversation(conversation)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        self.Close()
                        return
                else:
                    break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addConversation(conversation, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))       
        if not base.le.saved:
            base.le.fNeedToSave = True
        
        base.le.ui.libraryUI.update()
        base.le.ui.storyObjUI.update()
        
        self.Close()
    
    #restores any assets that have been "deleted"(moved to temp folder) if we cancel an import
    #also restores assets that were removed from library
    def restoreAssets(self):
        #restore any files which were "deleted"
        for dir in ('Models', 'Textures', 'Shaders', 'Sounds', 'Journal_Entries', 'Conversations', 'Scripts'):
            d = os.path.join(Util.getTempDir(), 'removedAssets', dir)
            if os.path.exists(d):
                for file in os.listdir(d):
                    shutil.move(os.path.join(d, file), (base.le.lib.projDir + '/' + dir + '/').toOsSpecific())
                    
        #add assets back into library
        for asset in self.removedAssets:
            base.le.lib.restoreAsset(asset)
            
        self.removedAssets = []
    
    def Close(self, evt=None):
        self.viewport.Close()
        base.direct.manipulationControl.widgetList.remove(self.handles)
        base.direct.drList.removeDisplayRegionContext(self.viewport.cam)
        base.direct.manipulationControl.enableManipulation()
        base.le.ui.bindKeyEvents(True)
        
        self.Destroy()
    
    def getMesh(self):
        if self.thumbnailTaken:
            thumbnailPath = Filename('/Models/Thumbnails/' + self.filename.getBasenameWoExtension() + '.jpg')
            return Library.Mesh(Util.toAssetName(self.name), self.filename, thumbnailPath)
        else:
            return Library.Mesh(Util.toAssetName(self.name), self.filename)
            
    def getTexture(self):
        return Library.Texture(Util.toAssetName(self.name), self.filename)
    
    def getActor(self):
        self.anims, myAnims = self.getAnims()
        
        if self.thumbnailTaken:
            thumbnailPath = Filename('/Models/Thumbnails/' + self.filename.getBasenameWoExtension() + '.jpg')
            return Library.Actor(Util.toAssetName(self.name), self.filename, thumbnailPath, anims=myAnims)
        else:
            return Library.Actor(Util.toAssetName(self.name), self.filename, anims=myAnims)
    
    def getAnimation(self):
        return Library.Animation(Util.toAssetName(self.name), self.filename)
    
    def getAnims(self):
        anims = []
        myAnims = {}
        for i in range(self.listCtrlAnim.GetItemCount()):
            a = Library.Animation(self.listCtrlAnim.GetItem(i,1).GetText(), Filename.fromOsSpecific(self.listCtrlAnim.GetItem(i,2).GetText()))
            if a not in anims:
                anims.append(a)
                myAnims[self.listCtrlAnim.GetItem(i, 0).GetText()] = a
            else:   #if an equivalent animation is already in the list, use that one
                myAnims[self.listCtrlAnim.GetItem(i, 0).GetText()] = anims[anims.index(a)]

          
        return anims, myAnims
        
    def getShader(self):
        return Library.Shader(Util.toAssetName(self.name), self.filename)
    
    def getSound(self):
        return Library.Sound(Util.toAssetName(self.name), self.filename)
    
    def getTerrain(self):
        return Library.Terrain(Util.toAssetName(self.name), self.filename)
    def getJournalEntry(self):
        return Library.JournalEntry(Util.toAssetName(self.name),self.filename)
    def getScript(self):
        return Library.Script(Util.toAssetName(self.name),self.filename)
    
    def getConversation(self):
        return Library.ConversationAsset(Util.toAssetName(self.name), self.filename)

OK = 1
SKIP = 2
CANCEL = 3
        
#dialog box when a duplicate name is chosen for an asset
class DuplicateNameDialog(wx.Dialog):
    def __init__(self, parent, id, error):
        wx.Dialog.__init__(self, parent, id, "Duplicate Name", size= (300,200))
        self.parent = parent
        self.asset = error.newAsset
        self.oldAsset = error.oldAsset
        self.overwrite = False
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        msgTxt = 'A ' + self.asset.__class__.__name__.lower() + ' named "' + error.name \
            + '"(filename: ' + error.oldAsset.filename.toOsSpecific() + \
') already exists in the library.  Enter a new name or click ' + \
'overwrite to replace the existing asset.' 
        
        message = wx.StaticText(self, -1, msgTxt)
        message.Wrap(self.GetSizeTuple()[0])
        
        split = self.asset.name.split('_')
        if split[-1].isdigit():
            suggestion = '_'.join(split[:-1]) + '_' + str(int(split[-1])+1)
        else:
            suggestion = self.asset.name + '_2'
            
        self.nameInput = wx.TextCtrl(self, -1, suggestion)
        self.nameInput.Bind(wx.EVT_TEXT, self.onNameInput)
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.renameButton = wx.Button(self, -1, 'Rename')
        self.renameButton.Bind(wx.EVT_BUTTON, self.onRename)
        
        overwriteButton = wx.Button(self, -1, 'Overwrite')
        overwriteButton.Bind(wx.EVT_BUTTON, self.onOverwrite)
        
        cancelButton = wx.Button(self, -1, 'Cancel')
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        
        skipButton = wx.Button(self, -1, 'Skip')
        skipButton.Bind(wx.EVT_BUTTON, self.onSkip)
        
        hSizer.Add(self.renameButton)
        hSizer.Add(overwriteButton)
        hSizer.Add(skipButton)
        hSizer.Add(cancelButton)
        
        sizer.Add(message)
        sizer.Add(self.nameInput, flag=wx.EXPAND)
        sizer.Add(hSizer)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
        self.canceled = False
        self.skipped = False
    
    def onNameInput(self, evt):
        iPoint = self.nameInput.GetInsertionPoint()
        self.nameInput.ChangeValue(Util.toAssetName(self.nameInput.GetValue(), False))
        self.nameInput.SetInsertionPoint(iPoint)
        
        self.renameButton.Enable(self.nameInput.GetValue() != '')
    
    def onRename(self, evt):
        self.asset.name = self.nameInput.GetValue()
        self.Close()
        
    def onOverwrite(self, evt):
        if self.asset.__class__.__name__ == "Mesh":
            base.le.lib.removeMesh(self.asset.name, force=True)
        elif self.asset.__class__.__name__ == "Texture":
            base.le.lib.removeTexture(self.asset.name, force=True)
        elif self.asset.__class__.__name__ == "Actor":
            base.le.lib.removeActor(self.asset.name, force=True)
        elif self.asset.__class__.__name__ == "Animation":
            base.le.lib.removeAnimation(self.asset.name, force=True)
        elif self.asset.__class__.__name__ == "Shader":
            base.le.lib.removeShader(self.asset.name, force=True)
        elif self.asset.__class__.__name__ == "Sound":
            base.le.lib.removeSound(self.asset.name, force=True)
        elif self.asset.__class__.__name__ == "Terrain":
            base.le.lib.removeTerrain(self.asset.name, force=True)
        else:
            raise Exception("Unrecognized asset type")
        
        self.asset.refCount = self.oldAsset.refCount
        self.asset.numInScene = self.oldAsset.numInScene
        
        self.parent.removedAssets.append(self.oldAsset)
         
        self.Close()
        
    def onCancel(self, evt):
        self.canceled = True
        self.Close()
        
    def onSkip(self, evt):
        self.skipped = True
        self.Close()

    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        if self.skipped:
            return SKIP
        elif self.canceled:
            return CANCEL
        else:
            return OK
        
#dialog box to resolve file conflicts        
class FileCollisionDialog(wx.Dialog):
    def __init__(self, parent, id, error):
        wx.Dialog.__init__(self, parent, id, "Duplicate Filename", size=(300,300))
        self.parent = parent
        self.asset = error.asset
        self.error = error
        self.overwrite = None
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        msgTxt = 'A ' + self.asset.__class__.__name__.lower() + '  file already exists in the ' + \
'project directory as '+ error.destPath + '.  Choose a new filename or click ' + \
'overwrite to replace the old file.'
        
        message = wx.StaticText(self, -1, msgTxt)
        message.Wrap(self.GetSizeTuple()[0])
        
        split = self.asset.filename.getBasenameWoExtension().split('_')
        if split[-1].isdigit():
            suggestion = '_'.join(split[:-1]) + '_' + str(int(split[-1])+1)
        else:
            suggestion = self.asset.filename.getBasenameWoExtension() + '_2'
         
        suggestion += '.' + self.asset.filename.getExtension()
            
        self.fileInput = wx.TextCtrl(self, -1, suggestion)
        self.fileInput.Bind(wx.EVT_TEXT, self.onFileInput)
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.renameButton = wx.Button(self, -1, 'Rename')
        self.renameButton.Bind(wx.EVT_BUTTON, self.onRename)
        
        destFilename = Filename.fromOsSpecific(error.destPath)
        destFilename.makeRelativeTo(base.le.lib.projDir)
        
        overwriteButton = wx.Button(self, -1, 'Overwrite')
        overwriteButton.Bind(wx.EVT_BUTTON, self.onOverwrite)
        if destFilename in base.le.lib.filenameIndex:
            overwriteButton.Enable(False)
        
        cancelButton = wx.Button(self, -1, 'Cancel')
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        
        skipButton = wx.Button(self, -1, 'Skip')
        skipButton.Bind(wx.EVT_BUTTON, self.onSkip)
        if destFilename not in base.le.lib.filenameIndex:
            skipButton.Enable(False)
        #to make sure we don't allow this if they are importing a mesh when there is already
        #an actor of the same filename or vice-versa
        elif base.le.lib.filenameIndex[destFilename].__class__ != self.asset.__class__:
            skipButton.Enable(False)
        
        hSizer.Add(self.renameButton)
        hSizer.Add(overwriteButton)
        hSizer.Add(skipButton)
        hSizer.Add(cancelButton)
        
        sizer.Add(message)
        sizer.Add(self.fileInput, flag=wx.EXPAND)
        sizer.Add(hSizer)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
        self.canceled = False
        self.skipped = False
    
    def onFileInput(self, evt):
        iPoint = self.fileInput.GetInsertionPoint()
        self.fileInput.ChangeValue(Util.toFilename(self.fileInput.GetValue(), False))
        self.fileInput.SetInsertionPoint(iPoint)
    
        self.renameButton.Enable(self.fileInput.GetValue() != '')
    
    def onRename(self, evt):
        #to prevent problems if an asset needs to be renamed twice
        if hasattr(self.asset, 'sourceFile') and self.asset.sourceFile:
            self.asset.filename = Filename(self.asset.sourceFile)
        self.asset.sourceFile = Filename(self.asset.filename)
        self.asset.filename.setBasename(self.fileInput.GetValue())
        self.Close()
        
    def onOverwrite(self, evt):
        try:
            if not os.path.exists(os.path.join(Util.getTempDir(), 'removedAssets', self.asset.filename.getDirname())):
                os.makedirs(os.path.join(Util.getTempDir(), 'removedAssets', self.asset.filename.getDirname()))
            shutil.move(self.error.destPath, os.path.join(Util.getTempDir(), 'removedAssets', self.asset.filename.getDirname()))
        except Exception as e:
            print e
            dlg = wx.MessageDialog(self, "Could not overwrite file '" + self.error.destPath +\
            "'. Make sure it is not marked read only and try again",\
            caption="Permission Denied", style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
        
        self.Close()
        
    def onCancel(self, evt):
        self.canceled = True
        self.Close()
        
    def onSkip(self, evt):
        self.skipped = True
        self.Close()
        
    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        if self.canceled:
            return CANCEL
        elif self.skipped:
            return SKIP
        else:
            return OK
        
