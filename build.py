import PyInstaller.__main__
import os
import sys
import shutil

# 设置标准输出编码为 UTF-8，避免 Windows 控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 清理之前的打包文件
dist_dir = os.path.join(current_dir, 'dist')
build_dir = os.path.join(current_dir, 'build')
spec_file = os.path.join(current_dir, '超星电子书下载工具.spec')

try:
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    print("已清理之前的打包文件")
except Exception as e:
    print(f"清理文件时出错: {str(e)}")

# 定义打包选项
options = [
    '--name=超星电子书下载工具',  # 程序名称
    '--onefile',  # 打包成单个文件
    '--windowed',  # 使用窗口模式（不显示控制台）
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不询问确认
    
    # 添加多进程支持
    '--runtime-hook=mp_hook.py',  # 添加运行时钩子
    
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
    '--hidden-import=io',  # 添加io模块
    '--hidden-import=os',  # 添加os模块
    '--hidden-import=sys',  # 添加sys模块
    '--hidden-import=tempfile',  # 添加tempfile模块
    '--hidden-import=multiprocessing',  # 添加multiprocessing模块
    '--hidden-import=multiprocessing.pool',  # 添加multiprocessing.pool模块
    '--hidden-import=multiprocessing.connection',  # 添加multiprocessing.connection模块
    '--hidden-import=multiprocessing.queues',  # 添加multiprocessing.queues模块
    '--hidden-import=multiprocessing.synchronize',  # 添加multiprocessing.synchronize模块
    
    # 添加数据文件收集
    '--collect-data=requests',
    '--collect-data=pypdf',
    
    # 移除调试信息
    # '--debug=all',  # 在打包时生成详细的调试信息
    
    # 优化选项
    '--noupx',  # 不使用UPX压缩（有时会导致问题）
    # 移除strip选项，因为Windows上不可用
    
    # 主程序文件
    os.path.join(current_dir, 'main.py'),
]

# 运行PyInstaller
PyInstaller.__main__.run(options)

print("打包完成！")