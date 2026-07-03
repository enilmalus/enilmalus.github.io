---
title: 代码、命令执行
date: 2026-06-25T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
  - 代码执行
  - 命令执行
---
## 原理

- 代码执行：执行的是编程语言层面的代码，比如 PHP 的 `eval()`、Python 的 `eval/exec`、Java 的表达式注入。攻击者注入的是该语言的语句，运行在语言解释器的上下文里。
- 命令执行：执行的是操作系统的 shell 命令，比如 PHP 的 `system()`、`exec()`，或者程序把用户输入拼进了一条系统命令。攻击者注入的是 `whoami`、`cat /etc/passwd` 这种 OS 命令，运行在系统 shell 的上下文里。

二者的根源是同一类问题，用户可控的输入流入了会执行的危险函数。区别在于流入的是代码解析函数还是命令执行函数。代码执行往往能进一步调用命令执行（比如 PHP `eval` 里写 `system()`），所以代码执行通常被认为危害更全能，但二者拿到的最终都是服务器上的执行能力。

## 命令执行

- 直接执行：程序直接把用户输入交给 `system($_GET['cmd'])`，本身就是设计缺陷。
- 命令拼接注入：更常见、更隐蔽。程序本意只想执行一条固定命令（比如 ping 一个用户输入的 IP：`system("ping".$ip)`），但没过滤，攻击者用命令连接符把自己的命令拼进去。

- `;`：顺序执行，前面跑完跑下一条。
- `&&`：前面一条执行成功才执行后一条。
- `||`：前一条失败才执行后一条。

比如：参数 `ip=127.0.0.1; whoami` 或 `ip=1270.0.0.1 | whoami`，ping 之外的 `whoami` 就被执行了。

### 代码执行

- PHP：`eval()`、`assert()`、`preg_replace`、的 `/e` 修饰符（老版本）、`create_function`、回调函数（`call_user_func`、`array_map`）
- Python：`eval()`、`exec()`、`pickle.loads`（反序列化）、模板注入（Jinja2 SSTI）
- Java：脚本引擎、表达式注入（SpEL、OGNL、对应 Struts2/Spring 的洞）`