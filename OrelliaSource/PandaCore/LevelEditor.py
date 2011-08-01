"""
This is just a sample code.

LevelEditor, ObjectHandler, ObjectPalette should be rewritten
to be game specific.
"""

from LevelEditorBase import *
from ObjectMgr import *
from SoundMgr import *
from JournalMgr import *
from InventoryMgr import *
from LevelEditorUI import *

class LevelEditor(LevelEditorBase):
    """ Class for Panda3D LevelEditor """ 
    def __init__(self):
        LevelEditorBase.__init__(self)

        # define your own config file similar to this
        self.settingsFile = os.path.dirname(__file__) + '/LevelEditor.cfg'

        self.objectMgr = ObjectMgr(self)
        self.soundMgr = SoundMgr(self)
        self.journalMgr = JournalMgr(self)
        self.inventoryMgr = InventoryMgr(self)

        # Populating uderlined data-structures
        self.ui = LevelEditorUI(self)
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))

        # When you define your own LevelEditor class inheriting LevelEditorBase
        # you should call self.initialize() at the end of __init__() function
        self.initialize()
        self.ui.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
