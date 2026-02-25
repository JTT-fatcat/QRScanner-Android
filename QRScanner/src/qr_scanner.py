# -*- coding: utf-8 -*-
"""
二维码扫描器核心模块
支持摄像头扫描和图片文件扫描
"""
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image as PILImage
from datetime import datetime


class QRCodeScanner:
    """二维码扫描器类"""
    
    def __init__(self):
        self.capture = None
        self.is_running = False
        self.last_result = None
        self.scan_history = []
        
    def start_camera(self, camera_id=0):
        """启动摄像头"""
        self.capture = cv2.VideoCapture(camera_id)
        if not self.capture.isOpened():
            raise Exception("无法打开摄像头")
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
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                return frame
        return None
        
    def scan_frame(self, frame):
        """扫描单帧图像中的二维码"""
        if frame is None:
            return None
            
        decoded_objects = decode(frame)
        results = []
        
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            rect = obj.rect
            result = {
                'data': data,
                'type': obj.type,
                'rect': (rect.left, rect.top, rect.width, rect.height),
                'polygon': obj.polygon
            }
            results.append(result)
            
            # 添加到历史记录
            if data not in [h['data'] for h in self.scan_history]:
                self.scan_history.append({
                    'data': data,
                    'type': obj.type,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
        return results
        
    def scan_image_file(self, image_path):
        """从图片文件扫描二维码"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                # 尝试用PIL打开
                pil_image = PILImage.open(image_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                
            return self.scan_frame(image)
        except Exception as e:
            print(f"扫描图片失败: {e}")
            return None
            
    def draw_scan_box(self, frame, results=None):
        """在图像上绘制扫描框"""
        if frame is None:
            return None
            
        h, w = frame.shape[:2]
        display_frame = frame.copy()
        
        # 绘制中心扫描框
        box_size = min(h, w) // 3
        x1 = (w - box_size) // 2
        y1 = (h - box_size) // 2
        x2 = x1 + box_size
        y2 = y1 + box_size
        
        # 绘制扫描框（四角）
        corner_length = 30
        color = (0, 255, 0)  # 绿色
        thickness = 3
        
        # 左上角
        cv2.line(display_frame, (x1, y1), (x1 + corner_length, y1), color, thickness)
        cv2.line(display_frame, (x1, y1), (x1, y1 + corner_length), color, thickness)
        
        # 右上角
        cv2.line(display_frame, (x2, y1), (x2 - corner_length, y1), color, thickness)
        cv2.line(display_frame, (x2, y1), (x2, y1 + corner_length), color, thickness)
        
        # 左下角
        cv2.line(display_frame, (x1, y2), (x1 + corner_length, y2), color, thickness)
        cv2.line(display_frame, (x1, y2), (x1, y2 - corner_length), color, thickness)
        
        # 右下角
        cv2.line(display_frame, (x2, y2), (x2 - corner_length, y2), color, thickness)
        cv2.line(display_frame, (x2, y2), (x2, y2 - corner_length), color, thickness)
        
        # 如果检测到二维码，绘制边界框
        if results:
            for result in results:
                if 'polygon' in result and result['polygon']:
                    points = np.array(result['polygon'], np.int32)
                    points = points.reshape((-1, 1, 2))
                    cv2.polylines(display_frame, [points], True, (0, 0, 255), 2)
                    
        return display_frame
        
    def save_result(self, data, save_dir='./saved'):
        """保存扫描结果"""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 判断数据类型
        if data.startswith('http://') or data.startswith('https://'):
            filename = f'url_{timestamp}.txt'
            file_type = 'URL'
        elif data.startswith('data:image'):
            # Base64编码的图片
            filename = f'image_{timestamp}.png'
            file_type = 'Image'
            try:
                import base64
                img_data = data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                with open(os.path.join(save_dir, filename), 'wb') as f:
                    f.write(img_bytes)
                return os.path.join(save_dir, filename), file_type
            except Exception as e:
                print(f"保存图片失败: {e}")
                filename = f'image_data_{timestamp}.txt'
        else:
            filename = f'text_{timestamp}.txt'
            file_type = 'Text'
            
        # 保存文本内容
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
            
        return filepath, file_type
        
    def get_history(self):
        """获取扫描历史"""
        return self.scan_history
        
    def clear_history(self):
        """清除历史记录"""
        self.scan_history = []
