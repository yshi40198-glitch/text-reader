# -*- coding: utf-8 -*-
"""录音跟读模块（复读机模式）：播放原句（AI 优先，可暂停/停止）、
手动录音（实时计时，3 分钟上限）、回放对比。"""
import ctypes
import os
import tempfile
import threading
import time
import wave


class FollowReader:
    """跟读器：播放原句（AI 优先，失败回退本地 SAPI）+ 手动录音 + 回放。"""

    MAX_REC_SEC = 180

    def __init__(self, voice_id='zh-CN-XiaoxiaoNeural'):
        self.voice_id = voice_id
        self._rec_path = None
        self._rec_frames = []
        self._rec_evt = None
        self._rec_stream = None
        self._rec_start = 0.0
        self._tmp = []
        self._mci_alias = None
        self._sapi = None
        self._stop_flag = False
        self._playing = False

    # ---------- 播放原句 ----------
    def play_sentence(self, text, rate=1.0, on_duration=None, on_done=None):
        """后台播放一句原文。on_duration(秒)/on_done() 由调用线程回调。"""
        def _run():
            self._playing = True
            self._stop_flag = False
            try:
                if not self._play_ai(text, rate, on_duration):
                    self._play_sapi(text)
            except Exception:
                pass
            self._playing = False
            if on_done:
                try:
                    on_done()
                except Exception:
                    pass
        threading.Thread(target=_run, daemon=True).start()

    def _play_ai(self, text, rate, on_duration):
        import asyncio
        import edge_tts
        mp3 = tempfile.mktemp(suffix='.mp3')
        pct = int(round(max(-50, min(100, (rate - 1) * 100))))
        rate_str = '%+d%%' % pct

        async def _do():
            await edge_tts.Communicate(
                text, voice=self.voice_id, rate=rate_str).save(mp3)
        asyncio.run(asyncio.wait_for(_do(), timeout=60))
        self._tmp.append(mp3)
        return self._play_mp3(mp3, on_duration)

    def _play_mp3(self, path, on_duration):
        alias = 'wyf%d' % int(time.time() * 1000)
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW(
            'open "%s" type mpegvideo alias %s' % (path, alias), None, 0, None)
        self._mci_alias = alias
        buf = ctypes.create_unicode_buffer(128)
        winmm.mciSendStringW('status %s length' % alias, buf, 128, None)
        try:
            dur = int(buf.value.strip()) / 1000.0
        except Exception:
            dur = 0.0
        if dur > 0 and on_duration:
            try:
                on_duration(dur)
            except Exception:
                pass
        winmm.mciSendStringW('play %s' % alias, None, 0, None)
        while not self._stop_flag:
            winmm.mciSendStringW('status %s mode' % alias, buf, 128, None)
            mode = buf.value.strip().lower()
            if mode == 'stopped':
                break
            time.sleep(0.05)
        try:
            winmm.mciSendStringW('stop %s' % alias, None, 0, None)
            winmm.mciSendStringW('close %s' % alias, None, 0, None)
        except Exception:
            pass
        if self._mci_alias == alias:
            self._mci_alias = None
        return True

    def _play_sapi(self, text):
        import comtypes.client
        import pythoncom
        pythoncom.CoInitialize()
        v = comtypes.client.CreateObject('SAPI.SpVoice')
        self._sapi = v
        try:
            v.Speak(text, 1)  # SVSFlagsAsync
            while not self._stop_flag:
                try:
                    st = int(v.Status.RunningState)
                except Exception:
                    break
                if st != 1:  # 1 = speaking
                    break
                time.sleep(0.05)
        except Exception:
            pass
        try:
            v.Speak('', 3)  # SPF_PURGE，清空未播内容
        except Exception:
            pass
        self._sapi = None
        pythoncom.CoUninitialize()

    # ---------- 播放控制 ----------
    def pause(self):
        if self._mci_alias:
            try:
                ctypes.windll.winmm.mciSendStringW(
                    'pause %s' % self._mci_alias, None, 0, None)
            except Exception:
                pass
        if self._sapi is not None:
            try:
                self._sapi.Pause()
            except Exception:
                pass

    def resume(self):
        if self._mci_alias:
            try:
                ctypes.windll.winmm.mciSendStringW(
                    'resume %s' % self._mci_alias, None, 0, None)
            except Exception:
                pass
        if self._sapi is not None:
            try:
                self._sapi.Resume()
            except Exception:
                pass

    def stop(self):
        self._stop_flag = True
        if self._mci_alias:
            try:
                ctypes.windll.winmm.mciSendStringW(
                    'stop %s' % self._mci_alias, None, 0, None)
            except Exception:
                pass
        if self._sapi is not None:
            try:
                self._sapi.Speak('', 3)
            except Exception:
                pass

    def is_playing(self):
        return self._playing

    # ---------- 录音（手动起止，实时计时，3 分钟上限） ----------
    def start_recording(self):
        import numpy as np
        import sounddevice as sd
        if self._rec_stream is not None:
            return False
        self._rec_frames = []
        self._rec_evt = threading.Event()
        self._rec_start = time.time()
        sr = 16000

        def cb(indata, frames, t, status):
            if self._rec_evt.is_set():
                return
            self._rec_frames.append(indata.copy())

        self._rec_stream = sd.InputStream(
            samplerate=sr, channels=1, dtype='int16', callback=cb)
        self._rec_stream.start()
        threading.Thread(target=self._rec_watch, daemon=True).start()
        return True

    def _rec_watch(self):
        while not self._rec_evt.wait(0.2):
            if time.time() - self._rec_start >= self.MAX_REC_SEC:
                self.stop_recording()
                break

    def recording_seconds(self):
        if self._rec_start <= 0:
            return 0.0
        return min(time.time() - self._rec_start, self.MAX_REC_SEC)

    def stop_recording(self):
        import numpy as np
        if self._rec_stream is None:
            return None
        if self._rec_evt:
            self._rec_evt.set()
        try:
            self._rec_stream.stop()
            self._rec_stream.close()
        except Exception:
            pass
        self._rec_stream = None
        if self._rec_frames:
            try:
                data = np.concatenate(self._rec_frames, axis=0).reshape(-1)
            except Exception:
                data = np.zeros(0, dtype=np.int16)
        else:
            data = np.zeros(0, dtype=np.int16)
        secs = len(data) / 16000.0
        out_path = tempfile.mktemp(suffix='.wav')
        self._save_wav(out_path, data, 16000)
        self._rec_path = out_path
        self._rec_frames = []
        self._rec_start = 0.0
        return out_path, secs

    # ---------- 回放 ----------
    def play_recording(self, path=None):
        import numpy as np
        import sounddevice as sd
        path = path or self._rec_path
        if not path or not os.path.exists(path):
            return None
        with wave.open(path, 'rb') as w:
            frames = w.readframes(w.getnframes())
            sr = w.getframerate()
        sd.play(np.frombuffer(frames, dtype=np.int16), sr)
        sd.wait()
        return self._wav_duration(path)

    @staticmethod
    def _wav_duration(path):
        try:
            with wave.open(path, 'rb') as w:
                return w.getnframes() / float(w.getframerate())
        except Exception:
            return 0.0

    def last_recording(self):
        return self._rec_path

    def cleanup(self):
        try:
            self.stop()
        except Exception:
            pass
        try:
            self.stop_recording()
        except Exception:
            pass
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
