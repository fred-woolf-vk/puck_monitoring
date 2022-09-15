# !/bin/sh

cd /home/user/gw6200_scripts
python3 configure_prometheus.py
cp prometheus.service  /usr/lib/systemd/system
systemctl daemon-reload
systemctl restart prometheus.service
systemctl status prometheus.service 

