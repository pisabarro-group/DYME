#!/usr/bin/env bash
mkdir -p /dyme_root/logs /dyme_root/data/db /dyme_root/projects /dyme_root/nodes/source /dyme_root/database/mongodb
chown -R mongodb:mongodb /dyme_root/logs /dyme_root/database/mongodb
chown -R www-data:www-data /dyme_root/projects
chmod -R 775 /dyme_root/logs
chmod -R 775 /dyme_root/projects

#Start Apache2 and WSGI
export LD_PRELOAD=/dyme_env/anaconda/envs/dyme_main/lib/libpython3.11.so.1.0
service apache2 start &

#Start MongoDB 
#service mongod start
#mongod --bind_ip_all --config /etc/mongod.conf
gosu mongodb mongod --bind_ip_all --config /etc/mongod.conf


