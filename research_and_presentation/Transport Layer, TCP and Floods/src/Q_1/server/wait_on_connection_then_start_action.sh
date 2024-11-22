#!/bin/bash
PORT=20201
ACTION_TIMEOUT=240
#this action will manage the timeout itself
ACTION="python3 syn_counter.py wlan0 $ACTION_TIMEOUT pcap_file"
ACTION2="bash server.sh"

nc -lvp 20201
$ACTION&
timeout -s INT $ACTION_TIMEOUT $ACTION2&

