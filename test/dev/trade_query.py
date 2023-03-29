import json

import requests

league = "Sanctum"

search_url = f"https://www.pathofexile.com/api/trade/search/{league}"
fetch_api = f"https://www.pathofexile.com/api/trade/fetch"
payload = {
    "query": {
        "filters": {
            "trade_filters": {
                "disabled": False,
                "filters": {
                    "price": {
                        "min": 1,
                        "max": 30
                    }
                }
            }
        },
        "status": {
            "option": "online"
        },
        "stats": [
            {
                "type": "and",
                "filters": []
            }
        ],
        # "name": "Divergent Spark",
        "type": "Spark"
    },
    "sort": {
        "price": "asc"
    }
}
gem_name = "DIVERGENT HERALD OF AGONY"
query = {"query":{"status":{"option":"online"},"term":gem_name,"stats":[{"type":"and","filters":[]}],"filters":{"misc_filters":{"filters":{"corrupted":{"option":"false"}}}}},"sort":{"price":"asc"}}


headers = {
    'User-Agent': 'Firefox 93.0',
    'From': 'peters@gmail.com'  # This is another valid field
}
r = requests.post(search_url, json=query, headers=headers)
body = json.loads(r.text)

#todo not hard code 10 but if there are fewer results -> fewer fetches
#todo abort if no results (prolly phantasmal XY gem doesnt exist)
r = requests.get(f"{fetch_api}/{','.join(body['result'][:10])}",params={"query":body['id']},headers=headers)
gems = json.loads(r.text)

avg_price = []
for result in gems["result"]:
    price = result["listing"]["price"]
    if price["currency"] == "chaos":
        avg_price.append(price["amount"])
    elif price["currency"] == "divine":
        avg_price.append(price["amount"]*250)
    else:
        continue

avg_price = sum(avg_price)/len(avg_price)
print(f"gem: {gem_name} had average price {avg_price}")