#!/usr/bin/env python
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import sys
import time

i2c_bus = board.I2C()
ina219 = INA219(i2c_bus)

# display some of the advanced field (just to test)
print('# Config register:')
print('#   bus_voltage_range:    0x%1X' % ina219.bus_voltage_range)
print('#   gain:                 0x%1X' % ina219.gain)
print('#   bus_adc_resolution:   0x%1X' % ina219.bus_adc_resolution)
print('#   shunt_adc_resolution: 0x%1X' % ina219.shunt_adc_resolution)
print('#   mode:                 0x%1X' % ina219.mode)
print('# ')

# optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
# optional : change voltage range to 16V
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V


def read():
    try:
        return (ina219.bus_voltage, ina219.power, ina219.current, ina219.shunt_voltage)
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resistor
        print('DeviceRangeError', e)


if __name__ == '__main__':
    time_start = int(time.time() * 1000)
    with open(sys.argv[1], 'w') as file1:
        file1.writelines('#time,voltage,current,power,shunt_voltage\n')
        while True:
            (a, b, c, d) = read()
            line = f'{int(time.time() * 1000) - time_start},{a},{b},{c},{d}'
            print(line)
            # Writing data to a file
            file1.writelines(line + "\n")
            file1.flush()
            time.sleep(0.1)
