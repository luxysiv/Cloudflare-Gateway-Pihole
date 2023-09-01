# Cloudflare-Gateway-Pihole
Create your block ad-lists to Cloudflare Gateway

# Note
Script only support same urls hosts file or same urls domains,not mix

# Introduce
Add variable secrets to 
`https://github.com/your-user/your-repository/settings/secrets/actions`
with

CF_IDENTIFIER take from Account ID https://dash.cloudflare.com/?to=/:account/workers

CF_API_TOKEN take from https://dash.cloudflare.com/profile/api-tokens

Secret Github Action like:
![1000015325](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/403a1174-cd4e-4854-9911-d03722bbb91b)


Generate CF_API_TOKEN like:
![CF_API_TOKEN](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/a5b90438-26cc-49ae-9a55-5409a90b683f)


# Credit
This repository modified from source [IanDesuyo/CloudflareGatewayAdBlock](https://github.com/IanDesuyo/CloudflareGatewayAdBlock)

# Chú ý 

* Hiện tại script chỉ hỗ trợ các urls cùng là file hosts hoặc cùng file text domains, không hỗ trợ url dạng ||abc^!

* Giới hạn của Cloudflare Gateway Zero Trust free là 300k domains nên các bạn nhớ chú ý log, nếu quá script sẽ stop

* Các bạn đã up lists bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

* Nếu không biết thêm vào Secret Github Action thì có thể điền giá trị vào file [.env](.env) và xoá phần dưới của dòng `python main.py` của file [main.yml](.github/workflows/main.yml) như sau
  

👌 Chúc các bạn thành công 
