from pandac.PandaModules import Filename
from Library import Library
from Objects import *
from Sound import *
import xml.dom.minidom
import os
from Conversation import * # Anton added 2/24
from InventoryMgr import *
from GameObject import * #Zeina added 3/23
import Debug

#class that stores dicionaries mapping asset names to filenames
class AssetIndex:
    def __init__(self, library):
        self.meshes = {}
        self.textures = {}
        self.actors = {}
        self.animations = {}
        self.sounds = {}
        self.terrains = {}
        self.conversations = {}
        
        for name, mesh in library.meshes.iteritems():
            self.meshes[name] = mesh.getFullFilename().getFullpath()
            
        for name, tex in library.textures.iteritems():
            self.textures[name] = tex.getFullFilename().getFullpath()
        
        for name, actor in library.actors.iteritems():
            self.actors[name] = actor.getFullFilename().getFullpath()
            
        for name, anim in library.animations.iteritems():
            self.animations[name] = actor.getFullFilename().getFullpath()
            
        for name, sound in library.sounds.iteritems():
            self.sounds[name] = sound.getFullFilename().getFullpath()
        
        for name, terrain in library.terrains.iteritems():
            self.terrains[name] = terrain.getFullFilename().getFullpath()
        
        for name, convo in library.conversations.iteritems():
            self.conversations[name] = convo.getFullFilename().getFullpath()

def loadConversations(sceneFile, libraryFile): # Anton added 2/24
    sceneFilename = Filename(sceneFile)
    libraryFilename = Filename.fromOsSpecific(os.getcwd()) + '/' + libraryFile
    lib = Library(Filename(libraryFilename.getDirname()))
    assetIndex = AssetIndex(lib)
    
    conversationAssets = assetIndex.conversations
    conversationObjects = {}
    
    for key, filename in conversationAssets.items():
        xmlFilename = Filename(filename)
        doc = xml.dom.minidom.parse(xmlFilename.toOsSpecific())
        Debug.debug(__name__,'loading '+str(xmlFilename.toOsSpecific())+'...')
        convo = Conversation.decode(doc)
        conversationObjects[key] = convo
    
    return conversationObjects

def loadInventory(inventoryMgr,inventoryFile):
    try:
        f = open(Filename(inventoryFile).toOsSpecific())
        doc = xml.dom.minidom.parse(f)
        root = doc.childNodes[0]
        
        for n in root.childNodes:
            if n.localName == "inventoryMapEntries":
                inventoryMgr.decode(n)
        
        f.close()
    except IOError:
        print "ERROR:There is no Inventory File exist to load."

