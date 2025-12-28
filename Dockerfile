# 简化的Dockerfile - 基于官方Python镜像
# 仅支持 amd64 架构
FROM --platform=linux/amd64 python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_NO_CACHE_DIR=1 \
    INSTALL=True \
    BROWSER_TYPE=webkit \
    PLAYWRIGHT_BROWSERS_PATH=/app/env/driver/_x86_64 \
    TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 基础工具
    gcc \
    g++ \
    make \
    wget \
    git \
    # Python编译依赖
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    # 数据库客户端
    postgresql-client \
    # 清理缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制应用代码
COPY . .

# 设置配置文件(如果不存在)
COPY config.example.yaml ./config.yaml

# 设置版本信息
RUN echo "1.0.$(date +%Y%m%d.%H%M)" >> docker_version.txt

# 设置脚本权限
RUN chmod +x install.sh start.sh

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["bash", "start.sh"]
