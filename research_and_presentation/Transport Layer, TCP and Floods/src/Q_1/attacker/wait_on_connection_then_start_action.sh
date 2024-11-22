#!/bin/bash
PORT=20201
TIMEOUT=10
#the timeout must be applied by the action itself since it will spawn other processes as well
ACTION="bash ./spawn_tcpreplay_times_with_timeout_of.sh 2 $TIMEOUT"

nc -lvp 20201
sudo $ACTION
