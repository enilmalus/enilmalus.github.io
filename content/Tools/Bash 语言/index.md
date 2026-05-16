---
title: Bash 语言
date: 2026-05-14T11:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## 一个 Bash 例子

```bash
#!/bin/bash

if [ $# -eq 0 ]
then
	echo -e "You need to specify the target domain.\n"
	echo -e "Usage:"
	echo -e "\t$0 <domain>"
	exit 1
else
	domain=$1
fi

<SNIP>
```

- `#!/bin/bash`：Shebang，告诉系统用 `/bin/bash` 来执行这个脚本
- `if-else-fi`：条件执行语句
- `echo`：输出
- `$#/$0/$1`：特殊变量
- `domain`：变量

- `$#` 是一个特殊变量，表示传入脚本的参数个数
- `-eq 0` 是数值比较，意思为等于 0
- `[` 和 `]` 前面必须要有空格，这是 bash 的硬性要求，因为 `[` 是命令 `test` 的别名
- `exit 1` 表示立即退出脚本，返回码为 1 ，返回 0 表示返回成功，非 0 表示出错。
- `$1` 表示第一个位置参数，以此类推

### Shebang

Shebang 以 `#!` 开头，告诉系统以什么环境执行。

如下面这两个例子。

```bash
#!/usr/bin/env python
```

```bash
#!/usr/bin/env perl
```

### If-Else-Fi

经典的 `IF-ELSE` 语句。

看下面这个例子。

```bash
if [the number of given arguments equals 0]
then
	Print: "You need to specify the target domain."
	Print: "<empty line>"
	Print: "Usage:"
	Print: "     <name of the script> <domain>"
else
	The "domain" variable servers as the alias for the given argument
finish the if-condition
```

### If-Only.sh

看这个例子。

```bash
#!/bin/bash

value=$1

if [ $value -gt "10" ]
then
	echo "Given argument is greater than 10"
fi
```

- `value=$1` 等号两边不能有空格，如果有空格会被 bash 当成执行 `value` 命令，参数是 `=` 和 `$1`
- `-gt` 是 `greater than`，即判断是否大于


| 运算符 | 含义               |
| --- | ---------------- |
| -eq | 等于（equal）        |
| -ne | 不等于（not equal）   |
| -gt | 大于（greater then） |
| -lt | 小于（less than）    |
| -ge | 大于等于             |
| -le | 小于等于             |


```bash
┌──(kali㉿kali)-[~/Work/Kali/Bash]
└─$ ./If_Only.sh 10                         
                                                                                                                                                    
┌──(kali㉿kali)-[~/Work/Kali/Bash]
└─$ ./If_Only.sh 18
Given argument is greater than 10
```

### If-Elif-Else.sh

看下面这个例子。

```bash
#!/bin/bash

value=$1

if [ $value -gt "10" ]
then
	echo "Given argument is greater than 10"
elif [ $value -lt "10" ]
then
	echo "Given argument is less than 10"
else
	echo "Given argument is not a number"
fi
```

### Exercise Script

```bash
#!/bin/bash

var="nef892na9s1p9asn2aJs71nIsm"

for counter in {1..40}
do
	var=$(echo $var | base64)
done
echo $var
```

这是一个简单的转换为 base64 的脚本。

## 传参

看这个例子。

```bash
#!/bin/bash

if [ $# -eq 0 ]
then
	echo -e "You need to specify the target domain.\n"
	echo -e "Usage:"
	echo -e "\t$0 <domain>"
	exit 1
else
	domain=$1
fi
```

不带参数执行。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Bash]
└─$ ./cidr.sh           
You need to specify the target domain.

Usage:
        ./cidr.sh <domain>
```


| 标识符 | 意义           |
| --- | ------------ |
| $#  | 记录传递给脚本的参数数量 |
| $@  | 检索命令行的参数列表   |
| $n  | $1           |
| $$  | 进程的 ID       |
| $?  | 脚本退出状态       |


| 文件操作符 | 描述                |
| ----- | ----------------- |
| -e    | 如果该文件存在           |
| -f    | 测试是否为文件           |
| -d    | 测试是否为目录           |
| -L    | 检验是否为符号链接         |
| -N    | 检查文件是否在最后一次阅读被修改  |
| -O    | 如果当前用户拥有该文件       |
| -G    | 如果文件的组 ID 与当前用户匹配 |
| -s    | 测试文件大小是否大于 0      |
| -r    | 测试文件是否拥有读取权限      |
| -w    | 测试文件是否具有写入权限      |
| -x    | 测试文件是否具有执行权限      |
