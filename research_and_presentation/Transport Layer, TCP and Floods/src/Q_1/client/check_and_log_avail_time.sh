#!/bin/bash
check_times=240
check_intervals=1

server_ip="127.0.0.1"
server_port=20202

log_dir=server_avail_time_logs
mkdir -p "$log_dir"
session_log_file="$log_dir/$(date | tr '[:blank:]' '_')"
touch "$session_log_file"

REDIRECT_DEST="$session_log_file"

function check_server_avail_time() {
		return $err

}

trap exit SIGINT 

err_status_file=$(mktemp)
for i in $(seq "$check_times");do
		echo "testing $i" | tee -a "$REDIRECT_DEST"

		#check if server responds, then store the connection check in $err_status_file, then echo response time to stdout and $REDIRECT_DEST
		 
		( time -p bash -c "nc -vz $server_ip $server_port; echo \$? > $err_status_file" ) 2>&1 | grep real | cut -f2 -d $'\t' | tee -a $REDIRECT_DEST
	
		if [ "$(cat $err_status_file)" = "0" ]; then
				echo success | tee -a "$REDIRECT_DEST"
		else
				echo fail | tee -a "$REDIRECT_DEST"
		fi
		sleep "$check_intervals"
done

