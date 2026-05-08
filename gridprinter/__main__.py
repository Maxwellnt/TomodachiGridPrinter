

import time
from typing import Generator
import serial
import threading
import logging
from gridprinter.MenuManager import MenuManager, UpperMenu
from gridprinter.controllers.ControlDummy import ControlDummy
from gridprinter.InputMap import InputMap, RStickInput, LStickInput
from gridprinter.controllers.Nuxbt import NuxbtController
from gridprinter.controllers.UARTSwitchCon import ControllerManager
import argparse


logging.basicConfig(level=logging.INFO)

DEFAULT_MS_INPUT = 100
DEFAULT_SLEEP_TIME = 100

def proses_inputs(cm: ControlDummy, inputs:list | Generator):
    global input_count
    global time_count
    
    for controller_command in inputs:
        if isinstance(controller_command, tuple):
            input_command = controller_command[0]
            ms = controller_command[1] or cm.DEFAULT_MS_INPUT
            if len(controller_command) > 2:
                sleep_time = controller_command[2] or cm.DEFAULT_SLEEP_TIME
            else:
                sleep_time = cm.DEFAULT_SLEEP_TIME
        else:
            ms = cm.DEFAULT_MS_INPUT
            sleep_time = cm.DEFAULT_SLEEP_TIME
            input_command = controller_command
            
        logging.info(f"Processing input: {input_command}, ms: {ms}, sleep_time: {sleep_time}")
        if isinstance(input_command, InputMap):

            cm.press_button(input_command, ms=ms, sleep_time=sleep_time)
            input_count += 1
            time_count += (ms + sleep_time)
        elif isinstance(input_command, RStickInput) or isinstance(input_command, LStickInput):
            cm.tilt_sticks(input_command, ms=ms, sleep_time=sleep_time)
            input_count += 1
            time_count += (ms + sleep_time)
        
        if input_count % 1000 == 0:
            cm.resync_controller()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optional app description')
    
    parser.add_argument('json_grid', type=str, help='Path to the grid JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Add more verbose logging')
    parser.add_argument('--controller', type=str, choices=['nuxbt', 'uart', 'dry-run'], default='nuxbt', help='Controller type to use (default: nuxbt)')
    parser.add_argument('--port', type=str, default="/dev/ttyUSB0", help='Serial port to connect to (default: /dev/ttyUSB0)')
    

    args = parser.parse_args()
    
    
    if args.controller != 'dry-run':
        input("Make sure to be in the right category, as the program will just press buttons without any feedback. Press Enter to continue...")
        input("Make sure to disconnect your controllers, If not press the 'sync' button one time to power them off. Press Enter to continue...")
    
    if args.controller == 'dry-run': 
        cm = ControlDummy()
    elif args.controller == 'nuxbt':
        cm = NuxbtController()
    elif args.controller == 'uart':
        cm = ControllerManager(port=args.port)
    else:
        raise ValueError("Invalid controller type")    
            
    mm = MenuManager(args.json_grid)
    
    input_count = 0
    time_count = 0
    
    try:
        cm.sync()
        time.sleep(1)  # Give some time for the connection to stabilize
        if args.controller != 'dry-run':
            input("Has your been selected? Press Enter to continue...")
            
            cm.get_controller_selected()
            time.sleep(2)
            proses_inputs(cm=cm, inputs=[(InputMap.A, 100, 2000)])
                
            reset_canvas=input("Is your canvas in an inconsent state? This will exit any windows and reset the canvas [Y/N]")
            
            if reset_canvas.upper() == 'Y':
                # Restore tool selection
                
                proses_inputs(cm=cm, inputs=[InputMap.B, InputMap.B])
                
                proses_inputs(cm, mm.select_tool(UpperMenu.UNDO))
                proses_inputs(cm, mm.select_tool(UpperMenu.BRUSH))
                
                # Restore palette selection
                proses_inputs(cm, mm.select_ingame_color(new_index=9, select_color=True))
                proses_inputs(cm, mm.select_ingame_color(new_index=0, select_color=True))
                
                proses_inputs(cm, mm.reset_canvas())  
                
              
        proses_inputs(cm, mm.select_tool(UpperMenu.BRUSH))
        proses_inputs(cm, mm.select_brush())
                
        proses_inputs(cm, mm.set_cusor_to_zero())
        proses_inputs(cm, mm.get_movement_instructions_strat_2(ingame_palette_size=9))
    

        
    finally:
        logging.info(f"Total inputs {input_count}")
        logging.info(f"Total time lapsed {(time_count/1000)/60:.2f} mins")
        cm.close_connection()
        logging.info("Connection closed, successfully exited.")
        
    

      