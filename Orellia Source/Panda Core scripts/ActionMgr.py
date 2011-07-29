from pandac.PandaModules import *
from copy import copy
from Objects import LEActor

#Class to manage all undoable actions taken in the editor
class ActionMgr:
    def __init__(self):
        self.undoList = []
        self.redoList = []

    def reset(self):
        while len(self.undoList) > 0:
            action = self.undoList.pop()

        while len(self.redoList) > 0:
            action = self.redoList.pop()

    def push(self, action):
        self.undoList.append(action)
        if len(self.redoList) > 0:
            self.redoList.pop()

    def undo(self, evt=None):
        if len(self.undoList) < 1:
            print 'No more undo'
        else:
            action = self.undoList.pop()
            self.redoList.append(action)
            action.undo()
            if base.direct.selected.last:
                obj = base.le.objectMgr.findObjectByNodePath(base.direct.selected.last)
                if obj:
                    base.le.ui.objectPropertyUI.updateProps(obj)

    def redo(self, evt=None):
        if len(self.redoList) < 1:
            print 'No more redo'
        else:
            action = self.redoList.pop()
            self.undoList.append(action)
            action.redo()
            if base.direct.selected.last:
                obj = base.le.objectMgr.findObjectByNodePath(base.direct.selected.last)
                if obj:
                    base.le.ui.objectPropertyUI.updateProps(obj)

class ActionBase:
    """ Base class for user actions """

    def __init__(self, editor, function, *args, **kargs):
        if function is None:
            def nullFunc():
                pass
            function = nullFunc
        self.function = function
        self.args = args
        self.kargs = kargs
        self.result = None
        self.editor = editor

    def __call__(self):
        self.saveStatus()
        self.result = self.function(*self.args, **self.kargs)
        self.editor.fNeedToSave = True
        self.postCall()
        return self.result

    def redo(self):
        return self()

    def saveStatus(self):
        # save object status for undo here
        pass

    def postCall(self):
        # implement post process here
        pass
        
    def undo(self):
        print "undo method is not defined for this action"

class ActionAddNewObj(ActionBase):
    """ Action class for adding new object """
    
    def __init__(self, editor, *args, **kargs):
        self.editor = editor
        function = self.editor.objectMgr.addNewObject
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.uid = None

    def postCall(self):
        obj = self.editor.objectMgr.findObjectByNodePath(self.result)
        if obj:
            self.uid = obj.getName()

    def redo(self):
        if self.uid is None:
            print "Can't redo this add"        
        else:
            self.result = self()
            return self.result
            
    def undo(self):
        if self.result is None:
            print "Can't undo this add"
        else:
            if self.uid:
                obj = self.editor.objectMgr.findObjectById(self.uid)
            else:
                obj = self.editor.objectMgr.findObjectByNodePath(self.result)
            if obj:
                self.uid = obj.getName()
                self.editor.ui.sceneGraphUI.delete(self.uid)
                base.direct.deselect(obj.getNodePath())
                base.direct.removeNodePath(obj.getNodePath())
                self.result = None
            else:
                print "Can't undo this add"
                
                
