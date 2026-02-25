# -*- coding: utf-8 -*-
"""
二维码扫描器 - 安全提取版 v2.1
功能：
1. 摄像头实时扫描二维码，在二维码上方显示内容（不自动跳转，防诈骗）
2. 上传图片扫描二维码（支持艺术二维码）
3. 智能链接安全检测（三档安全等级）
4. 文本内容安全检测（识别违规内容）
5. 现代化UI设计
6. 自动处理字体安装

使用方法：
直接运行此脚本，程序会自动：
1. 检查并安装字体（如果未安装）
2. 启动二维码扫描界面
"""
import os
import sys
import shutil
import re
import math
from urllib.parse import urlparse
from datetime import datetime

# ============================================================
# 第一部分：跨平台字体配置
# ============================================================

def get_platform():
    """获取当前平台"""
    import sys
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    elif hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in os.environ:
        return 'android'
    elif sys.platform.startswith('linux'):
        return 'linux'
    return 'unknown'


def setup_fonts():
    """
    跨平台字体配置
    - Windows: 尝试使用系统字体或打包字体
    - Android: 使用系统默认中文字体
    - 其他: 使用默认字体
    """
    current_platform = get_platform()
    print(f"[*] 当前平台: {current_platform}")
    
    font_config = {
        'font_name': 'Roboto',  # 默认字体
        'font_path': None,
        'chinese_supported': False
    }
    
    try:
        if current_platform == 'windows':
            # Windows: 尝试查找中文字体
            font_config = _setup_windows_fonts(font_config)
        elif current_platform == 'android':
            # Android: 使用系统字体
            font_config = _setup_android_fonts(font_config)
        elif current_platform == 'macos':
            # macOS: 使用系统字体
            font_config = _setup_macos_fonts(font_config)
        else:
            # Linux/其他: 尝试常见路径
            font_config = _setup_linux_fonts(font_config)
    except Exception as e:
        print(f"[!] 字体配置出错: {e}")
        print("[*] 使用默认字体")
    
    return font_config


def _setup_windows_fonts(config):
    """Windows字体配置"""
    # 尝试查找系统字体
    system_font_paths = [
        r"C:\Windows\Fonts",
        r"D:\QRScannerFonts",  # 打包字体目录
    ]
    
    target_fonts = [
        ('msyh.ttc', '微软雅黑'),
        ('msyhbd.ttc', '微软雅黑粗体'),
        ('simhei.ttf', '黑体'),
        ('simsun.ttc', '宋体'),
    ]
    
    for font_dir in system_font_paths:
        if not os.path.exists(font_dir):
            continue
        
        for font_file, font_name in target_fonts:
            font_path = os.path.join(font_dir, font_file)
            if os.path.exists(font_path):
                try:
                    LabelBase.register(name='ChineseFont', fn_regular=font_path)
                    config['font_name'] = 'ChineseFont'
                    config['font_path'] = font_path
                    config['chinese_supported'] = True
                    print(f"[✓] Windows字体: {font_name}")
                    return config
                except Exception as e:
                    print(f"[!] 注册字体失败: {e}")
                    continue
    
    print("[*] Windows: 未找到中文字体，使用默认")
    return config


def _setup_android_fonts(config):
    """Android字体配置 - 使用系统默认字体"""
    # Android常见中文字体路径
    android_font_paths = [
        '/system/fonts/NotoSansCJK-Regular.ttc',
        '/system/fonts/NotoSansSC-Regular.otf',
        '/system/fonts/DroidSansFallback.ttf',
        '/system/fonts/Roboto-Regular.ttf',
    ]
    
    for font_path in android_font_paths:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='AndroidChineseFont', fn_regular=font_path)
                config['font_name'] = 'AndroidChineseFont'
                config['font_path'] = font_path
                config['chinese_supported'] = True
                print(f"[✓] Android字体: {os.path.basename(font_path)}")
                return config
            except Exception as e:
                print(f"[!] Android字体注册失败: {e}")
                continue
    
    # 如果找不到中文字体，使用Roboto（Android默认支持中文）
    print("[*] Android: 使用系统默认字体")
    config['font_name'] = 'Roboto'
    config['chinese_supported'] = True  # Android Roboto通常支持中文
    return config


def _setup_macos_fonts(config):
    """macOS字体配置"""
    mac_fonts = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
    ]
    
    for font_path in mac_fonts:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='MacChineseFont', fn_regular=font_path)
                config['font_name'] = 'MacChineseFont'
                config['font_path'] = font_path
                config['chinese_supported'] = True
                print(f"[✓] macOS字体: {os.path.basename(font_path)}")
                return config
            except Exception as e:
                continue
    
    print("[*] macOS: 使用默认字体")
    return config


def _setup_linux_fonts(config):
    """Linux字体配置"""
    linux_fonts = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    for font_path in linux_fonts:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='LinuxChineseFont', fn_regular=font_path)
                config['font_name'] = 'LinuxChineseFont'
                config['font_path'] = font_path
                config['chinese_supported'] = True
                print(f"[✓] Linux字体: {os.path.basename(font_path)}")
                return config
            except Exception as e:
                continue
    
    print("[*] Linux: 使用默认字体")
    return config


# ============================================================
# 第二部分：内容安全检测系统
# ============================================================

