from direct.gui.DirectGui import *
from pandac.PandaModules import *

from UIBase import *

#import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage


class LifebarUI(UIBase):
    def __init__(self,world):
        UIBase.__init__(self,world)

        
        #self.mainChar = world.hero
        
        self.liferoundImage = DirectFrame(image='./LEGameAssets/Textures/health_tray.png',
                                            pos = (1.34,0,-1), scale = (1.34,1,1),
                                            frameColor = (1,1,1,0))
        self.lifebarImage = OnscreenImage(image='./LEGameAssets/Textures/lifebar.png', 
                                          pos = (0.285,0,-0.125),scale=(0.215, 1, 0.026))
        self.liferoundImage.setTransparency(1)
        
        self.liferoundImage.reparentTo(base.a2dTopLeft)
        self.lifebarImage.reparentTo(base.a2dTopLeft)
        self.entirelife = self.world.hero.getMaxHealth()
        #self.accept("a", self.update)
        #self.accept("s", self.reset)
        #self.update()
        
    def update(self):    
        self.life = self.world.hero.getHealth()
        self.lifebarupdate(self.entirelife, self.life)
        #self.accept("a", self.lifebarupdate)
        #self.accept("s", self.hide)
        #self.accept("d", self.show)
       # print "lifebar"
       #pass
        
    def lifebarupdate(self, entirelife, life):
        #entirelife = 100
        #self.life = self.life-10
        if life>0:
            self.lifebarImage['scale'] = (float(life)/entirelife*0.215,1,0.026)
            self.lifebarImage['pos'] = (0.285-(1-float(life)/entirelife)*0.215,0,-0.125)
        else:
            self.lifebarImage.hide()
    
    def reset(self):
        self.life = self.world.hero.getMaxHealth()
        self.lifebarImage['scale'] = (0.215, 1, 0.026)
        self.lifebarImage['pos'] = (0.285,0,-0.125)
        self.lifebarImage.show()
        
    def hide(self):
        self.liferoundImage.hide()
        self.lifebarImage.hide()
        
    def show(self):
        self.liferoundImage.show()
        self.lifebarImage.show()
        
#w = LifebarUI()
#run()