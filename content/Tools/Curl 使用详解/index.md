---
title: Curl 使用详解
date: 2025-12-28T17:29:33+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
---
## curl 原理剖析

### curl 核心机制

- Libcurl 驱动：curl 是 libcurl 库的命令行前端，实际上 curl 的每一个参数都在映射 libcurl 的 curl_easy_setopt()  函数调用。
- 协议自动协商：curl 不仅发送 HTTP，它会根据 URL scheme（ftp://、dict://、gopher://）自动切换底层协议栈。
- 连接复用：再以此命令中请求多个 URL 时，curl 会尝试复用 TCP 连接

> Libcurl 是 curl 项目提供的跨平台 C 库，用于处理 URL 数据传输，支持 HTTP、FTP、SMTP 等多种协议。
## curl 参数详解

### curl 帮助命令

下面为 curl 详细地帮助命令

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ curl -h                             
Usage: curl [options...] <url>
 -d, --data <data>           HTTP POST data
 -f, --fail                  Fail fast with no output on HTTP errors
 -h, --help <subject>        Get help for commands
 -o, --output <file>         Write to file instead of stdout
 -O, --remote-name           Write output to file named as remote file
 -i, --show-headers          Show response headers in output
 -s, --silent                Silent mode
 -T, --upload-file <file>    Transfer local FILE to destination
 -u, --user <user:password>  Server user and password
 -A, --user-agent <name>     Send User-Agent <name> to server
 -v, --verbose               Make the operation more talkative
 -V, --version               Show version number and quit

This is not the full help; this menu is split into categories.
Use "--help category" to get an overview of all categories, which are:
auth, connection, curl, deprecated, dns, file, ftp, global, http, imap, ldap, output, pop3, post, proxy, scp, sftp, smtp, ssh, telnet, tftp, timeout, tls, upload, verbose.
Use "--help all" to list all options
Use "--help [option]" to view documentation for a given option
```

### 参数详解

#### -d/--data \<data\> 参数

使用 -d 参数，curl 默认将 HTTP 方法切换为 POST，默认 Content-Type 被设置为 `application/x-www-form-urlencoded` 。

#### -T/--upload-file \<file\> 参数

文件上传

#### -A/--user-agent \<name\> 参数

修改 HTTP 请求头中的 User-Agent 字段

#### -u/--user \<user:password\> 参数

将 user:password 进行 Base64 编码，并添加到 `Header: Authorization: Basic <base64_string>。`

#### -v/--verbose 参数

这个参数是笔者在实际渗透测试中最常用的参数之一，作用为开启详细模式，便于阅读返回的数据。

#### -i/--show-headers 参数

查看响应头。

#### -f/--fail 参数

即使服务器返回 404 或 500 也会输出页面内容。

#### -o filename/-O

- -o enil：重命名保存为名称为 enil 的文件。
- -O：原名保存。

#### -s 参数

静默模式，不显示进度条。