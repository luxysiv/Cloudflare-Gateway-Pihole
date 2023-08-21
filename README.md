# Cloudflare-Gateway-Pihole
Create your block ad-lists to Cloudflare Gateway

# Note
Script only support hosts file `0.0.0.0`

# Introduce
Add variable secrets to 
`https://github.com/your-user/your-repository/settings/secrets/actions`
with

CF_ACCOUNT_ID take from Account ID https://dash.cloudflare.com/?to=/:account/workers

CF_TOKEN take from https://dash.cloudflare.com/profile/api-tokens

Secret Github Action like:
</img>https://github.com/slashtechno/cloudflare-gateway-adblocking/issues/8#issuecomment-1679287545<img>

Generate CF_TOKEN like:
</img>https://github.com/slashtechno/cloudflare-gateway-adblocking/issues/8#issuecomment-1676480638<img>

# Credit
This repository run Github Action from source [slashtechno/cloudflare-gateway-adblocking](https://github.com/slashtechno/cloudflare-gateway-adblocking)

# Run on Termux 

```
yes | pkg upgrade -y
yes | pkg install python-pip -y
export CF_ACCOUNT_ID=""
export CF_TOKEN="
"
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
grep "^0\.0\.0\.0" "$tempfile" | awk '!seen[$0]++' | sed '/0\.0\.0\.0 0\.0\.0\.0/d' > "$outfile"
rm "$tempfile"
pip install cloudflare-gateway-adblocking
cloudflare-gateway-adblocking --account-id "$CF_ACCOUNT_ID" --token "$CF_TOKEN" delete
cloudflare-gateway-adblocking --account-id "$CF_ACCOUNT_ID" --token "$CF_TOKEN" upload --blocklists "$outfile"
rm "$outfile"
```

# One line Termux 
```
curl -s https://github.com/luxysiv/Cloudflare-Gateway-Pihole/main/termux.sh | bash
```
