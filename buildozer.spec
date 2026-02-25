[app]
title = 二维码安全扫描器
package.name = qrscanner
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 2.1.0
requirements = python3,kivy,opencv-python,pyzbar,Pillow,numpy
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a
[buildozer]
log_level = 2
warn_on_root = 1
