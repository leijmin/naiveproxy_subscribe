# Subscription Service

一个简单的订阅服务，支持通过 API 获取节点配置信息。

## 功能特点

- 支持基本的节点配置
- 提供 Base64 编码的订阅内容
- Docker 容器化部署
- 支持环境变量配置

## 快速开始

### 本地运行

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/subscription-service.git
cd subscription-service
```

2. 创建并配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行服务：
```bash
python app.py
```

### Docker 部署

1. 使用 docker-compose：
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Railway 部署

1. Fork 这个仓库
2. 在 Railway 中创建新项目，选择 GitHub 仓库
3. 配置环境变量
4. Railway 会自动部署服务

## API 文档

### 获取订阅内容

```README.md
GET /api/subscribe
```

响应：Base64 编码的配置内容

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| PORT | 服务端口 | 5000 |
| NODE_NAME | 节点名称 | Default Node |
| NODE_ADDRESS | 节点地址 | - |
| NODE_PORT | 节点端口 | 443 |
| NODE_USER | 用户名 | - |
| NODE_PASSWORD | 密码 | - |
| NODE_TLS | 是否启用 TLS | true |
| NODE_PLUGIN | 插件类型 | none |
| NODE_TCP_FAST_OPEN | 是否启用 TCP Fast Open | false |

## License

MIT
