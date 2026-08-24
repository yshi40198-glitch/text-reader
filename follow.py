# -*- coding: utf-8 -*-
"""录音跟读模块：逐句听原音 → 跟读录音 → 回放对比。"""
import asyncio
import ctypes
import os
import tempfile
import wave


class FollowReader:
    """跟读器：播放原句（AI 优先，失败回退本地 SAPI）+ 录音 + 回放。"""

    def __init__(self, voice_id='zh-CN-XiaoxiaoNeural'):
        self.voice_id = voice_id
        self._rec_path = None
        self._tmp = []

    # ---------- 播放原句 ----------
    def play_sentence(self, text, rate=1.0):
        """播放一句原文，阻塞到播完。AI 引擎失败自动回退本地语音。"""
        try:
            mp3 = tempfile.mktemp(suffix='.mp3')
            pct = int(round(max(-50, min(100, (rate - 1) * 100))))
            rate_str = '%+d%%' % pct

            async def _do():
                import edge_tts
                await edge_tts.Communicate(
                    text, voice=self.voice_id, rate=rate_str).save(mp3)
            asyncio.run(asyncio.wait_for(_do(), timeout=60))
            self._tmp.append(mp3)
            self._play_mp3(mp3)
            return 'ai'
        except Exception:
            self._play_sapi(text)
            return 'sapi'

    def _play_mp3(self, path):
        alias = 'follow'
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW(
            'open "%s" type mpegvideo alias %s' % (path, alias),
            None, 0, None)
        winmm.mciSendStringW('play %s wait' % alias, None, 0, None)
        winmm.mciSendStringW('close %s' % alias, None, 0, None)

    def _play_sapi(self, text):
        import comtypes.client
        import pythoncom
        pythoncom.CoInitialize()
        v = comtypes.client.CreateObject('SAPI.SpVoice')
        v.Speak(text, 0)
        pythoncom.CoUninitialize()

    # ---------- 录音 ----------
    def record(self, seconds=6, out_path=None):
        """录 seconds 秒，返回 wav 文件路径。"""
        import numpy as np
        import sounddevice as sd
        if out_path is None:
            out_path = tempfile.mktemp(suffix='.wav')
        sr = 16000
        data = sd.rec(int(seconds * sr), samplerate=sr, channels=1,
                      dtype='int16')
        sd.wait()
        self._save_wav(out_path, data, sr)
        self._rec_path = out_path
        return out_path

    def play_recording(self, path=None):
        """回放录音（同步）。"""
        import numpy as np
        import sounddevice as sd
        path = path or self._rec_path
        if not path or not os.path.exists(path):
            return False
        with wave.open(path, 'rb') as w:
            frames = w.readframes(w.getnframes())
            sr = w.getframerate()
        sd.play(np.frombuffer(frames, dtype=np.int16), sr)
        sd.wait()
        return True

    def last_recording(self):
        return self._rec_path

    def cleanup(self):
        for p in self._tmp:
            try:
                os.remove(p)
            except Exception:
                pass
        self._tmp = []

    @staticmethod
    def _save_wav(path, data, sr):
        with wave.open(path, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(data.tobytes())
