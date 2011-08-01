'''
Created on Feb 23, 2011

@author: qiaosic
'''

from direct.gui.DirectGui import *


from pandac.PandaModules import *
from direct.gui.DirectGui import DirectFrame



from UIBase import *


class InventoryUI(UIBase):
    '''
    This is the UI of inventory
    '''

    def __init__(self,world):
        '''
        Constructor
        '''
        UIBase.__init__(self, world)

      
        maps = self.world.loader.loadModel("./LEGameAssets/Models/button") 
        
        self.inventory_window_frame = None
        self.window_show = True  
        self.inventory_window = None
        self.frame = None
        self.canvas = None
        
        self.inventories= []
       
        self.canvas_size = (0.3, 1.25, 0.015, 0.75)
        self.frame_size = (0.3, 1.25, 0.015, 0.75)
       
       
        self.count = [0,0,0,0]


        self.icon_count = 0
        self.top_line = 0.15
        self.longest_line = 0
        self.buttons_1 = []
 
    
        self.page_canvas_size= (0,0,0,0)

        b = DirectButton( text = ("Inventory", "click!!!", "rolling over", "disabled"), 
                         #geom = (maps.find("**/ok"),maps.find("**/click"),maps.find("**/rolling_over"),maps.find("**/disable")),
                         text_scale = (0.15,0.15), pos = (0.6, 0, 0.85), relief=None, scale=0.4, command=self.popoutWindow)
        #b = DirectButton( text = ("Inventory", "click!!!", "rolling over", "disabled"), 
        #                  text_scale = (0.15,0.15), pos = (0.6, 0, 0.85), relief=None, scale=0.4, command=self.popoutWindow)

    def update(self):
        pass
    
    #Create a window        
    def popoutWindow(self):
        if self.window_show:
            self.createWindow()     
        else:
            self.destroyWindow()
        self.window_show = not self.window_show
    
    def createWindow(self):
        self.longest_line = 0
        self.count = [0,0,0,0]
        self.inventory_window_frame = DirectFrame(frameColor=(0, 0, 0, 0.2),frameSize=(0.28, 1.27, -0.005, 0.77))
        self.inventory_window = DirectScrolledFrame(canvasSize = (self.canvas_size), frameSize = (self.frame_size),frameColor=(0, 0, 0, 0.2),
                                                  autoHideScrollBars = True, manageScrollBars = True, parent = self.inventory_window_frame ) 
        #self.changeSkin()
        self.canvas= self.inventory_window.getCanvas()        
        self.createMenu()
        self.showMenu()

    
    def destroyWindow(self):
        self.inventory_window_frame.destroy()
        # if the button list has been detached when the parent(inventory_window) is destroyed, them won't be destroyed
        for button in self.buttons_1:
            button.destroy()
        # clean up the button list
        for i in range(len(self.buttons_1)):
            self.buttons_1.pop()
    
    
    def hideButton(self, page):            
        for button in page:
            button.detachNode()
            
            
    def showButton(self, page):
        for button in page:
            button.reparentTo(self.canvas)
    
    

    def addButton(self, text, position, scale, img_file, func_call):     
        
        button =  DirectButton(text = (""),pos =(position),text_scale = (scale), image = (img_file), image_scale = (0.1,0,0.1), relief = None,command=func_call)
        if(self.icon_count == 0):
            self.count[0] = self.canvas_size[0]
            self.longest_line = position[0] + button.getWidth()/2.0
            self.count[2] = position[2]-button.getHeight()/2.0

        
        if(position[0] + button.getWidth()/2.0 >= self.longest_line):
            self.count[1] = position[0] + button.getWidth()/2.0 #right
            self.longest_line = self.count[1]  
            
        '''
        add 0.06 to bottom
        '''
        self.count[2] = position[2]-button.getHeight()/2.0-0.06#bottom
            
        self.inventory_window['canvasSize']=(self.count[0],self.count[1],self.count[2],self.count[3])
        button.detachNode()  #make sure your button won't be shown at the first time it is created           
        self.buttons_1.append(button)
        self.page_canvas_size = (self.count[0],self.count[1],self.count[2],self.count[3])

                        
        if(self.icon_count == 2):
            self.icon_count = 0
        else:
            self.icon_count += 1
    
   
   
    def createMenu(self):
              
        #initialize value for the beginning line, this will never change
        self.count[3]= self.top_line
        #add button 
        down_offset = 0
        right_offset = 0
        button_count = 0
        self.inventories=["title1","title1","title1","title1","title1","title1"]
        for inventory in self.inventories:
            self.addButton(inventory,(0.45+right_offset, 0, -0.02+down_offset),(0.05,0.05),"./LEGameAssets/Textures/inventory_placeholder.png",self.doSomething)
            if(button_count  == 2):
                down_offset += -0.3
                button_count = 0
                right_offset = 0
            else:
                button_count +=1
                right_offset += 0.3
    
        
        
    def showMenu(self):
        self.showButton(self.buttons_1)
        

    def doSomething(self):
        pass    
    
    def changeSkin(self):
        self.inventory_window['image']=("../textures/background.png")
        self.inventory_window['image_scale']=(0.43,0,0.43)
        self.inventory_window['image_pos']=(0.75,0,0.33)
        self.inventory_window.setTransparency(1) 
        self.inventory_window['frameColor']=(0,0,0,0)
        self.inventory_window_frame['image']=("../textures/background.png")
        self.inventory_window_frame['image_scale']=(0.44,0,0.44)
        self.inventory_window_frame['image_pos']=(0.75,0,0.33)
        self.inventory_window_frame.setTransparency(1)
        self.inventory_window_frame['frameColor']=(0,0,0,0)
        