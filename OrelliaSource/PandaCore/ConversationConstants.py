import wx

class SpeakerType: # to uml
    PLAYER = 'player'
    NPC = 'npc'
    
    def typeAsColor(type):
        if type == SpeakerType.PLAYER:
            return wx.BLUE
        elif type == SpeakerType.NPC:
            return wx.RED
        else:
            return wx.BLACK
    typeAsColor = staticmethod(typeAsColor)
    
    # needed?
    def typeAsString(type):
        if type == PLAYER:
            return 'Player'
        elif type == NPC:
            return 'NPC'
        else:
            return 'non-standard'
    typeAsString = staticmethod(typeAsString)

class LineIDType: # to uml
    ROOT = 0
    END_CONVERSATION = -1
    UNASSIGNED = -2
    
    # needed?
    def isValidID(id):
        return (id != ROOT and id != END_CONVERSATION)
    isValidID = staticmethod(isValidID)
    
class EditorLineType: # to uml
    NEW = 1
    LINK = 2