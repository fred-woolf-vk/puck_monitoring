#!/bin/sh

# NB: This script must be run as root or sudo

apt-get update -y
apt-get install python3-pip -y
echo "--------------------------------------------------------------------------------"

python3 -m pip install influxdb 
echo "--------------------------------------------------------------------------------"

apt-get install influxdb -y
echo "--------------------------------------------------------------------------------"

apt-get install prometheus-node-exporter -y
echo "--------------------------------------------------------------------------------"

apt-get install prometheus -y
echo "--------------------------------------------------------------------------------"

cd /
mkdir -p /home/user/influxdb
chmod 755 /home/user/influxdb
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

chmod 755 collect_db_stats.py
chmod 755 get_modem_status.py
chmod 777 puck_monitoring_script.sh
chmod 755 prometheus 
# set up puck as a service
mv puck_monitoring_service.service /etc/systemd/system 
# set prometheus max retention argument
mv prometheus /etc/default/
echo "--------------------------------------------------------------------------------"

systemctl daemon-reload
# start puck monitoring service
systemctl enable puck_monitoring_service.service
systemctl restart puck_monitoring_service.service

# prometheus service starts automatically; restart to pick up retention policy changes 
systemctl enable prometheus
systemctl restart prometheus


