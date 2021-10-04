"""
@Date    : 2021-09-07
@Author  : liyachao

modified by liyanbo at 20210927
"""
import ast
import datetime
import json
import os
import time
import webbrowser
from pprint import pprint
import argparse
import pymysql.cursors
import requests
import tidevice
from grafana import Grafana
from mysql import Mysql
from ios_device import py_ios_device


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
    perf = tidevice.Performance(t)

    def callback(_type: tidevice.DataType, value: dict):
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

    perf.start(app_bundle_id, callback=callback)
    time.sleep(99999)  # 测试时长
    perf.stop()
    py_ios_device.stop_get_gpu(channel)
    py_ios_device.stop_get_fps(channel2)
    channel.stop()
    channel2.stop()


if __name__ == "__main__":
    # 参数处理部分
    parser = argparse.ArgumentParser()
    parser.add_argument("--udid", type=str, required=False, default="")
    parser.add_argument("--bundleid", type=str, required=False, default="com.insta360.oner")
    parser.add_argument("--grafana_host", type=str, required=False, default="localhost")
    parser.add_argument("--mysql_host", type=str, required=False, default="localhost")
    parser.add_argument("--grafana_port", type=str, required=False, default="30000")
    parser.add_argument("--mysql_port", type=str, required=False, default="33306")
    parser.add_argument("--grafana_username", type=str, required=False, default="admin")
    parser.add_argument("--mysql_username", type=str, required=False, default="root")
    parser.add_argument("--grafana_password", type=str, required=False, default="admin")
    parser.add_argument("--mysql_password", type=str, required=False, default="admin")
    parser.add_argument("--mysql_db", type=str, required=False, default="iOSPerformance")
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

    # 运行代码
    table_name = tidevice.Device(device_id).name + "_" + datetime.datetime.now().strftime("%m%d_%H%M")

    mysql = Mysql(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, table_name, device_id)
    mysql.db_init()

    grafana = Grafana(grafana_host, grafana_port, grafana_username, grafana_password, mysql_host, mysql_port,
                      mysql_username, mysql_password, mysql_db, table_name, device_id)
    grafana.add_mysql_source()
    grafana.setup_dashboard()
    grafana.to_explorer()

    start_test()
