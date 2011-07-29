'''
Created on Mar 11, 2011

@author: qiaosic
'''
from direct.gui.DirectGui import *
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import *


from UIBase import *

class ModifierSporeUI(UIBase):
    '''
    classdocs
    '''


    def __init__(self,world):
        '''
        Constructor
        '''
        UIBase.__init__(self, world)
        
        self.buttons = []
        self.img_file = ["./LEGameAssets/Textures/item_1.png","./LEGameAssets/Textures/item_2.png","./LEGameAssets/Textures/item_3.png","./LEGameAssets/Textures/item_4.png"]
        self.position = (0,0,0)
        self.number = 3
        self.i = 0
        self.textNumber = None
        self.funcs = [self.spell1, self.spell2, self.spell3,self.spell4]
        
        #add frame of item tray
        self.frame = DirectFrame(image = ("./LEGameAssets/Textures/item_tray.png"), frameColor=(0, 0, 0, 0),
                                 image_scale = (1.335,1,1),image_pos = (-1.34, 0, 1),frameSize=(-1,1,-1,1),pos=(0,0,0),parent = base.a2dBottomRight)
        self.frame.setTransparency(1)
        
        #add item buttons
#        for s in self.funcs:
#            self.position=(-0.58+self.i*0.15,0,0.12)
#            self.addButton(s,self.img_file[self.i])
#            self.i += 1
        
        self.number = ["","","",""]
        self.numbers = []
        #self.countNumber(self.number)
        
        
    
    def update(self):
        pass
#-------------------------------------------------------    
    def hideAll(self):
        self.frame.hide()
        for b in self.buttons:
            b.hide()
            
          
    def showAll(self):
        self.frame.show()
        for b in self.buttons:
            b.show()       
    
    
    def hideButton(self, button):
        self.buttons[button].detachNode()
        
    def showButton(self, button):
        self.buttons[button].reparentTo(self.frame)
    
    def destroyAll(self):
        self.frame.destroy()
        for b in self.buttons:
            b.destroy()
            
    def createAll(self):
        #add frame of item tray
        self.frame = DirectFrame(image = ("./LEGameAssets/Textures/item_tray.png"), frameColor=(0, 0, 0, 0),
                                 image_scale = (1.335,1,1),image_pos = (0, 0, 0),frameSize=(-1,1,-1,1),pos=(0,0,0))
        self.frame.setTransparency(1)       
        #add item buttons
        self.i = 0
        for s in self.funcs:
            self.position=(0.76+self.i*0.15,0,0.12-1)
            self.addButton(s,self.img_file[self.i])
            self.i += 1
        
#-------------------------------------------------------          
    def insertButton(self, index, func_call, img_file):
        position=(-0.58+index*0.15,0,0.12)
        b = DirectButton( scale=.05, relief = None,
                          image = (img_file),pos =(position),command= func_call, parent = self.frame )#parent frame to buttons
        b.setTransparency(1)
        self.buttons.insert(index, b)#self.buttons.append(b)
            
    
    def addButton(self, func_call, img_file, count = 0):
        position=(-0.60+len(self.buttons)*0.155,0,0.12) #
        
        fullsize = PNMImage(Filename(img_file))
        resizedImage = PNMImage(32,30)
        resizedImage.addAlpha()
        resizedImage.gaussianFilterFrom(1.0, fullsize)
        myTexture=Texture()
        myTexture.load(resizedImage)
        #image = (img_file)
        b = DirectButton( scale=.05, relief = None,
                          image =myTexture,pos =(position),command= func_call, parent = self.frame )#parent frame to buttons
        b.setTransparency(1)
        self.buttons.append(b)
        textScale = 0.07
        textPosition = (b["pos"][0],b["pos"][2],0)
        text = OnscreenText( text = str(count), pos = textPosition,scale = textScale, parent = self.frame)
        self.numbers.append(text)
        return len(self.buttons)-1
    
    def removeButton(self, index):
        self.buttons[index].destroy()
    
    def changeItemCount(self, index, count):
        #self.number[index] = str(count)#self.buttons[index]["text"] = newText
        #position = self.buttons[index]["pos"]
        position = self.numbers[index]["pos"]
        #print "HEEEEEEEEEERE"
        #print position
        self.numbers[index]["text"] = str(count)
        self.numbers[index]["pos"] = position
        #self.countNumber(self.number)

        
    #def countNumber(self,number): 
    #    string = str(number[0])+"        " +str(number[1])+"          " + str(number[2])+"       " + str(number[3])
    #    self.textNumber = OnscreenText( text = string, pos = (-0.36,0.08,0),scale = 0.07, parent = self.frame)
        
    def spell1(self):
        print "ModifierSpore 1"

        
    def spell2(self):
        print "ModifierSpore 2"
        
    def spell3(self):
        print "ModifierSpore 3"
        
    def spell4(self):
        print "ModifierSpore 4"
        
