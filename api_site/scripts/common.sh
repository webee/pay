#!/usr/bin/env bash

ENV_FILE=${HOME}/.pay_env.sh

if [ -f ${ENV_FILE} ]; then
    source ${ENV_FILE}
fi
