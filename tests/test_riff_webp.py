"""tests/test_riff_webp.py — RIFF/WEBP 二次确认逻辑测试"""

import unittest
from media_interceptor.core import MediaInterceptor

class TestRIFFWebPDetection(unittest.TestCase):
    """RIFF 容器格式二次确认测试"""

    def setUp(self):
        self.interceptor = MediaInterceptor()

    def test_detect_webp(self):
        """测试 WEBP 文件识别"""
        # RIFF header + WEBP 标记
        webp_data = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(webp_data)
        self.assertEqual(file_type, "WEBP")
        self.assertEqual(ext, ".webp")

    def test_detect_wav(self):
        """测试 WAV 文件识别"""
        # RIFF header + WAVE 标记
        wav_data = b"RIFF" + b"\x00\x00\x00\x00" + b"WAVE" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(wav_data)
        self.assertEqual(file_type, "WAV")
        self.assertEqual(ext, ".wav")

    def test_detect_avi(self):
        """测试 AVI 文件识别"""
        # RIFF header + AVI 标记
        avi_data = b"RIFF" + b"\x00\x00\x00\x00" + b"AVI " + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(avi_data)
        self.assertEqual(file_type, "AVI")
        self.assertEqual(ext, ".avi")

    def test_detect_generic_riff(self):
        """测试未知 RIFF 容器"""
        # RIFF header 但无已知子类型
        riff_data = b"RIFF" + b"\x00\x00\x00\x00" + b"UNKN" + b"\x00" * 100
        file_type, ext = self.interceptor.detect_media_type(riff_data)
        self.assertEqual(file_type, "RIFF")
        self.assertEqual(ext, ".riff")

if __name__ == "__main__":
    unittest.main()