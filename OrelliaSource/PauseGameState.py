import sys,random

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from textwrap import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *

from JournalMgr import *
from UIBase import *
sys.path.append("./PandaCore") 

import ScriptInterface


class PauseGameState(DirectObject):
    def __init__(self, world):
        DirectObject.__init__(self)
        self.world = world;
        self.ui = PauseStateUI(world);
        self.deactivate();

    def activate(self):
        self.ui.showAll();
        print("ACTIVATED");
        
    def deactivate(self):
        self.ui.hideAll();
        print("DEACTIVATED");
        
class PauseStateUI(UIBase):
    def __init__(self, world):
        # call super constructor
        UIBase.__init__(self, world)
        self.world = world
        
        self.button_maps = self.world.loader.loadModel("./LEGameAssets/Models/resumeBtn")
        self.button_maps2 = self.world.loader.loadModel("./LEGameAssets/Models/exitBtn")
        
        self.resumeBtn = DirectButton( geom = (self.button_maps.find("**/ok"),self.button_maps.find("**/click"),self.button_maps.find("**/rolling_over"),self.button_maps.find("**/disable")),
                          text_scale = (0.15,0.15), pos = (-1.4, 0, -0.34), relief=None, scale=0.38, command=self.OnResume, parent= base.a2dTopRight)
        self.quitBtn = DirectButton( geom = (self.button_maps2.find("**/ok"),self.button_maps2.find("**/click"),self.button_maps2.find("**/rolling_over"),self.button_maps2.find("**/disable")),
                          text_scale = (0.15,0.15), pos = (-1.4, 0, -0.34 - 0.26), relief=None, scale=0.38, command=self.OnQuit, parent= base.a2dTopRight)
                          
    def OnResume(self):
        self.world.pauseToggle();
    def OnSave(self):
        self.world.saveMan.saveWorld();
    def OnQuit(self):
        sys.exit();
        
    def showAll(self):
        self.resumeBtn.show();
        self.quitBtn.show();
    def hideAll(self):
        self.resumeBtn.hide();
        self.quitBtn.hide();