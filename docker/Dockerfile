FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码文件到容器中
COPY . .

# 使用 Gunicorn 作为 WSGI 服务器，并绑定到 PORT 环境变量
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
