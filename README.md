# 🎯 Media Interceptor

**AI 输出多媒体被动提取工具** — 从 Grok/Claude/ChatGPT 等 AI 的输出中提取隐藏的 Base64 编码多媒体文件。

---

## ✨ 特性

- 🔍 **智能识别** — 通过魔术数字识别 PNG/JPEG/PDF/MP3/MP4/GIF/WebP 等 20+ 种格式
- 🧹 **文本清理** — 移除零宽字符、框线、Emoji、HTML 实体、URL 编码
- 📦 **三种模式** — MCP 插件 / Python API / CLI 命令行
- 🔄 **流式处理** — 支持 streaming 输出场景（实时提取）
- 🎨 **占位标记** — 自动生成 `[PNG 1: ./media/media_01.png]` 格式标记

---

## 📦 安装

### 方式 1: pip 安装（推荐）

```bash
pip install media-interceptor
