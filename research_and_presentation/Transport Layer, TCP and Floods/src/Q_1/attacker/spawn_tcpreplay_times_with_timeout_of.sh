mkdir tcp_replay_logs &>/dev/null

current_log_file=$(echo "tcp_replay_logs/$(date)" | tr ' ' _)
mkdir $current_log_file
for i in $(seq $1); do
		timeout -s INT $2 tcpreplay -K -l 99999999 --intf1=wlan0 --mbps=100 syn_flood_packets &>"$current_log_file/log$i"&
done

sleep $2

rate=$(cat $current_log_file/* | grep pps | cut -d , -f3 | cut -d ' ' -f 2 | tr '\n' , | python3 -c "s=input().strip().split(',')[0:-1]; s=list(map(float,s));print(sum(s))")

echo rate was $rate

