# GitHub Actions 自动打包 APK 指南

## 方法一：使用 GitHub Actions（推荐 - 最简单）

### 步骤 1：创建 GitHub 仓库

1. 打开 https://github.com/new
2. 仓库名称：`QRScanner-Android`
3. 选择 "Public" 或 "Private"
4. 点击 "Create repository"

### 步骤 2：上传代码到 GitHub

在本地项目目录执行：

```powershell
# 进入项目目录
cd "C:\Users\25362\Desktop\编程实用项目总\二维码系列"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit - QR Scanner Android App"

# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/QRScanner-Android.git

# 推送到GitHub
git push -u origin main
```

### 步骤 3：触发自动构建

1. 打开你的GitHub仓库页面
2. 点击 "Actions" 标签
3. 你会看到 "Build Android APK" 工作流
4. 点击 "Run workflow" 手动触发构建

### 步骤 4：下载APK

1. 等待构建完成（约15-30分钟）
2. 点击 "Actions" → 选择最新的工作流运行
3. 在 "Artifacts" 部分下载 "QRScanner-APK"
4. 解压下载的文件，得到 `.apk` 文件

---

## 方法二：使用 WSL2 本地打包

### 前提条件
- Windows 10/11 已安装 WSL2
- Ubuntu 已安装

### 打包步骤

```bash
# 1. 打开 WSL2 Ubuntu
wsl

# 2. 进入项目目录
cd /mnt/c/Users/25362/Desktop/编程实用项目总/二维码系列

# 3. 安装依赖
sudo apt update
sudo apt install -y python3-pip build-essential git zip unzip openjdk-17-jdk

# 4. 安装 buildozer
pip3 install --user buildozer cython

# 5. 开始打包
~/.local/bin/buildozer android debug

# 6. 等待打包完成（第一次可能需要30-60分钟）
# APK将生成在 ./bin/ 目录下
```

---

## 方法三：使用 Docker 打包

### 前提条件
- 已安装 Docker Desktop

### 打包步骤

```powershell
# 1. 进入项目目录
cd "C:\Users\25362\Desktop\编程实用项目总\二维码系列"

# 2. 使用 Docker 运行 buildozer
docker run --rm -v ${PWD}:/app kivy/buildozer android debug

# 3. APK将生成在 ./bin/ 目录下
```

---

## 安装APK到手机

### 方法 1：直接传输安装
1. 将APK文件发送到手机（微信、QQ、邮件等）
2. 在手机上点击APK文件
3. 允许安装未知来源应用
4. 完成安装

### 方法 2：使用ADB安装
```powershell
# 连接手机，开启USB调试
adb install bin/qrscanner-2.1.0-arm64-v8a_armeabi-v7a-debug.apk
```

---

## 常见问题

### Q: 构建失败怎么办？
A: 检查GitHub Actions日志，常见原因：
- 依赖项版本冲突
- 网络问题导致下载失败
- 代码语法错误

### Q: APK安装失败？
A: 确保：
- 允许安装未知来源应用
- 手机Android版本 >= 5.0 (API 21)
- 有足够的存储空间

### Q: 摄像头无法使用？
A: 检查是否授予了摄像头权限：
- 设置 → 应用 → 二维码安全扫描器 → 权限 → 摄像头 → 允许

---

## 文件说明

- `buildozer.spec` - 打包配置文件
- `main.py` - Android入口文件
- `.github/workflows/build-apk.yml` - GitHub Actions工作流
- `二维码扫描器.py` - 主程序代码

## 技术支持

如有问题，请查看：
- Buildozer文档：https://buildozer.readthedocs.io/
- Kivy文档：https://kivy.org/doc/stable/
