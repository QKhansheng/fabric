Before Using the script you must deploy the python.fabric in your system (RH/CentOS)

Here is the setup:

	1: download python source code by following this URL:https://www.python.org/downloads/source/ , Our script is coding on python27
	
	2: start deploy python in your system by the setup 
		1)  yum install -y gcc gcc-c++ zlib-devel openssl-devel
		2)  cd /usr/local	
		3)  tar -xf Python-2.7.14.tgz
	 	4)  cd Python-2.7.14
	 	5)  vim Modules/Setup.dist

		" Please remove these comments !"
		#zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz 
		# _socket socketmodule.c timemodule.c
	 	# _ssl _ssl.c \
	 	#-DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
	 	#-L$(SSL)/lib -lssl -lcrypto

		6)  ./configure --prefix=/usr/local/python2.7
		7)  make
		8)  make install

	3: deploy python.pip
		/usr/local/python2.7/bin/python get-pip.py 

	4: deploy python.fabric
		/usr/local/python2.7/bin/pip install fabric==1.10.0
		/usr/local/python2.7/bin/pip install pycrypto
		ln -s /usr/local/python2.7/bin/fab /usr/bin/fab

Through the above steps, we successfully deployed python.fabric , next you can type the cmd "fab help" to see how to use this script!

If you got any idea to imporve the script , you'll always be grateful to send a Email to me , thank you! :)
