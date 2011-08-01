# Conversation class
# for gameplay export

from ConversationLine import *

# temp?
import xml.dom.minidom
from ConversationConstants import *


class Conversation:
    
    def __init__(self):
        self.lines = {} # key: id from XML node (int), value: line (ConversationLine)
        
        self.lines[LineIDType.ROOT] = ConversationLine(LineIDType.ROOT, SpeakerType.PLAYER, '[start]')
        
        self.filePath = None # TODO: to init param
    
    
    # encodes the conversation as XML
    def encode(self, doc):
        node = doc.createElement('conversation')
        
        node.appendChild(doc.createTextNode('my_convo_1'))

        writtenIDs = set()
        self.rec_encode(node, self.getRootLine(), writtenIDs, doc)
        
        return node
    
    def rec_encode(self, parent_node, line, writtenIDs, doc):
        line_node = doc.createElement('line')
        parent_node.appendChild(line_node)
            
        # line id (attribute node)
        line_node.setAttribute('id', line.getID().__str__())
        
        # speaker (attribute node)
        line_node.setAttribute('speaker', line.getSpeaker())
        
        if not line.getID() in writtenIDs:
            # text (element and text nodes)
            text_node = doc.createElement('text') # an XML element node that contains the text for the line
            text_node.appendChild(doc.createTextNode(line.getText())) # creates an XML text node
            line_node.appendChild(text_node)
            
            # TODO conditions
            
            scripts = line.getScripts()#for script in line.getScripts():#getScriptTags():
                #script_node = doc.createElement('script') # an XML element node that contains a script to execute with the line
            for triggerType, scriptTuples in scripts.iteritems():
                for scriptID in sorted(scriptTuples):
                    script_node = doc.createElement("script")
                    triggerTypeNode = doc.createElement("triggerType")
                    triggerTypeNode.appendChild(doc.createTextNode(triggerType))
                    script_node.appendChild(triggerTypeNode)
                    
                    scriptName, scriptArguments = scriptTuples[scriptID]
                    scriptNameNode = doc.createElement("scriptName")
                    script_node.appendChild(scriptNameNode)
                    scriptNameNode.appendChild(doc.createTextNode(scriptName))
                    temp = []
                    for argument in scriptArguments:
                        scriptArgument = doc.createElement("parameter")
                        scriptArgument.appendChild(doc.createTextNode(str(argument)))
                        script_node.appendChild(scriptArgument)
                          
                    #script_node.appendChild(script)
                #script_node.appendChild(doc.createTextNode(script))
                    line_node.appendChild(script_node)
            
            # CAUTION: writtenIDs is a pointer I believe...so will update same thing on separate branches of recursive call
            writtenIDs.add(line.getID())
            
            for succ_id in line.getSuccessors():
                self.rec_encode(line_node, self.lines[succ_id], writtenIDs, doc)
        
        
    
    def decode(doc):
        conversation = Conversation()
        lineElements = doc.getElementsByTagName('line')
        processedIDs = set()
        for elem in lineElements:
            # get id
            assert elem.hasAttribute('id')
            idString = elem.getAttribute('id')
            id = int(idString)
            # get speaker
            assert elem.hasAttribute('speaker')
            speaker = elem.getAttribute('speaker')
            
            text = ''
            condition = None
            scripts = []
            successorIDs = []
            
            if not id in processedIDs:
                for child in elem.childNodes:
                    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                        # get text
                        if child.tagName == 'text':
                            if len(child.childNodes) > 0: # just in case there is no text type node...ie. <text/> for root
                                textNode = child.childNodes[0]
                                if textNode.nodeType == xml.dom.Node.TEXT_NODE:
                                    text = textNode.data 
                                else:
                                    text = ""
                            else:
                                text = ""
                        
                        # TODO: condition
                        
                        if child.tagName == 'script':
                            arguments = []
                            for n2 in child.childNodes:
                                if n2.localName == "triggerType":
                                    triggerType = n2.childNodes[0].data.strip()
                                elif n2.localName == "scriptName":
                                    scriptName = n2.childNodes[0].data.strip()
                                elif n2.localName == "parameter":
                                    if(len(n2.childNodes) > 0):
                                        parameter = n2.childNodes[0].data.strip()
                                    else:
                                        parameter = ""
                                    arguments.append(str(parameter))
                            scripts.append((triggerType,scriptName,arguments))
#                                    textNode = child.childNodes[0]
#                                    if textNode.nodeType == xml.dom.Node.TEXT_NODE:
#                                        scripts.append[textNode.data]
                        
                        if child.tagName == 'line':
                            # get successor ids
                            assert child.hasAttribute('id')
                            succIDString = child.getAttribute('id')
                            succID = int(succIDString)
                            successorIDs.append(succID)
                            
                newLine = ConversationLine(id, speaker, text, condition, scripts)
                for s in scripts:
                    triggerType, scriptName, arguments = s
                    id = newLine.addScript(triggerType, scriptName)
                    newLine.setScriptArguments(triggerType, id, arguments) 
                
                for succ in successorIDs:
                    newLine.addSuccessor(succ)
                conversation.addLine(newLine)
                processedIDs.add(id)
        return conversation
    decode = staticmethod(decode)
    
    # used when constructing a conversation from an XML resource
    def addLine(self, line):
        id = line.getID()
        self.lines[id] = line
    
    def getLine(self, line_id):
        return self.lines[line_id]
    
    def hasLine(self, line_id): # to uml
        if line_id in self.lines:
            return True
        else:
            return False
    
    def getRootLine(self): # to uml
        return self.lines[LineIDType.ROOT]
    
    def __str__(self): # mainly for debugging
        string = ''
        for id, line in self.lines.items():
            string += line.__str__() + '\n'
        return string