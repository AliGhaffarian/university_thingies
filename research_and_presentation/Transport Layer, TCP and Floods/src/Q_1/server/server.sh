function die(){
		echo $0 died
		exit
}
trap die SIGINT

while true;do
		nc -lvp 20202
done

