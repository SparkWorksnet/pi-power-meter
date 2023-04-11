import logging
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import psutil
import board
import busio

NAME = 'stat_util'
LOGGING_FORMAT = '%(asctime)s-%(filename)s:%(lineno)d-%(levelname)s- %(message)s'
# initialize logger
logger = logging.getLogger(NAME)
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)

power_stats = ['voltage', 'power', 'current', 'shunt_voltage']
cpu_stats = ['1', '5', '15']
mem_stats = ['total', 'available', 'percent', 'used', 'free', 'active', 'inactive', 'buffers', 'cached', 'shared',
             'slab']
disk_stats = ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time', 'read_merged_count',
              'write_merged_count', 'busy_time']
net_stats = ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout']


def setup_ina219():
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    ina219 = INA219(i2c_bus)

    # display some of the advanced field (just to test)
    logger.info('# Config register:')
    logger.info('#   bus_voltage_range:    0x%1X' % ina219.bus_voltage_range)
    logger.info('#   gain:                 0x%1X' % ina219.gain)
    logger.info('#   bus_adc_resolution:   0x%1X' % ina219.bus_adc_resolution)
    logger.info('#   shunt_adc_resolution: 0x%1X' % ina219.shunt_adc_resolution)
    logger.info('#   mode:                 0x%1X' % ina219.mode)
    logger.info('# ')

    # optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
    ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    # optional : change voltage range to 16V
    ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

    return ina219


def convert_to_percent(load_tuple):
    num_log_cpus = psutil.cpu_count()
    percent_lst = []
    for load in load_tuple:
        percent = (load / num_log_cpus) * 100
        percent_lst.append(percent)
    return percent_lst


def read_power_sensor(ina219):
    try:
        return [ina219.bus_voltage, ina219.power, ina219.current, ina219.shunt_voltage]
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resistor
        print('DeviceRangeError', e)


def read_cpu_usage():
    return convert_to_percent(psutil.getloadavg())


def read_memory_usage():
    return [x for x in psutil.virtual_memory()]


def read_disk_io():
    return [x for x in psutil.disk_io_counters(perdisk=False)]


def read_net_io():
    return [x for x in psutil.net_io_counters()]
