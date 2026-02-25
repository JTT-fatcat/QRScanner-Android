# 二维码安全扫描器 - APK打包说明

## 方法一：使用WSL2 (推荐)

### 1. 安装WSL2和Ubuntu
```powershell
# 在PowerShell中运行
wsl --install -d Ubuntu
```

### 2. 在Ubuntu中安装依赖
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install -y python3 python3-pip python3-venv git zip unzip

# 安装buildozer依赖
sudo apt install -y libltdl-dev libffi-dev libssl-dev autoconf autotools-dev build-essential

# 安装Java JDK
sudo apt install -y openjdk-17-jdk

# 安装Android SDK依赖
sudo apt install -y libncurses5-dev libncursesw5-dev libtinfo5 cmake
```

### 3. 安装buildozer
```bash
pip3 install --user buildozer cython
```

### 4. 进入项目目录并打包
```bash
# 进入项目目录（假设在Windows D盘）
cd /mnt/d/编程实用项目总/二维码系列

# 初始化buildozer（如果还没有buildozer.spec）
# buildozer init

# 调试模式打包
buildozer android debug

# 或者发布模式打包
# buildozer android release
```

### 5. 输出位置
打包完成后，APK文件位于：
```
./bin/qrscanner-2.1.0-arm64-v8a_armeabi-v7a-debug.apk
```

---

## 方法二：使用Docker

### 1. 安装Docker Desktop
下载并安装：https://www.docker.com/products/docker-desktop

### 2. 创建Dockerfile
```dockerfile
FROM kivy/buildozer:latest

USER root
WORKDIR /app

# 复制项目文件
COPY . /app/

# 运行buildozer
CMD ["buildozer", "android", "debug"]
```

### 3. 构建镜像并运行
```powershell
# 在PowerShell中
docker build -t qrscanner-build .
docker run -v ${PWD}:/app qrscanner-build
```

---

## 方法三：使用GitHub Actions自动打包

### 1. 创建 `.github/workflows/build-apk.yml`
```yaml
name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y python3-pip build-essential git
        sudo apt install -y libffi-dev libssl-dev autoconf automake libtool
        pip3 install --user buildozer cython
    
    - name: Build APK
      run: |
        ~/.local/bin/buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: qrscanner-apk
        path: bin/*.apk
```

### 2. 推送到GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

然后在GitHub Actions中查看构建进度，下载APK。

---

## 常见问题

### 1. 摄像头权限问题
确保 `buildozer.spec` 中包含：
```
android.permissions = CAMERA,INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
```

### 2. OpenCV在Android上的问题
可能需要添加：
```
requirements = python3,kivy,opencv-python,pyzbar,Pillow,numpy,android
```

### 3. 字体问题
Android上会自动使用系统字体，无需额外配置。

### 4. 打包失败清理缓存
```bash
buildozer android clean
buildozer android debug
```

---

## 安装APK到手机

1. 启用开发者模式：
   - 设置 → 关于手机 → 连续点击"版本号"7次

2. 启用USB调试：
   - 设置 → 开发者选项 → USB调试

3. 连接手机并安装：
```bash
adb install bin/qrscanner-2.1.0-arm64-v8a_armeabi-v7a-debug.apk
```

或者直接将APK文件发送到手机，点击安装。
