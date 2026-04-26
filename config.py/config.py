"""media_interceptor/config.py — 全局配置与魔术数字映射"""

from pathlib import Path

# ── 魔术数字 → 文件扩展名映射 ──────────────────────────
MAGIC_MAP = {
    b"\x89PNG\r\n\x1a\n":       ".png",
    b"\xff\xd8\xff":             ".jpg",
    b"GIF87a":                   ".gif",
    b"GIF89a":                   ".gif",
    b"%PDF":                     ".pdf",
    b"RIFF":                     ".webp",   # 需二次确认 WEBP 标记
    b"PK\x03\x04":              ".zip",     # 也可能是 docx/xlsx/pptx
    b"\x1a\x45\xdf\xa3":        ".webm",    # 也可能是 mkv
    b"\x00\x00\x00\x18ftypmp4": ".mp4",
    b"\x00\x00\x00\x1cftypmp4": ".mp4",
    b"\x00\x00\x00\x20ftypmp4": ".mp4",
    b"ID3":                      ".mp3",
    b"\xff\xfb":                 ".mp3",
    b"\xff\xf3":                 ".mp3",
    b"OggS":                     ".ogg",
    b"fLaC":                     ".flac",
    b"\x1f\x8b":                 ".gz",
    b"BM":                       ".bmp",
    b"\x00\x00\x01\x00":        ".ico",
}

# ── MIME → 扩展名映射（用于 data:URI 解析）──────────────
MIME_EXT_MAP = {
    "image/png":       ".png",
    "image/jpeg":      ".jpg",
    "image/gif":       ".gif",
    "image/webp":      ".webp",
    "image/bmp":       ".bmp",
    "image/svg+xml":   ".svg",
    "image/x-icon":    ".ico",
    "audio/mpeg":      ".mp3",
    "audio/ogg":       ".ogg",
    "audio/flac":      ".flac",
    "audio/wav":       ".wav",
    "video/mp4":       ".mp4",
    "video/webm":      ".webm",
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/gzip":".gz",
}

# ── 默认配置 ─────────────────────────────────────────
DEFAULT_OUT_DIR = Path("./media")
MAX_BLOB_SIZE = 100 * 1024 * 1024   # 100 MB 上限
MIN_BASE64_LEN = 40                  # 最短 Base64 片段（约 30 字节原始数据）

# ── 常见标点符号集（用于文本清理）─────────────────────
COMMON_PUNCT = set(
    ' .,:;!?\'"'
    '，。；：、！？'
    '（）()[]{}<>'
    '\u201c\u201d\u2018\u2019'   # " " ' '
    '\u00b7\u2026\u2014'          # · … —
    '-_/\\|@#$%^&*+=~`'
)