from ConversationMgr import *
from Conversation import *

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
import xml.dom.minidom

import sys

class ConversationTest(DirectObject):
    
    def __init__(self, filename):
        
        self.convo = self.XMLToConversation(filename)
        self.convoMgr = ConversationMgr(self)
        
        # temp hack
        self.convoMgr.conversations['myConvo'] = self.convo
        
        self.convoMgr.openConversation('myConvo')
        self.showLines()
        
        self.accept('escape', sys.exit)
        
    def XMLToConversation(self, xml_filename):
        print 'parsing XML to make Conversation...'
        doc = xml.dom.minidom.parse(xml_filename)
        root = doc.documentElement
        convo = Conversation.decode(doc)
        return convo
    
    def showLines(self):
        npc = self.convoMgr.getNPCStatement()
        responses = self.convoMgr.getValidResponses()
        
        if npc == None:
            print '==== npc line is None...spacebar to reset'
            self.accept('space', self.reset)
        else:
            print 'NPC says: %s' %(npc)
            if len(responses) == 0:
                print '==== player response list is empty...spacebar to reset'
                self.accept('space', self.reset)
            else:
                for i in range(len(responses)):
                    print 'choice %d: %s' %(i, responses[i])
                    self.accept('%d' %(i), self.onChoiceMade, extraArgs=[i])
                print '==== Make your choice...'
    
    def onChoiceMade(self, index):
        responses = self.convoMgr.getValidResponses()
        for i in range(len(responses)):
            self.ignore('%d' %(i))
            
        self.convoMgr.playResponse(index)
        print '==== choice %d' %(index)
        self.showLines()
    
    def reset(self):
        self.convoMgr.closeConversation() # needed
        print 'conversation closed'
        self.convoMgr.openConversation('myConvo')
        self.showLines()


world = ConversationTest('convo_editorFile.xml')
run()