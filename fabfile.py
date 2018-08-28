# -*- coding: utf-8 -*-

#Date£º2018/08/27
#Author£ºqiankunhansheng
#Mail£ºacths@outlook.com
#Features£ºUse to deploy software in centOS such as JDK nginx memcache ...(Continuous update)
#Version£º1.0

from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

import os
import sys

#set information about ssh host list
env.roledefs = {
		'host1' : ['root@192.168.1.2'] ,
		'host2' : ['root@192.168.1.3'] ,
		'host3' : ['root@192.168.1.4'] ,
}

env.passwords = {
		'root@192.168.1.2:22' : '123456' ,
		'root@192.168.1.3:22' : '123456' ,
		'root@192.168.1.4:22' : '123456' ,
}

#set error info with red color and warning with pink color
env.colorize_errors = True
#close task which is already finished to avoid too much conversation
env.eagerly_disconnect = True
#change into bite stdout under the mode of parallel
env.linewise = True
#set all tasks excute with parallel mode
env.parallel = True
#set the number of concurrent processes default by cpu core
env.pool_size = 4

#set base parameter in system enviroment 
@roles('host1' , 'host2' , 'host3')
def setBaseEnv():
	host1 = str(env.roledefs["host1"]).split('@' , 1)[1]
	host2 = str(env.roledefs["host2"]).split('@' , 1)[1]
	host3 = str(env.roledefs["host3"]).split('@' , 1)[1]
	
	hostIP1 = host1.split("'" ,1)[0]
	hostIP2 = host2.split("'" ,1)[0]
	hostIP3 = host3.split("'" ,1)[0]
	
	with settings(warning_only = True):
		#set fast DNS of hosts
		run('echo -e "{0} host1\n{1} host2\n{2} host3\n" >> /etc/hosts'.format(hostIP1 , hostIP2 , hostIP3)
		run("cat hosts")

		#set language
		run("echo LANG=en_US.UTF-8 > /etc/sysconfig/i18n")
		run("source /etc/sysconfig/i18n")
		run("echo $LANG")

		#close the iptables and selinux forever
		run("chkconfig iptables off")
		run("chkconfig --list iptables")
		run("sed -i 's/enforcing/disabled/g' /etc/selinux/config")
		run("cat /etc/selinux/config")

		#set localtime
		run("\cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime")
		run("cat /etc/localtime")

		#set file limit
		run('echo -e "*    soft    nofile    65536\n*    hard    nofile    65536" >> /etc/security/limits.conf')
		run("cat /etc/security/limits.conf")
		run("sed -i '/1024/s/^/#/' /etc/security/limits.d/90-nproc.conf")
		
		#close THP
		run('echo -e "never > /sys/kernel/mm/redhat_transparent_hugepage/defrag" >> /etc/rc.local')
		run('echo -e "never > /sys/kernel/mm/redhat_transparent_hugepage/enabled" >> /etc/rc.local')
		run('echo -e "never > /sys/kernel/mm/transparent_hugepage/defrag" >> /etc/rc/local')
		run('echo -e "never > /sys/kernel/mm/transparent_hugepage/enabled" >> /etc/rc/local')

		#deploy gcc gcc-c++
		run('yum install -y gcc gcc-c++')
			
		#mkdir,after that , it is supposed to be the default dir which uoload  opensource software   
		run('mkdir -p /software')

		#reboot
		reboot()

#display the info of help		
def help():
        print("Usage list : fab setBaseEnv\n"
                "                   fab -H hostIPorName deployJDK\n"
                "                   fab -H hostIPorName deployMemcache\n"
				"					fab -H hostIPorName startMemcache:memory=128,user=root,IP=127.0.0.1,port=12000,connections=1024,pid=/tmp/memcached.pid\n"
				"					fab -H hostIPorName deployNginx\n"					 
				"					fab -H hostIPorName startNginx\n"
				"					"
				"					"
				"					"
				"					"
				"					"
				"					"
				"					"
				"					"
				)
						

#deploy java jdk
def deployJDK():
	with cd('/software'):
		run('tar -xf jdk-8u144-linux-x64.tar.gz')
		run('mv jdk1.8.0_144 jdk1.8')
	with cd('/etc') , shell_env(JAVA_HOME = '/software/jdk1.8'):
		run('echo -e "JAVA_HOME=$JAVA_HOME\nCLASSPATH=.:$JAVA_HOME/lib:$JAVA_HOME/jre/lib\nPATH=$JAVA_HOME/bin:$PATH:$JAVA_HOME/jre/bin\nexport JAVA_HOME CLASSPATH PATH" >> profile')
		run('source profile')
		run('java -version')
		
#deploy memcache
def deployMemcache():
	with cd('/software'):
		run('tar -xf libevent-2.0.20-stable.tar.gz')
		run('tar -xf memcached-1.4.29.tar.gz')
	with cd('/software/libevent-2.0.20-stable'):
		run('./configure --prefix=/software/libevent')
		run('make')
		run('make install')
	with cd('/software/memcached-1.4.29')
		run('./configure --prefix=/software/memcached --with-libevent=/software/libevent')
		run('make')
		run('make install')

#start memcache
def startMemcache(memory , user , IP , port , connections , pid):
	with cd('/software/memcache/bin'):
		run('./memcached -d -m %s -u %s -l %s -p %s -c %s -P %s' % (memory , user , IP , port , connections , pid))
		
#deploy nginx
def deployNginx():
	with cd('/software'):
		run('service httpd stop')
		run('chkconfig httpd off')
		run('unzip nginx.zip')
		run('tar -xf nginx-1.8.1.tar.gz')
		run('tar -xf openssl-1.0.2j.tar.gz')
		run('tar -xf pcre-8.21.tar.gz')
		run('tar -xf zlib-1.2.7.tar.gz')
		run('unzip nginx-http-concat-master.zip')
		run('unzip nginx_upstream_check_module-master.zip')
	with cd('/software/nginx-1.8.1'):
		run('./configure --prefix=/software/nginx --with-pcre=/software/pcre-8.21 --with-zlib=/software/zlib-1.2.7 --add-module=/software/nginx-http-concat-master --add-module=/software/nginx_upstream_check_module-master --with-http_ssl_module  --with-openssl=/software/openssl-1.0.2j --with-http_realip_module')
		run('make')
		run('make install')
		run('/software/nginx/sbin/nginx -t')
		
#start nginx after 
def startNginx():
	with cd('/software/nginx/sbin'):
		run('./nginx')