# this is a template of what will be exported from LE

SCRIPTS_LIST = []


# template
#def MyScript(world):
#    def helper(world):
#        pass
#    def main(world):
#        pass
#    main(world)
#SCRIPTS_LIST.append(MyScript)


# For testing
def script1(world):
    def main(world):
        print 'script1: '
    main(world)
SCRIPTS_LIST.append(script1)

def script2(world, a):
    def main(world, a):
        print 'script2: %s' %(a)
    main(world, a)
SCRIPTS_LIST.append(script2)

def script3(world, a, b, c):
    def main(world, a, b, c):
        print 'script3: %s %s %s' %(a, b, c)
    main(world, a, b, c)
SCRIPTS_LIST.append(script3)

def PrintToConsole(world, message):
    def main(world, message):
        world.scriptInterface.PrintToConsole(message)
    main(world, message)
SCRIPTS_LIST.append(PrintToConsole)


# For Journal
def OpenJournalEntry(world, entryTag):
    def main(world, entryTag):
        world.scriptInterface.OpenJournalEntry(entryTag)
    main(world, entryTag)
SCRIPTS_LIST.append(OpenJournalEntry)

def SetJournalEntryValue(world, entryTag, value):
    def main(world, entryTag, value):
        world.scriptInterface.SetJournalEntryValue(entryTag, value)
    main(world, entryTag, value)
SCRIPTS_LIST.append(SetJournalEntryValue)


# For Conversations
def OpenConversation(world, conversation):
    def main(world, conversation):
        world.scriptInterface.OpenConversation(conversation)
    main(world, conversation)
SCRIPTS_LIST.append(OpenConversation)

def CloseConversation(world):
    def main(world):
        world.scriptInterface.CloseConversation()
    main(world)
SCRIPTS_LIST.append(CloseConversation)


# Scenes
def ChangeScene(world, sceneName):
    def main(world, sceneName):
        world.scriptInterface.ChangeScene(world, sceneName)
    main(world, sceneName)
SCRIPTS_LIST.append(ChangeScene)

def RunCamera(world, cameraName):
    def main(world, cameraName):
        world.scriptInterface.RunCamera(world, cameraName)
    main(world, cameraName)
SCRIPTS_LIST.append(RunCamera)


#class ScriptInterface:
#    
#    def __init__(self, world):
#        self.world = world
        

#SCRIPTS_LIST = []
#
#def script1(world):
#    print 'script1: '
#SCRIPTS_LIST.append(script1)
#
#def script2(world, a):
#    print 'script2: %s' %(a)
#SCRIPTS_LIST.append(script2)
#
#def script3(world, a, b, c):
#    print 'script3: %s %s %s' %(a, b, c)
#SCRIPTS_LIST.append(script3)
#
#def convoFunc(world):
#    world.conversationMgr.openConversation('play')
#SCRIPTS_LIST.append(convoScript)
#
#
#
#
#
#
#
#
#
#
#def convoScript(a, b, c):
#    LEFunction.
#
#
#
#
#
#
## script
#def convoScript(world, a, b, c):
#    world.interface.convoFunc(a, b, c)
























#class printToConsole:
#    
#    def printToConsole_mainFn():
#        print 'printToConsole_mainFn called'

#class MyScriptsClass:
#    
#    def script1():
#        print 'printToConsoleScript_fn called'
#    staticmethod(script1)
#    
#    def script2():
#        print 'MATH IS FUN, MMKAY?'
#    staticmethod(script2)
    
#def script1():
#    print 'printToConsoleScript_fn called'
#    
#def script2():
#    print 'MATH IS FUN, MMKAY?'

#class Script1:
#    def __init__(self):
#        print 'script1!'
#        
#class Script2:
#    def __init__(self):
#        print 'script 2 ...'