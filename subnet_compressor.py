import sys
import ipaddress
from tqdm import tqdm
import os
from datetime import datetime

def read_ips_from_file(filename):
    ips = []
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            line = line.split('#')[0].strip()
            if line:
                ips.append(line)
    return ips

def ip_to_cidr(ips):
    ip_objects = (ipaddress.ip_address(ip) for ip in ips)
    ip_objects = sorted(ip_objects)
    cidr_list = []
    i = 0
    n = len(ip_objects)
    while i < n:
        start = ip_objects[i]
        while (i + 1 < n and int(ip_objects[i + 1]) - int(ip_objects[i]) == 1):
            i += 1
        end = ip_objects[i]
        if start == end:
            cidr_list.append(f"{start}/32")
        else:
            cidr = ipaddress.summarize_address_range(start, end)
            cidr_list.extend([str(c) for c in cidr])
        i += 1
    return cidr_list

def count_ips_in_cidr(cidr_list):
    total_ips = 0
    for cidr in cidr_list:
        network = ipaddress.ip_network(cidr, strict=False)
        total_ips += network.num_addresses
    return total_ips

def main(input_file):
    ips = read_ips_from_file(input_file)
    original_count = len(ips)
    print("Processing IP addresses...")
    cidr_notations = ip_to_cidr(ips)
    expanded_count = count_ips_in_cidr(cidr_notations)
    compressed_count = len(cidr_notations)
    base_name, file_ext = os.path.splitext(input_file)
    output_file = f"{base_name}_compressed{file_ext}"
    updated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = (
        f"# Original IP count: {original_count}\n"
        f"# Compressed subnet count: {compressed_count}\n"
        f"# Expanded IP count: {expanded_count}\n"
        f"# Compression ratio: {compressed_count / original_count:.2f}x\n"
        f"# Updated on: {updated_on}\n"
    )
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(header)
        for cidr in cidr_notations:
            file.write(cidr + '\n')
    print(header)
    print(f"CIDR notations written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file.py input.txt")
        sys.exit(1)
    input_file = sys.argv[1]
    main(input_file)
