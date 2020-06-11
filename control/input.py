import pygame
import time
import os
from .config import Config, Vectors, Actions

class Input:
    index = 0
    config = None     
    
    def __init__(self, config, js_index):
        self.config = config
        if js_index != None:
            self.index = int(js_index)
        os.putenv('DISPLAY', ':0.0') 
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        print("Joystick index: {}\nJoystick count: {}".format(self.index, joystick_count))
        if self.index > joystick_count - 1:
            raise Exception("Joystick index out of range. {} was provided, which exceeds max allowable of {}".format(self.index, joystick_count))
        joystick = pygame.joystick.Joystick(self.index)
        joystick.init()
        name = joystick.get_name()
        print("Joystick connected: {}".format(name))
        
    
    def get_state(self):
        state = self.config.get_base_state()
        pygame.event.get()
        joystick = pygame.joystick.Joystick(self.index)
        joystick.init()
        axes = joystick.get_numaxes()
        buttons = joystick.get_numbuttons()
        hats = joystick.get_numhats()
        for i in range(axes):
            vector = None
            axis = joystick.get_axis(i)
            for key in self.config.AXIS_MAP:
                if key == i:
                    if axis < 0.0:
                        vector = self.config.AXIS_MAP[key][0]
                    else:
                        vector = self.config.AXIS_MAP[key][1]
                    if vector != None:
                        self.emit_event(vector, axis, state)
        for i in range(buttons):
            button = joystick.get_button(i)
            for key in self.config.ACTIONS_MAP:
                if key == i:
                    if button == 1:
                        self.emit_event(self.config.ACTIONS_MAP[key], button, state)
                       
        return state
                        
 
    def emit_event(self, event, axis, state):
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
        
