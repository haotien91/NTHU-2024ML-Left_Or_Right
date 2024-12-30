import os
import json
import re
from collections import defaultdict

def get_location_info(filename):
    # 文件名匹配正则表达式
    pattern = re.compile(r'^(\d+)_(\d+)_(\d+)_(\d+)_(\d+)\.txt$')
    match = pattern.match(filename)
    
    if match:
        lat_deg = match.group(1)
        lat_dec = match.group(2)
        lng_deg = match.group(3)
        lng_dec = match.group(4)
        angle = match.group(5)
        
        # 解析经纬度和角度
        lat = float(f"{lat_deg}.{lat_dec}")
        lng = float(f"{lng_deg}.{lng_dec}")
        
        return {
            'lat': lat,
            'lng': lng,
            'angle': int(angle),
            'base_filename': f"{lat_deg}_{lat_dec}_{lng_deg}_{lng_dec}_{angle}"
        }
    return None

def process_folder(folder_path):
    # 获取文件夹中的所有.txt文件名
    filenames = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
    # 用于按位置分组的字典
    locations = defaultdict(list)
    
    for filename in filenames:
        # 检查文件是否为空
        filepath = os.path.join(folder_path, filename)
        if os.path.getsize(filepath) > 0:  # 如果文件不为空
            info = get_location_info(filename)
            if info:
                # 使用经纬度作为键来分组
                key = (info['lat'], info['lng'])
                locations[key].append({
                    'angle': info['angle'],
                    'filename': info['base_filename']
                })
    
    # 转换为列表格式
    data_list = []
    for (lat, lng), angles in locations.items():
        data_list.append({
            'lat': lat,
            'lng': lng,
            'images': sorted(angles, key=lambda x: x['angle'])  # 按角度排序
        })
    
    return data_list

# 处理文件夹
data = process_folder('labeled_HsinChu')

# 将数据写入 JSON 文件
with open('leftturnbox.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"已生成数据文件：leftturnbox.json，共有 {len(data)} 个唯一坐标点")
print("位置分布统计：")
for loc in data:
    print(f"位置 ({loc['lat']}, {loc['lng']}) 有 {len(loc['images'])} 张图片")