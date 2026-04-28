---
title: RPC
date: 2026-02-15T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## Rpcclient

连接 135 rcp 端口。

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ rpcclient -U '' -N 10.129.5.91
Cannot connect to server.  Error was NT_STATUS_ACCESS_DENIED
```

- -U 指定用户名参数，使用空字符串表示匿名用户
- -N 表示不使用密码进行认证

标准枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Blackfield]
└─$ rpcclient -U '' -N 10.129.229.17 
rpcclient $> srvinfo
do_cmd: Could not initialise srvsvc. Error was NT_STATUS_ACCESS_DENIED
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
rpcclient $> querydispinfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> getdompwinfo
result was NT_STATUS_ACCESS_DENIED
rpcclient $> lsaquery
Domain Name: BLACKFIELD
Domain Sid: S-1-5-21-4194615774-2175524697-3563712290
```