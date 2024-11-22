#!/bin/bash
PORT=20201
ACTION_TIMEOUT=240
ACTION="bash ./check_and_log_avail_time.sh"

nc -lvp 20201
timeout -vs INT $ACTION_TIMEOUT $ACTION
