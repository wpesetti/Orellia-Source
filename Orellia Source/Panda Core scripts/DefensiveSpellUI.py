'''
Created on Mar 11, 2011

@author: qiaosic
'''
from direct.showbase import DirectObject
from direct.gui.DirectGui import *

from UIBase import *

class DefensiveSpellUI(UIBase,DirectObject.DirectObject):
    '''
    classdocs
    '''


    def __init__(self,world):
        '''
        Constructor
        '''
        UIBase.__init__(self, world)
        
        self.buttons = []
        self.img_file = ["./LEGameAssets/Textures/defense_1.png","./LEGameAssets/Textures/defense_2.png","./LEGameAssets/Textures/defense_3.png"]
        self.position = (0,0,0)
        self.number = 3
        self.i = 0
        self.funcs = [self.spell1, self.spell2, self.spell3]
        
        for s in self.funcs:
            self.position=(0.12+self.i*0.16,0,0.12)
            self.addButton(s,self.img_file[self.i])
            self.i += 1
        
        self.hotkey()
        
    
    def update(self):
        pass
#-----------------------------------------------------    
    def hideAll(self):
        for b in self.buttons:
            b.hide()
            
    def showAll(self):
        for b in self.buttons:
            b.show()
            
    def destroyAll(self):
        for b in self.buttons:
           b.destroy()
    
    def createAll(self):
        self.i = 0
        for s in self.funcs:
            self.position=(-1.2+self.i*0.14,0,0.12-1.0)
            self.addButton(s,self.img_file[self.i])
            self.i += 1
#-----------------------------------------------------    
    
    
    def addButton(self, func_call, img_file):
        b = DirectButton( scale=0.11, relief = None,
                          image = (img_file),pos =(self.position),command= func_call, parent = base.a2dBottomLeft)
        b.setTransparency(1)
        self.buttons.append(b)
        
    def hotkey(self):
        self.accept("1",self.funcs[0])
        self.accept("2",self.funcs[1])
        self.accept("3",self.funcs[2])

        
    def spell1(self):
        print "DefensiveSpell 1"
    
    def spell2(self):
        print "DefensiveSpell 2"
        
    def spell3(self):
        print "DefensiveSpell 3"