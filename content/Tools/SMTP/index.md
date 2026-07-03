---
title: SMTP
date: 2026-07-02T09:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - SMTP
  - 技术
---
## 简介

SMTP（Simple Mail Transfer Protocol）简单邮件传输协议，是互联网中用于发送和转发电子邮件的应用层协议。

邮件客户端/邮件服务器把邮件交给下一台邮件服务器，直到送到收件人的邮箱服务器。

基本工作流程如下：

Enil 给 Malus 发邮件

1. Enil 的邮件客户端把邮件提交给自己的邮件服务器
2. Enil 的邮件服务器查询 Malus 邮箱域名的 MX 记录，找到负责接收该域邮件的服务器
3. Enil 的服务器通过 SMTP 与 Malus 的邮件服务器建立连接
4. 发送方依次告诉对方：
	
	- 发件人是谁 ：`MAIL FROM`
	- 收件人是谁：`RCPT TO`
	- 邮件内容开始：`DATA`

5. 收件服务器接受邮件后，将其存入 Malus 的邮箱
6. Malus 再通过 IMAP 或 POP3 读取邮件

## SMTP 常见命令

```SMTP
HELO / EHLO
MAIL FROM:<enil12408@gmail.com>
RCPT TO:<malus12408@gmail.com>
DATA
Subject: TEST

Hello Malus
.
QUIT
```

其中 `HELO / EHLO` 表示客户端发送的自我介绍命令；单独一行的 `.` 表示邮件正文结束。

## 实例

在一次 Nmap 的扫描结果如下：

```Nmap
25/tcp    open  smtp?
| smtp-commands: REEL, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Kerberos, LDAPBindReq, LDAPSearchReq, LPDString, NULL, RPCCheck, SMBProgNeg, SSLSessionReq, TLSSessionReq, X11Probe: 
|     220 Mail Service ready
|   FourOhFourRequest, GenericLines, GetRequest, HTTPOptions, RTSPRequest: 
|     220 Mail Service ready
|     sequence of commands
|     sequence of commands
|   Hello: 
|     220 Mail Service ready
|     EHLO Invalid domain address.
|   Help: 
|     220 Mail Service ready
|     DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
|   SIPOptions: 
|     220 Mail Service ready
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|     sequence of commands
|   TerminalServerCookie: 
|     220 Mail Service ready
|_    sequence of commands
```

存在 SMTP 服务，可以进行基础通讯。

测试 SMTP 的通讯情况。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ telnet 10.129.30.46 25                     
Trying 10.129.30.46...
Connected to 10.129.30.46.
Escape character is '^]'.
220 Mail Service ready
HELO test
250 Hello.
MAIL FROM: <enil@admin.com>
250 OK
RCPT TO: <nico@megabank.com>
250 OK
RCPT TO: <administrator@megabank.com>
550 Unknown user
```

- 这里使用 telnet 连接目标，使用 `HELO test` 发起对话，返回 `250 Hello` 表示服务器接受了这个会话。
- `MAIL FROM: <enil@admin.com>` 设置了邮件系信封发送人为 `enil@admin.com`。
- `RCP TO: <nico@megabank.com>` 指定了收件人为 `nico@megabank.com`，服务端返回 `OK` 说明接受该收件人地址。
- 继续测试指定收件人为 `administrator@megabank.com` 失败，说明该地址不存在。

可以使用 sendEmail 发送邮件并附带文件。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Reel]
└─$ sendEmail -f enil@megabank.com -t nico@megabank.com -u "Invoice Attached" -m "You are overdue payment" -a invo.rtf -s 10.129.173.182 -v 
May 31 03:41:48 kali sendEmail[4463]: DEBUG => Connecting to 10.129.173.182:25
May 31 03:41:48 kali sendEmail[4463]: DEBUG => My IP address is: 10.10.16.15
May 31 03:41:48 kali sendEmail[4463]: SUCCESS => Received:      220 Mail Service ready
May 31 03:41:48 kali sendEmail[4463]: INFO => Sending:  EHLO kali
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      250-REEL, 250-SIZE 20480000, 250-AUTH LOGIN PLAIN, 250 HELP
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending:  MAIL FROM:<enil@megabank.com>
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      250 OK
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending:  RCPT TO:<nico@megabank.com>
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      250 OK
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending:  DATA
May 31 03:41:49 kali sendEmail[4463]: SUCCESS => Received:      354 OK, send.
May 31 03:41:49 kali sendEmail[4463]: INFO => Sending message body
May 31 03:41:49 kali sendEmail[4463]: Setting content-type: text/plain
May 31 03:41:49 kali sendEmail[4463]: DEBUG => Sending the attachment [invo.rtf]
May 31 03:42:00 kali sendEmail[4463]: SUCCESS => Received:      250 Queued (11.224 seconds)
May 31 03:42:00 kali sendEmail[4463]: Email was sent successfully!  From: <enil@megabank.com> To: <nico@megabank.com> Subject: [Invoice Attached] Attachment(s): [invo.rtf] Server: [10.129.173.182:25]
```