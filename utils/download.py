"""
PDF 下载服务 - 处理 PDF 文件的下载、合并和压缩
"""
import os
import io
import time
import gc
from typing import List, Tuple, Dict, Any
from multiprocessing.dummy import Pool

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pypdf import PdfWriter, PdfReader
from PIL import Image
from reportlab.pdfgen import canvas

from config import (
    MAX_RETRIES, REQUEST_TIMEOUT, DEFAULT_COMPRESS_LEVEL,
    PROGRESS_UPDATE_INTERVAL, WEB_BASE_URL
)
from utils.encrypt import createVerificationData
from utils.file import createFolder, deleteFolderAndFile


def get_page_pdf_info(url: str, ua: str, max_retries: int = None, timeout: int = None) -> bytes:
    """
    获取单页 PDF 信息
    
    Args:
        url: PDF 页面 URL
        ua: User-Agent
        max_retries: 最大重试次数
        timeout: 超时时间（秒）
        
    Returns:
        bytes: PDF 文件内容
    """
    if max_retries is None:
        max_retries = MAX_RETRIES
    if timeout is None:
        timeout = REQUEST_TIMEOUT
    
    headers = {
        'User-Agent': ua,
        'Referer': f'{WEB_BASE_URL}/'
    }
    
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    for attempt in range(max_retries + 1):
        try:
            response = session.get(url, headers=headers, stream=True, timeout=timeout)
            return response.content
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt == max_retries:
                print(f"下载失败，URL: {url}")
                raise
            print(f"连接超时，正在进行第 {attempt + 1} 次重试...")
            time.sleep(2 * attempt)
    
    raise Exception(f"下载失败：{url}")


def download_pdf(book_data: Dict[str, Any], book_id: str, ua: str, compress_level: int = None) -> None:
    """
    下载 PDF 文件
    
    Args:
        book_data: 书籍数据
        book_id: 书籍 ID
        ua: User-Agent
        compress_level: 压缩级别 (0-不压缩，1-轻度，2-中度，3-高度)
    """
    if compress_level is None:
        compress_level = DEFAULT_COMPRESS_LEVEL
    
    # 提取书籍信息
    book_name = book_data["title"]
    total_page = int(book_data["totalPage"])
    catalog = book_data.get("catalog", [])
    file_path = book_data["filePath"]
    pdf_name = f"{book_name}.pdf"
    
    # 检查文件是否已存在
    if os.path.exists(pdf_name):
        choice = input(f"文件 {pdf_name} 已存在，是否重新下载？(y/n): ")
        if choice.lower() != 'y':
            print(f"跳过下载，使用已存在的文件：{pdf_name}")
            return
    
    merger = PdfWriter()
    createFolder(book_id)
    
    print("正在下载单页 pdf 中，请等待...")
    page_pdf_list = []
    
    # 检查已下载的页面
    existing_pages = _get_existing_pages(book_id, total_page)
    
    if existing_pages:
        print(f"发现已下载的页面：{len(existing_pages)}/{total_page}")
        choice = input("是否继续上次的下载？(y/n): ")
        if choice.lower() != 'y':
            print("重新开始下载...")
            deleteFolderAndFile(book_id)
            createFolder(book_id)
            existing_pages = []
    
    # 构建下载任务列表
    for i in range(total_page):
        if i in existing_pages:
            continue
        
        verification = createVerificationData()
        url = f'{file_path}?pageno={i}&bookruid={book_id}&nonce={verification["nonce"]}&stime={verification["stime"]}&sign={verification["sign"]}'
        page_pdf_list.append((url, f"{book_id}/{i}.pdf", ua))
    
    # 执行下载
    if page_pdf_list:
        _execute_download(page_pdf_list, book_data.get("webPath"))
    else:
        print("所有页面已下载完成，跳过下载步骤")
    
    # 合并 PDF
    _merge_pdfs(merger, book_id, total_page)
    
    # 设置压缩选项
    if compress_level > 0:
        print(f"正在以压缩级别 {compress_level} 压缩 PDF...")
        merger.compress_content_streams = True
    
    # 写入最终文件
    try:
        print(f"正在写入最终 PDF 文件：{pdf_name}")
        merger.write(pdf_name)
        merger.close()
        print("PDF 文件写入成功")
    except Exception as e:
        print(f"写入 PDF 文件时出错：{str(e)}")
        return
    
    # 清理临时文件
    print("正在删除临时文件及目录...")
    deleteFolderAndFile(book_id)
    
    # 添加书签
    print("正在为书籍增加书签中...")
    add_bookmark(pdf_name, catalog)
    
    # 额外压缩
    if compress_level >= 2:
        print("正在进行额外的 PDF 压缩...")
        compress_pdf(pdf_name, compress_level)
    
    print(f"下载完毕，书籍位置：{os.getcwd()}/{pdf_name}")


