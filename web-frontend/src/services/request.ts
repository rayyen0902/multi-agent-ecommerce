import axios, { type AxiosRequestConfig } from 'axios'
import { message } from 'antd'
import { useAuthStore } from '../stores/useAuthStore'
import type { ApiResponse } from '../types'

const request = axios.create({
  baseURL: '/ecom/api/v1',
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

// 获取 SPA 应用的基础路径（Vite base 配置）
const appBase = import.meta.env.BASE_URL.replace(/\/$/, '') || ''

// 响应拦截器 — 返回 ApiResponse<T> 而非 AxiosResponse
request.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.code !== 0) {
      message.error(data.message || '请求失败')
      if (data.code === 10002 || data.code === 10003) {
        useAuthStore.getState().logout()
        window.location.href = `${appBase}/login`
      }
      return Promise.reject(new Error(data.message))
    }
    return data as ApiResponse<unknown>
  },
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = `${appBase}/login`
    }
    message.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

// 封装类型正确的请求方法
const http = {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return request.get(url, config).then(r => r.data as ApiResponse<T>)
  },
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return request.post(url, data, config).then(r => r.data as ApiResponse<T>)
  },
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return request.put(url, data, config).then(r => r.data as ApiResponse<T>)
  },
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return request.delete(url, config).then(r => r.data as ApiResponse<T>)
  },
}

export default http
