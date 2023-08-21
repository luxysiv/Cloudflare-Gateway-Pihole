yes | pkg upgrade && pkg install python-pip git -y
git clone https://github.com/manhduonghn/cloudflare-gateway-adblocking
cd cloudflare-gateway-adblocking
pip install -r requirements.txt
nano .env
nano hosts-urls.ini
python -m src delete
python -m src --timeout 600 upload 
