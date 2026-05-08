
from enum import Enum
import logging
import serial
import time

from gridprinter.InputMap import InputMap, LStickInput, RStickInput
from gridprinter.controllers.ControlDummy import ControlDummy



"""
Abandone this 
"""

    
    
# TODO: Add enum for easy joystick directions (e.g. UP = ly=255, DOWN=ly=0, etc)


class ControllerManager(ControlDummy):
    DEFAULT_MS_INPUT = 120
    DEFAULT_SLEEP_TIME = 160
    class ButtonIndex(Enum):
        def __new__(cls, bit_shift, zone):
            obj = object.__new__(cls)
            obj._value_ = f"{bit_shift:02X} (zone {zone})"
            obj.bit_shift = bit_shift
            obj.zone = zone
            return obj

        NONE        = (8, 3)
        
        Y           = ((1 << 0), 2)
        X           = ((1 << 3), 2)
        B           = ((1 << 1), 2)
        A           = ((1 << 2), 2)
        R           = ((1 << 5), 2)
        ZR          = ((1 << 7), 2)
        
        HOME        = ((1 << 4), 1) # Not tested
        CAPTURE     = ((1 << 5), 1) # Not tested
        
        L           = ((1 << 4), 2)
        ZL          = ((1 << 6), 2)
        MINUS       = ((1 << 0), 1)
        PLUS        = ((1 << 1), 1)
        R_STICK     = ((1 << 3), 1)
        
        UP          = (0, 3)
        UP_RIGHT    = (1, 3)
        RIGHT       = (2, 3)
        RIGHT_DOWN  = (3, 3)
        DOWN        = (4, 3)    
        DOWN_LEFT   = (5, 3)
        LEFT        = (6, 3)    
        LEFT_UP     = (7, 3)
    
    class JStickIndex(Enum):
        UP          = (128, 0)
        UP_RIGHT    = (255, 255)
        RIGHT       = (255, 128)
        RIGHT_DOWN  = (255, 0)
        DOWN        = (128, 255)    
        DOWN_LEFT   = (0, 0)
        LEFT        = (0, 128)   
        LEFT_UP     = (0, 255)
    
    def __init__(self, port="/dev/ttyUSB0", baudrate=19200, timeout=1):
        self.serial = serial.Serial(port, baudrate, timeout=1)

    # ── Handshake (must be done before sending inputs) ──
    def sync(self):
        print("Syncing...")

        # Step 1: send SYNC_START (0xFF) and wait for 0xFF back
        self.serial.write(bytes([0xFF]))
        resp = self.serial.read(1)
        
        if resp == bytes([0x90]):
            print("Already synced (ESP32 was in SYNCED state), ready to go!")
            return
        elif resp == bytes([0x03]):
            print("Already in CHOCO_SYNCED state, ready to go!")
            return
        elif resp != bytes([0xFF]):
            if not resp.hex():
                logging.error("No response received during sync. Trying to force resync...")
                self.force_resync()
            else:
                raise Exception(f"Unexpected response during sync: Expected 0xFF, got {resp.hex()}")
        
        self.serial.write(bytes([0x44]))
        resp = self.serial.read(1)
        assert resp == bytes([0xEE]), f"Expected 0xEE, got {resp.hex()}"

        # Step 3: send 0xCC, expect 0x33 back → SYNCED
        self.serial.write(bytes([0xEE]))
        resp = self.serial.read(1)
        if resp == bytes([0x03]):
            print("CHOCO_SYNCED with PRO_CONTROLER")
        elif resp == bytes([0x01]):
            print("CHOCO_SYNCED with JOYCON_L")
        elif resp == bytes([0x02]):
            print("CHOCO_SYNCED with JOYCON_R")
        else:
            raise Exception(f"Expected controller type, got {resp.hex()}")


    
    def press_button(self, input : InputMap = InputMap.NONE,ms=DEFAULT_MS_INPUT, sleep_time=DEFAULT_SLEEP_TIME):
        
        button = self.ButtonIndex[input.value]
            
        self.send_input(**{"but"+str(button.zone): button.bit_shift})
        
        time.sleep(ms / 1000)
        self.send_input()   
        time.sleep(sleep_time/1000)
        
    def tilt_sticks(self, input_stick, ms=DEFAULT_MS_INPUT, sleep_time=DEFAULT_SLEEP_TIME):
        x = self.JStickIndex[input_stick.value].value[0]
        y = self.JStickIndex[input_stick.value].value[1]

        if isinstance(input_stick, RStickInput):
            self.send_input(but3=8, lx=128, ly=128, cx=x, cy=y)
        elif isinstance(input_stick, LStickInput):
            self.send_input(but3=8, lx=x, ly=y, cx=128, cy=128)
            
        time.sleep(ms / 1000)
        self.send_input()   
        time.sleep(sleep_time/1000)
        
    
    def get_controller_selected(self):
        # Press R+L to get the current controller type
        self.press_button(input=InputMap.R, ms=120, sleep_time=100)
        self.press_button(input=InputMap.L, ms=120, sleep_time=100)
        

    def force_resync(self):
        print("Forcing resync...")
        packet = [0, 0, 0, 128, 128, 128, 128, 0, 255]
        self.serial.write(bytes(packet))
        resp = self.serial.read(1)
        
        assert resp == bytes([0xFF]), f"Expected 0xFF, got {resp.hex()}"
        print("Resync successful, ready to sync again!")

        
    def send_input(self,but1=0, but2=0, but3=8,lx=128, ly=128, cx=128, cy=128):
        # ── CRC8 CCITT ──
        def crc8(data: list[int]) -> int:
            crc = 0
            for byte in data:
                crc ^= byte
                for _ in range(8):
                    if crc & 0x80:
                        crc = ((crc << 1) ^ 0x07) & 0xFF
                    else:
                        crc = (crc << 1) & 0xFF
            return crc
        
        packet = [but1, but2, but3, lx, ly, cx, cy, 0]
        packet.append(crc8(packet))      # 9th byte = CRC

        self.serial.write(bytes(packet))
        resp = self.serial.read(1)
        if resp == bytes([0x90]):
            pass  # UPDATE_ACK - all good
        elif resp == bytes([0x92]):
            print(f"Packet: {packet} ()")
            print("NACK - packet rejected (bad CRC?) {packet}")
        else:
            print(f"Unexpected response: {resp.hex()}")
            
    def close_connection(self):
        self.press_button()  # Send neutral input before closing
        self.serial.close()
