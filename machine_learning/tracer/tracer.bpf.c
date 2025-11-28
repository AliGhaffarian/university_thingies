
#include <linux/bpf.h>
#include <linux/types.h>
#include <stdint.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include <string.h>

#include "shared.h"

extern int bpf_strcmp(const char *s1__ign, const char *s2__ign) __ksym;
extern int bpf_strlen(const char *s__ign) __ksym;
extern int bpf_strstr(const char *s1__ign, const char *s2__ign) __ksym;

const volatile int do_trace_all = 0;

// TODO: move these configs to userspace loader later for more flexibility

#define EXECVE_ID 59
#define EXECVEAT_ID 322
#define IS_EXEC(id) (id == EXECVE_ID || id == EXECVEAT_ID)

#define PATHNAME_DELIM '/'

struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __type(key, uint32_t);
    __type(value, char[STRING_LEN]);
    __uint(max_entries, MAX_TRACKED_PROCESSES);
} progs SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, uint32_t);
    __type(value, int); //index of program name in progs map (-1 means pid is irrelevant)
    __uint(max_entries, MAX_TRACKED_PROCESSES);
} pid_relevancy_cache SEC(".maps");

struct {
	__uint(type, BPF_MAP_TYPE_RINGBUF);
	__uint(max_entries, 1024 * sizeof(struct submit_info));
} ring_buff SEC(".maps");

struct trace_entry {
    unsigned short common_type;
    unsigned char common_flags;
    unsigned char common_preempt_count;
    int common_pid;
};
struct parsed_ctx {
    struct trace_entry ent;
    long id;
    unsigned long args[6];
};

int is_current_process_relevant(){
    uint32_t current_pid = bpf_get_current_pid_tgid() & 0xffff;
    void *relevency_index_ptr = bpf_map_lookup_elem(&pid_relevancy_cache, &current_pid);
    if(! relevency_index_ptr)
        return -1;
    return *((int*)relevency_index_ptr);
}

int program_name_from_pathname(char *pathname){
    //int current_delim_pos = 0;
    int last_delim_pos = -1;

    int i;
    for(i = 0; pathname[i] && i < STRING_LEN; i++)
        if(pathname[i] == PATHNAME_DELIM)
            last_delim_pos = i;

    return last_delim_pos + 1;
}

inline int submit_this_syscall(__u32 pid, long id, uint64_t *args){
    bpf_printk("submitting %d:%d", pid, id);
    struct submit_info *submit = bpf_ringbuf_reserve(&ring_buff, 
        sizeof(struct submit_info), 
        0
        );
	if (!submit)
		return 1;

    //we only need the syscall_id
    submit->syscall_id = id;
    submit->pid = pid;

    //submit->pathname
    bpf_get_current_comm(submit->pathname, STRING_LEN);

	bpf_ringbuf_submit(submit, 0);
    return 0;
}

int process_exec(uint64_t pathname){
    int match = 0;
    uint32_t current_pid = bpf_get_current_pid_tgid() & 0xffff;
    int relevancy_index = 0;
    int map_value = -1;
    if(do_trace_all == 1){
        match = 1;
        map_value = 1;
        goto after_progname_match;
    }

    char current_prog_pathname[STRING_LEN];
    int err = bpf_core_read_user(current_prog_pathname, STRING_LEN, (char *)pathname);
    if(err){
        bpf_printk("failed to bpf_core_read the current_progname");
        return -1;
    }

    int prog_name_idx = program_name_from_pathname(current_prog_pathname);
    if(prog_name_idx < 0 || prog_name_idx >= STRING_LEN)
        return -1;

    const void *current_elem;
    for(relevancy_index = 0; relevancy_index < MAX_TRACKED_PROCESSES; relevancy_index++){
        int i = relevancy_index;
        if ((current_elem = bpf_map_lookup_elem(&progs, &i)) == NULL)
            break;
        match |= bpf_strcmp(current_prog_pathname + prog_name_idx, current_elem) ? 0 : 1;
        bpf_printk("comparing %s with %s", current_prog_pathname + prog_name_idx, current_elem);
        if(match) break;
    }

    map_value = match ? relevancy_index : -1;
after_progname_match:
    err = bpf_map_update_elem(&pid_relevancy_cache, &current_pid, &map_value, BPF_NOEXIST);
    if(err){
        bpf_printk("error adding a relevant process: %s:%d", pathname, err);
    }

    return map_value;
}

SEC("tp/raw_syscalls/sys_enter")
int proccess_sys_enter(struct parsed_ctx *c)
{
    if (IS_EXEC(c->id)){
        bpf_printk("%s", c->args[0]);
        return process_exec(c->args[0]);
    }
    int prog_index = 0;
    if ((prog_index = is_current_process_relevant()) == -1)
        return 0;
    submit_this_syscall(bpf_get_current_pid_tgid() & 0xffffffff, c->id, c->args);
    return 0;
}

char __license[] SEC("license") = "GPL";
