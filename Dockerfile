FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码文件到容器中
COPY . .

# 这里用的是 Shell 形式 CMD，而非 JSON 数组
CMD ["/bin/bash", "-c", "echo 'The $PORT is: ' $PORT && gunicorn run:app --bind 0.0.0.0:$PORT"]

