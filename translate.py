# -*- coding: utf-8 -*-
"""文本翻译模块：免费在线翻译（MyMemory），中英互译，支持朗读译文。"""
import json
import re
import urllib.parse
import urllib.request


def _split_parts(text, limit=450):
    """把长文本按句切成不超过 limit 字符的段（免费接口单次有长度限制）。"""
    sents = re.split(r'(?<=[。！？；….!?])\s*', text)
    out, buf = [], ''
    for s in sents:
        s = s.strip()
        if not s:
            continue
        if len(s) > limit:
            if buf:
                out.append(buf)
                buf = ''
            while len(s) > limit:
                out.append(s[:limit])
                s = s[limit:]
            buf = s
        elif len(buf) + len(s) <= limit:
            buf += s
        else:
            out.append(buf)
            buf = s
    if buf:
        out.append(buf)
    return [p for p in out if p.strip()]


def detect_lang(text):
    """简单语言检测：含中文字符 → zh，否则 → en。"""
    if re.search(r'[\u4e00-\u9fff]', text or ''):
        return 'zh'
    return 'en'


def _lang_code(lang):
    return {'zh': 'zh-CN', 'en': 'en'}.get(lang, lang)


def translate(text, src=None, dst=None, timeout=15):
    """翻译文本，返回译文。失败抛异常。

    src/dst 取 'zh' / 'en'；不指定时自动检测源语言并翻成另一种。
    """
    text = (text or '').strip()
    if not text:
        return ''
    if src is None:
        src = detect_lang(text)
    if dst is None:
        dst = 'en' if src == 'zh' else 'zh'
    if src == dst:
        return text
    langpair = '%s|%s' % (_lang_code(src), _lang_code(dst))
    parts = _split_parts(text)
    outs = []
    for part in parts:
        outs.append(_translate_one(part, langpair, timeout))
    return '\n'.join(outs)


def _translate_one(part, langpair, timeout):
    """翻译单段；失败自动重试一次。"""
    last = None
    for attempt in range(2):
        try:
            q = urllib.parse.quote(part)
            url = ('https://api.mymemory.translated.net/get?q=%s&langpair=%s'
                   % (q, langpair))
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = json.loads(r.read().decode('utf-8', 'ignore'))
            out = (data.get('responseData') or {}).get('translatedText') or ''
            if out.strip():
                return out.strip()
            last = RuntimeError('翻译服务返回异常')
        except Exception as e:
            last = e
        if attempt == 0:
            import time
            time.sleep(1.0)
    raise RuntimeError('翻译服务连接失败：%s' % last)
