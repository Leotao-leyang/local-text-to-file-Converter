"""media_interceptor/utils.py — 通用工具函数"""

import re
import html
import base64
import urllib.parse
from .config import COMMON_PUNCT

def decode_html_entities(text: str) -> str:
    """解码 HTML 实体（&amp; &#60; &#x3C; 等）"""
    return html.unescape(text)

def decode_url_encoding(text: str) -> str:
    """解码 URL 百分号编码（%20 %3D 等）"""
    try:
        return urllib.parse.unquote(text)
    except Exception:
        return text

def is_valid_base64(s: str) -> bool:
    """检查字符串是否为合法 Base64"""
    s = s.strip()
    if len(s) < 40:
        return False
    # Base64 字符集: A-Z a-z 0-9 + / = 以及可能的换行
    pattern = re.compile(r'^[A-Za-z0-9+/\n\r]+=*$')
    if not pattern.match(s):
        return False
    try:
        decoded = base64.b64decode(s, validate=True)
        return len(decoded) > 0
    except Exception:
        return False

def safe_b64decode(s: str) -> bytes | None:
    """安全地 Base64 解码，失败返回 None"""
    try:
        # 清理空白字符
        cleaned = re.sub(r'\s+', '', s)
        # 补齐 padding
        missing_padding = len(cleaned) % 4
        if missing_padding:
            cleaned += '=' * (4 - missing_padding)
        return base64.b64decode(cleaned, validate=True)
    except Exception:
        return None

def is_common_punct(ch: str) -> bool:
    """判断字符是否为常见标点"""
    return ch in COMMON_PUNCT

def strip_invisible_chars(text: str) -> str:
    """移除零宽字符和其他不可见控制字符"""
    # 零宽字符
    zero_width = re.compile(
        '[\u200b\u200c\u200d\u200e\u200f'
        '\u202a\u202b\u202c\u202d\u202e'
        '\u2060\u2061\u2062\u2063\u2064'
        '\ufeff\ufffe]'
    )
    text = zero_width.sub('', text)
    # 控制字符（保留 \n \r \t）
    text = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]').sub('', text)
    return text

def strip_box_drawing(text: str) -> str:
    """移除 Unicode 框线字符 U+2500–U+257F"""
    return re.compile(r'[\u2500-\u257f]+').sub('', text)

def strip_emoji(text: str) -> str:
    """移除 Emoji 字符"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub('', text)