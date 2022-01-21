# iOS-perf

This is a Performance Monitoring Tool for iOS device. OS X, Windows, Linux all support. USB or Wireless.

Data type including GPU, CPU, Memery, FPS, Battery, Network, Temporary, also lots of iPhone info.

This project is based on the draft of jlintxia's. Performance data is from `tidevce` and `py-ios-device`, which implement `instruments`.

ATTENTION：This project use `MySQL` to save data，and use `Grafana` to show the real-time charts. YOU HAVE TO SET UP THESE TWO SERVICE. `docker-compose` in this project is the best choice to set up.



## REAL-TIME Charts

![](iOS-perf-3x.gif)

  





## Preparation

install docker and docker-compose

>https://dockerdocs.cn/get-docker/
>
>https://dockerdocs.cn/get-started/08_using_compose/

install python

>https://www.python.org/downloads/


### Server

run in cli:

```
docker -v && docker-compose -v
```

If the outputs contain versions info means you succeed

>Docker version 20.10.8, build 3967b7d
>
>docker-compose version 1.29.2, build 5becea4c

Pull image and run：

```
docker-compose up -d  
```
**Tips：first time accessing `Grafana`, you will be asked to change your default account. YOU'D BETTER IGNORE IT，keeping the username and password as `admin`，or you need to pass new username and password. **



### Local Env

run in cli:

```
pip install -r requirements.txt
```








## Command
run in cli:
```shell
python run.py --udid=00008110-001A4D483CF2801E \
--bundleid=com.apple.Preferences \
--grafana_host=localhost \
--grafana_port=30000 \
--grafana_user=admin \
--grafana_password=admin \
--mysql_host=localhost \
--mysql_port=33306 \
--mysql_username=root \
--mysql_password=admin \
--mysql_db=iOSPerformance
```


### Parameters



#### Target Parameters

>- --bundleid：bundle id for your app，using `ideviceinstaller -l`to see all，default value is `com.apple.Preferences`
>- --udid iPhone udid using `idevice_id -l` to get this. If you connect only one device, no need to pass



#### Grafana Parameters

> - --grafana_host：Grafana host，without Scheme，without`http://`or`https//`，default value is localhost
> - --grafana_port：Grafana port，default value is 30000
> - --grafana_user：Grafana username，default value is admin
> - --grafana_password：Grafana password，default value is admin



#### MySQL Parameters

> - --mysql_host：MySQL host，without Scheme，without`http://`or`https//`，default value is localhost
> - --mysql_port：MySQL port，default value is 33306
> - --mysql_user：MySQL username，default value is root
> - --mysql_password：MySQL password，default value is admin



## Export as Excel

run in cli:
```shell
python mysql.py --runid=iphone6_1008_1532 \
--mysql_host=localhost \
--mysql_port=33306 \
--mysql_username=root \
--mysql_password=admin \
--mysql_db=iOSPerformance
```

`--runid` is necessary，you can found this on the left top of `Grafana` page, or the url.，the pattern is like `PhoneName + Datetime`.

