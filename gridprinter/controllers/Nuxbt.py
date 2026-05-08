

from enum import Enum
import time
import logging

from gridprinter.controllers.ControlDummy import ControlDummy
from gridprinter.InputMap import InputMap, RStickInput, LStickInput

import nuxbt
from nuxbt import Sticks, Buttons



# Done with https://github.com/hannahbee91/nuxbt
class NuxbtController(ControlDummy):
    DEFAULT_MS_INPUT = 100
    DEFAULT_SLEEP_TIME = 100
    
    class ButtonIndex(Enum):
        Y = Buttons.Y
        X = Buttons.X
        B = Buttons.B
        A = Buttons.A
        R = Buttons.R
        ZR = Buttons.ZR
        HOME = Buttons.HOME
        CAPTURE = Buttons.CAPTURE
        L = Buttons.L
        ZL = Buttons.ZL
        MINUS = Buttons.MINUS
        PLUS = Buttons.PLUS
        UP = Buttons.DPAD_UP
        UP_RIGHT = None
        RIGHT = Buttons.DPAD_RIGHT
        RIGHT_DOWN = None
        DOWN = Buttons.DPAD_DOWN
        DOWN_LEFT = None
        LEFT =  Buttons.DPAD_LEFT   
        LEFT_UP = None
    
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
        self.nx = nuxbt.Nuxbt(log_file_path=True, debug=False)
        self.controller_index = self.nx.create_controller(nuxbt.PRO_CONTROLLER)
        
    def press_button(self, input : InputMap = InputMap.NONE, ms=DEFAULT_MS_INPUT, sleep_time=DEFAULT_SLEEP_TIME):
        if input is not InputMap.NONE:
            self.nx.press_buttons(self.controller_index, [self.ButtonIndex[input.value].value],down=ms/1000, up=sleep_time/1000)
        
            
    def tilt_sticks(self, input_stick: RStickInput|LStickInput, ms=DEFAULT_MS_INPUT, sleep_time=DEFAULT_SLEEP_TIME):
        if isinstance(input_stick, RStickInput):
            stick = Sticks.RIGHT_STICK
        elif isinstance(input_stick, LStickInput):
            stick = Sticks.LEFT_STICK
            
        x = self.JStickIndex[input_stick.value].value[0]
        y = self.JStickIndex[input_stick.value].value[1]
        
        self.nx.tilt_stick(self.controller_index, stick, x, y, tilted=ms/1000, released=sleep_time/1000)
    
    def get_controller_selected(self):
        pass
    
    def close_connection(self):
        self.nx.remove_controller(self.controller_index)
    
    def sync(self):
        self.nx.wait_for_connection(self.controller_index)
        
    def resync_controller(self):
        logging.info("Cleaning all macros")
        self.nx.clear_all_macros()
    