#loads a scene outside of the level editor
def loadLevel(sceneFile, libraryFile):
    sceneFilename = Filename(sceneFile)
    libraryFilename = Filename.fromOsSpecific(os.getcwd()) + '/' + libraryFile
    lib = Library(Filename(libraryFilename.getDirname()))
    
    objects = {}
    tempObjs = {}
    assetIndex = AssetIndex(lib)
    sounds = {}
    sequences = {}
    
    f = open(sceneFilename.toOsSpecific())
    doc = xml.dom.minidom.parse(f)
    root = doc.childNodes[0]
    for node in root.childNodes:
        if node.localName == "objects":
            for n in node.childNodes:
                if n.localName:
                    if n.localName == "dummy":
                        obj = Object.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "staticmesh":
                        obj = StaticMesh.decode(n, lib=lib)
                    elif n.localName == "actor":
                        obj = LEActor.decode(n, lib=lib)
                    elif n.localName == "ambient":
                        obj = AmbLight.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "directional":
                        obj = DirLight.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "point":
                        obj = PoiLight.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "spot":
                        obj = SpoLight.decode(n, inEditor=False, lib=lib)
                        if obj.castsShadows:
                            obj.light.setShadowCaster(True, obj.bufferX, obj.bufferY)
                        else:
                            obj.light.setShadowCaster(False)
                    elif n.localName == "camera":
                        obj = Cam.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "sphere":
                        obj = SphereCollider.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "box":
                        obj = BoxCollider.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "plane":
                        obj = PlaneCollider.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "texturecard":
                        obj = LETextureCard.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "LETerrain":
                        obj = LETerrain.decode(n, inEditor=False, lib=lib)
                    
                    tempObjs[obj.name] = obj
                    # If the object is an actor
                    if isinstance(obj, LEActor):
                        # Add any joints to the dictionary
                        for jointName in obj.joints:
                            # Reference by "actorname/jointname"
                            tempObjs[obj.name+"/"+jointName] = obj.joints[jointName]
        elif node.localName == "sounds":
            for n in node.childNodes:
                if n.localName:
                    if n.localName == "sound":
                        sound = Sound.decode(n, inEditor=False, lib=lib)
                    sounds[sound.name] = sound
    
    #make sure everything is parented correctly
    for obj in tempObjs.values():
        # If object is not a joint
        if not isinstance(obj, Joint):
            if obj.parentName == "*render":
                parent = render
            # If the parent is a joint
            elif obj.parentName.find(" <joint>") != -1:
                parName = obj.parentName[0:obj.parentName.index(" <joint>")]
                parent = tempObjs[parName].joint
                parent.setName(parent.getName()[0:parent.getName().index(" <joint>")])
            else:
                parent = tempObjs[obj.parentName].nodePath
                
            obj.nodePath.reparentTo(parent)
            objects[obj.name] = obj.nodePath
        else:
            objects[obj.joint.getParent().getName()+"/"+obj.getName()] = obj.joint
    #apply shaders
    toUpdate = []
    for obj in tempObjs.values():
        # If it is not a joint
        if not isinstance(obj, Joint):
            if obj.shader:
                #fix object shader inputs
                for i in obj.shader.inputs.values():
                    if i.__class__.__name__ == "LEShaderInputObj":
                        i.obj = tempObjs[i.obj]
                    if i.updateMe:
                        toUpdate.append(obj.shader)
                        break
                if obj.shader.active:
                    obj.applyShader()
            
            if isinstance(obj, LELight):
                for name in obj.targetNames:
                    target = tempObjs[name]
                    obj.addTarget(target)
            # Terrain focal points
            # elif isinstance(obj, LETerrain):
                # fpNP = tempObjs[obj.fp]
                # obj.setFocalPoint(fpNP.getNodePath())
            # Camera Waypoints rope and sequence
            elif isinstance(obj, Cam):
                if obj.waypoints != []:
                    # Generate the sequence
                    vertices = []
                    vertices.append({'point': obj.getPos()})
                    for wp in obj.waypoints:
                        o = tempObjs[wp]
                        if o:
                            vertices.append({'node': o.getNodePath()})
                        else:
                            o.waypoints.remove(wp)
                    
                    obj.rope.verts = vertices
                    obj.rope.recompute()
                    obj.genCamSequence()
                    sequences[obj.getName()] = obj.sequence
    def updateShaders(task):
        for s in toUpdate:
            s.update()
        return task.cont
        
    taskMgr.add(updateShaders, 'updateShaders')
    
    return assetIndex, objects, sounds, sequences
        
