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

if [ $# -lt 2 ]; then
    echo "usage: $0 host port" >/dev/stderr
    exit 123
fi

site=$1
host=$2
port=$3

cd src

#exec uwsgi --http ${host}:${port} --module ${site}_wsgi --callable app --gevent 2000 -l 1000 -p 8 -L
exec gunicorn -b$host:$port -w7 -kgevent ${site}_wsgi:app
