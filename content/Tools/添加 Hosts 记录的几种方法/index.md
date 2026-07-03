---
title: 添加 Hosts 记录的几种方法
date: 2026-02-14T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
---
## 添加 hosts 记录

### Bash

```bash
sudo bash -c 'echo "10.129.187.74 conversor.htb" >> /etc/hosts'
```

### Sed

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo sed -i '1i 10.129.227.191 json.htb' /etc/hosts 
```

### Tee

```bash
sudo echo "10.129.227.191 json.htb" | tee -a /etc/hosts
```
