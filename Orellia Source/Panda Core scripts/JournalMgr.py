"""
Defines JournalMgr
"""
from JournalMgrBase import JournalMgrBase

class JournalMgr(JournalMgrBase):
    """ JournalMgr will create, manage, update Journal Entries in the Journal """
    
    def __init__(self, world):
        JournalMgrBase.__init__(self, world)
        
#class LEJournalMgr(JournalMgrBase):
#    
#    def __init__(self,world):
#        JournalMgrBase.__init__(self,world)
#        self.filenameIndex = {}
#        
#    def addLEJournalEntry(self, LEjournalEntry):
#        if(self.journalEntries.has_key(LEjournalEntry.tag)):
#            return False
#        else:
#            self.journalEntries[LEjournalEntry.tag] = LEjournalEntry
#            self.filenameIndex[LEjournalEntry.filename] = LEjournalEntry.tag
#            return True
#        
#    def reset(self):
#        self.journalEntries = {}
#        self.openedEntryIDs = {}
#        self.filenameIndex = {}
#        
#    def hasJournalEntryFile(self, filename):
#        print self.filenameIndex
#        if(self.filenameIndex.has_key(filename)):
#            return True
#        else:
#            return False
#        
    
