"""
用户数据模型
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    """用户信息数据类"""
    authorization: Optional[str] = None
    book_id: Optional[str] = None
    school_id: str = "null"

    def set_authorization(self, auth: str) -> None:
        """设置授权令牌，自动去除 Bearer 前缀"""
        if auth.startswith("Bearer "):
            self.authorization = auth[7:]
        else:
            self.authorization = auth

    def set_book_id(self, book_id: str) -> None:
        """设置书籍 ID"""
        self.book_id = book_id

    def set_school_id(self, school_id: str) -> None:
        """设置学校 ID"""
        self.school_id = school_id

    def is_valid_book_id(self) -> bool:
        """验证书籍 ID 格式是否正确（18 位）"""
        return self.book_id is not None and len(self.book_id) == 18
