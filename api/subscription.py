from flask.views import MethodView
from flask import jsonify, current_app, make_response
from utils.config_reader import read_config, ConfigurationError
import base64
import json
from typing import Tuple, Any

class SubscriptionAPI(MethodView):
    def get(self) -> Tuple[Any, int, dict]:
        """获取订阅内容"""
        try:
            nodes = read_config()
            subscription_content = []
            
            for node in nodes:
                node_info = self._build_node_info(node)
                encoded_str = self._encode_node_info(node_info)
                subscription_content.append(encoded_str)
            
            final_content = '\n'.join(subscription_content)
            final_encoded = base64.b64encode(final_content.encode()).decode()
            
            response = make_response(final_encoded)
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Cache-Control'] = 'no-cache'
            return response
            
        except ConfigurationError as ce:
            current_app.logger.error(f'Configuration error: {str(ce)}')
            return jsonify({'error': 'Configuration error', 'message': str(ce)}), 500
        except Exception as e:
            current_app.logger.error(f'Subscription error: {str(e)}', exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500
    
    def _build_node_info(self, node: dict) -> dict:
        """构建节点信息"""
        return {
            "name": node["name"],
            "address": node["address"],
            "port": node["port"],
            "user": node["user"],
            "password": node["password"],
            "tls": node["tls"],
            "plugin": node["plugin"],
            "tcp_fast_open": node["tcp_fast_open"]
        }
    
    def _encode_node_info(self, node_info: dict) -> str:
        """编码节点信息"""
        node_str = json.dumps(node_info)
        return base64.b64encode(node_str.encode()).decode() 