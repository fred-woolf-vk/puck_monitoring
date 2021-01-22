#!/bin/sh

sudo apt-get update -y
sudo apt-get install python3-pip -y
echo "--------------------------------------------------------------------------------"

sudo python3 -m pip install influxdb 
echo "--------------------------------------------------------------------------------"

sudo apt-get install influxdb -y
echo "--------------------------------------------------------------------------------"

sudo apt-get install prometheus-node-exporter -y
echo "--------------------------------------------------------------------------------"

sudo apt-get install prometheus -y
echo "--------------------------------------------------------------------------------"

cd /
sudo mkdir -p /home/user/influxdb
sudo chmod 755 /home/user/influxdb
cd /home/user/influxdb
rm -f *.1
rm -f collect_db_stats.py
rm -f get_modem_status.py
rm -f puck_monitoring_service.service
rm -f puck_monitoring_script.sh
echo "--------------------------------------------------------------------------------"
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/collect_db_stats.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/get_modem_status.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/puck_monitoring_script.sh
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/puck_monitoring_service.service
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/prometheus
echo "--------------------------------------------------------------------------------"
sudo chmod 755 collect_db_stats.py
sudo chmod 755 get_modem_status.py
sudo chmod 777 puck_monitoring_script.sh
sudo chmod 755 prometheus

echo "--------------------------------------------------------------------------------"
systemctl stop puck_monitoring_service
systemctl stop prometheus

# prometheus service starts automatically; set prometheus max storage for 2 days
#   in /etc/default/prometheus and restart below
sudo mv -f prometheus /etc/default
sudo mv -f puck_monitoring_service.service /etc/systemd/system
sudo systemctl daemon-reload

# start puck monitoring service
systemctl enable puck_monitoring_service
systemctl start puck_monitoring_service

# start prometheus service
systemctl enable prometheus
systemctl start prometheus
echo "--------------------------------------------------------------------------------"

