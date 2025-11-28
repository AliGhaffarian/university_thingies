# Overview
This project is a small eBPF-based syscall tracer that:

- Attaches to `tp/raw_syscalls/sys_enter` (tracepoint for syscall entry).
- Optionally recognizes `execve`/`execveat` events to mark processes of interest.
- For relevant processes, captures syscall IDs and the process identifier (and process comm) and pushes events to a **ring buffer** map.
- A userspace loader consumes the ring buffer and writes lines in the format:

  ```
  <pid>:<syscall_id>:<pathname>
  ```
- `formatter.py` converts that `trace.log` into per-(pathname, pid) files where each file contains the space-separated syscall IDs observed for that (pathname, pid).
This README documents how to build/run the project, explains internals (maps, BPF program flow, userspace loader), shows data-path diagrams, lists known issues in the provided sources, and suggests improvements.

# Quick start
```bash
# Build

# (project root containing Makefile)
make
# This builds:
#  - tracer.bpf.o           (clang -target bpf)
#  - tracer.skel.h          (bpftool gen skel)
#  - loader_and_logger      (gcc linking libbpf)

# Run

# Trace a particular program by baseline name:
sudo ./loader_and_logger /bin/bash

# Trace *all* programs (special behavior in loader:
# pass '*' as argv[1]):
sudo ./loader_and_logger '*'
```

Recorded output is written to `trace.log` by default (see loader source).

To convert `trace.log` into per-(pathname,pid) files:

```bash
python3 formatter.py trace.log
# Results: files named <pathname>:<pid>.log containing space-separated syscall IDs
```

# Files — short description
- `tracer.bpf.c` — eBPF program. Attaches to `tp/raw_syscalls/sys_enter`. Maintains maps and submits events to ring buffer.
- `loader_and_logger.c` — userspace loader + ring buffer consumer. Loads BPF object (via `tracer.skel.h`), attaches, polls ring buffer and writes `PID:syscall:comm` lines to stdout and `trace.log`. Also writes program name into `progs` BPF map to indicate which processes to trace.
- `shared.h` — `struct submit_info` and constants used by both kernel and userspace.
- `formatter.py` — simple script that parses `trace.log` and splits it into files by (pathname, pid).
- `Makefile` — build rules

# Internals — detailed explanation
This section explains the components and how they interact.

## Key data structures
From `shared.h`:

```c
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
```

- `STRING_LEN` = 20 — used widely, **limited length** for program name/path storage.
- `MAX_TRACKED_PROCESSES` = 2048 — maximum number of program names kept in the `progs` array map.

## BPF maps (in `tracer.bpf.c`)
1. `progs` — `BPF_MAP_TYPE_ARRAY`

   - `key`: `uint32_t` index (0..MAX_TRACKED_PROCESSES-1)
   - `value`: `char[STRING_LEN]` — stores a program basename (e.g., `bash`, `sshd`, `myprog`)
   - Used as the canonical whitelist of program basenames to trace.

2. `pid_relevancy_cache` — `BPF_MAP_TYPE_HASH`

   - `key`: `uint32_t` pid
   - `value`: `int` (index in `progs` array, or `-1` meaning "irrelevant")
   - Cached on first `execve` of a process; allows per-syscall fast lookup.

3. `ring_buff` — `BPF_MAP_TYPE_RINGBUF`

   - Ring buffer that carries `struct submit_info` to userspace.

## BPF program logic (high level)

The BPF program attaches to `tp/raw_syscalls/sys_enter` via:

```c
SEC("tp/raw_syscalls/sys_enter")
int proccess_sys_enter(struct parsed_ctx *c)
```

`parsed_ctx` contains minimal parsed tracepoint data: an `id` for the syscall and six `args`.

Algorithm:
1. If the syscall is `execve`or `execveat`, check for relevancy of the process, if `do_trace_all` is set, all processes are considered relevant.
2. For non-`execve` syscalls:
   - Checks `pid_relevancy_cache` for current PID via `is_current_process_relevant()`. If value is `-1` => return (ignore syscall).
   - If relevant, submit the syscall info

## Post-processing (`formatter.py`)

- Reads lines of the form `pid:syscall_id:pathname`.
- Splits by `:`.
- Groups values by `(pathname, pid)`.
- Writes files named `<pathname>:<pid>.log` with space-separated syscall IDs seen for that pair.

This script is minimal and expects the exact format produced by loader.

# Data-path diagrams

Below are two representations: a mermaid flowchart (renderable on many markdown viewers) and an ASCII diagram (max compatibility).

## ASCII diagram (universal)

```

[Process syscall] 
      │
      ▼
[Tracepoint: sys_enter]
      │
      ▼
[BPF proccess_sys_enter]
      ├─ if syscall is execve/execveat:
      │     ├─ compare basename with entries in `progs` array
      │     └─ write result into pid_relevancy_cache[pid]
      │
      └─ else (normal syscall):
            ├─ lookup pid_relevancy_cache[pid]
            ├─ if not relevant -> return
            ├─ fill submit_info (syscall_id, pid, comm in pathname field)
            └─ submit ringbuf entry
      │
      ▼
[Userspace loader ring_buffer__poll]
      ├─ call handle_event(submit_info)
      └─ fprintf "%d:%lu:%s\n"  (pid:syscall:comm)
      │
      ▼
[trace.log file]
      │
      ▼
[formatter.py] -> write files "<comm>:<pid>.log" containing space-separated syscall IDs

```

# Example run & sample output

Run (as root):

```bash
sudo ./loader_and_logger /bin/bash
# produces lines such as:
# 1234:60:bash
# 1234:1:bash
# 1234:2:bash
# 2345:1:sshd
```

After running `python3 formatter.py trace.log`, a file `bash:1234.log` will contain something like:
```
60 1 2
```

(each number is a syscall ID observed for that pid & comm).

# How to interpret logs
- File created by the tracer (`trace.log`):
	- Each log line: `PID:SYSCALL_ID:COMM`
	  - `PID` — process id
	  - `SYSCALL_ID` — syscall number as given by tracepoint
	  - `COMM` — process `comm` (task name)
- Files created by the formatter (`<COMM>:<PID>.log`):
  - space-separated syscall IDs observed for that PID/COMM during the program run.

