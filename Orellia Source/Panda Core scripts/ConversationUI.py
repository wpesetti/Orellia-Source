# @WESLEY: search for "playConvoSound" without quotations (this is the method to implement).

from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from ConversationMgr import *

from JournalUI import *
from OffensiveSpellUI import *
from ModifierSporeUI import *
from DefensiveSpellUI import *

from UIBase import *
import textwrap
import Debug

class ConversationUI(UIBase):
    '''
    This is the UI of Conversation
    '''

    def __init__(self,world):
        '''
        Constructor
        '''
        UIBase.__init__(self,world)
        self.world = world
        t = ""
        playChoices = ['']
        self.myFrame = DirectFrame(frameColor = (0,1,1,0), pos =(0,0,0))
        self.npcchat(t,25)
        self.playerchat(playChoices)
        self.syncedWithConvoMgr = False
    
    def update(self):
        '''
        iherit from UIBase     
        update the ConversationUI
        '''    
        #self.accept("a", self.reposition)
        if self.world.conversationMgr.isConversationOpen():
            if not self.syncedWithConvoMgr:
                self.npcchatList.destroy()
                self.radioButtonList.destroy()
                self.playerbgFrame.destroy()
                self.npcbgFrame.destroy()
                
                npc_t = self.world.conversationMgr.getNPCStatement()  
                
                if(npc_t == None):
                    self.showotherUI()
                    return
                
                #hide other UI components
                self.hideotherUI()
                self.world.disableMovement(self.world.hero);
                playChoices = self.world.conversationMgr.getValidResponses()    
                textwrap = 110
                if npc_t =="":#there is no npc chat
                    if len(playChoices) != 0:
                        self.playerchat(playChoices)
                        
                else:            
                    if len(playChoices) == 0:#there is only npc chat             
                        self.npcchat(npc_t,textwrap)  
                        self.noPlayerchat()             
                       
                    else: #we have both of them             
                        self.npcchat(npc_t,textwrap)                
                        self.playerchat(playChoices)

                    self.playConvoSound();
        
                self.syncedWithConvoMgr = True
        else:
            #print "show all the ui"
            self.showotherUI()
            self.npcchatList.destroy()
            self.radioButtonList.destroy()
            self.playerbgFrame.destroy()
            self.npcbgFrame.destroy()
            self.world.enableMovement(self.world.hero);
         
            if self.syncedWithConvoMgr:
                self.syncedWithConvoMgr = False

    def playConvoSound(self):
        #@Wesley: this is the method you want to implement.
        print("HALLO WORLD");
         
                                    
    #npc text display
    def npcchat(self,t,text_wrap):
        '''create a npc conversation list'''
        
        self.npcbgFrame = DirectFrame(image='./LEGameAssets/Textures/dialog_npc_tray.png',
                                      scale = (1.34, 1.0, 1.0),
                                      pos = (0.0,0.0,0.0),
                                      frameColor = (1,1,1,0))
        self.npcbgFrame.setTransparency(1);       
        #scroll text for NPC, t is the content of conversation,text_wrap is the length of each text line
        self.npcchatList = DirectScrolledList(           
            frameSize = (-1.2, 1.2, -0.40, -0.60),
            frameColor = (0,0,0,0),
            pos=(0.13,0,-0),
            numItemsVisible = 3,
        
            itemFrame_pos = (-1.28,0,-0.54),
            forceHeight = 0.065,
            
        
            incButton_pos= (1.13,0,-0.68),
            incButton_scale= (0.3,1,0.3),
            
            itemsAlign=TextNode.ALeft,
        
            decButton_pos= (1.13,0,-0.51),
            decButton_scale= (0.3,1,0.3),
            )
        self.npcchatList.incButton['image'] = ("./LEGameAssets/Textures/journal_scrollbutton_down.png")
        self.npcchatList.incButton['relief'] = None
        self.npcchatList.incButton["image_scale"]=(0.2,1,0.2)
        self.npcchatList.decButton['image'] = ("./LEGameAssets/Textures/journal_scrollbutton_up.png")
        self.npcchatList.decButton['relief'] = None
        self.npcchatList.decButton["image_scale"]=(0.2,1,0.2) 
        self.npcchatList.incButton.setTransparency(1);
        self.npcchatList.decButton.setTransparency(1);
       
        self.npcbgFrame.reparentTo(self.myFrame)

        t_dedent=textwrap.dedent(t)
        
        t_wrap = textwrap.wrap(t,text_wrap)
        n=len(t_wrap)
 
        for i in range(n):
            item=DirectFrame(text = t_wrap[i],
                        text_align = 0,
                        text_scale = 0.04,
                        text_fg = (0.0,0.0,0.0,1.0),
                        relief = None)
            self.npcchatList.addItem(item)
   
        self.npcchatList.reparentTo(self.myFrame)
        
        if(n<=3):
            self.npcchatList.incButton.hide()
            self.npcchatList.decButton.hide()
        
        a = "NPC:"  #a is the name of NPC, which would be a return value from manager
        self.npcmessage = DirectLabel(
            text=a,
            pos=(-1.35,0,-0.54),
            text_bg=(1,0,0,0),
            text_fg=(0,0.8,0,1),
            frameColor=(0,0,0,0),
            scale=0.05)
        self.npcmessage.reparentTo(self.npcchatList)
        
    def playerchat(self,playChoices):
        '''create a player conversation list'''
        #a list of player's choices, playChoices is a list of player's choices, text_wrap is the length of each line
        self.playerbgFrame = DirectFrame(image='./LEGameAssets/Textures/dialog_player_tray.png',
                                      scale = (1.34, 1.0, 1.0),
                                      pos = (0.0,0.0,0.0),
                                      frameColor = (1,1,1,0))
        self.playerbgFrame.setTransparency(1);
        
        self.buttons=[]
        itemHeight=0.05
        itemNum=1
        text_wrap = 45

        for j in range(len(playChoices)):
            button=DirectButton(text = playChoices[j],
                                text_wordwrap=text_wrap,
                                command = self.setPlayerChoice,
                                extraArgs=[j],
                                relief=None,
                                text_align=0,
                                text_scale=0.04,
                                text_fg=(0.0,0.0,0.0,1.0),
                                )
            self.buttons.append(button)

            if itemHeight<button.getHeight():
               itemHeight=button.getHeight()

        itemHeight=itemHeight+0.02
        itemNum=int(round(0.2/itemHeight))
        
        
        for j in range(len(self.buttons)):
            self.buttons[j].bind(DGG.WITHIN,self.onrollover,extraArgs=[j])
            self.buttons[j].bind(DGG.WITHOUT,self.notonrollover, extraArgs=[j])
        
        self.radioButtonList = DirectScrolledList(
                frameSize = (-1.2, 1.2, -0.70, -0.94),
                frameColor = (0,0,0,0),
                pos=(-0.13,0,0),
                numItemsVisible = itemNum,

                itemFrame_pos = (-1,0,-0.8),
                forceHeight = itemHeight,
        
                incButton_pos= (1.3,0,-0.93),
                incButton_scale= (0.3,1,0.3),
        
                decButton_pos= (1.3,0,-0.77),
                decButton_scale= (0.3,1,0.3),
                )
        
        if(len(self.buttons)<=itemNum):
            self.radioButtonList.incButton.hide()
            self.radioButtonList.decButton.hide()
        self.radioButtonList.incButton['image'] = ("./LEGameAssets/Textures/journal_scrollbutton_down.png")
        self.radioButtonList.incButton["image_scale"]=(0.2,1,0.2)
        self.radioButtonList.incButton['relief'] = None
        self.radioButtonList.decButton['image'] = ("./LEGameAssets/Textures/journal_scrollbutton_up.png")
        self.radioButtonList.decButton["image_scale"]=(0.2,1,0.2)
        self.radioButtonList.decButton['relief'] = None 
        self.radioButtonList.incButton.setTransparency(1);
        self.radioButtonList.decButton.setTransparency(1);                                            
   
        for button in self.buttons:
            self.radioButtonList.addItem(button)
        self.playerbgFrame.reparentTo(self.myFrame)    
        self.radioButtonList.reparentTo(self.myFrame)
        

        a = "Player:"  #a is the name of player, which would be a return value from manager
        self.playermessage = DirectLabel(
            text=a,
            pos=(-1.09,0,-0.8),
            text_bg=(1,0,0,0),
            text_fg=(0,0,1,1),
            frameColor=(0,0,0,0),
            scale=0.05)
        self.playermessage.reparentTo(self.radioButtonList)
        
    
    def setPlayerChoice(self,n):
        #[antonjs] temp
        Debug.debug(__name__,'setPlayerChoice called')
        
        '''pass the player's choice to ConversationMgr'''
        self.world.conversationMgr.playResponse(n)
        
        self.syncedWithConvoMgr = False
    
    def noPlayerchat(self): 
        '''if there is no player conversation but only npc conversation, show continue'''
        self.noplayerchat = DirectFrame(image='./LEGameAssets/Textures/dialog_player_tray.png',
                                      scale = (1.34, 1.0, 1.0),
                                      pos = (0.0,0.0,0.0),
                                      frameColor = (1,1,1,0)) 
        self.noplayerchat.setTransparency(1);
        self.noplayerchat.reparentTo(self.myFrame)
        a = "Player:"  #a is the name of player, which would be a return value from manager
        self.playermessage = DirectLabel(
            text=a,
            pos=(-1.22,0,-0.8),
            text_bg=(1,0,0,0),
            text_fg=(0,0,1,1),
            frameColor=(0,0,0,0),
            scale=0.05)
        self.playermessage.reparentTo(self.myFrame)
        self.continuebutton = DirectButton(text ="Continue",
                                           text_fg=(0,0,0,1),
                                           relief = None,
                                           text_scale=0.05,
                                           command = self.destroyall,
                                           pos = (0,0,-0.85))
        self.continuebutton.reparentTo(self.myFrame)
        self.continuebutton.bind(DGG.WITHIN,self.onrollovercontinue)
        self.continuebutton.bind(DGG.WITHOUT,self.notonrollovercontinue)
    
    def destroyall(self):#destroy all the list
        # close the conversation
        self.world.conversationMgr.closeConversation()
        
        self.npcchatList.destroy()
        self.radioButtonList.destroy()
        self.playerbgFrame.destroy()
        self.npcbgFrame.destroy()
        self.noplayerchat.destroy()
        self.playermessage.destroy()
        self.continuebutton.destroy()
        self.showotherUI()
    
    def onrollover(self,j,position):
        #when mouse roll over the choices, change the size and color of text
        self.buttons[j]['text_fg'] = (0,0.2,1,1)
        self.buttons[j]['text_scale'] = 0.042
    
    def notonrollover(self,j,position):
        #when mouse roll away from the choices, change back the size and color of text
        self.buttons[j]['text_fg'] = (0.0,0.0,0.0,1.0)
        self.buttons[j]['text_scale'] = 0.04   
    
    def onrollovercontinue(self,position):
        self.continuebutton['text_fg'] = (0,0.2,1,1)
        self.continuebutton['text_scale'] = 0.052
    
    def notonrollovercontinue(self,position):
        self.continuebutton['text_fg'] = (0,0,0,1.0)
        self.continuebutton['text_scale'] = 0.05 
        
    def hideotherUI(self): 
        #self.world.gameplayUI.lifebarUI.hide()
        self.world.gameplayUI.journalUI.hideAll()
        #self.world.gameplayUI.offensiveSpellUI.hideAll()
        #self.world.gameplayUI.modifierSporeUI.hideAll()
        #self.world.gameplayUI.defensiveSpellUI.hideAll()
        #pass
    
    def showotherUI(self):
        #self.world.gameplayUI.lifebarUI.show()
        self.world.gameplayUI.journalUI.showAll()
        #self.world.gameplayUI.offensiveSpellUI.showAll()
        #self.world.gameplayUI.modifierSporeUI.showAll()
        #self.world.gameplayUI.defensiveSpellUI.showAll()
        
    def repositionUp(self):
        self.myFrame.setPos(0,0,1.45)
        
    def repositionDown(self):
        self.myFrame.setPos(0,0,0)
 