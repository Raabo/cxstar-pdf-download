<h2 align="center">
    <p><img src="./images/logo.png" width="100" alt="logo"></p>
    <a href="https://github.com/Raabo/cxstar-pdf-download">Cxstar PDF Download</a>
</h2>

<p align="center">
    📚 帮助您下载畅想之星您有权限阅读的 PDF 书籍
</p>

<p align="center">
    <a href="https://github.com/Raabo/cxstar-pdf-download/releases/latest">
        <img src="https://img.shields.io/github/v/release/Raabo/cxstar-pdf-download?style=flat-square" alt="Release">
    </a>
    <a href="https://github.com/Raabo/cxstar-pdf-download/actions">
        <img src="https://img.shields.io/github/actions/workflow/status/Raabo/cxstar-pdf-download/ci-cd.yml?branch=main&style=flat-square" alt="CI/CD">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square" alt="Python">
    </a>
    <a href="https://github.com/Raabo/cxstar-pdf-download/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/Raabo/cxstar-pdf-download?style=flat-square" alt="License">
    </a>
</p>

<p align="center">
    <img src="./images/ui.png" alt="UI Preview" width="600">
</p>

---

## ✨ 功能特点

- 📖 **完整下载** - 支持下载您有权限阅读的完整 PDF 书籍
- 🗜️ **智能压缩** - 内置 PDF 压缩功能（需安装 Ghostscript）
- 🎨 **现代 UI** - 美观易用的图形界面，支持深色模式
- ⏸️ **断点续传** - 网络中断后可继续下载
- 🔖 **书签支持** - 自动添加书籍目录书签
- 🚀 **高速下载** - 多线程并发下载，提升效率
- 💻 **双模式** - 支持命令行和图形界面两种操作方式

---

## 📋 使用前准备

### 1️⃣ 获取 Authorization Token

1. 打开浏览器并登录 [畅想之星](https://www.cxstar.com)
2. 按 `F12` 打开开发者工具
3. 切换到 **Console（控制台）** 标签
4. 复制并执行以下代码，Token 将自动复制到剪贴板：

```javascript
copy(document.cookie.match(/token=([^;]+)/)[1])
```

> 💡 **提示**: Token 有效期有限，失效后请重新获取

### 2️⃣ 获取书籍 ID

**PC 网页版:**
```
https://www.cxstar.com/Book/Detail?ruid=29e2af210001a5XXXX
                                          ↑ 这就是书籍 ID
```

**手机版网页:**
```
https://m.cxstar.com/book/29e2af210001a5XXXX
                            ↑ 这就是书籍 ID
```

---

## 🚀 使用方法

### 方法一：使用已编译程序（推荐新手）

1. 前往 [Releases](https://github.com/Raabo/cxstar-pdf-download/releases/latest) 下载最新版本
2. 解压下载的压缩包
3. 双击运行 `.exe` 文件
4. 输入 **Authorization Token** 和 **书籍 ID**，点击开始下载

### 方法二：从源码运行

#### 步骤 1: 克隆项目
```bash
git clone https://github.com/Raabo/cxstar-pdf-download.git
cd cxstar-pdf-download
```

#### 步骤 2: 创建虚拟环境（可选但推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 步骤 3: 安装依赖
```bash
pip install -U -r requirements.txt
```

#### 步骤 4: 运行程序
```bash
# 图形界面模式（默认）
python main.py

# 命令行模式
python main.py --cli
```

---

## 🗜️ PDF 压缩功能

如需减小生成的 PDF 文件体积：

1. **安装 Ghostscript**
   - Windows: [下载安装包](https://ghostscript.com/releases/gsdnld.html)
   - macOS: `brew install ghostscript`
   - Linux: `sudo apt-get install ghostscript`

2. 在程序界面中勾选 **"启用 PDF 压缩"** 选项

---

## ⚙️ 配置说明

程序会自动读取同目录下的 `config.ini` 配置文件（首次运行自动生成）：

```ini
[settings]
# 下载线程数 (1-10)
threads = 5

# 超时时间（秒）
timeout = 30

# 是否启用压缩
enable_compression = false

# 压缩质量 (1-100)
compression_quality = 75
```

---

## ⚠️ 注意事项

- 🔐 **Token 安全**: 请妥善保管您的 Authorization Token，不要分享给他人
- ⏰ **有效期**: Token 会过期，失效后请重新获取
- 📖 **阅读权限**: 若只有部分阅读权限，将只能下载试读章节
- 🌐 **网络稳定**: 下载过程中请保持网络连接稳定
- 📊 **下载频率**: 建议每日下载不超过 10 本书，避免触发反爬机制
- 📜 **使用限制**: 仅供个人学习研究使用，请勿用于商业用途

---

## ❓ 常见问题

<details>
<summary><b>Q: 下载失败或卡住怎么办？</b></summary>
<br>

1. 检查网络连接是否正常
2. 确认 Authorization Token 是否有效（重新获取）
3. 检查书籍 ID 是否正确
4. 尝试降低下载线程数（修改 config.ini）
5. 查看日志输出获取详细错误信息

</details>

<details>
<summary><b>Q: 压缩功能无法使用？</b></summary>
<br>

1. 确认已正确安装 Ghostscript
2. 验证 Ghostscript 是否添加到系统 PATH
3. 测试命令行：`gswin64c -version`（Windows）或 `gs -version`（Mac/Linux）

</details>

<details>
<summary><b>Q: 如何更新到最新版本？</b></summary>
<br>

**源码运行用户:**
```bash
git pull origin main
pip install -U -r requirements.txt
```

**编译程序用户:** 前往 Releases 下载最新版本覆盖即可

</details>

<details>
<summary><b>Q: 支持哪些操作系统？</b></summary>
<br>

- ✅ Windows 10/11（推荐）
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 18.04+, CentOS 7+)

</details>

---

## 🛠️ 开发相关

### 项目结构
```
cxstar-pdf-download/
├── main.py              # 程序入口
├── config.py            # 配置管理
├── models/              # 数据模型
├── services/            # 业务逻辑层
├── utils/               # 工具函数
└── ui.py                # 图形界面
```

### 本地开发
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black .
flake8
```

### CI/CD 状态
本项目已配置自动化 CI/CD 流程：
- ✅ 每次推送自动运行测试和代码检查
- ✅ 推送到主分支自动构建并发布
- 📦 支持多 Python 版本测试 (3.8 - 3.11)

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

⭐ 如果这个项目对您有帮助，欢迎给个 Star 支持一下！

---

<p align="center">
    <i>最后更新：2024 | Made with ❤️ by Raabo</i>
</p>
