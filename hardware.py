import time
import board, busio, adafruit_bno055, adafruit_mcp4725, adafruit_ina219, adafruit_drv2605
from ina219 import INA219
from ina219 import DeviceRangeError

import numpy as np

class Hardware:

    def __init__(self):
        self.IMU_ADDRESS = 0x29
        self.DRV_ADDRESS = 0x5A
        self.METER_ADDRESS = '0x40'
        self.DACL_ADDRESS = 0x62
        self.DACR_ADDRESS = 0x63

        self.i2c = busio.I2C(board.SCL, board.SDA)
        devices = self.scan_bus()
        print(devices)
        if len(devices) == 0: print('* No I/O device found')

        if str(self.IMU_ADDRESS) in devices:
            print('* Motion sensor detected')
            self.motion = adafruit_bno055.BNO055_I2C(self.i2c, self.IMU_ADDRESS)
        else: 
            self.motion = None
        
        if str(self.DRV_ADDRESS) in devices:
            haptic = adafruit_drv2605.DRV2605(self.i2c, self.DRV_ADDRESS)
            haptic.mode(0x03) # Analog/PWM Mode
            haptic.use_LRM() 
            print('* Haptic driver detected (and set to analog mode)')
        else:
            self.haptic = None
    
        if str(self.METER_ADDRESS) in devices:
            self.meter = INA219(0.1, 3)
            self.meter.configure(self.meter.RANGE_16V)
            print('* Current sensor detected')
        else: 
            self.meter = None

        if str(self.DACL_ADDRESS) in devices:
            self.leftDAC = adafruit_mcp4725.MCP4725(self.i2c, self.DACL_ADDRESS)
            print('* Left DAC detected')
        else: 
            self.leftDAC = None

        if str(self.DACL_ADDRESS) in devices:
            self.rightDAC = adafruit_mcp4725.MCP4725(self.i2c, self.DACR_ADDRESS)
            print('* Left DAC detected')
        else:
            self.rightDAC = None

    def has_haptic(self):
        return self.haptic != None

    def has_motion(self):
        return self.motion != None

    def has_meter(self):
        return self.meter != None

    def has_left_dac(self):
        return self.leftDAC != None

    def has_right_dac(self):
        return self.rightDAC != None
    
    def scan_bus(self):
        return [hex(x) for x in self.i2c.scan()]

    def read_imu(self):
        if self.motion != None:
            acc = list(self.motion.acceleration)
            gyro = list(self.motion.gyro)
            mag = list(self.motion.magnetic)
            return acc, gyro, mag
        else: raise Exception('Motion sensor not available !')

    def read_power(self):
        if self.meter != None:
            voltage = abs(self.meter.voltage())
            current = round(abs(self.meter.current()),2)
            power = round(self.meter.power(), 2)
            return voltage, current, power
        else: raise Exception('Power sensor not available !')







  