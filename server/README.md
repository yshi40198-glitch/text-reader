# 薇阅云端书库 · 服务器端组件（Server Components）

These scripts let anyone self-host the Weiyue cloud library and AI voice
relay on their own server. The desktop app and the phone web page connect
only to the server address you configure — nothing is hardcoded.

这些脚本让任何人都能在自己的服务器上部署薇阅云端书库与 AI 声线中转。
电脑版 / 手机网页版只连接你自己配置的服务器地址，代码里不写死任何服务器。

---

## What's inside / 包含什么

| Script | Purpose / 用途 |
|--------|----------------|
| `install_bookscan.sh` | Scan the `library` folder every minute and generate `books.json` / 每分钟扫描 library 文件夹，自动生成书单 |
| `install_del.sh` | Delete service with admin-key protection (`/wydel`) / 带密钥保护的删书服务 |
| `install_tts_proxy.sh` | edge-tts AI voice relay for phones (`/wytts`) / 手机 AI 声线中转 |
| `install_tts_route.sh` | Add the relay route to the Cloudflare tunnel / 把中转路由加进 Cloudflare 隧道 |
| `fix_tts_route.sh` | Repair / rewrite the tunnel config / 修复或重写隧道配置 |
| `install_epub_support.sh` + `update_books.py` | Auto-convert EPUB dropped into `library` / 自动把 EPUB 转成 txt 上架 |
| `install_bookfetcher.sh` | Optional: auto-fetch public-domain books daily / 可选：每天自动抓取公版书 |
| `install_morning_ai.sh` + `morning_news.py` | Optional: auto-generate today's morning news from public RSS feeds / 可选：每天自动从公开 RSS 生成早间新闻 |

## Install order / 安装顺序

1. Put these scripts in your web root, e.g. `/var/www/your-site/`.
2. Run `bash install_bookscan.sh`.
3. Run `sudo bash install_del.sh` — it will ask you for a **delete key**.
   Remember it; you will type it in the app when deleting a book.
4. (Optional, for AI voices on phones) Run
   `sudo bash install_tts_proxy.sh`, then `sudo bash install_tts_route.sh`.
5. Upload the phone web page (`tts.html`) to the same folder.

## Security notes / 安全提示

- **Change your delete key**: `install_del.sh` generates a random key if you
  don't set one. Keep it secret — it is the only thing that protects your
  books from deletion. / 删除密钥请务必保密，这是保护书库不被删的唯一凭据。
- The delete key is stored in a `.wydel_key` file on the server, never in the
  app code. / 密钥只存在服务器文件里，绝不写入软件代码。
- The `books.json` list and book files are public by design (anyone with your
  link can listen); deletion is protected by the key. / 书单和书默认公开
  （知道链接就能听），删除则需要密钥。
- All scripts assume a Cloudflare tunnel on `/root/.cloudflared/config.yaml`
  and a local web server. Adjust the variables at the top of each script to
  match your server. / 脚本假设使用 Cloudflare 隧道，路径可按需修改。

## How the app connects / 软件如何连接

- Desktop: Library → Cloud Library → Server Settings, enter `https://your-domain`.
- Phone: the web page itself is hosted on your server, so it needs no setup.
