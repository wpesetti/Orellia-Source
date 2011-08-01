# ConversationMgrBase class
# for gameplay export

from ConversationMgrBase import ConversationMgrBase

class ConversationMgr(ConversationMgrBase):
    
    def __init__(self, world, conversations):
        ConversationMgrBase.__init__(self, world, conversations)