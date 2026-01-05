---
title: 如何为靶机配置 DHCP
date: 2025-06-10T17:29:33+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
---
> 此文章以 kali 地址为 10.10.10.5 为示例

## 环境判断

确保靶机为 NAT 连接

![NTA](NTA.png)

在 kali 中执行 nmap 扫描，未发现靶机的地址

![初次扫描](初次扫描.png)

## 获取 DHCP

> [如何进入单用户模式](https://www.volcengine.com/docs/6396/81140)

以 Debian 为例，进入单用户模式后查看网卡信息，为 ens33

![ipa](ipa.png)

为 interface 文件添加 ens33

![修改前](修改前.png)

![修改后](修改后.png)

保存后执行网络重启命令后获得 ip

```bash
service networking restart
```

![获得](获得.png)

回到 kali 中，重新获得 ip

![获得ip.png](获得ip.png)