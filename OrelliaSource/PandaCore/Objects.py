from pandac.PandaModules import *
from direct.actor.Actor import Actor
from Shaders import *
from Util import *
import copy
from Rope import *
from Scriptable import * 
from Particle import *
import os

import Debug
#import Library
from Sound import *

"""
This class represents a base object, or a NodePath,
for the Panda3d level editor, designed at the ETC.

If no nodePath is passed to the constructor of this class,
the object created is a dummy, or empty, node.
"""
class Object(Scriptable, ParticleHolder):
    def __init__(self, name="", type="dummy", nodePath=None, parent=None, inEditor=True):
        Scriptable.__init__(self)
        # Set the nodepath
        if nodePath == None:
            # If no nodepath is passed, create a dummy node
            # with the given name
            self.nodePath = NodePath(PandaNode(name))
        else:
            # Otherwise, set the nodepath to be the passed nodepath
            self.nodePath = nodePath
            # and set the nodepath's name
            self.nodePath.setName(name)
        
        # If the type is a dummy node
        if type == "dummy" and inEditor:
            # Load a virtual representation of an empty node
            model = loader.loadModel("models/dummy_box")
            model.setScale(0.5,0.5,0.5)
            model.setRenderModeWireframe()
            model.setLightOff()
            # Hide the dummy node from instantiated cameras
            model.hide(BitMask32.bit(5))
            # Attach it to the nodepath
            model.reparentTo(self.nodePath)
            model.setTag("LEObjRep", "")    #So we know not to copy this
            
            
        self.type = type
        self.name = name
        self.shader = None
        self.particleEffectList = [] #qiaosi
        self.particleList = [] #qiaosi
        self.nodePath.setShaderAuto()
        # Set the parent
        if parent != None:
            self.nodePath.reparentTo(parent)
        else: 
            self.nodePath.reparentTo(render)
        
        #keys are texture stage for which textures have been set,
        #values are texture assets set on that stage
        self.texSwaps = {}
        
        #set of all lights that reference this node
        self.lights = set()
        
        #holds the scripts and their parameters as tuple that are attached to this object.
        #The keys are the trigger types
        #self.scripts = {}
        #self.scriptCounter = 0
        
    #returns a copy of the object, but does not handle parenting
    #does not copy children or their nodepaths
    #object is automatically added to the scene, but not objectMgr or scene graph UI
    def __copy__(self):
        newNP = copy.copy(self.nodePath)

        for child in newNP.getChildren():
            #remove children
            if child.hasTag('OBJRoot'):
                child.removeNode()
            elif child.hasTag('LEObjRep'):
                child.removeNode()
            #don't copy bounding box
            elif child.getName() == 'bboxLines':
                child.removeNode()
            #qiaosi------ don't copy the particle render parents
            elif child.getName () == 'particleRenderParents':
                child.removeNode()
        
        newObj = Object(copy.copy(self.name), copy.copy(self.type), newNP, None, True)
        if self.shader:
            newObj.useShader(copy.copy(self.shader))
            if self.shaderActive:
                newObj.applyShader()
        
        newObj.texSwaps = copy.copy(self.texSwaps)
        newObj.lights = copy.copy(self.lights)
        #newObj.scripts = copy.copy(self.scripts)
        newObj.scriptCounter = copy.copy(self.scriptCounter)
        
        #qiaosi-------------   
        if self.particleList != []:
            for p in self.particleList:
                newObj.addParticleEffect(p.configFile, p.position, p.scale)
        #---------------------
        
        return newObj        
    
    #decodes the object from an xml node
    def decode(node, nodePath=None, inEditor=True, lib=None):
        tags = {}
        texSwaps = {}
        scripts = []
        transparency = None
        hidden = False
        twoSided = False
        shader = None
        particleList = []
        for n in node.childNodes:
            if n.localName == "name":
                name = n.childNodes[0].data.strip()
            elif n.localName == "parent":
                parent = n.childNodes[0].data.strip()
            elif n.localName == "pos":
                pos = decodeVec3(n)
            elif n.localName == "scale":
                scale = decodeVec3(n)
            elif n.localName == "hpr":
                hpr = decodeVec3(n)
            elif n.localName == "shear":
                shear = decodeVec3(n)
            elif n.localName == "colorScale":
                colorScale = decodeColor(n)
            elif n.localName == "tag":
                key, value = decodeBaseTag(n)
                tags[key] = value
            elif n.localName == "transparency":
                transparency = int(n.childNodes[0].data.strip())
            elif n.localName == "texture":
                texture = n.childNodes[0].data.strip()
            elif n.localName == "normalMap":
                normalMap = n.childNodes[0].data.strip()
            elif n.localName == "Shader":
                shader = LEShader.decode(n, lib=lib)
            elif n.localName == "twoSided":
                twoSided = bool(int(n.childNodes[0].data.strip()))
            elif n.localName == "hidden":
                hidden = bool(int(n.childNodes[0].data.strip()))
            elif n.localName == "collideMask":
                collideMask = int(n.childNodes[0].data.strip())
            elif n.localName == "texSwap":
                for n2 in n.childNodes:
                    if n2.localName == "stage":
                        stageName = n2.childNodes[0].data.strip()
                    elif n2.localName == "texture":
                        textureName = n2.childNodes[0].data.strip()
                    
                texSwaps[stageName] = textureName
            elif n.localName =="script":
                    arguments = []
                    for n2 in n.childNodes:
                        if n2.localName == "triggerType":
                            triggerType = n2.childNodes[0].data.strip()
                        elif n2.localName == "scriptName":
                            scriptName = n2.childNodes[0].data.strip()
                        elif n2.localName == "parameter":
                            parameter = n2.childNodes[0].data.strip()
                            arguments.append(str(parameter))
                    #print triggerType, " ", scriptName
                    scripts.append((triggerType,scriptName,arguments))
#           #qiaosi
            elif n.localName == "particleList":
                for n2 in n.childNodes:
                    if n2.localName == "particle":
                        particleList.append(Particle.decode(n2))
            #-------------------------------    
                
        obj = Object(name, node.localName, nodePath, inEditor=inEditor)
        obj.parentName = parent
        obj.setPos(pos)
        obj.setScale(scale)
        obj.setHpr(hpr)
        obj.setShear(shear)
        obj.setColorScale(colorScale)
        obj.lights = set()

        for k,v in tags.iteritems():
            obj.setTag(k,v)
        
        for s in scripts:
            triggerType, scriptName, arguments = s
            id = obj.addScript(triggerType, scriptName)
            obj.setScriptArguments(triggerType, id, arguments) 

        for s, t in texSwaps.iteritems():
            stage = obj.nodePath.findTextureStage(s)
            texAsset = lib.textures[t]
            tex = loader.loadTexture(texAsset.getFullFilename())
            obj.nodePath.setTexture(stage, tex, 1)
            obj.texSwaps[stage] = texAsset
            
#        if transparency:
#            obj.setTransparency(transparency)
        
        
        #qiaosi--------------------------
        if particleList != []:
            for p in particleList:
                obj.addParticleEffect(p.configFile, p.position, p.scale)
        #-------------------------------
        
        if shader:
            obj.shader = shader
            obj.shaderActive = False
        
        if hidden:
            obj.nodePath.hide()
            
        if twoSided:
            obj.nodePath.setTwoSided(twoSided)
        
        return obj
            
                
    decode = staticmethod(decode)
    
    #encodes the object as xml
    def encode(self, doc):
        node = doc.createElement(self.type)
        
        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(self.name))
        node.appendChild(name)
        
        parent = doc.createElement("parent")
        parentName = self.nodePath.getParent().getName()
        #avoids conflict if someone decides it's a good idea to name one of their objects render
        if parentName == "render":
            parentName = "*render"
        elif parentName.find(" <joint>") != -1:
            parentName = self.nodePath.getParent().getParent().getName()+"/"+parentName
        parent.appendChild(doc.createTextNode(parentName))
        node.appendChild(parent)
        
        pos = encodeVec3(self.getPos(), "pos", doc)
        node.appendChild(pos)
        
        scale = encodeVec3(self.getScale(), "scale", doc)
        node.appendChild(scale)
        
        hpr = encodeVec3(self.getHpr(), "hpr", doc)
        node.appendChild(hpr)
        
        shear = encodeVec3(self.getShear(), "shear", doc)
        node.appendChild(shear)
        
        colorScale = encodeColor(self.getColorScale(), "colorScale", doc)
        node.appendChild(colorScale)
        
        #Is this really the easiest way to list all of the tags of a node?
        #Seriously, Panda, this is ridiculous
        stream = StringStream()
        self.nodePath.node().listTags(stream, ' ')
        tags = stream.getData().split()
        for key in tags:
            value = self.nodePath.getTag(key)
            tag = encodeBaseTag((key,value), "tag", doc)
            node.appendChild(tag)
            
        transparency = doc.createElement("transparency")
        transparency.appendChild(doc.createTextNode(str(self.nodePath.getTransparency())))
        node.appendChild(transparency)
        
        if self.nodePath.getTwoSided():
            twoSided = doc.createElement("twoSided")
            twoSided.appendChild(doc.createTextNode(str(self.nodePath.getTwoSided())))
            node.appendChild(twoSided)
        
        if self.nodePath.isHidden():
            hidden = doc.createElement("hidden")
            hidden.appendChild(doc.createTextNode(str(self.nodePath.isHidden())))
            node.appendChild(hidden)
        
        if self.shader:
            node.appendChild(self.shader.encode(doc))
        
        for stage, texAsset in self.texSwaps.iteritems():
            texSwap = doc.createElement("texSwap")
            stageNode = doc.createElement("stage")
            stageNode.appendChild(doc.createTextNode(stage.getName()))
            texSwap.appendChild(stageNode)
            texNode = doc.createElement("texture")
            texNode.appendChild(doc.createTextNode(texAsset.name))
            texSwap.appendChild(texNode)
            
            node.appendChild(texSwap)
        
        for triggerType, scriptTuples in self.scripts.iteritems():
            for scriptID in sorted(scriptTuples):
                script = doc.createElement("script")
                triggerTypeNode = doc.createElement("triggerType")
                triggerTypeNode.appendChild(doc.createTextNode(triggerType))
                script.appendChild(triggerTypeNode)
                
                scriptName, scriptArguments = scriptTuples[scriptID]
                scriptNameNode = doc.createElement("scriptName")
                script.appendChild(scriptNameNode)
                scriptNameNode.appendChild(doc.createTextNode(scriptName))
                temp = []
                for argument in scriptArguments:
                    scriptArgument = doc.createElement("parameter")
                    scriptArgument.appendChild(doc.createTextNode(str(argument)))
                    script.appendChild(scriptArgument)
                      
                node.appendChild(script)
                
        #qiaosi--------------------------------
        if self.particleList != []:       
            particles = doc.createElement("particleList")
            for p in self.particleList:
                particles.appendChild(p.encode(doc)) 
            node.appendChild(particles)
        #----------------------------------    
        
        return node       
    
    #encode the object as python code
    def BVWEncode(self):
        lines = []
        
        if self.type == "dummy":
            lines.append("    objects['" + self.name + "'] = NodePath(PandaNode('" + self.name + "'))\n")
        
        if self.nodePath.getParent() == render:
            lines.append("    objects['" + self.name + "'].reparentTo(render)\n")
        
        lines.append("    objects['" + self.name + "'].setName('" + self.name + "')\n")
        lines.append("    objects['" + self.name + "'].setPos(" + str(self.nodePath.getPos()) + ")\n")
        lines.append("    objects['" + self.name + "'].setHpr(" + str(self.nodePath.getHpr()) + ")\n")
        lines.append("    objects['" + self.name + "'].setScale(" + str(self.nodePath.getScale()) + ")\n")
        lines.append("    objects['" + self.name + "'].setColorScale(" + str(self.nodePath.getColorScale()) + ")\n")
        
        stream = StringStream()
        self.nodePath.node().listTags(stream, ' ')
        tags = stream.getData().split()
        for key in tags:
            value = self.nodePath.getTag(key)
            lines.append("    objects['" + self.name + "'].setTag('" + key + "', '" + value + "')\n")
        
        if self.nodePath.getTwoSided():
            lines.append("    objects['" + self.name + "'].setTwoSided(True)\n")
        
        if self.nodePath.isHidden():
            lines.append("    objects['" + self.name + "'].hide()\n")
        
        for stage, tex in self.texSwaps.iteritems():
            lines.append("    tex = loader.loadTexture('" + tex.filename.getFullpath() + "')\n")
            lines.append("    texStage = objects['" + self.name + "'].findTextureStage('" + stage.getName() + "')\n")
            lines.append("    objects['" + self.name + "'].setTexture(texStage, tex, 1)\n")
        
        return lines
    
    #This method should be overridden to handle anything that needs to be done when an object is added to the scene
    # (e.g., updating refCounts)
    def onAdd(self):
        if self.shader:
            self.shader.incRefCounts()
        for l in self.lights:
            l.addTarget(self)
    
    #This method should be overrriden to handle anything that needs to be done when an object is removed from the scene
    # (e.g., updating refCounts, clearing lights)
    def onRemove(self):
        if self.shader:
            self.shader.decRefCounts()
        
        for l in self.lights:
            l.removeTarget(self, fromRemove=True)
    
    #This method should be overridden to handle anything that needs to be done when an object is being
    #re-added to the scene (for undoing a delete)
    #(also used when an object is duplicated)
    def reattach(self):
        for l in self.lights:
            l.addTarget(self)
        
    ## Accessors and Mutators
    
    # NodePath
    def getNodePath(self):
        return self.nodePath
    
    # Name
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        self.nodePath.setName(name)
    
    # Type
    def getType(self):
        return self.type
    
    # Net Tag
    ## returns string
    def getNetTag(self, key):
        return self.nodePath.getNetTag(key)
    
    ## returns NodePath
    def findNetTag(self, key):
        return self.nodePath.findNetTag(key)
    
    ## returns Boolean
    def hasNetTag(self, key):
        return self.nodePath.hasNetTag(key)
    
    # Tag
    # returns boolean
    def hasTag(self, key):
        return self.nodePath.hasTag(key)
    
    def setTag(self, key, val):
        self.nodePath.setTag(key, val)
    
    def getTag(self, key):
        return self.nodePath.getTag(key)
    
