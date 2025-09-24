# 网站图标文件说明

## 如何更换博客图标

1. 访问 [RealFaviconGenerator.net](https://realfavicongenerator.net/)
2. 上传你的图标图片（建议 512x512 像素或更高）
3. 按照网站指导调整设置
4. 下载生成的图标包
5. 将以下文件放到这个 static 文件夹中：

### 必需的图标文件：
- `favicon.ico` - 传统的网站图标
- `favicon-16x16.png` - 16x16 像素的PNG图标
- `favicon-32x32.png` - 32x32 像素的PNG图标
- `apple-touch-icon.png` - Apple设备的图标
- `android-chrome-192x192.png` - Android Chrome 192x192图标
- `android-chrome-512x512.png` - Android Chrome 512x512图标
- `mstile-150x150.png` - Windows磁贴图标
- `safari-pinned-tab.svg` - Safari固定标签图标
- `site.webmanifest` - Web应用清单文件

### 注意事项：
- 文件名必须完全匹配上述列表
- 图标会自动被Hugo识别并应用到网站
- 更新图标后需要重新构建网站：`hugo server` 或 `hugo`