
if Controller.isDebugVersion(): print("[config.py]")

from configparser import ConfigParser

# .................................................................................................................
#                                               KIKI CONFIG
# .................................................................................................................
class KikiConfig (ConfigParser):
    """kiki configuration parser"""
    
    def __init__ (self):
        """initialization"""
        ConfigParser.__init__ (self)
        
        self.readfp (open(kikipy_path + "kiki.cfg"))
        
        try:
            if os.uname()[0] == "Darwin":
                self.config_file_path = os.path.expanduser ("~/Library/Preferences/kiki.cfg")
            else:
                self.config_file_path = os.path.expanduser ("~/.kiki.cfg")
        except:
            console.out("--- writing config to %s" % (os.path.expanduser ("~/.kiki.cfg"),))
            self.config_file_path = os.path.expanduser ("~/.kiki.cfg")

        self.read (self.config_file_path)
                
        for section in self.sections():
            for option in self.options (section):
                self.apply (section, option, self.getit(section, option))
        
    def apply (self, section, option, value):
        """sets and applies value for option in section"""
        self.setit (section, option, value)
        if section == "sound":
            if option == "volume":
                volume = int(int(value)*(128/9))
                sound.setSoundVolume (volume)
            elif option == "mute":
                sound.setMute (self.getboolean(section, option))
        elif section == "display":
            if option == "fov":
                Controller.getPlayer().getProjection().setFov (int(value))
            elif option == "gamma":
                Controller.setGamma(int(value))
            elif option == "fullscreen":
                fullscreen = self.getboolean(section, option)
                if fullscreen != Controller.getFullscreen():
                    screen_size = self.getit (section, fullscreen and "fullscreen size" or "window size")
                    screen_size = tuple (map (int, screen_size.split("x")))
                    Controller.changeScreenSize (screen_size[0], screen_size[1], self.getboolean(section, option))
                    self.setit (section, "fullscreen size", "%dx%d" % Controller.getScreenSize())
        elif section == "keyboard":
            player = Controller.getPlayer()
            player.setKeyForAction (value, option.replace("_", " "))
        elif section == "game":
            if option == "speed":
                Controller.setSpeed (int(value))
            elif option == "language":
                Controller.language = value
        
    def setit (self, section, option, value):
        """do not override, we have a differing method signature"""
        ConfigParser.set (self, section, str(option).replace(" ", "_"), str(value))
            
    def getit(self, section, option):
        """do not override, we have a differing method signature"""
        return ConfigParser.get (self, section, str(option).replace(" ", "_"))

    def save (self):
        """save the configuration"""
        try:
            cfg_file = file (self.config_file_path, "w+")
            self.write (cfg_file)
            cfg_file.close()
        except:
            console.printError ("unable to write configuration to " + self.config_file_path)

# .................................................................................................................

config = KikiConfig ()
