from pandac.PandaModules import *

from direct.stdpy.file import *

import platform, os, shutil

VERSION_NUMBER = 1.0

def getTempDir():
    if platform.system() == 'Windows':
        return os.environ['TMP'] + '\\PandaLE'
    else:
        return os.environ['HOME'] + '/.PandaLE'

#returns a copy of the string that is a valid filename
# i.e. : all characters not allowed in filenames are removed
#(windows specific for now)
def toFilename(s, stripEnd=True):
    illegalChars = ["<",">",":",'"',"/","|","?","*"]
    newStr = s[:]
    for c in illegalChars:
        newStr = newStr.replace(c,'')
    
    if stripEnd:
        newStr = newStr.strip(". ")
    else:
        newStr = newStr.lstrip(". ")
    
    return newStr

#see above: returns a copy of the string that is valid for an asset name    
def toAssetName(s, stripEnd=True):
    newStr = toObjectName(s, stripEnd)
    illegalChars = [":"]
    for c in illegalChars:
        newStr = newStr.replace(c,'')
    
    if stripEnd:
        newStr = newStr.strip()
    else:
        newStr = newStr.lstrip()
    
    return newStr

#see above: returns a copy of the string that is valid for an object name    
def toObjectName(s, stripEnd=True):
    illegalChars = ["<",">",'"',"/","|","?","*",".","\\"]
    newStr = s[:]
    for c in illegalChars:
        newStr = newStr.replace(c,'')
    newStr = newStr.strip()
    
    return newStr
    
    
## encoding and decoding helper functions

def decodeVec3(node):
    for n in node.childNodes:
        if n.localName == "x":
            x = float(n.childNodes[0].data.strip())
        elif n.localName == "y":
            y = float(n.childNodes[0].data.strip())
        elif n.localName == "z":
            z = float(n.childNodes[0].data.strip())
    return VBase3(x,y,z)
    
def encodeVec3(vec, name, doc):
    node = doc.createElement(name)

    x = doc.createElement("x")
    x.appendChild(doc.createTextNode(str(vec.getX())))
    
    y = doc.createElement("y")
    y.appendChild(doc.createTextNode(str(vec.getY())))
    
    z = doc.createElement("z")
    z.appendChild(doc.createTextNode(str(vec.getZ())))
    
    node.appendChild(x)
    node.appendChild(y)
    node.appendChild(z)
    
    return node
    
def decodeColor(node):
    for n in node.childNodes:
        if n.localName == "r":
            r = float(n.childNodes[0].data.strip())
        elif n.localName == "g":
            g = float(n.childNodes[0].data.strip())
        elif n.localName == "b":
            b = float(n.childNodes[0].data.strip())
        elif n.localName == "a":
            a = float(n.childNodes[0].data.strip())
        
    return VBase4(r,g,b,a)
        
def encodeColor(vec, name, doc):
    node = doc.createElement(name)
    
    r = doc.createElement("a")
    r.appendChild(doc.createTextNode(str(vec.getW())))
    g = doc.createElement("r")
    g.appendChild(doc.createTextNode(str(vec.getX())))
    b = doc.createElement("g")
    b.appendChild(doc.createTextNode(str(vec.getY())))
    a = doc.createElement("b")
    a.appendChild(doc.createTextNode(str(vec.getZ())))
    
    node.appendChild(r)
    node.appendChild(g)
    node.appendChild(b)
    node.appendChild(a)
    
    return node
    
def decodeBaseTag(node):
    for n in node.childNodes:
        if n.localName == "key":
            key = n.childNodes[0].data.strip()
        elif n.localName == "tag":
            value = n.childNodes[0].data.strip()
    
    return (key,value)
    
def encodeBaseTag(tag, name, doc):
    node = doc.createElement(name)
    
    key = doc.createElement("key")
    key.appendChild(doc.createTextNode(tag[0]))
    
    tagNode = doc.createElement("tag")
    tagNode.appendChild(doc.createTextNode(tag[1]))
    
    node.appendChild(key)
    node.appendChild(tagNode)
    
    return node
    
