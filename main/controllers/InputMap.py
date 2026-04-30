
from enum import Enum


class InputMap(Enum):
    NONE        = "NONE"
    
    Y           = "Y"
    B           = "B"
    A           = "A"
    X           = "X"
    L           = "L"
    R           = "R"
    ZL          = "ZL"
    ZR          = "ZR"
    GL          = "GL"
    GR          = "GR"
    HOME        = "HOME"
    CAPTURE     = "CAPTURE"
    MINUS       = "MINUS"
    PLUS        = "PLUS"
    R_STICK     = "R_STICK"
    L_STICK     = "L_STICK"
    
    UP          = "UP"
    UP_RIGHT    = "UP_RIGHT"
    RIGHT       = "RIGHT"
    RIGHT_DOWN  = "RIGHT_DOWN"
    DOWN        = "DOWN"    
    DOWN_LEFT   = "DOWN_LEFT"
    LEFT        = "LEFT"   
    LEFT_UP     = "LEFT_UP"
    
class JStickInput(Enum):
    UP          = (0, 100)
    UP_RIGHT    = (-100, 100)
    RIGHT       = (-100, 0)
    RIGHT_DOWN  = (-100, -100)
    DOWN        = (0, -100)    
    DOWN_LEFT   = (100, -100)
    LEFT        = (100, 0)   
    LEFT_UP     = (100, 100)