def loadWorld(sceneFile, libraryFile):
    Debug.debug(__name__,"Loading the world.")
    sceneFilename = Filename(sceneFile)
    libraryFilename = Filename.fromOsSpecific(os.getcwd()) + '/' + libraryFile
    lib = Library(Filename(libraryFilename.getDirname()))
    
    objects = {}
    gameObjects = {}
    tempObjs = {}
    assetIndex = AssetIndex(lib)
    sounds = {}
    sequences = {}
    
    f = open(sceneFilename.toOsSpecific())
    doc = xml.dom.minidom.parse(f)
    root = doc.childNodes[0]
    for node in root.childNodes:
        if node.localName == "objects":
            for n in node.childNodes:
                if n.localName:
                    if n.localName == "dummy":
                        obj = Object.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "staticmesh":
                        obj = StaticMesh.decode(n, lib=lib)
                    elif n.localName == "actor":
                        obj = LEActor.decode(n, lib=lib)
                    elif n.localName == "ambient":
                        obj = AmbLight.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "directional":
                        obj = DirLight.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "point":
                        obj = PoiLight.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "spot":
                        obj = SpoLight.decode(n, inEditor=False, lib=lib)
                        if obj.castsShadows:
                            obj.light.setShadowCaster(True, obj.bufferX, obj.bufferY)
                        else:
                            obj.light.setShadowCaster(False)
                    elif n.localName == "camera":
                        obj = Cam.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "sphere":
                        obj = SphereCollider.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "box":
                        obj = BoxCollider.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "plane":
                        obj = PlaneCollider.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "texturecard":
                        obj = LETextureCard.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "LETerrain":
                        obj = LETerrain.decode(n, inEditor=False, lib=lib)
                    elif n.localName == "LERope":
                        obj = LERope.decode(n, inEditor =  False, lib=lib)
                    
                    tempObjs[obj.name] = obj
                    # If the object is an actor
                    if isinstance(obj, LEActor):
                        # Add any joints to the dictionary
                        for jointName in obj.joints:
                            # Reference by "actorname/jointname"
                            tempObjs[obj.name+"/"+jointName] = obj.joints[jointName]
        elif node.localName == "sounds":
            for n in node.childNodes:
                if n.localName:
                    if n.localName == "sound":
                        sound = Sound.decode(n, inEditor=False, lib=lib)
                    sounds[sound.name] = sound
    
    #make sure everything is parented correctly
    for obj in tempObjs.values():
        # If object is not a joint
        if not isinstance(obj, Joint):
            if obj.parentName == "*render":
                parent = render
            # If the parent is a joint
            elif obj.parentName.find(" <joint>") != -1:
                parName = obj.parentName[0:obj.parentName.index(" <joint>")]
                parent = tempObjs[parName].joint
                parent.setName(parent.getName()[0:parent.getName().index(" <joint>")])
            else:
                parent = tempObjs[obj.parentName].nodePath
            
            if isinstance(obj, LERope):
               vertices = []
               vertices.append({'point': obj.getPos()})
               for wp in obj.waypoints:
                    o = tempObjs[wp]
                    if o:
                        vertices.append({'node': o.getNodePath()})
                    else:
                        obj.waypoints.remove(wp)
                        
               obj.rope.verts = vertices
               obj.rope.recompute()
                   
               obj.nodePath.reparentTo(parent)
               objects[obj.name] = obj.rope
            else:
               obj.nodePath.reparentTo(parent)
               objects[obj.name] = obj.nodePath
               gameObjects[obj.name] = GameObject(obj.nodePath)
               gameObjects[obj.name].setScripts(obj.scripts)
        else:
            objects[obj.joint.getParent().getName()+"/"+obj.getName()] = obj.joint
    #apply shaders
    toUpdate = []
    for obj in tempObjs.values():
        # If it is not a joint
        if not isinstance(obj, Joint):
            if obj.shader:
                #fix object shader inputs
                for i in obj.shader.inputs.values():
                    if i.__class__.__name__ == "LEShaderInputObj":
                        i.obj = tempObjs[i.obj]
                    if i.updateMe:
                        toUpdate.append(obj.shader)
                        break
                if obj.shader.active:
                    obj.applyShader()
            
            if isinstance(obj, LELight):
                for name in obj.targetNames:
                    target = tempObjs[name]
                    obj.addTarget(target)
            # Terrain focal points
            # elif isinstance(obj, LETerrain):
                # fpNP = tempObjs[obj.fp]
                # obj.setFocalPoint(fpNP.getNodePath())
            # Camera Waypoints rope and sequence
            elif isinstance(obj, Cam):
                if obj.waypoints != []:
                    if obj.lookAt is not None:
                        #print obj.lookAt
                        obj.lookAt = tempObjs[obj.lookAt].getNodePath()

                    # Generate the sequence
                    vertices = []
                    #vertices.append({'point': obj.getPos()})
                    for wp in obj.waypoints:
                        o = tempObjs[wp]
                        if o:
                            vertices.append({'node': o.getNodePath()})
                        else:
                            o.waypoints.remove(wp)
                    
                    obj.rope.verts = vertices
                    obj.rope.recompute()
                    obj.genCamSequence()
#            if isinstance(obj, Cam):
#                print obj.waypoints
#                if obj.waypoints != []:
#                    if obj.lookAt is not None:
#                        print obj.lookAt
#                        #obj.lookAt = tempObjs[obj.lookAt].nodePath
#                        print obj.lookAt
#                    obj.genWaypointRope()
#                    print "Here passed"
                    sequences[obj.getName()] = obj.sequence
            #print "weeee"
    def updateShaders(task):
        for s in toUpdate:
            s.update()
        return task.cont
        
    #taskMgr.add(updateShaders, 'updateShaders')
    return assetIndex, objects, gameObjects, sounds, sequences
    
