#!/user/bin/env python
# coding=utf8


import requests
import urllib2
import datetime
import re
import smtplib
import time
import gevent
import gevent.monkey

gevent.monkey.patch_socket()

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr


class Spider():
    """Get proxy and confirm it"""

    def __init__(self):
        self.confirm_url = 'http://www.baidu.com'
        self.from_addr = ''
        self.password = ''
        self.to_addr = ''
        self.smtp_server = ''

    def get_proxy(self, url):
        pass

    def check(self, proxy):
        proxies = {
            "http": str(proxy),
        }
        try:
            resp = requests.get(self.confirm_url, proxies=proxies, timeout=2)
        except Exception, e:
            print '\033[1;35mConfirming: {proxy}\t False\033[0m'.format(proxy=proxy)
        else:
            if resp.status_code == 200:
                print '\033[1;32mConfirming: {proxy}\t OK \t200\033[0m'.format(proxy=proxy)
                with open(''.join([str(datetime.date.today()), '.txt']), 'a') as f:
                    f.writelines(''.join([proxy, '\n']))
            else:
                print '\033[1;37mConfirming: {proxy} \t ERROR \t{code}\033[0m'.format(proxy=proxy,
                                                                                      code=resp.status_code)

    def confirm_proxy(self, proxies):
        threads = [gevent.spawn(self.check, i) for i in proxies]
        gevent.joinall(threads)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr))


    def send_mail(self):
        msg = MIMEMultipart()
        msg['From'] = self._format_addr(u'Test <%s>' % self.from_addr)
        msg['Subject'] = Header(u"Today's proxies", 'utf-8').encode()

        msg.attach(MIMEText(''.join(['This is ', str(datetime.date.today()), ' proxies']), 'plain', 'utf8'))

        filename = ''.join([str(datetime.date.today()), '.txt'])
        att = MIMEText(open(filename, 'r').read(), 'utf-8', 'utf-8')
        att['Content-Type'] = 'application/octet-stream'
        att['Content-Dispostion'] = 'attachment; filename=%s' % filename
        msg.attach(att)

        server = smtplib.SMTP(self.smtp_server, 25)
        server.set_debuglevel(1)
        server.login(self.from_addr, self.password)
        server.sendmail(self.from_addr, [self.to_addr], msg.as_string())
        server.quit()


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
        proxy_site.confirm_proxy(iplists)
