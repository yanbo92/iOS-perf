# iOS-perf

本项目基于jlintxia开源的iOS测试方案修改而来，增加动态建表，动态增加grafana面板以及docker打包环境等特性。其中iOS性能数据来源于开源工具tidevice和py-ios-device。



## 环境搭建

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

拉去镜像并启动服务：

`docker-compose up -d  `

### 

### 本地环境搭建

命令行运行

`pip install -r requirements.txt`



## 运行命令
命令行执行：

`python run.py --udid=XXXXXX --bundleid=com.insta360.oner`



### 运行参数说明

#### 必须参数

如果在本机直接运行Docker，可以只传这两个参数，其他均默认

> - --udid iPhone：手机的唯一标识符，通过 `idevice_id -l` 获取
> - --bundleid：待测APP的包名，通过`ideviceinstaller -l`获取



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