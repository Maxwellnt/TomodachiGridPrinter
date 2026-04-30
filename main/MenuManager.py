from enum import Enum
import os
import json
import logging

from main.controllers.InputMap import InputMap, JStickInput

class UpperMenu(Enum):
    UNDO = 0
    REDO = 1
    MOVE = 2 # First Tool
    SELECT = 3
    TEXT = 4
    STAMPS = 5
    SHAPES = 6
    FILL = 7
    BRUSH = 8
    ERASER = 9
    PICKER = 10 # Last Tool
    EFFECTS = 11
    SETTINGS = 12
    DONE = 13

class BrushType(Enum):
    SMOOTH = "smooth"
    SHADOW = "shadow"
    PIXEL = "pixel"


class MenuManager:
    def __init__(self, gird_json_path:str):
        if not os.path.isfile(gird_json_path):
            raise ValueError("The provided path does not exist or is not a file.")

        with open(gird_json_path, 'r') as file:
            canvas_data : dict = json.load(file)
            # Validating the JSON structure
            
            if not canvas_data.get("source") == "living-the-grid.com":  
                logging.warning("The JSON source is not from 'living the grid'. The structure might be different than expected.")
            if not canvas_data.get("version") == 2:
                logging.warning("The JSON version is not 1. The structure might be different than expected.")
        
            self.brush = canvas_data["brush"]
        
            self.canvas_width = canvas_data["width"]
            self.canvas_height = canvas_data["height"]

            self.palette = canvas_data["palette"]
            self.pixels = canvas_data["pixels"]

        self.selected_tool = UpperMenu.BRUSH.value
        self.selelected_palette = None
        self.selelected_ingame_palette = 0
        self.ingame_palette = [None, None, None, None, None, None, None, None, None]

    
    def delta_inputs(self, delta_value:int, positive_input: InputMap|JStickInput, negative_input: InputMap|JStickInput):
        if delta_value >= 0:
            input_value = positive_input
        else:
            input_value = negative_input
    
            
        for _ in range(abs(delta_value)):
            yield input_value
    
    def select_ingame_color(self, new_index=None, new_color=None, select_color=False):
        yield InputMap.Y
        
        if new_color:
            new_index = self.ingame_palette.index(new_color)
            
        
        delta_index = new_index - self.selelected_ingame_palette
        
        yield from self.delta_inputs(delta_index, InputMap.DOWN, InputMap.UP)

        if select_color:
            yield InputMap.A
            self.selelected_ingame_palette = new_index
    
    def edit_ingame_color(self, color_data: dict, reset=True, old_color_data: dict|None=None, palette_menu_active=False):   
        if not palette_menu_active:
            yield InputMap.Y
            
        yield InputMap.Y
        yield InputMap.R
        
        hsb_new_color = color_data["press"]
        
        if reset:
            if hsb_new_color["h"] > (201/2):
                yield InputMap.ZR, 4000
                input_for_h = InputMap.ZL
                steps_h = 201 - hsb_new_color["h"]
            else: 
                yield InputMap.ZL, 4000
                input_for_h = InputMap.ZR
                steps_h = hsb_new_color["h"]
            
            if hsb_new_color["s"] > (211/2):
                yield JStickInput.RIGHT, 4000
                input_for_s = InputMap.LEFT
                steps_s = 211 - hsb_new_color["s"]
            else:
                yield JStickInput.LEFT, 4000
                input_for_s = InputMap.RIGHT
                steps_s = hsb_new_color["s"]
                
            if hsb_new_color["b"] > (110/2):
                yield JStickInput.UP, 4000
                input_for_b = InputMap.DOWN
                steps_b = 110 - hsb_new_color["b"]
            else:
                yield JStickInput.DOWN, 4000
                input_for_b = InputMap.UP
                steps_b = hsb_new_color["b"]    
            
            
        elif old_color_data is not None:
            logging.debug("Using delta selector")
            hsb_old_color = old_color_data["press"]

        for _ in range(steps_h):
            yield input_for_h

        for _ in range(steps_s):
            yield input_for_s
                
        for _ in range(steps_b):
            yield input_for_b   
        
        yield InputMap.A
        
        
    def old_color_picker(self, palette_index:int):
        
                
    
        # Acces to the palet
        yield InputMap.Y
        yield InputMap.Y
        
        yield InputMap.R
        
        
        
        color = self.palette[palette_index]["press"]
        
        # Selected palete: H 
        
        if self.selelected_palette is not None:
            delta_h = color["h"] - self.selelected_palette["h"]
            delta_s = color["s"] - self.selelected_palette["s"]
            delta_b = color["b"] - self.selelected_palette["b"]
            
            for h_input in self.delta_inputs(delta_h, positive_input=InputMap.ZR, negative_input=InputMap.ZL):
                yield h_input
            for s_input in self.delta_inputs(delta_s, positive_input=InputMap.RIGHT, negative_input=InputMap.LEFT):
                yield s_input
            for b_input in self.delta_inputs(delta_b, positive_input=InputMap.UP, negative_input=InputMap.DOWN):
                yield b_input
        else:
            yield JStickInput.DOWN_LEFT, 5000
            yield InputMap.ZL, 5000
        
            for _ in range(color["h"]):
                yield InputMap.ZR, 100

            for _ in range(color["s"]):
                yield InputMap.RIGHT
                
            for _ in range(color["b"]):
                yield InputMap.UP
            
        yield InputMap.A
        self.selelected_palette = color
        
    def select_tool(self, new_tool:UpperMenu, select=True):
        yield InputMap.X
        
        delta_tool_index = new_tool.value - self.selected_tool
        
        for input_command in self.delta_inputs(delta_tool_index, InputMap.RIGHT, InputMap.LEFT):
            yield input_command
        
        self.selected_tool = new_tool.value
        
        if select:
            yield InputMap.A
    
    def select_brush(self, brush_type:str = None, brush_size:str = None):
        # This will fail if the brush is already the selected type
        
        if brush_type is None:
            brush_type = self.brush.get("mode")
        if brush_size is None:
            brush_size = self.brush.get("px")
        
        # Enter the brush menu
        yield InputMap.X
        yield InputMap.X
        
        # Select the brush type
        yield InputMap.UP
        yield InputMap.UP
        
        # TODO: Remove hardcode inputs
        # At the start of every paint the smooth brush is selected
        if brush_type == "pixel":
            for _ in range(3):
                yield InputMap.RIGHT
            yield InputMap.A
                
        if brush_type == "shadow":
            yield InputMap.LEFT
            yield InputMap.A    
        
        # Select the brush form (square)
        yield InputMap.DOWN
        yield InputMap.DOWN
        
        # 5 Smooth
        # 3
        for _ in range( 3 if brush_type == BrushType.PIXEL.value else 5 ):
            yield InputMap.LEFT
            
        if brush_size >= 8:
            yield InputMap.RIGHT
        if brush_size >= 16:
            yield InputMap.RIGHT
        if brush_size >= 32:
            yield InputMap.RIGHT
        
        yield InputMap.A
        yield InputMap.A # Exit the menu
        
    def set_cusor_to_zero(self):
        # Lets get the cursor to 0,0
        for _ in range( int(self.canvas_width / 2) ):
            yield InputMap.LEFT
            
        for _ in range( int(self.canvas_height / 2) ):
            yield InputMap.UP
    
    
    
    def get_movement_instructions_strat_1(self):
        # Make the movement be rizg-zag, so we dont have to move all the way to the left after each row
        
        for pallete_index in range(len(self.palette)):
            for command in self.old_color_picker(pallete_index):
                yield command
            
            is_right = True
        
            for row_index in range(len(self.pixels)):
                logging.info(f"Processing row {row_index+1}/{len(self.pixels)}")
                # If the row is empty then move down and dont reverse the direction
            
                if any(( pixel is not None ) or ( pixel is not pallete_index ) for pixel in self.pixels[row_index]):   
                
                    row = self.pixels[row_index] if is_right else list(reversed(self.pixels[row_index]))
                    for pixel_index in range(len(row)):
                        if row[pixel_index] is not None or row[pixel_index] is not pallete_index:
                            yield InputMap.A
                        
                        if pixel_index != len(row) - 1:
                            if is_right:
                                yield InputMap.RIGHT
                            else:
                                yield InputMap.LEFT
                        
                    is_right ^= True
                yield InputMap.DOWN
                
            if not is_right:
                # Cursos is in the bottom_right
                for _ in range(self.canvas_width):
                    yield InputMap.LEFT
            for _ in range(self.canvas_height):
                yield InputMap.UP
            
    def get_movement_instructions_strat_2(self, ingame_palette_size=9):
        n = ingame_palette_size
        palette_chunks = [self.palette[i:i + n] for i in range(0, len(self.palette), n)]
        
        for mini_palette in palette_chunks:
            for mini_palette_index in range(len(mini_palette)):
        
                yield from self.select_ingame_color(mini_palette_index, select_color=True)
                yield from self.edit_ingame_color(mini_palette[mini_palette_index])
                self.ingame_palette[mini_palette_index] = mini_palette[mini_palette_index]
                
        
            is_right = True
        
            for row_index in range(len(self.pixels)):
                #logging.info(f"Processing row {row_index+1}/{len(self.pixels)}")
                # If the row is empty then move down and dont reverse the direction
                
                if any(pixel_color is not None and self.palette[pixel_color] in self.ingame_palette for pixel_color in self.pixels[row_index]):   
                    
                    row = self.pixels[row_index] if is_right else list(reversed(self.pixels[row_index]))
                    
                    for pixel_index in range(len(row)):
                        if (row[pixel_index] is not None and self.palette[row[pixel_index]] in self.ingame_palette):
                            
                            if self.ingame_palette[self.selelected_ingame_palette] is not self.palette[row[pixel_index]]:
                                yield from self.select_ingame_color(new_color=self.palette[row[pixel_index]], select_color=True)
                                
                            yield InputMap.A
                            
                        if pixel_index != len(row) - 1:
                            if is_right:
                                yield InputMap.RIGHT
                            else:
                                yield InputMap.LEFT
                    
                    is_right ^= True
                yield InputMap.DOWN
                
            if not is_right:
                # Cursos is in the bottom_right
                for _ in range(self.canvas_width):
                    yield InputMap.LEFT
            for _ in range(self.canvas_height):
                yield InputMap.UP
                

    def switch_menu(self, name):
        if name in self.menus:
            self.current_menu = self.menus[name]
            self.current_menu.display()
        else:
            print(f"Menu '{name}' not found.")

    def get_current_menu(self):
        return self.current_menu