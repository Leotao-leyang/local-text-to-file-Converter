"""tests/test_core.py — 核心引擎单元测试"""

import unittest
import base64
from pathlib import Path
import tempfile
import shutil

from media_interceptor.core import MediaInterceptor
from media_interceptor.utils import is_valid_base64, safe_b64decode

class TestMediaInterceptor(unittest.TestCase):
    """MediaInterceptor 核心功能测试"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.interceptor = MediaInterceptor(out_dir=self.temp_dir)

    def tearDown(self):
        """每个测试后清理临时目录"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_png_magic(self):
        """测试 PNG 魔术数字识别"""
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(png_header)
        self.assertEqual(file_type, "PNG")
        self.assertEqual(ext, ".png")

    def test_detect_jpeg_magic(self):
        """测试 JPEG 魔术数字识别"""
        jpeg_header = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(jpeg_header)
        self.assertEqual(file_type, "JPEG")
        self.assertEqual(ext, ".jpg")

    def test_detect_pdf_magic(self):
        """测试 PDF 魔术数字识别"""
        pdf_header = b"%PDF-1.7" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(pdf_header)
        self.assertEqual(file_type, "PDF")
        self.assertEqual(ext, ".pdf")

    def test_detect_mp3_id3_magic(self):
        """测试 MP3 ID3 标签识别"""
        mp3_header = b"ID3\x03\x00" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(mp3_header)
        self.assertEqual(file_type, "MP3")
        self.assertEqual(ext, ".mp3")

    def test_detect_unknown_magic(self):
        """测试未知文件类型"""
        unknown = b"UNKNOWN_HEADER" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(unknown)
        self.assertEqual(file_type, "UNKNOWN")
        self.assertEqual(ext, ".bin")

    def test_extract_data_uri_png(self):
        """测试提取 data:URI 格式的 PNG"""
        # 创建一个最小的 PNG
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        b64_png = base64.b64encode(png_data).decode('ascii')
        text = f'Here is an image: data:image/png;base64,{b64_png}'

        result = self.interceptor.process_text(text)

        self.assertEqual(len(result.media_files), 1)
        self.assertEqual(result.media_files[0].file_type, "PNG")
        self.assertIn("[PNG 1:", result.cleaned_text)

    def test_extract_data_uri_jpeg(self):
        """测试提取 data:URI 格式的 JPEG"""
        jpeg_data = b"\xff\xd8\xff\xe0" + b"\x00" * 50
        b64_jpeg = base64.b64encode(jpeg_data).decode('ascii')
        text = f'data:image/jpeg;base64,{b64_jpeg}'

        result = self.interceptor.process_text(text)

        self.assertEqual(len(result.media_files), 1)
        self.assertEqual(result.media_files[0].file_type, "JPEG")

    def test_extract_base64_blob(self):
        """测试提取独立 Base64 块"""
        pdf_data = b"%PDF-1.7" + b"\x00" * 100
        b64_pdf = base64.b64encode(pdf_data).decode('ascii')
        text = f'Here is a PDF blob: {b64_pdf}'

        result = self.interceptor.process_text(text)

        self.assertEqual(len(result.media_files), 1)
        self.assertEqual(result.media_files[0].file_type, "PDF")
        self.assertIn("[PDF 1:", result.cleaned_text)

    def test_skip_short_base64(self):
        """测试跳过过短的 Base64 字符串"""
        text = "Short base64: YWJjZA=="  # 只有 4 字节
        result = self.interceptor.process_text(text)
        self.assertEqual(len(result.media_files), 0)

    def test_skip_text_base64(self):
        """测试跳过纯文本的 Base64 编码"""
        text_data = b"This is just plain text content for testing purposes."
        b64_text = base64.b64encode(text_data).decode('ascii')
        text = f'Base64 text: {b64_text}'

        result = self.interceptor.process_text(text)
        # 纯文本 Base64 应该被跳过
        self.assertEqual(len(result.media_files), 0)

    def test_html_entity_decoding(self):
        """测试 HTML 实体解码"""
        text = "Test &amp; &lt;tag&gt; &#60;&#62;"
        result = self.interceptor.process_text(text)
        self.assertIn("& <tag> <>", result.cleaned_text)

    def test_url_decoding(self):
        """测试 URL 百分号编码解码"""
        text = "Test%20URL%20encoding%3A%20hello%21"
        result = self.interceptor.process_text(text)
        self.assertIn("Test URL encoding: hello!", result.cleaned_text)

    def test_strip_emoji(self):
        """测试移除 Emoji"""
        text = "Hello 😀 World 🌍 Test 🎉"
        result = self.interceptor.process_text(text)
        self.assertNotIn("😀", result.cleaned_text)
        self.assertNotIn("🌍", result.cleaned_text)
        self.assertIn("Hello", result.cleaned_text)
        self.assertIn("World", result.cleaned_text)

    def test_keep_emoji(self):
        """测试保留 Emoji"""
        interceptor = MediaInterceptor(out_dir=self.temp_dir, keep_emoji=True)
        text = "Hello 😀 World"
        result = interceptor.process_text(text)
        self.assertIn("😀", result.cleaned_text)

    def test_strip_box_drawing(self):
        """测试移除框线字符"""
        text = "┌─────┐\n│ Box │\n└─────┘"
        result = self.interceptor.process_text(text)
        self.assertNotIn("┌", result.cleaned_text)
        self.assertNotIn("─", result.cleaned_text)

    def test_keep_boxes(self):
        """测试保留框线字符"""
        interceptor = MediaInterceptor(out_dir=self.temp_dir, keep_boxes=True)
        text = "┌─────┐\n│ Box │\n└─────┘"
        result = interceptor.process_text(text)
        self.assertIn("┌", result.cleaned_text)
        self.assertIn("─", result.cleaned_text)

    def test_strip_invisible_chars(self):
        """测试移除零宽字符"""
        text = "Hello\u200bWorld\u200c\u200dTest\ufeff"
        result = self.interceptor.process_text(text)
        self.assertEqual(result.cleaned_text, "HelloWorldTest")

    def test_collapse_blank_lines(self):
        """测试压缩空行"""
        text = "Line 1\n\n\n\n\nLine 2"
        result = self.interceptor.process_text(text)
        self.assertNotIn("\n\n\n", result.cleaned_text)

    def test_multiple_media_extraction(self):
        """测试提取多个媒体文件"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        jpeg_data = b"\xff\xd8\xff\xe0" + b"\x00" * 50
        pdf_data = b"%PDF-1.7" + b"\x00" * 100

        b64_png = base64.b64encode(png_data).decode('ascii')
        b64_jpeg = base64.b64encode(jpeg_data).decode('ascii')
        b64_pdf = base64.b64encode(pdf_data).decode('ascii')

        text = f'PNG: {b64_png}\nJPEG: {b64_jpeg}\nPDF: {b64_pdf}'

        result = self.interceptor.process_text(text)

        self.assertEqual(len(result.media_files), 3)
        types = {m.file_type for m in result.media_files}
        self.assertEqual(types, {"PNG", "JPEG", "PDF"})

    def test_stats_generation(self):
        """测试统计信息生成"""
        text = "Test text with some content"
        result = self.interceptor.process_text(text)

        self.assertIn("original_length", result.stats)
        self.assertIn("cleaned_length", result.stats)
        self.assertIn("media_extracted", result.stats)
        self.assertEqual(result.stats["media_extracted"], 0)

    def test_process_chunk_streaming(self):
        """测试流式处理"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        b64_png = base64.b64encode(png_data).decode('ascii')

        chunk1 = "First chunk "
        chunk2 = f"with image: {b64_png}"

        cleaned1, media1 = self.interceptor.process_chunk(chunk1)
        cleaned2, media2 = self.interceptor.process_chunk(chunk2)

        self.assertEqual(len(media1), 0)
        self.assertEqual(len(media2), 1)
        self.assertEqual(media2[0].file_type, "PNG")

