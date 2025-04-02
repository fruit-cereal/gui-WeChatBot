# 微信智能聊天机器人 (gui-WeChatBot)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-支持-brightgreen)](https://github.com/PaddlePaddle/PaddleOCR)
[![DeepSeek API](https://img.shields.io/badge/DeepSeek%20API-驱动-orange)](https://deepseek.com/)

## 📝 项目简介

这是一个基于屏幕识别技术的微信聊天机器人，利用 **PaddleOCR** 识别屏幕上的文字内容，通过 **DeepSeek API** 生成智能回复。机器人能够自动识别微信群聊中有人 `@` 自己的消息并进行回复，支持多种角色切换，让回复更有趣、更贴合场景。

**核心特性**：

- 🤖 **多角色扮演**：支持多种预设角色，每个角色都有独特的人格特质和语言风格
- 🔍 **自动识别消息**：使用OCR技术自动识别屏幕上的@消息并提取问题内容
- 💬 **智能回复**：调用DeepSeek API生成符合角色设定的回复
- 📚 **对话历史管理**：自动保存每个角色的聊天记录，提供上下文连贯的对话体验
- 🔄 **自动角色切换**：根据@后使用的名称自动切换角色

> **重要提示**：此机器人需要微信窗口保持在前台（未最小化）才能正常工作。

---

## 🏗️ 项目结构及功能详解

### 核心文件

- **`main.py`** - 程序入口
  - 导入WeChatBot类并创建实例
  - 启动机器人运行流程

### 核心模块 (`core/`)

- **`core/bot.py`** - 机器人核心逻辑

  - 实现WeChatBot类，整合各模块功能
  - 管理窗口状态与主循环
  - 协调消息检测、生成回复和发送消息的流程
- **`core/message_detector.py`** - 消息检测模块

  - 检测OCR识别结果中的触发词
  - 提取问题内容和发送者信息
  - 切换到对应的角色
  - 防止重复回复相同问题
- **`core/message_sender.py`** - 消息发送模块

  - 通过模拟键盘和鼠标操作发送消息
  - 处理消息粘贴和发送操作
  - 添加随机延迟模拟真人行为

### 配置模块 (`config/`)

- **`config/__init__.py`** - 配置模块初始化

  - 导入和导出logger和Config类
  - 提供统一的配置访问接口
- **`config/settings.py`** - 应用程序设置

  - 定义Config类，统一管理全局配置
  - 加载角色配置与系统提示词
  - 设置API参数、窗口参数、截图区域
- **`config/logger.py`** - 日志配置

  - 配置日志记录器
  - 实现自定义日志过滤器
  - 设置日志格式和输出

> **注意**：项目提供了config_example文件夹作为配置模板。使用时，请复制config_example文件夹为config文件夹，并按照说明修改必要的配置项。

### 工具模块 (`utils/`)

- **`api_client.py`** - API通信模块

  - 调用DeepSeek API生成回复
  - 处理API请求与响应
  - 异常处理与错误重试
- **`chat_history.py`** - 对话历史管理

  - 保存和加载不同角色的对话历史
  - 支持角色间的切换，保持上下文连贯
  - 实现问题相似度检测，避免回答重复问题
  - 自动将对话保存为JSON文件
- **`ocr_handler.py`** - 文字识别处理

  - 使用PaddleOCR识别屏幕文字
  - 分析文本位置关系，判断文本行之间的上下文联系
  - 根据置信度过滤识别结果
- **`window_manager.py`** - 窗口管理

  - 查找和管理微信窗口
  - 处理窗口截图与状态检测
  - 提供窗口交互操作（点击、输入等）

### 角色管理 (`roles/`)

- **`__init__.py`** - 角色配置加载

  - 自动加载所有角色配置文件
  - 验证角色配置的有效性
- **`manager.py`** - 角色管理工具

  - 提供交互式命令行界面
  - 管理角色的创建、编辑和删除
  - 可视化展示角色配置
- **`*.json`** - 角色配置文件

  - 定义角色名称、别名和系统提示词
  - 设置角色的行为模式和语言风格

### 对话历史存储 (`chat_histories/`)

- 按角色分别保存对话历史记录
- 使用JSON格式存储发送者、问题、回复和时间戳

---

## ✨ 功能特点

### 1. 多角色人格系统

机器人支持多种预设角色，每个角色都有独特的语言风格和回复方式。用户可以通过在微信中使用不同的@名称来触发不同的角色。

**内置角色示例**：

- 👨‍🍳 厨神bot - 专业的烹饪顾问
- 🏃 健身教练bot - 提供健身建议
- 🐱 猫娘bot - 可爱的猫娘风格
- 🏀 科比bot - 模仿科比风格的回复
- 📝 专业助手bot - 正式、专业的回答风格
- 更多角色可通过roles管理工具添加...

角色切换是智能的 - 机器人会自动识别@的名称，并切换到相应的角色。每个角色都维护独立的聊天历史，保证对话的连贯性。

### 2. 智能消息识别与处理

- **OCR文本识别**：使用PaddleOCR识别屏幕上的文字
- **@消息检测**：自动识别包含@机器人名称的消息
- **用户名识别**：基于OCR识别结果智能推断消息发送者的名称
- **问题提取**：智能提取@之后的文本作为问题内容
- **上下文理解**：分析文本的位置关系，智能拼接多行内容
- **状态检测**：自动检测微信窗口的状态，仅在窗口可见时工作

### 3. 高质量AI回复

- **角色扮演**：根据当前角色的设定生成符合人格的回复
- **上下文感知**：考虑历史对话内容，生成连贯的回复
- **智能防重**：针对同一用户的重复问题避免重复回答，不同用户可获得独立回复
- **自动分段**：对于长回复，自动分段发送，避免消息过长

### 4. 高效的对话历史管理

- **角色隔离**：每个角色独立保存对话历史
- **智能上下文**：为API提供适量的历史对话作为上下文
- **自动持久化**：定期将对话历史保存到本地文件
- **内存优化**：限制内存中保存的对话轮数，避免内存占用过大

---

## 🚀 使用指南

### 环境准备

1. **安装Python环境**

   - 需要Python 3.8或更高版本
   - 推荐使用虚拟环境隔离依赖
2. **安装PaddleOCR**

   - 按照[PaddleOCR官方文档](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md)安装
3. **获取DeepSeek API密钥**

   - 注册[DeepSeek开发者账户](https://deepseek.com/)
   - 创建API密钥并保存

### 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/your-username/gui-WeChatBot.git
   cd gui-WeChatBot
   ```
2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```
3. **配置机器人**

   - 复制示例配置文件夹为实际配置文件夹：
     ```bash
     cp -r config_example config
     ```
   - 设置DeepSeek API密钥环境变量：
     - Windows: `set DEEPSEEK_API_KEY=your_api_key_here`
     - Linux/Mac: `export DEEPSEEK_API_KEY=your_api_key_here`
   - 或将密钥直接添加到配置文件中：
     - 打开 `config/settings.py`，找到 `DEEPSEEK_API_KEY`设置项
     - 将其修改为：`DEEPSEEK_API_KEY = "your_api_key_here"`
4. **调整配置参数**

   - 打开 `config/settings.py`，根据需要调整如下参数：
     - `WECHAT_WINDOW_NAME`：微信窗口标题（必须修改为你的微信群名称）
     - `WECHAT_WINDOW_NAME_ALIASES`：微信窗口标题的可能OCR识别变体
     - `CHAT_INPUT_BOX_RELATIVE_X/Y`：聊天输入框的相对位置（必须根据你的屏幕分辨率调整）
     - `SEND_BUTTON_RELATIVE_X/Y`：发送按钮的相对位置
     - `SCREENSHOT_INTERVAL`：截图间隔时间
   - 配置用户名识别（推荐）：
     - 在 `USER_NAMES`列表中添加群成员的名称和可能的OCR识别变体

### 首次运行

1. **启动微信并登录**

   - 确保微信处于登录状态
   - 调整微信窗口到合适位置和大小
2. **运行机器人**

   ```bash
   python main.py
   ```
3. **测试机器人**

   - 在微信群中@机器人名称，例如：`@专业助手bot 今天天气怎么样？`
   - 等待机器人自动回复

### 管理角色

1. **查看现有角色**

   ```bash
   python roles/manager.py list
   ```
2. **添加新角色**

   ```bash
   python roles/manager.py add
   ```
3. **编辑现有角色**

   ```bash
   python roles/manager.py edit
   ```

### 常见问题排查

- **无法识别@消息**：检查OCR配置和微信窗口位置
- **回复不发送**：检查聊天输入框位置配置
- **角色不切换**：确认角色名称和别名配置正确
- **API错误**：检查API密钥是否正确设置

---

## 🛠️ 高级配置

### 自定义角色模板

创建新角色时，你可以参考以下模板：

```json
{
  "name": "@你的角色名",
  "aliases": ["@别名1", "@别名2"],
  "system_prompt": "详细的角色设定和行为指导..."
}
```

### 窗口定位

如果窗口截图或点击位置不准确，请调整 `config/settings.py`中的窗口位置参数：

```python
CHAT_INPUT_BOX_RELATIVE_X = 0.5  # 聊天输入框的X坐标（窗口宽度的百分比）
CHAT_INPUT_BOX_RELATIVE_Y = 0.88  # 聊天输入框的Y坐标（窗口高度的百分比）
```

---

## 📝 注意事项

1. **窗口位置**：首次使用或更换显示器/分辨率后，可能需要重新调整 `config/settings.py`中的窗口位置参数
2. **资源占用**：OCR识别会消耗一定的系统资源，请合理设置截图间隔
3. **隐私安全**：机器人会读取并处理屏幕上的文字内容，请确保在使用时不显示敏感信息
4. **错误处理**：出现问题时，请查看日志文件 `log/wechat_bot.log`获取详细错误信息
5. **适用范围**：此机器人仅在微信PC客户端上工作，不适用于移动设备或网页版微信
