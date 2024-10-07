


import requests
res = requests.get(f'http://127.0.0.1:1712/result/9e96fb5b-e30d-44c4-94d9-8cd30de961e0')
print(res.text)