#    def addScript(self,triggerName, scriptName):
#        if(self.scripts.has_key(triggerName)==False):
#            self.scripts[triggerName] = {}
#        temp = (scriptName, [] )
#        #if(len(self.scripts[triggerName])<=scriptNo):
#        #    self.scripts[triggerName][self.scriptCounter] = (temp)
#        #else:
#        self.scripts[triggerName][self.scriptCounter] = temp
#        counter = self.scriptCounter
#        self.scriptCounter += 1
#        
#        return counter
#        #else:
#        #    self.
#        #self.scripts[triggerName] = scriptName
#    def setScript(self, triggerName, scriptID,  scriptName, arguments =[]):
#        self.scripts[triggerName][scriptID] = (scriptName, arguments)
#        
#    def setScriptArguments(self, triggerName, scriptID,arguments):
#        scriptName, values = self.scripts[triggerName][scriptID]
#        self.scripts[triggerName][scriptID] = (scriptName, arguments)
#    
#    def getScriptsAndArguments(self, triggerName):
#        return self.scripts[triggerName]
#    
#    def getScriptArguments(self, triggerName, scriptID):
#        scriptName, arguments =  self.scripts[triggerName][scriptID]
#        return arguments
#    
#    def removeScript(self, triggerName, scriptNo):
#        if self.scripts.has_key(triggerName) == False:
#            print "Trigger name with ", triggerName, " doesn't exist!"
#            return False
#        #print self.scripts[triggerName][scriptNo]
#        del self.scripts[triggerName][scriptNo]
#        if(len(self.scripts[triggerName]) == 0):
#            del self.scripts[triggerName]
#        return True
    
    def clearTag(self, key):
        self.nodePath.clearTag(key)
    
    #returns a dictionary of tags on this object
    def getAllTags(self):
        tagDict = {}
        stream = StringStream()
        self.nodePath.node().listTags(stream, ' ')
        tags = stream.getData().split()
        for key in tags:
            tagDict[key] = self.nodePath.getTag(key)
        
        return tagDict
    
    def renameTag(self, oldName, newName):
        value = self.nodePath.getTag(oldName)
        self.nodePath.clearTag(oldName)
        self.nodePath.setTag(newName, value)
    
    # Position
    def getPos(self, *args, **kargs):
        return self.nodePath.getPos(*args, **kargs)
    
    ## ## Accepts the position as an LVecBase3f
    def setPos(self, *args, **kargs):
        self.nodePath.setPos(*args, **kargs)
    
    # Rotation (heading, pitch, and roll)
    
    def getHpr(self, *args, **kargs):
        return self.nodePath.getHpr(*args, **kargs)
    
    ## Accepts hpr as an LVecBase3f or a constant
    def setHpr(self, *args, **kargs):
        self.nodePath.setHpr(*args, **kargs)
    
    # Scale
    
    def getScale(self, *args, **kargs):
        return self.nodePath.getScale(*args, **kargs)
    
    ## Set a uniform scale, or an LVecBase3f scale
    def setScale(self, *args, **kargs):
        self.nodePath.setScale(*args, **kargs)
    
    ## # Shear
    
    def getShear(self):
        return self.nodePath.getShear()
    
    def setShear(self, shear):
        self.nodePath.setShear(shear)
    
    # Color Scale
    
    def getColorScale(self):
 
        return self.nodePath.getColorScale()
    
    ## or with an LVecBase4f
    def setColorScale(self, color):

        self.nodePath.setColorScale(color)
    ##Sets the rendering transparency for the given node
    

    #sets a shader but does not actually start using it yet
    def useShader(self, shader):
        if shader != self.shader:
            if self.shader:
                self.shader.decRefCounts()
            self.shader = shader
            self.shaderActive = False
            shader.incRefCounts()
    
    #removes any custom shaders from the object and uses the autoshader
    def useAutoShader(self):
        if self.shader:
            self.shader.decRefCounts()
            for k in self.shader.inputs.keys():
                self.nodePath.clearShaderInput(k)
        
        self.nodePath.setShaderAuto()
        self.shader = None
    
    #actually start using the shader
    def applyShader(self):
        if self.shader:
            self.shader.applyToObject(self)
            self.shaderActive = True
    
    #stops using the custom shader, but does not completely remove it from teh object
    def unapplyShader(self):
        if self.shader:
            for k in self.shader.inputs.keys():
                self.nodePath.clearShaderInput(k)
        
        self.nodePath.setShaderAuto()
        self.shaderActive = False
        self.shader.obj = None
    
    #returns a list of texture assets used by the object
    #'None' indicates a texture that is not part of the library
    def getTexList(self):
        textures = []
        
        np = copy.copy(self.nodePath)
        for child in np.getChildren():
            if child.hasTag('OBJRoot'):
                child.removeNode()
            elif child.hasTag('LEObjRep'):
                child.removeNode()
            elif child.getName() == 'bboxLines':
                child.removeNode()
        
        for texStage in np.findAllTextureStages():
            tex = np.findTexture(texStage)
            texFile = Filename(tex.getFilename())
            if not texFile.makeRelativeTo(base.le.lib.projDir):
                dir = texFile.getDirname()
                texFile.setDirname("Textures" + dir.split("/Textures")[-1])
            try:
                texAsset = base.le.lib.filenameIndex[texFile]
            except KeyError:
                texAsset = None
            
            textures.append(texAsset)
        
        return textures
    
    #replaces a texture on the object
    def replaceTexture(self, id, asset):
        count = 0
        newTex = loader.loadTexture(asset.getFullFilename())
        
        np = copy.copy(self.nodePath)
        for child in np.getChildren():
            if child.hasTag('OBJRoot'):
                child.removeNode()
            elif child.hasTag('LEObjRep'):
                child.removeNode()
            elif child.getName() == 'bboxLines':
                child.removeNode()
        
        for texStage in np.findAllTextureStages():
            tex = np.findTexture(texStage)
            if tex:
                if count == id:
                    self.nodePath.clearTexture(texStage)
                    self.nodePath.setTexture(texStage, newTex, 1)
                    if texStage not in self.texSwaps:
                        self.texSwaps[texStage] = asset
                        return (texStage, None)
                    else:
                        oldAsset = self.texSwaps[texStage]
                        self.texSwaps[texStage] = asset
                        return (texStage, oldAsset)
                count += 1 
    
    #resotres the original textures from the egg file
    def clearTextureSwaps(self):
        self.texSwaps = {}
        self.nodePath.clearTexture()
"""
The StaticMesh class inherits from the Object class,
and also has a filePath where its model is located
"""
class StaticMesh(Object):
    def __init__(self, name, asset, parent=None):
        # Create the static mesh node
        model = loader.loadModel(asset.getFullFilename())
        Object.__init__(self, name, "staticmesh", model, parent)
        self.asset = asset  #the mesh asset used to create this object
    
    def getAsset(self):
        return self.asset
    
    def __copy__(self):
        newMesh = Object.__copy__(self)
        newMesh.__class__ = StaticMesh
        newMesh.asset = self.asset
        
        return newMesh
    
    def onAdd(self):
        Object.onAdd(self)
        self.asset.incSceneCount()
        
    def onRemove(self):
        Object.onRemove(self)
        self.asset.decSceneCount()
    
    def decode(node, lib=None):
        for n in node.childNodes:
            if n.localName == "asset":
                assetName = n.childNodes[0].data.strip()
                asset = lib.meshes[assetName]
                
        nodePath = loader.loadModel(asset.getFullFilename())
        obj = Object.decode(node, nodePath, lib=lib)
        obj.__class__ = StaticMesh
        obj.asset = asset
        
        return obj
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        asset = doc.createElement("asset")
        asset.appendChild(doc.createTextNode(self.asset.name))
        node.appendChild(asset)
        
        return node
        
    def BVWEncode(self):
        lines = []
        lines.append("    objects['" + self.name + "'] = loader.loadModel('" + self.asset.filename.getFullpath() + "')\n")
        
        lines.extend(Object.BVWEncode(self))
        
        return lines

