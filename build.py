import PyInstaller.__main__
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义打包选项
options = [
    '--name=超星电子书下载工具',  # 程序名称
    '--onefile',  # 打包成单个文件
    '--windowed',  # 使用窗口模式（不显示控制台）
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不询问确认
    # 移除图标选项，除非您有图标文件
    
    # 排除不需要的模块以减小体积
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=scipy',
    '--exclude-module=PyQt5',
    '--exclude-module=PySide2',
    '--exclude-module=IPython',
    '--exclude-module=notebook',
    '--exclude-module=sphinx',
    '--exclude-module=pytest',
    '--exclude-module=PIL.ImageQt',
    '--exclude-module=PIL.ImageTk',
    '--exclude-module=PIL.ImageGrab',
    '--exclude-module=PIL.ImageDraw2',
    '--exclude-module=PIL.ImageCms',
    '--exclude-module=PIL.ImageMath',
    '--exclude-module=PIL.ImageGL',
    '--exclude-module=PIL.ImageColor',
    '--exclude-module=PIL.ImageFilter',
    '--exclude-module=PIL.ImageEnhance',
    '--exclude-module=PIL.ImageOps',
    '--exclude-module=PIL.ImageWin',
    '--exclude-module=PIL.ImagePath',
    '--exclude-module=PIL.ImageShow',
    '--exclude-module=PIL.ImageMorph',
    '--exclude-module=PIL.ImageChops',
    '--exclude-module=PIL.ImageTransform',
    '--exclude-module=PIL.ImageStat',
    '--exclude-module=PIL.ImageSequence',
    
    '--collect-submodules=requests',
    '--collect-submodules=pypdf',
    
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    
    # 优化选项
    '--noupx',  # 不使用UPX压缩（有时会导致问题）
    # 移除strip选项，因为Windows上不可用
    
    # 主程序文件
    os.path.join(current_dir, 'main.py'),
]

# 运行PyInstaller
PyInstaller.__main__.run(options)

print("打包完成！")