class ActionDeleteObj(ActionBase):
    """ Action class for deleting object """

    def __init__(self, editor, *args, **kargs):
        self.editor = editor
        
        def detachAllSelected():
            for np in base.direct.selected.getSelectedAsList():
                np.detachNode()
                obj = self.editor.objectMgr.findObjectByNodePath(np)
                if obj:
                    uid = obj.name
                    self.editor.objectMgr.removeObjectByNodePath(np)
                    self.editor.ui.sceneGraphUI.delete(uid)
            base.direct.selected.deselectAll()
        
        #function = base.direct.removeAllSelected
        function = detachAllSelected
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.selectedUIDs = []
        self.hierarchy = {}
        self.objs = {}
    
    def saveStatus(self):
        selectedNPs = base.direct.selected.getSelectedAsList()
        self.layerIndex = {}
        def saveObjStatus(np, isRecursive=True):
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            if obj:
                uid = obj.getName()
                if not isRecursive:
                    self.selectedUIDs.append(uid)
                objNP = obj.getNodePath()
                self.objs[uid] = obj
                parentNP = objNP.getParent()
                if parentNP == render:
                    self.hierarchy[uid] = None
                else:
                    parentObj = self.editor.objectMgr.findObjectByNodePath(parentNP)
                    if parentObj:
                        self.hierarchy[uid] = parentObj.getName()
                
                if obj in self.editor.ui.layerEditorUI.objIndex:
                    self.layerIndex[obj] = self.editor.ui.layerEditorUI.objIndex[obj]
                
                for child in np.getChildren():
                    if child.hasTag('OBJRoot'):
                        saveObjStatus(child)

        for np in selectedNPs:
            saveObjStatus(np, False)

    def undo(self):
        if len(self.hierarchy.keys()) == 0 or\
           len(self.objs.keys()) == 0:
            print "Can't undo this deletion"
        else:
            def restoreObject(uid, parentNP):
                self.objs[uid].nodePath.reparentTo(parentNP)
                self.objs[uid].reattach()
                self.editor.objectMgr.addExistingObj(self.objs[uid])
                if self.objs[uid] in self.layerIndex:
                    layerName = self.layerIndex[self.objs[uid]].name
                    self.editor.ui.layerEditorUI.addObjectToLayer(layerName, self.objs[uid])
                

            while (len(self.hierarchy.keys()) > 0):
                for uid in self.hierarchy.keys():
                    if self.hierarchy[uid] is None:
                        parentNP = render
                        restoreObject(uid, parentNP)
                        del self.hierarchy[uid]
                    else:
                        parentObj = self.editor.objectMgr.findObjectById(self.hierarchy[uid])
                        if parentObj:
                            parentNP = parentObj.getNodePath()
                            restoreObject(uid, parentNP)
                            del self.hierarchy[uid]

            base.direct.deselectAllCB()
            for uid in self.selectedUIDs:
                obj = self.editor.objectMgr.findObjectById(uid)
                if obj:
                    self.editor.select(obj.getNodePath(), fMultiSelect=1, fUndo=0)

            self.selectedUIDs = []
            self.hierarchy = {}
            self.objs = {}                     

class ActionChangeHierarchy(ActionBase):
     """ Action class for changing Scene Graph Hierarchy """

     def __init__(self, editor, oldGrandParentId, oldParentId, newParentId, childName, *args, **kargs):
         self.editor = editor
         self.oldGrandParentId = oldGrandParentId
         self.oldParentId = oldParentId
         self.newParentId = newParentId
         self.childName = childName
         function = self.editor.ui.sceneGraphUI.parent
         ActionBase.__init__(self, editor, function, self.oldParentId, self.newParentId, self.childName, **kargs)

     def undo(self):
         self.editor.ui.sceneGraphUI.parent(self.oldParentId, self.oldGrandParentId, self.childName)

class ActionSelectObj(ActionBase):
    """ Action class for adding new object """
    
    def __init__(self, editor, *args, **kargs):
        self.editor = editor
        function = base.direct.selectCB
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.selectedUIDs = []

    def saveStatus(self):
        self.id = self.editor.objectMgr.findObjectByNodePath(self.args[0]).name
        selectedNPs = base.direct.selected.getSelectedAsList()
        for np in selectedNPs:
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            if obj:
                uid = obj.getName()
                self.selectedUIDs.append(uid)
    
    def redo(self):
        #make sure we find the object by id in case we are dealing with a new node path
        np = self.editor.objectMgr.findObjectById(self.id).nodePath
        base.direct.selectCB(np,*self.args[1:], **self.kargs)
                
    def undo(self):
        base.direct.deselectAllCB()
        for uid in self.selectedUIDs:
            obj = self.editor.objectMgr.findObjectById(uid)
            if obj:
                self.editor.select(obj.getNodePath(), fMultiSelect=1, fUndo=0)
        self.selectedUIDs = []
        
class ActionTransformObj(ActionBase):
    """ Action class for object transformation """

    def __init__(self, editor, *args, **kargs):
        self.editor = editor
        function = self.editor.objectMgr.setObjectTransform
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.uid = args[0]
        self.origMat = None

    def saveStatus(self):
        obj = self.editor.objectMgr.findObjectById(self.uid)
        if obj:
            self.origMat = Mat4(self.editor.objectMgr.objectsLastXform[obj.getName()])

    def __call__(self, *args, **kargs):
        self.result = ActionBase.__call__(self, *args, **kargs)
        obj = self.editor.objectMgr.findObjectById(self.uid)
        if obj:
            self.editor.objectMgr.objectsLastXform[self.uid] = Mat4(obj.getNodePath().getMat())        
        return self.result

    def undo(self):
        if self.origMat is None:
            print "Can't undo this transform"
        else:
            obj = self.editor.objectMgr.findObjectById(self.uid)
            if obj:
                obj.getNodePath().setMat(self.origMat)
                self.editor.objectMgr.objectsLastXform[self.uid] = Mat4(self.origMat)
            del self.origMat
            self.origMat = None

