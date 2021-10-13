"""
@Date    : 2021-09-07
@Author  : liyachao

modified by liyanbo at 20210927
"""
# -*- coding: UTF-8 -*-
import datetime
import time
import argparse
import tidevice
from grafana import Grafana
from mysql import Mysql
from ios_device import py_ios_device
from tidevice._proto import MODELS
from tidevice._perf import DataType


def callback_fps(res):
    print('FPS打印', res)
    # fps数据
    ss = str(res)
    fps_test = ss.split("'FPS':")[1].split(".")[0]
    jank_test = ss.split("'jank':")[1].split(",")[0]
    big_jank = ss.split("'big_jank':")[1].split(",")[0]
    stutter = ss.split("'stutter':")[1][0:5].split("}")[0]
    # 数据存数据库连接数据库
    mysql.insert_fps(fps_test, jank_test, big_jank, stutter)


def callback_gpu(res):
    print('GPU打印', res)
    # gpu数据
    ss = str(res)  # 转数据类型
    gpu_Device = ss.split("'Device Utilization %':")[1].split(",")[0]
    gpu_Renderer = ss.split("'Renderer Utilization %':")[1].split(",")[0]
    gpu_Tiler = ss.split("'Tiler Utilization %':")[1].split(",")[0]
    # 数据存数据库连接数据库
    mysql.insert_gpu(gpu_Device, gpu_Renderer, gpu_Tiler)


def start_test():
    channel = py_ios_device.start_get_gpu(callback=callback_gpu)
    channel2 = py_ios_device.start_get_fps(callback=callback_fps)
    t = tidevice.Device(device_id)  # iOS设备
    perf = tidevice.Performance(t, [DataType.CPU, DataType.MEMORY, DataType.NETWORK])

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
    try:
        perf.start(app_bundle_id, callback=callback)
    except BaseException as ssl_error:
        print(ssl_error)
        time.sleep(5)
        perf.start(app_bundle_id, callback=callback)

    time.sleep(99999)  # 测试时长
    perf.stop()
    py_ios_device.stop_get_gpu(channel)
    py_ios_device.stop_get_fps(channel2)
    channel.stop()
    channel2.stop()


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
    parser.add_argument("--grafana_host", type=str, required=False, default="localhost")
    parser.add_argument("--mysql_host", type=str, required=False, default="localhost")
    # parser.add_argument("--grafana_host", type=str, required=False, default="localhost")
    # parser.add_argument("--mysql_host", type=str, required=False, default="localhost")
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
    if not export:
        tidevice_obj = tidevice.Device(device_id)  # iOS设备

        MarketName = get_device_info("MarketName")
        run_id = get_device_info("MarketName") + "_" + datetime.datetime.now().strftime("%m%d_%H%M")

        mysql = Mysql(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, run_id)

        grafana = Grafana(grafana_host, grafana_port, grafana_username, grafana_password, mysql_host, mysql_port,
                          mysql_username, mysql_password, mysql_db, run_id, device_id)
        grafana.setup_dashboard()
        grafana.to_explorer()

        start_test()
    else:
        mysql = Mysql(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, run_id)
        mysql.export()


