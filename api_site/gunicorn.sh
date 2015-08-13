#!/usr/bin/env bash

env=${1:-dev}
host=${2:-127.0.0.1}
port=${3:-5000}

PROJ_ROOT=$(dirname $0)
NAME="pay-api-site"
FLASK_DIR=${PROJ_ROOT}/src
VENV_DIR=${PROJ_ROOT}/api_venv
NUM_WORKERS=${NUM_WORKERS:-8}

echo "Starting $NAME"

# activate the virtualenv
source ${VENV_DIR}/bin/activate

export PYTHONPATH=$FLASK_DIR:$PYTHONPATH

# Start your unicorn
export ENV=${env}
exec gunicorn main:app -b ${host}:${port} \
  --name $NAME \
  -k gevent \
  -w $NUM_WORKERS \
  --log-level=info \
