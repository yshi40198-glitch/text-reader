# -*- coding: utf-8 -*-
"""薇阅 · 文字朗读工具 v3.0（朝阳暖色 · AI 神经网络语音 · 中英双语 · 便携版）

功能:
- 打开 PDF / Word / txt → 从头朗读
- 从光标朗读 / 朗读选中 / 右键快捷菜单
- AI 神经网络语音（edge-tts，自然逼真，需联网），断网自动用本地语音
- 倍速 0.5x ~ 3.0x（两级变速：合成变速 + 播放变速，真实可感）
- 实时进度条 + 正在朗读的段落高亮
- 导出 MP3（AI 语音）/ WAV（本地语音）
- 系统托盘：关窗口最小化，朗读不中断
- 文本翻译 / 录音跟读（复读机模式）/ 读链接 / 智能过滤
- 书库：本地书库 + 云端书库（浏览 / 朗读 / 删除）
- 跟读升级：暂停 / 停止 / 复读次数 / 间隔 / 原句时长 / 录音时长
- 大字号模式，老人看得更清楚
- 翻译窗口支持暂停 / 停止朗读译文
- 自动记住阅读位置：关掉再打开，问"继续读吗"一键续读
- 自定义发音词典：指定词的正确读法，中文多音字/人名/品牌更好听
- 支持 MOBI / AZW / FB2 电子书格式
- 早间新闻提醒：文件夹里有当天的新闻，打开软件就提示朗读
"""
import os
import json
import re
import hashlib
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from extract import extract_text, clean_for_speech, split_chunks
from speaker import Speaker
from translate import translate

