#!/bin/bash

# dev
export PROJ_ROOT=`pwd`
export PY_BIN_DIR=${PROJ_ROOT}/venv/bin
source ${PY_BIN_DIR}/activate
export SYSTEM_CONFIG=development

# prod
# export PROJ_ROOT=`pwd`
# export PY_BIN_DIR=/home/xx/python/bin
# source ${PY_BIN_DIR}/activate
# export SYSTEM_CONFIG=production
