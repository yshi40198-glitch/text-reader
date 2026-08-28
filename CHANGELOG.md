# Changelog / 更新日志

All notable changes are recorded here. Versions start from n2.1;
since v2.7 we unify all versions with the "v" prefix.
所有重要改动都会记录在这里，版本从 n2.1 开始编号；
自 v2.7 起，桌面版与手机版统一使用「v」前缀。

---

## [v3.0] - 2026-08

**Theme: remember where you stopped, and read even more formats.**
**主题：记住读到哪、想怎么读就怎么读。**

### Added / 新增
- Auto resume: the app remembers your reading position and asks
  "Continue?" when you open the book again / 自动记住阅读位置：
  关掉再打开，问"继续读吗"一键续读
- Custom pronunciation dictionary: force how names, brands and
  homographs are read (e.g. iPhone = ai-fon) / 自定义发音词典：
  人名、品牌、多音字按你指定的读法朗读
- MOBI / AZW / FB2 ebook formats (PalmDoc decompression built in) /
  新增 MOBI / AZW / FB2 电子书格式（内置 PalmDoc 解压，无需装软件）
- Morning news reminder: drop today's news file into the "早间新闻"
  folder and Weiyue offers to read it on startup / 早间新闻提醒：
  当天新闻放进「早间新闻」文件夹，打开软件就提示朗读
- AI-ready morning news: if a cloud server is configured, Weiyue also
  fetches today's news from the server automatically on startup /
  云端早间新闻：配置服务器后，薇阅启动时自动从服务器拉取当天新闻
- Cloud library change alert: Weiyue compares the book list on startup
  and notifies you when new books arrive (e.g. added by AI / scripts) /
  云端书库更新提醒：启动时自动对比书单，服务器上新书会提示
- Cloud library refresh button is now available in cloud mode /
  云端书库模式显示「刷新」按钮，随时重新拉取书单
- Tray menu "Morning News" opens the latest news file / 托盘菜单新增
  「早间新闻」，随时打开最新一期

### Changed / 改进
- Pronunciation dictionary applies to reading, follow-reading and
  audio export / 发音词典同时作用于朗读、跟读、导出音频
- Resume also saves when you press Stop or quit, and clears after
  finishing the whole book / 停止或退出时也保存进度，整本读完自动清除

### Benefits / 对使用者的帮助
- Never lose your place in a long audiobook / 长书听到一半再也不怕丢位置
- Correct readings for tricky names and words in one click / 多音字、
  人名、品牌想怎么读就怎么读
- Kindle / FB2 readers can listen directly without converting / 
  Kindle 和 FB2 书直接读，不用先转格式
- Open the app in the morning and your news is one click away /
  早上打开软件，新闻一键开读

### Security fixes / 安全修复（2026-08-28）
- Cloud delete now sends the admin key in the request body instead of the URL,
  so it no longer appears in server access logs / 云端删书密钥改为随请求体发送，
  不再出现在网址与访问日志里
- Tunnel configuration scripts back up config.yaml before modifying and keep
  existing routes / 隧道配置脚本修改前自动备份，并保留原有路由

---

## [v2.7] - 2026-08

**Theme: cloud library + repeater follow-reading, as complete as the phone version.**
**主题：云端书库 + 复读机跟读，功能追上手机版。**

### Added / 新增
- Cloud library built in: browse, read and delete books on the cloud server /
  云端书库内嵌：直接在电脑版浏览、朗读、删除云端书库的书
- Repeater mode for follow-reading: pause / resume / stop, repeat 1 / 3 / 5 / loop,
  gap 0.5 / 1 / 2 s, original-sentence duration, recording duration /
  跟读升级为复读机模式：暂停/继续/停止，复读 1/3/5 次或循环，
  间隔 0.5/1/2 秒，显示原句时长与录音时长
- Manual recording with live timer (3-minute cap) / 手动录音，实时计时，3 分钟上限
- Big-text mode for elderly users / 大字号模式，老人看得更清楚

### Changed / 改进
- Version naming unified with the phone version ("v" prefix) / 版本号与手机版统一（v 前缀）
- Previous/next sentence in follow-reading auto-plays the new sentence /
  跟读「上一句/下一句」自动连播，练习更顺手

### Benefits / 对使用者的帮助
- Desktop users can read and manage the cloud library without opening a browser /
  电脑上直接管理云端书库，不用再开网页
