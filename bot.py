#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信机器人主模块
整合各个模块的功能，实现机器人的主要逻辑
注意：仅在微信窗口未最小化时工作
"""

import time
import random
import pyperclip
import pyautogui
from config import Config, logger
from utils.window_manager import WindowManager
from utils.ocr_handler import OCRHandler
from utils.chat_history import ChatHistoryManager
from utils.api_client import APIClient

class WeChatBot:
    def __init__(self):
        """初始化微信机器人"""
        logger.info("正在初始化微信机器人...")
        
        # 初始化各个模块
        self.window_manager = WindowManager()
        self.ocr_handler = OCRHandler()
        self.chat_history_manager = ChatHistoryManager()
        self.api_client = APIClient()
        
        # 上一次识别到的消息，用于避免重复回复
        self.last_message = ""
        
        logger.info(f"当前角色: {self.chat_history_manager.current_role}")
        logger.info(f"当前已加载{len(self.chat_history_manager.chat_history)}轮历史对话")
    
    def detect_trigger(self, texts):
        """检测是否有人@机器人，并识别对应的角色"""
        for text, confidence, position in texts:
            # 检查是否包含任何角色的触发词或其别名
            trigger_found = False
            trigger_word = None
            role_name = None
            
            # 遍历所有角色配置
            for role in Config.ROLES:
                # 检查主触发词
                if role["name"] in text:
                    trigger_found = True
                    trigger_word = role["name"]
                    role_name = role["name"]
                    break
                
                # 检查别名
                for alias in role["aliases"]:
                    if alias in text:
                        logger.info(f"检测到触发词别名: {alias}，将作为 {role['name']} 处理")
                        trigger_found = True
                        trigger_word = alias
                        role_name = role["name"]
                        break
                
                if trigger_found:
                    break
            
            if trigger_found:
                # 如果检测到新角色，切换到该角色
                if role_name != self.chat_history_manager.current_role:
                    self.chat_history_manager.switch_role(role_name)
                
                # 尝试提取发送者名称（通常在@前面）
                sender = "用户"  # 默认发送者名称
                trigger_pos = text.find(trigger_word)
                if trigger_pos > 0:
                    # 尝试从文本中提取发送者名称
                    possible_sender = text[:trigger_pos].strip()
                    if possible_sender:
                        sender = possible_sender
                
                # 提取@后面的内容
                after_trigger = text[text.find(trigger_word) + len(trigger_word):].strip()
                
                # 如果当前文本中没有完整的问题，尝试在下一行找
                if not after_trigger and len(texts) > 1:
                    # 获取当前文本的位置
                    current_pos = position
                    
                    # 查找位置接近的下一行文本
                    for next_text, next_conf, next_pos in texts:
                        if next_text != text and self.ocr_handler.is_next_line(current_pos, next_pos):
                            after_trigger = next_text.strip()
                            break
                
                # 如果找到了触发词和问题
                if after_trigger:
                    # 检查是否与上一次相同，避免重复回复
                    if after_trigger != self.last_message:
                        # 检查问题是否在历史记录中已经出现过
                        if self.chat_history_manager.is_question_already_answered(after_trigger):
                            logger.info(f"问题'{after_trigger}'已在历史记录中出现过，继续检查后续问题")
                            continue  # 继续检查后续问题，而不是直接返回None
                        
                        self.last_message = after_trigger
                        logger.info(f"检测到触发词 {trigger_word}，发送者: {sender}，问题: {after_trigger}")
                        return sender, after_trigger
        
        return None, None
    
    def send_message(self, message):
        """发送消息到微信聊天框"""
        try:
            # 首先复制消息到剪贴板
            logger.info(f"复制消息到剪贴板: {message[:30]}...")
            pyperclip.copy(message)
            time.sleep(random.uniform(0.3, 0.8))  # 随机等待复制完成
            
            # 点击聊天输入框
            if not self.window_manager.click_chat_input():
                return False
            time.sleep(random.uniform(0.2, 0.5))  # 随机等待点击完成
            
            # 粘贴消息
            logger.info("粘贴消息")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(random.uniform(0.8, 1.5))  # 随机等待粘贴完成
            
            # 随机决定是否添加额外延迟
            if random.random() < 0.3:  # 30%概率添加额外延迟
                extra_delay = random.uniform(0.2, 0.5)
                logger.info(f"添加额外思考延迟: {extra_delay:.2f}s")
                time.sleep(extra_delay)
            
            # 按下Enter键发送消息
            logger.info("按下Enter键发送消息")
            pyautogui.press('enter')
            time.sleep(random.uniform(0.3, 0.8))  # 随机等待发送完成
            
            logger.info("消息已发送")
            return True
        
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    def run(self):
        """运行机器人主循环"""
        logger.info("微信机器人已启动，正在监控群聊...")
        logger.info(f"当前角色: {self.chat_history_manager.current_role}")
        
        # 打印所有可用角色
        logger.info("可用角色列表:")
        for role in Config.ROLES:
            logger.info(f"- {role['name']} (别名: {', '.join(role['aliases'])})")
        
        # 记录窗口最初的状态
        initial_minimized = False
        if self.window_manager.wechat_hwnd:
            initial_minimized = self.window_manager.is_window_minimized()
        else:
            # 查找微信窗口
            self.window_manager.find_wechat_window()
            if self.window_manager.wechat_hwnd:
                initial_minimized = self.window_manager.is_window_minimized()
        
        logger.info(f"微信窗口初始状态: {'最小化' if initial_minimized else '正常'}")
        
        try:
            while True:
                # 截取微信窗口（如果窗口最小化则跳过截图）
                screenshot = self.window_manager.capture_wechat_screen()
                
                if screenshot is not None:
                    # 识别文字
                    texts = self.ocr_handler.recognize_text(screenshot)
                    
                    # 检查是否识别到微信窗口名称
                    if not self.ocr_handler.detect_wechat_window_name(texts):
                        logger.warning("未检测到微信窗口名称，可能是微信窗口被其他窗口遮挡，跳过后续处理")
                        time.sleep(Config.SCREENSHOT_INTERVAL)
                        continue
                    
                    # 检测触发词
                    sender, question = self.detect_trigger(texts)
                    
                    if sender and question:
                        logger.info("检测到需要回复的消息，准备回复...")
                        
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
                        self.send_message(response)
                
                # 等待一段时间再次截图
                time.sleep(Config.SCREENSHOT_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("收到中断信号，微信机器人已停止")
            # 保存当前对话历史
            self.chat_history_manager.save_chat_history()
        except Exception as e:
            logger.error(f"运行出错: {e}")
            # 保存当前对话历史
            self.chat_history_manager.save_chat_history()
