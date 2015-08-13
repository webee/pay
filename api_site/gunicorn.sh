#!/usr/bin/env bash

env=${1:-dev}

PROJ_ROOT=$(dirname $0)
NAME="pay-api-site"
FLASK_DIR=${PROJ_ROOT}/src
VENV_DIR=${PROJ_ROOT}/venv
SOCK_FILE=${PROJ_ROOT}/run/pay_api.sock
USER=${USER:-lvye_pay}
GROUP=${GROUP:-lvye_pay}
NUM_WORKERS=${NUM_WORKERS:-8}

echo "Starting $NAME"

# activate the virtualenv
source ${VENV_DIR}/bin/activate

export PYTHONPATH=$FLASK_DIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUN_DIR=$(dirname $SOCK_FILE)
test -d $RUN_DIR || mkdir -p $RUN_DIR

# Start your unicorn
export ENV=${env}
exec gunicorn main:app -b 127.0.0.1:5000 \
  --name $NAME                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=info \
  --bind=unix:$SOCK_FILE
