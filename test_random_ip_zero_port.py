import os
from PIL import Image
import numpy as np
from tqdm import tqdm
import scapy.all as scapy

def parse_image_ips(image_path):
    try:
        img = Image.open(image_path).convert("L")
        data = np.array(img).flatten()
        hex_string = ''.join([f'{byte:02x}' for byte in data])
        packet_count = 5
        packet_hex_size = 160 + 480
        packets_hex = [hex_string[i * packet_hex_size:(i + 1) * packet_hex_size] for i in range(packet_count)]

        def extract_ips(packet_hex):
            try:
                ip_header_hex = packet_hex[:160]
                ip_header_bytes = bytes.fromhex(ip_header_hex)
                src_ip = ".".join(str(b) for b in ip_header_bytes[12:16])
                dst_ip = ".".join(str(b) for b in ip_header_bytes[16:20])
                if all(0 <= int(x) <= 255 for x in src_ip.split(".")) and all(0 <= int(x) <= 255 for x in dst_ip.split(".")):
                    return src_ip, dst_ip
                return None, None
            except:
                return None, None

        ips = []
        for packet in packets_hex:
            src, dst = extract_ips(packet)
            if src and dst:
                ips.append((src, dst))
        return ips
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return []

def is_randomized(ip_pairs):
    valid_random_ips = {"0.0.0.0", "1.1.1.1"}
    for src, dst in ip_pairs:
        if src not in valid_random_ips or dst not in valid_random_ips:
            return False
    return True

def analyze_ip_statistics(ip_pairs):
    src_ips = set()
    dst_ips = set()
    for src, dst in ip_pairs:
        src_ips.add(src)
        dst_ips.add(dst)
    return src_ips, dst_ips

def analyze_directory(folder_path):
    # 遍历train目录下的所有子目录（标签目录）
    for label_dir in os.listdir(folder_path):
        label_path = os.path.join(folder_path, label_dir)
        if not os.path.isdir(label_path):
            continue
            
        results = {}
        all_src_ips = set()
        all_dst_ips = set()
        
        # 获取标签名
        label = label_dir
        
        # 统计当前标签目录下的文件总数
        total_files = sum(1 for root, _, files in os.walk(label_path)
                         for f in files if f.lower().endswith('.png'))
        
        if total_files == 0:
            continue
        
        # 使用tqdm创建进度条
        with tqdm(total=total_files, desc=f"正在分析 {label}") as pbar:
            for root, dirs, files in os.walk(label_path):
                for filename in files:
                    if filename.lower().endswith(".png"):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, label_path)
                        ip_pairs = parse_image_ips(full_path)
                        src_ips, dst_ips = analyze_ip_statistics(ip_pairs)
                        results[rel_path] = (src_ips, dst_ips)
                        all_src_ips.update(src_ips)
                        all_dst_ips.update(dst_ips)
                        pbar.update(1)

        print(f"\n{label} 分析完成 ✅")
        
        # 保存结果到文件
        output_file = "ip_statistics.txt"
        with open(output_file, "a", encoding='utf-8') as f:
            # 写入标签、源IP和目的IP，用制表符分隔
            src_ips_str = ','.join(sorted(all_src_ips))
            dst_ips_str = ','.join(sorted(all_dst_ips))
            f.write(f"{label}\t{src_ips_str}\t{dst_ips_str}\n")
        
        # 打印统计信息
        print(f"\n标签: {label}")
        print(f"所有不同的源IP ({len(all_src_ips)}):")
        for ip in sorted(all_src_ips):
            print(f"  - {ip}")
        print(f"\n所有不同的目的IP ({len(all_dst_ips)}):")
        for ip in sorted(all_dst_ips):
            print(f"  - {ip}")
        print(f"结果已保存到 {output_file}")
        print("-" * 50)

# 示例调用
analyze_directory("YaTC_datasets/ISCXVPN2016_MFR/train")
