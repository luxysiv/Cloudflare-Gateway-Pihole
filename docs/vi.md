![CF_logo_stacked_whitetype](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/b8b7b12b-2fd8-4978-8e3c-2472a4167acb)

# Dành cho các bạn Việt Nam

Các bạn cần phân biệt `bộ lọc DNS` và `bộ lọc browser`. Mình thấy nhiều bạn đem `bộ lọc browser` lên chạy -> lỗi lướt web

# Hướng dẫn sử dụng

Thêm `Variables Secrets` vào 
`https://github.com/your-user/your-repository/settings/secrets/actions`:

* `CF_IDENTIFIER` được lấy từ tài khoản CF của bạn (dãy ký tự ngay sau `https://dash.cloudflare.com/`: **https://dash.cloudflare.com/?to=/:account/workers**

* `CF_API_TOKEN` lấy từ : **https://dash.cloudflare.com/profile/api-tokens** với `3 permissions`
   1. `Account.Zero Trust : Edit` 
   2. `Account.Account Firewall Access Rules : Edit`
   3. `Account.Access: Apps and Policies : Edit`

hoặc có thể thêm vào **[.env](../.env)** ( **không khuyến khích** )

`Secret Github Action` giống như sau:
![1000015672](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/6bd7f41d-0ca5-4944-95d3-d41dfd913c60)

Tạo `CF_API_TOKEN` giống như sau:
![CF_API_TOKEN](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/a5b90438-26cc-49ae-9a55-5409a90b683f)

# Cài thời gian script tự động chạy 
> Sử dụng Cloudflare Workers để chạy Github Action. Không lo sau 2 tháng Github tắt Action.Tạo Github Token không hết hạn với tất cả các quyền
```javascript
addEventListener('scheduled', event => {
  event.waitUntil(handleScheduledEvent());
});

async function handleScheduledEvent() {
  const GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN_HERE';
  try {
    const dispatchResponse = await fetch('https://api.github.com/repos/YOUR_USER_NAME/YOUR_REPO_NAME/actions/workflows/main.yml/dispatches', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
      },
      body: JSON.stringify({
        ref: 'main'
      }),
    });

    if (!dispatchResponse.ok) throw new Error('Failed to dispatch workflow');
  } catch (error) {
    console.error('Error handling scheduled event:', error);
  }
}
```
Nhớ cài cron trigger cho Cloudflare Workers 

# Chú ý 

* Đã hỗ trợ sử dụng list nào cũng được 

* `Giới hạn` của `Cloudflare Gateway Zero Trust free` là `300k domains` nên các bạn nhớ chú ý log, `nếu quá script sẽ stop`

* Các bạn đã tải các danh sách bộ lọc bằng script khác thì nên xoá đi bằng tính năng xoá của script đã up hoặc xoá tay

* Script có 2 workflows dự phòng nếu tải danh sách chặn lên thất bại sẽ chạy tiếp 2 lần mỗi lần là 5p (hạn chế vượt giới hạn requests của Cloudflare). Cho nên tỉ lệ thất bại sẽ rất thấp

* Nếu không biết thêm vào Secret Github Action thì có thể điền giá trị vào file **[.env](../.env)** và sửa file **[main.yml](../.github/workflows/main.yml)** như sau, loại bỏ các dòng secret env
```yml
- name: Cloudflare Gateway Zero Trust 
  run: python -m src 
```

* Mình đã update thêm tính năng xoá danh sách khi các bạn không muốn sử dụng script nữa. Vào **[__main__.py](../src/__main__.py)** để như sau:

```python
if __name__ == "__main__":
    cloudflare_manager = CloudflareManager(PREFIX, MAX_LISTS, MAX_LIST_SIZE)
    cloudflare_manager.run()
    # cloudflare_manager.leave() # Leave script 
```

* Hỗ trợ **[dynamic_blacklist.txt](../lists/dynamic_blacklist.txt)** và **[dynamic_whitelist.txt](../lists/dynamic_whitelist.txt)** để các bạn tự **chặn hoặc bỏ chặn** tên miền theo ý thích 

* Bạn có thể thay tên **DNS-Filters** bằng các tên bạn thích 

* Thêm danh sách `chặn` của bạn vào **[adlist.ini](../lists/adlist.ini)** và `loại bỏ chặn` ở **[whitelist.ini](../lists/whitelist.ini)**

* Đã hỗ trợ 2 loại định dạng danh sách 

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
