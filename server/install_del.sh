#!/bin/bash
# 薇阅云端书库 · 删除功能安装脚本（请用 sudo 运行）
#
# 可配置项（环境变量）：
#   DOMAIN   你的域名，例如 your-domain.com（默认读取隧道配置里的域名）
#   WEB_ROOT 网站根目录（默认 /var/www/html，请改成你自己的）
#   DEL_KEY  删除密钥（不设置则自动生成一个随机密钥并打印出来）
cd "$(dirname "$0")"
APP_DIR="$PWD"
DOMAIN="${DOMAIN:-}"
WEB_ROOT="${WEB_ROOT:-/var/www/html}"
DEL_KEY="${DEL_KEY:-}"

if [ -z "$DEL_KEY" ]; then
  DEL_KEY=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 24)
  echo ""
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "已为你生成随机删除密钥（请务必记下来）："
  echo "  $DEL_KEY"
  echo "删书时需要在软件里输入这个密钥。"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo ""
fi

echo "===== 第 1 步：写入删除服务 ====="
cat > del_server.py <<PYEOF
# -*- coding: utf-8 -*-
"""薇阅云端书库 · 删除服务：校验密钥后删除 library 里的 txt 书，并刷新书单。

密钥通过 POST 请求体发送（兼容旧版 GET），不会出现在网址和访问日志里。
"""
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.environ.get('WY_WEB_ROOT', '/var/www/html')
LIB = os.path.join(BASE, 'library')
KEY_FILE = os.path.join(BASE, '.wydel_key')


def load_key():
    try:
        return open(KEY_FILE, encoding='utf-8').read().strip()
    except Exception:
        return ''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self._handle(urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query))

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(length).decode('utf-8', 'ignore') if length else ''
        self._handle(urllib.parse.parse_qs(body))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _handle(self, q):
        try:
            rel = (q.get('file') or [''])[0].strip().lstrip('/')
            key = (q.get('key') or [''])[0].strip()
            if not key or key != load_key():
                self._send(403, 'BAD_KEY')
                return
            name = os.path.basename(rel)
            if not name.lower().endswith('.txt'):
                self._send(400, 'NOT_TXT')
                return
            target = os.path.abspath(os.path.join(LIB, name))
            if not target.startswith(os.path.abspath(LIB) + os.sep):
                self._send(400, 'BAD_PATH')
                return
            if not os.path.exists(target):
                self._send(404, 'NOT_FOUND')
                return
            os.remove(target)
            try:
                os.system('/usr/bin/python3 %s/update_books.py >/dev/null 2>&1' % BASE)
            except Exception:
                pass
            self._send(200, 'OK')
        except Exception as e:
            self._send(500, 'ERR:' + str(e))

    def _send(self, code, text):
        body = text.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8124), Handler).serve_forever()
PYEOF

echo "===== 第 2 步：写入密钥文件 ====="
printf '%s' "$DEL_KEY" > "$APP_DIR/.wydel_key"
chmod 600 "$APP_DIR/.wydel_key"

echo "===== 第 3 步：注册为系统服务（开机自启） ====="
cat > /etc/systemd/system/weiyue-del.service <<UNIT
[Unit]
Description=Weiyue library delete service
After=network.target

[Service]
WorkingDirectory=$APP_DIR
Environment=WY_WEB_ROOT=$WEB_ROOT
ExecStart=/usr/bin/python3 $APP_DIR/del_server.py
Restart=always

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable weiyue-del >/dev/null 2>&1
systemctl restart weiyue-del
sleep 1
if ! systemctl is-active --quiet weiyue-del; then
  echo "删除服务启动失败，请把下面内容发给我："
  systemctl status weiyue-del --no-pager | tail -8
  exit 1
fi
echo "删除服务已运行"

