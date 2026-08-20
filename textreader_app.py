# -*- coding: utf-8 -*-
"""月薇阁 · 文字朗读工具 n2.5（极简黑白风格 · AI 神经网络语音 · 中英双语 · 便携版）

功能:
- 打开 PDF / Word / txt → 从头朗读
- 从光标朗读 / 朗读选中 / 右键快捷菜单
- AI 神经网络语音（edge-tts，自然逼真，需联网），断网自动用本地语音
- 倍速 0.5x ~ 3.0x（两级变速：合成变速 + 播放变速，真实可感）
- 实时进度条 + 正在朗读的段落高亮
- 导出 MP3（AI 语音）/ WAV（本地语音）
- 系统托盘：关窗口最小化，朗读不中断
"""
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from extract import extract_text, clean_for_speech, split_chunks
from speaker import Speaker

# ---------- 多语言界面 ----------
UI = {
    'zh': {
        'title': '薇阅 · 文字朗读工具 n2.5',
        'app_title': '薇阅',
        'app_sub': '文字朗读工具',
        'btn_en': 'EN',
        'open': '打开文件',
        'no_file': '未打开文件',
        'ready': '就绪',
        'read_all': '从头朗读',
        'read_cursor': '从光标朗读',
        'read_sel': '朗读选中',
        'read_mark': '从标记朗读',
        'pause': '暂停',
        'stop': '停止',
        'export': '导出音频',
        'clear': '清空',
        'mark': '打标记',
        'speed': '速度',
        'quick': '快选',
        'voice_src': '语音来源',
        'engine_neural': 'AI 网络语音（推荐）',
        'engine_sapi': '本地系统语音',
        'voice': '声线',
        'timer': '定时关闭',
        'timer_off': '关闭',
        'timer_15': '15 分钟',
        'timer_30': '30 分钟',
        'timer_60': '60 分钟',
        'timer_90': '90 分钟',
        'volume': '音量',
        'not_started': '尚未开始',
        'no_voices': '(无可用语音)',
        'ctx_here': '从这里开始朗读',
        'ctx_sel': '朗读选中内容',
        'tray_show': '打开界面',
        'tray_pause': '暂停 / 继续',
        'tray_stop': '停止朗读',
        'tray_quit': '退出',
        'ai_ready': 'AI 网络语音已就绪（联网）',
        'ai_fallback': 'AI 网络语音不可用，已自动改用本地语音',
        'local_ready': '本地系统语音已就绪（离线）',
        'voice_switched': '已切换声线：',
        'tray_min': '已最小化到托盘，点图标呼出',
        'volume_set': '音量 %d%%',
        'loading': '正在读取…',
        'timer_off_msg': '定时关闭：已关闭',
        'timer_set': '定时关闭：%d 分钟后停止朗读',
        'timer_left': '剩余 %02d:%02d',
        'timer_fire': '定时关闭：时间到，朗读已停止',
        'speed_set': '速度 %.1fx（0.5x 慢速 / 3x 高速）',
        'loaded': '已载入 %d 字',
        'cleared': '已清空',
        'marked': '已标记：第 %d 字处',
        'marked_hint': '已打标记，可随时点「从标记朗读」继续',
        'paused_msg': '已暂停，点继续',
        'resuming': '继续朗读…',
        'stopped': '已停止',
        'exporting': '正在生成音频…（长文档需要几分钟）',
        'lang_switched': '界面语言已切换为 English',
        'progress': '%s · 第 %d / %d 段',
        'dlg_tip': '提示',
        'dlg_err': '读取失败',
        'dlg_speech_init': '语音初始化失败',
        'dlg_open_first': '请先打开一个文档',
        'dlg_cursor_end': '光标已在文档末尾，没有可读的内容',
        'dlg_no_mark': '还没有打标记，请先点「打标记」',
        'dlg_mark_end': '标记已在文档末尾，没有可读的内容',
        'dlg_no_read': '没有可朗读的文字',
        'dlg_doc_read_title': '无法读取此 .doc',
        'dlg_doc_read_body': '这个旧版 Word 文档（.doc）没能读出文字。\n\n'
                             '解决办法：用 Word 打开它 → 另存为 → 选「Word 文档 (*.docx)」'
                             '→ 再用本工具打开。\n（.docx 是最稳定的格式，建议所有 Word 都用它）',
        'dlg_no_text': '这个文件里没读到文字。\n'
                       '（PDF 如果是扫描件/图片，需 OCR，暂不支持）',
        'dlg_export_result': '导出结果',
        'export_info': '文件：%s\n大小：%.1f MB\n时长约：%d 分 %d 秒',
        'dlg_open_title': '选择要朗读的文件',
        'dlg_save_title': '保存朗读音频',
        'ft_docs': '支持的文档',
        'ft_pdf': 'PDF',
        'ft_word': 'Word',
        'ft_epub': '电子书',
        'ft_web': '网页',
        'ft_text': '文本',
        'ft_all': '所有文件',
        'ft_mp3': 'MP3 音频',
        'ft_wav': 'WAV 音频',
    },
    'en': {
        'title': 'Weiyue Text Reader n2.5',
        'app_title': '薇阅',
        'app_sub': 'Text Reader',
        'btn_en': '中',
        'open': 'Open File',
        'no_file': 'No file opened',
        'ready': 'Ready',
        'read_all': 'Read from Start',
        'read_cursor': 'Read from Cursor',
        'read_sel': 'Read Selection',
        'read_mark': 'Read from Mark',
        'pause': 'Pause',
        'stop': 'Stop',
        'export': 'Export Audio',
        'clear': 'Clear',
        'mark': 'Mark',
        'speed': 'Speed',
        'quick': 'Quick',
        'voice_src': 'Voice Source',
        'engine_neural': 'AI Neural Voice (Recommended)',
        'engine_sapi': 'System Voice (Offline)',
        'voice': 'Voice',
        'timer': 'Timer',
        'timer_off': 'Off',
        'timer_15': '15 min',
        'timer_30': '30 min',
        'timer_60': '60 min',
        'timer_90': '90 min',
        'volume': 'Volume',
        'not_started': 'Not started',
        'no_voices': '(No voices available)',
        'ctx_here': 'Read from Here',
        'ctx_sel': 'Read Selected Text',
        'tray_show': 'Show Window',
        'tray_pause': 'Pause / Resume',
        'tray_stop': 'Stop Reading',
        'tray_quit': 'Quit',
        'ai_ready': 'AI neural voice ready (online)',
        'ai_fallback': 'AI neural voice unavailable, using local voice',
        'local_ready': 'Local system voice ready (offline)',
        'voice_switched': 'Voice switched: ',
        'tray_min': 'Minimized to tray, click icon to show',
        'volume_set': 'Volume %d%%',
        'loading': 'Loading...',
        'timer_off_msg': 'Timer: off',
        'timer_set': 'Timer: stop reading in %d min',
        'timer_left': 'Left %02d:%02d',
        'timer_fire': 'Timer: time is up, reading stopped',
        'speed_set': 'Speed %.1fx (0.5x slow / 3x fast)',
        'loaded': 'Loaded %d characters',
        'cleared': 'Cleared',
        'marked': 'Marked at character %d',
        'marked_hint': 'Marked. Use "Read from Mark" to continue later',
        'paused_msg': 'Paused, click to resume',
        'resuming': 'Resuming...',
        'stopped': 'Stopped',
        'exporting': 'Generating audio... (long documents may take minutes)',
        'lang_switched': 'Interface language switched to Chinese',
        'progress': '%s - Segment %d / %d',
        'dlg_tip': 'Notice',
        'dlg_err': 'Read Failed',
        'dlg_speech_init': 'Voice init failed',
        'dlg_open_first': 'Please open a document first',
        'dlg_cursor_end': 'Cursor is at the end of the document',
        'dlg_no_mark': 'No mark yet. Click "Mark" first',
        'dlg_mark_end': 'Mark is at the end of the document',
        'dlg_no_read': 'Nothing to read',
        'dlg_doc_read_title': 'Cannot read this .doc',
        'dlg_doc_read_body': 'This old Word file (.doc) could not be read.\n\n'
                             'Fix: open it in Word, choose Save As, select '
                             '"Word Document (*.docx)", then open it here.\n'
                             '(.docx is the most reliable format.)',
        'dlg_no_text': 'No text found in this file.\n'
                       '(Scanned/image PDFs need OCR, not supported yet)',
        'dlg_export_result': 'Export Result',
        'export_info': 'File: %s\nSize: %.1f MB\nDuration: %d min %d s',
        'dlg_open_title': 'Choose a file to read',
        'dlg_save_title': 'Save audio',
        'ft_docs': 'Supported documents',
        'ft_pdf': 'PDF',
        'ft_word': 'Word',
        'ft_epub': 'eBook',
        'ft_web': 'Web',
        'ft_text': 'Text',
        'ft_all': 'All files',
        'ft_mp3': 'MP3 audio',
        'ft_wav': 'WAV audio',
    },
}

