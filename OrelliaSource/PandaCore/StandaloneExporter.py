import os.path
#from os import getcwd
from pandac.PandaModules import Filename

import shutil

class StandaloneExporter:
    def __init__(self, editor):
        self.editor = editor
    
    def export(self, opts):
        
        file = opts['path']
        
        templateFile = open('ExportTemplate.py')
        
        lines = templateFile.readlines()
        outputLines = []
        if opts['loadScreen']:
            outputLines.append("from direct.gui.OnscreenImage import OnscreenImage\n")
            
        for line in lines:
            if line.startswith('SCENE_FILE'):
                outputLines.append(line.replace('None',\
                "'" + self.editor.currentProj.getOpeningScene().getFullpath() + "'"))
            elif line.startswith('LIBRARY_INDEX'):
                outputLines.append(line.replace('None',\
                "'lib.index'"))
            elif line.startswith('HEIGHT'):
                outputLines.append(line.replace('None', str(opts['camHeight'])))
            elif line.startswith('CAM_MOVE_SPEED'):
                outputLines.append(line.replace('None', str(opts['camSpeed'])))
            elif line.strip().startswith('ShowBase.__init__'):
                outputLines.append(line)
                
                if opts['loadScreen']:
                    path = base.le.lib.textures[ opts['loadScreen'] ].filename.getFullpath()
                    outputLines.append("\n        loadScreen = OnscreenImage(image = '" + path + "')\n")
                    outputLines.append("        taskMgr.step()\n")
                    outputLines.append("        taskMgr.step()\n")
            
            elif line.strip().startswith('self.cTrav = '):
                outputLines.append(line)
                if opts['camPusher']:
                    outputLines.append("\n        cameraSphere = CollisionNode('cameraSphere')\n")
                    outputLines.append("        cameraSphere.addSolid(CollisionSphere(Point3(0, 0, 0), 1))\n")
                    outputLines.append("        self.cameraCollide = self.cam.attachNewNode(cameraSphere)\n")
                    outputLines.append("        self.cameraPusher = CollisionHandlerPusher()\n")
                    outputLines.append("        self.cTrav.addCollider(self.cameraCollide, self.cameraPusher)\n")
                    outputLines.append("        self.cameraPusher.addCollider(self.cameraCollide, self.cam)\n")
                if opts['useSceneBG']:
                    outputLines.append("\n")
                    outputLines.append("        base.setBackgroundColor(" + str(base.getBackgroundColor()) + ")\n")
                    outputLines.append("\n")
                if opts['cam']:
                    outputLines.append("\n")
                    outputLines.append("        # Set the camera's properties from the camera in the level editor scene\n")
                    outputLines.append("        self.cam.reparentTo(self.objects['" + opts['cam'] + "'].getParent())\n")
                    outputLines.append("        self.cam.setMat(self.objects['" + opts['cam'] + "'].getMat())\n")
                    outputLines.append("        self.cam.wrtReparentTo(self.objects['" + opts['cam'] + "'])\n")
                    outputLines.append("        self.cam.node().setLens(self.objects['" + opts['cam'] + "'].node().getLens())\n")
                    outputLines.append("        self.camLens = self.cam.node().getLens()\n")
                    outputLines.append("        self.objects['" + opts['cam'] + "'].hide()\n")
                    outputLines.append("        self.cam = self.objects['" + opts['cam'] + "']\n")
                if opts['defaultSound']:
                    outputLines.append("\n")
                    
                    outputLines.append("        self.defaultSound = loader.loadSfx(self.assets.sounds['" + opts['defaultSound'] + "'])\n")
                    outputLines.append("        self.defaultSound.setLoop(True)\n")
                    outputLines.append("        self.defaultSound.play()\n\n")
                
                if opts['loadScreen']:
                    outputLines.append("\n        loadScreen.destroy()\n")
            else:
                outputLines.append(line)

        f = open(file, 'w')
        f.writelines(outputLines)
        f.close()
        
        batFile = os.path.join(os.path.dirname(file), 'runWorld.bat')
        f = open(batFile, 'w')
        f.write('python "' + os.path.basename(file) + '"')
        f.close()
        
    
    def exportBVW(self, opts):
        
        file = opts['path']
        #write out the level file
        lines = []
        lines.append("# WARNING: modify this code at your own risk\n")
        lines.append("# This code will be overwritten if the project from which it was generated is exported again\n")
        lines.append("from pandac.PandaModules import *\n")
        lines.append("from direct.actor.Actor import Actor\n")
        lines.append("from direct.ETCleveleditor.Rope import *\n")
        lines.append("\n")
        lines.extend(self.editor.objectMgr.BVWEncode())
        lines.append("\n")
        lines.extend(self.editor.soundMgr.BVWEncode())
        f = open(file, 'w')
        f.writelines(lines)
        f.close()
        
        mainFile = os.path.join(os.path.dirname(file), 'main.py')
        if not os.path.exists(mainFile):
            # write out the main file
           
            templateFile = open('ExportTemplate.py')
            
            lines = templateFile.readlines()
            outputLines = []
            if opts['loadScreen']:
                outputLines.append("from direct.gui.OnscreenImage import OnscreenImage\n")
            
            for line in lines:
                if line.startswith('SCENE_FILE'):
                    pass
                elif line.startswith('LIBRARY_INDEX'):
                    pass
                elif line.startswith("from direct.ETCleveleditor"):
                    outputLines.append("level = __import__('" + os.path.basename(file).split('.')[0] + "')\n")
                    
                elif line.find('LevelLoader.loadLevel') != -1:
                    outputLines.append("        self.objects, self.sequences = level.loadLevel()\n")
                    outputLines.append("        self.sounds = level.loadSounds()\n")
                elif line.startswith('HEIGHT'):
                    outputLines.append(line.replace('None', str(opts['camHeight'])))
                elif line.startswith('CAM_MOVE_SPEED'):
                    outputLines.append(line.replace('None', str(opts['camSpeed'])))
                elif line.strip().startswith('ShowBase.__init__'):
                    outputLines.append(line)
                    
                    if opts['loadScreen']:
                        path = base.le.lib.textures[ opts['loadScreen'] ].filename.getFullpath()
                        outputLines.append("\n        loadScreen = OnscreenImage(image = '" + path + "')\n")
                        outputLines.append("        taskMgr.step()\n")
                        outputLines.append("        taskMgr.step()\n")
                
                elif line.strip().startswith('self.cTrav = '):
                    outputLines.append(line)
                    if opts['camPusher']:
                        outputLines.append("\n        cameraSphere = CollisionNode('cameraSphere')\n")
                        outputLines.append("        cameraSphere.addSolid(CollisionSphere(Point3(0, 0, 0), 1))\n")
                        outputLines.append("        self.cameraCollide = self.cam.attachNewNode(cameraSphere)\n")
                        outputLines.append("        self.cameraPusher = CollisionHandlerPusher()\n")
                        outputLines.append("        self.cTrav.addCollider(self.cameraCollide, self.cameraPusher)\n")
                        outputLines.append("        self.cameraPusher.addCollider(self.cameraCollide, self.cam)\n")
                    if opts['useSceneBG']:
                        outputLines.append("\n")
                        outputLines.append("        base.setBackgroundColor(" + str(base.getBackgroundColor()) + ")\n")
                        outputLines.append("\n")
                    if opts['cam']:
                        outputLines.append("\n")
                        outputLines.append("        # Set the camera's properties from the camera in the level editor scene\n")
                        outputLines.append("        self.cam.reparentTo(self.objects['" + opts['cam'] + "'].getParent())\n")
                        outputLines.append("        self.cam.setMat(self.objects['" + opts['cam'] + "'].getMat())\n")
                        outputLines.append("        self.cam.wrtReparentTo(self.objects['" + opts['cam'] + "'])\n")
                        outputLines.append("        self.cam.node().setLens(self.objects['" + opts['cam'] + "'].node().getLens())\n")
                        outputLines.append("        self.camLens = self.cam.node().getLens()\n")
                        outputLines.append("        self.objects['" + opts['cam'] + "'].hide()\n")
                        outputLines.append("        self.cam = self.objects['" + opts['cam'] + "']\n")
                    if opts['defaultSound']:
                        outputLines.append("\n")
                        path = base.le.lib.sounds[opts['defaultSound']].filename.getFullpath()
                        outputLines.append("        self.defaultSound = loader.loadSfx('" + path + "')\n")
                        outputLines.append("        self.defaultSound.setLoop(True)\n")
                        outputLines.append("        self.defaultSound.play()\n\n")
                    
                    if opts['loadScreen']:
                        outputLines.append("\n        loadScreen.destroy()\n")
                else:
                    outputLines.append(line)
                
            f = open(mainFile, 'w')
            f.writelines(outputLines)
            f.close()
        
            batFile = os.path.join(os.path.dirname(mainFile), 'runWorld.bat')
            f = open(batFile, 'w')
            f.write('python "' + os.path.basename(mainFile) + '"')
            f.close()

    def exportGame(self, opts):
        file = opts['path']
        #print file
        #print opts
        #print os.getcwd()
        
        templateFile = open('ExportGameTemplate.py')
        
        #print base.le.currentProj.dir
        #copy the LEGame Assets to the project folder
        dest = Filename(Filename.fromOsSpecific(file).getDirname()+'/LEGameAssets').toOsSpecific()#base.le.currentProj.dir.toOsSpecific()
        src = "./LEGameAssets"#Filename.fromOsSpecific(os.getcwd()).getFullpath()+'/LEGameAssets'
        
        
        scriptsFilename = self.exportScripts(file)

        #if os.path.exists(dest):
        #    shutil.rmtree(dest)
            
        if not os.path.isdir(dest):
        #shutil.rmtree(dest)
            shutil.copytree(src,dest)# dst, symlinks, ignore)base.le.currentProj.dir#.toOsSpecific()
        
        dest = Filename(Filename.fromOsSpecific(file).getDirname()+'/particles').toOsSpecific()
        src = "./particles"
        
        if not os.path.isdir(dest):
        #shutil.rmtree(dest)
            shutil.copytree(src,dest)
        
