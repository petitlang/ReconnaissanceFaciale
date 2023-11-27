import os
import random
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class TripletFaceDataset(Dataset):
    def __init__(self, base_dir, transform=None):
        self.base_dir = base_dir
        self.transform = transform

        self.persons = os.listdir(base_dir)
        self.person_to_images = {person: os.listdir(os.path.join(base_dir, person)) for person in self.persons}

    def __getitem__(self, index):
        # 随机选择一个人物作为锚点和正例
        person = random.choice(self.persons)
        pos_image_name = random.choice(self.person_to_images[person])
        anchor_image_name = random.choice([img for img in self.person_to_images[person] if img != pos_image_name])
        
        anchor_image = Image.open(os.path.join(self.base_dir, person, anchor_image_name))
        positive_image = Image.open(os.path.join(self.base_dir, person, pos_image_name))

        # 随机选择另一个人物作为反例
        negative_person = random.choice([p for p in self.persons if p != person])
        negative_image_name = random.choice(self.person_to_images[negative_person])
        negative_image = Image.open(os.path.join(self.base_dir, negative_person, negative_image_name))

        # 应用转换
        if self.transform is not None:
            anchor_image = self.transform(anchor_image)
            positive_image = self.transform(positive_image)
            negative_image = self.transform(negative_image)

        return anchor_image, positive_image, negative_image
    
 
# Dataloader
from torch.utils.data import DataLoader

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

# 实例化数据集
dataset = TripletFaceDataset('DataTraite', transform=transform)

# 数据加载器
data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# model
import torch.nn as nn
import torch.nn.functional as F

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=5)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=5)
        self.fc1 = nn.Linear(64 * 29 * 29, 256)
        self.fc2 = nn.Linear(256, 128)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# train
import torch.optim as optim
import torch

# 初始化模型、优化器和损失函数
model = SimpleCNN()
optimizer = optim.Adam(model.parameters(), lr=0.001)
triplet_loss = nn.TripletMarginLoss(margin=1.0)

# 训练周期
num_epochs = 100

for epoch in range(num_epochs):
    for i, (anchor_img, positive_img, negative_img) in enumerate(data_loader):
        # 将模型的模式设置为训练模式
        model.train()

        # 前向传播
        optimizer.zero_grad()
        anchor_output = model(anchor_img)
        positive_output = model(positive_img)
        negative_output = model(negative_img)

        # 计算三元损失
        loss = triplet_loss(anchor_output, positive_output, negative_output)

        # 反向传播和优化
        loss.backward()
        optimizer.step()

        # 打印日志
        if (i + 1) % 100 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(data_loader)}], Loss: {loss.item():.4f}')
