# -*- coding: UTF-8 -*-
"""
@Author  : liyanbo

"""
import datetime
import time
import argparse
import threading
from grafana import Grafana
from mysql import Mysql
import tidevice
from tidevice._usbmux import Usbmux
from tidevice._proto import MODELS
from tidevice._perf import DataType
from ios_device.servers.Instrument import InstrumentServer
from ios_device import py_ios_device


def get_energy(rpc, pid):
    rpc._start()
    channel = "com.apple.xcode.debug-gauge-data-providers.Energy"
    attr = {}
    print("start", rpc.call(channel, "startSamplingForPIDs:", {pid}).selector)
    while True:
        ret = rpc.call(channel, "sampleAttributes:forPIDs:", attr, {pid})
        # print(ret.selector)
        if 'energy.gpu.cost' in ret.selector[pid].keys():
            print("gpu:", ret.selector[pid]['energy.gpu.cost'])
            gpu_cost = ret.selector[pid]['energy.gpu.cost']
        else:
            gpu_cost = '0'

        if 'energy.cpu.cost' in ret.selector[pid].keys():
            print("cpu:", ret.selector[pid]['energy.cpu.cost'])
            cpu_cost = ret.selector[pid]['energy.cpu.cost']
        else:
            cpu_cost = '0'

        if 'energy.networking.cost' in ret.selector[pid].keys():
            print("networking:", ret.selector[pid]['energy.networking.cost'])
            network_cost = ret.selector[pid]['energy.networking.cost']
        else:
            network_cost = '0'

        mysql.insert_eng(gpu_cost, cpu_cost, network_cost)
        time.sleep(1)


def get_fps(rpc):
    def callback_fps(res):
        print('FPS打印', res)
        # fps数据
        ss = str(res)
        fps_test = ss.split("'FPS':")[1].split(".")[0]
        jank_test = ss.split("'jank':")[1].split(",")[0]
        big_jank = ss.split("'big_jank':")[1].split(",")[0]
        stutter = ss.split("'stutter':")[1][0:5].split("}")[0]
        mysql.insert_fps(fps_test, jank_test, big_jank, stutter)

    py_ios_device.start_get_fps(rpc_channel=rpc, callback=callback_fps)


def get_temp(td):
    while True:
        io_power = (td.get_io_power())
        diagnostics = io_power['Diagnostics']
        io_registry = diagnostics['IORegistry']
        temperature = io_registry['Temperature']
        temp_float = str(float(temperature) / 100)
        print("temp:", temp_float)
        mysql.insert_temp(temp_float)
        time.sleep(5)


def start_test():
    
    def get_pid(bid):
        t = tidevice.Device(device_id)
        app_infos = list(t.instruments.app_list())
        for app in app_infos:
            plugin = []
            if app['CFBundleIdentifier'] == bid:
                print('app',app)
                plugin = [app]
            if plugin.count == 1:
                pid = 0
                ps = t.instruments.app_process_list(plugin)
                for p in ps:
                    pid = p['pid']
                if pid:
                    return pid
        return None
    
    t = tidevice.Device(device_id)  # iOS设备
    try:
        pid = t.app_start(app_bundle_id)
    except BaseException as e:
        pid = get_pid(app_bundle_id)
    rpc = InstrumentServer(udid=device_id, network=True).init()

    t_energy = threading.Thread(target=get_energy, args=(rpc, pid))
    t_fps = threading.Thread(target=get_fps, args=[rpc])
    t_temp = threading.Thread(target=get_temp, args=[t])

    perf = tidevice.Performance(t, [DataType.CPU, DataType.MEMORY, DataType.NETWORK, DataType.FPS, DataType.PAGE,
                                    DataType.GPU, DataType.SCREENSHOT])

    def callback(_type: tidevice.DataType, value: dict):
        print(_type, value)
        if _type.value == "cpu":
            print('CPU打印', value)
            ss = str(value)  # 转成str
            use_cpu = ss.split("'value':")[1][0:6].split("}")[0]
            # 数据存数据库连接数据库
            mysql.insert_cpu(use_cpu)
        if _type.value == "memory":
            print('内存打印', value)
            ss = str(value)
            memory = ss.split("'value':")[1][0:6].split("}")[0]
            # 数据存数据库连接数据库
            mysql.insert_memory(memory)
        if _type.value == "network":
            print('网络打印', value)
            downFlow = value['downFlow']
            upFlow = value['upFlow']
            mysql.insert_net(upFlow, downFlow)
        # if _type.value == "fps":
        #     print('tidevice.fps打印', value)
        #     fps = value['fps']
        #     mysql.insert_fps(fps)
        if _type.value == "gpu":
            print('GPU', value)
            device = value['device']
            renderer = value['renderer']
            tiler = value['tiler']
            mysql.insert_gpu(device, renderer, tiler)

    try:
        perf.start(app_bundle_id, callback=callback)
    except BaseException as ssl_error:
        print(ssl_error)
        time.sleep(5)
        perf.start(app_bundle_id, callback=callback)

    t_temp.start()
    t_energy.start()
    t_fps.start()
    time.sleep(99999)  # 测试时长
    perf.stop()