"""
The LEActor class inherits from the Object class,
and also has a asset, and a dictionary of animations
"""
class LEActor(Object):
    def __init__(self, name, asset, anims={}, parent=None):
        # Put the anims in the the proper directory
        anims2 = {}
        self.sounds_anims_map={}#added by qiaosi
        
        for n in anims:
            anims2[n] = anims[n].getFullFilename()

        # Create the actor
        actor = Actor(asset.getFullFilename(), anims2)
        Object.__init__(self, name, "actor", actor, parent)
        self.asset = asset  #the actor asset used to create this object
        # Create a blank dictionary that will hold any extra
        # animtions applied to the individual object
        self.extraAnims = {}
        
        # Variables to keep track of posing, looping, and playing
        self.looping = False
        self.playing = False
        self.posed = False
        self.frame = 0
        
        # Current Animation
        self.currentAnim = None
        
        # Playrate
        self.playRate = 1.0
        
        # Joints
        self.joints = {}
    
    def __copy__(self):
        newActor = Object.__copy__(self)
        newActor.__class__ = LEActor
        newActor.nodePath.removeNode()
        newActor.nodePath = Actor()
        newActor.nodePath.copyActor(self.nodePath, True)
        for child in newActor.nodePath.getChildren():
            #remove children
            if child.hasTag('OBJRoot'):
                child.removeNode()
            #remove anything parented to joints
            elif child.getName().find(" <joint>") !=-1:
                for c in child.getChildren():
                    c.removeNode()
            #don't copy bounding box
            elif child.getName() == 'bboxLines':
                child.removeNode()
        currentAnim = self.nodePath.getCurrentAnim()
        if self.looping:
             newActor.nodePath.loop(currentAnim)
             newActor.nodePath.setPlayRate(self.nodePath.getPlayRate(currentAnim), currentAnim)
        elif self.playing:
            newActor.nodePath.play(currentAnim, fromFrame=self.nodePath.getCurrentFrame())
            newActor.nodePath.setPlayRate(self.nodePath.getPlayRate(currentAnim), currentAnim)
        elif self.posed:
            newActor.nodePath.pose(currentAnim, self.nodePath.getCurrentFrame())
            
        newActor.nodePath.setName(newActor.name)
        
        newActor.asset = self.asset
        newActor.extraAnims = copy.copy(self.extraAnims)
        newActor.playing = self.playing
        newActor.posed = self.posed
        newActor.frame = self.frame
        newActor.looping = self.looping
        newActor.currentAnim = self.currentAnim
        newActor.playRate = self.playRate
        newActor.joints = {}
        for key, joint in self.joints.iteritems():
            np = newActor.nodePath.find(joint.joint.getName())
            if joint.type == "exposed":
                newActor.addExposedJoint(key, np)
            else:
                newActor.addControlledJoint(key, np)
    
        #[antonjs 4/4/11] Added...this was causing problems on project save when duplicating an actor in LE and sound info didn't come with it
        newActor.sounds_anims_map = self.sounds_anims_map.copy()
    
        return newActor
   
    def onAdd(self):
        Object.onAdd(self)
        self.asset.incSceneCount()
        for a in self.extraAnims.values():
            a.incSceneCount()
    
    def onRemove(self):
        Object.onRemove(self)
        self.asset.decSceneCount()
        for a in self.extraAnims.values():
            a.decSceneCount()
    
   ## Mutators and Accessors
    
    def addExposedJoint(self, key, np):
        joint = Joint(np,"exposed")
        self.joints[key] = joint
        base.le.ui.sceneGraphUI.addJoint(joint.getNodePath(), np.getParent())
    
    def addControlledJoint(self, key, np):
        joint = Joint(np,"controlled")
        self.joints[key] = joint
        base.le.ui.sceneGraphUI.addJoint(joint.getNodePath(), np.getParent())
    
    def removeJoint(self, jointName, np):
        # Remove from the scenegraphui
        base.le.ui.sceneGraphUI.removeJoint(jointName, self.joints[jointName])
        # Remove from the list
        del self.joints[jointName]
    
    def reattachJoint(self, key, joint):
        self.joints[key] = joint
        base.le.ui.sceneGraphUI.addJoint(joint.joint, joint.joint.getParent())
    
    def setLooping(self):
        self.looping = True
        self.playing = False
        self.posed = False
        
    
    def setPlaying(self):
        self.looping = False
        self.playing = True
        self.posed = False
    
    def setPosed(self, frame):
        self.posed = True
        self.frame = frame
        self.playing = False
        self.looping = False
    
    def getAsset(self):
        return self.asset
    
    def getAnims(self):
        return copy.copy(self.asset.anims)
    
    def getExtraAnims(self):
        return copy.copy(self.extraAnims)
    
    def getAllAnims(self):
        # Merge the dictionaries
        anims = copy.copy(self.asset.anims)
        anims.update(self.extraAnims)
        return anims
    
    def addExtraAnim(self, anim):
        # Add it to the actor's animations
        anim.incSceneCount()
        self.getNodePath().loadAnims({anim.name:anim.getFullFilename()})
        self.extraAnims[anim.name] = anim
    
    # added by qiaosi
# this one use mapping of sound names and animations names, an editor instance should be passed to the function to get the sound from SoundMrg
# the good thing for this is that you can hold the sound's name
#    def getSoundOfAnim(self, anim, editor):
#        if self.sounds_anims_map != {}:
#            anim_fullname = self.getAnims()[anim].getFullFilename()# get the full name of the animation
#            for key in self.sounds_anims_map.keys():
#                if key == anim_fullname:
#                    sound_for_anim = self.sounds_anims_map[anim_fullname]
#                    sound = editor.soundMgr.sounds[sound_for_anim]
#                    return sound
#        else:
#            return None
# this one use mapping of sound instances and animations names
# the good thing is that you don't need to have the editor instance, but you don't know the name of the sound
    def getSoundOfAnim(self,anim):
        if self.sounds_anims_map != {}:
             #anim_fullname = self.getAllAnims()[anim].getFullFilename()# get the full name of the animation
             for key in self.sounds_anims_map.keys():
                 if key == anim:
                     sound = self.sounds_anims_map[anim]
                     return sound
        else:
            return None
    
    def playSoundOfAnim(self,anim):
        sound  = self.getSoundOfAnim(anim)
        if sound != None :
            sound.setLoop(False)
            sound.play()
            
    def loopSoundOfAnim(self,anim):
        sound  = self.getSoundOfAnim(anim)
        if sound != None :
            sound.setLoop(True)
            sound.play()
    
    def stopSoundOfAnim(self,anim):
        sound  = self.getSoundOfAnim(anim)
        if sound != None :
            sound.setLoop(False)
            sound.stop()
            
            
    def createSoundOfAnimInGame(self, anim, soundName, lib):
        sound_asset = lib.sounds[soundName]
        soundObj = Sound(soundName, sound_asset)
        self.sounds_anims_map[anim] = soundObj

    def createSoundOfAnimInLE(self, anim, soundName):
        #soundObj = base.le.soundMgr.sounds[soundName] 
        self.sounds_anims_map[anim]= soundName
    #----------------------------------------------------
    def BVWEncode(self):
        lines = []
        
        animsDict = {}
        for key, value in self.getAllAnims().iteritems():
            animsDict[key] = value.filename.getFullpath()
        
        lines.append("    objects['" + self.name + "'] = Actor('" + self.asset.filename.getFullpath() + "', " + str(animsDict) + ")\n")
        
        lines.extend(Object.BVWEncode(self))
        
        if self.posed:
            lines.append("    objects['" + self.name + "'].pose('" + self.currentAnim + "', " + str(self.frame) + ")\n")
        elif self.playing:
            lines.append("    objects['" + self.name + "'].play('" + self.currentAnim + "')\n")
            lines.append("    objects['" + self.name + "'].setPlayRate(" + str(self.playRate) + ", '" + self.currentAnim + "')\n")
        elif self.looping:
            lines.append("    objects['" + self.name + "'].loop('" + self.currentAnim + "')\n")
            lines.append("    objects['" + self.name + "'].setPlayRate(" + str(self.playRate) + ", '" + self.currentAnim + "')\n")
        
        for j in self.joints.values():
            jointName = j.joint.getName().split(' <')[0]
            lines.append("\n")
            if j.type == "exposed":
                lines.append("    objects['" + self.name + "/" + jointName + "'] = objects['" + self.name + "'].exposeJoint(None, 'modelRoot', '" + jointName + "')\n")
            elif j.type == "controlled":
                lines.append("    objects['" + self.name + "/" + jointName + "'] = objects['" + self.name + "'].controlJoint(None, 'modelRoot', '" + jointName + "')\n")
    
        return lines
        
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        assetNode = doc.createElement("asset")
        node.appendChild(assetNode)
        assetNode.appendChild(doc.createTextNode(self.asset.name))
        
        for localName,asset in self.extraAnims.iteritems():
            animNode = doc.createElement("anim")
            node.appendChild(animNode)
            localNameNode = doc.createElement("localName")
            animNode.appendChild(localNameNode)
            localNameNode.appendChild(doc.createTextNode(localName))
            assetNameNode = doc.createElement("assetName")
            animNode.appendChild(assetNameNode)
            assetNameNode.appendChild(doc.createTextNode(asset.name))
        
        currentAnim = doc.createElement("currentAnim")
        currentAnim.appendChild(doc.createTextNode(str(self.currentAnim)))
            
        isLooping = doc.createElement("isLooping")
        isLooping.appendChild(doc.createTextNode(str(self.looping)))
        
        isPlaying = doc.createElement("isPlaying")
        isPlaying.appendChild(doc.createTextNode(str(self.playing)))
        
        playRate = doc.createElement("playRate")
        playRate.appendChild(doc.createTextNode(str(self.playRate)))
        
        isPosed = doc.createElement("isPosed")
        isPosed.appendChild(doc.createTextNode(str(self.posed)))
        
        frame = doc.createElement("frame")
        frame.appendChild(doc.createTextNode(str(self.frame)))
        
        # added by qiaosi
        if self.sounds_anims_map != {}:
            sounds_anims_map_node = doc.createElement("soundsOfAnimationsList")
            for anim,sound in self.sounds_anims_map.iteritems():
                sound_anim_node = doc.createElement("soundOfAnimation")
                sound_name_node = doc.createElement("soundName")
                sound_name_node.appendChild(doc.createTextNode(str(sound.name)))
                sound_anim_node.appendChild(sound_name_node)
                anim_node = doc.createElement("animationWithSound")
                sound_anim_node.appendChild(anim_node)
                anim_node.appendChild(doc.createTextNode(str(Filename(anim).getBasenameWoExtension())))
                sounds_anims_map_node.appendChild(sound_anim_node)
            node.appendChild(sounds_anims_map_node)  
        #--------------------
        
        for jointName in self.joints:
            node.appendChild(self.joints[jointName].encode(doc))
        
        node.appendChild(currentAnim)
        node.appendChild(isLooping)
        node.appendChild(isPlaying)
        node.appendChild(playRate)
        node.appendChild(isPosed)
        node.appendChild(frame)

            
        return node
        
    def decode(node, lib=None):
        extraAnims = {}
        joints = {}
        sounds_anims_map_temp = {}# added by qiaosi
        soundName = None
        animWithSound = None
        #----------------------------------
        for n in node.childNodes:
            if n.localName == "asset":
                assetName = n.childNodes[0].data.strip()
            elif n.localName == "anim":
                for n2 in n.childNodes:
                    if n2.localName == "localName":
                        localName = n2.childNodes[0].data.strip()
                    elif n2.localName == "assetName":
                        animAssetName = n2.childNodes[0].data.strip()
                extraAnims[localName] = lib.animations[animAssetName]
            elif n.localName == "currentAnim":
                currentAnim = n.childNodes[0].data.strip()
            elif n.localName == "isLooping":
                isLooping = n.childNodes[0].data.strip()
            elif n.localName == "isPlaying":
                isPlaying = n.childNodes[0].data.strip()
            elif n.localName == "isPosed":
                isPosed = n.childNodes[0].data.strip()
            elif n.localName == "frame":
                frame = int(float(n.childNodes[0].data.strip()))
            elif n.localName == "playRate":
                playRate = float(n.childNodes[0].data.strip())
            elif n.localName == "joint":
                name, type = Joint.decode(n,lib=lib)
                joints[name] = type
            elif n.localName == "soundsOfAnimationsList": # added by qiaosi
                for n2 in n.childNodes:
                    if n2.localName == "soundOfAnimation":
                        for n3 in n2.childNodes:
                            if n3.localName == "soundName":
                                soundName = n3.childNodes[0].data.strip()
                                Debug.debug(__name__,str(soundName))
                            elif n3.localName == "animationWithSound":
                                animWithSound = n3.childNodes[0].data.strip()
                                Debug.debug(__name__,str(animWithSound))
                    if soundName != None and animWithSound != None:
                        #soundName = str(soundName)
                        #animWithSound = str(animWithSound)
                        sounds_anims_map_temp[animWithSound]=soundName
                Debug.debug(str(sounds_anims_map_temp))
            #-----------------------------------------------
                    
    
        asset = lib.actors[assetName]
        anims = {}
        for k, v in asset.anims.iteritems():
            anims[k] = v.getFullFilename()
            
        nodePath = Actor(asset.getFullFilename(), anims)
        
        obj = Object.decode(node, nodePath, lib=lib)
        obj.__class__ = LEActor
        obj.asset = asset
        obj.extraAnims = {}
        for a in extraAnims.values():
            obj.addExtraAnim(a)
        
        # Load current animation
        if currentAnim == "None":
            obj.currentAnim = None
        else:
            obj.currentAnim = currentAnim
        obj.frame = frame
        
        obj.playRate = playRate
        
        # Looping, playing, and posing
        if isLooping == "True":
            obj.looping = True
            obj.nodePath.loop(obj.currentAnim)
            obj.nodePath.setPlayRate(playRate, obj.currentAnim)
        else:
            obj.looping = False
        if isPlaying == "True":
            obj.playing = True
            obj.nodePath.play(obj.currentAnim)
            obj.nodePath.setPlayRate(playRate, obj.currentAnim)
        else:
            obj.playing = False
        if isPosed == "True":
            obj.posed = True
            obj.nodePath.pose(obj.currentAnim, obj.frame)
        else:
            obj.posed = False
        
        # Joints
        obj.joints = {}
        for jointName in joints:
            np = None
            if joints[jointName] == "exposed":
                np = obj.nodePath.exposeJoint(None, 'modelRoot', jointName)
            elif joints[jointName] == "controlled":
                np = obj.nodePath.controlJoint(None, 'modelRoot', jointName)
            joint = Joint(np, joints[jointName])
            obj.joints[jointName] = joint
            #base.le.ui.sceneGraphUI.addJoint(joint.getNodePath(), joint.getNodePath().getParent())
        
        #added by qiaosi
        obj.sounds_anims_map={}
        Debug.debug(__name__,"here1"+str(sounds_anims_map_temp))
        if sounds_anims_map_temp != {}:
            for animName,soundName in sounds_anims_map_temp.iteritems():
                #obj.createSoundOfAnimInGame(animName, soundName, lib)
                obj.createSoundOfAnimInLE(animName, soundName)
        #----------------------------------
        return obj
    decode = staticmethod(decode)

