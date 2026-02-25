# -*- coding: utf-8 -*-
"""
Android APK打包脚本
"""
import os
import sys
import subprocess
import shutil


def check_buildozer():
    """检查是否安装了buildozer"""
    try:
        subprocess.run(['buildozer', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_buildozer():
    """安装buildozer"""
    print("正在安装buildozer...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'buildozer'], check=True)
    print("buildozer安装完成")


def setup_android_sdk():
    """设置Android SDK环境"""
    print("""
Android SDK设置说明:
1. 下载Android SDK Command Line Tools
2. 设置环境变量 ANDROID_SDK_ROOT
3. 安装必要的组件:
   - platform-tools
   - platforms;android-33
   - build-tools;33.0.0
   - ndk;25.2.9519653
""")


def build_apk():
    """构建APK"""
    if not check_buildozer():
        install_buildozer()
    
    print("开始构建APK...")
    print("这可能需要较长时间，请耐心等待...")
    
    try:
        # 清理之前的构建
        if os.path.exists('.buildozer'):
            print("清理之前的构建...")
            shutil.rmtree('.buildozer')
        
        # 构建APK
        result = subprocess.run(
            ['buildozer', '-v', 'android', 'debug'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ APK构建成功!")
            print("APK文件位置: ./bin/qrscanner-1.0-armeabi-v7a_debug.apk")
        else:
            print("\n❌ APK构建失败")
            print("请检查错误信息并修复问题")
            
    except Exception as e:
        print(f"构建过程中出现错误: {e}")


def main():
    """主函数"""
    print("=" * 50)
    print("二维码扫描器 - Android APK打包工具")
    print("=" * 50)
    
    print("\n选择操作:")
    print("1. 构建APK")
    print("2. 设置Android SDK")
    print("3. 退出")
    
    choice = input("\n请输入选项 (1-3): ").strip()
    
    if choice == '1':
        build_apk()
    elif choice == '2':
        setup_android_sdk()
    elif choice == '3':
        print("退出")
    else:
        print("无效选项")


if __name__ == '__main__':
    main()
