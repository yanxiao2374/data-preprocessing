import os
import cv2
import numpy as np
from imutils import rotate_bound
import random
import shutil
from tqdm import tqdm


class YOLOAugmentor:
    def __init__(self, input_dir, output_dir):
        """
        初始化YOLO数据增强器

        参数:
            input_dir: 输入目录，包含images和labels子目录
            output_dir: 输出目录，增强后的数据将保存在这里
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.image_dir = os.path.join(input_dir, 'images', 'train')
        self.label_dir = os.path.join(input_dir, 'labels', 'train')

        # 创建输出目录结构
        os.makedirs(os.path.join(output_dir, 'images', 'train'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', 'train'), exist_ok=True)

    def load_yolo_annotation(self, label_path, img_width, img_height):
        """
        加载YOLO格式的标注文件

        参数:
            label_path: 标注文件路径
            img_width: 图像宽度
            img_height: 图像高度

        返回:
            list: 包含(class_id, x_center, y_center, width, height)的列表
        """
        annotations = []
        with open(label_path, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    annotations.append((class_id, x_center, y_center, width, height))
        return annotations

    def save_yolo_annotation(self, label_path, annotations):
        """
        保存YOLO格式的标注文件

        参数:
            label_path: 标注文件路径
            annotations: 标注列表，格式为[(class_id, x_center, y_center, width, height), ...]
        """
        with open(label_path, 'w') as f:
            for ann in annotations:
                f.write(f"{ann[0]} {ann[1]:.6f} {ann[2]:.6f} {ann[3]:.6f} {ann[4]:.6f}\n")

    def horizontal_flip(self, image, annotations):
        """
        水平翻转图像和标注

        参数:
            image: 原始图像
            annotations: 原始标注

        返回:
            tuple: (翻转后的图像, 翻转后的标注)
        """
        h_flipped = cv2.flip(image, 1)
        flipped_annotations = []

        for ann in annotations:
            class_id, x_center, y_center, width, height = ann
            # 水平翻转只需要改变x_center
            new_x_center = 1.0 - x_center
            flipped_annotations.append((class_id, new_x_center, y_center, width, height))

        return h_flipped, flipped_annotations

    def vertical_flip(self, image, annotations):
        """
        垂直翻转图像和标注

        参数:
            image: 原始图像
            annotations: 原始标注

        返回:
            tuple: (翻转后的图像, 翻转后的标注)
        """
        v_flipped = cv2.flip(image, 0)
        flipped_annotations = []

        for ann in annotations:
            class_id, x_center, y_center, width, height = ann
            # 垂直翻转只需要改变y_center
            new_y_center = 1.0 - y_center
            flipped_annotations.append((class_id, x_center, new_y_center, width, height))

        return v_flipped, flipped_annotations

    def rotate_image(self, image, angle, annotations):
        """
        旋转图像和调整标注

        参数:
            image: 原始图像
            angle: 旋转角度(90, 180, 270)
            annotations: 原始标注

        返回:
            tuple: (旋转后的图像, 旋转后的标注)
        """
        if angle not in [90, 180, 270]:
            raise ValueError("Angle must be 90, 180 or 270 degrees")

        # 旋转图像
        rotated = rotate_bound(image, angle)
        h, w = rotated.shape[:2]

        rotated_annotations = []

        for ann in annotations:
            class_id, x_center, y_center, width, height = ann

            # 将归一化坐标转换为绝对坐标
            orig_h, orig_w = image.shape[:2]
            x_center_abs = x_center * orig_w
            y_center_abs = y_center * orig_h
            width_abs = width * orig_w
            height_abs = height * orig_h

            # 计算边界框坐标
            x1 = x_center_abs - width_abs / 2
            y1 = y_center_abs - height_abs / 2
            x2 = x_center_abs + width_abs / 2
            y2 = y_center_abs + height_abs / 2

            # 旋转坐标
            if angle == 90:
                new_x1 = y1
                new_y1 = orig_w - x2
                new_x2 = y2
                new_y2 = orig_w - x1
            elif angle == 180:
                new_x1 = orig_w - x2
                new_y1 = orig_h - y2
                new_x2 = orig_w - x1
                new_y2 = orig_h - y1
            elif angle == 270:
                new_x1 = orig_h - y2
                new_y1 = x1
                new_x2 = orig_h - y1
                new_y2 = x2

            # 计算新的中心点和宽高
            new_width = new_x2 - new_x1
            new_height = new_y2 - new_y1
            new_x_center = (new_x1 + new_x2) / 2
            new_y_center = (new_y1 + new_y2) / 2

            # 转换为新图像的归一化坐标
            if angle in [90, 270]:
                new_h, new_w = w, h
            else:
                new_w, new_h = w, h

            new_x_center_norm = new_x_center / new_w
            new_y_center_norm = new_y_center / new_h
            new_width_norm = new_width / new_w
            new_height_norm = new_height / new_h

            rotated_annotations.append((class_id, new_x_center_norm, new_y_center_norm,
                                        new_width_norm, new_height_norm))

        return rotated, rotated_annotations

    def adjust_contrast(self, image, factor):
        """
        调整图像对比度

        参数:
            image: 原始图像
            factor: 对比度因子 (>1增强, <1减弱)

        返回:
            ndarray: 对比度调整后的图像
        """
        mean = np.mean(image)
        contrasted = np.clip((image - mean) * factor + mean, 0, 255).astype(np.uint8)
        return contrasted

    def apply_gaussian_blur(self, image, kernel_size=(5, 5)):
        """
        应用高斯模糊

        参数:
            image: 原始图像
            kernel_size: 高斯核大小

        返回:
            ndarray: 模糊后的图像
        """
        blurred = cv2.GaussianBlur(image, kernel_size, 0)
        return blurred

    def augment_image(self, image_path, label_path):
        """
        对单个图像和标注文件进行数据增强

        参数:
            image_path: 图像路径
            label_path: 标注路径
        """
        # 读取原始图像和标注
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return

        img_height, img_width = image.shape[:2]
        annotations = self.load_yolo_annotation(label_path, img_width, img_height)

        # 获取文件名和扩展名
        filename = os.path.splitext(os.path.basename(image_path))[0]
        ext = os.path.splitext(image_path)[1]

        # 1. 水平翻转
        h_flipped, h_annotations = self.horizontal_flip(image, annotations)
        cv2.imwrite(os.path.join(self.output_dir, 'images', 'train', f"{filename}_hflip{ext}"), h_flipped)
        self.save_yolo_annotation(os.path.join(self.output_dir, 'labels', 'train', f"{filename}_hflip.txt"), h_annotations)

        # 2. 垂直翻转
        v_flipped, v_annotations = self.vertical_flip(image, annotations)
        cv2.imwrite(os.path.join(self.output_dir, 'images', 'train', f"{filename}_vflip{ext}"), v_flipped)
        self.save_yolo_annotation(os.path.join(self.output_dir, 'labels', 'train', f"{filename}_vflip.txt"), v_annotations)

        # 3. 多角度旋转
        for angle in [90, 180, 270]:
            rotated, rotated_annotations = self.rotate_image(image, angle, annotations)
            cv2.imwrite(os.path.join(self.output_dir, 'images', 'train', f"{filename}_rotate{angle}{ext}"), rotated)
            self.save_yolo_annotation(os.path.join(self.output_dir, 'labels', 'train', f"{filename}_rotate{angle}.txt"),
                                      rotated_annotations)

        # 4. 对比度调整
        for factor in [0.5, 1.5]:  # 减弱和增强
            contrasted = self.adjust_contrast(image, factor)
            cv2.imwrite(os.path.join(self.output_dir, 'images', 'train', f"{filename}_contrast{factor}{ext}"), contrasted)
            # 对比度调整不影响标注
            shutil.copy(label_path, os.path.join(self.output_dir, 'labels', 'train', f"{filename}_contrast{factor}.txt"))

        # 5. 高斯模糊
        blurred = self.apply_gaussian_blur(image)
        cv2.imwrite(os.path.join(self.output_dir, 'images', 'train', f"{filename}_blurred{ext}"), blurred)
        # 高斯模糊不影响标注
        shutil.copy(label_path, os.path.join(self.output_dir, 'labels', 'train', f"{filename}_blurred.txt"))

    def augment_all(self):
        """
        增强输入目录中的所有图像和标注
        """
        # 获取所有图像文件
        image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # 处理每个图像
        for img_file in tqdm(image_files, desc="Processing images"):
            image_path = os.path.join(self.image_dir, img_file)
            label_path = os.path.join(self.label_dir, os.path.splitext(img_file)[0] + '.txt')

            if not os.path.exists(label_path):
                print(f"警告: 找不到标注文件 {label_path}")
                continue

            self.augment_image(image_path, label_path)


if __name__ == "__main__":
    # 使用示例
    input_directory = "D:\OneDrive\Data\Datasets\heading"  # 包含images和labels子目录
    output_directory = "E:\wheat_head\Datasets_augmented\heading"

    augmentor = YOLOAugmentor(input_directory, output_directory)
    augmentor.augment_all()

    print(f"数据增强完成! 结果已保存到 {output_directory}")