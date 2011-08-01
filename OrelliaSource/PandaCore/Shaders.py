from Util import *
import copy

""" This class manages a shader and all of its inputs as it is applied to an object """
class LEShader:
    def __init__(self, asset, inputs={}):
        self.asset = asset
        self.inputs = inputs    #keys are names, values are shader input objects (see below)
        self.obj = None #the object that this shader affects
      
    def __copy__(self):
        return LEShader(self.asset, copy.deepcopy(self.inputs))
    
    #adds or replaces an input to this shader
    def setInput(self, input):
        if self.obj:
            self.obj.nodePath.setShaderInput(input.name, input.getValue())
        self.inputs[input.name] = input
    
    #renames an existing input to this shader
    def renameInput(self, oldName, newName):
        input = self.inputs[oldName]
        input.name = newName
        self.inputs[newName] = input
        del self.inputs[oldName]
    
    #removes an input from this shader
    def clearInput(self, name):
        del self.inputs[name]
        if self.obj:
            self.obj.nodePath.clearShaderInput(name)
    
    #actually applies this shader to an object
    def applyToObject(self, obj):
        shader = Shader.load(self.asset.getFullFilename())
        obj.nodePath.setShader(shader)
        for i in self.inputs.values():
            i.updateOnce = False
            obj.nodePath.setShaderInput(i.name, i.getValue())
        
        self.obj = obj
        
    #updates any shader inputs for this shader    
    def update(self):
        for i in self.inputs.values():
            if i.updateMe:
                self.obj.nodePath.setShaderInput(i.name, i.getValue())
            elif i.updateOnce:
                i.updateOnce = False
                self.obj.nodePath.setShaderInput(i.name, i.getValue())
    
    def encode(self, doc):
        node = doc.createElement("Shader")
        asset = doc.createElement("Asset")
        node.appendChild(asset)
        asset.appendChild(doc.createTextNode(self.asset.name))
        for i in self.inputs.values():
            node.appendChild(i.encode(doc))
        

        active = doc.createElement("Active")
        active.appendChild(doc.createTextNode(str(int(self.obj!=None))))
        node.appendChild(active)
        
        return node
    
    def decode(node, lib=None):
        inputs = {}
        for n in node.childNodes:
            if n.localName == "Asset":
                assetName = n.childNodes[0].data.strip()
                assetName = n.childNodes[0].data.strip()
                asset = lib.shaders[assetName]
            elif n.localName == "Active":
                active = bool(int(n.childNodes[0].data.strip()))
            elif n.localName == "LEShaderInputFloat":
                i = LEShaderInputFloat.decode(n)
                inputs[i.name] = i 
            elif n.localName == "LEShaderInputFloat3":
                i = LEShaderInputFloat3.decode(n)
                inputs[i.name] = i 
            elif n.localName == "LEShaderInputFloat4":
                i = LEShaderInputFloat4.decode(n)
                inputs[i.name] = i 
            elif n.localName == "LEShaderInputFloat4x4":
                i = LEShaderInputFloat4x4.decode(n)
                inputs[i.name] = i 
            elif n.localName == "LEShaderInputTime":
                i = LEShaderInputTime.decode(n)
                inputs[i.name] = i
            elif n.localName == "LEShaderInputObj":
                i = LEShaderInputObj.decode(n)
                inputs[i.name] = i
            elif n.localName == "LEShaderInputCameraPos":
                i = LEShaderInputCameraPos.decode(n)
                inputs[i.name] = i
            elif n.localName == "LEShaderInputTexture":
                i = LEShaderInputTexture.decode(n, lib=lib)
                inputs[i.name] = i
            elif n.localName == "LEShaderInputCubemap":
                i = LEShaderInputCubemap.decode(n, lib=lib)
                inputs[i.name] = i
                
        shader = LEShader(asset, inputs)
        shader.active = active
    
        return shader
    
    decode = staticmethod(decode)
    
    def BVWEncode(self):
        lines = []
        
        lines.append("    shader = Shader.load('" + self.asset.filename.getFullpath() + "')\n")
        lines.append("    objects['" + self.obj.name + "'].setShader(shader)\n")
        
        for i in self.inputs.values():
            lines.extend(i.BVWEncode(self.obj.name))
        
        return lines
    
    def incRefCounts(self):
        self.asset.incSceneCount()
        for i in self.inputs.values():
            i.incRefCounts()
        
    def decRefCounts(self):
        self.asset.decSceneCount()
        for i in self.inputs.values():
            i.decRefCounts()
        
