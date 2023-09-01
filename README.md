# Credit
This repository modified from source [IanDesuyo/CloudflareGatewayAdBlock](https://github.com/IanDesuyo/CloudflareGatewayAdBlock)

# Cloudflare-Gateway-Pihole
Create your block ad-lists to Cloudflare Gateway

# Note
* Script only support same urls hosts file or same urls domains,not mix

* Add your lists to [lists.ini](lists.ini)

# Introduce
Add variables secrets to 
`https://github.com/your-user/your-repository/settings/secrets/actions`
with

`CF_IDENTIFIER` take from Account ID https://dash.cloudflare.com/?to=/:account/workers

`CF_API_TOKEN` take from https://dash.cloudflare.com/profile/api-tokens

or add to  [env](.env)

# Use .env

If you add `CF_IDENTIFIER` and `CF_API_TOKEN` to [.env](.env) , you must edit [main.yml](.github/workflows/main.yml) like this 
![1000015344](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/57bbaf33-daa7-46e5-acdd-4d5f64a69d5f)

# More informations about Secret Github Action and API TOKEN 

Secret Github Action like:
![1000015325](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/403a1174-cd4e-4854-9911-d03722bbb91b)


Generate `CF_API_TOKEN` like:
![CF_API_TOKEN](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/a5b90438-26cc-49ae-9a55-5409a90b683f)

# Chú ý 

* Hiện tại script chỉ hỗ trợ các urls cùng là file hosts hoặc cùng file text domains, không hỗ trợ url dạng ||abc^!

* Giới hạn của Cloudflare Gateway Zero Trust free là 300k domains nên các bạn nhớ chú ý log, nếu quá script sẽ stop

* Các bạn đã up lists bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

* Nếu không biết thêm vào Secret Github Action thì có thể điền giá trị vào file [.env](.env) và sửa file [main.yml](.github/workflows/main.yml) như sau
![1000015344](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/57bbaf33-daa7-46e5-acdd-4d5f64a69d5f)

* Mình đã update thêm tính năng xoá lists khi các bạn không cần sử dụng script nữa. Vào [main.py](main.py) để như sau
![1000015349](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/2cfe6b02-09b5-4d92-888e-73ae92a90c59)

* Bạn có thể thay tên ManhDuong bằng các tên bạn thích 

* Thêm danh sách của bạn vào [lists.ini](lists.ini)

👌 Chúc các bạn thành công 

👌 Mọi thắc mắc về script các bạn có thể mở issue
