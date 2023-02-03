from stat_util import power_stats, cpu_stats, mem_stats, disk_stats, net_stats


def get_fields(stats, data):
    js_data = {}
    for index, label in enumerate(stats):
        js_data[label] = data[index]
    return js_data


def get_points(now_time, power_data, cpu_data, mem_data, disk_data, net_data):
    js_measurements = [
        {"measurement": "power", "time": now_time.utcnow().isoformat(), "fields": get_fields(power_stats, power_data)},
        {"measurement": "cpu", "time": now_time.utcnow().isoformat(), "fields": get_fields(cpu_stats, cpu_data)},
        {"measurement": "mem", "time": now_time.utcnow().isoformat(), "fields": get_fields(mem_stats, mem_data)},
        {"measurement": "disk", "time": now_time.utcnow().isoformat(), "fields": get_fields(disk_stats, disk_data)},
        {"measurement": "net", "time": now_time.utcnow().isoformat(), "fields": get_fields(net_stats, net_data)}
    ]
    return js_measurements
