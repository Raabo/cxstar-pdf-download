"""
User-Agent 工具 - 提供随机 User-Agent
"""
import random

from config import DEFAULT_USER_AGENTS


def userAgent() -> str:
    """
    获取随机 User-Agent
    
    Returns:
        str: 随机选择的 User-Agent 字符串
    """
    return random.choice(DEFAULT_USER_AGENTS)
