---
title: 公私钥
date: 2026-01-01T17:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## 关于 id_rsa

访问 `http://facts.htb/admin/media/download_private_file?file=../../../../../../home/trivia/id_ed25519` 尝试下载他们的 `id_rsa` 文件

```id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABDPFoJGv5
iCd2KL8Mk98VRJAAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIIJhikYx00CYMUNJ
bkfs15NSAgTKVW07Aw2N4nxQ/RZ6AAAAoAj0NoVnW97AXPxNpphTUEKgehTfW3KWvX/9ps
AvdkbwNKeW1F/CkRpsFkmcc1/cvTrzBueLfuJI/2Cm8RB55xHgkJNtkk9Fc3HLRF8Z/kZC
Mn8NP3Z2qOuHzSO5yoqU2mFiFBouc56nWkR50JElA2z0L65KU81xDPB3YVujEf/yxbvoxJ
ElX+bGho7xDsCOubcJxarL+rGEZ5DQTxpAjGk=
-----END OPENSSH PRIVATE KEY-----
```

值得注意的是，下载 `id_rsa` 是失败的，需要下载 `id_ed25519`；`id_ed25519` 是现代 SSH 推荐的 `Ed25519` 算法私钥文件。

## ssh2john 提取私钥

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ ssh2john id_rsa | tee key_hash
```

SSH 私钥文件本身采用专门的格式储存，其中包含了加密的参数消息、加密算法以及密文数据，而不是直接的密码哈希字符串，私钥加密时会采用密钥派生函数（如 PBKDF2 或 bcrypt ）来对口令生成对称密钥，然后用该密钥对私钥数据进行加密，使得文件内容看起来像是一段难以辨别的编码数据。John 是一个专门用于破解密码哈希的工具，他需要知道加密算法的具体参数（例如加密方式、迭代次数、盐值等），才能通过暴力破解或者字典攻击验证猜测的口令是否正确。ssh2john 就是用来解析 SSH 私钥文件，提取出其中的加密参数和密文数据，构造出一个标准化的哈希格式，这种格式正式 John 能够识别并处理的。只有经过这种转换，John 才能根据已知的加密参数对猜测的口令进行验证，否则直接对原始密钥文件进行暴力破解是不现实的，因为文件格式本身并不直接暴露口令的哈希。

John 设计的初衷在于专注于高效破解，而不是兼顾解析和转换各种格式文件。各种密钥文件和加密数据都有自己独特的储存格式、加密参数和版本演变，内置所有解析逻辑会使得核心代码变得臃肿，增加维护难度和安全风险，同时也会分散团队在算法优化和并行处理上的精力。事实上，文件格式转换本身是一项非常复杂且不断演进的工作，许多转换工具最初由社区不同专家针对各自领域开发出来，这种分工使得每个工具都可以专注于特定格式的深度解析和不断更新，而 John 的核心开发者可以集中精力提升密码破解的速度和准确性。再者，不同格式的解析逻辑通常需要对各种加密协议和密钥派生函数有精确而细致的处理，若将这些所有细节内知道主程序中，不仅会增加软件整体的复杂度，还会使得未来支持新格式的工作变得更为繁琐和风险巨大。通过采用独立的 ssh2john 攻击，整个破解流程得以模块化：用户首先通过专门的转换工具提取破解所需的关键信息，再交由 John 进行针对性暴力破解或字典攻击，这样的架构既提高了灵活性，也确保了每个环节都能在各自领域达到最佳效果。

## John 破解提取的私钥

```bash
┌──(kali㉿kali)-[~/Work/Kali]
└─$ john key_hash
```

John the Ripper 默认会按照一套预设的攻击策略以此尝试不同的破解模式。当不指定特定模式时，John 首先启动单一模式（Single crack mode），利用哈希文件中的信息（例如用户名、文件名等）生成候选密码并进行尝试；这就是输出模式中显示 “Proceeding with single,rule:Single” 所表达的含义。单一模式通常能在很短的时间内尝试一些最可能的密码组合，当 John 发现还有缓冲的候选密码没有处理完时，它会尽快完成这部分工作。接下来，John 会自动进入下一阶段，也就是使用默认字典进行攻击。如果前面两种都没有破解成功，John 就会启动最全面但是效率较低的增量模式（Incrementak mode），即基于 ASCII 字符的穷举攻击。整个流程的设计逻辑在于先用最后可能的密码组合进行快速尝试，再逐步扩大候选密码空间，再有限的时间内尽可能高效地覆盖大部分实际使用的密码组合。