class ContentSafetyChecker:
    """文本内容安全检测器 - 检测违规内容"""
    
    # 色情相关关键词
    PORNOGRAPHIC_KEYWORDS = [
        '色情', 'av', 'porn', 'sex', 'xxx', 'adult', 'nude', 'naked',
        'pussy', 'dick', 'cock', 'boobs', 'tits', 'ass', 'fuck', 'bitch',
        'slut', 'whore', 'prostitute', 'escort', 'camgirl', 'onlyfans',
        'hentai', 'erotic', 'masturbat', 'orgasm', 'ejaculat', 'blowjob',
        'handjob', 'cum', 'squirt', 'anal', 'vagina', 'penis', 'clitoris',
        'fetish', 'bdsm', 'bondage', 'swinger', 'milf', 'teen porn',
        '强奸', '乱伦', '卖淫', '嫖娼', '裸聊', '约炮', '性服务',
        '成人视频', '黄色网站', '福利姬', '援交', '包养', '裸照',
    ]
    
    # 暴力相关关键词
    VIOLENCE_KEYWORDS = [
        '暴力', 'kill', 'murder', 'death', 'die', 'suicide', ' homicide',
        'assassinat', 'terrorist', 'bomb', 'explosive', 'gun', 'weapon',
        'knife', 'stab', 'shoot', 'massacre', 'genocide', 'torture',
        'abuse', 'beat', 'fight', 'war', 'battle', 'bloodshed',
        '杀人', '自杀', '死亡', '尸体', '血腥', '虐待', '殴打',
        '恐怖袭击', '爆炸', '炸弹', '枪支', '武器', '刀具', '刺杀',
        '屠杀', '酷刑', '家暴', '校园暴力', '打架斗殴', '械斗',
    ]
    
    # 血腥相关关键词
    GORE_KEYWORDS = [
        '血腥', 'blood', 'gore', 'gory', 'dismember', 'decapitat',
        'mutilat', 'corpse', 'dead body', 'rotting', 'cannibal',
        'necro', 'snuff', 'beheading', 'execution', 'torture porn',
        '断肢', '分尸', '斩首', '碎尸', '尸体', '腐烂', '食人',
        '虐杀', '处决', '活体解剖', '器官贩卖', '人体实验',
    ]
    
    # 赌博相关关键词
    GAMBLING_KEYWORDS = [
        '赌博', '博彩', '赌场', 'bet', 'gamble', 'casino', 'lottery',
        'jackpot', 'slot machine', 'poker', 'blackjack', 'roulette',
        'sports betting', 'online casino', '彩票', '六合彩', '赌球',
        '百家乐', '老虎机', '德州扑克', '麻将赌博', '网络赌博',
        '赌马', '赌狗', '飞艇', '快三', '时时彩', '北京赛车',
    ]
    
    # 毒品相关关键词
    DRUG_KEYWORDS = [
        '毒品', '吸毒', '贩毒', 'drug', 'cocaine', 'heroin', 'meth',
        'marijuana', 'cannabis', 'weed', 'lsd', 'ecstasy', 'mdma',
        'opium', 'fentanyl', 'overdose', 'narcotic', '冰毒', '海洛因',
        '可卡因', '大麻', '摇头丸', '麻古', 'k粉', '白粉', '罂粟',
        '致幻剂', '兴奋剂', '镇静剂', '吸毒工具', '制毒',
    ]
    
    # 诈骗相关关键词
    FRAUD_KEYWORDS = [
        '诈骗', '欺诈', 'scam', 'fraud', 'phishing', 'deception',
        'hoax', 'con', 'swindle', 'extortion', 'blackmail', 'ransom',
        'pyramid scheme', 'ponzi', 'multi-level marketing', 'mlm',
        '电信诈骗', '网络诈骗', '钓鱼网站', '虚假中奖', '冒充公检法',
        '杀猪盘', '刷单诈骗', '贷款诈骗', '投资诈骗', '传销',
        '非法集资', '洗钱', '套现', '盗刷', '信用卡诈骗',
    ]
    
    @classmethod
    def check_content(cls, text):
        """
        检测文本内容安全
        返回: (是否安全, 违规类型, 详细提示, 风险等级颜色)
        """
        if not text or len(text.strip()) == 0:
            return (True, None, '内容为空', (0.5, 0.5, 0.5, 1))
        
        text_lower = text.lower()
        violations = []
        
        # 检查各类违规内容
        checks = [
            (cls.PORNOGRAPHIC_KEYWORDS, '色情内容', '🔞'),
            (cls.VIOLENCE_KEYWORDS, '暴力内容', '💀'),
            (cls.GORE_KEYWORDS, '血腥内容', '🩸'),
            (cls.GAMBLING_KEYWORDS, '赌博内容', '🎲'),
            (cls.DRUG_KEYWORDS, '毒品内容', '💊'),
            (cls.FRAUD_KEYWORDS, '诈骗内容', '⚠️'),
        ]
        
        for keywords, category, icon in checks:
            found = cls._check_keywords(text_lower, keywords)
            if found:
                violations.append((category, found, icon))
        
        if violations:
            # 构建详细提示
            details = []
            for category, found_words, icon in violations:
                word_str = ', '.join(found_words[:3])
                details.append(f"{icon} 检测到{category}: {word_str}")
            
            detail_text = '\n'.join(details)
            return (False, '违规内容', detail_text, (0.9, 0.1, 0.1, 1))  # 红色
        
        # 如果是普通文本，认为是安全的
        return (True, '安全文本', '✅ 普通文本内容，无违规信息', (0.2, 0.8, 0.2, 1))  # 绿色
    
    @staticmethod
    def _check_keywords(text, keywords):
        """检查文本中是否包含关键词"""
        found = []
        for keyword in keywords:
            if keyword.lower() in text:
                found.append(keyword)
        return found


