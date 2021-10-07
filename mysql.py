# -*- coding: UTF-8 -*-
import pymysql.cursors
import time


class Mysql:
    def __init__(self, mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, table_name, device_id):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_username = mysql_username
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.table_name = table_name
        self.device_id = device_id
        self.db_init()
        
    def db_connect(self):
        # 根据mysql配置参数 返回游标对象
        connect = pymysql.Connect(
            host=self.mysql_host,
            port=int(self.mysql_port),
            user=self.mysql_username,
            passwd=self.mysql_password,
            db=self.mysql_db,
            charset='utf8'
        )
        # 获取连接对象
        return connect

    def db_init(self):
        #
        try:
            connect = self.db_connect()
            # 获取游标
            cursor = connect.cursor()
            cursor.execute("use {};".format(self.mysql_db))
            cursor.execute("CREATE TABLE FPS (fps VARCHAR(255), jank VARCHAR(255), big_jank  VARCHAR(255), "
                           "stutter  VARCHAR(255),runid  VARCHAR(255),  time timestamp)")
            cursor.execute("CREATE TABLE GPU (gpu_Device VARCHAR(255), gpu_Renderer VARCHAR(255), "
                           "gpu_Tiler VARCHAR(255),runid  VARCHAR(255), time  timestamp)")
            cursor.execute(
                "CREATE TABLE CPU (use_cpu VARCHAR(255), sys_cpu VARCHAR(255), count_cpu VARCHAR(255), "
                "runid  VARCHAR(255), time  timestamp)")
            cursor.execute("CREATE TABLE MEM (memory VARCHAR(255), runid  VARCHAR(255), "
                           "time  timestamp)")
            time.sleep(3)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()
            print("db init success")
        except BaseException as e:
            print("Error Info: " + str(e))
            print("Maybe this database dont need initializing, just ignore the error")
    
    def insert_cpu(self, value):
        cpu_sql_prefix = "INSERT INTO CPU (use_cpu,runid) VALUES('"
        sql = cpu_sql_prefix + value + "','" + self.table_name + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_memory(self, value):
        mem_sql_prefix = "INSERT INTO MEM (memory,runid) VALUES('"
        sql = mem_sql_prefix + value + "','" + self.table_name + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_fps(self, fps, jank, big_jank, stutter):
        fps_sql_prefix = "INSERT INTO FPS (fps,jank,big_jank,stutter,runid) VALUES('"
        sql = fps_sql_prefix + fps + "','" + jank + "','" + big_jank + "','" + stutter + "','" + self.table_name + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_gpu(self, gpu_device, gpu_renderer, gpu_tiler):
        gpu_sql_prefix = "INSERT INTO GPU (gpu_Device,gpu_Renderer,gpu_Tiler,runid) VALUES('"
        sql = gpu_sql_prefix + gpu_device + "','" + gpu_renderer + "','" + gpu_tiler + "','" + self.table_name + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()







