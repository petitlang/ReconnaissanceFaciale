import os
from torchvision.datasets import ImageFolder
from torchvision import transforms
from PIL import Image, ImageFilter

def process_and_save_images(dataset_path, output_folder, num_images, resize_dim=(128, 128)):
    """
    Process and save a specified number of images from a dataset.

    Args:
    - dataset_path (str): The path to the dataset.
    - output_folder (str): The folder where processed images will be saved.
    - num_images (int): The number of images to process and save.
    - resize_dim (tuple): The dimensions to resize the images to. Default is (128, 128).
    """

    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 数据预处理
    transform = transforms.Compose([
        transforms.Resize(resize_dim),
        transforms.ToTensor(),
    ])

    # 加载数据集
    dataset = ImageFolder(dataset_path, transform=transform)

    # 处理并保存指定数量的图片
    for i, (image, label) in enumerate(dataset):
        if i >= num_images:
            break

        # 获取标签（人物）名称
        label_name = dataset.classes[label]

        # 创建对应的子文件夹
        label_folder = os.path.join(output_folder, label_name)
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)

        # 将Tensor转换回PIL图片
        image_pil = transforms.ToPILImage()(image).convert("RGB")

        # 二值化处理
        image_pil = image_pil.convert('L').point(lambda x: 0 if x < 128 else 255, '1')

        # 简单降噪处理
        image_pil = image_pil.filter(ImageFilter.MedianFilter())

        # 保存图片到对应的子文件夹
        image_pil.save(os.path.join(label_folder, f'image_{i}.jpg'))

# instance of using
process_and_save_images('path_to_ms_celeb_1m', 'DataTraite', 10000)
