import xml.dom.minidom
import os
import subprocess
import stat
import shutil
from pandac.PandaModules import *

from direct.stdpy.file import *

from Util import copy_vfs

#Manages all of the assets in the project directory
class Library:
    def __init__(self,projDir):
        self.projDir=projDir
        #if library exists, load it
        #if not, create a new one
        
        #dictionaries for each asset type mapping name to asset object
        self.meshes = {}
        self.textures = {}
        self.actors = {}
        self.animations = {}
        self.shaders = {}
        self.sounds = {}
        self.terrains = {}
        self.journalEntries = {}
        self.conversations = {}
        self.scripts = {}
        #script types
        self.conditionScripts = {}
        self.actionScripts = {}
        
        
        self.filenameIndex = {} #maps filenames to assets
        
        try:
            f = open(os.path.join(projDir.toOsSpecific(),"lib.index"))
            self.decode(f)
            f.close()
        except IOError:
            print 'creating new library'
    
    #adds a sound asset to the library including copying file to project directory
    def addSound(self, sound, saveAfter= False, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + sound.name in self.sounds:
            raise DuplicateNameError(prefix + sound.name, self.sounds[prefix + sound.name], sound)
        
        sound.projDir = self.projDir
        
        dest = 'Sounds/'
        if otherName:
            dest += otherName + '/'
        
        if hasattr(sound, 'sourceFile'):
            sound.moveTo(dest, self.projDir, source=sound.sourceFile)
        else:
            sound.moveTo(dest,self.projDir)
        
        sound.name = prefix + sound.name
        self.sounds[sound.name] = sound
        self.filenameIndex[sound.filename] = sound
                    
        if saveAfter:
            self.saveToFile()
    def removeSound(self, name, delFile=True, force=False):
        if not force:
            if self.sounds[name].numInScene != 0:
                raise AssetInUseError(self.sounds[name])
        
        if delFile:
            toDel = self.sounds[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
            except OSError as e:
                print e
        
        self.sounds[name].onRemove()
        del self.filenameIndex[self.sounds[name].filename]
        del self.sounds[name]
    
    #checks to see if an exception will be raised by adding a sound to the library
    def checkSound(self, sound, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + sound.name in self.sounds:
            raise DuplicateNameError(prefix + sound.name, self.sounds[prefix + sound.name], sound)
        
        folder = 'Sounds/'
        if otherName:
            folder += otherName + '/'
        
        dest = (self.projDir + '/' + folder + sound.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, sound.filename.toOsSpecific(), sound)
    
    def renameSound(self, oldName, newName):
        if newName in self.sounds:
            raise DuplicateNameError(newName, self.sounds[newName], self.sounds[oldName])
            
        sound = self.sounds[oldName]
        sound.name = newName
        del self.sounds[oldName]
        self.sounds[newName] = sound
        
    #adds an asset to the library including copying file to project directory
    def genericAdd(self,list, asset, destinationFile, saveAfter= False, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + asset.name in list:
            raise DuplicateNameError(prefix + asset.name, list[prefix + asset.name], asset)
        
        asset.projDir = self.projDir
        
        dest = destinationFile#'Journal_Entries/'
        if otherName:
            dest += otherName + '/'
        
        if hasattr(asset, 'sourceFile'):
            asset.moveTo(dest, self.projDir, source=asset.sourceFile)
        else:
            asset.moveTo(dest,self.projDir)
        
        asset.name = prefix + asset.name
        list[asset.name] = asset
        self.filenameIndex[asset.filename] = asset
                    
        if saveAfter:
            self.saveToFile()
            
    #removes the asset with "name" name and delete it from the list          
    def genericRemove(self, list, name, delFile = True, force = False ):
        if not force:
            if list[name].numInScene != 0:
                raise AssetInUseError(list[name])
        
        if delFile:
            toDel = list[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
            except OSError as e:
                print e
        
        #print "Name in genericRemove", name
        list[name].onRemove()
        del self.filenameIndex[list[name].filename]
        del list[name]
    
    #checks to see if an exception will be raised by adding a sound to the library
    def genericCheck(self, list, asset, folderName, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + asset.name in list:
            raise DuplicateNameError(prefix + asset.name, list[prefix + asset.name], asset)
        
        folder = folderName
        if otherName:
            folder += otherName + '/'
        
        dest = (self.projDir + '/' + folder + asset.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, asset.filename.toOsSpecific(), asset)
    
    def genericRename(self,list,oldName, newName):
        if newName in list:
            raise DuplicateNameError(newName, list[newName], list[oldName])
            
        asset = list[oldName]
        asset.name = newName
        del list[oldName]
        list[newName] = asset

    #adds a journalEntry asset to the library including copying file to project directory
    def addJournalEntry(self, journalEntry, saveAfter= False, otherName=""):
        self.genericAdd(self.journalEntries, journalEntry,'Journal_Entries/', saveAfter, otherName)
    
    
        
    def removeJournalEntry(self, name, delFile=True, force=False):
        self.genericRemove(self.journalEntries,name, delFile, force)
            
    
    def checkJournalEntry(self, journalEntry, otherName = ""):
        self.genericCheck(self.journalEntries,journalEntry, 'Journal_Entries/', otherName)
    
        
    def renameJournalEntry(self, oldName, newName):
        self.genericRename(self.journalEntries, oldName, newName)
    
    def processScriptType(self, script):
        #filename = script#self.editor.lib.scripts[script].getFullFilename()
        filename = script.filename
        #print filename
        if hasattr(script, 'sourceFile'):
            script.sourceFile
            filename = Filename(script.sourceFile)
        else:
            if not exists(filename.toOsSpecific()):
                filename = self.projDir + '/' + filename.getFullpath()
        #print filename
        scriptFileStream = open(filename.toOsSpecific())
        
        lines = scriptFileStream.readlines()
        scriptFileStream.close()
        
        mainLine = None
        mainLineSpaceCount = 0
        mainNestedFuncQueue = [] #(Holds the space counts)
        isConditionScript = False
        for line in lines:
            strippedLine = line.strip()
            if(strippedLine.startswith("#")):
               continue
            if(strippedLine.startswith("def main")):
                mainLine = line
                mainLineSpaceCount = len(mainLine)-len(mainLine.lstrip())
                continue
                    
            if(mainLine):
                #print line
                spaceCount = len(line)-len(line.lstrip())
                #print "spaceCount", spaceCount, " ", mainLineSpaceCount
                #if mainline finishes, 
                #no need to check they type of function, it doesn't return anything.
                if(spaceCount <= mainLineSpaceCount):
                    break    
                if(strippedLine.startswith("def")):
                    mainNestedFuncQueue.append(spaceCount)
                    continue       
                if(len(mainNestedFuncQueue) == 0): # if there is no nested function that means the return is main's return
                    if(spaceCount > mainLineSpaceCount and strippedLine.startswith("return")):
                         #add it to the condition list because main returns something
                         isConditionScript = True
                else:
                    #if there is a line that is indented 
                    #less or equal distance as latest def,
                    #that means function definition is ended
                    if(spaceCount < mainNestedFuncQueue[len(mainNestedFuncQueue)-1]):
                        mainNestedfuncQueue.pop()
            
        #if there is no mainLine then this is not a proper script        
        if(mainLine == None):
             print "ERROR: Script: \"", script.name, " doesn't have a mainLine"
             return False
        else:
             if(isConditionScript):
                 self.conditionScripts[script.name] = 0
             else:
                 self.actionScripts[script.name] = 0
             return True        
                
        
    #adds a script asset to the library including copying file to project directory
    def addScript(self, script, saveAfter= False, otherName=""):
        if(self.processScriptType(script)==False):
            return 
        self.genericAdd(self.scripts, script,'Scripts/', saveAfter, otherName)
       
    def removeScript(self, name, delFile=True, force=False):
        self.genericRemove(self.scripts,name, delFile, force)
        if(self.actionScripts.has_key(name)):
            del self.actionScripts[name]
        elif(self.conditionScripts.has_key(name)):
            del self.conditionScripts[name]
            
    
    def checkScript(self, script, otherName = ""):
        self.genericCheck(self.scripts,script, 'Scripts/', otherName)
    
        
    def renameScript(self, oldName, newName):
        self.genericRename(self.scripts, oldName, newName)
        if(self.actionScripts.has_key(oldName)):
            del self.actionScripts[oldName]
            self.actionScripts[newName]
        elif(self.conditionScripts.has_key(oldName)):
            del self.conditionScripts[oldName]
            self.conditionScripts[newName]
    
    
    #adds a conversation asset to the library including copying file to project directory
    def addConversation(self, convo, saveAfter= False, otherName=""):
        self.genericAdd(self.conversations, convo, 'Conversations/', saveAfter, otherName)
        
    def removeConversation(self, name, delFile=True, force=False):
        self.genericRemove(self.conversations, name, delFile, force)
            
    
    def checkConversation(self, convo, otherName = ""):
        self.genericCheck(self.conversations, convo, 'Conversations/', otherName)
    
        
    def renameConversation(self, oldName, newName):
        self.genericRename(self.conversations, oldName, newName)
        
    
    #add a mesh to the library including copying all files and fixing texture paths
    def addMesh(self,mesh,saveAfter=False, addTextures=True, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + mesh.name in self.meshes:
            raise DuplicateNameError(prefix + mesh.name, self.meshes[prefix + mesh.name], mesh)
        
        if otherName:
            oldProjDir = mesh.projDir
        
        mesh.projDir = self.projDir
        
        if addTextures:
            for tex in mesh.getTextures():
                self.addTexture(tex, False, otherName=otherName)
                tex.refCount += 1
        dest = 'Models/'
        if otherName:
            dest+= otherName + '/'
        if hasattr(mesh, 'sourceFile'):
            mesh.moveTo(dest, self.projDir, source=mesh.sourceFile)
        else:
            mesh.moveTo(dest,self.projDir)
        
        mesh.fixTexturePaths(otherName)
        mesh.name = prefix + mesh.name
        self.meshes[mesh.name] = mesh
        
        #copy thumbnail from other project directory
        if otherName and mesh.thumbnail:
            newThumbnailDir = Filename(dest + 'Thumbnails/')
            if not os.path.exists((self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific()):
                os.makedirs((self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific())
            try:
                copy_vfs((oldProjDir + mesh.thumbnail.getFullpath()).toOsSpecific(), (self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific())
            except Exception as e:
                print e
                mesh.thumbnail = None
            else:
                mesh.thumbnail = newThumbnailDir + mesh.thumbnail.getBasename()
                path = (self.projDir + '/' + mesh.thumbnail.getFullpath()).toOsSpecific()
                fileAtt = os.stat(path)[0]
                if (not fileAtt & stat.S_IWRITE):
                    os.chmod(path, stat.S_IWRITE)
                
        
        self.filenameIndex[mesh.filename] = mesh
        
        if saveAfter:
            self.saveToFile()
    
    #used to check if adding a mesh to the library will raise an exception
    def checkMesh(self, mesh, addTextures=True, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + mesh.name in self.meshes:
            raise DuplicateNameError(prefix + mesh.name, self.meshes[prefix + mesh.name], mesh)
        folder = 'Models/'
        if otherName:
            folder += otherName + '/'
        dest =(self.projDir + '/' + folder + mesh.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, mesh.filename.toOsSpecific(), mesh)
            
        if addTextures:
            for tex in mesh.getTextures():
                self.checkTexture(tex, otherName=otherName)
    
    #used to check if adding a texture to the library will raise an exception
    def checkTexture(self, texture, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + texture.name in self.textures:
            if texture == self.textures[prefix + texture.name]:
                return
            else:
                raise DuplicateNameError(prefix + texture.name, self.textures[prefix + texture.name], texture)
            
        #check that the texture exists (to find broken texture paths in egg, not necessary when importing from other library)
        if hasattr(texture, 'sourceFile'):
            path = texture.sourceFile
        else:
            path = texture.filename
        if not otherName and not exists(path.toOsSpecific()):
            raise TextureNotFoundError(path)
            
        folder = 'Textures/'
        if otherName:
            folder+= otherName + '/'
        dest =(self.projDir + '/' + folder + texture.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, texture.filename.toOsSpecific(), texture)           
    
    def checkTerrain(self, terrain, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + terrain.name in self.terrains:
            raise DuplicateNameError(prefix + terrain.name, self.terrains[prefix + terrain.name], terrain)
            
        #check that the terrain exists (to find broken terrain paths in egg, not necessary when importing from other library)
        if hasattr(terrain, 'sourceFile'):
            path = terrain.sourceFile
        else:
            path = terrain.filename
        if not otherName and not exists(path.toOsSpecific()):
            raise TextureNotFoundError(path)
        
        folder = 'Textures/'
        if otherName:
            folder+= otherName + '/'
        dest =(self.projDir + '/' + folder + terrain.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, terrain.filename.toOsSpecific(), terrain)
        
    #removes a mesh from the library and deletes the file
    def removeMesh(self, name, delFile=True, force=False, removeTextures=False):
        if not force:
            if self.meshes[name].numInScene != 0:
                raise AssetInUseError(self.meshes[name])
        
        if delFile:
            toDel = self.meshes[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
                if toDel.thumbnail:
                    os.remove(toDel.getThumbnail().toOsSpecific())
            except OSError as e:
                print e
        
        self.meshes[name].onRemove()
        
        if removeTextures:
            for tex in self.meshes[name].getTextures():
                if tex.numInScene == 0 and tex.refCount == 0:
                    self.removeTexture(tex.name, delFile=delFile)
        
        del self.filenameIndex[self.meshes[name].filename]
        del self.meshes[name]
    
    #removes a texture from the library and delete the file
    def removeTexture(self, name, delFile=True, force=False):
        if not force:
            if self.textures[name].numInScene != 0:
                raise AssetInUseError(self.textures[name])
            
            if self.textures[name].refCount != 0:
                raise AssetReferencedError(self.textures[name])
    
        if delFile:
            toDel = self.textures[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
                if toDel.thumbnail:
                    os.remove(toDel.getThumbnail().toOsSpecific())
            except OSError as e:
                print e
        
        self.textures[name].onRemove()
        
        del self.filenameIndex[self.textures[name].filename]
        del self.textures[name]
    
    def removeTerrain(self, name, delFile=True, force=False):
        if not force:
            if self.terrains[name].numInScene != 0:
                raise AssetInUseError(self.terrains[name])
            
            if self.terrains[name].refCount != 0:
                raise AssetReferencedError(self.terrains[name])
    
        if delFile:
            toDel = self.terrains[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
                if toDel.thumbnail:
                    os.remove(toDel.getThumbnail().toOsSpecific())
            except OSError as e:
                print e
        
        self.terrains[name].onRemove()
        
        del self.filenameIndex[self.terrains[name].filename]
        del self.terrains[name]
    #add a texture to the library and copy it to the project directory
    def addTexture(self, texture,saveAfter=False, otherName=""):  
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + texture.name in self.textures:
            #ignore if already in library
            if texture == self.textures[prefix + texture.name]:
                return
            else:
                raise DuplicateNameError(prefix + texture.name, self.textures[texture.name], texture)
        
        if hasattr(texture, 'sourceFile'):
            path = texture.sourceFile
        else:
            path = texture.filename
        if not exists(path.toOsSpecific()):
            print 'ERROR:Texture not found: ' + path.toOsSpecific()
            raise TextureNotFoundError(path)
        
        if hasattr(texture, 'projDir') and texture.projDir:
            oldProjDir = texture.projDir + '/'
        
        texture.projDir = self.projDir
        dest = 'Textures/'
        if otherName:
            dest += otherName + '/'
            
        if hasattr(texture, 'sourceFile'):
            texture.moveTo(dest, self.projDir, source=texture.sourceFile)
        else:
            texture.moveTo(dest, self.projDir)
        
        texture.name = prefix + texture.name
        self.textures[texture.name] = texture
        
        if not texture.isCubeMap():
            if not otherName and not texture.thumbnail:
                if not os.path.exists((self.projDir + '/' + dest +'/Thumbnails').toOsSpecific()):
                    os.makedirs((self.projDir + '/' + dest + '/Thumbnails').toOsSpecific())
                cwd = os.getcwd()
                os.chdir((self.projDir + '/' + dest).toOsSpecific())
                thumbnailPath = Filename('Thumbnails/' + texture.filename.getBasename())
                subprocess.call(["image-resize","-x 60", "-y 60", "-g 1", "-o" + thumbnailPath.toOsSpecific(), texture.filename.getBasename()])
                os.chdir(cwd)
                texture.thumbnail = Filename(dest + thumbnailPath.getFullpath())
            elif texture.thumbnail:
                newThumbnailDir = Filename(dest + '/' + 'Thumbnails/')
                if not os.path.exists((self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific()):
                    os.makedirs((self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific())
                try:
                    copy_vfs((oldProjDir + texture.thumbnail.getFullpath()).toOsSpecific(), (self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific())
                except Exception as e:
                    print e
                    texture.thumbnail = None
                else:
                    texture.thumbnail = newThumbnailDir + texture.thumbnail.getBasename()
                    path = (self.projDir + '/' + texture.thumbnail.getFullpath()).toOsSpecific()
                    fileAtt = os.stat(path)[0]
                    if (not fileAtt & stat.S_IWRITE):
                        os.chmod(path, stat.S_IWRITE)
                
        
        self.filenameIndex[texture.filename] = texture
        
        if saveAfter:
            self.saveToFile()
            
    def addTerrain(self, terrain,saveAfter=False, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + terrain.name in self.terrains:
            raise DuplicateNameError(prefix + terrain.name, self.terrains[terrain.name], terrain)
        
        if hasattr(terrain, 'sourceFile'):
            path = terrain.sourceFile
        else:
            path = terrain.filename
        if not exists(path.toOsSpecific()):
            raise TextureNotFoundError(path)
        
        terrain.projDir = self.projDir
        dest = 'Textures/'
        if otherName:
            dest += otherName + '/'
            
        if hasattr(terrain, 'sourceFile'):
            terrain.moveTo(dest, self.projDir, source=terrain.sourceFile)
        else:
            terrain.moveTo(dest, self.projDir)
        
        terrain.name = prefix + terrain.name
        self.terrains[terrain.name] = terrain
        
        if not os.path.exists((self.projDir + '/' + dest +'/Thumbnails').toOsSpecific()):
            os.makedirs((self.projDir + '/' + dest + '/Thumbnails').toOsSpecific())
        cwd = os.getcwd()
        os.chdir((self.projDir + '/' + dest).toOsSpecific())
        thumbnailPath = Filename('Thumbnails/' + terrain.filename.getBasename())
        subprocess.call(["image-resize","-x 60", "-y 60", "-g 1", "-o" + thumbnailPath.toOsSpecific(), terrain.filename.getBasename()])
        os.chdir(cwd)
        terrain.thumbnail = Filename(dest + thumbnailPath.getFullpath())
            
        self.filenameIndex[terrain.filename] = terrain
            
        if saveAfter:
            self.saveToFile()
    def renameMesh(self, oldName, newName):
        if newName in self.meshes:
            raise DuplicateNameError(newName, self.meshes[newName],\
            self.meshes[oldName])
            
        mesh = self.meshes[oldName]
        mesh.name = newName
        del self.meshes[oldName]
        self.meshes[newName] = mesh
        
    def renameTexture(self, oldName, newName):
        if newName in self.textures:
            raise DuplicateNameError(newName, self.textures[newName],\
            self.textures[oldName])
            
        tex = self.textures[oldName]
        tex.name = newName
        del self.textures[oldName]
        self.textures[newName] = tex
   
    def renameTerrain(self, oldName, newName):
        if newName in self.terrains:
            raise DuplicateNameError(newName, self.terrains[newName],\
            self.terrains[oldName])
            
        terrain = self.terrains[oldName]
        terrain.name = newName
        del self.terrains[oldName]
        self.terrains[newName] = terrain
        
    def addActor(self, actor, saveAfter=False, addTextures=True, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + actor.name in self.actors:
            raise DuplicateNameError(prefix + actor.name, self.actors[prefix + actor.name], actor)
        
        if otherName:
            oldProjDir = actor.projDir
        
        actor.projDir = self.projDir
        
        if addTextures:
            for tex in actor.getTextures():
                self.addTexture(tex,False, otherName="")
                tex.refCount += 1
                
        for anim in actor.anims.values():
            anim.refCount += 1
        
        dest= 'Models/'
        if otherName:
            dest += otherName +'/'
            
        if hasattr(actor, 'sourceFile'):
            actor.moveTo(dest, self.projDir, source=actor.sourceFile)
        else:
            actor.moveTo(dest, self.projDir)
        
        actor.fixTexturePaths(otherName)
        
        actor.name = prefix + actor.name
        self.actors[actor.name] = actor
        
        if otherName and actor.thumbnail:
            newThumbnailDir = Filename(dest + '/' + 'Thumbnails/')
            if not os.path.exists((self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific()):
                os.makedirs((self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific())
            try:
                copy_vfs((oldProjDir + actor.thumbnail.getFullpath()).toOsSpecific(), (self.projDir + '/' + newThumbnailDir.getFullpath()).toOsSpecific())
            except Exception as e:
                print e
                actor.thumbnail = None
            else:
                actor.thumbnail = newThumbnailDir + actor.thumbnail.getBasename()
                path = (self.projDir + '/' + actor.thumbnail.getFullpath()).toOsSpecific()
                fileAtt = os.stat(path)[0]
                if (not fileAtt & stat.S_IWRITE):
                    os.chmod(path, stat.S_IWRITE)
        
        self.filenameIndex[actor.filename] = actor
        
        if saveAfter:
            self.saveToFile()
    
    def removeActor(self, name, delFile=True, force=False, removeAnimsAndTextures=False):
        if not force:
            if self.actors[name].numInScene != 0:
                raise AssetInUseError(self.actors[name])
            
        if delFile:
            toDel = self.actors[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
                if toDel.thumbnail:
                    os.remove(toDel.getThumbnail().toOsSpecific())
            except OSError as e:
                print e
        
        self.actors[name].onRemove()
        
        if removeAnimsAndTextures:
            for tex in self.actors[name].getTextures():
                if tex.numInScene == 0 and tex.refCount == 0:
                    self.removeTexture(tex.name, delFile=delFile)
                    
            for anim in self.actors[name].anims.values():
                if anim.numInScene == 0 and anim.refCount == 0:
                    self.removeAnimation(anim.name, delFile=delFile)
                
        
        del self.filenameIndex[self.actors[name].filename]
        del self.actors[name]
    
    def checkActor(self, actor, addTextures=True, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + actor.name in self.actors:
            raise DuplicateNameError(prefix + actor.name, self.actors[prefix + actor.name], actor) 
        
        folder= 'Models/'
        if otherName:
            folder += otherName + '/' 
        
        dest =(self.projDir + '/' + folder + actor.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, actor.filename.toOsSpecific(), actor)
       
        if addTextures:
            for tex in actor.getTextures():
                self.checkTexture(tex, otherName=otherName)
            
    def renameActor(self, oldName, newName):
        if newName in self.actors:
            raise DuplicateNameError(newName, self.actors[newName], self.actors[oldName])
        
        actor = self.actors[oldName]
        actor.name = newName
        del self.actors[oldName]
        self.actors[newName] = actor    
    
    def addAnimation(self, anim, saveAfter=True, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
            
        if prefix + anim.name in self.animations:
            if anim == self.animations[prefix + anim.name]:
                return
            else:
                raise DuplicateNameError(prefix + anim.name, self.animations[prefix + anim.name], anim)
        
        anim.projDir = self.projDir
        dest = 'Models/'
        if otherName:
            dest += otherName + '/'
            
        if hasattr(anim, 'sourceFile'):
            anim.moveTo(dest, self.projDir, source=anim.sourceFile)
        else:
            anim.moveTo(dest, self.projDir)
        
        anim.name = prefix + anim.name
        self.animations[anim.name] = anim
        
        self.filenameIndex[anim.filename] = anim
        
        if saveAfter:
            self.saveToFile()
            
    def removeAnimation(self, name, delFile=True, force=False):
        if not force:
            if self.animations[name].numInScene != 0:
                raise AssetInUseError(self.animations[name])
            if self.animations[name].refCount != 0:
                raise AssetReferencedError(self.animations[name])
            
        if delFile:
            toDel = self.animations[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
            except OSError as e:
                print e
                
        self.animations[name].onRemove()
        
        del self.filenameIndex[self.animations[name].filename]
        del self.animations[name]
        
    def checkAnimation(self, anim, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix =""
            
        if prefix + anim.name in self.animations:
            if anim == self.animations[prefix + anim.name]:
                return
            else:
                raise DuplicateNameError(prefix + anim.name, self.animations[prefix + anim.name], anim)
        folder = 'Models/'
        if otherName:
            folder += otherName + '/'
        dest =(self.projDir + '/' + folder + anim.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, anim.filename.toOsSpecific(), anim)
    
    def renameAnimation(self, oldName, newName):
        if newName in self.animations:
            raise DuplicateNameError(newName, self.animations[newName], self.animations[oldName])
        
        anim = self.animations[oldName]
        anim.name = newName
        del self.animations[oldName]
        self.animations[newName] = anim
    
    def addShader(self, shader, saveAfter=True, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + shader.name in self.shaders:
            raise DuplicateNameError(prefix + shader.name, self.shaders[prefix + shader.name], shader)
        
        shader.projDir = self.projDir
        dest= 'Shaders/'
        if otherName:
            dest += otherName + '/'
            
        if hasattr(shader, 'sourceFile'):
            shader.moveTo(dest, self.projDir, source=shader.sourceFile)
        else:
            shader.moveTo(dest, self.projDir)
        
        shader.name = prefix + shader.name
        self.shaders[shader.name] = shader
        
        self.filenameIndex[shader.filename] = shader
        
        if saveAfter:
            self.saveToFile()
    
    def removeShader(self, name, delFile=True, force=False):
        if not force:
            if self.shaders[name].numInScene != 0:
                raise AssetInUseError(self.shaders[name])
        
        if delFile:
            toDel = self.shaders[name]
            try:
                os.remove(toDel.getFullFilename().toOsSpecific())
            except OSError as e:
                print e
        
        self.shaders[name].onRemove()
        
        del self.filenameIndex[self.shaders[name].filename]
        del self.shaders[name]
        
    def checkShader(self, shader, otherName=""):
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        if prefix + shader.name in self.shaders:
            raise DuplicateNameError(prefix + shader.name, self.shaders[prefix + shader.name], shader)
        folder = 'Shaders/'
        if otherName:
            folder += otherName + '/'
        dest = (self.projDir + '/' + folder + shader.filename.getBasename()).toOsSpecific()
        if os.path.exists(dest):
            raise FileCollisionError(dest, shader.filename.toOsSpecific(), shader)
    
    def renameShader(self, oldName, newName):
        if newName in self.shaders:
            raise DuplicateNameError(newName, self.shaders[newName], self.shaders[oldName])
            
        shader = self.shaders[oldName]
        shader.name = newName
        del self.shaders[oldName]
        self.shaders[newName] = shader
    
    #check to see if merging with other library will cause an exception
    def checkLibrary(self, otherLib, otherName):
        for t in otherLib.textures.values():
            self.checkTexture(t, otherName=otherName)
        
        for m in otherLib.meshes.values():
            self.checkMesh(m, False, otherName=otherName)
            
        for a in otherLib.animations.values():
            self.checkAnimation(a, otherName=otherName)
        
        for a in otherLib.actors.values():
            self.checkActor(a, False, otherName=otherName)
            
        for s in otherLib.shaders.values():
            self.checkShader(s, otherName=otherName)
            
        for s in otherLib.sounds.values():
            self.checkSound(s, otherName=otherName)
        
        for t in otherLib.terrains.values():
            self.checkTerrain(t, otherName=otherName) 
               
    #adds all assets from another library into this one
    #prepends a prefix to all asset names and puts them
    #in subdirectories within the project folder
    def mergeWith(self, otherLib, otherName, saveAfter=False):
        for t in otherLib.textures.values():
            try:
                t.filename = t.getFullFilename()
                self.addTexture(t, otherName=otherName)
            except TextureNotFoundError as e:
                print "ERROR:Error in loading a texture at ", e.filename
        for m in otherLib.meshes.values():
            m.filename = m.getFullFilename()
            self.addMesh(m, addTextures=False, otherName=otherName)
            
        for a in otherLib.animations.values():
            a.filename = a.getFullFilename()
            self.addAnimation(a, otherName=otherName)
            
        for a in otherLib.actors.values():
            a.filename = a.getFullFilename()
            self.addActor(a, addTextures=False, otherName=otherName)
            
        for s in otherLib.shaders.values():
            s.filename = s.getFullFilename()
            self.addShader(s, otherName=otherName)
            
        for s in otherLib.sounds.values():
            s.filename = s.getFullFilename()
            self.addSound(s, otherName=otherName)
        
        for t in otherLib.terrains.values():
            t.filename = t.getFullFilename()
            self.addTerrain(t, otherName=otherName) 
            
        if saveAfter:
            self.saveToFile()
    
    #moves to entire library to another directory - for save as
    def moveTo(self, newDir):
        self.projDir = newDir
        
        for m in self.meshes.values():
            m.projDir = newDir
            
        for t in self.textures.values():
            t.projDir = newDir
            
        for a in self.animations.values():
            a.projDir = newDir
            
        for a in self.actors.values():
            a.projDir = newDir
        
        for s in self.shaders.values():
            s.projDir = newDir
            
        for s in self.sounds.values():
            s.projDir = newDir
        
        for t in self.terrains.values():
            t.projDir = newDir
            
        for je in self.journalEntries.values():
            je.projDir = newDir
        
        for c in self.conversations.values():
            c.projDir = newDir
            
        for s in self.scripts.values():
            s.projDir = newDir
    
    #adds an asset back into the library that was previously removed
    #the file must still be intact in the project directory
    def restoreAsset(self, asset):
        if asset.type == "Mesh":
            self.meshes[asset.name] = asset
        elif asset.type == "Texture":
            self.textures[asset.name] = asset
        elif asset.type == "Actor":
            self.actors[asset.name] = asset
        elif asset.type == "Animation":
            self.animations[asset.name] = asset
        elif asset.type == "Shader":
            self.shaders[asset.name] = asset
        elif asset.type == "Terrain":
            self.terrains[asset.name] = asset
        else:
            raise Exception("Unrecognized asset type")
            
        self.filenameIndex[asset.filename] = asset
    
    #save the library index to an xml file
    def saveToFile(self):
        xmlText=self.encode()
        try:
            f = open(os.path.join(self.projDir.toOsSpecific(),"lib.index"),'w')
            f.write(xmlText)
            f.close()
        except IOError:
            raise LibrarySaveError(os.path.join(self.projDir.toOsSpecific(),"lib.index"))
    
    #exports the library as a .lbr multifile
    def exportToMultifile(self, filename):
        cwd = os.getcwd()
        os.chdir(self.projDir.toOsSpecific())
        
        try:
            subprocess.call(["multify", "-f" + filename.getBasename(), "-c", "-z", "./lib.index","./Conversations", "./Models", "./Textures","./Shaders", "./Sounds", "./Scripts"])
        except Exception as e:
            print e
        
        os.chdir(cwd)
    
    #decode the xml file and rebuild the library in memory
    def decode(self,xmlFile):
        doc = xml.dom.minidom.parse(xmlFile)
        root = doc.childNodes[0]
        
        meshes = doc.createElement("")
        textures = doc.createElement("")
        actors = doc.createElement("")
        anims = doc.createElement("")
        shaders = doc.createElement("")
        sounds = doc.createElement("")
        terrains = doc.createElement("")
        journalEntries = doc.createElement("")
        scripts = doc.createElement("")
        conversations = doc.createElement("")
        
        for n in root.childNodes:
            if n.localName == "Meshes":
                meshes = n
            elif n.localName == "Textures":
                textures = n
            elif n.localName == "Animations":
                anims = n
            elif n.localName == "Actors":
                actors = n
            elif n.localName == "Shaders":
                shaders = n
            elif n.localName == "Sounds":
                sounds = n
            elif n.localName == "Terrains":
                terrains = n
            elif n.localName == "JournalEntries":
                journalEntries = n
            elif n.localName == "Conversations":
                conversations = n
            elif n.localName == "Scripts":
                scripts = n
         
        for texture in textures.childNodes:
            if texture.localName == "Texture":
                t = Texture.decode(texture)
                t.projDir = self.projDir
                self.textures[t.name] = t
                self.filenameIndex[t.filename] = t
         
        for mesh in meshes.childNodes:
            if mesh.localName == "Mesh":
                m = Mesh.decode(mesh, self)
                m.projDir = self.projDir
                self.meshes[m.name] = m
                self.filenameIndex[m.filename] = m
        
        for anim in anims.childNodes:
            if anim.localName == "Animation":
                a = Animation.decode(anim)
                a.projDir = self.projDir
                self.animations[a.name] = a
                self.filenameIndex[a.filename] = a
                
        for actor in actors.childNodes:
            if actor.localName == "Actor":
                a = Actor.decode(actor, self)
                a.projDir = self.projDir
                self.actors[a.name] = a
                self.filenameIndex[a.filename] = a
                
        for shader in shaders.childNodes:
            if shader.localName == "Shader":
                s = Shader.decode(shader)
                s.projDir = self.projDir
                self.shaders[s.name] = s
                self.filenameIndex[s.filename] = s
        
        for sound in sounds.childNodes:
            if sound.localName == "Sound":
                s = Sound.decode(sound)
                s.projDir = self.projDir
                self.sounds[s.name] = s
                self.filenameIndex[s.filename] = s
        
        for terrain in terrains.childNodes:
            if terrain.localName == "Terrain":
                t = Terrain.decode(terrain)
                t.projDir = self.projDir
                self.terrains[t.name] = t
                self.filenameIndex[t.filename] = t
        
        for journalEntry in journalEntries.childNodes:
            if journalEntry.localName == "JournalEntry":
                je = JournalEntry.decode(journalEntry)
                je.projDir = self.projDir
                self.journalEntries[je.name] = je
                self.filenameIndex[je.filename] = je
        
        for script in scripts.childNodes:
            if script.localName == "Script":
                s = Script.decode(script)
                s.projDir = self.projDir
                self.processScriptType(s)
                self.scripts[s.name] = s
                self.filenameIndex[s.filename] = s
        
        for convo in conversations.childNodes:
            if convo.localName == "Conversation":
                c = ConversationAsset.decode(convo)
                c.projDir = self.projDir
                self.conversations[c.name] = c
                self.filenameIndex[c.filename] = c
                
    # encode the library as an xml string    
    def encode(self):
        doc = xml.dom.minidom.Document()
        root = doc.createElement("Library")
        doc.appendChild(root)
        
        meshes = doc.createElement("Meshes")
        root.appendChild(meshes)
        for mesh in self.meshes.values():
            meshes.appendChild(mesh.encode(doc))
        
        textures = doc.createElement("Textures")
        root.appendChild(textures)
        for texture in self.textures.values():
            textures.appendChild(texture.encode(doc))
            
        anims = doc.createElement("Animations")
        root.appendChild(anims)
        for anim in self.animations.values():
            anims.appendChild(anim.encode(doc))
        
        actors = doc.createElement("Actors")
        root.appendChild(actors)
        for actor in self.actors.values():
            actors.appendChild(actor.encode(doc))
            
        shaders = doc.createElement("Shaders")
        root.appendChild(shaders)
        for shader in self.shaders.values():
            shaders.appendChild(shader.encode(doc))
        
        sounds = doc.createElement("Sounds")
        root.appendChild(sounds)
        for sound in self.sounds.values():
            sounds.appendChild(sound.encode(doc))
            
        journalEntries = doc.createElement("JournalEntries")
        root.appendChild(journalEntries)
        for journalEntry in self.journalEntries.values():
            journalEntries.appendChild(journalEntry.encode(doc))
            
        scripts = doc.createElement("Scripts")
        root.appendChild(scripts)
        for script in self.scripts.values():
            scripts.appendChild(script.encode(doc))
            
        conversations = doc.createElement("Conversations")
        root.appendChild(conversations)
        for convo in self.conversations.values():
            conversations.appendChild(convo.encode(doc))
        
        terrains = doc.createElement("Terrains")
        root.appendChild(terrains)
        for terrain in self.terrains.values():
            terrains.appendChild(terrain.encode(doc))
        
        return doc.toprettyxml()
        
    
#base class for all assets in the library        
class Asset:
    def __init__(self,name,filename,thumbnail=None, type="Asset"):
        self.name=name
        self.filename = filename #relative to the project directory
                                 #beofer asset is added to the library, this is the source path
        self.thumbnail = thumbnail
        self.type = type
        self.refCount = 0   #the number of times this asset is referenced either by another asset
        self.numInScene = 0 #number of times this asset is referenced by something in the scene
    
    #overrride this to also call this method on any asset this one references
    def incSceneCount(self):
        self.numInScene += 1
    
    #override this to also call this method on any asset thisone references
    def decSceneCount(self):
        self.numInScene -= 1
    
    #should be overrriden to handle anything that needs to happen when an asset is removed from the library
    # (e.g., updating reference counts)
    def onRemove(self):
        pass
    
    #returns the full file name( including project directory)
    #Pre-condition: Asset is already in a library
    def getFullFilename(self):
        return Filename(self.projDir.getFullpath() + '/' + self.filename.getFullpath())

    #moves the source file into the project directory and changes the filename
    def moveTo(self,folder,projFolder, source=None):
        if not source:
            source = self.filename
        dest = (projFolder + '/' + folder + '/' + self.filename.getBasename()).toOsSpecific()
        if not exists(source.toOsSpecific()):
            source = self.projDir + '/' + source.getFullpath()
        
        if os.path.exists(dest):
            raise FileCollisionError(dest, source.toOsSpecific(), self)
        
        destFolder = (projFolder + '/' + folder).toOsSpecific()
        if not os.path.exists(destFolder):
            os.makedirs(destFolder)
        copy_vfs(source.toOsSpecific(), dest)
        
        fileAtt = os.stat(dest)[0]
        if (not fileAtt & stat.S_IWRITE):
            os.chmod(dest, stat.S_IWRITE)
        
        self.filename.setDirname(folder)

    #links this asset with a new file from disk and copies that file to the project
    #directory
    def relink(self, newFile):
        newFilename = Filename.fromOsSpecific(newFile)
        dest = (self.projDir + '/' + self.filename.getDirname() +'/' + newFilename.getBasename()).toOsSpecific()        
        try:
            copy_vfs(newFilename.toOsSpecific(), dest)
            fileAtt = os.stat(dest)[0]
            if (not fileAtt & stat.S_IWRITE):
                os.chmod(dest, stat.S_IWRITE)
        except IOError as e:
            raise e
        else:
            self.filename.setBasename(newFilename.getBasename())
            
        if self.thumbnail and newFilename.getBasename() != self.thumbnail.getBasename():    
            cwd = os.getcwd()
            
            oldThumbnail = self.thumbnail.getBasename()
            newThumbnail = self.filename.getBasenameWoExtension() + '.' + self.thumbnail.getExtension()
            thumbnailDir = Filename((self.projDir + '/' + self.thumbnail.getFullpath()).getDirname()).toOsSpecific()
            
            os.chdir(thumbnailDir)
            try:
                shutil.move(oldThumbnail, newThumbnail)
            except Exception as e:
                print e
            else:
                self.thumbnail.setBasename(newThumbnail)
            os.chdir(cwd)
    
    #returns the filename of the thumbnail to show for this asset
    def getThumbnail(self):
        return Filename('default_thumb.jpg')
    
    #encodes this asset as an xml string
    def encode(self, doc):
        node = doc.createElement(self.type)
        fileNode = doc.createElement("File")
        node.appendChild(fileNode)
        fileNode.appendChild(doc.createTextNode(self.filename.getFullpath()))
        nameNode = doc.createElement("Name")
        node.appendChild(nameNode)
        nameNode.appendChild(doc.createTextNode(self.name))
        if self.thumbnail:
            thumbnailNode = doc.createElement("Thumbnail")
            node.appendChild(thumbnailNode)
            thumbnailNode.appendChild(doc.createTextNode(self.thumbnail.getFullpath()))
        
        return node
    
    #decode from an xml node
    def decode(node):
        thumbnail=None
        
        for n in node.childNodes:
            if n.localName == "File":
                eggFile = n.childNodes[0].data.strip()
            elif n.localName == "Name":
                name = n.childNodes[0].data.strip()
            elif n.localName == "Thumbnail":
                thumbnail = Filename(n.childNodes[0].data.strip())
        
        return Asset(name,Filename(eggFile),thumbnail, type=node.localName)
    decode = staticmethod(decode)
    
#static mesh asset      
class Mesh(Asset):
    def __init__(self,name,filename,thumbnail=None):
        Asset.__init__(self,name,filename,thumbnail, type="Mesh")
        self.textures=[]    #textures in the mesh's egg file
        self.findTextures()
    
    def incSceneCount(self):
        Asset.incSceneCount(self)
        for t in self.textures:
            t.incSceneCount()
            
    def decSceneCount(self):
        Asset.decSceneCount(self)
        for t in self.textures:
            t.decSceneCount()
    
    def onRemove(self):
        for tex in self.textures:
            tex.refCount-=1
    
    def findTextures(self):
        if self.textures:
            for tex in self.textures:
                tex.refCount-=1
            self.textures = []
        # This maps the original filename in the egg file to texture assets - so we can handle textures that get
        # renamed due to conflicts when we change the texture paths later
        self.textureOrigFilenameIndex = {}    
        
        textureFilenames = []

        eggData = EggData() #creates empty egg data
        eggData.read(self.filename) #loads the actual egg
        eggTexColl = EggTextureCollection() #create empty egg texture collection
        eggTexColl.extractTextures(eggData) #copies all of the textures from the egg file to eggTexColl
        
        for eggTex in eggTexColl:   #loop through every texture
            f=Filename.fromOsSpecific(eggTex.getFilename().getFullpath())
            if f.isLocal(): #create absolute path
                f = Filename(self.filename.getDirname() + '/' + f.getFullpath())
                
            if f.getFullpath() not in textureFilenames: #to account for textures that show up twice in the same egg
                textureFilenames.append(f.getFullpath())
                tex = Texture(self.name + "_" + f.getBasenameWoExtension(),f)
                self.textures.append(tex)
                self.textureOrigFilenameIndex[Filename(eggTex.getFilename())] = tex
                
            if eggTex.hasAlphaFilename():   #account for seperate alpha file
                f=Filename(eggTex.getAlphaFilename())
                if f.isLocal():
                    f = Filename(self.filename.getDirname() + '/' + f.getFullpath()) 
                if f.getFullpath() not in textureFilenames:
                    textureFilenames.append(f.getFullpath())
                    tex = Texture(self.name + "_" + f.getBasenameWoExtension() + '_alpha', f)
                    self.textures.append(tex)
                    self.textureOrigFilenameIndex[Filename(eggTex.getAlphaFilename())] = tex
    
    def getThumbnail(self):
        if self.thumbnail:
            return self.projDir + '/' + self.thumbnail.getFullpath()
        else:
            return Filename('models/mesh.jpg')
    
    def encode(self,doc):
        meshNode = Asset.encode(self, doc)
        
        for tex in self.textures:
            texNode = doc.createElement('TexRef')
            meshNode.appendChild(texNode)
            texNode.appendChild(doc.createTextNode(tex.name))
        
        return meshNode
        
    def decode(meshNode, lib):
        mesh = Asset.decode(meshNode)
        mesh.__class__ = Mesh
        mesh.textures = []
        mesh.textureOrigFilenameIndex = {}

        for n in meshNode.childNodes:
            if n.localName == "TexRef":
                tex = lib.textures[n.childNodes[0].data.strip()]
                mesh.textures.append(tex)
                
                dir = Filename(mesh.filename.getDirname())
                dir.makeAbsolute()
                fName = Filename(tex.filename)
                fName.makeAbsolute()
                fName.makeRelativeTo(dir)
                mesh.textureOrigFilenameIndex[fName] = tex
                
                tex.refCount += 1
        
        return mesh
    decode = staticmethod(decode)
    
    def relink(self, newFile):
        otherName = ''

        dirName = self.filename.getDirname()
        if dirName.find('/') != -1:
            otherName = dirName.split('/', 1)[1]
        
        self.textures = []
        Asset.relink(self, newFile)
        
        eggData = EggData()
        eggData.read(self.projDir + '/' + self.filename.getFullpath())
        eggTexColl = EggTextureCollection()
        eggTexColl.extractTextures(eggData)
        
        eggTextures = []
        #generate a list of all texture files in the egg, including alpha files
        for eggTex in eggTexColl:
            eggTextures.append(eggTex.getFilename())
            if eggTex.hasAlphaFilename():
                eggTextures.append(eggTex.getAlphaFilename())
        
        for texFile in eggTextures:
            f = texFile.getBasename()
            if otherName:
                prefix = 'Textures/' + otherName + '/'
                f = Filename(prefix + f)
            else:
                f = Filename('Textures/' + f)
                
            if texFile.isLocal():
                textureFile = Filename(Filename.fromOsSpecific(newFile).getDirname()) + '/' + texFile.getFullpath()
            else:
                textureFile = Filename(textureFile)
                
            if not f in base.le.lib.filenameIndex:  #if this file is not part of the library, add it
                name = textureFile.getBasenameWoExtension()
                i = 2
                while name in self.textures:
                    name = name + '_' + str(i)
                    
                #make sure we aren't overwriting some other file
                if not os.path.exists((self.projDir + '/' + f.getFullpath()).toOsSpecific()):
                    newTex = Texture(self.name+ '_' + name, textureFile)
                    base.le.lib.addTexture(newTex)
                    self.textures.append(newTex)
                    self.textureOrigFilenameIndex[texFile] = newTex
                else:
                    print 'ERROR:Texture ' + str(textureFile) + ' will not be copied to the project folder because another '\
                    + 'file already exists in that directory with the same name.'
            else:   #if it is, just relink that file
                try:
                    base.le.lib.filenameIndex[f].relink(textureFile.toOsSpecific())
                except Exception as e:
                    print 'ERROR:Could not relink texture named "' + base.le.lib.filenameIndex[f].name + '"'
                    print e
 
                self.textures.append(base.le.lib.filenameIndex[f])
                self.textureOrigFilenameIndex[texFile] = base.le.lib.filenameIndex[f]
        
        self.fixTexturePaths(otherName)
    
    #returns a list of all texture files in the egg
    def getTextures(self):
        return self.textures
    
    #changes the texture paths in the egg to point to the copy in the project folder
    def fixTexturePaths(self, otherName=''):
        eggData = EggData()
        eggData.read(self.projDir + '/' + self.filename.getFullpath())
        eggTexColl = EggTextureCollection()
        eggTexColl.extractTextures(eggData)
        
        for eggTex in eggTexColl:
            if otherName:
                dirName = '../' * (otherName.count('/') + 2) + 'Textures/' + otherName + '/'
            else:
                dirName = '../Textures/'
                
            tex = self.textureOrigFilenameIndex[Filename(eggTex.getFilename())]
            f = tex.filename
            eggTex.setFilename(dirName + f.getBasename())
            if eggTex.hasAlphaFilename():
                a = Filename.fromOsSpecific(eggTex.getAlphaFilename().getFullpath())
                eggTex.setAlphaFilename(dirName + a.getBasename())
            
        eggData.writeEgg(self.projDir + '/' + self.filename.getFullpath())

#Texture asset        
class Texture(Asset):
    def __init__(self,name,filename, thumbnail=None):
        Asset.__init__(self,name,filename,thumbnail, type="Texture")
        
    def getThumbnail(self):
        if self.thumbnail:
            return self.projDir + '/' + self.thumbnail.getFullpath()
        else:
            return Asset.getThumbnail(self)
    
    def relink(self, newFile):
        Asset.relink(self, newFile)
        
        #take a new thumbnail
        if not self.isCubeMap() and self.thumbnail:
            newFilename = Filename.fromOsSpecific(newFile)
            thumbnailPath = Filename('Thumbnails/' + self.filename.getBasename()).toOsSpecific()
            try:
                cwd = os.getcwd()
                os.chdir((self.projDir + '/' + self.filename.getDirname()).toOsSpecific())
                subprocess.call(["image-resize", "-x 60", "-y 60", "-g 1", "-o" + thumbnailPath, self.filename.getBasename()])
                os.chdir(cwd)
            except Exception as e:
                print e
            else:
                self.thumbnail.setBasename(newFilename.getBasename())
            
    
    def decode(textureNode):
        tex = Asset.decode(textureNode)
        tex.__class__ = Texture
                
        return tex
        
    decode = staticmethod(decode)
    
    def isCubeMap(self):
        return self.filename.getExtension() == "dds"

#Actor asset
class Actor(Mesh):
    def __init__(self, name, filename, thumbnail=None, anims={}):
        Mesh.__init__(self, name, filename, thumbnail)
        self.type ="Actor"
        self.anims = anims #keys are local names, values are animation asset
    
    def incSceneCount(self):
        Mesh.incSceneCount(self)
        for a in self.anims.values():
            a.incSceneCount()
            
    def decSceneCount(self):
        Mesh.decSceneCount(self)
        for a in self.anims.values():
            a.decSceneCount()
    
    def onRemove(self):
        Mesh.onRemove(self)
        
        for a in self.anims.values():
            a.refCount -= 1
    
    def getThumbnail(self):
        if self.thumbnail:
            return self.projDir + '/' + self.thumbnail.getFullpath()
        else:
            return Filename('models/actor.jpg')
    
    def encode(self, doc):
        node = Mesh.encode(self, doc)
        for name, anim in self.anims.iteritems():
            animNode = doc.createElement("Anim")
            node.appendChild(animNode)
            localName = doc.createElement("LocalName")
            animNode.appendChild(localName)
            localName.appendChild(doc.createTextNode(name))
            assetName = doc.createElement("AssetName")
            animNode.appendChild(assetName)
            assetName.appendChild(doc.createTextNode(anim.name))
            
        return node
    
    def decode(actorNode, lib):
        actor = Mesh.decode(actorNode, lib)
        actor.__class__ = Actor

        actor.anims = {}
        for node in actorNode.childNodes:
            if node.localName == "Anim":
                for n in node.childNodes:
                    if n.localName == "LocalName":
                        localName = n.childNodes[0].data.strip()
                    elif n.localName == "AssetName":
                        assetName = n.childNodes[0].data.strip()
                
                actor.anims[localName] = lib.animations[assetName]
        
        for a in actor.anims.values():
            a.refCount += 1
        
        return actor
        
    decode = staticmethod(decode)

class Animation(Asset):
    def __init__(self, name, filename):
        Asset.__init__(self, name, filename, type="Animation")
    
    def getThumbnail(self):
        return Filename('models/animation.jpg')
        
    def decode(node):
        anim = Asset.decode(node)
        anim.__class__ = Animation
        
        return anim
    
    def __eq__(self, other):
        return self.name == other.name and self.filename == other.filename
    
    decode = staticmethod(decode)


class Shader(Asset):
    def __init__(self, name, filename):
        Asset.__init__(self, name, filename, type="Shader")
    
    def getThumbnail(self):
        return Filename('models/shader.jpg')
    
    def decode(node):
        shader = Asset.decode(node)
        shader.__class__ = Shader
        
        return shader
   
    decode = staticmethod(decode)

class Sound(Asset):
    def __init__(self,name,filename, thumbnail=None):
        Asset.__init__(self,name,filename, type="Sound") 
        
    def getThumbnail(self):
        return Filename('models/sound.jpg')
        
    def decode(soundNode):
        sound = Asset.decode(soundNode)
        sound.__class__ = Sound
                
        return sound
        
    decode = staticmethod(decode)
    
class JournalEntry(Asset):
    def __init__(self,name,filename, thumbnail=None):
        Asset.__init__(self,name,filename, type="JournalEntry") 
        
    def getThumbnail(self):
        return Filename('models/journalEntry.jpg')
        
    def decode(journalEntryNode):
        journalEntry = Asset.decode(journalEntryNode)
        journalEntry.__class__ = JournalEntry
                
        return journalEntry
        
    decode = staticmethod(decode)

class Script(Asset):
    def __init__(self,name,filename, thumbnail=None):
        Asset.__init__(self,name,filename, type="Script")
        
    def getThumbnail(self):
        return Filename('models/journalEntry.jpg')
        
    def decode(scriptNode):
        script = Asset.decode(scriptNode)
        script.__class__ = Script
                
        return script
        
    decode = staticmethod(decode)

class ConversationAsset(Asset):
    def __init__(self, name, filename, thumbnail=None):
        Asset.__init__(self, name, filename, type="Conversation") 
        
    def getThumbnail(self):
        # TODO: change
        return Filename('models/journalEntry.jpg')
        
    def decode(convoNode):
        conversation = Asset.decode(convoNode)
        conversation.__class__ = ConversationAsset # CAUTION: or just "Conversation"?
                
        return conversation
    decode = staticmethod(decode)
    
#heightmap terrain asset
class Terrain(Asset):
    def __init__(self,name,filename, thumbnail=None):
        Asset.__init__(self,name,filename,thumbnail, type="Terrain")
        
    def getThumbnail(self):
        if self.thumbnail:
            return self.projDir + '/' + self.thumbnail.getFullpath()
        else:
            return Asset.getThumbnail(self)
    
    def decode(terrainNode):
        terrain = Asset.decode(terrainNode)
        terrain.__class__ = Terrain
                
        return terrain
        
    decode = staticmethod(decode)
    
    def isCubeMap(self):
        return self.filename.getExtension() == "dds"    

#Base class for exceptions in this module    
class Error(Exception):
        pass

#Raised when trying to add an asset with a name that already exists in the library        
class DuplicateNameError(Error):
    def __init__(self, name, oldAsset, newAsset):
        self.name = name
        self.oldAsset = oldAsset
        self.newAsset = newAsset
 
#Raised when trying to move a file into the project directory in such a way that would
#overwrite an existing file 
class FileCollisionError(Error):
    def __init__(self, destPath, sourcePath, asset):
        self.destPath = destPath
        self.sourcePath = sourcePath
        self.asset = asset

class LibrarySaveError(Error):
    def __init__(self, filename):
        self.filename = filename
        
#Raised when an egg file contains a bad texture path        
class TextureNotFoundError(Error):
    def __init__(self, filename):
        self.filename = filename
        
#Raised when an attempt is made to remove an asset that is being used in the scene      
class AssetInUseError(Error):
    def __init__(self, asset):
        self.asset = asset
        
#Raised when an attempt is made to remove an asset that is being referenced by another asset        
class AssetReferencedError(Error):
    def __init__(self, asset):
        self.asset = asset