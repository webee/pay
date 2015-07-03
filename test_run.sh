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

site=$1

host=${2:-'127.0.0.1'}
port=${3:-2222}

python ./src/${site}_manager.py  runserver -h${host} -p${port} -r -d
