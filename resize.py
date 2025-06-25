import os
import cv2

def resize_images(input_dir, output_dir, size=(512, 512), suffix=".png"):
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 支持的图片后缀
    valid_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']

    for filename in os.listdir(input_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_exts:
            img_path = os.path.join(input_dir, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"无法读取图像：{img_path}")
                continue

            # resize 操作
            resized_img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)

            # 输出路径
            out_path = os.path.join(output_dir, os.path.splitext(filename)[0] + suffix)
            cv2.imwrite(out_path, resized_img)
            print(f"已保存：{out_path}")

# 示例使用
if __name__ == "__main__":
    input_folder = r"D:\OneDrive\Data\Datasets\dough\images\train"          # 输入图像目录
    output_folder = r"D:\OneDrive\Data\Datasets_512\dough\images\train" # 输出目录
    resize_size = (512, 512)         # 目标尺寸

    resize_images(input_folder, output_folder, resize_size)
    input_folder=input_folder.replace("train","test")
    output_folder = output_folder.replace("train", "test")
    resize_images(input_folder, output_folder, resize_size)
    input_folder = input_folder.replace("test", "val")
    output_folder = output_folder.replace("test", "val")
    resize_images(input_folder, output_folder, resize_size)