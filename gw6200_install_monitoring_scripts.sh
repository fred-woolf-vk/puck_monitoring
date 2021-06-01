#!/bin/sh

# NB: This script must be run as root or sudo

apt-get update -y
apt-get install python3-pip -y
echo "--------------------------------------------------------------------------------"

apt-get install prometheus -y
echo "--------------------------------------------------------------------------------"
apt-get install prometheus-node-exporter -y
echo "--------------------------------------------------------------------------------"
pip3 install prometheus-client
echo "--------------------------------------------------------------------------------"

mkdir -p /home/user/gw6200_scripts
chmod 755 /home/user/gw6200_scripts
cd /home/user/gw6200_scripts
rm -f *.1

echo "--------------------------------------------------------------------------------"
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/collect_db_stats_prometheus.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/get_modem_status.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/prometheus.yml
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/gw6200_exporter.service
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/gw6200_exporter_params.txt
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/gw6200_monitoring_script.sh
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/update_monitoring_scripts_from_repo.sh 
echo "--------------------------------------------------------------------------------"

chmod 755 gw6200_monitoring_script.sh
chmod 755 collect_db_stats_prometheus.py
chmod 755 get_modem_status.py
mv prometheus.yml /etc/prometheus/
chmod 755 /etc/prometheus/prometheus.yml

# set up monitoring as a service
mv gw6200_exporter.service /etc/systemd/system/
chmod 777 /etc/systemd/system/gw6200_exporter.service
echo "--------------------------------------------------------------------------------"

systemctl daemon-reload
# prometheus service starts automatically; restart to pick up retention policy changes 
systemctl enable prometheus
systemctl restart prometheus
systemctl enable prometheus-node-exporter
systemctl restart prometheus-node-exporter
systemctl enable gw6200_exporter
systemctl restart gw6200_exporter
