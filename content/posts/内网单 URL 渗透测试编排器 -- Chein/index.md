---
title: 内网单 URL 渗透测试编排器 -- Chein
date: 2026-08-20T14:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack - 技术
---
# Chein —— 内网单 URL 渗透测试编排器

在无法连接外网的内网环境中，输入一个 URL，一键调度多款成熟安全工具完成侦察与扫描，
自动发现目标背后的 API 接口、自动执行越权测试，并把异构输出收敛为统一、带证据的
渗透测试报告。

> ⚠️ **本工具仅限授权测试使用。请勿对未获得书面授权的目标运行。**

开源地址：[Chein](https://github.com/enilmalus/Chein)

```
   ____ _     _
  / ___| |__ (_)_ __      nmap · httpx · whatweb · feroxbuster
 | |   | '_ \| | '_ \     nuclei · ZAP · sqlmap · arjun
 | |___| | | | | | | |    + API 自动探测 + 自动越权测试 (IDOR)
  \____|_| |_|_| |_| |_   纯离线 · 零 Python 依赖 · 单文件 HTML 报告
```

---

## 目录

- [它是什么](#它是什么)
- [特性](#特性)
- [整体架构](#整体架构)
- [快速开始](#快速开始)
- [认证与登录](#认证与登录)
- [API 自动探测](#api-自动探测)
- [自动越权测试](#自动越权测试)
- [流水线](#流水线)
- [命令行参数](#命令行参数)
- [配置参考](#配置参考)
- [报告解读](#报告解读)
- [目录结构](#目录结构)
- [离线部署](#离线部署)
- [安全与合规](#安全与合规)
- [已知限制](#已知限制)
- [路线图](#路线图)

## 它是什么

Chein 是一个**编排器，不是扫描引擎**。它不重复发明 nmap / nuclei / ZAP 的能力，
而是：

1. **调度**：按流水线自动串起八类成熟安全工具，阶段内并行、工具缺失自动降级跳过；
2. **探测**：内置 API 自动探测模块（文档探针 / JS 提取 / 字典爆破 / 方法枚举），
   把"目标有哪些接口"这步从手工变成全自动；
3. **测试**：内置自动越权测试（未授权重放 + 水平越权 IDOR），补上扫描器测不到的
   访问控制缺陷——OWASP Top 10 第一名；
4. **收敛**：把各工具的异构输出归一化为统一的 Finding 模型，去重、评分，
   生成带证据的 Markdown / 单文件 HTML / JSON 三种报告。

设计目标：**输入一个 URL（可带登录凭据），一条命令得到可交付、可追溯的渗透测试结果。**

## 特性

- **统一 Adapter 接口**：nmap / httpx / whatweb / feroxbuster / nuclei / ZAP /
  sqlmap / arjun 八工具即插即用，任一缺失只跳过对应阶段，不影响其余流程
- **API 自动探测四路通道**：接口文档探针（OpenAPI/Swagger/GraphQL/WADL）+
  前端 JS 资产提取 + API 字典爆破 + 已发现路径方法枚举，汇聚为统一端点表
- **自动越权测试**：基于端点表 + 登录态，自动做未授权重放与水平越权（IDOR）探测，
  输出带证据的越权线索（仅 GET，默认开启）
- **认证登录支持**：表单登录（账号/密码）、HTTP Basic、会话 Cookie 注入、自定义
  请求头；登录态自动贯通内置探测与全部工具；ZAP 通过官方认证 API 自登录
- **ZAP 全自动编排**：无头守护 + REST API（Spider → AJAX Spider → OpenAPI 导入 →
  Active Scan），未启动时自动拉起守护进程
- **纯离线**：核心只用 Python 标准库，零 pip 依赖；运行时零外网请求
- **跨平台**：Linux / macOS / Windows 均可运行（进程管理、ZAP 启动脚本已做平台自适应）
- **证据留痕**：每步工具的原始 stdout/stderr 全量落盘 `raw/`，每条发现可追溯
- **安全内建**：授权人必填抬头、scope 同源校验、跨域重定向拒绝跟随、默认保守速率、
  方法枚举只发安全方法（OPTIONS/HEAD/GET）

## 整体架构

```
┌────────────────────────────────────────────────────────────┐
│  CLI (argparse)      chein.py <URL> [选项]                  │
├────────────────────────────────────────────────────────────┤
│  编排层  orchestrator.py   9 阶段流水线, 阶段内并行, 降级跳过 │
│  认证    auth.py           表单登录 / Basic / Cookie / 头    │
│  越权    idor.py           未授权重放 + 水平越权 IDOR        │
│  收敛    dedup.py          去重 · 评分 · 严重度              │
├────────────────────────────────────────────────────────────┤
│  API 探测  api_discovery/   文档探针 / JS 提取 / 方法枚举    │
│  工具适配  adapters/        8 个 Adapter (统一接口)          │
│  执行器    runner.py        超时控制 / 原始输出落盘 / 流式回显│
│  HTTP      http_util.py     内置客户端 (Cookie jar/重定向)   │
├────────────────────────────────────────────────────────────┤
│  报告  reporting.py         findings.json / report.md/html   │
└────────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求

- Python 3.10+（无第三方依赖，无需 pip install）
- 按需安装安全工具（清单与离线下载地址见 [`tools.txt`](tools.txt)），
  工具缺失时对应阶段自动跳过

### 三步跑起来

```bash
# 1. 环境自检 —— 工具/字典/模板是否就绪
python3 chein.py --list-tools

# 2. 基础扫描（自动探测接口 + 生成报告）
python3 chein.py http://10.0.0.5/

# 3. 带登录的完整扫描（有测试账号时推荐）
python3 chein.py http://10.0.0.5/ \
    --username tester --password 'P@ssw0rd' \
    --login-url http://10.0.0.5/login \
    --authorized-by "Enil/2026-08-20"
```

Windows 下把 `python3` 换成 `python`，其余一致；建议使用 Windows Terminal
以获得正确的中文与颜色显示。

### 典型命令

```bash
# 快速摸底（几分钟出资产与接口, 跳过重工具）
python3 chein.py http://10.0.0.5/ --skip zap,nuclei,sqlmap

# 完整扫描（全端口 + ZAP + nuclei + 注入验证, 数十分钟~数小时）
python3 chein.py http://10.0.0.5:8080/app \
    --full-ports --zap-port 8080 --with-sqlmap \
    --username tester --password pass --login-url http://10.0.0.5:8080/login \
    --authorized-by "张三"

# 只深挖 API 接口（目标明确是接口服务时）
python3 chein.py http://10.0.0.5:8080/ --skip nmap
```

### 输出

结果在 `output/<主机>_<时间戳>/`：

| 文件 | 说明 |
|---|---|
| `report.html` | 单文件离线报告（深色主题，浏览器直接打开，交付/汇报用） |
| `report.md` | Markdown 报告（写正式文档直接抄） |
| `findings.json` | 结构化结果（发现 + 端点表 + 告警 + 认证状态），二次处理用 |
| `raw/` | 所有工具的原始 stdout/stderr，证据留痕 |

## 认证与登录

目标需要账号密码时，四种方式任选其一或组合使用。登录成功后会话 Cookie 自动贯通
所有探测通道，报告"概览"区会记录认证状态：

```bash
# 方式 1: 表单登录（最常见）—— 自动提交凭据并捕获会话 Cookie
python3 chein.py http://10.0.0.5/ \
    --username tester --password 'P@ssw0rd' \
    --login-url http://10.0.0.5/login

# 自定义登录请求体（{u}/{p} 为账号密码占位符; 以 { 开头按 JSON 提交）
#   --login-data 'user={u}&pass={p}&remember=1'
#   --login-data '{"username":"{u}","password":"{p}"}'
# 登录成功校验标记（响应体必须包含, 防"登录失败仍返回 200"误判）
#   --login-success '欢迎'

# 方式 2: HTTP Basic 认证
python3 chein.py http://10.0.0.5/ --auth-basic 'admin:P@ssw0rd'

# 方式 3: 已有浏览器会话, 直接注入 Cookie（跳过登录流程）
python3 chein.py http://10.0.0.5/ --cookie 'JSESSIONID=abc123; token=xyz'

# 方式 4: 自定义请求头（如 API Token）
python3 chein.py http://10.0.0.5/ --header 'Authorization: Bearer eyJ...'
```

行为约定：

- 登录失败会**明确告警**并降级为匿名扫描（报告可见），不会静默误报
- 登录地址默认必须与目标同主机；同注册域（`sso.corp.com` 之于 `app.corp.com`）
  或解析到同一 IP 时自动放行；真正的跨域 SSO 加 `--allow-cross-host-login` 放行
- 跨域重定向拒绝跟随（防凭据被带出 scope）
- ZAP 不共享 Cookie，而是通过 `formBasedAuthentication` 等官方 API 让 ZAP
  自己用测试账号登录（需 add-on 齐全，见 `tools.txt`）
- 凭据会出现在工具进程参数中（可被 `ps` 看到）；介意可写入
  `config.json -> auth` 段避免出现在命令行

## API 自动探测

给定 URL 后，从四个方向并行收集接口线索，汇聚为统一**端点表**（方法 × 路径 ×
参数 × 认证要求 × 证据来源），再分发到扫描器：

| 通道 | 原理 | 说明 |
|---|---|---|
| 文档主动发现 | 探测 swagger/openapi/graphql/wadl 常见路径并解析 | 命中率最高；OpenAPI 同步导入 ZAP |
| 前端 JS 提取 | 拉取页面与爬虫发现的 JS，正则提取接口路径与方法 | SPA 应用核心通道 |
| 字典爆破 | feroxbuster 挂 API 字典 + 常规目录字典 | 兜底通道 |
| 方法枚举 | 对已发现路径发 OPTIONS/HEAD/GET 探测允许的方法 | 只发安全方法 |

端点表在报告中独立成章，可当作后续手工测试的靶子清单。

## 自动越权测试

登录态就绪时，阶段 5.5 对端点表自动执行两档检测（**仅 GET**、走 scope 校验与限速、
默认开启）：

- **未授权重放**：去掉会话 Cookie 重放每个 GET 端点；匿名仍返回相同内容（相似度
  ≥ 阈值）→ 高/中危"未授权访问"线索
- **水平越权（IDOR）**：对 `{id}` 路径参数或 id 类 query 参数，从基线响应中提取
  候选值（他处出现的 id）替换重放；返回同结构不同数据 → 中危 IDOR 线索

```bash
python3 chein.py http://10.0.0.5/ --username tester --password pass \
    --login-url http://10.0.0.5/login   # 越权测试自动执行
python3 chein.py http://10.0.0.5/ --no-idor   # 关闭
```

产出写入报告"发现明细"（tool=idor），带证据（两组 URL + 状态码 + 响应片段），
属于**线索**，需人工打开证据确认。上限与阈值在 `config.json -> idor` 调整；
垂直越权（低权限账号调管理接口）需要第二个账号，暂未启用。

## 流水线

```
阶段0   认证      (可选) 表单登录 → 捕获会话 Cookie
阶段1   存活      httpx（缺失回退内置 HTTP 检查）
阶段2   侦察      nmap + whatweb 并行
阶段3   发现      ZAP 爬虫 ∥ feroxbuster(目录) ∥ feroxbuster(API) ∥ 文档探针 并行
阶段4   分析      JS 端点提取 + 方法枚举 → 端点表去重汇聚
阶段5   参数      arjun 隐藏参数（可选, --with-arjun）
阶段5.5 越权      自动越权测试: 未授权重放 + 水平越权 IDOR（默认开启）
阶段6   扫描      ZAP 主动扫描 ∥ nuclei 模板验证 并行
阶段7   注入      sqlmap（可选, --with-sqlmap, 仅含参端点）
阶段8   报告      去重 → 评分 → findings.json / report.md / report.html
```

任一阶段失败或工具缺失只记录告警并继续，不会中断整条流水线。

## 命令行参数

```
用法: python chein.py <URL> [选项]

扫描控制:
  --full-ports             nmap 全端口扫描 (1-65535)
  --aggressive             激进模式 (提高速度/线程, 慎用)
  --with-sqlmap            对含参端点运行 sqlmap 注入验证
  --with-arjun             运行 arjun 隐藏参数探测
  --zap-port PORT          启用 ZAP 并指定 REST API 端口
  --no-idor                关闭自动越权测试
  --skip TOOLS             跳过模块 (逗号分隔: nmap,whatweb,feroxbuster,
                           zap,nuclei,sqlmap,arjun,discovery,httpx,idor)
  --threads N              feroxbuster 并发线程数
  --timeout SEC            单工具默认超时 (秒)

认证与登录:
  --auth-basic USER:PASS   HTTP Basic 认证
  --username U / --password P    表单登录凭据
  --login-url URL          登录提交地址
  --login-data STR         登录请求体模板 ({u}/{p} 占位符, { 开头为 JSON)
  --login-method {POST,GET}
  --login-success TEXT     登录成功后响应体必须包含的标记
  --allow-cross-host-login 放行跨域 SSO 登录 (默认拒绝)
  --cookie STR             直接注入会话 Cookie 'a=b; c=d'
  --header "K: V"          附加请求头 (可重复)

其他:
  --config FILE            配置文件 (默认 ./config.json)
  --outdir DIR             报告输出根目录 (默认 ./output)
  --authorized-by NAME     授权人 (写入报告抬头, 务必填写)
  --list-tools             打印工具/字典/模板可用性清单后退出
  --version                显示版本
```

## 配置参考

全部配置在 `config.json`（开箱含默认值；`tool_paths` 为空时从 PATH 查找）：

| 配置段 | 说明 |
|---|---|
| `tool_paths` | 各工具二进制/脚本绝对路径（Windows 建议直接填，免改系统 PATH） |
| `tool_interp` | 脚本型工具解释器（`sqlmap`→python、`whatweb`→ruby） |
| `wordlists` | 四类字典路径：目录/API/文档探针/参数名（内置起步字典，可换 SecLists） |
| `nuclei` | `templates` 离线模板库目录（不配置则跳过 nuclei）、速率与并发 |
| `zap` | `enabled`、地址/端口、`start_command` 自动启动命令、爬虫/扫描超时 |
| `sqlmap` / `arjun` | 启用开关与目标数上限（也可用 `--with-sqlmap`/`--with-arjun` 临时开） |
| `auth` | 认证默认值（CLI 优先；可把凭据写在这里避免出现在命令行） |
| `http` | 内置客户端超时、限速、UA、TLS 校验 |
| `discovery` | 方法枚举上限、JS 文件数上限 |
| `idor` | 越权测试开关与阈值（enabled/max_endpoints/max_probes_per_endpoint/unauth_similarity） |
| `feroxbuster_*` / `nmap_*` | 爆破线程与扩展名、nmap 端口与速率档位 |

## 报告解读

打开 `report.html`，按顺序看四处：

1. **概览**：严重度统计（critical/high/medium/low/info）+ API 端点数 + 风险评分
   + 认证状态 —— 5 秒判断目标风险水位；
2. **执行工具**：谁跑了、谁跳了 —— 判断这份结果覆盖度够不够；
3. **自动发现的 API 端点**：接口清单（方法/路径/参数/来源）—— 后续手工测试的靶子；
4. **发现明细**：按严重度排序，每条带工具、置信度、证据（原始请求/响应片段）、CWE。

**关于"线索"与"发现"**：`tool=idor` 的条目以及低置信度条目是自动化给出的**线索**，
打开证据人工复现确认后，才构成可交付的漏洞结论——这是渗透测试的正常流程。

## 目录结构

```
Chein/
├── chein.py                # 入口
├── config.json             # 全部配置（默认值齐全）
├── tools.txt               # 依赖工具与字典清单（含离线下载地址）
├── 安装清单.md             # 内网部署体检与安装清单
├── chein/
│   ├── cli.py              # 命令行入口
│   ├── orchestrator.py     # 9 阶段流水线调度（阶段内并行、降级跳过）
│   ├── auth.py             # 认证: 表单登录 / Basic / Cookie / 请求头
│   ├── idor.py             # 自动越权测试（未授权重放 + IDOR）
│   ├── models.py           # Target / Finding / Endpoint / ScanReport
│   ├── runner.py           # 命令执行器（超时/落盘/流式回显）
│   ├── http_util.py        # 内置 HTTP 客户端（Cookie jar/手动重定向）
│   ├── reporting.py        # md / html / json 报告
│   ├── dedup.py            # 去重与风险评分
│   ├── compat.py           # Windows/POSIX 平台兼容层
│   ├── adapters/           # 8 个工具适配器（统一 Adapter 接口）
│   └── api_discovery/      # 文档探针 / JS 提取 / 方法枚举 / 端点表
├── data/wordlists/         # 内置起步字典（可替换为大字典）
└── output/                 # 扫描结果（每次扫描一个时间戳目录）
```

## 离线部署

1. 在外网下载全部二进制 / 字典 / nuclei 模板 / ZAP（含预装 add-on），清单见 `tools.txt`；
2. 整个目录拷贝进内网；二进制放入 PATH，或直接写 `config.json -> tool_paths`；
3. `python chein.py --list-tools` 自检全绿后，断网跑一遍验证零外网依赖。

> 公司 EDR 可能查杀 nuclei/sqlmap 等工具的压缩包，AES 加密包 + 安全团队白名单
> 的应对方式见 `安装清单.md`。

## 安全与合规

- **仅限授权测试**。`--authorized-by` 写入报告抬头，作为授权留痕
- 所有子请求严格限定目标主机（scope 校验），越界熔断
- 默认保守速率与并发；`--aggressive` 需确认目标承受能力
- 方法枚举只发 OPTIONS/HEAD/GET；越权测试只发 GET；sqlmap/arjun 默认关闭

## 已知限制

- 复杂登录流程（验证码 / CSRF token / 多步跳转）需先浏览器登录再 `--cookie` 注入
- 垂直越权需第二个低权限账号（尚未实现）
- 动态内容（时间戳等）会导致越权测试少量漏报（相似度阈值取舍，宁漏勿滥报）
- IDOR 候选值提取基于响应体启发式，存在少量噪音线索，需人工确认
- 单 URL 定位：批量/多目标场景需重复执行（路线图待办）

## 路线图

- [x] M1: 编排骨架 + 4 基础工具 + API 探测四路通道 + 报告
- [x] M2: 认证登录（表单/Basic/Cookie/头）+ ZAP 认证上下文 + 跨平台
- [x] M3: 自动越权测试（未授权重放 + IDOR）
- [ ] M4: 垂直越权（低权限账号对比）、GraphQL 盲探测增强、OpenAPI 导出 Postman
- [ ] M5: Web 看板、任务持久化与审计库、多目标批处理