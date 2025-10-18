import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import xml.etree.ElementTree as ET

def rename_files_in_directories(base_directory):
    try:
        about_path = os.path.join(base_directory, 'About.xml')
        about_old_path = os.path.join(base_directory, 'About_old.xml')

        if os.path.exists(about_old_path):
            tree = ET.parse(about_path)
            root = tree.getroot()
            name_element = root.find('name')

            if name_element is not None and not any('\u4e00' <= char <= '\u9fff' for char in name_element.text):
                os.rename(about_path, os.path.join(base_directory, 'About_temp.xml'))
                os.rename(about_old_path, about_path)
                os.rename(os.path.join(base_directory, 'About_temp.xml'), about_old_path)
    except Exception as e:
        print(f"处理目录 {base_directory} 时出错: {e}")

def swap_about_files(base_directory):
    try:
        about = os.path.join(base_directory, 'About.xml')
        about_old = os.path.join(base_directory, 'About_old.xml')
        
        if os.path.exists(about_old):
            tree = ET.parse(about)
            root = tree.getroot()
            name_element = root.find('name')

            if name_element is not None and not any('\u4e00' <= char <= '\u9fff' for char in name_element.text):
                pass
            else:
                if os.path.exists(about):
                    os.rename(about, os.path.join(base_directory, 'About_temp.xml'))
                os.rename(about_old, about)
                os.rename(os.path.join(base_directory, 'About_temp.xml'), about_old)
    except Exception as e:
        print(f"处理目录 {base_directory} 时出错: {e}")

def get_directory_names(path):
    try:
        return [os.path.join(path, name) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {e}")
        return []

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_var.set(directory)

def process_directories(action):
    base_directory = directory_var.get()
    if not base_directory:
        messagebox.showwarning("警告", "请选择一个文件路径")
        return

    all_directories = get_directory_names(base_directory)
    progress_var.set(0)
    progress_bar['maximum'] = len(all_directories)

    for i, directory in enumerate(all_directories):
        about_directory = os.path.join(directory, 'About')
        if action == 'rename':
            rename_files_in_directories(about_directory)
        elif action == 'swap':
            swap_about_files(about_directory)

        progress_var.set(i + 1)
        root.update_idletasks()

    messagebox.showinfo("完成", "操作完成")

root = tk.Tk()
root.title("made by Daisy")

directory_var = tk.StringVar()
# 设置默认路径
default_path = r"C:\SteamLibrary\steamapps\workshop\content\294100"
if os.path.exists(default_path):
    directory_var.set(default_path)
else:
    directory_var.set("")  # 如果默认路径不存在则设为空

progress_var = tk.IntVar()

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="选择目录:").grid(row=0, column=0, sticky=tk.W)
ttk.Entry(frame, textvariable=directory_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E))
ttk.Button(frame, text="浏览", command=select_directory).grid(row=0, column=2, sticky=tk.W)

ttk.Button(frame, text="一键替换", command=lambda: process_directories('rename')).grid(row=1, column=0, pady=10)
ttk.Button(frame, text="一键还原", command=lambda: process_directories('swap')).grid(row=1, column=1, pady=10)

progress_bar = ttk.Progressbar(frame, orient='horizontal', length=400, mode='determinate', variable=progress_var)
progress_bar.grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