#base class for all shader inputs    
class LEShaderInput:
    def __init__(self, name, updateMe=False):
        self.name = name
        self.updateMe = updateMe    #specifies whether this input needs to be updated every frame
        self.updateOnce = False     #change this when something has changed that requires a one-time update
        
    def encode(self, doc):
        node = doc.createElement(self.__class__.__name__)
        name = doc.createElement("Name")
        node.appendChild(name)
        name.appendChild(doc.createTextNode(self.name))
        
        return node
        
    def decode(node):
        for n in node.childNodes:
            if n.localName == "Name":
                name = n.childNodes[0].data.strip()
                
        return LEShaderInput(name)
        
    decode = staticmethod(decode)
    
    def incRefCounts(self):
        pass
        
    def decRefCounts(self):
        pass
    
#base class for all constant shader inputs
class LEShaderInputConst(LEShaderInput):
    def __init__(self, name, value=None):
        LEShaderInput.__init__(self, name, updateMe=False)
        self.value = value
    
    def __deepcopy__(self, memo):
        return self.__class__(copy.copy(self.name), copy.copy(self.value))
    
    def decode(node):
        i = LEShaderInput.decode(node)
        i.updateMe = False
        i.__class__ = LEShaderInputConst
        return i
        
    decode = staticmethod(decode)
    
    def BVWEncode(self, objName):
        lines = []
        
        lines.append("    objects['" + objName + "'].setShaderInput('" + self.name + "', " + str(self.getValue()) + ")\n")
        
        return lines
    
    def getValue(self):
        return self.value
        
    def setValue(self, newValue):
        self.value = newValue
        self.updateOnce = True
        
#constant shader input with a float value    
class LEShaderInputFloat(LEShaderInputConst):
    def __init__(self, name, value=0.0):
        LEShaderInputConst.__init__(self, name, value=value)
    def encode(self, doc):
        node = LEShaderInputConst.encode(self, doc)
        value = doc.createElement("Value")
        node.appendChild(value)
        value.appendChild(doc.createTextNode(str(self.value)))
        
        return node
    
    def decode(node):
        input = LEShaderInputConst.decode(node)
        input.__class__ = LEShaderInputFloat
        for n in node.childNodes:
            if n.localName == "Value":
                input.value = float(n.childNodes[0].data.strip())
        
        return input
    
    decode = staticmethod(decode)

#constant shader input whose value is a vector of 3 floats    
class LEShaderInputFloat3(LEShaderInputConst):
    def __init__(self, name, value=Vec3(0,0,0)):
        LEShaderInputConst.__init__(self, name, value=value)
    def encode(self, doc):
        node = LEShaderInputConst.encode(self, doc)
        node.appendChild(encodeVec3(self.value, "Value", doc))
        
        return node
        
    def decode(node):
        input = LEShaderInputConst.decode(node)
        input.__class__ = LEShaderInputFloat3
        for n in node.childNodes:
            if n.localName == "Value":
                input.value = decodeVec3(n)
                
        return input
    
    decode = staticmethod(decode)

#constant shader input whose value is a vector of 4 floats    
class LEShaderInputFloat4(LEShaderInputConst):
    def __init__(self, name, value=VBase4(0,0,0,0)):
        LEShaderInputConst.__init__(self, name, value=value)
    def encode(self, doc):
        node = LEShaderInputConst.encode(self, doc)
        node.appendChild(encodeColor(self.value, "Value", doc))
        
        return node
        
    def decode(node):
        input = LEShaderInputConst.decode(node)
        input.__class__ = LEShaderInputFloat4
        for n in node.childNodes:
            if n.localName == "Value":
                input.value = decodeColor(n)
                
        return input
    
    decode = staticmethod(decode)

