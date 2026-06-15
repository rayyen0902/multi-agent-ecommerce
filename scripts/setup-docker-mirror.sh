#!/bin/bash
# Docker 镜像加速器配置 + 预拉取基础镜像脚本
# 使用阿里云镜像加速器: https://3odwuynp.mirror.aliyuncs.com

echo "=== 配置 Docker 镜像加速器 ==="

# 1. 备份原有配置
if [ -f /etc/docker/daemon.json ]; then
    cp /etc/docker/daemon.json /etc/docker/daemon.json.bak.$(date +%Y%m%d%H%M%S)
    echo "[✓] 已备份 /etc/docker/daemon.json"
fi

# 2. 写入加速器配置
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF' > /dev/null
{
  "registry-mirrors": [
    "https://3odwuynp.mirror.aliyuncs.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"],
  "live-restore": true
}
EOF

echo "[✓] 已写入 /etc/docker/daemon.json"

# 3. 重载 Docker 配置并重启
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "[✓] Docker 已重启"

# 4. 验证配置
echo ""
echo "=== 验证配置 ==="
docker info 2>/dev/null | grep -A 5 "Registry Mirrors" || echo "无法验证，请手动检查"

# 5. 预拉取 Docker Hub 基础镜像（阿里云加速器不代理 Docker Hub）
echo ""
echo "=== 预拉取基础镜像（需要几分钟）==="
echo "正在拉取 postgres:16-alpine ..."
docker pull postgres:16-alpine && echo "[✓] postgres:16-alpine 拉取成功" || echo "[✗] postgres:16-alpine 拉取失败"

echo "正在拉取 redis:7-alpine ..."
docker pull redis:7-alpine && echo "[✓] redis:7-alpine 拉取成功" || echo "[✗] redis:7-alpine 拉取失败"

echo ""
echo "=== 配置完成 ==="
echo "加速器地址: https://3odwuynp.mirror.aliyuncs.com"
echo "额外配置: DNS 优化 + live-restore"
echo ""
echo "已预拉取的基础镜像："
echo "  - postgres:16-alpine"
echo "  - redis:7-alpine"
echo ""
echo "下次部署时 docker compose pull 速度会明显提升。"
