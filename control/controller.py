from .input import Input
from .config import Config, Actions, Vectors, Mode
from .robot import Robot
from .server import Server
from .client import Client
import sys
import getopt
import time
import threading
import json


class Controller:
    config_file = None
    inputs = None
    config = None
    server = None
    client = None
    robot = None
    
    def __init__(self, config=None):
        mode = None
        opts, args = getopt.getopt(sys.argv[1:], "h", ["conf="])
        for opt, arg in opts:
            if opt == '-h':
                print ('remote --conf=</path/to/config.json>')
                sys.exit()
            elif opt in ("--conf"):
                self.config_file = arg
            elif opt in ("--mode"):
                mode = Mode[opt]
        if config == None:
            self.config = Config()
            if self.config_file != None:
                with open(self.config_file, 'r') as file:
                    self.config.map_values(json.load(file))
        else:
            self.config = config
        
        if mode != None:
            self.config.mode = mode
            
        print("Config File = {}".format(self.config_file))
        if self.config.mode == Mode.CLIENT:
            self.init_client()
        elif self.config.mode == Mode.SERVER:
            self.init_server()
        elif self.config.mode == Mode.LOCAL:
            self.init_local()

    def init_input(self):
        self.inputs = Input(self.config)

    def init_client(self):
        self.init_input()
        self.client = Client(self.config)
        
    def init_server(self):
        self.init_output()
        self.server = Server(self.config)
        threading.Thread(target=self.server.start).start()
        
    def init_local(self):
        self.init_input()
        self.init_output()

    def init_output(self):
        self.robot = Robot(self.config)
    
    """ State handling. If we are local, we want to send the control
        surface directly to the robot and skip our networking layer
    """
    
    """ Retrieve state, either from the server or our control surface """

    def get_state(self):
        if self.config.mode == Mode.CLIENT or self.config.mode == Mode.LOCAL:
            return self.inputs.get_state()
        else:
            return self.server.get_state()
    
    """ Write thet state to the robot """

    def write_state(self, state):
            self.robot.set_action_state(state)
            self.robot.set_motion(state)
            self.robot.set_heading(state)
            self.robot.set_pan_tilt(state)
    
    """ Emit the state, either to the robot or to the server """

    def emit_state(self, state):
        if self.config.mode == Mode.CLIENT:
            self.client.send_state(state)
        else:
            self.write_state(state)
    
    """ If we are in local or client mode, we get the state from
        the control surface; if we are in server mode, we get the
        state from the REST server. If we are in client mode, we
        send the state to the server. If we are in local or server
        mode, we write the state to the robot """

    def start(self):
        print("starting in {} mode...".format(self.config.mode))
        while True:
            state = self.get_state()
            self.emit_state(state)
            time.sleep(self.config.sampling_frequency)
                
