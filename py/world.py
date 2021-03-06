
if Controller.isDebugVersion(): print("[world.py]")

import random
import types

exec(compile(open(kikipy_path + "colors.py", "rb").read(), kikipy_path + "colors.py", 'exec'))
exec(compile(open(kikipy_path + "action.py", "rb").read(), kikipy_path + "action.py", 'exec'))
exec(compile(open(kikipy_path + "lang.py", "rb").read(), kikipy_path + "lang.py", 'exec'))

# .................................................................................................................
#                                           KikiWorld Extensions
# .................................................................................................................

# .................................................................................................................
def toggle (self, objectName):
    """toggles object with name objectName"""
    Controller.startTimedAction(self.getObjectWithName(objectName).getActionWithName("toggle"))

KikiWorld.toggle = toggle
del toggle

# .................................................................................................................
def activate (self, objectName):
    """activates object with name objectName"""
    object = self.getObjectWithName(objectName)
    if object.getClassName() == "KikiSwitch":
        kikiObjectToSwitch(object).setActive(1)
    elif object.getClassName() == "KikiGate":
        kikiObjectToGate(object).setActive(1)

KikiWorld.activate = activate
del activate

# .................................................................................................................
def decenter (self, *args):
    s = self.getSize()
    if len(args) == 3:
        x, y, z = args[0], args[1], args[2]
    elif len(args) == 1:
        x, y, z = args[0]

    return KikiPos(int(x+s.x/2), int(y+s.y/2), int(z+s.z/2))

KikiWorld.decenter = decenter
del decenter

# .................................................................................................................
def addObjectLine (self, object, start, end):
    """adds a line of objects of type to the world. start and end should be 3-tuples or KikiPos objects"""
    if isinstance (start, KikiPos):
        start = (start.x, start.y, start.z)
    sx, sy, sz = start
    if isinstance (end, KikiPos):
        end = (end.x, end.y, end.z)
    ex, ey, ez = end
    
    diff = list(map (lambda a,b: a-b, end, start))
    maxdiff = max(list(map (abs, diff)))
    deltas = list(map (lambda a, d = float (maxdiff): a/d, diff))
    for i in range (maxdiff):
        pos = KikiPos(*(list(map (lambda a, b: int(a+i*b), start, deltas))))
        if self.isUnoccupiedPos (pos):
            if type(object) == bytes:
                self.addObjectAtPos (eval(object), pos)
            else:
                self.addObjectAtPos (object(), pos)
   
KikiWorld.addObjectLine = addObjectLine
del addObjectLine

# .................................................................................................................
def addObjectPoly (self, object, points, close=1):
    """adds a polygon of objects of type to the world. points should be 3-tuples or KikiPos objects"""
    if close:
        points.append (points[0])
    for index in range(1, len(points)):
        self.addObjectLine (object, points[index-1], points[index])
   
KikiWorld.addObjectPoly = addObjectPoly
del addObjectPoly

# .................................................................................................................
def addObjectRandom (self, object, number):
    """adds number objects of type at random positions to the world"""
    for i in range (number):
        if type (object) == bytes:
            self.setObjectRandom (eval(object))
        else:
            self.setObjectRandom (object())
    
KikiWorld.addObjectRandom = addObjectRandom
del addObjectRandom

# .................................................................................................................
def setObjectRandom (self, object):
    """adds number objects of type at random positions to the world"""
    size = self.getSize()
    object_set = 0
    while not object_set:                                   # hack alert!
        random_pos = KikiPos (random.randrange (size.x), \
                              random.randrange (size.y), \
                              random.randrange (size.z))
        if not object.isSpaceEgoistic() or self.isUnoccupiedPos (random_pos):
            self.addObjectAtPos (object, random_pos)
            object_set = 1
    
KikiWorld.setObjectRandom = setObjectRandom
del setObjectRandom

# .................................................................................................................
#                                               KikiPyWorld
# .................................................................................................................

