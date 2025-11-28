#ifndef SUBMIT_INFO
#define SUBMIT_INFO

#include <stdint.h>

#define STRING_LEN 20
#define MAX_TRACKED_PROCESSES 2048

struct submit_info {
    int prog_index;
    long syscall_id;
    uint32_t pid;
    uint64_t timestamp_nanoseconds;
    unsigned long args[6];
    char pathname[STRING_LEN];
};

#endif // !SUBMIT_INFO