def _get_existing_pages(book_id: str, total_page: int) -> List[int]:
    """获取已下载的页面列表"""
    existing_pages = []
    for i in range(total_page):
        temp_file_name = f"{book_id}/{i}.pdf"
        if os.path.exists(temp_file_name) and os.path.getsize(temp_file_name) > 0:
            existing_pages.append(i)
    return existing_pages


def _execute_download(page_pdf_list: List[Tuple], web_path: str = None) -> None:
    """执行下载任务"""
    pool = Pool()
    try:
        total = len(page_pdf_list)
        completed = 0
        
        if not web_path:
            print(f"开始下载 {total} 页 PDF...")
            for _ in pool.imap_unordered(_download_page, page_pdf_list):
                completed += 1
                if completed % PROGRESS_UPDATE_INTERVAL == 0 or completed == total:
                    print(f"下载进度：{completed}/{total} 页 ({completed/total*100:.1f}%)")
        else:
            print(f"开始下载 {total} 页图片 PDF...")
            for _ in pool.imap_unordered(_save_image_pdf, page_pdf_list):
                completed += 1
                if completed % PROGRESS_UPDATE_INTERVAL == 0 or completed == total:
                    print(f"下载进度：{completed}/{total} 页 ({completed/total*100:.1f}%)")
    except Exception as e:
        print(f"下载过程中出错：{str(e)}")
    finally:
        pool.close()
        pool.join()


def _download_page(args: Tuple) -> None:
    """下载单个页面"""
    url, file_name, ua = args
    
    # 检查文件是否已存在且有效
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        try:
            with open(file_name, 'rb') as f:
                PdfReader(f)
            return
        except Exception:
            print(f"文件 {file_name} 已存在但无效，重新下载")
    
    try:
        content = get_page_pdf_info(url, ua)
        
        # 验证 PDF 格式
        if not content.startswith(b'%PDF-'):
            print(f"警告：从 {url} 下载的内容不是有效的 PDF，跳过")
            return
        
        with open(file_name, 'wb') as f:
            f.write(content)
        
        # 验证写入的文件
        try:
            with open(file_name, 'rb') as f:
                PdfReader(f)
        except Exception as e:
            print(f"警告：写入的文件 {file_name} 不是有效的 PDF: {str(e)}")
    except Exception as e:
        print(f"下载页面时出错：{str(e)}")


def _save_image_pdf(args: Tuple, compress_level: int = None) -> None:
    """将图片保存为 PDF"""
    if compress_level is None:
        compress_level = DEFAULT_COMPRESS_LEVEL
    
    _, file_name, ua = args
    
    # 检查 PDF 文件是否已存在
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        return
    
    # 下载图片
    verification = createVerificationData()
    url = f'{args[0]}&nonce={verification["nonce"]}&stime={verification["stime"]}&sign={verification["sign"]}'
    image_data = get_page_pdf_info(url, ua)
    
    temp_file_name = file_name.rsplit(".", 1)[0] + ".png"
    
    # 压缩并保存图片
    if compress_level > 0:
        try:
            image = Image.open(io.BytesIO(image_data))
            quality = 100 - (compress_level * 15)
            
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            with open(temp_file_name, "wb") as f:
                f.write(output.getvalue())
        except Exception as e:
            print(f"图片压缩失败，使用原图：{e}")
            with open(temp_file_name, "wb") as f:
                f.write(image_data)
    else:
        with open(temp_file_name, "wb") as f:
            f.write(image_data)
    
    # 转换为 PDF
    image = Image.open(temp_file_name)
    image_width, image_height = image.size
    
    pdf = canvas.Canvas(file_name, pagesize=(image_width, image_height))
    pdf.drawImage(temp_file_name, 0, 0, width=image_width, height=image_height)
    pdf.save()