"""
The Joint class represents the joint of an actor.
Creating a joint involves passing the nodepath controlled or
exposed joint
"""
class Joint:
    def __init__(self, joint, type):
        self.type = type
        self.joint = joint
        if self.joint.getName().find(" <joint>") == -1:
            self.joint.setName(self.joint.getName()+" <joint>")            
        
    def getNodePath(self):
        return self.joint
    
    def setName(self, name):
        if name.index("<joint>") == -1:
            self.joint.setName(name+" <joint>")
        else:
            self.joint.setName(name)
    
    def getName(self):
        return self.joint.getName()
    
    def encode(self, doc):
        node = doc.createElement("joint")
        
        name = doc.createElement("name")
        fullName = self.joint.getName()
        realName = fullName[0:fullName.index(" <joint>")]
        name.appendChild(doc.createTextNode(realName))
        node.appendChild(name)
        
        type = doc.createElement("type")
        type.appendChild(doc.createTextNode(self.type))
        node.appendChild(type)
        
        return node
    
    def decode(node, lib=None):
        for n in node.childNodes:
            if n.localName == "name":
                name = n.childNodes[0].data.strip()
            elif n.localName == "type":
                type = n.childNodes[0].data.strip()
        
        return name,type
    decode = staticmethod(decode)

"""
The MultiPartActor class inherits from the Object class,
and also has a dictionary of part names with their corresponding assets,
a dictionary of part names with a dictionary of their corresponding animation names and animation file names,
and a dictionary of joints and a list of parts they attach

THIS IS NOT FULLY IMPLEMENTED, and has NOT been tested
"""

class MultiPartActor(Object):
    # parts = {"partName1": actorAsset1, "partName2: actorAsset2, ...}
    # joints = {"jointName1":["partName1","partName2"],
    #           "jointName2":["partName2, "partName3"], ...}
    def __init__(self, name, parts, joints={}, parent=None):
        
        # Create a dictionary of the given assets (get rid of the assets references)
        models = {}
        anims = {}
        for partName in parts:
            # Get the asset file name
            models[partName] = parts[partName].getFullFilename()
            
            for animName in parts[partName].anims:
                # Get the file names
                anims[partName][animName] = parts[partName][animName].getFullFilename()
        
        # Finally create the actor
        actor = Actor(models, anims)
        Object.__init__(self, name, "multipartactor", actor, parent)
        
        self.assets = assets
        self.anims = anims
        # Attach parts by given joints
        for jointName in joints:
            # Make sure the parts exist
            part1 = joints[jointName][0]
            part2 = joints[jointName][1]
            p1Test = self.getNodePath().getPart(part1)
            p2Test = self.getNodePath().getPart(part2)
            # If the parts exist...
            if (part1 != None) and (part2 != None):
                # Attach them by the given jointName
                self.getNodePath.attach(part1, part2, jointName)
    
    def __copy__(self):
        pass
    ## Mutators and Accessors
    
    # part = {"partName"
    def attachPart(self, asset, partName):
        model = asset.getFullFilename()
        self.nodePath.loadModel(model, partName)
        anims = {}
        for animName in asset.anims:
            anims[animName] = asset.anims[animName].getFullFilename()
        

