"""tests/test_streaming.py — 流式处理测试"""

import unittest
import base64
from media_interceptor.streaming import StreamingInterceptor

class TestStreamingInterceptor(unittest.TestCase):
    """流式处理测试"""

    def test_basic_streaming(self):
        """测试基本流式处理"""
        streamer = StreamingInterceptor(buffer_size=100)

        chunks = [
            "This is chunk 1. ",
            "This is chunk 2. ",
            "This is chunk 3. ",
        ]

        outputs = []
        for chunk in chunks:
            output, media = streamer.feed_chunk(chunk)
            if output:
                outputs.append(output)

        final_output, final_media = streamer.finalize()
        outputs.append(final_output)

        full_output = "".join(outputs)
        self.assertIn("chunk 1", full_output)
        self.assertIn("chunk 2", full_output)
        self.assertIn("chunk 3", full_output)

    def test_streaming_with_media(self):
        """测试流式处理中的媒体提取"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
        b64_png = base64.b64encode(png_data).decode('ascii')

        streamer = StreamingInterceptor(buffer_size=50)

        # 将 Base64 分成多个 chunk
        chunk_size = 100
        chunks = [b64_png[i:i+chunk_size] for i in range(0, len(b64_png), chunk_size)]

        all_media = []
        for chunk in chunks:
            output, media = streamer.feed_chunk(chunk)
            all_media.extend(media)

        final_output, final_media = streamer.finalize()
        all_media.extend(final_media)

        # 应该提取到 1 个 PNG
        self.assertEqual(len(all_media), 1)
        self.assertEqual(all_media[0].file_type, "PNG")

    def test_reset(self):
        """测试重置功能"""
        streamer = StreamingInterceptor()

        streamer.feed_chunk("Test data")
        streamer.reset()

        self.assertEqual(streamer._buffer, "")
        self.assertEqual(len(streamer._accumulated_media), 0)

if __name__ == "__main__":
    unittest.main()