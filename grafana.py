# -*- coding: UTF-8 -*-
import ast
import json
import time
import webbrowser

import jsonpath
import requests
import tidevice
from tidevice._proto import MODELS


class Grafana:
    def __init__(self, grafana_host, grafana_port, grafana_username, grafana_password, mysql_host, mysql_port,
                 mysql_username, mysql_password, mysql_db, run_id, device_id):
        self.grafana_host = grafana_host
        self.mysql_host = mysql_host
        self.grafana_port = grafana_port
        self.mysql_port = mysql_port
        self.grafana_username = grafana_username
        self.mysql_username = mysql_username
        self.grafana_password = grafana_password
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.run_id = run_id
        self.device_id = device_id
        self.dashboard_url = "http://{}:{}".format(grafana_host, grafana_port)
        self.add_mysql_source()

    def get_device_info(self, name):
        device = tidevice.Device(self.device_id)  # iOS设备
        value = device.get_value()

        if name == "MarketName":
            return MODELS.get(value['ProductType']).replace(" ", "")
        for attr in ('DeviceName', 'ProductVersion', 'ProductType',
                     'ModelNumber', 'SerialNumber', 'PhoneNumber',
                     'CPUArchitecture', 'ProductName', 'ProtocolVersion',
                     'RegionInfo', 'TimeIntervalSince1970', 'TimeZone',
                     'UniqueDeviceID', 'WiFiAddress', 'BluetoothAddress',
                     'BasebandVersion'):
            if attr == name:
                if value.get(attr):
                    return str(value.get(attr)).replace(" ", "")

        return None

    def set_anonymous(self):
        # useless cos this API needs grafana v8.0 +
        base_url = 'http://{}:{}@{}:{}/api/'.format(self.grafana_username, self.grafana_password, self.grafana_host,
                                                    self.grafana_port)
        url = base_url + 'admin/settings'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        body = {
            "updates": {
                "auth.anonymous": {"enabled": "true", "org_name": "Main Org.", "org_role": "Viewer"}
            }
        }
        response = requests.put(url=url, data=body, headers=headers)
        # response = requests.get(url)
        if response.status_code == 200:
            print("set anonymous success")
            # print("return : \n" + str(response.content.decode()))
        else:
            print("Error Code：" + str(response.status_code))
            # print("Error Message: \n" + str(response.content.decode()))

    def get_current_panels(self, uid):
        # 从当前的grafana上获取panel对象
        # 参数为dashboaard的uid，从ui中获取
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        base_url = 'http://{}:{}@{}:{}/api/'.format(self.grafana_username, self.grafana_password, self.grafana_host,
                                                    self.grafana_port)
        url = base_url + 'dashboards/uid/{}'.format(uid)
        response = requests.get(url, headers=headers)
        # pprint(response.text)
        jsonobj = json.loads(response.text)
        panels = jsonpath.jsonpath(jsonobj, "$..panels")[0]
        return panels

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
        panels_list_old = [{'cacheTimeout': None,
                            'content': '\n# INFO\n\nMarketName:       {}'
                                       '    \n\nProductVersion:   {}\n\n'
                                       'ProductType:      {}\n\nModelNumber:      {}\n\nSerialNumber:     {}'
                                       '\n\nPhoneNumber:      {}\n\nCPUArchitecture:  {}\n\nProductName:      '
                                       '{}\n\nProtocolVersion:  {}\n\nRegionInfo:       {}\n\nTimeIntervalSince1970: '
                                       '{}\n\nTimeZone:         {}\n\nUniqueDeviceID:   '
                                       '{}\n\nWiFiAddress:      {}\n\n'
                                       'BluetoothAddress: {}\n\nBasebandVersion:  {}\n\n\n\n'.format(
                                self.get_device_info("MarketName"),
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
                            'datasource': 'MySQL', 'gridPos': {'h': 25, 'w': 5, 'x': 0, 'y': 0}, 'id': 10, 'links': [],
                            'mode': 'markdown', 'pluginVersion': '6.7.4', 'targets': [
                {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': False,
                 'rawSql': 'SELECT\n  UNIX_TIMESTAMP(<time_column>) as time_sec,\n  <value column> as value,\n  <series name column> as metric\nFROM <table name>\nWHERE $__timeFilter(time_column)\nORDER BY <time_column> ASC\n',
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'timeFrom': None,
                            'timeShift': None, 'title': 'INFO', 'type': 'text'},
                           {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                            'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 5, 'w': 17, 'x': 6, 'y': 0},
                            'hiddenSeries': False, 'id': 6,
                            'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                       'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                            'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                            'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                            'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(fps) AS "FPS"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(jank) AS "Jank"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'B', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(big_jank) AS "Big_Jank"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'C', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(stutter) AS "Stutter"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'D', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                            'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'FPS',
                            'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                            'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                            'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True},
                                      {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                           {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                            'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 5, 'w': 17, 'x': 6, 'y': 5},
                            'hiddenSeries': False, 'id': 2,
                            'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                       'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                            'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                            'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                            'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                               {'format': 'time_series', 'group': [{'params': ['1s', 'none'], 'type': 'time'}],
                                'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(gpu_Device) AS "GPU_Device"\nFROM GPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'A', 'select': [[{'params': ['gpu_Device'], 'type': 'column'},
                                                          {'params': ['avg'], 'type': 'aggregate'},
                                                          {'params': ['gpu_Device'], 'type': 'alias'}]], 'table': 'GPU',
                                'timeColumn': 'time', 'timeColumnType': 'timestamp',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'},
                                          {'datatype': 'varchar', 'name': '',
                                           'params': ['runid', '=', "'iPhone8_1011_2245'"], 'type': 'expression'}]},
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(gpu_Renderer) AS "GPU_Renderer"\nFROM GPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(self.run_id),
                                'refId': 'B', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(gpu_Tiler) AS "GPU_Tiler"\nFROM GPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(self.run_id),
                                'refId': 'C', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                            'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'GPU',
                            'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                            'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                            'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True},
                                      {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                           {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                            'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 5, 'w': 17, 'x': 6, 'y': 10},
                            'hiddenSeries': False, 'id': 12,
                            'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                       'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                            'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                            'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                            'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(upflow) AS "up"\nFROM NET\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'A', 'select': [[{'params': ['upflow'], 'type': 'column'}]], 'table': 'NET',
                                'timeColumn': 'time', 'timeColumnType': 'timestamp',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(downflow) AS "down"\nFROM NET\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'B', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                            'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'NET',
                            'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                            'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                            'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True},
                                      {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                           {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                            'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 5, 'w': 17, 'x': 6, 'y': 15},
                            'hiddenSeries': False, 'id': 4,
                            'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                       'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                            'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                            'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                            'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(use_cpu) AS "USE_CPU"\nFROM CPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                            'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'CPU',
                            'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                            'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                            'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True},
                                      {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                           {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                            'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 5, 'w': 17, 'x': 6, 'y': 20},
                            'hiddenSeries': False, 'id': 8,
                            'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                       'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                            'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                            'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                            'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                               {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                                'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(memory) AS "MEM"\nFROM MEM\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(self.run_id),
                                'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]],
                                'timeColumn': 'time',
                                'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                            'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'MEM',
                            'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                            'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                            'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True},
                                      {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                       'show': True}], 'yaxis': {'align': False, 'alignLevel': None}}]

        panels_list = [{'cacheTimeout': None,
                        'content': '\n# INFO\n\nMarketName:       {}'
                                   '    \n\nProductVersion:   {}\n\n'
                                   'ProductType:      {}\n\nModelNumber:      {}\n\nSerialNumber:     {}'
                                   '\n\nPhoneNumber:      {}\n\nCPUArchitecture:  {}\n\nProductName:      '
                                   '{}\n\nProtocolVersion:  {}\n\nRegionInfo:       {}\n\nTimeIntervalSince1970: '
                                   '{}\n\nTimeZone:         {}\n\nUniqueDeviceID:   '
                                   '{}\n\nWiFiAddress:      {}\n\n'
                                   'BluetoothAddress: {}\n\nBasebandVersion:  {}\n\n\n\n'.format(
                            self.get_device_info("MarketName"),
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
                 'rawSql': 'SELECT\n  UNIX_TIMESTAMP(<time_column>) as time_sec,\n  <value column> as value,\n  <series name column> as metric\nFROM <table name>\nWHERE $__timeFilter(time_column)\nORDER BY <time_column> ASC\n'.format(
                     self.run_id),
                 'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
                 'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'timeFrom': None,
                        'timeShift': None, 'title': 'INFO', 'type': 'text'},
                       {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                        'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 0},
                        'hiddenSeries': False, 'id': 8,
                        'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                   'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                        'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                        'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                        'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(memory) AS "MEM"\nFROM MEM\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                        'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'MEM',
                        'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                        'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                        'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True},
                                  {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                       {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                        'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 6},
                        'hiddenSeries': False, 'id': 4,
                        'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                   'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                        'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                        'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                        'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(use_cpu) AS "USE_CPU"\nFROM CPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                        'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'CPU',
                        'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                        'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                        'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True},
                                  {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                       {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                        'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 12},
                        'hiddenSeries': False, 'id': 2,
                        'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                   'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                        'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                        'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                        'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                           {'format': 'time_series', 'group': [{'params': ['1s', 'none'], 'type': 'time'}],
                            'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(gpu_Device) AS "GPU_Device"\nFROM GPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'A', 'select': [[{'params': ['gpu_Device'], 'type': 'column'},
                                                      {'params': ['avg'], 'type': 'aggregate'},
                                                      {'params': ['gpu_Device'], 'type': 'alias'}]], 'table': 'GPU',
                            'timeColumn': 'time', 'timeColumnType': 'timestamp',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'},
                                      {'datatype': 'varchar', 'name': '',
                                       'params': ['runid', '=', "'{}'".format(self.run_id)], 'type': 'expression'}]},
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(gpu_Renderer) AS "GPU_Renderer"\nFROM GPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(
                                self.run_id),
                            'refId': 'B', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,3s),\n  avg(gpu_Tiler) AS "GPU_Tiler"\nFROM GPU\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,3s)'.format(
                                self.run_id),
                            'refId': 'C', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                        'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'GPU',
                        'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                        'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                        'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True},
                                  {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True}], 'yaxis': {'align': False, 'alignLevel': None}},
                       {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL',
                        'fill': 1, 'fillGradient': 0, 'gridPos': {'h': 6, 'w': 17, 'x': 6, 'y': 18},
                        'hiddenSeries': False, 'id': 6,
                        'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True,
                                   'total': False, 'values': False}, 'lines': True, 'linewidth': 1,
                        'nullPointMode': 'null', 'options': {'dataLinks': []}, 'percentage': False,
                        'pointradius': 2, 'points': False, 'renderer': 'flot', 'seriesOverrides': [],
                        'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(fps) AS "FPS"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(jank) AS "Jank"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'B', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(big_jank) AS "Big_Jank"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'C', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]},
                           {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
                            'rawSql': 'SELECT\n  $__timeGroupAlias(time,1s),\n  avg(stutter) AS "Stutter"\nFROM FPS\nWHERE\n  $__timeFilter(time) AND\n  runid = \'{}\'\nGROUP BY 1\nORDER BY $__timeGroup(time,1s)'.format(
                                self.run_id),
                            'refId': 'D', 'select': [[{'params': ['value'], 'type': 'column'}]],
                            'timeColumn': 'time',
                            'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [],
                        'timeFrom': None, 'timeRegions': [], 'timeShift': None, 'title': 'FPS',
                        'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
                        'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
                        'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True},
                                  {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None,
                                   'show': True}], 'yaxis': {'align': False, 'alignLevel': None}}]
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
            ''' % (self.run_id, str(json.dumps(panels_list_old)))
        # pprint(data)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        response = requests.post(url="http://{}:{}@{}:{}/api/dashboards/db".format(self.grafana_username,
                                                                                   self.grafana_password,
                                                                                   self.grafana_host,
                                                                                   self.grafana_port),
                                 data=data, headers=headers)
        # print(response)
        # print(response.text)
        response_dict = ast.literal_eval(response.text)
        self.dashboard_url = "http://{}:{}".format(self.grafana_host, self.grafana_port) + response_dict['url'] + \
                             "?orgId=1&refresh=1s&from=now-5m&to=now"

    def to_explorer(self):
        webbrowser.open(self.dashboard_url)


if __name__ == "__main__":
    grafana = Grafana("localhost", "30000", "admin", "admin", "localhost", "33306",
                      "root", "admin", "iOSPerformance", "iphone8_1011_2245",
                      "c6b0ab4fa8867c51cf1c5b6d8cd076d3957192b2")
    panels = grafana.get_current_panels("CycdY_vnk")
    time.sleep(1)
