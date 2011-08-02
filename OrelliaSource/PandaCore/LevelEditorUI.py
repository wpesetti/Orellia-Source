from LevelEditorUIBase import *

class LevelEditorUI(LevelEditorUIBase):
    """ Class for Panda3D LevelEditor """ 
    appversion      = '0.1'
    appname         = 'Pandamonium Storyteller'
    
    def __init__(self, editor):
        LevelEditorUIBase.__init__(self, editor)
