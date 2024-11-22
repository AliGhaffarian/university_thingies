import os
from re import sub
import sys
import time
import subprocess

interface=sys.argv[1]
timeout = sys.argv[2]
write_file = sys.argv[3]

sniff_script=f"\
sudo timeout {timeout} sudo tcpdump -i {interface} 'tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0' -w {write_file}\
"
os.system(sniff_script)
OUT_DIR="recv_syn_logs"
OUT_FILE=subprocess.check_output(["date"]).decode()

from scapy.all import *

def count_syn_reqs(pcap_file):
    res = 0
    for packet in pcap_file:
        if TCP in packet\
                and packet[TCP].flags == "S":
                    res += 1
    return res

pcap = rdpcap(write_file)
out = str(count_syn_reqs(pcap)) + f" over {timeout}"
print(out)
open(f"{OUT_DIR}/{OUT_FILE}", "w").write(out)


