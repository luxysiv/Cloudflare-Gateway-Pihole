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
</img>https://github.com/slashtechno/cloudflare-gateway-adblocking/issues/8#issuecomment-1679287545<img>

Generate CF_API_TOKEN like:
[1000015325](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/91e6d793-573c-4e03-91f3-f265d9bd1cdb)

# Credit
This repository modified from source [IanDesuyo/CloudflareGatewayAdBlock](https://github.com/IanDesuyo/CloudflareGatewayAdBlock)

# Chú ý 

* Hiện tại script chỉ hỗ trợ các urls cùng là file hosts hoặc cùng file text domains, không hỗ trợ url dạng ||abc^!

* Giới hạn của Cloudflare Gateway Zero Trust free là 300k domains nên các bạn nhớ chú ý log, nếu quá script sẽ stop

* Các bạn đã up lists bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

👌 Chúc các bạn thành công 
