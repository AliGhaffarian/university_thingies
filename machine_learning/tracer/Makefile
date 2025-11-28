all: loader_and_logger 

clean:
	rm -rf *.o \
		*.skel.h \
		loader_and_logger \
		vmlinux.h \
		*.log


tracer.bpf.o: tracer.bpf.c
	clang -Wall -Os -g -target bpf -c tracer.bpf.c
tracer.skel.h: tracer.bpf.o
	bpftool gen skel tracer.bpf.o > tracer.skel.h
loader_and_logger: loader_and_logger.c tracer.skel.h
	gcc -g loader_and_logger.c -lbpf -o loader_and_logger
