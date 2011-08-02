"""
Defines ObjectMgrBase
"""

import os, time, wx, types, copy

from direct.task import Task
from direct.actor.Actor import Actor
from pandac.PandaModules import *
from ActionMgr import *
from Objects import *
import xml.dom.minidom

class ObjectMgrBase:
    """ ObjectMgr will create, manage, update objects in the scene """
    
    def __init__(self, editor):
        self.editor = editor

        # main obj repository of objects in the scene
        self.objects = {}
        self.npIndex = {}   #maps nodepaths to objects
        self.colliders = set()  #all of the colliders in the scene
        self.showColliders = True
        self.objectsLastXform = {}  #keeps track of the last transform of all objects for undo purposes

        self.lastUid = ''
        self.lastUidMode = 0
        self.currNodePath = None   

        self.currLiveNP = None
        
        self.mainCharWidget = loader.loadModel('models/startIcon.egg')
        self.mainCharWidget.setColor(0.3, 1.0, 0.3) # CONSIDER: setting colors of the main character could influence startIcon's color
        # CONSIDER: add a camera icon behind the startIcon representing game camera (but could be confusing...cannot click on it)

    #removes all objects from the scene and resets internal data structures
    def reset(self):
        base.direct.deselectAllCB()
        for id in self.objects.keys():
            try:
                self.objects[id].nodePath.detachNode()
                self.removeObjectById(id)
            except KeyError as e:
                pass

        for np in self.npIndex.keys():
            del self.npIndex[np]
               
        self.objects = {}
        self.npIndex = {}
        self.colliders = set()  #node paths of all collision objects in the scene

    #returns an enumerated version of a name that is not currently being used by the scene
    def makeNameUnique(self, name):
        if name.find(':') == -1:
            baseName = name
        else:
            baseName = "".join(name.split(':')[:-1])
        
        n=1
        while True: 
            newName = baseName + ':' + str(n)
            if not newName in self.objects:
                return newName
            n = n + 1

    #Creates a new object of the given type and adds it to the scene        
    def addNewObject(self, type, name = None, nodePath = None, parent=None, asset = None, anims={}, fSelectObject=True, nameStr=None, pos=Vec3(0,0,0)):
        """ function to add new obj to the scene """
        base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        # If no parent is provided, set render to be the parent
        if parent is None:
            parent = self.editor.NPParent

        # Keep this ****
        if not name:
            name = type + ':1'        
        if name in self.objects:
            name = self.makeNameUnique(name)

        # Start the creation of the new object
        newobj = None
        if type == "Empty Node":
            newobj = Object(name, "dummy", nodePath, parent)
        elif type == "Meshes":
            newobj = StaticMesh(name, asset, parent)
        elif type == "Actors":
            newobj = LEActor(name, asset, anims, parent=parent)
        elif type == "Perspective":
            newobj = Cam(name,"persp")
        elif type == "Orthographic":
            newobj = Cam(name,"ortho")
        elif type == "Ambient":
            newobj = AmbLight(name)
        elif type == "Directional":
            newobj = DirLight(name)
        elif type == "Spot":
            newobj = SpoLight(name)
        elif type == "Point":
            newobj = PoiLight(name)
        elif type == "Collision Sphere":
            newobj = SphereCollider(name)
            self.colliders.add(newobj.nodePath)
        elif type == "Collision Box":
            newobj = BoxCollider(name)
            self.colliders.add(newobj.nodePath)
        elif type == "Collision Plane":
            newobj = PlaneCollider(name)
            self.colliders.add(newobj.nodePath)
        elif type == "Textures":
            newobj = LETextureCard(name,asset)
        elif type == "Terrains":
            newobj = LETerrain(name, asset)
        elif type == "Rope":
            newobj = LERope(name,parent=parent)
        else:
            print 'Unrecognized object type: ', type
            return None
        
        newobj.onAdd()
        
        for np in newobj.nodePath.findAllMatches('**/+CollisionNode'):
            self.colliders.add(np)
            if self.showColliders:
                np.show()

        # May want to change the tag ****
        newobj.setTag('OBJRoot','1')

        # insert obj data to main repository
        self.objects[name] = newobj
        self.npIndex[NodePath(newobj.getNodePath())] = name
        
        if not pos:
            pos = Vec3(0,0,0)
        
        newobj.setPos(pos)
        
        if self.editor:
            if fSelectObject:
                self.editor.select(newobj.getNodePath(), fUndo=0)
            self.editor.ui.sceneGraphUI.add(newobj.getNodePath(), parent)
            self.editor.fNeedToSave = True
            
        base.le.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        return newobj
    
    #Adds an already constructed object to the scene
    def addExistingObj(self, obj):
        obj.onAdd()
        self.objects[obj.getName()] = obj
        self.npIndex[NodePath(obj.getNodePath())] = obj.getName()
        self.editor.ui.sceneGraphUI.add(obj.getNodePath(), obj.nodePath.getParent())
        if isinstance(obj, LEActor):
            for j in obj.joints.values():
                self.editor.ui.sceneGraphUI.addJoint(j.joint, j.joint.getParent())
                for child in j.joint.getChildren():
                    if child.hasTag('OBJRoot'):
                        self.editor.ui.sceneGraphUI.add(child, j.joint)
                        

        for np in obj.nodePath.findAllMatches('**/+CollisionNode'):
            self.colliders.add(np)
            if self.showColliders:
                np.show()
        
        if isinstance(obj, Collider):
            self.colliders.add(obj.nodePath)
            if not self.showColliders:
                obj.nodePath.hide()
    
    #changes the name of an object in the scene and updates internal data structures to reflect the change
    def renameObj(self, obj, newName):
        del self.objects[obj.getName()]
        self.objects[newName] = obj
        
        #make sure the object stays locked if it was
        if obj.getName() in base.direct.iRay.unpickable:
            base.direct.iRay.unpickable.remove(obj.getName())
            base.direct.iRay.unpickable.append(newName)
            
        obj.setName(newName)       
        self.npIndex[NodePath(obj.getNodePath())] = newName
    
    #removes an object by name(id)
    def removeObjectById(self, uid):
        obj = self.findObjectById(uid)
        if obj is not None:
            nodePath = obj.getNodePath()
            self.removeObjectByNodePath(nodePath)

            
    def removeObjectByNodePath(self, nodePath):
        uid = self.npIndex.get(NodePath(nodePath))
        if uid:
            if self.objects[uid].nodePath in self.colliders:
                self.colliders.remove(self.objects[uid].nodePath)
            
            for np in self.objects[uid].nodePath.findAllMatches('**/+CollisionNode'):
                if np in self.colliders:
                    self.colliders.remove(np)
            
            self.objects[uid].onRemove()
            #make sure the layer editor doesn't have a reference to this object laying around
            self.editor.ui.layerEditorUI.clearObject(self.objects[uid])
            del self.objects[uid]
            del self.npIndex[NodePath(nodePath)]
            

            # remove children also
            for child in nodePath.getChildren():
                if child.hasTag('OBJRoot'):
                    self.removeObjectByNodePath(child)
            self.editor.fNeedToSave = True
            self.deselectAll()
            base.direct.deselectAllCB()
            
    #returns the object with the given id(name)        
    def findObjectById(self, uid):
        return self.objects.get(uid)

    #returns the object by its nodepath
    def findObjectByNodePath(self, nodePath):
        uid = None
        try:
            uid = self.npIndex.get(NodePath(nodePath))
        except TypeError as e:
            if nodePath is not None:
                uid = self.npIndex.get(NodePath(nodePath.getNodePath()))
        if uid is None:
            return None
        else:
            return self.objects[uid]

    def findObjectByNodePathBelow(self, nodePath):
        for ancestor in nodePath.getAncestors():
            if ancestor.hasTag('OBJRoot'):
                return self.findObjectByNodePath(ancestor)

        return None

    def findObjectsByAsset(self, asset):
        results = []
        for uid in self.objects.keys():
            obj = self.objects[uid]
            if obj.asset == asset: 
                results.append(obj)
                
        return results
    
    def findObjectsByAssetRName(self, asset):
        results = []
        resultsName = []
        for uid in self.objects.keys():
            obj = self.objects[uid]
            if obj.type == asset:
                results.append(obj)
                resultsName.append(obj.name)
        return results, resultsName
    
    # added by Anton on 1/28/11
    def findObjectsByTag(self, tagKey):
        matches = []
        for name, obj in self.objects.items():
             if obj.hasTag(tagKey):
                 matches.append(obj)
        return matches

    def deselectAll(self):
        self.currNodePath = None
        taskMgr.remove('_le_updateObjectUITask')
        self.editor.ui.objectPropertyUI.clearPropUI()

    def selectObject(self, nodePath, fLEPane=0, fMultiSelect=False):
        obj = self.findObjectByNodePath(nodePath)
        if obj is None:
            return
        self.selectObjectCB(obj, fLEPane, fMultiSelect)

    def selectObjectCB(self, obj, fLEPane, fMultiSelect=False):
        self.currNodePath = obj.getNodePath()
        self.objectsLastXform[obj.getName()] = Mat4(self.currNodePath.getMat())
        
        if fLEPane == 0:
            self.editor.ui.sceneGraphUI.select(obj.getName(), ensureVisible=not fMultiSelect)
        
        if not fMultiSelect:
            # [gjeon] to connect transform UI with nodepath's transform
            self.spawnUpdateObjectUITask(obj)
            self.updateObjectPropertyUI(obj)

        # Based on the object type, make certain panels and panes
        # accessible and others not
        
        # Actor
        if isinstance(obj, LEActor):
            self.editor.ui.objectPropertyUI.actorPane.Show()
        else:
            self.editor.ui.objectPropertyUI.actorPane.Hide()
        # Appearance
        if isinstance(obj, LEActor) or isinstance(obj, StaticMesh) or isinstance(obj, LETextureCard):
            self.editor.ui.objectPropertyUI.appearancePane.Show()
        else:
            self.editor.ui.objectPropertyUI.appearancePane.Hide()
        # Light
        if isinstance(obj, LELight):
            self.editor.ui.objectPropertyUI.lightPane.Show()
        else:
            self.editor.ui.objectPropertyUI.lightPane.Hide()
        # Lens
        if isinstance(obj, Cam) and isinstance(obj.getLens(), PerspectiveLens):
            self.editor.ui.objectPropertyUI.lensPane.Show()
        else:
            self.editor.ui.objectPropertyUI.lensPane.Hide()
            
        # Ortho Lens
        if isinstance(obj, Cam) and isinstance(obj.getLens(), OrthographicLens):
            self.editor.ui.objectPropertyUI.orthoLensPane.Show()
        else:
            self.editor.ui.objectPropertyUI.orthoLensPane.Hide()
        
        # Light lens
        if isinstance(obj, SpoLight):
            self.editor.ui.objectPropertyUI.lightLensPane.Show()
        else:
            self.editor.ui.objectPropertyUI.lightLensPane.Hide()
        
        if isinstance(obj, LETerrain):
            self.editor.ui.objectPropertyUI.terrainPane.Show()
            self.editor.ui.objectPropertyUI.appearancePane.Show()
        else:
            self.editor.ui.objectPropertyUI.terrainPane.Hide()
        # Camera
        if isinstance(obj, Cam):
            self.editor.ui.objectPropertyUI.cameraPane.Show()
        else:
            self.editor.ui.objectPropertyUI.cameraPane.Hide()
            
        if isinstance(obj, Collider):
            self.editor.ui.objectPropertyUI.colliderPane.Show()
        else:
            self.editor.ui.objectPropertyUI.colliderPane.Hide()
        
        # Shader
        if isinstance(obj, Cam) or isinstance(obj, LELight) or\
        isinstance(obj, Collider):
            self.editor.ui.objectPropertyUI.shaderPane.Hide()
        else:
            self.editor.ui.objectPropertyUI.shaderPane.Show()
        
        # Game
        if isinstance(obj, LEActor):
            self.editor.ui.objectPropertyUI.gamePane.Show()
        else:
            self.editor.ui.objectPropertyUI.gamePane.Hide()
            
        #Script
        if isinstance(obj, LEActor) or isinstance(obj,StaticMesh)or isinstance(obj, Collider):
            self.editor.ui.objectPropertyUI.scriptPane.Show()
            self.editor.ui.objectPropertyUI.scriptPanel.update()
        else:
            self.editor.ui.objectPropertyUI.scriptPane.Hide()
            
        # Rope
        if isinstance(obj, LERope):
            self.editor.ui.objectPropertyUI.ropePane.Show()
            self.editor.ui.objectPropertyUI.particlePane.Hide()
        else:
            self.editor.ui.objectPropertyUI.particlePane.Show()
            self.editor.ui.objectPropertyUI.ropePane.Hide()
            
                                                                                
        self.editor.ui.objectPropertyUI.Layout()
        self.editor.ui.objectPropertyUI.Refresh()
        self.editor.ui.objectPropertyUI.Update()

    def updateObjectPropertyUI(self, obj):
        self.editor.ui.objectPropertyUI.updateProps(obj, True)
        self.editor.fNeedToSave = True
    
    def updateMainCharWidget(self):
        mainCharList = self.findObjectsByTag('LE-mainChar')
        if len(mainCharList) <= 0:
            return
        elif len(mainCharList) > 1:
            print 'WARNING: more than one main character was found : ', mainCharList
        mainChar = mainCharList[0]
        
        if mainChar != None:
            self.mainCharWidget.reparentTo(mainChar.getNodePath())
            offset = int(mainChar.getTag('LE-mainChar'))
            self.mainCharWidget.setH(render, offset + mainChar.getNodePath().getH(render))
        else:
            self.mainCharWidget.hide()
        
    def onEnterObjectPropUI(self, unBind=True):
        taskMgr.remove('_le_updateObjectUITask')
        if unBind:
            self.editor.ui.bindKeyEvents(False)

    def onLeaveObjectPropUI(self, unBind=True):
        if hasattr(base,"direct"):
            obj = self.findObjectByNodePath(base.direct.selected.last)
            self.spawnUpdateObjectUITask(obj)
            if unBind:
                self.editor.ui.bindKeyEvents(True)

    def spawnUpdateObjectUITask(self, obj):
        if self.currNodePath is None:
            return

        taskMgr.remove('_le_updateObjectUITask')
        t = Task.Task(self.updateObjectUITask)
        t.obj = obj
        taskMgr.add(t, '_le_updateObjectUITask')
        
    def updateObjectUITask(self, state):
        self.editor.ui.objectPropertyUI.updateProps(state.obj, True)
        
        return Task.cont
        
    def updateObjectTransform(self, event):
        if self.currNodePath is None:
            return

        np = hidden.attachNewNode('temp')
        np.setX(float(self.editor.ui.objectPropertyUI.propX.getValue()))
        np.setY(float(self.editor.ui.objectPropertyUI.propY.getValue()))
        np.setZ(float(self.editor.ui.objectPropertyUI.propZ.getValue()))

        h = float(self.editor.ui.objectPropertyUI.propH.getValue())
        while h < 0:
            h = h + 360.0

        while h > 360:
            h = h - 360.0

        p = float(self.editor.ui.objectPropertyUI.propP.getValue())
        while p < 0:
            p = p + 360.0

        while p > 360:
            p = p - 360.0

        r = float(self.editor.ui.objectPropertyUI.propR.getValue())
        while r < 0:
            r = r + 360.0

        while r > 360:
            r = r - 360.0 
            
        np.setH(h)
        np.setP(p)
        np.setR(r)

        np.setSx(float(self.editor.ui.objectPropertyUI.propSX.getValue()))
        np.setSy(float(self.editor.ui.objectPropertyUI.propSY.getValue()))
        np.setSz(float(self.editor.ui.objectPropertyUI.propSZ.getValue()))        

        obj = self.findObjectByNodePath(self.currNodePath)
        action = ActionTransformObj(self.editor, obj.getName(), Mat4(np.getMat()))
        self.editor.actionMgr.push(action)
        np.remove()
        action()
        self.editor.fNeedToSave = True
        
    def setObjectTransform(self, uid, xformMat):
        obj = self.findObjectById(uid)
        if obj:
            obj.getNodePath().setMat(xformMat)
        self.editor.fNeedToSave = True
        
    def updateObjectColor(self, r, g, b, a, np=None):
        if np is None:
            np = self.currNodePath

        obj = self.findObjectByNodePath(np)
        if not obj:
            return
        name = str(np)
        if isinstance(obj, LELight):
            obj.setColor(Vec4(r,g,b,a))
        else:
            np.setColorScale(r,g,b,a)
            for child in np.getChildren():
                if not child.hasTag('OBJRoot') and\
                   not child.hasTag('_le_sys') and\
                   child.getName() != 'bboxLines':
                    child.setTransparency(1)
                    child.setColorScale(r, g, b, a)
        self.editor.fNeedToSave = True
    
    def encode(self, doc):
        objs = doc.createElement("objects")
        for obj in self.objects.values():
            objs.appendChild(obj.encode(doc))
            
        return objs
    
    def BVWEncode(self):
        lines = []
        lines.append("def loadLevel():\n")
        lines.append("    objects = {}\n")
        lines.append("    sequences = {}\n")
        lines.append("\n")
        
        lines.append("    ##Initialize objects\n")
        lines.append("\n")
        
        lights = []
        shaderObjs = []
        cameras = []
        
        for o in self.objects.values():
            lines.extend(o.BVWEncode())
            lines.append("\n")
            if isinstance(o, LELight):
                lights.append(o)
            elif isinstance(o, Cam):
                cameras.append(o)
            if o.shader and o.shaderActive:
                shaderObjs.append(o)
            
        
        lines.append("    ##Parent everything correctly\n")
        lines.append("\n")
        for o in self.objects.values():
            if o.nodePath.getParent() != render:
                parent = self.findObjectByNodePath(o.nodePath.getParent())
                if parent:
                    lines.append("    objects['" + o.name + "'].reparentTo(objects['" + parent.name + "'])\n")
                else:   #Handle joints
                    jointName = o.nodePath.getParent().getName().split(" <")[0]
                    grandParentName = o.nodePath.getParent().getParent().getName()
                    fullName = grandParentName + '/' + jointName
                    lines.append("    objects['" + o.name + "'].reparentTo(objects['" + fullName + "'])\n")
        
        lines.append("\n    #Make sure camera sequences are added correctly\n")
        for o in cameras:
            if isinstance(o, Cam):
                if o.waypoints != []:
                    lines.extend(o.BVWEncodeSequence())
                
        lines.append("\n")
        lines.append("    ##Set light targets\n")
        lines.append("\n")
        for light in lights:
            if light.targets:
                for t in light.targets:
                    lines.append("    objects['" + t.name + "'].setLight(objects['" + light.name + "'])\n")
                lines.append("\n")
          
        if shaderObjs:
            lines.append("    ##Set up shaders\n")
            lines.append("\n")
            lines.append("    global timeObjs, cameraObjs\n")
            lines.append("    timeObjs = []\n")
            lines.append("    cameraObjs = []\n")
            lines.append("\n")
            lines.append("    render.setShaderAuto()\n")
            lines.append("\n")
            
            for o in shaderObjs:
                lines.extend(o.shader.BVWEncode())      
            lines.append("\n")
            
            lines.append("    taskMgr.add(updateShaders, 'updateShaders')\n")
            
        lines.append("    return objects, sequences\n")
        
        if shaderObjs:
            lines.append("\n")
            lines.append("def updateShaders(task):\n")
            lines.append("    global timeObjs, cameraObjs\n")
            lines.append("\n")
            lines.append("    for inputName, offset, np in timeObjs:\n")
            lines.append("        np.setShaderInput(inputName, globalClock.getFrameTime() + offset)\n")
            lines.append("\n")
            lines.append("    for inputName, np in cameraObjs:\n")
            lines.append("        np.setShaderInput(inputName, base.cam.getPos(render))\n")
            lines.append("\n")
            lines.append("    return task.cont\n")
        
        return lines
    
    #loads a new scene or merges one into the curretn one
    def decode(self, node, merge=False, lib=None, otherName=None, newNodeName=''):
        if not merge:
            #clear the scene
            self.reset()
            
        if not lib:
            lib = base.le.lib
            
        #add prefixes to all of the objects that are added from another project
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
        
        if newNodeName:
            newNode = self.addNewObject('Empty Node', name = newNodeName, parent=render, pos = Vec3(0,0,0))
            
        
        newobjs = {}
        for n in node.childNodes:
            if n.localName:
                if n.localName == "dummy":
                    obj = Object.decode(n, lib=lib)
                elif n.localName == "staticmesh":
                    obj = StaticMesh.decode(n, lib=lib)
                elif n.localName == "actor":
                    obj = LEActor.decode(n, lib=lib)
                elif n.localName == "ambient":
                    obj = AmbLight.decode(n, lib=lib)
                elif n.localName == "directional":
                    obj = DirLight.decode(n, lib=lib)
                elif n.localName == "point":
                    obj = PoiLight.decode(n, lib=lib)
                elif n.localName == "spot":
                    obj = SpoLight.decode(n, lib=lib)
                elif n.localName == "camera":
                    obj = Cam.decode(n, lib=lib)
                elif n.localName == "sphere":
                    obj = SphereCollider.decode(n, lib=lib)
                elif n.localName == "box":
                    obj = BoxCollider.decode(n, lib=lib)
                elif n.localName == "texturecard":
                    obj = LETextureCard.decode(n, lib=lib)
                elif n.localName == "plane":
                    obj = PlaneCollider.decode(n, lib=lib)
                elif n.localName == "LETerrain":
                    obj = LETerrain.decode(n, lib=lib)
                elif n.localName == "LERope":
                    obj = LERope.decode(n, lib=lib)
                else:
                    print 'Unrecognized object type: ' + n.localName
                obj.setName(prefix + obj.name)
                if obj.parentName != "*render":
                    obj.parentName = prefix + obj.parentName
                ## if obj.parentName.find(" <joint>") != -1:
                    ## if obj.grandParentName != "*render":
                        ## obj.grandParentName = prefix + obj.grandParentName
                    
                newobjs[obj.getName()] = obj
                if obj.getName() in self.objects:
                    raise Util.SceneMergeError()
        
        #actually add things to the scene
        for obj in newobjs.values():
            self.addExistingObj(obj)
        
        #make sure everything is parented correctly
        for obj in newobjs.values():
            if obj.parentName == "*render":
                if newNodeName:
                    parent = newNode.nodePath
                else:
                    parent = render
            # If the parent is a joint
            elif obj.parentName.find(" <joint>") != -1:
                grandParent = newobjs[obj.parentName[0:obj.parentName.index("/")]]
                parentsName = obj.parentName[obj.parentName.index("/")+1:obj.parentName.index(" <joint>")]
                parent = grandParent.joints[parentsName].joint
            else:
                parent = newobjs[obj.parentName].nodePath
            obj.nodePath.reparentTo(parent)
            pos = obj.nodePath.getPos()
            
            #fix the scenegraph UI
            
            # If the object is an actor
            if isinstance(obj, LEActor):
                # Put the exposed and controlled joints in the scenegraph tree
                for jointName in obj.joints:
                    self.editor.ui.sceneGraphUI.addJoint(obj.joints[jointName], obj)
            
            if parent.getName().find(" <joint>") != -1:
                sceneGraphUI = self.editor.ui.sceneGraphUI
                objItem = sceneGraphUI.traverse(sceneGraphUI.tree.GetRootItem(), obj.getName())
                parentItem = sceneGraphUI.tree.GetItemParent(objItem)
                grandParentNP = parent.getParent()
                newParentItem = sceneGraphUI.traverse(sceneGraphUI.tree.GetRootItem(), grandParentNP.getName()+"/"+parent.getName())
                
                sceneGraphUI.reParent(objItem, newParentItem, obj.getName())
            elif parent != render:
                sceneGraphUI = self.editor.ui.sceneGraphUI
                objItem = sceneGraphUI.traverse(sceneGraphUI.tree.GetRootItem(), obj.getName())
                parentItem = sceneGraphUI.tree.GetItemParent(objItem)
                parentObj = self.findObjectByNodePath(parent)
                newParentItem = sceneGraphUI.traverse(sceneGraphUI.tree.GetRootItem(), parentObj.getName())
                
                sceneGraphUI.reParent(objItem, newParentItem, obj.getName())
            
            obj.setPos(pos)
        
        #apply shaders and set light targets
        for obj in newobjs.values():
            if obj.shader:
                #fix object shader inputs
                for i in obj.shader.inputs.values():
                    if i.__class__.__name__ == "LEShaderInputObj":
                        i.obj = newobjs[prefix + i.obj]
                if obj.shader.active:
                    obj.applyShader()
            # Light targets
            if isinstance(obj, LELight):
                for name in obj.targetNames:
                    target = newobjs[prefix + name]
                    obj.addTarget(target)
                if not obj.targetNames and newNodeName:
                    obj.addTarget(newNode)
            # Terrain focal points
