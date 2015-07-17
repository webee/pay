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


cd lianlian_mock/

exec celery "$@"