"""
The following class represents a camera object
"""
class Cam(Object):
    def __init__(self, name, type):
        self.camera = None
        # Load camera model
        model = loader.loadModel("models/camera")
        # Create a new camera
        self.camera = Camera(name+"_cam")
        
        # Create the lens
        self.lens = None
        if type == "ortho":
            self.lens = OrthographicLens()
        elif type == "persp":
            self.lens = PerspectiveLens()
        # Attach the lens
        self.camera.setLens(self.lens)
        # Attach it to render
        camera = render.attachNewNode(self.camera)
        model.reparentTo(camera)        
        # Use this nodePath as the new object
        Object.__init__(self, name, "camera", camera)
        # Set the camera mask, so the model is not seen
        self.camera.setCameraMask(BitMask32.bit(5))
        model.hide(BitMask32.bit(5))
        
        self.frustumHidden = True
        
        # List of waypoints
        self.waypoints = []
        
        self.sequence = None
        
        # Sequence settings
        self.speed = 1.0
        self.seqTime = 10.0
        
        self.rope = Rope()
        self.rope.setup(3,[{'node': self.getNodePath()}])
        self.rope.reparentTo(render)
        self.rope.ropeNode.setThickness(5.0)
        a = AmbientLight("")
        amb = render.attachNewNode(a)
        self.rope.setLight(amb)
        
        self.lookAt = None
        self.followPath = False
        
    
    def __copy__(self):
        newCam = Object.__copy__(self)
        newCam.__class__ = Cam
        newCam.camera = newCam.nodePath.node()
        #newCam.camera.setLens(copy.copy(self.camera.getLens()))
        
        newCam.frustumHidden = self.frustumHidden
        
        newCam.waypoints = copy.copy(self.waypoints)
        newCam.rope = Rope()
        newCam.rope.setup(3,[{'node': newCam.getNodePath()}])
        newCam.rope.reparentTo(render)
        newCam.rope.ropeNode.setThickness(5.0)
        a = AmbientLight("")
        amb = render.attachNewNode(a)
        newCam.rope.setLight(amb)
        
        #print newCam.rope
        newCam.seqTime = self.seqTime
        newCam.speed = self.speed
        newCam.lookAt = self.lookAt
        newCam.followPath = self.followPath
        newCam.genWaypointRope()
        

        return newCam
    
    ## Mutators and Accessors
    
    # Camera
    
    def getCamera(self):
        return self.camera
    
    # Frustum
    
    def hideFrustum(self):
        self.frustumHidden = True
        self.camera.hideFrustum()
    
    def showFrustum(self):
        self.frustumHidden = False
        self.camera.showFrustum()
        
    def getLens(self):
        return self.camera.getLens()

    # Waypoint functions
    def addWaypoint(self, wp):
        self.waypoints.append(wp)
    
    def clearWaypoints(self):
        self.waypoints = []
    
    def traverseWaypoints(self):
        way = Sequence()
        for point in self.waypoints:
            way.append(Func(self.nodePath.posInterval(point.posTime, point.getPos())))
        
        way.start()
    
    def genWaypointRope(self):
        # Get all the waypoints actual objects
        vertices = []
        vertices.append({'point': self.getPos()})
        for wp in self.waypoints:
            obj = base.le.objectMgr.findObjectById(wp)
            if obj:
                vertices.append({'node': obj.getNodePath()})
            else:
                self.waypoints.remove(wp)
        
        self.rope.verts = vertices
        self.rope.recompute()
        self.genCamSequence()
    
    def genCamSequence(self):
        if(len(self.waypoints)<=1):
            self.sequence = None
            return
        self.sequence = UniformRopeMotionInterval(self.rope, self.getNodePath(), self.seqTime, followPath=self.followPath, lookAt=self.lookAt)
    
    def previewSequence(self):
        self.startPos = self.getPos()
        self.sequence.start()
    
    def pauseSequence(self):
        self.sequence.pause()
    
    def resumeSequence(self):
        self.sequence.resume()
    
    def resetSequence(self):
        self.sequence.finish()
        self.setPos(self.startPos)
    
    def getSeqTime(self):
        return self.seqTime
    
    def setSeqTime(self, time):
        self.seqTime = time
    
    def decode(node, inEditor=True, lib=None):
        waypoints = []
        lookAt = None
        for n in node.childNodes:
            if n.localName == 'name':
                name = n.childNodes[0].data.strip()            
            elif n.localName == "lens":
                lens = decodeLens(n)
            elif n.localName == "frustumHidden":
                frustumHidden = bool(int(n.childNodes[0].data.strip()))
            elif n.localName == "speed":
                speed = float(n.childNodes[0].data.strip())
            elif n.localName == "seqTime":
                seqTime = float(n.childNodes[0].data.strip())
            elif n.localName == "waypoint":
                waypoints.append(n.childNodes[0].data.strip())
            elif n.localName == "followPath":
                if n.childNodes[0].data.strip() == "0":
                    followPath = False
                elif n.childNodes[0].data.strip() == "1":
                    followPath = True
            elif n.localName == "lookAt":
                lookAt = n.childNodes[0].data.strip()
        
        camera = Camera(name)
        camera.setLens(lens)
        nodePath = render.attachNewNode(camera)
        if inEditor:
            model = loader.loadModel("models/camera")
            model.reparentTo(nodePath)        
        obj = Object.decode(node, nodePath, inEditor, lib=lib)
        obj.__class__ = Cam
        
        if inEditor:
            camera.setCameraMask(BitMask32.bit(5))
            model.hide(BitMask32.bit(5))
        
        obj.camera = camera
        obj.frustumHidden = frustumHidden
        if frustumHidden:
            obj.camera.hideFrustum()
        else:
            obj.camera.showFrustum()
        
        obj.waypoints = waypoints
        obj.speed = speed
        obj.seqTime = seqTime
        # Setup the rope
        obj.rope = Rope()
        obj.rope.setup(3,[{'node': obj.getNodePath()}])
        obj.rope.reparentTo(render)
        if not inEditor:
            obj.rope.hide()
        else:
            obj.rope.ropeNode.setThickness(5.0)
            a = AmbientLight("")
            amb = render.attachNewNode(a)
            obj.rope.setLight(amb)
        
        obj.followPath = followPath
        if lookAt is not None:
            obj.lookAt = lookAt
        else:
            obj.lookAt = None
        
        return obj      
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        lens = encodeLens(self.getLens(), doc, self.frustumHidden)
        node.appendChild(lens)
        
        frustumHidden = doc.createElement("frustumHidden")
        if self.frustumHidden:
            frustumHidden.appendChild(doc.createTextNode("1"))
        else:
            frustumHidden.appendChild(doc.createTextNode("0"))
        node.appendChild(frustumHidden)
        
        speed = doc.createElement("speed")
        speed.appendChild(doc.createTextNode(str(self.speed)))
        node.appendChild(speed)
        
        seqTime = doc.createElement("seqTime")
        seqTime.appendChild(doc.createTextNode(str(self.seqTime)))
        node.appendChild(seqTime)
        
        for wp in self.waypoints:
            waypoint = doc.createElement("waypoint")
            waypoint.appendChild(doc.createTextNode(wp))
            node.appendChild(waypoint)
        
        followPath = doc.createElement("followPath")
        if self.followPath:
            followPath.appendChild(doc.createTextNode("1"))
        else:
            followPath.appendChild(doc.createTextNode("0"))
        node.appendChild(followPath)
        
        
        if self.lookAt is not None:
            lookAt = doc.createElement("lookAt")
            lookAt.appendChild(doc.createTextNode(self.lookAt.getName()))
            node.appendChild(lookAt)
        
        return node
        
    def BVWEncode(self):
        lines = []
        
        lines.append("    camera = Camera('" + self.name + "_cam')\n")
        if isinstance(self.getLens(), PerspectiveLens):
            lines.append("    lens = PerspectiveLens()\n")
            lines.append("    lens.setFov(" + str(self.getLens().getFov()) +")\n")
        else:
            lines.append("    lens = OrthographicLens()\n")
            lines.append("    lens.setFilmSize(" + str(self.getLens().getFilmSize()) +")\n")
            
        lines.append("    lens.setNearFar(" + str(self.getLens().getNear()) + ", " + str(self.getLens().getFar()) + ")\n")
        lines.append("    camera.setLens(lens)\n")
        
        # Camera path
        if self.waypoints != []:
            lines.append("    # Camera waypoints\n")
            lines.append("    waypoints = []\n")
            lines.append("    waypoints.append({'point':"+str(self.getPos())+"})\n")
            for wp in self.waypoints:
                obj = base.le.objectMgr.findObjectById(wp)
                if obj:
                    lines.append("    waypoints.append({'point':"+str(obj.getPos())+"})\n")
                else:
                    self.waypoints.remove(wp)
            lines.append("    rope = Rope()\n")
            lines.append("    rope.setup(3, waypoints)\n")
            lines.append("    rope.reparentTo(render)\n")
            lines.append("    rope.hide()\n\n")
        
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(camera)\n")      
        lines.extend(Object.BVWEncode(self))
        
        return lines
    
    def onRemove(self):
        self.rope.detachNode()
        Object.onRemove(self)
        
    def onAdd(self):
        self.rope.reparentTo(render)
        Object.onAdd(self)
    
    def BVWEncodeSequence(self):
        lines = []
        lines.append("    # Waypoint sequence\n")
        # Should only create the sequence when the camera is the base camera
        if self.lookAt is not None:
            lookAtText = "objects['" + self.lookAt.getName() + "']"
        else:
            lookAtText = "None"
        lines.append("    camSequence = UniformRopeMotionInterval(rope, base.cam, "+str(self.seqTime)+", followPath="+str(self.followPath)+", lookAt="+lookAtText+")\n")
        lines.append("    sequences['" + self.name + "'] = camSequence\n\n")
        return lines
    
    ## # Bitmask/Cameramask
    
    ## def setCameraMask(self, mask):
        ## self.camera.setCameraMask(mask)
    
    ## def getCameraMask(self):
        ## self.camera.getCameraMask()
    
    ## # Cull Center
    
    ## def getCullCenter(self):
        ## return self.camera.getCullCenter()
    
    ## def setCullCenter(self, cull):
        ## self.camera.setCullCenter(cull)
    
    ## # LOD Center
    
    ## def getLodCenter(self):
        ## return self.camera.getLodCenter()
    
    ## def setLodCenter(self, lod):
        ## self.camera.setLodCenter(lod)
    
    ## # Is this Camera Active?
    
    ## def isActive(self):
        ## return self.camera.isAcitve
    
    ## def setActive(self, active):
        ## self.camera.setActive(active)
    
    ## # Scene
    
    ## def getScene(self):
        ## return self.camera.getScene()
    
    ## def setScene(self, scene):
        ## self.camera.setScene(scene)
    
    ## # Display Region
    
    ## def getDisplayRegion(self, n):
        ## return self.camera.getDisplayRegion(n)
    
    ## def getDisplayRegions(self):
        ## return self.camera.getDisplayRegions()
    
    ## def getNumDisplayRegions(self):
        ## return self.camera.getNumDisplayRegions()
    
    ## # Point in view of camera?
    
    ## def isInView(self, point):
        ## return self.camera.isInView(point)

"""
The next five classes have to do with Light objects:
A generic light, ambient light, directional light,
point light, and spot light.
"""
class LELight(Object):
    def __init__(self, name, type, light):
        self.light = light

        # Load the model
        self.model = None
        if type == "ambient":
            self.model = loader.loadModel("models/ambient")
            self.model.setScale(0.2)
        elif type == "directional":
            self.model = loader.loadModel("models/direct")
            self.model.setRenderModeWireframe()
            self.model.setScale(0.2)
        elif type == "point":
            self.model = loader.loadModel("models/point")
            self.model.setRenderModeWireframe()
            self.model.setScale(0.2)
        elif type == "spot":
            self.model = loader.loadModel("models/spot")
            self.model.setRenderModeWireframe()
            self.model.setScale(0.5)
        
        self.model.setTag("LEObjRep", "")
        
        # Make sure the model does not render lighting
        self.model.setLightOff()
        
        self.model.hide(BitMask32.bit(5))
        
        # Attach the light and set it
        np = render.attachNewNode(self.light)
        render.setLight(np)
        self.targets = set()   #set of objects that this light has been set on
                               #if this is empty, light effects entire scene

        # Create the object for the light
        Object.__init__(self, name, type, np)
        self.model.reparentTo(self.nodePath)
    
    def __copy__(self):
        newLight = Object.__copy__(self)
        newLight.__class__ = self.__class__
        newLight.light = newLight.nodePath.node()
        newLight.targets = copy.copy(self.targets)
        
        newLight.model = copy.copy(self.model)
        newLight.model.reparentTo(newLight.nodePath)
        
        return newLight
    
    def addTarget(self, obj):
        if not self.targets:
            render.clearLight(self.nodePath)
            
        self.targets.add(obj)
        obj.lights.add(self)
        obj.nodePath.setLight(self.nodePath)        
        
    def removeTarget(self, obj, fromRemove=False):
        obj.nodePath.clearLight(self.nodePath)
        self.targets.remove(obj)
        
        if not fromRemove:
            obj.lights.remove(self)
        
        if not self.targets:
            render.setLight(self.nodePath)
    
    def decode(node, modelFile, lightClass, inEditor=True, lib=None):
        color = None
        targetNames = []
        for n in node.childNodes:
            if n.localName == 'name':
                name = n.childNodes[0].data.strip()
            elif n.localName == "color":
                color = decodeColor(n)
            elif n.localName == 'target':
                targetNames.append(n.childNodes[0].data.strip())
                
        if inEditor:        
            model = loader.loadModel(modelFile)
            model.setLightOff(True)
            model.setTag("LEObjRep","")
        light = lightClass(name)
        np = render.attachNewNode(light)
        render.setLight(np)
        
        obj = Object.decode(node, np, lib=lib)
        obj.__class__ = LELight
        obj.light = light
        if inEditor:
            obj.model = model
            model.reparentTo(obj.nodePath)
        else:
            obj.model = None
        if color:
            obj.setColor(color)
        
        obj.targetNames = targetNames
        obj.targets = set()
        return obj
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        color = encodeColor(self.getColor(), "color", doc)
        node.appendChild(color)
        
        for t in self.targets:
            if t.name in base.le.objectMgr.objects:
                targetNode = doc.createElement("target")
                targetNode.appendChild(doc.createTextNode(t.name))
                node.appendChild(targetNode)
        
        return node
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    objects['" + self.name + "'].node().setColor(" + str(self.light.getColor()) + ")\n")
        
        if not self.targets:
            lines.append("    render.setLight(objects['" + self.name + "'])\n")
            
        lines.extend(Object.BVWEncode(self))
        
        return lines
    
    def onRemove(self):
        Object.onRemove(self)
        if self.targets:
            for t in self.targets:
                t.nodePath.clearLight(self.nodePath)
                t.lights.remove(self)
        else:
            render.clearLight(self.nodePath)
            
    
    def reattach(self):
        if self.targets:
            for t in self.targets:
                t.nodePath.setLight(self.nodePath)
                t.lights.add(self)
        else:
            render.setLight(self.nodePath)
    
    def setColor(self, color):
        self.light.setColor(color)
        if self.model:
            self.model.setColorScale(color)
    
    def getColor(self):
        return self.light.getColor()

