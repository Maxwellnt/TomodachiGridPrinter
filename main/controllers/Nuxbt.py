

from enum import Enum

from main.controllers.InputMap import InputMap

import nuxbt
from nuxbt import Sticks, Buttons

class ButtonIndex_Nuxbt(Enum):
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

# Done with https://github.com/hannahbee91/nuxbt
class NuxbtController():
    def __init__(self):
        self.nx = nuxbt.Nuxbt(disable_logging=True)
        # Create a Pro Controller and wait for it to connect
        
    def press(self, input : InputMap = InputMap.NONE, lx=0, ly=0, cx=0, cy=0, ms=100):
        if input is not InputMap.NONE:
            self.nx.press_buttons(self.controller_index, [ButtonIndex_Nuxbt[input.value].value],down=ms/1000)
        else:
            self.nx.tilt_stick(self.controller_index, Sticks.LEFT_STICK, lx, ly, tilted=ms/1000)

    
    def get_controller_selected(self):
        pass
    
    def close_connection(self):
        self.nx.remove_controller(self.controller_index)
    
    def sync(self):
        self.controller_index = self.nx.create_controller(nuxbt.PRO_CONTROLLER)
        self.nx.wait_for_connection(self.controller_index)