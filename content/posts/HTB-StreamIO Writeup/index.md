---
title: HTB-StreamIO Writeup
date: 2026-03-19T13:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
---

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]                                                                                                                                  
└─$ sudo nmap --min-rate 10000 -p- 10.129.6.162 -oA ports                                                                                                               
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-19 02:35 EDT                                                                                                         
Nmap scan report for 10.129.6.162                                                                                                                                       
Host is up (0.17s latency).                                                                                                                                             
Not shown: 65515 filtered tcp ports (no-response)                                                                                                                       
PORT      STATE SERVICE                                                                                                                                                 
53/tcp    open  domain                                                                                                                                                  
80/tcp    open  http                                                                                                                                                    
88/tcp    open  kerberos-sec                                                                                                                                            
135/tcp   open  msrpc                                                                                                                                                   
139/tcp   open  netbios-ssn                                                                                                                                             
389/tcp   open  ldap                                                                                                                                                    
443/tcp   open  https
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49677/tcp open  unknown
49678/tcp open  unknown
49704/tcp open  unknown
49731/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 13.75 seconds

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ post=$(grep open ports.nmap | awk -F '/' '{print $1}' | paste -sd ',')
                                                                                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ echo $post 
53,80,88,135,139,389,443,445,464,593,636,3268,3269,5985,9389,49667,49677,49678,49704,49731
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo nmap --script=http-brute -p 53,80,88,135,139,389,443,445,464,593,636,3268,3269,5985,9389,49667,49677,49678,49704,49731 10.129.6.162 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-19 02:44 EDT
Nmap scan report for 10.129.6.162
Host is up (0.16s latency).

PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
| http-brute:   
|_  Path "/" does not require authentication
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
443/tcp   open  https
| http-brute:   
|_  Path "/" does not require authentication
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49677/tcp open  unknown
49678/tcp open  unknown
49704/tcp open  unknown
49731/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 1.47 seconds

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo nmap -sT -sC -sV -O -p 53,80,88,135,139,389,443,445,464,593,636,3268,3269,5985,9389,49667,49677,49678,49704,49731 10.129.6.162
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-19 02:43 EDT
Stats: 0:00:08 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 20.00% done; ETC: 02:44 (0:00:24 remaining)
Nmap scan report for 10.129.6.162
Host is up (0.16s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-03-19 13:43:42Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: streamIO.htb0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http      Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| tls-alpn: 
|_  http/1.1
|_http-server-header: Microsoft-HTTPAPI/2.0
| ssl-cert: Subject: commonName=streamIO/countryName=EU
| Subject Alternative Name: DNS:streamIO.htb, DNS:watch.streamIO.htb
| Not valid before: 2022-02-22T07:03:28
|_Not valid after:  2022-03-24T07:03:28
|_http-title: Not Found
|_ssl-date: 2026-03-19T13:45:20+00:00; +7h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: streamIO.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49678/tcp open  msrpc         Microsoft Windows RPC
49704/tcp open  msrpc         Microsoft Windows RPC
49731/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-03-19T13:44:39
|_  start_date: N/A
|_clock-skew: mean: 6h59m59s, deviation: 0s, median: 6h59m58s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 108.90 seconds

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo vim /etc/hosts                                  
                                                                                                 
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ tail -n 1 /etc/hosts
10.129.6.162 watch.streamIO.htb streamIO.htb
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ smbmap -H streamIO.htb -u enil

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
[!] Something weird happened on (10.129.6.162) Error occurs while reading from remote(104) on line 1015                      
[*] Closed 1 connections
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ smbclient -L //10.129.6.162 -N
session setup failed: NT_STATUS_ACCESS_DENIED
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ crackmapexec smb 10.129.6.162
SMB         10.129.6.162    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:streamIO.htb) (signing:True) (SMBv1:False)

```

![](Pasted%20image%2020260319152602.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo gobuster dir -u http://streamio.htb/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt                                                                        
[sudo] password for kali: 
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://streamio.htb/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/*checkout*           (Status: 400) [Size: 3420]
Progress: 7831 / 207644 (3.77%)^C
[!] Keyboard interrupt detected, terminating.
Progress: 7831 / 207644 (3.77%)
===============================================================
Finished
===============================================================
```


![](Pasted%20image%2020260319153008.png)

![](Pasted%20image%2020260319154053.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]                                                                                                                                                            
└─$ sudo feroxbuster -u https://streamio.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -k                                                                                                   
                                                                                                                                                                                                   
 ___  ___  __   __     __      __         __   ___                                                                                                                                                                
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__                                                                                                                                                                 
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___                                                                                                                                                
by Ben "epi" Risher 🤓                 ver: 2.11.0                                                                                                                                                                
───────────────────────────┬──────────────────────                                                                           
 🎯  Target Url            │ https://streamio.htb                                                                            
 🚀  Threads               │ 50                                                                                                                                                   
 📖  Wordlist              │ /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt                                                                                           
 👌  Status Codes          │ All Status Codes!                                                                               
 💥  Timeout (secs)        │ 7                                                                                                                                                                    
 🦡  User-Agent            │ feroxbuster/2.11.0                                                                                                                                                                   
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml                                                               
 🔎  Extract Links         │ true                                                                                            
 🏁  HTTP methods          │ [GET]                                                                                            
 🔓  Insecure              │ true                                                                                             
 🔃  Recursion Depth       │ 4                                                                                               