class AmbLight(LELight):
    def __init__(self, name):
        light = AmbientLight(name)        
        LELight.__init__(self, name, "ambient", light)        
    
    def decode(node, inEditor=True, lib=None):
        obj = LELight.decode(node, "models/ambient", AmbientLight, inEditor, lib=lib)
        obj.__class__ = AmbLight
        if inEditor:
            obj.model.setScale(0.2)
        
        return obj
    decode = staticmethod(decode)

    def encode(self, doc):
        return LELight.encode(self, doc)
        
    def BVWEncode(self):
        lines = []
        
        lines.append("    light = AmbientLight('" + self.name + "')\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(light)\n")
        
        lines.extend(LELight.BVWEncode(self))
        
        return lines
        
class DirLight(LELight):
    def __init__(self, name):
        light = DirectionalLight(name)
        LELight.__init__(self, name, "directional", light)
    
    def decode(node, inEditor=True, lib=None):
        obj = LELight.decode(node, "models/direct", DirectionalLight, inEditor, lib=lib)
        obj.__class__ = DirLight
        obj.frustumHidden = True
        if inEditor:
            obj.model.setRenderModeWireframe()
            obj.model.setScale(0.2)
        for n in node.childNodes:
            if n.localName == "specularColor":
                obj.setSpecularColor(decodeColor(n))
        return obj      
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = LELight.encode(self, doc)
        
        specularColor = encodeColor(self.getSpecularColor(), "specularColor", doc)
        node.appendChild(specularColor)
        
        return node
    
    def BVWEncode(self):
        lines =[]
        
        lines.append("    light = DirectionalLight('" + self.name + "')\n")
        lines.append("    light.setSpecularColor(" + str(self.getSpecularColor()) + ")\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(light)\n")
        
        lines.extend(LELight.BVWEncode(self))
        
        return lines
    
    ## Mutators and Accessors
        
    # Specular Color
    
    def getSpecularColor(self):
        return self.light.getSpecularColor()
    
    ## The color argument must be a Vec4,
    ## Vec4(r,g,b,a)
    def setSpecularColor(self, color):
        self.light.setSpecularColor(color)
        
class PoiLight(LELight):
    def __init__(self, name):
        light = PointLight(name)
        LELight.__init__(self, name, "point", light)
    
    def decode(node, inEditor=True, lib=None):
        obj = LELight.decode(node, "models/point", PointLight, inEditor, lib=lib)
        obj.__class__ = PoiLight
        obj.frustumHidden = True
        if inEditor:
            obj.model.setRenderModeWireframe()
            obj.model.setScale(0.2)
        for n in node.childNodes:
            if n.localName == "specularColor":
                obj.setSpecularColor(decodeColor(n))
            elif n.localName == "attenuation":
                obj.setAttenuation(decodeVec3(n))
        return obj      
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = LELight.encode(self, doc)
        
        attenuation = encodeVec3(self.getAttenuation(), "attenuation", doc)
        node.appendChild(attenuation)
        
        specularColor = encodeColor(self.getSpecularColor(), "specularColor", doc)
        node.appendChild(specularColor)
        
        return node
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    light = PointLight('" + self.name + "')\n")
        lines.append("    light.setSpecularColor(" + str(self.getSpecularColor()) + ")\n")
        lines.append("    light.setAttenuation(" + str(self.getAttenuation()) + ")\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(light)\n")
        
        lines.extend(LELight.BVWEncode(self))
        
        return lines
    
    ## Mutators and Accessors
    
    # Attentuation
    
    def getAttenuation(self):
        return self.light.getAttenuation()
    
    ## The att argument must be a Point3 or Vec3
    def setAttenuation(self, att):
        self.light.setAttenuation(att)
    
    # Specular Color
    
    def getSpecularColor(self):
        return self.light.getSpecularColor()
    
    ## The color argument must be a Vec4,
    ## Vec4(r,g,b,a)
    def setSpecularColor(self, color):
        self.light.setSpecularColor(color)
        
class SpoLight(LELight):
    def __init__(self, name):
        light = Spotlight(name)
        light.setCameraMask(BitMask32.bit(5))
        LELight.__init__(self, name, "spot", light)
        
        # Frustum
        self.frustumHidden = True
        
        # Shadows
        self.castsShadows = False
        self.bufferX = 2048
        self.bufferY = int(self.bufferX / self.getLens().getAspectRatio())
    
    def __copy__(self):
        newSpot = LELight.__copy__(self)
        newSpot.__class__ = SpoLight
        newSpot.light.setLens(copy.copy(self.light.getLens()))
        newSpot.frustumHidden = self.frustumHidden
        newSpot.castsShadows = self.castsShadows
        newSpot.bufferX = self.bufferX
        newSpot.bufferY = self.bufferY
        
        return newSpot
    
    def setCastsShadows(self, casts):
        self.castsShadows = casts
    
    def getCastsShadows(self):
        return self.castsShadows
    
    def hideFrustum(self):
        self.frustumHidden = True
        self.light.hideFrustum()
    
    def showFrustum(self):
        self.frustumHidden = False
        self.light.showFrustum()
        
    def setBuffer(self, buff):
        ar = self.getLens().getAspectRatio()        
        self.bufferX = buff
        self.bufferY = int(buff / ar)
    
    def getBuffer(self):
        return self.bufferX
        
    def getLens(self):
        return self.light.getLens()
    
    def decode(node, inEditor=True, lib=None):
        obj = LELight.decode(node, "models/spot", Spotlight, inEditor, lib=lib)
        obj.__class__ = SpoLight
        obj.frustumHidden = True
        obj.bufferX = 2048
        obj.bufferY = None
        if inEditor:
            obj.model.setRenderModeWireframe()
            obj.model.setScale(0.5)
        for n in node.childNodes:
            if n.localName == "exponent":
                obj.setExponent(float(n.childNodes[0].data.strip()))
            elif n.localName == "specularColor":
                obj.setSpecularColor(decodeColor(n))
            elif n.localName == "attenuation":
                obj.setAttenuation(decodeVec3(n))
            elif n.localName == "lens":
                obj.light.setLens(decodeLens(n))
            elif n.localName == "shadowCaster":
                if bool(int(n.childNodes[0].data.strip())):
                    #obj.light.setShadowCaster(True, 2048, 2048)
                    obj.castsShadows = True
                else:
                    #obj.light.setShadowCaster(False)
                    obj.castsShadows = False
            elif n.localName == "bufferX":
                obj.bufferX = int(n.childNodes[0].data.strip())
            elif n.localName == "bufferY":
                obj.bufferY = int(n.childNodes[0].data.strip())
                
        if obj.bufferY is None:
            obj.bufferY = int(obj.bufferX / obj.getLens().getAspectRatio())
                
        return obj 
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = LELight.encode(self, doc)
        
        attenuation = encodeVec3(self.getAttenuation(), "attenuation", doc)
        node.appendChild(attenuation)
        
        exponent = doc.createElement("exponent")
        exponent.appendChild(doc.createTextNode(str(self.getExponent())))
        node.appendChild(exponent)
        
        specularColor = encodeColor(self.getSpecularColor(), "specularColor", doc)
        node.appendChild(specularColor)
        
        lens = encodeLens(self.getLens(), doc, self.frustumHidden)
        node.appendChild(lens)
        
        shadowCaster = doc.createElement("shadowCaster")
        if self.castsShadows:
            shadowCaster.appendChild(doc.createTextNode("1"))
        else:
            shadowCaster.appendChild(doc.createTextNode("0"))
        node.appendChild(shadowCaster)
        
        bufferX = doc.createElement("bufferX")
        bufferX.appendChild(doc.createTextNode(str(self.bufferX)))
        node.appendChild(bufferX)
        bufferY = doc.createElement("bufferY")
        bufferY.appendChild(doc.createTextNode(str(self.bufferY)))
        node.appendChild(bufferY)
        
        return node
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    light = Spotlight('" + self.name + "')\n")
        lines.append("    light.setSpecularColor(" + str(self.getSpecularColor()) + ")\n")
        lines.append("    light.setAttenuation(" + str(self.getAttenuation()) + ")\n")
        lines.append("    light.setExponent(" + str(self.getExponent()) + ")\n")
        lines.append("    lens = PerspectiveLens()\n")
        lines.append("    lens.setFov(" + str(self.getLens().getFov()) + ")\n")
        lines.append("    lens.setNearFar(" + str(self.getLens().getNear()) + ", " + str(self.getLens().getFar()) + ")\n")
        lines.append("    light.setLens(lens)\n")
        if self.castsShadows:
            lines.append("    light.setShadowCaster(True, " + str(self.bufferX) + ", " + str(self.bufferY) + ")\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(light)\n")
       
        lines.extend(LELight.BVWEncode(self))
        
        return lines
    
    ## Mutators and Accessors
    
    # Exponent
    
    def getExponent(self):
        return self.light.getExponent()
    
    def setExponent(self, exp):
        self.light.setExponent(exp)
    
    # Attentuation
    
    def getAttenuation(self):
        return self.light.getAttenuation()
    
    ## The att argument must be a Point3 or Vec3
    def setAttenuation(self, att):
        self.light.setAttenuation(att) 
    
    # Specular Color
    
    def getSpecularColor(self):
        return self.light.getSpecularColor()
    
    ## The color argument must be a Vec4,
    ## Vec4(r,g,b,a)
    def setSpecularColor(self, color):
        self.light.setSpecularColor(color)
        

