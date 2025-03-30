#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""日志配置模块：配置日志记录器和自定义过滤器"""

import logging
import os
import time
import glob
from logging.handlers import BaseRotatingHandler

# 确保日志目录存在
os.makedirs("log", exist_ok=True)

class DirectDailyRotatingFileHandler(BaseRotatingHandler):
    """日志处理器，直接写入以当前日期命名的文件 (YYYY-MM-DD-basename.log)，并在午夜自动切换"""
    
    def __init__(self, filename_base, when='midnight', backupCount=0, encoding=None, delay=False, utc=False):
        self.log_dir = os.path.dirname(filename_base)
        self.base_name_part = os.path.basename(filename_base)
        self.suffix_format = "%Y-%m-%d"
        self.utc = utc
        self.backupCount = backupCount
        self.when = 'D' if when.upper() == 'MIDNIGHT' else when.upper()
        
        if self.when not in ['S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6']:
            raise ValueError(f"Invalid rollover time specified: {when}")
            
        # 计算当前文件名并初始化
        current_time_tuple = time.gmtime() if self.utc else time.localtime()
        current_date_str = time.strftime(self.suffix_format, current_time_tuple)
        self.current_filename = os.path.join(self.log_dir, f"{current_date_str}-{self.base_name_part}")
        
        BaseRotatingHandler.__init__(self, self.current_filename, mode='a', encoding=encoding, delay=delay)
        
        # 计算第一次轮转时间
        self.rolloverAt = self.computeRollover(int(time.time()))

    def computeRollover(self, currentTime):
        """计算下一次轮转的时间戳"""
        if self.when != 'D':
            raise NotImplementedError("只支持每日午夜('D'或'midnight')轮转")

        t = time.gmtime(currentTime) if self.utc else time.localtime(currentTime)
        
        # 计算到午夜的秒数
        seconds_since_midnight = (t[3] * 3600) + (t[4] * 60) + t[5]
        rolloverTime = currentTime - seconds_since_midnight + 86400
        
        return int(rolloverTime)

    def shouldRollover(self, record):
        """检查是否应该执行轮转"""
        return 1 if int(time.time()) >= self.rolloverAt else 0

    def doRollover(self):
        """执行轮转：关闭当前流，更新文件名到新日期，打开新流，清理旧文件"""
        # 关闭当前流
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # 计算新文件名
        current_time_tuple = time.gmtime() if self.utc else time.localtime()
        new_date_str = time.strftime(self.suffix_format, current_time_tuple)
        self.baseFilename = os.path.join(self.log_dir, f"{new_date_str}-{self.base_name_part}")
        
        # 打开新文件
        if not self.delay:
            self.stream = self._open()
        
        # 清理旧日志
        if self.backupCount > 0:
            try:
                # 获取所有匹配的日志文件
                log_pattern = os.path.join(self.log_dir, f"????-??-??-{self.base_name_part}")
                existing_logs = glob.glob(log_pattern)
                
                # 排除当前文件
                current_real_path = os.path.abspath(self.baseFilename)
                logs_to_consider = [log for log in existing_logs if os.path.abspath(log) != current_real_path]
                logs_to_consider.sort()
                
                # 删除超出保留数量的旧日志
                if len(logs_to_consider) >= self.backupCount:
                    for log_path in logs_to_consider[:len(logs_to_consider) - self.backupCount]:
                        try:
                            os.remove(log_path)
                        except OSError as e:
                            print(f"无法删除旧日志文件 {log_path}: {e}")
            except Exception as e:
                print(f"日志清理过程中出错: {e}")
        
        # 计算下一次轮转时间
        current_timestamp = int(time.time())
        newRolloverAt = self.computeRollover(current_timestamp)
        # 确保轮转时间在未来
        while newRolloverAt <= current_timestamp:
            newRolloverAt += 86400  # 增加一天
        self.rolloverAt = newRolloverAt


class FileLogFilter(logging.Filter):
    """自定义日志过滤器，只允许带有 'save_to_file' 标记的记录通过"""
    def filter(self, record):
        return getattr(record, 'save_to_file', False)


# 配置Logger
logger = logging.getLogger("WeChatBotLogger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 文件处理器
file_handler = DirectDailyRotatingFileHandler(
    filename_base=os.path.join("log", "wechat_bot.log"),
    when="midnight",
    backupCount=30,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
file_handler.addFilter(FileLogFilter())
logger.addHandler(file_handler)

# 防止日志向上传播
logger.propagate = False
