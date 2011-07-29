import sys,random

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.task import Task
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
sys.path.append("./Panda Core scripts")
import ScriptInterface  


class PauseGameState(DirectObject):
    def __init__(self, world):
        DirectObject.__init__(self)
        self.world = world;

    def activate(self):
        print("ACTIVATED");
        
    def deactivate(self):
        print("DEACTIVATED");