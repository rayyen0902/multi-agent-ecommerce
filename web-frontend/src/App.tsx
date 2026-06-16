import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import Dashboard from './pages/Dashboard'
import OrderList from './pages/Orders/OrderList'
import OrderDetail from './pages/Orders/OrderDetail'
import ShopList from './pages/Shops/ShopList'
import ProductList from './pages/Products/ProductList'
import LogisticsList from './pages/Logistics/LogisticsList'
import RuleList from './pages/Rules/RuleList'
import Settings from './pages/Settings'
import Login from './pages/Login'
import { useAuthStore } from './stores/useAuthStore'

const appBase = import.meta.env.BASE_URL.replace(/\/$/, '') || ''

function App() {
  const token = useAuthStore((state) => state.token)

  if (!token) {
    return (
      <Routes>
        <Route path={`${appBase}/login`} element={<Login />} />
        <Route path="*" element={<Navigate to={`${appBase}/login`} replace />} />
      </Routes>
    )
  }

  return (
    <Routes>
      <Route path={appBase} element={<MainLayout />}>
        <Route index element={<Navigate to={`${appBase}/dashboard`} replace />} />
        <Route path={`${appBase}/dashboard`} element={<Dashboard />} />
        <Route path={`${appBase}/orders`} element={<OrderList />} />
        <Route path={`${appBase}/orders/:id`} element={<OrderDetail />} />
        <Route path={`${appBase}/shops`} element={<ShopList />} />
        <Route path={`${appBase}/products`} element={<ProductList />} />
        <Route path={`${appBase}/logistics`} element={<LogisticsList />} />
        <Route path={`${appBase}/rules`} element={<RuleList />} />
        <Route path={`${appBase}/settings`} element={<Settings />} />
      </Route>
      <Route path={`${appBase}/login`} element={<Navigate to={`${appBase}/dashboard`} replace />} />
      <Route path="*" element={<Navigate to={`${appBase}/dashboard`} replace />} />
    </Routes>
  )
}

export default App
