"""
主程序入口 - 超星电子书下载工具
"""
import argparse
import sys
from typing import Optional

from config import DEFAULT_COMPRESS_LEVEL
from models.user import User
from services.api_service import ApiService
from utils.userAgent import userAgent
from utils.userInfo import UserInteractionService
from utils.command import display_book_info, ask_exit
from utils.download import download_pdf


def run_cli_mode() -> None:
    """运行命令行界面模式"""
    # 获取随机 UA，本次下载操作中 UA 一致
    user_agent = userAgent()
    
    # 初始化用户交互服务
    interaction_service = UserInteractionService()
    
    # 获取用户 Authorization
    interaction_service.initialize_user()
    
    # 初始化 API 服务
    api_service = ApiService(interaction_service.user.authorization, user_agent)
    
    # 验证身份并获取用户信息
    user_info_response = api_service.get_user_info()
    while user_info_response.status_code != 200:
        interaction_service.reinput_authorization()
        api_service.set_authorization(interaction_service.user.authorization)
        user_info_response = api_service.get_user_info()
    
    # 设置学校 ID
    interaction_service.user.set_school_id(user_info_response.json()["schoolId"])
    
    # 主循环
    while True:
        # 获取书籍 ID
        interaction_service.input_book_id()
        
        # 验证书籍信息
        book_info_response = api_service.get_book_info(
            interaction_service.user.book_id,
            interaction_service.user.school_id
        )
        
        while book_info_response.status_code != 200:
            interaction_service.reinput_book_id()
            book_info_response = api_service.get_book_info(
                interaction_service.user.book_id,
                interaction_service.user.school_id
            )
        
        book_info = book_info_response.json()
        
        # 显示书籍信息并获取类型
        book_type = display_book_info(book_info)
        
        # 根据书籍类型下载
        if book_type == 1:  # 矢量 PDF
            book_data = api_service.get_new_pdf_info(
                interaction_service.user.book_id,
                interaction_service.user.school_id
            )
            download_pdf(book_data, interaction_service.user.book_id, user_agent)
        elif book_type == 2:  # 图片 PDF
            book_data = api_service.get_old_pdf_info(
                interaction_service.user.book_id,
                interaction_service.user.school_id
            )
            download_pdf(book_data, interaction_service.user.book_id, user_agent)
        
        # 询问是否退出
        if ask_exit():
            break


def run_gui_mode() -> None:
    """运行图形界面模式"""
    try:
        from utils.ui import start_ui
        start_ui()
    except ImportError as e:
        print(f"无法启动图形界面：{e}")
        print("正在切换到命令行模式...")
        run_cli_mode()


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='超星电子书下载工具')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面模式')
    args = parser.parse_args()
    
    if args.cli:
        run_cli_mode()
    else:
        run_gui_mode()


if __name__ == '__main__':
    main()
