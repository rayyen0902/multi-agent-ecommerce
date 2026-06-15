import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // 生产环境使用 /ecom/ 前缀，开发环境保持根路径
  const isEcomDeploy = process.env.VITE_ECOM_DEPLOY === 'true'
  const base = isEcomDeploy ? '/ecom/' : '/'

  return {
    plugins: [react()],
    base,
    server: {
      port: 3000,
      proxy: {
        '/ecom/api/agent': {
          target: 'http://localhost:9000',
          changeOrigin: true,
          ws: true,
          rewrite: (path) => path.replace(/^\/ecom/, ''),
        },
        '/ecom/api': {
          target: 'http://localhost:8080',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/ecom/, ''),
        },
        '/api/agent': {
          target: 'http://localhost:9000',
          changeOrigin: true,
          ws: true,
        },
        '/api': {
          target: 'http://localhost:8080',
          changeOrigin: true,
        },
      },
    },
  }
})
