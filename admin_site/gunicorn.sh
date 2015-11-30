#!/usr/bin/env bash

env=${1:-dev}
host=${2:-127.0.0.1}
port=${3:-5104}

PROJ_ROOT=$(dirname $0)
NAME="pay-admin-site"
FLASK_DIR=${PROJ_ROOT}/src
VENV_DIR=${PROJ_ROOT}/venv
NUM_WORKERS=${NUM_WORKERS:-8}
ENV_FILE=${HOME}/.pay_env.sh

echo "Starting $NAME"

# activate the virtualenv
source ${VENV_DIR}/bin/activate

export PYTHONPATH=$FLASK_DIR:$PYTHONPATH

# Start your unicorn
export ENV=${env}
if [ -f ${ENV_FILE} ]; then
    source ${ENV_FILE}
fi

exec gunicorn main:app -b ${host}:${port} \
  --name $NAME \
  -k gevent \
  -w $NUM_WORKERS \
  --access-logfile - \
  --access-logformat '%(h)s/%({X-Real-IP}i)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
  --log-level=info \
