#!/bin/bash
# 薇阅云端书库 · EPUB 自动转换安装脚本（请用 sudo 运行）
cd "$(dirname "$0")"
APP_DIR="$PWD"

echo "===== 第 1 步：安装增强版扫描脚本（epub 自动转 txt） ====="
cp -f update_books.py "$APP_DIR/update_books.py"

echo "===== 第 2 步：自检 epub 转换功能 ====="
python3 "$APP_DIR/update_books.py" --selftest || exit 1

echo "===== 第 3 步：立即生成一次书单（顺手转换已有 epub） ====="
python3 "$APP_DIR/update_books.py"

echo "===== 第 4 步：确认每分钟自动更新 ====="
( crontab -l 2>/dev/null | grep -v 'update_books.py' ; \
  echo '* * * * * cd '"$APP_DIR"' && python3 update_books.py >/dev/null 2>&1' ) | crontab -

echo ""
echo "===== 完成！====="
echo "以后往 library 文件夹丢 .txt 或 .epub，1 分钟内自动上架。"
echo ".epub 会自动转成 txt；转换失败的书会保留原文件并跳过。"
