from .output import mDEV
from .config import Config, Actions, Vectors

class Robot():
    mdev = None
    config = None
    action_state = {
        "r": 0,
        "g": 0,
        "b": 0,
    }
    
    last_state = {
        "rlast": 0,
        "glast": 0,
        "blast": 0,
    }
    
    def __init__(self, config):
        self.mdev = mDEV()
        self.config = config
    
    def get_dict_value(self, dictionary, key):
        if key in dictionary:
            return dictionary[key]
        elif str(key) in dictionary:
            return dictionary[str(key)]
        else:
            return None
    
    def num_map(self, value, fromLow, fromHigh, toLow, toHigh):
        return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

    def set_led_state(self, led_name, led_state):
        if led_state == True:
            if self.last_state[led_name + "last"] != 1:
                if self.action_state[led_name] == 0:
                    self.action_state[led_name] = 1
                else:
                    self.action_state[led_name] = 0
            self.last_state[led_name + "last"] = 1
        else:
             self.last_state[led_name + "last"] = 0

    def set_action_state(self, state):
        self.set_led_state("r", self.get_dict_value(state["actions"], Actions.R_TOGGLE))
        self.set_led_state("g", self.get_dict_value(state["actions"], Actions.G_TOGGLE))
        self.set_led_state("b", self.get_dict_value(state["actions"], Actions.B_TOGGLE))
        
        self.mdev.writeReg(self.mdev.CMD_IO1, self.action_state["r"])
        self.mdev.writeReg(self.mdev.CMD_IO3, self.action_state["b"])
        self.mdev.writeReg(self.mdev.CMD_IO2, self.action_state["g"])
        
        if self.get_dict_value(state["actions"], Actions.BEEP) == True:
            self.mdev.writeReg(self.mdev.CMD_BUZZER, 2000)
        else:
            self.mdev.writeReg(self.mdev.CMD_BUZZER, 0)

    def set_motion(self, state):
        forward_value = self.get_dict_value(state["vectors"], Vectors.FORWARD) 
        reverse_value = self.get_dict_value(state["vectors"], Vectors.REVERSE) 
        #TODO make a tank mode where left and right motors can be spun indepedently
        if forward_value < 0.0:
            self.mdev.writeReg(self.mdev.CMD_DIR1,1)
            self.mdev.writeReg(self.mdev.CMD_DIR2,1)
            self.mdev.writeReg(self.mdev.CMD_PWM1, forward_value * -1000)
            self.mdev.writeReg(self.mdev.CMD_PWM2, forward_value * -1000)
        elif reverse_value > 0.0:
            self.mdev.writeReg(self.mdev.CMD_DIR1,0)
            self.mdev.writeReg(self.mdev.CMD_DIR2,0)
            self.mdev.writeReg(self.mdev.CMD_PWM1, reverse_value * 1000)
            self.mdev.writeReg(self.mdev.CMD_PWM2, reverse_value * 1000)
        else:
            self.mdev.writeReg(self.mdev.CMD_PWM1, 0.0)
            self.mdev.writeReg(self.mdev.CMD_PWM2, 0.0)
            
    def set_heading(self, state):
        l = self.get_dict_value(state["vectors"], Vectors.LEFT)
        r = self.get_dict_value(state["vectors"], Vectors.RIGHT)
        deg = 90
        if l < 0.0:
            deg =  90 + (l * 40)
        elif r > 0.0:
            deg = 90 + (r * 40)
        self.set_servo_angle(deg, self.mdev.CMD_SERVO1)
    
    def set_pan_tilt(self, state):
        u = self.get_dict_value(state["vectors"], Vectors.LOOK_UP)
        d = self.get_dict_value(state["vectors"], Vectors.LOOK_DOWN)
        l = self.get_dict_value(state["vectors"], Vectors.LOOK_LEFT)
        r = self.get_dict_value(state["vectors"], Vectors.LOOK_RIGHT)
        x = 90
        y = 90
        if l < 0.0:
            x =  90 + (l * 40)
        elif r > 0.0:
            x = 90 + (r * 40)
        if u < 0.0:
            y =  90 + (u * 40)
        elif d > 0.0:
            y = 90 + (d * 40)
        self.set_servo_angle(x, self.mdev.CMD_SERVO2)
        self.set_servo_angle(y, self.mdev.CMD_SERVO3)
                
    def set_servo_angle(self, angle, servo):
        self.mdev.writeReg(servo, self.num_map(angle, 0, 180, 500, 2500))
