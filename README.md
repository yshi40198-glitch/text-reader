# Weiyue · Text Reader（薇阅 · 文字朗读工具）

> Read with your ears — a warm, ready-to-use text-to-speech reader for Windows.

**English** | [中文文档](README.zh-CN.md)

Weiyue turns PDF, Word, EPUB, MOBI, FB2, TXT — and even photos of printed pages —
into natural spoken audio. Whether it's a novel on your commute, work documents
late at night, or English articles for listening practice, Weiyue keeps you
company with a warm, human-like voice.
**Free · Open source · No installation · Unzip and go.**

---

## 1. What it does for you

| Use case | How |
|----------|-----|
| 📖 **Audiobook / e-book listening** | Open EPUB / PDF / TXT / MOBI / FB2, press "Read from Start" and finish whole books with your eyes closed; reopen and it asks "Continue?" right where you stopped |
| 🖼️ **Read printed pages & screenshots** | Point the built-in OCR at a photo of a book page or a screenshot — the text is recognized offline and read aloud instantly |
| 🎧 **Chinese & English listening practice** | Translate Chinese <-> English in-app, listen to the translation, or follow along sentence by sentence |
| 🎙️ **Follow-reading (speaking practice)** | Listen to a sentence, record your own voice, replay and compare — like having a speaking partner |
| 💼 **Business docs & meeting materials** | Skim Word / PDF briefs at 2x; mark key points and resume anytime |
| 🌙 **Sleep timer** | Auto-stop after 15 / 30 / 60 / 90 minutes |
| ☁️ **Cloud library · multi-device sync** | Users with their own server (VPS) can connect a cloud library and read the same books on PC and phone |
| 🤖 **AI / automation ready** | AI agents or scripts on your server can drop books and news into the cloud library; Weiyue detects new content and offers to read it |

---

## 2. Quick start (3 steps)

1. Download the latest zip from **Releases** and unzip it.
2. Double-click 「创建桌面快捷方式.bat」 to create a desktop shortcut.
3. Open the app, choose a document, press "Read from Start".

> No Python installation needed — fully portable.

---

## 3. Reading & controls (most used)

### Three ways to read
- **Read from Start**: read the whole document from the beginning.
- **Read from Cursor**: click a position in the text, then read from there.
- **Read Selection**: select a passage with the mouse, then read only that part.

Right-click the text for a context menu: read from here, read selection,
cut / copy / paste / delete / select all.

### Shortcuts
- `Ctrl+O` open file
- `Ctrl+P` pause / resume
- `Esc` stop

### Listening controls
- **Speed**: presets 0.5 / 1 / 1.5 / 2 / 3x, switching works while reading.
- **Volume**: slider 0–100%.
- **Voices**: AI neural voices (60+, requires internet); local system voices (offline).
- **Sleep timer**: 15 / 30 / 60 / 90 minutes.

---

## 4. Never lose your place

### Auto resume
- Close the app mid-book and it asks "Continue?" on the next launch.
  One click and you're back where you stopped.
- Progress also saves on Stop / quit and clears after finishing the whole book.

### Bookmarks
- Press "Mark" at a key point, then "Read from Mark" anytime.

### Pronunciation dictionary
- Add "word = reading" pairs (e.g. iPhone = ai-fon) for names, brands and
  homographs. Applies to reading, follow-reading and audio export.

---

## 5. Library

### Local library
- Choose a folder of e-books (Calibre library or your own novels folder).
- Weiyue scans automatically and lists title / author / format; double-click to
  read. Remembers your last folder.
- Supports EPUB / PDF / Word / TXT / MOBI / FB2 / HTML.
- **Delete & recycle bin**: press "Delete Book" to move a book to the recycle
  bin; the recycle bin lets you "Restore" or "Delete Forever".

### Cloud library (connect your own VPS)
- Weiyue connects to **no server by default** — fully local and private.
- If you have your own server (VPS), open "Library → Cloud Library → Server
  Settings" and enter your server address:
  - Read the same books on PC and phone.
  - When new books or news appear on the server, Weiyue notifies you
    ("Cloud library has new content").
  - Deleting cloud books requires an admin key (never embedded in the code).
- Server-side components live in the `server/` directory (book scan, voice
  relay, EPUB conversion, etc.) for those who want to self-host. Weiyue only
  connects to the server you configure — never to any third party.

---

## 6. Learning features

### Translation
- Translate Chinese <-> English in-app; long text is auto-split; results can be
  read aloud with pause / stop.

### Follow-reading (repeater mode)
- Open an article, then "Follow": listen to each sentence (pause / resume /
  stop, repeat 1 / 3 / 5 times or loop).
- Record your own reading, replay and compare. 3-minute cap per recording;
  recordings live in memory only.

### Image OCR
- Recognize text from photos, screenshots and scanned pages using the built-in
  Windows engine — fully offline.

### Smart filter (automatic)
- Skips page numbers, headers and footers while reading for a cleaner listen.

---

## 7. Export audio

- Export AI voice to MP3 or local voice to WAV; long documents retry
  automatically.

---

## 8. Morning news (AI / automation friendly)

- A 「早间新闻」 folder is created next to the app: drop today's news
  (txt/md) in and Weiyue offers to read it on startup.
- With a cloud server configured, Weiyue also fetches today's news from the
  server's 「早间新闻」 folder automatically (great for AI agents or scripts
  that generate news daily).
- The tray menu also opens the latest news anytime.

---

## 9. Other features

- **Bilingual UI**: one-click switch between 中文 and English.
- **Big-text mode**: enlarge the reader with one click, easier for seniors.
- **System tray**: closing minimizes to tray (reading continues); tray menu
  offers pause / stop / morning news / quit.
- **Read a link**: paste a news/article URL and read the extracted text aloud.
- **Config file**: `weiyue_config.json` stores your settings (library folder,
  pronunciation dictionary, server address, etc.) — back it up to keep settings.

---

## 10. Developers: run from source

```bash
pip install -r requirements.txt
python textreader_app.py
```

> Note: Image OCR uses the Windows built-in OCR engine — make sure the
> "Chinese (Simplified) OCR" language pack is installed in Windows settings.

---

## 11. Tech stack

- UI: Python Tkinter (warm sunrise theme, embossed buttons)
- AI voice: edge-tts (neural voices, requires internet)
- Offline fallback: Windows SAPI system voices
- OCR: Windows.Media.Ocr (offline, built-in engine)
- Recording: sounddevice / numpy
- Text extraction: PyMuPDF / python-docx / HTMLParser / built-in MOBI & FB2
- Cloud: configurable server address, no server connected by default

---

## 12. Contributing

Contributions of all kinds are welcome — bug reports, feature ideas, or pull
requests that make Weiyue better.

1. Found a problem or have an idea? Open an [Issue](../../issues)
2. Want to improve the code? Fork the repo and submit a [Pull Request](../../pulls)
3. Like it? Give it a ⭐ so more people can find it

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 13. License

[MIT License](LICENSE) — free to use, modify and distribute.
