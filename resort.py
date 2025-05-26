import os
import re


def rename_sequential_files(folder_path, prefix="filling_"):
    # 获取所有匹配前缀的png文件
    files = [f for f in os.listdir(folder_path) if f.startswith(prefix) and f.endswith('.json')]

    # 提取数字并排序
    files.sort(key=lambda x: int(re.search(r'\d+', x).group()))

    expected_num = 1  # 我们期望的下一个数字

    for filename in files:
        # 提取当前文件的数字
        current_num = int(re.search(r'\d+', filename).group())

        # 如果当前数字不等于期望的数字，则重命名
        if current_num != expected_num:
            new_filename = f"{prefix}{expected_num:03d}.json"
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            # 确保新文件名不存在
            while os.path.exists(new_path):
                expected_num += 1
                new_filename = f"{prefix}{expected_num:03d}.json"
                new_path = os.path.join(folder_path, new_filename)

            os.rename(old_path, new_path)
            print(f"Renamed {filename} to {new_filename}")

        expected_num += 1


if __name__ == "__main__":
    folder_path = f"G:/wheat_head/Datasets/filling"
    rename_sequential_files(folder_path)