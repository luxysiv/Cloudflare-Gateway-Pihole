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

![1000015362](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/ce7d552a-aa4b-4fcf-9b69-f0d8287fd2a1)

or
![1000015364](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/373467b5-1798-4dc5-b49e-a9fdf64a3ad7)

* Supported white list 

# Introduce
Add variables secrets to 
`https://github.com/your-user/your-repository/settings/secrets/actions`
with

`CF_IDENTIFIER` take from Account ID https://dash.cloudflare.com/?to=/:account/workers

`CF_API_TOKEN` take from https://dash.cloudflare.com/profile/api-tokens

or add to  [.env](.env)

# Use .env

If you add `CF_IDENTIFIER` and `CF_API_TOKEN` to [.env](.env) , you must edit [main.yml](.github/workflows/main.yml) like this 
![1000015673](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/d7f5663b-0d47-4958-acbc-0d8efb7cc0e9)



# More informations about Secret Github Action and API TOKEN 

Secret Github Action like:
![1000015672](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/6bd7f41d-0ca5-4944-95d3-d41dfd913c60)



Generate `CF_API_TOKEN` like:
![CF_API_TOKEN](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/a5b90438-26cc-49ae-9a55-5409a90b683f)

# Chú ý 

* Đã hỗ trợ sử dụng list nào cũng được 

* Giới hạn của Cloudflare Gateway Zero Trust free là 300k domains nên các bạn nhớ chú ý log, nếu quá script sẽ stop

* Các bạn đã up lists bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

* Nếu không biết thêm vào Secret Github Action thì có thể điền giá trị vào file [.env](.env) và sửa file [main.yml](.github/workflows/main.yml) như sau
![1000015673](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/d7f5663b-0d47-4958-acbc-0d8efb7cc0e9)

* Mình đã update thêm tính năng xoá lists khi các bạn không cần sử dụng script nữa. Vào [__main__.py](src/__main__.py) để như sau
![1000015676](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/1fd1b1ad-5644-419a-9d30-43f0ab0784af)


* Đã thêm tính năng white lists

* Bạn có thể thay tên ManhDuong bằng các tên bạn thích 

* Thêm danh sách của bạn vào [lists.ini](lists.ini)

* Đã hỗ trợ 2 loại [lists.ini](lists.ini)

![1000015362](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/ce7d552a-aa4b-4fcf-9b69-f0d8287fd2a1)

hoặc
![1000015364](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/373467b5-1798-4dc5-b49e-a9fdf64a3ad7)


👌 Chúc các bạn thành công 

👌 Mọi thắc mắc về script các bạn có thể mở issue
