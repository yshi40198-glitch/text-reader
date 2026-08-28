#!/bin/bash
# 薇阅 AI 声线 · Cloudflare 隧道路由配置（请用 sudo 运行）
# 可选环境变量 DOMAIN=你的域名；不设置则从现有隧道配置里读取
echo "===== 第 1 步：修改隧道配置，加入 /wytts 路由 ====="
python3 <<'PYEOF'
import os
import re
p = '/root/.cloudflared/config.yaml'
with open(p, encoding='utf-8') as f:
    s = f.read()
d = os.environ.get('DOMAIN', '')
if not d:
    m = re.search(r'hostname:\s*([^\s]+)', s)
    d = m.group(1) if m else ''
if not d:
    print('没检测到域名，请先设置环境变量 DOMAIN=你的域名')
    raise SystemExit(1)
if 'http://localhost:8123' in s:
    print('已配置过，跳过修改。')
else:
    old = '  service: http://localhost:8080'
    new = ('- hostname: %s\n'
           '  path: /wytts\n'
           '  service: http://localhost:8123\n'
           '- hostname: %s\n'
           '  service: http://localhost:8080') % (d, d)
    if old not in s:
        print('没找到原来的配置行，请手动把 config.yaml 的内容发给我。')
        raise SystemExit(1)
    s = s.replace(old, new, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print('路由已加入。')
PYEOF
RC=$?
if [ $RC -ne 0 ]; then
  exit 1
fi

echo "===== 第 2 步：重启隧道（网站会闪断几秒，正常） ====="
systemctl restart cloudflared 2>/dev/null \
  || service cloudflared restart 2>/dev/null \
  || echo "自动重启失败，请手动执行：sudo systemctl restart cloudflared"
sleep 4

echo "===== 第 3 步：测试语音中转 ====="
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
echo "现在 https://你的域名/wytts 会转发到语音中转服务。"
echo "请上传新版 tts.html，手机刷新后 AI 声线即可稳定使用。"
