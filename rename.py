import os
import re


def rename_files(folder_path):
    """
    将文件夹中所有heading_xxx.png重命名为flowering_xxx.png
    :param folder_path: 目标文件夹路径
    """
    # 编译正则表达式，匹配heading_数字.png的模式
    pattern = re.compile(r'flowering_(\d+)\.json', re.IGNORECASE)

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件名是否匹配模式
        match = pattern.fullmatch(filename)
        if match:
            # 提取数字部分
            number = match.group(1)
            # 构造新文件名
            new_filename = f'filling_{number}.json'
            # 获取旧文件和新文件的完整路径
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            # 重命名文件
            try:
                os.rename(old_path, new_path)
                print(f'Renamed: {filename} -> {new_filename}')
            except Exception as e:
                print(f'Error renaming {filename}: {e}')


if __name__ == '__main__':
    # 替换为你的文件夹路径
    target_folder = 'G:/wheat_head/Datasets/filling'
    rename_files(target_folder)