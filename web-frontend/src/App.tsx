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

function App() {
  const token = useAuthStore((state) => state.token)

  if (!token) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="orders" element={<OrderList />} />
        <Route path="orders/:id" element={<OrderDetail />} />
        <Route path="shops" element={<ShopList />} />
        <Route path="products" element={<ProductList />} />
        <Route path="logistics" element={<LogisticsList />} />
        <Route path="rules" element={<RuleList />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
