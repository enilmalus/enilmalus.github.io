---
title: 爆破相关
date: 2026-02-11T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## 目录爆破

### Dirb

```bash
sudo dirb https://10.10.10.10
```

### Gobuster

- 常规爆破

```bash
sudo gobuster dir -u http://api.mentorquotes.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,php.bak,jsp,zip,tar,html,txt,tar,tar.gz,git,js,md
```

- POST 爆破

```bash
sudo gobuster dir -u http://driver.htb -U admin -P admin -x php -w /usr/share/wordlists/dirb/common.txt
```

### Feroxbuster

```bash
sudo feroxbuster -u http://driver.htb -x php -H "Authorization: Basic YWRtaW46YWRtaW4=" 
```

### Ffuf

```bash
sudo ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://10.129.230.159:3000/?FUZZ=value -fs 81
```

## 关于子域名爆破

### Gobuster

```bash
sudo gobuster vhost -u http://10.129.230.193 --domain crafty.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain -k -r -t 100
```

- vhost：指定虚拟主机枚举模式
- --domain：指定基础域名
- -k：跳过 `SSL/TLS` 证书验证
- -r：自动跟随重定向
- -t 100：设置并发线程为 100

### Ffuf

```bash
sudo ffuf -H "Host: FUZZ.soulmate.htb" -u http://soulmate.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac
```

- -H：添加自定义 `HTTP` 请求头
- Host: FUZZ.soulmate.htb：设置 `Host` 头部
- FUZZ：`ffuf` 的关键占位符
- -ac：自动校准模式

## 登入认证破解

### Nmap

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ sudo nmap -p80 --script=http-brute 10.129.5.91  
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-28 08:11 EST
Stats: 0:08:01 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 0.00% done
Stats: 0:08:47 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 0.00% done
Nmap scan report for 10.129.5.91
Host is up (0.095s latency).

PORT   STATE SERVICE
80/tcp open  http
| http-brute: 
|   Accounts: 
|     admin:admin - Valid credentials
|_  Statistics: Performed 45009 guesses in 535 seconds, average tps: 84.6

Nmap done: 1 IP address (1 host up) scanned in 535.72 seconds
```

## 暴力破解

### Hashcat

- 破解 `MD5`

```bash
sudo hashcat -m 0 -a 0 hash/hash.lst /usr/share/wordlists/rockyou.txt
```

- 破解 `7z`

```bash
sudo hashcat -m 11600 -a 0 7z_hash.txt /usr/share/wordlists/rockyou.txt
```

- 查看破解过的 `hash`

```bash
sudo hashcat -m 0 --show hash/hash.lst
```

- 规则模式

```bash
sudo hashcat -m 0 -a 0 hash/hash.lst /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/InsidePro-PasswordsPro.rule -0 -w 3
```

### Hydra

- 破解多个用户

```bash
sudo hydra -L users.txt -P wordlist.txt
```

- 破解单个用户

```bash
sudo hydra -l "aaa" -P wordlist.txt
```

- 破解 Web POST

```bash
sudo hydra -l "key" -P /usr/share/wordlists/rockyou.txt 10.10.10.7 http-form-post "/kzMb5nVYJw/index.php:key=^PASS^:invalid key"
```

- FTP 密码喷射

```bash
sudo hydra -L hash/users.lst -P /usr/share/wordlists/rockyou.txt ftp://10.10.10.35 -f
```

- SSH 密码喷射

```bash
hydra -l sword -P passwords.txt ssh://10.10.10.5 -t 30 -V
```

- 破解登入框

```bash
sudo hydra -l shaldon -P password.txt -f 10.10.10.39 -s 80 http-get /the_real_secret_dir
```

### Ffuf

- 破解 Web POST

```bash
sudo wfuzz -c -z file,/usr/share/wordlists/rockyou.txt --hc 404,401 -d "username=admin&password=FUZZ" http://driver.htb
```

### John

- 破解 `hash`

```bash
sudo john hash/hash.lst --wordlist=/usr/share/wordlists/rockyou.txt
```

- 破解 `id_rsa`

```bash
/usr/share/john/ssh2john.py hash/id_rsa > crack.txt  
```

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa     
```

- 破解 7z

```bash
/usr/share/john/7z2john.py backup.7z > 7z_hash.txt
```

```bash
john 7z_hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

- 破解 zip

```bash
sudo /usr/sbin/zip2john flag.zip > flag.txt
```

```bash
john flag.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

- 生成更好的字典

```bash
john -rules -wordlist=password.txt - stdout | sort | uniq > wordlist.txt
```