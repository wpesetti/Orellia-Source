import xml.dom.minidom

class JournalEntry:
    def __init__(self,tag,name):
        self.tag = tag
        self.name = name
        self.journalLines = {}
        self.lineOrder = []
        
    def setTag(self, newTag):
        self.tag = newTag
    
    def getJournalLine(self, entryValue):
        if not(self.journalLines.has_key(entryValue)):
            print "ERROR:A line with given entryValue: ", entryValue, " doesn't exist. " 
            return None
        else:
            return self.journalLines[entryValue]
        
    def journalLineExists(self, entryValue):
        if self.journalLines.has_key(entryValue):
            return True
        else:
            return False
        
    def addJournalLine(self, journalLine):
        if self.journalLines.has_key(journalLine.entryValue):
            print "ERROR:A line with given entryValue: ", journalLine.entryValue, " already exist. " 
            return False
        else:
            self.journalLines[journalLine.entryValue] = journalLine
            self.lineOrder.append(journalLine.entryValue)
            return True
    def removeJournalLine(self, entryValue):
        if not self.journalLines.has_key(entryValue):
            print "ERROR:There is no Journal Line with entryValue: ", entryValue,"."
            return False
        else:
            del self.journalLines[entryValue]
            self.lineOrder.remove(entryValue)
            return True
    
    def clearJournalLines(self):
        self.journalLines = {}
        self.lineOrder = []
        
    def getJournalLinesInOrder(self):
        self.lineOrder.sort()
        return self.lineOrder
    
    def changeLineEntryValue(self, oldValue, newValue):
        if(self.journalLineExists(newValue)):
            return False
        
        journalLine = self.getJournalLine(oldValue)
        if(journalLine == None):
            return False
        del self.journalLines[oldValue]
        
        journalLine.setEntryValue(newValue)
        self.journalLines[newValue] = journalLine
        
        for i in range(len(self.lineOrder)):
            if(self.lineOrder[i] == oldValue):
                self.lineOrder[i] = newValue
        return True
    
    def encode(self, doc):
        je = doc.createElement("journalEntry")
        
        tag = doc.createElement("tag")
        tag.appendChild(doc.createTextNode(self.tag))
        je.appendChild(tag)
         
        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(self.name))
        je.appendChild(name)
        
        for line in self.lineOrder:
            je.appendChild(self.journalLines[line].encode(doc))
        return je
    
    #decodes the JournalEntry from an xml node
    def decode(node):
        #lines = {}
        temp = JournalEntry("temp", "temp")
        for n in node.childNodes:
            #print n.localName
            if(n.localName == "tag"):
                tag = n.childNodes[0].data.strip()
            elif(n.localName == "name"):
                name = n.childNodes[0].data.strip()
            elif(n.localName == "line"):
                line = JournalLine.decode(n)
                temp.addJournalLine(line)
                #lines[line.entryValue] = line
            else:
                pass#print "Non-Existent information for Journal Entry"
        temp.tag = tag
        temp.name = name
        #journalEntry = JournalEntry(tag,name)
        #journalEntry.journalLines = temp.journalLines
        #journalEntry.
        #journalEntry.journalLines = lines 
        return temp
    decode = staticmethod(decode)


class JournalLine:
    def __init__(self,text ="",entryValue=10, endpoint = False):
        self.text = text
        self.endpoint = endpoint
        self.entryValue = entryValue
        
    def setEntryValue(self,newValue):
        self.entryValue = newValue
        
    def decode(node):
        for n in node.childNodes:
            if(n.localName == "text"):
                text = n.childNodes[0].data.strip()
            elif(n.localName == "entryValue"):
                entryValue = n.childNodes[0].data.strip()
            elif(n.localName == "endpoint"):
                endpoint = n.childNodes[0].data.strip()
                if(endpoint == "True"):
                    endpoint = True
                else:
                    endpoint = False
            else:
                pass#print "Non-Existent information for Journal Line: ", n.localName
        journalLine = JournalLine(text,int(entryValue),bool(endpoint))
        return journalLine
    decode = staticmethod(decode)
    
    def encode(self, doc):
        line = doc.createElement("line")
        
        text = doc.createElement("text")
        text.appendChild(doc.createTextNode(self.text))
        line.appendChild(text)
        
        endpoint = doc.createElement("endpoint")
        endpoint.appendChild(doc.createTextNode(str(self.endpoint)))
        line.appendChild(endpoint)
        
        entryValue = doc.createElement("entryValue")
        entryValue.appendChild(doc.createTextNode(str(self.entryValue)))
        line.appendChild(entryValue)
        
        return line
        
        
        
        
        
        
        
        