# ---------- 配色：朝阳暖色 · 奶油底 + 杏橙浮雕 ----------
COL_BG     = "#FFF9F0"   # 奶油白底
COL_PANEL  = "#FFFDF8"   # 面板米白
COL_PANEL2 = "#FFEAD0"   # 浅杏
COL_BLACK  = "#4A2F17"   # 暖棕文字
COL_GRAY   = "#B58A5A"   # 暖灰橙
COL_LINE   = "#EBC79B"   # 暖色分隔
COL_RED    = "#B2682E"   # 暖橙
COL_YELLOW = "#B2682E"
COL_BLUE   = "#B2682E"
COL_HL     = "#FFE2BA"   # 阅读段落高亮（朝阳金）
COL_ACCENT = "#FF9E45"   # 强调橙（进度/状态条）
FONT = "Microsoft YaHei"


def _f(size, bold=False):
    return (FONT, size, "bold" if bold else "normal")


def _make_tray_icon():
    """托盘图标：优先用同目录 assets 里的金色羽毛图标，失败回退手绘喇叭。"""
    here = os.path.dirname(os.path.abspath(__file__))
    png = os.path.join(here, 'assets', 'feather_tray.png')
    ico = os.path.join(here, 'assets', 'app.ico')
    try:
        from PIL import Image
        if os.path.exists(png):
            return Image.open(png).convert('RGBA')
        if os.path.exists(ico):
            return Image.open(ico).convert('RGBA')
    except Exception:
        pass
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.polygon([(8, 26), (22, 26), (34, 14), (34, 50), (22, 38), (8, 38)],
                  fill=(17, 17, 17, 255))
        d.arc((30, 10, 56, 34), -60, 60, fill=(17, 17, 17, 255), width=4)
        d.arc((34, 4, 62, 40), -60, 60, fill=(17, 17, 17, 255), width=4)
        return img
    except Exception:
        return None


