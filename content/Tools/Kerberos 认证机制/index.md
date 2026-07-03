---
title: Kerberos 认证机制
date: 2026-04-07T21:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
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

## AS-REP Roasting

AS-REP Roasting 利用的就是 Kerberos 预身份验证的机制缺陷。正常情况下用户向 KDC 申请 TGT 时（AS-REQ），必须先用自己的密码派生出的密钥加密一个时间戳发送，KDC 解密成功才证明你确实知道这个密码，这就是预认证。但如果某个账户设置了 `DONT_REQ_PREAUTH` 这个 UCA 标志位，KDC 就会跳过这一步验证，直接返回 AS-REP 响应。这个响应有一段是用密码派生的密钥加密的，相当于 KDC 主动把一段用目标密码加密的密文发给了我。只要将其拿到本地离线爆破，就能还原出明文密码。

举一个具体的例子，在我的 Writeup  `Blackfield` 中已经拿到了一个用户列表，然后使用 `Impacket` 套件的 `GetNPUsers`，带着 `-no-pass` 和这份用户列表去请求 `AS-REP`，然后发现 support 这个账户预认证是关的，于是拿到一段 `krb5asrep$23$...` 的 hash。

站在防御角度上尽量不要给账户开启 `DONT_REQ_PREAUTH`，如果一定要开的话要配置高强度密码，并优先使用 AES 而不是 RC4 降低离线爆破成功率；同时监控大量 `AS-REQ` 但没有预认证数据的一场请求（事件 ID 4768）。

## Kerberoasting

Keberoasting 利用的是 TGS 的签发机制。在 AD 里，任何一个拿到了有效 TGT 的域用户都可以向 KDC 申请访问某个服务的 TGS 票据。指定目标服务 SPN（Service Principal Name），KDC 就会签发。KDC 返回的这张 TGS 票据里，有一部分是用该服务账号密码派生出的 NTLM hash 加密。也就是说，KDC 会把这一段用服务账号密码加密的密文交到手里，它不会校验我到底有没有权限访问这个服务。整个过程不需要和目标服务有任何实际交互，也不会在目标服务上留下登录痕迹。

这个利用的前提有两个：

1. 有一组有效的域凭据，哪怕是最低权限的普通域用户也行，因为申请 TGS 的前提是有 TGT。
2. 目标域里存在注册了 SPN 的用户账户。（是用户账户而不是机器账户）

举一个例子，在我的 Writeup `Active` 中先通过匿名访问 SMB 的 Replication 共享，在 SYSVOL 策略目录翻到一个 Groups.xml，里面有 GPP 加密的 cpassword，用 gpp-decrypt 解出了SVC_TGS 这个低权限域用户的密码。拿到这组域凭据后就要想到 Kerberoasting，然后使用 `impacket` 套件的 `GetUserSPNs` 带上 `request` 参数去枚举域内注册的 SPN 账户，然后拿到了 Administrator 账户。

在防御的角度上有以下几点需要注意：

1. 服务账户使用足够长、足够随机的强密码，最好上 gMSA（组托管服务账户），让系统自动管理 120 位的随机密码并定期轮换。
2. 把加密类型从 RC4 强制升级到 AES。
3. 不给高权限用户注册 SPN。
4. 监控异常的 TGS 请求，如单个账户申请大量不同的 SPN 票据（事件 ID 4769），尤其是 RC4 加密类型的请求。

### 为什么 RC4 比 AES 更容易爆破

爆破的时候拿候选密码推导出密钥，去解密那段密文，然后看解出来的结构对不对（HMAC 校验能不能通过），如果对说明猜中了。

RC4 派生的密钥几乎都是免费的，一次 MD4 运算就出密钥了。MD4 极快、无迭代、且没有 salt 使用成本比较低。

AES 的密钥派生比较贵，一次试密码要 1096 论 HMAC-SHA1，且有 salt。

## Golden Ticket

Goldent Ticket 是一张伪造的 TGT。域里所有的 TGT 都是由 KDC 用一个叫 krbtgt 的账户的密码 hash 来加密和签名的。客户端拿着 TGT 去申请服务票据时候 KDC 的校验逻辑是：只要能用 krbtgt 的密钥成功解密这张 TGT 就认为是合法的，里面写的身份和权限就全盘接受。

一旦拿到 krbtgt 的 hash，就可以离线伪装一张 TGT，用户名可以填任意值，组 SID 可以塞进 Domain Admins、Enterprise Admins 这些高权限组的 SID。这张票拿到域里 KDC 用 krbtgt 密钥解开了就会接受，进而变为管理员，等同于拿到了整个域的万能钥匙。

举一个例子，在 Forest 的最后阶段就是通过 DCSync 复制凭据完成域控制的，而 DCSync 拿到的东西就包括 krbtgt hash。