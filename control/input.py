import ctypes
from sdl2 import *

from .config import Config, Vectors, Actions


class Input:
    config = None     
    device = None
    axes = None
    buttons = None
    hat = None
    
    def __init__(self, config):
        self.config = config
        SDL_Init(SDL_INIT_JOYSTICK)
        self.axes = {}
        self.buttons = {}
        self.hat = self.__hat_factory()
 
    def __hat_factory(self):
        return {
            "N" : False,
            "NE" : False,
            "E" : False,
            "SE" : False,
            "S" : False,
            "SW" : False,
            "W" : False,
            "NW" : False,
        }

    def get_axes(self):
        if self.device != None:
            return self.axes
        else:
            return {}
        
    def get_buttons(self):
        if self.device != None:
            return self.buttons
        else:
            return {}
    
    def get_hat(self):
        if self.device != None:
            return self.hat
        else:
            return self.__hat_factory()

    def poll(self):
        event = SDL_Event()
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_JOYDEVICEADDED:
                self.device = SDL_JoystickOpen(event.jdevice.which)
            elif event.type == SDL_JOYDEVICEREMOVED:
                self.device = None
            elif event.type == SDL_JOYAXISMOTION:
                self.axes[event.jaxis.axis] = event.jaxis.value
            elif event.type == SDL_JOYBUTTONDOWN:
                self.buttons[event.jbutton.button] = True
            elif event.type == SDL_JOYBUTTONUP:
                self.buttons[event.jbutton.button] = False
            elif event.type == SDL_JOYHATMOTION:
                self.hat = self.__hat_factory()
                value = event.jhat.value
                if value == 1:
                    self.hat["N"] = True
                elif value == 3:
                    self.hat["NE"] = True
                elif value == 2:
                    self.hat["E"] = True
                elif value == 6:
                    self.hat["SE"] = True
                elif value == 4:
                    self.hat["S"] = True
                elif value == 12:
                    self.hat["SW"] = True
                elif value == 8:
                    self.hat["W"] = True
                elif value == 9:
                    self.hat["NW"] = True
    
    def get_state(self):
        state = self.config.get_base_state()
        self.poll()
        axes = self.get_axes()
        buttons = self.get_buttons()
        hat = self.get_hat()
        
        for i in axes:
            vector = None
            value = self.__scale_input(axes[i])
            for key in self.config.AXIS_MAP:
                if key == i:
                    if value < 0.0:
                        vector = Vectors[self.config.AXIS_MAP[key][0]]
                    else:
                        vector = Vectors[self.config.AXIS_MAP[key][1]]
                    if vector != None:
                        self.update_state(vector, value, state)
        for i in buttons:
            for key in self.config.ACTIONS_MAP:
                if key == i:
                    if buttons[i] == True:
                        self.update_state(Actions[self.config.ACTIONS_MAP[key]], None, state)
                       
        return state
                        
    def __scale_input(self, value):
        scale = 32768
        return (value / scale)
 
    def update_state(self, event, axis, state):
        if isinstance(event, Vectors):
            for event_type in state:
                if event_type == "vectors":
                    for vector in state[event_type]:
                        if vector == event:
                            state[event_type][vector] = axis
        elif isinstance(event, Actions):
            for event_type in state:
                if event_type == "actions":
                    for action in state[event_type]:
                        if action == event:
                            state[event_type][action] = True
        