class ActionDropSelectedToGround(ActionBase):
    def __init__(self, editor, *args, **kargs):
        func = editor.dropSelectedToGround
        ActionBase.__init__(self, editor, func, *args, **kargs)
    
    def saveStatus(self):
        self.origTransforms = {}
        
        for np in base.direct.selected.getSelectedAsList():
            id = self.editor.objectMgr.findObjectByNodePath(np).name
            self.origTransforms[id] = copy(np.getMat())
    
    def __call__(self, *args, **kargs):
        self.result = ActionBase.__call__(self, *args, **kargs)
        
        for np in base.direct.selected.getSelectedAsList():
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            if obj:
                self.editor.objectMgr.objectsLastXform[obj.name] = Mat4(obj.getNodePath().getMat())
                
        return self.result
    
    def undo(self):
        for id, mat in self.origTransforms.iteritems():
            obj = self.editor.objectMgr.findObjectById(id)
            if obj:
                obj.nodePath.setMat(mat)
                self.editor.objectMgr.objectsLastXform[obj.name] = Mat4(obj.getNodePath().getMat())
            
#Generic action for basic setter/getter methods
class ActionSetProperty(ActionBase):
    def __init__(self, editor, setter, getter, *args, **kargs):
        self.setter = setter
        self.getter = getter
        ActionBase.__init__(self, editor, self.setter, *args, **kargs)

    def saveStatus(self):
        self.oldValue = copy(self.getter())
    
    def undo(self):
        self.setter(self.oldValue)

#Generic action for things that don't require saving state
class ActionGeneric(ActionBase):
    def __init__(self, editor, doFunc, undoFunc, *args, **kargs):
        function = doFunc
        self.undoFunc = undoFunc
        ActionBase.__init__(self, editor, function, *args, **kargs)
        
    def undo(self):
        self.undoFunc()

class ActionCreateJoint(ActionBase):
    def __init__(self, editor, doFunc, undoFunc, *args, **kargs):
        function = doFunc
        self.undoFunc = undoFunc
        ActionBase.__init__(self, editor, function, *args, **kargs)
    
    def undo(self):
        self.undoFunc(self.args[0], self.args[1])

class ActionRemoveJoint(ActionBase):
    def __init__(self, editor, doFunc, undoFunc, *args, **kargs):
        function = doFunc
        self.undoFunc = undoFunc
        ActionBase.__init__(self, editor, function, *args, **kargs)
    
    def undo(self):
        self.undoFunc(self.args[0], self.args[1])
        
class ActionRenameObj(ActionBase):
    def __init__(self, editor, oldName, newName, *args, **kargs):
        self.editor = editor
        self.obj = self.editor.objectMgr.findObjectById(oldName)
        self.oldName = oldName
        self.newName = newName
        
        def rename():
            self.editor.objectMgr.renameObj(self.obj, self.newName)
            self.editor.ui.sceneGraphUI.changeLabel(self.oldName, self.newName)
            if isinstance(self.obj, LEActor):
                for j in self.obj.joints.keys():
                    self.editor.ui.sceneGraphUI.changeLabel(self.oldName + '/' + j + ' <joint>', self.newName + '/' + j + ' <joint>')
            if self.oldName in self.editor.objectMgr.objectsLastXform:
                self.editor.objectMgr.objectsLastXform[self.newName] = self.editor.objectMgr.objectsLastXform[self.oldName]
                del self.editor.objectMgr.objectsLastXform[self.oldName]
    
        function = rename
        ActionBase.__init__(self, editor, function, *args, **kargs)
    
    def undo(self):
        self.editor.objectMgr.renameObj(self.obj, self.oldName)
        self.editor.ui.sceneGraphUI.changeLabel(self.newName, self.oldName)
        self.editor.objectMgr.objectsLastXform[self.oldName] = self.editor.objectMgr.objectsLastXform[self.newName]
        del self.editor.objectMgr.objectsLastXform[self.newName]
    
class ActionDeselectAll(ActionBase):
    
    def __init__(self, editor, *args, **kargs):
        self.editor = editor
        function = base.direct.deselectAllCB
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.selectedUIDs = []

    def saveStatus(self):
        selectedNPs = base.direct.selected.getSelectedAsList()
        for np in selectedNPs:
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            if obj:
                uid = obj.getName()
                self.selectedUIDs.append(uid)

    def undo(self):
        base.direct.deselectAllCB()
        for uid in self.selectedUIDs:
            obj = self.editor.objectMgr.findObjectById(uid)
            if obj:
                self.editor.select(obj.getNodePath(), fMultiSelect=1, fUndo=0)
        self.selectedUIDs = []

