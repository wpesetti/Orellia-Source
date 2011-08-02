import os
import imp

from ObjectMgr import ObjectMgr
from JournalMgr import JournalMgr
import xml.dom.minidom

class FileMgr:
    """ To handle data file """
    
    def __init__(self, editor=None):
        self.editor = editor

    #Saves the scene into the file with informations from Layers, Objects and Sounds
    def saveToFile(self, filename):
        hiddenLayers = []
        for layer in self.editor.ui.layerEditorUI.layers.values():
            if layer.hidden:
                hiddenLayers.append(layer)
                layer.show(saveHack = True)
    
        doc = xml.dom.minidom.Document()
        root = doc.createElement("scene")
        doc.appendChild(root)
        root.appendChild(self.editor.objectMgr.encode(doc))
        root.appendChild(self.editor.ui.layerEditorUI.encode(doc))
        root.appendChild(self.editor.soundMgr.encode(doc))
        
        try:
            f = open(filename.toOsSpecific(), 'w')
            f.write(doc.toprettyxml())
            f.close()
        except IOError:
            raise SceneSaveError(filename.toOsSpecific())
        else:
            if self.editor.saved:
                self.editor.updateStatusReadout('Sucessfully saved to %s'%filename.toOsSpecific())
            self.editor.fNeedToSave = False
            
            for layer in hiddenLayers:
                layer.hide()
    #Loads the scene from the file with Layers, Objects and Sounds informations from 
    def loadFromFile(self, filename, merge=False, lib=None, otherName=None, newNodeName=''):
        f = open(filename.toOsSpecific())
        doc = xml.dom.minidom.parse(f)
        root = doc.childNodes[0]
        
        for n in root.childNodes:
            if n.localName == "objects":
                self.editor.objectMgr.decode(n, merge=merge, lib=lib, otherName=otherName, newNodeName=newNodeName)
            elif n.localName == "layers":
                self.editor.ui.layerEditorUI.decode(n, merge=merge, otherName=otherName)
            elif n.localName == "sounds":
                self.editor.soundMgr.decode(n, merge=merge, lib=lib, otherName=otherName)
                
        f.close()
    
    def saveJournalToFile(self, filename):
        doc = xml.dom.minidom.Document()
        
        root = doc.createElement("journal")
        doc.appendChild(root)
        root.appendChild(self.editor.journalMgr.encode(doc))
        
        self.tryToSaveDoc(filename,doc)
        
    
    def loadJournalFromFile(self, filename, merge=False,otherName=None):
        f = open(filename.toOsSpecific())
        doc = xml.dom.minidom.parse(f)
        root = doc.childNodes[0]
        
        for n in root.childNodes:
            if n.localName == "journalEntries":
                self.editor.journalMgr.decode(n, merge,otherName)
                
        f.close()
        pass
    
    def saveInventoryMapToFile(self, filename):
        doc = xml.dom.minidom.Document()
        root = doc.createElement("inventoryMap")
        doc.appendChild(root)
        root.appendChild(self.editor.inventoryMgr.encode(doc))
        self.tryToSaveDoc(filename,doc)
        
    def loadInventoryMapFromFile(self, filename, merge = False, otherName = None):
        try:
            f = open(filename.toOsSpecific())
            doc = xml.dom.minidom.parse(f)
            root = doc.childNodes[0]
        
            for n in root.childNodes:
                if n.localName == "inventoryMapEntries":
                    self.editor.inventoryMgr.decode(n)
        
            f.close()
        except IOError:
            print "ERROR:There is no Inventory File exist to load."
            
    def tryToSaveDoc(self, filename, doc):
        try:
            f = open(filename.toOsSpecific(), 'w')
            f.write(doc.toprettyxml())
            f.close()
        except IOError:
            raise SceneSaveError(filename.toOsSpecific())
        else:
            if self.editor.saved:
                self.editor.updateStatusReadout('Sucessfully saved to %s'%filename.toOsSpecific())
            self.editor.fNeedToSave = False
        pass

class SceneSaveError(Exception):
    def __init__(self, filename):
        self.filename = filename