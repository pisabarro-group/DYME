#!/usr/bin/env bash
mkdir -p /dyme_root/logs /dyme_root/data/db /dyme_root/projects /dyme_root/nodes/source /dyme_root/database/mongodb
chown -R mongodb:mongodb /dyme_root/logs /dyme_root/database/mongodb
chown -R www-data:www-data /dyme_root/projects
chown -R www-data:www-data /dyme_base/backend

chmod -R 777 /dyme_root/logs
chmod -R 777 /dyme_root/projects
chmod -R 755 /dyme_base/backend

# Update or clone the frontend from GitHub on every start
REPO_URL="https://github.com/pisabarro-group/DYME.git"
FRONTEND_DIR="/dyme_base/frontend"

echo "Updating frontend from GitHub..."
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" /tmp/dyme_repo
git -C /tmp/dyme_repo sparse-checkout set frontend
cp -R /tmp/dyme_repo/frontend/. "$FRONTEND_DIR/"
rm -rf /tmp/dyme_repo
chown -R www-data:www-data "$FRONTEND_DIR"


#Start Apache2 and WSGI module from the dyme_main environment
export CONDA_ENV=/dyme_env/anaconda/envs/dyme_main
export LD_LIBRARY_PATH="${CONDA_ENV}/lib:${LD_LIBRARY_PATH}"
export LD_PRELOAD="${CONDA_ENV}/lib/libstdc++.so.6"

#Start like this so it reads our LD_LIB preferences
#This is a hack to make the environment work with apache.. standard libstdc misses the symbols
#necesary for openmm and some other packages
/usr/sbin/apache2ctl start


#Start MongoDB 
#service mongod start
#mongod --bind_ip_all --config /etc/mongod.conf
gosu mongodb mongod --bind_ip_all --config /etc/mongod.conf


