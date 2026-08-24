# Changelog / 更新日志

All notable changes are recorded here. Versions start from n2.1.
所有重要改动都会记录在这里，版本从 n2.1 开始编号。

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
