"""
配置文件 - 集中管理所有常量和配置项
"""
from dataclasses import dataclass
from typing import List


# API 基础 URL
API_BASE_URL = "https://m.cxstar.com"
WEB_BASE_URL = "https://www.cxstar.com"

# API 端点
USER_INFO_ENDPOINT = f"{API_BASE_URL}/api/user"
BOOK_INFO_ENDPOINT = f"{API_BASE_URL}/api/books/{{book_id}}"
PDF_INFO_ENDPOINT = f"{WEB_BASE_URL}/api/books/{{book_id}}/pdf"
ACCESS_CHECK_ENDPOINT = f"{WEB_BASE_URL}/api/books/{{book_id}}/access"
OLD_PDF_ENDPOINT = f"{WEB_BASE_URL}/onlinebook"
CATALOG_ENDPOINT = f"{WEB_BASE_URL}/onlinebook/GetBookCatalog"
READ_RULE_ENDPOINT = f"{WEB_BASE_URL}/onlinebook/readRule"

# 加密相关
ENCRYPTION_SECRET = "123456"

# 请求头
DEFAULT_HEADERS = {
    "Referer": f"{WEB_BASE_URL}/",
}

# 重试配置
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
RETRY_BACKOFF_FACTOR = 1

# 下载配置
DEFAULT_COMPRESS_LEVEL = 2
PROGRESS_UPDATE_INTERVAL = 10  # 每下载多少页更新一次进度

# 书籍类型
BOOK_TYPE_VECTOR_PDF = 1
BOOK_TYPE_IMAGE_PDF = 2
BOOK_TYPE_EPUB = 3
BOOK_TYPE_UNKNOWN = 4

# 压缩级别
COMPRESS_NONE = 0
COMPRESS_LIGHT = 1
COMPRESS_MEDIUM = 2
COMPRESS_HIGH = 3

# 默认 User-Agent 列表
DEFAULT_USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/116.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
]

# UI 配置
UI_WINDOW_TITLE = "超星电子书下载工具"
UI_DEFAULT_WIDTH = 800
UI_DEFAULT_HEIGHT = 600
UI_MIN_WIDTH = 700
UI_MIN_HEIGHT = 500

# 配置文件
CONFIG_DIR_NAME = ".cxstar"
CONFIG_FILE_NAME = "config.json"


@dataclass
class DownloadConfig:
    """下载配置数据类"""
    compress_level: int = DEFAULT_COMPRESS_LEVEL
    max_retries: int = MAX_RETRIES
    timeout: int = REQUEST_TIMEOUT
    progress_interval: int = PROGRESS_UPDATE_INTERVAL
