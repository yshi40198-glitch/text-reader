# -*- coding: utf-8 -*-
"""便携版自检脚本：验证所有依赖能否正常导入（在 Windows 上双击 自检.bat 运行）"""
import sys, threading
print("Python 版本:", sys.version.split()[0])

ok = True
def chk(name):
    global ok
    try:
        __import__(name)
        print("  [OK]", name)
    except Exception as e:
        ok = False
        print("  [FAIL]", name, ":", e)

print("== 核心依赖 ==")
chk("tkinter")
chk("comtypes")
chk("pymupdf")
chk("docx")
chk("lxml")
chk("edge_tts")

print("== 程序模块 ==")
try:
    import extract
    print("  [OK] extract")
except Exception as e:
    ok = False; print("  [FAIL] extract:", e)
try:
    import speaker
    print("  [OK] speaker")
except Exception as e:
    ok = False; print("  [FAIL] speaker:", e)

print()
if ok:
    print("总体: 全部通过 OK")
else:
    print("总体: 有失败，请把上面报错发给我")
print("（自检完成，可关闭本窗口）")
