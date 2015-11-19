#!/usr/bin/env bash

env=${1:-dev}
name=${2:-api_venv}

PROJ_ROOT=$(dirname $(dirname $0))
VENV_DIR=${PROJ_ROOT}/${name}

source ${PROJ_ROOT}/scripts/common.sh
# activate the virtualenv
source ${VENV_DIR}/bin/activate

${PROJ_ROOT}/src/manager.py -e ${env} query_notify_refund