class URLSecurityChecker:
    """URL安全检测器 - 三档安全等级"""
    
    # 危险关键词（权重：严重=3, 警告=1）
    DANGEROUS_KEYWORDS = {
        # 严重危险关键词 (权重3)
        'login': 3, 'signin': 3, 'account': 3, 'password': 3, 'verify': 3,
        'secure': 3, 'update': 3, 'confirm': 3, 'banking': 3, 'payment': 3,
        'wallet': 3, 'crypto': 3, 'bitcoin': 3, 'verify-account': 3,
        'security-check': 3, 'authenticate': 3, 'credential': 3,
        
        # 警告关键词 (权重1)
        'free': 1, 'gift': 1, 'prize': 1, 'winner': 1, 'bonus': 1,
        'discount': 1, 'offer': 1, 'limited': 1, 'urgent': 1, 'alert': 1,
        'suspend': 1, 'restricted': 1, 'locked': 1, 'unusual': 1,
        'click': 1, 'download': 1, 'install': 1, 'upgrade': 1,
    }
    
    # 可疑顶级域名
    SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.top', '.xyz', '.club', '.work', '.date']
    
    # 可疑URL模式
    SUSPICIOUS_PATTERNS = [
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP地址
        r'[a-zA-Z0-9]{30,}',  # 超长随机字符串
        r'[0o][0o]',  # 数字0和字母o混淆
        r'[il1][il1][il1]',  # i, l, 1混淆
    ]
    
    # 短链接服务
    SHORT_URL_SERVICES = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 
                          'short.link', 'is.gd', 'buff.ly', 'rebrand.ly']
    
    @classmethod
    def check_url(cls, url):
        """
        检测URL安全等级
        返回: (安全等级, 风险分数, 详细提示, 颜色)
        安全等级: 'safe', 'warning', 'dangerous'
        """
        if not url.startswith(('http://', 'https://')):
            return ('safe', 0, '非链接内容', (0.5, 0.5, 0.5, 1))
        
        risk_score = 0
        risk_factors = []
        
        # 1. 检查协议 (http vs https)
        if url.startswith('http://'):
            risk_score += 1
            risk_factors.append('使用不安全的HTTP协议')
        
        # 2. 解析URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            query = parsed.query.lower()
            
            # 3. 检查域名长度 (过短或过长都可疑)
            if len(domain) < 5:
                risk_score += 2
                risk_factors.append('域名过短')
            elif len(domain) > 50:
                risk_score += 2
                risk_factors.append('域名过长')
            
            # 4. 检查可疑顶级域名
            for tld in cls.SUSPICIOUS_TLDS:
                if domain.endswith(tld):
                    risk_score += 2
                    risk_factors.append(f'使用可疑域名后缀 {tld}')
                    break
            
            # 5. 检查短链接
            for short_service in cls.SHORT_URL_SERVICES:
                if short_service in domain:
                    risk_score += 2
                    risk_factors.append('使用短链接服务（可能隐藏真实目标）')
                    break
            
            # 6. 检查数字和特殊字符比例
            domain_chars = re.sub(r'[^a-zA-Z0-9]', '', domain)
            if domain_chars:
                digit_ratio = sum(c.isdigit() for c in domain_chars) / len(domain_chars)
                if digit_ratio > 0.3:
                    risk_score += 2
                    risk_factors.append('域名包含过多数字')
            
            # 7. 检查URL熵值（随机性）
            url_entropy = cls.calculate_entropy(url)
            if url_entropy > 4.5:
                risk_score += 1
                risk_factors.append('URL结构异常复杂')
            
            # 8. 检查危险关键词
            full_url = (domain + path + query).lower()
            for keyword, weight in cls.DANGEROUS_KEYWORDS.items():
                if keyword in full_url:
                    risk_score += weight
                    if weight >= 3:
                        risk_factors.append(f'包含严重危险关键词: {keyword}')
            
            # 9. 检查可疑模式
            for pattern in cls.SUSPICIOUS_PATTERNS:
                if re.search(pattern, url, re.IGNORECASE):
                    risk_score += 2
                    risk_factors.append('URL包含可疑模式')
                    break
            
            # 10. 检查子域名数量
            subdomain_count = domain.count('.') - 1
            if subdomain_count > 3:
                risk_score += 2
                risk_factors.append('子域名层级过多')
            
            # 11. 检查@符号（钓鱼常用）
            if '@' in url:
                risk_score += 3
                risk_factors.append('URL包含@符号（钓鱼攻击特征）')
            
            # 12. 检查端口号
            if ':' in domain and not (':80' in domain or ':443' in domain):
                risk_score += 1
                risk_factors.append('使用非标准端口')
                
        except Exception as e:
            risk_score += 1
            risk_factors.append('URL解析异常')
        
        # 确定安全等级
        max_possible_score = 20  # 理论最大风险分
        risk_percentage = (risk_score / max_possible_score) * 100
        
        if risk_percentage < 20:
            level = 'safe'
            icon = '✅'
            color = (0.2, 0.8, 0.2, 1)  # 绿色
        elif risk_percentage < 60:
            level = 'warning'
            icon = '⚠️'
            color = (1.0, 0.6, 0.0, 1)  # 橙色
        else:
            level = 'dangerous'
            icon = '🚨'
            color = (0.9, 0.1, 0.1, 1)  # 红色
        
        # 生成详细提示
        if risk_factors:
            detail = f"{icon} 发现 {len(risk_factors)} 个风险点:\n" + "\n".join([f"  • {f}" for f in risk_factors[:5]])
        else:
            detail = f"{icon} 未发现明显风险"
        
        return (level, risk_percentage, detail, color)
    
    @staticmethod
    def calculate_entropy(string):
        """计算字符串的熵值（随机性）"""
        if not string:
            return 0
        
        prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
        entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy


# ============================================================
# 第三部分：导入依赖库
# ============================================================

try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    from PIL import Image as PILImage
    LIBS_AVAILABLE = True
