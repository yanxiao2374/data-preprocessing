import os
import json
import re


def check_and_update_json_files(folder_path):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            # 提取文件名中的数字
            file_num_match = re.search(r'(\d+)', filename)
            if not file_num_match:
                print(f"文件名中未找到数字: {filename}")
                continue

            file_num = file_num_match.group(1)
            json_path = os.path.join(folder_path, filename)

            try:
                # 读取JSON文件
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查imagePath是否存在
                if 'imagePath' not in data:
                    print(f"{filename} 中没有找到 imagePath 字段")
                    continue

                # 提取imagePath中的数字
                image_path = data['imagePath']
                image_num_match = re.search(r'(\d+)', image_path)
                if not image_num_match:
                    print(f"{filename} 的 imagePath 中未找到数字: {image_path}")
                    continue

                image_num = image_num_match.group(1)

                # 比较数字是否一致
                if image_num != file_num:
                    # 更新imagePath中的数字
                    new_image_path = re.sub(r'\d+', file_num, image_path)
                    data['imagePath'] = new_image_path

                    # 写回JSON文件
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    print(f"已更新 {filename}: {image_path} -> {new_image_path}")
                else:
                    print(f"{filename} 的数字一致: {image_path}")

            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")


if __name__ == '__main__':
    folder_path = "G:/wheat_head/Datasets/filling"
    check_and_update_json_files(folder_path)