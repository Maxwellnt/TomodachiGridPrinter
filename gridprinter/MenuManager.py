from enum import Enum
import os
import json
import logging
import time

from gridprinter.InputMap import InputMap, LStickInput, RStickInput

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
        elif not gird_json_path.endswith('.json'):
            raise ValueError("The provided file is not a JSON file.")
        
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
        self.selected_palette = None
        self.selected_ingame_palette_index = 0
        
        self.x_cursor = int(self.canvas_width/2)
        self.y_cursor = int(self.canvas_height/2)
        
        self.ingame_canvas = [[None] * self.canvas_height] * self.canvas_width
        self.ingame_palette = [{}] * 9
        
        self.color_quantity = self.count_colors_in_canvas()
    
    def delta_inputs(self, 
                     delta_value:int, 
                     positive_input: InputMap|RStickInput|LStickInput, 
                     negative_input: InputMap|RStickInput|LStickInput, sleep_time=0):
        if delta_value >= 0:
            input_value = positive_input
        else:
            input_value = negative_input
    
            
        for _ in range(abs(delta_value)):
            # Added Sleep time to make the palette selection more reliable
            yield input_value, 100, sleep_time
            
    def count_colors_in_canvas(self):
        color_count = {}
        for row in self.pixels:
            for pixel in row:
                if pixel is not None:
                    if pixel in color_count:
                        color_count[pixel] += 1
                    else:
                        color_count[pixel] = 1
        return color_count    
            
    def select_ingame_color(self, new_index=None, new_color=None, select_color=False):
        yield InputMap.Y
        
        if new_color:
            new_index = self.ingame_palette.index(new_color)
            
        assert new_index is not None, "Either new_index or new_color must be provided."
        
        delta_index = new_index - self.selected_ingame_palette_index
        
        yield from self.delta_inputs(delta_index, InputMap.DOWN, InputMap.UP, sleep_time=200)

        if select_color:
            yield InputMap.A
            self.selected_ingame_palette_index = new_index
    
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
                yield LStickInput.RIGHT, 4000
                input_for_s = InputMap.LEFT
                steps_s = 211 - hsb_new_color["s"]
            else:
                yield LStickInput.LEFT, 4000
                input_for_s = InputMap.RIGHT
                steps_s = hsb_new_color["s"]
                
            if hsb_new_color["b"] > (110/2):
                yield LStickInput.UP, 4000
                input_for_b = InputMap.DOWN
                steps_b = 110 - hsb_new_color["b"]
            else:
                yield LStickInput.DOWN, 4000
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
        
    def select_tool(self, new_tool:UpperMenu, select=True):
        yield InputMap.X, None, 150
        
        delta_tool_index = new_tool.value - self.selected_tool
        
        yield from self.delta_inputs(delta_tool_index, InputMap.RIGHT, InputMap.LEFT, sleep_time=200)
        
        self.selected_tool = new_tool.value
        
        if select:
            yield InputMap.A
    
    def select_brush(self, brush_type:str|None = None, brush_size:int|None = None):        
        if brush_type is None:
            brush_type = self.brush.get("mode")
        if brush_size is None:
            brush_size = self.brush.get("px")
        
        if brush_type is None or brush_size is None:
            logging.error("Brush type or size not found in JSON. Using default values.")
            raise ValueError("Brush type or size not found in JSON.")
        
        # Enter the brush menu
        yield InputMap.X
        yield InputMap.X
        
        # Select the brush type
        yield InputMap.UP
        yield InputMap.UP
        

        yield from [InputMap.RIGHT] * 3
        yield InputMap.LEFT
        yield InputMap.A
        
        if brush_type == BrushType.SMOOTH.value:
            yield InputMap.LEFT
        elif brush_type == BrushType.PIXEL.value:
            yield InputMap.RIGHT
        
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
        
        # This combo ensures synchronization between if the size is already selected or not
        yield InputMap.A
        yield InputMap.X
        yield InputMap.A
            
    def get_movement_instructions(self, ingame_palette_size=9):
        # TODO: Clean this up, its really hard to read. Maybe split the logic in diferent functions?
        # Even the AI suggestions is ashamed of this code
        
        n = ingame_palette_size
        palette_chunks = [self.palette[i:i + n] for i in range(0, len(self.palette), n)]
        
        for mini_palette in palette_chunks:
            for mini_palette_index in range(len(mini_palette)):
        
                yield from self.select_ingame_color(mini_palette_index, select_color=True)
                yield from self.edit_ingame_color(mini_palette[mini_palette_index])
                self.ingame_palette[mini_palette_index] = mini_palette[mini_palette_index]
                
            if self.y_cursor > self.canvas_height/2:
                range_y = range(len(self.pixels)-1, 0, -1)
            else:
                range_y = range(len(self.pixels))

            for row_index in range_y:
                to_y = row_index
                
                if self.x_cursor > self.canvas_width/2:
                    range_x = range(len(self.pixels[row_index])-1, 0, -1)
                else:
                    range_x = range(len(self.pixels[row_index]))

                for pixel_index in range_x:
                    to_x = pixel_index
                                        
                    if self.pixels[to_y][to_x] is not None and self.palette[self.pixels[to_y][to_x]] in self.ingame_palette:
                        yield from self.move_to_cords(x_target=to_x, y_target=to_y)
                        
                        new_color = self.palette[self.pixels[to_y][to_x]]
                        
                        assert self.selected_ingame_palette_index is not None
                        current_color = self.ingame_palette[self.selected_ingame_palette_index]
                        
                        if current_color is not new_color:
                            yield from self.select_ingame_color(new_color=new_color, select_color=True)
                        
                        yield InputMap.A
                        
                        self.ingame_canvas[to_y][to_x] = new_color
                        self.color_quantity[self.pixels[to_y][to_x]] -= 1
        
    def move_to_cords(self, x_target, y_target):
        delta_x = x_target - self.x_cursor
        delta_y = y_target - self.y_cursor
        
        for input_command in self.delta_inputs(delta_x, InputMap.RIGHT, InputMap.LEFT):
            yield input_command
            
        for input_command in self.delta_inputs(delta_y, InputMap.DOWN, InputMap.UP):
            yield input_command
            
        self.x_cursor = x_target
        self.y_cursor = y_target
    
    
    
    def reset_canvas(self):
        yield from [(InputMap.B, None, 500), (InputMap.B, None, 500)]
        
        yield from self.select_tool(UpperMenu.UNDO, select=False)
        yield from self.select_tool(UpperMenu.BRUSH, select=True)
                
        yield from self.select_ingame_color(new_index=8, select_color=True)
        yield from self.select_ingame_color(new_index=0, select_color=True)         
        
        yield LStickInput.UP, 2000
        yield from self.select_tool(UpperMenu.ERASER,select=False)
        
        yield InputMap.X
        
        yield InputMap.UP
        yield InputMap.UP
        yield InputMap.UP

        
        yield InputMap.DOWN
        yield InputMap.DOWN
        yield InputMap.DOWN
        
        yield InputMap.A, 100, 1000
        # Tomodachi Quirk: When deleting all, brush gets automatically selected
        self.selected_tool = UpperMenu.BRUSH.value
    