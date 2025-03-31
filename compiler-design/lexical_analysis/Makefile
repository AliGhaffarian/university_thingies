CC = gcc
CFLAGS =

all: main
debug: CFLAGS += "-DLEXICAL_ANALYSIS_DEBUG=1 -g"
debug: CFLAGS += "-DTOKEN_T_DEBUG=1"
debug: clean all

main: main.c $(wildcard lexical_analysis.*) $(wildcard token_t.*)
	$(CC) $(CFLAGS) main.c lexical_analysis.c token_t.c -o main

clean:
	rm -f main
