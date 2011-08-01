"""
This class represents a script-able Object. Scripts
gives functionality to the objects.
"""
class Scriptable:
    def __init__(self):
        self.scripts = {}#Scripts is a map where the key are event types that are defined for LE. 
                         #The values are maps of
        self.scriptCounter = 0
    
    def __copy__(self):
        newObj = Scriptable 
        newObj.scripts = copy.copy(self.scripts) 
        return newObj

    def addScript(self,triggerName, scriptName):
        if(self.scripts.has_key(triggerName)==False):
            self.scripts[triggerName] = {}
        temp = (scriptName, [] )
        #if(len(self.scripts[triggerName])<=scriptNo):
        #    self.scripts[triggerName][self.scriptCounter] = (temp)
        #else:
        self.scripts[triggerName][self.scriptCounter] = temp
        counter = self.scriptCounter
        self.scriptCounter += 1
        
        return counter
        #else:
        #    self.
        #self.scripts[triggerName] = scriptName
    def setScript(self, triggerName, scriptID,  scriptName, arguments =[]):
        self.scripts[triggerName][scriptID] = (scriptName, arguments)
        
    def setScriptArguments(self, triggerName, scriptID,arguments):
        scriptName, values = self.scripts[triggerName][scriptID]
        self.scripts[triggerName][scriptID] = (scriptName, arguments)
    
    def getScriptsAndArguments(self, triggerName):
        #[antonjs 3/29/2011] Now returns empty dict if trigger key has no scripts with it
        if triggerName in self.scripts:
            return self.scripts[triggerName]
        else:
            return {}
    
    def getScripts(self):
        return self.scripts
    
    def getScriptArguments(self, triggerName, scriptID):
        scriptName, arguments =  self.scripts[triggerName][scriptID]
        return arguments
    
    def getScriptAndArguments(self, triggerName, scriptID):
        return self.scripts[triggerName][scriptID]
    
    def removeScript(self, triggerName, scriptNo):
        if self.scripts.has_key(triggerName) == False:
            print "ERROR:Trigger name with ", triggerName, " doesn't exist!"
            return False
        del self.scripts[triggerName][scriptNo]
        if(len(self.scripts[triggerName]) == 0):
            del self.scripts[triggerName]
        return True
    
    def decodeHelper(n):
        scripts = []
        if n.localName =="script":
                    arguments = []
                    for n2 in n.childNodes:
                        if n2.localName == "triggerType":
                            triggerType = n2.childNodes[0].data.strip()
                        elif n2.localName == "scriptName":
                            scriptName = n2.childNodes[0].data.strip()
                        elif n2.localName == "parameter":
                            parameter = n2.childNodes[0].data.strip()
                            arguments.append(str(parameter))
                    scripts.append((triggerType,scriptName,arguments))
        return scripts
                    
    decodeHelper = staticmethod(decodeHelper)
    
    
    def encodeHelper(self, doc, parent):
        for triggerType, scriptTuples in self.scripts.iteritems():
            for scriptID in sorted(scriptTuples):
                script = doc.createElement("script")
                triggerTypeNode = doc.createElement("triggerType")
                triggerTypeNode.appendChild(doc.createTextNode(triggerType))
                script.appendChild(triggerTypeNode)
                
                scriptName, scriptArguments = scriptTuples[scriptID]
                scriptNameNode = doc.createElement("scriptName")
                script.appendChild(scriptNameNode)
                scriptNameNode.appendChild(doc.createTextNode(scriptName))
                temp = []
                for argument in scriptArguments:
                    scriptArgument = doc.createElement("parameter")
                    scriptArgument.appendChild(doc.createTextNode(str(argument)))
                    script.appendChild(scriptArgument)
                      
                #node.appendChild(script)
                parent.appendChild(script)
