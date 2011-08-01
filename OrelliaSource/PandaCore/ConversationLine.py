# ConversationLine class
# for gameplay export

from Scriptable import * 
import Debug

class ConversationLine(Scriptable):
    
    def __init__(self, id, speaker, text="", condition=None, scripts=[]): # speaker param to uml
        Scriptable.__init__(self)
        # CONSIDER: generalize speaker param types to include camera, waypoints, etc. (see ConversationConstants.py)
        self.id = id
        self.text = text
        self.speaker = speaker # to uml
        self.condition = condition # a boolean function or script
        self.oldScripts = [] # list of script tags to execute when line appears in game...to uml
        
        self.successorIDs = [] # a list of ConversationLine ids (int)
    
    def getSpeaker(self): # to uml
        return self.speaker
    
    def addSuccessor(self, id):
        if not id in self.successorIDs:
            self.successorIDs.append(id)
            Debug.debug(__name__,'added successor (id='+str(id)+') to line (id='+str(self.id)+')')
            return True
        else:
            return False
    
#    def repositionSuccessor(self, succID, posChange):
##        curIndex = -1
##        for index in range(len(self.successorIDs)):
##            id = self.successorIDs[index]
##            if id == succID:
##                curIndex = index
##                break
##        if curIndex != -1:
##            newIndex = curIndex + posChange
##            if newIndex >= 0 and newIndex < len(self.successorIDs):
##                del self.successorIDs[curIndex]
##                self.successorIDs.insert(newIndex, succID)
#
#
#        if succID in self.successorIDs:
#            curIndex = self.successorIDs.index(succID)
#            neWIndex = curIndex + posChange
#            if newIndex >= 0 and newIndex < len(self.successorIDs):
#                
#            else:
#                return
#        else:
#            return

    def moveSuccessorUp(self, id):
        if id in self.successorIDs:
            curIndex = self.successorIDs.index(id)
            newIndex = curIndex - 1
            if newIndex >= 0 and newIndex < len(self.successorIDs):
                swap_id = self.successorIDs[newIndex]
                self.successorIDs[newIndex] = id
                self.successorIDs[curIndex] = swap_id
                return True
        return False
    
    def moveSuccessorDown(self, id):
        if id in self.successorIDs:
            curIndex = self.successorIDs.index(id)
            newIndex = curIndex + 1
            if newIndex >= 0 and newIndex < len(self.successorIDs):
                swap_id = self.successorIDs[newIndex]
                self.successorIDs[newIndex] = id
                self.successorIDs[curIndex] = swap_id
                return True
        return False
        
    
    def removeSuccessor(self, id): # to uml
        # this is tricky...there is a difference between removing one instance of a line (ie. a link)
        # and removing all instances of a line from the conversation.  This is probably the difference
        # between removing the id from the parent's successors and removing the id from self.lines as a whole
        if id in self.successorIDs:
            #print 'removed successor (id=%d) from line (id=%d)' %(id, self.id)
            self.successorIDs.remove(id)
            return True
        else:
            print 'WARNING: tried to remove a successor (id=%d) that was not a successor for that line (id=%d)' %(id, self.id)
            return False
        
    
    def getSuccessors(self):
        return self.successorIDs
    
    def getID(self):
        return self.id
    
    def getText(self):
        return self.text
    
    def setText(self, newText): # to uml; links to ConversationEditor
        self.text = newText
    
    def getConditionFn(self):
        if self.condition == None:
            def always(): # TODO: check
                return True
            return always
        else:
            return self.condition
    
    def getScriptTags(self): # to uml
        return self.scripts

    def callTrigger(self, scriptMgr): # to uml
        pass
    
    def __str__(self): # mainly for debugging
        string = '(id: %d -> ' %(self.id) + self.successorIDs.__str__() + ') ' + self.text
        return string