"""
### thumb of rule to crawl image from GCP

https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={latitude},{longitude}&heading={heading}&pitch={pitch}&fov={fov}
- viewpoint 視點: 可選擇經緯度位置為視點.
- heading 方向: 可選擇以正北邊為0度, 順時鐘範圍為-180度到360度之間.
- pitch 仰角: 可選擇以水平為0度, 上下範圍為-90度到90度之間.
- fov 視界: 檢視的平面範圍. 可選擇範圍為10到100之間, 預設為90.
"""

# HINT: 每天/每API限制爬~20000張圖片

import os
import pandas as pd
import requests
import time
import random
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

#### 參數區 ####
pitch = 0
fov = 90
num_images = None  # 將默認值設為 None
################

def download_image(url, file_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return False
    except RequestException as e:
        print(f"Error downloading image: {str(e)}")
        return False

def download_images_from_csv(num_images=None, images_per_position=5):
    csv_folder = os.path.join(os.getcwd(), 'public_railway')
    collection_folder = os.path.join(os.getcwd(), 'HighSpeedRailwayCollection')

    if not os.path.exists(collection_folder):
        os.makedirs(collection_folder)

    api_key = os.getenv('GCP_MAP_API_KEY')
    if not api_key:
        print("Error: GCP_MAP_API_KEY not found in .env file")
        return

    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            csv_path = os.path.join(csv_folder, filename)
            df = pd.read_csv(csv_path)
            
            if num_images is not None:
                df = df.head(num_images)

            total_rows = len(df)
            for index, row in df.iterrows():
                latitude = row['latitude']
                longitude = row['longitude']
                
                print(f"Processing {index + 1}/{total_rows}: {latitude}, {longitude}")
                
                heading_interval = 360 // images_per_position
                
                for heading in range(0, 360, heading_interval):
                    url = f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={latitude},{longitude}&heading={heading}&pitch={pitch}&fov={fov}&key={api_key}"
                    
                    safe_latitude = str(latitude).replace('.', '_')
                    safe_longitude = str(longitude).replace('.', '_')
                    image_path = os.path.join(collection_folder, f"{safe_latitude}_{safe_longitude}_{heading}.jpg")
                    
                    if download_image(url, image_path):
                        print(f"Successfully downloaded image for {latitude}, {longitude}, heading {heading}")
                    else:
                        print(f"Failed to download image for {latitude}, {longitude}, heading {heading}")
                    
                    time.sleep(random.uniform(1, 3))  # 添加隨機延遲

if __name__ == "__main__":
    download_images_from_csv(num_images=num_images)
