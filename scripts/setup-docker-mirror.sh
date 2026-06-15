#!/bin/bash
# Docker 镜像加速器配置脚本
# 使用阿里云镜像加速器: https://3odwuynp.mirror.aliyuncs.com

echo "=== 配置 Docker 镜像加速器 ==="

# 1. 备份原有配置
if [ -f /etc/docker/daemon.json ]; then
    cp /etc/docker/daemon.json /etc/docker/daemon.json.bak.$(date +%Y%m%d%H%M%S)
    echo "[✓] 已备份 /etc/docker/daemon.json"
fi

# 2. 写入加速器配置
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://3odwuynp.mirror.aliyuncs.com"
  ]
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
echo "下次部署时 docker pull 速度会明显提升。"
