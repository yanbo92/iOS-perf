import ast
import json
import os
import webbrowser
from pprint import pprint
import requests
import jsonpath


class Grafana:
    def __init__(self, grafana_host, grafana_port, grafana_username, grafana_password, mysql_host, mysql_port,
                 mysql_username, mysql_password, mysql_db, table_name, device_id):
        self.grafana_host = grafana_host
        self.mysql_host = mysql_host
        self.grafana_port = grafana_port
        self.mysql_port = mysql_port
        self.grafana_username = grafana_username
        self.mysql_username = mysql_username
        self.grafana_password = grafana_password
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.table_name = table_name
        self.device_id = device_id
        self.dashboard_url = "http://{}:{}".format(grafana_host, grafana_port)

    def get_device_info(self, name):
        if self.device_id == "":
            cmd = "tidevice info | grep {}".format(name)
        else:
            cmd = "tidevice -u {} info | grep {}".format(self.device_id, name)
        result = os.popen(cmd)
        # 返回的结果是一个<class 'os._wrap_close'>对象，需要读取后才能处理
        context = result.read()
        info_line = ""
        for line in context.splitlines():
            info_line = line
        value = info_line.split("{}:".format(name))[1]
        result.close()
        return value.replace(" ", "")
    
    def add_mysql_source(self):
        base_url = 'http://{}:{}@{}:{}/api/'.format(self.grafana_username, self.grafana_password, self.grafana_host,
                                                    self.grafana_port)
        url = base_url + 'datasources'
        response = requests.get(url)
        if self.mysql_host == 'localhost' and self.mysql_port == '33306':
            db_url = 'db'
        else:
            db_url = self.mysql_host + ":" + self.mysql_port
        if 'mysql' not in response.content.decode():
            body = {
                "name": "MySQL",
                "type": "mysql",
                "url": "{}".format(db_url),
                "password": "{}".format(self.mysql_password),
                "user": "{}".format(self.mysql_username),
                "database": "{}".format(self.mysql_db),
                "access": "proxy"
            }
            response = requests.post(url=url, data=body)
            if response.status_code == 200:
                print("add datasource MySQL success")
            else:
                print("Error Code：" + str(response.status_code))
                print("Error Message: \n" + str(response.content.decode()))

    def setup_dashboard(self):
        panels_list = [
            {'cacheTimeout': None,
             'content': '\n# INFO\n\nMarketName:       {}\n\nDeviceName:       {}\n\nProductVersion:   {}\n\n'
                        'ProductType:      {}\n\nModelNumber:      {}\n\nSerialNumber:     {}'
                        '\n\nPhoneNumber:      {}\n\nCPUArchitecture:  {}\n\nProductName:      '
                        '{}\n\nProtocolVersion:  {}\n\nRegionInfo:       {}\n\nTimeIntervalSince1970: '
                        '{}\n\nTimeZone:         {}\n\nUniqueDeviceID:   '
                        '{}\n\nWiFiAddress:      {}\n\n'
                        'BluetoothAddress: {}\n\nBasebandVersion:  {}\n\n\n\n'.format(self.get_device_info("MarketName"),
                                                                                      self.get_device_info("DeviceName"),
                                                                                      self.get_device_info("ProductVersion"),
                                                                                      self.get_device_info("ProductType"),
                                                                                      self.get_device_info("ModelNumber"),
                                                                                      self.get_device_info("SerialNumber"),
                                                                                      self.get_device_info("PhoneNumber"),
                                                                                      self.get_device_info(
                                                                                          "CPUArchitecture"),
                                                                                      self.get_device_info("ProductName"),
                                                                                      self.get_device_info(
                                                                                          "ProtocolVersion"),
                                                                                      self.get_device_info("RegionInfo"),
                                                                                      self.get_device_info(
                                                                                          "TimeIntervalSince1970"),
                                                                                      self.get_device_info("TimeZone"),
                                                                                      self.get_device_info("UniqueDeviceID"),
                                                                                      self.get_device_info("WiFiAddress"),
                                                                                      self.get_device_info(
                                                                                          "BluetoothAddress"),
                                                                                      self.get_device_info(
                                                                                          "BasebandVersion")),
             'datasource': 'MySQL', 'gridPos': {'h': 24, 'w': 5, 'x': 0, 'y': 0}, 'id': 10, 'links': [],
             'mode': 'markdown', 'pluginVersion': '6.7.4', 'targets': [
                {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': False,
                 'rawSql': 'SELECT\n  UNIX_TIMESTAMP(<time_column>) as time_sec,\n  <value column> as value,\n '
                           ' <series name column> as metric\nFROM <table name>\nWHERE $__timeFilter(time_column)\nORDER'
                           ' BY <time_column> ASC\n',
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'timeFrom': None,
             'timeShift': None,
             'title': 'INFO', 'type': 'text'},
            {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
             'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 0}, 'hiddenSeries': False, 'id': 8,
             'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                        'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
             'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
             'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                 'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(memory) AS "MEM"\nFROM my_memory_{}\nWHERE\n '
                           ' $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(self.table_name),
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
             'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'MEM',
             'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
             'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
             'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                       {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
             'yaxis': {'align': False, 'alignLevel': None}},
            {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
             'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 6}, 'hiddenSeries': False, 'id': 4,
             'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                        'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
             'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
             'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                 'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(use_cpu) AS "CPU"\nFROM my_cpu_{}\nWHERE\n  '
                           '$__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(self.table_name),
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
             'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'CPU',
             'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
             'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
             'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                       {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
             'yaxis': {'align': False, 'alignLevel': None}},
            {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
             'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 12}, 'hiddenSeries': False, 'id': 2,
             'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                        'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
             'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
             'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                 'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(gpu_Device) AS "GPU"\nFROM my_gpu_{}\nWHERE\n '
                           ' $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(self.table_name),
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
             'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'GPU',
             'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
             'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
             'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                       {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
             'yaxis': {'align': False, 'alignLevel': None}},
            {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
             'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 18}, 'hiddenSeries': False, 'id': 6,
             'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                        'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
             'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
             'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                 'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(fps) AS "FPS"\nFROM my_fps_{}\nWHERE\n '
                           ' $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(self.table_name),
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
             'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'FPS',
             'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
             'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
             'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                       {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
             'yaxis': {'align': False, 'alignLevel': None}}
        ]
        data = '''
            {
              "dashboard": {
                "id": null,
                "uid": null,
                "title": "%s",

                "timezone": "browser",
                "timepicker": {
                    "refresh_intervals": [
                      "1s",
                      "5s",
                      "10s",
                      "30s",
                      "1m",
                      "5m",
                      "15m",
                      "30m"
                    ]
                  },
                "panels": %s  ,
                "templating": {
                "list": []
              },
                "annotations": {
                "list": []
              },
                "schemaVersion": 16,
                "version": 2
              },
              "folderId": 0,
              "overwrite": true
            }
            ''' % (self.table_name, str(json.dumps(panels_list)))
        pprint(data)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        response = requests.post(url="http://{}:{}@{}:{}/api/dashboards/db".format(self.grafana_username,
                                                                                   self.grafana_password,
                                                                                   self.grafana_host,self.grafana_port),
                                 data=data, headers=headers)
        print(response)
        print(response.text)
        response_dict = ast.literal_eval(response.text)
        self.dashboard_url = "http://{}:{}".format(self.grafana_host, self.grafana_port) + response_dict['url'] + \
                            "?orgId=1&refresh=1s&from=now-5m&to=now"

    def to_explorer(self):
        webbrowser.open(self.dashboard_url)

