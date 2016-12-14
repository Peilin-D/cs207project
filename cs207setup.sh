#!/bin/bash

# update / upgrade the current software libraries
sudo apt-get update
sudo apt-get --upgrade

# install Python3 pip and development essentials + the psycopg2 library for PostgreSQL access
printf "\n*******************************************************"
printf "\nInstalling virtualenv, python3-pip, python3-dev, and psycopg2 ...\n"
sudo apt-get install python3-pip python3.4-dev apache2 libapache2-mod-wsgi-py3

# "~" specifies the AWS EC2 instance home directory for virtual environment
# cd ~
# mkdir venvs

# use the AWS EC2 Ubuntu 16.04 instance python3 installation
# virtualenv --python=/usr/bin/python3 venvs/flaskproj
# source ~/venvs/flaskproj/bin/activate

printf "\n*******************************************************"
printf "\nUpgrading pip ...\n"
sudo pip3 install --upgrade pip

# install numpy for Python3
printf "\n*******************************************************"
printf "\nInstalling numpy ...\n"
sudo pip3 install numpy scipy

printf "\n*******************************************************"
printf "\nInstalling Flask and SQL Alchemy ...\n"

# install flask and SQLAlchemy for Python3
sudo pip3 install flask flask_sqlalchemy flask_bootstrap flask_wtf

# git clone
sudo apt-get install git

cd /var/www/
sudo git clone https://github.com/rubix-cube/cs207project.git

# install timeseries module and rbtree module
cd cs207project/timeseries
sudo python3 setup.py install

cd ../cs207rbtree/
sudo python3 setup.py install

# change permission for cs207project
cd /var/www/
sudo chmod 777 cs207project/

# change permission for ui
cd cs207project/
sudo chmod 777 ui/
cd ui
sudo chmod 777 app.db

# change permission for simsearch/ts_db_index/
cd  /var/www/cs207project/simsearch/
sudo chmod -R 777 ts_db_index/

# mv config file to sites-available, and enable
sudo mv /var/www/cs207project/cs207.conf /etc/apache2/sites-available/
cd /etc/apache2/sites-available
sudo a2ensite cs207
sudo a2enmod wsgi
sudo service apache2 restart
sudo service apache2 reload
cd /etc/apache2/sites-enabled
sudo rm 000-default.conf

# uncomment below when release
cd /var/www/cs207project/
python3 StorageManagerServer.py --update &
python3 RBTreeServer.py &


