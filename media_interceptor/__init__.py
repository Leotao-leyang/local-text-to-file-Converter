"""media_interceptor — AI 输出多媒体被动提取工具包"""

from .core import MediaInterceptor, ProcessResult, ExtractedMedia
from .api import process_text, detect_media, create_interceptor

__version__ = "0.1.0"
__all__ = [
    "MediaInterceptor",
    "ProcessResult",
    "ExtractedMedia",
    "process_text",
    "detect_media",
    "create_interceptor",
]