- Language learners get a real "repeater" like the old English-learning machines /
  学英语像用复读机：一句连听几遍，暂停对比，跟读更高效
- Seniors can enlarge the text with one click / 老人一键放大字号，看得更清楚

---

## [n2.6] - 2026-08

**Theme: translate, follow along, and read anything.**
**主题：翻译、跟读、什么都能读。**

### Added / 新增
- Text translation (Chinese <-> English) with "speak result" / 文本翻译（中英互译），可朗读译文
- Follow-reading recorder: listen -> repeat -> replay / 录音跟读：听原句 → 跟读 → 回放对比
- Image OCR: scan photos/screenshots/scanned pages, read text aloud offline / 图片识别：扫描图片文字并朗读（离线）
- Smart filter: auto-skip page numbers, headers and footers / 智能过滤：自动跳过页码、页眉页脚等杂音

### Changed / 改进
- Tool buttons (Translate / Follow / Image OCR) grouped with Mark buttons / 翻译、跟读、图片识别与标记按钮同排
- Following uses the currently selected voice / 跟读使用当前所选声线
- Translation auto-splits long text to stay within free API limits / 翻译自动分段，长文本也能翻
- OCR auto-resizes large images and retries on small text / 图片识别自动缩放、小字放大重试

### Benefits / 对使用者的帮助
- Learn English by listening to translations and recording your own voice / 听译文、录自己声音练口语
- Read printed pages and screenshots aloud / 纸质书页、截图也能"读"
- Cleaner listening experience without page-number noise / 朗读更干净，没有页码杂音

---

## [n2.5] - 2026-08

**Theme: prettier, smoother, and usable by more people.**
**主题：更美、更顺、更多人能用。**

### Added / 新增
- Bilingual interface (中文 / EN) with one-click switch / 中英双语界面，右上角一键切换
- Brand title: feather badge + "Weiyue" / 羽毛徽章 + 「薇阅」品牌标题
- Sunrise warm UI with embossed buttons / 朝阳暖色浮雕界面，按钮立体浮雕
- Background file loading — large docs no longer freeze / 后台读取文件，大文档不再卡死
- One-click desktop shortcut (fixed) / 桌面快捷方式一键创建（已修复）

### Changed / 改进
- Buttons grouped and equal-width; voice source + voice merged into one card / 朗读按钮等宽成组，「语音来源 + 声线」合并成一张卡片
- Speed slider replaced by quick presets (0.5x / 1x / 1.5x / 2x / 3x) / 速度滑杆改为快选按钮
- English buttons auto-widen so text is never cut off / 英文界面按钮自动加宽，文字完整显示
- Smoother speed changes while reading (AI voice) / 朗读中切换倍速更流畅

### Fixed / 修复
- Desktop shortcut script encoding / 桌面快捷方式脚本编码与解析错误
- White-screen UI build issue / 界面构建异常导致的白屏问题
- English button text truncation / 英文按钮文字显示不全

### Benefits / 对使用者的帮助
- Warm comfortable UI for long listening sessions / 暖色界面长时间听书不累
- English voices for listening & pronunciation practice / 英语声线练习听力、跟读发音
- Faster document loading / 打开大文件不再卡顿

---

## [n2.4] - 2026-08

### Added / 新增
- Bookmark: mark position and resume from mark / 打标记，从标记处继续朗读
- Smooth speed switching while reading / 阅读中切换倍速平滑生效

### Changed / 改进
- Speed range adjusted to 0.5x ~ 3x with noticeable difference / 倍速 0.5x~3x，真实可感
- Cleaner title & smaller font / 工具名精简、字体缩小
- 100% volume is real full volume / 音量 100% 为真实满音量

---

## [n2.2] - 2026-08

### Added / 新增
- Sleep timer (15 / 30 / 60 / 90 min) / 定时关闭
- Volume control / 音量调节
- Stable audio export (AI → MP3, local → WAV) / 稳定的音频输出

### Changed / 改进
- Minimalist UI with at most two colors / 极简界面，最多两种颜色
- Fixed volume being too quiet / 修复音量过小

---

## [n2.1] - 2026-08

### Added / 新增
- Speed presets 0.5x ~ 4x (later 0.5x ~ 3x) / 倍速预设
- First pass of industrial design / 整体工业设计

### Changed / 改进
- Noticeable speed differences / 倍速差异明显可感
- Cleaner layout, removed redundant elements / 布局精简，去掉冗余
