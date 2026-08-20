# Weiyue · Text Reader（薇阅 · 文字朗读工具）

> Read with your ears — a warm, ready-to-use text-to-speech reader for Windows.

**English** | [中文文档](README.zh-CN.md)

Weiyue reads PDF, Word, EPUB and TXT out loud in natural voices. Whether it's
a novel on your commute, work documents late at night, or English articles
for listening practice, Weiyue keeps you company with a warm, human-like voice.

---

## 🎯 What it does for you

| Use case | How |
|----------|-----|
| 📖 **Audiobook / e-book listening** | Open EPUB / PDF / TXT, press "Read from Start" and finish whole books with your eyes closed; 1.5x is perfect for stories |
| 🎧 **Chinese & English listening practice** | Pick an English voice (Aria / Guy / Jenny / Sonia), slow down to 0.5x and follow along for pronunciation |
| 💼 **Business docs & meeting materials** | Skim Word / PDF briefs at 2x; mark key points and resume from the mark anytime |
| 🌙 **Sleep timer** | Auto-stop after 15 / 30 / 60 / 90 minutes — drift off while listening |
| ✍️ **Screen-free reading** | Give your eyes a break: turn text into voice and listen while doing chores |

---

## ✨ n2.5 Highlights

- 🌅 **Sunrise warm UI**: cream background, apricot-orange accents, embossed buttons
- 🌍 **Bilingual interface**: one-click switch between 中文 and English
- 🪶 **Brand title**: feather badge + "Weiyue"
- ⚡ **Non-blocking file loading**: large documents no longer freeze the app
- 🖱️ **One-click desktop shortcut** (fixed)
- 🔊 **60+ AI voices** (Mandarin, English, Cantonese, Taiwanese...), auto fallback to local voice when offline

Full history: [CHANGELOG.md](CHANGELOG.md)

---

## ✨ Features

- Open PDF / Word (.docx / .doc) / txt / md / EPUB / HTML and read aloud
- Read from start / from cursor / selection / from mark
- Speed presets 0.5x ~ 3x, smooth switching while reading
- Volume 0~100%, sleep timer (15 / 30 / 60 / 90 min)
- Bookmark: mark where you are, resume anytime
- Export audio: AI voice to MP3 / local voice to WAV (auto retry)
- Progress bar + reading-paragraph highlight, system tray, desktop shortcut

---

## 🚀 Quick Start

### End users (recommended)
Download the latest zip from **Releases**, unzip it, then double-click
**「启动朗读工具.bat」** — no Python installation needed.

### Developers (from source)
```bash
pip install -r requirements.txt
python textreader_app.py
```

---

## 🧩 Tech Stack

- UI: Python Tkinter (warm sunrise theme, embossed buttons)
- AI voice: edge-tts (neural voices, requires internet)
- Offline fallback: Windows SAPI system voices
- Text extraction: PyMuPDF / python-docx / HTMLParser

---

## 🤝 Contributing

Contributions of all kinds are welcome — bug reports, feature ideas, or pull
requests that make Weiyue better.

1. Found a problem or have an idea? Open an [Issue](../../issues)
2. Want to improve the code? Fork the repo and submit a [Pull Request](../../pulls)
3. Like it? Give it a ⭐ so more people can find it

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

[MIT License](LICENSE) — free to use, modify and distribute.
