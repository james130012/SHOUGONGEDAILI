import requests
from urllib.parse import urlparse, parse_qs, unquote
import yaml
import re

def parse_hysteria_url_to_clash(url, index):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # 获取解析后的参数
    host = parsed_url.hostname
    port = parsed_url.port
    upmbps = int(query_params.get('upmbps', [100])[0])
    downmbps = int(query_params.get('downmbps', [100])[0])
    auth = query_params.get('auth', [''])[0]
    insecure = query_params.get('insecure', ['0'])[0] == '1'
    peer = query_params.get('peer', [''])[0]
    alpn = query_params.get('alpn', [''])[0]
    
    # 生成唯一名称
    name = extract_node_name(url)
    if not name:
        name = f"MyHysteriaProxy_{index}"
    
    # 构建 Clash 配置字典
    proxy_config = {
        "name": name,
        "type": "hysteria",
        "server": host,
        "port": port,
        "auth_str": auth,
        "up": upmbps,
        "down": downmbps,
        "obfs": "",
        "sni": peer,
        "alpn": [alpn],
        "skip-cert-verify": insecure
    }
    
    return proxy_config, name

def extract_node_name(url):
    # 使用正则表达式提取节点名称部分
    match = re.search(r'#(.*?)$', url)
    if match:
        # URL解码节点名称
        node_name = unquote(match.group(1))
        return node_name
    return None

# 从URL获取内容
url = "https://raw.githubusercontent.com/dimzon/scaling-sniffle/main/freedom/hysteria.txt"
response = requests.get(url)
if response.status_code == 200:
    data = response.text
else:
    print(f"无法从URL获取数据，状态码：{response.status_code}")
    data = ""

# 存储所有代理配置的列表
proxies = []
proxy_names = []

# 逐行读取内容并解析 URL
lines = data.splitlines()
for index, line in enumerate(lines):
    url = line.strip()  # 去除行末的换行符和空格
    if url:
        proxy_config, proxy_name = parse_hysteria_url_to_clash(url, index)
        proxies.append(proxy_config)
        proxy_names.append(proxy_name)

# 构建 Clash 总配置
clash_config = {
    "proxies": proxies,
    "proxy-groups": [
        {
            "name": "Auto",
            "type": "select",
            "proxies": proxy_names
        }
    ],
    "rules": [
        "DOMAIN-SUFFIX,example.com,Auto",
        "GEOIP,CN,DIRECT",
        "MATCH,Auto"
    ]
}

# 将配置写入 YAML 文件
with open("clash_config.yaml", "w", encoding='utf-8') as file:
    yaml.dump(clash_config, file, allow_unicode=True)

print("配置文件生成成功：clash_config.yaml")

# 等待用户输入以防窗口关闭
input("按任意键退出...")
