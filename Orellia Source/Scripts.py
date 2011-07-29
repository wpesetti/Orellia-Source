import ast
SCRIPTS_LIST = []


def CloseConversation(world):
    def main(world):
        world.scriptInterface.CloseConversation()
    main(world)
SCRIPTS_LIST.append(CloseConversation)

def AddItem(world, itemType,count):
    def main(world, itemType,count):
        world.scriptInterface.AddItem(itemType, count)
    

    main(world, itemType,count)
SCRIPTS_LIST.append(AddItem)

def DestroyObject(world, gameObjName):
    def main(world, gameObjName):
        world.scriptInterface.DestroyGameObject(gameObjName)
    main(world, gameObjName)
SCRIPTS_LIST.append(DestroyObject)

def PrintToConsole(world, message):
    def main(world, message):
        world.scriptInterface.PrintToConsole(message)
    main(world, message)
SCRIPTS_LIST.append(PrintToConsole)

def RunObjectOnRopeLookAt(world, gameObj,rope,sequenceTime,lookAtObj):
    def main(world, gameObj,rope,sequenceTime,lookAtObj):
        world.scriptInterface.RunObjectOnRope(gameObj, rope, sequenceTime, False,False,lookAtObj)
    main(world, gameObj,rope,sequenceTime,lookAtObj)
SCRIPTS_LIST.append(RunObjectOnRopeLookAt)

def RunObjectOnRope(world, gameObj,rope,sequenceTime):
    def main(world, gameObj,rope,sequenceTime):
        world.scriptInterface.RunObjectOnRope(gameObj, rope, sequenceTime,True,True)
    main(world, gameObj,rope,sequenceTime)
SCRIPTS_LIST.append(RunObjectOnRope)

def SetJournalEntryValue(world, entryTag,value,isIncr=False,listOfValues = None):
    minValue = 0
    delObj = None
    if not listOfValues == None and not listOfValues == "":
        listOfValues = ast.literal_eval(listOfValues)
        for ii in range(len(listOfValues)):
            print ii,listOfValues[ii]
            if ii == 0:
                minValue = listOfValues[0]
            if ii == 1:
                delObj = listOfValues[1]
    def main(world, entryTag,value,isIncr,minValue,delObj):
        print delObj
        world.scriptInterface.SetJournalEntryValue(entryTag, value,isIncr,minValue,delObj)
    main(world, entryTag,value,isIncr,minValue,delObj)
SCRIPTS_LIST.append(SetJournalEntryValue)

def RunObjectOnRopeFollow(world, gameObj,rope,sequenceTime):
    def main(world, gameObj,rope,sequenceTime):
        world.scriptInterface.RunObjectOnRope(gameObj, rope, sequenceTime, False,True, None)
    main(world, gameObj,rope,sequenceTime)
SCRIPTS_LIST.append(RunObjectOnRopeFollow)

def LoopObjectOnRopeFollow(world, gameObj,rope,sequenceTime):
    def main(world, gameObj,rope,sequenceTime):
        world.scriptInterface.RunObjectOnRope(gameObj, rope, sequenceTime, True,True, None)
    main(world, gameObj,rope,sequenceTime)
SCRIPTS_LIST.append(LoopObjectOnRopeFollow)

def HasJournalEntryAndValue(world, entryTag,value):
    def main(world, entryTag,value):
        return world.scriptInterface.HasJournalEntryAndValue(entryTag, value)
    return main(world, entryTag,value)
SCRIPTS_LIST.append(HasJournalEntryAndValue)

def OpenConversation(world, convo):
    def main(world, convo):
        world.scriptInterface.OpenConversation(convo)
    main(world, convo)
SCRIPTS_LIST.append(OpenConversation)

def OpenJournalEntry(world, entryTag):
    def main(world, entryTag):
        world.scriptInterface.OpenJournalEntry(entryTag)
    main(world, entryTag)
SCRIPTS_LIST.append(OpenJournalEntry)

def LoopObjectOnRopeLookAt(world, gameObj,rope,sequenceTime,lookAtObj):
    def main(world, gameObj,rope,sequenceTime,lookAtObj):
        world.scriptInterface.RunObjectOnRope(gameObj, rope, sequenceTime, True,False,lookAtObj)
    main(world, gameObj,rope,sequenceTime,lookAtObj)