def encodeMat4(mat, name, doc):
    node = doc.createElement(name)
    for i in range(4):
        row = doc.createElement("row" + str(i))
        row.appendChild(encodeColor(mat.getRow(i)))
        node.appendChild(row)
        
    return node
    
    
def decodeMat4(node):
    mat = Mat4()
    for n in node.childNodes:
        if n.localName.startwith("row"):
            rowNum = n.localName[3:]
            mat.setRow(rowNum, decodeColor(n))
            
    return mat

def decodeLens(node):
    lens = None
    for n in node.childNodes:
        if n.localName == "lensType":
            type = (n.childNodes[0].data.strip())
            if type == "perspective":
                lens = PerspectiveLens()
            elif type == "orthographic":
                lens = OrthographicLens()
        elif n.localName == "fovHoriz":
            horiz = float(n.childNodes[0].data.strip())
        elif n.localName == "fovVert":
            vert = float(n.childNodes[0].data.strip())
        elif n.localName == "near":
            near = float(n.childNodes[0].data.strip())
        elif n.localName == "far":
            far = float(n.childNodes[0].data.strip())
        elif n.localName == "filmSizeWidth":
            width = float(n.childNodes[0].data.strip())
        elif n.localName == "filmSizeHeight":
            height = float(n.childNodes[0].data.strip())
        elif n.localName == "focalLength":
            fl = float(n.childNodes[0].data.strip())
            
    lens.setFov(Vec2(horiz,vert))
    lens.setNearFar(near,far)
    if type == "orthographic":
        lens.setFilmSize(Vec2(width, height))
    return lens
    
def encodeLens(lens, doc, frustumHidden):
    node = doc.createElement("lens")
    
    type = doc.createElement("lensType")
    if lens.isPerspective():
        type.appendChild(doc.createTextNode("perspective"))
    elif lens.isOrthographic():
        type.appendChild(doc.createTextNode("orthographic"))
    node.appendChild(type)

    fovH = doc.createElement("fovHoriz")
    fovH.appendChild(doc.createTextNode(str(lens.getFov()[0])))
    
    fovV = doc.createElement("fovVert")
    fovV.appendChild(doc.createTextNode(str(lens.getFov()[1])))
    
    near = doc.createElement("near")
    near.appendChild(doc.createTextNode(str(lens.getNear())))
    
    far = doc.createElement("far")
    far.appendChild(doc.createTextNode(str(lens.getFar())))
    
    width = doc.createElement("filmSizeWidth")
    width.appendChild(doc.createTextNode(str(lens.getFilmSize()[0])))
    
    height = doc.createElement("filmSizeHeight")
    height.appendChild(doc.createTextNode(str(lens.getFilmSize()[1])))
    
    node.appendChild(fovH)
    node.appendChild(fovV)
    node.appendChild(near)
    node.appendChild(far)
    node.appendChild(width)
    node.appendChild(height)
    
    return node
    

#Re-implementation of shutil.copy that works with Panda's Virtual File System
#This works for copying thigns from a multifile to the real filesystem, but
#not vice-versa
def copy_vfs(source, dest):
    sourceFile = open(source, 'rb')
    if not isdir(dest):
        destFile = open(dest, 'wb')
    else:
        sf = Filename.fromOsSpecific(source)
        destFile = open(join(dest, sf.getBasename()), 'wb')
    
    bytes = sourceFile.read(1024)
    while bytes:
        destFile.write(bytes)
        bytes = sourceFile.read(1024)

    sourceFile.close()
    destFile.close()

def getArgumentsFromScriptFile(filename):
        scriptFile = open(filename.toOsSpecific())
        
        lines = scriptFile.readlines()
        scriptFile.close()
        mainLine = None
        for line in lines:
            strippedLine = line.strip()
            #print strippedLine
            #pos = strippedLine.find("def main")
            #if(pos != -1):
            #    mainLine = line
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
    

class SceneMergeError(Exception):
    pass

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

class SceneDeleteError(Exception):
    def __init__(self):
        print "ERROR:Cannot Delete the last scene"
        pass
