"""
RimWorld Mod 名称翻译工具 - PySide6版本
功能：批量处理RimWorld模组的About.xml文件，使用AI生成中文名称
作者：daisy
"""

import os
import xml.etree.ElementTree as ET
import time
import json
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QFileDialog,
    QGroupBox, QProgressBar, QMessageBox, QTabWidget
)
from PySide6.QtCore import QThread, Signal, Slot, QObject
from PySide6.QtGui import QFont, QTextCursor

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("提示：未安装 python-dotenv，请确保手动设置环境变量")

import chat2gpt4o


class RenameSwapWorkerSignals(QObject):
    """重命名和交换操作的信号定义"""
    log = Signal(str)  # 日志信号
    progress = Signal(int, int)  # 进度信号 (当前, 总数)
    finished = Signal()  # 完成信号
    error = Signal(str)  # 错误信号


class RenameSwapWorker(QThread):
    """重命名和交换操作工作线程"""
    
    def __init__(self, directory_path: str, operation: str):
        super().__init__()
        self.directory_path = directory_path
        self.operation = operation  # 'rename' or 'swap'
        self.signals = RenameSwapWorkerSignals()
        self.is_running = True

    def stop(self):
        """停止处理"""
        self.is_running = False
        self.signals.log.emit("⚠️ 正在停止处理...")

    def run(self):
        """执行重命名/交换任务"""
        try:
            # 获取所有子目录
            folder_paths = self._get_directory_names(self.directory_path)
            
            if not folder_paths:
                self.signals.error.emit("未找到任何子文件夹")
                return
            
            total = len(folder_paths)
            self.signals.log.emit(f"📁 找到 {total} 个模组文件夹")
            self.signals.log.emit("=" * 60)
            
            processed = 0
            skipped = 0
            failed = 0
            
            for i, folder_path in enumerate(folder_paths):
                if not self.is_running:
                    self.signals.log.emit("❌ 处理已被用户停止")
                    break

                about_directory = os.path.join(folder_path, 'About')
                try:
                    if self.operation == 'rename':
                        success = self._rename_files_in_directories(about_directory)
                    else:  # swap
                        success = self._swap_about_files(about_directory)
                    
                    if success:
                        processed += 1
                        folder_name = os.path.basename(folder_path)
                        self.signals.log.emit(f"✅ [{processed}/{total}] {folder_name}")
                    else:
                        skipped += 1
                        folder_name = os.path.basename(folder_path)
                        self.signals.log.emit(f"⏭️  [{skipped}/{total}] 跳过: {folder_name}")
                    
                    self.signals.progress.emit(i + 1, total)
                    
                except Exception as e:
                    failed += 1
                    folder_name = os.path.basename(folder_path)
                    self.signals.log.emit(f"❌ 处理失败 [{folder_name}]: {str(e)}")
                    self.signals.progress.emit(i + 1, total)
            
            # 输出统计信息
            if self.is_running:
                self.signals.log.emit("=" * 60)
                self.signals.log.emit(
                    f"📊 处理完成！成功: {processed}, 跳过: {skipped}, 失败: {failed}"
                )
            
        except Exception as e:
            self.signals.error.emit(f"处理过程出错: {str(e)}")
        finally:
            self.signals.finished.emit()

    def _get_directory_names(self, path: str) -> List[str]:
        """获取目录下的所有子目录"""
        try:
            return [
                os.path.join(path, name) 
                for name in os.listdir(path) 
                if os.path.isdir(os.path.join(path, name))
            ]
        except Exception as e:
            self.signals.error.emit(f"读取目录失败: {str(e)}")
            return []

    def _rename_files_in_directories(self, base_directory: str) -> bool:
        """重命名文件 - 交换 About.xml 和 About_old.xml"""
        try:
            about_path = os.path.join(base_directory, 'About.xml')
            about_old_path = os.path.join(base_directory, 'About_old.xml')

            if os.path.exists(about_old_path):
                tree = ET.parse(about_path)
                root = tree.getroot()
                name_element = root.find('name')

                if name_element is not None and not any('\u4e00' <= char <= '\u9fff' for char in name_element.text or ''):
                    os.rename(about_path, os.path.join(base_directory, 'About_temp.xml'))
                    os.rename(about_old_path, about_path)
                    os.rename(os.path.join(base_directory, 'About_temp.xml'), about_old_path)
                    return True
            return False
        except Exception as e:
            self.signals.log.emit(f"❌ 重命名错误: {str(e)}")
            return False

    def _swap_about_files(self, base_directory: str) -> bool:
        """交换文件 - 还原 About.xml 和 About_old.xml"""
        try:
            about = os.path.join(base_directory, 'About.xml')
            about_old = os.path.join(base_directory, 'About_old.xml')
            
            if os.path.exists(about_old):
                tree = ET.parse(about)
                root = tree.getroot()
                name_element = root.find('name')

                if name_element is not None and any('\u4e00' <= char <= '\u9fff' for char in name_element.text or ''):
                    if os.path.exists(about):
                        os.rename(about, os.path.join(base_directory, 'About_temp.xml'))
                    os.rename(about_old, about)
                    os.rename(os.path.join(base_directory, 'About_temp.xml'), about_old)
                    return True
            return False
        except Exception as e:
            self.signals.log.emit(f"❌ 交换错误: {str(e)}")
            return False


