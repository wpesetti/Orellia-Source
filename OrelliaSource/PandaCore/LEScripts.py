SCRIPTS_LIST = []


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

def ChangeScene(world, sceneName):
    def main(world, sceneName):
        world.scriptInterface.ChangeScene(sceneName)
    main(world, sceneName)
SCRIPTS_LIST.append(ChangeScene)

def PrintToConsole(world, message):
    def main(world, message):
        world.scriptInterface.PrintToConsole(message)
    main(world, message)
SCRIPTS_LIST.append(PrintToConsole)

def RunCamera(world, cameraName):
    def main(world, cameraName):
        world.scriptInterface.RunCamera(cameraName)
    main(world, cameraName)
SCRIPTS_LIST.append(RunCamera)