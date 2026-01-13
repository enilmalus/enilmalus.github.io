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
- 