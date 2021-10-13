# iOS-perf

这是一款iOS性能监控工具，支持Mac以及Windows端运行，电脑通过USB连接手机后运行脚本即可。

本项目基于jlintxia开源的iOS测试方案修改而来，增加动态建表，动态增加grafana面板以及docker打包环境等特性。其中iOS性能数据来源于开源工具tidevice和py-ios-device。





## 效果展示

![](iOS-perf-3x.gif)

  





## 准备工作

服务端搭建依赖docker以及docker-compose，安装指南：

>https://dockerdocs.cn/get-docker/
>
>https://dockerdocs.cn/get-started/08_using_compose/

运行测试依赖python3环境，安装指南：

>https://www.python.org/downloads/

  







### 服务端搭建

命令行运行

`docker -v && docker-compose -v`

如果能正常输出版本，如下，则表示docker环境正常，可以继续

>Docker version 20.10.8, build 3967b7d
>
>docker-compose version 1.29.2, build 5becea4c

拉取镜像并启动服务：

`docker-compose up -d  `

  







### 本地环境搭建

命令行执行

`pip install -r requirements.txt`



  





## 运行命令
命令行执行：

`python run.py --udid=00008101-00XXXXXXXXXX \`

 `
--bundleid=com.apple.Preferences \`

 `
--grafana_host=localhost \`

 `
--grafana_port=30000 \`

 `
--grafana_user=admin \`

 `
--grafana_password=admin \`

 `
--mysql_host=localhost \`

 `
--mysql_port=33306 \`

 `
--mysql_username=root \`

 `
--mysql_password=admin \`

 `
--mysql_db=iOSPerformance `





  





### 运行参数说明



#### 建议修改参数

>- --bundleid：待测APP的包名，通过`ideviceinstaller -l`获取，默认值为`com.apple.Preferences`
>- --udid iPhone：手机的唯一标识符，通过 `idevice_id -l` 获取，客户端只连接一台手机时不用写

  



#### Grafana可选参数

> - --grafana_host：Grafana的主机地址，只写ip，不用写Scheme，也就是`http://`或者`https//`，默认值localhost
> - --grafana_port：Grafana的端口号，默认值30000
> - --grafana_user：Grafana的用户名，默认值admin
> - --grafana_password：Grafana的密码，默认值admin

  



#### MySQL可选参数

> - --mysql_host：MySQL的主机地址，不用写Scheme，也就是`http://`或者`https//`，默认值localhost
> - --mysql_port：MySQL的端口号，默认值33306
> - --mysql_user：MySQL的用户名，默认值root
> - --mysql_password：MySQL的用户名，默认值admin

  



## 数据导出

命令行执行：

`python mysql.py --runid=iphone6_1008_1532 \`

 `
--mysql_host=localhost \`

 `
--mysql_port=33306 \`

 `
--mysql_username=root \`

 `
--mysql_password=admin \`

 `
--mysql_db=iOSPerformance `



  







其中，`--runid`为必须参数，可以从显示测试数据的Grafana页面的左上角找到，通常为手机名称+月日+时分。其余Mysql参数均为可选参数，默认值与上方[MySQL可选参数](#MySQL可选参数)相同。
