# cs207project
For this project we've implemented 3 modules.

To use the *TimeSeries* module, from the root directory, `$ cd timeseries` and `$ python setup.py install` to install the package to your python site-packages. More details can be found [here](https://github.com/rubix-cube/cs207project/tree/master/timeseries).

For the *cs207rbtree* module, there's a PyPI version that you can directly pip install, but we recommand to install it by `$ cd cs207rbtree` and `$ python setup.py install`, since the version on PyPI may be outdated. See [here](https://github.com/rubix-cube/cs207project/tree/master/cs207rbtree) for more details.

The *similarity search* module and its usage can be found [here](https://github.com/rubix-cube/cs207project/tree/master/simsearch).

#How to deploy the Web-interface on AWS EC2
* Launch a EC2 instance with Ubuntu Server 14.04, during the launching process add a new rule to the security group "HTTP -- From Anywhere"
* Connect to your EC2 instance using ssh
* At the desktop of your EC2 instance desktop, git clone this directory
```
git clone https://github.com/rubix-cube/cs207project.git
``` 
* Get into the cs207project folder and run the setup bash
``` 
cd cs207project/
chmod a+x cs207setup.sh
./cs207setup.sh
``` 
* Now your server is running. Access your web-interface from browser by typing in your AWS public DNS address

[![Build Status](https://travis-ci.org/rubix-cube/cs207project.svg?branch=master)](https://travis-ci.org/rubix-cube/cs207project)

[![Coverage Status](https://coveralls.io/repos/github/Peilin-D/cs207project/badge.svg?branch=master)](https://coveralls.io/github/Peilin-D/cs207project?branch=master)
