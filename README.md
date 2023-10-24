# For Everyone

# Credit

* Inspired by [IanDesuyo/CloudflareGatewayAdBlock](https://github.com/IanDesuyo/CloudflareGatewayAdBlock)

* Thanks alot [@nhubaotruong](https://github.com/nhubaotruong) for his contribution 

# Cloudflare-Gateway-Pihole
Create your blocked ad-list using Cloudflare Gateway

> # Note
* Supported white list

* Supported 2 kinds balcklist [adlist.ini](adlist.ini)

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


# Setup
Add variables secrets to your forked repository
`https://github.com/<username>/<repository>/settings/secrets/actions`:

* Grab your Account ID from https://dash.cloudflare.com/?to=/:account/workers and set to `CF_IDENTIFIER`
* `CF_API_TOKEN` take from : https://dash.cloudflare.com/profile/api-tokens with 3 permissions `Account.Zero Trust : Edit` `Account.Account Firewall Access Rules : Edit` `Account.Access: Apps and Policies : Edit`

* Script has 2 backup workflow files that if the upload fails, will run 2 more times every 5 minutes.  So the failure rate will be very low


# Termux

Now you can run on Termux

* Download [Termux](https://github.com/termux/termux-app/releases/latest)

* Copy and paste commands

```
yes | pkg upgrade
yes | pkg install python-pip
yes | pkg install git
git clone https://github.com/luxysiv/Cloudflare-Gateway-Pihole
cd Cloudflare-Gateway-Pihole
nano .env
```

Input your value then 

* Command
```
nano adlist.ini
```
to edit block list

* Command
```
nano whitelist.ini
```
to edit white list

* Command
```
python -m src
```
to upload 

* If Termux not work you can copy and paste this command
```
termux-change-repo
```
Enter 3 times

Next time only use commands to run 
```
cd Cloudflare-Gateway-Pihole
python -m src
```

# Chú ý 

* Supports using any list

* The limit of Cloudflare Gateway Zero Trust free is 300k domains so remember to pay attention to the log, if it exceeds the script will stop

* If you have uploaded lists using another script, you should delete them using the delete feature of the uploaded script or delete them manually
```

* I have updated the feature to delete lists when you no longer need to use the script. Go to [__main__.py](src/__main__.py) as follows:

```python
async def main():
    adlist_urls = read_urls_from_file("adlist.ini")
    whitelist_urls = read_urls_from_file("whitelist.ini")
    adlist_name = "DNS-Filters"
    app = App(adlist_name, adlist_urls, whitelist_urls)
    await app.delete()  # Leave script
    # await app.run()
```

👌 Wishing you success

👌 If you have any questions about the script, you can open an issue