class ActionDuplicateSelected(ActionBase):
    def __init__(self, editor, *args, **kargs):
        self.editor = editor
        function = self.editor.objectMgr.duplicateSelected
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.selectedUIDs = []
        
    def saveStatus(self):
        selectedNPs = base.direct.selected.getSelectedAsList()
        for np in selectedNPs:
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            if obj:
                uid = obj.getName()
                self.selectedUIDs.append(uid)

    def undo(self):
        for np in base.direct.selected.getSelectedAsList():
            obj = self.editor.objectMgr.findObjectByNodePath(np)
            if not obj:
                continue
            uid = obj.name
            self.editor.ui.sceneGraphUI.delete(uid)
            self.editor.objectMgr.removeObjectByNodePath(np)
            np.removeNode()
        base.direct.removeAllSelected()
        base.direct.deselectAllCB()
        for uid in self.selectedUIDs:
            obj = self.editor.objectMgr.findObjectById(uid)
            if obj:
                self.editor.select(obj.getNodePath(), fMultiSelect=1, fUndo=0)
        self.selectedUIDs = []
        
#### layer operations
class ActionAddLayer(ActionBase):
    def __init__(self, editor, *args, **kargs):
        function = editor.ui.layerEditorUI.addNewLayer
        ActionBase.__init__(self, editor, function, *args, **kargs)
        
    def undo(self):
        self.editor.ui.layerEditorUI.deleteLayer(self.result)

class ActionDeleteLayer(ActionBase):
    def __init__(self, editor, layerName, *args, **kargs):
        function = editor.ui.layerEditorUI.deleteLayer
        self.layerName = layerName
        ActionBase.__init__(self, editor, function, self.layerName, *args, **kargs)
    
    def saveStatus(self):
        self.deletedLayer = self.editor.ui.layerEditorUI.layers[self.layerName]
        self.objs = list(self.deletedLayer.objects)
    
    def undo(self):
        self.editor.ui.layerEditorUI.addNewLayer(self.layerName)
        for obj in self.objs:
            self.editor.ui.layerEditorUI.addObjectToLayer(self.layerName, obj)
        if self.deletedLayer.locked:
            self.editor.ui.layerEditorUI.lockLayer(self.layerName)
        if self.deletedLayer.hidden:
            self.editor.ui.layerEditorUI.hideLayer(self.layerName)
        
