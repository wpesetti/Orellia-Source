## import wx
## import os
## from wx.lib.agw import fourwaysplitter as FWS

from pandac.PandaModules import *
from direct.wxwidgets.WxPandaShell import *
from direct.directtools.DirectSelection import SelectionRay
from direct.directtools.DirectGlobals import DIRECT_NO_MOD, DIRECT_SHIFT_MOD, DIRECT_CONTROL_MOD, DIRECT_ALT_MOD

from ObjectPropertyUI import *
from SceneGraphUI import *
from ScenesUI import *
from LayerEditorUI import *
from HotKeyUI import *
from ActionMgr import *
from SaveProjectUI import *
from ImportUI import *
from JournalDialog import *
from LEInventoryUI import *
from ConversationEditor import *
from LibraryUI import *
from SoundUI import *
from PrefsUI import *
from LibraryBrowserUI import *
from MergeProjectUI import *

from ExportOptionsDialog import *
import Library
import shutil
import random
import subprocess
from cStringIO import StringIO

class PandaTextDropTarget(wx.TextDropTarget):
    def __init__(self, editor, view):
        wx.TextDropTarget.__init__(self)
        self.editor = editor
        self.view = view
        
    def OnDropText(self, x, y, text):
        # create new object
        parentNPRef = [None]
        if not self.editor.propMeetsReq(text, parentNPRef):
            return
        # Get the libraryType and name
        ind = text.index(">")
        libraryType = text[0:ind]
        objectName = text[ind+1:len(text)]
        # Get the type,
        type = None
        # and the file path...
        asset = None
        # in case it is an actor with animations
        anims = {}
        # only if it is a mesh
        if libraryType == "Meshes":
            type = "Meshes"
            asset = base.le.lib.meshes[objectName]
        # if it is an actor
        elif libraryType == "Actors":
            type = libraryType
            asset = base.le.lib.actors[objectName]
            anims = asset.anims
        elif libraryType == "Textures":
            type = libraryType
            asset = base.le.lib.textures[objectName]
        elif libraryType == "Terrains":
            type = libraryType
            asset = base.le.lib.terrains[objectName]
        # Otherwise, if the libraryType is a PandaObject
        elif libraryType == "PandaObject":
            # The object type is the object name
            type = objectName
            objectName = objectName

        # change window coordinate to mouse coordinate
        mx = 2 * (x/float(self.view.ClientSize.GetWidth()) - 0.5)
        my = -2 * (y/float(self.view.ClientSize.GetHeight()) - 0.5)

        # create ray from the camera to detect 3d position
        iRay = SelectionRay(self.view.camera)
        iRay.collider.setFromLens(self.view.camNode, mx, my)
        hitPt = None

        iRay.collideWithBitMask(BitMask32.bit(21))
        iRay.ct.traverse(self.view.collPlane)
        if iRay.getNumEntries() > 0:
            entry = iRay.getEntry(0)
            hitPt = entry.getSurfacePoint(entry.getFromNodePath())
        pos = None
        if hitPt:
            # create a temp nodePath to get the position
            np = NodePath('temp')
            np.setPos(self.view.camera, hitPt)

            if base.direct.manipulationControl.fGridSnap:
                snappedPos = self.view.grid.computeSnapPoint(np.getPos())
                np.setPos(snappedPos)
            
            pos = np.getPos()
            np.remove()
            
        iRay.collisionNodePath.removeNode()
        del iRay
        if type:
            # Set the action
            action = ActionAddNewObj(self.editor, type, name = objectName + ':1', asset=asset, anims=anims, parent=parentNPRef[0], pos=pos)
            self.editor.actionMgr.push(action)
            newobj = action()

ID_NEW = 101
ID_OPEN = 102
ID_SAVE = 103
ID_SAVE_AS = 104
ID_IMPORT = 105
ID_EXPORT = 106
ID_MERGE = 107
#ID_BVW_EXPORT = 108
ID_GAME_EXPORT = 115 # CONSIDER: pick different value
ID_GAME_EXPORT_RUN = 116
ID_IMPORT_EXTERNAL_LIB = 109
ID_EXPORT_LIBRARY = 110
ID_BROWSE_LIB = 111
ID_BROWSE_DEFAULT_LIB = 112

ID_DUPLICATE = 201
ID_MAKE_LIVE = 202
ID_UNDO = 203
ID_REDO = 204
ID_DROP_TO_GROUND = 205

ID_SHOW_GRID = 301
ID_GRID_SIZE = 302

ID_SHOW_COLLIDERS = 304
ID_HOT_KEYS = 305
ID_PARENT_TO_SELECTED = 306
ID_UNIQUE_NAMES = 307
ID_PREFERENCES = 308
ID_SCENE_STATS = 309
ID_SELECTED_OBJECT_STATS = 310

ID_TRANSLATE_MODE = 501
ID_ROTATE_MODE = 502
ID_SCALE_MODE = 503
ID_LOCAL_MODE = 504
ID_WORLD_MODE = 505

ID_SHOW_JOURNAL = 601
ID_CONVO_EDITOR = 602
ID_INVENTORY = 603



