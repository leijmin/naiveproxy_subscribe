from flask.views import MethodView
from flask import Flask, jsonify, make_response, request
import os
import yaml
import requests
import base64
import json

app = Flask(__name__)

###############################################################################
# 1) 构建 Clash YAML
###############################################################################
def build_clash_yaml(config_data: dict) -> str:
    """
    将节点信息转成最简 Clash YAML
    假设 nodes 数据格式:
    {
      "uid": "naiveproxy",
      "nodes": [
        {
          "name": "node_1",
          "address": "openaishop.top",
          "port": 443,
          "password": "774256119a",
          "tls": true,
          "plugin": "trojan",
          "tcp_fast_open": false
        }
      ]
    }
    """
    nodes = config_data.get("nodes", [])
    
    proxies = []
    for node in nodes:
        clash_node = {
            "name": node["name"],
            "type": "trojan",  # 这里只是示例，可以根据node["plugin"]等判断
            "server": node["address"],
            "port": node["port"],
            "password": node["password"],
            "sni": node["address"] if node.get("tls") else None,
            "skip-cert-verify": True,
            "udp": True
        }
        proxies.append(clash_node)
    
    proxy_groups = [
        {
            "name": "PROXY",
            "type": "select",
            "proxies": [p["name"] for p in proxies] + ["DIRECT"]
        }
    ]
    rules = [
        "MATCH,PROXY"
    ]
    
    clash_config = {
        "proxies": proxies,
        "proxy-groups": proxy_groups,
        "rules": rules
    }
    
    return yaml.dump(clash_config, sort_keys=False)


###############################################################################
# 2) 构建 V2Ray(vmess) 订阅 (多节点 -> 二次 Base64)
###############################################################################
def build_v2ray_subscription(config_data: dict) -> str:
    """
    将 nodes 列表转换成多行 vmess://Base64(JSON)，
    然后对整段做二次 Base64。
    
    客户端(Shadowrocket、Clash Meta、V2RayNG等)添加订阅后，会自动解析。
    """
    nodes = config_data.get("nodes", [])
    lines = []

    for node in nodes:
        name = node.get("name", "Unnamed")
        address = node.get("address", "example.com")
        port = node.get("port", 443)
        password = node.get("password", "uuid-here")
        tls_enabled = node.get("tls", False)
        
        # V2Ray(JSON)字段
        v2ray_json = {
            "v": "2",
            "ps": name,           # 备注
            "add": address,
            "port": str(port),
            "id": password,       # 这里最好是真正的UUID
            "aid": "0",
            "net": "tcp",         # 简化写法，实际可能是 ws/grpc
            "type": "none",
            "host": "",
            "path": "",
            "tls": "tls" if tls_enabled else ""
        }

        v2_json_str = json.dumps(v2ray_json, separators=(',', ':'))
        v2_base64 = base64.b64encode(v2_json_str.encode('utf-8')).decode('utf-8')
        full_link = f"vmess://{v2_base64}"
        lines.append(full_link)
    
    # 多节点 -> 用换行拼接
    subscription_raw = "\n".join(lines)
    # 再对这个多行文本做二次 Base64
    final_base64 = base64.b64encode(subscription_raw.encode('utf-8')).decode('utf-8')
    
    return final_base64


###############################################################################
# 3) SubscriptionAPI: /sub
#    根据 query 参数 ?type=clash / clash_b64 / vmess
#    分别返回不同的订阅内容
###############################################################################
class SubscriptionAPI(MethodView):
    def get(self):
        """
        访问方式:
          /sub?type=clash      -> 返回明文 Clash YAML
          /sub?type=clash_b64  -> 返回 Base64 编码后的 Clash YAML
          /sub?type=vmess      -> 返回 V2Ray(vmess) 多节点订阅 (二次 Base64)
        其他值或不传就默认 clash
        """
        try:
            # 0. 从环境变量读取远程 JSON 地址
            node_json_url = os.getenv("NODE_JSON_URL")
            if not node_json_url:
                return jsonify({"error": "Missing NODE_JSON_URL"}), 500

            # 1. 请求远程 JSON
            resp = requests.get(node_json_url, timeout=5)
            resp.raise_for_status()
            config_data = resp.json()

            # 2. 根据 ?type=xxx 判断返回格式
            sub_type = request.args.get("type", "clash").lower()
            
            if sub_type == "clash":
                # 明文 Clash YAML
                yaml_str = build_clash_yaml(config_data)
                response = make_response(yaml_str)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

            elif sub_type == "clash_b64":
                # Base64后的 Clash YAML
                yaml_str = build_clash_yaml(config_data)
                yaml_b64 = base64.b64encode(yaml_str.encode('utf-8')).decode('utf-8')
                response = make_response(yaml_b64)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

            elif sub_type == "vmess":
                # V2Ray 多节点订阅 (二次 Base64)
                vmess_b64 = build_v2ray_subscription(config_data)
                response = make_response(vmess_b64)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

            else:
                # 默认返回 clash YAML
                yaml_str = build_clash_yaml(config_data)
                response = make_response(yaml_str)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

        except Exception as e:
            return jsonify({"error": str(e)}), 500