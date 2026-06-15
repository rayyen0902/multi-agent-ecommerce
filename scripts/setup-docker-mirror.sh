#!/bin/bash
# Docker 镜像加速器配置脚本
# 使用阿里云镜像加速器: https://3odwuynp.mirror.aliyuncs.com

echo "=== 配置 Docker 镜像加速器 ==="

# 1. 备份原有配置
if [ -f /etc/docker/daemon.json ]; then
    cp /etc/docker/daemon.json /etc/docker/daemon.json.bak.$(date +%Y%m%d%H%M%S)
    echo "[✓] 已备份 /etc/docker/daemon.json"
fi

# 2. 写入加速器配置（同时包含 ghcr.io 和 Docker Hub 的加速器）
cat > /etc/docker/daemon.json << 'EOF'
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

echo ""
echo "=== 配置完成 ==="
echo "加速器地址: https://3odwuynp.mirror.aliyuncs.com"
echo "额外配置: DNS 优化 + live-restore"
echo ""
echo "请在服务器上重新运行一次:"
echo "  curl -sL https://raw.githubusercontent.com/rayyen0902/multi-agent-ecommerce/main/scripts/setup-docker-mirror.sh | sudo bash"
