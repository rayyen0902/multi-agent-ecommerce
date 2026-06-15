#!/bin/bash
set -euo pipefail

# Ecom 部署脚本
# 用法: ./deploy.sh [latest|版本号]

cd /opt/ecom

IMAGE_TAG="${1:-latest}"

echo "=== 拉取最新镜像 ==="
docker compose -f docker-compose.ecom.yml pull

echo "=== 停止旧容器 ==="
docker compose -f docker-compose.ecom.yml down

echo "=== 启动新容器 ==="
docker compose -f docker-compose.ecom.yml up -d

echo "=== 等待服务就绪 ==="
sleep 10

echo "=== 检查容器状态 ==="
docker compose -f docker-compose.ecom.yml ps

echo "=== 重新加载 Nginx ==="
nginx -t && nginx -s reload

echo "=== 部署完成 ==="
echo "访问地址: https://knownot.cc/ecom/"
