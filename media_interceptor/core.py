"""media_interceptor/core.py — 核心解码/识别引擎"""

import re
from pathlib import Path
from dataclasses import dataclass, field

from .config import MAGIC_MAP, MIME_EXT_MAP, RIFF_SUBTYPES, DEFAULT_OUT_DIR, MIN_BASE64_LEN, MAX_BLOB_SIZE
from .utils import (
    decode_html_entities,
    decode_url_encoding,
    safe_b64decode,
    strip_invisible_chars,
    strip_box_drawing,
    strip_emoji,
)

@dataclass
class ExtractedMedia:
    """提取出的媒体文件描述"""
    index: int
    file_type: str          # "PNG", "JPEG", "PDF" 等
    extension: str          # ".png", ".jpg" 等
    file_path: str          # 保存路径
    size_bytes: int         # 文件大小
    source_hint: str = ""   # 来源提示: "base64_blob", "data_uri" 等

@dataclass
class ProcessResult:
    """处理结果"""
    cleaned_text: str = ""
    media_files: list[ExtractedMedia] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "cleaned_text": self.cleaned_text,
            "media_count": len(self.media_files),
            "media_files": [
                {
                    "index": m.index,
                    "type": m.file_type,
                    "path": m.file_path,
                    "size": m.size_bytes,
                    "source": m.source_hint,
                }
                for m in self.media_files
            ],
            "stats": self.stats,
        }

