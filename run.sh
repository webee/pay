#!/usr/bin/env bash
#set -x
#set -e
source $(dirname $0)/scripts/env_conf.sh

root=$(dirname $(${abspath} $0))
cd ${root}
source /etc/profile
source ${root}/env.local.sh
if [ $? -ne 0 ]; then
    echo "${root}/env.local.sh not exists." >/dev/stderr
    echo "need local env config." >/dev/stderr
    exit 123
fi

site=${1:-api}
host=${2:-0.0.0.0}
port=${3:-5000}

mkdir -p logs
cd src

#exec uwsgi --http ${host}:${port} --module ${site}_wsgi --callable app --gevent 2000 -l 1000 -p 8 -L
export SITE=${site}
exec gunicorn -b${host}:${port} -w7 -kgevent wsgi:app -ngunicorn-${site} --max-requests 100 -c ${root}/conf/gunicorn.conf.py
