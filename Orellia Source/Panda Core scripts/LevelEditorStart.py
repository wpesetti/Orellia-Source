import LevelEditor
import sys, datetime
from Logger import *

sys.stdout = Logger('LevelEditor.log')
sys.stderr = sys.stdout

print '**************************************************'
print datetime.datetime.now()

base.le = LevelEditor.LevelEditor()
# You should define LevelEditor instance as
# base.le so it can be reached in global scope

run()
