import Library
import xml.dom.minidom
import shutil
from pandac.PandaModules import Filename
import os.path
import os, stat
from Util import DuplicateNameError , FileCollisionError, SceneDeleteError

import Debug

class Project:
    def __init__(self, filename, name = ""):
        self.filename = filename    #absolute
        self.dir = Filename(filename.getDirname())
        #[Zeina]CONSIDER: the sceneFilename can be changed to starting sceneFile or default sceneFile
        #The default scene file cannot be deleted.
        #self.sceneFilename = None #Filename(filename.getBasenameWoExtension() + '.scene')
        self.sceneName = None
        self.scenes = {}#key:Scene Name, value:Scene Filename
        self.scenesOrder = []
        self.filenameIndexes = {}
        #self.addScene(filename.getBasenameWoExtension(), self.sceneFilename)
        self.journalFilename = Filename(filename.getBasenameWoExtension() + '.journal')
        self.inventoryMapFilename = Filename(filename.getBasenameWoExtension()+'.inventory')
        self.name = name
        
        try:
            f = open(filename.toOsSpecific())
            self.decode(f)
            f.close()
        except IOError:
            pass
            self.addScene()
        #if self.scenes.has_key("startScene"):
        #    self.sceneName = "startScene"
        #create the folder structure
        if not os.path.isdir(self.dir.toOsSpecific()):
            os.makedirs(self.dir.toOsSpecific())
        
        for d in ('Models','Textures', 'Models/Thumbnails', 'Textures/Thumbnails', 'Shaders', 'Sounds', 'Journal_Entries', 'Conversations', 'Scripts'):
            dir = os.path.join(self.dir.toOsSpecific(),d)
            if not os.path.isdir(dir):
                os.mkdir(dir)
        
        self.lib = Library.Library(self.dir)
            
    def decode(self, xmlFile):
        doc = xml.dom.minidom.parse(xmlFile)
        root = doc.childNodes[0]
        startingSceneName = None
        for n in root.childNodes:
            if n.localName == "Name":
                self.name = n.childNodes[0].data.strip()
            elif n.localName == "StartingSceneName":
                startingSceneName = n.childNodes[0].data.strip()
            elif n.localName == "SceneFile":
                for m in n.childNodes:
                    if(m.localName == "Name"):
                        name = str(m.childNodes[0].data.strip())
                    if(m.localName == "Filepath"):
                        filepath = Filename(m.childNodes[0].data.strip())
                self.addScene(name, filepath)
                    #self.sceneFilename = Filename(n.childNodes[0].data.strip())
            elif n.localName == "JournalFile":
                self.journalFilename = Filename(n.childNodes[0].data.strip())
        if(startingSceneName != None):
            self.sceneName = startingSceneName
        
    def encode(self):
        doc = xml.dom.minidom.Document()
        root = doc.createElement("Project")
        doc.appendChild(root)
        
        name = doc.createElement("Name")
        name.appendChild(doc.createTextNode(self.name))
        root.appendChild(name)
        
        startingSceneName = doc.createElement("StartingSceneName")
        #startingSceneName = doc.createElement("Name")
        startingSceneName.appendChild(doc.createTextNode(self.sceneName))
        #startingSceneFile.appendChild(startingSceneName)
        
        root.appendChild(startingSceneName)
        
        for s in self.scenesOrder:
            sceneFile = doc.createElement("SceneFile")
            sceneName = doc.createElement("Name")
            sceneName.appendChild(doc.createTextNode(s))
            sceneFile.appendChild(sceneName)
            sceneFilepath = doc.createElement("Filepath")
            sceneFilepath.appendChild(doc.createTextNode(self.scenes[s].getFullpath()))
            sceneFile.appendChild(sceneFilepath)
            root.appendChild(sceneFile)
            
        journalFile = doc.createElement("JournalFile")
        journalFile.appendChild(doc.createTextNode(self.journalFilename.getFullpath()))
        root.appendChild(journalFile)
        inventoryMapFile = doc.createElement("InventoryMapFile")
        inventoryMapFile.appendChild(doc.createTextNode(self.inventoryMapFilename.getFullpath()))
        root.appendChild(inventoryMapFile)
        
        
        return doc.toprettyxml()
        
    def saveToFile(self):
        xmlText = self.encode()
        try:
            f = open(self.filename.toOsSpecific(), "w")
            f.write(xmlText)
            f.close()
        except IOError:
            raise ProjectSaveError(self.filename.toOsSpecific())
    
    def saveAs(self, newDir, newName, keepOld=False):
        if keepOld:
            shutil.copytree(self.dir.toOsSpecific(), newDir.toOsSpecific())
        else:
            if not os.path.exists(newDir.toOsSpecific()):
                os.makedirs(newDir.toOsSpecific())
            for x in os.listdir(self.dir.toOsSpecific()):
                shutil.move((self.dir + '/' + x).toOsSpecific(), (newDir + '/' + x).toOsSpecific())
        
        #make sure everything in the new directory is not marked read only
        for root, dirs, files in os.walk(newDir.toOsSpecific()):
            for name in files:
                os.chmod(os.path.join(root, name), stat.S_IWRITE)
        
        newFilename = newDir + '/' +newName + '.proj'
        newSceneFilename = Filename(newName + '.scene')
        newJournalFilename = Filename(newName + '.journal')
        newInventoryMapFilename = Filename(newName + '.inventory')
        
        f = Filename(self.filename)
        f.setDirname(newDir.getFullpath())
        
        f2 = Filename(self.scenes[self.sceneName])#self.sceneFilename)
        f2.setDirname(newDir.getFullpath())
        
        f3 = Filename(self.journalFilename)
        f3.setDirname(newDir.getFullpath())
        
        f4 = Filename(self.inventoryMapFilename)
        f4.setDirname(newDir.getFullpath())
        
        #make sure we don't end up with a project or scene file with the old name
        #in the new directory
        if os.path.exists(f.toOsSpecific()):
            os.remove(f.toOsSpecific())
        if os.path.exists(f2.toOsSpecific()):
            os.remove(f2.toOsSpecific())
        if os.path.exists(f3.toOsSpecific()):
            os.remove(f3.toOsSpecific())
        if os.path.exists(f4.toOsSpecific()):
            os.remove(f4.toOsSpecific())
        
        self.name = newName   
        self.dir = newDir        
        self.filename = newFilename
        #self.scenes["default"] = newSceneFilename      
        #self.sceneFilename = newSceneFilename
        self.journalFilename = newJournalFilename
        self.inventoryMapFilename = newInventoryMapFilename
        
        self.lib.moveTo(newDir)
        
        self.saveToFile()
    
    def addScene(self,name=None, sceneFile=None):
        if(name == None):
            suffix = len(self.scenes)
            defaultname = "default_"
            
            name = defaultname+str(suffix)
            sceneFile = Filename(name+".scene")
            f = Filename(sceneFile)
            f.setDirname(self.dir.getFullpath())
            while(os.path.exists(f.toOsSpecific())or self.filenameIndexes.has_key(sceneFile.getBasenameWoExtension())):
                suffix += 1
                name = defaultname+str(suffix)
                sceneFile = Filename(name+".scene")
                f = Filename(sceneFile)
                f.setDirname(self.dir.getFullpath())
        #if there is a name but no  sceneFile given for that name
        #create a file with that name
        #TO DO: make it more error prone, for example this is not checking
        #if the file with the name already exist in the folder. This part may not be
        #be used at all but should be thought about.
        if(sceneFile == None):
             sceneFile = Filename(name+".scene")            
        self.scenes[name] = sceneFile
        self.filenameIndexes[sceneFile.getBasenameWoExtension()] = sceneFile
        if(len(self.scenes) == 1 ):
            #self.sceneFilename = sceneFile
            self.sceneName = name
        
        #f = Filename(sceneFile)
        #f.setDirname(self.dir.getFullpath())
        self.scenesOrder = sorted(self.scenes)
        return (name,sceneFile)
    
    def getOpeningScene(self):
        return self.scenes[self.sceneName]
    
    def getScene(self,sceneName):
        if self.scenes.has_key(sceneName):
            return self.scenes[sceneName]
        else:
            print "There is no scene under name ", sceneName, " in the project."
            return None
    def renameScene(self, name, newName):
        if(self.getScene(newName)!= None):
            raise DuplicateNameError(newName,name, newName)
        #print name," ", newName
        sceneFile = self.getScene(name)
        del self.scenes[name]
        self.scenes[newName] = sceneFile
        
        if(self.sceneName == name):
            self.sceneName = newName
        self.scenesOrder = sorted(self.scenes)

        Debug.debug(__name__,str(self.scenes))
        Debug.debug(__name__,str(self.scenesOrder))
    
    def removeScene(self, sceneName, delFile = False):
        if(len(self.scenes)==1):
            raise SceneDeleteError() 
        else:
            #delete the file in the folder too.
            if delFile:
                toDel = Filename(self.dir.getFullpath() + '/' + self.scenes[sceneName].getFullpath())
                try:
                    os.remove(toDel.toOsSpecific())
                except OSError as e:
                    pass
            if(self.sceneName == sceneName):
                self.sceneName = self.scenesOrder[0]
                #self.sceneFilename = self.scenes[self.sceneName]
            del self.filenameIndexes[self.scenes[sceneName].getBasenameWoExtension()]
            del self.scenes[sceneName]
            self.scenesOrder = sorted(self.scenes)
    def setOpeningScene(self, name):
        self.sceneName = name       


class ProjectSaveError(Exception):
    def __init__(self, filename):
        self.filename = filename