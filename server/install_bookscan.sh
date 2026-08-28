#!/bin/bash
# 薇阅云端书库自动上架安装脚本
cd "$(dirname "$0")"

echo "===== 第 1 步：检查 Python ====="
if ! command -v python3 >/dev/null 2>&1; then
  echo "错误：服务器上没有 python3，无法继续。"
  exit 1
fi
python3 --version

echo "===== 第 2 步：生成自动扫描脚本 ====="
cat > update_books.py <<'PYEOF'
# -*- coding: utf-8 -*-
"""自动扫描 library 文件夹，生成 books.json 书单。"""
import glob
import json
import os

base = os.path.dirname(os.path.abspath(__file__))
lib = os.path.join(base, 'library')
books = []
if os.path.isdir(lib):
    for p in sorted(glob.glob(os.path.join(lib, '*.txt'))):
        name = os.path.splitext(os.path.basename(p))[0].strip()
        author = ''
        if '-' in name:
            title, author = [x.strip() for x in name.rsplit('-', 1)]
        else:
            title = name
        books.append({
            'title': title,
            'author': author,
            'file': 'library/' + os.path.basename(p),
            'format': 'TXT'
        })
with open(os.path.join(base, 'books.json'), 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
print('已生成 books.json，书库共 %d 本。' % len(books))
PYEOF

echo "===== 第 3 步：立即生成一次书单 ====="
python3 update_books.py

echo "===== 第 4 步：设置每分钟自动更新 ====="
( crontab -l 2>/dev/null | grep -v 'update_books.py' ; \
  echo '* * * * * cd '"$PWD"' && python3 update_books.py >/dev/null 2>&1' ) | crontab -

echo ""
echo "===== 完成！====="
echo "以后往 library 文件夹里丢 .txt 书，1 分钟内书单自动更新。"
echo "书名格式建议：书名-作者.txt（例如 道德经-老子.txt）"
