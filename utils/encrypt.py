"""
加密工具 - 生成验证数据
"""
import hashlib
import time
import uuid

from config import ENCRYPTION_SECRET


def createVerificationData() -> dict:
    """
    创建验证数据（nonce, stime, sign）
    
    Returns:
        dict: 包含 nonce, stime, sign 的字典
    """
    stime = str(round(time.time()))
    nonce = str(uuid.uuid4())
    sign = hashlib.md5((ENCRYPTION_SECRET + nonce + stime).encode()).hexdigest().upper()
    return {
        "stime": stime,
        "nonce": nonce,
        "sign": sign,
    }