class MediaInterceptor:
    """核心媒体拦截/提取引擎"""

    # ── data:URI 正则 ──────────────────────────────────
    DATA_URI_RE = re.compile(
        r'data:([a-zA-Z0-9]+/[a-zA-Z0-9.+_-]+);base64,([A-Za-z0-9+/\s]+=*)',
        re.DOTALL,
    )

    # ── 独立 Base64 块正则（至少 MIN_BASE64_LEN 字符）──
    BASE64_BLOB_RE = re.compile(
        r'(?<![A-Za-z0-9+/])([A-Za-z0-9+/]{' + str(MIN_BASE64_LEN) + r',}={0,3})(?![A-Za-z0-9+/=])',
    )

    def __init__(
        self,
        out_dir: str | Path = DEFAULT_OUT_DIR,
        keep_boxes: bool = False,
        keep_emoji: bool = False,
        prefix: str = "media",
    ):
        self.out_dir = Path(out_dir)
        self.keep_boxes = keep_boxes
        self.keep_emoji = keep_emoji
        self.prefix = prefix
        self._media_counter = 0
        self._extracted: list[ExtractedMedia] = []

    # ── 公开 API ────────────────────────────────────────
    def process_text(self, text: str) -> ProcessResult:
        """
        主入口：处理一段文本，提取媒体并清理文字。
        返回 ProcessResult（包含干净文本 + 媒体文件列表）。
        """
        original_len = len(text)
        self._media_counter = 0
        self._extracted = []

        # Step 1: 预解码
        text = decode_html_entities(text)
        text = decode_url_encoding(text)

        # Step 2: 提取 data:URI
        text = self._extract_data_uris(text)

        # Step 3: 提取独立 Base64 块
        text = self._extract_base64_blobs(text)

        # Step 4: 文本清理
        text = strip_invisible_chars(text)
        if not self.keep_boxes:
            text = strip_box_drawing(text)
        if not self.keep_emoji:
            text = strip_emoji(text)

        # Step 5: 整理空行
        text = self._collapse_blank_lines(text)

        result = ProcessResult(
            cleaned_text=text.strip(),
            media_files=self._extracted,
            stats={
                "original_length": original_len,
                "cleaned_length": len(text.strip()),
                "media_extracted": len(self._extracted),
                "total_media_bytes": sum(m.size_bytes for m in self._extracted),
            },
        )
        return result

    def process_chunk(self, chunk: str) -> tuple[str, list[ExtractedMedia]]:
        """
        流式处理：处理一个文本块，返回 (清理后文本, 新提取的媒体列表)。
        适用于 streaming 场景。
        """
        before_count = len(self._extracted)

        chunk = decode_html_entities(chunk)
        chunk = decode_url_encoding(chunk)
        chunk = self._extract_data_uris(chunk)
        chunk = self._extract_base64_blobs(chunk)
        chunk = strip_invisible_chars(chunk)
        if not self.keep_boxes:
            chunk = strip_box_drawing(chunk)
        if not self.keep_emoji:
            chunk = strip_emoji(chunk)

        new_media = self._extracted[before_count:]
        return chunk, new_media

    def detect_media_type(self, data: bytes) -> tuple[str, str]:
        """
        根据魔术数字检测媒体类型。
        返回 (类型名, 扩展名)，未识别返回 ("UNKNOWN", ".bin")。
        """
        # ── RIFF 容器需要二次确认 ──────────────────────────
        if data[:4] == b"RIFF" and len(data) >= 12:
            subtype = data[8:12]
            if subtype in RIFF_SUBTYPES:
                ext = RIFF_SUBTYPES[subtype]
                type_name = ext.lstrip('.').upper()
                return type_name, ext
            # 未知 RIFF 子类型
            return "RIFF", ".riff"

        # ── 常规魔术数字匹配 ──────────────────────────────
        for magic, ext in MAGIC_MAP.items():
            if data[:len(magic)] == magic:
                type_name = ext.lstrip('.').upper()
                if type_name == "JPG":
                    type_name = "JPEG"
                return type_name, ext

        return "UNKNOWN", ".bin"

    # ── 内部方法 ────────────────────────────────────────
    def _next_filename(self, ext: str) -> Path:
        """生成下一个媒体文件名"""
        self._media_counter += 1
        self.out_dir.mkdir(parents=True, exist_ok=True)
        return self.out_dir / f"{self.prefix}_{self._media_counter:02d}{ext}"

    def _save_blob(self, data: bytes, source_hint: str, ext_override: str = "") -> str | None:
        """保存二进制数据为文件，返回占位标记文本"""
        if len(data) > MAX_BLOB_SIZE:
            return None

        file_type, ext = self.detect_media_type(data)
        if ext_override:
            ext = ext_override

        filepath = self._next_filename(ext)
        filepath.write_bytes(data)

        media = ExtractedMedia(
            index=self._media_counter,
            file_type=file_type,
            extension=ext,
            file_path=str(filepath),
            size_bytes=len(data),
            source_hint=source_hint,
        )
        self._extracted.append(media)

        # 返回占位标记
        return f"[{file_type} {self._media_counter}: {filepath}]"

    def _extract_data_uris(self, text: str) -> str:
        """提取并替换 data:URI"""
        def replacer(match):
            mime_type = match.group(1).lower()
            b64_data = match.group(2)
            raw = safe_b64decode(b64_data)
            if raw is None:
                return match.group(0)

            ext = MIME_EXT_MAP.get(mime_type, "")
            placeholder = self._save_blob(raw, "data_uri", ext_override=ext)
            return placeholder if placeholder else match.group(0)

        return self.DATA_URI_RE.sub(replacer, text)

    def _extract_base64_blobs(self, text: str) -> str:
        """提取独立的 Base64 编码块"""
        def replacer(match):
            b64_str = match.group(1)
            raw = safe_b64decode(b64_str)
            if raw is None:
                return match.group(0)

            # 检查是否能识别为已知媒体类型
            file_type, _ = self.detect_media_type(raw)
            if file_type == "UNKNOWN":
                # 如果无法识别，且看起来像纯文本，跳过
                try:
                    raw.decode('utf-8')
                    # 纯文本 Base64 不提取，保留原样
                    if len(raw) < 200:
                        return match.group(0)
                except UnicodeDecodeError:
                    pass  # 二进制数据，继续提取

            placeholder = self._save_blob(raw, "base64_blob")
            return placeholder if placeholder else match.group(0)

        return self.BASE64_BLOB_RE.sub(replacer, text)

    @staticmethod
    def _collapse_blank_lines(text: str) -> str:
        """将连续空行压缩为最多两个"""
        return re.sub(r'\n{3,}', '\n\n', text)