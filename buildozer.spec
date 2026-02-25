[app]
# 应用标题
title = 二维码安全扫描器

# 包名（使用反向域名格式）
package.name = qrscanner
package.domain = com.example

# 源文件目录
source.dir = .

# 主程序入口
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc,md
source.include_patterns = 二维码扫描器.py,main.py

# 版本号
version = 2.1.0

# 依赖项
requirements = python3==3.10.13,kivy==2.3.0,opencv-python,pyzbar,Pillow,numpy,urllib3,chardet,idna,certifi,requests

# Android权限
android.permissions = CAMERA,INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FLASHLIGHT

# Android API设置
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.gradle_dependencies = com.android.support:support-compat:28.0.0

# 应用图标（可选）
# android.icon = icon.png
# android.presplash_icon = icon.png

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# 日志设置
android.logcat_filters = *:S python:D

# 构建模式
android.debug_artifact = apk

# 架构支持
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
# 构建目录
build_dir = ./.buildozer

# 构建模式
build_mode = debug

# 日志级别
log_level = 2

# 警告设置
warn_on_root = 1
