# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from dataclasses import dataclass
import datetime




DEFAULT_SERIAL_PORT="COM4"
DEFAULT_BAUD_RATE=9600


# Reading PZEM-004t power sensor (new version v3.0) through Modbus-RTU protocol over TTL UART
# Run as:
# python3 pzem_004t.py

# To install dependencies: 
# pip install modbus-tk
# pip install pyserial

@dataclass
class Reading:
    timestamp:datetime.datetime
    voltage:float
    current:float
    power:float
    power_factor:float

    def to_json(self):
        b=chr(34)
        return ("{"+f"\"timestamp\":\"{self.timestamp}\",\"voltage\":{self.voltage},\"current\":{self.current},\"power\":{self.power},\"power_factor\":{self.power_factor}"+"}")





class Measurer:

    def __init__(self,
                serial_port:str=DEFAULT_SERIAL_PORT,
                baud_rate:int=DEFAULT_BAUD_RATE):

        # Connect to the sensor
        self.sensor_port = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            bytesize=8,
            parity='N',
            stopbits=1,
            xonxoff=0
        )



        self.sensor_master:modbus_rtu.RtuMaster = modbus_rtu.RtuMaster(self.sensor_port)
        self.sensor_master.set_timeout(2.0)
        self.sensor_master.set_verbose(True)


    def get_reading_set(self):
        data = self.sensor_master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)

        voltage:float = data[0] / 10.0 # [V]
        current:float = (data[1] + (data[2] << 16)) / 1000.0 # [A]
        power:float = (data[3] + (data[4] << 16)) / 10.0 # [W]
        # energy = data[5] + (data[6] << 16) # [Wh]
        # frequency = data[7] / 10.0 # [Hz]
        power_factor:float = data[8] / 100.0


        res=Reading(datetime.datetime.now(),voltage,current,power,power_factor)
        # alarm = data[9] # 0 = no alarm

        # print('Voltage [V]: ', voltage)
        #print('Current [A]: ', current)
        # print('Power [W]: ', power) # active power (V * I * power factor)
        # print('Energy [Wh]: ', energy)
        # print('Frequency [Hz]: ', frequency)
        # print('Power factor []: ', powerFactor)
        # print('Alarm : ', alarm)

        # Changing power alarm value to 100 W
        # master.execute(1, cst.WRITE_SINGLE_REGISTER, 1, output_value=100)

        return res

    def close(self):
        try:
            self.master.close()
            if self.sensor_port.is_open:
                self.sensor_port.close()
        except:
            pass



if __name__=="__main__":
    print("Running")
    test_sensor:Measurer=Measurer()
    print("Sensor set up")
    # Takes just over 1 min for 1000 readings- so approx 15 readings per second
    for i in range(1000):
        print(test_sensor.get_reading_set())
    test_sensor.close()

