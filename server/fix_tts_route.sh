#!/bin/bash
# 薇阅 AI 声线 · 修复隧道配置并重启（请用 sudo 运行）
# 可选环境变量 DOMAIN=你的域名；不设置则从现有隧道配置里读取
echo "===== 第 1 步：重写隧道配置为正确内容 ====="
python3 <<'PYEOF'
import os
import re
import shutil
import datetime
p = '/root/.cloudflared/config.yaml'
s = open(p, encoding='utf-8').read()
tm = re.search(r'^tunnel:\s*(\S+)', s, re.M)
if not tm:
    print('没找到 tunnel 行，请把 config.yaml 的内容发给我。')
    raise SystemExit(1)
cm = re.search(r'^credentials-file:\s*(\S+)', s, re.M)
cred = cm.group(1) if cm else '/root/.cloudflared/%s.json' % tm.group(1)
d = os.environ.get('DOMAIN', '')
if not d:
    m = re.search(r'hostname:\s*([^\s]+)', s)
    d = m.group(1) if m else ''
if not d:
    print('没检测到域名，请先设置环境变量 DOMAIN=你的域名')
    raise SystemExit(1)
new = (
    'tunnel: %s\n'
    'credentials-file: %s\n'
    '\n'
    'ingress:\n'
    '- hostname: %s\n'
    '  path: /wytts\n'
    '  service: http://localhost:8123\n'
    '- hostname: %s\n'
    '  service: http://localhost:8080\n'
    '- service: http_status:404\n'
) % (tm.group(1), cred, d, d)
shutil.copy2(p, p + '.bak-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
open(p, 'w', encoding='utf-8').write(new)
print('配置已重写为正确内容。')
PYEOF
RC=$?
if [ $RC -ne 0 ]; then
  exit 1
fi

echo "===== 第 2 步：重启 Cloudflare 隧道 ====="
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

echo "===== 第 3 步：测试语音中转 ====="
sleep 1
CODE=$(curl -s -o /tmp/wy_tts_route.mp3 -w "%{http_code}" \
  "http://localhost:8123/tts?text=%E6%B5%8B%E8%AF%95%E4%B8%80%E4%B8%8B&voice=zh-CN-XiaoxiaoNeural&rate=%2B0%25")
echo "本地语音服务返回：$CODE"
if [ "$CODE" = "200" ] && [ -s /tmp/wy_tts_route.mp3 ]; then
  echo "本地语音服务正常。"
else
  echo "本地语音服务异常，请检查 weiyue-tts 服务"
fi

echo ""
echo "===== 完成！====="
echo "配置已修复，隧道已重启。请把新版 tts.html 上传覆盖后使用。"
