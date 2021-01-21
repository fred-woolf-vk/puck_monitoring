#!/bin/sh

sudo apt-get update -y
sudo apt-get install python3-pip -y
sudo python3 -m pip install influxdb 
sudo apt-get install influxdb -y
sudo apt-get install prometheus-node-exporter -y
sudo apt-get install prometheus -y

cd /
sudo mkdir -p /home/user/influxdb
sudo chmod 755 /home/user/influxdb
cd /home/user/influxdb
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/collect_db_stats.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/get_modem_status.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/puck_monitoring_service.service
sudo mv puck_monitoring_service.service /etc/systemd/service
sudo chmod 755 collect_db_stats.py
sudo chmod 755 get_modem_status.py
sudo chmod 777 puck_monitoring_script.sh

# set puck monitoring retention policy 

# start puck monitoring service
systemctl enable puck_monitoring_service.service
systemctl start puck_monitoring_service.service


# prometheus service starts automatically; set prometheus max storage 
#systemctl stop prometheus-node-exporter


