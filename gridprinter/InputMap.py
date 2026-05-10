
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


class RStickInput(Enum):
    UP          = "UP"
    UP_RIGHT    = "UP_RIGHT"
    RIGHT       = "RIGHT"
    RIGHT_DOWN  = "RIGHT_DOWN"
    DOWN        = "DOWN" 
    DOWN_LEFT   = "DOWN_LEFT"
    LEFT        = "LEFT"
    LEFT_UP     = "LEFT_UP"

class LStickInput(Enum):
    UP          = "UP"
    UP_RIGHT    = "UP_RIGHT"
    RIGHT       = "RIGHT"
    RIGHT_DOWN  = "RIGHT_DOWN"
    DOWN        = "DOWN" 
    DOWN_LEFT   = "DOWN_LEFT"
    LEFT        = "LEFT"
    LEFT_UP     = "LEFT_UP"