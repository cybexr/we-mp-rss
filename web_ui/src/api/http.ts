import axios from 'axios'
import { getToken } from '@/utils/auth'
import { Message } from '@arco-design/web-vue'
import router from '@/router'

// 创建axios实例
const http = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL || '') + 'api/v1/',
  timeout: 30000, // 30 seconds timeout for all requests
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    // 处理标准响应格式
    if (response.data?.code === 0) {
      return response.data?.data||response.data?.detail||response.data||response
    }
    if(response.data?.code==401){
      Message.error("未登录或登录已过期，请重新登录。")
      router.push("/login")
      return Promise.reject(new Error("未登录或登录已过期"))
    }
    const data=response.data?.detail||response.data
    const errorMsg = data?.message || '请求失败'
    if(response.headers['content-type']==='application/json') {
      Message.error(errorMsg)
    }else{
      return response.data
    }
    return Promise.reject(new Error(errorMsg))
  },
  error => {
    // 处理请求超时
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      const timeoutMsg = '请求超时，请检查网络连接或稍后重试'
      Message.error(timeoutMsg)
      return Promise.reject(new Error(timeoutMsg))
    }

    // HTTP 错误状态码处理
    if (error.response) {
      const status = error.response.status
      let errorMsg = '请求失败'

      // 从响应中提取错误消息
      const errorData = error.response.data
      if (typeof errorData === 'string') {
        errorMsg = errorData
      } else if (errorData?.detail?.message) {
        errorMsg = errorData.detail.message
      } else if (errorData?.detail) {
        errorMsg = errorData.detail
      } else if (errorData?.message) {
        errorMsg = errorData.message
      }

      // 根据状态码处理
      if (status === 401) {
        Message.error("未登录或登录已过期，请重新登录。")
        router.push("/login")
        return Promise.reject(new Error("未登录或登录已过期"))
      } else if (status === 403) {
        errorMsg = errorMsg || '没有权限访问此资源'
        Message.error(errorMsg)
      } else if (status === 404) {
        errorMsg = errorMsg || '请求的资源不存在'
        Message.error(errorMsg)
      } else if (status === 400) {
        errorMsg = errorMsg || '请求参数错误'
        Message.error(errorMsg)
      } else if (status >= 500) {
        errorMsg = errorMsg || '服务器内部错误'
        Message.error(errorMsg)
      } else {
        Message.error(errorMsg)
      }

      return Promise.reject(new Error(errorMsg))
    }

    // 网络错误或其他错误
    const errorMsg = error?.message || '网络错误，请检查网络连接'
    Message.error(errorMsg)
    return Promise.reject(new Error(errorMsg))
  }
)

export default http