#            elif isinstance(obj, LETerrain):
#                fpNP = self.editor.objectMgr.findObjectById(obj.fp)
#                obj.setFocalPoint(fpNP.getNodePath())
            # Camera Waypoints rope and sequence
            if isinstance(obj, Cam):
                if obj.waypoints != []:
                    if obj.lookAt is not None:
                        #print obj.lookAt
                        obj.lookAt = self.findObjectById(obj.lookAt).nodePath
                    obj.genWaypointRope()
            
            if isinstance(obj, LERope):
                if obj.waypoints != []:
                    #if obj.lookAt is not None:
                    #    print obj.lookAt
                    #    obj.lookAt = self.findObjectById(obj.lookAt).nodePath
                    obj.genWaypointRope()
            
    #copies an object and everything below it in the scene graph adn adds it to the scene    
    def duplicateObject(self, nodePath, parentNP=None):
        obj = self.findObjectByNodePath(nodePath)
        if isinstance(obj, LETerrain):
            return
        if nodePath in self.copiedNPs or nodePath in self.newNPs:
            return
        else:
            self.copiedNPs.append(nodePath)
            
        if not parentNP:
            parentNP = nodePath.getParent()
        
        obj = self.findObjectByNodePath(nodePath)
        if obj is None:
            return None
       
        newObj = copy.copy(obj)
        newObj.nodePath.reparentTo(parentNP)
        newObj.setName(self.makeNameUnique(newObj.name))
        newObj.reattach()
        self.newNPs.append(newObj.nodePath)
        self.addExistingObj(newObj)
        
        for child in nodePath.getChildren():
            if child.hasTag('OBJRoot'):
                self.duplicateObject(child, newObj.nodePath)
        
        if isinstance(obj, LEActor):
            for k in obj.joints.keys():
                oldJoint = obj.joints[k]
                newJoint = newObj.joints[k]
                for child in oldJoint.joint.getChildren():
                    if child.hasTag('OBJRoot'):
                        self.duplicateObject(child, newJoint.joint)
        
        return newObj
    
    #duplicates all of the selected objects
    def duplicateSelected(self):
        selectedNPs = base.direct.selected.getSelectedAsList()
        self.newNPs = []
        self.copiedNPs = []
        newSelection = []
        for nodePath in selectedNPs:
            copy = True
            for otherNP in selectedNPs:
                if nodePath != otherNP and otherNP.isAncestorOf(nodePath):
                    copy = False
            
            if copy:
                newObj = self.duplicateObject(nodePath)
                if newObj:
                    newSelection.append(newObj.nodePath)

        base.direct.deselectAllCB()
        for newNodePath in newSelection:
            base.direct.select(newNodePath, fMultiSelect = 1, fUndo=0)

        self.editor.fNeedToSave = True
