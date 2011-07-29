# test conversation XML parser

import xml.dom.minidom
from Conversation import *
from ConversationLine import *

import os

# temp
#from xml.dom.ext import PrettyPrint
#from StringIO import StringIO

class ConversationParser:
    
    def __init__(self):
        print 'parser running...'
        
        convo = self.XMLToConversation('storyConvo.xml')
        print convo
        self.ConversationToXML(convo, 'storyConvo_output.xml')
    
    def XMLToConversation(self, xml_filename):
        print 'parsing XML to make Conversation...'
        doc = xml.dom.minidom.parse(xml_filename)
        root = doc.documentElement
        convo = Conversation.decode(doc)
        return convo
    
    def ConversationToXML(self, convo, xml_filename):
        print 'using Conversation to make XML...'
        
        doc = xml.dom.minidom.Document()
        root = doc.createElement("the_root")
        doc.appendChild(root)
        root.appendChild(convo.encode(doc))
        f = open(xml_filename, 'w')
        f.write(doc.toxml())
        f.close()
        
        print 'saved...'
    
#    def toReadableString(self, doc):
#        tmpStream = StringIO()
#        PrettyPrint(doc, stream=tmpStream, encoding='utf-8')
#        return tmpStream.getvalue()
        
        
#        outputFile = open(filename, 'w')
#        outputLines = []
#        
#        self.rec_writeNode(doc.childNodes[0], '', outputLines)
#        
#        outputFile.writelines(outputLines)
#        outputFile.close()
#    
#    def rec_writeNode(self, node, prefix, str_array):
#        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
#            str_array.append(prefix + node.localName + ' ' + node.getAttribute('id') + ' ' + node.getAttribute('endpoint') + '\n')
#        elif node.nodeType == Node.TEXT_NODE:
#            str_array.append(prefix + node.data + '\n')
#        
#        for child in node.childNodes:
#            if child.localName != None: # um, what?
#                self.rec_writeNode(child, prefix + '    ', str_array)
        
    ## def rec_writeNode(self, node, prefix, str_array):
        ## str_array.append(prefix + node.localName + ' ' + node.getAttribute('id') + ' ' + node.getAttribute('endpoint') + '\n')
        ## for child in node.childNodes:
            ## if child.localName != None: # um, what?
                ## self.rec_writeNode(child, prefix + '    ', str_array)
    
    

parser = ConversationParser()