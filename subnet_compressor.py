import ipaddress
from ipaddress import IPv4Address
import os
import requests
from datetime import datetime
from typing import List, Iterator

IPV4_URLS = [
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-120d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-14d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-1d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-30d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-3d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-60d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-7d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-90d.ipv4",
    "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-all.ipv4",
]


def download_files(urls: List[str]) -> None:
    """
    Downloads files from the given URLs to the 'downloads' directory.

    Args:
        urls (List[str]): A list of URLs to download from.
    """
    os.makedirs("downloads", exist_ok=True)
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join("downloads", url.split("/")[-1])
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")


def read_ips_from_file(filename: str) -> Iterator[str]:
    """
    Reads IP addresses from a file, yielding each IP address.

    Args:
        filename (str): The path to the file containing IP addresses.

    Yields:
        str: Each IP address found in the file.
    """
    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.split("#")[0].strip()
            if line:
                yield line


def ip_to_cidr(ips: List[str]) -> List[str]:
    """
    Converts a list of IP addresses to CIDR notations by summarizing consecutive ranges.

    Args:
        ips (List[str]): A list of IP addresses as strings.

    Returns:
        List[str]: A list of CIDR notations representing the compressed IP ranges.
    """
    ip_objects: List[IPv4Address] = sorted(IPv4Address(ip) for ip in ips)
    cidr_list: List[str] = []
    i = 0
    n = len(ip_objects)
    while i < n:
        start = ip_objects[i]
        while i + 1 < n and int(ip_objects[i + 1]) - int(ip_objects[i]) == 1:
            i += 1
        end = ip_objects[i]
        if start == end:
            cidr_list.append(f"{start}/32")
        else:
            cidr = ipaddress.summarize_address_range(start, end)
            cidr_list.extend(str(c) for c in cidr)
        i += 1
    return cidr_list


def count_ips_in_cidr(cidr_list: List[str]) -> int:
    """
    Counts the total number of IP addresses represented by a list of CIDR notations.

    Args:
        cidr_list (List[str]): A list of CIDR notations.

    Returns:
        int: The total number of IP addresses.
    """
    return sum(
        ipaddress.ip_network(cidr, strict=False).num_addresses for cidr in cidr_list
    )


def process_file(input_file: str) -> None:
    """
    Processes an input file containing IP addresses, compresses them into CIDR notations,
    and writes the compressed output to a new file with statistics.

    Args:
        input_file (str): The path to the input file containing IP addresses.
    """
    ips = list(read_ips_from_file(input_file))
    original_count = len(ips)
    print(f"Processing {input_file}...")
    cidr_notations = ip_to_cidr(ips)
    expanded_count = count_ips_in_cidr(cidr_notations)
    compressed_count = len(cidr_notations)

    base_name, file_ext = os.path.splitext(os.path.basename(input_file))
    output_file = f"{base_name}_compressed{file_ext}"

    updated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = (
        f"# Original IP count: {original_count}\n"
        f"# Compressed CIDR count: {compressed_count}\n"
        f"# Expanded IP count: {expanded_count}\n"
        f"# Compression ratio: {compressed_count / original_count:.2f}x\n"
        f"# Updated on: {updated_on}\n"
    )
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(header)
        file.write("\n".join(cidr_notations) + "\n")
    print(header)
    print(f"CIDR notations written to {output_file}")


def main() -> None:
    """
    Main function that downloads files and processes each downloaded IPv4 file.
    """
    download_files(IPV4_URLS)
    ipv4_files = [f for f in os.listdir("downloads") if f.endswith(".ipv4")]
    if not ipv4_files:
        print("No .ipv4 files found in the downloads directory.")
        return

    for input_file in ipv4_files:
        process_file(os.path.join("downloads", input_file))


if __name__ == "__main__":
    main()
