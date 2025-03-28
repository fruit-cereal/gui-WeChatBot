#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OCR处理模块
处理图像文字识别相关功能
"""

import logging
from paddleocr import PaddleOCR
from config import Config, logger

class OCRHandler:
    def __init__(self):
        """初始化OCR处理器"""
        logger.info("正在初始化PaddleOCR引擎...")
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False)
        # 存储最近识别的文本结果，用于推断消息发送者
        self.last_recognized_texts = []
        logger.info("PaddleOCR引擎初始化完成")
        
    def detect_wechat_window_name(self, texts):
        """检测OCR识别结果中是否包含微信窗口名称或其别名"""
        for text, confidence, _ in texts:
            # 检查主窗口名称
            if Config.WECHAT_WINDOW_NAME in text:
                logger.info(f"检测到微信窗口名称：'{Config.WECHAT_WINDOW_NAME}'")
                return True
            
            # 检查别名
            for alias in Config.WECHAT_WINDOW_NAME_ALIASES:
                if alias in text:
                    logger.info(f"检测到微信窗口名称别名：'{alias}'")
                    return True
        
        logger.warning(f"OCR识别结果中未包含微信窗口名称或其别名，可能是微信窗口被其他窗口遮挡")
        return False
    
    def recognize_text(self, image):
        """使用PaddleOCR识别图像中的文字"""
        if image is None:
            return []
        
        try:
            result = self.ocr.ocr(image, cls=True)
            if result is None or len(result) == 0:
                return []
            
            # PaddleOCR返回格式: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], [text, confidence]]
            texts = []
            
            # 打印所有识别到的文本和置信度，无论置信度高低
            logger.info("OCR识别结果:")
            for line in result[0]:
                text, confidence = line[1]
                logger.info(f"文本: '{text}', 置信度: {confidence:.4f}")
                
                if confidence >= Config.OCR_CONFIDENCE_THRESHOLD:
                    texts.append((text, confidence, line[0]))  # 文本、置信度、位置
            
            # 保存当前识别结果，用于下次推断发送者
            self.last_recognized_texts = texts.copy()
            
            return texts
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return []
    
    def is_next_line(self, current_pos, next_pos):
        """判断next_pos是否是current_pos的下一行"""
        # 获取当前行的y坐标范围
        current_y_min = min(p[1] for p in current_pos)
        current_y_max = max(p[1] for p in current_pos)
        
        # 获取下一行的y坐标范围
        next_y_min = min(p[1] for p in next_pos)
        
        # 如果下一行的y坐标大于当前行的最大y坐标，则认为是下一行
        return next_y_min > current_y_max
    
    def infer_sender_name(self):
        """根据上一次OCR识别结果推断可能的发送者名称"""
        if not self.last_recognized_texts:
            logger.info("没有上一次OCR识别结果，无法推断发送者名称")
            return None
        
        # 选择上一次识别结果中的第一项作为可能的发送者名称
        # 通常，微信中消息的格式是：[发送者名称] [消息内容]
        # 所以最近识别结果中可能包含发送者名称
        possible_sender = self.last_recognized_texts[0][0]
        logger.info(f"从上一次OCR识别结果推断可能的发送者名称: '{possible_sender}'")
        
        # 验证推断的名称是否在配置的用户名列表中
        if hasattr(Config, 'USER_NAMES') and Config.USER_NAMES:
            # 检查主名称
            for user in Config.USER_NAMES:
                if possible_sender == user['name']:
                    logger.info(f"推断的发送者名称 '{possible_sender}' 匹配用户列表中的主名称")
                    return possible_sender
                
                # 检查别名
                if 'aliases' in user and user['aliases']:
                    for alias in user['aliases']:
                        if possible_sender == alias:
                            logger.info(f"推断的发送者名称 '{possible_sender}' 匹配用户 '{user['name']}' 的别名")
                            return user['name']  # 返回主名称而不是别名
        
        logger.info(f"推断的发送者名称 '{possible_sender}' 不在配置的用户名列表中，将使用默认用户名")
        return None  # 如果没有匹配，返回None
