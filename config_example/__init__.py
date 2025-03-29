#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块
包含应用程序所需的所有配置项和日志设置
"""

from config.logger import logger
from config.settings import Config

__all__ = ['Config', 'logger']
