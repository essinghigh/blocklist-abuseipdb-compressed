import ipaddress
from typing import List, Tuple
import re
import multiprocessing as mp
from tqdm import tqdm
import sys
import os
from intervaltree import Interval, IntervalTree

def parse_ip_list(content: str) -> List[str]:
    ip_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    ips = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            match = re.match(ip_pattern, line)
            if match:
                ips.append(match.group(1))
    return sorted(list(set(ips)))

def get_network_address(ip: str, prefix_length: int) -> str:
    network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
    return str(network.network_address)

def find_optimal_subnet_for_chunk(chunk_data: Tuple[List[str], int, int]) -> List[str]:
    ips, start_idx, chunk_size = chunk_data
    chunk = sorted(ips[start_idx:start_idx + chunk_size], key=lambda x: int(ipaddress.IPv4Address(x)))
    if not chunk:
        return []
    optimized_subnets = []
    i = 0
    while i < len(chunk):
        current_ip = chunk[i]
        current_ip_int = int(ipaddress.IPv4Address(current_ip))
        j = i + 1
        while j < len(chunk) and int(ipaddress.IPv4Address(chunk[j])) == current_ip_int + (j - i):
            j += 1
        first_ip = chunk[i]
        last_ip = chunk[j - 1]
        first_ip_int = int(ipaddress.IPv4Address(first_ip))
        last_ip_int = int(ipaddress.IPv4Address(last_ip))
        prefix_length = 32
        while prefix_length > 0:
            network = ipaddress.IPv4Network(f"{first_ip}/{prefix_length}", strict=False)
            if int(network.network_address) == first_ip_int and int(network.broadcast_address) == last_ip_int:
                optimized_subnets.append(f"{str(network.network_address)}/{prefix_length}")
                break
            prefix_length -= 1
        i = j
    return optimized_subnets

def merge_overlapping_subnets(subnets: List[str]) -> List[str]:
    if not subnets:
        return []
    subnets = sorted(subnets, key=lambda x: int(ipaddress.IPv4Network(x).network_address))
    merged_subnets = []
    current_network = ipaddress.IPv4Network(subnets[0])

    for subnet in subnets[1:]:
        next_network = ipaddress.IPv4Network(subnet)
        if current_network.overlaps(next_network):
            combined_network = ipaddress.summarize_address_range(
                current_network.network_address, next_network.broadcast_address)
            current_network = list(combined_network)[0]
        else:
            merged_subnets.append(str(current_network))
            current_network = next_network
    merged_subnets.append(str(current_network))
    return merged_subnets


def optimize_subnets_parallel(ips: List[str], num_processes: int = None) -> List[str]:
    if not ips:
        return []
    if num_processes is None:
        num_processes = mp.cpu_count()
    ips = sorted(ips, key=lambda x: int(ipaddress.IPv4Address(x)))
    chunk_size = max(1000, len(ips) // (num_processes * 4))
    chunks = [(ips, i, chunk_size) for i in range(0, len(ips), chunk_size)]
    with mp.Pool(processes=num_processes) as pool:
        results = list(tqdm(pool.imap(find_optimal_subnet_for_chunk, chunks), total=len(chunks), desc="Processing IP chunks", unit="chunk"))
    optimized_subnets = [subnet for chunk_result in results for subnet in chunk_result]
    return sorted(optimized_subnets, key=lambda x: (int(ipaddress.IPv4Network(x).network_address), int(x.split('/')[1])))

def expand_subnets(subnets: List[str]) -> int:
    expanded_ip_count = 0
    for subnet in subnets:
        network = ipaddress.IPv4Network(subnet, strict=False)
        if network.prefixlen == 32:
            expanded_ip_count += 1
        else:
            expanded_ip_count += network.num_addresses
    return expanded_ip_count


def main(input_content: str, num_processes: int = None) -> Tuple[List[str], dict]:
    original_ips = parse_ip_list(input_content)
    optimized_subnets = optimize_subnets_parallel(original_ips, num_processes=num_processes)
    merged_subnets = merge_overlapping_subnets(optimized_subnets)
    expanded_ip_count = expand_subnets(merged_subnets)
    stats = {
        "original_ip_count": len(original_ips),
        "optimized_subnet_count": len(merged_subnets),
        "expanded_ip_count": expanded_ip_count,
        "compression_ratio": (len(original_ips) - len(merged_subnets)) / len(original_ips) * 100
    }
    return merged_subnets, stats

if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    if len(sys.argv) == 1:
        input_content = sys.stdin.read()
        original_filename = "stdin"
    else:
        original_filename = sys.argv[1]
        with open(original_filename, 'r', encoding='utf-8', errors='replace') as f:
            input_content = f.read()

    optimized_subnets, stats = main(input_content, num_processes=mp.cpu_count())

    print(f"\nStatistics:")
    print(f"Original IP count: {stats['original_ip_count']:,}")
    print(f"Optimized subnet count: {stats['optimized_subnet_count']:,}")
    print(f"Expanded IP count: {stats['expanded_ip_count']:,}")
    print(f"Compression ratio: {stats['compression_ratio']:.2f}%\n")

    base, ext = os.path.splitext(original_filename)
    output_filename = f"{base}_compressed{ext}"

    with open(output_filename, 'w') as output_file:
        output_file.write(f"# {output_filename} - Compressed\n# Statistics:\n# Original IP count: {stats['original_ip_count']:,}\n# Optimized subnet count: {stats['optimized_subnet_count']:,}\n# Expanded IP count: {stats['expanded_ip_count']:,}\n# Compression ratio: {stats['compression_ratio']:.2f}%\n\n")
        for subnet in optimized_subnets:
            output_file.write(f"{subnet}\n")

    print(f"Optimized subnets written to {output_filename}")