---
title: CSRF
date: 2026-06-21T20:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
  - 技术
  - CSRF
---
## 原理

CSRF（跨站请求伪造）利用的是浏览器会自动为某个域名携带它的 Cookie 这一机制，只要登录过某网站、Cookie 还在，那么无论这个请求是从哪个页面发出的，浏览器都会把该站的 Cookie 附上，于是服务器收到请求时，光看 Cookie 没法分辨这到底是用户本人再网站上点的还是攻击者诱导发出的伪造请求。

XSS 是利用用户对网站的信任，CSRF 是利用网站对用户浏览器的信任。

例如某个银行的转账接口是 `bank.com/transfer?to=enil&amount=10000`。

那么我们可以做一个恶意页面，里面放上：

```bash
<img src="http://bank.com/transfer?to=enil&amount=10000">
```

受害者再登录银行的情况下访问了这个页面，浏览器加载这张 “图片” 的时候就向银行发了转账请求，并自动带上了银行的 Cookie，钱就转走了。

利用的三个前提是：

1. 受害者当前处于登录态（Cookie 有效）；
2. 目标接口只靠 Cookie 鉴权；
3. 请求里没有不可预测的值（比如没有 CSRF token）；
4. 攻击者能诱导受害者再登录状态下访问页面

## 防御

### CSRF Token

服务器给每个会话生成一个不可预测的 token，藏在表单里，提交时校验。

### SameSite Cookie

给 Cookie 设 `SameSite=Lax/Strict`，浏览器在跨站请求时就不带这个 Cookie 了。现代浏览器默认 `SameSite=Lax`。

### 校验 Origin / Referer 头

判断请求来源是不是本站，跨站来的拒掉。

### 敏感操作二次校验

转账、改密码这些高危操作的时候要求重新输入密码或验证码。