def _merge_pdfs(merger: PdfWriter, book_id: str, total_page: int) -> None:
    """合并所有 PDF 页面"""
    print("正在合并所有 pdf 中...")
    valid_pages = 0
    
    for i in range(total_page):
        temp_file_name = f"{book_id}/{i}.pdf"
        
        if not os.path.exists(temp_file_name) or os.path.getsize(temp_file_name) == 0:
            print(f"警告：页面 {i+1} 文件不存在或为空，跳过此页")
            continue
        
        try:
            with open(temp_file_name, 'rb') as f:
                reader = PdfReader(f)
                if len(reader.pages) > 0:
                    merger.add_page(reader.pages[0])
                    valid_pages += 1
                else:
                    print(f"警告：页面 {i+1} 没有内容，跳过此页")
        except Exception as e:
            print(f"警告：无法读取页面 {i+1}，错误：{str(e)}，跳过此页")
    
    if valid_pages == 0:
        print("错误：没有有效的页面可以合并，无法创建 PDF")
        return
    
    print(f"成功合并了 {valid_pages}/{total_page} 页")


def add_bookmark(file_name: str, catalog: List[Dict[str, Any]]) -> None:
    """
    为 PDF 添加书签
    
    Args:
        file_name: PDF 文件名
        catalog: 目录数据
    """
    with open(file_name, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        pdf_writer = PdfWriter()
        
        # 添加所有页面
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        # 添加书签
        _add_bookmarks_recursive(pdf_writer, catalog, parent=None)
        
        # 写入文件
        with open(file_name, 'wb') as output_file:
            pdf_writer.write(output_file)


def _add_bookmarks_recursive(pdf_writer: PdfWriter, catalog: List[Dict], parent=None, depth: int = 0) -> None:
    """递归添加书签"""
    max_depth = 4  # 限制最大深度
    
    for item in catalog:
        title = item.get("title", "")
        page = int(item.get("page", 1)) - 1
        
        if depth == 0:
            bookmark = pdf_writer.add_outline_item(title, page)
        elif parent is not None:
            bookmark = pdf_writer.add_outline_item(title, page, parent=parent)
        else:
            continue
        
        # 递归处理子书签
        children = item.get("children", [])
        if children and depth < max_depth - 1:
            _add_bookmarks_recursive(pdf_writer, children, parent=bookmark, depth=depth + 1)


def compress_pdf(file_name: str, compress_level: int = None) -> None:
    """
    使用 Ghostscript 压缩 PDF
    
    Args:
        file_name: PDF 文件名
        compress_level: 压缩级别 (1-轻度，2-中度，3-高度)
    """
    if compress_level is None:
        compress_level = DEFAULT_COMPRESS_LEVEL
    
    import subprocess
    import shutil
    
    temp_file = f"{file_name}.temp.pdf"
    
    # 查找 Ghostscript
    gs_path = shutil.which("gswin64c") or shutil.which("gswin32c") or shutil.which("gs")
    
    if not gs_path:
        print("未找到 Ghostscript 可执行文件，跳过 PDF 压缩")
        return
    
    # 设置压缩参数
    params_map = {
        1: ["-dPDFSETTINGS=/prepress", "-dCompatibilityLevel=1.4"],
        2: ["-dPDFSETTINGS=/ebook", "-dCompatibilityLevel=1.4", "-dEmbedAllFonts=true", "-dSubsetFonts=true"],
        3: ["-dPDFSETTINGS=/screen", "-dCompatibilityLevel=1.4", "-dEmbedAllFonts=true", "-dSubsetFonts=true", "-dCompressFonts=true"]
    }
    params = params_map.get(compress_level, params_map[2])
    
    # 构建命令
    gs_cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dSAFER",
        f"-sOutputFile={temp_file}"
    ] + params + [file_name]
    
    print(f"正在使用 Ghostscript 压缩 PDF，压缩级别：{compress_level}...")
    
    # 隐藏窗口（Windows）
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
    
    try:
        result = subprocess.run(gs_cmd, capture_output=True, text=True, startupinfo=startupinfo)
        
        if result.returncode != 0:
            print(f"Ghostscript 压缩失败：{result.stderr}")
            return
        
        gc.collect()
        
        # 检查压缩效果
        original_size = os.path.getsize(file_name)
        compressed_size = os.path.getsize(temp_file)
        
        if compressed_size >= original_size:
            print(f"压缩后文件大小未减小，保留原文件")
            os.remove(temp_file)
            return
        
        # 替换文件
        try:
            os.replace(temp_file, file_name)
            print(f"PDF 压缩完成")
            print(f"文件大小：{original_size/1024/1024:.2f}MB -> {compressed_size/1024/1024:.2f}MB")
        except PermissionError:
            print("直接替换文件失败，尝试备用方法...")
            os.remove(file_name)
            os.rename(temp_file, file_name)
            print(f"PDF 压缩完成")
    
    except Exception as e:
        print(f"PDF 压缩过程中出错：{e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
