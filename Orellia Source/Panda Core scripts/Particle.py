'''
Created on Apr 19, 2011

@author: qiaosic
'''

from panda3d.physics import BaseParticleEmitter,BaseParticleRenderer
from panda3d.physics import PointParticleFactory,SpriteParticleRenderer
from panda3d.physics import LinearNoiseForce,DiscEmitter
from panda3d.core import TextNode
from panda3d.core import AmbientLight,DirectionalLight
from panda3d.core import Point3,Vec3,Vec4
from panda3d.core import Filename
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.showbase.DirectObject import DirectObject

from pandac.PandaModules import *


class Particle():
    
    def __init__(self,file,name=None, pos=(0.0,0.0,0.0),scale=(1.0,1.0,1.0)):
        

        self.particleEffect = None
        self.configFile = file
        self.name = name
        self.position = pos
        self.scale = scale
        
        self.particleEffect = ParticleEffect(name)
        self.particleEffect.loadConfig(Filename(file))        

        self.particleEffect.setPos(pos[0], pos[1], pos[2])
        self.particleEffect.setScale(scale[0],scale[1],scale[2])
        
        base.enableParticles()


    
    def encode(self,doc):
        node = doc.createElement("particle")
        
        configFilename = doc.createElement("configFilename")
        configFilename.appendChild(doc.createTextNode(self.configFile))
        node.appendChild(configFilename)
        
        #CONSIDER: What happens if the name was none
        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(self.name))
        node.appendChild(name)
        
        
        pos = doc.createElement("position")
        x_p = doc.createElement("x")
        x_p.appendChild(doc.createTextNode(str(self.position[0])))
        pos.appendChild(x_p)
        y_p = doc.createElement("y")
        y_p.appendChild(doc.createTextNode(str(self.position[1])))
        pos.appendChild(y_p)
        z_p = doc.createElement("z")
        z_p.appendChild(doc.createTextNode(str(self.position[2])))
        pos.appendChild(z_p)
        node.appendChild(pos)
        
        
        scale = doc.createElement("scale")
        x_s = doc.createElement("x")
        x_s.appendChild(doc.createTextNode(str(self.scale[0])))
        scale.appendChild(x_s)
        y_s = doc.createElement("y")
        y_s.appendChild(doc.createTextNode(str(self.scale[1])))
        scale.appendChild(y_s)
        z_s = doc.createElement("z")
        z_s.appendChild(doc.createTextNode(str(self.scale[2])))
        scale.appendChild(z_s)
        node.appendChild(scale)
        
        
        
        return node
    
    def decode(node):
        configFilename =None
        name =None
        pos = None
        scale = None
        x = 0
        y = 0
        z = 0 
        for n in node.childNodes:
            if n.localName == "configFilename":
                configFilename =  n.childNodes[0].data.strip()
            elif n.localName == "name":
                name =  n.childNodes[0].data.strip()
            elif n.localName == "position":
                for n1 in n.childNodes:
                    if n1.localName =="x":
                       x =  n1.childNodes[0].data.strip()
                    elif n1.localName =="y":
                       y =  n1.childNodes[0].data.strip()
                    elif n1.localName =="z":
                       z =  n1.childNodes[0].data.strip()
                    x = float(x)
                    y = float(y)
                    z = float(z)
                    pos = (x,y,z)
            elif n.localName == "scale":
                for n1 in n.childNodes:
                    if n1.localName =="x":
                       x =  n1.childNodes[0].data.strip()
                    elif n1.localName =="y":
                       y =  n1.childNodes[0].data.strip()
                    elif n1.localName =="z":
                       z =  n1.childNodes[0].data.strip()
                    x = float(x)
                    y = float(y)
                    z = float(z)
                    scale = (x,y,z)
                    
        return Particle(configFilename, name, pos,scale)
    
    decode = staticmethod(decode)            
                
        
class ParticleHolder():
    def __init__(self):

        self.particleEffectList = []       
        self.particleList = []
        
    def addParticleEffect(self, particleConfig, pos = (0.0,0.0,0.0), scale = (1.0,1.0,1.0)):
        
        #name = str(particleConfig)+'-%d'%len(self.particleEffectList)
        name = Filename(particleConfig).getBasenameWoExtension()+'-%d'%len(self.particleEffectList)


        particle = Particle(particleConfig,name, pos, scale)
        
        self.particleList.append(particle)
        self.particleEffectList.append(particle.particleEffect)
        self.showParticleEffectByIndex(len(self.particleEffectList)-1)
        

    def getParticlePositionByIndex(self, index):
        return self.particleEffectList[index].getPos()
        
    def getParticleScaleByIndex(self, index):
        return self.particleEffectList[index].getScale()
    
    
    
    def setParticlePositionByIndex(self, index, x, y, z):
        self.particleEffectList[index].setPos(x, y, z)
        self.particleList[index].position = (x,y,z)
        
        
    def setParticleScaleByIndex(self, index, x, y, z):
        self.particleEffectList[index].setScale(x, y, z)
        self.particleList[index].scale = (x,y,z)  
        #print "set scale to", x,y,z  
        
    def delParticleEffectByIndex(self, index):
        if self.particleEffectList != []:
            self.particleEffectList[index].cleanup()
            self.particleEffectList.pop(index)
            self.particleList.pop(index)

            
    def showParticleEffectByIndex(self, index):

        particles = self.getNodePath().attachNewNode('particleRenderParents')
        particles.setLightOff()
        particles.setTransparency(TransparencyAttrib.MAlpha)
        particles.setBin ('fixed', 0)
        particles.setDepthWrite (False)
        particles.setShaderOff()
                
        self.particleEffectList[index].start(self.getNodePath(),particles)    
         

         
    def encode(self, doc):
        pass
    
    
    def decode(self):
        pass 
            