#!/bin/sh

echo " ----------------------   stop monitoring service"
systemctl stop puck_monitoring_service.service

cd /home/user/influxdb
rm -f collect_db_stats.py
rm -f get_modem_status.py

echo " ----------------------   get updated files "
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/collect_db_stats.py
wget https://raw.githubusercontent.com/fred-woolf-vk/puck_monitoring/master/get_modem_status.py

chmod 755 collect_db_stats.py
chmod 755 get_modem_status.py

echo " ----------------------   restart monitoring service "
systemctl restart puck_monitoring_service.service


