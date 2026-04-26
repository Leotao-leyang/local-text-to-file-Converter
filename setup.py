"""setup.py — pip 打包配置"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="media-interceptor",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI 输出多媒体被动提取工具 — 从 Grok/Claude/ChatGPT 输出中提取隐藏的 Base64 编码文件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/media-interceptor",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",  # MCP Server 支持
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "media-interceptor=media_interceptor.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)