except ImportError as e:
    LIBS_AVAILABLE = False
    print("[!] 错误: 缺少必要的库")
    print("请安装: pip install opencv-python pyzbar Pillow numpy")
    input("按回车键退出...")
    sys.exit(1)

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.relativelayout import RelativeLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.image import Image
    from kivy.uix.popup import Popup
    from kivy.uix.filechooser import FileChooserListView
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.core.text import LabelBase
    from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
    from kivy.utils import platform
    from kivy.core.clipboard import Clipboard
    from kivy.metrics import dp
    KIVY_AVAILABLE = True
except ImportError as e:
    KIVY_AVAILABLE = False
    print("[!] 错误: 缺少Kivy库")
    print("请安装: pip install kivy")
    input("按回车键退出...")
    sys.exit(1)


# ============================================================
# 第四部分：字体配置（Kivy加载后执行）
# ============================================================

FONT_NAME = 'Roboto'
FONT_CONFIG = None

if KIVY_AVAILABLE:
    try:
        FONT_CONFIG = setup_fonts()
        FONT_NAME = FONT_CONFIG.get('font_name', 'Roboto')
        print(f"[*] 使用字体: {FONT_NAME}")
    except Exception as e:
        print(f"[!] 字体配置失败: {e}")
        FONT_NAME = 'Roboto'


# ============================================================
# 第五部分：二维码扫描核心类
# ============================================================