class Collider(Object):
    def __init__(self, name, type):
        self.collNode = CollisionNode(name)
        #so this object can be selected in the editor
        self.collNode.setIntoCollideMask(BitMask32.allOn())
        np = render.attachNewNode(self.collNode)
        np.show()
        np.setLightOff()
        np.hide(BitMask32.bit(5))
        Object.__init__(self, name, type, np)
        self.fromBitMask = CollisionNode.getDefaultCollideMask()
        self.intoBitMask = CollisionNode.getDefaultCollideMask()
        
    def __copy__(self):
        newCollider = Object.__copy__(self)
        newCollider.__class__ = self.__class__
        newCollider.fromBitMask = copy.copy(self.fromBitMask)
        newCollider.intoBitMask = copy.copy(self.intoBitMask)
        newCollider.collNode = newCollider.nodePath.node()
        
        return newCollider
        
    def decode(node, inEditor=True, lib=None):
        tangible = True
        fromMask = BitMask32.allOn().getWord()
        intoMask = BitMask32.allOn().getWord()
        for n in node.childNodes:
            if n.localName == 'name':
                name = n.childNodes[0].data.strip()
            if n.localName == 'fromBitMask':
                fromMask = int(n.childNodes[0].data.strip())
            elif n.localName == 'intoBitMask':
                intoMask = int(n.childNodes[0].data.strip())
        
        collNode = CollisionNode(name)
        np = render.attachNewNode(collNode)
        obj = Object.decode(node, np, inEditor=inEditor, lib=lib)
        obj.__class__ = Collider
        obj.collNode = collNode
        
        if inEditor:
            np.show()
            np.setLightOff()
            np.hide(BitMask32.bit(5))
            #so this object can be selected
            collNode.setIntoCollideMask(BitMask32.allOn())
            obj.fromBitMask = BitMask32(fromMask)
            obj.intoBitMask = BitMask32(intoMask)
        else:
            np.hide()
            collNode.setFromCollideMask(BitMask32(fromMask))
            collNode.setIntoCollideMask(BitMask32(intoMask))
        
        return obj
    decode = staticmethod(decode)
    
    def setTangible(self, tangible):
        self.collNode.modifySolid(0).setTangible(tangible)
        
    def isTangible(self):
        return self.collNode.getSolid(0).isTangible()
    
    def getFromCollideMask(self):
        return self.fromBitMask.getWord()
        
    def setFromCollideMask(self, mask):
        self.fromBitMask = BitMask32(mask)
        
    def getIntoCollideMask(self):
        return self.intoBitMask.getWord()
        
    def setIntoCollideMask(self, mask):
        self.intoBitMask = BitMask32(mask)
    
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        tangibleNode = doc.createElement('tangible')
        node.appendChild(tangibleNode)
        tangibleNode.appendChild(doc.createTextNode(str(self.isTangible())))
        
        fromMask = doc.createElement('fromBitMask')
        node.appendChild(fromMask)
        fromMask.appendChild(doc.createTextNode(str(self.fromBitMask.getWord())))
        
        intoMask = doc.createElement('intoBitMask')
        node.appendChild(intoMask)
        intoMask.appendChild(doc.createTextNode(str(self.intoBitMask.getWord())))
        
        return node
        
    def BVWEncode(self):
        lines = Object.BVWEncode(self)
        if not self.isTangible():
            lines.append("    collNode.modifySolid(0).setTangible(False)\n")
        lines.append("    collNode.setFromCollideMask(BitMask32(" + str(self.getFromCollideMask()) + "))\n")
        lines.append("    collNode.setIntoCollideMask(BitMask32(" + str(self.getIntoCollideMask()) + "))\n")
            
        return lines

class SphereCollider(Collider):
    def __init__(self, name):
        Collider.__init__(self, name, "sphere")
        self.collNode.addSolid(CollisionSphere(0,0,0,10))
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    collNode = CollisionNode('" + self.name + "')\n")
        lines.append("    collNode.addSolid(CollisionSphere(0, 0, 0, 10))\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(collNode)\n")
        
        lines.extend(Collider.BVWEncode(self))
        
        return lines
    
    def decode(node, inEditor=True, lib=None):
        tangible = True
        for n in node.childNodes:
            if n.localName == 'tangible':
                tangible = bool(int(n.childNodes[0].data.strip()))
        
        obj = Collider.decode(node, inEditor=inEditor, lib=lib)
        obj.__class__ = SphereCollider
        obj.collNode.addSolid(CollisionSphere(0,0,0,10))
        obj.collNode.modifySolid(0).setTangible(tangible)
        
        return obj
    decode = staticmethod(decode)
        
class BoxCollider(Collider):
    def __init__(self, name):
        Collider.__init__(self, name, "box")
        self.collNode.addSolid(CollisionBox(Point3(0,0,0), 10, 10, 10))
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    collNode = CollisionNode('" + self.name + "')\n")
        lines.append("    collNode.addSolid(CollisionBox(Point3(0, 0, 0), 10, 10, 10))\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(collNode)\n")
        
        lines.extend(Collider.BVWEncode(self))
        
        return lines
    
    def decode(node, inEditor=True, lib=None):
        tangible = True
        for n in node.childNodes:
            if n.localName == 'tangible':
                tangible = bool(int(n.childNodes[0].data.strip()))
    
        obj = Collider.decode(node, inEditor=inEditor, lib=lib)
        obj.__class__ = BoxCollider
        obj.collNode.addSolid(CollisionBox(Point3(0,0,0), 10, 10, 10))
        obj.collNode.modifySolid(0).setTangible(tangible)
        return obj
    decode = staticmethod(decode)

    
class PlaneCollider(Collider):
    def __init__(self, name):
        Collider.__init__(self, name, "plane")
        self.collNode.addSolid(CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0))))

    def BVWEncode(self):
        lines = []
        
        lines.append("    collNode = CollisionNode('" + self.name + "')\n")
        lines.append("    collNode.addSolid(CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0))))\n")
        lines.append("    objects['" + self.name + "'] = render.attachNewNode(collNode)\n")
        
        lines.extend(Collider.BVWEncode(self))
        
        return lines
        
    def decode(node, inEditor=True, lib=None):
        for n in node.childNodes:
            if n.localName == 'tangible':
                tangible = bool(int(n.childNodes[0].data.strip()))
    
        obj = Collider.decode(node, inEditor=inEditor, lib=lib)
        obj.__class__ = PlaneCollider
        obj.collNode.addSolid(CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0))))
        obj.collNode.modifySolid(0).setTangible(tangible)
        return obj
    decode = staticmethod(decode)

class LETextureCard(Object):
    def __init__(self, name, asset, parent= None):
        
        tex = loader.loadTexture(asset.getFullFilename().getFullpath())
        maker = CardMaker( name )
        x = float(tex.getXSize())
        y = float(tex.getYSize())
        if x == 0 or y == 0:
            x = float(tex.getVideoWidth()) 
            y = float(tex.getVideoHeight())
        maker.setFrame(-10, 10,-10 * (y/x),10 * (y/x))
        geom = maker.generate()
        card = NodePath(name)
        card.attachNewNode(geom)
        card.flattenStrong()
        card.setTexture(tex)
        if hasattr(tex, 'getTexScale'):
            card.setScale(tex.getTexScale().getX(), 1, tex.getTexScale().getY())
            card.setTexScale(TextureStage.getDefault(), tex.getTexScale())
        Object.__init__(self, name, "texturecard", card, parent)
        self.asset = asset
   
    def __copy__(self):
        newObj = Object.__copy__(self)
        newObj.asset = self.asset
        newObj.__class__ = LETextureCard
        return newObj
    
    def onAdd(self):
        Object.onAdd(self)
        self.asset.incSceneCount()
        
    def onRemove(self):
        Object.onAdd(self)
        self.asset.decSceneCount()
    
    def getAsset(self):
        return self.asset
    
    def decode(node, inEditor=True, lib=None):
        for n in node.childNodes:
            if n.localName == "asset":
                assetName = n.childNodes[0].data.strip()
                asset = lib.textures[assetName]
                
        tex = loader.loadTexture(asset.getFullFilename().getFullpath())
        maker = CardMaker( "blank" )
        maker.setFrame(-10, 10,-10 * (tex.getYSize()/tex.getXSize()),10 * (tex.getYSize()/tex.getXSize()))
        geom = maker.generate()
        card = NodePath("blank")
        card.attachNewNode(geom)
        card.flattenStrong()
        card.setTexture(tex)
        obj = Object.decode(node, card, lib=lib)
        obj.__class__ = LETextureCard
        obj.asset = asset
        
        return obj
    decode = staticmethod(decode)
        
    
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        asset = doc.createElement("asset")
        asset.appendChild(doc.createTextNode(self.asset.name))
        node.appendChild(asset)
        
        return node   
        
    def BVWEncode(self):
        lines = []
        
        lines.append("    tex = loader.loadTexture('" + self.asset.filename.getFullpath() + "')\n")
        lines.append("    cm = CardMaker('cm')\n")
        lines.append("    cm.setFrame(-10, 10, -10 * (tex.getYSize()/tex.getXSize()), 10 * (tex.getYSize()/tex.getXSize()))\n")
        lines.append("    objects['" + self.name + "'] = NodePath('" + self.name + "')\n")
        lines.append("    objects['" + self.name + "'].attachNewNode(cm.generate())\n")
        lines.append("    objects['" + self.name + "'].flattenStrong()\n")
        lines.append("    objects['" + self.name + "'].setTexture(tex)\n")
        
        lines.extend(Object.BVWEncode(self))
        
        return lines
    
