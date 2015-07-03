#!/bin/bash
source /etc/profile

if which greadlink >/dev/null 2>&1; then
    export abspath="greadlink -f"
else
    export abspath="readlink -f"
fi

if which gdate >/dev/null 2>&1; then
    export DATE=gdate
else
    export DATE=date
fi
