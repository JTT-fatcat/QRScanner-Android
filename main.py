"""
二维码安全扫描器 - Android打包入口
"""
import os
import sys

# 设置Kivy环境变量
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_GL_BACKEND'] = 'sdl2'

# Android平台检测
def is_android():
    return 'ANDROID_ARGUMENT' in os.environ or hasattr(sys, 'getandroidapilevel')

# 导入主程序
from 二维码扫描器 import QRScannerApp

if __name__ == '__main__':
    QRScannerApp().run()
