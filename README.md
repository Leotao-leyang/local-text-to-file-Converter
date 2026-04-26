
# 🎯 Media Interceptor

**AI 输出多媒体被动提取工具** — 从 Grok/Claude/ChatGPT 等 AI 的输出中提取隐藏的 Base64 编码多媒体文件。

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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
```

### 方式 2: 从源码安装

```bash
git clone https://github.com/yourusername/media-interceptor.git
cd media-interceptor
pip install -e .
```

---

## 🚀 快速开始

### 1️⃣ MCP 插件模式（Claude Code）

**配置 `.claude/mcp.json`:**

```json
{
    "mcpServers": {
        "media-interceptor": {
            "command": "python",
            "args": ["-m", "media_interceptor.mcp_server"]
        }
    }
}
```

**在 Claude Code 中使用:**

```
你: 帮我提取这段 AI 输出中的图片
Claude: [自动调用 extract_media 工具]
```

---

### 2️⃣ Python API 模式

```python
from media_interceptor import process_text

text = """
这是一段包含隐藏图片的文本
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
"""

result = process_text(text, output_dir="./output")

print(result["cleaned_text"])
print(f"提取了 {result['media_count']} 个文件")
for media in result["media_files"]:
    print(f"  [{media['type']}] {media['path']}")
```

**输出示例:**

```
这是一段包含隐藏图片的文本 [PNG 1: ./output/media_01.png]
提取了 1 个文件
  [PNG] ./output/media_01.png
```

---

### 3️⃣ CLI 命令行模式

```bash
# 处理文件
media-interceptor input.txt -o clean.txt --out-dir ./media

# 处理剪贴板（Windows PowerShell）
media-interceptor

# 保留 Emoji 和框线
media-interceptor input.txt --keep-emoji --keep-boxes
```

---

## 🔧 支持的文件格式

| 类型 | 格式 | 魔术数字识别 |
|------|------|-------------|
| **图片** | PNG, JPEG, GIF, WebP, BMP, ICO | ✅ |
| **文档** | PDF | ✅ |
| **音频** | MP3, OGG, FLAC, WAV | ✅ |
| **视频** | MP4, WebM | ✅ |
| **压缩** | ZIP, GZ | ✅ |

---

## 🧪 运行测试

```bash
# 安装测试依赖
pip install -e ".[dev]"

# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=media_interceptor --cov-report=html
```

---

## 📚 API 文档

### `process_text(text, output_dir="./media", keep_boxes=False, keep_emoji=False)`

处理一段文本，提取媒体并清理文字。

**参数:**
- `text` (str): 待处理的文本
- `output_dir` (str): 媒体文件输出目录
- `keep_boxes` (bool): 是否保留框线字符
- `keep_emoji` (bool): 是否保留 Emoji

**返回:**

```python
{
    "cleaned_text": "干净的文本...",
    "media_count": 2,
    "media_files": [
        {
            "index": 1,
            "type": "PNG",
            "path": "./media/media_01.png",
            "size": 12345,
            "source": "data_uri"
        }
    ],
    "stats": {
        "original_length": 5000,
        "cleaned_length": 1000,
        "media_extracted": 2,
        "total_media_bytes": 25000
    }
}
```

### `detect_media(data: bytes)`

检测二进制数据的媒体类型。

**返回:**

```python
{"type": "PNG", "extension": ".png"}
```

### `create_interceptor(**kwargs)`

创建 `MediaInterceptor` 实例（高级用法）。

---

## 🔄 流式处理示例

```python
from media_interceptor.streaming import StreamingInterceptor

streamer = StreamingInterceptor(buffer_size=4096)

for chunk in ai_output_stream:
    cleaned, media = streamer.feed_chunk(chunk)
    if cleaned:
        print(cleaned, end="", flush=True)
    for m in media:
        print(f"\n[提取] {m.file_type} → {m.file_path}")

# 处理完毕
final_text, final_media = streamer.finalize()
print(final_text)
```

---

## 🛠️ 项目结构

```
media_interceptor/
├── __init__.py          # 包入口
├── core.py              # 核心引擎
├── api.py               # Python API
├── mcp_server.py        # MCP Server
├── streaming.py         # 流式处理
├── config.py            # 配置常量
└── utils.py             # 工具函数

tests/
├── test_core.py         # 核心测试
├── test_riff_webp.py    # RIFF 格式测试
└── test_streaming.py    # 流式处理测试
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 灵感来源：处理 Grok AI 输出的乱码问题
- MCP 协议：[Model Context Protocol](https://modelcontextprotocol.io/)
- Claude Code：[Anthropic Claude](https://www.anthropic.com/)

---

## 📧 联系方式

- **作者**: Leo Tao
- **邮箱**: geniusleotao@outlook.com
- **GitHub**: [@Leotao-leyang]((https://github.com/Leotao-leyang))

---

**Made with ❤️ for the AI community**
