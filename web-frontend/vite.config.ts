import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(() => {
  // 部署到 knownot.cc/ecom/ 时 base 必须是 /ecom/
  const base = '/ecom/'

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
