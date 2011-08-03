'''
Created on July 23, 2011

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
from direct.gui.OnscreenImage import OnscreenImage

from direct.task import Task

class PauseUI(UIBase):
    def __init__(self, world):
        # call super constructor
        UIBase.__init__(self, world)
        
        self.button_maps = self.world.loader.loadModel("./LEGameAssets/Models/pauseBtn")
           
        def dummyMethod(): # in order to make the button do nothing when clicked
            pass
        
        #self.b = DirectButton( geom = (self.button_maps.find("**/ok"),self.button_maps.find("**/click"),self.button_maps.find("**/rolling_over"),self.button_maps.find("**/disable")),
        #                  text_scale = (0.15,0.15), pos = (-0.8, 0, -0.12), relief=None, scale=0.38, command=dummyMethod, parent= base.a2dTopRight)
    '''
    These functions are for the other parts to call to hide/show the JournalUI
    '''        
#----------------------------------------------
    def hideAll(self):
        pass#self.b.hide()

    def showAll(self):
        pass#self.b.show();

#-------------------------------------------------
    def destroyAll(self):
        self.destroy()
        #self.b.destroy()
    
    def createAll(self):
        pass 