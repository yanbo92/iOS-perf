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
from ios_device import py_ios_device


fps_sql_prefix = ""
cpu_sql_prefix = ""
gpu_sql_prefix = ""
mem_sql_prefix = ""


def db_connect(host, port, user, pw, db):
    # 接受mysql配置参数 返回游标对象
    connect = pymysql.Connect(
        host=host,
        port=int(port),
        user=user,
        passwd=pw,
        db=db,
        charset='utf8'
    )
    # 获取游标
    return connect


def db_init(table_name):
    try:
        global fps_sql_prefix, cpu_sql_prefix, gpu_sql_prefix, mem_sql_prefix
        fps_sql_prefix = "INSERT INTO my_fps_{} (fps,jank,big_jank,stutter) VALUES('".format(table_name)
        cpu_sql_prefix = "INSERT INTO my_cpu_{} (use_cpu) VALUES('".format(table_name)
        gpu_sql_prefix = "INSERT INTO my_gpu_{} (gpu_Device,gpu_Renderer,gpu_Tiler) VALUES('".format(table_name)
        mem_sql_prefix = "INSERT INTO my_memory_{} (memory) VALUES('".format(table_name)
        connect = db_connect(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db)
        # 获取游标
        cursor = connect.cursor()
        cursor.execute("use test;")
        cursor.execute("CREATE TABLE my_fps_{} (fps VARCHAR(255), jank VARCHAR(255), big_jank  VARCHAR(255), "
                       "stutter  VARCHAR(255), time timestamp)".format(table_name))
        cursor.execute("CREATE TABLE my_gpu_{} (gpu_Device VARCHAR(255), gpu_Renderer VARCHAR(255), "
                       "gpu_Tiler VARCHAR(255), time  timestamp)".format(table_name))
        cursor.execute("CREATE TABLE my_cpu_{} (use_cpu VARCHAR(255), sys_cpu VARCHAR(255), count_cpu VARCHAR(255), "
                       "time  timestamp)".format(table_name))
        cursor.execute("CREATE TABLE my_memory_{} (memory VARCHAR(255), time  timestamp)".format(table_name))

        time.sleep(5)

    except BaseException as e:
        print("Error: " + str(e))


def callback_fps(res):
    print('FPS打印', res)
    # fps数据
    ss = str(res)
    fps_test = ss.split("'FPS':")[1].split(".")[0]
    jank_test = ss.split("'jank':")[1].split(",")[0]
    big_jank = ss.split("'big_jank':")[1].split(",")[0]
    stutter = ss.split("'stutter':")[1][0:5].split("}")[0]
    # 数据存数据库连接数据库
    connect = db_connect(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db)

    # 获取游标
    cursor = connect.cursor()
    sql = fps_sql_prefix + fps_test + "','" + jank_test + "','" + big_jank + "','" + stutter + "')"
    cursor.execute(sql)
    connect.commit()
    # 关闭连接
    cursor.close()
    connect.close()


def callback_gpu(res):
    print('GPU打印', res)
    # gpu数据
    ss = str(res)  # 转数据类型
    gpu_Device = ss.split("'Device Utilization %':")[1].split(",")[0]
    gpu_Renderer = ss.split("'Renderer Utilization %':")[1].split(",")[0]
    gpu_Tiler = ss.split("'Tiler Utilization %':")[1].split(",")[0]
    # 数据存数据库连接数据库
    connect = db_connect(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db)

    # 获取游标
    cursor = connect.cursor()
    sql = gpu_sql_prefix + gpu_Device + "','" + gpu_Renderer + "','" + gpu_Tiler + "')"
    cursor.execute(sql)
    connect.commit()
    # print('GPU成功插入', cursor.rowcount, '条数据')
    # 关闭连接
    cursor.close()
    connect.close()


def start_test():
    channel = py_ios_device.start_get_gpu(callback=callback_gpu)
    channel2 = py_ios_device.start_get_fps(callback=callback_fps)
    t = tidevice.Device(device_id)  # iOS设备
    # perf = tidevice.Performance(t, perfs=list(tidevice.DataType))
    perf = tidevice.Performance(t)

    def callback(_type: tidevice.DataType, value: dict):
        if _type.value == "cpu":
            print('CPU打印', value)
            ss = str(value)  # 转成str
            use_cpu = ss.split("'value':")[1][0:6].split("}")[0]
            # 数据存数据库连接数据库
            connect = db_connect(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db)

            # 获取游标
            cursor = connect.cursor()
            sql = cpu_sql_prefix + use_cpu + "')"
            cursor.execute(sql)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()
        if _type.value == "memory":
            print('内存打印', value)
            ss = str(value)
            memory = ss.split("'value':")[1][0:6].split("}")[0]
            # 数据存数据库连接数据库
            connect = db_connect(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db)

            # 获取游标
            cursor = connect.cursor()
            sql = mem_sql_prefix + memory + "')"
            cursor.execute(sql)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()

    perf.start(app_bundle_id, callback=callback)
    time.sleep(99999)  # 测试时长
    perf.stop()
    py_ios_device.stop_get_gpu(channel)
    py_ios_device.stop_get_fps(channel2)
    channel.stop()
    channel2.stop()


if __name__ == "__main__":

    print("wait for mysql setup")
    # time.sleep(10)
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
    parser.add_argument("--mysql_db", type=str, required=False, default="test")
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

    table_name = tidevice.Device(device_id).name + "_" + datetime.datetime.now().strftime("%m%d_%H%M")

    grafana = Grafana(grafana_host, grafana_port, grafana_username, grafana_password, mysql_host, mysql_port,
                      mysql_username, mysql_password, mysql_db, table_name, device_id)
    grafana.add_mysql_source()
    grafana.setup_dashboard()
    grafana.to_explorer()
    db_init(table_name)
    # grafana_setup(table_name)
    start_test()
