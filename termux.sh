yes | pkg upgrade -y
yes | pkg install python-pip -y
yes | pkg install git -y
git clone | https://github.com/manhduonghn/cloudflare-gateway-adblocking
cd cloudflare-gateway-adblocking
nano .env.example
nano hosts-urls.ini
python -m src delete
python -m src --timeout 600 upload 
