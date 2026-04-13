---
title: Kerberos 认证机制
date: 2026-04-07T21:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## Kerberos 认证机制

Kerberos 是 Active Directory 的网络认证协议。采用票根系统，而非网络发送密码。

举个例子，在进入游乐园前要检票，检完票给手腕上戴一个手环，之后可以凭借手环游玩游乐园内的游乐设备。这个手环就是 ticket，游乐设备就是 services。

### KDC 密钥分发中心

KDC（Key Distribution Center） 运行在域控制器上，有两个组成部分：

1. AS（Authentication Service）验证身份
2. TGS（Ticket Granting Service）为特定服务发放票根

### TGT 

TGT（Ticket Granting Ticket）是票根，用于证明已获得认证。

### TGS 

TGS（Ticket Granting Service Ticket）为特殊服务发放票根。

### SPN

SPN（Service Principal Name）用于识别在主机上运行的服务的身份（唯一）

## 认证过程

1. AS-REQ（Authentication Service Request）用户客户端发送请求给 KDC “我是 Hernandez ，我想登入。” 这包含了用户密码哈希加密的时间戳，称为预认证。
2. AS-REP（Authentication Service Replay）KDC 用用户储存的哈希解密时间戳，如果匹配则 KDC 传回带账号加密的 TGT。
3. TGS-REQ（Ticket Granting Service Request）当用户想访问某个服务时客户端发送 TGT 到 KDC 请求获取这个服务的票根。
4. TGS-REP（Ticket Granting Service Replay）KDC 验证 TGT，如何发布目标服务账户密码哈希加密的服务票根。
5. AP-REQ（Application Request）客户端向目标服务展示服务票根，该服务用自己的哈希解密并授予访问权限。