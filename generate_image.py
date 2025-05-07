import os
import glob
import binascii
from PIL import Image
import scapy.all as scapy
from tqdm import tqdm
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def makedir(path):
    """Create a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def read_MFR_bytes(pcap_dir, max_packets=5):
    """Read pcap file and convert it to MFR byte sequence."""
    try:
        packets = scapy.rdpcap(pcap_dir)
        data = []
        for packet in packets[:max_packets]:
            header = (binascii.hexlify(bytes(packet['IP']))).decode()
            try:
                payload = (binascii.hexlify(bytes(packet['Raw']))).decode()
                header = header.replace(payload, '')
            except:
                payload = ''
            header = header[:160].ljust(160, '0')
            payload = payload[:480].ljust(480, '0')
            data.append((header, payload))
        
        # Ensure we have exactly max_packets entries
        while len(data) < max_packets:
            data.append(('0'*160, '0'*480))
        
        final_data = ''.join(h + p for h, p in data)
        return final_data
    except Exception as e:
        logging.error(f"Error processing {pcap_dir}: {e}")
        return None

def process_flow(flow, flows_pcap_path, output_path, image_size=(40, 40)):
    """Process a single flow and save as an image."""
    content = read_MFR_bytes(flow)
    if content:
        content = np.array([int(content[i:i + 2], 16) for i in range(0, len(content), 2)])
        fh = np.reshape(content, image_size)
        fh = np.uint8(fh)
        im = Image.fromarray(fh)
        im.save(flow.replace('.pcap', '.png').replace(flows_pcap_path, output_path))

def MFR_generator(flows_pcap_path, output_path, max_workers=4):
    """Generate MFR images from pcap files using parallel processing."""
    flows = glob.glob(flows_pcap_path + "/*/*/*.pcap")
    makedir(output_path)
    makedir(output_path + "/train")
    makedir(output_path + "/test")
    classes = glob.glob(flows_pcap_path + "/*/*")
    for cla in classes:
        makedir(cla.replace(flows_pcap_path, output_path))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_flow, flow, flows_pcap_path, output_path) for flow in flows]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing flows"):
            future.result()  # To raise any exceptions caught during processing

# Example usage:
# MFR_generator('./path/to/pcap/files', './output/path', max_workers=8)

# Color Encoding: Instead of grayscale, use color channels to encode different types of information (e.g., header, payload, and metadata).
# Feature Extraction: Apply image processing techniques to extract features that could be useful for classification tasks.

# Augmentation Techniques: Apply data augmentation techniques to increase the diversity of the training dataset (e.g., rotation, scaling, noise addition).

# Visualization and Analysis:
# Interactive Visualization: Develop a tool to visualize the generated images interactively, allowing users to explore and analyze the data.
# Statistical Analysis: Integrate statistical analysis to provide insights into the traffic patterns.

if __name__ == "__main__":
    MFR_generator('./datasets', './data/test_MFR_images', max_workers=8)