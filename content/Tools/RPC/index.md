---
title: RPC
date: 2026-02-15T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - RPC
---
## 概念

RPC 是 Remote Procedure Call，远程过程调用。

核心的意思是让一台机器上的程序像调用本地函数一样调用另一台机器上的功能或服务，在 Windows 域环境中 RPC 被大量用于管理和查询服务。

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

看下面这个例子

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

建立匿名的 RPC 会话，但目标只允许匿名用户查询少量 LSA 域信息，不允许枚举用户、共享或密码策略。

- srvinfo：访问 SRVSVC RPC 接口，通常用于查询服务器信息，如服务器版本、注释、角色
- enumdomusers：通过 SAMR 结果枚举域内用户
- querydispinfo：枚举 用户/组 信息
- getdompwinfo：读取域密码策略
- lsaquery：访问 LSARPC/LSA 接口，用于查询安全策略和域标识信息