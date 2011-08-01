'''
Created on July 24, 2011

@author: Michael Coleman
'''

from direct.gui.DirectGui import *

#from pandac.PandaModules import TextNode
from pandac.PandaModules import *
from direct.gui.DirectGui import DirectFrame
from textwrap import *

from direct.task import Task

from JournalMgr import *
from UIBase import *

from direct.task import Task

class TimerUI(UIBase):
    def __init__(self, world):
        # call super constructor
        UIBase.__init__(self, world)
        
        self.button_maps = self.world.loader.loadModel("./LEGameAssets/Models/shroomToggle")
        self.running = False;
        self.time = 0.0;
        def dummyMethod(): # in order to make the button do nothing when clicked
            pass
        
        self.b = DirectButton( geom = (self.button_maps.find("**/ok"),self.button_maps.find("**/click"),self.button_maps.find("**/rolling_over"),self.button_maps.find("**/disable")),
                          text_scale = (0.15,0.15), pos = (-1.25, 0, -0.36), relief=None, scale=0.38, command=dummyMethod, parent= base.a2dTopRight,
                          text = "Time: 0")
        self.updateTime(0);
            
    '''
    These functions are for the other parts to call to hide/show the JournalUI
    '''        
#----------------------------------------------
    def hideAll(self):
        self.b.hide()

    def showAll(self):
        pass
        
    def startTimer(self, time):
        self.time = time;
        self.running = True;
        self.b.show();
        
    def stopTimer(self):
        self.running = False;
    
    def killTimer(self):
        self.time = 0.0;
        self.running = False;
        self.b.hide();
        
    def update(self):
        if self.running:
            self.time -= globalClock.getDt();
            self.updateTime(self.time);
            if self.time <= 0:
                self.time = 0;
                self.onTime();
    
    def onTime(self):
        self.stopTimer();
    
    def updateTime(self, timeLeft):
        self.b["text"] = "Time: " + str(int(timeLeft));
        self.b.setText();
            

#-------------------------------------------------
    def destroyAll(self):
        self.destroy()
        self.b.destroy()
    
    def createAll(self):
        pass 