#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置模块
配置日志记录器和自定义过滤器
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
        # 标记是否需要记录OCR结果
        self.should_record = False
        # 标记是否正在记录OCR识别结果
        self.recording_ocr = False
        # 存储临时OCR日志
        self.ocr_buffer = []
        # 标记是否正在缓冲OCR日志
        self.buffering = False
    
    def filter(self, record):
        # 始终允许非OCR识别结果的日志通过（初始化、错误等信息）
        if "OCR识别结果:" not in record.msg and not self.recording_ocr and not self.buffering:
            # 如果消息包含"消息已发送"，表示消息成功发送，应该记录之前缓冲的OCR日志
            if "消息已发送" in record.msg:
                self.should_record = True
                # 输出缓冲的OCR日志
                for buffered_record in self.ocr_buffer:
                    # 创建一个新的日志记录，复制缓冲的内容
                    new_record = logging.LogRecord(
                        buffered_record.name,
                        buffered_record.levelno,
                        buffered_record.pathname,
                        buffered_record.lineno,
                        buffered_record.msg,
                        buffered_record.args,
                        buffered_record.exc_info,
                        func=buffered_record.funcName
                    )
                    # 将新记录传递给处理器（绕过过滤器）
                    for handler in logging.getLogger(buffered_record.name).handlers:
                        if isinstance(handler, logging.FileHandler) or isinstance(handler, logging.handlers.TimedRotatingFileHandler):
                            handler.emit(new_record)
                
                # 清空缓冲区并重置状态
                self.ocr_buffer = []
                self.buffering = False
                self.should_record = False
            
            return True
        
        # 如果检测到触发词，开始缓冲OCR日志但不立即记录
        if "检测到触发词" in record.msg:
            self.buffering = True
            # 将触发词日志添加到缓冲区
            self.ocr_buffer.append(record)
            return True
        
        # 标记OCR识别结果的开始
        if "OCR识别结果:" in record.msg:
            self.recording_ocr = True
            # 如果正在缓冲，添加到缓冲区
            if self.buffering:
                self.ocr_buffer.append(record)
                return False  # 暂时不记录到文件
            return self.should_record
        
        # 处理OCR识别的文本行
        if self.recording_ocr and "文本:" in record.msg:
            # 如果正在缓冲，添加到缓冲区
            if self.buffering:
                self.ocr_buffer.append(record)
                return False  # 暂时不记录到文件
            return self.should_record
        
        # 标记OCR识别结果的结束，重置状态
        if self.recording_ocr and "文本:" not in record.msg:
            self.recording_ocr = False
            
        return True

# 自定义日志文件名格式，基于当前日期
def get_log_filename():
    """根据当前日期生成日志文件名"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("log", f"{today}-wechat_bot.log")

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