# ---------- 多语言界面 ----------
UI = {
    'zh': {
        'title': '薇阅 · 文字朗读工具 v3.0',
        'app_title': '薇阅',
        'app_sub': '文字朗读工具',
        'btn_en': 'EN',
        'open': '打开文件',
        'library': '书库',
        'cloud_lib': '云端书库',
        'lib_title': '书库',
        'lib_choose': '选择书库文件夹',
        'lib_refresh': '刷新',
        'lib_open': '朗读本书',
        'lib_col_title': '书名',
        'lib_col_author': '作者',
        'lib_col_format': '格式',
        'lib_scanning': '正在扫描书库…',
        'lib_count': '共 %d 本',
        'lib_empty': '这个文件夹里没有找到可朗读的书\n（支持 EPUB / PDF / Word / TXT / MOBI / FB2）',
        'lib_pick_first': '请先选择书库文件夹',
        'lib_tab_local': '本地书库',
        'lib_tab_cloud': '云端书库',
        'cloud_loading': '正在加载云端书库…',
        'cloud_fail': '云端书库加载失败：',
        'cloud_empty': '云端书库还是空的，去手机网页版书库上传几本吧',
        'cloud_no_server': '还没配置云端服务器。\n点右下「服务器设置」，填你自己的服务器地址',
        'cloud_setup': '服务器设置',
        'cloud_setup_hint': '填写你的云端书库服务器地址，例如：\nhttps://你的服务器.com\n（不填则不会连接任何服务器）',
        'cloud_del_key_title': '删除确认',
        'cloud_del_key_prompt': '输入删除密钥（只有书库管理员知道）：',
        'cloud_del_key_empty': '请输入删除密钥',
        'cloud_delete': '删除本书',
        'cloud_del_confirm': '确定从云端删除《%s》吗？删除后无法恢复。',
        'cloud_del_ok': '已删除《%s》',
        'cloud_del_fail': '删除失败：',
        'cloud_opening': '正在打开云端书籍…',
        'cloud_offline': '云端书库需要联网，当前无法连接',
        'local_del_confirm': '确定把《%s》移入书库回收站吗？\n（文件不会被删除，可在「薇阅回收站」文件夹找回）',
        'local_del_ok': '《%s》已移入书库回收站',
        'local_del_fail': '移入回收站失败：',
        'trash': '回收站',
        'trash_title': '回收站',
        'trash_empty': '回收站是空的',
        'trash_restore': '还原',
        'trash_delete': '彻底删除',
        'trash_close': '关闭',
        'trash_restore_ok': '已还原《%s》',
        'trash_del_confirm': '确定彻底删除《%s》吗？\n删除后无法恢复！',
        'trash_del_ok': '已彻底删除《%s》',
        'trash_fail': '操作失败：',
        'trash_need_lib': '请先在「本地书库」里选择一个书库文件夹',
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
        'translate': '翻译',
        'follow': '跟读',
        'ocr': '图片识别',
        'not_started': '尚未开始',
        'no_voices': '(无可用语音)',
        'ctx_here': '从这里开始朗读',
        'ctx_sel': '朗读选中内容',
        'menu_cut': '剪切',
        'menu_copy': '复制',
        'menu_paste': '粘贴',
        'menu_delete': '删除',
        'menu_select_all': '全选',
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
        'resume_title': '继续阅读',
        'resume_ask': '上次你读到《%s》第 %d 段附近。\n要接着往下读吗？',
        'resume_ask2': '上次《%s》还没读完。\n要打开接着读吗？',
        'resume_btn': '续读',
        'pron_dict': '发音词典',
        'pron_dict_title': '自定义发音词典',
        'pron_dict_hint': '让某些词按你指定的读法朗读，例如：\n薇阅 = 薇 阅（多音字、人名、品牌都可以）\n每行一条：原词 = 读法',
        'pron_add': '添加',
        'pron_edit': '修改',
        'pron_del': '删除',
        'pron_clear': '清空',
        'pron_word': '原词',
        'pron_repl': '读法',
        'pron_saved': '发音词典已保存',
        'pron_empty': '原词和读法都不能为空',
        'morning_title': '早间新闻',
        'morning_ready': '早间新闻已就绪：《%s》\n要现在听吗？',
        'morning_none': '早间新闻文件夹里还没有内容',
        'morning_cloud_check': '正在从服务器查找今天的早间新闻…',
        'cloud_update_title': '云端书库有新内容',
        'cloud_update_msg': '云端书库有更新（可能服务器上新加了书或新闻）。\n去「书库 → 云端书库」查看。',
        'tray_morning': '早间新闻',
        'morning_open_fail': '打开早间新闻失败：',
        'ft_mobi': 'Kindle 电子书',
        'ft_fb2': 'FB2 电子书',
        'dlg_save_title': '保存朗读音频',
        'translate_title': '文本翻译',
        'src_label': '原文',
        'dst_label': '译文',
        'translate_btn': '翻译',
        'speak_result': '朗读译文',
        'resume': '继续',
        'translating': '正在翻译…',
        'translate_done': '翻译完成',
        'translate_fail': '翻译失败：',
        'input_first': '请先输入要翻译的文字',
        'speaking': '正在朗读译文…',
        'follow_title': '录音跟读',
        'follow_hint': '听一句 → 跟读 → 回放对比',
        'prev_sentence': '上一句',
        'next_sentence': '下一句',
        'play_original': '▶ 听原句',
        'record_btn': '● 录音',
        'replay': '▶ 回放',
        'follow_repeat': '复读',
        'follow_gap': '间隔',
        'repeat_1': '1 次',
        'repeat_3': '3 次',
        'repeat_5': '5 次',
        'repeat_loop': '循环',
        'gap_05': '0.5 秒',
        'gap_1': '1 秒',
        'gap_2': '2 秒',
        'orig_secs': '原句 %s 秒',
        'rec_live': '录音中 %s 秒（上限 3 分钟）',
        'rec_done': '录音 %s 秒',
        'rec_max': '已达 3 分钟上限，自动停止',
        'recording': '录音中…',
        'recorded': '已录音，可回放',
        'recording_fail': '录音失败：',
        'no_recording': '还没有录音，先点「录音」',
        'replaying': '正在回放…',
        'replay_done': '回放结束，可再录一遍或听原句对比',
        'follow_repeating': '正在复读第 %d 句（第 %d/%d 遍）',
        'follow_looping': '正在循环复读第 %d 句，点「停止」结束',
        'follow_done': '第 %d 句复读完成，可录音或点「下一句」',
        'follow_play_fail': '播放原句失败',
        'no_sentences': '没有可跟读的句子',
        'big_text': '大字号',
        'normal_text': '标准字号',
        'link_title': '输入网址',
        'link_prompt': '粘贴新闻/文章网址，薇阅将抓取正文朗读',
        'fetching': '正在抓取网页…',
        'fetch_fail': '抓取失败：',
        'link_loaded': '已载入网页正文',
        'link_empty': '网页里没提取到正文',
        'link_antibot': '该网站有反爬保护，无法直接抓取正文。\n'
                        '建议：复制正文后粘贴到软件里朗读，'
                        '或下载成文本文件再打开。',
        'ocr_title': '选择图片',
        'ocr_working': '正在识别图片文字…',
        'ocr_done': '已识别图片文字',
        'ocr_fail': '识别失败：',
        'ocr_empty': '图片里没识别到文字',
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
        'title': 'Weiyue Text Reader v3.0',
        'app_title': '薇阅',
        'app_sub': 'Text Reader',
        'btn_en': '中',
        'open': 'Open File',
        'library': 'Library',
        'cloud_lib': 'Cloud Library',
        'lib_title': 'Library',
        'lib_choose': 'Choose Library Folder',
        'lib_refresh': 'Refresh',
        'lib_open': 'Read This Book',
        'lib_col_title': 'Title',
        'lib_col_author': 'Author',
        'lib_col_format': 'Format',
        'lib_scanning': 'Scanning library...',
        'lib_count': '%d books',
        'lib_empty': 'No readable books found here\n(EPUB / PDF / Word / TXT / MOBI / FB2 supported)',
        'lib_pick_first': 'Please choose a library folder first',
        'lib_tab_local': 'Local Library',
        'lib_tab_cloud': 'Cloud Library',
        'cloud_loading': 'Loading cloud library...',
        'cloud_fail': 'Cloud library failed: ',
        'cloud_empty': 'Cloud library is empty. Add books on the phone web page first',
        'cloud_no_server': 'Cloud server is not configured yet.\nClick "Server Settings" and enter your server address',
        'cloud_setup': 'Server Settings',
        'cloud_setup_hint': 'Enter your cloud library server address, e.g.:\nhttps://your-server.com\n(If empty, no server is connected)',
        'cloud_del_key_title': 'Confirm Delete',
        'cloud_del_key_prompt': 'Enter the delete key (only the library admin knows it):',
        'cloud_del_key_empty': 'Please enter the delete key',
        'cloud_delete': 'Delete Book',
        'cloud_del_confirm': 'Delete "%s" from the cloud? This cannot be undone.',
        'cloud_del_ok': 'Deleted "%s"',
        'cloud_del_fail': 'Delete failed: ',
        'cloud_opening': 'Opening cloud book...',
        'cloud_offline': 'Cloud library needs internet, currently offline',
        'local_del_confirm': 'Move "%s" to the library recycle bin?\n(The file is not deleted; you can restore it from the "Weiyue Recycle" folder)',
        'local_del_ok': '"%s" moved to the library recycle bin',
        'local_del_fail': 'Failed to move to recycle bin: ',
        'trash': 'Recycle Bin',
        'trash_title': 'Recycle Bin',
        'trash_empty': 'The recycle bin is empty',
        'trash_restore': 'Restore',
        'trash_delete': 'Delete Forever',
        'trash_close': 'Close',
        'trash_restore_ok': 'Restored "%s"',
        'trash_del_confirm': 'Permanently delete "%s"?\nThis cannot be undone!',
        'trash_del_ok': 'Deleted "%s" forever',
        'trash_fail': 'Operation failed: ',
        'trash_need_lib': 'Choose a library folder in "Local Library" first',
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
        'translate': 'Translate',
        'follow': 'Follow',
        'ocr': 'Image OCR',
        'not_started': 'Not started',
        'no_voices': '(No voices available)',
        'ctx_here': 'Read from Here',
        'ctx_sel': 'Read Selected Text',
        'menu_cut': 'Cut',
        'menu_copy': 'Copy',
        'menu_paste': 'Paste',
        'menu_delete': 'Delete',
        'menu_select_all': 'Select All',
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
        'resume_title': 'Continue Reading',
        'resume_ask': 'You last read "%s" around segment %d.\nContinue from there?',
        'resume_ask2': 'You haven\'t finished "%s".\nOpen it and continue?',
        'resume_btn': 'Resume',
        'pron_dict': 'Pronunciation',
        'pron_dict_title': 'Pronunciation Dictionary',
        'pron_dict_hint': 'Control how certain words are read, e.g.:\nWeiyue = Way-yue (names, brands, homographs)\nOne per line: word = reading',
        'pron_add': 'Add',
        'pron_edit': 'Edit',
        'pron_del': 'Delete',
        'pron_clear': 'Clear',
        'pron_word': 'Word',
        'pron_repl': 'Reading',
        'pron_saved': 'Pronunciation dictionary saved',
        'pron_empty': 'Word and reading cannot be empty',
        'morning_title': 'Morning News',
        'morning_ready': 'Morning news is ready: "%s"\nRead it now?',
        'morning_none': 'No morning news files yet',
        'morning_cloud_check': 'Checking the server for today\'s morning news...',
        'cloud_update_title': 'Cloud Library Updated',
        'cloud_update_msg': 'The cloud library has new content (new books or news may have been added to your server).\nOpen "Library -> Cloud Library" to see it.',
        'tray_morning': 'Morning News',
        'morning_open_fail': 'Failed to open morning news: ',
        'ft_mobi': 'Kindle eBook',
        'ft_fb2': 'FB2 eBook',
        'dlg_save_title': 'Save audio',
        'translate_title': 'Translate',
        'src_label': 'Source',
        'dst_label': 'Translation',
        'translate_btn': 'Translate',
        'speak_result': 'Speak Result',
        'resume': 'Resume',
        'translating': 'Translating...',
        'translate_done': 'Done',
        'translate_fail': 'Translate failed: ',
        'input_first': 'Enter some text first',
        'speaking': 'Speaking translation...',
        'follow_title': 'Follow Reading',
        'follow_hint': 'Listen -> Repeat -> Compare',
        'prev_sentence': 'Prev',
        'next_sentence': 'Next',
        'play_original': 'Listen',
        'record_btn': 'Record',
        'replay': 'Replay',
        'follow_repeat': 'Repeat',
        'follow_gap': 'Gap',
        'repeat_1': '1x',
        'repeat_3': '3x',
        'repeat_5': '5x',
        'repeat_loop': 'Loop',
        'gap_05': '0.5s',
        'gap_1': '1s',
        'gap_2': '2s',
        'orig_secs': 'Original %s s',
        'rec_live': 'Recording %s s (max 3 min)',
        'rec_done': 'Recorded %s s',
        'rec_max': '3-minute limit reached, auto stopped',
        'recording': 'Recording...',
        'recorded': 'Recorded, you can replay',
        'recording_fail': 'Record failed: ',
        'no_recording': 'No recording yet. Click Record first',
        'replaying': 'Replaying...',
        'replay_done': 'Replay done. Record again or listen to the original',
        'follow_repeating': 'Repeating sentence %d (%d/%d)',
        'follow_looping': 'Looping sentence %d. Click Stop to end',
        'follow_done': 'Sentence %d done. Record or go to Next',
        'follow_play_fail': 'Failed to play the original',
        'no_sentences': 'No sentences to follow',
        'big_text': 'Big Text',
        'normal_text': 'Standard Text',
        'link_title': 'Enter URL',
        'link_prompt': 'Paste a news/article URL to read aloud',
        'fetching': 'Fetching page...',
        'fetch_fail': 'Fetch failed: ',
        'link_loaded': 'Web content loaded',
        'link_empty': 'No readable content found',
        'link_antibot': 'This site has anti-bot protection and cannot be '
                        'fetched directly.\nTip: copy the text and paste it '
                        'here, or open a downloaded text file instead.',
        'ocr_title': 'Select Image',
        'ocr_working': 'Recognizing text...',
        'ocr_done': 'Text recognized',
        'ocr_fail': 'OCR failed: ',
        'ocr_empty': 'No text found in image',
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
        self._last_resume_save = 0.0
        self._follow_win = None
        self._tr_win = None
        self._lib_win = None
        self._lib_last_dir = ''
        self._cloud_base = ''
        self._cloud_del_key = ''
        self._cloud_books_sig = ''
        self._lib_load_config()

        self._set_window_icon()
        self._build_ui()
        self._setup_tray()
        self._bind_shortcuts()
        try:
            root.after(300, self._refresh_voices)
        except Exception:
            pass
        try:
            root.after(900, self._check_startup_resume)
            root.after(1200, self._check_morning)
            root.after(1500, self._check_cloud_updates)
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

    def _toggle_big(self):
        self._big = not self._big
        size = 18 if self._big else 13
        try:
            self.text.configure(font=(FONT, size))
        except Exception:
            pass
        self.btn_big.config(text=self.T('normal_text' if self._big
                                        else 'big_text'))
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
        self.btn_library.config(text=self.T('library'))
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
        self.btn_translate.config(text=self.T('translate'))
        self.btn_follow.config(text=self.T('follow'))
        self.btn_ocr.config(text=self.T('ocr'))
        self.btn_pron.config(text=self.T('pron_dict'))
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
            self._ctx.add_separator()
            self._ctx.add_command(label=self.T('menu_cut'),
                                  command=self._edit_cut)
            self._ctx.add_command(label=self.T('menu_copy'),
                                  command=self._edit_copy)
            self._ctx.add_command(label=self.T('menu_paste'),
                                  command=self._edit_paste)
            self._ctx.add_command(label=self.T('menu_delete'),
                                  command=self._edit_delete)
            self._ctx.add_command(label=self.T('menu_select_all'),
                                  command=self._edit_select_all)
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
                pystray.MenuItem(self.T('tray_morning'), self._tray_morning),
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
        style.configure("Min.Treeview",
                        background=COL_PANEL, fieldbackground=COL_PANEL,
                        foreground=COL_BLACK, rowheight=28,
                        bordercolor=COL_LINE, lightcolor=COL_PANEL,
                        darkcolor=COL_LINE, relief="flat")
        style.map("Min.Treeview",
                  background=[('selected', COL_HL)],
                  foreground=[('selected', COL_BLACK)])
        style.configure("Min.Treeview.Heading",
                        background=COL_PANEL2, foreground=COL_BLACK,
                        relief="flat", padding=(6, 6))
        style.map("Min.Treeview.Heading",
                  background=[('active', COL_PANEL2)])

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
        self.btn_library = self._flat_btn(file_row, self.T('library'),
                                          COL_PANEL, COL_BLACK,
                                          self.open_library, padx=16)
        self.btn_library.pack(side=tk.LEFT, padx=(8, 0))
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

        # ===== 标记 + 工具行（疏）：打标记 / 从标记朗读 / 翻译 / 跟读 / 读链接 =====
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
        self.btn_translate = self._flat_btn(mark_row, self.T('translate'),
                                            COL_PANEL, COL_BLACK,
                                            self.open_translate,
                                            padx=12, pady=5, font_size=10)
        self.btn_translate.pack(side=tk.LEFT)
        self.btn_follow = self._flat_btn(mark_row, self.T('follow'),
                                         COL_PANEL, COL_BLACK,
                                         self.open_follow,
                                         padx=12, pady=5, font_size=10)
        self.btn_follow.pack(side=tk.LEFT, padx=6)
        self.btn_ocr = self._flat_btn(mark_row, self.T('ocr'),
                                      COL_PANEL, COL_BLACK,
                                      self.scan_image,
                                      padx=12, pady=5, font_size=10)
        self.btn_ocr.pack(side=tk.LEFT, padx=6)
        self.btn_pron = self._flat_btn(mark_row, self.T('pron_dict'),
                                       COL_PANEL, COL_BLACK,
                                       self.open_pron_dict,
                                       padx=12, pady=5, font_size=10)
        self.btn_pron.pack(side=tk.LEFT, padx=6)
        self.mark_lbl = tk.Label(mark_row, text="", bg=COL_BG, fg=COL_GRAY,
                                 font=_f(10))
        self.mark_lbl.pack(side=tk.LEFT, padx=14)
        self.btn_big = self._flat_btn(mark_row, self.T('big_text'),
                                      COL_PANEL, COL_BLACK, self._toggle_big,
                                      padx=12, pady=5, font_size=10)
        self.btn_big.pack(side=tk.RIGHT)
        self._big = False

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
        self._ctx.add_separator()
        self._ctx.add_command(label=self.T('menu_cut'),
                              command=self._edit_cut)
        self._ctx.add_command(label=self.T('menu_copy'),
                              command=self._edit_copy)
        self._ctx.add_command(label=self.T('menu_paste'),
                              command=self._edit_paste)
        self._ctx.add_command(label=self.T('menu_delete'),
                              command=self._edit_delete)
        self._ctx.add_command(label=self.T('menu_select_all'),
                              command=self._edit_select_all)
        self.text.bind("<Button-3>", self._show_ctx)

    def _edit_cut(self):
        self.text.event_generate('<<Cut>>')

    def _edit_copy(self):
        self.text.event_generate('<<Copy>>')

    def _edit_paste(self):
        self.text.event_generate('<<Paste>>')

    def _edit_delete(self):
        try:
            r = self.text.tag_ranges(tk.SEL)
            if r:
                self.text.delete(r[0], r[1])
        except Exception:
            pass

    def _edit_select_all(self):
        try:
            self.text.tag_add(tk.SEL, '1.0', 'end')
            self.text.mark_set('insert', 'end')
            self.text.see('insert')
        except Exception:
            pass

    def _bind_text_menu(self, widget):
        """给任意文本控件绑定右键编辑菜单（剪切/复制/粘贴/删除/全选）。"""
        menu = tk.Menu(widget, tearoff=0, font=_f(10),
                       bg=COL_PANEL, fg=COL_BLACK,
                       activebackground=COL_BLACK,
                       activeforeground=COL_PANEL,
                       bd=1, relief="solid")

        def _cut():
            widget.event_generate('<<Cut>>')

        def _copy():
            widget.event_generate('<<Copy>>')

        def _paste():
            widget.event_generate('<<Paste>>')

        def _delete():
            try:
                r = widget.tag_ranges(tk.SEL)
                if r:
                    widget.delete(r[0], r[1])
            except Exception:
                pass

        def _select_all():
            try:
                widget.tag_add(tk.SEL, '1.0', 'end')
                widget.mark_set('insert', 'end')
                widget.see('insert')
            except Exception:
                pass

        def _show(event):
            try:
                widget.mark_set("insert", "@%d,%d" % (event.x, event.y))
                menu.delete(0, 'end')
                menu.add_command(label=self.T('menu_cut'), command=_cut)
                menu.add_command(label=self.T('menu_copy'), command=_copy)
                menu.add_command(label=self.T('menu_paste'), command=_paste)
                menu.add_command(label=self.T('menu_delete'), command=_delete)
                menu.add_command(label=self.T('menu_select_all'),
                                 command=_select_all)
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    menu.grab_release()
                except Exception:
                    pass

        widget.bind("<Button-3>", _show)

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
                pystray.MenuItem(self.T('tray_morning'), self._tray_morning),
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

    def _tray_morning(self, icon=None, item=None):
        self.root.after(0, self._open_latest_morning)

    def _tray_quit(self, icon=None, item=None):
        self._save_resume(force=True)
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
                        "*.pdf *.docx *.doc *.txt *.md *.epub *.mobi *.azw "
                        "*.azw3 *.fb2 *.html *.htm"),
                       (self.T('ft_pdf'), "*.pdf"),
                       (self.T('ft_word'), "*.docx *.doc"),
                       (self.T('ft_epub'), "*.epub"),
                       (self.T('ft_mobi'), "*.mobi *.azw *.azw3"),
                       (self.T('ft_fb2'), "*.fb2"),
                       (self.T('ft_web'), "*.html *.htm"),
                       (self.T('ft_text'), "*.txt *.md"),
                       (self.T('ft_all'), "*.*")])
        if not path:
            return
        if getattr(self, '_open_pending', False):
            return
        self._skip_resume_ask = False
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

    def _open_path_quiet(self, path, skip_resume_ask=False, auto_read=False):
        """后台打开指定路径（用于启动续读 / 早间新闻 / AI 推送内容）。

        auto_read=True 时：打开完成后自动从头朗读（适合早间新闻、
        AI 推送的比分/提醒等内容，点了就直接听）。
        """
        if not path or not os.path.isfile(path):
            return
        if getattr(self, '_open_pending', False):
            return
        self._skip_resume_ask = bool(skip_resume_ask)
        self._auto_read_after_open = bool(auto_read)
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
        auto_read = getattr(self, '_auto_read_after_open', False)
        self._auto_read_after_open = False
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
        self.state_lbl.config(text=self.T('loading'), fg=COL_BLACK)
        self.root.update_idletasks()
        self._load_text(text)
        self.file_lbl.config(text=os.path.basename(path), fg=COL_BLACK)
        self.state_lbl.config(text=self.T('loaded', len(self.full_text)),
                              fg=COL_BLUE)
        if not getattr(self, '_skip_resume_ask', False):
            self._ask_resume()
        else:
            self._skip_resume_ask = False
            self._auto_jump_resume()
        if auto_read:
            if self.full_text:
                self._start_reading(self.full_text, base=0, label='read_all')

    def _auto_jump_resume(self):
        """启动续读确认后：自动跳到上次位置开始朗读。"""
        if not self._resume or not self._resume.get('path'):
            return
        try:
            path = os.path.normcase(os.path.abspath(self.current_path))
            if path != self._resume.get('path'):
                return
            off = int(self._resume.get('offset', 0) or 0)
            if 0 < off < len(self.full_text):
                try:
                    self.text.mark_set("insert", "1.0+%dc" % off)
                    self.text.see("insert")
                except Exception:
                    pass
                self._start_reading(self.full_text[off:], base=off,
                                    label='read_cursor')
        except Exception:
            pass

    def _load_text(self, text):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
        self.text.see("1.0")
        self.text.mark_set("insert", "1.0")

    # ---------- 自定义发音词典 ----------
    def _apply_pron_dict(self, text):
        """朗读前按发音词典替换文本（长词优先，避免部分替换）。"""
        if not text or not self._pron_dict:
            return text
        out = text
        for word, repl in sorted(self._pron_dict,
                                 key=lambda x: len(x[0] or ''),
                                 reverse=True):
            if word and repl and word in out:
                out = out.replace(word, repl)
        return out

    def open_pron_dict(self):
        """发音词典窗口：添加/修改/删除 原词=读法 条目。"""
        win = tk.Toplevel(self.root)
        win.title(self.T('pron_dict_title'))
        win.geometry('520x420')
        win.configure(bg=COL_BG)
        win.transient(self.root)
        win.minsize(440, 320)

        tk.Label(win, text=self.T('pron_dict_hint'), bg=COL_BG, fg=COL_GRAY,
                 font=_f(10), justify='left', anchor='w',
                 wraplength=470).pack(fill=tk.X, padx=18, pady=(14, 6))

        box = tk.Frame(win, bg=COL_BG)
        box.pack(fill=tk.BOTH, expand=True, padx=18, pady=4)
        lb = tk.Listbox(box, font=_f(11), bg=COL_PANEL, fg=COL_BLACK,
                        selectbackground=COL_HL, selectforeground=COL_BLACK,
                        relief="sunken", bd=1,
                        highlightbackground=COL_LINE,
                        highlightthickness=2)
        sb = tk.Scrollbar(box, command=lb.yview, bg=COL_BG,
                          troughcolor=COL_LINE, relief="flat", bd=0)
        lb.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def refresh():
            lb.delete(0, tk.END)
            for word, repl in self._pron_dict:
                lb.insert(tk.END, '%s = %s' % (word, repl))

        def add():
            word = simpledialog.askstring(self.T('pron_dict_title'),
                                          self.T('pron_word'), parent=win)
            if word is None:
                return
            word = word.strip()
            repl = simpledialog.askstring(self.T('pron_dict_title'),
                                          self.T('pron_repl'), parent=win)
            if repl is None:
                return
            repl = repl.strip()
            if not word or not repl:
                messagebox.showinfo(self.T('pron_dict_title'),
                                    self.T('pron_empty'), parent=win)
                return
            self._pron_dict = [(w, r) for w, r in self._pron_dict
                               if w != word]
            self._pron_dict.append((word, repl))
            self._lib_save_config()
            refresh()
            self.state_lbl.config(text=self.T('pron_saved'), fg=COL_BLUE)

        def edit():
            sel = lb.curselection()
            if not sel:
                return
            old_word, old_repl = self._pron_dict[sel[0]]
            word = simpledialog.askstring(self.T('pron_dict_title'),
                                          self.T('pron_word'),
                                          initialvalue=old_word, parent=win)
            if word is None:
                return
            word = word.strip()
            repl = simpledialog.askstring(self.T('pron_dict_title'),
                                          self.T('pron_repl'),
                                          initialvalue=old_repl, parent=win)
            if repl is None:
                return
            repl = repl.strip()
            if not word or not repl:
                messagebox.showinfo(self.T('pron_dict_title'),
                                    self.T('pron_empty'), parent=win)
                return
            self._pron_dict = [(w, r) for w, r in self._pron_dict
                               if w != old_word]
            self._pron_dict.append((word, repl))
            self._lib_save_config()
            refresh()
            self.state_lbl.config(text=self.T('pron_saved'), fg=COL_BLUE)

        def delete():
            sel = lb.curselection()
            if not sel:
                return
            self._pron_dict.pop(sel[0])
            self._lib_save_config()
            refresh()
            self.state_lbl.config(text=self.T('pron_saved'), fg=COL_BLUE)

        def clear():
            if not self._pron_dict:
                return
            if not messagebox.askyesno(self.T('pron_dict_title'),
                                       self.T('pron_clear') + '?',
                                       parent=win):
                return
            self._pron_dict = []
            self._lib_save_config()
            refresh()
            self.state_lbl.config(text=self.T('pron_saved'), fg=COL_BLUE)

        btns = tk.Frame(win, bg=COL_BG)
        btns.pack(fill=tk.X, padx=18, pady=(8, 14))
        for text_key, cmd in (('pron_add', add), ('pron_edit', edit),
                              ('pron_del', delete), ('pron_clear', clear)):
            b = self._flat_btn(btns, self.T(text_key), COL_PANEL, COL_BLACK,
                               cmd, padx=12, pady=5, font_size=10)
            b.pack(side=tk.LEFT, padx=(0, 6))
        refresh()

    # ---------- 自动记住阅读位置 ----------
    def _current_offset(self):
        """取当前朗读位置对应的原文偏移（优先当前段落起点）。"""
        if self._current_chunk > 0 and self._chunk_ranges and \
                self._current_chunk - 1 < len(self._chunk_ranges):
            rng = self._chunk_ranges[self._current_chunk - 1]
            if rng:
                return rng[0]
        try:
            return self._index_to_offset("insert")
        except Exception:
            return 0

    def _save_resume(self, force=False):
        """把当前进度存进配置（限频，防频繁写盘）。"""
        if not self.current_path or not self.full_text:
            return
        now = time.time()
        if not force and now - self._last_resume_save < 3:
            return
        self._last_resume_save = now
        try:
            off = self._current_offset()
            self._resume = {
                'path': os.path.normcase(os.path.abspath(self.current_path)),
                'offset': max(0, min(off, len(self.full_text))),
                'time': now,
            }
            self._lib_save_config()
        except Exception:
            pass

    def _clear_resume(self):
        if self._resume:
            self._resume = None
            self._lib_save_config()

    def _ask_resume(self):
        """刚打开文件后，如果和上次进度匹配，问是否续读。"""
        if not self.current_path or not self.full_text or not self._resume:
            return
        try:
            path = os.path.normcase(os.path.abspath(self.current_path))
            if path != self._resume.get('path'):
                return
            off = int(self._resume.get('offset', 0) or 0)
            if not (0 < off < len(self.full_text)):
                return
            seg = 1
            if self._chunk_ranges:
                for i, rng in enumerate(self._chunk_ranges, 1):
                    if rng and rng[0] >= off:
                        seg = i
                        break
            if messagebox.askyesno(
                    self.T('resume_title'),
                    self.T('resume_ask', os.path.basename(self.current_path),
                           seg)):
                try:
                    self.text.mark_set("insert", "1.0+%dc" % off)
                    self.text.see("insert")
                except Exception:
                    pass
                self._start_reading(self.full_text[off:], base=off,
                                    label='read_cursor')
            else:
                self._clear_resume()
        except Exception:
            pass

    def _check_startup_resume(self):
        """启动时：如果有上次没读完的书，问要不要接着读。"""
        if not self._resume or not self._resume.get('path'):
            return
        try:
            path = self._resume.get('path')
            if not os.path.isfile(path):
                self._clear_resume()
                return
            if messagebox.askyesno(
                    self.T('resume_title'),
                    self.T('resume_ask2', os.path.basename(path))):
                self._open_path_quiet(path, skip_resume_ask=True)
        except Exception:
            pass

    # ---------- 早间新闻（AI agent 内容接入） ----------
    def _morning_dir(self):
        """早间新闻文件夹：程序目录下的「早间新闻」，没有就自动创建。"""
        here = os.path.dirname(os.path.abspath(__file__))
        d = os.path.join(here, '早间新闻')
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass
        return d

    def _list_morning_files(self):
        d = self._morning_dir()
        if not os.path.isdir(d):
            return []
        files = []
        try:
            for fn in os.listdir(d):
                if not fn.lower().endswith(('.txt', '.md', '.text')):
                    continue
                p = os.path.join(d, fn)
                try:
                    files.append((os.path.getmtime(p), p, fn))
                except Exception:
                    continue
        except Exception:
            return []
        files.sort(key=lambda x: x[0], reverse=True)
        return files

    def _check_morning(self):
        """启动时检查：本地或云端有没有当天的早间新闻，有就提示朗读。"""
        try:
            today = time.strftime('%Y-%m-%d')
            files = self._list_morning_files()
            if self._morning_last == today:
                return
            if files:
                mt, p, fn = files[0]
                self._morning_last = today
                self._lib_save_config()
                if messagebox.askyesno(
                        self.T('morning_title'),
                        self.T('morning_ready', fn)):
                    self._open_path_quiet(p)
                return
            # 本地没有：去云端服务器找当天的早间新闻
            base = self._cloud_base_url()
            if base:
                self._fetch_cloud_morning(base, today)
        except Exception:
            pass

    def _fetch_cloud_morning(self, base, today, retries=10):
        """从云端服务器拉取当天的早间新闻（后台线程，不卡界面）。

        网络未就绪等原因拉取失败时，会每隔 30 秒自动重试（最多 10 次），
        避免"开机就打开软件"时错过当天新闻。
        """

        def work():
            tmp = None
            try:
                name = '早间新闻-%s.txt' % today
                url = base + urllib.parse.quote('/早间新闻/' + name)
                req = urllib.request.Request(
                    url, headers={'User-Agent': 'Weiyue/3.0'})
                buf = urllib.request.urlopen(req, timeout=12).read()
                if not buf or not buf.strip():
                    return
                fd, tmp = tempfile.mkstemp(suffix='.txt',
                                           prefix='weiyue_morning_')
                with os.fdopen(fd, 'wb') as fh:
                    fh.write(buf)

                def ask():
                    if self._morning_last == today:
                        return
                    self._morning_last = today
                    self._lib_save_config()
                    if messagebox.askyesno(
                            self.T('morning_title'),
                            self.T('morning_ready', name)):
                        self._open_path_quiet(tmp, skip_resume_ask=True,
                                               auto_read=True)
                    else:
                        try:
                            os.remove(tmp)
                        except Exception:
                            pass

                self.root.after(0, ask)
            except Exception:
                if tmp:
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
                # 拉取失败：今天还没提示过的话，稍后自动重试
                if retries > 0 and self._morning_last != today:
                    self.root.after(
                        30000,
                        lambda: self._fetch_cloud_morning(base, today,
                                                          retries - 1))

        threading.Thread(target=work, daemon=True).start()

    def _open_latest_morning(self):
        """托盘菜单：打开最新的早间新闻（本地没有就去云端拉）。"""
        try:
            files = self._list_morning_files()
            if not files:
                base = self._cloud_base_url()
                if base:
                    today = time.strftime('%Y-%m-%d')
                    self._fetch_cloud_morning(base, today)
                    messagebox.showinfo(
                        self.T('morning_title'),
                        self.T('morning_cloud_check'))
                    return
                messagebox.showinfo(self.T('morning_title'),
                                    self.T('morning_none'))
                return
            mt, p, fn = files[0]
            self._open_path_quiet(p, skip_resume_ask=True, auto_read=True)
        except Exception as e:
            messagebox.showerror(self.T('morning_title'),
                                 self.T('morning_open_fail') + str(e))

    def _cloud_books_signature(self, books):
        """根据书单内容生成指纹，用于判断云端书库是否有变化。"""
        try:
            parts = []
            for b in books or []:
                parts.append('%s|%s|%s' % (b.get('title', ''),
                                           b.get('author', ''),
                                           b.get('file', '')))
            raw = '\n'.join(sorted(parts)).encode('utf-8', 'ignore')
            return hashlib.md5(raw).hexdigest()
        except Exception:
            return ''

    def _check_cloud_updates(self):
        """启动时检查云端书库有没有变化（后台线程，不卡界面）。"""
        base = self._cloud_base_url()
        if not base:
            return

        def work():
            try:
                req = urllib.request.Request(
                    base + '/books.json',
                    headers={'User-Agent': 'Weiyue/3.0'})
                data = json.loads(urllib.request.urlopen(
                    req, timeout=12).read().decode('utf-8'))
                sig = self._cloud_books_signature(data)
            except Exception:
                return
            if not sig:
                return
            old = self._cloud_books_sig
            self._cloud_books_sig = sig
            self._lib_save_config()
            if old and old != sig:
                self.root.after(
                    0, lambda: messagebox.showinfo(
                        self.T('cloud_update_title'),
                        self.T('cloud_update_msg')))

        threading.Thread(target=work, daemon=True).start()

    # ---------- 书库 ----------
    def _cloud_base_url(self):
        """云端书库服务器地址（去掉结尾斜杠），未配置返回空串。"""
        return (self._cloud_base or '').strip().rstrip('/')

    def _get_cloud_del_key(self, parent=None):
        """取删除密钥：已记住直接用，否则弹出输入框（输一次记住）。"""
        if self._cloud_del_key:
            return self._cloud_del_key
        key = simpledialog.askstring(
            self.T('cloud_del_key_title'),
            self.T('cloud_del_key_prompt'),
            show='*', parent=parent)
        if key:
            self._cloud_del_key = key.strip()
            self._lib_save_config()
        return self._cloud_del_key

    def open_library(self):
        if self._lib_win is not None and self._lib_win.winfo_exists():
            self._lib_win.lift()
            return
        win = tk.Toplevel(self.root)
        win.title(self.T('lib_title'))
        win.geometry('820x600')
        win.configure(bg=COL_BG)
        win.minsize(680, 460)
        win.transient(self.root)

        top = tk.Frame(win, bg=COL_BG)
        top.pack(fill=tk.X, padx=18, pady=(16, 8))
        btn_local = self._flat_btn(top, self.T('lib_tab_local'), COL_PANEL2,
                                   COL_BLACK, None, padx=12, pady=5,
                                   font_size=10)
        btn_local.pack(side=tk.LEFT)
        btn_cloud = self._flat_btn(top, self.T('lib_tab_cloud'), COL_PANEL,
                                   COL_BLACK, None, padx=12, pady=5,
                                   font_size=10)
        btn_cloud.pack(side=tk.LEFT, padx=(6, 14))
        path_lbl = tk.Label(top, text='', bg=COL_BG, fg=COL_GRAY,
                            font=_f(10), anchor='w')
        path_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_choose = self._flat_btn(top, self.T('lib_choose'), COL_PANEL,
                                    COL_BLACK, None, padx=12, pady=5,
                                    font_size=10)
        btn_choose.pack(side=tk.RIGHT)
        btn_refresh = self._flat_btn(top, self.T('lib_refresh'), COL_PANEL,
                                     COL_BLACK, None, padx=12, pady=5,
                                     font_size=10)
        btn_refresh.pack(side=tk.RIGHT, padx=(0, 8))

        mid = tk.Frame(win, bg=COL_BG)
        mid.pack(fill=tk.BOTH, expand=True, padx=18)
        tree = ttk.Treeview(mid, columns=('title', 'author', 'fmt'),
                            show='headings', style='Min.Treeview')
        tree.heading('title', text=self.T('lib_col_title'))
        tree.heading('author', text=self.T('lib_col_author'))
        tree.heading('fmt', text=self.T('lib_col_format'))
        tree.column('title', width=380, anchor='w')
        tree.column('author', width=230, anchor='w')
        tree.column('fmt', width=90, anchor='center')
        sb = ttk.Scrollbar(mid, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        bottom = tk.Frame(win, bg=COL_BG)
        bottom.pack(fill=tk.X, padx=18, pady=(10, 14))
        cnt_lbl = tk.Label(bottom, text='', bg=COL_BG, fg=COL_GRAY,
                           font=_f(10))
        cnt_lbl.pack(side=tk.LEFT)
        btn_open = self._flat_btn(bottom, self.T('lib_open'), COL_PANEL2,
                                  COL_BLACK, None, padx=16, pady=6,
                                  font_size=11)
        btn_open.pack(side=tk.RIGHT)
        btn_setup = self._flat_btn(bottom, self.T('cloud_setup'), COL_PANEL,
                                   COL_BLACK, None, padx=12, pady=6,
                                   font_size=10)
        btn_setup.pack(side=tk.RIGHT, padx=(0, 8))
        btn_del = self._flat_btn(bottom, self.T('cloud_delete'), COL_PANEL,
                                 COL_BLACK, None, padx=16, pady=6,
                                 font_size=11)
        btn_del.pack(side=tk.RIGHT, padx=(0, 8))
        btn_trash = self._flat_btn(bottom, self.T('trash'), COL_PANEL,
                                   COL_BLACK, None, padx=12, pady=6,
                                   font_size=10)
        btn_trash.pack(side=tk.RIGHT, padx=(0, 8))
        btn_open.config(state='disabled')
        btn_del.config(state='disabled')

        self._lib_win = win
        self._lib_path_lbl = path_lbl
        self._lib_tree = tree
        self._lib_cnt = cnt_lbl
        self._lib_btn_open = btn_open
        self._lib_books = []
        self._cloud_books = []
        mode = {'v': 'local'}

        def _clear_tree():
            items = tree.get_children()
            if items:
                tree.delete(*items)

        def _scan_local():
            self._lib_scan(self._lib_last_dir or '')

        def _load_cloud():
            _clear_tree()
            cnt_lbl.config(text='')
            base = self._cloud_base_url()
            if not base:
                path_lbl.config(text=self.T('cloud_no_server'), fg=COL_GRAY)
                return
            path_lbl.config(text=self.T('cloud_loading'), fg=COL_GRAY)

            def work():
                try:
                    req = urllib.request.Request(
                        base + '/books.json',
                        headers={'User-Agent': 'Weiyue/3.0'})
                    data = json.loads(urllib.request.urlopen(
                        req, timeout=15).read().decode('utf-8'))
                except Exception as e:
                    self.root.after(0, lambda: _cloud_fail(str(e)))
                    return
                self.root.after(0, lambda: _cloud_show(data))
            threading.Thread(target=work, daemon=True).start()

        def _cloud_setup():
            cur = self._cloud_base_url()
            val = simpledialog.askstring(
                self.T('cloud_setup'),
                self.T('cloud_setup_hint'),
                initialvalue=cur, parent=win)
            if val is None:
                return
            self._cloud_base = val.strip().rstrip('/')
            self._lib_save_config()
            if mode['v'] == 'cloud':
                _load_cloud()

        def _cloud_fail(msg):
            _clear_tree()
            cnt_lbl.config(text='')
            path_lbl.config(text=self.T('cloud_fail') + msg, fg=COL_RED)

        def _cloud_show(books):
            self._cloud_books = books or []
            _clear_tree()
            for i, b in enumerate(self._cloud_books):
                tree.insert('', 'end', iid=str(i),
                            values=(b.get('title', ''), b.get('author', ''),
                                    b.get('format', 'TXT')))
            sig = self._cloud_books_signature(self._cloud_books)
            if sig:
                self._cloud_books_sig = sig
                self._lib_save_config()
            path_lbl.config(text=self.T('cloud_lib'), fg=COL_GRAY)
            cnt_lbl.config(text=self.T('lib_count', len(self._cloud_books)))

        def _set_mode(v):
            mode['v'] = v
            btn_local.config(bg=COL_PANEL2 if v == 'local' else COL_PANEL)
            btn_cloud.config(bg=COL_PANEL2 if v == 'cloud' else COL_PANEL)
            btn_open.config(state='disabled')
            btn_del.config(state='disabled')
            btn_setup.config(state='normal')
            _clear_tree()
            cnt_lbl.config(text='')
            if v == 'cloud':
                btn_choose.pack_forget()
                btn_refresh.pack(side=tk.RIGHT, padx=(0, 8))
                btn_trash.pack_forget()
                _load_cloud()
            else:
                btn_choose.pack(side=tk.RIGHT)
                btn_refresh.pack(side=tk.RIGHT, padx=(0, 8))
                btn_trash.pack(side=tk.RIGHT, padx=(0, 8))
                path_lbl.config(text=self._lib_last_dir
                                or self.T('lib_pick_first'),
                                fg=COL_GRAY)
                _scan_local()

        def _choose():
            d = filedialog.askdirectory(title=self.T('lib_choose'),
                                        parent=win,
                                        initialdir=self._lib_last_dir or '')
            if d:
                self._lib_last_dir = d
                self._lib_save_config()
                _scan_local()

        def _refresh():
            if mode['v'] == 'cloud':
                _load_cloud()
            elif self._lib_last_dir:
                _scan_local()

        def _open_sel():
            sel = tree.selection()
            if not sel:
                return
            iid = sel[0]
            if mode['v'] == 'cloud':
                _open_cloud(iid)
                return
            if iid.isdigit() and int(iid) < len(self._lib_books):
                self._load_book_from_library(self._lib_books[int(iid)][0])

        def _open_cloud(iid):
            try:
                i = int(iid)
                b = self._cloud_books[i]
            except Exception:
                return
            f = b.get('file', '')
            if not f:
                return
            base = self._cloud_base_url()
            if not base:
                path_lbl.config(text=self.T('cloud_no_server'), fg=COL_GRAY)
                return
            url = base + '/' + urllib.parse.quote(f)
            path_lbl.config(text=self.T('cloud_opening'), fg=COL_BLACK)

            def work():
                tmp = None
                try:
                    req = urllib.request.Request(
                        url, headers={'User-Agent': 'Weiyue/3.0'})
                    buf = urllib.request.urlopen(req, timeout=30).read()
                    fd, tmp = tempfile.mkstemp(suffix='.txt',
                                               prefix='weiyue_cloud_')
                    with os.fdopen(fd, 'wb') as fh:
                        fh.write(buf)
                    self.root.after(
                        0, lambda: self._load_book_from_library(tmp))
                except Exception as e:
                    if tmp:
                        try:
                            os.remove(tmp)
                        except Exception:
                            pass
                    self.root.after(0, lambda: _cloud_fail(str(e)))
            threading.Thread(target=work, daemon=True).start()

        def _del_local(iid):
            """本地书库删除：把书移入书库回收站文件夹（不真正删除）。"""
            try:
                i = int(iid)
                p, title, author, fmt = self._lib_books[i]
            except Exception:
                return
            if not messagebox.askyesno(
                    self.T('dlg_tip'),
                    self.T('local_del_confirm', title or os.path.basename(p))):
                return
            try:
                trash = os.path.join(os.path.dirname(p), '薇阅回收站')
                os.makedirs(trash, exist_ok=True)
                dst = os.path.join(trash, os.path.basename(p))
                n = 1
                while os.path.exists(dst):
                    root_n, ext_n = os.path.splitext(os.path.basename(p))
                    dst = os.path.join(trash, '%s_%d%s' % (root_n, n, ext_n))
                    n += 1
                os.rename(p, dst)
            except Exception as e:
                messagebox.showerror(self.T('dlg_tip'),
                                     self.T('local_del_fail') + str(e))
                return
            cnt_lbl.config(text=self.T('local_del_ok', title
                                       or os.path.basename(p)), fg=COL_BLUE)
            _scan_local()

        def _del_cloud(iid):
            try:
                i = int(iid)
                b = self._cloud_books[i]
            except Exception:
                return
            title = b.get('title', '')
            if not messagebox.askyesno(
                    self.T('dlg_tip'),
                    self.T('cloud_del_confirm', title)):
                return
            f = b.get('file', '')
            base = self._cloud_base_url()
            if not base:
                path_lbl.config(text=self.T('cloud_no_server'), fg=COL_GRAY)
                return
            key = self._get_cloud_del_key(parent=win)
            if not key:
                return
            url = base + '/wydel'
            body = urllib.parse.urlencode(
                {'file': f, 'key': key}).encode('utf-8')

            def work():
                try:
                    req = urllib.request.Request(
                        url, data=body,
                        headers={'User-Agent': 'Weiyue/3.0',
                                 'Content-Type': 'application/x-www-form-urlencoded'})
                    r = urllib.request.urlopen(req, timeout=15).read()
                    r = r.decode('utf-8', 'ignore').strip()
                except Exception as e:
                    self.root.after(0, lambda: _cloud_fail(str(e)))
                    return
                self.root.after(0, lambda: _cloud_del_done(r, title))
            threading.Thread(target=work, daemon=True).start()

        def _cloud_del_done(r, title):
            if r == 'OK':
                cnt_lbl.config(text=self.T('cloud_del_ok', title),
                               fg=COL_BLUE)
                _load_cloud()
            else:
                _cloud_fail(r)

        def _on_select():
            has = bool(tree.selection())
            btn_open.config(state='normal' if has else 'disabled')
            btn_del.config(state='normal' if has else 'disabled')

        btn_local.config(command=lambda: _set_mode('local'))
        btn_cloud.config(command=lambda: _set_mode('cloud'))
        btn_choose.config(command=_choose)
        btn_refresh.config(command=_refresh)
        btn_open.config(command=_open_sel)
        btn_setup.config(command=_cloud_setup)
        btn_trash.config(command=self._open_trash)
        btn_del.config(command=lambda: (
            _del_cloud(tree.selection()[0])
            if mode['v'] == 'cloud' and tree.selection()
            else _del_local(tree.selection()[0])
            if mode['v'] == 'local' and tree.selection() else None))
        tree.bind('<<TreeviewSelect>>', lambda e: _on_select())
        tree.bind('<Double-1>', lambda e: _open_sel())

        _set_mode('local')
    def _lib_config_path(self):
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(here, 'weiyue_config.json')

    def _lib_load_config(self):
        self._pron_dict = []
        self._resume = None
        self._morning_last = ''
        try:
            with open(self._lib_config_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._lib_last_dir = data.get('last_library', '') or ''
            self._pron_dict = data.get('pron_dict', []) or []
            self._resume = data.get('resume')
            self._morning_last = data.get('morning_last', '') or ''
            self._cloud_base = (data.get('cloud_base', '') or '').strip()
            self._cloud_del_key = data.get('cloud_del_key', '') or ''
            self._cloud_books_sig = data.get('cloud_books_sig', '') or ''
        except Exception:
            self._lib_last_dir = ''

    def _lib_save_config(self):
        try:
            with open(self._lib_config_path(), 'w', encoding='utf-8') as f:
                json.dump({
                    'last_library': self._lib_last_dir,
                    'pron_dict': self._pron_dict,
                    'resume': self._resume,
                    'morning_last': self._morning_last,
                    'cloud_base': self._cloud_base,
                    'cloud_del_key': self._cloud_del_key,
                    'cloud_books_sig': self._cloud_books_sig,
                }, f, ensure_ascii=False)
        except Exception:
            pass

    def _lib_scan(self, root_dir):
        if self._lib_win is None:
            return
        if not root_dir or not os.path.isdir(root_dir):
            self._lib_path_lbl.config(text=self.T('lib_pick_first'),
                                      fg=COL_GRAY)
            self._lib_cnt.config(text='')
            self._lib_tree.delete(*self._lib_tree.get_children())
            self._lib_books = []
            return
        self._lib_path_lbl.config(text=root_dir, fg=COL_BLACK)
        self._lib_cnt.config(text=self.T('lib_scanning'), fg=COL_BLACK)
        self._lib_tree.delete(*self._lib_tree.get_children())
        self._lib_books = []

        def work():
            books = self._collect_books(root_dir)
            self.root.after(0, lambda: self._lib_show(books))

        threading.Thread(target=work, daemon=True).start()

    def _collect_books(self, root_dir):
        exts = ('.pdf', '.docx', '.doc', '.txt', '.md', '.text',
                '.epub', '.mobi', '.azw', '.azw3', '.fb2',
                '.html', '.htm')
        books = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # 跳过回收站文件夹（删除的书不该再出现在书库列表）
            dirnames[:] = [d for d in dirnames
                           if d != '薇阅回收站']
            for fn in filenames:
                ext = os.path.splitext(fn)[1].lower()
                if ext not in exts:
                    continue
                p = os.path.join(dirpath, fn)
                title, author = self._book_info(p)
                books.append((p, title, author, ext.lstrip('.').upper()))
        books.sort(key=lambda x: (x[1].lower() or x[0].lower()))
        return books

    def _trash_dir(self):
        """本地书库回收站目录（书库根目录下的「薇阅回收站」）。"""
        d = self._lib_last_dir or ''
        if not d:
            return ''
        return os.path.join(d, '薇阅回收站')

    def _open_trash(self):
        """回收站窗口：查看、还原、彻底删除被删的书。"""
        trash = self._trash_dir()
        if not trash:
            messagebox.showinfo(self.T('trash_title'),
                                self.T('trash_need_lib'))
            return
        try:
            os.makedirs(trash, exist_ok=True)
        except Exception:
            pass

        win = tk.Toplevel(self.root)
        win.title(self.T('trash_title'))
        win.geometry('560x420')
        win.configure(bg=COL_BG)
        win.minsize(460, 300)
        win.transient(self.root)

        tk.Label(win, text=self.T('trash'), bg=COL_BG, fg=COL_GRAY,
                 font=_f(10)).pack(anchor='w', padx=18, pady=(14, 6))

        box = tk.Frame(win, bg=COL_BG)
        box.pack(fill=tk.BOTH, expand=True, padx=18)
        tree = ttk.Treeview(box, columns=('name', 'size'), show='headings',
                            style='Min.Treeview')
        tree.heading('name', text=self.T('lib_col_title'))
        tree.heading('size', text='大小')
        tree.column('name', width=380, anchor='w')
        tree.column('size', width=100, anchor='e')
        sb = ttk.Scrollbar(box, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._trash_win = win
        self._trash_tree = tree
        self._trash_dir_path = trash

        def refresh():
            tree.delete(*tree.get_children())
            try:
                items = []
                for fn in sorted(os.listdir(trash)):
                    fp = os.path.join(trash, fn)
                    if not os.path.isfile(fp):
                        continue
                    try:
                        size = os.path.getsize(fp)
                    except Exception:
                        size = 0
                    items.append((fn, size))
                for fn, size in items:
                    tree.insert('', 'end', values=(fn, '%.0f KB' % (size / 1024.0)))
                if not items:
                    tree.insert('', 'end', values=(self.T('trash_empty'), ''))
            except Exception as e:
                tree.insert('', 'end', values=(self.T('trash_fail') + str(e), ''))

        def restore():
            sel = tree.selection()
            if not sel:
                return
            fn = tree.item(sel[0], 'values')[0]
            if fn == self.T('trash_empty'):
                return
            src = os.path.join(trash, fn)
            dst = os.path.join(self._lib_last_dir, fn)
            try:
                n = 1
                root_n, ext_n = os.path.splitext(fn)
                while os.path.exists(dst):
                    dst = os.path.join(self._lib_last_dir,
                                       '%s_%d%s' % (root_n, n, ext_n))
                    n += 1
                os.rename(src, dst)
                self.state_lbl.config(
                    text=self.T('trash_restore_ok', os.path.basename(dst)),
                    fg=COL_BLUE)
            except Exception as e:
                messagebox.showerror(self.T('trash_title'),
                                     self.T('trash_fail') + str(e), parent=win)
                return
            refresh()
            if self._lib_win is not None and self._lib_win.winfo_exists():
                try:
                    self._lib_scan(self._lib_last_dir or '')
                except Exception:
                    pass

        def delete_forever():
            sel = tree.selection()
            if not sel:
                return
            fn = tree.item(sel[0], 'values')[0]
            if fn == self.T('trash_empty'):
                return
            if not messagebox.askyesno(
                    self.T('trash_title'),
                    self.T('trash_del_confirm', fn), parent=win):
                return
            try:
                os.remove(os.path.join(trash, fn))
                self.state_lbl.config(
                    text=self.T('trash_del_ok', fn), fg=COL_BLUE)
            except Exception as e:
                messagebox.showerror(self.T('trash_title'),
                                     self.T('trash_fail') + str(e), parent=win)
                return
            refresh()

        btns = tk.Frame(win, bg=COL_BG)
        btns.pack(fill=tk.X, padx=18, pady=(10, 14))
        b_restore = self._flat_btn(btns, self.T('trash_restore'), COL_PANEL2,
                                   COL_BLACK, restore, padx=14, pady=6,
                                   font_size=10)
        b_restore.pack(side=tk.LEFT)
        b_del = self._flat_btn(btns, self.T('trash_delete'), COL_PANEL,
                               COL_BLACK, delete_forever, padx=14, pady=6,
                               font_size=10)
        b_del.pack(side=tk.LEFT, padx=(8, 0))
        b_close = self._flat_btn(btns, self.T('trash_close'), COL_PANEL,
                                 COL_BLACK, win.destroy, padx=14, pady=6,
                                 font_size=10)
        b_close.pack(side=tk.RIGHT)

        refresh()

    def _book_info(self, path):
        """优先读 Calibre 书库同目录的 metadata.opf 拿到书名作者。"""
        opf = os.path.join(os.path.dirname(path), 'metadata.opf')
        if os.path.isfile(opf):
            try:
                with open(opf, 'r', encoding='utf-8',
                          errors='ignore') as f:
                    s = f.read()
                m = re.search(r'<dc:title[^>]*>(.*?)</dc:title>', s, re.S)
                title = re.sub(r'<[^>]+>', '',
                               m.group(1)).strip() if m else ''
                m = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>',
                              s, re.S)
                author = re.sub(r'<[^>]+>', '',
                                m.group(1)).strip() if m else ''
                if title:
                    return title, author
            except Exception:
                pass
        base = os.path.splitext(os.path.basename(path))[0]
        base = re.sub(r'\s*\(\d+\)\s*$', '', base).strip()
        return base, ''

    def _lib_show(self, books):
        if self._lib_win is None:
            return
        self._lib_books = books
        tree = self._lib_tree
        tree.delete(*tree.get_children())
        for i, (p, title, author, fmt) in enumerate(books):
            tree.insert('', 'end', iid=str(i),
                        values=(title, author, fmt))
        if not books:
            self._lib_cnt.config(text=self.T('lib_empty'), fg=COL_GRAY)
        else:
            self._lib_cnt.config(text=self.T('lib_count', len(books)),
                                 fg=COL_BLUE)
        self._lib_btn_open.config(state='disabled')

    def _load_book_from_library(self, path):
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
        try:
            self._lib_win.destroy()
        except Exception:
            pass
        self._lib_win = None

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

    # ---------- 文本翻译 ----------
    def open_translate(self):
        if self._tr_win is not None and self._tr_win.winfo_exists():
            self._tr_win.lift()
            return
        win = tk.Toplevel(self.root)
        win.title(self.T('translate_title'))
        win.geometry('680x560')
        win.configure(bg=COL_BG)
        win.minsize(560, 420)
        win.transient(self.root)

        tk.Label(win, text=self.T('src_label'), bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(anchor='w', padx=18, pady=(16, 4))
        src = tk.Text(win, wrap=tk.WORD, font=(FONT, 12), height=7,
                      bg=COL_PANEL, fg=COL_BLACK, relief='sunken', bd=1,
                      padx=10, pady=8, insertbackground=COL_BLACK,
                      selectbackground=COL_HL, selectforeground=COL_BLACK,
                      highlightbackground=COL_LINE, highlightthickness=2)
        src.pack(fill=tk.X, padx=18)
        self._bind_text_menu(src)

        btn_row = tk.Frame(win, bg=COL_BG)
        btn_row.pack(fill=tk.X, padx=18, pady=8)
        btn_go = self._flat_btn(btn_row, self.T('translate_btn'), COL_PANEL,
                                COL_BLACK, None, padx=16, pady=6, font_size=11)
        btn_go.pack(side=tk.LEFT)
        btn_speak = self._flat_btn(btn_row, self.T('speak_result'), COL_PANEL,
                                   COL_BLACK, None, padx=14, pady=6,
                                   font_size=11)
        btn_speak.pack(side=tk.LEFT, padx=8)
        btn_pause = self._flat_btn(btn_row, self.T('pause'), COL_PANEL,
                                   COL_BLACK, None, padx=14, pady=6,
                                   font_size=11)
        btn_pause.pack(side=tk.LEFT, padx=(0, 8))
        btn_stop = self._flat_btn(btn_row, self.T('stop'), COL_PANEL,
                                  COL_BLACK, None, padx=14, pady=6,
                                  font_size=11)
        btn_stop.pack(side=tk.LEFT)
        tr_state = tk.Label(btn_row, text='', bg=COL_BG, fg=COL_GRAY,
                            font=_f(10))
        tr_state.pack(side=tk.LEFT, padx=12)

        tk.Label(win, text=self.T('dst_label'), bg=COL_BG, fg=COL_BLACK,
                 font=_f(11, True)).pack(anchor='w', padx=18, pady=(6, 4))
        dst = tk.Text(win, wrap=tk.WORD, font=(FONT, 12), height=9,
                      bg=COL_PANEL2, fg=COL_BLACK, relief='sunken', bd=1,
                      padx=10, pady=8, insertbackground=COL_BLACK,
                      selectbackground=COL_HL, selectforeground=COL_BLACK,
                      highlightbackground=COL_LINE, highlightthickness=2)
        dst.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))
        self._bind_text_menu(dst)

        self._tr_win = win
        self._tr_src = src
        self._tr_dst = dst
        self._tr_state = tr_state
        self._tr_btn_go = btn_go
        self._tr_btn_pause = btn_pause
        self._tr_btn_stop = btn_stop
        btn_go.config(command=self._do_translate)
        btn_speak.config(command=self._speak_translation)
        btn_pause.config(command=self._tr_toggle_pause, state='disabled')
        btn_stop.config(command=self._tr_stop_speak, state='disabled')

        def _close_tr():
            if self.speaker is not None:
                try:
                    self.speaker.stop()
                except Exception:
                    pass
            win.destroy()
            self._tr_win = None
        win.protocol('WM_DELETE_WINDOW', _close_tr)

    def _do_translate(self):
        text = self._tr_src.get('1.0', 'end').strip()
        if not text:
            messagebox.showinfo(self.T('dlg_tip'), self.T('input_first'),
                                parent=self._tr_win)
            return
        self._tr_state.config(text=self.T('translating'), fg=COL_GRAY)
        self._tr_btn_go.config(state='disabled')

        def work():
            try:
                out = translate(text)
                err = None
            except Exception as e:
                out, err = None, e
            self.root.after(0, lambda: self._tr_done(out, err))
        threading.Thread(target=work, daemon=True).start()

    def _tr_done(self, out, err):
        try:
            self._tr_btn_go.config(state='normal')
        except Exception:
            pass
        if err is not None:
            self._tr_state.config(text=self.T('translate_fail') + str(err),
                                  fg=COL_RED)
            return
        self._tr_dst.delete('1.0', 'end')
        self._tr_dst.insert('1.0', out or '')
        self._tr_state.config(text=self.T('translate_done'), fg=COL_BLUE)

    def _speak_translation(self):
        txt = self._tr_dst.get('1.0', 'end').strip()
        if not txt:
            return
        sp = self._get_speaker()
        if not sp:
            return
        chunks = split_chunks(clean_for_speech(txt))
        self._tr_btn_pause.config(text=self.T('pause'), state='normal')
        self._tr_btn_stop.config(state='normal')
        self._tr_state.config(text=self.T('speaking'), fg=COL_GRAY)
        sp.speak(chunks, on_progress=None, on_state=self._tr_on_speak_state)

    def _tr_on_speak_state(self, text):
        def _apply():
            try:
                if any(k in text for k in ('完成', '停止', 'done', 'stopped',
                                           'finished', 'finish')):
                    self._tr_btn_pause.config(text=self.T('pause'),
                                              state='disabled')
                    self._tr_btn_stop.config(state='disabled')
                self._tr_state.config(text=text, fg=COL_BLACK)
            except Exception:
                pass
        self.root.after(0, _apply)

    def _tr_toggle_pause(self):
        sp = self._get_speaker()
        if not sp:
            return
        st = sp.toggle_pause_resume()
        if st == 'pause':
            self._tr_btn_pause.config(text=self.T('resume'))
            self._tr_state.config(text=self.T('paused_msg'), fg=COL_GRAY)
        else:
            self._tr_btn_pause.config(text=self.T('pause'))
            self._tr_state.config(text=self.T('resuming'), fg=COL_RED)

    def _tr_stop_speak(self):
        sp = self._get_speaker()
        if sp:
            sp.stop()
        try:
            self._tr_btn_pause.config(text=self.T('pause'), state='disabled')
            self._tr_btn_stop.config(state='disabled')
        except Exception:
            pass
        self._tr_state.config(text=self.T('stopped'), fg=COL_GRAY)

    # ---------- 录音跟读 ----------
    def open_follow(self):
        from follow import FollowReader  # 用到才加载录音库，加快启动
        if self._follow_win is not None and self._follow_win.winfo_exists():
            self._follow_win.lift()
            return
        chunks = split_chunks(clean_for_speech(self.full_text)) \
            if self.full_text else []
        win = tk.Toplevel(self.root)
        win.title(self.T('follow_title'))
        win.geometry('760x520')
        win.configure(bg=COL_BG)
        win.minsize(640, 430)
        win.transient(self.root)

        tk.Label(win, text=self.T('follow_hint'), bg=COL_BG, fg=COL_GRAY,
                 font=_f(10)).pack(anchor='w', padx=20, pady=(14, 6))
        sent_lbl = tk.Label(win, text='', bg=COL_PANEL, fg=COL_BLACK,
                            font=(FONT, 14), wraplength=680, justify='left',
                            padx=16, pady=16, relief='sunken', bd=1,
                            highlightbackground=COL_LINE,
                            highlightthickness=2)
        sent_lbl.pack(fill=tk.X, padx=20)

        ctrl = tk.Frame(win, bg=COL_BG)
        ctrl.pack(fill=tk.X, padx=20, pady=(12, 4))
        btn_prev = self._flat_btn(ctrl, self.T('prev_sentence'), COL_PANEL,
                                  COL_BLACK, None, padx=12, pady=6,
                                  font_size=10)
        btn_prev.pack(side=tk.LEFT)
        btn_play = self._flat_btn(ctrl, self.T('play_original'), COL_PANEL2,
                                  COL_BLACK, None, padx=12, pady=6,
                                  font_size=10)
        btn_play.pack(side=tk.LEFT, padx=6)
        btn_pause = self._flat_btn(ctrl, self.T('pause'), COL_PANEL,
                                   COL_BLACK, None, padx=12, pady=6,
                                   font_size=10)
        btn_pause.pack(side=tk.LEFT, padx=6)
        btn_stop = self._flat_btn(ctrl, self.T('stop'), COL_PANEL,
                                  COL_BLACK, None, padx=12, pady=6,
                                  font_size=10)
        btn_stop.pack(side=tk.LEFT, padx=6)
        btn_next = self._flat_btn(ctrl, self.T('next_sentence'), COL_PANEL,
                                  COL_BLACK, None, padx=12, pady=6,
                                  font_size=10)
        btn_next.pack(side=tk.LEFT, padx=6)

        rep = tk.Frame(win, bg=COL_BG)
        rep.pack(fill=tk.X, padx=20, pady=4)
        tk.Label(rep, text=self.T('follow_repeat'), bg=COL_BG, fg=COL_GRAY,
                 font=_f(10)).pack(side=tk.LEFT)
        rep_combo = ttk.Combobox(rep, state="readonly", width=5, font=_f(10),
                                 style="Min.TCombobox")
        rep_combo['values'] = [self.T('repeat_1'), self.T('repeat_3'),
                               self.T('repeat_5'), self.T('repeat_loop')]
        rep_combo.current(1)
        rep_combo.pack(side=tk.LEFT, padx=(6, 14))
        tk.Label(rep, text=self.T('follow_gap'), bg=COL_BG, fg=COL_GRAY,
                 font=_f(10)).pack(side=tk.LEFT)
        gap_combo = ttk.Combobox(rep, state="readonly", width=5, font=_f(10),
                                 style="Min.TCombobox")
        gap_combo['values'] = [self.T('gap_05'), self.T('gap_1'),
                               self.T('gap_2')]
        gap_combo.current(1)
        gap_combo.pack(side=tk.LEFT, padx=(6, 14))
        dur_lbl = tk.Label(rep, text='', bg=COL_BG, fg=COL_BLACK,
                           font=_f(10, True))
        dur_lbl.pack(side=tk.LEFT)

        rec_row = tk.Frame(win, bg=COL_BG)
        rec_row.pack(fill=tk.X, padx=20, pady=4)
        btn_rec = self._flat_btn(rec_row, self.T('record_btn'), COL_PANEL2,
                                 COL_BLACK, None, padx=12, pady=6,
                                 font_size=10)
        btn_rec.pack(side=tk.LEFT)
        btn_replay = self._flat_btn(rec_row, self.T('replay'), COL_PANEL,
                                    COL_BLACK, None, padx=12, pady=6,
                                    font_size=10)
        btn_replay.pack(side=tk.LEFT, padx=6)
        rec_lbl = tk.Label(rec_row, text='', bg=COL_BG, fg=COL_RED,
                           font=_f(10, True))
        rec_lbl.pack(side=tk.LEFT, padx=(14, 0))

        status = tk.Label(win, text='', bg=COL_BG, fg=COL_GRAY, font=_f(10))
        status.pack(anchor='w', padx=20, pady=(6, 14))

        vid = 'zh-CN-XiaoxiaoNeural'
        try:
            if self.speaker is not None:
                vid = self.speaker.current_voice_id()
        except Exception:
            pass
        try:
            rate = self._speed_mult
        except Exception:
            rate = 1.0
        st = {'idx': 0, 'chunks': chunks,
              'reader': FollowReader(voice_id=vid),
              'playing': False, 'paused': False,
              'left': 0, 'total': 1, 'gap_ms': 1000,
              'repeat_job': None, 'rec_job': None,
              'rec_on': False, 'auto_stop': False}

        def show():
            if not st['chunks']:
                sent_lbl.config(text=self.T('no_sentences'))
                return
            sent_lbl.config(
                text='[%d/%d]  %s' % (st['idx'] + 1, len(st['chunks']),
                                      st['chunks'][st['idx']]))

        def set_status(text='', color=COL_GRAY):
            status.config(text=text, fg=color)

        def repeat_count():
            i = rep_combo.current()
            return (1, 3, 5, 0)[i if 0 <= i < 4 else 1]

        def gap_ms():
            i = gap_combo.current()
            return (500, 1000, 2000)[i if 0 <= i < 3 else 1]

        def cancel_repeat_job():
            if st['repeat_job']:
                try:
                    win.after_cancel(st['repeat_job'])
                except Exception:
                    pass
                st['repeat_job'] = None

        def stop_playback(msg=None):
            cancel_repeat_job()
            try:
                st['reader'].stop()
            except Exception:
                pass
            st['playing'] = False
            st['paused'] = False
            btn_pause.config(text=self.T('pause'))
            set_status(msg if msg is not None else self.T('stopped'),
                       COL_GRAY)

        def _on_play_done():
            if not st['playing']:
                return
            if st['total'] == 0:  # 循环
                st['repeat_job'] = win.after(st['gap_ms'], play_current)
                return
            st['left'] -= 1
            if st['left'] > 0:
                st['repeat_job'] = win.after(st['gap_ms'], play_current)
                set_status(
                    self.T('follow_repeating', st['idx'] + 1,
                           st['total'] - st['left'] + 1, st['total']),
                    COL_BLACK)
            else:
                st['playing'] = False
                set_status(self.T('follow_done', st['idx'] + 1), COL_BLUE)

        def play_current():
            if not st['chunks'] or st['playing']:
                return
            try:
                if self.speaker is not None:
                    self.speaker.stop()
            except Exception:
                pass
            stop_playback()
            i = st['idx']
            r = repeat_count()
            st['playing'] = True
            st['paused'] = False
            st['total'] = r
            st['left'] = r
            st['gap_ms'] = gap_ms()
            btn_pause.config(text=self.T('pause'))
            dur_lbl.config(text='')

            def on_duration(secs):
                self.root.after(0, lambda: dur_lbl.config(
                    text=self.T('orig_secs', '%.1f' % secs)))

            def on_done():
                self.root.after(0, _on_play_done)

            try:
                st['reader'].play_sentence(
                    self._apply_pron_dict(st['chunks'][i]), rate=rate,
                    on_duration=on_duration, on_done=on_done)
            except Exception:
                st['playing'] = False
                set_status(self.T('follow_play_fail'), COL_RED)
                return
            if r == 0:
                set_status(self.T('follow_looping', st['idx'] + 1),
                           COL_BLACK)
            else:
                set_status(self.T('follow_repeating',
                                  st['idx'] + 1, 1, r), COL_BLACK)

        def prev():
            if not chunks:
                return
            stop_playback()
            st['idx'] = (st['idx'] - 1) % len(chunks)
            show()
            play_current()

        def nxt():
            if not chunks:
                return
            stop_playback()
            st['idx'] = (st['idx'] + 1) % len(chunks)
            show()
            play_current()

        def toggle_pause():
            if not st['playing']:
                set_status(self.T('not_started'))
                return
            if st['paused']:
                try:
                    st['reader'].resume()
                except Exception:
                    pass
                st['paused'] = False
                btn_pause.config(text=self.T('pause'))
                set_status(self.T('resuming'), COL_BLACK)
            else:
                try:
                    st['reader'].pause()
                except Exception:
                    pass
                st['paused'] = True
                btn_pause.config(text=self.T('resume'))
                set_status(self.T('paused_msg'), COL_GRAY)

        def _tick_rec():
            if not st['rec_on']:
                return
            try:
                secs = st['reader'].recording_seconds()
            except Exception:
                secs = 0.0
            rec_lbl.config(text=self.T('rec_live', '%.1f' % secs))
            if secs >= FollowReader.MAX_REC_SEC - 0.01:
                st['auto_stop'] = True
                _finish_rec()
                return
            st['rec_job'] = win.after(200, _tick_rec)

        def _finish_rec():
            st['rec_on'] = False
            if st['rec_job']:
                try:
                    win.after_cancel(st['rec_job'])
                except Exception:
                    pass
                st['rec_job'] = None
            btn_rec.config(text=self.T('record_btn'))
            try:
                res = st['reader'].stop_recording()
            except Exception:
                res = None
            last = st['reader'].last_recording()
            if res:
                _path, secs = res
            elif last:
                secs = st['reader']._wav_duration(last)
            else:
                set_status(self.T('recording_fail'), COL_RED)
                return
            rec_lbl.config(text=self.T('rec_done', '%.1f' % secs))
            if st['auto_stop']:
                set_status(self.T('rec_max'), COL_RED)
            else:
                set_status(self.T('recorded'), COL_BLUE)
            st['auto_stop'] = False

        def rec():
            if not chunks:
                return
            if st['playing']:
                set_status(self.T('not_started'))
                return
            if st['rec_on']:
                _finish_rec()
                return
            try:
                ok = st['reader'].start_recording()
            except Exception:
                ok = False
            if not ok:
                set_status(self.T('recording_fail'), COL_RED)
                return
            st['rec_on'] = True
            st['auto_stop'] = False
            btn_rec.config(text='■ ' + self.T('stop'))
            set_status(self.T('recording'), COL_RED)
            _tick_rec()

        def replay():
            if not st['reader'].last_recording():
                set_status(self.T('no_recording'))
                return
            if st['playing']:
                set_status(self.T('not_started'))
                return
            set_status(self.T('replaying'), COL_GRAY)

            def work():
                try:
                    st['reader'].play_recording()
                except Exception:
                    pass
                self.root.after(
                    0, lambda: set_status(self.T('replay_done'), COL_BLUE))
            threading.Thread(target=work, daemon=True).start()

        btn_prev.config(command=prev)
        btn_play.config(command=play_current)
        btn_pause.config(command=toggle_pause)
        btn_stop.config(command=lambda: stop_playback())
        btn_next.config(command=nxt)
        btn_rec.config(command=rec)
        btn_replay.config(command=replay)

        def on_close():
            stop_playback()
            try:
                st['reader'].cleanup()
            except Exception:
                pass
            win.destroy()
            self._follow_win = None

        win.protocol('WM_DELETE_WINDOW', on_close)
        self._follow_win = win
        show()
    # ---------- 图片识别（OCR） ----------
    def scan_image(self):
        from ocr import ocr_image  # 用到才加载 OCR 组件
        path = filedialog.askopenfilename(
            title=self.T('ocr_title'),
            filetypes=[('Image', '*.png *.jpg *.jpeg *.bmp *.webp'),
                       (self.T('ft_all'), '*.*')])
        if not path:
            return
        self.state_lbl.config(text=self.T('ocr_working'), fg=COL_BLACK)

        def work():
            try:
                text = ocr_image(path)
                err = None
            except Exception as e:
                text, err = None, e
            self.root.after(0, lambda: self._finish_ocr(path, text, err))
        threading.Thread(target=work, daemon=True).start()

    def _finish_ocr(self, path, text, err):
        if err is not None:
            self.state_lbl.config(text=self.T('ready'), fg=COL_GRAY)
            messagebox.showerror(self.T('dlg_err'),
                                 self.T('ocr_fail') + str(err))
            return
        text = (text or '').strip()
        if not text:
            self.state_lbl.config(text=self.T('ready'), fg=COL_GRAY)
            messagebox.showinfo(self.T('dlg_tip'), self.T('ocr_empty'))
            return
        self.current_path = None
        self.full_text = text
        self.state_lbl.config(text=self.T('ocr_working'), fg=COL_BLACK)
        self.root.update_idletasks()
        self._load_text(text)
        self.file_lbl.config(text=os.path.basename(path), fg=COL_BLACK)
        self.state_lbl.config(text=self.T('ocr_done'), fg=COL_BLUE)
        self._start_reading(text, base=0, label='read_all')

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
        speak_chunks = [self._apply_pron_dict(c) for c in chunks]
        sp.speak(speak_chunks, on_progress=self._on_progress,
                 on_state=self._on_state)

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
            if total and i >= total:
                # 全部读完：清掉续读记录
                self._clear_resume()
            else:
                self._save_resume()
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
        self._save_resume(force=True)

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
            ok, out, msg = sp.export(
                self._apply_pron_dict(clean_for_speech(self.full_text)), path)
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
