#!/bin/bash
#source .env
urls=(
    https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
    https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
    https://raw.githubusercontent.com/luxysiv/hosts/main/hosts.txt
)
outfile="hosts.txt"
tempfile="temp.txt"
for url in "${urls[@]}"
do
    curl -s "$url" >> "$tempfile"
    echo >> "$tempfile"
done
grep "^0\.0\.0\.0" "$tempfile" | awk '!seen[$0]++' | sort > "$outfile"
rm "$tempfile"
pip install cloudflare-gateway-adblocking
cloudflare-gateway-adblocking --account-id "$CF_ACCOUNT_ID" --token "$CF_TOKEN" delete
cloudflare-gateway-adblocking --account-id "$CF_ACCOUNT_ID" --token "$CF_TOKEN" upload --blocklists "$outfile"
rm "$outfile"
