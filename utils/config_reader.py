import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

class ConfigurationError(Exception):
    """配置相关的自定义异常"""
    pass

def load_env() -> None:
    """加载环境变量，优先从项目根目录加载"""
    current_dir = Path(__file__).parent.parent
    env_path = current_dir / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")

def validate_port(port: str) -> int:
    """验证端口号的有效性"""
    try:
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return port_num
    except ValueError as e:
        raise ConfigurationError(f"Invalid port number: {str(e)}")

def read_config() -> List[Dict[str, Any]]:
    """从环境变量读取配置信息"""
    load_env()
    
    try:
        # 获取并验证必要的环境变量
        required_vars = {
            "NODE_ADDRESS": os.environ.get("NODE_ADDRESS"),
            "NODE_USER": os.environ.get("NODE_USER"),
            "NODE_PASSWORD": os.environ.get("NODE_PASSWORD")
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ConfigurationError(f"Missing required environment variables: {', '.join(missing)}")
        
        # 验证端口
        port = validate_port(os.environ.get("NODE_PORT", "443"))
        
        # 构建节点配置
        node = {
            "name": os.environ.get("NODE_NAME", "Default Node"),
            "address": required_vars["NODE_ADDRESS"],
            "port": port,
            "user": required_vars["NODE_USER"],
            "password": required_vars["NODE_PASSWORD"],
            "tls": os.environ.get("NODE_TLS", "true").lower() == "true",
            "plugin": os.environ.get("NODE_PLUGIN", "none"),
            "tcp_fast_open": os.environ.get("NODE_TCP_FAST_OPEN", "false").lower() == "true"
        }
        
        return [node]
        
    except ConfigurationError as ce:
        raise ce
    except Exception as e:
        raise ConfigurationError(f"Unexpected error while reading configuration: {str(e)}") 