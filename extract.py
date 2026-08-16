# -*- coding: utf-8 -*-
"""文档内容提取：PDF / Word(.docx .doc) / 纯文本(全部格式)，含朗读整理工具"""
import os


_BOX_CHARS = set(chr(c) for c in range(0x2500, 0x2580))  # 表格框线等装饰字符


def clean_for_speech(text):
    """整理成适合朗读的文本：去掉表格框线/装饰字符、压缩连续空行。"""
    lines = []
    for line in (text or '').splitlines():
        line = ''.join(ch for ch in line if ch not in _BOX_CHARS).strip()
        if line:
            lines.append(line)
        else:
            if lines and lines[-1] != '':
                lines.append('')
    out, blank = [], False
    for line in lines:
        if line == '':
            if not blank:
                out.append('')
            blank = True
        else:
            blank = False
            out.append(line)
    while out and out[-1] == '':
        out.pop()
    return '\n'.join(out)


def split_chunks(text, max_len=180):
    """按句切块，每块约 max_len 字；无标点的超长段也强制切分。"""
    import re
    sentences = re.split(r'(?<=[。！？；…\n])', text or '')
    out, buf = [], ''
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        while len(s) > max_len:
            out.append(s[:max_len])
            s = s[max_len:]
        if s:
            buf += s
        if len(buf) >= max_len:
            out.append(buf)
            buf = ''
    if buf:
        out.append(buf)
    return out


def extract_text(path):
    """按扩展名提取文本。读不了时抛异常(由上层转成友好提示)。"""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return extract_pdf(path)
    elif ext == '.docx':
        return extract_docx(path)
    elif ext == '.doc':
        return extract_doc(path)
    elif ext in ('.epub',):
        return extract_epub(path)
    elif ext in ('.html', '.htm'):
        return extract_html(path)
    elif ext in ('.txt', '.md', '.text'):
        return read_text_file(path)
    else:
        raise ValueError(f"暂不支持此格式 ({ext or '无扩展名'})")


def read_text_file(path):
    """读纯文本：自动识别常见中文编码(UTF-8 / GBK / UTF-16)，避免乱码。"""
    with open(path, 'rb') as f:
        raw = f.read()
    # 1) 尝试 UTF-8
    try:
        return raw.decode('utf-8')
    except (UnicodeDecodeError, ValueError):
        pass
    # 2) 尝试 GBK（中文 Windows ANSI 最常见）
    try:
        return raw.decode('gbk')
    except (UnicodeDecodeError, ValueError):
        pass
    # 3) 尝试 UTF-16 (带 BOM)
    for enc in ('utf-16', 'gb18030', 'big5'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    # 4) 最后兜底：忽略错误
    return raw.decode('utf-8', errors='ignore')


def extract_pdf(path):
    import pymupdf  # PyMuPDF
    doc = pymupdf.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return '\n'.join(pages)


def extract_docx(path):
    """Word .docx（现代 XML 格式）用 python-docx 提取。"""
    import docx
    d = docx.Document(path)
    parts = []
    # 正文段落
    for para in d.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    # 表格
    for table in d.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append(' | '.join(cells))
    return '\n'.join(parts)


def extract_epub(path):
    """EPUB 电子书：本质是 zip，把里面的 XHTML/HTML 正文提取出来。"""
    import zipfile
    from html.parser import HTMLParser

    class _Text(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []

        def handle_data(self, data):
            self.parts.append(data)

    texts = []
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist()
                 if n.lower().endswith(('.xhtml', '.html', '.htm'))]
        names.sort()
        for n in names:
            try:
                p = _Text()
                p.feed(z.read(n).decode('utf-8', errors='ignore'))
                chunk = ''.join(p.parts).strip()
                if chunk:
                    texts.append(chunk)
            except Exception:
                continue
    return '\n'.join(texts)


def extract_html(path):
    """网页/HTML 文件：去掉标签只留文字。"""
    from html.parser import HTMLParser

    class _Text(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []

        def handle_data(self, data):
            self.parts.append(data)

    p = _Text()
    p.feed(read_text_file(path))
    return ''.join(p.parts)


def extract_doc(path):
    """Word .doc（旧版二进制格式）读取。

    优先用本机安装的 Microsoft Word 通过 COM 打开并取文本（最可靠，
    需装了 Microsoft Office/Word）。若本机没装 Word，返回 None，
    由上层引导把文件另存为 .docx。
    """
    try:
        # 尝试用 Word 的 COM 接口打开（仅 Windows + 装了 Office 时有效）
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        try:
            doc = word.Documents.Open(os.path.abspath(path), ReadOnly=True)
            try:
                text = doc.Content.Text
            finally:
                doc.Close(False)
            return text
        finally:
            word.Quit()
    except Exception:
        pass
    return None


def extract_chunks(text, words_per_chunk=120):
    """按句切成长度不超 words_per_chunk 的分块，用于逐句朗读。"""
    import re
    sentences = re.split(r'(?<=[。！？；…\n.])\s*', text)
    chunks, cur, cnt = [], [], 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        cur.append(s)
        cnt += len(s)
        if cnt >= words_per_chunk:
            chunks.append(''.join(cur))
            cur, cnt = [], 0
    if cur:
        chunks.append(''.join(cur))
    return chunks