class ActionDeleteJoint(ActionBase):
    """ Action class for deleting object """

    def __init__(self, editor, joint, *args, **kargs):
        self.editor = editor
        self.joint = joint
        
        self.children = {}
        def detachAllChildren():
            for child in joint.joint.getChildren():
                child.detachNode()
            base.direct.selected.deselectAll()
        
        #function = base.direct.removeAllSelected
        function = detachAllChildren
        ActionBase.__init__(self, editor, function, *args, **kargs)
        self.selectedUIDs = []
        self.hierarchy = {}
        self.objs = {}
    
    def saveStatus(self):
        selectedNPs = base.direct.selected.getSelectedAsList()
        #selectedNPs.insert(1,self.joint.joint)
        self.layerIndex = {}
        def saveObjStatus(np, isRecursive=True):
            if np.getName().find(" <joint>") != -1:
                uid = np.getParent().getName()+"/"+np.getName()
                parentObj = self.editor.objectMgr.findObjectByNodePath(np.getParent())
                self.objs[uid] = parentObj.joints[np.getName()[0:np.getName().index(" <joint>")]]
                self.hierarchy[uid] = np.getParent().getName()
                for child in np.getChildren():
                    if child.hasTag('OBJRoot'):
                        saveObjStatus(child)
            else:
                obj = self.editor.objectMgr.findObjectByNodePath(np)
                if obj:
                    uid = obj.getName()
                    if not isRecursive:
                        self.selectedUIDs.append(uid)
                    objNP = obj.getNodePath()
                    self.objs[uid] = obj
                    parentNP = objNP.getParent()
                    if parentNP == render:
                        self.hierarchy[uid] = None
                    elif parentNP.getName().find(" <joint>") != -1:
                        grandParentObj = self.editor.objectMgr.findObjectByNodePath(parentNP.getParent())
                        parentObj = grandParentObj.joints[parentNP.getName()[0:parentNP.getName().index(" <joint>")]]
                        if parentObj:
                            self.hierarchy[uid] = grandParentObj.getName()+"/"+parentObj.getName()
                    else:
                        parentObj = self.editor.objectMgr.findObjectByNodePath(parentNP)
                        if parentObj:
                            self.hierarchy[uid] = parentObj.getName()
                    
                    if obj in self.editor.ui.layerEditorUI.objIndex:
                        self.layerIndex[obj] = self.editor.ui.layerEditorUI.objIndex[obj]
                    if isinstance(obj, LEActor):
                        for joint in obj.joints:
                            saveObjStatus(obj.joints[joint].joint)
                    
                    for child in np.getChildren():
                        if child.hasTag('OBJRoot'):
                            saveObjStatus(child, False)

        for np in selectedNPs:
            saveObjStatus(np, False)
            
    def undo(self):
        self.editor.actionMgr.undo()
        if len(self.hierarchy.keys()) == 0 or\
           len(self.objs.keys()) == 0:
            print "Can't undo this deletion"
        else:
            def restoreObject(uid, parentNP):
                if uid.find(" <joint>") != -1:
                    parentObj = self.editor.objectMgr.findObjectByNodePath(parentNP)
                    parentObj.reattachJoint(uid[0:uid.index(" <joint>")], self.objs[uid])
                else:
                    self.objs[uid].getNodePath().reparentTo(parentNP)
                    self.objs[uid].reattach()
                    self.editor.objectMgr.addExistingObj(self.objs[uid])
                if self.objs[uid] in self.layerIndex:
                    layerName = self.layerIndex[self.objs[uid]].name
                    self.editor.ui.layerEditorUI.addObjectToLayer(layerName, self.objs[uid])
                
            while (len(self.hierarchy.keys()) > 0):
                for uid in self.hierarchy.keys():
                    if self.hierarchy[uid] is None:
                        # It is the parent of the joint
                        # Do not restore this object, as it is already
                        # in the scene
                        del self.hierarchy[uid]
                    elif self.hierarchy[uid].find(" <joint>") != -1:
                        name = self.hierarchy[uid]
                        grandParentName = name[0:name.index("/")]
                        grandParentObj = self.editor.objectMgr.findObjectById(grandParentName)
                        parentObj = grandParentObj.joints[name[name.index("/")+1:name.index(" <joint>")]]
                        if parentObj:
                            parentNP = parentObj.joint
                            try:
                                restoreObject(uid, parentNP)
                            except ValueError as e:
                                print "Parent not in tree yet"
                            else:
                                del self.hierarchy[uid]
                    else:
                        parentObj = self.editor.objectMgr.findObjectById(self.hierarchy[uid])
                        if parentObj:
                            parentNP = parentObj.getNodePath()
                            try:
                                restoreObject(uid, parentNP)
                            except ValueError as e:
                                print "Parent not in tree yet"
                            else:
                                del self.hierarchy[uid]

            base.direct.deselectAllCB()
            for uid in self.selectedUIDs:
                obj = self.editor.objectMgr.findObjectById(uid)
                if obj:
                    self.editor.select(obj.getNodePath(), fMultiSelect=1, fUndo=0)

            self.selectedUIDs = []
            self.hierarchy = {}
            self.objs = {}
            
class ActionReplaceTexture(ActionBase):
    def __init__(self, editor, obj, *args, **kargs):
        self.obj = obj
        function = self.obj.replaceTexture
        ActionBase.__init__(self, editor, function, *args, **kargs)
        
    def undo(self):
        if self.result[1]:
            tex = loader.loadTexture(self.result[1].getFullFilename())
            self.obj.nodePath.clearTexture(self.result[0])
            self.obj.nodePath.setTexture(self.result[0], tex, 1)
            self.obj.texSwaps[self.result[0]] = self.result[1]
        else:
            self.obj.nodePath.clearTexture(self.result[0])
            del self.obj.texSwaps[self.result[0]]

class ActionClearTextureSwaps(ActionBase):
    def __init__(self, editor, obj, *args, **kargs):
        self.obj = obj
        function = self.obj.clearTextureSwaps
        ActionBase.__init__(self, editor, function, *args, **kargs)
    
    def saveStatus(self):
        self.prevTexSwaps = copy(self.obj.texSwaps)
    
    def undo(self):
        self.obj.texSwaps = copy(self.prevTexSwaps)
        
        for stage, texAsset in self.obj.texSwaps.iteritems():
            tex = loader.loadTexture(texAsset.getFullFilename())
            self.obj.nodePath.setTexture(stage, tex, 1)

class ActionJournalGeneric(ActionGeneric):
    def __init__(self, editor, doFunc, undoFunc, *args, **kargs):
        ActionGeneric.__init__(self, editor, doFunc, undoFunc, *args, **kargs)
    
    def undo(self):
        self.undoFunc(*self.args, **self.kargs)
        