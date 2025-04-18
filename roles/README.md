# 角色管理系统

这个目录包含了微信机器人的角色配置文件和管理工具。每个角色都有自己的JSON配置文件，包含触发词、别名和系统提示词。

## 角色配置文件格式

每个角色配置文件都是一个JSON文件，包含以下字段：

```json
{
  "name": "@角色名bot",  // 主触发词
  "aliases": ["@角色1名bot", "@角色l名bot"],  // 别名（OCR可能错误识别的变体）
  "system_prompt": "角色的系统提示词，定义了角色的行为和回复风格"
}
```

## 使用角色管理工具

我们提供了一个命令行工具来管理角色配置，可以轻松地添加、编辑和删除角色。

### 列出所有角色

```bash
python roles/manager.py list
```

这将显示所有可用的角色，包括它们的名称、别名和配置文件名。

### 添加新角色

```bash
python roles/manager.py add
```

这将启动一个交互式会话，引导您创建新的角色配置：
1. 输入角色的主触发词（例如：`@新角色bot`）
2. 输入角色的别名，多个别名用逗号分隔（例如：`@新1角色bot,@新l角色bot`）
3. 输入角色的系统提示词（定义角色的行为和回复风格）
4. 完成后，配置将保存到一个新的JSON文件中

### 编辑现有角色

```bash
python roles/manager.py edit
```

这将显示所有可用的角色，并允许您选择要编辑的角色。然后，您可以修改角色的名称、别名和系统提示词。

### 删除角色

```bash
python roles/manager.py delete
```

这将显示所有可用的角色，并允许您选择要删除的角色。删除前会要求确认。

## 手动编辑角色配置

如果您熟悉JSON格式，也可以直接编辑角色配置文件。只需确保遵循正确的格式，并包含所有必需的字段（name、aliases和system_prompt）。

## 重启机器人

在添加、编辑或删除角色后，需要重启机器人以加载新的配置。
