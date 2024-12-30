import os
import json
import re

def is_valid_coordinates(lat, lng):
    """檢查經緯度值是否在新竹市的合理範圍內"""
    # 新竹市大致範圍
    HSINCHU_BOUNDS = {
        'lat_min': 24.70,
        'lat_max': 24.85,
        'lng_min': 120.90,
        'lng_max': 121.05
    }
    
    return (HSINCHU_BOUNDS['lat_min'] <= lat <= HSINCHU_BOUNDS['lat_max'] and
            HSINCHU_BOUNDS['lng_min'] <= lng <= HSINCHU_BOUNDS['lng_max'])

def process_folder(folder_path):
    """處理指定資料夾中的圖片檔案，解析檔名生成資料"""
    if not os.path.exists(folder_path):
        print(f"資料夾不存在：{folder_path}")
        return []
    
    filenames = os.listdir(folder_path)
    data_list = []
    invalid_coords = []
    
    pattern = re.compile(r'^(\d+)_(\d+)_(\d+)_(\d+)_(\d+)(\.\w+)?$')
    
    print(f"開始處理 {folder_path} 資料夾...")
    print(f"找到 {len(filenames)} 個檔案")
    
    for filename in filenames:
        match = pattern.match(filename)
        if match:
            try:
                lat_part = f"{match.group(1)}.{match.group(2)}"
                lng_part = f"{match.group(3)}.{match.group(4)}"
                
                lat = float(lat_part)
                lng = float(lng_part)
                angle = float(match.group(5))
                ext = match.group(6) if match.group(6) else ''
                
                # 檢查經緯度是否在新竹市範圍內
                if not is_valid_coordinates(lat, lng):
                    invalid_coords.append((filename, lat, lng))
                    continue
                
                data_list.append({
                    'filename': filename,
                    'lat': lat,
                    'lng': lng,
                    'angle': angle,
                    'ext': ext
                })
                
            except ValueError as e:
                print(f"錯誤：處理檔案 {filename} 時發生數值轉換錯誤：{str(e)}")
                continue
        else:
            print(f"跳過不符合格式的檔案：{filename}")
    
    # 輸出統計資訊
    print(f"\n處理完成：")
    print(f"- 總檔案數：{len(filenames)}")
    print(f"- 有效資料數：{len(data_list)}")
    print(f"- 無效座標數：{len(invalid_coords)}")
    
    if invalid_coords:
        print("\n以下檔案的座標超出新竹市範圍：")
        for filename, lat, lng in invalid_coords[:10]:  # 只顯示前10筆
            print(f"- {filename}: ({lat}, {lng})")
        if len(invalid_coords) > 10:
            print(f"... 還有 {len(invalid_coords) - 10} 筆")
    
    return data_list

def main():
    # 處理資料夾
    allpoint_data = process_folder('LeftTurnBoxPhoto_allpoint')
    
    if allpoint_data:
        output_file = 'data.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(allpoint_data, f, ensure_ascii=False, indent=4)
            print(f"\n已成功生成 {output_file}")
            print(f"- 包含 {len(allpoint_data)} 筆資料")
            
            # 顯示範例資料
            if len(allpoint_data) > 0:
                print("\n資料範例：")
                print(json.dumps(allpoint_data[0], ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"錯誤：寫入 {output_file} 時發生錯誤：{str(e)}")
    else:
        print("\n警告：沒有可用的資料可寫入")

if __name__ == '__main__':
    main()