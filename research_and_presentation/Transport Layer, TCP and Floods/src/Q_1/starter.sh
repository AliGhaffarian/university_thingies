dev1_ip="192.168.150.143"
dev2_ip="192.168.150.125"
dev3_ip="192.168.150.161"
dst_port=20201

nc -vz $dev1_ip $dst_port
nc -zv $dev2_ip $dst_port
nc -zv $dev3_ip $dst_port
