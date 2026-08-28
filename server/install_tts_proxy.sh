#!/bin/bash
# 薇阅 AI 声线 · 服务器中转安装脚本（请用 sudo 运行）
cd "$(dirname "$0")"
APP_DIR="$PWD"

echo "===== 第 1 步：准备 Python 环境并安装 edge-tts ====="
if ! command -v python3 >/dev/null 2>&1; then
  echo "错误：没有 python3"
  exit 1
fi
if [ -d ttsenv ] && [ ! -x ttsenv/bin/pip ]; then
  echo "发现上次残缺的环境，正在清理…"
  rm -rf ttsenv
fi
if [ ! -x ttsenv/bin/pip ]; then
  echo "正在创建运行环境（可能需要安装缺失组件，请稍等）…"
  if ! python3 -m venv ttsenv 2>/tmp/wy_venv_err.txt; then
    echo "首次创建失败，尝试安装 python3-venv 后重试…"
    (apt-get update -qq && apt-get install -y -qq python3-venv) >/dev/null 2>&1 \
      || apt-get install -y -qq python3.12-venv >/dev/null 2>&1
    python3 -m venv ttsenv || {
      echo "仍然失败。请先执行下面这条命令，再重新运行本脚本："
      echo "  sudo apt install -y python3-venv"
      exit 1
    }
  fi
fi
./ttsenv/bin/pip install --quiet --upgrade pip || true
./ttsenv/bin/pip install --quiet edge-tts || {
  echo "安装 edge-tts 失败（可能网络问题），请检查网络后重试"
  exit 1
}
echo "edge-tts 已装好"

echo "===== 第 2 步：写入语音中转服务 ====="
cat > tts_server.py <<'PYEOF'
# -*- coding: utf-8 -*-
"""薇阅 AI 声线中转服务：手机请求 /tts，服务器用 edge-tts 合成 MP3 返回。"""
import asyncio
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import edge_tts


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        try:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            text = (q.get('text') or [''])[0]
            voice = (q.get('voice') or ['zh-CN-XiaoxiaoNeural'])[0]
            rate = (q.get('rate') or ['+0%'])[0]
            if not text:
                self.send_error(400, 'no text')
                return
            mp3 = asyncio.run(self._synth(text, voice, rate))
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(mp3)))
            self.end_headers()
            self.wfile.write(mp3)
        except Exception as e:
            try:
                body = ('TTS_ERROR: %s' % e).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                pass

    async def _synth(self, text, voice, rate):
        buf = bytearray()
        comm = edge_tts.Communicate(text, voice=voice, rate=rate)
        async for chunk in comm.stream():
            if chunk['type'] == 'audio':
                buf.extend(chunk['data'])
        if not buf:
            raise RuntimeError('empty audio')
        return bytes(buf)


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8123), Handler).serve_forever()
PYEOF

echo "===== 第 3 步：注册为系统服务（开机自启） ====="
cat > /etc/systemd/system/weiyue-tts.service <<UNIT
[Unit]
Description=Weiyue TTS proxy
After=network.target

[Service]
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/ttsenv/bin/python $APP_DIR/tts_server.py
Restart=always

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable weiyue-tts >/dev/null 2>&1
systemctl restart weiyue-tts
sleep 2
if ! systemctl is-active --quiet weiyue-tts; then
  echo "服务启动失败，请把下面内容发给我："
  systemctl status weiyue-tts --no-pager | tail -8
  exit 1
fi
echo "语音中转服务已运行"

echo "===== 第 4 步：测试（本机直连） ====="
sleep 1
CODE=$(curl -s -o /tmp/wy_tts_test.mp3 -w "%{http_code}" \
  "http://127.0.0.1:8123/tts?text=%E6%B5%8B%E8%AF%95%E4%B8%80%E4%B8%8B&voice=zh-CN-XiaoxiaoNeural&rate=%2B0%25")
echo "本地测试返回：$CODE"
if [ "$CODE" = "200" ] && [ -s /tmp/wy_tts_test.mp3 ]; then
  SIZE=$(stat -c%s /tmp/wy_tts_test.mp3)
  echo "本地测试成功：收到音频 $SIZE 字节"
else
  echo "本地测试失败，请检查 tts_server.py 运行日志"
fi

echo ""
echo "===== 完成！====="
echo "语音中转服务已运行在 127.0.0.1:8123。"
echo "接下来请运行 install_tts_route.sh 配置 Cloudflare 隧道路由，"
echo "然后把新版 tts.html 上传覆盖，手机刷新即可使用 AI 声线。"
