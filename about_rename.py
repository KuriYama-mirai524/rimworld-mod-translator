import os


import xml.etree.ElementTree as ET

# 重命名为中文
def rename_files_in_directories(base_directory):
    about_path = os.path.join(base_directory, 'About.xml')
    about_old_path = os.path.join(base_directory, 'About_old.xml')

    # 检查 About_old.xml 是否存在
    if os.path.exists(about_old_path):
        # 检查 About.xml 中的 name 值是否包含中文
        tree = ET.parse(about_path)
        root = tree.getroot()
        name_element = root.find('name')

        if name_element is not None and not any('\u4e00' <= char <= '\u9fff' for char in name_element.text):
            print('正在替换', about_path)
            os.rename(about_path, os.path.join(base_directory, 'About_temp.xml'))
            os.rename(about_old_path, about_path)
            os.rename(os.path.join(base_directory, 'About_temp.xml'), about_old_path)


def get_directory_names(path):
    try:
        # 获取指定目录下的所有文件夹的完整路径
        return [os.path.join(path, name) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    except Exception as e:
        print(f"发生错误: {e}")
        return []
    
# 还原重命名
def swap_about_files(base_directory):
    about = os.path.join(base_directory, 'About.xml')
    about_old = os.path.join(base_directory, 'About_old.xml')
    
    # 检查 about_old.xml 是否存在
    if os.path.exists(about_old):
        # 检查 About.xml 中的 name 值是否包含中文
        tree = ET.parse(about)
        root = tree.getroot()
        name_element = root.find('name')

        if name_element is not None and not any('\u4e00' <= char <= '\u9fff' for char in name_element.text):
            pass
        else:
            print('正在还原', about)
            if os.path.exists(about):
                os.rename(about, os.path.join(base_directory, 'About_temp.xml'))
            os.rename(about_old, about)
            os.rename(os.path.join(base_directory, 'About_temp.xml'), about_old)


base_directory = rf'C:\SteamLibrary\steamapps\workshop\content\294100'
all_directories = get_directory_names(base_directory)
# print(all_directories)
for i in all_directories:
#     rename_files_in_directories(i + rf'\About')

    # # 调用还原方法
    swap_about_files(i + rf'\About')