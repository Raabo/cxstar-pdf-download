"""
命令行工具 - 处理书籍信息显示和退出逻辑
"""
import sys

from config import BOOK_TYPE_VECTOR_PDF, BOOK_TYPE_IMAGE_PDF, BOOK_TYPE_EPUB, BOOK_TYPE_UNKNOWN


def display_book_info(book_info: dict) -> int:
    """
    显示书籍信息并返回书籍类型
    
    Args:
        book_info: 书籍信息字典
        
    Returns:
        int: 书籍类型代码
    """
    message = f"""==================================================
书名：《{book_info["title"]}》
作者：{book_info["author"]}
大小：{book_info["fileSize"]}(官方标注大小，完全不代表下载后大小)
ISBN: {book_info["isbn"]}
出版社：{book_info["publisher"]}
出版时间：{book_info["publishDate"]}
--------------------------------------------------"""
    print(message)
    
    is_new_pdf = int(book_info.get("isNewPdf", 0))
    file_type = int(book_info.get("fileType", -1))
    
    if is_new_pdf == 1:
        print("恭喜您，这是一本矢量 pdf 书籍，即将开始下载！\n==================================================")
        return BOOK_TYPE_VECTOR_PDF
    elif file_type == 0:
        print("恭喜您，这是一本图片版 pdf 书籍，即将开始下载！\n==================================================")
        return BOOK_TYPE_IMAGE_PDF
    elif file_type == 3:
        print("很抱歉，因为能力所限，暂时无法支持 epub 格式的书籍下载。\n==================================================")
        return BOOK_TYPE_EPUB
    else:
        print("很抱歉，您发现了我们暂时还没看到的书籍格式，请联系我们进行尝试！\n==================================================")
        return BOOK_TYPE_UNKNOWN


def ask_exit() -> bool:
    """
    询问用户是否退出
    
    Returns:
        bool: True 表示退出，False 表示继续
    """
    message = """==================================================
是否选择退出？
    退出：请输入 1
    继续：请输入任意内容 | 直接回车 
=================================================="""
    print(message)
    cmd = input(">>> ").strip()
    
    if cmd == "1":
        sys.exit(0)
    return False
