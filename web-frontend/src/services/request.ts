import axios from 'axios'
import { message } from 'antd'
import { useAuthStore } from '../stores/useAuthStore'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.code !== 0) {
      message.error(data.message || '请求失败')
      if (data.code === 10002 || data.code === 10003) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
      return Promise.reject(new Error(data.message))
    }
    return data
  },
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    message.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
