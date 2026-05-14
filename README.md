# 学术英文翻译器

一款基于Python和PyQt5构建的桌面浮动翻译工具。该工具专注于中英文学术或专业文本的翻译，并通过兼容OpenAI的聊天补全格式调用DeepSeek API。

## 功能特性

- 集成DeepSeek API，配备学术翻译系统提示词
- 自动识别中英文语言方向
- 支持剪贴板粘贴功能

## 快速开始

1. 配置本地**Python环境或虚拟环境**。

   前往Python官方网站：`https://www.python.org/`

   选择**3.12**版本并下载安装。

2. 下载源代码

3. 安装依赖项：

   在项目目录下运行以下指令

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 翻译模型配置

以Deepseek为例，进入Deepseek开放平台：`https://platform.deepseek.com/usage` 

充值额度，获取 **api key**（sk-xxx...)

**api url**	`https://api.deepseek.com/chat/completions`

选择模型，建议使用最新发布的deepseek v4模型：

**model**

- `deepseek-v4-flash`
- `deepseek-v4-pro`

如需使用其他兼容模型，可在设置对话框中更改模型参数。

打开**Settings**，将以上参数分别填写到**API Key ，API URL， model**

示例：

> | API Key     | `sk-xxxxxx....`                             |
> | ----------- | ------------------------------------------- |
> | **API URL** | `https://api.deepseek.com/chat/completions` |
> | **model**   | `deepseek-v4-flash`                         |



## **注意事项**

- 全局热键格式采用`pynput`语法，例如`<ctrl>+t`。

- 部分操作系统可能需要为全局热键授予辅助功能权限。

- 翻译历史记录存储于`history.json`文件中。

- 应用程序日志存储于`translator.log`文件中。

  



