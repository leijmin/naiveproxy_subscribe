from flask.views import MethodView
from flask import jsonify, current_app, make_response
from utils.config_reader import read_config, ConfigurationError
import yaml  # 需要在你的 requirements.txt 安装 PyYAML
from typing import Tuple, Any

class SubscriptionAPI(MethodView):
    def get(self) -> Tuple[Any, int, dict]:
        """获取订阅内容 (返回 Clash YAML)"""
        try:
            nodes = read_config()  # 读取你已有的节点配置列表
            # 构建 Clash 所需的 proxies 列表
            proxies = []
            for node in nodes:
                # 这里以 Trojan 节点为例，你也可以根据需求改成 vmess、shadowsocks 等
                # Clash YAML 有多种节点 type，可根据你的节点实际协议选用
                clash_node = {
                    "name": node["name"],
                    "type": "trojan",
                    "server": node["address"],
                    "port": node["port"],
                    "password": node["password"],
                    # TLS 等可选项
                    "sni": node["address"] if node["tls"] else None,
                    "skip-cert-verify": True,   # 视情况而定
                    "udp": True,               # Clash/Shadowrocket 中是否启用 UDP
                }
                proxies.append(clash_node)

            # 定义一个最基本的 proxy-groups
            # 例如，让用户可以在客户端里手动选择节点
            proxy_groups = [
                {
                    "name": "PROXY",
                    "type": "select",
                    # 将所有节点 + "DIRECT" 都加进这个组
                    "proxies": [p["name"] for p in proxies] + ["DIRECT"]
                }
            ]

            # 定义最基本的匹配规则
            # 这里为了演示，简单搞一个全量流量走 PROXY
            # 也可以自定义成更丰富的规则
            rules = [
                "MATCH,PROXY"
            ]

            # 最终组装成 Clash 配置的字典
            clash_config = {
                "proxies": proxies,
                "proxy-groups": proxy_groups,
                "rules": rules
            }

            # 转换成 YAML 字符串
            yaml_str = yaml.dump(clash_config, sort_keys=False)

            # Flask 返回
            response = make_response(yaml_str)
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Cache-Control'] = 'no-cache'
            return response

        except ConfigurationError as ce:
            current_app.logger.error(f'Configuration error: {str(ce)}')
            return jsonify({'error': 'Configuration error', 'message': str(ce)}), 500
        except Exception as e:
            current_app.logger.error(f'Subscription error: {str(e)}', exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500