class KikiPyWorld (KikiPyActionObject):
    """class for creating worlds from dictionaries"""

    # ................................................................ init
    def __init__ (self):
        """initializes a KikiPyWorld object"""
        KikiPyActionObject.__init__(self)
        self.preview = false

    # ................................................................ world creation
    def create (self, world_dict = {}):
        """creates the world from a level name or a dictionary"""

        print ("world dict ", world_dict)
        #print (level_dict)
        #print (level_dict["sandbox"])

        if world_dict:
            if type (world_dict) == bytes:
                world.level_index = level_list.index (world_dict)
                world.level_name = world_dict
                self.dict = level_dict[world_dict]
            else:
                self.dict = world_dict

        # ............................................................ appearance

        #hack: something is going wrong
        self.dict = level_dict["sandbox"]
        world.level_name = "sandbox"

        print(self.dict)
        print("self.dict: ", self.dict)
        print("self.dict[size]: ", self.dict["size"])
        x, y, z = self.dict["size"]
        world.setSize (x, y, z)

        if "scheme" in self.dict:
            applyColorScheme (eval(self.dict["scheme"]))
        else:
            applyColorScheme (default_scheme)

        if "border" in self.dict:
            border = self.dict["border"]
        else:
            border = True

        world.setDisplayBorder (border)

        # ............................................................ intro text   
        if "intro" in self.dict:
            if not self.preview:
                intro_text = KikiScreenText ()
                intro_text.addText (self.dict["intro"])
                intro_text.show ()
            world.setName (self.dict["intro"])
        else:
            world.setName ("noname")
        
        if self.preview:
            world.getProjection().setViewport (0.0, 0.4, 1.0, 0.6)
        else:
            world.getProjection().setViewport (0.0, 0.0, 1.0, 1.0)
        
        # ............................................................ escape
        escape_event = Controller.getEventWithName ("escape")
        escape_event.removeAllActions()
        escape_event.addAction (continuous (self.escape, "escape"))

        # ............................................................ exits

        if "exits" in self.dict:
            exit_id = 0
            for entry in self.dict["exits"]:
                exit_gate = KikiGate ( entry["active"] == True)
                
                if "name" in entry:
                    name = entry["name"]
                else:
                    name = "exit "+str(exit_id)
                exit_gate.setName(name)

                exit_action  = once (self, "exit " + str(exit_id))
                delay_action = once (lambda a = exit_action: Controller.timer_event.addAction (a))
                exit_gate.getEventWithName ("enter").addAction (delay_action)
                if "position" in entry:
                    pos = world.decenter (entry["position"])
                elif "coordinates" in entry:
                    pos = KikiPos(*entry["coordinates"])
                world.addObjectAtPos (exit_gate, pos)
                exit_id += 1

        # ............................................................ creation

        if "create" in self.dict:
            if callable(self.dict["create"]):
                self.dict["create"]()
            else:
                exec(self.dict["create"], globals())

        # ............................................................ player

        player = Controller.player
        
        player_dict = self.dict["player"]
        
        if "orientation" in player_dict:
            player.setOrientation (player_dict["orientation"])
        else:
            player.setOrientation (roty90)
            
        if "position" in player_dict:
            world.addObjectAtPos (player, world.decenter(player_dict["position"]))
        elif "coordinates" in player_dict:
            pos = player_dict["coordinates"]
            world.addObjectAtPos (player, KikiPos(pos[0], pos[1], pos[2]))

        if "nostatus" in player_dict:
            if player_dict["nostatus"] or self.preview:
                Controller.player_status.hide()
            else:
                Controller.player_status.show()
        else:
            if self.preview:
                Controller.player_status.hide()
            else:
                Controller.player_status.show()
        
        world.getProjection().setPosition (KVector())

        score = highscore.levelParMoves (world.level_name)
        print(score)
        Controller.player.getStatus().setMinMoves (score)
        Controller.player.getStatus().setMoves (0)

        # ............................................................ init
        world.init() # tell the world that we are finished

    # ................................................................ restart level
    def restart (self):
        """restores the player status and restarts the current level"""
        Controller.player.getStatus().setMoves (0)
        Controller.player.reborn()
        self.create()

    # ................................................................ finish level
    def finish (self):
        """saves the current level status in highscore file"""
        highscore.levelFinished (world.level_name, Controller.player.getStatus().getMoves())

    # ................................................................ player reset
    def resetPlayer (self):
        """reset the player to it's original position and orientation"""
        
        player_dict = self.dict["player"]
        player = Controller.getPlayer()
        
        if "reset orientation" in player_dict:
            player.setOrientation (player_dict["reset orientation"])
        elif "orientation" in player_dict:
            player.setOrientation (player_dict["orientation"])
        else:
            player.setOrientation (rot0)
            
        if "reset position" in player_dict:
            world.moveObjectToPos (player, world.decenter (player_dict["reset position"]))
        else:
            world.moveObjectToPos (player, world.decenter (player_dict["position"]))
            
    # ................................................................ actions
    def performAction (self, name, time):
        """action callback. used to exit current world"""
        if name.find ("exit") == 0:
            self.finish()
            Controller.player.getStatus().setMoves (0)
            if "world" in self.dict["exits"][int(name[5:])]:
                w = self.dict["exits"][int(name[5:])]["world"]
                if isinstance (w, KikiPyWorld):
                    w.create()
                elif callable (w):
                    w()
                else:
                    exec("KikiPyWorld().create(" + world + ")")
            else:
                KikiPyWorld().create (level_list[world.level_index+1])
                
    # ................................................................ help
    def help (self, index = 0):
        """displays help messages"""

        text_list = self.dict["help"]
        more_text = index < len (text_list) - 1
        less_text = index > 0
        
        list = text_list[index].split("$key(")     
        for i in range (1, len(list)):
            close = list[i].find(")")
            list[i] = Controller.player.getKeyForAction (list[i][:close]) + list[i][close+1:]
                         
        list.append ("\n\n$scale(0.5)(%d/%d)" % (index+1, len (text_list)))
        help_text = KikiPageText ("".join(list), more_text, less_text)
            
        if more_text:
            help_text.getEventWithName ("next").addAction (once (lambda i=index+1: self.help (i)))
        if less_text:
            help_text.getEventWithName ("previous").addAction (once (lambda i=index-1: self.help (i)))
 
    # ................................................................  
    def resetProjection(self):
        world.getProjection().setViewport (0.0, 0.0, 1.0, 1.0)
                                    
    # ................................................................ escape key
    def escape (self):
        """handles an ESC key event"""

        self.resetProjection()
        
        if "escape" in self.dict:
            if callable(self.dict["escape"]):
                self.dict["escape"]()
            else:
                exec(self.dict["escape"], globals())
            return

        menu = KikiMenu()
        menu.getEventWithName ("hide").addAction (once(self.resetProjection))
        
        if Controller.isDebugVersion ():
            menu.addItem (Controller.getLocalizedString ("next level"), once (lambda w=self: w.performAction("exit 0",0)))
        if "help" in self.dict:
            menu.addItem (Controller.getLocalizedString ("help"), once (self.help))
        menu.addItem (Controller.getLocalizedString ("restart"), once (self.restart))
        
        esc_menu_action = once (self.escape)
        console.out("level_index %d" % world.level_index)
        menu.addItem (Controller.getLocalizedString ("load level"), once (lambda i=world.level_index,a=esc_menu_action: levelSelection(i, a)))
        menu.addItem (Controller.getLocalizedString ("setup"), once (quickSetup))        
        menu.addItem (Controller.getLocalizedString ("about"), once (display_about))
        menu.addItem (Controller.getLocalizedString ("quit"), once (Controller.quit))
     
# .................................................................................................................
exec(compile(open(kikipy_path + "config.py", "rb").read(), kikipy_path + "config.py", 'exec'))
exec(compile(open(kikipy_path + "setup.py", "rb").read(), kikipy_path + "setup.py", 'exec'))
exec(compile(open(kikipy_path + "levels.py", "rb").read(), kikipy_path + "levels.py", 'exec'))
exec(compile(open(kikipy_path + "levelselection.py", "rb").read(), kikipy_path + "levelselection.py", 'exec'))
exec(compile(open(kikipy_path + "highscore.py", "rb").read(), kikipy_path + "highscore.py", 'exec'))
exec(compile(open(kikipy_path + "intro.py", "rb").read(), kikipy_path + "intro.py", 'exec'))
