# Dành cho các bạn Việt Nam

Các bạn cần phân biệt bộ lọc DNS và bộ lọc browser. Mình thấy nhiều bạn đem bộ lọc browser lên chạy -> lỗi lướt web

# Hướng dẫn sử dụng

Thêm Variables Secret vào 
`https://github.com/your-user/your-repository/settings/secrets/actions`:

* `CF_IDENTIFIER` được lấy từ tài khoản CF của bạn: https://dash.cloudflare.com/?to=/:account/workers

* `CF_API_TOKEN` lấy từ : https://dash.cloudflare.com/profile/api-tokens with 3 permissions `Account.Zero Trust : Edit` `Account.Account Firewall Access Rules : Edit` `Account.Access: Apps and Policies : Edit`

hoặc có thể thêm vào [.env](.env) (không khuyến khích)

Secret Github Action giống như sau:
![1000015672](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/6bd7f41d-0ca5-4944-95d3-d41dfd913c60)

Tạo `CF_API_TOKEN` giống như sau:
![CF_API_TOKEN](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/a5b90438-26cc-49ae-9a55-5409a90b683f)

# Chú ý 

* Đã hỗ trợ sử dụng list nào cũng được 

* Giới hạn của Cloudflare Gateway Zero Trust free là 300k domains nên các bạn nhớ chú ý log, nếu quá script sẽ stop

* Các bạn đã up lists bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

* Script có 2 files workflow dự phòng nếu upload thất bại sẽ chạy tiếp 2 lần sau mỗi 5p. Cho nên tỉ lệ fail sẽ rất thấp

* Nếu không biết thêm vào Secret Github Action thì có thể điền giá trị vào file [.env](.env) và sửa file [main.yml](.github/workflows/main.yml) , [re-run.yml](.github/workflows/re-run.yml) và [re-run2.yml](.github/workflows/re-run2.yml) như sau, loại bỏ các dòng secret env
```yml
- name: Cloudflare Gateway Zero Trust 
  run: python -m src 
```

* Mình đã update thêm tính năng xoá lists khi các bạn không cần sử dụng script nữa. Vào [__main__.py](src/__main__.py) để như sau:

```python
async def main():
    adlist_urls = read_urls_from_file("adlist.ini")
    whitelist_urls = read_urls_from_file("whitelist.ini")
    adlist_name = "DNS-Filters"
    app = App(adlist_name, adlist_urls, whitelist_urls)
    await app.delete()  # Leave script
    # await app.run()
```

* Hỗ trợ [dynamic_blacklist.txt](dynamic_blacklist.txt) và [dynamic_whitelist.txt](dynamic_whitelist.txt) để các bạn tự chặn hoặc bỏ chặn tên miền theo ý thích 

* Bạn có thể thay tên `DNS-Filters` bằng các tên bạn thích 

* Thêm danh sách chặn của bạn vào [adlist.ini](adlist.ini) và loại bot chặn ở [whitelist.ini](whitelist.ini)

* Đã hỗ trợ 2 loại định dạng list

```ini
https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
```
hoặc
```ini
[Hosts-Urls]
hostsVN = https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
```


👌 Chúc các bạn thành công 

👌 Mọi thắc mắc về script các bạn có thể mở issue
