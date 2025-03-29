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

# 自定义日志文件名格式，基于当前日期
def get_log_filename():
    """根据当前日期生成日志文件名"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("log", f"{today}-wechat_bot.log")

# --- 自定义过滤器 ---
class FileLogFilter(logging.Filter):
    """
    自定义日志过滤器，只允许带有 'save_to_file' 标记的记录通过。
    """
    def filter(self, record):
        # 检查记录是否有名为 'save_to_file' 的属性，并且其值为 True
        # 如果没有这个属性，默认为 False (即不保存到文件)
        return getattr(record, 'save_to_file', False)

# --- Logger 设置 ---
logger = logging.getLogger("WeChatBotLogger") # 给logger一个名字
# 设置全局最低日志级别为 INFO (不再依赖Config)
logger.setLevel(logging.INFO)


# --- 格式化器 ---
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # 添加了logger名字

# --- 控制台处理器 ---
# 控制台始终显示INFO及以上级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
# 控制台处理器不过滤，显示所有达到其级别的日志
logger.addHandler(console_handler)


# --- 文件处理器 ---
# 文件处理器也使用INFO级别，但会通过过滤器筛选
file_handler = TimedRotatingFileHandler(
    filename=get_log_filename(),
    when="midnight",
    interval=1,
    backupCount=30,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO) # 与logger级别一致
file_handler.setFormatter(formatter)

# --- 添加过滤器到文件处理器 ---
file_filter = FileLogFilter()
file_handler.addFilter(file_filter) # 只给文件处理器添加过滤器

# --- 添加文件处理器到Logger ---
logger.addHandler(file_handler)


# --- 防止日志向上传播 ---
# 如果根logger有处理器，可能会导致日志重复打印
logger.propagate = False
