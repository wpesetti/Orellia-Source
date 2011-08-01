'''
Created on Feb 28, 2011

@author: qiaosic
'''

from direct.showbase import DirectObject
from direct.gui.DirectGui import *


from UIBase import *

class OffensiveSpellUI(UIBase,DirectObject.DirectObject):
    '''
    classdocs
    '''


    def __init__(self, world):
        '''
        Constructor
        '''
        UIBase.__init__(self, world)
        
        '''
        init variables
        '''
        self.world = world
        self.buttons = []
        self.img_file = ["./LEGameAssets/Textures/offense_1.png","./LEGameAssets/Textures/offense_2.png","./LEGameAssets/Textures/offense_3.png"]
        self.img_file_disable=["./LEGameAssets/Textures/offense_disable_1.png","./LEGameAssets/Textures/offense_disable_2.png","./LEGameAssets/Textures/offense_disable_3.png"]
        self.position = (0,0,0)
        self.addButton(3,self.buttonOnClick,self.img_file)
        self.count = 0
        self.number = 3

        self.arrowImg = OnscreenImage(image = './LEGameAssets/Textures/offense_arrow.png', pos = (0.25, 0, -0.85),scale = (0.04,0.04,0.035), parent = base.a2dTopLeft)
        self.arrowImg.setTransparency(1)
        
        self.hotKey(3)
        self.changeFunc(self.number)
       
    
    def update(self):
        pass
#---------------------------------------------------    
    def hideAll(self):
        self.arrowImg.hide()
        for b in self.buttons:
            b.hide()
            
    def showAll(self):
        self.arrowImg.show()
        for b in self.buttons:
            b.show()
    
    def destroyAll(self):
       for b in self.buttons:
           b.destroy()
    
    def createAll(self):
        self.addButton(3,self.buttonOnClick,self.img_file)
#---------------------------------------------------      
    def addButton(self, number,func_call, img_file):
        for i in range(number):
            self.position=(0.13,0,(i*-1+3)*0.15-1.3)
            b = DirectButton(scale=0.11, relief = None,
                             image = (img_file[i]),pos =(self.position),command= func_call, extraArgs = [i], parent = base.a2dTopLeft)
            b.setTransparency(1)
            self.buttons.append(b)
            
    def disableButton(self, index):
        self.disable_count = 0
        for b in self.buttons:
            b["image"]= self.img_file_disable[self.disable_count]
            self.disable_count += 1
        self.buttons[index]["image"]= self.img_file[index]
       
    
    def changeFunc(self, number):
        if self.count == 0:
            self.doSomething1()
            self.disableButton(self.count)
        elif self.count == 1:
            self.doSomething2()
            self.disableButton(self.count)
        elif self.count == 2:
            self.doSomethingelse() 
            self.disableButton(self.count)
        self.changeArrow(self.count)  
        self.count = (self.count + 1)%number
         
       
    def buttonOnClick(self,index):
        self.disableButton(index)
        self.count = (index + 1)%self.number
        if index == 0:
            self.doSomething1()
        elif index == 1:
            self.doSomething2()
        elif index == 2:
            self.doSomethingelse()
        self.changeArrow(index)
    
    def hotKey(self, number):
        self.accept("tab", self.changeFunc,[number])
    
    
    def changeArrow(self,i):
        self.arrowImg['pos']=(0.25, 0, -0.85-i*0.15)

    def doSomething1(self):
        self.world.curSpellIndex = 0 

        
    def doSomething2(self):
        self.world.curSpellIndex = 1

    
    def doSomethingelse(self):
        self.world.curSpellIndex = 2

            