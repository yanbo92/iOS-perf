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
        try:
            connect = self.db_connect()
            # 获取游标
            cursor = connect.cursor()
            cursor.execute("use {};".format(self.mysql_db))
            cursor.execute("CREATE TABLE my_fps_{} (fps VARCHAR(255), jank VARCHAR(255), big_jank  VARCHAR(255), "
                           "stutter  VARCHAR(255), time timestamp)".format(self.table_name))
            cursor.execute("CREATE TABLE my_gpu_{} (gpu_Device VARCHAR(255), gpu_Renderer VARCHAR(255), "
                           "gpu_Tiler VARCHAR(255), time  timestamp)".format(self.table_name))
            cursor.execute(
                "CREATE TABLE my_cpu_{} (use_cpu VARCHAR(255), sys_cpu VARCHAR(255), count_cpu VARCHAR(255), "
                "time  timestamp)".format(self.table_name))
            cursor.execute("CREATE TABLE my_memory_{} (memory VARCHAR(255), time  timestamp)".format(self.table_name))
            time.sleep(3)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()
            
        except BaseException as e:
            print("Error: " + str(e))
    
    def insert_cpu(self, value):
        cpu_sql_prefix = "INSERT INTO my_cpu_{} (use_cpu) VALUES('".format(self.table_name)
        sql = cpu_sql_prefix + value + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_memory(self, value):
        mem_sql_prefix = "INSERT INTO my_memory_{} (memory) VALUES('".format(self.table_name)
        sql = mem_sql_prefix + value + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_fps(self, fps, jank, big_jank, stutter):
        fps_sql_prefix = "INSERT INTO my_fps_{} (fps,jank,big_jank,stutter) VALUES('".format(self.table_name)
        sql = fps_sql_prefix + fps + "','" + jank + "','" + big_jank + "','" + stutter + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_gpu(self, gpu_device, gpu_renderer, gpu_tiler):
        gpu_sql_prefix = "INSERT INTO my_gpu_{} (gpu_Device,gpu_Renderer,gpu_Tiler) VALUES('".format(self.table_name)
        sql = gpu_sql_prefix + gpu_device + "','" + gpu_renderer + "','" + gpu_tiler + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()







