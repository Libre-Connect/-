import tkinter as tk
from tkinter import scrolledtext
import openai
import pyautogui
from PIL import Image, ImageTk, ImageGrab
import io
import os
import base64
import mss
import mss.tools

import Quartz

def get_scale_factor():
    main_monitor = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
    scale_factor = Quartz.CGDisplayScreenSize(Quartz.CGMainDisplayID()).width / main_monitor.size.width
    return scale_factor

scale_factor = get_scale_factor()


# 设置OpenAI API密钥
openai.api_key = '请替换为你的openai api'  # 请替换为您的实际API密钥

region = None
running = False
all_comments = []
interval = 5
root = None
screenshot_image = None
screen_width, screen_height = pyautogui.size()  # 获取屏幕分辨率
def select_area():
    global region, root, screen_width, screen_height

    print("正在截取整个屏幕...")

    # 截取整个屏幕
    screenshot = pyautogui.screenshot()

    # 创建一个新的窗口显示截图
    selection_window = tk.Toplevel(root)
    selection_window.title("选择截图区域")

    # 调整截图大小以适应屏幕分辨率
    screenshot_resized = screenshot.resize((screen_width, screen_height), Image.LANCZOS)
    screenshot_image = ImageTk.PhotoImage(screenshot_resized)

    canvas = tk.Canvas(selection_window, width=screen_width, height=screen_height, cursor="cross")
    canvas.pack()
    canvas.create_image(0, 0, image=screenshot_image, anchor=tk.NW)

    start_x = start_y = end_x = end_y = 0
    selection_rectangle = None

    def on_button_press(event):
        nonlocal start_x, start_y, selection_rectangle
        start_x, start_y = event.x, event.y
        if selection_rectangle:
            canvas.delete(selection_rectangle)
        selection_rectangle = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_move_press(event):
        nonlocal end_x, end_y, selection_rectangle
        end_x, end_y = event.x, event.y
        canvas.coords(selection_rectangle, start_x, start_y, end_x, end_y)

    def on_button_release(event):
        nonlocal start_x, start_y, end_x, end_y
        global region
        end_x, end_y = event.x, event.y

        # 计算选择区域的实际坐标
        x1 = int(min(start_x, end_x))
        y1 = int(min(start_y, end_y))
        x2 = int(max(start_x, end_x))
        y2 = int(max(start_y, end_y))
        region = (x1, y1, x2, y2)
        print(f"已选择区域：{region}")
        selection_window.destroy()

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)

    # 等待窗口关闭
    selection_window.wait_window()

def capture_screenshot():
    global region
    if region:
        x1, y1, x2, y2 = region
        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        return screenshot
    else:
        print("请先选择区域")
        return None
def upload_image_and_get_url(image):
    """
    将图像保存到本地并获取文件路径，模拟URL上传。
    """
    image_path = os.path.abspath("temp_image.png")
    image.save(image_path)  # 保存图像到本地路径
    return image_path  # 返回本地文件路径


def generate_comment(image):
    """
    使用OpenAI GPT-4 API生成吐槽评论
    """
    try:
        # 上传图片并获取URL
        image_path = upload_image_and_get_url(image)

        system_prompt = (
            "你是一个幽默的评论员。你将根据图像内容用中文进行讽刺和幽默的评论，避免分条列举评论，而是类似于这样：“希望它不会像你的一些火箭那样在发射台上爆炸。你的推特就像是一辆 Cybertruck 原型：充满了破碎的承诺和不该有的锋利边缘。”"
        )

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": ""},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ]
                }
            ],
            max_tokens=1280
        )

        comment = response['choices'][0]['message']['content'].strip()
        return comment

    except Exception as e:
        return f"Error generating comment: {e}"


def add_comment_to_box():
    """
    获取吐槽结果并添加到消息框
    """
    global running
    if running:
        screenshot = capture_screenshot()
        if screenshot:
            comment = generate_comment(screenshot)
            all_comments.append(comment)
            comment_box.insert(tk.END, comment + "\n")
            comment_box.yview(tk.END)  # 自动滚动到底部

        # 再次调用自身，每隔interval秒
        root.after(interval * 1000, add_comment_to_box)


def start_comments():
    """
    开始自动生成吐槽
    """
    global running
    running = True
    add_comment_to_box()


def stop_comments():
    """
    停止自动生成吐槽
    """
    global running
    running = False


def manual_comment():
    """
    手动生成一次吐槽
    """
    screenshot = capture_screenshot()
    if screenshot:
        comment = generate_comment(screenshot)
        all_comments.append(comment)
        comment_box.insert(tk.END, comment + "\n")
        comment_box.yview(tk.END)


summary_system_prompt = (
    "你是一个幽默的评论员。你将根据之前生成的一系列吐槽评论进行幽默讽刺的总结，"
)


def show_summary():
    """
    使用GPT-4生成所有吐槽结果的汇总
    """
    global all_comments

    if not all_comments:
        summary_box.delete(1.0, tk.END)
        summary_box.insert(tk.END, "还没有生成任何吐槽评论。")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # 或者使用 "gpt-3.5-turbo"，取决于您的需求和API访问权限
            messages=[
                {"role": "system", "content": summary_system_prompt},
                {"role": "user", "content": "请根据以下吐槽评论生成一个幽默讽刺的总结：\n\n" + "\n".join(all_comments)}
            ],
            max_tokens=1280
        )

        summary = response['choices'][0]['message']['content'].strip()
        summary_box.delete(1.0, tk.END)
        summary_box.insert(tk.END, summary)

    except Exception as e:
        error_message = f"生成汇总时出错: {str(e)}"
        summary_box.delete(1.0, tk.END)
        summary_box.insert(tk.END, error_message)


def update_interval():
    """
    更新吐槽频率
    """
    global interval
    try:
        interval = int(interval_entry.get())
    except ValueError:
        interval = 5  # 默认5秒


# 初始化Tkinter窗口
root = tk.Tk()
root.title("吐槽生成器")

# 消息框（滚动文本框）
comment_box = scrolledtext.ScrolledText(root, width=50, height=10, wrap=tk.WORD)
comment_box.pack(pady=10)

# 选择区域按钮
select_area_button = tk.Button(root, text="选择截图区域", command=select_area)
select_area_button.pack(pady=5)

# 开始按钮
start_button = tk.Button(root, text="开始自动吐槽", command=start_comments)
start_button.pack(pady=5)

# 停止按钮
stop_button = tk.Button(root, text="停止自动吐槽", command=stop_comments)
stop_button.pack(pady=5)

# 手动吐槽按钮
manual_button = tk.Button(root, text="手动吐槽", command=manual_comment)
manual_button.pack(pady=5)

# 汇总按钮
summary_button = tk.Button(root, text="显示汇总", command=show_summary)
summary_button.pack(pady=5)

# 汇总框（滚动文本框）
summary_box = scrolledtext.ScrolledText(root, width=50, height=10, wrap=tk.WORD)
summary_box.pack(pady=10)

# 设置频率标签和输入框
interval_label = tk.Label(root, text="设置自动吐槽频率（秒）：")
interval_label.pack(pady=5)
interval_entry = tk.Entry(root)
interval_entry.insert(0, "5")
interval_entry.pack(pady=5)

# 更新频率按钮
update_button = tk.Button(root, text="更新频率", command=update_interval)
update_button.pack(pady=5)

# 运行Tkinter主循环
root.mainloop()