class QRCodeScanner:
    """二维码扫描器核心类"""
    
    def __init__(self):
        self.capture = None
        self.is_running = False
        self.last_result = None
        
    def start_camera(self, camera_id=0):
        """启动摄像头"""
        self.capture = cv2.VideoCapture(camera_id)
        if not self.capture.isOpened():
            raise Exception("无法打开摄像头")
        
        # 设置较低的分辨率以提高性能
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_running = True
        return True
        
    def stop_camera(self):
        """停止摄像头"""
        self.is_running = False
        if self.capture:
            self.capture.release()
            self.capture = None
            
    def get_frame(self):
        """获取一帧图像"""
        if self.capture and self.is_running:
            ret, frame = self.capture.read()
            if ret:
                return frame
        return None
        
    def preprocess_for_artistic_qr(self, image):
        """增强预处理 - 支持异形二维码和难识别二维码"""
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        preprocessed_images = []
        
        # 1. 原始灰度图
        preprocessed_images.append(gray)
        
        # 2. 对比度增强（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        preprocessed_images.append(enhanced)
        
        # 3. 自适应阈值 - 小窗口（对细节保留好）
        adaptive_small = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 7, 2)
        preprocessed_images.append(adaptive_small)
        
        # 4. 自适应阈值 - 大窗口（对整体效果好）
        adaptive_large = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 21, 5)
        preprocessed_images.append(adaptive_large)
        
        # 5. OTSU自动阈值
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        preprocessed_images.append(otsu)
        
        # 6. 高斯模糊后OTSU（去除噪声）
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, blurred_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        preprocessed_images.append(blurred_otsu)
        
        # 7. 中值滤波（去除椒盐噪声）
        median = cv2.medianBlur(gray, 5)
        preprocessed_images.append(median)
        
        # 8. 形态学闭运算（填充小孔）
        kernel_close = np.ones((3, 3), np.uint8)
        morph_close = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel_close)
        preprocessed_images.append(morph_close)
        
        # 9. 形态学开运算（去除小噪点）
        kernel_open = np.ones((2, 2), np.uint8)
        morph_open = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel_open)
        preprocessed_images.append(morph_open)
        
        # 10. 锐化（增强边缘）
        kernel_sharpen = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
        sharpened = cv2.filter2D(gray, -1, kernel_sharpen)
        preprocessed_images.append(sharpened)
        
        # 11. 双边滤波（保边去噪）
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        preprocessed_images.append(bilateral)
        
        # 12. 直方图均衡化
        equalized = cv2.equalizeHist(gray)
        preprocessed_images.append(equalized)
        
        # 13. 反色图像（有些二维码是反色的）
        inverted = cv2.bitwise_not(gray)
        preprocessed_images.append(inverted)
        
        # 14. 缩放图像（对过小或过大的二维码）
        height, width = gray.shape
        if height < 200 or width < 200:
            # 放大小图像
            scaled_up = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            preprocessed_images.append(scaled_up)
        elif height > 1000 or width > 1000:
            # 缩小大图像
            scaled_down = cv2.resize(gray, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            preprocessed_images.append(scaled_down)
        
        # 15. 透视变换校正（对倾斜/变形的二维码）
        try:
            # 检测轮廓并尝试校正
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 近似多边形
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # 如果是四边形（可能是二维码）
                if len(approx) == 4 and cv2.contourArea(approx) > 1000:
                    pts = approx.reshape(4, 2)
                    rect = np.zeros((4, 2), dtype="float32")
                    
                    # 排序点：左上、右上、右下、左下
                    s = pts.sum(axis=1)
                    rect[0] = pts[np.argmin(s)]
                    rect[2] = pts[np.argmax(s)]
                    
                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]
                    rect[3] = pts[np.argmax(diff)]
                    
                    # 计算目标尺寸
                    width = max(int(np.linalg.norm(rect[1] - rect[0])),
                               int(np.linalg.norm(rect[2] - rect[3])))
                    height = max(int(np.linalg.norm(rect[3] - rect[0])),
                                int(np.linalg.norm(rect[2] - rect[1])))
                    
                    dst = np.array([
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1],
                        [0, height - 1]], dtype="float32")
                    
                    # 透视变换
                    M = cv2.getPerspectiveTransform(rect, dst)
                    warped = cv2.warpPerspective(gray, M, (width, height))
                    preprocessed_images.append(warped)
                    break
        except Exception:
            pass
        
        # 16. 圆形二维码检测（极坐标转换）
        try:
            height, width = gray.shape
            center = (width // 2, height // 2)
            max_radius = min(center[0], center[1])
            
            # 转换为极坐标
            polar = cv2.warpPolar(gray, (360, max_radius), center, max_radius, cv2.WARP_POLAR_LINEAR)
            preprocessed_images.append(polar)
            
            # 旋转后的极坐标
            polar_rotated = cv2.rotate(polar, cv2.ROTATE_90_CLOCKWISE)
            preprocessed_images.append(polar_rotated)
        except Exception:
            pass
        
        # 17. 多尺度检测
        for scale in [0.8, 1.2, 1.5]:
            try:
                scaled = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                preprocessed_images.append(scaled)
            except Exception:
                continue
        
        return preprocessed_images
        
    def scan_frame(self, frame):
        """增强扫描 - 支持各种难识别二维码和异形二维码"""
        if frame is None:
            return []
        
        all_results = []
        seen_data = set()
        
        # 1. 首先尝试直接扫描原图（支持所有二维码类型）
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            try:
                data = self._decode_data(obj.data)
                if data and data not in seen_data:
                    seen_data.add(data)
                    rect = obj.rect
                    all_results.append({
                        'data': data,
                        'type': obj.type,
                        'rect': (rect.left, rect.top, rect.width, rect.height)
                    })
            except Exception:
                continue
        
        # 如果已经识别到，直接返回（优化性能）
        if all_results:
            return all_results
        
        # 2. 尝试扫描原图的灰度版本
        try:
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            decoded_objects = decode(gray)
            for obj in decoded_objects:
                try:
                    data = self._decode_data(obj.data)
                    if data and data not in seen_data:
                        seen_data.add(data)
                        rect = obj.rect
                        all_results.append({
                            'data': data,
                            'type': obj.type,
                            'rect': (rect.left, rect.top, rect.width, rect.height)
                        })
                except Exception:
                    continue
            
            if all_results:
                return all_results
        except Exception:
            pass
        
        # 3. 预处理图像并尝试多种方法
        preprocessed_images = self.preprocess_for_artistic_qr(frame)
        
        # 4. 对每种预处理方法尝试识别
        for processed_img in preprocessed_images:
            try:
                decoded_objects = decode(processed_img)
                
                for obj in decoded_objects:
                    try:
                        data = self._decode_data(obj.data)
                        
                        if data and data not in seen_data:
                            seen_data.add(data)
                            rect = obj.rect
                            all_results.append({
                                'data': data,
                                'type': obj.type,
                                'rect': (rect.left, rect.top, rect.width, rect.height)
                            })
                    except Exception:
                        continue
                
                # 如果识别到结果，可以提前结束
                if all_results:
                    break
                    
            except Exception:
                continue
        
        return all_results
    
    def _decode_data(self, raw_data):
        """解码二维码数据 - 支持多种编码"""
        if not raw_data:
            return None
        
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'shift_jis', 'euc-jp', 'latin-1', 'ascii']
        
        for encoding in encodings:
            try:
                return raw_data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 如果都失败，使用utf-8带错误忽略
        try:
            return raw_data.decode('utf-8', errors='ignore')
        except:
            return str(raw_data) if raw_data else None
        
    def scan_image_file(self, image_path):
        """增强图片文件扫描 - 支持各种格式、异形和难识别二维码"""
        try:
            # 尝试多种方式读取图片
            img = None
            
            # 方法1: OpenCV直接读取
            img = cv2.imread(image_path)
            
            # 方法2: 如果OpenCV失败，使用PIL
            if img is None:
                try:
                    pil_img = PILImage.open(image_path)
                    # 转换为RGB（处理RGBA等格式）
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    img = np.array(pil_img)
                    # RGB转BGR（OpenCV格式）
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                except Exception as e:
                    print(f"PIL读取失败: {e}")
            
            if img is None:
                print(f"无法读取图片: {image_path}")
                return []
            
            # 先尝试直接扫描
            results = self.scan_frame(img)
            if results:
                return results
            
            # 如果失败，尝试旋转图片（有些二维码是倾斜的）
            for angle in [90, 180, 270]:
                try:
                    height, width = img.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated = cv2.warpAffine(img, rotation_matrix, (width, height))
                    results = self.scan_frame(rotated)
                    if results:
                        return results
                except Exception as e:
                    continue
            
            # 尝试裁剪不同区域（对局部二维码有效）
            height, width = img.shape[:2]
            crops = [
                (0, 0, width, height),  # 全图
                (0, 0, width//2, height//2),  # 左上
                (width//2, 0, width, height//2),  # 右上
                (0, height//2, width//2, height),  # 左下
                (width//2, height//2, width, height),  # 右下
                (width//4, height//4, width*3//4, height*3//4),  # 中心
            ]
            
            for x1, y1, x2, y2 in crops:
                try:
                    cropped = img[y1:y2, x1:x2]
                    if cropped.size > 0:
                        results = self.scan_frame(cropped)
                        if results:
                            return results
                except Exception as e:
                    continue
            
            # 尝试水平翻转（有些二维码是镜像的）
            try:
                flipped = cv2.flip(img, 1)
                results = self.scan_frame(flipped)
                if results:
                    return results
            except Exception:
                pass
            
            # 尝试垂直翻转
            try:
                flipped = cv2.flip(img, 0)
                results = self.scan_frame(flipped)
                if results:
                    return results
            except Exception:
                pass
            
            return []
            
        except Exception as e:
            print(f"扫描图片失败: {e}")
            return []


# ============================================================
# 第六部分：现代化UI组件
# ============================================================

# 现代化配色方案 - 深色主题
COLORS = {
    'primary': (0.15, 0.68, 0.38, 1),      # 主色调 - 翠绿
    'secondary': (0.2, 0.6, 0.86, 1),      # 次要色 - 天蓝
    'accent': (0.9, 0.3, 0.3, 1),          # 强调色 - 暗红
    'background': (0.12, 0.12, 0.14, 1),   # 背景色 - 深灰黑
    'surface': (0.18, 0.18, 0.2, 1),       # 表面色 - 稍浅灰
    'card': (0.22, 0.22, 0.25, 1),         # 卡片色
    'text_primary': (0.95, 0.95, 0.95, 1), # 主要文字 - 近白
    'text_secondary': (0.6, 0.6, 0.65, 1), # 次要文字 - 灰
    'success': (0.2, 0.8, 0.4, 1),         # 成功绿
    'warning': (1.0, 0.7, 0.2, 1),         # 警告黄
    'danger': (0.95, 0.25, 0.25, 1),       # 危险红
}


class ModernButton(Button):
    """现代化按钮 - 固定大小"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = (1, 1, 1, 1)
        self.font_size = dp(14)
        self.border = (0, 0, 0, 0)
        # 固定高度，不随窗口变化
        self.size_hint_y = None
        self.height = dp(45)


class ModernCard(BoxLayout):
    """现代化卡片组件"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(pos=self.draw_background, size=self.draw_background)
        
    def draw_background(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS['card'])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])


class SecurityIndicator(BoxLayout):
    """安全等级指示器 - 带说明和弹窗"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(55)
        self.padding = [dp(10), dp(5)]
        
        # 主布局 - 水平排列
        main_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30)
        )
        
        # 安全等级文字
        self.level_label = Label(
            text='安全检测中...',
            font_name=FONT_NAME,
            font_size=dp(13),
            halign='left',
            valign='middle',
            color=COLORS['text_secondary'],
            size_hint_x=0.6
        )
        self.level_label.bind(size=self.level_label.setter('text_size'))
        main_layout.add_widget(self.level_label)
        
        # 说明按钮（可点击）
        self.info_btn = Button(
            text='[?] 安全评估说明',
            markup=True,
            font_name=FONT_NAME,
            font_size=dp(10),
            halign='right',
            valign='middle',
            color=COLORS['secondary'],
            background_color=(0, 0, 0, 0),
            background_normal='',
            size_hint_x=0.4
        )
        self.info_btn.bind(on_press=self.show_security_info)
        main_layout.add_widget(self.info_btn)
        
        self.add_widget(main_layout)
        
        # 小字说明
        self.hint_label = Label(
            text='百分比越小越安全，超过60%不建议跳转',
            font_name=FONT_NAME,
            font_size=dp(9),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(15),
            halign='left'
        )
        self.hint_label.bind(size=self.hint_label.setter('text_size'))
        self.add_widget(self.hint_label)
        
    def update_security(self, level, percentage, detail, color):
        """更新安全显示"""
        level_names = {
            'safe': '安全',
            'warning': '警告',
            'dangerous': '严重危险',
            'text_safe': '安全文本',
            'text_dangerous': '违规内容'
        }
        
        self.level_label.text = f"{level_names.get(level, '未知')} ({percentage:.0f}%)"
        self.level_label.color = color
        
        # 根据安全等级更新提示文字
        if percentage < 20:
            hint = '该链接安全，可放心访问'
        elif percentage < 60:
            hint = '该链接存在一定风险，请谨慎访问'
        else:
            hint = '该链接风险较高，强烈建议不要访问'
        self.hint_label.text = hint
        
    def show_security_info(self, instance):
        """显示安全评估说明弹窗（大字，方便老人查看）"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        # 标题
        title_label = Label(
            text='[b]安全评估说明[/b]',
            markup=True,
            font_name=FONT_NAME,
            font_size=dp(22),
            color=COLORS['primary'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title_label)
        
        # 说明内容 - 使用ScrollView以防内容过长
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1))
        
        info_text = Label(
            text='''
[b]安全等级划分：[/b]

[color=00cc00]● 安全 (0-20%)[/color]
  链接安全可靠，可放心访问

[color=ffaa00]● 警告 (20-60%)[/color]
  链接存在一定风险
  建议谨慎访问，仔细核对网址

[color=ff4444]● 严重危险 (60-100%)[/color]
  链接风险极高！
  [b]强烈建议不要访问[/b]
  可能是钓鱼网站或恶意链接

[b]评估原则：[/b]
• 百分比越小越安全
• 使用HTTPS比HTTP更安全
• 短链接和可疑域名风险较高
• 包含敏感词汇的链接需谨慎

[b]安全建议：[/b]
• 不随意点击不明链接
• 仔细核对网址是否正确
• 涉及金钱交易务必谨慎
• 遇到可疑链接及时关闭
            ''',
            markup=True,
            font_name=FONT_NAME,
            font_size=dp(16),
            color=COLORS['text_primary'],
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        info_text.bind(texture_size=info_text.setter('size'))
        info_text.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))
        scroll.add_widget(info_text)
        content.add_widget(scroll)
        
        # 关闭按钮
        close_btn = ModernButton(
            text='我知道了',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(45),
            background_color=COLORS['primary']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, 0.8),
            separator_height=0,
            background_color=COLORS['surface']
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


class CameraPreview(RelativeLayout):
    """摄像头预览组件，带二维码追踪显示"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 摄像头图像显示
        self.image = Image(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            fit_mode='contain'
        )
        self.add_widget(self.image)
        
        # 扫描框装饰 - 固定大小
        with self.canvas:
            Color(0.2, 0.8, 0.4, 0.6)
            self.scan_line = Line(width=dp(2))
        
        # 二维码信息标签（浮动在图像上方）- 固定大小
        self.qr_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(11),
            size_hint=(None, None),
            size=(dp(300), dp(30)),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            markup=True,
            color=(1, 1, 1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        self.add_widget(self.qr_label)
        
        # 扫描状态标签 - 固定大小
        self.status_label = Label(
            text='点击"开始扫描"启动摄像头',
            font_name=FONT_NAME,
            font_size=dp(12),
            size_hint=(1, None),
            height=dp(30),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            color=COLORS['secondary']
        )
        self.add_widget(self.status_label)
        
        self.current_result = None
        
    def update_frame(self, frame, qr_results=None):
        """更新帧并显示二维码信息"""
        if frame is not None:
            # 转换颜色空间
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame_rgb.shape[:2]
            
            # 绘制二维码方框和信息
            if qr_results:
                for result in qr_results:
                    x, y, w_rect, h_rect = result['rect']
                    data = result['data']
                    
                    # 绘制方框
                    cv2.rectangle(frame_rgb, (x, y), (x + w_rect, y + h_rect), (0, 255, 100), 2)
                    
                    # 在方框上方显示内容（截断过长的内容）
                    display_text = data if len(data) < 20 else data[:20] + '...'
                    cv2.putText(frame_rgb, display_text, (x, y - 8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 100), 1)
                    
                    # 更新浮动标签
                    self.current_result = result
                    self.qr_label.text = f"[b]{display_text}[/b]"
                    self.qr_label.color = (0.2, 1, 0.4, 1)
            else:
                self.qr_label.text = ''
            
            # 更新图像
            buf = frame_rgb.tobytes()
            from kivy.graphics.texture import Texture
            from kivy.metrics import dp
            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.flip_vertical()
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture
            
    def set_status(self, text, color=None):
        """设置状态文字"""
        if color is None:
            color = COLORS['secondary']
        self.status_label.text = text
        self.status_label.color = color


# ============================================================
# 第七部分：主界面
# ============================================================

class MainScreen(BoxLayout):
    """主界面 - 优化布局"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(10)
        
        # 设置背景色
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        self.scanner = QRCodeScanner()
        self.is_scanning = False
        self.scan_event = None
        
        self.setup_ui()
        
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
    def setup_ui(self):
        from kivy.metrics import dp
        
        # 标题栏 - 固定高度
        title_bar = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            padding=[dp(15), dp(10)]
        )
        with title_bar.canvas.before:
            Color(*COLORS['surface'])
            Rectangle(pos=title_bar.pos, size=title_bar.size)
        title_bar.bind(pos=self.update_title_bar, size=self.update_title_bar)
        
        title = Label(
            text='[b]二维码安全扫描器[/b]',
            markup=True,
            font_name=FONT_NAME,
            font_size=dp(18),
            color=COLORS['primary'],
            halign='center'
        )
        title_bar.add_widget(title)
        self.add_widget(title_bar)
        
        # 安全提示卡片 - 固定高度
        security_card = ModernCard()
        security_card.height = dp(45)
        
        security_text = Label(
            text='安全防护已开启 | 仅提取内容，不会自动跳转',
            font_name=FONT_NAME,
            font_size=dp(12),
            color=COLORS['text_secondary'],
            halign='center',
            valign='center'
        )
        security_text.bind(size=security_text.setter('text_size'))
        security_card.add_widget(security_text)
        
        self.add_widget(security_card)
        
        # 摄像头预览区域 - 使用weight分配空间
        preview_card = ModernCard()
        preview_card.size_hint_y = 1  # 占据剩余空间
        preview_card.padding = dp(8)
        
        self.preview = CameraPreview(size_hint=(1, 1))
        preview_card.add_widget(self.preview)
        self.add_widget(preview_card)
        
        # 安全等级指示器 - 固定高度
        self.security_indicator = SecurityIndicator()
        self.add_widget(self.security_indicator)
        
        # 结果显示区域 - 固定高度
        result_card = ModernCard()
        result_card.height = dp(100)
        
        result_title = Label(
            text='识别结果',
            font_name=FONT_NAME,
            font_size=dp(12),
            color=COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(20),
            halign='left'
        )
        result_title.bind(size=result_title.setter('text_size'))
        result_card.add_widget(result_title)
        
        self.result_label = Label(
            text='请将二维码对准摄像头',
            font_name=FONT_NAME,
            font_size=dp(13),
            size_hint=(1, 1),
            halign='center',
            valign='middle',
            color=COLORS['text_primary'],
            markup=True
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        result_card.add_widget(self.result_label)
        
        self.add_widget(result_card)
        
        # 按钮区域 - 固定高度，2行2列
        btn_layout = GridLayout(
            cols=2,
            size_hint=(1, None),
            height=dp(100),
            spacing=dp(10)
        )
        
        # 开始/停止扫描按钮
        self.scan_btn = ModernButton(
            text='开始扫描',
            font_size=dp(14),
            background_color=COLORS['secondary']
        )
        self.scan_btn.bind(on_press=self.toggle_scanning)
        btn_layout.add_widget(self.scan_btn)
        
        # 上传图片按钮
        self.upload_btn = ModernButton(
            text='上传图片',
            font_size=dp(14),
            background_color=COLORS['primary']
        )
        self.upload_btn.bind(on_press=self.show_file_chooser)
        btn_layout.add_widget(self.upload_btn)
        
        # 复制内容按钮
        self.copy_btn = ModernButton(
            text='复制内容',
            font_size=dp(14),
            background_color=COLORS['accent'],
            disabled=True
        )
        self.copy_btn.bind(on_press=self.copy_result)
        btn_layout.add_widget(self.copy_btn)
        
        # 清除结果按钮
        self.clear_btn = ModernButton(
            text='清除结果',
            font_size=dp(14),
            background_color=COLORS['text_secondary']
        )
        self.clear_btn.bind(on_press=self.clear_result)
        btn_layout.add_widget(self.clear_btn)
        
        self.add_widget(btn_layout)
        
    def update_title_bar(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*COLORS['surface'])
            Rectangle(pos=instance.pos, size=instance.size)
        
    def toggle_scanning(self, instance):
        """切换扫描状态"""
        if not self.is_scanning:
            self.start_scanning()
        else:
            self.stop_scanning()
            
    def start_scanning(self):
        """开始扫描"""
        try:
            self.scanner.start_camera()
            self.is_scanning = True
            self.scan_btn.text = '⏹ 停止扫描'
            self.scan_btn.background_color = COLORS['accent']
            self.preview.set_status('摄像头运行中... 请将二维码对准摄像头')
            
            # 启动定时更新
            self.scan_event = Clock.schedule_interval(self.update_camera, 1.0 / 30.0)
        except Exception as e:
            self.preview.set_status(f'摄像头启动失败: {str(e)}', COLORS['accent'])
            
    def stop_scanning(self):
        """停止扫描"""
        self.is_scanning = False
        if self.scan_event:
            self.scan_event.cancel()
            self.scan_event = None
        self.scanner.stop_camera()
        self.scan_btn.text = '▶ 开始扫描'
        self.scan_btn.background_color = COLORS['secondary']
        self.preview.set_status('扫描已停止')
        self.preview.qr_label.text = ''
        
    def update_camera(self, dt):
        """更新摄像头画面 - 识别结果保持显示"""
        frame = self.scanner.get_frame()
        if frame is not None:
            # 扫描二维码
            results = self.scanner.scan_frame(frame)
            
            # 更新预览（带追踪显示）
            self.preview.update_frame(frame, results)
            
            # 更新结果标签 - 只在识别到新内容时更新，保持显示
            if results:
                result = results[0]
                data = result['data']
                
                # 检查是否是新内容（避免重复更新同一内容）
                if not hasattr(self, 'last_scanned_data') or self.last_scanned_data != data:
                    self.last_scanned_data = data
                    self.preview.current_result = result
                    
                    # 检测内容安全并显示
                    self.analyze_content(data)
            # 不识别到时不清空结果，保持上次识别的内容
                
    def analyze_content(self, data):
        """分析内容安全（链接或文本）- 允许复制所有内容"""
        # 存储完整数据供复制使用
        self.current_data = data
        
        # 首先检测是否为链接
        if data.startswith(('http://', 'https://', 'ftp://', 'file://')):
            # 链接安全检测
            level, percentage, detail, color = URLSecurityChecker.check_url(data)
            self.security_indicator.update_security(level, percentage, detail, color)
            
            # 显示完整内容（不截断）
            self.result_label.text = f"[b]链接内容：[/b]\n{data}\n\n[b]安全状态：[/b]{detail}"
        else:
            # 文本内容安全检测
            is_safe, violation_type, detail, color = ContentSafetyChecker.check_content(data)
            
            if is_safe:
                self.security_indicator.update_security('text_safe', 0, detail, color)
                content_type = '文本内容'
            else:
                self.security_indicator.update_security('text_dangerous', 100, detail, color)
                content_type = f'⚠️ {violation_type}'
            
            # 显示完整文本内容（不截断）
            self.result_label.text = f"[b]{content_type}：[/b]\n{data}\n\n[b]安全状态：[/b]{detail}"
        
        # 始终启用复制按钮
        self.copy_btn.disabled = False
                
    def show_file_chooser(self, instance):
        """显示文件选择器"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        select_btn = ModernButton(text='选择')
        cancel_btn = ModernButton(text='取消', background_color=COLORS['text_secondary'])
        
        popup = Popup(title='', content=content, size_hint=(0.9, 0.9), separator_height=0)
        
        def on_select(instance):
            if filechooser.selection:
                self.scan_image(filechooser.selection[0])
                popup.dismiss()
                
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()
        
    def scan_image(self, path):
        """扫描图片"""
        results = self.scanner.scan_image_file(path)
        
        if results:
            result = results[0]
            data = result['data']
            self.preview.current_result = result
            
            # 使用统一的内容分析方法
            self.analyze_content(data)
            self.preview.set_status('图片扫描成功')
        else:
            self.result_label.text = '未检测到二维码'
            self.preview.set_status('未检测到二维码', COLORS['accent'])
            
    def copy_result(self, instance):
        """复制结果 - 复制完整内容"""
        # 优先使用当前分析的数据（完整内容）
        if hasattr(self, 'current_data') and self.current_data:
            Clipboard.copy(self.current_data)
            self.preview.set_status('内容已复制到剪贴板')
        elif self.preview.current_result:
            Clipboard.copy(self.preview.current_result['data'])
            self.preview.set_status('内容已复制到剪贴板')
    
    def clear_result(self, instance):
        """清除识别结果"""
        # 重置所有结果相关数据
        self.last_scanned_data = None
        self.current_data = None
        self.preview.current_result = None
        
        # 重置显示
        self.result_label.text = '请将二维码对准摄像头\n识别结果将显示在这里'
        self.security_indicator.level_label.text = '安全检测中...'
        self.security_indicator.level_label.color = COLORS['text_secondary']
        self.copy_btn.disabled = True
        self.preview.set_status('结果已清除，请扫描新的二维码')


# ============================================================
# 第八部分：应用入口
# ============================================================

class QRScannerApp(App):
    """二维码扫描器应用"""
    
    def build(self):
        self.title = '二维码安全扫描器'
        Window.size = (500, 800)
        Window.clearcolor = COLORS['background']
        
        return MainScreen()
        
    def on_stop(self):
        """应用关闭时清理"""
        pass


if __name__ == '__main__':
    print("=" * 60)
    print("二维码安全扫描器 v2.1")
    print("功能：提取二维码内容 + 智能安全检测 + 文本内容审查")
    print("=" * 60)
    print()
    
    QRScannerApp().run()
