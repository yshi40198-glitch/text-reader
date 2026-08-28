#!/bin/bash
# 薇阅书库 · 自动找书安装脚本（每天自动从维基文库抓一本公版书）
cd "$(dirname "$0")"

echo "===== 第 1 步：检查 Python ====="
if ! command -v python3 >/dev/null 2>&1; then
  echo "错误：服务器上没有 python3，无法继续。"
  exit 1
fi
python3 --version

echo "===== 第 2 步：生成自动找书脚本 ====="
cat > fetch_books.py <<'PYEOF'
# -*- coding: utf-8 -*-
"""薇阅书库自动找书：从维基文库（公版书）每天抓一本经典到 library 文件夹。

只抓公版书（古代经典，作者逝世超过 50 年），不存在版权风险。
"""
import os
import re
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(BASE, 'library')
WIKI = 'https://zh.wikisource.org'

# (维基文库页面名, 显示书名, 作者)
BOOKS = [
    ('道德經', '道德经', '老子'),
    ('論語', '论语', '孔子及其弟子'),
    ('大學', '大学', '曾参'),
    ('中庸', '中庸', '子思'),
    ('孟子', '孟子', '孟子'),
    ('莊子', '庄子', '庄周'),
    ('荀子', '荀子', '荀况'),
    ('墨子', '墨子', '墨翟'),
    ('韓非子', '韩非子', '韩非'),
    ('孫子兵法', '孙子兵法', '孙武'),
    ('詩經', '诗经', '佚名'),
    ('尚書', '尚书', '佚名'),
    ('周易', '周易', '佚名'),
    ('禮記', '礼记', '佚名'),
    ('左傳', '左传', '左丘明'),
    ('戰國策', '战国策', '刘向'),
    ('史記', '史记', '司马迁'),
    ('漢書', '汉书', '班固'),
    ('後漢書', '后汉书', '范晔'),
    ('三國志', '三国志', '陈寿'),
    ('資治通鑑', '资治通鉴', '司马光'),
    ('世說新語', '世说新语', '刘义庆'),
    ('聊齋志異', '聊斋志异', '蒲松龄'),
    ('西遊記', '西游记', '吴承恩'),
    ('三國演義', '三国演义', '罗贯中'),
    ('水滸傳', '水浒传', '施耐庵'),
    ('紅樓夢', '红楼梦', '曹雪芹'),
    ('儒林外史', '儒林外史', '吴敬梓'),
    ('鏡花緣', '镜花缘', '李汝珍'),
    ('老殘遊記', '老残游记', '刘鹗'),
    ('浮生六記', '浮生六记', '沈复'),
    ('千字文', '千字文', '周兴嗣'),
    ('百家姓', '百家姓', '佚名'),
    ('三字經', '三字经', '王应麟'),
    ('唐詩三百首', '唐诗三百首', '蘅塘退士'),
    ('宋詞三百首', '宋词三百首', '朱孝臧'),
    ('千家詩', '千家诗', '谢枋得'),
    ('幼學瓊林', '幼学琼林', '程登吉'),
    ('茶經', '茶经', '陆羽'),
    ('黃帝內經·素問', '黄帝内经·素问', '佚名'),
]


def fetch_raw(title):
    """用 ?action=raw 拿维基文库页面原文。"""
    url = WIKI + '/wiki/' + urllib.parse.quote(title.replace(' ', '_')) + '?action=raw'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'WeiyueBookBot/1.0 (personal e-book library)'
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'ignore')


def clean_wikitext(wt):
    """把维基文本粗略清理成适合朗读的纯文本。"""
    wt = re.sub(r'<!--.*?-->', '', wt, flags=re.S)
    wt = re.sub(r'\{\{[^{}]*\}\}', '', wt)
    wt = re.sub(r'<ref[^>]*>.*?</ref>', '', wt, flags=re.S)
    wt = re.sub(r'<[^>]+>', '', wt)
    wt = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', wt)
    wt = re.sub(r'\[\[([^\]]*)\]\]', r'\1', wt)
    wt = re.sub(r'^=+\s*.*?\s*=+\s*$', '', wt, flags=re.M)
    wt = wt.replace('&nbsp;', ' ').replace('&quot;', '"')
    wt = wt.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    lines = []
    for line in wt.split('\n'):
        s = line.strip()
        if not s:
            continue
        if re.match(r'^[|{\-*#:]', s):
            continue
        lines.append(s)
    return '\n'.join(lines)


def main():
    os.makedirs(LIB, exist_ok=True)
    existing = set(os.listdir(LIB))
    for page, title, author in BOOKS:
        fname = '%s-%s.txt' % (title, author)
        if title in existing or fname in existing:
            continue
        try:
            wt = fetch_raw(page)
            text = clean_wikitext(wt)
            if len(text) < 200:
                print('跳过 %s：内容太少或页面不对' % page)
                continue
            with open(os.path.join(LIB, fname), 'w', encoding='utf-8') as f:
                f.write('%s\n\n作者：%s\n\n%s\n' % (title, author, text))
            print('已抓取：%s（%d 字）' % (title, len(text)))
            return
        except Exception as e:
            print('抓取失败 %s：%s' % (page, e))
            continue
    print('本次没有抓到新书（可能都抓过了，或书单里的页面暂时不可用）')


if __name__ == '__main__':
    main()
PYEOF

echo "===== 第 3 步：立即试抓一本 ====="
python3 fetch_books.py

echo "===== 第 4 步：设置每天凌晨自动抓一本 ====="
( crontab -l 2>/dev/null | grep -v 'fetch_books.py' ; \
  echo '0 3 * * * cd '"$PWD"' && python3 fetch_books.py >> bookscan.log 2>&1' ) | crontab -

echo ""
echo "===== 完成！====="
echo "以后每天凌晨 3 点，书库会自动从公版书库抓一本经典书，"
echo "配合已装好的自动上架，1 分钟内书单自动更新。"
echo "手机刷新书库就能看到新书。你什么都不用管。"
echo "想看抓书记录：打开 bookscan.log 文件。"
