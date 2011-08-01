# ScriptMgrBase.py
# Class for handling, running scripts in an exported world

import inspect
import Debug
#from LEScripts import *

class ScriptMgrBase:
    
    def __init__(self, world):
        self.world = world
        self.tagMap = {} # { scriptTag string : scriptFn function }
        
        #self.loadScripts(SCRIPTS_LIST)
        Debug.debug(__name__,str(self.tagMap))
        
    def loadScripts(self, scriptList):
        for script in scriptList:
            scriptName = script.__name__
            Debug.debug(__name__,str(scriptName))
            self.tagMap[scriptName] = script
    
    # TODO: A doScript function that puts the script in a queue to execute when a different scene is loaded
    
    # scriptData is a tuple = ( 'scriptName' , [ arg1 , arg2 ] )
    # NOTE: a singleton tuple is compiled into just its element, so for example len(args) if args is ('message') will return 7, the length of the string 
    def doScript(self, scriptData):
        #temp
        Debug.debug(__name__,'==?= regular script data form : '+str(scriptData))
        print "ScriptData = ",scriptData
        tag = scriptData[0]
        if len(scriptData) > 1:
            args = scriptData[1]
        else:
            args = []
        
        if self.hasScript(tag):
            if not self.getNumScriptArgs(tag) == len(args):
                if not self.getNumScriptArgs(tag) == len(args):
                    for ii in range(self.getNumScriptArgs(tag)):
                        print ii
                        if ii > len(args):
                            args.append("")
            scriptFn = self.tagMap[tag]
            scriptFn(self.world, *args) # always pass the world as parameter 0
            ## else:
                ## # CONSIDER: exception class
                ## print 'ERROR: script \'%s\' takes %d args (%d given)' %(tag, self.getNumScriptArgs(tag), len(args))
        else:
            print 'ERROR: script name \'%s\' not found' %(tag)
    
    # TODO: merge with doScript fn...only diff is return statement
    def doConditionScript(self, scriptData):
        Debug.debug(__name__,'==?= condition script data form : '+str(scriptData))
        tag = scriptData[0]
        if len(scriptData) > 1:
            args = scriptData[1]
        else:
            args = []
        ##print tag,",",args
        if self.hasScript(tag):
            if not self.getNumScriptArgs(tag) == len(args):
                for ii in range(self.getNumScriptArgs(tag)):
                    print ii
                    if ii > len(args):
                        args.append("")
                    
            scriptFn = self.tagMap[tag]
            bool = scriptFn(self.world, *args)
            
            # temp
            #bool = False
            #print '=test= scriptFn type : ', type(scriptFn)
            #print '=test= scriptFn with world and args type : ', type(scriptFn(self.world, *args))
            #print '=test= scriptFn return when eval used : ', eval(scriptFn(self.world, *args))
            
            Debug.debug(__name__,'==== script '+str(tag)+' with args '+str(args)+ ' evaluated to be : '+str(bool)) 
            return bool
            ## else:
                ## # CONSIDER: exception class
                ## print 'ERROR: script \'%s\' takes %d args (%d given)' %(tag, self.getNumScriptArgs(tag), len(args))
        else:
            print 'ERROR: script name \'%s\' not found in doConditionScript function' %(tag)
    
#    def doScript(self, tag, argsList=[]):
#        if self.hasScript(tag):
#            if self.getNumScriptArgs(tag) == len(argsList):
#                scriptFn = self.tagMap[tag]
#                scriptFn(self.world, *argsList) # always pass the world as parameter 0
#            else:
#                # CONSIDER: exception class
#                print 'ERROR: script \'%s\' takes %d args (%d given)' %(tag, self.getNumScriptArgs(tag), len(argsList))
#        else:
#            print 'ERROR: script name \'%s\' not found' %(tag)
    
    def hasScript(self, tag):
        return (tag in self.tagMap)
    
    # returns the number of args for a script, NOT INCLUDING the world object automatically passed as parameter 0
    def getNumScriptArgs(self, tag):
        if self.hasScript(tag):
            fn = self.tagMap[tag]
            argData = inspect.getargspec(fn)
            return len(argData[0]) - 1
        else:
            # CONSIDER: make custom exception class
            print 'ERROR: script name \'%s\' not found' %(tag)
    
    # will overwrite an old script with the same tag
    def addScript(self, scriptTag, fn):
        self.tagMap[scriptTag] = fn