class TestUtils(unittest.TestCase):
    """工具函数测试"""

    def test_is_valid_base64_valid(self):
        """测试有效的 Base64"""
        valid = base64.b64encode(b"Hello World").decode('ascii')
        self.assertTrue(is_valid_base64(valid))

    def test_is_valid_base64_invalid_chars(self):
        """测试包含非法字符的 Base64"""
        invalid = "Hello@World#"
        self.assertFalse(is_valid_base64(invalid))

    def test_is_valid_base64_too_short(self):
        """测试过短的字符串"""
        short = "abc"
        self.assertFalse(is_valid_base64(short))

    def test_safe_b64decode_valid(self):
        """测试安全解码有效 Base64"""
        data = b"Test data"
        encoded = base64.b64encode(data).decode('ascii')
        decoded = safe_b64decode(encoded)
        self.assertEqual(decoded, data)

    def test_safe_b64decode_invalid(self):
        """测试安全解码无效 Base64"""
        invalid = "Not@Valid#Base64!"
        result = safe_b64decode(invalid)
        self.assertIsNone(result)

    def test_safe_b64decode_with_whitespace(self):
        """测试解码包含空白的 Base64"""
        data = b"Test data"
        encoded = base64.b64encode(data).decode('ascii')
        with_whitespace = encoded[:10] + "\n  " + encoded[10:]
        decoded = safe_b64decode(with_whitespace)
        self.assertEqual(decoded, data)

if __name__ == "__main__":
    unittest.main()