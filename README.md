# Weiyue · Text Reader（薇阅 · 文字朗读工具）

> Read with your ears — a warm, ready-to-use text-to-speech reader for Windows.

**English** | [中文文档](README.zh-CN.md)

Weiyue turns PDF, Word, EPUB, TXT — and even photos of printed pages — into
natural spoken audio. Whether it's a novel on your commute, work documents
late at night, or English articles for listening practice, Weiyue keeps you
company with a warm, human-like voice. **Free, open source, no installation.**

---

## 🎯 What it does for you

| Use case | How |
|----------|-----|
| 📖 **Audiobook / e-book listening** | Open EPUB / PDF / TXT, press "Read from Start" and finish whole books with your eyes closed; 1.5x is perfect for stories |
| 🖼️ **Read printed pages & screenshots** | Point the built-in OCR at a photo of a book page or a screenshot — the text is recognized offline and read aloud instantly |
| 🎧 **Chinese & English listening practice** | Translate Chinese <-> English in-app, listen to the translation, or follow along sentence by sentence with the recorder |
| 🎙️ **Follow-reading (speaking practice)** | Listen to a sentence, record your own voice, replay and compare — like having a speaking partner |
| 💼 **Business docs & meeting materials** | Skim Word / PDF briefs at 2x; mark key points and resume from the mark anytime |
| 🌙 **Sleep timer** | Auto-stop after 15 / 30 / 60 / 90 minutes — drift off while listening |

---

## ✨ n2.6 Highlights

- 🌐 **Text translation** (Chinese <-> English): long text is auto-split and
  translated reliably, with one-click "Speak Result"
- 🎙️ **Follow-reading recorder**: listen -> repeat -> replay and compare
- 🖼️ **Image OCR**: recognize text from photos, screenshots and scanned pages
  using the built-in Windows engine — **fully offline**
- 🧹 **Smart filter**: automatically skips page numbers, headers and footers
  while reading, for a cleaner listening experience
- 🌍 **Bilingual interface**: one-click switch between 中文 and English
- ⚡ Fast startup and non-blocking file loading

Full history: [CHANGELOG.md](CHANGELOG.md)

---

## ✨ Features

- Open PDF / Word (.docx / .doc) / txt / md / EPUB / HTML and read aloud
- Image OCR (PNG / JPG / BMP / WEBP / TIFF), auto-resize for large photos,
  auto-retry with 2x zoom for small text
- Text translation (Chinese <-> English) with speakable result
- Follow-reading: listen to each sentence, record and replay your voice
- Read from start / from cursor / selection / from mark
- Speed presets 0.5x ~ 3x, smooth switching while reading
- Volume 0~100%, sleep timer (15 / 30 / 60 / 90 min)
- Bookmark: mark where you are, resume anytime
- Export audio: AI voice to MP3 / local voice to WAV (auto retry)
- Progress bar + reading-paragraph highlight, system tray, desktop shortcut
- Full edit menus (cut / copy / paste / delete) everywhere text is editable

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

> Note: Image OCR uses the Windows built-in OCR engine — make sure the
> "Chinese (Simplified) OCR" language pack is installed in Windows settings.

---

## 🧩 Tech Stack

- UI: Python Tkinter (warm sunrise theme, embossed buttons)
- AI voice: edge-tts (neural voices, requires internet)
- Offline fallback: Windows SAPI system voices
- OCR: Windows.Media.Ocr (offline, built-in engine)
- Recording: sounddevice / numpy
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