echo "===== 第 4 步：更新隧道配置（增加 /wydel 路由，保留 /wytts） ====="
if [ -z "$DOMAIN" ]; then
  DOMAIN=$(python3 -c "
import re
s = open('/root/.cloudflared/config.yaml', encoding='utf-8').read()
m = re.search(r'hostname:\s*([^\s]+)', s)
print(m.group(1) if m else '')
" 2>/dev/null)
fi
if [ -z "$DOMAIN" ]; then
  echo "没有检测到域名，请在运行前设置环境变量 DOMAIN=你的域名"
  exit 1
fi
export DOMAIN
python3 <<'PYEOF'
import os
import re
import shutil
import datetime
p = '/root/.cloudflared/config.yaml'
s = open(p, encoding='utf-8').read()
need_tts = 'http://localhost:8123' not in s
need_del = 'http://localhost:8124' not in s
if not need_tts and not need_del:
    print('隧道配置已包含薇阅路由，跳过修改。')
    raise SystemExit(0)
tm = re.search(r'^tunnel:\s*(\S+)', s, re.M)
if not tm:
    print('没找到 tunnel 行，请把 config.yaml 的内容发给我。')
    raise SystemExit(1)
d = os.environ.get('DOMAIN', '')
if not d:
    m = re.search(r'hostname:\s*([^\s]+)', s)
    d = m.group(1) if m else ''
if not d:
    print('没有检测到域名，请在运行前设置环境变量 DOMAIN=你的域名')
    raise SystemExit(1)
bak = p + '.bak-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy2(p, bak)
print('已备份原配置到：%s' % bak)
routes = ''
if need_tts:
    routes += ('- hostname: %s\n'
               '  path: /wytts\n'
               '  service: http://localhost:8123\n') % d
if need_del:
    routes += ('- hostname: %s\n'
               '  path: /wydel\n'
               '  service: http://localhost:8124\n') % d
lines = s.splitlines(True)
idx = None
for i, line in enumerate(lines):
    if re.match(r'^\s*-\s*hostname:', line):
        idx = i
        break
if idx is None:
    for i, line in enumerate(lines):
        if re.match(r'^\s*-\s*service:', line):
            idx = i
            break
if idx is None:
    print('没找到 ingress 路由行，请把 config.yaml 的内容发给我。')
    raise SystemExit(1)
lines[idx:idx] = [routes]
open(p, 'w', encoding='utf-8').write(''.join(lines))
print('隧道配置已更新（保留原有路由）。')
PYEOF
RC=$?
if [ $RC -ne 0 ]; then
  exit 1
fi

echo "===== 第 5 步：重启 Cloudflare 隧道 ====="
RESTARTED=0
UNIT=$(systemctl list-unit-files 2>/dev/null | grep -i cloudflared | awk '{print $1}' | head -1)
if [ -n "$UNIT" ]; then
  echo "找到系统服务：$UNIT，正在重启…"
  systemctl restart "$UNIT" 2>/dev/null && RESTARTED=1
fi
if [ $RESTARTED -eq 0 ]; then
  service cloudflared restart 2>/dev/null && RESTARTED=1
fi
if [ $RESTARTED -eq 0 ]; then
  P=$(pgrep -f 'cloudflared' | head -1)
  if [ -n "$P" ]; then
    CMD=$(tr '\0' ' ' < /proc/$P/cmdline)
    CWD=$(readlink /proc/$P/cwd 2>/dev/null)
    echo "用原命令重新启动 cloudflared…"
    kill "$P" 2>/dev/null
    sleep 2
    if [ -n "$CWD" ]; then cd "$CWD"; fi
    nohup $CMD >/tmp/cloudflared_restart.log 2>&1 &
    sleep 4
    if pgrep -f 'cloudflared' >/dev/null 2>&1; then
      RESTARTED=1
      echo "cloudflared 已重新启动。"
    fi
  fi
fi
if [ $RESTARTED -eq 0 ]; then
  echo "无法自动重启 cloudflared，请把上面输出发给我。"
  exit 1
fi

echo "===== 第 6 步：测试删除服务 ====="
sleep 1
CODE=$(curl -s -o /tmp/wy_del_test.txt -w "%{http_code}" \
  -X POST -d "file=library/abc.txt&key=wrong" \
  "http://localhost:8124/wydel")
BODY=$(cat /tmp/wy_del_test.txt)
echo "密钥校验测试：HTTP $CODE，返回 $BODY"
if [ "$CODE" = "403" ]; then
  echo "删除服务正常（错误密钥被拒绝，保护生效）。"
else
  echo "删除服务异常，请把上面输出发给我。"
  systemctl status weiyue-del --no-pager | tail -8
  exit 1
fi

echo ""
echo "===== 完成！====="
echo "书库删除功能已装好。请把新版 tts.html 上传覆盖，"
echo "手机刷新后在书库每本书后面就能看到「删除」按钮。"
