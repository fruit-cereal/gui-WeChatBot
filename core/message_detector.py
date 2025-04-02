#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
消息检测模块
负责检测和识别微信消息中的触发词和问题内容
"""

from config import Config, logger

class MessageDetector:
    def __init__(self, ocr_handler, chat_history_manager):
        """初始化消息检测器"""
        self.ocr_handler = ocr_handler
        self.chat_history_manager = chat_history_manager
        # 上一次识别到的消息，用于避免重复回复
        self.last_message = ""
    
    def detect_trigger(self, texts):
        """检测是否有人@机器人，并识别对应的角色
        
        Args:
            texts: OCR识别到的文本列表，每项包含(文本内容, 置信度, 位置)
            
        Returns:
            tuple: (发送者, 问题内容) 如果没有检测到触发词或问题则返回(None, None)
        """
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
                        logger.info(f"检测到触发词别名: {alias}，将作为 {role['name']} 处理", extra={'save_to_file': True})
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
                
                # 尝试从上一条OCR识别结果推断发送者名称
                inferred_sender = self.ocr_handler.infer_sender_name()
                
                # 如果能够从上一条OCR结果中推断出发送者名称，则使用它
                if inferred_sender:
                    sender = inferred_sender
                else:
                    # 如果无法推断，尝试从当前文本中提取发送者名称
                    sender = Config.DEFAULT_USER_NAME  # 默认发送者名称
                    trigger_pos = text.find(trigger_word)
                    if trigger_pos > 0:
                        # 尝试从文本中提取发送者名称
                        possible_sender = text[:trigger_pos].strip()
                        if possible_sender:
                            # 验证提取的名称是否在配置的用户名列表中
                            for user in Config.USER_NAMES:
                                if possible_sender == user['name'] or (
                                    'aliases' in user and possible_sender in user['aliases']):
                                    sender = user['name']
                                    break
                
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
                    logger.info(f"检测到触发词 {trigger_word}，发送者: {sender}，问题: {after_trigger}", extra={'save_to_file': True})
                    # 检查是否与上一次相同，避免重复回复
                    if after_trigger != self.last_message:
                        # 检查问题是否在历史记录中已经出现过（考虑发送者）
                        if self.chat_history_manager.is_question_already_answered(after_trigger, sender):
                            logger.info(f"当前问题'{after_trigger}'重复问题检查未通过，继续检查后续问题", extra={'save_to_file': True})
                            continue  # 继续检查后续问题，而不是直接返回None
                        
                        self.last_message = after_trigger
                        return sender, after_trigger
        
        return None, None
