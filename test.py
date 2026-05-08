import os
import json
import sys

def replace_flower_to_fill(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                with open(json_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 替换所有的flower为fill
                new_content = content.replace('douth', 'dough')
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = '.'
    replace_flower_to_fill(directory)
    print(f"已完成，处理了{'多个' if len(os.listdir(directory)) > 1 else '一个'}文件夹里的所有JSON文件。")
