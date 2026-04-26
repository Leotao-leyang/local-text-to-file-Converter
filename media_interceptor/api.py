"""media_interceptor/api.py — 对外 Python API"""

from pathlib import Path
from .core import MediaInterceptor, ProcessResult

def process_text(
    text: str,
    output_dir: str = "./media",
    keep_boxes: bool = False,
    keep_emoji: bool = False,
) -> dict:
    """
    一站式 API：传入文本，返回处理结果字典。

    返回格式:
    {
        "cleaned_text": "干净文本...",
        "media_count": 2,
        "media_files": [
            {"index": 1, "type": "PNG", "path": "./media/media_01.png", "size": 12345, "source": "data_uri"},
            ...
        ],
        "stats": {"original_length": ..., "cleaned_length": ..., ...}
    }
    """
    interceptor = MediaInterceptor(out_dir=output_dir, keep_boxes=keep_boxes, keep_emoji=keep_emoji)
    result = interceptor.process_text(text)
    return result.to_dict()

def detect_media(data: bytes) -> dict:
    """
    检测二进制数据的媒体类型。
    返回 {"type": "PNG", "extension": ".png"}
    """
    interceptor = MediaInterceptor()
    file_type, ext = interceptor.detect_media_type(data)
    return {"type": file_type, "extension": ext}

def create_interceptor(**kwargs) -> MediaInterceptor:
    """
    创建一个 MediaInterceptor 实例，用于流式处理等高级场景。
    """
    return MediaInterceptor(**kwargs)