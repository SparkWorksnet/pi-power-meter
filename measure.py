#!/usr/bin/env python
import getopt
import logging
from tempfile import gettempdir

import sys
import time
from influxdb import InfluxDBClient
import datetime
from stat_util import *
from influx_util import get_points

NAME = 'measure'

LOGGING_FORMAT = '%(asctime)s-%(filename)s:%(lineno)d-%(levelname)s- %(message)s'
# initialize logger
logger = logging.getLogger(NAME)
log_dir = gettempdir()
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)


def loop(time_start, interval, output_file, ina219, influx_client):
    while True:
        now_time = datetime.datetime.utcnow()
        power_data = read_power_sensor(ina219)
        data_list = power_data
        cpu_data = read_cpu_usage()
        data_list.extend(cpu_data)
        mem_data = read_memory_usage()
        data_list.extend(mem_data)
        disk_data = read_disk_io()
        data_list.extend(disk_data)
        net_data = read_net_io()
        data_list.extend(net_data)
        line = f'{int(time.time() * 1000) - time_start},{",".join([str(i) for i in data_list])}'
        if output_file is not None:
            # Writing data to a file
            output_file.writelines(line + "\n")
            output_file.flush()
        if influx_client is not None:
            influx_client.write_points(get_points(now_time, power_data, cpu_data, mem_data, disk_data, net_data))
        time.sleep(interval)


def help():
    print(f'{NAME}.py -o outfile.data')


def append_header(output_file):
    try:
        output_file.writelines(','.join([
            '#time',
            ','.join(['power_' + x for x in power_stats]),
            ','.join(['cpu_' + x for x in cpu_stats]),
            ','.join(['mem_' + x for x in mem_stats]),
            ','.join(['disk_' + x for x in disk_stats]),
            ','.join(['net_' + x for x in net_stats]),
            '\n'
        ]))
    except Exception as e:
        logging.error(e)


def main(argv):
    outfile = None
    output_file = None
    influx_host = None
    influx_db = 'stat'
    influx_client = None
    interval = 0.5
    time_start = int(time.time() * 1000)
    try:
        opts, args = getopt.getopt(argv, 'vhio:h:d:', ['output=', 'host=', 'db=', 'interval='])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ('-o', '--output'):
            outfile = arg
        elif opt in ('-h', '--host'):
            influx_host = arg
        elif opt in ('-d', '--db'):
            influx_db = arg
        elif opt in ('-i', '--interval'):
            interval = float(arg)
    if influx_host is not None and influx_db is not None:
        influx_client = InfluxDBClient(host=influx_host, port=8086)
        influx_client.create_database(influx_db)
        influx_client.switch_database(influx_db)
        logger.info('db connected')
    ina219 = setup_ina219()
    if outfile is not None:
        output_file = open(outfile, 'w')
        append_header(output_file)
    loop(time_start, interval, output_file, ina219, influx_client)


if __name__ == '__main__':
    main(sys.argv[1:])
