# -*- coding: utf-8 -*-
"""图片 OCR：调用 Windows 自带 OCR 引擎（Windows.Media.Ocr）识别图片文字。

先用 PIL 统一读图（支持 PNG/JPG/BMP/WEBP/TIFF 等），必要时缩放；
识别结果为空时放大再试一次（应对小字/模糊图片）。
"""
import asyncio
import os
import re
import tempfile


def _ocr_png(path, lang):
    """识别单张 PNG（winrt 引擎）。"""
    import winrt.windows.media.ocr as ocr
    import winrt.windows.globalization as globalization
    import winrt.windows.graphics.imaging as imaging
    import winrt.windows.storage as storage
    import winrt.windows.storage.streams as streams

    async def _do():
        file = await storage.StorageFile.get_file_from_path_async(path)
        stream = await file.open_async(storage.FileAccessMode.READ)
        decoder = await imaging.BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = None
        for tag in (lang, 'zh-Hans-CN', 'zh-CN', 'zh', 'en-US'):
            try:
                engine = ocr.OcrEngine.try_create_from_language(
                    globalization.Language(tag))
                if engine is not None:
                    break
            except Exception:
                continue
        if engine is None:
            engine = ocr.OcrEngine.try_create_from_user_profile_languages()
        if engine is None:
            raise RuntimeError('系统没有可用的 OCR 引擎，'
                               '请在 Windows 设置中安装 OCR 语言包')
        result = await engine.recognize_async(bitmap)
        text = result.text or ''
        # OCR 常在汉字之间插入空格，去掉汉字间的空格让文本连贯
        text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', text)
        return text

    return asyncio.run(_do())


def ocr_image(path, lang='zh-CN'):
    """识别图片中的文字，返回文本。自动缩放/放大重试，格式更兼容。"""
    from PIL import Image
    try:
        img = Image.open(path)
    except Exception:
        raise RuntimeError('无法读取该图片，请换用 PNG/JPG/BMP 格式')
    img = img.convert('RGB')

    def _run_once(image, scale):
        w, h = image.size
        if scale == 1:
            max_side = 2600
            if max(w, h) > max_side:
                s = max_side / float(max(w, h))
                image = image.resize((int(w * s), int(h * s)),
                                     Image.LANCZOS)
        else:
            image = image.resize((w * scale, h * scale), Image.LANCZOS)
        tmp = tempfile.mktemp(suffix='.png')
        try:
            image.save(tmp)
            return _ocr_png(tmp, lang)
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass

    text = _run_once(img, 1)
    if text and text.strip():
        return text.strip()
    # 原图没识别到：放大 1.6 倍再试（小字/模糊图）
    text = _run_once(img, 2)
    return text.strip() if text else ''

    return asyncio.run(_do())
