# -*- coding: utf-8 -*-
"""月薇阁 · 文字朗读工具 n2.4（极简黑白风格 · AI 神经网络语音 · 便携版）

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

# ---------- 配色：极简黑白，全界面只使用黑 + 白（灰为中性层次） ----------
COL_BG     = "#FFFFFF"   # 白底
COL_PANEL  = "#FFFFFF"   # 白
COL_PANEL2 = "#F5F5F5"   # 浅灰
COL_BLACK  = "#111111"   # 黑
COL_GRAY   = "#9A9A9A"   # 中灰
COL_LINE   = "#E3E3E3"   # 浅灰分隔
COL_RED    = "#111111"   # 统一为黑
COL_YELLOW = "#111111"   # 统一为黑
COL_BLUE   = "#111111"   # 统一为黑
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
        self.root.title("文字朗读工具 n2.4")
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
        self._reading_label = "朗读"
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
                self.voice_combo.set("(无可用语音)")
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
            self.state_lbl.config(text="AI 网络语音已就绪（联网）", fg=COL_BLUE)
        else:
            if self.engine_mode == 'neural':
                self.state_lbl.config(
                    text="AI 网络语音不可用，已自动改用本地语音", fg=COL_RED)
            else:
                self.state_lbl.config(text="本地系统语音已就绪（离线）", fg=COL_GRAY)

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
                self.state_lbl.config(text="已切换声线：" + self.voice_combo.get(),
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
                        sliderlength=22, sliderrelief='flat')
        style.map("Min.Horizontal.TScale",
                  background=[('active', COL_BLACK), ('pressed', COL_BLACK)])
        style.configure("Min.Horizontal.TProgressbar",
                        troughcolor=COL_LINE, background=COL_BLACK,
                        bordercolor=COL_BLACK,
                        lightcolor=COL_BLACK, darkcolor=COL_BLACK)
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

        # ===== 顶栏：标题 =====
        header = tk.Frame(self.root, bg=COL_BG)
        header.pack(fill=tk.X, padx=24, pady=(18, 4))

        title_block = tk.Frame(header, bg=COL_BG)
        title_block.pack(side=tk.LEFT)
        tk.Label(title_block, text="文字朗读工具", bg=COL_BG, fg=COL_BLACK,
                 font=_f(17, True)).pack(anchor="w")
        tk.Label(title_block, text="AI NEURAL VOICE  ·  n2.4",
                 bg=COL_BG, fg=COL_GRAY, font=_f(9, True)).pack(anchor="w")

        # ===== 文件行 =====
        file_row = tk.Frame(self.root, bg=COL_BG)
        file_row.pack(fill=tk.X, padx=24, pady=(10, 4))
        self.btn_open = self._flat_btn(file_row, "打开文件", COL_PANEL, COL_BLACK,
                                       self.open_file)
        self.btn_open.pack(side=tk.LEFT)
        self.file_lbl = tk.Label(file_row, text="未打开文件", bg=COL_BG,
                                 fg=COL_GRAY, font=_f(11))
        self.file_lbl.pack(side=tk.LEFT, padx=14)
        self.state_lbl = tk.Label(file_row, text="就绪", bg=COL_BG,
                                  fg=COL_GRAY, font=_f(10))
        self.state_lbl.pack(side=tk.RIGHT)

        # ===== 动作按钮行 =====
        act = tk.Frame(self.root, bg=COL_BG)
        act.pack(fill=tk.X, padx=24, pady=(6, 4))
        self._read_btns = {}
        w1, b1, s1 = self._flat_btn_box(act, "从头朗读", COL_PANEL, COL_BLACK,
                                        self.read_all, padx=18)
        w1.pack(side=tk.LEFT)
        self._read_btns["从头朗读"] = (b1, s1)
        w2, b2, s2 = self._flat_btn_box(act, "从光标朗读", COL_PANEL, COL_BLACK,
                                        self.read_from_cursor, padx=18)
        w2.pack(side=tk.LEFT, padx=6)
        self._read_btns["从光标朗读"] = (b2, s2)
        w3, b3, s3 = self._flat_btn_box(act, "朗读选中", COL_PANEL, COL_BLACK,
                                        self.read_selection, padx=18)
        w3.pack(side=tk.LEFT, padx=6)
        self._read_btns["朗读选中"] = (b3, s3)
        self._flat_btn(act, "暂停", COL_PANEL, COL_BLACK,
                       self.toggle_pause, padx=12).pack(side=tk.LEFT, padx=6)
        self._flat_btn(act, "停止", COL_PANEL, COL_BLACK,
                       self.stop, padx=12).pack(side=tk.LEFT, padx=2)
        self.btn_export = self._flat_btn(act, "导出音频", COL_PANEL, COL_BLACK,
                                         self.export_audio, padx=14)
        self.btn_export.pack(side=tk.LEFT, padx=6)
        self._flat_btn(act, "清空", COL_PANEL, COL_GRAY,
                       self.clear_text, padx=12).pack(side=tk.LEFT, padx=2)

        # ===== 标记行：打标记 / 从标记朗读 =====
        mark_row = tk.Frame(self.root, bg=COL_BG)
        mark_row.pack(fill=tk.X, padx=24, pady=(2, 0))
        self._flat_btn(mark_row, "打标记", COL_PANEL, COL_BLACK,
                       self.mark_position, padx=10, pady=3,
                       font_size=10).pack(side=tk.LEFT)
        self._flat_btn(mark_row, "从标记朗读", COL_PANEL, COL_BLACK,
                       self.read_from_mark, padx=10, pady=3,
                       font_size=10).pack(side=tk.LEFT, padx=6)
        self.mark_lbl = tk.Label(mark_row, text="", bg=COL_BG, fg=COL_GRAY,
                                 font=_f(9))
        self.mark_lbl.pack(side=tk.LEFT, padx=10)

        # ===== 倍速行：滑杆 + 快选按钮 =====
        spd = tk.Frame(self.root, bg=COL_BG)
        spd.pack(fill=tk.X, padx=24, pady=(8, 2))
        tk.Label(spd, text="速度", bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(spd, from_=50, to=300,
                                     orient="horizontal",
                                     style="Min.Horizontal.TScale",
                                     command=self._on_speed_change)
        self.speed_scale.set(100)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=14)
        self.speed_scale.bind("<ButtonRelease-1>", self._on_speed_release)

        preset_row = tk.Frame(self.root, bg=COL_BG)
        preset_row.pack(fill=tk.X, padx=24)
        tk.Label(preset_row, text="快选", bg=COL_BG, fg=COL_GRAY,
                 font=_f(10)).pack(side=tk.LEFT, padx=(2, 12))
        self._speed_btns = {}
        for m in (0.5, 1.0, 1.5, 2.0, 3.0):
            label = ("%g×" % m)
            w, b, s = self._flat_btn_box(preset_row, label, COL_PANEL,
                                         COL_BLACK,
                                         lambda x=m: self._preset_speed(x),
                                         padx=10, pady=3, font_size=10)
            w.pack(side=tk.LEFT, padx=2)
            self._speed_btns[m] = (b, s)
        self._update_preset_highlight()

        # ===== 声线与语音来源 =====
        voice_row = tk.Frame(self.root, bg=COL_BG)
        voice_row.pack(fill=tk.X, padx=24, pady=(8, 2))
        tk.Label(voice_row, text="语音来源", bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(side=tk.LEFT)
        self.engine_combo = ttk.Combobox(voice_row, state="readonly",
                                         font=_f(10), width=15,
                                         style="Min.TCombobox")
        self.engine_combo['values'] = ["AI 网络语音（推荐）", "本地系统语音"]
        self.engine_combo.current(0)
        self.engine_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.engine_combo.bind("<<ComboboxSelected>>", self._on_engine_change)

        tk.Label(voice_row, text="声线", bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(side=tk.LEFT, padx=(24, 0))
        self.voice_combo = ttk.Combobox(voice_row, state="readonly",
                                        font=_f(10), width=26,
                                        style="Min.TCombobox")
        self.voice_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_change)

        # ===== 定时关闭 + 音量 =====
        opt_row = tk.Frame(self.root, bg=COL_BG)
        opt_row.pack(fill=tk.X, padx=24, pady=(8, 2))
        tk.Label(opt_row, text="定时关闭", bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(side=tk.LEFT)
        self.timer_combo = ttk.Combobox(opt_row, state="readonly", width=10,
                                        font=_f(10),
                                        style="Min.TCombobox")
        self.timer_combo['values'] = ["关闭", "15 分钟", "30 分钟",
                                      "60 分钟", "90 分钟"]
        self.timer_combo.current(0)
        self.timer_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.timer_combo.bind("<<ComboboxSelected>>", self._on_timer_change)
        self.timer_lbl = tk.Label(opt_row, text="", bg=COL_BG, fg=COL_BLACK,
                                  font=_f(10, True), width=12, anchor="w")
        self.timer_lbl.pack(side=tk.LEFT, padx=(8, 0))

        self.vol_lbl = tk.Label(opt_row, text="100%", bg=COL_BG, fg=COL_BLACK,
                                font=_f(11, True), width=5, anchor="e")
        self.vol_lbl.pack(side=tk.RIGHT)
        self.vol_scale = ttk.Scale(opt_row, from_=0, to=100,
                                   orient="horizontal",
                                   style="Min.Horizontal.TScale",
                                   command=self._on_volume_change)
        self.vol_scale.set(100)
        self.vol_scale.pack(side=tk.RIGHT, fill=tk.X, padx=(0, 8))
        tk.Label(opt_row, text="音量", bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(side=tk.RIGHT, padx=(0, 8))

        # ===== 进度行 =====
        prog_row = tk.Frame(self.root, bg=COL_BG)
        prog_row.pack(fill=tk.X, padx=24, pady=(6, 2))
        self.progress = ttk.Progressbar(prog_row, orient="horizontal",
                                        maximum=100, value=0,
                                        style="Min.Horizontal.TProgressbar")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_lbl = tk.Label(prog_row, text="尚未开始", bg=COL_BG,
                                     fg=COL_GRAY, font=_f(10), width=20,
                                     anchor="e")
        self.progress_lbl.pack(side=tk.LEFT, padx=(12, 0))

        # ===== 文本区（黑框白底） =====
        mid = tk.Frame(self.root, bg=COL_BG)
        mid.pack(fill=tk.BOTH, expand=True, padx=24, pady=8)
        self.text = tk.Text(mid, wrap=tk.WORD, font=(FONT, 13),
                            bg=COL_PANEL, fg=COL_BLACK, relief="flat",
                            padx=16, pady=14,
                            insertbackground=COL_BLACK,
                            selectbackground="#E8E8E8",
                            selectforeground=COL_BLACK,
                            highlightbackground=COL_BLACK,
                            highlightcolor=COL_BLACK,
                            highlightthickness=2)
        self.text.tag_configure('reading', background='#ECECEC',
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
        footer.pack(fill=tk.X, padx=24, pady=(4, 14))
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
        self._ctx.add_command(label="从这里开始朗读", command=self.read_from_cursor)
        self._ctx.add_command(label="朗读选中内容", command=self.read_selection)
        self.text.bind("<Button-3>", self._show_ctx)

    def _flat_btn(self, parent, text, bg, fg, cmd=None, padx=12, pady=7,
                  font_size=11):
        return tk.Button(parent, text=text, command=cmd, font=_f(font_size, True),
                         bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg,
                         relief="flat", bd=0,
                         padx=padx, pady=pady, cursor="hand2",
                         highlightbackground=COL_BLACK,
                         highlightthickness=2)

    def _flat_btn_box(self, parent, text, bg, fg, cmd=None, padx=12, pady=7,
                      font_size=11):
        """带底部状态条的按钮：返回 (外层, 按钮, 状态条)。激活时状态条变灰。"""
        wrap = tk.Frame(parent, bg=COL_BG)
        btn = tk.Button(wrap, text=text, command=cmd, font=_f(font_size, True),
                        bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                        relief="flat", bd=0, padx=padx, pady=pady,
                        cursor="hand2", highlightbackground=COL_BLACK,
                        highlightthickness=2)
        btn.pack(fill=tk.X)
        strip = tk.Frame(wrap, bg=COL_BG, height=3)
        strip.pack(fill=tk.X)
        return wrap, btn, strip

    def _set_active_read(self, key):
        """切换当前朗读方式：底部状态条变灰。key=None 表示清除。"""
        for k, (b, s) in getattr(self, "_read_btns", {}).items():
            if k == key:
                b.config(bg=COL_PANEL2)
                s.config(bg=COL_GRAY)
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
                pystray.MenuItem("打开界面", self._tray_show, default=True),
                pystray.MenuItem("暂停 / 继续", self._tray_pause),
                pystray.MenuItem("停止朗读", self._tray_stop),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", self._tray_quit),
            )
            icon = pystray.Icon("textreader",
                                self._tray_icon_img or Image.new('RGB', (64, 64), COL_BLACK),
                                "文字朗读工具 n2.4", menu)
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
                self.state_lbl.config(text="已最小化到托盘，点图标呼出")
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
        self.state_lbl.config(text="音量 %d%%" % v, fg=COL_BLACK)

    # ---------- 定时关闭 ----------
    def _on_timer_change(self, _e=None):
        self._cancel_timer()
        idx = self.timer_combo.current()
        if idx <= 0:
            self._timer_minutes = 0
            self._timer_remaining = 0
            self.timer_lbl.config(text="")
            self.state_lbl.config(text="定时关闭：已关闭", fg=COL_GRAY)
            return
        minutes = (15, 30, 60, 90)[idx - 1]
        self._timer_minutes = minutes
        self._timer_remaining = minutes * 60
        self.state_lbl.config(text="定时关闭：%d 分钟后停止朗读" % minutes,
                              fg=COL_RED)
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
        self.timer_lbl.config(text="剩余 %02d:%02d" % (mm, ss))
        self._timer_remaining -= 1
        self._timer_job = self.root.after(1000, self._timer_tick)

    def _timer_fire(self):
        self._timer_job = None
        self._timer_remaining = 0
        self.timer_lbl.config(text="")
        if self.speaker:
            self.speaker.stop()
        self.state_lbl.config(text="定时关闭：时间到，朗读已停止", fg=COL_RED)
        try:
            self.timer_combo.current(0)
        except Exception:
            pass

    def _set_speed(self, mult, restart=False, from_slider=False):
        mult = max(0.5, min(3.0, mult))
        self._speed_mult = mult
        # 注意：ttk 滑杆的 set() 会再次触发回调，这里不能从回调里再 set，
        # 否则进入主循环后会无限循环（这也是之前打不开的根因）。
        if not from_slider:
            try:
                self.speed_scale.set(mult * 100)
            except Exception:
                pass
        self._update_preset_highlight()
        if self.speaker is not None:
            self.speaker.set_rate(mult)
        self.state_lbl.config(text="速度 %.1fx（0.5x 慢速 / 3x 高速）" % mult,
                              fg=COL_BLACK)
        if restart:
            self._on_speed_release()

    def _update_preset_highlight(self):
        btns = getattr(self, "_speed_btns", None)
        if not btns:
            return
        best = min(btns, key=lambda m: abs(m - self._speed_mult))
        for m, (b, s) in btns.items():
            if m == best:
                b.config(bg=COL_PANEL2, fg=COL_BLACK)
                s.config(bg=COL_GRAY)
            else:
                b.config(bg=COL_PANEL, fg=COL_BLACK)
                s.config(bg=COL_BG)

    # ---------- 文件 ----------
    def open_file(self):
        path = filedialog.askopenfilename(
            title="选择要朗读的文件",
            filetypes=[("支持的文档", "*.pdf *.docx *.doc *.txt *.md *.epub *.html *.htm"),
                       ("PDF", "*.pdf"), ("Word", "*.docx *.doc"),
                       ("电子书", "*.epub"), ("网页", "*.html *.htm"),
                       ("文本", "*.txt *.md"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            text = extract_text(path)
        except Exception as e:
            messagebox.showerror("读取失败", str(e))
            return
        if text is None or not text.strip():
            ext = os.path.splitext(path)[1].lower()
            if ext == '.doc':
                messagebox.showwarning(
                    "无法读取此 .doc",
                    "这个旧版 Word 文档（.doc）没能读出文字。\n\n"
                    "解决办法：用 Word 打开它 → 另存为 → 选「Word 文档 (*.docx)」→ 再用本工具打开。\n"
                    "（.docx 是最稳定的格式，建议所有 Word 都用它）")
            else:
                messagebox.showwarning("提示", "这个文件里没读到文字。\n"
                                      "（PDF 如果是扫描件/图片，需 OCR，暂不支持）")
            return
        self.current_path = path
        self.full_text = text
        self._load_text(text)
        self.file_lbl.config(text=os.path.basename(path), fg=COL_BLACK)
        self.state_lbl.config(text="已载入 %d 字" % len(self.full_text), fg=COL_BLUE)

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
        self.progress_lbl.config(text="尚未开始")
        self._current_chunk = 0
        self.file_lbl.config(text="未打开文件", fg=COL_GRAY)
        self.state_lbl.config(text="已清空", fg=COL_GRAY)
        self._reading_label = "朗读"

    # ---------- 语音 ----------
    def _get_speaker(self):
        if self.speaker is None:
            try:
                self.speaker = Speaker(self.engine_mode)
                self.speaker.set_fallback(self._local_fallback)
            except Exception as e:
                messagebox.showerror("语音初始化失败", str(e))
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
            messagebox.showinfo("提示", "请先打开一个文档")
            return
        self._start_reading(self.full_text, base=0, label="从头朗读")

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
                    self._start_reading(sub, base=start, label="朗读选中")
                    return
        # 没有选中内容：从光标位置开始
        self.read_from_cursor()

    def read_from_cursor(self):
        """从光标所在位置读到文档结尾。"""
        if not self.full_text:
            messagebox.showinfo("提示", "请先打开一个文档")
            return
        start = self._index_to_offset("insert")
        if start >= len(self.full_text):
            messagebox.showinfo("提示", "光标已在文档末尾，没有可读的内容")
            return
        self._start_reading(self.full_text[start:], base=start, label="从光标处朗读")

    def mark_position(self):
        """打标记：正在读时记下当前段落位置；没在读时记下鼠标光标位置。"""
        if not self.full_text:
            messagebox.showinfo("提示", "请先打开一个文档")
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
        self.mark_lbl.config(text="已标记：第 %d 字处" % off)
        self.state_lbl.config(text="已打标记，可随时点「从标记朗读」继续", fg=COL_GRAY)

    def read_from_mark(self):
        """从标记处读到文档结尾。"""
        if not self.full_text:
            messagebox.showinfo("提示", "请先打开一个文档")
            return
        if self._mark_offset is None:
            messagebox.showinfo("提示", "还没有打标记，请先点「打标记」")
            return
        start = self._mark_offset
        if start >= len(self.full_text):
            messagebox.showinfo("提示", "标记已在文档末尾，没有可读的内容")
            return
        try:
            self.text.mark_set("insert", "1.0+%dc" % start)
        except Exception:
            pass
        self._start_reading(self.full_text[start:], base=start, label="从标记朗读")

    def _start_reading(self, text, base=0, label="朗读"):
        sp = self._get_speaker()
        if not sp:
            return
        chunks = split_chunks(clean_for_speech(text))
        if not chunks:
            messagebox.showinfo("提示", "没有可朗读的文字")
            return
        self._reading_label = label
        key = {"从头朗读": "从头朗读",
               "从光标处朗读": "从光标朗读",
               "朗读选中": "朗读选中"}.get(label)
        self._set_active_read(key)
        self._current_chunk = 0
        self.speech_chunks = chunks
        self._chunk_ranges = self._build_chunk_ranges(text, base)
        self.progress['value'] = 0
        self.progress_lbl.config(text="%s · 第 0 / %d 段" % (label, len(chunks)))
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
            label = getattr(self, '_reading_label', None) or "朗读"
            self.progress_lbl.config(text="%s · 第 %d / %d 段" % (label, i, total))
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
        if '完成' in text or '停止' in text:
            self._set_active_read(None)
        self.root.after(0, lambda: self.state_lbl.config(
            text=text,
            fg=COL_BLUE if ('完成' in text or '就绪' in text) else
               (COL_RED if ('失败' in text or '不可用' in text) else COL_BLACK)))

    # ---------- 控制 ----------
    def toggle_pause(self):
        if self.speaker is None:
            return
        st = self.speaker.toggle_pause_resume()
        self.state_lbl.config(text="已暂停，点继续" if st == 'pause' else "继续朗读…",
                              fg=COL_GRAY if st == 'pause' else COL_RED)

    def stop(self):
        if self.speaker:
            self.speaker.stop()
            self.state_lbl.config(text="已停止", fg=COL_GRAY)
        self._set_active_read(None)

    # ---------- 导出音频 ----------
    def export_audio(self):
        if self._export_busy:
            return
        if not self.full_text:
            messagebox.showinfo("提示", "请先打开一个文档")
            return
        sp = self._get_speaker()
        if not sp:
            return
        if sp.active_engine == 'neural':
            ft = [("MP3 音频", "*.mp3")]
            default = ".mp3"
        else:
            ft = [("WAV 音频", "*.wav")]
            default = ".wav"
        path = filedialog.asksaveasfilename(
            title="保存朗读音频",
            defaultextension=default,
            initialfile=os.path.splitext(os.path.basename(self.current_path or '朗读'))[0],
            filetypes=ft)
        if not path:
            return
        self._export_busy = True
        try:
            self.btn_export.config(state="disabled")
        except Exception:
            pass
        self.state_lbl.config(text="正在生成音频…（长文档需要几分钟）", fg=COL_BLACK)

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
                msg += "\n\n文件：%s\n大小：%.1f MB\n时长约：%d 分 %d 秒" % (
                    out, size / 1024.0 / 1024.0, m, s)
            except Exception:
                pass
        messagebox.showinfo("导出结果", msg)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
