"""
API 服务 - 处理所有网络请求
"""
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional

from config import (
    API_BASE_URL, WEB_BASE_URL, ENCRYPTION_SECRET, DEFAULT_HEADERS,
    MAX_RETRIES, REQUEST_TIMEOUT, RETRY_BACKOFF_FACTOR
)
from utils.encrypt import createVerificationData
from utils.analysis import htmlPath, jsonPath


class ApiService:
    """API 服务类，封装所有与服务器交互的逻辑"""

    def __init__(self, authorization: str, user_agent: str):
        self.authorization = authorization
        self.user_agent = user_agent
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建带有重试机制的会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @property
    def headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {self.authorization}",
            "Cookie": f"token={self.authorization}",
            "User-Agent": self.user_agent,
        }

    def set_authorization(self, token: str) -> None:
        """更新授权令牌"""
        self.authorization = token

    def get_user_info(self) -> requests.Response:
        """获取用户信息"""
        url = f"{API_BASE_URL}/api/user"
        return self.session.get(url, headers=self.headers)

    def get_book_info(self, book_id: str, school_id: str) -> requests.Response:
        """获取书籍信息"""
        url = f"{API_BASE_URL}/api/books/{book_id}?pinst={school_id}"
        return self.session.get(url, headers=self.headers)

    def get_new_pdf_info(self, book_id: str, school_id: str) -> Dict[str, Any]:
        """获取新版 PDF 信息"""
        verification = createVerificationData()
        url = f"{WEB_BASE_URL}/api/books/{book_id}/pdf"
        params = {
            "pinst": school_id,
            "nonce": verification["nonce"],
            "stime": verification["stime"],
            "sign": verification["sign"],
            "typecode": "ebook",
        }
        res = self.session.get(url, headers=self.headers, params=params)
        
        # 检查是否有完整访问权限
        if not self._check_new_pdf_access(book_id):
            print("当前用户权限所限，只能下载试看内容！")
            book_data = res.json()
            book_data["totalPage"] = book_data["trialPage"]
            return book_data
        
        return res.json()

    def _check_new_pdf_access(self, book_id: str) -> bool:
        """检查新版 PDF 访问权限"""
        verification = createVerificationData()
        url = f"{WEB_BASE_URL}/api/books/{book_id}/access"
        params = {
            "nonce": verification["nonce"],
            "stime": verification["stime"],
            "sign": verification["sign"],
            "typecode": "ebook",
        }
        res = self.session.get(url, headers=self.headers, params=params)
        if res.status_code == 200:
            return res.json().get("access", False)
        return False

    def get_old_pdf_info(self, book_id: str, school_id: str) -> Dict[str, Any]:
        """获取旧版 PDF 信息"""
        url = f"{WEB_BASE_URL}/onlinebook?ruid={book_id}&school={school_id}&typecode=ebook&pageno="
        res = self.session.get(url, headers=self.headers)
        html_content = res.text
        
        # 解析 HTML 获取书籍数据
        book_data = htmlPath(html_content)
        
        # 获取目录数据
        catalog = self._get_book_catalog(book_id)
        book_data["catalog"] = jsonPath(catalog)
        
        # 检查访问权限
        if not self._check_old_pdf_access(book_id, book_data):
            print("当前用户权限所限，只能下载试看内容！")
            book_data["totalPage"] = book_data["trialPage"]
        
        return book_data

    def _check_old_pdf_access(self, book_id: str, book_data: Dict[str, Any]) -> bool:
        """检查旧版 PDF 访问权限"""
        import random
        page_no = random.randint(int(book_data["trialPage"]), int(book_data["totalPage"]))
        url = f"{WEB_BASE_URL}/onlinebook/readRule"
        params = {
            "BookId": book_id,
            "FilePath": book_data["filePath"],
            "PageNo": page_no,
            "borrowtoken": "",
            "typecode": "ebook"
        }
        res = self.session.get(url, headers=self.headers, params=params)
        return res.json().get("code", -1) != -1

    def _get_book_catalog(self, book_id: str) -> Dict[str, Any]:
        """获取书籍目录"""
        url = f"{WEB_BASE_URL}/onlinebook/GetBookCatalog"
        params = {
            "bookruid": book_id,
            "typecode": "ebook"
        }
        res = self.session.post(url, headers=self.headers, params=params)
        return res.json()
