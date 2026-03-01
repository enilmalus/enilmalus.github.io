---
title: HTB-Json Writeup
date: 2026-03-01T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Windows
  - Writeup
  - HTB
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.227.191 -oA port
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-01 01:13 EST
Nmap scan report for 10.129.227.191
Host is up (0.10s latency).
Not shown: 65521 closed tcp ports (reset)
PORT      STATE SERVICE
21/tcp    open  ftp
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5985/tcp  open  wsman
47001/tcp open  winrm
49152/tcp open  unknown
49153/tcp open  unknown
49154/tcp open  unknown
49155/tcp open  unknown
49156/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 11.14 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ grep open port.nmap | awk -F '/' '{print $1}' | paste -sd ','
21,80,135,139,445,5985,47001,49152,49153,49154,49155,49156,49157,49158
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p21,80,135,139,445,5985,47001,49152,49153,49154,49155,49156,49157,49158 10.129.227.191                      

[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-01 01:17 EST
Nmap scan report for 10.129.227.191
Host is up (0.097s latency).

PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          FileZilla ftpd 0.9.60 beta
| ftp-syst: 
|_  SYST: UNIX emulated by FileZilla
80/tcp    open  http         Microsoft IIS httpd 8.5
|_http-server-header: Microsoft-IIS/8.5
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Json HTB
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
49158/tcp open  msrpc        Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Microsoft Windows 2012
OS CPE: cpe:/o:microsoft:windows_server_2012:r2
OS details: Microsoft Windows Server 2012 or 2012 R2
Network Distance: 2 hops
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:0:2: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: JSON, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:b9:8d:d4 (VMware)
| smb-security-mode: 
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-03-01T06:18:26
|_  start_date: 2026-03-01T06:05:01

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 69.77 seconds
```

### Nmap 漏洞脚本扫描



对 `hosts` 文件添加域解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo sed -i '1i 10.129.227.191 json.htb' /etc/hosts 
                           
┌──(kali㉿kali)-[~/Work/Kali]
└─$ head -n 1 /etc/hosts
10.129.227.191 json.htb
```

## 21-ftp 渗透

Nmap 扫描出开放了 21/ftp 端口，尝试匿名登入。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ftp json.htb
Trying 10.129.227.191:21 ...
Connected to json.htb.
220-FileZilla Server 0.9.60 beta
220-written by Tim Kosse (tim.kosse@filezilla-project.org)
220 Please visit https://filezilla-project.org/
Name (json.htb:kali): anonymous
331 Password required for anonymous
Password: 
530 Login or password incorrect!
ftp: Login failed
ftp> ls
530 Please log in with USER and PASS first.
530 Please log in with USER and PASS first.
ftp: Can't bind for data connection: Address already in use
```

无法匿名登入，ftp 使用的是 `FileZilla`，搜索一下有没有公开的漏洞利用。

```bash
──(kali㉿kali)-[~/Work/Kali]
└─$ searchsploit FileZilla 0.9                         
-------------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                          |  Path
-------------------------------------------------------------------------------------------------------- ---------------------------------
FileZilla FTP Server 0.9.20b/0.9.21 - 'STOR' Denial of Service                                          | windows/dos/2901.php
FileZilla FTP Server 0.9.21 - 'LIST/NLST' Denial of Service                                             | windows/dos/2914.php
FileZilla Server Terminal 0.9.4d - Buffer Overflow (PoC)                                                | windows/dos/1336.cpp
-------------------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
Papers: No Results
```

都是 Dos 漏洞，无法利用。

## 445-Smb 渗透

使用 `smbmap` 匿名枚举失败

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ smbmap -H json.htb         

    ________  ___      ___  _______   ___      ___       __         _______
   /"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
  (:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
   \___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
    __/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
   /" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
  (_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
-----------------------------------------------------------------------------
SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
                     https://github.com/ShawnDEvans/smbmap

[*] Detected 1 hosts serving SMB                                                                                                  
[*] Established 1 SMB connections(s) and 0 authenticated session(s)                                                      
[!] Something weird happened on (10.129.227.191) Error occurs while reading from remote(104) on line 1015                    
[*] Closed 1 connections
```