#!/bin/bash

if [ -z $1 ];then
    echo "usage $0 [<PROGRAM_NAME> || ALL]"
    exit 1
fi
PROGRAM_NAME="$1"
if [ "$PROGRAM_NAME" = "ALL" ];then
    PROGRAM_NAME='*'
fi
TRACER_PATH=./tracer

if ! ls $TRACER_PATH/loader_and_logger &>/dev/null ; then
    echo building the tracer
    make -C $TRACER_PATH
fi

echo running tracer, stop via CTRL+C
sudo $TRACER_PATH/loader_and_logger "$PROGRAM_NAME"

echo formatting the tracer\'s output
python3 $TRACER_PATH/formatter.py trace.log

rm trace.log

echo formatted logs are written in the $PWD
