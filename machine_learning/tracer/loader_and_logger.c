#include <stdlib.h>
#include <stdio.h>
#include <bpf/libbpf.h>
#include "tracer.skel.h"
#include "shared.h"

uint poll_timeout = 100;
char outfile_name[512] = "trace.log";
FILE *outfile = NULL;
#define log_event(file, submit) fprintf(file, "%d:%lu:%s\n", submit->pid, submit->syscall_id, submit->pathname);

int handle_event(void *ctx, void *data, size_t data_sz){
	struct submit_info *submit = data;
    log_event(stdout, submit);
	log_event(outfile, submit);
	return 0;
}

int do_exit = 0;
void sig_handler(int sig){
	do_exit = 1;
}


int main(int argc, char **argv){
	struct ring_buffer *rb = NULL;
	struct tracer_bpf *skel;
	int err;
    char program_name[STRING_LEN];

    if(argc < 2 || strlen(argv[1]) > STRING_LEN){
        printf("usage: %s <PROGRAM_TO_TRACE>\n", argv[0]);
        exit(1);
    }

	skel = tracer_bpf__open();
	if(!skel){
		printf("failed to tracer_bpf__open()\n");
		exit(1);
	}

    if(argv[1][0] == '*'){
        printf("tracing all programs\n");
        skel->rodata->do_trace_all = 1;
    }

	err = tracer_bpf__load(skel);
	if(err){
		printf("failed to tracer_bpf__load()\n");
		exit(1);
	}

	err = tracer_bpf__attach(skel);
	if(err){
		printf("failed to tracer_bpf__attach\n");
		goto cleanup;
	}
	
	outfile = fopen(outfile_name, "w");
	if(!outfile){
		printf("failed to open outfile\n");
		goto cleanup_rb;
	}
    setvbuf(outfile, NULL, _IOLBF, 0);

	rb = ring_buffer__new(
			bpf_map__fd(skel->maps.ring_buff), 
			handle_event, 
			NULL, 
			NULL
			);

	if(!rb){
		printf("failed to make ringbuffer\n");
		goto cleanup_rb;
	}

    int idx = 0;
    err = 0;
    memcpy(program_name, argv[1], strlen(argv[1]));

    err = bpf_map__update_elem(
        skel->maps.progs,
        &idx,
        sizeof(idx),
        program_name,
        STRING_LEN,
        BPF_ANY
    );
    if(err)
        printf("err updateing map: %s\n", strerror(errno));


    printf("bpf program is attached\n");
    while(!do_exit){
        err = ring_buffer__poll(rb, poll_timeout);
        if(err == -EINTR)
            break;
        if(err < 0){
            printf("error polling\n");
            break;
        }
    }

    fclose(outfile);
cleanup_rb:
	ring_buffer__free(rb);
cleanup:
	tracer_bpf__destroy(skel);
}
