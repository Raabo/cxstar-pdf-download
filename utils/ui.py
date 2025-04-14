import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import json
from io import StringIO

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = StringIO()
        self.original_stdout = sys.stdout  # 保存原始的stdout

    def write(self, string):
        try:
            self.buffer.write(string)
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, string)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")
        except Exception as e:
            # 如果写入UI出错，尝试写入到原始stdout
            try:
                self.original_stdout.write(f"UI写入错误: {str(e)}, 原始消息: {string}\n")
            except:
                pass
    
    def flush(self):
        try:
            self.buffer.flush()
        except Exception as e:
            try:
                self.original_stdout.write(f"UI刷新错误: {str(e)}\n")
            except:
                pass

# 添加一个模拟输入类，用于替代标准输入
class MockInput:
    def __init__(self):
        self.responses = {}
        
    def set_response(self, prompt, response):
        self.responses[prompt] = response
        
    def input(self, prompt):
        if prompt in self.responses:
            return self.responses[prompt]
        # 如果没有预设的响应，返回空字符串
        return ""

# 全局模拟输入对象
mock_input = MockInput()

# 重写内置input函数
def mock_input_function(prompt):
    return mock_input.input(prompt)

# 添加Authorization存储和读取功能
def save_authorization(auth):
    config_dir = os.path.join(os.path.expanduser("~"), ".cxstar")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_file = os.path.join(config_dir, "config.json")
    config = {"authorization": auth}
    
    try:
        with open(config_file, "w") as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print(f"保存Authorization失败: {e}")
        return False

def load_authorization():
    config_file = os.path.join(os.path.expanduser("~"), ".cxstar", "config.json")
    if not os.path.exists(config_file):
        return ""
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config.get("authorization", "")
    except Exception as e:
        print(f"读取Authorization失败: {e}")
        return ""

class DownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("超星电子书下载工具")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入区域框架
        self.input_frame = ttk.LabelFrame(self.main_frame, text="输入信息", padding="10")
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # Authorization输入
        ttk.Label(self.input_frame, text="Authorization:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.auth_var = tk.StringVar(value=load_authorization())  # 加载保存的Authorization
        self.auth_entry = ttk.Entry(self.input_frame, textvariable=self.auth_var, width=50)
        self.auth_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 添加保存Authorization的复选框
        self.save_auth_var = tk.BooleanVar(value=True)
        self.save_auth_check = ttk.Checkbutton(self.input_frame, text="保存Authorization", 
                                              variable=self.save_auth_var)
        self.save_auth_check.grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # 书籍ID输入
        ttk.Label(self.input_frame, text="书籍ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.book_id_var = tk.StringVar()
        self.book_id_entry = ttk.Entry(self.input_frame, textvariable=self.book_id_var, width=50)
        self.book_id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 压缩级别选择
        ttk.Label(self.input_frame, text="压缩级别:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.compress_var = tk.IntVar(value=2)
        compress_frame = ttk.Frame(self.input_frame)
        compress_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(compress_frame, text="不压缩", variable=self.compress_var, value=0).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(compress_frame, text="轻度压缩", variable=self.compress_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(compress_frame, text="中度压缩", variable=self.compress_var, value=2).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(compress_frame, text="高度压缩", variable=self.compress_var, value=3).pack(side=tk.LEFT, padx=5)
        
        # 保存位置选择
        ttk.Label(self.input_frame, text="保存位置:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.save_path_var = tk.StringVar(value=os.getcwd())
        save_path_frame = ttk.Frame(self.input_frame)
        save_path_frame.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        self.save_path_entry = ttk.Entry(save_path_frame, textvariable=self.save_path_var, width=40)
        self.save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_btn = ttk.Button(save_path_frame, text="浏览...", command=self.browse_save_path)
        self.browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.download_btn = ttk.Button(self.button_frame, text="开始下载", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(self.button_frame, text="清空日志", command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.main_frame, text="下载日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 重定向标准输出到日志区域
        self.redirect = RedirectText(self.log_text)
        sys.stdout = self.redirect
        
        # 下载线程
        self.download_thread = None
        
        # 设置关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def browse_save_path(self):
        directory = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if directory:
            self.save_path_var.set(directory)
    
    def start_download(self):
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showinfo("提示", "下载任务正在进行中，请等待完成")
            return
        
        auth = self.auth_var.get().strip()
        book_id = self.book_id_var.get().strip()
        compress_level = self.compress_var.get()
        save_path = self.save_path_var.get()
        
        if not auth:
            messagebox.showerror("错误", "请输入Authorization")
            return
        
        if not book_id:
            messagebox.showerror("错误", "请输入书籍ID")
            return
        
        # 如果选择了保存Authorization，则保存
        if self.save_auth_var.get():
            save_authorization(auth)
        
        # 设置模拟输入的响应
        mock_input.set_response("请输入代表您身份信息的Authorization:\n>>>", auth)
        mock_input.set_response("请输入书籍id:\n>>>", book_id)
        mock_input.set_response("是否继续上次的下载？(y/n): ", "y")
        mock_input.set_response("是否重新下载？(y/n): ", "y")
        mock_input.set_response("是否合并PDF？(y/n): ", "y")  # 添加合并PDF的响应
        mock_input.set_response("是否压缩PDF？(y/n): ", "y")  # 添加压缩PDF的响应
        mock_input.set_response("请选择压缩级别(0-3): ", str(compress_level))  # 添加压缩级别的响应
        
        # 替换内置input函数
        original_input = __builtins__['input']
        __builtins__['input'] = mock_input_function
        
        # 切换到保存目录
        original_dir = os.getcwd()
        try:
            os.chdir(save_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法切换到保存目录: {e}")
            # 恢复原始input函数
            __builtins__['input'] = original_input
            return
        
        # 禁用下载按钮
        self.download_btn.configure(state="disabled")
        self.status_var.set("下载中...")
        
        # 启动下载线程
        self.download_thread = threading.Thread(target=self.download_task, 
                                               args=(auth, book_id, compress_level, original_dir, original_input))
        self.download_thread.daemon = True
        self.download_thread.start()
        
        # 启动检查线程状态的定时器
        self.root.after(100, lambda: self.check_thread(original_dir, original_input))
    
    def download_task(self, auth, book_id, compress_level, original_dir, original_input):
        try:
            from utils.userAgent import userAgent
            from utils.userInfo import User
            from utils.network import WebInfo
            from utils.command import disposeBookInfo
            from utils.download import pdfDownload
            
            # 获取随机ua
            user_agent = userAgent()
            
            # 设置用户信息
            user = User()
            user.authorization = auth
            user.book_id = book_id
            
            # 网络初始化
            web_info = WebInfo(user.authorization, user_agent)
            
            # 验证身份权限
            user_info = web_info.getUserInfo()
            if user_info.status_code != 200:
                print("Authorization验证失败，请检查输入是否正确")
                return
            
            # 设置学校ID
            user.setSchoolId(user_info.json()["schoolId"])
            
            # 验证书籍信息
            book_info = web_info.getBookInfo(user.book_id, user.school_id)
            if book_info.status_code != 200:
                print("书籍ID验证失败，请检查输入是否正确")
                return
            
            book_info = book_info.json()
            # 打印书籍信息并获取书籍类型
            book_type = disposeBookInfo(book_info)
            
            try:
                if book_type == 1:
                    book_data = web_info.getNewPdfInfo(user.book_id, user.school_id)
                    print("开始下载新版PDF...")
                    pdfDownload(book_data, user.book_id, user_agent, compress_level)
                elif book_type == 2:
                    book_data = web_info.getOldPdfWebInfo(user.book_id, user.school_id)
                    print("开始下载旧版PDF...")
                    pdfDownload(book_data, user.book_id, user_agent, compress_level)
                else:
                    print("不支持的书籍类型")
            except Exception as e:
                print(f"PDF下载或处理过程中出错: {str(e)}")
                import traceback
                print(f"错误详情: {traceback.format_exc()}")
                
            print("下载任务完成")
            
        except Exception as e:
            print(f"下载过程中出错: {str(e)}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
        finally:
            # 恢复原始目录
            os.chdir(original_dir)
            # 恢复原始input函数
            __builtins__['input'] = original_input
    
    def check_thread(self, original_dir, original_input):
        if self.download_thread and self.download_thread.is_alive():
            # 线程仍在运行，继续检查
            self.root.after(100, lambda: self.check_thread(original_dir, original_input))
        else:
            # 线程已结束，恢复UI状态
            self.download_btn.configure(state="normal")
            self.status_var.set("就绪")
            # 恢复原始目录
            os.chdir(original_dir)
            # 确保恢复原始input函数
            __builtins__['input'] = original_input
    
    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
    
    def on_closing(self):
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        # 确保恢复原始input函数
        if 'original_input' in globals():
            __builtins__['input'] = globals()['original_input']
        self.root.destroy()

def start_ui():
    root = tk.Tk()
    app = DownloaderUI(root)
    root.mainloop()