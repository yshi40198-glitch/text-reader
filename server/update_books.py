# -*- coding: utf-8 -*-
"""自动扫描 library：epub 自动转 txt，然后生成 books.json 书单。"""
import glob
import html.parser
import io
import json
import os
import re
import sys
import tempfile
import zipfile


class _TextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0
        self.cur = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6",
                   "li", "tr", "blockquote", "section", "article", "pre"):
            self.flush()

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                   "li", "tr", "blockquote", "section", "article", "pre"):
            self.flush()

    def handle_data(self, data):
        if self.skip == 0:
            t = data.strip()
            if t:
                self.cur.append(t)

    def flush(self):
        if self.cur:
            self.parts.append("".join(self.cur))
            self.cur = []


def _epub_text(path):
    """从 epub 提取纯文本（段落之间空一行），返回 (text, title, author)。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "META-INF/container.xml" not in names:
            return None
        container = z.read("META-INF/container.xml").decode("utf-8", "ignore")
        m = re.search(r'full-path="([^"]+)"', container)
        if not m:
            return None
        opf_path = m.group(1)
        opf = z.read(opf_path).decode("utf-8", "ignore")
        base = os.path.dirname(opf_path)
        manifest = dict(re.findall(r'<item[^>]+id="([^"]+)"[^>]+href="([^"]+)"', opf))
        spine = re.findall(r'<itemref[^>]+idref="([^"]+)"', opf)
        tm = re.search(r'<dc:title[^>]*>([^<]+)</dc:title>', opf)
        cm = re.search(r'<dc:creator[^>]*>([^<]+)</dc:creator>', opf)
        title = tm.group(1).strip() if tm else ""
        author = cm.group(1).strip() if cm else ""
        paras = []
        for sid in spine:
            href = manifest.get(sid)
            if not href or not href.lower().endswith((".html", ".htm", ".xhtml")):
                continue
            p = os.path.join(base, href).replace("\\", "/")
            try:
                data = z.read(p)
            except KeyError:
                continue
            s = data.decode("utf-8", "ignore")
            ex = _TextExtractor()
            try:
                ex.feed(s)
            except Exception:
                pass
            for para in ex.parts:
                para = re.sub(r"\s+", " ", para).strip()
                if not para:
                    continue
                norm = re.sub(r"\s+", "", para)
                if paras and re.sub(r"\s+", "", paras[-1]) == norm:
                    continue
                paras.append(para)
        if paras and paras[0].strip().lower() == "cover":
            paras.pop(0)
        return "\n\n".join(paras), title, author


def _safe(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "", s or "").strip()


def _convert_epubs(lib):
    for p in sorted(glob.glob(os.path.join(lib, "*.epub"))):
        try:
            res = _epub_text(p)
            if not res:
                print("跳过（不是有效 epub）: %s" % os.path.basename(p))
                continue
            text, title, author = res
            if not text.strip():
                print("跳过（没有正文）: %s" % os.path.basename(p))
                continue
            stem = os.path.splitext(os.path.basename(p))[0].strip()
            t = _safe(title) or stem
            a = _safe(author)
            out_name = (t + "-" + a) if a else t
            out_path = os.path.join(lib, out_name + ".txt")
            if os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(p):
                continue
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print("已转换: %s -> %s" % (os.path.basename(p), os.path.basename(out_path)))
        except Exception as e:
            print("转换失败: %s (%s)" % (os.path.basename(p), e))


def _write_books(base, lib):
    books = []
    for p in sorted(glob.glob(os.path.join(lib, "*.txt"))):
        name = os.path.splitext(os.path.basename(p))[0].strip()
        author = ""
        if "-" in name:
            title, author = [x.strip() for x in name.rsplit("-", 1)]
        else:
            title = name
        books.append({
            "title": title,
            "author": author,
            "file": "library/" + os.path.basename(p),
            "format": "TXT"
        })
    with open(os.path.join(base, "books.json"), "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print("已生成 books.json，书库共 %d 本。" % len(books))


def _selftest():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0"?><container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("OEBPS/content.opf",
                   '<?xml version="1.0"?><package '
                   'xmlns="http://www.idpf.org/2007/opf" '
                   'xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">'
                   '<metadata><dc:title>测试书</dc:title><dc:creator>测试作者</dc:creator></metadata>'
                   '<manifest><item id="c1" href="c1.xhtml" media-type="application/xhtml+xml"/>'
                   '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml"/></manifest>'
                   '<spine><itemref idref="c1"/><itemref idref="nav"/></spine></package>')
        z.writestr("OEBPS/c1.xhtml",
                   '<html><body><p>第一段文字</p><p>第一段文字</p>'
                   '<p>第二段文字</p></body></html>')
        z.writestr("OEBPS/nav.xhtml",
                   '<html><body><nav><p>目录</p><p>第一章</p></nav></body></html>')
    buf.seek(0)
    fd, tmp = tempfile.mkstemp(suffix=".epub", prefix="wy_epub_selftest_")
    with os.fdopen(fd, "wb") as f:
        f.write(buf.getvalue())
    try:
        res = _epub_text(tmp)
        ok = res is not None and res[0] == "第一段文字\n\n第二段文字\n\n目录\n\n第一章" \
            and res[1] == "测试书" and res[2] == "测试作者"
        if ok:
            print("自检通过：epub 转换功能正常。")
        else:
            print("自检失败：转换结果不符合预期。res = %r" % (res,))
        return ok
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    lib = os.path.join(base, "library")
    if not os.path.isdir(lib):
        os.makedirs(lib)
    _convert_epubs(lib)
    _write_books(base, lib)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    main()
