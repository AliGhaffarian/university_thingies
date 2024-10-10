so everytime i solve a ctf challenge i do all these in my mind

## the problem 
solving rstcon/forensics/d1n0p13v3
## assumptions
the given pcap file contains encoded data using [d1n0p13](https://github.com/nblair2/D1N0P13)

## expected solution
understand the dnp3 protocol
understand d1n0p13
extract the encoded data

## keywords to start the research
dnp3, IEEE-1815
## references to study DNP3
https://www.rfc-editor.org/rfc/rfc8578.txt mentions DNP 3 as an alias to `IEEE-1815`
https://www.dnp.org/About/Overview-of-DNP3-Protocol
https://www.dnp.org/Portals/0/AboutUs/DNP3%20Primer%20Rev%20A.pdf
## learning more about DNP3
### what is DNP3?
DNP3 is a protocol for
transmission of data from point A to point B using serial and IP 
communications. It has been used primarily by utilities such as
the electric and water companies, but it functions well for other areas
### a high level overview of DNP3
Outstations collect and provide the master with:
- Binary input data that is useful to monitor two-state devices. For 		
		example a circuit breaker is closed or tripped; a
		pipeline pressure alarm shows normal or excessive.
- Analog input data that conveys voltages, currents, power, reservoir 
		water levels and temperatures.
- Count input data that reports energy in kilowatt hours or fluid volume.
- Files that contain configuration data.


The master station issues control commands that take the form of:
- Close or trip a circuit breaker, start or stop a motor, and open or 
		close a valve.
- Analog output values to set a regulated pressure or a desired voltage 
		level

DNP3 is **not** a general purpose protocol
It is intended for SCADA (Supervisory Control and Data Acquisition) applications.

https://automationcommunity.com/dnp3-distributed-network-protocol-3/

question: isnt the TCP/IP stack enough for such equipment to communicate?
### my summarized understanding

some devices are output sensors or input devices that are having a serial pin for I/O like a device that shows patients heartbeat
these devices don't operate on TCP/IP
instead a TCP/IP device is connected to these I/O devices and will provide the remote TCP/IP hosts with information received on these pins or will put the data received from a remote host on the requested pin
and these are done the DNP 3 protocol


### wiki pedia
![656562dab890b61cbd99d03f546bdd95.png](:/d6856384bf9f44d98d36ad80983e9374)

https://www.youtube.com/watch?v=CwMFrvins5Q


## d1n0p13 source code:
```
.
├── docker
│   ├── docker-compose.yml
│   └── Dockerfile
├── README.md
├── requirements.txt
└── src
    ├── d1n0p13-client.py
    ├── d1n0p13-server.py
    ├── DNP3_Lib.py
    └── __pycache__
        └── DNP3_Lib.cpython-312.pyc

4 directories, 8 files
    
```

### DNP3_Lib.py
a library that implements the dnp3 headers in scapy framework

### client and server
these two work by intercepting the traffic based on the passed argument
then they do their job accordingly based on the encoding method (iin, app-req, app-resp)
#### client
intercepts the traffic and encodes the given message in the packets
alter_packet function
#### server
intercepts the traffic and extracts the message 
extract function

## solution
use the extract_packets function of d1n0p13 server to extract any encoded message in the pcap
```python
for method in methods:
	message = bitarray.bitarray()
	args.method = method
	print(args.method)
	for packet in pcap_file:
		extract_packets(packet)
	print(message.to01())
	print("----")
```
nothing...
### why did it fail?
after some debugging, i realized the script didn't recognize any packet to extract data

so i did a pretty dumb thing
i removed the whole matching the packet part of the code
it worked 
```python
#!/usr/local/bin/python


import argparse
import bitarray
import bitarray.util
import crc
import netfilterqueue
import random
import subprocess

from DNP3_Lib import *
from scapy.all import *
methods=['iin', 'app-req', 'app-resp']
host1_ip="10.0.1.10"
host1_port=44222
host2_ip="10.0.2.5"
host2_port=20000
class args:
    src =host2_ip
    dst=host1_ip
    sport=host2_ip
    dport=host1_ip
    method=""
message=bitarray.bitarray()
pcap_file = rdpcap("./d1n0p13v3.pcap")
def extract_packets(pkt):
	global args, message
	

	# check if the packet is DNP3 and going to the right spot
	if True:
		changed = False
		# if packet has ApplicationIIN
		if ((args.method == "iin") and pkt.haslayer(DNP3ApplicationIIN)):
			#decode the nmessage into the two reserved fieldsS
			message += str(pkt[DNP3ApplicationIIN].RESERVED_1)
			message += str(pkt[DNP3ApplicationIIN].RESERVED_2)


			# reset the IIN RESERVED bits to 0 to cover our tracks
			pkt[DNP3ApplicationIIN].RESERVED_1 = 0
			pkt[DNP3ApplicationIIN].RESERVED_2 = 0
			changed = True

		elif ((args.method == "app-resp")
				and pkt.haslayer(DNP3ApplicationResponse)
				and pkt[DNP3ApplicationResponse].FUNC_CODE
						not in [0x81, 0x82, 0x83]):
			extra = pkt[DNP3ApplicationResponset].FUNC_CODE - 0x83
			message += bitarray.util.int2ba(extra // 0x3 - 1, length=4)
			pkt[DNP3ApplicationRequest].FUNC_CODE = 0x81 + (extra % 0x3)
			changed = True

		elif ((args.method == "app-req")
				and pkt.haslayer(DNP3ApplicationRequest)
				and (pkt[DNP3ApplicationRequest].FUNC_CODE >= 0x22)):
			message += bitarray.util.int2ba(
					pkt[DNP3ApplicationRequest].FUNC_CODE // 0x22 - 1,
					length=2)
			pkt[DNP3ApplicationRequest].FUNC_CODE = \
					pkt[DNP3ApplicationRequest].FUNC_CODE % 0x22
			changed = True

		if changed:
			# and update the CRC
			crc = update_data_chunk_crc(bytes(pkt[DNP3Transport]))
			pkt[Raw].load = pkt[Raw].load[:-2] + crc[-2:]

			# and delete other checksums so scapy will calculate
			del pkt[IP].chksum
			del pkt[TCP].chksum


	# check if we have reached the end of the stream
	if ((len(message) > 0)
			and (len(message) % 8 == 0)
			and (message[-8:] == bitarray.bitarray('00000000'))):
		print(bytearray(message))

		raise NameError("EndOfStream")


for method in methods:
	message = bitarray.bitarray()
	args.method = method
	print(args.method)
	for packet in pcap_file:
		try:
			extract_packets(packet)
		except:
			break
	print("----")
```

>iin
bytearray(b'rstcon{r3s3rv3d_f13ld5?}\xfe\x00')
\----
app-req
\----
app-resp
----

i could have solved this challenge without ever knowing what dnp3 does however, but it would defeat the whole purpose me doing ctf challenges: learning 
