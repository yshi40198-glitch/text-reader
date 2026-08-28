#!/bin/bash
# 薇阅 · 云端早间新闻自动生成安装脚本（请用 sudo 运行）
#
# 可配置项（环境变量）：
#   WEB_ROOT 网站根目录（默认 /var/www/html，请改成你自己的）
#   NEWS_TIME 每天生成新闻的时间（默认 05:00，用 "分 时" 格式写）
cd "$(dirname "$0")"
APP_DIR="$PWD"
WEB_ROOT="${WEB_ROOT:-/var/www/html}"
NEWS_TIME="${NEWS_TIME:-0 5}"

echo "===== 第 1 步：检查 Python ====="
if ! command -v python3 >/dev/null 2>&1; then
  echo "错误：服务器上没有 python3，无法继续。"
  exit 1
fi

echo "===== 第 2 步：写入早间新闻生成脚本 ====="
cat > morning_news.py <<'PYEOF'
# -*- coding: utf-8 -*-
"""薇阅云端早间新闻生成器。

每天从公开 RSS 新闻源抓取新闻，整理成当天的早间新闻文件，
输出到网站根目录的 早间新闻/ 文件夹（文件名：早间新闻-YYYY-MM-DD.txt）。
薇阅电脑版配置好服务器地址后，启动时会自动拉取这份文件并提示朗读。

也可以由你自己的 AI agent / 脚本接管：直接把当天新闻写成
早间新闻/早间新闻-YYYY-MM-DD.txt 即可，薇阅同样能读到。
"""
import html
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

WEB_ROOT = os.environ.get('WY_WEB_ROOT', '/var/www/html')
OUT_DIR = os.path.join(WEB_ROOT, '早间新闻')
MAX_ITEMS = 15
READ_TIMEOUT = 20

# 公开 RSS 新闻源（任选可用即可，全部失败会提示）
SOURCES = [
    'https://feeds.bbci.co.uk/zhongwen/simp/rss.xml',          # BBC 中文
    'https://www.zaobao.com.sg/rss',                            # 联合早报
    'https://www.cna.com.tw/rss/rssall.aspx',                   # 中央社
    'https://rsshub.app/zhihu/daily',                           # 知乎日报（若可用）
]


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'WeiyueMorningNews/1.0 (+https://github.com/)'
    })
    with urllib.request.urlopen(req, timeout=READ_TIMEOUT) as r:
        return r.read()


def clean(text):
    text = html.unescape(text or '')
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def parse_rss(data):
    items = []
    root = ET.fromstring(data)
    for item in root.iter('item'):
        title = clean(item.findtext('title'))
        desc = clean(item.findtext('description'))
        link = clean(item.findtext('link'))
        if title:
            items.append((title, desc, link))
    return items


def main():
    today = time.strftime('%Y-%m-%d')
    all_items = []
    used = set()
    for url in SOURCES:
        try:
            for title, desc, link in parse_rss(fetch(url)):
                if title in used:
                    continue
                used.add(title)
                all_items.append((title, desc, link))
        except Exception as e:
            print('来源不可用：%s（%s）' % (url, e))
        if len(all_items) >= MAX_ITEMS:
            break
    if not all_items:
        print('所有新闻源都失败了，今天没有生成早间新闻。')
        return 1

    lines = ['早间新闻 · %s' % today, '']
    for i, (title, desc, link) in enumerate(all_items[:MAX_ITEMS], 1):
        lines.append('%d. %s' % (i, title))
        if desc and desc != title:
            lines.append('   %s' % desc[:80])
        if link:
            lines.append('   %s' % link)
        lines.append('')

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, '早间新闻-%s.txt' % today)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('已生成：%s（%d 条）' % (out, len(all_items)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
PYEOF

echo "===== 第 3 步：立即生成一次今天的早间新闻 ====="
WY_WEB_ROOT="$WEB_ROOT" python3 morning_news.py

echo "===== 第 4 步：设置每天自动生成 ====="
CRON_LINE="$NEWS_TIME * * * cd $APP_DIR && WY_WEB_ROOT=$WEB_ROOT python3 morning_news.py >> morning_news.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'morning_news.py' ; echo "$CRON_LINE" ) | crontab -

echo ""
echo "===== 完成！====="
echo "以后每天 $NEWS_TIME 服务器会自动生成当天的早间新闻。"
echo "薇阅电脑版配置好服务器地址后，启动时自动拉取并提示朗读。"
echo "生成记录：morning_news.log"
