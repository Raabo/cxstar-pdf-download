"""
文件操作工具 - 创建和删除文件夹
"""
import os
import shutil


def createFolder(folder_name: str) -> None:
    """
    创建文件夹
    
    Args:
        folder_name: 要创建的文件夹名称
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def deleteFolderAndFile(folder_path: str) -> None:
    """
    删除文件夹及其下所有文件
    
    Args:
        folder_path: 要删除的文件夹路径
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
