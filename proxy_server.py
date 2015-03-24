#!/user/bin/env python
# coding=utf8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8000, help="run on the 8000 port", type=int)

import requests
import urllib2
import datetime
import re
import threadpool
import time
import redis
import gevent
import gevent.monkey

gevent.monkey.patch_socket()


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		greeting = self.get_argument('greeting', 'hello')
		self.write(greeting + ', user~')

# if __name__ == '__main__':
# 	tornado.options.parse_command_line()
# 	app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
# 	http_server = tornado.httpserver.HTTPServer(app)
# 	http_server.listen(options.port)
# 	tornado.ioloop.IOLoop.instance().start()

def make_proxy(func):
	def wrapper(self, proxy):
		proxies = {
		    "http": str(proxy)
		}
		return func(self, proxies)
	return wrapper


class Spider():
    """Get proxy and confirm it"""

    def __init__(self):
        self.confirm_url = 'http://www.baidu.com'
        self.cache = redis.StrictRedis(host='localhost', port=6379)

    def get_proxy(self, url):
        pass


    @make_proxy
    def check(self, proxy):
    	real_proxy = proxy.get('http')
        try:
            resp = requests.get(self.confirm_url, proxies=proxy, timeout=2)
        except Exception, e:
        	pass
        else:
            if resp.status_code == 200:
            	if not self.cache.hget('proxy', real_proxy):
            		self.cache.hset('proxy', real_proxy, 0)

    @make_proxy
    def redis_check(self,proxy):
    	print proxy
    	real_proxy = proxy.get('http')
    	value = int(self.cache.hget('proxy', real_proxy))
    	try:
    		resp = requests.get(self.confirm_url, proxies=proxy, timeout=2)
    	except Exception, e:
    		self.cache.hset('proxy', real_proxy, value+1)
    	else:
    		if resp.status_code != 200:
    			self.cache.hset('proxy', real_proxy, value+1)
    
    def redis_clean(self):
    	proxy_dic = self.cache.hgetall('proxy')
    	proxy_list = [proxy for proxy, value in proxy_dic.iteritems()]
    	self.confirm_proxy(self.redis_check, proxy_list)


    def confirm_proxy(self, func, proxies):
        threads = [gevent.spawn(func, i) for i in proxies]
        gevent.joinall(threads)



class Mesk(Spider):
    """Spider for Mesk.cn"""

    def __init__(self):
        Spider.__init__(self)
        self.url = 'http://www.mesk.cn/ip/china/'

    def get_proxy(self):
        content = requests.get(self.url).text
        pat0 = re.compile(r'<a href="(.*?)" class="ico"')
        link = ''.join(['http://www.mesk.cn', pat0.search(content).group(1)])
        new_content = requests.get(link).text
        pat1 = re.compile(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,6}')
        ip_ports = re.findall(pat1, new_content)
        print 'There are\033[1;33m {total} \033[0mproxies'.format(total=len(ip_ports))
        return ip_ports


class PaChong(Spider):
    """Spider for pachong.org"""

    def __init__(self):
        Spider.__init__(self)
        self.url = "http://pachong.org/high.html"

    def get_proxy(self):
        ip = []
        port = []
        content = requests.get(self.url).text
        pat0 = re.compile(r'<td>(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})</td>\s*<td><script>doc.*write(.*);</script></td>')
        animal = re.findall(re.compile(r'var (.*?);'), content)
        for i in animal[:5]:
            exec (i)
        for m, n in re.findall(pat0, content):
            ip.append(m)
            exec ("port.append(" + n + ")")
        ip_ports = [''.join([p[0], ':', str(p[1])]) for p in zip(ip, port)]
        print 'There are\033[1;33m {total} \033[0mproxies'.format(total=len(ip_ports))
        return ip_ports


if __name__ == "__main__":
    for proxy_site in [Mesk(), PaChong()]:
        iplists = proxy_site.get_proxy()
        proxy_site.confirm_proxy(proxy_site.check, iplists)
    Spider().redis_clean()