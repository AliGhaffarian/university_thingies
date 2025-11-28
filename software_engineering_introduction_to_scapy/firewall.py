#!/usr/local/bin/python


import argparse
import netfilterqueue
import subprocess

from scapy.all import *

import logging
import logging.config
import colorlog
import sys

# Define the format and log colors
log_format = '%(asctime)s [%(levelname)s] %(name)s [%(funcName)s]: %(message)s'
log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
        }

# Create the ColoredFormatter object
console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s' + log_format,
        log_colors = log_colors
        )


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(console_formatter)

logger.addHandler(stdout_handler)

def nfque_clean_up(nfque, RULE_NUM, RULE_LEN):
    # Cleanup
    nfque.unbind()
    for i in range(RULE_LEN):
        subprocess.run(['/usr/sbin/iptables', '-D', 'FORWARD', RULE_NUM])
        subprocess.run(['/usr/sbin/iptables', '-D', 'OUTPUT', RULE_NUM])
        subprocess.run(['/usr/sbin/iptables', '-D', 'INPUT', RULE_NUM])

def drop_black_listed_ip_ranges(file_name):
    ipranges = open(file_name).read().splitlines()
    rules_len = 0
    for iprange in ipranges:
        if iprange.startswith("#"):
            logger.debug(f"ignoring rule line {iprange}")
            continue
        subprocess.run(["sudo", "iptables" ,"-A", "FORWARD", "-d", iprange, "-j" "DROP"])
        subprocess.run(["sudo", "iptables" ,"-A", "OUTPUT", "-d", iprange, "-j" "DROP"])
        subprocess.run(["sudo", "iptables" ,"-A", "INPUT", "-d", iprange, "-j" "DROP"])
        rules_len += 1
    return rules_len
    
def main():
    
    RULE_LEN = 0    

    # The NFQUEUE to use, just need to be consitent between nfqueue and iptables
    QUE_NUM = 0

    # Setup iptables rules to collect traffic
    RULE_NUM = '1'
    interceptRule = ['/usr/sbin/iptables', '-t', 'filter', '-I', 'FORWARD', RULE_NUM]
    interceptRule.extend(['--protocol', 'udp'])
    interceptRule.extend(['--jump', 'NFQUEUE', '--queue-num', str(QUE_NUM)])
    subprocess.run(interceptRule)
    RULE_LEN += 1

    interceptRule = ['/usr/sbin/iptables', '-t', 'filter', '-I', 'FORWARD', RULE_NUM]
    interceptRule.extend(['--protocol', 'tcp'])
    interceptRule.extend(['--jump', 'NFQUEUE', '--queue-num', str(QUE_NUM)])
    subprocess.run(interceptRule)
    RULE_LEN += 1


    interceptRule = ['/usr/sbin/iptables', '-t', 'filter', '-I', 'OUTPUT', RULE_NUM]
    interceptRule.extend(['--protocol', 'udp'])
    interceptRule.extend(['--jump', 'NFQUEUE', '--queue-num', str(QUE_NUM)])
    subprocess.run(interceptRule)

    interceptRule = ['/usr/sbin/iptables', '-t', 'filter', '-I', 'OUTPUT', RULE_NUM]
    interceptRule.extend(['--protocol', 'tcp'])
    interceptRule.extend(['--jump', 'NFQUEUE', '--queue-num', str(QUE_NUM)])
    subprocess.run(interceptRule)

    interceptRule = ['/usr/sbin/iptables', '-t', 'filter', '-I', 'INPUT', RULE_NUM]
    interceptRule.extend(['--protocol', 'udp'])
    interceptRule.extend(['--jump', 'NFQUEUE', '--queue-num', str(QUE_NUM)])
    subprocess.run(interceptRule)

    interceptRule = ['/usr/sbin/iptables', '-t', 'filter', '-I', 'INPUT', RULE_NUM]
    interceptRule.extend(['--protocol', 'tcp'])
    interceptRule.extend(['--jump', 'NFQUEUE', '--queue-num', str(QUE_NUM)])
    subprocess.run(interceptRule)



    nfque = netfilterqueue.NetfilterQueue()
    nfque.bind(QUE_NUM, filter_packet)

    try:
        logger.info("initializing the firewall")
        nfque.run()
    except KeyboardInterrupt:
        logger.info('User interupt, exiting')
    except Exception as e:
        print(e)
        nfque_clean_up(nfque, RULE_NUM, RULE_LEN)
        exit(1)
    nfque_clean_up(nfque, RULE_NUM, RULE_LEN)
    exit(0)

def filter_packet(packet):
    global args, message

    pkt = IP(packet.get_payload())
    if TCP in pkt:
        pkt[TCP].reserved = 3
    packet.set_payload(bytes(pkt))

    if False:
        logger.debug(f"dropping {pkt}")

    logger.debug(f"accepting {pkt}")
    packet.accept()

if __name__ == "__main__":
    main()
