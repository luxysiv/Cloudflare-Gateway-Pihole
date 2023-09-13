# Dành cho các bạn Việt Nam

Các bạn cần phân biệt bộ lọc DNS và bộ lọc browser. Mình thấy nhiều bạn đem bộ lọc browser lên chạy -> lỗi lướt web

# Credit

* This repository modified from source [IanDesuyo/CloudflareGatewayAdBlock](https://github.com/IanDesuyo/CloudflareGatewayAdBlock)

* Thanks alot [@nhubaotruong](https://github.com/nhubaotruong) for his contribute 

# Cloudflare-Gateway-Pihole
Create your block ad-lists to Cloudflare Gateway

# Note

* Supported mix list

* Add your lists to [lists.ini](lists.ini)

* Supported 2 kind of [lists.ini](lists.ini)

```ini
https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
https://raw.githubusercontent.com/Yhonay/antipopads/master/hosts
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/light-onlydomains.txt
```
or
```ini
[Hosts-Urls]
hostsVN = https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
Antipopup = https://raw.githubusercontent.com/Yhonay/antipopads/master/hosts
Hagezi = https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/light-onlydomains.txt
```

* Supported white list 

# Introduce
Add variables secrets to 
`https://github.com/your-user/your-repository/settings/secrets/actions`:

* `CF_IDENTIFIER` from your Account ID from : https://dash.cloudflare.com/?to=/:account/workers

* `CF_API_TOKEN` take from : https://dash.cloudflare.com/profile/api-tokens with 3 permissions `Account.Zero Trust : Edit` `Account.Account Firewall Access Rules : Edit` `Account.Access: Apps and Policies : Edit`

or add to  [.env](.env)

# Use .env

If you add `CF_IDENTIFIER` and `CF_API_TOKEN` to [.env](.env) , you must edit [main.yml](.github/workflows/main.yml) like this, remove secret env:

```yml
- name: Install Dependencies
  run: pip install -r requirements.txt
          
- name: Cloudflare Gateway Zero Trust 
  run: python -m src 
```

# More informations about Secret Github Action and API TOKEN 

Secret Github Action like:
![1000015672](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/6bd7f41d-0ca5-4944-95d3-d41dfd913c60)



Generate `CF_API_TOKEN` like:
![CF_API_TOKEN](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/a5b90438-26cc-49ae-9a55-5409a90b683f)

# Chú ý 

* Đã hỗ trợ sử dụng list nào cũng được 

* Giới hạn của Cloudflare Gateway Zero Trust free là 300k domains nên các bạn nhớ chú ý log, nếu quá script sẽ stop

* Các bạn đã up lists bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

* Nếu không biết thêm vào Secret Github Action thì có thể điền giá trị vào file [.env](.env) và sửa file [main.yml](.github/workflows/main.yml) như sau, loại bỏ các dòng secret env
```yml
- name: Install Dependencies
  run: pip install -r requirements.txt
          
- name: Cloudflare Gateway Zero Trust 
  run: python -m src 
```

* Mình đã update thêm tính năng xoá lists khi các bạn không cần sử dụng script nữa. Vào [__main__.py](src/__main__.py) để như sau:

```python
for _ in range(3):
        try:
            await app.run()
            success = True
            break  
        except Exception:
            await asyncio.sleep(60)
    return 0 if success else 1
```


* Đã thêm tính năng white lists

* Bạn có thể thay tên `DNS-Filters` bằng các tên bạn thích 

* Thêm danh sách của bạn vào [lists.ini](lists.ini)

* Đã hỗ trợ 2 loại [lists.ini](lists.ini)

```ini
https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
https://raw.githubusercontent.com/Yhonay/antipopads/master/hosts
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/light-onlydomains.txt
```
hoặc
```ini
[Hosts-Urls]
hostsVN = https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
Antipopup = https://raw.githubusercontent.com/Yhonay/antipopads/master/hosts
Hagezi = https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/light-onlydomains.txt
```


👌 Chúc các bạn thành công 

👌 Mọi thắc mắc về script các bạn có thể mở issue
