# 使用官方 Python 镜像作为基础
FROM python:3.11-slim

# 设置环境变量，防止 Python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 确保 Python 输出是无缓冲的
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /app

# 安装依赖
# 首先只复制 requirements.txt 以利用 Docker 的层缓存
COPY ./requirements.txt /app/requirements.txt

# --no-cache-dir: 不存储包缓存，减小镜像大小
# -r: 从指定文件安装
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
# . 表示当前目录（在 docker-compose.yml 中定义的 context）下的所有内容
# 复制到工作目录 /app
COPY . /app

# 暴露 FastAPI 应用运行的端口
EXPOSE 8000

# 容器启动时执行的命令
# 运行 uvicorn 服务器，使其可以从网络中的任何 IP 地址访问
# --host 0.0.0.0: 允许容器外的访问
# --port 8000: 监听 8000 端口
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
