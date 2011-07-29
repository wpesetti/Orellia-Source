import wx
from wx import xrc

from Util import copy_vfs
import Util

from direct.stdpy.file import *
import os.path, shutil
from ImportUI import DuplicateNameDialog, FileCollisionDialog, CANCEL, SKIP, OK
import Library
from pandac.PandaModules import Filename
from copy import copy

XRC_FILE = 'XRC/LibraryBrowserUI.xrc'

class LibraryBrowserUI(wx.Dialog):
    def __init__(self, parent, lib, libName):
        pre = wx.PreDialog()
        self.res = xrc.XmlResource(XRC_FILE)
        self.res.LoadOnDialog(pre, parent, 'dlgLibraryBrowser')
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_INIT_DIALOG, self.OnCreate)
        
        self.parent = parent
        self.lib = lib
        self.libName = libName
        
    def OnCreate(self, e):
        self.Unbind(wx.EVT_INIT_DIALOG)
        
        self.lblLibName = xrc.XRCCTRL(self, "lblLibName")
        self.notebook = xrc.XRCCTRL(self, "notebook")
        self.meshTab = xrc.XRCCTRL(self.notebook, "meshTab")
        self.listMeshes = xrc.XRCCTRL(self.meshTab, "listMeshes")
        self.textureTab = xrc.XRCCTRL(self.notebook, "textureTab")
        self.listTextures = xrc.XRCCTRL(self.textureTab, "listTextures")
        self.actorTab = xrc.XRCCTRL(self.notebook, "actorTab")
        self.listActors = xrc.XRCCTRL(self.actorTab, "listActors")
        self.animTab = xrc.XRCCTRL(self.notebook, "animTab")
        self.listAnims = xrc.XRCCTRL(self.animTab, "listAnims")
        self.shaderTab = xrc.XRCCTRL(self.notebook, "shaderTab")
        self.listShaders = xrc.XRCCTRL(self.shaderTab, "listShaders")
        self.soundTab = xrc.XRCCTRL(self.notebook, "soundTab")
        self.listSounds = xrc.XRCCTRL(self.soundTab, "listSounds")
        self.terrainTab = xrc.XRCCTRL(self.notebook, "terrainTab")
        self.listTerrains = xrc.XRCCTRL(self.terrainTab, "listTerrains")
        self.conversationTab = xrc.XRCCTRL(self.notebook, "conversationTab")
        self.listConversations = xrc.XRCCTRL(self.conversationTab, "listConversations")
        self.scriptTab = xrc.XRCCTRL(self.notebook, "scriptTab")
        self.listScripts = xrc.XRCCTRL(self.scriptTab, "listScripts")
        
        self.btnAddToLibrary = xrc.XRCCTRL(self, "btnAddToLibrary")
        self.btnAddToLibrary.Bind(wx.EVT_BUTTON, self.onAddToLibrary)
        
        self.btnClose = xrc.XRCCTRL(self, "btnClose")
        self.btnClose.Bind(wx.EVT_BUTTON, lambda x: self.Destroy())
        
        self.lblLibName.SetLabel(self.libName)
        
        ##make sure filenames in other library assets are complete so we can import them
        
        for t in self.lib.textures.values():
            t.filename = t.getFullFilename()
        for m in self.lib.meshes.values():
            m.filename = m.getFullFilename()
            
        for a in self.lib.animations.values():
            a.filename = a.getFullFilename()
            
        for a in self.lib.actors.values():
            a.filename = a.getFullFilename()
            
        for s in self.lib.shaders.values():
            s.filename = s.getFullFilename()
            
        for s in self.lib.sounds.values():
            s.filename = s.getFullFilename()
        
        for t in self.lib.terrains.values():
            t.filename = t.getFullFilename()
            
        for c in self.lib.conversations.values():
            c.filename = c.getFullFilename()
        
        for s in self.lib.scripts.values():
            s.filename = s.getFullFilename()
        
        ##Load all of the asset lists and thumbnails
        
        #Meshes
        meshThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.meshes.keys()):
            mesh = self.lib.meshes[name]
            try:
                thumb = mesh.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    meshThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    meshThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                meshThumbnails.Add(wx.Bitmap('models/mesh.jpg'))
        self.listMeshes.AssignImageList(meshThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.meshes.keys())):
            self.listMeshes.InsertImageStringItem(i, name, i)    
        
        #Textures
        texThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.textures.keys()):
            tex = self.lib.textures[name]
            try:
                thumb = tex.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    texThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    texThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                texThumbnails.Add(wx.Bitmap('default_thumb.jpg'))
        self.listTextures.AssignImageList(texThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.textures.keys())):
            self.listTextures.InsertImageStringItem(i, name, i)
            
        #Actors
        actorThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.actors.keys()):
            actor = self.lib.actors[name]
            try:
                thumb = actor.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    actorThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    actorThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                actorThumbnails.Add(wx.Bitmap('models/actor.jpg'))
        self.listActors.AssignImageList(actorThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.actors.keys())):
            self.listActors.InsertImageStringItem(i, name, i) 
            
        #Animations
        animThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.animations.keys()):
            anim = self.lib.animations[name]
            try:
                thumb = anim.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    animThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    animThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                animThumbnails.Add(wx.Bitmap('models/animation.jpg'))
        self.listAnims.AssignImageList(animThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.animations.keys())):
            self.listAnims.InsertImageStringItem(i, name, i)
            
        #Shaders
        shaderThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.shaders.keys()):
            shader = self.lib.shaders[name]
            try:
                thumb = shader.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    shaderThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    shaderThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                shaderThumbnails.Add(wx.Bitmap('models/shader.jpg'))
        self.listShaders.AssignImageList(shaderThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.shaders.keys())):
            self.listShaders.InsertImageStringItem(i, name, i)
            
        #Sounds
        soundThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.sounds.keys()):
            sound = self.lib.sounds[name]
            try:
                thumb = sound.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    soundThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    soundThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                soundThumbnails.Add(wx.Bitmap('models/sound.jpg'))
        self.listSounds.AssignImageList(soundThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.sounds.keys())):
            self.listSounds.InsertImageStringItem(i, name, i)     
    
        #Terrains
        terrainThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.terrains.keys()):
            terrain = self.lib.terrains[name]
            try:
                thumb = terrain.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    terrainThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    terrainThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                terrainThumbnails.Add(wx.Bitmap('default_thumb.jpg'))
        self.listTerrains.AssignImageList(terrainThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.terrains.keys())):
            self.listTerrains.InsertImageStringItem(i, name, i)
            
        #Conversations
        conversationThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.conversations.keys()):
            conversation = self.lib.conversations[name]
            try:
                thumb = conversation.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    conversationThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    conversationThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                conversationThumbnails.Add(wx.Bitmap('default_thumb.jpg'))
        self.listConversations.AssignImageList(conversationThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.conversations.keys())):
            self.listConversations.InsertImageStringItem(i, name, i)
            
        #Scripts
        scriptThumbnails = wx.ImageList(60, 60)
        for name in sorted(self.lib.scripts.keys()):
            script = self.lib.scripts[name]
            try:
                thumb = script.getThumbnail()
                if os.path.exists(thumb.toOsSpecific()):
                    scriptThumbnails.Add(wx.Bitmap(thumb.toOsSpecific()))
                else:   #to handle loading a bitmap from a multifile
                    f = open(thumb.toOsSpecific())
                    img = wx.ImageFromStream(f)
                    scriptThumbnails.Add(wx.BitmapFromImage(img))
                    
            except Exception as e:
                print e
                scriptThumbnails.Add(wx.Bitmap('default_thumb.jpg'))
        self.listScripts.AssignImageList(scriptThumbnails, wx.IMAGE_LIST_NORMAL)
        
        for i, name in enumerate(sorted(self.lib.scripts.keys())):
            self.listScripts.InsertImageStringItem(i, name, i)
    
    def onAddToLibrary(self, evt=None):
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
                
        if os.path.exists((Filename.fromOsSpecific(Util.getTempDir()) + '/removedAssets/').toOsSpecific()):
            shutil.rmtree((Filename.fromOsSpecific(Util.getTempDir()) + '/removedAssets').toOsSpecific())
        
        self.removedAssets = []
        page = self.notebook.GetPage(self.notebook.GetSelection())
        if page == self.meshTab:
            item = self.listMeshes.GetFirstSelected()
            if item == -1:
                return         
            name = self.listMeshes.GetItemText(item)
            mesh = self.lib.meshes[name]
        
            while True:
                try:
                    base.le.lib.checkMesh(mesh)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL:
                        self.restoreAssets()
                        return
                    elif result == SKIP:
                        if e.oldAsset.__class__.__name__ == 'Mesh':
                            self.restoreAssets()
                            return
                        mesh.textures.remove(e.newAsset)
                        mesh.textures.append(e.oldAsset)
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL:
                        self.restoreAssets()
                        return
                    elif result == SKIP:
                        if e.asset.__class__.__name__ == 'Mesh':
                            self.restoreAssets()
                            return
                        mesh.textures.remove(e.asset)
                        f = Filename.fromOsSpecific(e.destPath)
                        f.makeRelativeTo(base.le.lib.projDir)
                        mesh.textures.append(base.le.lib.filenameIndex[f])
                else:
                    break
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addMesh(mesh, True)

            if mesh.thumbnail:
                thumbnailPath = base.le.lib.projDir + '/Models/Thumbnails/'
                oldThumbnailPath = self.lib.projDir + mesh.thumbnail.getFullpath()
            
                copy_vfs(oldThumbnailPath.toOsSpecific(), thumbnailPath.toOsSpecific())
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        elif page == self.actorTab:
            item = self.listActors.GetFirstSelected()
            if item == -1:
                return         
            name = self.listActors.GetItemText(item)
            actor = self.lib.actors[name]
            anims = copy(actor.anims.values())
            
            for anim in anims:
                while True:
                    try:
                        base.le.lib.checkAnimation(anim)
                    except Library.DuplicateNameError as e:
                        dialog = DuplicateNameDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
                            return
                        elif result == SKIP:
                            anims.remove(e.newAsset)
                            anims.append(e.oldAsset)
                    except Library.FileCollisionError as e:
                        dialog = FileCollisionDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
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
                        elif result == SKIP:
                            if e.oldAsset.__class__.__name__ == 'Actor':
                                self.restoreAssets()
                                return
                            actor.textures.remove(e.newAsset)
                            actor.textures.append(e.oldAsset)
                    except Library.FileCollisionError as e:
                        dialog = FileCollisionDialog(self, -1, e)
                        result = dialog.ShowModal()
                        dialog.Destroy()
                        if result == CANCEL:
                            self.restoreAssets()
                        elif result == SKIP:
                            if e.asset.__class__.__name__ == 'Actor':
                                self.restoreAssets()
                                return
                            actor.textures.remove(e.asset)
                            f = Filename.fromOsSpecific(e.destPath)
                            f.makeRelativeTo(base.le.lib.projDir)
                            actor.textures.append(base.le.lib.filenameIndex[f])
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
                            return
                        actor.textures.remove(e.newAsset)
                        actor.textures.append(e.oldAsset)
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL:
                        self.restoreAssets()
                        return
                    elif result == SKIP:
                        if e.asset.__class__.__name__ == 'Actor':
                            self.restoreAssets()
                            return
                        actor.textures.remove(e.asset)
                        f = Filename.fromOsSpecific(e.destPath)
                        f.makeRelativeTo(base.le.lib.projDir)
                        actor.textures.append(base.le.lib.filenameIndex[f])
                else:
                        break
               
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            for anim in anims:
                base.le.lib.addAnimation(anim)
                        
            base.le.lib.addActor(actor, True)
            
            if actor.thumbnail:
                thumbnailPath = base.le.lib.projDir + '/Models/Thumbnails/'
                oldThumbnailPath = self.lib.projDir + actor.thumbnail.getFullpath()
            
                copy_vfs(oldThumbnailPath.toOsSpecific(), thumbnailPath.toOsSpecific())
            
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        elif page == self.textureTab:
            item = self.listTextures.GetFirstSelected()
            if item == -1:
                return         
            name = self.listTextures.GetItemText(item)
            texture = self.lib.textures[name]
        
            while True:
                try:
                    base.le.lib.checkTexture(texture)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)                    
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                else:
                    break
                    
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addTexture(texture,True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        elif page == self.animTab:
            item = self.listAnims.GetFirstSelected()
            if item == -1:
                return
            name = self.listAnims.GetItemText(item)
            anim = self.lib.animations[name]
            
            while True:
                try:
                    base.le.lib.checkAnimation(anim)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                else:
                    break
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))        
            base.le.lib.addAnimation(anim)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))            
            
        
        elif page == self.shaderTab:
            item = self.listShaders.GetFirstSelected()
            if item == -1:
                return
            name = self.listShaders.GetItemText(item)
            shader = self.lib.shaders[name]
            
            while True:
                try:
                    base.le.lib.checkShader(shader)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                else:
                    break
                    
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            base.le.lib.addShader(shader, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
        elif page == self.soundTab:
            item = self.listSounds.GetFirstSelected()
            if item == -1:
                return
            name = self.listSounds.GetItemText(item)
            sound = self.lib.sounds[name]
            
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
        
        elif page == self.terrainTab:
            item = self.listTerrains.GetFirstSelected()
            if item == -1:
                return
            name = self.listTerrains.GetItemText(item)
            terrain = self.lib.terrains[name]
            
            while True:
                try:
                    base.le.lib.checkTerrain(terrain)
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
            base.le.lib.addTerrain(terrain, True)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        elif page == self.conversationTab:
            item = self.listConversations.GetFirstSelected()
            if item == -1:
                return
            name = self.listConversations.GetItemText(item)
            conversation = self.lib.conversations[name]
            
            while True:
                try:
                    base.le.lib.checkConversation(conversation)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                else:
                    break
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))        
            base.le.lib.addConversation(conversation)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        elif page == self.scriptTab:
            item = self.listScripts.GetFirstSelected()
            if item == -1:
                return
            name = self.listScripts.GetItemText(item)
            script = self.lib.scripts[name]
            
            while True:
                try:
                    base.le.lib.checkScript(script)
                except Library.DuplicateNameError as e:
                    dialog = DuplicateNameDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                except Library.FileCollisionError as e:
                    dialog = FileCollisionDialog(self, -1, e)
                    result = dialog.ShowModal()
                    dialog.Destroy()
                    if result == CANCEL or result == SKIP:
                        self.restoreAssets()
                        return
                else:
                    break
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))        
            base.le.lib.addScript(script)
            base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        if not base.le.saved:
            base.le.fNeedToSave = True
            
        base.le.ui.libraryUI.update()
        base.le.ui.storyObjUI.update()
        
    #restores any assets that have been "deleted"(moved to temp folder) if we cancel an import
    #also restores assets that were removed from library
    def restoreAssets(self):
        #restore any files which were "deleted"
        for dir in ('Models', 'Textures', 'Shaders', 'Sounds', 'Conversations', 'Scripts'):
            d = os.path.join(Util.getTempDir(), 'removeAssets', dir)
            if os.path.exists(d):
                for file in os.listdir(d):
                    shutil.move(os.path.join(d, file), (base.le.lib.projDir + '/' + dir + '/').toOsSpecific())\
                    
        #add assets back into library
        for asset in self.removedAssets:
            base.le.lib.restoreAsset(asset)
            
        self.removedAssets = []
