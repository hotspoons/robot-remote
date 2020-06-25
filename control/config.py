from enum import Enum
import copy

class Vectors(str, Enum):
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    LOOK_UP = "LOOK_UP"
    LOOK_DOWN = "LOOK_DOWN"
    LOOK_LEFT = "LOOK_LEFT"
    LOOK_RIGHT = "LOOK_RIGHT"
    
class Actions(str, Enum):
    G_TOGGLE = "G_TOGGLE"
    B_TOGGLE = "B_TOGGLE"
    R_TOGGLE = "R_TOGGLE"
    BEEP = "BEEP"
    
class Mode(str, Enum):
    LOCAL = "LOCAL"
    CLIENT = "CLIENT"
    SERVER = "SERVER"
    
class State():
    default_state = {
        "vectors":{
            Vectors.FORWARD: 0.00,
            Vectors.REVERSE: 0.00,
            Vectors.LEFT: 0.00,
            Vectors.RIGHT: 0.00,
            Vectors.LOOK_UP: 0.00,
            Vectors.LOOK_DOWN: 0.00,
            Vectors.LOOK_LEFT: 0.00,
            Vectors.LOOK_RIGHT: 0.00,
        },
        "actions":{
            Actions.G_TOGGLE: False,
            Actions.B_TOGGLE: False,
            Actions.R_TOGGLE: False,
            Actions.BEEP: False,
        }
    }
    
    
#TODO Make this read from a configuration file
class Config:
    
    """ If you have an MJPEG streamer running on your robot, e.g. 
        https://github.com/Freenove/Freenove_Three-wheeled_Smart_Car_Kit_for_Raspberry_Pi/tree/master/mjpg-streamer,
        embed the stream into the client"""
    
    mjpeg_url = "http://{hostname}:8090/?action=stream"
    
    """ For future use, I may try my hand at more modern video streaming,
        and possibly embed it into this application if I can find a 
        hardware-accelerated h264 encoder that works with Python. """
    
    h264_url = None
    
    """ The mode in which is runs. LOCAL reads directly from a configured
        controller and sends events directly to the robot. CLIENT reads
        events from the configured controller and sends it to the server.
        SERVER reads state in the format of the State class above and 
        sends them to the robot, either over REST or WebSockets"""
        
    mode = Mode.LOCAL
    
    """ The binding address for the server (e.g. 0.0.0.0 = all) in server
        mode, or the host name or IP address of the server"""
        
    address = "0.0.0.0"
    
    """ The port you wish to run the REST/WS server on, or connect to a
        server on, depending on client/server mode"""
        
    port = 9090
    
    """ How often, in millseconds, you wish the application to poll for
        a change in state, either from a controller or from REST/WS
        """
        
    sampling_frequency = 0.06
    
    """ When receiving state over REST or WebSocket, how long between
    state updates from a client before we set the state to ground, to 
    prevent our robot from driving endlessly in the same heading it 
    was going"""
    
    server_state_update_timeout = 1.0
    
    """ This dictionary needs to be configured for your input controller
        
        I used a $12 Matricom bluetooth controller in dual shock/xbox
        mode to prototype with, these axes may not be consistent with
        other industry standard controllers """
        
    AXIS_MAP = {
        0: [Vectors.LEFT, Vectors.RIGHT],
        1: [Vectors.FORWARD, Vectors.REVERSE],
        2: [Vectors.LOOK_LEFT, Vectors.LOOK_RIGHT],
        3: [Vectors.LOOK_UP, Vectors.LOOK_DOWN],
    }
    
    """ These correspond to the A/B/X/Y buttons on this Matricom controller,
        this may need to be adjusted to match your buttons"""
        
    ACTIONS_MAP = {
        0:Actions.G_TOGGLE,
        1:Actions.R_TOGGLE,
        3:Actions.B_TOGGLE,
        4:Actions.BEEP,
    }
    
    def map_values(self, dictionary):
        for key in dictionary:
            if hasattr(self, key):
                # Since JSON doesn't support numeric keys, convert types here
                if type(getattr(self, key)) is dict and type(dictionary[key]) is dict:
                    target_dict = getattr(self, key)
                    print("before {}".format(target_dict))
                    for dict_key in dictionary[key]:
                        
                        target_dict[int(dict_key)] = dictionary[key][dict_key]
                    print("after {}".format(target_dict))
                else:
                    setattr(self, key, dictionary[key])
    
    def get_base_state(self):
        return copy.deepcopy(State().default_state)
