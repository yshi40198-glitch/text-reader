# -*- coding: utf-8 -*-
"""AI 神经网络语音专项测试：验证 edge-tts 组件 + 网络是否可达。
通过 = AI 网络语音可用；失败 = 会自动改用本地语音，或检查网络后重试。
"""
import asyncio
import os
import sys
import tempfile


def main():
    print("== AI 神经网络语音测试 ==")
    try:
        import edge_tts
        print("  [OK] edge-tts 组件版本", edge_tts.__version__)
    except Exception as e:
        print("  [FAIL] AI 语音组件缺失:", e)
        return 1
    out = os.path.join(tempfile.gettempdir(), 'ai_voice_test.mp3')
    try:
        asyncio.run(edge_tts.Communicate(
            "你好，这是 AI 神经网络语音测试。", voice='zh-CN-XiaoxiaoNeural').save(out))
        size = os.path.getsize(out) if os.path.exists(out) else 0
        if size > 1000:
            print("  [OK] 已联网生成测试音频，", size, "字节")
            try:
                os.remove(out)
            except Exception:
                pass
            print("全部通过 —— AI 网络语音可用，可以朗读了")
            return 0
        print("  [FAIL] 生成的音频太小")
        return 1
    except Exception as e:
        print("  [FAIL] 联网生成失败:", repr(e))
        print("提示：AI 语音需要联网。断网时软件会自动改用本地语音。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