#        shutil.copy("./ConversationLine.py",dest)
#        shutil.copy("./Conversation.py",dest)
#        shutil.copy("./ConversationMgr.py",dest)
#        shutil.copy("./ConversationMgrBase.py",dest)
#        shutil.copy("./ConversationUI.py",dest)
#        shutil.copy("./JournalUI.py",dest)
#        shutil.copy("./JournalMgr.py",dest)
#        shutil.copy("./JournalMgrBase.py",dest)
#        shutil.copy("./JournalEntry.py",dest)
#        shutil.copy("./GameplayUI.py",dest)
#        shutil.copy("./UIBase.py",dest)
        
        lines = templateFile.readlines()
        outputLines = []
        
        if opts['loadScreen']:
                outputLines.append("from direct.gui.OnscreenImage import OnscreenImage\n")
        
        for line in lines:
            if line.startswith('SCENE_FILE'):
                outputLines.append(line.replace('None',\
                "'" + self.editor.currentProj.getOpeningScene().getFullpath() + "'"))
            elif line.startswith('LIBRARY_INDEX'):
                outputLines.append(line.replace('None',\
                "'lib.index'"))
            elif line.startswith('JOURNAL_FILE'):
                outputLines.append(line.replace('None',\
                 "'" + self.editor.currentProj.journalFilename.getFullpath() + "'"))
            elif line.startswith('INVENTORY_FILE'):
                outputLines.append(line.replace('None',\
                 "'" + self.editor.currentProj.inventoryMapFilename.getFullpath() + "'"))
            elif line.startswith('GAMEPLAY_FOLDER'):
                filename = Filename.fromOsSpecific("'" + os.getcwd()+ "'")
                outputLines.append(line.replace('None',\
                filename.getFullpath()))
            elif line.startswith('SCRIPTS_FILE'):
                outputLines.append(line.replace('None',\
                 "'" + scriptsFilename.getBasename () + "'"))
                outputLines.append('\nfrom '+scriptsFilename.getBasenameWoExtension()+' import *\n')
            elif line.strip().startswith('ShowBase.__init__'):
                    outputLines.append(line)
                    
                    if opts['loadScreen']:
                        path = base.le.lib.textures[ opts['loadScreen'] ].filename.getFullpath()
                        outputLines.append("\n        self.loadScreen = OnscreenImage(image = '" + path + "')\n")
                        outputLines.append("        self.loadScreen.reparentTo(render2d)\n")
                        outputLines.append("        taskMgr.step()\n")
                        outputLines.append("        taskMgr.step()\n")
                        outputLines.append("        self.accept(\"enter\",self.destroyLoadScreen)")
                    else:
                        #TODO: Change this back later
                        pass
                        #outputLines.append("\n        self.gameplayUI = GameplayUI(self)")
            elif line.strip().startswith('def loadScenes(self):'):
                outputLines.append(line)
                for s in self.editor.currentProj.scenes.keys():
                    outputLines.append("\n        self.scenes['"+s+"'] = '"+\
                                       self.editor.currentProj.scenes[s].getFullpath()+"'")
                outputLines.append("\n")
            else:
                outputLines.append(line)
        
        f = open(file, 'w')
        f.writelines(outputLines)
        f.close()
        
        batFile = os.path.join(os.path.dirname(file), 'runWorld.bat')
        f = open(batFile, 'w')
        f.write('python "' + os.path.basename(file) + '"')
        #f.write('\npause')
        f.close()
        
    def exportScripts(self, file):
        outputLines = []
        tab = "    "
        outputLines.append("SCRIPTS_LIST = []\n\n")
        #whole file
        for script, asset in self.editor.lib.scripts.iteritems():
            
            #writing a script file to the whole file
            filename = self.editor.lib.scripts[script].getFullFilename()
            scriptFile = open(filename.toOsSpecific())
            
            lines = scriptFile.readlines()
            
            mainArguments = self.getArgumentsFromScriptFile(lines)
            scriptFunctionName = script
            if(len(mainArguments) == 0):
                prefix = "world"
            else:
                prefix = "world, "
            functionHeader = "\ndef "+scriptFunctionName+"("+prefix+",".join(mainArguments)+"):\n"
            mainFunc = "main("+prefix+",".join(mainArguments)+")"
            mainFuncHeader = "def "+mainFunc+":\n"
            outputLines.append(functionHeader)
            isReturn = False
            for line in lines:
                #print line
                if line.strip().startswith("#"):
                    continue
                if line.strip().startswith("def main"):
                    newline = mainFuncHeader
                elif line.find("Interface")!=-1:
                    newline = line.replace('Interface', "world.scriptInterface")
                else:
                    newline = line
                if line.strip().startswith("return"):
                    isReturn = True
                outputLines.append(tab+newline)
            
            if(isReturn):   
                outputLines.append("\n"+tab+"return "+mainFunc)
            else:
                outputLines.append("\n"+tab+mainFunc)
            outputLines.append("\nSCRIPTS_LIST.append("+scriptFunctionName+")\n")
            scriptFile.close()
        scriptsFilename = Filename(Filename.fromOsSpecific(file).getDirname()+'/Scripts.py')
        
        
        
        
                                     
        try:
            scriptsFile = open(scriptsFilename.toOsSpecific(), 'w')
        except IOError:
            print "ERROR: Couldn't open the script file for writing"
        
        scriptsFile.writelines(outputLines)
        scriptsFile.close()
        return scriptsFilename
                
    #TODO:Similar function is in the script Panel, maybe make this a general function
    def getArgumentsFromScriptFile(self, scriptLines):        
        lines = scriptLines
        mainLine = None
        for line in lines:
            strippedLine = line.strip()

            if(strippedLine.startswith("def main")):
                mainLine = line
        
        start = mainLine.find('(')+1
        end = mainLine.find(')')
        
        argumentsText = mainLine[start:end]
        
        if(mainLine.find(',')==-1):
            arguments = str(argumentsText).strip()
            if(arguments == ""):
                return []
        
        arguments = [str(v).strip() for v in mainLine[start:end].split(',')]
        return arguments
        
        