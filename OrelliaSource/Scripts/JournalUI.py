'''
Created on Feb 3, 2011

@author: qiaosic
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

class JournalUI(UIBase):
    '''
    This is the UI of journal
    '''

    def __init__(self,world):
        '''
        Constructor
        '''
        UIBase.__init__(self, world)

              
        '''
        init variables
        '''
        #load skin of journal button and scrollbar as egg files
        self.button_maps = self.world.loader.loadModel("./LEGameAssets/Models/button") 
        self.scrollbar_maps = self.world.loader.loadModel("./LEGameAssets/Models/scrollbar")

        #skin for the journal tray
        self.img_files = ["./LEGameAssets/Textures/journal_rollout_tray.png"]

        #variables that store the UI elements which are going to be created
        self.journal_window_frame = None
        self.window_show = True
        self.journal_window = None
        self.frame = None
        self.canvas = None
        
        #variables that store list of title and statement of journal from journalMrg
        self.journal_entries= []
        self.quest_text = []

        #size of the screen
        self.screen_size_x = base.win.getXSize()
        self.screen_size_y = base.win.getYSize()
        
        
        #variables that help to make the popout window and arrange the text
        self.count = [0,0,0,0]
        self.char_size = 0.05
        self.last_char_size = None
        self.line_space = 0.2
        self.top_line = 0.1
        self.longest_line = {"menu":[0,0],"quest":[0,0]}
        self.buttons_1 = []
        self.buttons_2 = []
    
        self.page_canvas_size= {"menu": (0,0,0,0), "quest": (0,0,0,0)}
        self.page_buttons = {"menu": self.buttons_1, "quest": self.buttons_2}
        self.showing_page = "menu" 
                
        #set the default canvas size and frame size
        self.canvas_size = (0.3, 1.25, 0.015, 0.75)
        self.frame_size = (0.3, 1.25, 0.015, 0.75)
           
        def dummyMethod(): # in order to make the button do nothing when clicked
            pass
        
        self.b = DirectButton( geom = (self.button_maps.find("**/ok"),self.button_maps.find("**/click"),self.button_maps.find("**/rolling_over"),self.button_maps.find("**/disable")),
                          text_scale = (0.15,0.15), pos = (-0.23, 0, -0.12), relief=None, scale=0.38, command=dummyMethod, parent= base.a2dTopRight)
        world.accept("j", self.popoutWindow);
        world.accept("j-up", self.popoutWindow);
        

        
    def update(self):
        self.journal_entries = self.world.journalMgr.getOpenedJournalEntries()
        #self.journal_entries = [("title1","Now if I take out the task argument all is fine obviously. However I need a way to access the time the task runs.This will give you a scrollbar at the lower left side of the screen. If you want to parent the scrollbar to a determined frame, you add the keyword parent to the set of keyboards like so.DirectScrollBar is available beginning in Panda3D 1.1. It consists of a long trough, a thumb that slides along the trough, and a pair of buttons on either side of the trough to scroll one line at a time. A DirectScrollBar can be oriented either vertically or horizontally."),("title2","Completed"),("title3","statement3")]
        #print base.win.getXSize(),base.win.getYSize()
        #print "update"
        
    #Create a popout window        
    def popoutWindow(self):
        if self.window_show:
            self.longest_line = {"menu":[0,0],"quest":[0,0]}
            self.count = [0,0,0,0]
            self.update()
            self.journal_window_frame = DirectFrame(frameColor=(0, 0, 0, 0.12),frameSize=(0.28, 1.27, -0.005, 0.77), parent= base.a2dTopRight, pos = (-1.3,0,-1))
            self.journal_window = DirectScrolledFrame(canvasSize = (self.canvas_size), frameSize = (self.frame_size),frameColor=(0, 0, 0, 0.12),
                                                      autoHideScrollBars = True, manageScrollBars = True, parent = self.journal_window_frame ) 
            self.changeSkin(self.img_files)
            self.changeScrollbarSkin()
            self.canvas= self.journal_window.getCanvas()        
            self.createMenu()
            self.createQuest()
            self.showMenu()
            self.changeButtonColor()
            try:
                self.showQuest(self.journal_entries[0][0]);
            except:
                pass

            
      
        else:
            self.destroy()       
        self.window_show = not self.window_show
    
    #destroy the popout window
    def destroy(self):
        self.journal_window_frame.destroy()
        # if the button list has been detached when the parent(journal_window) is destroyed, them won't be destroyed
        for button in self.buttons_1:
            button.destroy()
        for button in self.buttons_2:
            button.destroy()
        for label in self.quest_text:
            label.destroy()
        # clean up the button list
        for i in range(len(self.buttons_1)):
            self.buttons_1.pop()
        for j in range(len(self.buttons_2)):
            self.buttons_2.pop()
        for k in range(len(self.quest_text)):
            self.quest_text.pop()
            
    '''
    These functions are for the other parts to call to hide/show the JournalUI
    '''        
#----------------------------------------------
    def hideAll(self):
        #self.b.hide()
        if not self.window_show:
            self.journal_window_frame.hide()
            

    def showAll(self):
        #self.b.show()
        if not self.window_show:
            self.journal_window_frame.show()
            

#-------------------------------------------------
    def destroyAll(self):
        self.destroy()
        #self.b.destroy()
    
    def createAll(self):
        pass
#-----------------------------------------------------------------------------------------           
        
        
    def switchPage(self, page):
        self.journal_window['canvasSize']=(self.page_canvas_size[page])
        self.hideButton(self.page_buttons[self.showing_page])
        self.showButton(self.page_buttons[page]) 
        self.showing_page = page
        
        #------------quest------------------
        if page == "quest":
            for label in self.quest_text:
                label.reparentTo(self.canvas)
        else :
            self.hideText()
            
 
            
    def hideButton(self, page):                   
        for button in page:
            button.detachNode()
            
            
    def showButton(self, page):
        for button in page:
            button.reparentTo(self.canvas)
        
    def hideText(self):

        for label in self.quest_text:
            label.detachNode()
        
        for k in range(len(self.quest_text)):
            self.quest_text.pop()

     
  
    def showMenu(self):
        self.switchPage("menu")

    
    def showQuest(self, tag):   
        for entry in self.journal_entries:
            if entry[0] == tag:
                temp_text = entry[1]                
                self.addText(temp_text, 0.05, "quest")
                break           
        self.switchPage("quest")  
       

    def addButton(self, text, position, scale, func_call, type, page):     
        if type  == 1:
            button =  DirectButton(text = (text),text_fg =(1,0,0,1),text_bg =(0,0,0,0),pos =(position),text_scale = (scale), relief = None,command=func_call, extraArgs = [text])
        else:
            button =  DirectButton(text = (text),text_fg =(1,0,0,1),text_bg =(0,0,0,0),pos =(position),text_scale = (scale), relief = None,command=func_call)

        if(position[0] - button.getWidth()/2.0 < self.longest_line[page][0]):
            '''
            something different here -0.02 for the right side 
            ''' 
            self.count[0] = position[0] - button.getWidth()/2.0 - 0.02 #right
            self.longest_line[page][0] = self.count[0]
        if(position[1] + button.getWidth()/2.0 > self.longest_line[page][1]):
            self.count[1] = position[1] + button.getWidth()/2.0 #left
            self.longest_line[page][1] = self.count[1]  
        self.count[2] = position[2]-button.getHeight()#bottom
        self.journal_window['canvasSize']=(self.count[0],self.count[1],self.count[2],self.count[3])
        
        button.detachNode()  #make sure buttons won't be shown at the first time it is created           
        self.page_buttons[page].append(button)
        self.page_canvas_size[page] = (self.count[0],self.count[1],self.count[2],self.count[3])
    
    def addText(self, show_text, text_scale, page):

        self.page_canvas_size[page]=(self.canvas_size)
        
        max_window_width = abs(self.canvas_size[1] - self.canvas_size[0])
        
        # the width of the DirectLabel object is only changing with the length of the string in text attribute, but this width is different from the width of the DriectFrame and DriectButton,
        # so I don't know what is the unit of this DriectLable width, if you change the scale of the label, the width is not going to change, and the text will going out of the boundary,
        # I should change the max number of character with scale
        text_len =  len(show_text)        

        offset = text_scale - 0.05
        
        if(offset > 0):
            max_text_len = 35 - offset * 500
        if(offset <= 0):
            max_text_len = 35 + abs(offset) * 500

        
        text_lines = []
        
        if  text_len > max_text_len:
            wrapper = TextWrapper(initial_indent="* ", width = max_text_len)
            text_lines = wrapper.wrap(show_text)
        
        else:
            text_lines.append(show_text)
     
        line_space  = 0.0
        for t in text_lines:
            temp_text = DirectLabel(text = t,pos = (0.75,0,0.52-line_space),scale = text_scale, text_bg = (0,1,1,0.0),text_fg=(0,0,0,1),frameColor=(0,0,0,0))
            self.quest_text.append(temp_text)
            if (0.5 - line_space)< self.canvas_size[2]:
                self.page_canvas_size[page]=(self.canvas_size[0],self.canvas_size[1]-0.1, 0.48 - line_space,self.canvas_size[3])
            line_space +=0.08

        for label in self.quest_text:    
            label.detachNode()  
   
    def createMenu(self):
        #initialize value for the beginning line, this will never change
        self.count[3]= self.top_line
        #add button
        offset = 0
        #self.journal_entries= [("title1","Now if I take out the task argument all is fine obviously. However I need a way to access the time the task runs."),("title2","statement2"),("title3","statement3")]
        for entry in self.journal_entries:
            self.addButton(entry[0],(-0.08, 0, -0.02+offset),(0.05,0.05),self.showQuest,1 ,"menu")
            offset += -0.08
           

    def createQuest(self):    
        self.addButton("Back",(0.45, 0, 0.62),(0.08,0.08),self.showMenu,0,"quest" )
        
        
        
    def changeSkin(self, img_files):
        if len(img_files) == 1:
            self.journal_window['image']=(img_files[0])
            #self.journal_window['image_scale']=(0.43,0,0.43) #old scale without size 800*600
            #self.journal_window['image_pos']=(0.75,0,0.33) #old position without size 800*600
            self.journal_window['image_scale']=(1.335,1,1)
            self.journal_window['image_pos']=(0,0,0)
            self.journal_window.setTransparency(1) 
            self.journal_window['frameColor']=(0,0,0,0)
        if len (img_files) == 2:
            self.journal_window_frame['image']=(img_files[1])
            #self.journal_window_frame['image_scale']=(0.44,0,0.44)#old scale without size 800*600
            #self.journal_window_frame['image_pos']=(0.75,0,0.33)#old position without size 800*600
            self.journal_window_frame['image_scale']=(1.335,1,1)
            self.journal_window_frame['image_pos']=(0,0,0)
            self.journal_window_frame.setTransparency(1)
            self.journal_window_frame['frameColor']=(0,0,0,0)
            
    def changeScrollbarSkin(self):
        self.journal_window['verticalScroll_relief']= None#  Relief appearance of the frame
        self.journal_window['verticalScroll_image']= ("./LEGameAssets/Textures/journal_scrollbar.png")
        self.journal_window.verticalScroll['image_pos']=(1.21,0.1,0.36)
        self.journal_window.verticalScroll['image_scale']=(0.05,0.1,0.38)
        self.journal_window.verticalScroll.incButton['geom']=(self.scrollbar_maps.find("**/journal_scrollbutton_down"))
        self.journal_window.verticalScroll.incButton['relief']=None#  Relief appearance of the frame
        self.journal_window.verticalScroll.incButton['geom_scale']=(0.15,0.15,0.15)
        self.journal_window.verticalScroll.decButton['geom']=(self.scrollbar_maps.find("**/journal_scrollbutton_up"))
        self.journal_window.verticalScroll.decButton['relief']=None#  Relief appearance of the frame
        self.journal_window.verticalScroll.decButton['geom_scale']=(0.15,0.15,0.15)
        self.journal_window.verticalScroll.thumb['geom']=(self.scrollbar_maps.find("**/journal_scroll_button_updown"))
        self.journal_window.verticalScroll.thumb['relief']=None#  Relief appearance of the frame
        self.journal_window.verticalScroll.thumb['geom_scale']=(0.2,0.2,0.2)
        self.journal_window.verticalScroll.thumb['frameVisibleScale']=(0.5,0.25)#Relative scale of the visible frame to its clickable bounds. Useful for creating things like the paging region of a slider, which is visibly smaller than the acceptable click region 
        self.journal_window.verticalScroll['resizeThumb']=(True)
        self.journal_window.verticalScroll['scrollSize']=(0.1) #change the amount to jump the thumb when user click up/right and down/left
        self.journal_window.verticalScroll['range']=(-1,1)# change the (min, max) range of the thumb
        
        
    #--------UI feedback-----------------    
    def changeButtonColor(self):
        for entry in self.journal_entries:
            if (entry[1] == "Completed"):
                for b in self.buttons_1:
                    if (b['text'] == entry[0]):
                        b['text_fg'] = (0,1,0,1)
                        
    def flashJournalButton(self,task):
        if task.time <= 0.5:
            self.b['geom_scale']=(0.01,0.01,0.01)
            return task.cont
        
        elif task.time <=1.0:
            self.b['geom_scale']=(1.0,1.0,1.0)
            return task.cont
        elif self.window_show != True:
            return task.done
        else:
            return task.again

    def startFlash(self):   
        self.task = taskMgr.add(self.flashJournalButton, 'flashJournalButton') 
        