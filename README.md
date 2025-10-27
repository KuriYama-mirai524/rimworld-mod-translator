# RimWorld Mod 名称翻译工具 🤖

一个基于 PySide6 的图形界面工具，用于批量处理 RimWorld 模组的中文名称翻译。使用 AI 技术自动生成模组的中文名称，让中文玩家更容易理解和选择模组。

在[rimsort](https://github.com/RimSort/RimSort)的表现如下：
![alt text](https://youke1.picui.cn/s1/2025/10/19/68f47fc11b4a4.png)


## GUI示例：
![alt text](https://youke1.picui.cn/s1/2025/10/27/68ff500fac89d.png)

## ✨ 功能特性

- **AI 智能翻译**：使用多种 AI 模型（GPT-4o、DeepSeek、GLM、通义千问）自动生成模组中文名称
- **自定义模型配置**：支持在界面中自定义模型名称、API密钥和API地址
- **配置保存/加载**：支持保存和加载模型配置，方便重复使用
- **批量处理**：支持一次性处理整个模组文件夹中的所有模组
- **安全备份**：自动备份原始文件为 `About_old.xml`，确保数据安全
- **文件交换**：一键替换或还原 About.xml 文件
- **进度显示**：实时显示处理进度和详细日志
- **多线程处理**：使用线程池提高处理效率
- **图形界面**：现代化的 PySide6 界面，操作简单直观

## 🚀 快速开始

### 环境要求

- Python 3.7+
- PySide6
- OpenAI Python 客户端
- requests 库
- python-dotenv 库

### 🔐 API密钥配置

**重要安全提醒**：请勿将API密钥直接写入代码中！

#### 方式一：环境变量配置（推荐）
1. **复制环境变量模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**，填入您的API密钥：
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   GLM_API_KEY=your_glm_api_key_here
   QWEN_API_KEY=your_qwen_api_key_here
   ALIYY_API_KEY=your_aliyy_api_key_here
   ```

3. **确保 .env 文件安全**：
   - 已将 `.env` 添加到 `.gitignore`，不会提交到版本库
   - 请勿分享或上传您的 `.env` 文件
   - 定期更换API密钥

#### 方式二：界面配置（新增）
1. **在界面中直接配置**：
   - 在"🤖 AI翻译"选项卡的"AI模型配置"区域
   - 填写模型名称（如：glm、deepseek、qwen、gpt）
   - 填写对应的API密钥
   - 可选：填写自定义API地址

2. **配置保存功能**：
   - 点击"💾 保存配置"可将当前配置保存为JSON文件
   - 点击"📂 加载配置"可从JSON文件加载配置
   - 方便重复使用和分享配置（不含敏感信息时）

### 安装依赖

```bash
pip install PySide6 openai requests python-dotenv
```

### 使用方法

1. **运行主程序**：
   ```bash
   python rename_ui_pyside6.py
   ```

2. **选择模组路径**：点击"浏览"按钮选择 RimWorld 模组文件夹路径（默认路径为 Steam Workshop 目录）

3. **配置 AI 模型**：
   - 在"🤖 AI翻译"选项卡的"AI模型配置"区域
   - 填写模型名称（支持：glm、deepseek、qwen、gpt）
   - 填写对应的 API 密钥
   - 可选：填写自定义 API 地址
   - 可以使用"💾 保存配置"和"📂 加载配置"功能

4. **AI 翻译功能**：
   - 确保已正确配置模型信息
   - 点击"▶️ 开始处理"按钮
   - 工具会自动读取每个模组的 About.xml 文件
   - 使用 AI 生成中文名称并更新文件

5. **文件交换功能**：
   - 切换到"🔄 重命名/交换"选项卡
   - 点击"🔄 替换文件"或"↩️ 还原文件"按钮
   - 可以批量替换或还原 About.xml 文件

## 📁 项目结构

```
f:/mod重命名/
├── rename_ui_pyside6.py    # 主程序 - PySide6 图形界面
├── chat2gpt4o.py          # AI 接口模块 - 支持多种 AI 模型
├── about_rename.py        # 早期版本 - 简单的文件重命名脚本
├── demo_ui.py            # Tkinter 演示版本
├── README.md             # 项目说明文档
└── .gitignore            # Git 忽略文件配置
```

## 🔧 技术实现

### AI 翻译流程

1. **XML 解析**：使用 `xml.etree.ElementTree` 解析 About.xml 文件
2. **内容提取**：提取模组的 `name` 和 `description` 字段
3. **中文检测**：检查名称是否已包含中文字符，避免重复处理
4. **AI 调用**：使用预设的提示词调用 AI 模型生成中文总结
5. **文件更新**：备份原文件并更新新的中文名称

### 支持的 AI 模型

- **GPT-4o**：通过 OpenAI API 调用
- **DeepSeek**：国产 AI 模型，支持中文理解
- **GLM-4**：智谱 AI 的通用语言模型
- **通义千问**：阿里云的大语言模型

### 自定义模型配置

程序现在支持在界面中自定义配置模型参数：

- **模型名称**：支持 glm、deepseek、qwen、gpt
- **API 密钥**：动态设置，支持界面输入
- **API 地址**：可选自定义 API 端点
- **配置持久化**：支持保存和加载配置到 JSON 文件
- **环境变量兼容**：同时支持传统的环境变量配置方式

### 文件交换机制

- **替换文件**：将 `About_old.xml` 替换为 `About.xml`
- **还原文件**：将 `About.xml` 还原为原始的 `About_old.xml`
- **安全检查**：确保文件存在且包含中文才执行操作

## ⚠️ 注意事项

### 🔐 安全提醒
1. **API 密钥安全**：请勿将API密钥硬编码在源代码中，使用环境变量或界面配置
2. **环境变量**：使用 `.env` 文件管理API密钥，确保 `.env` 文件在 `.gitignore` 中
3. **配置文件安全**：保存配置时注意不要包含敏感信息，或确保配置文件安全
4. **定期更新**：建议定期更换API密钥，避免密钥泄露风险
5. **界面输入**：在界面中输入API密钥时，确保周围环境安全

### 🚀 使用提醒
4. **网络连接**：AI 翻译功能需要稳定的网络连接
5. **文件备份**：工具会自动创建备份文件，但建议手动备份重要数据
6. **处理速度**：AI 调用有延迟，大量模组处理可能需要较长时间
7. **Steam 路径**：默认路径为 `E:\steam\steamapps\workshop\content\294100`，请根据实际情况调整

## 🛠️ 开发说明

### 主要类和方法

- `ModProcessorGUI`：主窗口类，负责界面展示和用户交互
- `ModProcessorWorker`：工作线程，处理 AI 翻译任务
- `RenameSwapWorker`：文件交换工作线程
- `chat2gpt4o.py`：封装了多种 AI 模型的调用接口

### 扩展功能

- 可以添加更多的 AI 模型支持
- 支持自定义翻译提示词
- 可以添加多语言支持
- 支持批量导出处理结果

## 📄 许可证

本项目采用 MIT 许可证，详见项目根目录。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📞 联系方式

作者：Daisy  
项目地址：GitHub 仓库（待发布）

---

**免责声明**：本工具仅供学习和个人使用，请遵守相关游戏和平台的使用条款。
