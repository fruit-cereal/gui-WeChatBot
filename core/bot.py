#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信机器人核心模块
整合各个模块的功能，实现机器人的主要逻辑
"""

import time
from config import Config, logger
from utils.window_manager import WindowManager
from utils.ocr_handler import OCRHandler
from utils.chat_history import ChatHistoryManager
from utils.api_client import APIClient
from core.message_detector import MessageDetector
from core.message_sender import MessageSender

class WeChatBot:
    def __init__(self):
        """初始化微信机器人"""
        # 这些初始化信息需要保存到文件
        logger.info("正在初始化微信机器人...", extra={'save_to_file': True})
        
        # 初始化各个模块
        self.window_manager = WindowManager()
        self.ocr_handler = OCRHandler()
        self.chat_history_manager = ChatHistoryManager()
        self.api_client = APIClient()
        
        # 初始化消息检测和发送组件
        self.message_detector = MessageDetector(self.ocr_handler, self.chat_history_manager)
        self.message_sender = MessageSender(self.window_manager)
        
        # 这些初始化信息需要保存到文件
        logger.info(f"当前角色: {self.chat_history_manager.current_role}", extra={'save_to_file': True})
        logger.info(f"当前已加载{len(self.chat_history_manager.chat_history)}轮历史对话", extra={'save_to_file': True})
    
    def run(self):
        """运行机器人主循环"""
        # 这些启动信息需要保存到文件
        logger.info("微信机器人已启动，正在监控群聊...", extra={'save_to_file': True})
        logger.info(f"当前角色: {self.chat_history_manager.current_role}", extra={'save_to_file': True})
        
        # 打印所有可用角色 (也保存到文件)
        logger.info("可用角色列表:", extra={'save_to_file': True})
        for role in Config.ROLES:
            logger.info(f"- {role['name']} (别名: {', '.join(role['aliases'])})", extra={'save_to_file': True})
        
        # 记录窗口最初的状态
        initial_minimized = False
        if self.window_manager.wechat_hwnd:
            initial_minimized = self.window_manager.is_window_minimized()
        else:
            # 查找微信窗口
            self.window_manager.find_wechat_window()
            if self.window_manager.wechat_hwnd:
                initial_minimized = self.window_manager.is_window_minimized()
        
        # 窗口状态信息保存到文件
        logger.info(f"微信窗口初始状态: {'最小化' if initial_minimized else '正常'}", extra={'save_to_file': True})
        
        try:
            while True:
                # 截取微信窗口（如果窗口最小化则跳过截图）
                screenshot = self.window_manager.capture_wechat_screen()
                
                if screenshot is not None:
                    # 识别文字 (置信度打印已在 ocr_handler.py 内部完成)
                    texts = self.ocr_handler.recognize_text(screenshot)

                    # 检查是否识别到微信窗口名称
                    if not self.ocr_handler.detect_wechat_window_name(texts):
                        time.sleep(Config.SCREENSHOT_INTERVAL)
                        continue
                    
                    # 检测触发词
                    sender, question = self.message_detector.detect_trigger(texts)
                    
                    if sender and question:
                        # 检测到消息的提示信息保存到文件
                        logger.info("检测到需要回复的消息，准备回复...", extra={'save_to_file': True})
                        
                        # 生成回复
                        response = self.api_client.generate_response(
                            sender, 
                            question, 
                            self.chat_history_manager.get_recent_history(),
                            self.chat_history_manager.current_role
                        )
                        
                        # 添加到聊天历史
                        self.chat_history_manager.add_chat(sender, question, response)
                        
                        # 发送回复
                        send_success = self.message_sender.send_message(response)
                        
                        # 在发送成功时将OCR结果写入日志文件
                        if send_success:
                            # 仅在发送成功时，将本次OCR详细结果记录到日志文件
                            if texts:
                                logger.info("---------- 本次成功回复对应的OCR识别详情 ----------", extra={'save_to_file': True})
                                for text, confidence, position in texts:
                                    # 格式化包含文本、置信度和位置的日志条目
                                    log_entry = f"文本: '{text}', 置信度: {confidence:.4f}, 位置: {position}"
                                    logger.info(log_entry, extra={'save_to_file': True})
                                logger.info("-----------------------------------------------------------------", extra={'save_to_file': True})
                            else:
                                logger.info("本次OCR未识别到有效文本", extra={'save_to_file': True})

                # 等待一段时间再次截图
                time.sleep(Config.SCREENSHOT_INTERVAL)
        
        except KeyboardInterrupt:
            # 停止信息保存到文件
            logger.info("收到中断信号，微信机器人已停止", extra={'save_to_file': True})
            # 保存当前对话历史
            self.chat_history_manager.save_chat_history() # 这个函数内部的日志也应该考虑是否加标记
        except Exception as e:
            # 错误信息保存到文件
            logger.error(f"运行出错: {e}", extra={'save_to_file': True})
            # 保存当前对话历史
            self.chat_history_manager.save_chat_history() # 这个函数内部的日志也应该考虑是否加标记
