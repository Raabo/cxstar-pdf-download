"""
现代化图形用户界面模块 - 提供符合现代审美的 Tkinter GUI 支持
采用扁平化设计、渐变色彩和流畅动画效果
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import json
from io import StringIO
from typing import Optional, Callable, Dict, Any
import webbrowser

from config import (
    UI_WINDOW_TITLE, UI_DEFAULT_WIDTH, UI_DEFAULT_HEIGHT,
    UI_MIN_WIDTH, UI_MIN_HEIGHT, CONFIG_DIR_NAME, CONFIG_FILE_NAME
)


# ============================================================================
# 现代配色方案
# ============================================================================
class ModernColors:
    """现代配色方案定义"""
    # 主色调 - 渐变蓝紫色系
    PRIMARY = "#6366f1"
    PRIMARY_DARK = "#4f46e5"
    PRIMARY_LIGHT = "#818cf8"
    
    # 辅助色
    SECONDARY = "#ec4899"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#3b82f6"
    
    # 中性色
    BACKGROUND = "#f8fafc"
    SURFACE = "#ffffff"
    CARD_BG = "#ffffff"
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    TEXT_MUTED = "#94a3b8"
    BORDER = "#e2e8f0"
    
    # 渐变配置
    GRADIENT_START = "#6366f1"
    GRADIENT_END = "#8b5cf6"


# ============================================================================
# 自定义样式组件
# ============================================================================
class ModernButton(tk.Canvas):
    """现代化按钮组件 - 支持悬停效果和点击动画"""
    
    def __init__(self, parent, text: str, command: Callable, 
                 width: int = 120, height: int = 40, 
                 bg_color: str = ModernColors.PRIMARY,
                 fg_color: str = "#ffffff",
                 hover_color: str = ModernColors.PRIMARY_DARK,
                 **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.is_hovered = False
        self.is_pressed = False
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self._draw()
    
    def _draw(self):
        """绘制按钮"""
        self.delete("all")
        
        # 确定当前颜色
        if self.is_pressed:
            color = self.hover_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.bg_color
        
        # 绘制圆角矩形背景
        radius = 8
        width = int(self['width'])
        height = int(self['height'])
        
        self.create_rounded_rect(2, 2, width-2, height-2, radius, 
                                fill=color, outline="")
        
        # 绘制文字
        self.create_text(width//2, height//2, text=self.text, 
                        fill=self.fg_color, font=("Segoe UI", 10, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """绘制圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self.is_hovered = True
        self._draw()
    
    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw()
    
    def _on_press(self, event):
        self.is_pressed = True
        self._draw()
    
    def _on_release(self, event):
        self.is_pressed = False
        self._draw()
        if self.command:
            self.command()


class ModernEntry(ttk.Entry):
    """现代化输入框组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 配置样式
        self.configure(
            font=("Segoe UI", 11),
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=ModernColors.PRIMARY,
            highlightbackground=ModernColors.BORDER,
            bg="#ffffff",
            fg=ModernColors.TEXT_PRIMARY,
            insertbackground=ModernColors.PRIMARY,
            selectbackground=ModernColors.PRIMARY_LIGHT,
            selectforeground="#ffffff"
        )


class ModernCard(ttk.Frame):
    """现代化卡片容器"""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(padding=15)
        
        # 卡片背景
        self.card_frame = ttk.Frame(self)
        self.card_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加阴影效果（通过边框模拟）
        self.card_frame.configure(
            padding=1
        )
        
        # 内容区域
        self.content_frame = ttk.Frame(self.card_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        if title:
            self.title_label = ttk.Label(
                self.content_frame, 
                text=title,
                font=("Segoe UI", 12, "bold"),
                foreground=ModernColors.TEXT_PRIMARY
            )
            self.title_label.pack(anchor=tk.W, pady=(0, 10))


class RedirectText:
    """重定向标准输出到文本控件 - 支持语法高亮"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = StringIO()
        self.original_stdout = sys.stdout
        
        # 配置标签
        self._configure_tags()
    
    def _configure_tags(self):
        """配置文本标签"""
        self.text_widget.tag_configure("info", foreground=ModernColors.INFO)
        self.text_widget.tag_configure("success", foreground=ModernColors.SUCCESS)
        self.text_widget.tag_configure("warning", foreground=ModernColors.WARNING)
        self.text_widget.tag_configure("error", foreground=ModernColors.ERROR)
        self.text_widget.tag_configure("default", foreground=ModernColors.TEXT_SECONDARY)
    
    def write(self, string):
        try:
            self.buffer.write(string)
            self.text_widget.configure(state="normal")
            
            # 简单的日志级别检测
            tag = "default"
            if "错误" in string or "Error" in string:
                tag = "error"
            elif "成功" in string or "完成" in string or "Success" in string:
                tag = "success"
            elif "警告" in string or "Warning" in string:
                tag = "warning"
            elif "信息" in string or "Info" in string:
                tag = "info"
            
            self.text_widget.insert(tk.END, string, tag)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")
        except Exception as e:
            try:
                self.original_stdout.write(f"UI 写入错误：{str(e)}, 原始消息：{string}\n")
            except:
                pass
    
    def flush(self):
        try:
            self.buffer.flush()
        except Exception as e:
            try:
                self.original_stdout.write(f"UI 刷新错误：{str(e)}\n")
            except:
                pass


