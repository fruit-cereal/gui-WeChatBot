#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置模块示例
配置日志记录器和自定义过滤器

【使用说明】
1. 请复制此文件到 config 文件夹中
2. 根据需要调整日志配置参数
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 确保日志目录存在
os.makedirs("log", exist_ok=True)

# 创建一个自定义的日志过滤器，根据消息内容决定是否记录到文件
class OCRLogFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        # 标记是否找到触发词并需要开始记录OCR结果
        self.trigger_found = False
        # 标记是否正在记录OCR识别结果
        self.recording_ocr = False
    
    def filter(self, record):
        # 始终允许非OCR识别结果的日志通过（初始化、错误等信息）
        if "OCR识别结果:" not in record.msg and not self.recording_ocr:
            return True
        
        # 如果消息包含"检测到触发词"，开始记录OCR
        if "检测到触发词" in record.msg:
            self.trigger_found = True
            return True
        
        # 标记OCR识别结果的开始
        if "OCR识别结果:" in record.msg:
            self.recording_ocr = True
            # 只有在找到触发词后才记录OCR识别结果
            return self.trigger_found
        
        # 处理OCR识别的文本行
        if self.recording_ocr and "文本:" in record.msg:
            # 只有在找到触发词后才记录OCR识别结果
            return self.trigger_found
        
        # 标记OCR识别结果的结束，重置状态
        if self.recording_ocr and "文本:" not in record.msg:
            self.recording_ocr = False
            
        # 如果消息包含"消息已发送"，表示一轮交互结束，重置触发词标记
        if "消息已发送" in record.msg:
            self.trigger_found = False
            
        return True

# 自定义日志文件名格式，基于当前日期
def get_log_filename():
    """根据当前日期生成日志文件名"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("log", f"{today}-bot-log.log")

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建一个控制台处理器（不过滤，所有信息都输出到控制台）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 创建一个文件处理器（使用过滤器，只记录符合条件的信息）
file_handler = TimedRotatingFileHandler(
    filename=get_log_filename(),  # 使用日期格式化的文件名
    when="midnight",
    interval=1,
    backupCount=30,  # 保留30天的日志
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# 创建并添加过滤器到文件处理器
ocr_filter = OCRLogFilter()
file_handler.addFilter(ocr_filter)

# 添加处理器到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 阻止日志传递到父logger
logger.propagate = False