def get_device_info(name):
    device = tidevice.Device(device_id)  # iOS设备
    value = device.get_value()

    for attr in ('DeviceName', 'ProductVersion', 'ProductType',
                 'ModelNumber', 'SerialNumber', 'PhoneNumber',
                 'CPUArchitecture', 'ProductName', 'ProtocolVersion',
                 'RegionInfo', 'TimeIntervalSince1970', 'TimeZone',
                 'UniqueDeviceID', 'WiFiAddress', 'BluetoothAddress',
                 'BasebandVersion'):
        if attr == name:
            if value.get(attr):
                return str(value.get(attr)).replace(" ", "")
    if name == "MarketName":
        return MODELS.get(value['ProductType']).replace(" ", "")
    return None


if __name__ == "__main__":

    # 参数处理部分
    parser = argparse.ArgumentParser()
    parser.add_argument("--udid", type=str, required=False, default="")
    parser.add_argument("--bundleid", type=str, required=False, default="com.apple.Preferences")
    # parser.add_argument("--grafana_host", type=str, required=False, default="10.0.43.163")
    # parser.add_argument("--mysql_host", type=str, required=False, default="10.0.43.163")
    parser.add_argument("--grafana_host", type=str, required=False, default="localhost")
    parser.add_argument("--mysql_host", type=str, required=False, default="localhost")
    parser.add_argument("--grafana_port", type=str, required=False, default="30000")
    parser.add_argument("--mysql_port", type=str, required=False, default="33306")
    parser.add_argument("--grafana_username", type=str, required=False, default="admin")
    parser.add_argument("--mysql_username", type=str, required=False, default="root")
    parser.add_argument("--grafana_password", type=str, required=False, default="admin")
    parser.add_argument("--mysql_password", type=str, required=False, default="admin")
    parser.add_argument("--mysql_db", type=str, required=False, default="iOSPerformance")
    parser.add_argument("--runid", type=str, required=False, default="")
    parser.add_argument('--export', type=int, required=False, default=0, help='python run.py --export=1 --runid=iphone6_1012_1111')

    args = parser.parse_args()
    print("Parameters list:")
    for arg in vars(args):
        print(arg, getattr(args, arg))

    app_bundle_id = args.bundleid  # 测试iOS应用包名
    device_id = args.udid  # 测试设备ID
    grafana_host = args.grafana_host
    mysql_host = args.mysql_host
    grafana_port = args.grafana_port
    mysql_port = args.mysql_port
    grafana_username = args.grafana_username
    mysql_username = args.mysql_username
    grafana_password = args.grafana_password
    mysql_password = args.mysql_password
    mysql_db = args.mysql_db
    run_id = args.runid
    export = args.export

    # 运行代码
    if not device_id:
        um = Usbmux()
        for d in um.device_list():
            if d.conn_type == ' USB':
                device_id = d.udid

    if not export:
        tidevice_obj = tidevice.Device(device_id)  # iOS设备

        MarketName = get_device_info("MarketName")
        run_id = get_device_info("MarketName") + "_" + datetime.datetime.now().strftime("%m%d_%H%M")

        mysql = Mysql(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, run_id)

        grafana = Grafana(grafana_host, grafana_port, grafana_username, grafana_password, mysql_host, mysql_port,
                          mysql_username, mysql_password, mysql_db, run_id, device_id, app_bundle_id)
        grafana.setup_dashboard()
        grafana.to_explorer()

        start_test()
    else:
        mysql = Mysql(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, run_id)
        mysql.export()


