"""media_interceptor/mcp_server.py — MCP Server 入口

启动方式:
    python -m media_interceptor.mcp_server
    或
    python media_interceptor/mcp_server.py

Claude Code 配置 (.claude/mcp.json):
{
    "mcpServers": {
        "media-interceptor": {
            "command": "python",
            "args": ["-m", "media_interceptor.mcp_server"]
        }
    }
}
"""

import json
import sys
import base64
import asyncio
from pathlib import Path

# MCP SDK — pip install mcp
from mcp.server import Server
from mcp.server.stdio import run_server
from mcp.types import Tool, TextContent

from .core import MediaInterceptor
from .api import process_text, detect_media

# ── 创建 MCP Server 实例 ─────────────────────────────
server = Server("media-interceptor")

# ══════════════════════════════════════════════════════
#  Tool 1: extract_media
# ══════════════════════════════════════════════════════
@server.tool()
async def extract_media(
    text: str,
    output_dir: str = "./media",
    keep_boxes: bool = False,
    keep_emoji: bool = False,
) -> str:
    """
    从 AI 输出文本中提取隐藏的 Base64 编码多媒体文件。

    功能:
    - 解码 HTML 实体、URL 编码
    - 识别并提取 data:URI 和独立 Base64 块
    - 通过魔术数字识别文件类型 (PNG/JPEG/PDF/MP3/MP4 等)
    - 清理乱码字符（零宽字符、框线、Emoji）
    - 输出干净文本 + 提取的媒体文件

    参数:
        text: 待处理的 AI 输出文本
        output_dir: 媒体文件输出目录 (默认 ./media)
        keep_boxes: 是否保留框线字符 (默认 False)
        keep_emoji: 是否保留 Emoji (默认 False)

    返回:
        JSON 格式的处理结果，包含 cleaned_text、media_files、stats
    """
    result = process_text(
        text=text,
        output_dir=output_dir,
        keep_boxes=keep_boxes,
        keep_emoji=keep_emoji,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════════════
#  Tool 2: detect_media_type
# ══════════════════════════════════════════════════════
@server.tool()
async def detect_media_type(base64_data: str) -> str:
    """
    检测 Base64 编码数据的媒体类型（通过魔术数字识别）。

    参数:
        base64_data: Base64 编码的二进制数据

    返回:
        JSON 格式: {"type": "PNG", "extension": ".png", "size_bytes": 12345}
    """
    try:
        raw = base64.b64decode(base64_data)
    except Exception as e:
        return json.dumps({"error": f"Base64 解码失败: {str(e)}"})

    info = detect_media(raw)
    info["size_bytes"] = len(raw)
    return json.dumps(info, ensure_ascii=False)

# ══════════════════════════════════════════════════════
#  Tool 3: clean_text
# ══════════════════════════════════════════════════════
@server.tool()
async def clean_text(
    text: str,
    keep_boxes: bool = False,
    keep_emoji: bool = False,
) -> str:
    """
    清理 AI 输出的乱码文本（不提取媒体，仅清理文字）。

    清理内容:
    - HTML 实体解码
    - URL 编码解码
    - 移除零宽字符和不可见控制字符
    - 移除 Unicode 框线字符 (可选保留)
    - 移除 Emoji (可选保留)
    - 压缩连续空行

    参数:
        text: 待清理的文本
        keep_boxes: 是否保留框线字符
        keep_emoji: 是否保留 Emoji

    返回:
        清理后的纯文本
    """
    from .utils import (
        decode_html_entities,
        decode_url_encoding,
        strip_invisible_chars,
        strip_box_drawing,
        strip_emoji as do_strip_emoji,
    )
    import re

    text = decode_html_entities(text)
    text = decode_url_encoding(text)
    text = strip_invisible_chars(text)
    if not keep_boxes:
        text = strip_box_drawing(text)
    if not keep_emoji:
        text = do_strip_emoji(text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

# ══════════════════════════════════════════════════════
#  Tool 4: batch_process (处理文件)
# ══════════════════════════════════════════════════════
@server.tool()
async def batch_process(
    input_path: str,
    output_path: str = "",
    media_dir: str = "./media",
) -> str:
    """
    批量处理文件：读取文本文件，提取媒体，输出清理后的文件。

    参数:
        input_path: 输入文本文件路径
        output_path: 输出文件路径 (默认: 输入文件名_clean.txt)
        media_dir: 媒体文件输出目录

    返回:
        JSON 格式的处理摘要
    """
    input_file = Path(input_path)
    if not input_file.exists():
        return json.dumps({"error": f"文件不存在: {input_path}"})

    text = input_file.read_text(encoding="utf-8", errors="replace")

    if not output_path:
        output_path = str(input_file.with_stem(input_file.stem + "_clean"))

    result = process_text(text=text, output_dir=media_dir)

    Path(output_path).write_text(result["cleaned_text"], encoding="utf-8")

    result["input_path"] = str(input_file)
    result["output_path"] = output_path
    # 不在文件处理结果中返回完整文本
    del result["cleaned_text"]

    return json.dumps(result, ensure_ascii=False, indent=2)

# ── 启动入口 ────────────────────────────────────────
async def main():
    """通过 stdio 启动 MCP Server"""
    await run_server(server)

if __name__ == "__main__":
    asyncio.run(main())