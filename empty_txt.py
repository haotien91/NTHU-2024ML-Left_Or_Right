import os

def process_directory(directory):
    # Step 1: 找出所有 .jpg 的檔名 (去除 .jpg 附檔結尾)，建立成 list
    jpg_files = [os.path.splitext(f)[0] for f in os.listdir(directory) if f.endswith('.jpg')]
    
    # Step 2: 去除掉存在對應 檔名.txt 的元素
    remaining_files = [f for f in jpg_files if not os.path.exists(os.path.join(directory, f + '.txt'))]
    
    # Step 3: 為剩下的檔名在相同路徑建立一個空白的 檔名.txt
    for file_name in remaining_files:
        txt_path = os.path.join(directory, file_name + '.txt')
        with open(txt_path, 'w') as txt_file:
            pass  # 建立空白檔案

    print(f"已處理目錄: {directory}")
    print(f"剩餘檔名清單: {remaining_files}")

# Example usage:
directory_path = "C://Users//USER//Desktop//Codes//Machine Learning Introduction//Final Project//再標_昊天"
process_directory(directory_path)
