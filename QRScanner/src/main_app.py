# -*- coding: utf-8 -*-
"""
二维码扫描器主应用
使用Kivy框架构建跨平台GUI
"""
import os
import sys
import threading
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import StringProperty, ListProperty
from kivy.utils import platform
from kivy.core.clipboard import Clipboard

# 导入扫描器核心
from qr_scanner import QRCodeScanner

# 注册字体
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
LabelBase.register(name='MicrosoftYaHei', fn_regular=os.path.join(FONT_DIR, 'msyh.ttc'))
LabelBase.register(name='SimHei', fn_regular=os.path.join(FONT_DIR, 'simhei.ttf'))
LabelBase.register(name='SimSun', fn_regular=os.path.join(FONT_DIR, 'simsun.ttc'))
LabelBase.register(name='Arial', fn_regular=os.path.join(FONT_DIR, 'arial.ttf'))


class CameraTab(BoxLayout):
    """摄像头扫描标签页"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.scanner = QRCodeScanner()
        self.is_scanning = False
        self.current_result = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 摄像头预览区域
        preview_container = RelativeLayout(size_hint=(1, 0.55))
        
        self.preview_image = Image(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        preview_container.add_widget(self.preview_image)
        
        # 扫描框覆盖层
        with preview_container.canvas:
            Color(0, 1, 0, 0.8)
            self.scan_box = Line(points=[], width=2)
            
        self.add_widget(preview_container)
        
        # 结果显示区域
        result_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.25),
            padding=5,
            spacing=5
        )
        
        # 结果标题
        result_title = Label(
            text='扫描结果',
            font_name='MicrosoftYaHei',
            font_size='16sp',
            size_hint=(1, 0.2),
            halign='left',
            color=(0.2, 0.2, 0.2, 1)
        )
        result_title.bind(size=result_title.setter('text_size'))
        result_container.add_widget(result_title)
        
        # 结果内容
        self.result_label = Label(
            text='请将二维码对准摄像头框内',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            size_hint=(1, 0.5),
            halign='center',
            valign='middle',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        result_container.add_widget(self.result_label)
        
        # 结果类型标签
        self.type_label = Label(
            text='',
            font_name='MicrosoftYaHei',
            font_size='12sp',
            size_hint=(1, 0.15),
            color=(0.5, 0.5, 0.5, 1)
        )
        result_container.add_widget(self.type_label)
        
        self.add_widget(result_container)
        
        # 按钮区域
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.12),
            spacing=10
        )
        
        self.start_btn = Button(
            text='开始扫描',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            background_color=(0.2, 0.7, 0.3, 1),
            background_normal=''
        )
        self.start_btn.bind(on_press=self.toggle_scanning)
        button_layout.add_widget(self.start_btn)
        
        self.save_btn = Button(
            text='保存内容',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            background_color=(0.3, 0.5, 0.8, 1),
            background_normal='',
            disabled=True
        )
        self.save_btn.bind(on_press=self.save_result)
        button_layout.add_widget(self.save_btn)
        
        self.copy_btn = Button(
            text='复制',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            background_color=(0.8, 0.6, 0.2, 1),
            background_normal='',
            disabled=True
        )
        self.copy_btn.bind(on_press=self.copy_result)
        button_layout.add_widget(self.copy_btn)
        
        self.add_widget(button_layout)
        
    def toggle_scanning(self, instance):
        """切换扫描状态"""
        if self.is_scanning:
            self.stop_scanning()
        else:
            self.start_scanning()
            
    def start_scanning(self):
        """开始扫描"""
        try:
            self.scanner.start_camera(0)
            self.is_scanning = True
            self.start_btn.text = '停止扫描'
            self.start_btn.background_color = (0.8, 0.2, 0.2, 1)
            
            # 启动扫描线程
            self.scan_thread = threading.Thread(target=self.scan_loop)
            self.scan_thread.daemon = True
            self.scan_thread.start()
            
            # 启动UI更新
            Clock.schedule_interval(self.update_preview, 1.0 / 30.0)
            
        except Exception as e:
            self.result_label.text = f'摄像头错误: {str(e)}'
            
    def stop_scanning(self):
        """停止扫描"""
        self.is_scanning = False
        self.scanner.stop_camera()
        self.start_btn.text = '开始扫描'
        self.start_btn.background_color = (0.2, 0.7, 0.3, 1)
        Clock.unschedule(self.update_preview)
        
    def scan_loop(self):
        """扫描循环"""
        while self.is_scanning:
            frame = self.scanner.get_frame()
            if frame is not None:
                results = self.scanner.scan_frame(frame)
                if results:
                    result = results[0]
                    Clock.schedule_once(
                        lambda dt, r=result: self.on_scan_success(r), 0
                    )
            time.sleep(0.1)
            
    def update_preview(self, dt):
        """更新预览"""
        frame = self.scanner.get_frame()
        if frame is not None:
            # 绘制扫描框
            results = self.scanner.scan_frame(frame)
            display_frame = self.scanner.draw_scan_box(frame, results)
            
            # 转换为RGB
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # 更新纹理
            h, w = display_frame.shape[:2]
            buf = display_frame.tobytes()
            
            from kivy.graphics.texture import Texture
            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.preview_image.texture = texture
            
    def on_scan_success(self, result):
        """扫描成功回调"""
        self.current_result = result
        data = result['data']
        code_type = result['type']
        
        # 截断显示过长的内容
        display_data = data if len(data) < 100 else data[:100] + '...'
        self.result_label.text = display_data
        self.type_label.text = f'类型: {code_type}'
        
        # 启用按钮
        self.save_btn.disabled = False
        self.copy_btn.disabled = False
        
    def save_result(self, instance):
        """保存结果"""
        if self.current_result:
            try:
                filepath, file_type = self.scanner.save_result(
                    self.current_result['data']
                )
                self.result_label.text = f'已保存到:\n{filepath}'
            except Exception as e:
                self.result_label.text = f'保存失败: {str(e)}'
                
    def copy_result(self, instance):
        """复制结果"""
        if self.current_result:
            Clipboard.copy(self.current_result['data'])
            self.result_label.text = '内容已复制到剪贴板'


class ImageTab(BoxLayout):
    """图片扫描标签页"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.scanner = QRCodeScanner()
        self.current_image_path = None
        self.current_result = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 图片预览区域
        self.preview_image = Image(
            size_hint=(1, 0.5),
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.preview_image)
        
        # 选择文件按钮
        select_btn = Button(
            text='选择图片',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            size_hint=(1, 0.08),
            background_color=(0.3, 0.5, 0.8, 1),
            background_normal=''
        )
        select_btn.bind(on_press=self.show_file_chooser)
        self.add_widget(select_btn)
        
        # 结果显示区域
        self.result_label = Label(
            text='请选择一张包含二维码的图片',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            size_hint=(1, 0.25),
            halign='center',
            valign='middle',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.add_widget(self.result_label)
        
        # 按钮区域
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=10
        )
        
        self.save_btn = Button(
            text='保存内容',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            background_color=(0.3, 0.5, 0.8, 1),
            background_normal='',
            disabled=True
        )
        self.save_btn.bind(on_press=self.save_result)
        button_layout.add_widget(self.save_btn)
        
        self.copy_btn = Button(
            text='复制',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            background_color=(0.8, 0.6, 0.2, 1),
            background_normal='',
            disabled=True
        )
        self.copy_btn.bind(on_press=self.copy_result)
        button_layout.add_widget(self.copy_btn)
        
        self.add_widget(button_layout)
        
    def show_file_chooser(self, instance):
        """显示文件选择器"""
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
        )
        content.add_widget(filechooser)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        select_btn = Button(text='选择', font_name='MicrosoftYaHei')
        cancel_btn = Button(text='取消', font_name='MicrosoftYaHei')
        
        popup = Popup(title='选择图片', content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                self.load_image(filechooser.selection[0])
                popup.dismiss()
                
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()
        
    def load_image(self, path):
        """加载并扫描图片"""
        self.current_image_path = path
        
        # 显示图片
        self.preview_image.source = path
        
        # 扫描二维码
        results = self.scanner.scan_image_file(path)
        
        if results:
            self.current_result = results[0]
            data = results[0]['data']
            display_data = data if len(data) < 100 else data[:100] + '...'
            self.result_label.text = f'扫描结果:\n{display_data}'
            self.save_btn.disabled = False
            self.copy_btn.disabled = False
        else:
            self.result_label.text = '未检测到二维码'
            self.current_result = None
            self.save_btn.disabled = True
            self.copy_btn.disabled = True
            
    def save_result(self, instance):
        """保存结果"""
        if self.current_result:
            try:
                filepath, file_type = self.scanner.save_result(
                    self.current_result['data']
                )
                self.result_label.text = f'已保存到:\n{filepath}'
            except Exception as e:
                self.result_label.text = f'保存失败: {str(e)}'
                
    def copy_result(self, instance):
        """复制结果"""
        if self.current_result:
            Clipboard.copy(self.current_result['data'])
            self.result_label.text = '内容已复制到剪贴板'


class HistoryTab(BoxLayout):
    """历史记录标签页"""
    
    def __init__(self, scanner, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.scanner = scanner
        
        self.setup_ui()
        Clock.schedule_interval(self.refresh_history, 2.0)
        
    def setup_ui(self):
        # 标题
        title = Label(
            text='扫描历史',
            font_name='MicrosoftYaHei',
            font_size='18sp',
            size_hint=(1, 0.08),
            color=(0.2, 0.2, 0.2, 1)
        )
        self.add_widget(title)
        
        # 历史列表
        scroll = ScrollView(size_hint=(1, 0.77))
        self.history_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None,
            padding=5
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        self.add_widget(scroll)
        
        # 清除按钮
        clear_btn = Button(
            text='清除历史',
            font_name='MicrosoftYaHei',
            font_size='14sp',
            size_hint=(1, 0.08),
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal=''
        )
        clear_btn.bind(on_press=self.clear_history)
        self.add_widget(clear_btn)
        
    def refresh_history(self, dt):
        """刷新历史记录"""
        history = self.scanner.get_history()
        
        if len(self.history_layout.children) != len(history):
            self.history_layout.clear_widgets()
            
            for item in reversed(history):
                history_item = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=80,
                    padding=5
                )
                
                with history_item.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    Rectangle(pos=history_item.pos, size=history_item.size)
                    
                # 时间和类型
                header = Label(
                    text=f"{item['time']} | {item['type']}",
                    font_name='MicrosoftYaHei',
                    font_size='11sp',
                    size_hint=(1, 0.3),
                    halign='left',
                    color=(0.5, 0.5, 0.5, 1)
                )
                header.bind(size=header.setter('text_size'))
                history_item.add_widget(header)
                
                # 数据内容
                data_text = item['data'] if len(item['data']) < 50 else item['data'][:50] + '...'
                data_label = Label(
                    text=data_text,
                    font_name='MicrosoftYaHei',
                    font_size='12sp',
                    size_hint=(1, 0.7),
                    halign='left',
                    valign='top',
                    color=(0.2, 0.2, 0.2, 1)
                )
                data_label.bind(size=data_label.setter('text_size'))
                history_item.add_widget(data_label)
                
                self.history_layout.add_widget(history_item)
                
    def clear_history(self, instance):
        """清除历史"""
        self.scanner.clear_history()
        self.history_layout.clear_widgets()


class QRScannerApp(App):
    """二维码扫描器应用"""
    
    def build(self):
        self.title = '二维码扫描器'
        Window.size = (480, 800)
        Window.clearcolor = (0.98, 0.98, 0.98, 1)
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical')
        
        # 创建标签页
        self.tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_pos='top_mid',
            tab_width=150
        )
        
        # 摄像头扫描标签
        self.camera_tab = CameraTab()
        camera_header = TabbedPanelHeader(text='摄像头扫描')
        camera_header.content = self.camera_tab
        self.tab_panel.add_widget(camera_header)
        
        # 图片扫描标签
        self.image_tab = ImageTab()
        image_header = TabbedPanelHeader(text='图片扫描')
        image_header.content = self.image_tab
        self.tab_panel.add_widget(image_header)
        
        # 历史记录标签（使用摄像头扫描的scanner实例）
        self.history_tab = HistoryTab(self.camera_tab.scanner)
        history_header = TabbedPanelHeader(text='历史记录')
        history_header.content = self.history_tab
        self.tab_panel.add_widget(history_header)
        
        # 默认选中摄像头标签
        self.tab_panel.default_tab = camera_header
        
        main_layout.add_widget(self.tab_panel)
        
        return main_layout
        
    def on_stop(self):
        """应用关闭时清理"""
        self.camera_tab.stop_scanning()


if __name__ == '__main__':
    QRScannerApp().run()
