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
