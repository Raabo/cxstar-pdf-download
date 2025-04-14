from utils.command import disposeBookInfo, isExit
from utils.download import pdfDownload
from utils.network import WebInfo
from utils.userInfo import User
from utils.userAgent import userAgent
import argparse
import sys

def run_cli_mode():
    # 获取随机ua，本次下载操作中ua一致
    user_agent = userAgent()

    # 首次获取用户的authorization验证信息
    user = User()

    # 网络初始化
    web_info = WebInfo(user.authorization, user_agent)

    # 验证身份权限，并拿到用户信息
    user_info = web_info.getUserInfo()
    while user_info.status_code != 200:
        user.inputAuthorization()
        web_info.setAuthorization(user.authorization)
        user_info = web_info.getUserInfo()

    # 拿到用户信息中的schoolId并传给用户
    user.setSchoolId(user_info.json()["schoolId"])

    while True:
        # 拿到用户输入的书籍id
        user.inputBookId()
        # 验证书籍信息
        book_info = web_info.getBookInfo(user.book_id, user.school_id)
        while book_info.status_code != 200:
            user.setBookId()
            book_info = web_info.getBookInfo(user.book_id, user.school_id)

        book_info = book_info.json()
        # 打印书籍信息并获取书籍类型
        book_type = disposeBookInfo(book_info)

        if book_type == 1:
            book_data = web_info.getNewPdfInfo(user.book_id, user.school_id)
            pdfDownload(book_data, user.book_id, user_agent)
        elif book_type == 2:
            book_data = web_info.getOldPdfWebInfo(user.book_id, user.school_id)
            pdfDownload(book_data, user.book_id, user_agent)

        isExit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='超星电子书下载工具')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面模式')
    args = parser.parse_args()
    
    if args.cli:
        # 命令行模式
        run_cli_mode()
    else:
        # 图形界面模式
        try:
            from utils.ui import start_ui
            start_ui()
        except ImportError as e:
            print(f"无法启动图形界面: {e}")
            print("正在切换到命令行模式...")
            run_cli_mode()
