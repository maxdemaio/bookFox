import requests
# (Reset)
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "dNQrswehPpauusC6kI5wA", "isbns": "9781632168146"})
print(res.json())