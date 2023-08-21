yes | pkg upgrade -y
yes | pkg install python-pip -y
pkg install git
git clone https://github.com/manhduonghn/cloudflare-gateway-adblocking
cd cloudflare-gateway-adblocking
nano .env
nano hosts-urls.ini
python -m src delete
python -m src --timeout 600 upload 
