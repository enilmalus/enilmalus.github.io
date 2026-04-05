---
title: BloodHound
date: 2026-04-01T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## 信息收集

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ bloodhound-python -c All -u jdgodd -p 'JDg0dd1s@d0p3cr3@t0r' -ns 10.129.12.116 -d streamio.htb -dc streamio.htb --zip                                                                        
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: streamio.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: streamio.htb
INFO: Testing resolved hostname connectivity dead:beef::1a9
INFO: Trying LDAP connection to dead:beef::1a9
INFO: Testing resolved hostname connectivity dead:beef::88b9:720e:3fbe:abf7
INFO: Trying LDAP connection to dead:beef::88b9:720e:3fbe:abf7
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: streamio.htb
INFO: Testing resolved hostname connectivity dead:beef::1a9
INFO: Trying LDAP connection to dead:beef::1a9
INFO: Testing resolved hostname connectivity dead:beef::88b9:720e:3fbe:abf7
INFO: Trying LDAP connection to dead:beef::88b9:720e:3fbe:abf7
INFO: Found 8 users
INFO: Found 54 groups
INFO: Found 4 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC.streamIO.htb
INFO: Done in 00M 31S
INFO: Compressing output into 20260401025555_bloodhound.zip
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ ls -liah 20260401025555_bloodhound.zip 
2784945 -rw-rw-r-- 1 kali kali 141K Apr  1 02:56 20260401025555_bloodhound.zip
                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ unzip -l 20260401025555_bloodhound.zip 
Archive:  20260401025555_bloodhound.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    82882  2026-04-01 02:56   20260401025555_groups.json
     7863  2026-04-01 02:56   20260401025555_gpos.json
     1986  2026-04-01 02:56   20260401025555_ous.json
    18581  2026-04-01 02:56   20260401025555_users.json
     4106  2026-04-01 02:56   20260401025555_computers.json
     3100  2026-04-01 02:56   20260401025555_domains.json
    24816  2026-04-01 02:56   20260401025555_containers.json
---------                     -------
   143334                     7 files

```

## 分析

初始化 `neo4j`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/StreamIO]
└─$ sudo neo4j restart
[sudo] password for kali: 
Neo4j is not running.
Directories in use:
home:         /usr/share/neo4j
config:       /usr/share/neo4j/conf
logs:         /etc/neo4j/logs
plugins:      /usr/share/neo4j/plugins
import:       /usr/share/neo4j/import
data:         /etc/neo4j/data
certificates: /usr/share/neo4j/certificates
licenses:     /usr/share/neo4j/licenses
run:          /var/lib/neo4j/run
Starting Neo4j.
Started neo4j (pid:7154). It is available at http://localhost:7474
There may be a short delay until the server is ready.

```

![](Pasted%20image%2020260401150040.png)

初始账号密码为 `neo4j`，登入后重新设置密码。

启动 `bloodhound`，账号密码均为 `admin`。

![](Pasted%20image%2020260401150835.png)

导入刚刚采集到的数据。

![](Pasted%20image%2020260401150946.png)

搜索 `STREAMIO.HTB`，有数据返回，已经成功导入。

![](Pasted%20image%2020260401151413.png)

使用 `Add to Owned` 添加用户。

![](Pasted%20image%2020260401153356.png)

![](Pasted%20image%2020260401153950.png)

将 `DC` 设置为 `ending node`。

![](Pasted%20image%2020260401154408.png)