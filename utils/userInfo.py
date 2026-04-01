"""
用户交互服务 - 处理用户输入和输出
"""
import sys
from typing import Optional

from models.user import User


class UserInteractionService:
    """用户交互服务类，处理所有与用户的交互"""

    def __init__(self):
        self.user = User()

    def input_authorization(self, prompt: str = "请输入代表您身份信息的 Authorization:") -> str:
        """
        获取用户输入的 Authorization
        
        Args:
            prompt: 提示消息
            
        Returns:
            str: 清理后的 authorization 字符串
        """
        print("=" * 50)
        print(prompt)
        auth = input(">>> ").strip()
        
        # 去除 Bearer 前缀
        if auth.startswith("Bearer "):
            auth = auth[7:]
        
        return auth

    def input_book_id(self, prompt: str = "请您输入要下载的书籍 ID:（例如：218c9e1a0013f2XXXX）") -> str:
        """
        获取用户输入的书籍 ID，并验证格式
        
        Args:
            prompt: 提示消息
            
        Returns:
            str: 有效的书籍 ID（18 位）
        """
        print("=" * 50)
        print(prompt)
        
        while True:
            book_id = input(">>> ").strip()
            
            if len(book_id) == 18:
                return book_id
            
            print("书籍 ID 长度错误，请重新输入（应为 18 位）:")

    def ask_exit(self) -> bool:
        """
        询问用户是否退出
        
        Returns:
            bool: True 表示退出，False 表示继续
        """
        print("=" * 50)
        print("是否选择退出？")
        print("    退出：请输入 1")
        print("    继续：请输入任意内容 | 直接回车")
        print("=" * 50)
        
        cmd = input(">>> ").strip()
        return cmd == "1"

    def initialize_user(self) -> User:
        """
        初始化用户信息，获取 Authorization
        
        Returns:
            User: 初始化后的用户对象
        """
        auth = self.input_authorization()
        self.user.set_authorization(auth)
        return self.user

    def reinput_authorization(self) -> str:
        """
        重新获取 Authorization（验证失败时调用）
        
        Returns:
            str: 清理后的 authorization 字符串
        """
        auth = self.input_authorization("身份验证失败，请您重新输入您的 Authorization:")
        self.user.set_authorization(auth)
        return auth

    def reinput_book_id(self) -> str:
        """
        重新获取书籍 ID（验证失败时调用）
        
        Returns:
            str: 有效的书籍 ID（18 位）
        """
        book_id = self.input_book_id("书籍 ID 经网络验证，确认书籍不存在，请重新输入:")
        self.user.set_book_id(book_id)
        return book_id