class WorkerSignals(QObject):
    """工作线程的信号定义"""
    log = Signal(str)  # 日志信号
    progress = Signal(int, int)  # 进度信号 (当前, 总数)
    finished = Signal()  # 完成信号
    error = Signal(str)  # 错误信号


class ModProcessorWorker(QThread):
    """模组处理工作线程"""
    
    def __init__(self, directory_path: str, model_name: str = "glm", api_key: str = "", base_url: str = ""):
        super().__init__()
        self.directory_path = directory_path
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.signals = WorkerSignals()
        self.is_running = True
        self.prompt = (
            '我会给出游戏《RIMWORLD》的模组名称和模组的描述，'
            '你需根据原来的英文名称和描述(不一定是英文，可能是任何语言)'
            '用大约20个字（不能超过20）来简短总结这个mod是什么或者有什么功能，'
            '请直接回答你对这个mod的总结即可，总结必须为中文。'
        )
    
    def stop(self):
        """停止处理"""
        self.is_running = False
        self.signals.log.emit("⚠️ 正在停止处理...")
    
    def run(self):
        """执行处理任务"""
        try:
            # 获取所有子目录
            folder_paths = self._get_directory_names(self.directory_path)
            
            if not folder_paths:
                self.signals.error.emit("未找到任何子文件夹")
                return
            
            total = len(folder_paths)
            self.signals.log.emit(f"📁 找到 {total} 个模组文件夹")
            self.signals.log.emit("=" * 60)
            
            # 使用线程池处理
            processed = 0
            skipped = 0
            failed = 0
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                futures = {
                    executor.submit(self._process_folder, folder): folder 
                    for folder in folder_paths
                }
                
                for future in as_completed(futures):
                    if not self.is_running:
                        # 取消所有未完成的任务
                        for f in futures:
                            f.cancel()
                        self.signals.log.emit("❌ 处理已被用户停止")
                        break
                    
                    folder = futures[future]
                    try:
                        result = future.result()
                        if result:
                            status, name, summary = result
                            if status == "success":
                                processed += 1
                                self.signals.log.emit(
                                    f"✅ [{processed}/{total}] {name}\n"
                                    f"   AI总结: {summary}"
                                )
                            elif status == "skipped":
                                skipped += 1
                                self.signals.log.emit(
                                    f"⏭️  [{processed + skipped}/{total}] 跳过: {name}"
                                )
                        else:
                            failed += 1
                            
                        self.signals.progress.emit(processed + skipped + failed, total)
                        
                    except Exception as e:
                        failed += 1
                        folder_name = os.path.basename(folder)
                        self.signals.log.emit(f"❌ 处理失败 [{folder_name}]: {str(e)}")
                        self.signals.progress.emit(processed + skipped + failed, total)
            
            # 输出统计信息
            if self.is_running:
                self.signals.log.emit("=" * 60)
                self.signals.log.emit(
                    f"📊 处理完成！成功: {processed}, 跳过: {skipped}, 失败: {failed}"
                )
            
        except Exception as e:
            self.signals.error.emit(f"处理过程出错: {str(e)}")
        finally:
            self.signals.finished.emit()
    
    def _get_directory_names(self, path: str) -> List[str]:
        """获取目录下的所有子目录"""
        try:
            return [
                os.path.join(path, name) 
                for name in os.listdir(path) 
                if os.path.isdir(os.path.join(path, name))
            ]
        except Exception as e:
            self.signals.error.emit(f"读取目录失败: {str(e)}")
            return []
    
    def _process_folder(self, folder_path: str) -> Optional[tuple]:
        """处理单个模组文件夹"""
        about_path = os.path.join(folder_path, 'About', 'About.xml')
        backup_path = os.path.join(folder_path, 'About', 'About_old.xml')
        
        # 检查备份文件是否存在，如果存在则跳过
        if os.path.exists(backup_path):
            folder_name = os.path.basename(folder_path)
            return ("skipped", folder_name, "已处理过")
        
        # 检查About.xml是否存在
        if not os.path.exists(about_path):
            return None
        
        try:
            # 解析XML文件
            tree = ET.parse(about_path)
            root = tree.getroot()
            
            # 获取名称和描述
            name_elem = root.find('name')
            desc_elem = root.find('description')
            
            if name_elem is None:
                return None
            
            name = name_elem.text if name_elem.text else '未找到名称'
            description = desc_elem.text if desc_elem is not None and desc_elem.text else '未找到描述'
            
            # 检查名称是否已包含中文
            if self._contains_chinese(name):
                return ("skipped", name, "已包含中文")
            
            # 调用AI生成中文总结
            message = f'名称：{name}，描述：{description}'
            try:
                import chat2gpt4o
                # 使用自定义模型配置
                summary = chat2gpt4o.call_model(
                    model_name=self.model_name,
                    message=message,
                    pormet=self.prompt,
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                # 如果chat2gpt4o不可用，使用简单的模拟
                summary = f"中文总结: {name[:10]}模组"
            except Exception as e:
                self.signals.log.emit(f"❌ AI调用失败: {str(e)}")
                return None
            
            if not summary:
                return None
            
            # 先备份原文件
            tree.write(backup_path, encoding='utf-8', xml_declaration=True)
            
            # 修改名称并保存
            name_elem.text = summary
            tree.write(about_path, encoding='utf-8', xml_declaration=True)
            
            # 添加延迟避免API限流
            time.sleep(1)
            
            return ("success", name, summary)
            
        except ET.ParseError as e:
            raise Exception(f"XML解析错误: {str(e)}")
        except Exception as e:
            raise Exception(f"处理错误: {str(e)}")
    
    @staticmethod
    def _contains_chinese(text: str) -> bool:
        """检查文本是否包含中文字符"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)


class ModProcessorGUI(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.rename_swap_worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("RimWorld Mod 名称翻译工具 - Made by Daisy")
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建选项卡控件
        tab_widget = QTabWidget()
        
        
        # 第一个选项卡：AI翻译功能
        ai_translation_tab = QWidget()
        ai_layout = QVBoxLayout(ai_translation_tab)
        
        # 模型配置区域
        model_group = QGroupBox("🤖 AI模型配置")
        model_group.setFont(QFont("Microsoft YaHei", 10))
        model_layout = QVBoxLayout()
        
        # 模型名称输入
        model_name_layout = QHBoxLayout()
        model_name_label = QLabel("模型名称:")
        model_name_label.setFont(QFont("Microsoft YaHei", 9))
        model_name_label.setMinimumWidth(80)
        self.model_name_input = QLineEdit()
        self.model_name_input.setText("glm")
        self.model_name_input.setFont(QFont("Microsoft YaHei", 9))
        self.model_name_input.setMinimumHeight(35)
        self.model_name_input.setPlaceholderText("例如: glm, deepseek, qwen, gpt")
        model_name_layout.addWidget(model_name_label)
        model_name_layout.addWidget(self.model_name_input)
        model_layout.addLayout(model_name_layout)
        
        # API密钥输入
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API密钥:")
        api_key_label.setFont(QFont("Microsoft YaHei", 9))
        api_key_label.setMinimumWidth(80)
        self.api_key_input = QLineEdit()
        self.api_key_input.setFont(QFont("Microsoft YaHei", 9))
        self.api_key_input.setMinimumHeight(35)
        self.api_key_input.setPlaceholderText("请输入API密钥")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        model_layout.addLayout(api_key_layout)
        
        # API基础URL输入
        base_url_layout = QHBoxLayout()
        base_url_label = QLabel("API地址:")
        base_url_label.setFont(QFont("Microsoft YaHei", 9))
        base_url_label.setMinimumWidth(80)
        self.base_url_input = QLineEdit()
        self.base_url_input.setFont(QFont("Microsoft YaHei", 9))
        self.base_url_input.setMinimumHeight(35)
        self.base_url_input.setPlaceholderText("可选，使用默认地址可留空")
        base_url_layout.addWidget(base_url_label)
        base_url_layout.addWidget(self.base_url_input)
        model_layout.addLayout(base_url_layout)
        
        # 配置保存/加载按钮
        config_button_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("💾 保存配置")
        self.save_config_btn.setFont(QFont("Microsoft YaHei", 9))
        self.save_config_btn.setMinimumSize(100, 35)
        self.save_config_btn.clicked.connect(self.save_model_config)
        
        self.load_config_btn = QPushButton("📂 加载配置")
        self.load_config_btn.setFont(QFont("Microsoft YaHei", 9))
        self.load_config_btn.setMinimumSize(100, 35)
        self.load_config_btn.clicked.connect(self.load_model_config)
        
        config_button_layout.addWidget(self.save_config_btn)
        config_button_layout.addWidget(self.load_config_btn)
        config_button_layout.addStretch()
        model_layout.addLayout(config_button_layout)
        
        model_group.setLayout(model_layout)
        ai_layout.addWidget(model_group)
        
        # 路径选择区域 (AI Translation tab)
        path_group = QGroupBox("📂 模组文件夹路径")
        path_group.setFont(QFont("Microsoft YaHei", 10))
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setText(r'E:\steam\steamapps\workshop\content\294100')
        self.path_input.setFont(QFont("Microsoft YaHei", 9))
        self.path_input.setMinimumHeight(35)
        
        self.browse_btn = QPushButton("🔍 浏览")
        self.browse_btn.setFont(QFont("Microsoft YaHei", 9))
        self.browse_btn.setMinimumSize(100, 35)
        self.browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        path_group.setLayout(path_layout)
        ai_layout.addWidget(path_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m (%p%)")
        ai_layout.addWidget(self.progress_bar)
        
        # 日志输出区域
        log_group = QGroupBox("📋 处理日志")
        log_group.setFont(QFont("Microsoft YaHei", 10))
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        ai_layout.addWidget(log_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("▶️ 开始处理")
        self.start_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.start_btn.setMinimumSize(150, 45)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.start_btn.clicked.connect(self.start_processing)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.stop_btn.setMinimumSize(150, 45)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
            QPushButton:pressed {
                background-color: #a52314;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_processing)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        
        ai_layout.addLayout(button_layout)
        
        # 第二个选项卡：重命名/交换功能
        rename_swap_tab = QWidget()
        rs_layout = QVBoxLayout(rename_swap_tab)
        
        # 路径选择区域 (重命名/交换选项卡)
        rs_path_group = QGroupBox("📂 模组文件夹路径")
        rs_path_group.setFont(QFont("Microsoft YaHei", 10))
        rs_path_layout = QHBoxLayout()
        
        self.rs_path_input = QLineEdit()
        self.rs_path_input.setText(r'E:\steam\steamapps\workshop\content\294100')
        self.rs_path_input.setFont(QFont("Microsoft YaHei", 9))
        self.rs_path_input.setMinimumHeight(35)
        
        self.rs_browse_btn = QPushButton("🔍 浏览")
        self.rs_browse_btn.setFont(QFont("Microsoft YaHei", 9))
        self.rs_browse_btn.setMinimumSize(100, 35)
        self.rs_browse_btn.clicked.connect(self.rs_browse_folder)
        
        rs_path_layout.addWidget(self.rs_path_input)
        rs_path_layout.addWidget(self.rs_browse_btn)
        rs_path_group.setLayout(rs_path_layout)
        rs_layout.addWidget(rs_path_group)
        
        # 进度条
        self.rs_progress_bar = QProgressBar()
        self.rs_progress_bar.setMinimumHeight(25)
        self.rs_progress_bar.setTextVisible(True)
        self.rs_progress_bar.setFormat("%v / %m (%p%)")
        rs_layout.addWidget(self.rs_progress_bar)
        
        # 日志输出区域
        rs_log_group = QGroupBox("📋 处理日志")
        rs_log_group.setFont(QFont("Microsoft YaHei", 10))
        rs_log_layout = QVBoxLayout()
        
        self.rs_log_text = QTextEdit()
        self.rs_log_text.setReadOnly(True)
        self.rs_log_text.setFont(QFont("Consolas", 9))
        self.rs_log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        rs_log_layout.addWidget(self.rs_log_text)
        rs_log_group.setLayout(rs_log_layout)
        rs_layout.addWidget(rs_log_group)
        
        # 按钮区域
        rs_button_layout = QHBoxLayout()
        rs_button_layout.addStretch()
        
        self.rename_btn = QPushButton("🔄 替换文件")
        self.rename_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.rename_btn.setMinimumSize(150, 45)
        self.rename_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.rename_btn.clicked.connect(lambda: self.start_rename_swap('rename'))
        
        self.swap_btn = QPushButton("↩️ 还原文件")
        self.swap_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.swap_btn.setMinimumSize(150, 45)
        self.swap_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
            QPushButton:pressed {
                background-color: #a52314;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.swap_btn.clicked.connect(lambda: self.start_rename_swap('swap'))
        
        self.rs_stop_btn = QPushButton("⏹️ 停止")
        self.rs_stop_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.rs_stop_btn.setMinimumSize(150, 45)
        self.rs_stop_btn.setEnabled(False)
        self.rs_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #888888;
            }
        """)
        self.rs_stop_btn.clicked.connect(self.stop_rename_swap)
        
        rs_button_layout.addWidget(self.rename_btn)
        rs_button_layout.addWidget(self.swap_btn)
        rs_button_layout.addWidget(self.rs_stop_btn)
        rs_button_layout.addStretch()
        
        rs_layout.addLayout(rs_button_layout)
        
        # 添加选项卡到控件
        tab_widget.addTab(ai_translation_tab, "🤖 AI翻译")
        tab_widget.addTab(rename_swap_tab, "🔄 重命名/交换")
        
        # 将选项卡控件添加到主布局
        main_layout.addWidget(tab_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 添加欢迎信息
        self.log_message("=" * 60)
        self.log_message("🎮 RimWorld Mod 名称翻译工具")
        self.log_message("📝 使用AI自动生成模组的中文名称")
        self.log_message("⚠️  注意：处理前会自动备份原文件为 About_old.xml")
        self.log_message("=" * 60)
        
        
        # Add welcome info for rename/swap tab
        self.rs_log_message("=" * 60)
        self.rs_log_message("🎮 RimWorld Mod 文件重命名工具")
        self.rs_log_message("📝 一键替换或还原 About.xml 文件")
        self.rs_log_message("⚠️  注意：此功能用于替换或还原已翻译的文件")
        self.rs_log_message("=" * 60)
    
    @Slot()
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择模组文件夹",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.path_input.setText(folder)
            self.log_message(f"📁 已选择路径: {folder}")
    
    @Slot()
    def start_processing(self):
        """开始处理"""
        directory_path = self.path_input.text().strip()
        
        if not directory_path:
            QMessageBox.warning(self, "警告", "请先选择模组文件夹路径！")
            return
        
        if not os.path.isdir(directory_path):
            QMessageBox.warning(self, "警告", "选择的路径不是有效的文件夹！")
            return
        
        # 清空日志和进度条
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        
        # 禁用开始按钮，启用停止按钮
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        self.path_input.setEnabled(False)
        
        self.log_message("🚀 开始处理模组文件...")
        self.statusBar().showMessage("处理中...")
        
        # 获取模型配置
        model_name = self.model_name_input.text().strip()
        api_key = self.api_key_input.text().strip()
        base_url = self.base_url_input.text().strip()
        
        if not model_name:
            QMessageBox.warning(self, "警告", "请填写模型名称！")
            self.on_processing_finished()
            return
            
        if not api_key:
            QMessageBox.warning(self, "警告", "请填写API密钥！")
            self.on_processing_finished()
            return
        
        # 创建并启动工作线程
        self.worker = ModProcessorWorker(
            directory_path=directory_path,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url
        )
        self.worker.signals.log.connect(self.log_message)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.on_processing_finished)
        self.worker.signals.error.connect(self.on_error)
        self.worker.start()
    
    @Slot()
    def stop_processing(self):
        """停止处理"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.stop_btn.setEnabled(False)
    
    @Slot()
    def on_processing_finished(self):
        """处理完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.browse_btn.setEnabled(True)
        self.path_input.setEnabled(True)
        self.statusBar().showMessage("处理完成")
        self.log_message("\n✨ 所有任务已完成！")
    
    @Slot(str)
    def on_error(self, error_msg: str):
        """处理错误"""
        self.log_message(f"❌ 错误: {error_msg}")
        QMessageBox.critical(self, "错误", error_msg)
        self.on_processing_finished()
    
    @Slot(str)
    def log_message(self, message: str):
        """添加日志消息"""
        self.log_text.append(message)
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    @Slot(int, int)
    def update_progress(self, current: int, total: int):
        """更新进度条"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(f"处理中... ({current}/{total})")

    @Slot()
    def rs_browse_folder(self):
        """浏览文件夹 (重命名/交换选项卡)"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择模组文件夹",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.rs_path_input.setText(folder)
            self.rs_log_message(f"📁 已选择路径: {folder}")

    @Slot()
    def start_rename_swap(self, operation: str):
        """开始重命名/交换操作"""
        directory_path = self.rs_path_input.text().strip()
        
        if not directory_path:
            QMessageBox.warning(self, "警告", "请先选择模组文件夹路径！")
            return
        
        if not os.path.isdir(directory_path):
            QMessageBox.warning(self, "警告", "选择的路径不是有效的文件夹！")
            return
        
        # 清空日志和进度条
        self.rs_log_text.clear()
        self.rs_progress_bar.setValue(0)
        self.rs_progress_bar.setMaximum(100)
        
        # 禁用开始按钮，启用停止按钮
        self.rename_btn.setEnabled(False)
        self.swap_btn.setEnabled(False)
        self.rs_stop_btn.setEnabled(True)
        self.rs_browse_btn.setEnabled(False)
        self.rs_path_input.setEnabled(False)
        
        operation_name = "替换" if operation == 'rename' else "还原"
        self.rs_log_message(f"🚀 开始{operation_name}操作...")
        self.statusBar().showMessage(f"{operation_name}操作中...")

        # 创建并启动工作线程
        self.rename_swap_worker = RenameSwapWorker(directory_path, operation)
        self.rename_swap_worker.signals.log.connect(self.rs_log_message)
        self.rename_swap_worker.signals.progress.connect(self.rs_update_progress)
        self.rename_swap_worker.signals.finished.connect(self.on_rs_processing_finished)
        self.rename_swap_worker.signals.error.connect(self.on_rs_error)
        self.rename_swap_worker.start()

    @Slot()
    def stop_rename_swap(self):
        """停止重命名/交换操作"""
        if self.rename_swap_worker and self.rename_swap_worker.isRunning():
            self.rename_swap_worker.stop()
            self.rs_stop_btn.setEnabled(False)

    @Slot()
    def on_rs_processing_finished(self):
        """重命名/交换处理完成"""
        self.rename_btn.setEnabled(True)
        self.swap_btn.setEnabled(True)
        self.rs_stop_btn.setEnabled(False)
        self.rs_browse_btn.setEnabled(True)
        self.rs_path_input.setEnabled(True)
        self.statusBar().showMessage("重命名/交换操作完成")
        self.rs_log_message("\n✨ 所有任务已完成！")

    @Slot(str)
    def on_rs_error(self, error_msg: str):
        """处理重命名/交换错误"""
        self.rs_log_message(f"❌ 错误: {error_msg}")
        QMessageBox.critical(self, "错误", error_msg)
        self.on_rs_processing_finished()

    @Slot(str)
    def rs_log_message(self, message: str):
        """添加重命名/交换日志消息"""
        self.rs_log_text.append(message)
        # 自动滚动到底部
        cursor = self.rs_log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.rs_log_text.setTextCursor(cursor)

    @Slot(int, int)
    def rs_update_progress(self, current: int, total: int):
        """更新重命名/交换进度条"""
        self.rs_progress_bar.setMaximum(total)
        self.rs_progress_bar.setValue(current)
        self.statusBar().showMessage(f"重命名/交换操作中... ({current}/{total})")


    @Slot()
    def save_model_config(self):
        """保存模型配置到文件"""
        config = {
            "model_name": self.model_name_input.text().strip(),
            "api_key": self.api_key_input.text().strip(),
            "base_url": self.base_url_input.text().strip()
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存模型配置",
            "model_config.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                self.log_message(f"✅ 模型配置已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
    
    @Slot()
    def load_model_config(self):
        """从文件加载模型配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "加载模型配置",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.model_name_input.setText(config.get("model_name", ""))
                self.api_key_input.setText(config.get("api_key", ""))
                self.base_url_input.setText(config.get("base_url", ""))
                
                self.log_message(f"✅ 模型配置已从文件加载: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置失败: {str(e)}")

def main():
    """主函数"""
    app = QApplication([])
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    window = ModProcessorGUI()
    window.show()
    
    # 运行应用
    app.exec()


if __name__ == "__main__":
    main()