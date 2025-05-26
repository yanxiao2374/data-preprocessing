import os
import argparse


def check_matching_files(directory):
    # 获取目录下所有文件
    files = os.listdir(directory)

    # 分离出png和json文件
    png_files = [f for f in files if f.endswith('.png')]
    json_files = [f for f in files if f.endswith('.json')]

    # 提取文件名前缀（不带扩展名）
    png_prefixes = {os.path.splitext(f)[0] for f in png_files}
    json_prefixes = {os.path.splitext(f)[0] for f in json_files}

    # 找出不匹配的文件
    only_png = png_prefixes - json_prefixes
    only_json = json_prefixes - png_prefixes

    # 输出结果
    if only_png:
        print("以下PNG文件没有对应的JSON文件:")
        for prefix in sorted(only_png):
            print(f"  - {prefix}.png")

    if only_json:
        print("\n以下JSON文件没有对应的PNG文件:")
        for prefix in sorted(only_json):
            print(f"  - {prefix}.json")

    if not only_png and not only_json:
        print("所有PNG和JSON文件都正确配对。")

    return len(only_png), len(only_json)


def main():
    parser = argparse.ArgumentParser(description='检查PNG和JSON文件是否成对存在')
    parser.add_argument('directory', help='要检查的目录路径')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"错误: '{args.directory}' 不是一个有效的目录")
        return

    png_only, json_only = check_matching_files(args.directory)

    print(f"\n统计: {png_only}个单独的PNG文件, {json_only}个单独的JSON文件")


if __name__ == '__main__':
    main()