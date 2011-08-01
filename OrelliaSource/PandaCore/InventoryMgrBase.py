import xml.dom.minidom
from ModifierSporeUI import *

from Scriptable import * 

ITEM_EVENT = "LE-OnUse"

class InventoryMgrBase():
    def __init__(self,world):
        
        #this is for linking a picture for the item to show up in the UI
        self.inventoryMap = {}
        
        #for game: items in the inventory
        #self.tagUIMap = {} #holds the tag and the index number in UI
        self.items = {}
        self.world = world
        
    def reset(self):
        self.inventoryMap = {}
        self.items = []
    
    def addInventoryMapEntry(self, tag, imageName, scriptAndArguments=[(ITEM_EVENT,"Do Nothing", [])]):
        #print "Script and Arguments ", scriptAndArguments 
        if(self.hasItemTag(tag)):
            raise DuplicateTagError(tag)
        if(len(self.inventoryMap)==4):
            #Do something here
            print "WARNING:LE Inventory: Cannot  have more than 4 items"
            return False
        
        self.inventoryMap[tag] = InventoryMapItem(tag,imageName, scriptAndArguments)
        return True
        
    def removeInventoryMapEntry(self,tag):
        if(len(self.inventoryMap)== 0):
            print "ERROR:There is nothing to remove from the Inventory Map"
        elif(self.inventoryMap.has_key(tag)== False):
            print "ERROR:There is no such entry in the Inventory Map with the ", tag, " tag."
        else:
            del self.inventoryMap[tag]
            
    def changeItemTag(self, oldTag, newTag):
        self.inventoryMap[newTag] = self.inventoryMap[oldTag]
        self.inventoryMap[newTag].tag = newTag
        del self.inventoryMap[oldTag]
        
    def changeItemImage(self, tag, imageName):
        self.inventoryMap[tag].imageName = imageName
        
    def changeScriptNameAndArguments(self, tag, newScript, newArguments):
        self.inventoryMap[tag].setScript(ITEM_EVENT, 0, newScript, newArguments )
        
    def changeScriptValues(self, tag, newValues):
        self.inventoryMap[tag].setScriptArguments(ITEM_EVENT, 0, newValues)
        
    def getScriptAndArguments(self, tag):
        return self.inventoryMap[tag].getScriptAndArguments(ITEM_EVENT, 0)
        
    #For inventory Map  which is for mapping the item type with images and scripts
    def hasItemTag(self, tag):
        if(self.inventoryMap.has_key(tag)):
            return True
        return False
    
    #For inventory Items
    def hasItem(self, tag):
        if(self.item.has_key(tag)):
            return True
        return False
        
        
    def encode(self, doc):
        itemsXML = doc.createElement("inventoryMapEntries")
        
        for t in self.inventoryMap.keys():
            entry = doc.createElement("inventoryEntry")
            tag = doc.createElement("itemTag")
            tag.appendChild(doc.createTextNode(t))
            entry.appendChild(tag)
            textureName = doc.createElement("image")
            textureName.appendChild(doc.createTextNode(self.inventoryMap[t].imageName))
            entry.appendChild(textureName)
            itemsXML.appendChild(entry)
            self.inventoryMap[t].encodeHelper(doc,entry)
        
        return itemsXML
            
    def decode(self, node):    
        for n in node.childNodes:
            #print n.localName
            if(n.localName == "inventoryEntry"):
                scripts = []
                for n2 in n.childNodes:
                    if(n2.localName == "itemTag"):
                        tag = n2.childNodes[0].data.strip()
                    elif(n2.localName == "image"):
                        texture = n2.childNodes[0].data.strip()
                    elif(n2.localName == "script"):
                        scripts = InventoryMapItem.decodeHelper(n2)
                if(self.addInventoryMapEntry(tag, texture, scripts)==False):
                    print "ERROR:Loading Inventory Item Map is failed"
                    
                
    def addItem(self, tag, number=1):
        if(self.items.has_key(tag)):
            index = self.items[tag].getUINo()
            self.items[tag].increment(number)
        else:
            #print "Here"
            imgFile = None
            if(self.inventoryMap.has_key(tag)):
                if(self.world.assets.textures.has_key(self.inventoryMap[tag].imageName)):
                    imgFile = self.world.assets.textures[self.inventoryMap[tag].imageName]
                else:
                    print "ERROR:There is no texture in the library named under ". tag, "."
            else:
                print "ERROR:There is no item tag in the Inventory Map named as ", tag,"."
                return
            
            #for now there is no script for the item on Use
            inventoryItem = InventoryItem(tag,0,self.inventoryMap[tag].getScriptAndarguments(), number)        
            index = self.world.gameplayUI.modifierSporeUI.addButton(lambda:self.useItem(tag), imgFile)
            inventoryItem.setUINo(index)
            self.items[tag] = inventoryItem
            
        self.world.gameplayUI.modifierSporeUI.changeItemCount(index,self.items[tag].getCount())
        
    def useItem(self,tag):
        if(self.items.has_key(tag)== False):
            print "ERROR:Item Use:There is no item tag in the Inventory named as ", tag,"."
        script = self.items[tag].use()
        if(script):
            self.world.scriptMgr.doScript(script)
        index = self.items[tag].getUINo()
        self.world.gameplayUI.modifierSporeUI.changeItemCount(index,self.items[tag].getCount()) 
    
    def removeItem(self, tag, number = 1):
        if(self.items.has_key(tag)== False):
            print "ERROR:Decrement Error:There is no item tag in the Inventory named as ", tag,"."
        
        items = self.items[tag]
        item.decrement(number)
            #index = self.items[]
        index = self.items[tag].getUINo()    
        self.world.gameplayUI.modifierSporeUI.changeItemCount(index,self.items[tag].getCount())
        
    def getItemCount(self, tag):
        if(self.items.has_key(tag)==False):
            return 0
        return self.items[tag].getCount()
        
        
