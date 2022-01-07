# -*- coding: UTF-8 -*-
import pymysql.cursors
import time
import xlwt
import argparse


class Mysql:
    def __init__(self, mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, run_id):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_username = mysql_username
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.run_id = run_id
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
            cursor.execute("CREATE TABLE TEMP (temp VARCHAR(255), runid  VARCHAR(255), "
                           "time  timestamp)")
            cursor.execute("CREATE TABLE ENG (gpu_cost VARCHAR(255), cpu_cost VARCHAR(255), network_cost VARCHAR(255), "
                           "runid  VARCHAR(255), time timestamp)")

            cursor.execute("CREATE TABLE FPS (fps VARCHAR(255), jank VARCHAR(255), big_jank  VARCHAR(255), "
                           "stutter  VARCHAR(255),runid  VARCHAR(255),  time timestamp)")
            cursor.execute("CREATE TABLE GPU (gpu_Device VARCHAR(255), gpu_Renderer VARCHAR(255), "
                           "gpu_Tiler VARCHAR(255),runid  VARCHAR(255), time  timestamp)")
            cursor.execute(
                "CREATE TABLE CPU (use_cpu VARCHAR(255), sys_cpu VARCHAR(255), count_cpu VARCHAR(255), "
                "runid  VARCHAR(255), time  timestamp)")
            cursor.execute("CREATE TABLE MEM (memory VARCHAR(255), runid  VARCHAR(255), "
                           "time  timestamp)")
            cursor.execute("CREATE TABLE NET (upflow VARCHAR(255), downflow VARCHAR(255), runid  VARCHAR(255), "
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
        sql = cpu_sql_prefix + value + "','" + self.run_id + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_memory(self, value):
        mem_sql_prefix = "INSERT INTO MEM (memory,runid) VALUES('"
        sql = mem_sql_prefix + value + "','" + self.run_id + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_fps(self, fps, jank=0, big_jank=0, stutter=0):
        # fps, jank, big_jank, stutter
        fps_sql_prefix = "INSERT INTO FPS (fps,jank,big_jank,stutter,runid) VALUES('"
        sql = fps_sql_prefix + str(fps) + "','" + str(jank) + "','" + str(big_jank) + "','" + str(stutter) + "','" \
              + self.run_id + "')"
        print("**************fps:" +sql)
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_gpu(self, gpu_device, gpu_renderer, gpu_tiler):
        gpu_sql_prefix = "INSERT INTO GPU (gpu_Device,gpu_Renderer,gpu_Tiler,runid) VALUES('"
        sql = gpu_sql_prefix + str(gpu_device) + "','" + str(gpu_renderer) + "','" + str(gpu_tiler) + \
              "','" + self.run_id + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_net(self, upflow, downflow):
        net_sql_prefix = "INSERT INTO NET (upflow,downflow,runid) VALUES('"
        sql = net_sql_prefix + str(upflow) + "','" + str(downflow) + "','" + self.run_id + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_temp(self, temp):
        tmp_sql_prefix = "INSERT INTO TEMP (temp,runid) VALUES('"
        sql = tmp_sql_prefix + str(temp) + "','" + self.run_id + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def insert_eng(self, gpu_cost, cpu_cost, network_cost):
        eng_sql_prefix = "INSERT INTO ENG (gpu_cost,cpu_cost,network_cost,runid) VALUES('"
        sql = eng_sql_prefix + str(gpu_cost) + "','" + str(cpu_cost) + "','" + str(network_cost) + "','" + \
              self.run_id + "')"
        connect = self.db_connect()
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        # 关闭连接
        cursor.close()
        connect.close()

    def export(self):
        table_list = ["FPS", "GPU", "CPU", "MEM", "NET", "ENG", "TEMP"]
        workbook = xlwt.Workbook()
        for t in table_list:
            connect = self.db_connect()
            cursor = connect.cursor()

            cursor.execute('select * from ' + t + ' WHERE runid = \'{}\''.format(self.run_id))
            # 重置游标的位置
            cursor.scroll(0, mode='absolute')
            # 搜取所有结果
            results = cursor.fetchall()

            # 获取MYSQL里面的数据字段名称
            fields = cursor.description
            sheet = workbook.add_sheet('table_' + '{}'.format(t), cell_overwrite_ok=True)

            # 写上字段信息
            for field in range(0, len(fields)):
                sheet.write(0, field, fields[field][0])

            # 获取并写入数据段信息
            row = 1
            col = 0
            for row in range(1, len(results) + 1):
                for col in range(0, len(fields)):
                    sheet.write(row, col, u'%s' % results[row - 1][col])

            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()

        workbook.save("{}.xls".format(self.run_id))
        print("export finish, check file: " + "{}.xls".format(self.run_id))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--mysql_host", type=str, required=False, default="10.0.43.163")
    parser.add_argument("--mysql_port", type=str, required=False, default="33306")
    parser.add_argument("--mysql_username", type=str, required=False, default="root")
    parser.add_argument("--mysql_password", type=str, required=False, default="admin")
    parser.add_argument("--mysql_db", type=str, required=False, default="iOSPerformance")
    parser.add_argument("--runid", type=str, required=True)

    args = parser.parse_args()
    print("Parameters list:")
    for arg in vars(args):
        print(arg, getattr(args, arg))

    mysql_host = args.mysql_host
    mysql_port = args.mysql_port
    mysql_username = args.mysql_username
    mysql_password = args.mysql_password
    mysql_db = args.mysql_db
    run_id = args.runid

    mysql = Mysql(mysql_host, mysql_port, mysql_username, mysql_password, mysql_db, run_id)
    mysql.export()







