# 多进程钩子文件
import os
import sys
import multiprocessing

# 确保多进程在冻结环境中正常工作
if hasattr(sys, 'frozen'):
    multiprocessing.freeze_support()
    
    # 设置多进程启动方法为 'spawn'
    if sys.platform.startswith('win'):
        multiprocessing.set_start_method('spawn')