class InventoryMapItem(Scriptable):
    def __init__(self, tag, imageName, scripts =[]):
        self.tag = tag
        self.imageName = imageName 
        Scriptable.__init__(self)
        for s in scripts:
            triggerType, scriptName, arguments = s
            id = self.addScript(triggerType, scriptName)
            self.setScriptArguments(triggerType, id, arguments)
            
    def getScriptAndarguments(self):
        if(len(self.scripts) == 0 ):
            return None
        scripts = self.scripts["LE-OnUse"]
        sortedList = sorted(scripts)
        for i in sortedList:
            return scripts[i]
        

class InventoryItem:
    def __init__(self,tag, uiNo, script = None, count = 1):
        self.tag = tag
        self.uiNo = uiNo
        self.count = count
        self.scriptOnUse = script # A tuple of script name and list of arguments
                
    def increment(self, number = 1):
        self.count += number
        
    def decrement(self, number = 1):
        self.count -=number
        if self.count <= 0:
            self.count = 0
        
    def getCount(self):
        return self.count
    
    def use(self):
        if(self.count <= 0):
            #print "ERROR: Cannot use the item: ", self.tag,", because there is none."
            return
        #if(self.scriptOnUse == None):
        #    return
        #else:
            #scriptsOnUse = self.scripts["LE-OnUse"]
        #    self.world.scriptMgr.doScript(scriptsOnUse)
            
        self.decrement()
        return self.scriptOnUse
        
    def setUINo(self, uiNo):
        self.uiNo = uiNo
    def getUINo(self):
        return self.uiNo
            
#Base class for exceptions in this module    
class Error(Exception):
        pass

#Raised when trying to add an asset with a name that already exists in the library        
class DuplicateTagError(Error):
    def __init__(self, tag):
        self.tag = tag
            
    
            
        
        
        
    
    