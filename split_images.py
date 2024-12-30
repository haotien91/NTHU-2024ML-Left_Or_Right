import os
import random
import shutil

# 設定目錄路徑
collection_dir = 'collection'
annotation_dir = 'annotation'
inference_dir = 'inference'

# 確保目標目錄存在
os.makedirs(annotation_dir, exist_ok=True)
os.makedirs(inference_dir, exist_ok=True)

# 獲取 collection 目錄中所有圖片文件
image_files = [f for f in os.listdir(collection_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 隨機選擇 500 張圖片
annotation_images = random.sample(image_files, min(500, len(image_files)))

# 複製圖片到相應的目錄
for image in image_files:
    source = os.path.join(collection_dir, image)
    if image in annotation_images:
        destination = os.path.join(annotation_dir, image)
    else:
        destination = os.path.join(inference_dir, image)
    shutil.copy2(source, destination)

print(f"已將 {len(annotation_images)} 張圖片複製到 {annotation_dir}")
print(f"已將 {len(image_files) - len(annotation_images)} 張圖片複製到 {inference_dir}")
