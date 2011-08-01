"""
Defines Sound Manager
"""
from SoundMgrBase import *

class SoundMgr(SoundMgrBase):
    """ SoundMgr will create, manage, update sounds in the scene """
    
    def __init__(self, editor):
        SoundMgrBase.__init__(self, editor)