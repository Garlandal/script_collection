##一些常用的python脚本集合

###[proxy_spider](https://github.com/Garlandal/script_collection/blob/master/proxy_spider.py 'proxy_spider' )

这是一个本地快速抓取代理并验证的脚本，目前可以抓取两个网站上的代理，结果保存在以当天日期为文件名的txt文件中，也可以把代理发送给指定邮箱

安装所需的库
```bash
$ sudo pip install requests gevent
```

###[proxy_server](https://github.com/Garlandal/script_collection/blob/master/proxy_server.py 'proxy_server' )

这是一个快速抓取代理验证并定时更新的服务端

安装所需的库
```bash
$ sudo apt-get install redis-server
$ sudo pip install requests gevent redis tornado
```
