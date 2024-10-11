# Solving the D1N0P13v3 CTF challenge
## The Problem   
  
The challenge involves solving `rstcon/forensics/D1N0P13v3` which provided us with a pcap file and we are asked to extract data that is encoded in the traffic using [D1N0P13](https://github.com/nblair2/D1N0P13).  
  
## Assumptions  
  
The given pcap file contains encoded data using [D1N0P13](https://github.com/nblair2/D1N0P13).  
  
## Expected Solution  
  
1. Understand the DNP3 protocol.    
2. Understand D1N0P13.  
3. Extract the encoded data.    
  
  
## Keywords to Start the Research  
  
DNP3, IEEE-1815, D1N0P13  
  
## What is D1N0P13?  
  
D1N0P13 (pronounced dino-pie) is a network storage covert channel that encodes information in legitimate DNP3 traffic.  
  
## References to Study  
  
https://github.com/nblair2/D1N0P13  
https://www.rfc-editor.org/rfc/rfc8578.txt mentions DNP 3 as an alias to `IEEE-1815`    
https://www.dnp.org/About/Overview-of-DNP3-Protocol    
https://www.dnp.org/Portals/0/AboutUs/DNP3%20Primer%20Rev%20A.pdf  
https://automationcommunity.com/dnp3-distributed-network-protocol-3/  
https://www.youtube.com/watch?v=CwMFrvins5Q  
  
## Learning More About DNP3  
  
### What is DNP3?    
  
![](https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/DNP-overview.png/600px-DNP-overview.png)    
DNP3 is a protocol for  
transmission of data from point A to point B using serial and IP   
communications. It has been used primarily by utilities such as  
the electric and water companies, but it functions well for other areas.  
  
### A High-Level Overview of DNP3  
  
Outstations collect and provide the master with:  
- **Binary input data**: Monitoring two-state devices like a circuit breaker (closed/tripped) or - pipeline pressure alarms (normal/excessive).  
- **Analog input data**: Conveying voltages, currents, power, reservoir water levels, and temperatures.  
- **Count input data**: Reporting energy (e.g., kilowatt-hours) or fluid volume.  
- **Files**: Containing configuration data.  
  
The master station issues control commands that take the form of:  
- Close or trip a circuit breaker, start or stop a motor, and open or   
		close a valve.  
- Analog output values to set a regulated pressure or a desired voltage   
		level  
  
DNP3 is **not** a general purpose protocol.  
It is intended for SCADA (Supervisory Control and Data Acquisition) applications.  
  
  
### My Summarized Understanding  
  
Some devices are output sensors or input devices that have a serial pin for I/O, such as devices that monitor a patient's heartbeat.    
These devices don't operate over TCP/IP.    
Instead, a TCP/IP-enabled device interfaces with these I/O devices, relaying information to remote TCP/IP hosts based on data received via the serial pins, or it forwards data from a remote host to the designated pin.    
These processes are managed using the DNP3 protocol.  
  
  
  
  
  
  
## D1N0P13 Source Code:  
  
```  
.
├── docker  
│   ├── docker-compose.yml  
│   └── Dockerfile  
├── README.md  
├── requirements.txt  
└── src  
    ├── D1N0P13-client.py  
    ├── D1N0P13-server.py  
    └── DNP3_Lib.py  
4 directories, 8 files  
```  
  
### DNP3_Lib.py  
  
A library that implements the dnp3 headers in scapy framework.  
  
### Client and Server  
  
These two work by intercepting the traffic based on the passed argument.  
Then they do their job accordingly based on the encoding method (iin, app-req, app-resp).  
  
#### Client  
  
Intercepts the traffic and encodes the given message in the packets using `alter_packets()`.   
  
#### Server  
  
Intercepts the traffic and extracts the message using `extract_packets()`.  
  
## Solution  
  
I used the extract_packets function from the D1N0P13 server to extract any encoded message in the pcap file.  
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
**Output**
```  
iin      
----    
app-req    
----    
app-resp    
----    
```  
no flag for us...  
  
### Why Did it Fail?  
  
After some debugging, I realized the script didn't recognize any packet to extract data.    
  
I made a wild guess and removed the whole packet filtering part of the code.  
surprisingly, it worked!  
  
### Solve Script  
  
note: printing the flag is happening inside the extract_packets()  
```python
import bitarray
import bitarray.util

from DNP3_Lib import *
from scapy.all import *
methods=['iin', 'app-req', 'app-resp']
class args:
    method=""
message=bitarray.bitarray()
pcap_file = rdpcap("./D1N0P13v3.pcap")
def extract_packets(pkt):
	global args, message
	
	# check if the packet is DNP3 and going to the right spot
	if True: #removed the packet match function
		# if packet has ApplicationIIN
		if ((args.method == "iin") and pkt.haslayer(DNP3ApplicationIIN)):
			#decode the nmessage into the two reserved fieldsS
			message += str(pkt[DNP3ApplicationIIN].RESERVED_1)
			message += str(pkt[DNP3ApplicationIIN].RESERVED_2)

		elif ((args.method == "app-resp")
				and pkt.haslayer(DNP3ApplicationResponse)
				and pkt[DNP3ApplicationResponse].FUNC_CODE
						not in [0x81, 0x82, 0x83]):
			extra = pkt[DNP3ApplicationResponset].FUNC_CODE - 0x83
			message += bitarray.util.int2ba(extra // 0x3 - 1, length=4)

		elif ((args.method == "app-req")
				and pkt.haslayer(DNP3ApplicationRequest)
				and (pkt[DNP3ApplicationRequest].FUNC_CODE >= 0x22)):
			message += bitarray.util.int2ba(
					pkt[DNP3ApplicationRequest].FUNC_CODE // 0x22 - 1,
					length=2)

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
**Output**
```  
iin    
bytearray(b'rstcon{r3s3rv3d_f13ld5?}\xfe\x00')    
----    
app-req    
----    
app-resp    
----    
```  


