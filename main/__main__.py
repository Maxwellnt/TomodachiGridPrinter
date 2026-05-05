

import time
from typing import Generator
import serial
import threading
import logging
from main.MenuManager import MenuManager, UpperMenu
from main.controllers.ControlDummy import ControlDummy
from main.InputMap import InputMap, RStickInput, LStickInput
from main.controllers.Nuxbt import NuxbtController
from main.controllers.UARTSwitchCon import ControllerManager
import argparse


logging.basicConfig(level=logging.INFO)
# V.0 Total inputs 293059
# V.1 Total inputs 75000~ 
# V.2 Total inputs 75710
# V.3 Total inputs 125789

# V.4 Total inputs 15786
# V.4 Total inputs 10014
def proses_inputs(cm: ControlDummy, inputs:list | Generator):
    global input_count
    global time_count
    
    for controller_command in inputs:
        if isinstance(controller_command, tuple):
            ms = controller_command[1]
            input_command = controller_command[0]
        else:
            ms = 100
            input_command = controller_command
            
        if isinstance(input_command, InputMap):

            cm.press_button(input_command, ms=ms)
            input_count += 1
            time_count += ms
        elif isinstance(input_command, RStickInput) or isinstance(input_command, LStickInput):
            cm.tilt_sticks(input_command, ms=ms)
            input_count += 1
            time_count += ms
        
        if input_count % 1000 == 0:
            cm.resync_controller()
        

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
    time_count = 0
    if not args.test:
        input("Did you go to the item category you want?")
        input("Did you disconnect your controllers?")
    try:
        cm.sync()
        time.sleep(1)  # Give some time for the connection to stabilize
        if not args.test:
            cm.get_controller_selected()
            time.sleep(2)
            cm.press_button(InputMap.A, ms=100)
            time.sleep(3)
                
            
        proses_inputs(cm, mm.reset_canvas())        
        proses_inputs(cm, mm.select_tool(UpperMenu.BRUSH))
        proses_inputs(cm, mm.select_brush())
                
        proses_inputs(cm, mm.set_cusor_to_zero())
        

        proses_inputs(cm, mm.get_movement_instructions_strat_2(ingame_palette_size=9))
    

        
    finally:
        logging.info(f"Total inputs {input_count}")
        logging.info(f"Total time lapsed {(time_count/1000)/60:.2f} mins")
        cm.close_connection()
        logging.info("Serial connection closed, successfully exited.")
        
    

      