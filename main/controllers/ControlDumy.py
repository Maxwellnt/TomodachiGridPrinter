

from main.controllers.InputMap import InputMap


class ControlDummy():
    
    def __init__(self):
        pass
    
    
    def press(self, input : InputMap = InputMap.NONE, lx=128, ly=128, cx=128, cy=128, ms=100):
        pass
    
    def get_controller_selected(self):
        pass
    
    def close_connection(self):
        pass
    
    def sync(self):
        pass