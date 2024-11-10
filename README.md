![CF_logo_stacked_whitetype](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/b8b7b12b-2fd8-4978-8e3c-2472a4167acb)


# Pihole 風格，但使用 Cloudflare Gateway
`適合開發人員、營運人員以及所有討厭廣告的人。`

使用 Cloudflare Gateway 建立廣告封鎖清單。

### 信用就在那裡
---

> 非常感謝 [@nhubaotruong](https://github.com/nhubaotruong) 感謝他的貢獻.

> 自述文件作者: [@minlaxz](https://github.com/minlaxz).

>> 新增了動態網域篩選（白名單和黑名單）的想法（請檢查「ini」文件，因為您可能還需要修改這些文件）.

>>> 將動態網域篩選器（白名單和黑名單）新增至Actions variables（請檢查 [dynamic_blacklist.txt](./lists/dynamic_blacklist.txt) 和 [dynamic_whitelist.txt](./lists/dynamic_whitelist.txt). 了解新增 "Value*" 的範例).使用 `DYNAMIC_BLACKLIST` 和 `DYNAMIC_WHITELIST` 新增 `Name*` 到 Actions variables 

### 支援的樣式
---
* ini 文件中 有兩種清單：白名單 [whitelist.ini](./lists/whitelist.ini) 和 黑名單 [adlist.ini](./lists/adlist.ini).

```ini
https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt
```
或
```ini
[Ad-Urls]
Adguard = https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt
```

### 自訂 URLs
---
* 新增到文件:
  > 白名單 [whitelist.ini](./lists/whitelist.ini) 和 黑名單 [adlist.ini](./lists/adlist.ini).

* 新增 到 GitHub Action variables:
  > `Name*`
  >> `ADLIST_URLS` or `WHITELIST_URLS`.

  > `Value*` `URLs list`
  >> 範例:
  ```text
  https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt
  https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/light-onlydomains.txt
  ```

*您應該將廣告清單和白名單加入Action variables。如果您更新您的分叉，您的自訂清單將不會遺失。

### 如何設定這個？
---
1. Fork 這 repository 到您的帳戶。
2. 擷取 **Cloudflare Account ID** (之後發現 `https://dash.cloudflare.com/`) 在 ➞ https://dash.cloudflare.com/?to=/:account/workers.
3. 創建您的 **API Token** 在 ➞ https://dash.cloudflare.com/profile/api-tokens 需要3個權限:
   1. `Account.Zero Trust : Edit`
   2. `Account.Account Firewall Access Rules : Edit`
   3. `Account.Access: Apps and Policies : Edit`

4. 新增 **Repository Secrets** 到你的 forked repository:
`➞ https://github.com/<username>/<forked-repository>/settings/secrets/actions`
   1. 設定 **Cloudflare Account ID** 到 `CF_IDENTIFIER`.
   2. 設定 **API Token** 到 `CF_API_TOKEN`.
---
* 免費的「Cloudflare Gateway Zero Trust」的 (*限制* 是 "300000 個網域")，因此 請記得 注意 workflow logs。 如果超過，腳本將停止。

* 如果您使用其他腳本上傳了列表，則應使用上傳腳本的刪除功能刪除它們或手動刪除它們。

* 我更新了當您不再需要使用腳本時刪除清單的功能。 前往 [main.yml](.github/workflows/main.yml) 如下:

```yml
      - name: Cloudflare Gateway Zero Trust 
        run: python -m src leave
```

註釋來自 [@minlaxz](https://github.com/minlaxz):
1. 網域清單樣式: 我個人更喜歡黑名單風格的第二種，它更具可讀性和簡潔性。
2. 動態域名列表: 您也可以使用更新動態（流動）白名單和黑名單 [dynamic_blacklist.txt](./lists/dynamic_blacklist.txt) 和 [dynamic_whitelist.txt](./lists/dynamic_whitelist.txt).
3. 已放棄用使用 `.env`: 在公共儲存庫中設定敏感資訊被認為太危險，因為任何不受歡迎的人都可以輕鬆地從中竊取您的 Cloudflare 憑證 '.env' 檔案.

🥂🥂 乾杯! 🍻🍻
===
