from flask import Flask, jsonify, make_response, request
from flask.views import MethodView
import os
import requests
import base64
import yaml
import json

app = Flask(__name__)

def build_clash_yaml_http(config_data: dict) -> str:
    """
    只处理 plugin=http 的节点，把它转换成 Clash type=http.
    如果你还有 plugin=socks 或别的，也可以在这里根据 plugin 判断。
    """
    nodes = config_data.get("nodes", [])
    
    proxies = []
    for node in nodes:
        plugin = node.get("plugin", "").lower()
        if plugin == "http":
            clash_node = {
                "name": node["name"],
                "type": "http",             # 关键：Clash 里 http=HTTP(s)正向代理
                "server": node["address"],
                "port": node["port"],
                "username": node.get("username", ""),
                "password": node.get("password", ""),
                "tls": bool(node.get("tls", False)),
                "skip-cert-verify": True,  # 如果你的证书是自签，可能需要开启
                "udp": True                # Clash 里http节点也可以开udp
            }
            proxies.append(clash_node)

    # 给 Clash 组装一个 Proxy Group
    proxy_groups = [
        {
            "name": "PROXY",
            "type": "select",
            "proxies": [p["name"] for p in proxies] + ["DIRECT"]
        }
    ]
    # 简单的 rule
    rules = [
        "MATCH,PROXY"
    ]

    clash_config = {
        "proxies": proxies,
        "proxy-groups": proxy_groups,
        "rules": rules
    }

    # 转成 YAML 字符串
    return yaml.dump(clash_config, sort_keys=False)

class SubscriptionAPI(MethodView):
    def get(self):
        """
        访问:
          /sub?type=clash      -> 明文 Clash YAML (仅HTTP正向代理节点)
          /sub?type=clash_b64  -> Base64 后的 Clash YAML
        不传 type / 其他值 -> 默认 clash
        """
        try:
            node_json_url = os.getenv("NODE_JSON_URL")
            if not node_json_url:
                return jsonify({"error": "Missing NODE_JSON_URL"}), 500
            
            # 拉取远程 JSON
            resp = requests.get(node_json_url, timeout=5)
            resp.raise_for_status()
            config_data = resp.json()

            sub_type = request.args.get("type", "clash").lower()

            # 生成 Clash YAML
            yaml_str = build_clash_yaml_http(config_data)

            if sub_type == "clash":
                # 明文 YAML
                response = make_response(yaml_str)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

            elif sub_type == "clash_b64":
                # Base64 后的 YAML
                yaml_b64 = base64.b64encode(yaml_str.encode('utf-8')).decode('utf-8')
                response = make_response(yaml_b64)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

            else:
                # 默认返回 clash
                response = make_response(yaml_str)
                response.headers["Content-Type"] = "text/plain; charset=utf-8"
                return response

        except Exception as e:
            return jsonify({"error": str(e)}), 500
