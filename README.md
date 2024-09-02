# 吐槽生成器

这是一个基于Python的GUI应用程序，使用`Tkinter`库创建一个界面，可以截图屏幕的部分区域，并通过调用`OpenAI GPT-4 API`生成幽默的评论。该应用程序还可以根据所有生成的评论生成一个总结。

## 主要功能

- 选择屏幕区域截图
- 自动定时截图并生成评论
- 手动截图并生成评论
- 汇总所有生成的评论
- 设置生成评论的频率

## 依赖

- Python 3.x
- Tkinter
- OpenAI
- Pillow
- pyautogui
- mss
- Quartz (仅限macOS)

## 安装

1. 克隆或下载本仓库。
2. 安装所需的Python库：

```bash
pip install openai Pillow pyautogui mss
```

3.	如果你在macOS上运行，还需要Quartz库：
```bash
pip install pyobjc-framework-Quartz
```

## 使用方法

1.	设置你的OpenAI API密钥：

在脚本中找到以下行，并将YOUR_API_KEY替换为你的实际API密钥：openai.api_key = 'YOUR_API_KEY'

2.	运行脚本： python script_name.py

	3.	使用GUI：

	•	选择截图区域: 单击选择截图区域按钮，然后使用鼠标选择屏幕上的区域。
	•	开始自动吐槽: 单击开始自动吐槽按钮以设定的时间间隔自动生成评论。
	•	停止自动吐槽: 单击停止自动吐槽按钮以停止自动评论生成。
	•	手动吐槽: 单击手动吐槽按钮立即生成一次评论。
	•	显示汇总: 单击显示汇总按钮生成和显示所有吐槽评论的幽默总结。
	•	设置频率: 更改输入框中的数字来设置自动吐槽的频率（以秒为单位），然后单击更新频率按钮。

注意事项

	•	确保你在使用前已经正确设置了OpenAI API密钥。
	•	使用本程序时请确保你的网络连接正常，因为生成评论需要调用OpenAI的API。
	•	本程序在macOS上运行，如果你在其他平台上运行，请确认相关库的兼容性。


 许可证

该项目基于MIT许可。请参阅LICENSE文件了解更多详情。
