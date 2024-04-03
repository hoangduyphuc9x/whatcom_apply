import requests

proxyip = "http://lumi-meodihere_area-JP_city-OSAKA_life-30_session-peFGUROwpX:12345678yukonmeo@eu.lumiproxy.com:5888"
url = "https://api.ipify.org?format=json"
proxies={
    'http':proxyip,
    'https':proxyip,
}
data = requests.get(url=url,proxies=proxies)
print(data.json())