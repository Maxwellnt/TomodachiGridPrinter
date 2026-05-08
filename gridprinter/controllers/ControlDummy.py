

from enum import Enum

from gridprinter.InputMap import InputMap, RStickInput, LStickInput


class ControlDummy():
    DEFAULT_MS_INPUT = 100
    DEFAULT_SLEEP_TIME = 100
    
    class ButtonIndex(Enum):
        Y = "A"
        X = "X"
        B = "B"
        A = "A"
        R = "R"
        ZR = "ZR"
        HOME = "HOME"
        CAPTURE = "CAPTURE"
        L = "L"
        ZL = "ZL"
        MINUS = "MINUS"
        PLUS = "PLUS"
        UP = "UP"
        UP_RIGHT = "UP_RIGHT"
        RIGHT = "RIGHT"
        RIGHT_DOWN = "RIGHT_DOWN"
        DOWN = "DOWN"
        DOWN_LEFT = "DOWN_LEFT"
        LEFT =  "LEFT" 
        LEFT_UP = "LEFT_UP"
    

    
    class JStickIndex(Enum):
        UP          = (0, 100)
        UP_RIGHT    = (-100, 100)
        RIGHT       = (100, 0)
        RIGHT_DOWN  = (-100, -100)
        DOWN        = (0, -100)    
        DOWN_LEFT   = (100, -100)
        LEFT        = (-100, 0)   
        LEFT_UP     = (100, 100)
    
    def __init__(self):
        pass
    
    
    def press_button(self, input : InputMap = InputMap.NONE, ms=DEFAULT_MS_INPUT, sleep_time=DEFAULT_SLEEP_TIME):
        pass
    
    def tilt_sticks(self, jstick : RStickInput|LStickInput, ms=DEFAULT_MS_INPUT, sleep_time=DEFAULT_SLEEP_TIME):
        pass
    
    def get_controller_selected(self):
        pass
    
    def close_connection(self):
        pass
    
    def sync(self):
        pass
    
    def resync_controller(self):
        pass