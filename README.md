![CF_logo_stacked_whitetype](https://github.com/luxysiv/Cloudflare-Gateway-Pihole/assets/46205571/b8b7b12b-2fd8-4978-8e3c-2472a4167acb)

**[English](README.md)** | **[Việt Nam](docs/vi.md)**

# Pihole styled, but using Cloudflare Gateway
`For Devs, Ops, and everyone who hates Ads.`

Create your ad blocklist using Cloudflare Gateway

### Credit goes there.
---

> First inspired by [IanDesuyo/CloudflareGatewayAdBlock](https://github.com/IanDesuyo/CloudflareGatewayAdBlock).

> Thanks alot to [@nhubaotruong](https://github.com/nhubaotruong) for his contributions.

> Readme by [@minlaxz](https://github.com/minlaxz).

>> Added dynamic domain filter (whitelist and blacklist) idea (please check `ini` files, as you may also need to modify those.)

### Supported styles
---
* White list [whitelist.ini](./lists/whitelist.ini) and block list [adlist.ini](./lists/adlist.ini)
* Two kinds of lists

```ini
https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
```
or
```ini
[Hosts-Urls]
hostsVN = https://raw.githubusercontent.com/bigdargon/hostsVN/master/option/hosts-VN
```


### How to set this up?
---
1. Fork this repository to your account.
2. Grab your **Cloudflare Account ID** (which after `https://dash.cloudflare.com/`) from ➞ https://dash.cloudflare.com/?to=/:account/workers
3. Create your **API Token** from ➞ https://dash.cloudflare.com/profile/api-tokens with 3 permissions 
   1. `Account.Zero Trust : Edit` 
   2. `Account.Account Firewall Access Rules : Edit`
   3. `Account.Access: Apps and Policies : Edit`

4. Add **Repository Secrets** to your forked repository
`➞ https://github.com/<username>/<forked-repository>/settings/secrets/actions`
   1. Set **Cloudflare Account ID** to `CF_IDENTIFIER`
   2. Set **API Token** to `CF_API_TOKEN`


#### Note
---
> Github Actions: it has 2 dependent backup workflows [re-run](.github/workflows/re-run.yml) and [re-run2]([re-run](.github/workflows/re-run2.yml)) in case if the **[main workflow](.github/workflows/main.yml)** fails, 

> They will retry after 5 minutes one after another only if the **main workflow** has been failed (not cancelled - if you cancelled the main workflow manually, they will not be triggered anyway).

### Schedule 
---
> Because limited 2 months commited from Github Actions. So you can create and paste this code to run on Cloudflare Workers. Remember,Github Token generate no expired and all permissions
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
>> Remember set up Cloudflare Workers triggers

### Note
---
* The **limit** of `Cloudflare Gateway Zero Trust` free is **300k domains** so remember to pay attention to the workflow logs, `if it is exceeded, the script will stop`

* If you have uploaded lists using another script, you should delete them using the delete feature of the uploaded script or delete them manually

* I have updated the feature to delete lists when you no longer need to use the script. Go to [__main__.py](src/__main__.py) as follows:

```python
async def main():
    adlist_urls = utils.read_urls_from_file("./lists/adlist.ini")
    whitelist_urls = utils.read_urls_from_file("./lists/whitelist.ini")
    adlist_name = "DNS-Filters"
    cloudflaremanager = CloudflareManager(adlist_name, adlist_urls, whitelist_urls)
    await cloudflaremanager.leave()  # Leave script
    # await cloudflaremanager.run()
```

Note from [@minlaxz](https://github.com/minlaxz):
1. Domain list style: I personally preferred second one in blacklist styles, which has more readablity and concise.
2. Dynamic domain list: You can also update your dynamic (fluid) whitelist and blacklist using [dynamic_blacklist.txt](./lists/dynamic_blacklist.txt) and [dynamic_whitelist.txt](./lists/dynamic_whitelist.txt)
3. Deprected using `.env` : Setting sensitive information inside a public repository is considered too dangerous use-case, since any unwanted person could easily steal your Cloudflare credentials from that `.env` file.



 🥂🥂 Cheers! 🍻🍻
===