class LETerrain(Object):
    def __init__(self, name, asset, parent= None):
        # Set up the GeoMipTerrain
        self.terrain = GeoMipTerrain("myDynamicTerrain")
        self.terrain.setHeightfield(asset.getFullFilename().getFullpath())
        
        self.terrain.setFocalPoint(base.le.ui.perspView.cam)
        self.root = self.terrain.getRoot()
        # Generate it.
        self.terrain.generate()
        Object.__init__(self, name, "LETerrain", self.root, parent)
        self.asset = asset
        self.tex = None
   
    def BVWEncode(self):
        lines = []
        
        lines.append("    terrain = GeoMipTerrain('myGeoTerrain')\n")
        lines.append("    terrain.setHeightfield('" + self.asset.filename.getFullpath() + "')\n")
        lines.append("    root = terrain.getRoot()\n")
        lines.append("    terrain.setFocalPoint(base.cam)\n")
        lines.append("    terrain.setFar(" + str(self.terrain.getFar()) + ")\n")
        lines.append("    terrain.setNear(" + str(self.terrain.getNear()) + ")\n")
        lines.append("    terrain.setBlockSize(" + str(self.terrain.getBlockSize()) + ")\n")
        lines.append("    terrain.setBruteforce(" + str(self.terrain.getBruteforce()) + ")\n")
        lines.append("    terrain.setAutoFlatten(" + str(self.terrain.getFlattenMode()) + ")\n")
        if self.tex != None:
            lines.append("    tex = loader.loadTexture('" + self.tex.filename.getFullpath() + "')\n")
            lines.append("    root.setTexture(tex)\n")
        lines.append("    terrain.generate()\n")
        lines.append("    objects['"+ self.name + "'] = root\n")
        
        
        lines.extend(Object.BVWEncode(self))
        
        return lines
    def __copy__(self):
        pass   
    def onAdd(self):
        Object.onAdd(self)
        self.asset.incSceneCount()
        
    def onRemove(self):
        Object.onAdd(self)
        self.asset.decSceneCount()
        
    def getAsset(self):
        return self.asset
    
    def decode(node, inEditor=True, lib=None):
        tex = None
        for n in node.childNodes:
            if n.localName == "asset":
                assetName = n.childNodes[0].data.strip()
                asset = lib.terrains[assetName]
            if n.localName == "colorTexture": 
                texName = n.childNodes[0].data.strip()
                tex = lib.textures[texName]
            if n.localName == "blockSize":
                bsize = int(n.childNodes[0].data.strip())
            if n.localName == "near":
                near = float(n.childNodes[0].data.strip())
            if n.localName == "far":
                far = float(n.childNodes[0].data.strip())
#            if n.localName == "focalPoint":
#                fp = n.childNodes[0].data.strip()
            if n.localName == "bruteforce":
                bf = bool(int(n.childNodes[0].data.strip()))
            if n.localName == "minLevel":
                minLevel = int(n.childNodes[0].data.strip())
#            if n.localName == "maxLevel":
#                maxLevel = int(n.childNodes[0].data.strip())
            if n.localName == "flattenMode":
                fmode = int(n.childNodes[0].data.strip())
                   
        
        terrain = GeoMipTerrain("myDynamicTerrain")
        root = terrain.getRoot()
        
        obj = Object.decode(node, root, lib=lib)
        obj.__class__ = LETerrain
        obj.tex = tex
        obj.asset = asset
        
        obj.terrain = terrain
        obj.root = root
        obj.terrain.setHeightfield(asset.getFullFilename().getFullpath())
        if inEditor:
            obj.terrain.setFocalPoint(base.le.ui.perspView.cam)
        else:
            obj.terrain.setFocalPoint(base.cam)
        
        # Generate it.
        obj.terrain.setNear(near)
        obj.terrain.setFar(far)
        obj.terrain.setBruteforce(bf)
        obj.terrain.setMinLevel(minLevel)
        obj.terrain.setBlockSize(bsize)
#        obj.terrain.setMaxLevel(maxLeval)
        obj.terrain.setAutoFlatten(fmode)
        if obj.tex != None:
            obj.root.setTexture(loader.loadTexture(obj.tex.getFullFilename()))
        obj.terrain.update()
        
        obj.terrain.generate()
        
        
        
        return obj
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = Object.encode(self, doc)
        
        asset = doc.createElement("asset")
        asset.appendChild(doc.createTextNode(self.asset.name))
        node.appendChild(asset)
#        
        if self.root.getTexture():
            colorMap = doc.createElement("colorTexture")
            colorMap.appendChild(doc.createTextNode(self.tex.name))
            node.appendChild(colorMap)

        
        bsize = doc.createElement("blockSize")
        bsize.appendChild(doc.createTextNode(str(self.terrain.getBlockSize())))
        node.appendChild(bsize)
        
        near = doc.createElement("near")
        near.appendChild(doc.createTextNode(str(self.terrain.getNear())))
        node.appendChild(near)
        
        far = doc.createElement("far")
        far.appendChild(doc.createTextNode(str(self.terrain.getFar())))
        node.appendChild(far)
#
#        fp = doc.createElement("focalPoint")
#        fp.appendChild(doc.createTextNode(self.terrain.getFocalPoint().getName()))
#        node.appendChild(fp)
        
        bforce = doc.createElement("bruteforce")
        if self.terrain.getBruteforce():
            bforce.appendChild(doc.createTextNode("1"))
        else:
            bforce.appendChild(doc.createTextNode("0"))
        node.appendChild(bforce)
        
        minLevel = doc.createElement("minLevel")
        minLevel.appendChild(doc.createTextNode(str(self.terrain.getMinLevel())))
        node.appendChild(minLevel)
        
#        maxLevel = doc.createElement("maxLevel")
#        maxLevel.appendChild(doc.createTextNode(str(self.terrain.getMaxLevel())))
#        node.appendChild(maxLevel)
        
        fmode = doc.createElement("flattenMode")
        fmode.appendChild(doc.createTextNode(str(self.terrain.getFlattenMode())))
        node.appendChild(fmode)
        
        return node
        
    
    
    def setColorMap(self, tex):
        self.tex = tex
        self.nodePath.setTexture(loader.loadTexture(tex.getFullFilename().getFullpath()))
        #self.terrain.setColorMap(loader.loadTexture(tex.getFullFilename().getFullpath()))    
    def setBlockSize(self, val):
        self.terrain.setBlockSize(val)
    
    def setNear(self, val):
        self.near = val
        self.terrain.setNear(val)
    
    def setFar(self, val):
        self.far = val
        self.terrain.setFar(val)
    
    def setBruteforce(self, val):
        self.terrain.setBruteforce(val)
        
#    def setFocalPoint(self, val):
#        #NOTE val should be (double, double) 
#        self.terrain.setFocalPoint(val)
    
    def generate(self):
        self.terrain.generate()
    
    def update(self):
        self.terrain.update()
        
    def getColorMap(self):
        return self.terrain.colorMap()
    
    def getBruteforce(self):
        return self.terrain.getBruteforce()
        
    def getBlockSize(self):
        return self.terrain.getBlockSize()
    
    def getNear(self):
        return self.terrain.getNear()
               
    def getFar(self):
        return self.terrain.getFar()
    
    def getFocalPoint(self):
        #returns a nodepath?
        return self.terrain.getFocalPoint()    
    
    def setMinLevel(self, val):
        self.terrain.setMinLevel(val)
    def getMinLevel(self):
        
        return self.terrain.getMinLevel()
    
    def hasColorMap(self):
        return self.terrain.hasColorMap()
        # Add a task to keep updating the terrain
#        def updateTask(task):
#          terrain.update()
#          return task.cont
#        taskMgr.add(updateTask, "update")
    def isDirty(self):
        return self.terrain.isDirty()
    
    def setAutoFlattenMode(self,val):
        #0-3 values 0 = NONE 3 = sTRONG
        self.terrain.setAutoFlatten(val)
    
    def getAutoFlattenMode(self):
        return self.terrain.getFlattenMode()
    
class LERope(Object):
    def __init__(self, name,parent):
        
        Object.__init__(self, name, "LERope")
        
        model = loader.loadModel("models/dummy_box")
        model.setScale(0.5,0.5,0.5)
        #model.setRenderModeWireframe()
        model.setLightOff()
        # Hide the dummy node from instantiated cameras
        model.hide(BitMask32.bit(5))
        # Attach it to the nodepath
        model.reparentTo(self.nodePath)
        #model.setTag("LEObjRep", "") 
        
        
        self.waypoints = []
        
        self.rope = Rope()
        self.rope.setup(3,[{'node': self.getNodePath()}])
        self.rope.reparentTo(render)        
        self.rope.ropeNode.setThickness(5.0)
        
        a = AmbientLight("")
        amb = render.attachNewNode(a)
        self.rope.setLight(amb)
        
        #followPath=False
        #lookAt=None
        self.object = None
        self.oldObject = None
        self.seqTime = 5.0
        self.orientationChoice = 1
        self.startPos = Point3()
        self.startHpr = VBase3()
     
        # Waypoint functions
    def addWaypoint(self, wp):
        self.waypoints.append(wp)
    
    def clearWaypoints(self):
        self.waypoints = []
    
    #depricated for now    
    def traverseWaypoints(self):
        way = Sequence()
        for point in self.waypoints:
            way.append(Func(self.nodePath.posInterval(point.posTime, point.getPos())))
        
        way.start()
    
    def genWaypointRope(self):
        # Get all the waypoints actual objects
        vertices = []
        vertices.append({'point': self.getPos()})
        for wp in self.waypoints:
            obj = base.le.objectMgr.findObjectById(wp)
            if obj:
                vertices.append({'node': obj.getNodePath()})
            else:
                self.waypoints.remove(wp)
        
        self.rope.ropeNode.setThickness(5.0)
        self.rope.verts = vertices
        self.rope.recompute()
        
    def decode(node, inEditor=True, lib=None):
        waypoints = []
        #lookAt = None
        for n in node.childNodes:
            if n.localName == 'name':
                name = n.childNodes[0].data.strip()            
            elif n.localName == "speed":
                speed = float(n.childNodes[0].data.strip())
            elif n.localName == "seqTime":
                seqTime = float(n.childNodes[0].data.strip())
            elif n.localName == "waypoint":
                waypoints.append(n.childNodes[0].data.strip())
        obj = Object.decode(node, nodePath=None, inEditor=inEditor, lib=lib)
        obj.__class__ = LERope
        
        if inEditor:
            model = loader.loadModel("models/dummy_box")
            model.setScale(0.5,0.5,0.5)
            model.reparentTo(obj.nodePath)        
            model.hide(BitMask32.bit(5))
        
        obj.waypoints = waypoints
        #obj.speed = speed
        #obj.seqTime = seqTime
        
        # Setup the rope
        obj.rope = Rope()
        obj.rope.setup(3,[{'node': obj.getNodePath()}])
        
        obj.rope.reparentTo(render)
        obj.object = None
        obj.oldObject = None
        obj.seqTime = 5.0
        obj.orientationChoice = 2
        obj.startPos = Point3()
        obj.startHpr = VBase3()
        
        
        if not inEditor:
            obj.rope.hide()
        else:
            obj.rope.ropeNode.setThickness(5.0)
            a = AmbientLight("")
            amb = render.attachNewNode(a)
            obj.rope.setLight(amb)
        
        return obj      
    decode = staticmethod(decode)
    
    def encode(self, doc):
        node = Object.encode(self, doc)

        
        for wp in self.waypoints:
            waypoint = doc.createElement("waypoint")
            waypoint.appendChild(doc.createTextNode(wp))
            node.appendChild(waypoint)
        
        return node
    
    def onRemove(self):
        self.rope.detachNode()
        Object.onRemove(self)
        
    def onAdd(self):
        self.rope.reparentTo(render)
        Object.onAdd(self)
        
    def setSeqTime(self, time):
        self.seqTime = time
    def getSeqTime(self):
        return self.seqTime