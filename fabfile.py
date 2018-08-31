# -*- coding: utf-8 -*-

#Date: 2018/08/27
#Author: qiankunhansheng
#Mail: acths@outlook.com
#Features: Use to deploy software in centOS such as JDK nginx memcache ...(Continuous update)
#Version: 1.0

from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

import os
import sys

#set information about ssh host list
env.roledefs = {
		'host1' : ['root@192.168.39.73'] ,
}
	
env.passwords = {
		'root@192.168.39.73:22' : '123456' ,
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
env.pool_size = 2

#set base parameter in system enviroment 
def setBaseEnv():
	host1 = str(env.roledefs["host1"]).split('@' , 1)[1]
	
	hostIP1 = host1.split("'" ,1)[0]
	
	with settings(warning_only = True):
		#set fast DNS of hosts
		run('echo -e "{0} host1" >> /etc/hosts'.format(hostIP1))
		run('cat /etc/hosts')

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
        print("Usage list : fab -H IP setBaseEnv\n"
		"             fab -H IP deployJDK\n"
                "             fab -H IP deployMemcache\n"
		"	     fab -H IP startMemcache:memory=128,user=root,IP=127.0.0.1,port=12000,connections=1024,pid=/tmp/memcached.pid\n"
		"	     fab -H IP deployNginx\n"					 
		"	     fab -H IP startNginx\n"
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
	with cd('/software/memcached-1.4.29'):
		run('./configure --prefix=/software/memcached --with-libevent=/software/libevent')
		run('make')
		run('make install')

#start memcache
def startMemcache(memory , user , IP , port , connections , pid):
	with cd('/software/memcached/bin'):
		run('./memcached -d -m %s -u %s -l %s -p %s -c %s -P %s' % (memory , user , IP , port , connections , pid))
		
#deploy nginx
def deployNginx():
	with cd('/software'):
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
		
#start nginx
def startNginx():
	with cd('/software/nginx/sbin'):
		run('./nginx')

#deploy Redis by cluster mode , it requires at least 3 machines ,each one will be runing 2 instances 
def deployRedis():
	with cd('/software'):
		run('tar -xf redis-3.2.8.tar.gz')

	with cd('/software/redis-3.2.8'):
		run('make')
		run('make install PREFIX=/software/redis')
		run('mkdir /software/redis-cluster')
		run('mkdir /software/redis-cluster/redis6371')
		run('mkdir /software/redis-cluster/redis6372')
		run('cp /software/redis/bin/* /software/redis-cluster/redis6371')
		run('cp /software/redis/bin/* /software/redis-cluster/redis6372')
		run("sed -i 's/127.0.0.1/0.0.0.0/g' redis.conf")
		run("sed -i '/protected-mode/s/yes/no/' redis.conf")
		run("sed -i '/daemonize no/s/no/yes/' redis.conf")
		run("sed -i '/cluster-enabled/s/^.*#//' redis.conf")
		run('cp redis.conf /software/redis-cluster/redis6371/redis6371.conf')
		run('cp redis.conf /software/redis-cluster/redis6372/redis6372.conf')

	with cd('/software/redis-cluster/redis6371'):
		run("sed -i '/port 6379/s/6379/6371/' redis6371.conf")
		run("sed -i '/pidfile/s/6379/6371/' redis6371.conf")
		run("sed -i '/logfile/s/{0}{1}/{2}{3}{4}/' redis6371.conf".format('"' , '"' , '"' , "redis6371.log" , '"'))
	
	with cd('/software/redis-cluster/redis6372'):
		run("sed -i '/port 6379/s/6379/6372/' redis6372.conf")
		run("sed -i '/pidfile/s/6379/6372/' redis6372.conf")
		run("sed -i '/logfile/s/{0}{1}/{2}{3}{4}/' redis6372.conf".format('"' , '"' , '"' , "redis6372.log" , '"'))

	run('cp /software/redis-3.2.8/src/redis-trib.rb /software/redis-cluster')

#start Redis
def startRedis():
	with cd('/software/redis-cluster/redis6371'):
		run('./redis-server /software/redis-cluster/redis6371/redis6371.conf')
	with cd('/software/redis-cluster/redis6372'):
		run('./redis-server /software/redis-cluster/redis6372/redis6372.conf')

#deploy ruby
def deployRuby():
	with cd('/software'):
		run('mkdir ruby')
		run('unzip ruby.zip')
		run('tar -xf ruby-2.4.1.tar.gz')
		run('tar -xf openssl-1.0.1f.tar.gz')
	with cd('/software/ruby-2.4.1'):
		run('./configure --prefix=/software/ruby')
		run('make')
		run('make install')
		run('ln -s /software/ruby/bin/ruby /usr/bin/ruby')
		run('ln -s /software/ruby/bin/gem /usr/bin/gem')
	with cd('/software/openssl-1.0.1f'):
		run('./config -fPIC --prefix=/software/openssl1f enable-shared')
		run('./config -t')
		run('make depend')
		run('make install')
	with cd('/software/ruby-2.4.1/ext/zlib'):
		run('yum install -y zlib zlib-devel')
		run('ruby extconf.rb')
		run("sed -i '16a top_srcdir = /software/ruby-2.4.1' Makefile")
		run('make')
		run('make install')
	with cd('/software/ruby-2.4.1/ext/openssl'):
		run('ruby extconf.rb --with-openssl-include=/software/openssl1f/include --with-openssl-lib=/software/openssl1f/lib')
		run("sed -i '16a top_srcdir = /software/ruby-2.4.1' Makefile")
		run('make')
		run('make install')
	with cd('/software'):
		run('gem install redis-4.0.1.gem')
		run('gem list')

#create redis cluster
def createRedisClu():
	with cd('/software/redis-cluster'):
		run('./redis-trib.rb create --replicas 1 host1:6371 host1:6372 host2:6371 host2:6372 host3:6371 host3:6372')


