

import time
from typing import Generator
import serial
import threading
import logging
from main.MenuManager import MenuManager, UpperMenu
from main.controllers.ControlDumy import ControlDummy
from main.controllers.InputMap import InputMap, JStickInput
from main.controllers.Nuxbt import NuxbtController
from main.controllers.UARTSwitchCon import ControllerManager
import argparse


# V.0 Total inputs 293059
# V.1 Total inputs 75000~ 
# V.2 Total inputs 75710
# V.3 Total inputs 125789

# V.4 Total inputs 15786
# V.4 Total inputs 10014
def prosses_inputs(cm:ControllerManager, inputs:list | Generator):
    global input_count
    
    for controler_command in inputs:
        if isinstance(controler_command, tuple):
            ms = controler_command[1]
            input_command = controler_command[0]
        else:
            ms = 110
            input_command = controler_command
            
        if isinstance(input_command, InputMap):
            print(f"{input_command}")
            cm.press(input_command, ms=ms)
            input_count += 1
        elif isinstance(input_command, JStickInput):
            cm.press(lx=input_command.value[0], ly=input_command.value[1], ms=ms)
            input_count += 1
           
        

if __name__ == "__main__":
    # Instantiate the parser
    
    
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('json_grid', type=str, help='Path to the grid JSON file')
    parser.add_argument('--port', type=str, default="/dev/ttyUSB0", help='Serial port to connect to (default: /dev/ttyUSB0)')
    parser.add_argument('--test', action='store_true',  help="Dosne't Connecto to a controller it only counts the number of inputs")
    args = parser.parse_args()
    
    if args.test:
        cm = ControlDummy()
    else:
        cm = NuxbtController()
    mm = MenuManager(args.json_grid)
    
    input_count = 0

    try:
        cm.sync()
        time.sleep(1)  # Give some time for the connection to stabilize
        if not args.test:
            pair_question = input("Do you need to sync the controller [Y/N]")
            if pair_question.upper() == "Y":
                cm.get_controller_selected()
                time.sleep(1)
                cm.press(InputMap.A, ms=200)
                
            reset_question = input("Do you need to reset the canvas [Y/N]")
            if reset_question.upper() == "Y":
                cm.press(InputMap.B, ms=100)
                time.sleep(0.5)
                cm.press(InputMap.MINUS, ms=100)
                time.sleep(2)
                cm.press(InputMap.A, ms=100)
                time.sleep(2)
                cm.press(InputMap.LEFT, ms=100)
                cm.press(InputMap.A, ms=100)
                time.sleep(2)
                cm.press(InputMap.A, ms=100)
                time.sleep(1)
                cm.press(InputMap.A, ms=100)
                time.sleep(1)
                cm.press(InputMap.A, ms=100)
                time.sleep(2)
                cm.press(InputMap.A, ms=100)
                time.sleep(3)
                
        prosses_inputs(cm, mm.select_tool(UpperMenu.BRUSH))
        prosses_inputs(cm, mm.select_brush())
                
        prosses_inputs(cm, mm.set_cusor_to_zero())
        

        prosses_inputs(cm, mm.get_movement_instructions_strat_2(ingame_palette_size=9))
    

        
    finally:
        logging.info(f"Total inputs {input_count}")
        cm.press()   # release everything
        cm.close_connection()
        logging.info("Serial connection closed, successfully exited.")
        
    

      