───────────────────────────┴──────────────────────                                                                                         
 🏁  Press [ENTER] to use the Scan Management Menu™                                                                           
──────────────────────────────────────────────────                                                                                                                                
404      GET       29l       95w     1245c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter                                           
301      GET        2l       10w      151c https://streamio.htb/images => https://streamio.htb/images/                        
200      GET      231l      571w     7825c https://streamio.htb/about.php                                                                                     
200      GET       51l      213w    19329c https://streamio.htb/images/client.jpg                                                          
200      GET      863l     1698w    16966c https://streamio.htb/css/style.css                                                               
200      GET      206l      430w     6434c https://streamio.htb/contact.php                                                                                 
200      GET      192l     1006w    82931c https://streamio.htb/images/icon.png                                                                             
200      GET        5l      374w    21257c https://streamio.htb/js/popper.min.js                                                                            
200      GET      913l     5479w   420833c https://streamio.htb/images/about-img.png                                                                        
200      GET      101l      173w     1663c https://streamio.htb/css/responsive.css                                                                          
200      GET      111l      269w     4145c https://streamio.htb/login.php                                                                                                         
200      GET      395l      915w    13497c https://streamio.htb/index.php                                                                                                                                         
200      GET        2l     1276w    88145c https://streamio.htb/js/jquery-3.4.1.min.js                                       
200      GET      367l     1995w   166220c https://streamio.htb/images/contact-img.png                                       
200      GET      395l      915w    13497c https://streamio.htb/                                                             
301      GET        2l       10w      151c https://streamio.htb/Images => https://streamio.htb/Images/                       
301      GET        2l       10w      150c https://streamio.htb/admin => https://streamio.htb/admin/                          
403      GET       29l       92w     1233c https://streamio.htb/js/                                                           
403      GET       29l       92w     1233c https://streamio.htb/css/                                                                                                                                                                                         
301      GET        2l       10w      157c https://streamio.htb/admin/images => https://streamio.htb/admin/images/            
301      GET        2l       10w      148c https://streamio.htb/css => https://streamio.htb/css/                              
301      GET        2l       10w      157c https://streamio.htb/admin/Images => https://streamio.htb/admin/Images/                                                                                                                                           
301      GET        2l       10w      147c https://streamio.htb/js => https://streamio.htb/js/                                             
301      GET        2l       10w      154c https://streamio.htb/admin/css => https://streamio.htb/admin/css/                                
301      GET        2l       10w      153c https://streamio.htb/admin/js => https://streamio.htb/admin/js/                                 
301      GET        2l       10w      150c https://streamio.htb/fonts => https://streamio.htb/fonts/                                                        
301      GET        2l       10w      156c https://streamio.htb/admin/fonts => https://streamio.htb/admin/fonts/                                            
301      GET        2l       10w      151c https://streamio.htb/IMAGES => https://streamio.htb/IMAGES/                                                      
404      GET       40l      156w     1885c https://streamio.htb/%20                                                                                         
404      GET       40l      156w     1892c https://streamio.htb/images/%20                                                                                  
404      GET       40l      156w     1888c https://streamio.htb/js/%20                                                                                      
404      GET       40l      156w     1889c https://streamio.htb/css/%20                                                                                     
404      GET       40l      156w     1892c https://streamio.htb/Images/%20                                                                                  
301      GET        2l       10w      157c https://streamio.htb/admin/IMAGES => https://streamio.htb/admin/IMAGES/                                          
404      GET       40l      156w     1891c https://streamio.htb/admin/%20                                                                                   
[>-------------------] - 74s    41222/3087697 2h      found:34      errors:0                                                                                  
🚨 Caught ctrl+c 🚨 saving scan state to ferox-https_streamio_htb-1773905978.state ...                                                                                            
[>-------------------] - 74s    41241/3087697 2h      found:34      errors:0                                                                                                      
[>-------------------] - 74s     4317/220546  58/s    https://streamio.htb/                                                                                                       
[>-------------------] - 73s     4155/220546  57/s    https://streamio.htb/images/                                                                                                  
[>-------------------] - 73s     4099/220546  56/s    https://streamio.htb/css/                                                                                                   
[>-------------------] - 73s     4099/220546  57/s    https://streamio.htb/js/                                                                                                    
[>-------------------] - 72s     4000/220546  56/s    https://streamio.htb/Images/                                                                                                
[>-------------------] - 71s     3900/220546  55/s    https://streamio.htb/admin/                                                                                                 
[>-------------------] - 70s     3751/220546  53/s    https://streamio.htb/admin/images/                                                                                          
[>-------------------] - 68s     3595/220546  53/s    https://streamio.htb/admin/Images/                                                                                          
[>-------------------] - 64s     3249/220546  51/s    https://streamio.htb/admin/css/                                                                                             
[>-------------------] - 57s     2849/220546  50/s    https://streamio.htb/admin/js/                                                                                              
[>-------------------] - 33s     1436/220546  44/s    https://streamio.htb/fonts/                                                                                                 
[>-------------------] - 25s      999/220546  41/s    https://streamio.htb/admin/fonts/                                                                                           
[>-------------------] - 15s      550/220546  37/s    https://streamio.htb/IMAGES/                                                                                                
[>-------------------] - 5s        99/220546  20/s    https://streamio.htb/admin/IMAGES/                                                                                            
[--------------------] - 0s         0/220546  -       https://streamio.htb/about.php      
                                            

```

![](Pasted%20image%2020260319153446.png)

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