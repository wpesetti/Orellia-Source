# ConversationMgrBase class
# for gameplay export
from Conversation import *
from ConversationLine import *
from ConversationConstants import *
import Debug

class ConversationMgrBase:
    
    def __init__(self, world, conversations):
        self.world = world
        
        self.conversations = conversations # key: conversation tag (string), value: Conversation object (Conversation)
        
        self.conversationIsOpen = False
    
    def openConversation(self, conversation_key):
        if not self.conversationIsOpen: # can open a new conversation
            if conversation_key in self.conversations: # check to make sure conversation_key is valid
                self.conversationIsOpen = True
                self.curConversationKey = conversation_key
                self.curNPCStatementID = self.__calculateNextNPCStatementID()
                if self.curNPCStatementID == LineIDType.END_CONVERSATION:
                    self.closeConversation()
                    return False
                else:
                    self.__doLineScripts(self.curNPCStatementID) # do the scripts for the first line of the conversation, since it appears right away
                    self.curValidResponseIDs = self.__calculateValidResponseIDs(self.curNPCStatementID)
                    self.world.toggleMouse(False)
                    return True
            else:
                print 'ERROR:%s is not a valid conversation key!' %(conversation_key)
                return False
        else: # cannot open a new conversation right now
            print 'ERROR:a conversation (%s) is already open!' %(conversation_key)
            return False
        
    def closeConversation(self):
        self.conversationIsOpen = False
        self.world.toggleMouse(True)
        return True
    
    def isConversationOpen(self):
        return self.conversationIsOpen
    
    # returns an id of the next NPC statement, or END_CONVERSATION if there is no next statement and conversation is over
    def __calculateNextNPCStatementID(self, playerLineID=LineIDType.ROOT): # TODO: change constant to be modular
        NPCLineIDs = self.conversations[self.curConversationKey].getLine(playerLineID).getSuccessors()
        
        # choose the first line that fits the conditions (may change)
        for id in NPCLineIDs:
            if self.__checkLineConditions(id):
                return id

        return LineIDType.END_CONVERSATION # if no successors to the player's line, then return value to end the conversation by default
    
    # returns a list of ids of the player responses, or an empty list if there are no responses and conversation is over
    def __calculateValidResponseIDs(self, NPCLineID):
        validResponseIDs = []
        responseLineIDs = self.conversations[self.curConversationKey].getLine(self.curNPCStatementID).getSuccessors()
        for id in responseLineIDs:
            if self.__checkLineConditions(id):
                validResponseIDs.append(id)
        return validResponseIDs
    
    # returns a string that the npc says, or NONE if it is the end of the conversation, or NONE if no conversation is open
    def getNPCStatement(self):
        if self.conversationIsOpen:
            if self.curNPCStatementID == LineIDType.END_CONVERSATION:
                return None
            else:
                return self.conversations[self.curConversationKey].getLine(self.curNPCStatementID).getText()
        else:
            print 'WARNING: getNPCStatement called when no conversation was open'
            return None

    # returns a list of strings, which may be empty (meaning conversation will end), or NONE if no conversation is open
    def getValidResponses(self):
        if self.conversationIsOpen:
            responseTexts = []
            for id in self.curValidResponseIDs:
                responseTexts.append(self.conversations[self.curConversationKey].getLine(id).getText())
            return responseTexts
        else:
            print 'WARNING: getValidResponses called when no conversation was open'
            return None
    
    def playResponse(self, text_id): # text_id is index from original array sent with getValidResponses
        if self.conversationIsOpen:
            responseID = self.curValidResponseIDs[text_id]
            
            # Do the scripts for the player's chosen response line
            self.__doLineScripts(responseID)
            #print "HERRREEEE"
            #playerLineScripts = self.conversations[self.curConversationKey].getLine(responseID).getScripts()
            #print '==== Player line scripts ~'
            #print playerLineScripts
#            for condition, scripts in playerLineScripts.iteritems():
#                print "Condition", condition
#                print scripts
#                if(condition == "LE-trigger-noCondition"):
#                    for i in sorted(scripts):
#                        self.world.scriptMgr.doScript(scripts[i])
#                else:
#                    #for other conditions which can be scripts as well.
#                    pass
            
            self.curNPCStatementID = self.__calculateNextNPCStatementID(responseID)
            if not self.curNPCStatementID == LineIDType.END_CONVERSATION:
                # Do the scripts for the next NPC line
                self.__doLineScripts(self.curNPCStatementID)
#                npcLineScripts = self.conversations[self.curConversationKey].getLine(self.curNPCStatementID).getScripts()
#                print '==== NPC line scripts ~'
#                for condition, scripts in playerLineScripts.iteritems():
#                    print "Condition", condition
#                    print scripts
#                    if(condition == "LE-trigger-noCondition"):
#                        for i in sorted(scripts):
#                            self.world.scriptMgr.doScript(scripts[i])
#                    else:
#                        #for other conditions which can be scripts as well.
#                        pass
                    
                self.curValidResponseIDs = self.__calculateValidResponseIDs(self.curNPCStatementID)
                # Yo dude
                self.playLineSound();
                if len(self.curValidResponseIDs) == 0:
                   Debug.debug(__name__,'(player response list is empty)')
                   # TODO: close conversation while still showing the last NPC line...involve ConversationUI?
            else:
                Debug.debug(__name__,'(NPC line is END)')
                self.closeConversation()
                    
        else:
            print 'WARNING: playResponse called when no conversation was open'
    
    def playLineSound(self):
        pass
    
    def __doLineScripts(self, lineID):
        if lineID == LineIDType.END_CONVERSATION:
            return
        else:
            lineScripts = self.conversations[self.curConversationKey].getLine(lineID).getScripts()
            for condition, scripts in lineScripts.iteritems():
                Debug.debug(__name__,"Condition"+str(condition))
                Debug.debug(__name__,str(scripts))
                if(condition == "LE-trigger-noCondition"):
                    for i in sorted(scripts):
                        self.world.scriptMgr.doScript(scripts[i])
                else:
                    #for other conditions which can be scripts as well.
                    pass
    
    def __checkLineConditions(self, lineID):
        if lineID == LineIDType.END_CONVERSATION:
            return False
        else:
            # TODO: better constant thingy...enforce same as constant in ConversationEditor
            conditionEvent = 'LE-convoLineCondition'
            conditionScripts = self.conversations[self.curConversationKey].getLine(lineID).getScriptsAndArguments(conditionEvent)
            conditionsMet = True
            # CONSIDER: for else loop, short circuiting
            for scriptID, condition in conditionScripts.iteritems():
                conditionsMet = conditionsMet and self.world.scriptMgr.doConditionScript(condition)
            return conditionsMet