import { Card, Typography } from 'antd'

const { Title, Paragraph } = Typography

export default function Settings() {
  return (
    <Card title="系统设置">
      <Typography>
        <Title level={4}>关于系统</Title>
        <Paragraph>
          电商订单管理自动化系统 v1.0.0
        </Paragraph>
        <Paragraph>
          技术栈：React + Go (Gin) + Python (FastAPI) + PostgreSQL + Redis
        </Paragraph>
        <Title level={4}>支持平台</Title>
        <Paragraph>
          淘宝开放平台、京东开放平台、拼多多开放平台
        </Paragraph>
        <Title level={4}>系统信息</Title>
        <Paragraph>
          Go 服务端口: 8080<br />
          Python Worker 端口: 8000<br />
          Celery Flower 监控: 5555
        </Paragraph>
      </Typography>
    </Card>
  )
}