SCRIPTS_LIST.append(LoopObjectOnRopeLookAt)

def RunCamera(world, cameraName,isLoop,length):
    def main(world, cameraName,isLoop,length):
        world.scriptInterface.RunCamera(cameraName,isLoop,length)
    main(world, cameraName,isLoop)
SCRIPTS_LIST.append(RunCamera)

def NotHasJournalEntryAndValue(world, entryTag,valueString):
    def main(world, entryTag,valueString):
        if(world.scriptInterface.HasJournalEntryAndValue(entryTag, valueString)):
            return False
        else:
            return True
    return main(world, entryTag,valueString)
SCRIPTS_LIST.append(NotHasJournalEntryAndValue)

def NotHasJournalEntry(world, entryTag):
    def main(world, entryTag):
        if(world.scriptInterface.HasJournalEntry(entryTag)):
            return False
        else:
            return True
    return main(world, entryTag)
SCRIPTS_LIST.append(NotHasJournalEntry)

def HasItem(world, itemTag):
    def main(world, itemTag):
        return world.scriptInterface.HasItem(itemTag)
    return main(world, itemTag)
SCRIPTS_LIST.append(HasItem)

def ChangeScene(world, sceneName):
    def main(world, sceneName):
        world.scriptInterface.ChangeScene(sceneName)
    main(world, sceneName)
SCRIPTS_LIST.append(ChangeScene)

def LoopObjectOnRope(world, gameObj,rope,sequenceTime):
    def main(world, gameObj,rope,sequenceTime):
        world.scriptInterface.RunObjectOnRope(gameObj, rope, sequenceTime, True,False, None)
    main(world, gameObj,rope,sequenceTime)
SCRIPTS_LIST.append(LoopObjectOnRope)

def ChangeSceneTo(world, sceneName,objectName):
    def main(world, sceneName,objectName):
        world.scriptInterface.ChangeSceneTo(sceneName, objectName)
    main(world, sceneName,objectName)
SCRIPTS_LIST.append(ChangeSceneTo)

def HasManyItems(world, itemTag,count):
    def main(world, itemTag,count):
        return world.scriptInterface.HasManyItems(itemTag, count)
    return main(world, itemTag,count)
SCRIPTS_LIST.append(HasManyItems)

def PlaySound(world, soundName,Loop):
    def main(world, soundName,Loop):
        world.scriptInterface.playSound(soundName,Loop)
    main(world, soundName,Loop)
SCRIPTS_LIST.append(PlaySound)

def playSound3d(world, soundName,Loop):
    def main(world,object, soundName,Loop):
        world.scriptInterface.playSound3d(object,soundName,Loop)
    main(world, object,soundName,Loop)
SCRIPTS_LIST.append(PlaySound)


def HasJournalEntry(world, entryTag):
    def main(world, entryTag):
        return world.scriptInterface.HasJournalEntry(entryTag)
    return main(world, entryTag)
SCRIPTS_LIST.append(HasJournalEntry)

def FillHP(world, gameObjName):
    def main(world, gameObjName):
        world.scriptInterface.FillHP(gameObjName)
    main(world, gameObjName)
SCRIPTS_LIST.append(FillHP)

def Billboard(world,npcName,type,PandaName):
    def main(world,npcName,type,PandaName):
    #type will be friendly, neutral, or hostile
        world.Billboard(npcName,type,PandaName)
    main(world,npcName,type,PandaName)
SCRIPTS_LIST.append(Billboard)

def PlayMovie(world,movieName):
    def main(world,movieName):
        world.playMovie(movieName)
    main(world,movieName)
SCRIPTS_LIST.append(PlayMovie)

def StartMob(world,mobName):
    def main(world,mobName):
        world.startMob(mobName)
    main(world,mobName)
SCRIPTS_LIST.append(StartMob)

def worldFunc(world,funcName,param=""):
    def main(world,funcName,param):
        if param == "":
            print "AUTOPARAM"
            world.callFunc(funcName)
        elif eval("world."+param):
            print "LOLOL",param
            world.callFunc(funcName)
    main(world,funcName,param)
SCRIPTS_LIST.append(worldFunc)