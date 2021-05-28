#!/bin/sh

echo " ----------------------   stop monitoring service"
systemctl stop puck_monitoring_service.service

cd /home/user/gw6200_exporter
rm -f collect_db_stats_prometheus.py
rm -f get_modem_status.py

echo " ----------------------   get updated files "
wget https://raw.githubusercontent.com/fred-woolf-vk/gw6200_monitoring/master/collect_db_stats_prometheus.py
wget https://raw.githubusercontent.com/fred-woolf-vk/gw6200_monitoring/master/get_modem_status.py

chmod 755 collect_db_stats_prometheus.py
chmod 755 get_modem_status.py

echo " ----------------------   restart monitoring service "
systemctl restart gw6200_exporter.service
