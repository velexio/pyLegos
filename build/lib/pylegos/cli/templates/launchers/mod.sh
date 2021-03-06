#!/bin/bash
SOURCE="${BASH_SOURCE[0]}"
ModName=`echo ${SOURCE}|awk '{split($0,a,"/"); print a[length(a)]}'`
BinDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
InstallBase="$(dirname "$BinDir")"
export PYTHONPATH=$PYTHONPATH:${InstallBase}/app
$InstallBase/app/modules/${ModName}/${AppName}.py $@