from ultralytics import YOLO

# Load the YOLO model
model = YOLO("yolo11x.pt")

# Train the model with improved parameters
model.train(
    # 基本配置
    data="/home/tim911004/ML/Final-Project/training_dataset/data.yaml",
    epochs=300,
    patience=50,
    batch=64,            # 降低 batch size 提高穩定性
    imgsz=800,          # 增加圖片大小以提升小目標檢測
    device=0,
    project="/home/tim911004/ML/Final-Project/yolo_training",
    name="LeftTurnBox_detection_all_HsinChu_300epoch_64batch",
    
    # 學習率設定 - 降低學習率提高穩定性
    lr0=1e-3,           
    lrf=1e-6,           
    momentum=0.95,      # 提高動量
    weight_decay=0.001, # 增加正則化
    warmup_epochs=5,    
    
    # 降低資料增強強度
    augment=True,
    mixup=0.0,          # 關閉 mixup
    mosaic=0.5,         # 降低 mosaic 概率
    degrees=5.0,        # 降低旋轉角度
    translate=0.1,      
    scale=0.3,         
    fliplr=0.5,         
    hsv_h=0.015,        
    hsv_s=0.5,
    hsv_v=0.3,
    
    # 調整損失權重
    box=5.0,            # 降低框損失權重
    cls=1.0,            # 提高分類權重
    dfl=1.0,            # 降低 dfl 損失權重
    
    # 訓練策略
    overlap_mask=True,
    dropout=0.1,        # 降低 dropout
    label_smoothing=0.0, # 關閉標籤平滑
    
    # 驗證設定
    val=True,           
    save=True,          
    save_period=10,      # 更頻繁保存
    
    # 其他設定
    plots=True,         
    rect=True,          # 啟用矩形訓練
    cos_lr=True,        
    close_mosaic=20,    # 提前關閉 mosaic
    
    # 效能設定
    cache=False,        
)

# 驗證
results = model.val(
    data="/home/tim911004/ML/Final-Project/training_dataset/data.yaml",
    conf=0.25,          # 降低驗證閾值
    iou=0.6,            # 降低 IOU 閾值
    max_det=300,        
    half=True,          
    plots=True          
)