#constant shader input whose value is a 4x4 matrix of floats    
class LEShaderInputFloat4x4(LEShaderInputConst):
    def __init__(self, name, value=Mat4.identMat()):
        LEShaderInputConst.__init__(self, name, value=value)
    def encode(self, doc):
        node = LEShaderInputConst.encode(self, doc)
        node.appendChild(encodeMat4(self.value, "Value", doc))
        
        return node
        
    def decode(node):
        input = LEShaderInputConst.decode(node)
        input.__class__ = LEShaderInputFloat4x4
        for n in node.childNodes:
            if n.localName == "Value":
                input.value = decodeMat4(n)
                
        return input
    
    decode = staticmethod(decode)

#shader input that is the current global clock time    
class LEShaderInputTime(LEShaderInput):
    def __init__(self, name, offset=0):
        LEShaderInput.__init__(self, name, updateMe=True)
        self.offset = offset    #this offset will be added to the global clock's time
    
    def __deepcopy__(self, memo):
        return LEShaderInputTime(copy.copy(self.name), copy.copy(self.offset))
    
    def encode(self, doc):
        node = LEShaderInput.encode(self, doc)
        offset = doc.createElement("Offset")
        offset.appendChild(doc.createTextNode(str(self.offset)))
        
        return node
    
    def decode(node):
        i = LEShaderInput.decode(node)
        i.updateMe = True
        i.__class__ = LEShaderInputTime
        
        i.offset = 0
        for n in node.childNodes:
            if n.localName == "Offset":
                i.offset = float(n.childNodes[0].data.strip())
        
        return i
        
    decode = staticmethod(decode)
    
    def BVWEncode(self, objName):
        lines = []
        
        lines.append("    objects['" + objName + "'].setShaderInput('" + self.name + "', globalClock.getFrameTime() + " + str(self.offset) + ")\n")
        lines.append("    timeObjs.append( ('" + self.name + "', " + str(self.offset) + ", objects['" + objName + "']) )\n")
        
        return lines
    
    def setOffset(self, offset):
        self.offset = offset
        
    def getOffset(self):
        return self.offset
    
    def getValue(self):
        return globalClock.getFrameTime() + self.offset

#Shader input that references another nodepath     
class LEShaderInputObj(LEShaderInput):
    def __init__(self, name, obj=None, updateMe=False):
        LEShaderInput.__init__(self, name, updateMe=updateMe)
        self.obj = obj
    
    def __deepcopy__(self, memo):
        return LEShaderInputObj(copy.copy(self.name), self.obj, copy.copy(self.updateMe))
    
    def encode(self, doc):
        node = LEShaderInput.encode(self, doc)
        obj = doc.createElement("Obj")
        obj.appendChild(doc.createTextNode(self.obj.name))
        node.appendChild(obj)
        
        return node
        
    def decode(node):
        i = LEShaderInput.decode(node)
        i.__class__ = LEShaderInputObj
        
        for n in node.childNodes:
            if n.localName == "Obj":
                i.obj = n.childNodes[0].data.strip()
                
        return i
    
    decode = staticmethod(decode)
    
    def BVWEncode(self, objName):
        lines = []
        
        lines.append("    objects['" + objName + "'].setShaderInput('" + self.name + "', objects['" + self.obj.name + "'])\n")
        
        return lines
    
    
    def getObj(self):
        return self.obj
    
    def setObj(self, newObj):
        self.obj = newObj
        self.updateOnce = True
    
    def getValue(self):
        return self.obj.nodePath

#For using the camera position as a shader input
class LEShaderInputCameraPos(LEShaderInput):
    def __init__(self, name):
        LEShaderInput.__init__(self, name, updateMe=True)
    
    def __deepcopy__(self, memo):
        return LEShaderInputCameraPos(copy.copy(self.name))
    
    def decode(node):
        i = LEShaderInput.decode(node)
        i.__class__ = LEShaderInputCameraPos
        i.updateMe = True
    
        return i
        
    decode = staticmethod(decode)
    
    def getValue(self):
        if base.cam:
            return base.cam.getPos(render)
        else:
            return base.le.ui.perspView.cam.getPos(render)
            
    def BVWEncode(self, objName):
        lines = []
        
        lines.append("    objects['" + objName + "'].setShaderInput('" + self.name + "', base.cam.getPos(render))\n")
        lines.append("    cameraObjs.append( ('" + self.name + "', objects['" + objName + "']) )\n")
        
        return lines
    
