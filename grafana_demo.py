# -*- coding: utf-8 -*-
import ast
import json
import webbrowser
from pprint import pprint
import requests
import jsonpath


def set_anonymous():
    # useless cos this API needs grafana v8.0 +
    base_url = 'http://admin:admin@localhost:30000/api/'
    url = base_url + 'admin/settings'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    body = {
      "updates": {
        "auth.anonymous": {"enabled": "true", "org_name": "Main Org.","org_role": "Viewer"}
      }
    }
    response = requests.put(url=url, data=body, headers=headers)
    # response = requests.get(url)
    if response.status_code == 200:
        print("set anonymous success")
        print("return : \n" + str(response.content.decode()))
    else:
        print("Error Code：" + str(response.status_code))
        print("Error Message: \n" + str(response.content.decode()))


def add_mysql_source():
    base_url = 'http://admin:admin@localhost:30000/api/'
    url = base_url + 'datasources'
    body = {
        "name": "MySQL",
        "type": "mysql",
        "host": "localhost:3306",
        "password": "admin",
        "user": "root",
        "database": "test",
        "access": "proxy"
    }
    response = requests.post(url=url, data=body)
    if response.status_code == 200:
        print("add datasource MySQL success")
    else:
        print("Error Code：" + str(response.status_code))
        print("Error Message: \n" + str(response.content.decode()))


def get_current_panels():
    # 从当前的grafana上获取panel对象
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = requests.get('http://admin:admin@localhost:30000/api/dashboards/uid/HpA728Hnk', headers=headers)
    pprint(response.text)
    jsonobj = json.loads(response.text)
    panels = jsonpath.jsonpath(jsonobj, "$..panels")[0]
    max_id = 1
    title_list = []
    for panel in panels:
        max_id = panel.get("id") if panel.get("id") > max_id else max_id
        title_list.append(panel.get('title'))
    return panels, max_id, title_list


def post_json(table_name):
    panels_list = [
        {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
         'fillGradient': 0, 'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 0}, 'hiddenSeries': False, 'id': 8,
         'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                    'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
         'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
         'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
            {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
             'rawSql': 'SELECT\n  $__timeGroupAlias(time,10s),\n  avg(memory) AS "MEM"\nFROM my_memory\nWHERE\n  $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,10s)',
             'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
             'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [], 'timeFrom': None,
         'timeRegions': [], 'timeShift': None, 'title': 'MEM',
         'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
         'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
         'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                   {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
         'yaxis': {'align': False, 'alignLevel': None}},
        {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
         'fillGradient': 0, 'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 0}, 'hiddenSeries': False, 'id': 6,
         'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                    'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
         'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
         'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
            {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
             'rawSql': 'SELECT\n  $__timeGroupAlias(time,10s),\n  avg(fps) AS "FPS"\nFROM my_fps\nWHERE\n  $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,10s)',
             'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
             'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [], 'timeFrom': None,
         'timeRegions': [], 'timeShift': None, 'title': 'FPS',
         'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
         'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
         'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                   {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
         'yaxis': {'align': False, 'alignLevel': None}},
        {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
         'fillGradient': 0, 'gridPos': {'h': 9, 'w': 12, 'x': 0, 'y': 8}, 'hiddenSeries': False, 'id': 2,
         'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                    'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
         'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
         'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
            {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
             'rawSql': 'SELECT\n  $__timeGroupAlias(time,10s),\n  avg(gpu_Device) AS "GPU"\nFROM my_gpu\nWHERE\n  $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,10s)',
             'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
             'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [], 'timeFrom': None,
         'timeRegions': [], 'timeShift': None, 'title': 'GPU',
         'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
         'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
         'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                   {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
         'yaxis': {'align': False, 'alignLevel': None}},
        {'aliasColors': {}, 'bars': False, 'dashLength': 10, 'dashes': False, 'datasource': 'MySQL', 'fill': 1,
         'fillGradient': 0, 'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 8}, 'hiddenSeries': False, 'id': 4,
         'legend': {'avg': False, 'current': False, 'max': False, 'min': False, 'show': True, 'total': False,
                    'values': False}, 'lines': True, 'linewidth': 1, 'nullPointMode': 'null',
         'options': {'dataLinks': []}, 'percentage': False, 'pointradius': 2, 'points': False, 'renderer': 'flot',
         'seriesOverrides': [], 'spaceLength': 10, 'stack': False, 'steppedLine': False, 'targets': [
            {'format': 'time_series', 'group': [], 'metricColumn': 'none', 'rawQuery': True,
             'rawSql': 'SELECT\n  $__timeGroupAlias(time,10s),\n  avg(use_cpu) AS "CPU"\nFROM my_cpu\nWHERE\n  $__timeFilter(time)\nGROUP BY 1\nORDER BY $__timeGroup(time,10s)',
             'refId': 'A', 'select': [[{'params': ['value'], 'type': 'column'}]], 'timeColumn': 'time',
             'where': [{'name': '$__timeFilter', 'params': [], 'type': 'macro'}]}], 'thresholds': [], 'timeFrom': None,
         'timeRegions': [], 'timeShift': None, 'title': 'CPU',
         'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'}, 'type': 'graph',
         'xaxis': {'buckets': None, 'mode': 'time', 'name': None, 'show': True, 'values': []},
         'yaxes': [{'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True},
                   {'format': 'short', 'label': None, 'logBase': 1, 'max': None, 'min': None, 'show': True}],
         'yaxis': {'align': False, 'alignLevel': None}}]
    data = '''
    {
      "dashboard": {
        "id": null,
        "uid": null,
        "title": "%s",

        "timezone": "browser",
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
    ''' % (table_name, str(json.dumps(panels_list)))
    pprint(data)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    response = requests.post(url="http://admin:admin@localhost:30000/api/dashboards/db", data=data, headers=headers)
    print(response)
    print(response.text)
    response_dict = ast.literal_eval(response.text)
    return "http://localhost:30000" + response_dict['url'] + "?orgId=1&from=now-5m&to=now"


if __name__ == "__main__":
    # grafana_url = post_json('92b2_0928_2228')
    # webbrowser.open(grafana_url)
    set_anonymous()
