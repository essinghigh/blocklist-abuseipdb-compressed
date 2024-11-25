# AbuseIPDB Blocklist Compression

Inspired by: [borestad/blocklist-abuseipdb](https://github.com/borestad/blocklist-abuseipdb)

I use `ipset` on a little EdgeRouter to drop nasty traffic, so I need to reduce volume where possible. Using this method, I can achieve a 10-15% reduction in total size by combining repeating IPs into subnets.

## Compression Results

As of writing:

### abuseipdb-s100-1d.ipv4
- **Original IP count:** 41464
- **Compressed subnet count:** 34701
- **Compression ratio:** 0.84x

### abuseipdb-s100-3d.ipv4
- **Original IP count:** 44214
- **Compressed subnet count:** 37341
- **Compression ratio:** 0.84x

### abuseipdb-s100-7d.ipv4
- **Original IP count:** 49647
- **Compressed subnet count:** 42551
- **Compression ratio:** 0.86x

### abuseipdb-s100-14d.ipv4
- **Original IP count:** 61142
- **Compressed subnet count:** 53636
- **Compression ratio:** 0.88x

### abuseipdb-s100-30d.ipv4
- **Original IP count:** 78595
- **Compressed subnet count:** 70447
- **Compression ratio:** 0.90x

### abuseipdb-s100-60d.ipv4
- **Original IP count:** 120870
- **Compressed subnet count:** 111654
- **Compression ratio:** 0.92x

### abuseipdb-s100-90d.ipv4
- **Original IP count:** 150983
- **Compressed subnet count:** 140678
- **Compression ratio:** 0.93x

### abuseipdb-s100-120d.ipv4
- **Original IP count:** 175689
- **Compressed subnet count:** 164465
- **Compression ratio:** 0.94x

### abuseipdb-s100-all.ipv4
- **Original IP count:** 752820
- **Compressed subnet count:** 719118
- **Compression ratio:** 0.96x
