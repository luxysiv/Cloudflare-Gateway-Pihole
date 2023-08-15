#!/bin/bash
#source .env
urls=(
    https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
    https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
)
outfile="hosts.txt"
for url in "${urls[@]}"
do
    curl -s "$url" >> "$outfile"
    echo >> "$outfile"
done
pip install cloudflare-gateway-adblocking
cloudflare-gateway-adblocking --account-id "$CF_ACCOUNT_ID" --token "$CF_TOKEN" delete
cloudflare-gateway-adblocking --account-id "$CF_ACCOUNT_ID" --token "$CF_TOKEN" upload --blocklists "$outfile"
rm build.sh
