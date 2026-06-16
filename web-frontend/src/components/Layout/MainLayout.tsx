import { Layout, Menu, Dropdown, Button } from 'antd'
import {
  DashboardOutlined,
  ShoppingCartOutlined,
  ShopOutlined,
  AppstoreOutlined,
  CarOutlined,
  ThunderboltOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/useAuthStore'
import ChatFloatButton from '../ChatFloatButton'

const { Header, Sider, Content } = Layout

const appBase = import.meta.env.BASE_URL.replace(/\/$/, '') || ''

const menuItems = [
  { key: `${appBase}/dashboard`, icon: <DashboardOutlined />, label: '数据看板' },
  { key: `${appBase}/orders`, icon: <ShoppingCartOutlined />, label: '订单管理' },
  { key: `${appBase}/shops`, icon: <ShopOutlined />, label: '店铺管理' },
  { key: `${appBase}/products`, icon: <AppstoreOutlined />, label: '商品管理' },
  { key: `${appBase}/logistics`, icon: <CarOutlined />, label: '物流跟踪' },
  { key: `${appBase}/rules`, icon: <ThunderboltOutlined />, label: '自动化规则' },
  { key: `${appBase}/settings`, icon: <SettingOutlined />, label: '系统设置' },
]

export default function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { username, logout } = useAuthStore()

  const selectedKey = appBase + '/' + location.pathname.replace(new RegExp(`^${appBase}/?`), '').split('/')[0]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={220}>
        <div style={{
          height: 64, display: 'flex', alignItems: 'center',
          justifyContent: 'center', color: '#fff', fontSize: 18, fontWeight: 'bold'
        }}>
          电商订单自动化
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff', padding: '0 24px',
          display: 'flex', justifyContent: 'flex-end', alignItems: 'center',
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
        }}>
          <Dropdown menu={{
            items: [
              { key: 'profile', icon: <UserOutlined />, label: username || '管理员' },
              { type: 'divider' },
              {
                key: 'logout', icon: <LogoutOutlined />, label: '退出登录',
                onClick: () => { logout(); navigate(`${appBase}/login`) }
              },
            ]
          }}>
            <Button type="text" icon={<UserOutlined />}>
              {username || '管理员'}
            </Button>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
      <ChatFloatButton />
    </Layout>
  )
}
