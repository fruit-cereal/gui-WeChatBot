#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信机器人配置文件示例
=====================

【使用说明】
1. 请复制此文件为 config.py
2. 修改下面标记为【必须修改】的配置项
3. 根据需要调整其他配置项

【配置步骤】
1. 设置DeepSeek API密钥（必须）
2. 设置微信窗口名称（必须）
3. 调整聊天输入框和发送按钮的位置（必须，需要根据自己的屏幕分辨率调整）
4. 配置群成员名称和别名（可选，但推荐设置）
5. 调整其他配置参数（可选）
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from roles import load_all_roles

# ===========================
# 【日志配置】
# ===========================
# 每日创建新的日志文件，保存在log目录下

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

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建一个控制台处理器（不过滤，所有信息都输出到控制台）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 自定义日志文件名格式，基于当前日期
def get_log_filename():
    """根据当前日期生成日志文件名"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("log", f"{today}-bot-log.log")

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


class Config:
    # ===========================
    # 【角色配置】
    # ===========================
    # 从roles目录加载所有角色配置，通常不需要在此处修改
    # 如需添加新角色，请在roles目录中创建对应的json文件
    
    ROLES = load_all_roles()
    
    # 默认角色（机器人启动时使用的角色）
    # 【可选修改】如需更改默认角色，请修改此处
    DEFAULT_ROLE = "@专业助手bot"
    
    # ===========================
    # 【用户配置】
    # ===========================
    # 群成员名称和别名配置，用于识别消息发送者
    # 当OCR识别出的名称匹配列表中的名称或别名时，使用对应的标准名称
    # 【推荐修改】添加群内常见成员的名称和可能的OCR识别变体
    
    USER_NAMES = [
        {
            "name": "张三",  # 用户的标准名称
            "aliases": ["张三1", "张三2", "张3"]  # OCR可能错误识别的变体
        },
        # 示例：添加更多用户
        # {
        #     "name": "李四",
        #     "aliases": ["李4", "李四1", "李思"]
        # }
    ]
    
    # 当无法匹配到用户名时使用的默认名称
    # 【可选修改】
    DEFAULT_USER_NAME = "未知用户"
    
    # ===========================
    # 【截图和OCR配置】
    # ===========================
    # 控制屏幕截图频率和OCR识别质量
    
    # 截图间隔（秒）
    # 【可选修改】值越小检测消息越及时，但CPU占用越高
    SCREENSHOT_INTERVAL = 5
    
    # OCR识别置信度阈值（0-1之间）
    # 【可选修改】值越高准确性越好但可能漏识别，值越低识别率高但可能有误识别
    OCR_CONFIDENCE_THRESHOLD = 0.6
    
    # ===========================
    # 【DeepSeek API配置】
    # ===========================
    # DeepSeek大模型API配置
    
    # 【必须修改】设置DeepSeek API密钥
    # 方法1（推荐）：在系统环境变量中设置DEEPSEEK_API_KEY
    # 方法2：直接在下面设置DEEPSEEK_API_KEY = "你的API密钥"
    
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        # 如果环境变量未设置，记录错误
        error_message = "错误：环境变量 DEEPSEEK_API_KEY 未设置。请设置该环境变量或直接在配置文件中设置API密钥。"
        logger.error(error_message)
        raise ValueError(error_message) 
    
    # DeepSeek API接口地址（通常不需要修改）
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # ===========================
    # 【微信窗口配置】
    # ===========================
    # 控制如何定位和操作微信窗口
    
    # 【必须修改】设置你的微信窗口标题（即微信群名称）
    # 可以在运行微信时查看窗口标题栏确定正确的名称
    WECHAT_WINDOW_NAME = "群名称"
    
    # 微信窗口标题可能的OCR识别变体
    # 【推荐修改】如果程序无法找到微信窗口，可以添加可能的OCR识别变体
    WECHAT_WINDOW_NAME_ALIASES = ["微群名称1", "群名称2", "群名称3"]
    
    # ===========================
    # 【聊天框位置配置】
    # ===========================
    # 【必须修改】聊天框和发送按钮的相对位置
    # 这些值是相对于窗口的百分比位置（0-1之间）
    # 需要根据自己的屏幕分辨率和微信窗口大小进行调整
    
    # 聊天输入框的位置
    CHAT_INPUT_BOX_RELATIVE_X = 0.5  # 聊天输入框的X坐标（窗口宽度的百分比）
    CHAT_INPUT_BOX_RELATIVE_Y = 0.88  # 聊天输入框的Y坐标（窗口高度的百分比）
    
    # 发送按钮的位置
    SEND_BUTTON_RELATIVE_X = 0.95  # 发送按钮的X坐标（窗口宽度的百分比）
    SEND_BUTTON_RELATIVE_Y = 0.85  # 发送按钮的Y坐标（窗口高度的百分比）
    
    # ===========================
    # 【聊天历史配置】
    # ===========================
    # 控制聊天历史记录的存储和使用
    
    # 聊天历史保存目录（通常不需要修改）
    CHAT_HISTORY_DIR = "chat_histories"
    
    # 内存中保存的最大对话轮数
    # 【可选修改】值越大记忆越长，但内存占用越高
    MAX_HISTORY_LENGTH = 20
    
    # 发送给API的最大对话轮数
    # 【可选修改】值越大上下文理解越好，但API调用成本越高
    MAX_API_HISTORY_LENGTH = 10
    
    # 检查重复问题时往前查找的对话轮数
    # 【可选修改】设为0表示禁用重复检查，大于0表示检查最近N轮对话中是否有重复问题
    DUPLICATE_CHECK_HISTORY_LENGTH = 5
    
    @classmethod
    def get_role_system_prompt(cls, role):
        """根据角色获取对应的系统提示词"""
        # 默认的系统提示词
        default_prompt = """
        你是一个微信机器人，要扮演一个特定角色在微信中回复他人
        【角色设定】
        - 友好、专业的助手
        - 回答简洁明了，有礼貌
        - 尽量提供有用的信息

        【强制规则】
        1. 回答简短，避免过长的回复
        2. 使用礼貌的语气
        3. 如果不确定，坦诚表示不知道
        """
        
        # 从ROLES列表中查找匹配的角色
        for role_config in cls.ROLES:
            if role_config["name"] in role or any(alias in role for alias in role_config["aliases"]):
                return role_config["system_prompt"]
        
        # 对于未知角色，使用默认提示词
        return default_prompt


# 确保聊天历史目录存在（通常不需要修改）
os.makedirs(Config.CHAT_HISTORY_DIR, exist_ok=True)

# ===========================
# 【配置检查】
# ===========================
# 检查是否已修改必要的配置项
if __name__ == "__main__":
    print("配置文件检查:")
    if Config.DEEPSEEK_API_KEY and Config.DEEPSEEK_API_KEY != "你的API密钥":
        print("✓ DeepSeek API密钥已设置")
    else:
        print("✗ 请设置DeepSeek API密钥")
    
    if Config.WECHAT_WINDOW_NAME != "微信窗口名称" and Config.WECHAT_WINDOW_NAME != "你的微信窗口名称":
        print("✓ 微信窗口名称已设置")
    else:
        print("✗ 请设置正确的微信窗口名称")
    
    print("\n请确保已根据自己的屏幕分辨率调整聊天输入框和发送按钮的位置")
    print("配置完成后，可以运行 main.py 启动机器人")
