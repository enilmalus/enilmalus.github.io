---
title: 网络安全 Skill---Enil-ling-pesing
date: 2026-08-18T10:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - Skill
  - 技术
---
> **仅限授权测试使用**：本 skill 用于内部渗透项目、SRC/众测平台、CTF、自建靶场，或书面授权的第三方资产。使用者须对目标拥有合法测试授权，并遵守当地法律与平台规则。作者不对任何滥用行为承担责任。

skill 开源地址：[enilmalus/Enil-ling-pesing](https://github.com/enilmalus/Enil-ling-pesing)

## Skill 特点

- 每阶段有 MUST 输出，未通过不得进入下一段
- 24 类漏洞 playbook
- 反幻觉硬约束
- 精心设计的提示词，用户权限高，便于使用

## 安装

```bash
git clone https://github.com/enilmalus/Enil-ling-pesing.git
ln -s "$(pwd)/Enil-ling-pesing" ~/.claude/skills/enil-ling-pesing
```

重启 Claude Code 会话后生效。Codex 与 dsh 的配置可自行研究。

## 使用

命中任一即触发：

- "渗透测试 / 红队 / 攻防演练 / 安全评估 / 漏洞挖掘 / 靶场"
- "SRC 挖洞 / 漏洞赏金 / bug bounty / 众测"
- "安全研究 / 漏洞复现 / CVE 分析"
- 直接给出目标域名 / IP / API / APP 要求测试

## 取材来源

playbook 内容改编参考（详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)）：

- [MyuriKanao/src-hunter-skill](https://github.com/MyuriKanao/src-hunter-skill)
- [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter)
- [SnailSploit/Claude-Red](https://github.com/SnailSploit/Claude-Red)
- 以及 PayloadsAllTheThings / SecLists / PortSwigger / HackTricks 等权威公开源