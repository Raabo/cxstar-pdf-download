"""
书籍数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import IntEnum


class BookType(IntEnum):
    """书籍类型枚举"""
    VECTOR_PDF = 1      # 矢量 PDF
    IMAGE_PDF = 2       # 图片 PDF
    EPUB = 3           # EPUB 格式
    UNKNOWN = 4        # 未知格式


@dataclass
class BookInfo:
    """书籍信息数据类"""
    title: str
    author: str
    file_size: str
    isbn: str
    publisher: str
    publish_date: str
    is_new_pdf: bool
    file_type: int
    book_type: BookType
    total_page: int = 0
    trial_page: int = 0
    file_path: str = ""
    web_path: str = ""
    catalog: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "BookInfo":
        """从 API 响应创建书籍信息"""
        is_new_pdf = int(data.get("isNewPdf", 0)) == 1
        file_type = int(data.get("fileType", -1))

        # 判断书籍类型
        if is_new_pdf:
            book_type = BookType.VECTOR_PDF
        elif file_type == 0:
            book_type = BookType.IMAGE_PDF
        elif file_type == 3:
            book_type = BookType.EPUB
        else:
            book_type = BookType.UNKNOWN

        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            file_size=data.get("fileSize", ""),
            isbn=data.get("isbn", ""),
            publisher=data.get("publisher", ""),
            publish_date=data.get("publishDate", ""),
            is_new_pdf=is_new_pdf,
            file_type=file_type,
            book_type=book_type,
        )

    def can_download(self) -> bool:
        """判断是否可以下载"""
        return self.book_type in (BookType.VECTOR_PDF, BookType.IMAGE_PDF)

    def get_type_message(self) -> str:
        """获取书籍类型消息"""
        messages = {
            BookType.VECTOR_PDF: "矢量 PDF 书籍，即将开始下载！",
            BookType.IMAGE_PDF: "图片版 PDF 书籍，即将开始下载！",
            BookType.EPUB: "暂时无法支持 epub 格式的书籍下载。",
            BookType.UNKNOWN: "暂时还不支持的书籍格式。",
        }
        return messages.get(self.book_type, "未知书籍格式。")
