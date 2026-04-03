---
title: SMB、共享目录相关
date: 2026-02-23T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## Mount

检查共享目录

```bash
showmount -e 10.10.10.13
```

连接共享目录

```bash
sudo mount -t nfs 10.10.10.13:/home/karl attact
```

## Smbclient

Smbclient 是类似 FTP 的客户端，用于访问服务器上的 SMB/CIFS 资源。

- 列出 SMB 共享

```bash
sudo smbclient -N -L \\\\10.10.10.10
```

- 连接到 SMB 共享

```bash
sudo smbclient \\\\10.10.10.10\\enil
```

## Smbmap

SMBMap 的核心功能如下：

1. 枚举共享目录，列出目标机器上所有的 SMB 共享，以及当前用户的读写权限
2. 匿名/凭据访问
3. 递归目录
4. 文件上传/下载
5. 执行命令（需要 sudo 权限）

- 枚举网站

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ smbmap -H json.htb         

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
[!] Something weird happened on (10.129.227.191) Error occurs while reading from remote(104) on line 1015                    
[*] Closed 1 connections
```

####  NXC

使用 nxc 进行 SMB 共享枚举，尝试使用空密码进行匿名登入。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ nxc smb driver.htb --shares -u enil -p ''
SMB         10.129.5.91     445    DRIVER           [*] Windows 10 Build 10240 x64 (name:DRIVER) (domain:DRIVER) (signing:False) (SMBv1:True) 
SMB         10.129.5.91     445    DRIVER           [-] DRIVER\enil: STATUS_LOGON_FAILURE
```

## Crackmapexec

CME 是一种后渗透测试工具，自动化评估大型 AD 网络的安全性。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ crackmapexec smb 10.129.6.162
SMB         10.129.6.162    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:streamIO.htb) (signing:True) (SMBv1:False)
```

批量登入尝试。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ crackmapexec smb streamio.htb -u user -p pass --no-bruteforce --continue-on-success
SMB         watch.streamIO.htb 445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:streamIO.htb) (signing:True) (SMBv1:False)
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:highschoolmusical STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:physics69i STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:paddpadd STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:66boysandgirls.. STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:%$clara STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:$monique$1991$ STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:$hadoW STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:$3xybitch STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:##123a8j8w5123## STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:!5psycho8! STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:!?Love?!123 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\user:!!sabrina$ STATUS_LOGON_FAILURE 
```

## Enum4linux

使用 `enum4linux` 进行进一步的枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ enum4linux-ng -A json.htb
ENUM4LINUX - next generation (v1.3.7)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... json.htb
[*] Username ......... ''
[*] Random Username .. 'cfxfhmar'
[*] Password ......... ''
[*] Timeout .......... 5 second(s)

 =================================
|    Listener Scan on json.htb    |
 =================================
[*] Checking LDAP
[-] Could not connect to LDAP on 389/tcp: connection refused
[*] Checking LDAPS
[-] Could not connect to LDAPS on 636/tcp: connection refused
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp

 =======================================================
|    NetBIOS Names and Workgroup/Domain for json.htb    |
 =======================================================
[+] Got domain/workgroup name: WORKGROUP
[+] Full NetBIOS names information:
- WORKGROUP       <00> - <GROUP> B <ACTIVE>  Domain/Workgroup Name
- JSON            <00> -         B <ACTIVE>  Workstation Service
- JSON            <20> -         B <ACTIVE>  File Server Service
- MAC Address = 00-50-56-B9-D4-5B

 =====================================
|    SMB Dialect Check on json.htb    |
 =====================================
[*] Trying on 445/tcp
[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: true
  SMB 2.0.2: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: false
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: false

 =======================================================
|    Domain Information via SMB session for json.htb    |
 =======================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: JSON
NetBIOS domain name: ''
DNS domain: json
FQDN: json
Derived membership: workgroup member
Derived domain: unknown

 =====================================
|    RPC Session Check on json.htb    |
 =====================================
[*] Check for anonymous access (null session)
[-] Could not establish null session: STATUS_ACCESS_DENIED
[*] Check for guest access
[-] Could not establish guest session: STATUS_LOGON_FAILURE
[-] Sessions failed, neither null nor user sessions were possible

 ===========================================
|    OS Information via RPC for json.htb    |
 ===========================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[-] Skipping 'srvinfo' run, not possible with provided credentials
[+] After merging OS information we have the following result:
OS: Windows Server 2012 R2 Datacenter 9600
OS version: '6.3'
OS release: ''
OS build: '9600'
Native OS: Windows Server 2012 R2 Datacenter 9600
Native LAN manager: Windows Server 2012 R2 Datacenter 6.3
Platform id: null
Server type: null
Server type string: null

[!] Aborting remainder of tests since sessions failed, rerun with valid credentials

Completed after 11.72 seconds
```

`json.htb` 属于 `WORKGROUP` 工作组，`NetBIOS` 的名称为 `JSON`，在 445/tcp 和 139/tcp 端口上分别开启了 SMB 和 NetBIOS 服务，主机支持多种 SMB 协议，首选协议为 SMB 3.0，未禁用 SMB 1.0，可能可以利用旧版 SMB 漏洞，确认目标操作系统为 `Windows Server 2012 R2 Datacenter`。

在连接 LDAP 和 LDAPS 端口时，389/tcp、636/tcp 端口均拒绝服务，这表明这些服务未开启或被防火墙阻止，Nmap 也没法发现开放。在尝试通过会话或随即用户进行访问 RPC 连接时，均因为权限不足而失败，目标主机对未认证用户的访问控制较为严格。