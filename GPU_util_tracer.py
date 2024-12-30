import subprocess
import time
from datetime import datetime
import pandas as pd
import os

def get_gpu_stats():
    try:
        result = subprocess.check_output([
            'nvidia-smi', 
            '--query-gpu=timestamp,utilization.gpu,power.draw,memory.used,memory.total',
            '--format=csv,noheader,nounits'
        ]).decode()
        
        timestamp, gpu_util, power, mem_used, mem_total = result.strip().split(',')
        return {
            'timestamp': datetime.now(),
            'utilization': float(gpu_util),
            'power': float(power),
            'memory_used': float(mem_used),
            'memory_total': float(mem_total)
        }
    except:
        return None

def save_stats(data, filename='gpu_stats.csv'):
    df = pd.DataFrame([data])
    
    if not os.path.exists(filename):
        df.to_csv(filename, index=False)
    else:
        df.to_csv(filename, mode='a', header=False, index=False)

def main():
    interval = 5
    
    while True:
        stats = get_gpu_stats()
        if stats:
            print(f"[{stats['timestamp']}] GPU: {stats['utilization']}%, "
                  f"Power: {stats['power']}W, "
                  f"Memory: {stats['memory_used']}/{stats['memory_total']} MB")
            save_stats(stats)
        
        time.sleep(interval)

if __name__ == '__main__':
    main()