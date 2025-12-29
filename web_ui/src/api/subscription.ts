import http from './http'
import { Message } from '@arco-design/web-vue'

export interface Subscription {
  id: string
  mp_name: string
  mp_cover: string
  mp_intro: string
  status: number
  cache_images: boolean
  remarks: string
  category: string
  created_at: string
  // Optional fields that may be added by the frontend
  sync_time?: string
}

export interface SubscriptionListResult {
  code: number
  data: {
    list: Subscription[]
    total: number
  }
}

export interface AddSubscriptionParams {
  mp_name: string
  mp_id: string
  avatar: string
  mp_intro?: string
  cache_images?: boolean
  remarks?: string
  category?: string
}

export interface MpItem {
  mp_id: string
  mp_name: string
  avatar: string
}

export interface MpSearchResult {
  code: number
  data: MpItem[]
}

export const getSubscriptions = (params?: { page?: number; pageSize?: number }) => {
  const apiParams = {
    offset: (params?.page || 0) * (params?.pageSize || 10),
    limit: params?.pageSize || 10,
    kw: params?.kw || ""
  }
  return http.get<SubscriptionListResult>('/wx/mps', { params: apiParams })
}

export const getSubscriptionDetail = (mp_id: string) => {
  return http.get<{code: number, data: Subscription}>(`/wx/mps/${mp_id}`)
}

// 添加订阅公众号信息
export const addSubscription = (data: AddSubscriptionParams) => {
  return http.post<{code: number, message: string}>('/wx/mps', data)
}
export const getSubscriptionInfo = (url: string) => {
  return http.post<{code: number, message: string}>(`/wx/mps/by_article?url=${url}`)
}

export const deleteMpApi = (mp_id: string) => {
  return http.delete<{code: number, message: string}>(`/wx/mps/${mp_id}`)
}

export const deleteSubscription = (mp_id: string) => {
  return http.delete<{code: number, message: string}>(`/wx/mps/${mp_id}`)
}

// 更新订阅公众号文章列表 
export const UpdateMps = (mp_id: string,params: { start_page?: number; end_page?: number }) => {
   const apiParams = {
    start_page: (params?.start_page || 0),
    end_page: params?.end_page || 1
  }
  return http.get<{code: number, message: string}>(`/wx/mps/update/${mp_id||'all'}?start_page=${apiParams.start_page}&end_page=${apiParams.end_page}`)
}

// 更新订阅公众号信息
export const updateSubscription = (mp_id: string, data: Partial<Subscription>) => {
  return http.put<{code: number, message: string}>(`/wx/mps/${mp_id}`, data)
}

export const searchBiz = (kw: string, params: { page?: number; pageSize?: number }) => {
  const apiParams = {
    offset: (params?.page || 0) * (params?.pageSize || 10),
    limit: params?.pageSize || 10
  }
  return http.get<SubscriptionListResult>(`/wx/mps/search/${kw}`,{ params: apiParams })
}

// 搜索公众号(不分页)
export const searchMps = (kw: string, params: { page?: number; pageSize?: number }) => {
  const apiParams = {
    kw:kw||"",
    offset: (params?.page || 0) * (params?.pageSize || 10),
    limit: params?.pageSize || 10
  }
  return http.get<SubscriptionListResult>(`/wx/mps`,{ params: apiParams })
}

export const getCategories = () => {
  return http.get<{code: number, data: { categories: string[] }}>('/wx/mps/categories')
}

export interface BatchUpdateCategoryParams {
  mp_ids: string[]
  category: string
}

export const batchUpdateCategory = async (params: BatchUpdateCategoryParams) => {
  try {
    const response = await http.put<{code: number, data: {updated_count: number}, message: string}>('/wx/mps/batch-category', params)
    return response.data
  } catch (error: any) {
    Message.error(error.message || '批量更新分类失败')
    throw error
  }
}