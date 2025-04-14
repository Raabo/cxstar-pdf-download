import os
import requests
from pypdf import PdfWriter, PdfReader
from multiprocessing.dummy import Pool
from reportlab.pdfgen import canvas
from PIL import Image
from utils.encrypt import createVerificationData
from utils.file import createFolder, deleteFolderAndFile
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import tqdm
import io


# 获取单页pdf信息,并返回接受到的内容
def getPagePdfInfo(url, ua, max_retries=3, timeout=30):
    headers = {
        'User-Agent': ua,
        'Referer': 'https://www.cxstar.com/'
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
            time.sleep(2 * attempt)  # 指数退避


def pdfDownload(book_data, book_id, ua, compress_level=2):
    """
    下载PDF文件
    compress_level: 压缩级别 0-不压缩, 1-轻度压缩, 2-中度压缩, 3-高度压缩
    """
    # 书名
    book_name = book_data["title"]
    # 页数
    total_page = int(book_data["totalPage"])
    # 目录数据
    catalog = book_data["catalog"]
    # 链接地址
    file_path = book_data["filePath"]

    pdf_name = book_name + ".pdf"
    
    # 检查最终PDF是否已存在，如果存在则询问是否重新下载
    if os.path.exists(pdf_name):
        choice = input(f"文件 {pdf_name} 已存在，是否重新下载？(y/n): ")
        if choice.lower() != 'y':
            print(f"跳过下载，使用已存在的文件: {pdf_name}")
            return
    
    merger = PdfWriter()
    createFolder(book_id)

    print("正在下载单页pdf中,请等待...")
    page_pdf_list = []
    
    # 检查哪些页面已经下载
    existing_pages = []
    for i in range(total_page):
        temp_file_name = f"{book_id}/{i}.pdf"
        if os.path.exists(temp_file_name) and os.path.getsize(temp_file_name) > 0:
            existing_pages.append(i)
    
    if existing_pages:
        print(f"发现已下载的页面: {len(existing_pages)}/{total_page}")
        choice = input("是否继续上次的下载？(y/n): ")
        if choice.lower() != 'y':
            # 如果不继续，则清空目录重新下载
            print("重新开始下载...")
            deleteFolderAndFile(book_id)
            createFolder(book_id)
            existing_pages = []

    for i in range(total_page):
        if i in existing_pages:
            continue  # 跳过已下载的页面
        verification = createVerificationData()
        url = f'{file_path}&pageno={i}&bookruid={book_id}&nonce={verification["nonce"]}&stime={verification["stime"]}&sign={verification["sign"]}'
        page_pdf_list.append((url, book_id + "/" + str(i) + ".pdf", ua))
    
    if page_pdf_list:
        pool = Pool()
        try:
            # 使用更安全的方式显示进度
            if not book_data.get("webPath"):
                # 替换tqdm进度条，使用自定义的进度显示
                total = len(page_pdf_list)
                completed = 0
                print(f"开始下载 {total} 页PDF...")
                
                # 使用map而不是imap，并手动显示进度
                for _ in pool.imap_unordered(pagePdfDownload, page_pdf_list):
                    completed += 1
                    if completed % 10 == 0 or completed == total:  # 每10页或最后一页显示一次进度
                        print(f"下载进度: {completed}/{total} 页 ({completed/total*100:.1f}%)")
            else:
                # 图片PDF的处理
                total = len(page_pdf_list)
                completed = 0
                print(f"开始下载 {total} 页图片PDF...")
                
                for _ in pool.imap_unordered(saveImagePdf, page_pdf_list):
                    completed += 1
                    if completed % 10 == 0 or completed == total:  # 每10页或最后一页显示一次进度
                        print(f"下载进度: {completed}/{total} 页 ({completed/total*100:.1f}%)")
        except Exception as e:
            print(f"下载过程中出错: {str(e)}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
        finally:
            pool.close()
            pool.join()
    else:
        print("所有页面已下载完成，跳过下载步骤")

    print("正在合并所有pdf中...")
    valid_pages = 0
    for i in range(total_page):
        temp_file_name = book_id + "/" + str(i) + ".pdf"
        try:
            # 检查文件是否存在且大小正常
            if not os.path.exists(temp_file_name) or os.path.getsize(temp_file_name) == 0:
                print(f"警告: 页面 {i+1} 文件不存在或为空，跳过此页")
                continue
                
            # 尝试打开PDF文件并验证其完整性
            try:
                with open(temp_file_name, 'rb') as f:
                    reader = PdfReader(f)
                    if len(reader.pages) > 0:
                        # 确保添加文件的第一页
                        merger.add_page(reader.pages[0])
                        valid_pages += 1
                    else:
                        print(f"警告: 页面 {i+1} 没有内容，跳过此页")
            except Exception as e:
                print(f"警告: 无法读取页面 {i+1}，错误: {str(e)}，跳过此页")
                continue
        except Exception as e:
            print(f"处理页面 {i+1} 时出错: {str(e)}")
            continue
    
    if valid_pages == 0:
        print("错误: 没有有效的页面可以合并，无法创建PDF")
        return
    
    print(f"成功合并了 {valid_pages}/{total_page} 页")

    # 设置压缩选项
    if compress_level > 0:
        print(f"正在以压缩级别 {compress_level} 压缩PDF...")
        merger.compress_content_streams = True  # 这会压缩PDF内容流

    try:
        print(f"正在写入最终PDF文件: {pdf_name}")
        merger.write(pdf_name)
        merger.close()
        print("PDF文件写入成功")
    except Exception as e:
        print(f"写入PDF文件时出错: {str(e)}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return

    # 删除缓存的文件及目录
    print("正在删除临时文件及目录...")
    deleteFolderAndFile(book_id)

    print("正在为书籍增加书签中...")
    addBookMark(pdf_name, catalog)

    # 如果需要进一步压缩，可以使用额外的压缩方法
    if compress_level >= 2:
        print("正在进行额外的PDF压缩...")
        compressPdf(pdf_name, compress_level)

    current_path = os.getcwd()
    print("下载完毕，书籍位置：" + current_path + "/" + pdf_name)


# 下载单页pdf到指定位置
def pagePdfDownload(page_pdf):
    url = page_pdf[0]
    file_name = page_pdf[1]
    ua = page_pdf[2]
    
    # 检查文件是否已存在且大小正常
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        # 尝试验证PDF文件的完整性
        try:
            with open(file_name, 'rb') as f:
                PdfReader(f)
            return  # 文件有效，直接返回
        except Exception:
            print(f"文件 {file_name} 已存在但无效，重新下载")
            # 文件无效，继续下载
    
    try:
        temp = getPagePdfInfo(url, ua)
        
        # 验证下载的内容是否为有效的PDF
        if not temp.startswith(b'%PDF-'):
            print(f"警告: 从 {url} 下载的内容不是有效的PDF，跳过")
            return
            
        # 写入文件
        with open(file_name, 'wb') as temp_file:
            temp_file.write(temp)
            
        # 再次验证写入的文件
        try:
            with open(file_name, 'rb') as f:
                PdfReader(f)
        except Exception as e:
            print(f"警告: 写入的文件 {file_name} 不是有效的PDF: {str(e)}")
    except Exception as e:
        print(f"下载页面时出错: {str(e)}")


# 将图片保存为pdf并下载
def saveImagePdf(page_pdf, compress_level=2):
    file_name = page_pdf[1]
    
    # 检查PDF文件是否已存在且大小正常
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        return
        
    verification = createVerificationData()
    url = f'{page_pdf[0]}&nonce={verification["nonce"]}&stime={verification["stime"]}&sign={verification["sign"]}'
    ua = page_pdf[2]
    temp = getPagePdfInfo(url, ua)
    temp_file_name = file_name.split(".")[0] + ".png"

    # 压缩图片
    if compress_level > 0:
        try:
            # 从内存中读取图片
            image = Image.open(io.BytesIO(temp))
            
            # 根据压缩级别设置质量
            quality = 100 - (compress_level * 15)  # 级别1=85%, 级别2=70%, 级别3=55%
            
            # 保存为压缩的JPEG（如果原图是PNG，转换为RGB模式）
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # 创建一个BytesIO对象来保存压缩后的图片
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            # 将压缩后的图片写入文件
            with open(temp_file_name, "wb") as f:
                f.write(output.getvalue())
        except Exception as e:
            print(f"图片压缩失败，使用原图: {e}")
            with open(temp_file_name, "wb") as f:
                f.write(temp)
    else:
        with open(temp_file_name, "wb") as f:
            f.write(temp)

    # 将图片转换为PDF
    image = Image.open(temp_file_name)
    image_width, image_height = image.size

    pdf_file_name = file_name
    pdf = canvas.Canvas(pdf_file_name, pagesize=(image_width, image_height))
    pdf.drawImage(temp_file_name, 0, 0, width=image_width, height=image_height)
    pdf.save()


# pdf增加目录列表
def addBookMark(file_name, catalog):
    pdf_file = open(file_name, 'rb')
    # 创建一个PdfFileReader对象
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    # 添加一页到新PDF
    total_pages = len(pdf_reader.pages)
    for i in range(total_pages):
        pdf_writer.add_page(pdf_reader.pages[i])

    for i in range(len(catalog)):
        catalog_data = catalog[i]
        bookmark = pdf_writer.add_outline_item(catalog_data["title"], int(catalog_data["page"])-1)
        children = catalog_data.get("children", [])

        for j in range(len(children)):
            bookdata2 = children[j]
            bookmark2 = pdf_writer.add_outline_item(bookdata2["title"], int(bookdata2["page"])-1, parent=bookmark)
            sub_children = bookdata2.get("children", [])

            for k in range(len(sub_children)):
                bookdata3 = sub_children[k]
                bookmark3 = pdf_writer.add_outline_item(bookdata3["title"], int(bookdata3["page"]) - 1, parent=bookmark2)
                grand_children = bookdata3.get("children", [])

                for z in range(len(grand_children)):
                    bookdata4 = grand_children[z]
                    pdf_writer.add_outline_item(bookdata4["title"], int(bookdata4["page"]) - 1, parent=bookmark3)

    # 创建一个新的PDF文件并保存
    output_pdf_file = open(file_name, 'wb')
    pdf_writer.write(output_pdf_file)

    # 关闭文件
    pdf_file.close()
    output_pdf_file.close()


# 压缩PDF文件
def compressPdf(file_name, compress_level=2):
    """
    使用Ghostscript对已生成的PDF文件进行压缩，特别优化嵌入字体
    compress_level: 压缩级别 1-轻度压缩, 2-中度压缩, 3-高度压缩
    """
    temp_file = file_name + ".temp.pdf"
    
    try:
        import subprocess
        import shutil
        
        # 检查是否安装了Ghostscript
        gs_path = shutil.which("gswin64c") or shutil.which("gswin32c") or shutil.which("gs")
        
        if not gs_path:
            # 尝试使用内置的Ghostscript路径
            possible_paths = [
                r"C:\Program Files\gs\gs9.56.1\bin\gswin64c.exe",
                r"C:\Program Files (x86)\gs\gs9.56.1\bin\gswin32c.exe",
                # 添加更多可能的路径
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    gs_path = path
                    break
            
            if not gs_path:
                print("未找到Ghostscript可执行文件，跳过PDF压缩")
                print("请安装Ghostscript: https://www.ghostscript.com/download/gsdnld.html")
                return
        
        # 根据压缩级别设置不同的压缩参数
        if compress_level == 1:
            # 轻度压缩
            params = [
                "-dPDFSETTINGS=/prepress",  # 较高质量
                "-dCompatibilityLevel=1.4"
            ]
        elif compress_level == 2:
            # 中度压缩
            params = [
                "-dPDFSETTINGS=/ebook",  # 中等质量
                "-dCompatibilityLevel=1.4",
                "-dEmbedAllFonts=true",
                "-dSubsetFonts=true"
            ]
        else:
            # 高度压缩
            params = [
                "-dPDFSETTINGS=/screen",  # 屏幕质量，最大压缩
                "-dCompatibilityLevel=1.4",
                "-dEmbedAllFonts=true",
                "-dSubsetFonts=true",
                "-dCompressFonts=true"
            ]
        
        # 构建Ghostscript命令
        gs_cmd = [
            gs_path,  # 使用找到的Ghostscript可执行文件
            "-sDEVICE=pdfwrite",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dSAFER",
            f"-sOutputFile={temp_file}"
        ] + params + [file_name]
        
        print(f"正在使用Ghostscript压缩PDF，压缩级别: {compress_level}...")
        
        # 使用subprocess.STARTUPINFO来隐藏窗口
        startupinfo = None
        if os.name == 'nt':  # 仅在Windows上设置
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
        
        # 使用startupinfo参数来隐藏窗口
        result = subprocess.run(gs_cmd, capture_output=True, text=True, startupinfo=startupinfo)
        
        if result.returncode != 0:
            print(f"Ghostscript压缩失败: {result.stderr}")
            raise Exception("Ghostscript压缩失败")
        
        # 确保所有文件句柄已关闭后再尝试替换文件
        import gc
        gc.collect()  # 强制垃圾回收，释放可能的文件句柄
        
        # 检查压缩后的文件大小
        original_size = os.path.getsize(file_name)
        compressed_size = os.path.getsize(temp_file)
        
        if compressed_size >= original_size:
            print(f"压缩后文件大小未减小 (原始: {original_size/1024/1024:.2f}MB, 压缩后: {compressed_size/1024/1024:.2f}MB)，保留原文件")
            os.remove(temp_file)
            return
        
        # 尝试替换文件
        try:
            os.replace(temp_file, file_name)
            print(f"PDF压缩完成，压缩级别: {compress_level}")
            print(f"文件大小: {original_size/1024/1024:.2f}MB -> {compressed_size/1024/1024:.2f}MB (节省 {(original_size-compressed_size)/1024/1024:.2f}MB)")
        except PermissionError:
            # 如果直接替换失败，尝试先删除原文件再重命名
            print("直接替换文件失败，尝试备用方法...")
            try:
                # 先尝试删除原文件
                os.remove(file_name)
                os.rename(temp_file, file_name)
                print(f"PDF压缩完成，压缩级别: {compress_level}")
                print(f"文件大小: {original_size/1024/1024:.2f}MB -> {compressed_size/1024/1024:.2f}MB (节省 {(original_size-compressed_size)/1024/1024:.2f}MB)")
            except Exception as e:
                # 如果仍然失败，保留临时文件并提示用户
                print(f"无法替换原文件: {e}")
                print(f"压缩后的文件已保存为: {temp_file}")
                print("您可以手动关闭所有PDF查看器后，将临时文件重命名为原文件名")
    except Exception as e:
        print(f"PDF压缩过程中出错: {e}")
        # 如果临时文件存在，尝试删除
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