class MockInput:
    """模拟输入类，用于替代标准输入"""
    
    def __init__(self):
        self.responses: Dict[str, str] = {}
        
    def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response
        
    def input(self, prompt: str) -> str:
        if prompt in self.responses:
            return self.responses[prompt]
        return ""


# 全局模拟输入对象
mock_input = MockInput()


def mock_input_function(prompt: str) -> str:
    return mock_input.input(prompt)


def save_authorization(auth: str) -> bool:
    """保存 Authorization 到配置文件"""
    config_dir = os.path.join(os.path.expanduser("~"), CONFIG_DIR_NAME)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_file = os.path.join(config_dir, CONFIG_FILE_NAME)
    config = {"authorization": auth}
    
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"保存 Authorization 失败：{e}")
        return False


def load_authorization() -> str:
    """从配置文件加载 Authorization"""
    config_file = os.path.join(os.path.expanduser("~"), CONFIG_DIR_NAME, CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        return ""
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config.get("authorization", "")
    except Exception as e:
        print(f"读取 Authorization 失败：{e}")
        return ""


class DownloaderUI:
    """现代化下载器图形界面类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        self._setup_styles()
        self._create_layout()
        
        # 重定向标准输出到日志区域
        self.redirect: Optional[RedirectText] = None
        
        # 下载线程
        self.download_thread: Optional[threading.Thread] = None
        
        # 设置关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_window(self):
        """配置窗口基本属性"""
        self.root.title(UI_WINDOW_TITLE)
        self.root.geometry(f"{UI_DEFAULT_WIDTH}x{UI_DEFAULT_HEIGHT}")
        self.root.minsize(UI_MIN_WIDTH, UI_MIN_HEIGHT)
        
        # 设置窗口背景色
        self.root.configure(bg=ModernColors.BACKGROUND)
        
        # 尝试设置窗口图标（如果存在）
        try:
            # self.root.iconbitmap("icon.ico")  # 可选：添加图标
            pass
        except:
            pass
    
    def _setup_styles(self):
        """配置 ttk 样式"""
        style = ttk.Style()
        
        # 配置全局字体
        style.configure(".", font=("Segoe UI", 10))
        
        # 配置 LabelFrame 样式
        style.configure(
            "Modern.TLabelframe",
            background=ModernColors.CARD_BG,
            foreground=ModernColors.TEXT_PRIMARY,
            bordercolor=ModernColors.BORDER,
            lightcolor=ModernColors.BORDER,
            darkcolor=ModernColors.BORDER
        )
        style.configure(
            "Modern.TLabelframe.Label",
            font=("Segoe UI", 11, "bold"),
            background=ModernColors.CARD_BG,
            foreground=ModernColors.TEXT_PRIMARY
        )
        
        # 配置按钮样式
        style.configure(
            "Modern.TButton",
            font=("Segoe UI", 10, "bold"),
            background=ModernColors.PRIMARY,
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            focuscolor=ModernColors.PRIMARY_DARK
        )
        style.map(
            "Modern.TButton",
            background=[("active", ModernColors.PRIMARY_DARK)],
            foreground=[("active", "#ffffff")]
        )
        
        # 配置 Entry 样式
        style.configure(
            "Modern.TEntry",
            fieldbackground="#ffffff",
            foreground=ModernColors.TEXT_PRIMARY,
            bordercolor=ModernColors.BORDER,
            focuscolor=ModernColors.PRIMARY
        )
        
        # 配置 Progressbar 样式
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=ModernColors.PRIMARY,
            troughcolor=ModernColors.BORDER,
            borderwidth=0,
            thinness=10
        )
    
    def _create_layout(self):
        """创建主布局"""
        # 主容器
        self.main_container = ttk.Frame(self.root, style="Modern.TLabelframe")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部标题栏
        self._create_header()
        
        # 内容区域（使用 PanedWindow 实现可调整大小）
        content_pane = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        content_pane.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 上半部分 - 输入表单
        self._create_input_section(content_pane)
        
        # 下半部分 - 日志和控制
        self._create_output_section(content_pane)
        
        # 状态栏
        self._create_status_bar()
    
    def _create_header(self):
        """创建顶部标题栏"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 标题
        title_label = ttk.Label(
            header_frame,
            text="📚 超星电子书下载工具",
            font=("Segoe UI", 18, "bold"),
            foreground=ModernColors.PRIMARY
        )
        title_label.pack(side=tk.LEFT)
        
        # 版本信息
        version_label = ttk.Label(
            header_frame,
            text="v2.0 Modern UI",
            font=("Segoe UI", 9),
            foreground=ModernColors.TEXT_MUTED
        )
        version_label.pack(side=tk.RIGHT, pady=5)
    
    def _create_input_section(self, parent):
        """创建输入表单区域"""
        input_frame = ttk.LabelFrame(
            parent, 
            text="📝 下载配置",
            style="Modern.TLabelframe",
            padding=15
        )
        parent.add(input_frame, weight=1)
        
        # 使用网格布局
        row = 0
        
        # 第一行：Authorization
        ttk.Label(
            input_frame, 
            text="🔑 Authorization:",
            font=("Segoe UI", 10, "bold"),
            foreground=ModernColors.TEXT_PRIMARY
        ).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        
        self.auth_var = tk.StringVar(value=load_authorization())
        self.auth_entry = ModernEntry(input_frame, textvariable=self.auth_var, width=60)
        self.auth_entry.grid(row=row, column=1, sticky=tk.W+tk.E, pady=8, padx=5)
        
        # 保存 Authorization 复选框
        self.save_auth_var = tk.BooleanVar(value=True)
        save_auth_check = ttk.Checkbutton(
            input_frame, 
            text="💾 记住授权信息",
            variable=self.save_auth_var,
            style="Modern.TCheckbutton"
        )
        save_auth_check.grid(row=row, column=2, sticky=tk.W, pady=8, padx=10)
        
        row += 1
        
        # 第二行：书籍 ID
        ttk.Label(
            input_frame,
            text="📖 书籍 ID:",
            font=("Segoe UI", 10, "bold"),
            foreground=ModernColors.TEXT_PRIMARY
        ).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        
        self.book_id_var = tk.StringVar()
        self.book_id_entry = ModernEntry(input_frame, textvariable=self.book_id_var, width=60)
        self.book_id_entry.grid(row=row, column=1, sticky=tk.W+tk.E, pady=8, padx=5)
        
        # 帮助按钮
        help_btn = ttk.Button(
            input_frame,
            text="❓ 如何获取",
            command=self._show_help,
            style="Modern.TButton"
        )
        help_btn.grid(row=row, column=2, sticky=tk.W, pady=8, padx=10)
        
        row += 1
        
        # 第三行：压缩级别
        ttk.Label(
            input_frame,
            text="🗜️ 压缩级别:",
            font=("Segoe UI", 10, "bold"),
            foreground=ModernColors.TEXT_PRIMARY
        ).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        
        self.compress_var = tk.IntVar(value=2)
        compress_frame = ttk.Frame(input_frame)
        compress_frame.grid(row=row, column=1, sticky=tk.W, pady=8, padx=5)
        
        compress_options = [
            ("❌ 不压缩", 0),
            ("🌱 轻度", 1),
            ("🌿 中度", 2),
            ("🌳 高度", 3)
        ]
        
        for text, value in compress_options:
            rb = ttk.Radiobutton(
                compress_frame,
                text=text,
                variable=self.compress_var,
                value=value
            )
            rb.pack(side=tk.LEFT, padx=8)
        
        row += 1
        
        # 第四行：保存路径
        ttk.Label(
            input_frame,
            text="📁 保存位置:",
            font=("Segoe UI", 10, "bold"),
            foreground=ModernColors.TEXT_PRIMARY
        ).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        
        self.save_path_var = tk.StringVar(value=os.getcwd())
        path_frame = ttk.Frame(input_frame)
        path_frame.grid(row=row, column=1, sticky=tk.W+tk.E, pady=8, padx=5)
        
        self.save_path_entry = ModernEntry(path_frame, textvariable=self.save_path_var, width=50)
        self.save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(
            path_frame,
            text="📂 浏览...",
            command=self.browse_save_path,
            style="Modern.TButton"
        )
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # 配置列权重
        input_frame.grid_columnconfigure(1, weight=1)
    
    def _create_output_section(self, parent):
        """创建输出和控制区域"""
        output_frame = ttk.LabelFrame(
            parent,
            text="📊 下载进度与日志",
            style="Modern.TLabelframe",
            padding=15
        )
        parent.add(output_frame, weight=2)
        
        # 进度条
        progress_frame = ttk.Frame(output_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100.0,
            mode="determinate",
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        self.progress_label = ttk.Label(
            progress_frame,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            foreground=ModernColors.PRIMARY,
            width=5
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # 日志区域
        log_container = ttk.Frame(output_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_container,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas", 9),
            bg="#f1f5f9",
            fg=ModernColors.TEXT_PRIMARY,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        log_text_scrollbar = ttk.Scrollbar(
            log_container,
            command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_text_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 控制按钮
        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.download_btn = ttk.Button(
            button_frame,
            text="🚀 开始下载",
            command=self.start_download,
            style="Modern.TButton"
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame,
            text="🧹 清空日志",
            command=self.clear_log,
            style="Modern.TButton"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 占位空间
        ttk.Frame(button_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.main_container)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="✅ 就绪")
        status_bar = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            foreground=ModernColors.TEXT_SECONDARY,
            anchor=tk.W
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 链接标签
        link_label = ttk.Label(
            status_frame,
            text="🔗 GitHub",
            font=("Segoe UI", 9),
            foreground=ModernColors.PRIMARY,
            cursor="hand2"
        )
        link_label.pack(side=tk.RIGHT)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com"))
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = (
            "获取书籍 ID 的方法：\n\n"
            "1. 打开超星电子书网站\n"
            "2. 进入您要下载的书籍页面\n"
            "3. 从浏览器地址栏复制书籍 ID\n"
            "4. 书籍 ID 通常是一串类似 '218c9e1a0013f2XXXX' 的字符\n\n"
            "获取 Authorization 的方法：\n\n"
            "1. 登录超星账户\n"
            "2. 打开浏览器开发者工具（F12）\n"
            "3. 在 Network 选项卡中找到任意请求\n"
            "4. 复制 Request Headers 中的 Authorization 值"
        )
        messagebox.showinfo("帮助", help_text)
    
    def browse_save_path(self):
        """浏览保存路径"""
        directory = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if directory:
            self.save_path_var.set(directory)
    
    def start_download(self):
        """开始下载"""
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showinfo("提示", "⏳ 下载任务正在进行中，请等待完成")
            return
        
        auth = self.auth_var.get().strip()
        book_id = self.book_id_var.get().strip()
        compress_level = self.compress_var.get()
        save_path = self.save_path_var.get()
        
        if not auth:
            messagebox.showerror("错误", "❌ 请输入 Authorization")
            return
        
        if not book_id:
            messagebox.showerror("错误", "❌ 请输入书籍 ID")
            return
        
        # 保存 Authorization
        if self.save_auth_var.get():
            save_authorization(auth)
        
        # 设置模拟输入的响应
        self._setup_mock_input(auth, book_id, compress_level)
        
        # 替换内置 input 函数
        original_input = __builtins__['input']
        __builtins__['input'] = mock_input_function
        
        # 切换到保存目录
        original_dir = os.getcwd()
        try:
            os.chdir(save_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法切换到保存目录：{e}")
            __builtins__['input'] = original_input
            return
        
        # 禁用下载按钮
        self.download_btn.configure(state="disabled")
        self.status_var.set("⏳ 下载中...")
        self.progress_var.set(0.0)
        self.progress_label.config(text="0%")
        
        # 启动下载线程
        self.download_thread = threading.Thread(
            target=self.download_task,
            args=(auth, book_id, compress_level, original_dir, original_input)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
        
        # 启动检查线程状态的定时器
        self.root.after(100, lambda: self.check_thread(original_dir, original_input))
    
    def _setup_mock_input(self, auth: str, book_id: str, compress_level: int):
        """设置模拟输入响应"""
        mock_input.set_response("请输入代表您身份信息的 Authorization:\n>>>", auth)
        mock_input.set_response("请您输入要下载的书籍 ID:（例如：218c9e1a0013f2XXXX）\n>>>", book_id)
        mock_input.set_response("是否继续上次的下载？(y/n): ", "y")
        mock_input.set_response("文件 .* 已存在，是否重新下载？(y/n): ", "y")
    
    def download_task(self, auth: str, book_id: str, compress_level: int, 
                     original_dir: str, original_input: Callable):
        """下载任务"""
        try:
            from utils.userAgent import userAgent
            from models.user import User
            from services.api_service import ApiService
            from utils.command import display_book_info
            from utils.download import download_pdf
            
            # 获取随机 ua
            user_agent = userAgent()
            
            # 设置用户信息
            user = User()
            user.set_authorization(auth)
            user.set_book_id(book_id)
            
            # 初始化 API 服务
            api_service = ApiService(user.authorization, user_agent)
            
            # 验证身份权限
            user_info = api_service.get_user_info()
            if user_info.status_code != 200:
                print("❌ Authorization 验证失败，请检查输入是否正确")
                return
            
            # 设置学校 ID
            user.set_school_id(user_info.json()["schoolId"])
            
            # 验证书籍信息
            book_info = api_service.get_book_info(user.book_id, user.school_id)
            if book_info.status_code != 200:
                print("❌ 书籍 ID 验证失败，请检查输入是否正确")
                return
            
            book_info_data = book_info.json()
            book_type = display_book_info(book_info_data)
            
            try:
                if book_type == 1:
                    book_data = api_service.get_new_pdf_info(user.book_id, user.school_id)
                    print("ℹ️ 开始下载新版 PDF...")
                    download_pdf(book_data, user.book_id, user_agent, compress_level)
                elif book_type == 2:
                    book_data = api_service.get_old_pdf_info(user.book_id, user.school_id)
                    print("ℹ️ 开始下载旧版 PDF...")
                    download_pdf(book_data, user.book_id, user_agent, compress_level)
                else:
                    print("❌ 不支持的书籍类型")
            except Exception as e:
                print(f"❌ PDF 下载或处理过程中出错：{str(e)}")
                
            print("✅ 下载任务完成")
            
        except Exception as e:
            print(f"❌ 下载过程中出错：{str(e)}")
        finally:
            os.chdir(original_dir)
            __builtins__['input'] = original_input
    
    def check_thread(self, original_dir: str, original_input: Callable):
        """检查线程状态"""
        if self.download_thread and self.download_thread.is_alive():
            self.root.after(100, lambda: self.check_thread(original_dir, original_input))
        else:
            self.download_btn.configure(state="normal")
            self.status_var.set("✅ 就绪")
            self.progress_var.set(100.0)
            self.progress_label.config(text="100%")
            os.chdir(original_dir)
            __builtins__['input'] = original_input
    
    def clear_log(self):
        """清空日志"""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        sys.stdout = sys.__stdout__
        self.root.destroy()


def start_ui():
    """启动图形界面"""
    root = tk.Tk()
    
    # 启用 DPI 感知（Windows）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = DownloaderUI(root)
    
    # 初始化日志重定向
    app.redirect = RedirectText(app.log_text)
    sys.stdout = app.redirect
    
    root.mainloop()
