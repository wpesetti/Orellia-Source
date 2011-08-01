from JournalEntry import *
from Util import *
from direct.interval.IntervalGlobal import *

class JournalMgrBase():
    def __init__(self, world):
        self.journalEntries = {}
        self.openedEntryIDs = {}
        self.entryOrder =[]#holds the order of the entries which is the add order.
        self.openOrder = []
        
        self.world = world

    #This function opens the JournalEntry with the given entryTag
    #So now the Journal Entry can be seen in the Journal UI
    #If the journal entry was already opened, this function does nothing
    #If the journal entry wasn't opened before, it opens it and sets its
    #first journal line.
    def openJournalEntry(self, entryTag):
        #Check if any entry with the given entryTag exist
        if(self.journalEntries.has_key(entryTag)):
            journalEntry = self.journalEntries[entryTag]
            #check if that entry is opened already
            if(self.openedEntryIDs.has_key(entryTag)):
                print "ERROR:The journal entry with tag: ", entryTag," is already opened"
                return False
            else:
                #if the entry doesn't have any lines then assign None to the entryLineValue
                if(len(journalEntry.journalLines) != 0):
                    val = journalEntry.journalLines[journalEntry.lineOrder[0]].entryValue
                else:
                    val = None
        else:
            print "ERROR:Tried to open non-existent Journal Entry with tag: ", entryTag
            return False
        self.openedEntryIDs[entryTag] = val
        self.openOrder.append(entryTag)
        self.world.gameplayUI.journalUI.startFlash()
        return True
    #checks the existence of an Journal Entry with the name
    def journalEntryExist(self, entryTag):
        if(self.journalEntries.has_key(entryTag)):
            return True
        else:
            return False
    
    #[Zeina] Should I open the Entry if something tries to setValue?
    def setEntryValue(self, entryTag, value,isIncr,minValue,delObj):
        if self.openedEntryIDs[entryTag] >= minValue:
            if(self.openedEntryIDs.has_key(entryTag)):
                if(self.journalEntries[entryTag].journalLines.has_key(value)):
                    if not isIncr:
                        self.openedEntryIDs[entryTag] = value
                    else:
                        self.openedEntryIDs[entryTag] += value
                    self.world.gameplayUI.journalUI.startFlash()
                    #if not delObj == None:
                        #Sequence(Wait(.1),Func(self.world.scriptInterface.DestroyGameObject,delObj)).start()
                    return True
                else:
                    print "ERROR:The entry value doesn't exist."
                    return False
            else:
                if(self.openJournalEntry(entryTag)):
                    if(self.journalEntries[entryTag].journalLines.has_key(value)):
                        if not isIncr:
                            self.openedEntryIDs[entryTag] = value
                        else:
                            self.openedEntryIDs[entryTag] += value
                        self.world.gameplayUI.journalUI.startFlash()
                        #if not delObj == None:
                            #Sequence(Wait(.1),Func(self.world.scriptInterface.DestroyGameObject,delObj)).start()
                        return True
                    else:
                        print "ERROR:The entry value doesn't exist."
                        return False
                else:    
                    print "ERROR:the Journal entryTag: ",entryTag, "doesn't exist"
                    return False
        else:
            return False
            
        
            
    
    def getOpenedJournalEntries(self):
        entries= []
        for key in self.openOrder:#self.openedEntryIDs.keys():
            title = self.journalEntries[key].name
            statement = self.journalEntries[key].journalLines[self.openedEntryIDs[key]].text
            entries.append((title,statement))
        return entries #[("The quest title:Hello Qiaosi!!!","Blah blah information information =)")]
    
    def addJournalEntry(self, journalEntry):
        if(self.journalEntries.has_key(journalEntry.tag)):
            return False
        else:
            self.journalEntries[journalEntry.tag] = journalEntry
            self.entryOrder.append(journalEntry.tag)
            return True
    def removeJournalEntry(self, journalEntryTag):
        if(not(self.journalEntries.has_key(journalEntryTag))):
            print "ERROR:There is no such Journal Entry tagged as "+journalEntryTag+"."
            return False
        else:
            del self.journalEntries[journalEntryTag]
            self.entryOrder.remove(journalEntryTag)  
            return True
    def reset(self):
        self.openedEntryIDs = {}
        self.entryOrder = []
        self.openOrder = []
    def getJournalEntry(self, journalEntryTag):
        if(self.journalEntries.has_key(journalEntryTag)==False):
            print "ERROR:There is no such Journal Entry tagged  as "+journalEntryTag+"."
            return None
        else:
            return self.journalEntries[journalEntryTag]
        
    def getJournalInOrder(self):
        return self.entryOrder
    
    #Dont use this function    
    def replaceJournalEntries(self, newJournalEntries):
        #del self.journalEntries
        self.journalEntries = None
        self.journalEntries = newJournalEntries
    
        
    def loadFromFile(self, filename, lib):
        if(journalFile == None):
            return {}
        
        #this part might be changed for better efficiency
        lib = Library(Filename(libraryFilename.getDirname()))
        
        journalFilename = Filename(journalFile)
        journalEntries = {}
        
        f = open(journalFilename.toOsSpecific())
        doc = xml.dom.minidom.parse(f)
        root = doc.childNodes[0]
        
        for node in root.childNodes:
            if node.localName == "name":#"journalEntry":
                #get the filename from the lib. with 
                #name = lib.journalEntries[node.childNodes[0].data.strip()]
                #journalEntryFilename = Filename(name)
                #f2 = open(journalEntryFilename.toOsSpecific())
                #journalEntrydoc = xml.dom.minidom.parse(f2)
                #journalEntry  = JournalEntry.decode(journalEntrydoc.childNodes[0], "None")
                journalEntry = JournalEntry.decode(node,"None")
                self.journalMgr.addJournalEntry(journalEntry)#journalEntriesjournalEntries[]journalEntry)
                #self.addJournalEntry(journalEntry)
            else:
                pass
        #return journalEntries

    #this function only  changes the book-keeping data of the Journal entry
    #It has no control of its lines.
    def changeJournalEntryTag(self, oldTag, newTag):
        
        if(self.journalEntryExist(newTag)):
            return False
        
        journalEntry = self.getJournalEntry(oldTag)
        if(journalEntry == None):
            return False
        del self.journalEntries[oldTag]
        
        journalEntry.setTag(newTag)
        self.journalEntries[newTag] = journalEntry
        
        for i in range(len(self.entryOrder)):
            if(self.entryOrder[i] == oldTag):
                self.entryOrder[i] = newTag
        return True
        
    def encode(self, doc):
        jes = doc.createElement("journalEntries")
        for je in self.entryOrder:
            jes.appendChild(self.journalEntries[je].encode(doc))         
        return jes
    
    def decode(self, node, merge=False, otherName=None):
        if not merge:
             #clear all of JournalMgr information
            self.reset()
        #add prefixes to all of the objects that are added from another project
        if otherName:
            prefix = otherName + "_"
        else:
            prefix = ""
            
        for n in node.childNodes:
            if n.localName:
                if n.localName == "journalEntry":
                    je = JournalEntry.decode(n)
            
                    if(not(self.addJournalEntry(je))):
                        raise Util.SceneMergeError()
                    
    
    def isJournalEntryOpen(self, entryTag):
        return self.openedEntryIDs.has_key(entryTag)
    
    def isJournalEntryOnValue(self, entryTag, entryValue):
        if(self.openedEntryIDs.has_key(entryTag)==False):
            return False
        
        if(self.openedEntryIDs[entryTag] == entryValue):
            return True
        else:
            return False
        
        
                
        
        


