from ultralytics import YOLO
import os
from PIL import Image, ImageDraw
import torch
import re
import shutil

def natural_sort_key(s):
    """實現自然排序的key函數，正確處理包含數字的檔名"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

# 設定 GPU 設備
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(f"使用設備: {device}")

# 設定目錄路徑
image_dir = "/home/tim911004/ML/Final-Project/inference_dataset"
output_dir = "/home/tim911004/ML/Final-Project/inference-result"

# 建立標註成功和未標註的資料夾
labeled_image_dir = os.path.join(output_dir, "labeled_image_dir")
labeled_txt_dir = os.path.join(output_dir, "labeled_txt_dir")
unlabeled_image_dir = os.path.join(output_dir, "unlabeled_image_dir")
unlabeled_txt_dir = os.path.join(output_dir, "unlabeled_txt_dir")

while True:
    try:
        confidence_threshold = float(input("請輸入信心度閾值 (0.0-1.0，建議 0.3-0.7): "))
        if 0.0 <= confidence_threshold <= 1.0:
            break
        else:
            print("請輸入 0.0 到 1.0 之間的數值")
    except ValueError:
        print("請輸入有效的數值")

print(f"\n使用信心度閾值: {confidence_threshold}")


# 建立所有需要的目錄
for dir_path in [output_dir, labeled_image_dir, labeled_txt_dir, unlabeled_image_dir, unlabeled_txt_dir]:
    os.makedirs(dir_path, exist_ok=True)

# 載入 YOLO 模型並移至 GPU
model = YOLO("/home/tim911004/ML/Final-Project/yolo_training/LeftTurnBox_detection_batch64_new1000dataset_350epoch4/weights/best.pt")
model.to(device)

# 取得類別名稱
class_names = model.names

def convert_to_yolo_format(box, image_width, image_height):
    """將 (x1, y1, x2, y2) 轉換為 YOLO 格式 (x_center, y_center, width, height)"""
    x1, y1, x2, y2 = box
    
    # 計算中心點和寬高
    x_center = ((x1 + x2) / 2) / image_width
    y_center = ((y1 + y2) / 2) / image_height
    width = (x2 - x1) / image_width
    height = (y2 - y1) / image_height
    
    return x_center, y_center, width, height

def draw_and_save_boxes(image, boxes, scores, labels, class_names, target_classes, filename, threshold=0.5):
    """繪製邊界框並儲存 YOLO 格式的標註檔案"""
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    detected_objects = []
    
    # 準備寫入 txt 檔案的內容
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    
    # 根據是否檢測到物件選擇保存路徑
    has_detection = False
    txt_content = []
    
    for box, score, label in zip(boxes, scores, labels):
        if score >= threshold and class_names[int(label)] in target_classes:
            has_detection = True
            # 繪製邊界框
            x1, y1, x2, y2 = box
            label_name = class_names[int(label)]
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            draw.text((x1, y1), f"{label_name} ({score:.2f})", fill="red")
            
            # 記錄檢測到的物件
            detected_objects.append({
                'label': label_name,
                'confidence': score
            })
            
            # 轉換為 YOLO 格式並記錄
            x_center, y_center, width, height = convert_to_yolo_format(box, image_width, image_height)
            txt_content.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    # 根據檢測結果選擇保存路徑並保存檔案
    if has_detection:
        txt_path = os.path.join(labeled_txt_dir, txt_filename)
    else:
        txt_path = os.path.join(unlabeled_txt_dir, txt_filename)
    
    # 寫入txt檔案
    with open(txt_path, 'w') as f:
        f.write('\n'.join(txt_content))
    
    return image, detected_objects, has_detection

# 設定目標類別
target_classes = ["LeftTurnBox"]

# 處理所有圖片
print("\n開始進行推論...\n")
print("說明：每當偵測到 LeftTurnBox 時，程式會暫停。按下 Enter 鍵繼續處理下一張圖片。")
print("圖片處理順序：按照檔名自然排序\n")

# 建立圖片路徑列表並排序
image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
image_files.sort(key=natural_sort_key)  # 使用自然排序
print("處理順序：")
for i, f in enumerate(image_files, 1):
    print(f"{i}. {f}")
print("\n" + "="*50 + "\n")

image_paths = [os.path.join(image_dir, f) for f in image_files]

# 統計檢測結果
total_images = len(image_paths)
detected_images = 0

# 使用批次處理來提高效能，但因為要暫停，所以把批次大小設為1
batch_size = 1
for i in range(0, len(image_paths), batch_size):
    batch_paths = image_paths[i:i + batch_size]
    
    # 批次執行推論
    results = model(batch_paths, device=device)
    
    # 處理每個結果
    for result, image_path in zip(results, batch_paths):
        filename = os.path.basename(image_path)
        
        # 提取邊界框、信心分數和類別 ID
        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        labels = result.boxes.cls.cpu().numpy()
        
        # 開啟圖片並繪製目標類別的邊界框
        image = Image.open(image_path).convert("RGB")
        annotated_image, detected_objects, has_detection = draw_and_save_boxes(
            image, boxes, scores, labels,
            class_names, target_classes,
            filename, threshold=confidence_threshold
        )
        
        # 根據檢測結果選擇保存路徑
        save_image_dir = labeled_image_dir if has_detection else unlabeled_image_dir
        
        # 儲存圖片
        annotated_image.save(os.path.join(save_image_dir, filename))
        
        # 如果檢測到目標物件，顯示資訊並暫停
        if has_detection:
            detected_images += 1
            print(f"✓ 在圖片 '{filename}' 中檢測到 LeftTurnBox:")
            for obj in detected_objects:
                print(f"   - 信心度: {obj['confidence']:.2%}")
            print(f"\n已標註圖片保存至: {os.path.join(labeled_image_dir, filename)}")
            print(f"已標註文件保存至: {os.path.join(labeled_txt_dir, os.path.splitext(filename)[0] + '.txt')}")
            input("\n按下 Enter 鍵繼續處理下一張圖片...")  # 等待用戶按下 Enter
            print("\n" + "="*50 + "\n")  # 分隔線
        else:
            # 可選：顯示未檢測到的圖片資訊
            print(f"- 圖片 '{filename}' 未檢測到 LeftTurnBox")

# 印出統計資訊
print("\n推論完成。統計資訊：")
print(f"- 總共處理的圖片數量: {total_images}")
print(f"- 檢測到 LeftTurnBox 的圖片數量: {detected_images}")
print(f"- 未檢測到的圖片數量: {total_images - detected_images}")
print(f"- 檢測率: {detected_images/total_images:.1%}")
print("\n檔案儲存位置：")
print(f"- 已標註圖片: {labeled_image_dir}")
print(f"- 已標註標籤: {labeled_txt_dir}")
print(f"- 未標註圖片: {unlabeled_image_dir}")
print(f"- 未標註標籤: {unlabeled_txt_dir}")