#Shader input whose value is a texture        
class LEShaderInputTexture(LEShaderInput):
    def __init__(self, name, tex = None, updateMe = False):
        LEShaderInput.__init__(self, name, updateMe = updateMe)
        self.tex = tex
        
        if tex != None:
            self.texture = loader.loadTexture(tex.getFullFilename())
    
    def __deepcopy__(self, memo):
        return LEShaderInputTexture(copy.copy(self.name), self.tex, self.updateMe)
    
    def encode(self,doc):
        node = LEShaderInput.encode(self, doc)
        
        if self.tex:
            tex = doc.createElement("Tex")
            tex.appendChild(doc.createTextNode(self.tex.name))
            node.appendChild(tex)
        
        return node
        
        
    def decode(node, lib=None):
        if not lib:
            lib = base.le.lib
        
        i = LEShaderInput.decode(node)
        i.__class__ = LEShaderInputTexture
        i.tex = None
        for n in node.childNodes:
            if n.localName == "Tex":
                texName = n.childNodes[0].data.strip()
                i.tex = lib.textures[texName]
                i.texture = loader.loadTexture(i.tex.getFullFilename())
        return i
        
        pass
    
    decode = staticmethod(decode)
    
    def BVWEncode(self, objName):
        lines = []
        
        lines.append("    tex = loader.loadTexture('" + self.tex.filename.getFullpath() + "')\n")
        lines.append("    objects['" + objName + "'].setShaderInput('" + self.name + "', tex)\n")
        
        return lines
      
    def incRefCounts(self):
        if self.tex:
            self.tex.incSceneCount()
        
    def decRefCounts(self):
        if self.tex:
            self.tex.decSceneCount()
    
    def getTexture(self):
        return self.tex
    
    def setTexture(self, texture):
        if self.tex:
            self.tex.decSceneCount()
        self.tex = texture  #pointer to a texture asset
        self.texture = loader.loadTexture(self.tex.getFullFilename())   #an actual panda texture
        self.tex.incSceneCount()
        
    def getValue(self):
        return self.texture

#Cube map shader input        
class LEShaderInputCubemap(LEShaderInput):
    def __init__(self, name, tex = None, updateMe = False):
        LEShaderInput.__init__(self, name, updateMe = updateMe)
        self.tex = tex
        if tex != None:
            self.texture = loader.loadCubeMap(tex.getFullFilename())
    
    def __deepcopy__(self, memo):
        return LEShaderInputCubemap(copy.copy(self.name), self.tex, self.updateMe)
    
    def encode(self,doc):
        node = LEShaderInput.encode(self, doc)
        if self.tex:
            tex = doc.createElement("Cubemap")
            tex.appendChild(doc.createTextNode(self.tex.name))
            node.appendChild(tex)
        
        return node
               
    def decode(node, lib=None):
        if not lib:
            lib = base.le.lib
            
        i = LEShaderInput.decode(node)
        i.__class__ = LEShaderInputCubemap
        i.tex = None
        
        for n in node.childNodes:
            if n.localName == "Cubemap":
                texName = n.childNodes[0].data.strip()
                i.tex = lib.textures[texName]
                i.texture = loader.loadCubeMap(i.tex.getFullFilename())
        return i
        
        pass
    
    decode = staticmethod(decode)
    
    def BVWEncode(self, objName):
        lines = []
        
        lines.append("    cubemap = loader.loadCubeMap('" + self.tex.filename.getFullpath() + "')\n")
        lines.append("    objects['" + objName + "'].setShaderInput('" + self.name + "', cubemap)\n")
        
        return lines
    
    def getTexture(self):
        return self.tex
    
    def setTexture(self, texture):
        if self.tex:
            self.tex.decSceneCount()
        self.tex = texture
        self.texture = loader.loadCubeMap(self.tex.getFullFilename())
        self.tex.incSceneCount()
        
    def getValue(self):
        return self.texture
        
    def incRefCounts(self):
        if self.tex:
            self.tex.incSceneCount()
        
    def decRefCounts(self):
        if self.tex:
            self.tex.decSceneCount()
class DuplicateInputError(Exception):
    def __init__(self, name):
        self.name = name