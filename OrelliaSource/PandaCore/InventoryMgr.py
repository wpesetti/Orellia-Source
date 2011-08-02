from InventoryMgrBase import InventoryMgrBase

class InventoryMgr(InventoryMgrBase):
    """ InventoryMgr will create, manage, update Inventory Entries in the Inventory """
    
    def __init__(self, world):
        InventoryMgrBase.__init__(self, world)