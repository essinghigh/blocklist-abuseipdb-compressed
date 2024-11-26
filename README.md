# AbuseIPDB Blocklist Compression

Inspired by: [borestad/blocklist-abuseipdb](https://github.com/borestad/blocklist-abuseipdb)

Please note that this repo is reliant on the above project and cannot exist without it, please support the original creator as the vast majority of the legwork is done by them.

I use `ipset` on a little EdgeRouter to drop nasty traffic, so I need to reduce volume where possible to fit within the maxlen of 65535. Using this method, I can achieve a 10-15% reduction in total size by combining contiguous IPs into subnets.

Compression Results can be found in each file. Please refer to borestad's repo for more information.

Please [support](https://www.abuseipdb.com/pricing) AbuseIPDB who make this data available.