class LevelEditorUIBase(WxPandaShell):
    """ Class for Panda3D LevelEditor """ 
    def __init__(self, editor):
        self.MENU_TEXTS.update({
            ID_NEW : ("New", "LE-NewScene"),
            ID_OPEN : ("Open...", "LE-OpenScene"),
            ID_SAVE : ("Save", "LE-SaveScene"),
            ID_SAVE_AS : ("Save As...", None),
            ID_IMPORT : ("Import Asset...", "LE-Import"),
            ID_IMPORT_EXTERNAL_LIB : ("Import External Library...", None),
            ID_EXPORT : ("Export Preview...", None),
            #ID_BVW_EXPORT : ("Export Standalone...", None),
            ID_GAME_EXPORT : ("Export World...", None),
            ID_GAME_EXPORT_RUN:("Export World and Run...", None),
            ID_EXPORT_LIBRARY : ("Export Library...", None),
            ID_BROWSE_LIB : ("Browse External Library...", None),
            ID_BROWSE_DEFAULT_LIB : ("Browse Default Library...", None),
            ID_MERGE : ("Merge...", None),
            wx.ID_EXIT : ("Quit", "LE-Quit"),
            ID_DUPLICATE : ("Duplicate", "LE-Duplicate"),
            ID_UNDO : ("Undo", "LE-Undo"),
            ID_REDO : ("Redo", "LE-Redo"),
            ID_DROP_TO_GROUND : ("Drop Selected To Ground", "LE-DropToGround"),
            ID_SHOW_GRID : ("Show Grid", None),
            ID_GRID_SIZE : ("Grid Size...", None),
            ID_SHOW_COLLIDERS : ("Show Colliders", None),
            ID_HOT_KEYS : ("Hot Keys...", None),
            ID_PARENT_TO_SELECTED : ("Parent To Selected", None),
            ID_UNIQUE_NAMES : ("Prepend Username to Names", None),
            ID_PREFERENCES : ("Editor Preferences...", None),
            ID_SCENE_STATS : ("Scene Stats...", None),
            ID_SELECTED_OBJECT_STATS : ("Selected Object Stats...", None),
            ID_TRANSLATE_MODE : ("Translate", "LE-translateMode"),
            ID_ROTATE_MODE : ("Rotate", "LE-rotateMode"),
            ID_SCALE_MODE : ("Scale", "LE-scaleMode"),
            ID_LOCAL_MODE : ("Local Space", "LE-localMode"),
            ID_WORLD_MODE : ("World Space", "LE-worldMode"),
            ID_SHOW_JOURNAL :("Show Journal", None),
            ID_CONVO_EDITOR :("Conversation Editor", None),
            ID_INVENTORY :("Show Inventory Map", None),
            })

        self.editor = editor
        WxPandaShell.__init__(self, fStartDirect=True)        
        self.contextMenu = ViewportMenu()
        self.bindKeyEvents(True)
        
        #prevent craziness with the splitter windows
        for x in (self.baseFrame, self.mainFrame, self.rightFrame, self.leftFrame):
            x.Bind(wx.EVT_SPLITTER_DCLICK, self.onDoubleClick)
            x.SetMinimumPaneSize(50)
            x.SetBorderSize(10)
                  
        self.viewFrame.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.onViewFrameChange)
        
        self.SetSize(wx.Size(1280,720))
        self.Maximize()
        
        
        self.leftBarUpPane.SetWindowStyleFlag(wx.wx.SUNKEN_BORDER)
        self.leftBarDownPane.SetWindowStyleFlag(wx.wx.SUNKEN_BORDER)
        self.rightBarUpPane.SetWindowStyleFlag(wx.wx.SUNKEN_BORDER)
        self.rightBarDownPane.SetWindowStyleFlag(wx.wx.SUNKEN_BORDER)
        
        self.mainFrame.SetSashPosition(250)
        self.baseFrame.SetSashPosition(self.baseFrame.GetSize()[0] - 250)
        self.rightFrame.SetSashPosition(self.rightFrame.GetSize()[1] -250)
        self.rightFrame.SetSashGravity(1)
        
        taskMgr.add(self.mouseTask, 'mouseTask')
        self.inPandaWindow = False
        self.leftMouseWasDown = False
        self.middleMouseWasDown = False
        self.rightMouseWasDown = False
                  
    #Overridden from wxAppShell
    def quit(self, event=None):
        if self.onDestroy(event):
            # to close Panda
            try:
                base
            except NameError:
                sys.exit()

            base.userExit()
   
    #overridden from wxAppShell
    def _WxAppShell__createAboutBox(self):
        aboutString = "Panda3D Level Editor\n\n" +\
                      "Version %.2f"%Util.VERSION_NUMBER + "\n\n"+\
                      "Developed by\n\n"+\
                      "Gyedo Jeon\n"+\
                      "Dan Pike\n"+\
                      "Craig Wells\n"+\
                      "Kent Vasko\n"+\
                      "Tatyana Koutepova\n"+\
                      "Andrew Gartner\n"+\
                      "Ayse Zeynep Tasar\n"+\
                      "Jue Wang\n"+\
                      "Qiaosi Chen\n"+\
                      "Thomas Luong\n"+\
                      "Anton Strenger\n"+\
                      "Russell Mester"
                      
        self.about = wx.MessageDialog(None, aboutString, "About Panda3D Level Editor",
                     wx.OK | wx.ICON_INFORMATION)
   
    def onDoubleClick(self, evt=None):
        evt.Veto()
    
    # detects when the mouse enters and leaves the panda window so we don't get caught thinking
    # the mouse or some key is held down when it isn't
    def mouseTask(self, task):
    
        mouseState = wx.GetMouseState()
        mousePoint = wx.Point(mouseState.GetX(), mouseState.GetY())
        viewports = (self.topView, self.leftView, self.frontView, self.perspView)
        
        inPandaWindow = False
               
        for x in viewports:
            if x.IsShownOnScreen():
                if x.GetScreenRect().Inside(mousePoint):
                    inPandaWindow = True

        if inPandaWindow and not self.inPandaWindow:
            self.onEnterPandaWindow()
        elif not inPandaWindow and self.inPandaWindow:
            self.onLeavePandaWindow()
                    
        self.inPandaWindow = inPandaWindow
        
        return task.cont
        
    def onEnterPandaWindow(self):
        base.direct.fAlt = int(wx.GetKeyState(wx.WXK_ALT))
        base.direct.fControl = int(wx.GetKeyState(wx.WXK_CONTROL))
        base.direct.fShift = int(wx.GetKeyState(wx.WXK_SHIFT))

        modifiers = DIRECT_NO_MOD
        ms = wx.GetMouseState()
        if ms.AltDown():
            modifiers |= DIRECT_ALT_MOD
        if ms.ShiftDown():
           modifiers |= DIRECT_SHIFT_MOD
        if ms.ControlDown():
            modifiers |= DIRECT_CONTROL_MOD
        if ms.LeftDown() and self.leftMouseWasDown:
            messenger.send('DIRECT-mouse1', sentArgs=[modifiers])
        if ms.MiddleDown() and self.middleMouseWasDown:
            messenger.send('DIRECT-mouse2', sentArgs=[modifiers])
        if ms.RightDown() and self.rightMouseWasDown:
            messenger.send('DIRECT-mouse3', sentArgs=[modifiers])
        
        
    def onLeavePandaWindow(self):
        base.direct.fAlt = int(wx.GetKeyState(wx.WXK_ALT))
        base.direct.fControl = int(wx.GetKeyState(wx.WXK_CONTROL))
        base.direct.fShift = int(wx.GetKeyState(wx.WXK_SHIFT))
        if base.direct.fMouse1:
            self.leftMouseWasDown = True
            messenger.send('DIRECT-mouse1Up')
        else:
            self.leftMouseWasDown = False
        if base.direct.fMouse2:
            messenger.send('DIRECT-mouse2Up')
            self.middleMouseWasDown = True
        else:
            self.middleMouseWasDown = False
        if base.direct.fMouse3:
            messenger.send('DIRECT-mouse3Up')
            self.rightMouseWasDown = True
        else:
            self.rightMouseWasDown = False
        
        
    def onViewFrameChange(self, evt=None):
        if evt.GetSashPosition()[0] < 50:
            evt.Veto()
        elif evt.GetSashPosition()[1] < 50:
            evt.Veto()
        elif self.viewFrame.GetSize()[0] - evt.GetSashPosition()[0] < 50:
            evt.Veto()
        elif self.viewFrame.GetSize()[1] - evt.GetSashPosition()[1] <50:
            evt.Veto()
    
    #binds or unbinds hotkeys to free them up for use in the ui
    def bindKeyEvents(self, toBind=True):
        if toBind:
            self.wxApp.Bind(wx.EVT_CHAR, self.onKeyEvent)
            self.wxApp.Bind(wx.EVT_KEY_DOWN, self.onKeyDownEvent)
            self.wxApp.Bind(wx.EVT_KEY_UP, self.onKeyUpEvent)
        else:
            self.wxApp.Unbind(wx.EVT_CHAR)
            self.wxApp.Unbind(wx.EVT_KEY_DOWN)
            self.wxApp.Unbind(wx.EVT_KEY_UP)

    def createMenu(self):
        menuItem = self.menuFile.Insert(0, ID_NEW, self.MENU_TEXTS[ID_NEW][0])
        self.Bind(wx.EVT_MENU, self.onNew, menuItem)
        
        menuItem = self.menuFile.Insert(1, ID_OPEN, self.MENU_TEXTS[ID_OPEN][0])
        self.Bind(wx.EVT_MENU, self.onOpen, menuItem)

        menuItem = self.menuFile.Insert(2, ID_SAVE, self.MENU_TEXTS[ID_SAVE][0])
        self.Bind(wx.EVT_MENU, self.onSave, menuItem)

        menuItem = self.menuFile.Insert(3, ID_SAVE_AS, self.MENU_TEXTS[ID_SAVE_AS][0])
        self.Bind(wx.EVT_MENU, self.onSaveAs, menuItem)
        
        menuItem = self.menuFile.Insert(4, ID_MERGE, self.MENU_TEXTS[ID_MERGE][0])
        self.Bind(wx.EVT_MENU, self.onMerge, menuItem)
        
        self.menuFile.InsertSeparator(5)
        
        menuItem = self.menuFile.Insert(6, ID_IMPORT, self.MENU_TEXTS[ID_IMPORT][0])
        self.Bind(wx.EVT_MENU, self.onImport, menuItem)
        
        menuItem = self.menuFile.Insert(7, ID_BROWSE_LIB, self.MENU_TEXTS[ID_BROWSE_LIB][0])
        self.Bind(wx.EVT_MENU, self.onBrowseLib, menuItem)
        
        menuItem = self.menuFile.Insert(8, ID_BROWSE_DEFAULT_LIB, self.MENU_TEXTS[ID_BROWSE_DEFAULT_LIB][0])
        self.Bind(wx.EVT_MENU, self.onBrowseDefaultLib, menuItem)
        
        menuItem = self.menuFile.Insert(9, ID_IMPORT_EXTERNAL_LIB, self.MENU_TEXTS[ID_IMPORT_EXTERNAL_LIB][0])
        self.Bind(wx.EVT_MENU, self.onImportLib, menuItem)
        
        menuItem = self.menuFile.Insert(10, ID_EXPORT_LIBRARY, self.MENU_TEXTS[ID_EXPORT_LIBRARY][0])
        self.Bind(wx.EVT_MENU, self.onExportLib, menuItem)
        
        self.menuFile.InsertSeparator(11)
        
        menuItem = self.menuFile.Insert(12, ID_EXPORT, self.MENU_TEXTS[ID_EXPORT][0])
        self.Bind(wx.EVT_MENU, self.onExport, menuItem)
        
        #menuItem = self.menuFile.Insert(13, ID_BVW_EXPORT, self.MENU_TEXTS[ID_BVW_EXPORT][0])
        #self.Bind(wx.EVT_MENU, self.onBVWExport, menuItem)
        
        menuItem = self.menuFile.Insert(13, ID_GAME_EXPORT, self.MENU_TEXTS[ID_GAME_EXPORT][0])
        self.Bind(wx.EVT_MENU, self.onGameExport, menuItem)
        
        menuItem = self.menuFile.Insert(14, ID_GAME_EXPORT_RUN, self.MENU_TEXTS[ID_GAME_EXPORT_RUN][0])
        self.Bind(wx.EVT_MENU, self.onGameExportRun, menuItem)
        
        self.menuFile.InsertSeparator(15)
        
        self.menuEdit = wx.Menu()
        self.menuBar.Insert(1, self.menuEdit, "&Edit")

        menuItem = self.menuEdit.Append(ID_UNDO, self.MENU_TEXTS[ID_UNDO][0])
        self.Bind(wx.EVT_MENU, self.editor.actionMgr.undo, menuItem)

        menuItem = self.menuEdit.Append(ID_REDO, self.MENU_TEXTS[ID_REDO][0])
        self.Bind(wx.EVT_MENU, self.editor.actionMgr.redo, menuItem)
        
        menuItem = self.menuEdit.Append(ID_DUPLICATE, self.MENU_TEXTS[ID_DUPLICATE][0])
        self.Bind(wx.EVT_MENU, self.onDuplicate, menuItem)
        
        menuItem = self.menuEdit.Append(ID_DROP_TO_GROUND, self.MENU_TEXTS[ID_DROP_TO_GROUND][0])
        self.Bind(wx.EVT_MENU, self.editor.onDropToGround, menuItem)

        self.menuManip = wx.Menu()
        self.menuBar.Insert(2, self.menuManip, "&Manip")
        
        self.translateMenuItem = self.menuManip.AppendRadioItem(ID_TRANSLATE_MODE, self.MENU_TEXTS[ID_TRANSLATE_MODE][0])
        self.Bind(wx.EVT_MENU, self.editor.translateMode, self.translateMenuItem)
        
        self.rotateMenuItem = self.menuManip.AppendRadioItem(ID_ROTATE_MODE, self.MENU_TEXTS[ID_ROTATE_MODE][0])
        self.Bind(wx.EVT_MENU, self.editor.rotateMode, self.rotateMenuItem)        
        
        self.scaleMenuItem = self.menuManip.AppendRadioItem(ID_SCALE_MODE, self.MENU_TEXTS[ID_SCALE_MODE][0])
        self.Bind(wx.EVT_MENU, self.editor.scaleMode, self.scaleMenuItem)
        
        self.menuManip.AppendSeparator()
        
        self.localMenuItem = self.menuManip.AppendRadioItem(ID_LOCAL_MODE, self.MENU_TEXTS[ID_LOCAL_MODE][0])
        self.Bind(wx.EVT_MENU, self.editor.localMode, self.localMenuItem)
        
        self.worldMenuItem = self.menuManip.AppendRadioItem(ID_WORLD_MODE, self.MENU_TEXTS[ID_WORLD_MODE][0])
        self.Bind(wx.EVT_MENU, self.editor.worldMode, self.worldMenuItem)
        
        self.menuOptions = wx.Menu()
        self.menuBar.Insert(3, self.menuOptions, "&Options")

        self.showGridMenuItem = self.menuOptions.Append(ID_SHOW_GRID, self.MENU_TEXTS[ID_SHOW_GRID][0], kind = wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggleGrid, self.showGridMenuItem)

        self.gridSizeMenuItem = self.menuOptions.Append(ID_GRID_SIZE, self.MENU_TEXTS[ID_GRID_SIZE][0])
        self.Bind(wx.EVT_MENU, self.onGridSize, self.gridSizeMenuItem)
        
        self.showCollidersMenuItem = self.menuOptions.Append(ID_SHOW_COLLIDERS, self.MENU_TEXTS[ID_SHOW_COLLIDERS][0], kind = wx.ITEM_CHECK)
        self.showCollidersMenuItem.Check(True)
        self.Bind(wx.EVT_MENU, self.onShowColliders, self.showCollidersMenuItem)

        #self.parentToSelectedMenuItem = self.menuOptions.Append(ID_PARENT_TO_SELECTED, self.MENU_TEXTS[ID_PARENT_TO_SELECTED][0], kind = wx.ITEM_CHECK)
        self.preferencesItem = self.menuOptions.Append(ID_PREFERENCES, self.MENU_TEXTS[ID_PREFERENCES][0])
        self.Bind(wx.EVT_MENU, self.onPreferences, self.preferencesItem)
        self.hotKeysMenuItem = self.menuOptions.Append(ID_HOT_KEYS, self.MENU_TEXTS[ID_HOT_KEYS][0])
        self.Bind(wx.EVT_MENU, self.onHotKeys, self.hotKeysMenuItem)
        
        self.sceneStatsMenuItem = self.menuOptions.Append(ID_SCENE_STATS, self.MENU_TEXTS[ID_SCENE_STATS][0])
        self.Bind(wx.EVT_MENU, self.onSceneStats, self.sceneStatsMenuItem)

        self.objectStatsMenuItem = self.menuOptions.Append(ID_SELECTED_OBJECT_STATS, self.MENU_TEXTS[ID_SELECTED_OBJECT_STATS][0])
        self.Bind(wx.EVT_MENU, self.onSelectedObjectStats, self.objectStatsMenuItem)
        
        WxPandaShell.createMenu(self)
        
        self.menuGame = wx.Menu()
        self.menuBar.Append(self.menuGame, "&Game")
        self.showJournalItem = self.menuGame.Append(ID_SHOW_JOURNAL, self.MENU_TEXTS[ID_SHOW_JOURNAL][0])
        self.Bind(wx.EVT_MENU, self.onShowJournal, self.showJournalItem)
        self.conversationEditorItem = self.menuGame.Append(ID_CONVO_EDITOR, self.MENU_TEXTS[ID_CONVO_EDITOR][0])
        self.Bind(wx.EVT_MENU, self.onConversationEditor, self.conversationEditorItem)
        self.inventoryItem = self.menuGame.Append(ID_INVENTORY, self.MENU_TEXTS[ID_INVENTORY][0])
        self.Bind(wx.EVT_MENU, self.onInventory, self.inventoryItem)
        
        #self.menuGame.AppendRadioItem()
        
        
    def updateMenu(self):
        hotKeyDict = {}
        for hotKey in base.direct.hotKeyMap.keys():
            desc = base.direct.hotKeyMap[hotKey]
            hotKeyDict[desc[1]] = hotKey
            
        for id in self.MENU_TEXTS.keys():
            desc = self.MENU_TEXTS[id]
            if desc[1]:
                menuItem = self.menuBar.FindItemById(id)
                hotKey = hotKeyDict.get(desc[1]).replace('control', 'ctrl')
                if hotKey:
                    menuItem.SetText(desc[0] + "\t%s"%hotKey)
    
    def createInterface(self):
        WxPandaShell.createInterface(self)
        
        self.leftBarUpNB = wx.Notebook(self.leftBarUpPane, style=wx.NB_BOTTOM)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.leftBarUpNB, 1, wx.EXPAND)
        self.leftBarUpPane.SetSizer(sizer)
        self.libraryUI = LibraryUI(self.leftBarUpNB,-1, self.editor)
        self.leftBarUpNB.AddPage(self.libraryUI, 'Library')
        self.pandaObjUI = PandaObjUI(self.leftBarUpNB, -1)
        self.leftBarUpNB.AddPage(self.pandaObjUI, 'Panda Objects')
        self.storyObjUI = StoryObjUI(self.leftBarUpNB, -1, self.editor)
        self.leftBarUpNB.AddPage(self.storyObjUI, 'Story Objects')
        

        self.leftBarDownNB = wx.Notebook(self.leftBarDownPane)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.leftBarDownNB, 1, wx.EXPAND)
        self.leftBarDownPane.SetSizer(sizer)
        self.leftBarDownPane0 = wx.Panel(self.leftBarDownNB, -1)
        self.leftBarDownNB.AddPage(self.leftBarDownPane0, 'Scene Graph')
        self.leftBarDownPane1 = wx.Panel(self.leftBarDownNB, -1)
        self.leftBarDownNB.AddPage(self.leftBarDownPane1, 'Scene List')
        self.soundUI = SoundUI(self.leftBarDownNB, -1, self.editor)
        self.leftBarDownNB.AddPage(self.soundUI, 'Sound List')
        

        self.rightBarDownNB = wx.Notebook(self.rightBarDownPane)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rightBarDownNB, 1, wx.EXPAND)
        self.rightBarDownPane.SetSizer(sizer)
        self.rightBarDownPane0 = wx.Panel(self.rightBarDownNB, -1)
        self.rightBarDownNB.AddPage(self.rightBarDownPane0, 'Layers')

        self.topView.SetDropTarget(PandaTextDropTarget(self.editor, self.topView))
        self.frontView.SetDropTarget(PandaTextDropTarget(self.editor, self.frontView))
        self.leftView.SetDropTarget(PandaTextDropTarget(self.editor, self.leftView))
        self.perspView.SetDropTarget(PandaTextDropTarget(self.editor, self.perspView))

        self.rightBarDownPane.Layout()
        self.Layout()
        self.baseFrame.SplitVertically(self.viewFrame, self.rightFrame, 500)
        self.objectPropertyUI = ObjectPropertyUI(self.rightBarUpPane, self.editor)
        self.sceneGraphUI = SceneGraphUI(self.leftBarDownPane0, self.editor)
        self.scenesUI = ScenesUI(self.leftBarDownPane1, self.editor)
        self.layerEditorUI = LayerEditorUI(self.rightBarDownPane0, self.editor)

        self.showGridMenuItem.Check(True)
    
    def onRightDown(self, evt=None):
        """Invoked when the viewport is right-clicked."""
        if evt == None:
            mpos = wx.GetMouseState()
            mpos = self.ScreenToClient((mpos.x, mpos.y))
        else:
            mpos = evt.GetPosition()

        base.direct.fMouse3 = 0
        #self.PopupMenu(self.contextMenu, mpos)

    def onKeyDownEvent(self, evt):
        if evt.GetKeyCode() == wx.WXK_ALT:
            base.direct.fAlt = 1
        elif evt.GetKeyCode() == wx.WXK_CONTROL:
            base.direct.fControl = 1
        elif evt.GetKeyCode() == wx.WXK_SHIFT:
            base.direct.fShift = 1
        elif evt.GetKeyCode() == wx.WXK_UP:
            messenger.send('arrow_up')
        elif evt.GetKeyCode() == wx.WXK_DOWN:
            messenger.send('arrow_down')
        elif evt.GetKeyCode() == wx.WXK_LEFT:
            messenger.send('arrow_left')
        elif evt.GetKeyCode() == wx.WXK_RIGHT:
            messenger.send('arrow_right')
        elif evt.GetKeyCode() == wx.WXK_PAGEUP:
            messenger.send('page_up')
        elif evt.GetKeyCode() == wx.WXK_PAGEDOWN:
            messenger.send('page_down')
        else:
            evt.Skip()

    def onKeyUpEvent(self, evt):
        if evt.GetKeyCode() == wx.WXK_ALT:
            base.direct.fAlt = 0
        elif evt.GetKeyCode() == wx.WXK_CONTROL:
            base.direct.fControl = 0
        elif evt.GetKeyCode() == wx.WXK_SHIFT:
            base.direct.fShift = 0
        elif evt.GetKeyCode() == wx.WXK_UP:
            messenger.send('arrow_up-up')
        elif evt.GetKeyCode() == wx.WXK_DOWN:
            messenger.send('arrow_down-up')
        elif evt.GetKeyCode() == wx.WXK_LEFT:
            messenger.send('arrow_left-up')
        elif evt.GetKeyCode() == wx.WXK_RIGHT:
            messenger.send('arrow_right-up')
        elif evt.GetKeyCode() == wx.WXK_PAGEUP:
            messenger.send('page_up-up')
        elif evt.GetKeyCode() == wx.WXK_PAGEDOWN:
            messenger.send('page_down-up')
        else:
            evt.Skip()
        
    def onKeyEvent(self, evt):
        input = ''
        if evt.GetKeyCode() in range(97, 123): # for keys from a to z
            if evt.GetModifiers() == 4: # when shift is pressed while caps lock is on
                input = 'shift-%s'%chr(evt.GetKeyCode())
            else:
                input = chr(evt.GetKeyCode())
        elif evt.GetKeyCode() in range(65, 91):
            if evt.GetModifiers() == 4: # when shift is pressed
                input = 'shift-%s'%chr(evt.GetKeyCode() + 32)
            else:
                input = chr(evt.GetKeyCode() + 32)
        elif evt.GetKeyCode() in range(1, 27): # for keys from a to z with control
            if evt.GetModifiers() == 2:
                input = 'control-%s'%chr(evt.GetKeyCode()+96)
        elif evt.GetKeyCode() == wx.WXK_DELETE:
            input = 'delete'
        elif evt.GetKeyCode() == wx.WXK_ESCAPE:
            input = 'escape'
        else:
            if evt.GetModifiers() == 4:
                input = 'shift-%s'%chr(evt.GetKeyCode())
            elif evt.GetModifiers() == 2:
                input = 'control-%s'%chr(evt.GetKeyCode())
            elif evt.GetKeyCode() < 256:
                input = chr(evt.GetKeyCode())
        if input in base.direct.hotKeyMap.keys():
            keyDesc = base.direct.hotKeyMap[input]
            messenger.send(keyDesc[1])

    def reset(self):
        self.sceneGraphUI.reset()
        self.scenesUI.reset()
        self.layerEditorUI.reset()

    def onNew(self, evt=None):
        self.editor.reset()
        self.editor.newProj()

    def onOpen(self, evt=None):
        dialog = wx.FileDialog(None, "Choose a project file", os.getcwd(), "", "*.proj", wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.editor.load(Filename.fromOsSpecific(dialog.GetPath()))
            self.libraryUI.update()
            self.storyObjUI.update()
            self.soundUI.update()
        dialog.Destroy()

    def onSave(self, evt=None):
        if not self.editor.saved:
            self.onSaveAs(evt)
        else:
            self.editor.save()

    def onSaveAs(self, evt):
        while True:
            dialog = SaveProjectUI(self, -1, "Save Project")
            if dialog.ShowModal() == wx.ID_OK:
                baseDir = dialog.dir
                projName = Util.toFilename(dialog.projName)
                if projName == '' or projName != dialog.projName:
                   dlg = wx.MessageDialog(self, "Invalid Project Name", style = wx.OK)
                   dlg.ShowModal()
                   dlg.Destroy()
                elif baseDir == None:
                    dlg = wx.MessageDialog(self, "Please Choose a save location", style = wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                else: 
                    dir = baseDir + '/' + projName
                    if os.path.exists(dir.toOsSpecific()):
                        dlg = wx.MessageDialog(self, "A folder with that name already exists in the"\
                                               + " directory you have chosen.  Please choose another name.", style = wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                    else:
                        self.editor.saveAs(dir, projName)
                        break
            else:
                break
            
    def onImport(self, evt=None):
        importUI = ImportUI(self, -1, "Import")      
        importUI.Show()
        
    def onImportLib(self, evt=None):
        dlg = wx.FileDialog(self, "Choose a library file to import.", wildcard = "*.lbr", style = wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
                    
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            vfs = VirtualFileSystem.getGlobalPtr()
            filename = Filename.fromOsSpecific(dlg.GetPath())
            otherName = filename.getBasenameWoExtension().strip()
            mountPt = "./externalLib_" + otherName
            vfs.mount(filename, mountPt, VirtualFileSystem.MFReadOnly)
            otherLib = Library.Library(Filename(mountPt))
            
            self.editor.lib.mergeWith(otherLib, otherName=otherName, saveAfter=True)
            vfs.unmountPoint(mountPt)
            
            self.libraryUI.update()
            self.storyObjUI.update()
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
    def onBrowseLib(self, evt=None):        
        dlg = wx.FileDialog(self, "Choose a library file to browse.", wildcard = "*.lbr", style = wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
                    
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            vfs = VirtualFileSystem.getGlobalPtr()
            filename = Filename.fromOsSpecific(dlg.GetPath())
            otherName = filename.getBasenameWoExtension().strip()
            mountPt = "./externalLib_" + otherName
            vfs.mount(filename, mountPt, VirtualFileSystem.MFReadOnly)
            otherLib = Library.Library(Filename(mountPt))
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
            libBrowser = LibraryBrowserUI(self, otherLib, otherName)
            
            libBrowser.ShowModal()
            
            vfs.unmountPoint(mountPt)
        
            self.libraryUI.update()
            self.storyObjUI.update()
    
    def onBrowseDefaultLib(self, evt=None):
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            vfs = VirtualFileSystem.getGlobalPtr()
            filename = Filename('models/Orelia.lbr')#'models/default.lbr')
            otherName = filename.getBasenameWoExtension().strip()
            mountPt = "./externalLib_" + otherName
            vfs.mount(filename, mountPt, VirtualFileSystem.MFReadOnly)
            otherLib = Library.Library(Filename(mountPt))
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
            libBrowser = LibraryBrowserUI(self, otherLib, otherName)
            
            libBrowser.ShowModal()
            
            vfs.unmountPoint(mountPt)
        
            self.libraryUI.update()
            self.storyObjUI.update()
        
    def onExportLib(self, evt=None):
        if self.editor.saved:
            dlg = wx.FileDialog(self, "Choose a filename for your exported library.", defaultDir = self.editor.projDir.toOsSpecific(),\
                defaultFile = self.editor.currentProj.name.strip() + ".lbr", wildcard="*.lbr", style = wx.FD_SAVE|wx.OVERWRITE_PROMPT)
                
            if dlg.ShowModal() == wx.ID_OK:
                f = Filename.fromOsSpecific(dlg.GetPath())
                if f.getDirname() != self.editor.projDir.getFullpath():
                    msg = wx.MessageDialog(self, "Must save to your current project directory.", style= wx.OK|wx.ICON_ERROR)
                    msg.ShowModal()
                    return
                self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
                self.editor.lib.exportToMultifile(Filename.fromOsSpecific(dlg.GetPath()))
                self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self, "Please save the project first.", "Cannot Export Library Before Saving",\
            style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    
    def onExport(self, evt):
        if not self.editor.saved:
            dlg = wx.MessageDialog(self, "Please save the project first.", "Cannot Export Before Saving",\
            style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
#            dlg = wx.FileDialog(self, "Choose a python file to export to.", \
#            defaultDir= self.editor.currentProj.dir.toOsSpecific(),\
#            defaultFile = self.editor.currentProj.name + '.py', wildcard="*.py", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
#            
#            if dlg.ShowModal() == wx.ID_OK:
#                self.editor.standaloneExporter.export(dlg.GetPath())
            dlg = ExportOptionsDialog(self)
            opts = dlg.ShowModal()
            if opts['path'] != '':
                self.editor.standaloneExporter.export(opts)
                self.editor.save()
    def onBVWExport(self, evt):
        if not self.editor.saved:
            dlg = wx.MessageDialog(self, "Please save the project first.", "Cannot Export Before Saving",\
            style=wx.OK|wx.ICON_ERROR)
            
            dlg.ShowModal()
            dlg.Destroy()
        else:
#            dlg = wx.FileDialog(self, "Choose a python file to export to.", \
#            defaultDir= self.editor.currentProj.dir.toOsSpecific(),\
#            defaultFile = self.editor.currentProj.name + '.py', wildcard="*.py", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
#            
#            if dlg.ShowModal() == wx.ID_OK:
#                self.editor.standaloneExporter.exportBVW(dlg.GetPath())
            dlg = ExportOptionsDialog(self)
            opts = dlg.ShowModal()
            if opts['path'] != '':
                self.editor.standaloneExporter.exportBVW(opts)
    
    def onGameExport(self, evt):
        if not self.editor.saved:
            dlg = wx.MessageDialog(self, "Please save the project first.", "Cannot Export Before Saving",\
            style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
#            dialog = wx.MessageDialog(self, "Cool stuff goes here", "Export as Game", wx.OK|wx.ICON_EXCLAMATION)
#            dialog.ShowModal()
#            dialog.Destroy()
            
            dlg = ExportOptionsDialog(self)
            opts = dlg.ShowModal()
            if opts['path'] != '':
                self.editor.standaloneExporter.exportGame(opts)
                self.editor.save()
                        
    def onGameExportRun(self, evt):
       if not self.editor.saved:
            dlg = wx.MessageDialog(self, "Please save the project first.", "Cannot Export Before Saving",\
            style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
       else:
#            dialog = wx.MessageDialog(self, "Cool stuff goes here", "Export as Game", wx.OK|wx.ICON_EXCLAMATION)
#            dialog.ShowModal()
#            dialog.Destroy()
            
            dlg = ExportOptionsDialog(self)
            opts = dlg.ShowModal()
            if opts['path'] != '':
                self.editor.standaloneExporter.exportGame(opts)
                self.editor.save() 
            
                filename = Filename("runWorld.bat")
                filename.setDirname(self.editor.projDir.getFullpath())
                #print filename
                cwd = os.getcwd()
                os.chdir(self.editor.projDir.toOsSpecific())
                subprocess.Popen(filename.toOsSpecific())
                os.chdir(cwd)
        
    def onMerge(self, evt):
        dlg = MergeProjectUI(self)
        
        dlg.ShowModal()
        
        dlg.Destroy()
    
    def onSceneStats(self, evt=None):
        f = StringIO()
        temp = sys.stdout
        sys.stdout = f
        render.analyze()
        
        sys.stdout = temp
        
        dlg = wx.MessageDialog(self, f.getvalue(), caption="Scene Statistics")
        dlg.ShowModal()
    
    def onSelectedObjectStats(self, evt=None):
        np = base.direct.selected.last
        
        f = StringIO()
        temp = sys.stdout
        sys.stdout = f
        np.analyze()
        
        sys.stdout = temp
        
        dlg = wx.MessageDialog(self, f.getvalue(), caption="Object Statistics")
        dlg.ShowModal()
    
    def onDuplicate(self, evt=None):
        action = ActionDuplicateSelected(self.editor)
        self.editor.actionMgr.push(action)
        action()
        #self.editor.objectMgr.duplicateSelected()

    def toggleGrid(self, evt):
        if self.showGridMenuItem.IsChecked():
            for grid in [self.perspView.grid, self.topView.grid, self.frontView.grid, self.leftView.grid]:
                if grid.isHidden():
                    grid.show()
        else:
            for grid in [self.perspView.grid, self.topView.grid, self.frontView.grid, self.leftView.grid]:
                if not grid.isHidden():
                    grid.hide()
                    
    def onShowJournal(self, evt):
        journalDialog = JournalDialog(self, -1, "Show Journal", self.editor)      
        journalDialog.Show()
        
    def onConversationEditor(self,evt):
        editor = ConversationEditor(self,self.editor)
        #editor.Show()
    
    def onInventory(self, evt):
        inventoryDialog = LEInventoryUI(self,-1,"Inventory Map", self.editor)
        inventoryDialog.Show()
        #inventoryDialog.ShowModal()
            
    def onGridSize(self, evt):
        gridSizeUI = GridSizeUI(self, -1, 'Change Grid Size', self.perspView.grid.gridSize, self.perspView.grid.gridSpacing)
        gridSizeUI.ShowModal()
        gridSizeUI.Destroy()
    
    def onShowColliders(self, evt):
        if self.showCollidersMenuItem.IsChecked():
            self.editor.objectMgr.showColliders = True
            for c in self.editor.objectMgr.colliders:
                c.show()
        else:
            self.editor.objectMgr.showColliders = False

            for c in self.editor.objectMgr.colliders:
                c.hide()


    def onDestroy(self, evt):
        dlg = wx.MessageDialog(self, "Are you sure you want to exit?", style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.editor.saveSettings()
            self.editor.reset()
            if self.editor.tempDir and os.path.exists(self.editor.tempDir):
                try:
                    shutil.rmtree(self.editor.tempDir)
                except:
                    pass
            dlg.Destroy()
            return True
        else:       
            dlg.Destroy()
            return False

    def updateGrids(self, newSize, newSpacing):
        self.perspView.grid.gridSize = newSize
        self.perspView.grid.gridSpacing = newSpacing
        self.perspView.grid.updateGrid()

        self.topView.grid.gridSize = newSize
        self.topView.grid.gridSpacing = newSpacing
        self.topView.grid.updateGrid()

        self.frontView.grid.gridSize = newSize
        self.frontView.grid.gridSpacing = newSpacing
        self.frontView.grid.updateGrid()

        self.leftView.grid.gridSize = newSize
        self.leftView.grid.gridSpacing = newSpacing
        self.leftView.grid.updateGrid()        

    def onHotKeys(self, evt):
        hotKeyUI = HotKeyUI(self, -1, 'Hot Key List')
        hotKeyUI.ShowModal()
        hotKeyUI.Destroy()
    
    def onPreferences(self, evt):
        ##Show a dialog with the few editor prefs we have
        dlg = PrefsDialog(self)
        dlg.Show()
        
    def buildContextMenu(self, nodePath):
        for menuItem in self.contextMenu.GetMenuItems():
            self.contextMenu.RemoveItem(menuItem)

        #self.contextMenu.addItem('Replace With Selected Asset', call=self.editor.objectMgr.replaceObjectWithAsset)
        self.contextMenu.addItem('Duplicate', call = self.onDuplicate)

class GridSizeUI(wx.Dialog):
    def __init__(self, parent, id, title, gridSize, gridSpacing):
        wx.Dialog.__init__(self, parent, id, title, size=(250, 240))

        self.parent = parent
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)

        wx.StaticBox(panel, -1, 'Grid Size', (5, 5), (235, 80))

        self.gridSizeSlider = WxSlider(panel, -1, float(gridSize), 10.0, 100000.0,
                           pos = (10, 25), size=(220, -1),
                           style=wx.SL_HORIZONTAL | wx.SL_LABELS, textSize=(80,20))
        self.gridSizeSlider.Enable()

        wx.StaticBox(panel, -1, 'Grid Space', (5, 90), (235, 80))

        self.gridSpacingSlider = WxSlider(panel, -1, float(gridSpacing), 0.01, 2000.0,
                           pos = (10, 115), size=(220, -1),
                           style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.gridSpacingSlider.Enable()
        
        okButton = wx.Button(self, -1, 'Apply', size=(70, 20))
        okButton.Bind(wx.EVT_BUTTON, self.onApply)
        vbox.Add(panel)
        vbox.Add(okButton, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)

        self.SetSizer(vbox)
        base.le.ui.bindKeyEvents(False)

    def onApply(self, evt):
        newSize = self.gridSizeSlider.GetValue()
        if newSize < 1:
            newSize = 1
            self.gridSizeSlider.SetValue(newSize)
        newSpacing = self.gridSpacingSlider.GetValue()
        if newSpacing < newSize/1000.0:
            newSpacing = newSize/1000.0
            self.gridSpacingSlider.SetValue(newSpacing)
        self.parent.updateGrids(newSize, newSpacing)
        base.le.ui.bindKeyEvents(True)
        self.Destroy()

class ViewportMenu(wx.Menu):
    """Represents a menu that appears when right-clicking a viewport."""
    def __init__(self):
        wx.Menu.__init__(self)
  
    def addItem(self, name, parent = None, call = None, id = None):
        if id == None: id = wx.NewId()
        if parent == None: parent = self
        item = wx.MenuItem(parent, id, name)
        parent.AppendItem(item)
        if call != None:
            self.Bind(wx.EVT_MENU, call, item)

    def addMenu(self, name, parent = None, id = None):
        if id == None: id = wx.NewId()
        subMenu = wx.Menu()
        if parent == None: parent = self
        parent.AppendMenu(id, name, subMenu)
        return subMenu