class App:
    def __init__(self, root):
        self.root = root
        self.lang = 'zh'
        self.root.title(UI['zh']['title'])
        self.root.geometry("980x760")
        self.root.minsize(760, 580)
        self.root.configure(bg=COL_BG)

        self.current_path = None
        self.full_text = ""
        self.speech_chunks = []
        self._chunk_ranges = []
        self.speaker = None
        self.engine_mode = 'neural'   # 'neural'=AI网络语音, 'sapi'=本地语音
        self._speed_mult = 1.0
        self._volume = 100
        self._timer_minutes = 0
        self._timer_remaining = 0
        self._timer_job = None
        self._export_busy = False
        self._reading_label = 'read_all'
        self._mark_offset = None
        self._current_chunk = 0

        self._set_window_icon()
        self._build_ui()
        self._setup_tray()
        self._bind_shortcuts()
        try:
            root.after(300, self._refresh_voices)
        except Exception:
            pass

    # ---------- 多语言 ----------
    def T(self, key, *args):
        msg = UI.get(self.lang, UI['zh']).get(key, key)
        return msg % args if args else msg

    def _make_logo_image(self):
        """生成圆形羽毛徽章（36x36 暖色底），失败返回 None。"""
        try:
            from PIL import Image, ImageDraw, ImageTk
            here = os.path.dirname(os.path.abspath(__file__))
            png = os.path.join(here, 'assets', 'feather_512.png')
            if not os.path.exists(png):
                png = os.path.join(here, 'assets', 'feather_tray.png')
            if not os.path.exists(png):
                return None
            img = Image.open(png).convert('RGBA').resize((36, 36),
                                                         Image.LANCZOS)
            mask = Image.new('L', (36, 36), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 36, 36), fill=255)
            out = Image.new('RGBA', (36, 36), (255, 253, 248, 255))
            out.paste(img, (0, 0), mask)
            return ImageTk.PhotoImage(out)
        except Exception:
            return None

    def _toggle_lang(self):
        self.lang = 'en' if self.lang == 'zh' else 'zh'
        if self.speaker is not None:
            try:
                self.speaker.set_language(self.lang)
            except Exception:
                pass
        self._apply_lang()
        self.state_lbl.config(text=self.T('lang_switched'), fg=COL_GRAY)

    def _apply_lang(self):
        """把当前界面所有静态文字刷新为 self.lang。"""
        self.root.title(self.T('title'))
        if getattr(self, 'title_lbl', None):
            self.title_lbl.config(text=self.T('app_title'))
        if getattr(self, 'title_sub_lbl', None):
            self.title_sub_lbl.config(text=self.T('app_sub'))
        if getattr(self, 'lang_btn', None):
            self.lang_btn.config(text=self.T('btn_en'))
        self.btn_open.config(text=self.T('open'))
        self.btn_export.config(text=self.T('export'))
        self.file_lbl.config(text=self.T('no_file') if not self.current_path
                             else os.path.basename(self.current_path))
        btn_w = 17 if self.lang == 'en' else 10
        for key, (b, s) in getattr(self, "_read_btns", {}).items():
            b.config(text=self.T(key), width=btn_w)
        self.btn_pause.config(text=self.T('pause'))
        self.btn_stop.config(text=self.T('stop'))
        self.btn_clear.config(text=self.T('clear'), width=btn_w)
        self.btn_mark.config(text=self.T('mark'))
        self.btn_read_mark.config(text=self.T('read_mark'))
        self.lbl_quick.config(text=self.T('quick'))
        self.lbl_voice_src.config(text=self.T('voice_src'))
        self.lbl_voice.config(text=self.T('voice'))
        self.lbl_timer.config(text=self.T('timer'))
        self.lbl_volume.config(text=self.T('volume'))
        try:
            idx = self.engine_combo.current()
            self.engine_combo['values'] = [self.T('engine_neural'),
                                           self.T('engine_sapi')]
            if idx >= 0:
                self.engine_combo.current(idx)
        except Exception:
            pass
        try:
            idx = self.timer_combo.current()
            self.timer_combo['values'] = [self.T('timer_off'), self.T('timer_15'),
                                          self.T('timer_30'), self.T('timer_60'),
                                          self.T('timer_90')]
            if idx >= 0:
                self.timer_combo.current(idx)
        except Exception:
            pass
        self._apply_ctx_lang()
        self._apply_tray_lang()

    def _apply_ctx_lang(self):
        try:
            self._ctx.delete(0, 'end')
            self._ctx.add_command(label=self.T('ctx_here'),
                                  command=self.read_from_cursor)
            self._ctx.add_command(label=self.T('ctx_sel'),
                                  command=self.read_selection)
        except Exception:
            pass

    def _apply_tray_lang(self):
        try:
            if self._tray is None:
                return
            import pystray
            menu = pystray.Menu(
                pystray.MenuItem(self.T('tray_show'), self._tray_show, default=True),
                pystray.MenuItem(self.T('tray_pause'), self._tray_pause),
                pystray.MenuItem(self.T('tray_stop'), self._tray_stop),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(self.T('tray_quit'), self._tray_quit),
            )
            self._tray.menu = menu
            self._tray.title = self.T('title')
        except Exception:
            pass

    # ---------- 语音列表 ----------
    def _refresh_voices(self):
        """后台拉取当前引擎的声线列表（AI 引擎顺便探测网络）。"""
        def work():
            try:
                sp = self._get_speaker()
                if sp is None:
                    return
                voices = sp.list_voices()
                active = sp.active_engine
                cur = sp.current_voice_id()
                self.root.after(0, lambda: self._apply_voices(voices, active, cur))
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    def _apply_voices(self, voices, active, cur):
        try:
            names = [v['name'] for v in voices]
            self._voice_list = voices
            self.voice_combo['values'] = names
            if not names:
                self.voice_combo.set(self.T('no_voices'))
            else:
                found = False
                for i, v in enumerate(voices):
                    if v['id'] == cur:
                        try:
                            self.voice_combo.current(i)
                        except Exception:
                            pass
                        found = True
                        break
                if not found:
                    try:
                        self.voice_combo.current(0)
                    except Exception:
                        pass
        except Exception:
            pass
        if active == 'neural':
            self.state_lbl.config(text=self.T('ai_ready'), fg=COL_BLUE)
        else:
            if self.engine_mode == 'neural':
                self.state_lbl.config(
                    text=self.T('ai_fallback'), fg=COL_RED)
            else:
                self.state_lbl.config(text=self.T('local_ready'), fg=COL_GRAY)

    def _on_voice_change(self, _e=None):
        try:
            idx = self.voice_combo.current()
            if idx < 0:
                return
            if not hasattr(self, '_voice_list') or idx >= len(self._voice_list):
                self._refresh_voices()
                return
            vid = self._voice_list[idx]['id']
            sp = self._get_speaker()
            if sp and sp.set_voice(vid):
                self.state_lbl.config(text=self.T('voice_switched')
                                      + self.voice_combo.get(),
                                      fg=COL_BLUE)
        except Exception:
            pass

    def _on_engine_change(self, _e=None):
        mode = 'neural' if self.engine_combo.current() == 0 else 'sapi'
        self.engine_mode = mode
        if self.speaker is not None:
            self.speaker.stop()
            self.speaker.set_engine_mode(mode)
        self._refresh_voices()

    # ---------- 窗口图标 ----------
    def _set_window_icon(self):
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(here, 'assets', 'app.ico')
            png = os.path.join(here, 'assets', 'feather_tray.png')
            if os.path.exists(ico):
                try:
                    self.root.iconbitmap(ico)
                except Exception:
                    pass
            if os.path.exists(png):
                try:
                    self.root.iconphoto(False, tk.PhotoImage(file=png))
                except Exception:
                    pass
        except Exception:
            pass

    # ---------- UI ----------
    def _build_ui(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Min.Horizontal.TScale",
                        background=COL_BLACK, troughcolor=COL_LINE,
                        sliderlength=20, sliderrelief='flat')
        style.map("Min.Horizontal.TScale",
                  background=[('active', COL_BLACK), ('pressed', COL_BLACK)])
        style.configure("Min.Horizontal.TProgressbar",
                        troughcolor=COL_LINE, background=COL_ACCENT,
                        bordercolor=COL_ACCENT,
                        lightcolor=COL_ACCENT, darkcolor=COL_ACCENT)
        style.configure("Min.TCombobox",
                        fieldbackground=COL_PANEL, background=COL_PANEL,
                        foreground=COL_BLACK, arrowcolor=COL_BLACK,
                        bordercolor=COL_LINE, lightcolor=COL_PANEL,
                        darkcolor=COL_LINE, padding=3)
        style.map("Min.TCombobox",
                  fieldbackground=[('readonly', COL_PANEL)],
                  foreground=[('readonly', COL_BLACK)])
        style.configure("Min.TScrollbar", background=COL_BLACK,
                        troughcolor=COL_LINE, arrowcolor=COL_BLACK)

        # ===== 顶栏：品牌标题（徽章 + 薇阅）+ 语言切换（疏） =====
        header = tk.Frame(self.root, bg=COL_BG)
        header.pack(fill=tk.X, padx=30, pady=(22, 6))

        title_block = tk.Frame(header, bg=COL_BG)
        title_block.pack(side=tk.LEFT)
        brand = tk.Frame(title_block, bg=COL_BG)
        brand.pack(anchor="w")
        self._logo_img = self._make_logo_image()
        if self._logo_img is not None:
            logo = tk.Label(brand, image=self._logo_img, bg=COL_PANEL2,
                            relief="raised", bd=1,
                            highlightbackground=COL_LINE,
                            highlightthickness=2)
            logo.pack(side=tk.LEFT, padx=(0, 14))
        tb = tk.Frame(brand, bg=COL_BG)
        tb.pack(side=tk.LEFT)
        self.title_lbl = tk.Label(tb, text=self.T('app_title'),
                                  bg=COL_BG, fg=COL_BLACK, font=_f(22, True))
        self.title_lbl.pack(anchor="w")
        self.title_sub_lbl = tk.Label(tb, text=self.T('app_sub'),
                                      bg=COL_BG, fg=COL_GRAY,
                                      font=_f(10, True))
        self.title_sub_lbl.pack(anchor="w", pady=(3, 0))

        self.lang_btn = self._flat_btn(header, self.T('btn_en'), COL_PANEL,
                                       COL_BLACK, self._toggle_lang,
                                       padx=16, pady=6, font_size=10)
        self.lang_btn.pack(side=tk.RIGHT, anchor="ne")

        # ===== 文件行（疏） =====
        file_row = tk.Frame(self.root, bg=COL_BG)
        file_row.pack(fill=tk.X, padx=30, pady=(12, 4))
        self.btn_open = self._flat_btn(file_row, self.T('open'), COL_PANEL,
                                       COL_BLACK, self.open_file, padx=16)
        self.btn_open.pack(side=tk.LEFT)
        self.file_lbl = tk.Label(file_row, text=self.T('no_file'), bg=COL_BG,
                                 fg=COL_GRAY, font=_f(11))
        self.file_lbl.pack(side=tk.LEFT, padx=14)
        self.state_lbl = tk.Label(file_row, text=self.T('ready'), bg=COL_BG,
                                  fg=COL_GRAY, font=_f(10))
        self.state_lbl.pack(side=tk.RIGHT)

        # ===== 朗读行（密）：从头 / 光标 / 选中 / 清空，等宽 =====
        act = tk.Frame(self.root, bg=COL_BG)
        act.pack(fill=tk.X, padx=30, pady=(10, 4))
        self._read_btns = {}
        for key, cmd in (("read_all", self.read_all),
                         ("read_cursor", self.read_from_cursor),
                         ("read_sel", self.read_selection)):
            w, b, s = self._flat_btn_box(act, self.T(key), COL_PANEL, COL_BLACK,
                                         cmd, padx=0, font_size=12, width=10)
            w.pack(side=tk.LEFT, padx=6)
            self._read_btns[key] = (b, s)
        wc, bc, sc = self._flat_btn_box(act, self.T('clear'), COL_PANEL,
                                        COL_BLACK, self.clear_text,
                                        padx=0, font_size=12, width=10)
        wc.pack(side=tk.LEFT, padx=6)
        self.btn_clear = bc

        # ===== 倍速快选 + 控制按钮（中密） =====
        quick_row = tk.Frame(self.root, bg=COL_BG)
        quick_row.pack(fill=tk.X, padx=30, pady=(4, 0))
        self.lbl_quick = tk.Label(quick_row, text=self.T('quick'), bg=COL_BG,
                                  fg=COL_GRAY, font=_f(10))
        self.lbl_quick.pack(side=tk.LEFT, padx=(2, 12))
        self._speed_btns = {}
        for m in (0.5, 1.0, 1.5, 2.0, 3.0):
            label = ("%g×" % m)
            b = self._flat_btn(quick_row, label, COL_PANEL, COL_BLACK,
                               lambda x=m: self._preset_speed(x),
                               padx=11, pady=5, font_size=10)
            b.pack(side=tk.LEFT, padx=3)
            self._speed_btns[m] = b
        self._update_preset_highlight()
        ctrl = tk.Frame(quick_row, bg=COL_BG)
        ctrl.pack(side=tk.LEFT, padx=(24, 0))
        self.btn_pause = self._flat_btn(ctrl, self.T('pause'), COL_PANEL,
                                        COL_BLACK, self.toggle_pause,
                                        padx=12, pady=5, font_size=11)
        self.btn_pause.pack(side=tk.LEFT, padx=3)
        self.btn_stop = self._flat_btn(ctrl, self.T('stop'), COL_PANEL,
                                       COL_BLACK, self.stop,
                                       padx=12, pady=5, font_size=11)
        self.btn_stop.pack(side=tk.LEFT, padx=3)
        self.btn_export = self._flat_btn(ctrl, self.T('export'), COL_PANEL,
                                         COL_BLACK, self.export_audio,
                                         padx=12, pady=5, font_size=11)
        self.btn_export.pack(side=tk.LEFT, padx=3)

        # ===== 标记行（疏）：打标记 / 从标记朗读 =====
        mark_row = tk.Frame(self.root, bg=COL_BG)
        mark_row.pack(fill=tk.X, padx=30, pady=(10, 0))
        self.btn_mark = self._flat_btn(mark_row, self.T('mark'), COL_PANEL,
                                       COL_BLACK, self.mark_position,
                                       padx=12, pady=5, font_size=10)
        self.btn_mark.pack(side=tk.LEFT)
        self.btn_read_mark = self._flat_btn(mark_row, self.T('read_mark'),
                                            COL_PANEL, COL_BLACK,
                                            self.read_from_mark,
                                            padx=12, pady=5, font_size=10)
        self.btn_read_mark.pack(side=tk.LEFT, padx=6)
        self.mark_lbl = tk.Label(mark_row, text="", bg=COL_BG, fg=COL_GRAY,
                                 font=_f(10))
        self.mark_lbl.pack(side=tk.LEFT, padx=10)

        # ===== 语音分组卡片（密）：语音来源 + 声线合并 =====
        voice_group = tk.Frame(self.root, bg=COL_PANEL2, relief="ridge", bd=1)
        voice_group.pack(fill=tk.X, padx=30, pady=(12, 2))
        inner = tk.Frame(voice_group, bg=COL_PANEL2)
        inner.pack(fill=tk.X, padx=14, pady=9)
        self.lbl_voice_src = tk.Label(inner, text=self.T('voice_src'),
                                      bg=COL_PANEL2, fg=COL_GRAY,
                                      font=_f(10, True))
        self.lbl_voice_src.pack(side=tk.LEFT)
        self.engine_combo = ttk.Combobox(inner, state="readonly",
                                         font=_f(10), width=15,
                                         style="Min.TCombobox")
        self.engine_combo['values'] = [self.T('engine_neural'),
                                       self.T('engine_sapi')]
        self.engine_combo.current(0)
        self.engine_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.engine_combo.bind("<<ComboboxSelected>>", self._on_engine_change)
        sep = tk.Frame(inner, bg=COL_LINE, width=1, height=22)
        sep.pack(side=tk.LEFT, padx=14)
        self.lbl_voice = tk.Label(inner, text=self.T('voice'), bg=COL_PANEL2,
                                  fg=COL_GRAY, font=_f(10, True))
        self.lbl_voice.pack(side=tk.LEFT)
        self.voice_combo = ttk.Combobox(inner, state="readonly",
                                        font=_f(10), width=26,
                                        style="Min.TCombobox")
        self.voice_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_change)

        # ===== 定时关闭 + 音量（疏 · 左右） =====
        opt_row = tk.Frame(self.root, bg=COL_BG)
        opt_row.pack(fill=tk.X, padx=30, pady=(12, 2))
        self.lbl_timer = tk.Label(opt_row, text=self.T('timer'), bg=COL_BG,
                                  fg=COL_BLACK, font=_f(11, True))
        self.lbl_timer.pack(side=tk.LEFT)
        self.timer_combo = ttk.Combobox(opt_row, state="readonly", width=8,
                                        font=_f(10),
                                        style="Min.TCombobox")
        self.timer_combo['values'] = [self.T('timer_off'), self.T('timer_15'),
                                      self.T('timer_30'), self.T('timer_60'),
                                      self.T('timer_90')]
        self.timer_combo.current(0)
        self.timer_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.timer_combo.bind("<<ComboboxSelected>>", self._on_timer_change)
        self.timer_lbl = tk.Label(opt_row, text="", bg=COL_BG, fg=COL_RED,
                                  font=_f(10, True), width=10, anchor="w")
        self.timer_lbl.pack(side=tk.LEFT, padx=(8, 0))

        vol_box = tk.Frame(opt_row, bg=COL_BG)
        vol_box.pack(side=tk.RIGHT)
        self.vol_lbl = tk.Label(vol_box, text="100%", bg=COL_BG, fg=COL_BLACK,
                                font=_f(11, True), width=5, anchor="e")
        self.vol_lbl.pack(side=tk.RIGHT)
        self.vol_scale = ttk.Scale(vol_box, from_=0, to=100,
                                   orient="horizontal",
                                   style="Min.Horizontal.TScale",
                                   command=self._on_volume_change)
        self.vol_scale.set(100)
        self.vol_scale.pack(side=tk.RIGHT, fill=tk.X, padx=(0, 8))
        self.lbl_volume = tk.Label(vol_box, text=self.T('volume'), bg=COL_BG,
                                   fg=COL_BLACK, font=_f(11, True))
        self.lbl_volume.pack(side=tk.RIGHT, padx=(0, 8))

        # ===== 进度行 =====
        prog_row = tk.Frame(self.root, bg=COL_BG)
        prog_row.pack(fill=tk.X, padx=30, pady=(10, 2))
        self.progress = ttk.Progressbar(prog_row, orient="horizontal",
                                        maximum=100, value=0,
                                        style="Min.Horizontal.TProgressbar")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_lbl = tk.Label(prog_row, text=self.T('not_started'),
                                     bg=COL_BG,
                                     fg=COL_GRAY, font=_f(10), width=20,
                                     anchor="e")
        self.progress_lbl.pack(side=tk.LEFT, padx=(12, 0))

        # ===== 文本区（内凹米白） =====
        mid = tk.Frame(self.root, bg=COL_BG)
        mid.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        self.text = tk.Text(mid, wrap=tk.WORD, font=(FONT, 13),
                            bg=COL_PANEL, fg=COL_BLACK, relief="sunken", bd=1,
                            padx=16, pady=14,
                            insertbackground=COL_BLACK,
                            selectbackground=COL_HL,
                            selectforeground=COL_BLACK,
                            highlightbackground=COL_LINE,
                            highlightcolor=COL_LINE,
                            highlightthickness=2)
        self.text.tag_configure('reading', background=COL_HL,
                                foreground=COL_BLACK)
        sb = tk.Scrollbar(mid, orient="vertical", command=self.text.yview,
                          bg=COL_BG, troughcolor=COL_LINE, relief="flat",
                          bd=0, highlightthickness=0,
                          activebackground=COL_BLACK)
        self.text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ===== 底部细线 =====
        footer = tk.Frame(self.root, bg=COL_BG)
        footer.pack(fill=tk.X, padx=30, pady=(6, 16))
        tk.Frame(footer, bg=COL_LINE, height=2).pack(fill=tk.X)

        self._saved_sel = None

        def _save_sel(_e=None):
            try:
                r = self.text.tag_ranges(tk.SEL)
                if r:
                    self._saved_sel = (r[0], r[1])
            except Exception:
                pass
        self.text.bind("<<Selection>>", _save_sel)
        self.text.bind("<ButtonRelease-1>", _save_sel)

        # 右键菜单
        self._ctx = tk.Menu(self.text, tearoff=0, font=_f(10),
                            bg=COL_PANEL, fg=COL_BLACK,
                            activebackground=COL_BLACK,
                            activeforeground=COL_PANEL,
                            bd=1, relief="solid")
        self._ctx.add_command(label=self.T('ctx_here'),
                              command=self.read_from_cursor)
        self._ctx.add_command(label=self.T('ctx_sel'),
                              command=self.read_selection)
        self.text.bind("<Button-3>", self._show_ctx)

    def _flat_btn(self, parent, text, bg, fg, cmd=None, padx=12, pady=7,
                  font_size=11, width=None):
        """浮雕风格按钮：凸起边缘 + 暖色高光感。"""
        return tk.Button(parent, text=text, command=cmd, font=_f(font_size, True),
                         bg=bg, fg=fg,
                         activebackground=COL_PANEL2, activeforeground=fg,
                         relief="raised", bd=1,
                         padx=padx, pady=pady, cursor="hand2",
                         highlightbackground=COL_LINE,
                         highlightthickness=1,
                         width=width)

    def _flat_btn_box(self, parent, text, bg, fg, cmd=None, padx=12, pady=7,
                      font_size=11, width=None):
        """带底部状态条的浮雕按钮：返回 (外层, 按钮, 状态条)。激活时状态条变橙。"""
        wrap = tk.Frame(parent, bg=COL_BG)
        btn = tk.Button(wrap, text=text, command=cmd, font=_f(font_size, True),
                        bg=bg, fg=fg, activebackground=COL_PANEL2,
                        activeforeground=fg,
                        relief="raised", bd=1, padx=padx, pady=pady,
                        cursor="hand2", highlightbackground=COL_BLACK,
                        highlightthickness=1, width=width)
        btn.pack(fill=tk.X)
        strip = tk.Frame(wrap, bg=COL_BG, height=4)
        strip.pack(fill=tk.X, pady=(4, 0))
        return wrap, btn, strip

    def _set_active_read(self, key):
        """切换当前朗读方式：底部状态条变橙。key=None 表示清除。"""
        for k, (b, s) in getattr(self, "_read_btns", {}).items():
            if k == key:
                b.config(bg=COL_PANEL2)
                s.config(bg=COL_ACCENT)
            else:
                b.config(bg=COL_PANEL)
                s.config(bg=COL_BG)

    def _show_ctx(self, event):
        try:
            self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
            self._ctx.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                self._ctx.grab_release()
            except Exception:
                pass

    def _index_to_offset(self, idx):
        """把文本框里的位置(行.列)换算成全文里的字符偏移。"""
        try:
            line, col = map(int, str(self.text.index(idx)).split("."))
            lines = self.full_text.split("\n")
            pos = 0
            for i in range(line - 1):
                pos += len(lines[i]) + 1
            return pos + col
        except Exception:
            return 0

    # ---------- 快捷键 ----------
    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-p>", lambda e: self.toggle_pause())
        self.root.bind("<Escape>", lambda e: self.stop())

    # ---------- 托盘 ----------
    def _setup_tray(self):
        self._tray = None
        self._tray_icon_img = _make_tray_icon()
        try:
            import pystray
            from PIL import Image
            menu = pystray.Menu(
                pystray.MenuItem(self.T('tray_show'), self._tray_show,
                                 default=True),
                pystray.MenuItem(self.T('tray_pause'), self._tray_pause),
                pystray.MenuItem(self.T('tray_stop'), self._tray_stop),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(self.T('tray_quit'), self._tray_quit),
            )
            icon = pystray.Icon("textreader",
                                self._tray_icon_img or Image.new('RGB', (64, 64), COL_BLACK),
                                self.T('title'), menu)
            self._tray = icon
            threading.Thread(target=icon.run, daemon=True).start()
        except Exception as e:
            self._tray = None
            print("托盘启动失败(不影响使用):", e)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def hide_to_tray(self):
        if self._tray is not None:
            self.root.withdraw()
            if self.state_lbl:
                self.state_lbl.config(text=self.T('tray_min'))
        else:
            self.root.iconify()

    def _tray_show(self, icon=None, item=None):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _tray_pause(self, icon=None, item=None):
        self.root.after(0, self.toggle_pause)

    def _tray_stop(self, icon=None, item=None):
        self.root.after(0, self.stop)

    def _tray_quit(self, icon=None, item=None):
        self._cancel_timer()
        if self.speaker:
            self.speaker.stop()
        if self._tray:
            self._tray.stop()
        self.root.after(0, self.root.destroy)

    # ---------- 倍速 ----------
    def _on_speed_change(self, val):
        try:
            v = float(val)
        except Exception:
            v = 100
        self._set_speed(v / 100.0, restart=False, from_slider=True)

    def _on_speed_release(self, _e=None):
        """松开速度滑杆时，让新的倍速立刻生效（从当前段落重新朗读）。"""
        try:
            if self.speaker is not None:
                self.speaker.restart_for_speed()
        except Exception:
            pass

    def _preset_speed(self, mult):
        self._set_speed(mult, restart=True, from_slider=False)

    # ---------- 音量 ----------
    def _on_volume_change(self, val):
        try:
            v = int(round(float(val)))
        except Exception:
            v = 100
        v = max(0, min(100, v))
        self._volume = v
        self.vol_lbl.config(text="%d%%" % v)
        if self.speaker is not None:
            self.speaker.set_volume(v)
        self.state_lbl.config(text=self.T('volume_set', v), fg=COL_BLACK)

    # ---------- 定时关闭 ----------
    def _on_timer_change(self, _e=None):
        self._cancel_timer()
        idx = self.timer_combo.current()
        if idx <= 0:
            self._timer_minutes = 0
            self._timer_remaining = 0
            self.timer_lbl.config(text="")
            self.state_lbl.config(text=self.T('timer_off_msg'), fg=COL_GRAY)
            return
        minutes = (15, 30, 60, 90)[idx - 1]
        self._timer_minutes = minutes
        self._timer_remaining = minutes * 60
        self.state_lbl.config(text=self.T('timer_set', minutes), fg=COL_RED)
        self._timer_tick()

    def _cancel_timer(self):
        if self._timer_job is not None:
            try:
                self.root.after_cancel(self._timer_job)
            except Exception:
                pass
            self._timer_job = None

    def _timer_tick(self):
        if self._timer_remaining <= 0:
            self._timer_fire()
            return
        mm, ss = divmod(self._timer_remaining, 60)
        self.timer_lbl.config(text=self.T('timer_left', mm, ss))
        self._timer_remaining -= 1
        self._timer_job = self.root.after(1000, self._timer_tick)

    def _timer_fire(self):
        self._timer_job = None
        self._timer_remaining = 0
        self.timer_lbl.config(text="")
        if self.speaker:
            self.speaker.stop()
        self.state_lbl.config(text=self.T('timer_fire'), fg=COL_RED)
        try:
            self.timer_combo.current(0)
        except Exception:
            pass

    def _set_speed(self, mult, restart=False, from_slider=False):
        mult = max(0.5, min(3.0, mult))
        self._speed_mult = mult
        self._update_preset_highlight()
        if self.speaker is not None:
            self.speaker.set_rate(mult)
        self.state_lbl.config(text=self.T('speed_set', mult), fg=COL_BLACK)
        if restart:
            self._on_speed_release()

    def _update_preset_highlight(self):
        btns = getattr(self, "_speed_btns", None)
        if not btns:
            return
        best = min(btns, key=lambda m: abs(m - self._speed_mult))
        for m, b in btns.items():
            if m == best:
                b.config(bg=COL_PANEL2, fg=COL_BLACK)
            else:
                b.config(bg=COL_PANEL, fg=COL_BLACK)

    # ---------- 文件 ----------
    def open_file(self):
        path = filedialog.askopenfilename(
            title=self.T('dlg_open_title'),
            filetypes=[(self.T('ft_docs'),
                        "*.pdf *.docx *.doc *.txt *.md *.epub *.html *.htm"),
                       (self.T('ft_pdf'), "*.pdf"),
                       (self.T('ft_word'), "*.docx *.doc"),
                       (self.T('ft_epub'), "*.epub"),
                       (self.T('ft_web'), "*.html *.htm"),
                       (self.T('ft_text'), "*.txt *.md"),
                       (self.T('ft_all'), "*.*")])
        if not path:
            return
        if getattr(self, '_open_pending', False):
            return
        self._open_pending = True
        self.file_lbl.config(text=os.path.basename(path), fg=COL_BLACK)
        self.state_lbl.config(text=self.T('loading'), fg=COL_BLACK)

        def work():
            try:
                text = extract_text(path)
                err = None
            except Exception as e:
                text, err = None, e
            self.root.after(0, lambda: self._finish_open(path, text, err))

        threading.Thread(target=work, daemon=True).start()

    def _finish_open(self, path, text, err):
        self._open_pending = False
        if err is not None:
            self.file_lbl.config(text=self.T('no_file'), fg=COL_GRAY)
            self.state_lbl.config(text=self.T('ready'), fg=COL_GRAY)
            messagebox.showerror(self.T('dlg_err'), str(err))
            return
        if text is None or not text.strip():
            ext = os.path.splitext(path)[1].lower()
            if ext == '.doc':
                messagebox.showwarning(self.T('dlg_doc_read_title'),
                                       self.T('dlg_doc_read_body'))
            else:
                messagebox.showwarning(self.T('dlg_tip'), self.T('dlg_no_text'))
            self.file_lbl.config(text=self.T('no_file'), fg=COL_GRAY)
            self.state_lbl.config(text=self.T('ready'), fg=COL_GRAY)
            return
        self.current_path = path
        self.full_text = text
        self._load_text(text)
        self.file_lbl.config(text=os.path.basename(path), fg=COL_BLACK)
        self.state_lbl.config(text=self.T('loaded', len(self.full_text)),
                              fg=COL_BLUE)

    def _load_text(self, text):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)

    def clear_text(self):
        if self.speaker:
            self.speaker.stop()
        self._set_active_read(None)
        self.text.delete("1.0", tk.END)
        self.current_path = None
        self.full_text = ""
        self.speech_chunks = []
        self._chunk_ranges = []
        self._mark_offset = None
        self.mark_lbl.config(text="")
        self.progress['value'] = 0
        self.progress_lbl.config(text=self.T('not_started'))
        self._current_chunk = 0
        self.file_lbl.config(text=self.T('no_file'), fg=COL_GRAY)
        self.state_lbl.config(text=self.T('cleared'), fg=COL_GRAY)
        self._reading_label = 'read_all'

    # ---------- 语音 ----------
    def _get_speaker(self):
        if self.speaker is None:
            try:
                self.speaker = Speaker(self.engine_mode)
                self.speaker.set_fallback(self._local_fallback)
                self.speaker.set_language(self.lang)
            except Exception as e:
                messagebox.showerror(self.T('dlg_speech_init'), str(e))
                return None
        try:
            self.speaker.set_rate(self._speed_mult)
        except Exception:
            pass
        try:
            self.speaker.set_volume(self._volume)
        except Exception:
            pass
        return self.speaker

    def _local_fallback(self, chunks, on_progress, on_state):
        """AI 网络中断时，剩余内容改用本地系统语音继续读。"""
        try:
            if self.speaker is not None:
                self.speaker.speak_local(chunks, on_progress, on_state)
        except Exception:
            pass

    def read_all(self):
        if not self.full_text:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_open_first'))
            return
        self._start_reading(self.full_text, base=0, label='read_all')

    def read_selection(self):
        """朗读选中的文字；如果没有选中，则从光标位置开始。"""
        sel = self.text.tag_ranges(tk.SEL)
        if not sel and self._saved_sel:
            sel = self._saved_sel
        if sel:
            start = self._index_to_offset(sel[0])
            end = self._index_to_offset(sel[1])
            if end > start:
                sub = self.text.get(sel[0], sel[1]).strip()
                if sub:
                    self._start_reading(sub, base=start, label='read_sel')
                    return
        # 没有选中内容：从光标位置开始
        self.read_from_cursor()

    def read_from_cursor(self):
        """从光标所在位置读到文档结尾。"""
        if not self.full_text:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_open_first'))
            return
        start = self._index_to_offset("insert")
        if start >= len(self.full_text):
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_cursor_end'))
            return
        self._start_reading(self.full_text[start:], base=start,
                            label='read_cursor')

    def mark_position(self):
        """打标记：正在读时记下当前段落位置；没在读时记下鼠标光标位置。"""
        if not self.full_text:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_open_first'))
            return
        off = None
        if self.speaker is not None and self._current_chunk > 0:
            rng = None
            if self._chunk_ranges and self._current_chunk - 1 < len(self._chunk_ranges):
                rng = self._chunk_ranges[self._current_chunk - 1]
            if rng:
                off = rng[0]
        if off is None:
            off = self._index_to_offset("insert")
        self._mark_offset = off
        self.mark_lbl.config(text=self.T('marked', off))
        self.state_lbl.config(text=self.T('marked_hint'), fg=COL_GRAY)

    def read_from_mark(self):
        """从标记处读到文档结尾。"""
        if not self.full_text:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_open_first'))
            return
        if self._mark_offset is None:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_no_mark'))
            return
        start = self._mark_offset
        if start >= len(self.full_text):
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_mark_end'))
            return
        try:
            self.text.mark_set("insert", "1.0+%dc" % start)
        except Exception:
            pass
        self._start_reading(self.full_text[start:], base=start,
                            label='read_mark')

    def _start_reading(self, text, base=0, label='read_all'):
        sp = self._get_speaker()
        if not sp:
            return
        chunks = split_chunks(clean_for_speech(text))
        if not chunks:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_no_read'))
            return
        self._reading_label = label
        self._set_active_read(label)
        self._current_chunk = 0
        self.speech_chunks = chunks
        self._chunk_ranges = self._build_chunk_ranges(text, base)
        self.progress['value'] = 0
        self.progress_lbl.config(text=self.T('progress', self.T(label), 0,
                                             len(chunks)))
        sp.speak(chunks, on_progress=self._on_progress, on_state=self._on_state)

    def _build_chunk_ranges(self, text, base=0):
        """把朗读分块映射回原文里的位置，用于高亮（找不到就跳过）。"""
        pos, ranges = 0, []
        for ch in self.speech_chunks:
            idx = text.find(ch, pos)
            if idx < 0:
                probe = ch[:12].strip()
                idx = text.find(probe, pos)
                if idx >= 0:
                    ranges.append((base + idx, base + idx + len(ch)))
                    pos = idx + len(ch)
                    continue
                ranges.append(None)
                continue
            ranges.append((base + idx, base + idx + len(ch)))
            pos = idx + len(ch)
        return ranges

    # ---------- 进度 / 状态回调（来自后台线程，转回主线程） ----------
    def _on_progress(self, i, total):
        self.root.after(0, lambda: self._ui_progress(i, total))

    def _ui_progress(self, i, total):
        try:
            if total:
                self.progress['value'] = i / float(total) * 100
            self._current_chunk = i
            label = getattr(self, '_reading_label', None) or 'read_all'
            self.progress_lbl.config(text=self.T('progress', self.T(label),
                                                 i, total))
            self.text.tag_remove('reading', "1.0", tk.END)
            if i > 0 and self._chunk_ranges and i - 1 < len(self._chunk_ranges):
                rng = self._chunk_ranges[i - 1]
                if rng:
                    start = "1.0+%dc" % rng[0]
                    end = "1.0+%dc" % rng[1]
                    self.text.tag_add('reading', start, end)
                    try:
                        self.text.see(start)
                    except Exception:
                        pass
        except Exception:
            pass

    def _on_state(self, text):
        if any(k in text for k in ('完成', '停止', 'done', 'stopped',
                                   'finished', 'finish')):
            self._set_active_read(None)
        ok_kw = ('完成', '就绪', '已导出', '切换', 'done', 'ready', 'exported',
                 'switched', 'finished')
        err_kw = ('失败', '不可用', '中断', 'fail', 'unavailable', 'interrupted',
                  'error')
        low = text.lower()
        self.root.after(0, lambda: self.state_lbl.config(
            text=text,
            fg=COL_BLUE if any(k in low for k in ok_kw) else
               (COL_RED if any(k in low for k in err_kw) else COL_BLACK)))

    # ---------- 控制 ----------
    def toggle_pause(self):
        if self.speaker is None:
            return
        st = self.speaker.toggle_pause_resume()
        self.state_lbl.config(text=self.T('paused_msg') if st == 'pause'
                              else self.T('resuming'),
                              fg=COL_GRAY if st == 'pause' else COL_RED)

    def stop(self):
        if self.speaker:
            self.speaker.stop()
            self.state_lbl.config(text=self.T('stopped'), fg=COL_GRAY)
        self._set_active_read(None)

    # ---------- 导出音频 ----------
    def export_audio(self):
        if self._export_busy:
            return
        if not self.full_text:
            messagebox.showinfo(self.T('dlg_tip'), self.T('dlg_open_first'))
            return
        sp = self._get_speaker()
        if not sp:
            return
        if sp.active_engine == 'neural':
            ft = [(self.T('ft_mp3'), "*.mp3")]
            default = ".mp3"
        else:
            ft = [(self.T('ft_wav'), "*.wav")]
            default = ".wav"
        path = filedialog.asksaveasfilename(
            title=self.T('dlg_save_title'),
            defaultextension=default,
            initialfile=os.path.splitext(
                os.path.basename(self.current_path or self.T('app_title')))[0],
            filetypes=ft)
        if not path:
            return
        self._export_busy = True
        try:
            self.btn_export.config(state="disabled")
        except Exception:
            pass
        self.state_lbl.config(text=self.T('exporting'), fg=COL_BLACK)

        def work():
            ok, out, msg = sp.export(clean_for_speech(self.full_text), path)
            self.root.after(0, lambda: self._export_done(ok, out, msg))

        threading.Thread(target=work, daemon=True).start()

    def _export_done(self, ok, out, msg):
        self._export_busy = False
        try:
            self.btn_export.config(state="normal")
        except Exception:
            pass
        self.state_lbl.config(text=msg, fg=COL_BLUE if ok else COL_RED)
        if ok and out:
            try:
                size = os.path.getsize(out)
                dur = int(size * 8 / 48000)  # 24kHz/48kbps 的 MP3 近似时长
                m, s = dur // 60, dur % 60
                msg += "\n\n" + self.T('export_info') % (
                    out, size / 1024.0 / 1024.0, m, s)
            except Exception:
                pass
        messagebox.showinfo(self.T('dlg_export_result'), msg)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
