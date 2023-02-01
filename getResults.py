import requests, time, random
import pandas as pd
resp = requests.get('https://www.sslproxies.org') 
df = pd.read_html(resp.text)[0]
df = df[["IP Address", "Port", "Https"]]
df["IP Address"] = df["IP Address"] + ":" + df["Port"].astype(str)
df = df[["IP Address", "Https"]]
someList = df.values.tolist()
proxyList = []
for proxy in someList:
    if proxy[1] == "no":
        proxyList.append({"http":proxy[0]})
    else:
        proxyList.append({"https":proxy[0]})

landingPage = "https://airover.travel/"
resultsPage = "https://airover.travel/result"


#print(proxyList)
'''
for proxy in proxyList:
    try:
        firstResponse = requests.get(landingPage, proxies=proxy)
        secondResponse = requests.get(resultsPage, proxies=proxy)
    except:
        continue
'''
anotherList = []
moreProxies = [
"190.60.37.50:999",
"191.101.58.7:999",
"95.217.62.36:3128",
"20.81.62.32:3128",
"47.242.52.247:3128",
"8.219.97.248:80",
"87.200.7.252:3128",
"47.242.48.178:3128",
"52.199.142.215:3128",
"18.180.165.62:8080",
"194.233.95.214:3128",
"78.111.97.180:8080",
"103.253.27.150:2030",
"62.193.99.174:80",
"47.243.91.156:3128",
"212.23.217.74:8080",
"78.137.248.41:3128",
"64.189.24.250:3129",
"65.20.159.245:8080",
"118.218.126.57:80",
"165.225.114.85:10605",
"62.193.108.140:1976",
"103.23.20.68:3128",
"104.248.40.98:80",
"202.47.80.75:80",
"170.81.240.235:999",
"181.78.19.197:999",
"45.4.219.92:8080",
"103.108.158.123:8181",
"165.225.104.94:10286",
"103.36.8.244:8080",
"118.218.126.53:9401",
"181.198.11.204:8889",
"88.218.251.189:8080",
"185.235.42.199:443"
]

for server in moreProxies:
    anotherList.append({"https":server})

for proxy in anotherList:
    try:
        firstResponse = requests.get(landingPage, proxies=proxy)
        secondResponse = requests.get(landingPage, proxies=proxy)
        thirdResponse = requests.get(resultsPage, proxies=proxy)
    except:
        continue
    time.sleep(random.randint(1, 60))
