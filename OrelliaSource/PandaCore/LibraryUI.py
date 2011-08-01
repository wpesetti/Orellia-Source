import wx
import os
import Library as LELibrary
import Util
from wx import xrc
from pandac.PandaModules import Filename
import subprocess
from ConversationEditor import *
import xml.dom.minidom # [antonjs 3/13] Added

from YesNoForAllDialog import *

RESOURCE_FILE = 'XRC/LibraryUI.xrc'

class LibraryUI(wx.Panel):
    def __init__(self, parent, id, editor):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(RESOURCE_FILE)
        self.res.LoadOnPanel(pre, parent, 'panelLibraryUI')
        self.PostCreate(pre)
        
        self.parent = parent
        self.editor = editor
        
        self.treeLibrary = xrc.XRCCTRL(self, "treeLibrary")
        self.thumbnail = xrc.XRCCTRL(self, "imgThumbnail")
        self.root = self.treeLibrary.AddRoot("Assets")
        self.lblInstanceCount = xrc.XRCCTRL(self, "lblInstanceCount")
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self.onRightClick)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.onBeginEditName)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onEndEditName)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectionChanged)
        
        self.meshes = self.treeLibrary.AppendItem(self.root, "Meshes")
        self.actors = self.treeLibrary.AppendItem(self.root, "Actors")
        self.animations = self.treeLibrary.AppendItem(self.root, "Animations")
        self.textures = self.treeLibrary.AppendItem(self.root, "Textures")
        self.shaders = self.treeLibrary.AppendItem(self.root, "Shaders")
        self.sounds = self.treeLibrary.AppendItem(self.root, "Sounds")
        self.terrains = self.treeLibrary.AppendItem(self.root, "Terrains")
        
    def buildTree(self):  
        for m in sorted(self.lib.meshes.keys()):
            self.treeLibrary.AppendItem(self.meshes, m)
        
        for a in sorted(self.lib.actors.keys()):
            self.treeLibrary.AppendItem(self.actors, a)
        
        for a in sorted(self.lib.animations.keys()):
            self.treeLibrary.AppendItem(self.animations, a)
        
        for t in sorted(self.lib.textures.keys()):
            self.treeLibrary.AppendItem(self.textures, t)
        
        for s in sorted(self.lib.shaders.keys()):
            self.treeLibrary.AppendItem(self.shaders, s)
            
        for s in sorted(self.lib.sounds.keys()):
            self.treeLibrary.AppendItem(self.sounds, s)
        
        for t in sorted(self.lib.terrains.keys()):
            self.treeLibrary.AppendItem(self.terrains, t)
        
               
    def update(self):
        self.lib = self.editor.lib
        for node in (self.meshes, self.actors, self.animations, self.textures, self.shaders, self.sounds, self.terrains):
            self.treeLibrary.DeleteChildren(node)
        self.buildTree()
        self.onSelectionChanged()
    
    def onSelectionChanged(self, evt=None):
        if not self.treeLibrary.GetSelections():
            item = None
        else:
            item = self.treeLibrary.GetSelections()[0]
        if item and item not in (self.root, self.meshes, self.actors, self.animations, self.textures, self.shaders, self.sounds, self.terrains):
            assetName = self.treeLibrary.GetItemText(item)
            parent = self.treeLibrary.GetItemParent(item)
            assetType = self.treeLibrary.GetItemText(parent)
            
            if assetType == "Meshes":
                asset = self.lib.meshes[assetName]
            elif assetType == "Textures":
                asset = self.lib.textures[assetName]
            elif assetType == "Actors":
                asset = self.lib.actors[assetName]
            elif assetType == "Animations":
                asset = self.lib.animations[assetName]
            elif assetType == "Shaders":
                asset = self.lib.shaders[assetName]
            elif assetType == "Sounds":
                asset = self.lib.sounds[assetName]
            elif assetType == "Terrains":
                asset = self.lib.terrains[assetName]    
                
            path = asset.getThumbnail().toOsSpecific()
            self.lblInstanceCount.SetLabel(str(asset.numInScene))
            try:
                self.thumbnail.SetBitmap(wx.Bitmap(path))
            except Exception as e:
                print e.message
            self.Refresh()
        else:
            self.thumbnail.SetBitmap(wx.Bitmap('default_thumb.jpg'))
            self.lblInstanceCount.SetLabel(str(0))
            self.Refresh()
                
             
        
    def onBeginDrag(self, evt):
        item = evt.GetItem()
        parent = self.treeLibrary.GetItemParent(item)
        if item not in (self.root, self.meshes, self.textures, self.actors, self.animations, self.shaders, self.sounds, self.terrains):
            
            txtData = wx.TextDataObject(\
            self.treeLibrary.GetItemText(parent) + '>' + self.treeLibrary.GetItemText(item))
            txtDropSource = wx.DropSource(self.treeLibrary)
            txtDropSource.SetData(txtData)
            txtDropSource.DoDragDrop(True)
            
    def onRightClick(self, evt):
        item = evt.GetItem()
        
        for x in (self.root, self.meshes, self.textures, self.actors, self.animations, self.shaders, self.sounds, self.terrains):
            if x in self.treeLibrary.GetSelections():
                return
        
        if len(self.treeLibrary.GetSelections()) > 1:
            menu = wx.Menu()
            it = wx.MenuItem(menu, wx.NewId(), "Remove... ")
            menu.AppendItem(it)
            menu.Bind(wx.EVT_MENU, lambda x : self.onRemove(x, item), it)
            
            self.PopupMenu(menu)
       
        else:
            if item and item not in (self.root, self.meshes, self.textures, self.actors, self.animations, self.shaders, self.sounds, self.terrains):
                menu = wx.Menu()
                it = wx.MenuItem(menu, wx.NewId(), "View/Edit Details...")
                menu.AppendItem(it)
                menu.Bind(wx.EVT_MENU, lambda x : self.onDetails(x, item), it)
                it = wx.MenuItem(menu, wx.NewId(), "Remove... ")
                menu.AppendItem(it)
                menu.Bind(wx.EVT_MENU, lambda x : self.onRemove(x, item), it)
                
                parent = self.treeLibrary.GetItemParent(item)
                if parent == self.meshes or parent == self.actors:
                    it = wx.MenuItem(menu, wx.NewId(), "Update Thumbnail from Main Viewport")
                    menu.AppendItem(it)
                    menu.Bind(wx.EVT_MENU, lambda x : self.onUpdateThumbnail(x, item), it)
                
                self.PopupMenu(menu)
    
    def onBeginEditName(self, evt):
        base.le.ui.bindKeyEvents(False)
        item = evt.GetItem()
        if item in (self.root, self.meshes, self.textures, self.actors, self.animations, self.shaders, self.sounds, self.terrains):
            evt.Veto()
        else:
            self.origName = self.treeLibrary.GetItemText(item)[:]
    
    def onEndEditName(self, evt):
        item = evt.GetItem()
        self.newName = Util.toAssetName(evt.GetLabel())
        if self.newName != evt.GetLabel() or self.newName == "":
            evt.Veto()
            if evt.GetLabel() != "":
                wx.MessageDialog(self, "Invalid Name", caption="Invalid Name",\
                style=wx.OK|wx.ICON_HAND).ShowModal()
        else:           
            parent = self.treeLibrary.GetItemParent(item)
            assetType = self.treeLibrary.GetItemText(parent)
            if self.newName != self.origName:
                try:
                    if assetType == "Meshes":
                        self.lib.renameMesh(self.origName, self.newName)
                    elif assetType == "Textures":
                        self.lib.renameTexture(self.origName, self.newName)
                    elif assetType == "Actors":
                        self.lib.renameActor(self.origName, self.newName)
                    elif assetType == "Animations":
                        self.lib.renameAnimation(self.origName, self.newName)
                    elif assetType == "Shaders":
                        self.lib.renameShader(self.origName, self.newName)
                    elif assetType == "Sounds":
                        self.lib.renameSound(self.origName, self.newName)
                    elif assetType == "Terrains":
                        self.lib.renameTerrain(self.origName, self.newName)
                        
                except LELibrary.DuplicateNameError:
                    d = wx.MessageDialog(self, "Name is already in use.",\
                    caption="Duplicate Name", style = wx.OK|wx.ICON_HAND)
                    d.ShowModal()
                    evt.Veto()
                else:
                    self.lib.saveToFile()
        base.le.ui.bindKeyEvents(True)
    
    def onDetails(self, evt, item):
        assetName = self.treeLibrary.GetItemText(item)
        parent = self.treeLibrary.GetItemParent(item)
        assetType = self.treeLibrary.GetItemText(parent)
        
        if assetType == "Meshes":
            asset = self.lib.meshes[assetName]
        elif assetType == "Textures":
            asset = self.lib.textures[assetName]
        elif assetType == "Actors":
            asset = self.lib.actors[assetName]
        elif assetType == "Animations":
            asset = self.lib.animations[assetName]
        elif assetType == "Shaders":
            asset = self.lib.shaders[assetName]
        elif assetType == "Sounds":
            asset = self.lib.sounds[assetName]
        elif assetType == "Terrains":
            asset = self.lib.terrains[assetName] 
              
        dlg = EditAssetUI(self, asset)
        updateNeeded = False
        if dlg.ShowModal() == wx.ID_OK:
            newAssetName = Util.toAssetName(dlg.txtAssetName.GetValue())
            if newAssetName != asset.name:
                try:
                    if assetType == "Meshes":
                        self.lib.renameMesh(asset.name, newAssetName)
                    elif assetType == "Textures":
                        self.lib.renameTexture(asset.name, newAssetName)
                    elif assetType == "Actors":
                        self.lib.renameActor(asset.name, newAssetName)
                    elif assetType == "Animations":
                        self.lib.renameAnimation(asset.name, newAssetName)
                    elif assetType == "Shaders":
                        self.lib.renameShader(asset.name, newAssetName)
                    elif assetType == "Sounds":
                        self.lib.renameSound(asset.name, newAssetName)
                    elif assetType == "Terrains":
                        self.lib.renameTerrain(asset.name, newAssetName)
                        
                except LELibrary.DuplicateNameError:
                    alert = wx.MessageDialog(self, "Name already in use.  Aborting operation.",\
                    caption="Duplicate Name", style=wx.OK|wx.ICON_HAND)
                    alert.ShowModal()
                    return
                else:
                    updateNeeded = True
                
            if dlg.txtNewFileLink.GetValue():
                dest = Filename.fromOsSpecific(dlg.txtNewFileLink.GetValue())
                dest.setDirname(asset.getFullFilename().getDirname())    
                if not os.path.exists(dest.toOsSpecific()):
                    try:
                        asset.relink(dlg.txtNewFileLink.GetValue())
                        updateNeeded = True
                    except IOError as e:
                        print e
                        alert = wx.MessageDialog(self, "Could not copy file to '" + e.filename + "'. Permission denied.",\
                        caption="File Error", style=wx.OK|wx.ICON_HAND)
                        alert.ShowModal()
                else:
                    destFilename = Filename(dest)
                    destFilename.makeRelativeTo(self.lib.projDir)
                    if destFilename in self.lib.filenameIndex:
                        if self.lib.filenameIndex[destFilename] != asset:
                            alert = wx.MessageDialog(self, "Cannot overwrite other asset named '" + self.lib.filenameIndex[destFilename].name + "'.",\
                            caption = "Cannot overwrite file", style=wx.OK|wx.ICON_HAND)
                            alert.ShowModal()                          
                            return
                            
                    alert = wx.MessageDialog(self, "Overwrite file: " + dest.toOsSpecific() + " ?",\
                    caption="Overwrite File?", style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                    if alert.ShowModal() == wx.ID_YES:
                        try:
                            asset.relink(dlg.txtNewFileLink.GetValue())
                            updateNeeded = True
                        except IOError as e:
                            print e
                            alert = wx.MessageDialog(self, "Could not copy file to '" + e.filename + "'. Permission denied.",\
                            caption="File Error", style=wx.OK|wx.ICON_HAND)
                            alert.ShowModal()
            if assetType == "Actors":
                if dlg.txtNewAnimLink.GetValue():
                    try:
                        # Create the animation asset
                        newAnim = Library.Animation(dlg.txtAnimName.GetValue(), Filename.fromOsSpecific(dlg.txtNewAnimLink.GetValue()))
                        self.editor.lib.addAnimation(newAnim)
                        # Add the animation asset to the actor's animations list
                        asset.anims[dlg.txtAnimName.GetValue()] = newAnim
                        updateNeeded = True
                    except IOError as e:
                        print e
                        alert = wx.MessageDialog(self, "Could not copy file to '" + e.filename + "'. Permission denied.",\
                        caption="File Error", style=wx.OK|wx.ICON_HAND)
                        alert.ShowModal()
        if updateNeeded:
            if self.editor.saved:
                dlg = wx.MessageDialog(self, "This will save the project.", style=wx.OK)
                dlg.ShowModal()
            self.editor.save()
            self.editor.load(self.editor.currentProj.filename, resetViews=False, setSaved=False)
            self.update()

        
    def onRemove(self, evt, item):
        assets = []
    
        for item in self.treeLibrary.GetSelections():
            assetName = self.treeLibrary.GetItemText(item)
            parent = self.treeLibrary.GetItemParent(item)
            assetType = self.treeLibrary.GetItemText(parent)
            assets.append( (assetName, assetType) )
        
        #comparison function to make sure that meshes ands actors
        #get removed before textures and animations
        def cmpAssets(x, y):
            if x[1] == y[1]:
                return cmp(x[0], y[0])
            else:
                if x[1] == "Meshes":
                    return -1
                elif x[1] == "Actors":
                    if y[1] == "Meshes":
                        return 1
                    else:
                        return -1
                elif y[1] == "Meshes":
                    return 1
                
                elif y[1] == "Actors":
                    return 1
                else:
                    return cmp(x[1], y[1])
            
        assets.sort(cmpAssets)
        
        msg = "Remove local files in addition to removing from library?"
        dialog = wx.MessageDialog(self, msg, caption = "Remove Asset", \
        style = wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        result = dialog.ShowModal()
        removeFile = result == wx.ID_YES
        if result == wx.ID_CANCEL:
            return
            
        removeAllMeshTextures = False
        removeAllActorTexsAndAnims = False
        
        ignoreAllMeshTextures = False
        ignoreAllActorTexsAndAnims = False
        
        success = False
        for assetName, assetType in assets:
            try:
                if assetType == "Meshes":
                    if removeAllMeshTextures:
                        removeTextures = True
                    elif ignoreAllMeshTextures:
                        removeTextures = False
                    else:
                        dlg = YesNoForAllDialog(self, "Remove textures associated with mesh '" + assetName + "' too?", checkBoxMessage = "Do this for all selected mesh assets.")
                        removeTextures, forAll = dlg.ShowModal()
                        if forAll:
                            if removeTextures:
                                removeAllMeshTextures = True
                            else:
                                ignoreAllMeshTextures = True
                        dlg.Destroy()
                    self.lib.removeMesh(assetName, removeFile, removeTextures=removeTextures)
                elif assetType == "Textures":
                    if assetName in self.lib.textures:  #make sure the asset hasn't already been removed
                        self.lib.removeTexture(assetName, removeFile)
                elif assetType == "Actors":
                    if removeAllActorTexsAndAnims:
                        removeOthers = True
                    elif ignoreAllActorTexsAndAnims:
                        removeOthers = False
                    else:
                        dlg = YesNoForAllDialog(self, "Remove textures and animations associated with actor '" + assetName + "' too?", checkBoxMessage = "Do this for all selected actor assets.")
                        removeOthers, forAll = dlg.ShowModal()
                        if forAll:
                            if removeOthers:
                                removeAllActorTexsAndAnims = True
                            else:
                                ignoreAllActorTexsAndAnims = True
                        dlg.Destroy()

                    self.lib.removeActor(assetName, removeFile, removeAnimsAndTextures=removeOthers)
                elif assetType == "Animations":
                    if assetName in self.lib.animations:    #make sure that asset hasn't already been removed
                        self.lib.removeAnimation(assetName, removeFile)
                elif assetType == "Shaders":
                    self.lib.removeShader(assetName, removeFile)
                elif assetType == "Sounds":
                    self.lib.removeSound(assetName, removeFile)
                elif assetType == "Terrains":
                    self.lib.removeTerrain(assetName, removeFile)

            except LELibrary.AssetInUseError as e:
                dlg = wx.MessageDialog(self, "The asset '" + e.asset.name + "' could not be removed because it is being used by the scene.",\
                caption = "Asset In Use", style = wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
            except LELibrary.AssetReferencedError as e:
                dlg = wx.MessageDialog(self, "The asset '" + e.asset.name + "' could not be removed because it is being referenced by another asset in the library.",\
                caption = "Could not Remove Asset", style = wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
            else:
                success = True

        if success:
            if self.editor.saved:
                dlg = wx.MessageDialog(self, "This will save the project.", style=wx.OK)
                dlg.ShowModal()
            self.editor.save()
            self.editor.load(self.editor.currentProj.filename, resetViews=False, setSaved=False)
            self.update()
    
    def onUpdateThumbnail(self, evt, item):
        if self.treeLibrary.GetItemParent(item) == self.meshes:
            asset = self.lib.meshes[self.treeLibrary.GetItemText(item)]
        elif self.treeLibrary.GetItemParent(item) == self.actors:
            asset = self.lib.actors[self.treeLibrary.GetItemText(item)]
        
        if asset.thumbnail:
            f = asset.getThumbnail()
        else:
            f = Filename(asset.getFullFilename().getDirname() + '/Thumbnails/' + asset.filename.getBasenameWoExtension() + '.jpg')
        camnode = self.editor.ui.perspView.cam.node()
        dr = camnode.getDisplayRegion(0)
        try:
            dr.saveScreenshot(f)
        except Exception:
            pass
        else:
            cwd = os.getcwd()
            os.chdir(Filename(f.getDirname()).toOsSpecific())
            subprocess.call(["image-resize","-x 60", "-y 60", "-g 1", "-o" + f.getBasename(), f.getBasename()])
            os.chdir(cwd)
            if not asset.thumbnail:
                asset.thumbnail = f
                asset.thumbnail.makeRelativeTo(asset.projDir)
    
EDIT_ASSET_RESOURCE = "XRC/dlgAssetUpdate.xrc"
EDIT_ACTOR_ASSET_RESOURCE = "XRC/dlgActorAssetUpdate.xrc"
 
class EditAssetUI(wx.Dialog):
        def __init__(self, parent, asset):
            pre = wx.PreDialog()
            if isinstance(asset, LELibrary.Actor):
                self.res = xrc.XmlResource(EDIT_ACTOR_ASSET_RESOURCE)
                self.res.LoadOnDialog(pre, parent, 'dlgEditActorAsset')
            else:
                self.res = xrc.XmlResource(EDIT_ASSET_RESOURCE)
                self.res.LoadOnDialog(pre, parent, 'dlgEditAsset')
            self.PostCreate(pre)
            
            self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
            
            self.parent = parent
            self.asset = asset
            self.assetType = self.asset.__class__.__name__
            
        def OnCreate(self, e):
            self.Unbind(wx.EVT_INIT_DIALOG)
            
            self.mainPanel = xrc.XRCCTRL(self, "mainPanel")
            self.txtAssetName = xrc.XRCCTRL(self.mainPanel, "txtAssetName")
            self.btnEditName = xrc.XRCCTRL(self.mainPanel, "btnEditName")
            self.lblFilepath = xrc.XRCCTRL(self.mainPanel, "lblFilepath")
            self.txtFilepath = xrc.XRCCTRL(self.mainPanel, "txtFilepath")
            self.txtNewFileLink = xrc.XRCCTRL(self.mainPanel, "txtNewFileLink")
            self.btnReplaceAsset = xrc.XRCCTRL(self.mainPanel, "btnReplaceAsset")               
            
            self.txtAssetName.SetValue(self.asset.name)
            self.txtFilepath.SetLabel(self.asset.filename.getFullpath())
            
            self.btnEditName.Bind(wx.EVT_BUTTON, self.onEditName)
            self.btnReplaceAsset.Bind(wx.EVT_BUTTON, self.onReplaceAsset)
            self.txtAssetName.Bind(wx.EVT_TEXT, self.onNameInput)
            
            if isinstance(self.asset, LELibrary.Actor):
                self.txtNewAnimLink = xrc.XRCCTRL(self.mainPanel, "txtNewAnimLink")
                self.btnAddAnim = xrc.XRCCTRL(self.mainPanel, "btnAddAnim")
                self.btnAddAnim.Bind(wx.EVT_BUTTON, self.onAddAnim)
                self.txtAnimName = xrc.XRCCTRL(self.mainPanel, "txtAnimName")
                self.txtAnimName.Enable(False)
                self.txtAnimName.Bind(wx.EVT_TEXT, self.onAnimNameInput)
        
        def onNameInput(self, evt):
            iPoint = self.txtAssetName.GetInsertionPoint()
            self.txtAssetName.ChangeValue(Util.toAssetName(self.txtAssetName.GetValue(), False))
            self.txtAssetName.SetInsertionPoint(iPoint)
        
        def onAnimNameInput(self, evt):
            iPoint = self.txtAnimName.GetInsertionPoint()
            self.txtAnimName.ChangeValue(Util.toAssetName(self.txtAnimName.GetValue(), False))
            self.txtAnimName.SetInsertionPoint(iPoint)
        
        def onEditName(self, evt):
            self.txtAssetName.Enable(True)
            self.btnEditName.Enable(False)
        
        def onReplaceAsset(self, evt):
            fileType = "*.*"
        
            if self.assetType == "Mesh" or self.assetType == "Actor" or self.assetType == "Animation":
                fileType = "Egg files (*.egg;*.egg.pz)|*.egg;*.egg.pz"
            elif self.assetType == "Texture" or self.assetType == "Terrain":
                fileType = "Texture files (*.png;*.jpg;*.jpeg;*.bmp;*.rgb;*.tif;*.avi;*.mpg;*.mpeg;*.dds)|*.png;*.jpg;*.jpeg;*.bmp;*.rgb;*.tif;*.avi;*.mpg;*.mpeg;*.dds"
            elif self.assetType == "Shader":
                fileType = "Shader files (*.sha;*.cg)|*.sha;*.cg" 
            elif self.assetType == "Sound":
                fileType = "Sound files (*.wav;*.mp3;*.aiff;*.ogg) | *.wav;*.mp3;*.aiff;*.ogg"
        
            dlg = wx.FileDialog(self, "Select a " +self.assetType+" file", os.getcwd(), "", fileType, wx.FD_OPEN)
            
            if dlg.ShowModal() == wx.ID_OK:
                self.txtNewFileLink.SetValue(dlg.GetPath())
        
        def onAddAnim(self, evt):
            fileType = "Egg files (*.egg;*.egg.pz)|*.egg;*.egg.pz"
            
            dlg = wx.FileDialog(self, "Select an Animation file", os.getcwd(), "", fileType, wx.FD_OPEN)
            
            if dlg.ShowModal() == wx.ID_OK:
                self.txtNewAnimLink.SetValue(dlg.GetPath())
            
                self.txtAnimName.Enable(True)
                path = dlg.GetPath()
                fName = Filename.fromOsSpecific(path)
                self.txtAnimName.SetValue(fName.getBaseNameWoExtension())

        def ShowModal(self):
            base.le.ui.bindKeyEvents(False)
            result = wx.Dialog.ShowModal(self)
            base.le.ui.bindKeyEvents(True)
            return result
            
PANDA_OBJS_FILE = 'XRC/PandaObjUI.xrc'

class PandaObjUI(wx.Panel):
    def __init__(self, parent, id):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(PANDA_OBJS_FILE)
        self.res.LoadOnPanel(pre, parent, 'panelPandaObjUI')
        self.PostCreate(pre)
        
        self.parent = parent

        self.treePandaObj = xrc.XRCCTRL(self, "treePandaObj")
        self.root = self.treePandaObj.AddRoot("Panda Objects")
        self.emptyNode = self.treePandaObj.AppendItem(self.root, "Empty Node")
        self.lights = self.treePandaObj.AppendItem(self.root, "Lights")
        self.ambient = self.treePandaObj.AppendItem(self.lights, "Ambient")
        self.directional = self.treePandaObj.AppendItem(self.lights, "Directional")
        self.point = self.treePandaObj.AppendItem(self.lights, "Point")
        self.spot = self.treePandaObj.AppendItem(self.lights, "Spot")
        self.cameras = self.treePandaObj.AppendItem(self.root, "Cameras")
        self.orthographic = self.treePandaObj.AppendItem(self.cameras, "Orthographic")
        self.perspective = self.treePandaObj.AppendItem(self.cameras, "Perspective")
        
        self.colliders = self.treePandaObj.AppendItem(self.root, "Colliders")
        self.sphere = self.treePandaObj.AppendItem(self.colliders, "Collision Sphere")
        self.box = self.treePandaObj.AppendItem(self.colliders, "Collision Box")
        self.plane = self.treePandaObj.AppendItem(self.colliders, "Collision Plane")
        
        self.rope = self.treePandaObj.AppendItem(self.root, "Rope")
        
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag)
    
    def onBeginDrag(self, evt):
        item = evt.GetItem()
        #check that item should be draggable
        if item not in (self.root, self.lights, self.cameras, self.colliders):
            txtData = wx.TextDataObject(\
            'PandaObject' + '>' + self.treePandaObj.GetItemText(item))
            txtDropSource = wx.DropSource(self.treePandaObj)
            txtDropSource.SetData(txtData)
            txtDropSource.DoDragDrop(True)

STORY_OBJS_FILE = 'XRC/StoryObjUI.xrc'
            
class StoryObjUI(wx.Panel):
    def __init__(self, parent, id, editor):
        pre = wx.PrePanel()
        self.res = xrc.XmlResource(STORY_OBJS_FILE)
        self.res.LoadOnPanel(pre, parent, 'panelStoryObjUI')
        self.PostCreate(pre)
        
        self.parent = parent
        self.editor = editor

        self.treeStoryObj = xrc.XRCCTRL(self, "treeStoryObj")
        self.root = self.treeStoryObj.AddRoot("Story Objects")        
        self.scripts = self.treeStoryObj.AppendItem(self.root, "Scripts")
        self.conversations = self.treeStoryObj.AppendItem(self.root, "Conversations")
        
        self.thumbnail = xrc.XRCCTRL(self, "imgThumbnail")
        self.lblInstanceCount = xrc.XRCCTRL(self, "lblInstanceCount")
        #self.quests = self.treePandaObj.AppendItem(self.root, "Quests")
        
        
        #self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag)
        #self.Bind(wx.EVT_TREE_ITEM_MENU, self.onRightClick)
        #self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.onBeginEditName)
        #self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onEndEditName)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectionChanged)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self.onRightClick)
    
    def onBeginDrag(self, evt):
        item = evt.GetItem()
        #check that item should be draggable
        if item not in (self.root, self.lights, self.cameras, self.colliders):
            txtData = wx.TextDataObject(\
            'StoryObject' + '>' + self.treePandaObj.GetItemText(item))
            txtDropSource = wx.DropSource(self.treePandaObj)
            txtDropSource.SetData(txtData)
            txtDropSource.DoDragDrop(True)
            
    def buildTree(self):
        for s in sorted(self.lib.scripts.keys()):
            self.treeStoryObj.AppendItem(self.scripts, s)
        for c in sorted(self.lib.conversations.keys()):
            self.treeStoryObj.AppendItem(self.conversations, c)
        
               
    def update(self):
        self.lib = self.editor.lib
        for node in (self.scripts, self.conversations):
            self.treeStoryObj.DeleteChildren(node)
        self.buildTree()
        self.onSelectionChanged()
        
    def onSelectionChanged(self, evt=None):
        if not self.treeStoryObj.GetSelections():
            item = None
        else:
            item = self.treeStoryObj.GetSelections()[0]
        if item and item not in (self.scripts, self.conversations, self.root):
            assetName = self.treeStoryObj.GetItemText(item)
            parent = self.treeStoryObj.GetItemParent(item)
            assetType = self.treeStoryObj.GetItemText(parent)
            
            #TO DO: Take the journal Entries out
            if assetType == "Scripts":
                asset = self.lib.scripts[assetName]
            elif assetType == "Conversations":
                asset = self.lib.conversations[assetName]
                  
                
            path = asset.getThumbnail().toOsSpecific()
            self.lblInstanceCount.SetLabel(str(asset.numInScene))
            try:
                self.thumbnail.SetBitmap(wx.Bitmap(path))
            except Exception as e:
                print e.message
            self.Refresh()
        else:
            self.thumbnail.SetBitmap(wx.Bitmap('default_thumb.jpg'))
            self.lblInstanceCount.SetLabel(str(0))
            self.Refresh()
    
    
    def onRightClick(self, evt):
        item = evt.GetItem()
        
        for x in (self.root ,self.scripts, self.conversations) :
            if x in self.treeStoryObj.GetSelections():
                return
        
        if len(self.treeStoryObj.GetSelections()) > 1:
            menu = wx.Menu()
            it = wx.MenuItem(menu, wx.NewId(), "Remove... ")
            menu.AppendItem(it)
            menu.Bind(wx.EVT_MENU, lambda x : self.onRemove(x, item), it)
            
            self.PopupMenu(menu)
        else:
            if item and item not in (self.root, self.conversations, self.scripts):
                parent = self.treeStoryObj.GetItemParent(item)
                if parent == self.conversations:
                    menu = wx.Menu()
                    it = wx.MenuItem(menu, wx.NewId(), "Open in Editor...")
                    menu.AppendItem(it)
                    menu.Bind(wx.EVT_MENU, lambda x : self.onOpenConvoEditor(x, item), it)
                    it = wx.MenuItem(menu, wx.NewId(), "Remove... ")
                    menu.AppendItem(it)
                    menu.Bind(wx.EVT_MENU, lambda x : self.onRemove(x, item), it)
                    self.PopupMenu(menu)
    
    
    def onRemove(self, evt, item):
        assets = []
        
        for item in self.treeStoryObj.GetSelections():
            assetName = self.treeStoryObj.GetItemText(item)
            parent = self.treeStoryObj.GetItemParent(item)
            assetType = self.treeStoryObj.GetItemText(parent)
            assets.append( (assetName, assetType) )
        
        for name, type in assets:
            if type == "Conversations":
                self.lib.removeConversation(name)
        
        self.update()
        
    
    def onOpenConvoEditor(self, x, item):
        convoKey = self.treeStoryObj.GetItemText(item)
        #print "treeStoryObj type: %s" %(type(self.treeStoryObj))
        #print 'convo key: %s' %(convoKey)
        if convoKey in self.lib.conversations:
            convoFilename = Filename(self.editor.lib.conversations[convoKey].getFullFilename())
            f = open(convoFilename.toOsSpecific())
            doc = xml.dom.minidom.parse(f)
            root = doc.documentElement
            convo = Conversation.decode(doc)
            f.close()
        else:
            convo = None
        editor = ConversationEditor(self, self.editor, convo, convoKey)